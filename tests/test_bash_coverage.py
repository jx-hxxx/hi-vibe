"""Bash로 들어온 변경이 안전망을 통째로 빠져나가던 구멍을 막는다.

PostToolUse 훅의 대상은 `Write|Edit|MultiEdit`뿐이다. Claude가 heredoc이나
`sed -i`, 생성 스크립트로 파일을 쓰면:

  1. 실시간 감지(에러 삼킴·비밀키)를 건너뛴다 — 훅이 그 도구를 안 본다
  2. 트랜스크립트의 `edited` 목록에도 안 남아서, Stop 훅이 그 턴을
     "코드 안 건드림"으로 보고 **리뷰까지 통째로 건너뛴다**
  3. 비밀키는 `check`의 저장소 전체 스캔에도 없어서 **영영 안 잡혔다**

1번은 Claude Code의 훅 계약이라 여기서 못 막는다. 2번은 Bash 명령까지 보고,
3번은 스캐너에 비밀키 검사를 붙여 막았다. 이 파일은 그 둘을 지킨다.
"""
import json
import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "hooks", "scripts"))
sys.path.insert(0, os.path.join(REPO, "skills", "repo-xray", "scripts"))

import _common          # noqa: E402
import audit            # noqa: E402
import post_write_guard  # noqa: E402


# 스캐너 검사용 가짜 키. 저장소를 스캔하면 이 파일도 걸리므로 마커를 단다 —
# 진짜 키가 아니라는 것을 기계가 알아야 `check` 결과가 거짓 경보로 오염되지
# 않는다 (자기 저장소에서 "비밀키 11건"이 뜨던 이유).
FAKE_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"  # hi-vibe: allow-secret
FAKE_ASSIGN = 'API_KEY = "%s"\n' % FAKE_KEY


def _transcript(commands):
    """Bash tool_use만 담긴 최소 트랜스크립트 파일을 만든다."""
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for cmd in commands:
            f.write(json.dumps({
                "type": "assistant",
                "message": {"role": "assistant", "content": [
                    {"type": "tool_use", "name": "Bash",
                     "input": {"command": cmd}}]},
            }) + "\n")
    return path


class BashWriteDetectionTest(unittest.TestCase):
    """`bash_wrote_files` — 넓게 잡되, 순수 조회는 안 잡는다."""

    def _check(self, cmd, expected):
        path = _transcript([cmd])
        try:
            self.assertEqual(_common.bash_wrote_files(path), expected,
                             f"{cmd!r} → {expected} 이어야 한다")
        finally:
            os.unlink(path)

    def test_writing_commands_are_detected(self):
        for cmd in [
            "cat > app.py <<'EOF'\nprint(1)\nEOF",
            "echo 'x = 1' > config.py",
            "echo more >> notes.py",
            "sed -i '' 's/a/b/' main.py",
            "cp a.py b.py",
            "mv old.py new.py",
            "printf 'x' | tee out.py",
            "python3 -c \"open('g.py','w').write('x')\"",
        ]:
            self._check(cmd, True)

    def test_read_only_commands_are_not_detected(self):
        """조회만 하는 턴까지 잡으면 '순수 대화 세션은 안 막는다'가 깨진다."""
        for cmd in [
            "git status --short",
            "ls -la",
            "python3 -m unittest discover -s tests 2>&1 | tail -5",
            "grep -n foo bar.py",
            "gh run list --limit 3",
            "cat README.md",
            "curl -s https://example.com > /dev/null",
        ]:
            self._check(cmd, False)

    def test_no_bash_at_all(self):
        path = _transcript([])
        try:
            self.assertFalse(_common.bash_wrote_files(path))
        finally:
            os.unlink(path)

    def test_missing_transcript_is_safe(self):
        """훅은 어떤 입력에도 죽지 않는다 (fail-open)."""
        self.assertFalse(_common.bash_wrote_files("/nonexistent/transcript.jsonl"))


class SecretScanTest(unittest.TestCase):
    """`check`의 저장소 전체 스캔이 비밀키를 잡는다 — 훅이 못 본 경로의 유일한 그물."""

    def test_scanner_and_hook_share_the_rule(self):
        """규칙을 두 벌 두면 한쪽만 고쳐져 결과가 갈린다 (SSOT)."""
        finder, exts = audit.load_secret_finder()
        self.assertIsNotNone(finder, "훅에서 비밀키 판정을 못 불러왔다")
        self.assertIs(finder, post_write_guard.iter_secrets)
        self.assertEqual(exts, post_write_guard.SECRET_EXT)

    def _scan(self, files):
        with tempfile.TemporaryDirectory(prefix="vibe-secret-") as root:
            for name, body in files.items():
                with open(os.path.join(root, name), "w", encoding="utf-8") as f:
                    f.write(body)
            finder, exts = audit.load_secret_finder()
            paths = [os.path.join(root, n) for n in files]
            return audit.secret_report(root, paths, finder, exts)

    def test_hardcoded_key_is_found(self):
        found = self._scan({
            "cfg.py": FAKE_ASSIGN,
            "clean.py": "x = 1\n",
        })
        self.assertTrue(found, "하드코딩된 키를 못 잡았다")
        self.assertEqual({f["file"] for f in found}, {"cfg.py"})
        self.assertEqual({f["line"] for f in found}, {1})

    def test_report_never_carries_the_value(self):
        """리포트가 키 유출 통로가 되면 안 된다 — 파일·줄·종류만."""
        found = self._scan({"cfg.py": FAKE_ASSIGN})
        self.assertTrue(found)
        for item in found:
            self.assertEqual(sorted(item), ["file", "kind", "line"])
            self.assertNotIn(FAKE_KEY, json.dumps(item, ensure_ascii=False))

    def test_one_line_counts_once(self):
        """한 줄이 여러 패턴에 걸려도 한 건이다.

        실제로 겪었다: 자기 저장소를 스캔하니 "비밀키 11건"이 떴는데
        고유 위치는 6곳이었다. 같은 키가 "OpenAI류 키"와 "하드코딩된 시크릿
        할당"에 동시에 잡혀 두 배로 세어진 것이다. 세는 단위는 **키가 있는
        자리**지 규칙이 걸린 횟수가 아니다 — 부풀린 숫자는 검사 신뢰도를
        깎는다."""
        found = self._scan({"cfg.py": FAKE_ASSIGN})
        self.assertEqual(len(found), 1, f"한 줄인데 {len(found)}건으로 셌다: {found}")
        # 종류는 합쳐서 보여준다 — 묶었다고 정보를 버리지는 않는다
        self.assertIn("/", found[0]["kind"])

    def test_own_repo_scan_is_clean(self):
        """hi-vibe 저장소 자신을 스캔하면 비밀키 0건이어야 한다.

        테스트 픽스처의 가짜 키에 `allow-secret`을 안 달면 자기 검사가
        거짓 경보로 오염된다 — "우리 도구로 우리를 검사하면 11건"은
        그 자체로 신뢰 문제다."""
        finder, exts = audit.load_secret_finder()
        _py, _js, text_files = audit.collect_files(REPO)
        found = audit.secret_report(REPO, text_files, finder, exts)
        self.assertEqual(
            found, [],
            "자기 저장소에서 비밀키가 잡힌다 — 진짜면 지우고, 테스트용 "
            "가짜 키면 그 줄에 `hi-vibe: allow-secret`을 달아라:\n"
            + "\n".join(f"  {f['file']}:{f['line']} ({f['kind']})" for f in found))

    def test_env_files_are_skipped(self):
        """`.env`는 원래 키를 두는 자리 — 훅과 같은 규칙."""
        body = FAKE_ASSIGN
        self.assertEqual(self._scan({".env": body}), [])
        self.assertEqual(self._scan({".env.local": body}), [])

    def test_allow_marker_is_honoured(self):
        body = FAKE_ASSIGN.rstrip("\n") + "  # hi-vibe: allow-secret\n"
        self.assertEqual(self._scan({"cfg.py": body}), [])

    def test_full_scan_writes_the_bucket(self):
        """실제 `check` 경로(cmd_scan)로 돌려서 리포트에 실리는지 본다.

        함수 단위로만 검사하면 "스캔은 되는데 리포트에 안 실리는" 상태를
        놓친다 — 스킬이 읽는 건 report.json이다."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory(prefix="vibe-secret-scan-") as root:
            with open(os.path.join(root, "cfg.py"), "w", encoding="utf-8") as f:
                f.write('TOKEN = "%s"\n' % FAKE_KEY)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                audit.cmd_scan(root)
            with open(os.path.join(root, ".repo-xray", "report.json"),
                      encoding="utf-8") as f:
                report = json.load(f)
        self.assertIn("hardcoded_secrets", report)
        self.assertTrue(report["hardcoded_secrets"], "리포트에 안 실렸다")
        self.assertEqual(report["scan"]["unavailable"], [])
        # 있을 때만, 눈에 띄게 요약 줄에 올린다
        self.assertIn("hardcoded secrets", buf.getvalue())

    def test_clean_repo_reports_no_secret_line(self):
        """0건이면 요약에 줄을 만들지 않는다 (없는 경고를 만들지 않는다)."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory(prefix="vibe-secret-clean-") as root:
            with open(os.path.join(root, "ok.py"), "w", encoding="utf-8") as f:
                f.write("x = 1\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                audit.cmd_scan(root)
        self.assertNotIn("hardcoded secrets", buf.getvalue())


if __name__ == "__main__":
    unittest.main()

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
            "cfg.py": 'API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"\n',
            "clean.py": "x = 1\n",
        })
        self.assertTrue(found, "하드코딩된 키를 못 잡았다")
        self.assertEqual({f["file"] for f in found}, {"cfg.py"})
        self.assertEqual({f["line"] for f in found}, {1})

    def test_report_never_carries_the_value(self):
        """리포트가 키 유출 통로가 되면 안 된다 — 파일·줄·종류만."""
        secret = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"
        found = self._scan({"cfg.py": f'API_KEY = "{secret}"\n'})
        self.assertTrue(found)
        for item in found:
            self.assertEqual(sorted(item), ["file", "kind", "line"])
            self.assertNotIn(secret, json.dumps(item, ensure_ascii=False))

    def test_env_files_are_skipped(self):
        """`.env`는 원래 키를 두는 자리 — 훅과 같은 규칙."""
        body = 'API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"\n'
        self.assertEqual(self._scan({".env": body}), [])
        self.assertEqual(self._scan({".env.local": body}), [])

    def test_allow_marker_is_honoured(self):
        body = ('API_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"'
                '  # hi-vibe: allow-secret\n')
        self.assertEqual(self._scan({"cfg.py": body}), [])

    def test_full_scan_writes_the_bucket(self):
        """실제 `check` 경로(cmd_scan)로 돌려서 리포트에 실리는지 본다.

        함수 단위로만 검사하면 "스캔은 되는데 리포트에 안 실리는" 상태를
        놓친다 — 스킬이 읽는 건 report.json이다."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory(prefix="vibe-secret-scan-") as root:
            with open(os.path.join(root, "cfg.py"), "w", encoding="utf-8") as f:
                f.write('TOKEN = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"\n')
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

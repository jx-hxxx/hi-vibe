"""훅 스크립트 동작 검증: _common 유틸, PreCompact 자동 기록,
Stop 알림(세션당 1회), PostToolUse 에러 삼킴 감지.

각 훅의 main(payload)을 직접 호출한다 — run() 래퍼는 모든 예외를
삼키므로(호스트 보호 계약) 테스트에서는 쓰지 않는다.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "hooks", "scripts"))
import _common
import post_write_guard
import pre_compact
import stop_nudge


class TempProject(unittest.TestCase):
    """handover.md가 있는(= init된) 임시 프로젝트."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="vibe-hook-test-")
        self.handover = os.path.join(self.root, "handover.md")
        with open(self.handover, "w", encoding="utf-8") as f:
            f.write("# Handover — 세션 인수인계\n")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def read_handover(self):
        with open(self.handover, encoding="utf-8") as f:
            return f.read()


class CommonTest(TempProject):
    def test_project_gate(self):
        self.assertTrue(_common.project_gate(self.root))
        self.assertFalse(_common.project_gate(tempfile.gettempdir()))
        self.assertFalse(_common.project_gate(""))

    def test_prepend_keeps_header_and_orders_newest_first(self):
        _common.prepend_entry(self.handover, "## 2026-01-01 00:00\n\n- old")
        _common.prepend_entry(self.handover, "## 2026-01-02 00:00\n\n- new")
        text = self.read_handover()
        self.assertTrue(text.startswith("# Handover"))
        self.assertLess(text.find("2026-01-02"), text.find("2026-01-01"))

    def test_rotate_moves_old_entries_to_archive(self):
        for i in range(25):
            _common.prepend_entry(self.handover, f"## entry-{i}\n\n- x")
        _common.rotate(self.handover)
        kept = self.read_handover()
        archive_path = os.path.join(self.root, "handover-archive.md")
        self.assertTrue(os.path.isfile(archive_path))
        with open(archive_path, encoding="utf-8") as f:
            archived = f.read()
        # 최신 10개 유지, 오래된 것은 아카이브로
        self.assertIn("entry-24", kept)
        self.assertNotIn("entry-0", kept)
        self.assertIn("entry-0", archived)

    def test_rotate_noop_under_limit(self):
        for i in range(5):
            _common.prepend_entry(self.handover, f"## entry-{i}\n\n- x")
        _common.rotate(self.handover)
        self.assertFalse(os.path.isfile(os.path.join(self.root, "handover-archive.md")))
        self.assertIn("entry-0", self.read_handover())

    def test_parse_transcript(self):
        transcript = os.path.join(self.root, "t.jsonl")
        lines = [
            {"type": "user", "message": {"role": "user", "content": "버그 고쳐줘"}},
            {"type": "assistant", "message": {"role": "assistant", "content": [
                {"type": "tool_use", "name": "Edit",
                 "input": {"file_path": "/p/core.py", "new_string": "x"}},
                {"type": "tool_use", "name": "Bash", "input": {"command": "ls"}},
            ]}},
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "text", "text": "이제 배포해줘"}]}},
            {"type": "user", "message": {"role": "user",
                                         "content": "<system-reminder>skip me</system-reminder>"}},
            "not json at all",
        ]
        with open(transcript, "w", encoding="utf-8") as f:
            for entry in lines:
                f.write(entry if isinstance(entry, str) else json.dumps(entry, ensure_ascii=False))
                f.write("\n")
        prompts, edited = _common.parse_transcript(transcript)
        self.assertEqual(prompts, ["버그 고쳐줘", "이제 배포해줘"])
        self.assertEqual(edited, ["/p/core.py"])


class PreCompactTest(TempProject):
    def payload(self, transcript=""):
        return {"cwd": self.root, "transcript_path": transcript,
                "trigger": "auto", "session_id": "test1234"}

    def test_writes_auto_entry(self):
        pre_compact.main(self.payload())
        text = self.read_handover()
        self.assertIn("compact 직전", text)
        self.assertIn("자동 생성", text)

    def test_gate_blocks_uninitialized_project(self):
        other = tempfile.mkdtemp(prefix="vibe-noinit-")
        try:
            pre_compact.main({"cwd": other, "transcript_path": "",
                              "trigger": "auto", "session_id": "x"})
            self.assertEqual(os.listdir(other), [])
        finally:
            shutil.rmtree(other, ignore_errors=True)


class StopNudgeTest(TempProject):
    def make_transcript(self, edited_files):
        transcript = os.path.join(self.root, "t.jsonl")
        with open(transcript, "w", encoding="utf-8") as f:
            for fp in edited_files:
                f.write(json.dumps({"type": "assistant", "message": {"content": [
                    {"type": "tool_use", "name": "Edit", "input": {"file_path": fp}},
                ]}}) + "\n")
        return transcript

    def run_nudge(self, transcript, sid="s1"):
        buf = io.StringIO()
        with redirect_stdout(buf):
            stop_nudge.main({"cwd": self.root, "session_id": sid,
                             "transcript_path": transcript})
        return buf.getvalue()

    def test_nudges_once_for_code_without_changelog(self):
        transcript = self.make_transcript(["/p/core.py"])
        first = self.run_nudge(transcript)
        self.assertIn("CHANGELOG", first)
        second = self.run_nudge(transcript)  # 같은 세션에선 침묵
        self.assertEqual(second, "")

    def test_silent_when_changelog_touched(self):
        transcript = self.make_transcript(["/p/core.py", "/p/CHANGELOG.md"])
        self.assertEqual(self.run_nudge(transcript, sid="s2"), "")

    def test_silent_for_doc_only_edits(self):
        transcript = self.make_transcript(["/p/README.md"])
        self.assertEqual(self.run_nudge(transcript, sid="s3"), "")


class PostWriteGuardTest(TempProject):
    def run_guard(self, tool, tool_input):
        buf = io.StringIO()
        with redirect_stdout(buf):
            post_write_guard.main({"cwd": self.root, "tool_name": tool,
                                   "tool_input": tool_input})
        return buf.getvalue()

    def test_write_with_bare_except_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": "try:\n    fetch()\nexcept:\n    pass\n",
        })
        self.assertIn("에러 삼킴", out)

    def test_write_with_broad_except_pass_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": "try:\n    fetch()\nexcept Exception:  # 나중에\n    pass\n",
        })
        self.assertIn("에러 삼킴", out)

    def test_allow_swallow_marker_skipped(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": "try:\n    fetch()\nexcept KeyError:\n    pass  # hi-vibe: allow-swallow — 캐시 미스는 무해\n",
        })
        self.assertEqual(out, "")

    def test_handled_except_not_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": "try:\n    fetch()\nexcept KeyError as e:\n    log.warning('miss: %s', e)\n    raise\n",
        })
        self.assertEqual(out, "")

    def test_empty_js_catch_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/app.ts",
            "content": "try { go(); } catch (e) {}\n",
        })
        self.assertIn("에러 삼킴", out)

    def test_empty_promise_catch_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/app.js",
            "content": "fetchData().catch(() => {});\n",
        })
        self.assertIn("에러 삼킴", out)

    def test_edit_preexisting_swallow_not_reflagged(self):
        """old_string에 이미 있던 삼킴을 그대로 옮기는 편집은 잔소리하지 않는다."""
        snippet = "try:\n    f()\nexcept:\n    pass\n"
        out = self.run_guard("Edit", {
            "file_path": "/p/svc.py",
            "old_string": snippet, "new_string": snippet + "x = 1\n",
        })
        self.assertEqual(out, "")

    def test_edit_new_swallow_flagged(self):
        out = self.run_guard("Edit", {
            "file_path": "/p/svc.py",
            "old_string": "x = 1\n",
            "new_string": "try:\n    f()\nexcept:\n    pass\n",
        })
        self.assertIn("에러 삼킴", out)

    def test_non_code_file_ignored(self):
        out = self.run_guard("Write", {
            "file_path": "/p/notes.md",
            "content": "except:\n    pass\n",
        })
        self.assertEqual(out, "")

    def test_gate_blocks_uninitialized_project(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            post_write_guard.main({"cwd": tempfile.gettempdir(), "tool_name": "Write",
                                   "tool_input": {"file_path": "/p/svc.py",
                                                  "content": "except:\n    pass\n"}})
        self.assertEqual(buf.getvalue(), "")


class SecretGuardTest(TempProject):
    FAKE_ANTHROPIC = "sk-ant-" + "a1B2" * 8          # 32자 본문
    FAKE_AWS = "AKIA" + "ABCDEFGHIJKLMNOP"           # AKIA + 16 대문자

    def run_guard(self, tool, tool_input):
        buf = io.StringIO()
        with redirect_stdout(buf):
            post_write_guard.main({"cwd": self.root, "tool_name": tool,
                                   "tool_input": tool_input})
        return buf.getvalue()

    def test_hardcoded_api_key_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": f'client = Client(key="{self.FAKE_ANTHROPIC}")\n',
        })
        self.assertIn("비밀키", out)

    def test_aws_key_in_config_json_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/config.json",
            "content": '{"aws_access_key_id": "%s"}\n' % self.FAKE_AWS,
        })
        self.assertIn("비밀키", out)

    def test_generic_secret_assignment_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/settings.py",
            "content": 'api_key = "abcd1234efgh5678ijkl"\n',
        })
        self.assertIn("비밀키", out)

    def test_env_file_is_correct_place_not_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/.env",
            "content": f"ANTHROPIC_API_KEY={self.FAKE_ANTHROPIC}\n",
        })
        self.assertEqual(out, "")

    def test_placeholder_not_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/settings.py",
            "content": 'api_key = "YOUR_API_KEY_GOES_HERE_123"\n',
        })
        self.assertEqual(out, "")

    def test_env_var_read_not_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/settings.py",
            "content": 'api_key = os.environ["ANTHROPIC_API_KEY"]\n'
                       'token = process.env.MY_TOKEN\n',
        })
        self.assertEqual(out, "")

    def test_allow_secret_marker_skipped(self):
        out = self.run_guard("Write", {
            "file_path": "/p/test_client.py",
            "content": f'FAKE = "{self.FAKE_ANTHROPIC}"  # hi-vibe: allow-secret 테스트용\n',
        })
        self.assertEqual(out, "")

    def test_edit_preexisting_secret_not_reflagged(self):
        line = f'key = "{self.FAKE_ANTHROPIC}"\n'
        out = self.run_guard("Edit", {
            "file_path": "/p/svc.py",
            "old_string": line, "new_string": line + "x = 1\n",
        })
        self.assertEqual(out, "")

    def test_swallow_and_secret_reported_together(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": f'key = "{self.FAKE_ANTHROPIC}"\n'
                       "try:\n    go()\nexcept:\n    pass\n",
        })
        self.assertIn("에러 삼킴", out)
        self.assertIn("비밀키", out)


# --- 파일 잠금 동시성 (멀티 터미널 handover 유실 방지) ---
# multiprocessing 자식이 top-level에서 찾을 수 있도록 모듈 레벨에 둔다.
_HOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "hooks", "scripts")


def _locked_prepend(args):
    """다른 프로세스에서 file_lock 하에 handover 항목 하나를 추가한다."""
    root, idx = args
    if _HOOKS_DIR not in sys.path:
        sys.path.insert(0, _HOOKS_DIR)
    import _common as c
    hp = os.path.join(root, "handover.md")
    with c.file_lock(hp):
        c.prepend_entry(hp, f"## entry-{idx}\n\n- body{idx}")


class FileLockTest(TempProject):
    def test_lock_basic_enter_exit(self):
        """정상 진입/종료 + 락 파일 생성 + 락 하 기록 정상."""
        with _common.file_lock(self.handover):
            _common.prepend_entry(self.handover, "## x\n\n- y")
        self.assertTrue(os.path.isfile(self.handover + ".lock"))
        self.assertIn("## x", self.read_handover())

    def test_lock_best_effort_on_bad_path(self):
        """락 파일을 못 만드는 경로여도 예외 없이 yield 되어야(best-effort)."""
        ran = []
        with _common.file_lock("/nonexistent-dir-xyz/handover.md"):
            ran.append(True)
        self.assertEqual(ran, [True])

    def test_concurrent_writes_no_loss(self):
        """여러 프로세스가 동시에 같은 handover에 써도 항목이 유실되지 않는다.
        락이 없으면 read-modify-write race로 일부 항목이 사라진다."""
        import multiprocessing
        n = 16
        with multiprocessing.Pool(4) as pool:
            pool.map(_locked_prepend, [(self.root, i) for i in range(n)])
        text = self.read_handover()
        missing = [i for i in range(n) if f"entry-{i}" not in text]
        self.assertEqual(missing, [], f"유실된 항목: {missing}")


if __name__ == "__main__":
    unittest.main()

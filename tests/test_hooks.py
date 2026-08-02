"""훅 스크립트 동작 검증: _common 유틸, PreCompact 자동 기록,
Stop 알림(세션당 1회), PostToolUse 에러 삼킴 감지.

각 훅의 main(payload)을 직접 호출한다 — run() 래퍼는 모든 예외를
삼키므로(호스트 보호 계약) 테스트에서는 쓰지 않는다.
"""
import io
import json
import os
import shutil
import subprocess
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
import session_start
import stop_nudge


class TempProject(unittest.TestCase):
    """hi-vibe가 init된(= .hi-vibe/ 마커 존재) 임시 프로젝트."""

    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="vibe-hook-test-")
        os.makedirs(os.path.join(self.root, ".hi-vibe"), exist_ok=True)  # init 마커(gate)
        self.handover = os.path.join(self.root, "handover.md")
        with open(self.handover, "w", encoding="utf-8") as f:
            f.write("# Handover — 세션 인수인계\n")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def read_handover(self):
        with open(self.handover, encoding="utf-8") as f:
            return f.read()

    def run_guard(self, tool, tool_input):
        """PostToolUse 가드를 실행하고 stdout(emit 결과)을 돌려준다."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            post_write_guard.main({"cwd": self.root, "tool_name": tool,
                                   "tool_input": tool_input})
        return buf.getvalue()


class CommonTest(TempProject):
    def test_project_gate(self):
        self.assertTrue(_common.project_gate(self.root))  # .hi-vibe/ 있음
        self.assertFalse(_common.project_gate(tempfile.gettempdir()))
        self.assertFalse(_common.project_gate(""))

    def test_gate_ignores_user_own_handover(self):
        """사용자가 자기 목적으로 handover.md만 갖고 있고 .hi-vibe/가 없으면
        gate는 OFF여야 한다 — 남의 handover.md를 hi-vibe 것으로 오판·오염
        하지 않도록. (이번 수정의 핵심)"""
        other = tempfile.mkdtemp(prefix="user-own-")
        try:
            with open(os.path.join(other, "handover.md"), "w", encoding="utf-8") as f:
                f.write("# 내 개인 인수인계 메모\n")
            self.assertFalse(_common.project_gate(other))  # handover.md만으론 gate 안 켜짐
        finally:
            shutil.rmtree(other, ignore_errors=True)

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
                {"type": "tool_use", "name": "MultiEdit",
                 "input": {"file_path": "/p/util.py",
                           "edits": [{"old_string": "a", "new_string": "b"}]}},
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
        # MultiEdit도 수정으로 집계되어야 함 (Bash는 제외)
        self.assertEqual(edited, ["/p/core.py", "/p/util.py"])

    def _transcript_with(self, cmd, output):
        p = os.path.join(self.root, "tt.jsonl")
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"message": {"content": [
                {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}) + "\n")
            f.write(json.dumps({"message": {"content": [
                {"type": "tool_result", "content": output}]}}) + "\n")
        return p

    def test_last_test_result_reads_pass_and_fail(self):
        ok = self._transcript_with("python3 -m unittest discover -s tests",
                                    "Ran 78 tests in 5s\n\nOK")
        self.assertEqual(_common.last_test_result(ok),
                         ("python3 -m unittest discover -s tests", "통과"))
        fail = self._transcript_with("pytest", "2 failed, 5 passed")
        self.assertEqual(_common.last_test_result(fail), ("pytest", "실패 2"))

    def test_records_the_test_command_not_whatever_came_before_it(self):
        """이어 붙인 명령에서 **실제로 돌린 것**을 적는다.

        예전엔 명령 전체의 앞 80자를 적었다. 테스트를 뒤에 붙이는 일이
        흔한데(`python3 - <<'PY' … PY` 다음 줄에 unittest), 그러면 판정은
        뒤를 보고 기록은 앞을 적어 **돌린 적 없는 명령이 handover에 검증
        기록으로 남았다.** 결과("통과")는 맞아서 딱 봐서는 안 이상한 게
        더 나쁘다 — 다음 세션이 그걸 믿는다."""
        cases = [
            ("python3 - <<'PY'\np='README.md'\nPY\n"
             "python3 -m unittest discover -s tests 2>&1 | grep -E \"^OK\"",
             "python3 -m unittest discover -s tests 2>&1"),
            ("cd /repo && pytest -q", "pytest -q"),
            ("ruff check . ; python3 -m pytest tests/ -x", "python3 -m pytest tests/ -x"),
            ("go test ./... | tee out.txt", "go test ./..."),
        ]
        for cmd, expected in cases:
            got = _common.last_test_result(
                self._transcript_with(cmd, "Ran 3 tests in 1s\n\nOK"))
            self.assertEqual(got, (expected, "통과"), f"명령: {cmd!r}")

    def test_plain_command_is_unchanged(self):
        """구간을 자르다 멀쩡한 단독 명령까지 깎으면 안 된다."""
        for cmd in ("pytest", "npm test", "python3 -m unittest discover -s tests"):
            got = _common.last_test_result(
                self._transcript_with(cmd, "Ran 1 test in 0s\n\nOK"))
            self.assertEqual(got, (cmd, "통과"))

    def test_last_test_result_none_when_ambiguous_or_nontest(self):
        # 테스트 명령이 아니면 무시
        self.assertIsNone(_common.last_test_result(
            self._transcript_with("ls -la", "total 8")))
        # 테스트 명령이어도 명확한 결과 신호 없으면 None (의미 판정하지 않음)
        self.assertIsNone(_common.last_test_result(
            self._transcript_with("pytest", "collecting ...")))


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

    def test_records_git_and_test_state(self):
        """git 저장소면 브랜치·변경 요약과, transcript의 명확한 테스트 결과를
        handover에 남긴다 — 다음 세션 재개용 객관적 상태."""
        subprocess.run(["git", "init", "-q"], cwd=self.root)
        with open(os.path.join(self.root, "new.py"), "w") as f:
            f.write("x=1\n")  # untracked = 신규
        tp = os.path.join(self.root, "t.jsonl")
        with open(tp, "w", encoding="utf-8") as f:
            f.write(json.dumps({"message": {"content": [
                {"type": "tool_use", "name": "Bash",
                 "input": {"command": "python3 -m unittest"}}]}}) + "\n")
            f.write(json.dumps({"message": {"content": [
                {"type": "tool_result", "content": "Ran 5 tests\n\nOK"}]}}) + "\n")
        pre_compact.main(self.payload(transcript=tp))
        text = self.read_handover()
        self.assertIn("- Git:", text)
        self.assertIn("master", text)   # 브랜치명
        self.assertIn("신규", text)      # untracked 파일 집계(new.py 등)
        self.assertIn("최근 검증:", text)
        self.assertIn("통과", text)

    def test_no_git_line_outside_repo(self):
        """git 저장소가 아니면 Git 줄을 조용히 생략(fail-open)."""
        pre_compact.main(self.payload())  # self.root는 git init 안 함
        self.assertNotIn("- Git:", self.read_handover())


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

    def test_summary_shown_once_per_session(self):
        # git 저장소가 아니라 리뷰 범위를 못 구하는 상황 = 막지 않고 요약만.
        transcript = self.make_transcript(["/p/core.py"])
        first = self.run_nudge(transcript)
        self.assertIn("검사", first)
        self.assertIn("This session", first)  # 한/영 병기 (외국인 사용자용)
        self.assertNotIn("block", first)      # 막을 근거가 없으면 안 막는다
        second = self.run_nudge(transcript)   # 같은 세션에선 침묵
        self.assertEqual(second, "")

    def test_session_summary_counts_writes_and_catches(self):
        # 코드 쓰기 2회 + 어시스턴트가 남긴 👋 마커 1개 → "2회 검사 · 👋 1건".
        transcript = os.path.join(self.root, "t2.jsonl")
        with open(transcript, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Write", "input": {"file_path": "/p/a.py"}}]}}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "text", "text": "고쳤어요. 👋 hi-vibe가 방금 빈 except를 잡았어요."}]}}) + "\n")
            f.write(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Edit", "input": {"file_path": "/p/b.py"}}]}}) + "\n")
        out = self.run_nudge(transcript, sid="sum1")
        self.assertIn("2회", out)
        self.assertIn("👋 1건", out)

    def test_session_summary_zero_catches_still_shown(self):
        # 잡은 게 없어도 "검사 N회 · 0건"으로 조용히 돌고 있었음을 증명한다.
        out = self.run_nudge(self.make_transcript(["/p/core.py"]), sid="sum2")
        self.assertIn("검사", out)
        self.assertIn("0건", out)

    def test_silent_for_doc_only_edits(self):
        transcript = self.make_transcript(["/p/README.md"])
        self.assertEqual(self.run_nudge(transcript, sid="s3"), "")

    def test_flag_dir_pruned_when_over_cap(self):
        """세션당 1개씩 쌓이는 .nudged 플래그가 상한을 넘으면 오래된 것부터
        정리돼야 한다 (무한 누적 방지)."""
        flag_dir = os.path.join(self.root, ".hi-vibe", "state")
        os.makedirs(flag_dir, exist_ok=True)
        for i in range(stop_nudge.MAX_FLAGS + 5):
            with open(os.path.join(flag_dir, f"old{i}.nudged"), "w") as f:
                f.write("nudged\n")
        transcript = self.make_transcript(["/p/core.py"])
        self.run_nudge(transcript, sid="fresh-session")  # 새 플래그 1개 추가 + 정리
        remaining = [f for f in os.listdir(flag_dir) if f.endswith(".nudged")]
        self.assertLessEqual(len(remaining), stop_nudge.MAX_FLAGS)


class StopBlockTest(TempProject):
    """안 받은 리뷰가 있으면 안내가 아니라 실행으로 넘긴다(decision: block).

    안내는 무시된다는 게 이 변경의 이유이므로, "막는다"와 "두 번은 안 막는다"를
    둘 다 고정한다 — 후자가 깨지면 잔소리 훅이 되어 플러그인이 지워진다.
    """

    def setUp(self):
        super().setUp()
        for args in (["init", "-q"], ["config", "user.email", "t@t.t"],
                     ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.root, check=True,
                           capture_output=True, text=True)
        with open(os.path.join(self.root, "feat.py"), "w", encoding="utf-8") as f:
            f.write("def a():\n    return 1\n")

    def run_nudge(self, sid="b1"):
        transcript = os.path.join(self.root, "t.jsonl")
        with open(transcript, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Edit",
                 "input": {"file_path": "feat.py"}}]}}) + "\n")
        buf = io.StringIO()
        with redirect_stdout(buf):
            stop_nudge.main({"cwd": self.root, "session_id": sid,
                             "transcript_path": transcript})
        return buf.getvalue()

    def test_blocks_when_change_is_unreviewed(self):
        out = json.loads(self.run_nudge())
        self.assertEqual(out["decision"], "block")
        self.assertIn("feat.py", out["reason"])
        self.assertIn("review", out["reason"])

    def test_does_not_block_twice_for_the_same_change(self):
        self.assertIn("block", self.run_nudge())
        second = self.run_nudge(sid="b2")   # 사용자가 넘겼어도 다시 막지 않는다
        self.assertNotIn("block", second)

    def test_blocks_again_after_code_changes(self):
        self.assertIn("block", self.run_nudge())
        with open(os.path.join(self.root, "feat.py"), "w", encoding="utf-8") as f:
            f.write("def a():\n    return 2\n")   # 내용이 실제로 바뀌면
        self.assertIn("block", self.run_nudge(sid="b3"))

    def test_no_block_once_reviewed(self):
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "skills", "write-gate", "scripts"))
        import review_scope
        review_scope.cmd_mark(self.root, ["feat.py"])
        self.assertNotIn("block", self.run_nudge(sid="b4"))

    def test_fails_open_when_scope_unavailable(self):
        """범위 계산이 실패하면 막지 않는다 — 훅이 호스트를 붙잡으면 안 된다."""
        original = stop_nudge.REVIEW_SCOPE
        stop_nudge.REVIEW_SCOPE = os.path.join(self.root, "does-not-exist.py")
        try:
            self.assertNotIn("block", self.run_nudge(sid="b5"))
        finally:
            stop_nudge.REVIEW_SCOPE = original


class HeartbeatTest(TempProject):
    """훅은 조용히 실패한다 — 살아있을 때 흔적을 남겨야 스킬 층이 죽음을
    알아챌 수 있다. 흔적이 안 남으면 이 감지 경로가 통째로 무의미해진다."""

    def test_hooks_record_that_they_ran(self):
        session_start.main({"cwd": self.root, "source": "startup"})
        beats = _common.read_heartbeat(self.root)
        self.assertIn("SessionStart", beats)
        self.assertGreater(beats["SessionStart"], 0)

    def test_multiple_hooks_accumulate(self):
        """한 훅이 다른 훅의 기록을 지우면 안 된다 — 어느 훅이 죽었는지
        구분할 수 없게 된다."""
        session_start.main({"cwd": self.root, "source": "startup"})
        self.run_guard("Write", {"file_path": os.path.join(self.root, "x.py"),
                                 "content": "x = 1\n"})
        beats = _common.read_heartbeat(self.root)
        self.assertIn("SessionStart", beats)
        self.assertIn("PostToolUse", beats)

    def test_never_creates_the_marker(self):
        """CI 캐시와 같은 함정 — 흔적을 남기겠다고 `.hi-vibe/`를 만들면
        init한 적 없는 저장소에 훅이 켜진다."""
        other = tempfile.mkdtemp(prefix="vibe-noinit-hb-")
        try:
            _common.touch_heartbeat(other, "SessionStart")
            self.assertFalse(os.path.isdir(os.path.join(other, ".hi-vibe")))
        finally:
            shutil.rmtree(other, ignore_errors=True)

    def test_optout_turns_the_gate_off(self):
        """마커가 있어도 opt-out이면 훅은 꺼져야 한다 — "여기선 안 쓸래"를
        기록할 곳이 없으면 계속 물어보게 된다."""
        self.assertTrue(_common.project_gate(self.root))
        with open(os.path.join(self.root, ".hi-vibe", "optout"), "w") as f:
            f.write("")
        self.assertFalse(_common.project_gate(self.root))


class GateSuggestionTest(TempProject):
    """gate를 칠 때 리모트가 없었으면 CI는 목록에서 빠진다. 그 판단이 한 번
    내려지고 다시 안 보이는 게 문제였다 — 나중에 GitHub에 붙여도 아무도
    알려주지 않았다."""

    def setUp(self):
        super().setUp()
        for args in (["init", "-q"], ["config", "user.email", "t@t.t"],
                     ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.root, check=True,
                           capture_output=True, text=True)
        self._ci = _common.ci_health
        _common.ci_health = lambda cwd, **kw: None   # CI 실패 경고와 분리

    def tearDown(self):
        _common.ci_health = self._ci
        super().tearDown()

    def add_remote(self):
        subprocess.run(["git", "remote", "add", "origin",
                        "https://github.com/x/y.git"], cwd=self.root,
                       check=True, capture_output=True, text=True)

    def start(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            session_start.main({"cwd": self.root, "source": "startup"})
        return buf.getvalue()

    def test_silent_without_a_remote(self):
        """GitHub에 안 올리는 프로젝트엔 CI가 돌 자리가 없다 — 권하면 소음."""
        self.assertNotIn("gate", self.start())

    def test_suggests_once_after_remote_is_added(self):
        self.add_remote()
        self.assertIn("gate", self.start())
        self.assertNotIn("gate", self.start())   # 두 번째부턴 침묵

    def test_silent_when_guard_already_installed(self):
        self.add_remote()
        wf = os.path.join(self.root, ".github", "workflows")
        os.makedirs(wf, exist_ok=True)
        with open(os.path.join(wf, "vibe-guards.yml"), "w") as f:
            f.write("name: vibe-guards\n")
        self.assertNotIn("gate", self.start())


class CiHealthTest(TempProject):
    """연속 실패 계산 — 여기가 틀리면 잔소리가 되거나(과다) 죽은 관문을
    놓친다(과소). 둘 다 이 기능을 무의미하게 만든다."""

    def setUp(self):
        super().setUp()
        for args in (["init", "-q"], ["config", "user.email", "t@t.t"],
                     ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.root, check=True,
                           capture_output=True, text=True)
        with open(os.path.join(self.root, "a.txt"), "w") as f:
            f.write("x\n")
        for args in (["add", "-A"], ["commit", "-qm", "init"]):
            subprocess.run(["git", *args], cwd=self.root, check=True,
                           capture_output=True, text=True)
        self._original = _common._run_gh_json

    def tearDown(self):
        _common._run_gh_json = self._original
        super().tearDown()

    def fake_runs(self, runs):
        _common._run_gh_json = lambda args, cwd: runs

    def run_health(self):
        # 캐시가 이전 케이스를 물고 오지 않도록 매번 지운다.
        cache = os.path.join(self.root, ".hi-vibe", "state", "ci.json")
        if os.path.isfile(cache):
            os.remove(cache)
        return _common.ci_health(self.root)

    @staticmethod
    def a_run(conclusion, date="2026-07-27", name="vibe-guards"):
        return {"status": "completed", "conclusion": conclusion,
                "createdAt": date + "T00:00:00Z", "workflowName": name}

    def test_counts_consecutive_failures_until_a_success(self):
        self.fake_runs([self.a_run("failure"), self.a_run("failure"),
                        self.a_run("success", "2026-07-23"), self.a_run("failure")])
        ci = self.run_health()
        self.assertEqual(ci["failures"], 2)          # 성공 뒤의 실패는 안 센다
        self.assertEqual(ci["last_success"], "2026-07-23")
        self.assertEqual(ci["workflow"], "vibe-guards")

    def test_returns_none_when_latest_is_green(self):
        self.fake_runs([self.a_run("success"), self.a_run("failure")])
        self.assertIsNone(self.run_health())

    def test_in_progress_run_does_not_break_the_streak(self):
        """도는 중인 실행은 판정 보류 — 아직 결과가 없는 걸 성공으로 쳐서
        죽은 관문을 놓치면 안 된다."""
        pending = dict(self.a_run("failure"), status="in_progress", conclusion=None)
        self.fake_runs([pending, self.a_run("failure"), self.a_run("failure")])
        self.assertEqual(self.run_health()["failures"], 2)

    def test_cancelled_run_stops_the_streak(self):
        """취소·스킵은 '실패'가 아니다 — 실패로 세면 없는 문제를 만든다."""
        self.fake_runs([self.a_run("failure"), self.a_run("cancelled"),
                        self.a_run("failure")])
        self.assertEqual(self.run_health()["failures"], 1)

    def test_returns_none_when_gh_unavailable(self):
        self.fake_runs(None)
        self.assertIsNone(self.run_health())

    def test_never_creates_the_hi_vibe_marker(self):
        """`.hi-vibe/`는 캐시 폴더가 아니라 **hi-vibe를 켜는 마커**다. 캐시를
        쓰겠다고 이걸 만들면 init한 적 없는 저장소에 훅이 돌기 시작한다."""
        other = tempfile.mkdtemp(prefix="vibe-noinit-ci-")
        try:
            for args in (["init", "-q"], ["config", "user.email", "t@t.t"],
                         ["config", "user.name", "t"]):
                subprocess.run(["git", *args], cwd=other, check=True,
                               capture_output=True, text=True)
            with open(os.path.join(other, "a.txt"), "w") as f:
                f.write("x\n")
            for args in (["add", "-A"], ["commit", "-qm", "init"]):
                subprocess.run(["git", *args], cwd=other, check=True,
                               capture_output=True, text=True)
            self.fake_runs([self.a_run("failure"), self.a_run("failure")])
            _common.ci_health(other)
            self.assertFalse(os.path.isdir(os.path.join(other, ".hi-vibe")),
                             "init 안 한 저장소에 마커를 만들었다")
        finally:
            shutil.rmtree(other, ignore_errors=True)

    def test_result_is_cached(self):
        self.fake_runs([self.a_run("failure"), self.a_run("failure")])
        self.assertEqual(self.run_health()["failures"], 2)
        calls = []
        _common._run_gh_json = lambda args, cwd: calls.append(1) or []
        self.assertEqual(_common.ci_health(self.root)["failures"], 2)  # 캐시 적중
        self.assertEqual(calls, [], "캐시가 있는데 gh를 다시 불렀다")


class SessionStartTest(TempProject):
    """SessionStart 주입 — 한때 유일하게 테스트가 없던 훅."""

    def run_start(self, source):
        buf = io.StringIO()
        with redirect_stdout(buf):
            session_start.main({"cwd": self.root, "source": source})
        return buf.getvalue()

    def test_startup_injects_charter(self):
        out = self.run_start("startup")
        self.assertIn("hi-vibe 규율", out)

    def test_startup_injects_context_tip(self):
        """세션 시작에 컨텍스트 관리 팁(/compact 권유)이 한 줄 주입돼야 한다 (#4)."""
        out = self.run_start("startup")
        self.assertIn("/compact", out)

    def test_ci_warning_shown_when_guard_is_dead(self):
        """세워둔 관문이 죽으면 세션 첫머리에 알려야 한다 — GitHub 알림은
        쌓이면 신호가 안 되므로(47/60 실패가 나흘 방치된 실사례)."""
        original = _common.ci_health
        _common.ci_health = lambda cwd, **kw: {
            "failures": 12, "workflow": "vibe-guards",
            "last_success": "2026-07-23", "branch": "main"}
        try:
            out = self.run_start("startup")
        finally:
            _common.ci_health = original
        self.assertIn("vibe-guards", out)
        self.assertIn("12", out)
        self.assertIn("2026-07-23", out)

    def test_single_ci_failure_is_not_nagged(self):
        """1회 실패는 흔하다(일시 장애·재시도). 매번 경고하면 잔소리가 되고,
        잔소리는 무시된다 — 이 훅을 만든 이유와 정반대가 된다."""
        original = _common.ci_health
        _common.ci_health = lambda cwd, **kw: {
            "failures": 1, "workflow": "vibe-guards",
            "last_success": "2026-07-27", "branch": "main"}
        try:
            out = self.run_start("startup")
        finally:
            _common.ci_health = original
        self.assertNotIn("vibe-guards", out)

    def test_ci_check_failure_is_silent(self):
        """gh가 없거나 오프라인이면 조용히 생략한다 — 세션 시작을 붙잡는 것이
        CI 상태를 아는 것보다 나쁘다 (fail-open)."""
        original = _common.ci_health
        _common.ci_health = lambda cwd, **kw: None
        try:
            out = self.run_start("startup")
        finally:
            _common.ci_health = original
        self.assertIn("hi-vibe 규율", out)   # 나머지 주입은 정상 동작
        self.assertNotIn("연속", out)

    def test_clear_injects_charter_like_startup(self):
        """/clear 직후는 컨텍스트가 통째로 사라진 순간 — 규율 재주입이 가장
        필요한데 예전엔 matcher에 clear가 없어 훅이 안 돌았다 (회귀 버그)."""
        out = self.run_start("clear")
        self.assertIn("hi-vibe 규율", out)

    def test_compact_injects_handover_entry(self):
        _common.prepend_entry(self.handover, "## 2026-01-02 00:00\n\n- 직전 작업 맥락")
        out = self.run_start("compact")
        self.assertIn("직전 작업 맥락", out)

    def test_gate_blocks_uninitialized_project(self):
        other = tempfile.mkdtemp(prefix="vibe-noinit-ss-")
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                session_start.main({"cwd": other, "source": "startup"})
            self.assertEqual(buf.getvalue(), "")
        finally:
            shutil.rmtree(other, ignore_errors=True)


class PostWriteGuardTest(TempProject):

    def test_write_with_bare_except_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": "try:\n    fetch()\nexcept:\n    pass\n",
        })
        self.assertIn("에러 삼킴", out)

    def test_auto_catch_emits_wave_marker(self):
        # 훅이 명령어 없이 자동으로 잡으면, 응답 끝에 👋 마커를 남기라고 지시한다.
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": "try:\n    fetch()\nexcept:\n    pass\n",
        })
        self.assertIn("👋 hi-vibe", out)

    def test_swallow_warning_is_on_demand(self):
        """에러 삼킴 경고는 짧게 짚고, '왜'는 사용자가 물어볼 때만 (#3 온디맨드)."""
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": "try:\n    fetch()\nexcept:\n    pass\n",
        })
        self.assertIn("한 줄로", out)
        self.assertIn("물어볼 때만", out)

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

    def test_js_allow_swallow_marker_skipped(self):
        """JS/TS의 allow-swallow 주석은 매치(`}`) 밖에 달리므로, 매치가 아니라
        그 줄 전체에서 마커를 찾아야 한다 — 안 그러면 플러그인이 직접 안내한
        해결법(`catch(e){} // allow-swallow`)이 JS에서 안 먹혔다 (회귀 버그)."""
        out = self.run_guard("Write", {
            "file_path": "/p/app.ts",
            "content": "try { go(); } catch (e) {} // hi-vibe: allow-swallow — 무해\n",
        })
        self.assertEqual(out, "")

    def test_js_promise_catch_allow_marker_skipped(self):
        out = self.run_guard("Write", {
            "file_path": "/p/app.js",
            "content": "fetchData().catch(() => {}); // hi-vibe: allow-swallow\n",
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

    def test_hardcoded_api_key_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": f'client = Client(key="{self.FAKE_ANTHROPIC}")\n',
        })
        self.assertIn("비밀키", out)

    def test_secret_warning_always_explains_why(self):
        """비밀키 경고는 '왜 위험한지' 한 줄을 항상 포함해야 한다 (#3)."""
        out = self.run_guard("Write", {
            "file_path": "/p/svc.py",
            "content": f'key = "{self.FAKE_ANTHROPIC}"\n',
        })
        self.assertIn("왜 위험한지", out)

    def test_aws_key_in_config_json_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/config.json",
            "content": '{"aws_access_key_id": "%s"}\n' % self.FAKE_AWS,
        })
        self.assertIn("비밀키", out)

    def test_generic_secret_assignment_flagged(self):
        out = self.run_guard("Write", {
            "file_path": "/p/settings.py",
            "content": 'api_key = "abcd1234efgh5678ijkl"\n',  # hi-vibe: allow-secret
        })
        self.assertIn("비밀키", out)

    def test_secret_swap_same_count_flagged(self):
        """기존 시크릿 1개를 다른 시크릿 1개로 교체하면 개수는 1→1로 같아도
        새 값이라 경고해야 한다 — 개수 비교가 놓치던 실제 탐지 공백(감사 재현)."""
        out = self.run_guard("Edit", {
            "file_path": "/p/svc.py",
            "old_string": f'key = "{self.FAKE_ANTHROPIC}"\n',
            "new_string": f'key = "{self.FAKE_AWS}"\n',
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

    def test_angle_bracket_placeholder_not_flagged(self):
        """`<YOUR_KEY>` 류 자리표시자는 계속 억제돼야 한다."""
        out = self.run_guard("Write", {
            "file_path": "/p/settings.py",
            "content": 'token = "<REPLACE_WITH_YOUR_TOKEN>"\n',
        })
        self.assertEqual(out, "")

    def test_real_key_on_jsx_line_still_flagged(self):
        """JSX(`<div>`)나 비교(`a < b`)가 섞인 줄이라도 진짜 키는 잡아야 한다 —
        예전엔 맨 `<` 하나가 오탐 억제라서 진짜 키를 삼켰다 (회귀 버그)."""
        out = self.run_guard("Write", {
            "file_path": "/p/App.tsx",
            "content": f'const el = <div data-key="{self.FAKE_ANTHROPIC}" />;\n',
        })
        self.assertIn("비밀키", out)

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

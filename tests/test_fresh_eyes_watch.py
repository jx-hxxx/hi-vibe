"""리뷰는 도는데 **fresh-eyes만 빠지는 것**을 기계가 알아채는지.

2026-08-07 실사용: 한 세션이 **하루 종일** 서브에이전트 호출이 막힌 채
돌았다(세션 설정이 Agent 도구를 금지). 체크리스트는 매번 돌았고 리뷰
보고도 정상으로 나갔는데, 설계 검토는 한 번도 안 돌았다. 그런데 그 사실이
**어디에도 안 남았다** — 훅이 죽으면 heartbeat가 잡는데, 에이전트가 죽는
건 아무도 안 보고 있었다.

핵심 설계 결정 두 가지:

1. **AI에게 물어보지 않는다.** `write-gate`는 "생략했으면 한 줄로 밝혀라"고
   지시하지만 그건 AI 주의력에 기대는 층이고, 정확히 그 층이 조용히 빠진
   사건이었다. 호출은 트랜스크립트에 `subagent_type`으로 남으므로 훅이 센다.
2. **읽은 위치를 기억하고 이어 읽는다.** 첫 구현은 매번 전체를 세고 누계와
   비교했는데, 전체 읽기가 `tail_lines`(끝 512KB)라 긴 세션에서는 예전
   호출이 창 밖으로 밀려 **누계가 줄어든 것처럼** 보였다. 그러면 델타가
   멈춰 **긴 세션일수록 안 센다.** 실제 16MB 세션에 돌려 0회가 나와서 잡았다.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "hooks", "scripts"))
import _common                                    # noqa: E402

STOP = os.path.join(REPO, "hooks", "scripts", "stop_nudge.py")
DOCTOR = os.path.join(REPO, "scripts", "doctor.py")
MARK_CMD = ('python3 "/plugins/hi-vibe/skills/write-gate/scripts/'
            'review_scope.py" mark backend/live.py --root .')


def rec(*blocks):
    return json.dumps({"type": "assistant",
                       "message": {"role": "assistant", "content": list(blocks)}})


def agent(kind):
    return {"type": "tool_use", "name": "Agent",
            "input": {"subagent_type": kind, "description": "review"}}


def bash(cmd):
    return {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}


def filler(n):
    """트랜스크립트를 실제처럼 부풀리는 잡음 (도구 호출이 아닌 텍스트)."""
    return [rec({"type": "text", "text": "x" * 900}) for _ in range(n)]


def write_lines(path, lines, mode="w"):
    with open(path, mode, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


class CountingTest(unittest.TestCase):
    """무엇을 세고 무엇을 안 세는지."""

    def setUp(self):
        self._d = tempfile.TemporaryDirectory(prefix="vibe-fe-")
        self.t = os.path.join(self._d.name, "t.jsonl")

    def tearDown(self):
        self._d.cleanup()

    def count(self, offset=0):
        return _common.review_activity(self.t, offset)

    def test_counts_fresh_eyes_and_marks(self):
        write_lines(self.t, [
            rec(agent("hi-vibe:fresh-eyes")),
            rec(bash(MARK_CMD)),
            rec(agent("hi-vibe:fresh-eyes"), bash(MARK_CMD)),
        ])
        fe, mk, _ = self.count()
        self.assertEqual((fe, mk), (2, 2))

    def test_other_agents_do_not_count(self):
        """`proof-eyes`는 check가 쓰는 다른 에이전트다 — 리뷰의 절반이 아니다."""
        write_lines(self.t, [rec(agent("hi-vibe:proof-eyes")),
                             rec(agent("general-purpose"))])
        self.assertEqual(self.count()[0], 0)

    def test_commit_message_saying_mark_is_not_a_mark(self):
        """실제 트랜스크립트에 있던 오탐 후보 — 커밋 메시지·echo 속 `mark`."""
        write_lines(self.t, [
            rec(bash('git commit -m "fix: mark stale rows"')),
            rec(bash('git status && echo "--- mark ---"')),
        ])
        self.assertEqual(self.count()[1], 0)

    def test_mark_survives_being_chained(self):
        """실사용에서 mark는 보통 `&&`로 다른 명령 뒤에 붙어 온다."""
        write_lines(self.t, [rec(bash('git status --short && ' + MARK_CMD))])
        self.assertEqual(self.count()[1], 1)

    def test_broken_lines_do_not_crash(self):
        write_lines(self.t, ["{not json", rec(agent("hi-vibe:fresh-eyes"))])
        self.assertEqual(self.count()[0], 1)

    def test_resumes_from_offset_and_does_not_recount(self):
        write_lines(self.t, [rec(agent("hi-vibe:fresh-eyes"))])
        fe, _mk, off = self.count()
        self.assertEqual(fe, 1)
        self.assertEqual(self.count(off)[0], 0, "같은 줄을 또 셌다")
        write_lines(self.t, [rec(agent("hi-vibe:fresh-eyes"))], mode="a")
        self.assertEqual(self.count(off)[0], 1)

    def test_survives_a_long_transcript(self):
        """**이게 실측으로 잡힌 결함이다.** 끝 512KB만 읽으면 앞이 안 보인다.

        16MB짜리 실제 세션에 돌렸더니 fresh-eyes 0회가 나왔다. 호출이 창
        밖에 있었기 때문이다."""
        write_lines(self.t, [rec(agent("hi-vibe:fresh-eyes"))] + filler(800))
        self.assertGreater(os.path.getsize(self.t), 512 * 1024,
                           "이 검사는 tail 창보다 커야 의미가 있다")
        self.assertEqual(self.count()[0], 1, "창 밖의 호출을 놓쳤다")

    def test_half_written_line_is_not_consumed(self):
        """훅이 기록 도중에 돌 수 있다 — 잘린 줄을 삼키면 그 호출은 영영 유실."""
        with open(self.t, "w", encoding="utf-8") as f:
            f.write(rec(agent("hi-vibe:fresh-eyes")) + "\n")
            f.write(rec(agent("hi-vibe:fresh-eyes"))[:40])   # 미완성
        fe, _mk, off = self.count()
        self.assertEqual(fe, 1)
        with open(self.t, "a", encoding="utf-8") as f:       # 나머지가 마저 쓰임
            f.write(rec(agent("hi-vibe:fresh-eyes"))[40:] + "\n")
        self.assertEqual(self.count(off)[0], 1, "잘렸던 줄을 놓쳤다")


class AccumulationTest(unittest.TestCase):
    """훅이 매 턴 도는 상황을 그대로 흉내 낸다."""

    def setUp(self):
        self._d = tempfile.TemporaryDirectory(prefix="vibe-fe-acc-")
        self.root = self._d.name
        os.makedirs(os.path.join(self.root, ".hi-vibe"))
        self.t = os.path.join(self.root, "t.jsonl")

    def tearDown(self):
        self._d.cleanup()

    def tick(self, sid="sid-1"):
        """Stop 훅 한 번 = 위치 읽기 → 새로 세기 → 누계에 더하기."""
        off = _common.agent_offset(self.root, sid)
        fe, mk, off2 = _common.review_activity(self.t, off)
        _common.note_agent_activity(self.root, sid, fe, mk, off2)

    def totals(self):
        d = _common.read_agent_activity(self.root)
        return d.get("fresh_eyes", 0), d.get("marks", 0)

    def test_repeated_ticks_do_not_double_count(self):
        """이걸 놓치면 턴이 늘수록 숫자가 부풀어 진단이 거짓말이 된다."""
        write_lines(self.t, [rec(agent("hi-vibe:fresh-eyes"), bash(MARK_CMD))])
        for _ in range(6):
            self.tick()
        self.assertEqual(self.totals(), (1, 1))

    def test_appending_over_many_turns_accumulates(self):
        write_lines(self.t, [rec(bash(MARK_CMD))])
        self.tick()
        for _ in range(3):
            write_lines(self.t, [rec(agent("hi-vibe:fresh-eyes"), bash(MARK_CMD))],
                        mode="a")
            self.tick()
        self.assertEqual(self.totals(), (3, 4))

    def test_separate_sessions_accumulate(self):
        write_lines(self.t, [rec(agent("hi-vibe:fresh-eyes"))])
        self.tick("sid-1")
        self.tick("sid-2")     # 다른 세션은 자기 위치가 0이라 처음부터 센다
        self.assertEqual(self.totals()[0], 2)

    def test_session_markers_are_pruned(self):
        write_lines(self.t, [rec(bash(MARK_CMD))])
        for i in range(_common.AGENT_SESSIONS_KEEP + 8):
            self.tick(f"sid-{i}")
        seen = _common.read_agent_activity(self.root)["sessions"]
        self.assertLessEqual(len(seen), _common.AGENT_SESSIONS_KEEP)

    def test_does_nothing_without_the_marker(self):
        """opt-in 원칙 — 훅이 `.hi-vibe/`를 만들면 안 켠 프로젝트에서 켜진다."""
        with tempfile.TemporaryDirectory(prefix="vibe-fe-none-") as other:
            _common.note_agent_activity(other, "sid", 1, 1, 10)
            self.assertFalse(os.path.exists(os.path.join(other, ".hi-vibe")))


class HookAndDoctorTest(unittest.TestCase):
    """훅을 실제로 돌려서 파일이 생기는지, doctor가 그걸 읽는지."""

    def setUp(self):
        self._d = tempfile.TemporaryDirectory(prefix="vibe-fe-e2e-")
        self.root = self._d.name
        os.makedirs(os.path.join(self.root, ".hi-vibe"))
        # 실제 프로젝트는 git 저장소다 — 아니면 review_scope가 다른 길로 샌다.
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        self.t = os.path.join(self.root, "t.jsonl")

    def tearDown(self):
        self._d.cleanup()

    def run_stop(self, sid="s1"):
        subprocess.run(
            [sys.executable, STOP],
            input=json.dumps({"cwd": self.root, "session_id": sid,
                              "transcript_path": self.t}),
            capture_output=True, text=True, timeout=60)

    def doctor_line(self):
        r = subprocess.run([sys.executable, DOCTOR, "--root", self.root],
                           capture_output=True, text=True, timeout=90)
        for ln in r.stdout.splitlines():
            if "fresh-eyes" in ln:
                return ln
        return ""

    def test_hook_records_and_doctor_warns_when_only_checklist_runs(self):
        write_lines(self.t, [rec(bash(MARK_CMD)) for _ in range(4)])
        self.run_stop()
        data = _common.read_agent_activity(self.root)
        self.assertEqual(data.get("marks"), 4, "훅이 mark를 기록하지 않았다")
        self.assertEqual(data.get("fresh_eyes"), 0)
        line = self.doctor_line()
        self.assertIn("⚠️", line, f"경고가 안 났다: {line}")
        self.assertIn("4회 중 0회", line)

    def test_running_the_hook_twice_does_not_inflate(self):
        write_lines(self.t, [rec(bash(MARK_CMD)) for _ in range(4)])
        self.run_stop()
        self.run_stop()
        self.assertEqual(_common.read_agent_activity(self.root).get("marks"), 4)

    def test_doctor_is_quiet_when_fresh_eyes_runs(self):
        write_lines(self.t, [rec(agent("hi-vibe:fresh-eyes"), bash(MARK_CMD))
                             for _ in range(4)])
        self.run_stop()
        line = self.doctor_line()
        self.assertIn("✅", line, f"멀쩡한데 경고가 났다: {line}")

    def test_doctor_holds_judgment_on_too_few_reviews(self):
        """리뷰 한두 번 만에 단정하면 늑대소년이 된다."""
        write_lines(self.t, [rec(bash(MARK_CMD))])
        self.run_stop()
        self.assertIn("✅", self.doctor_line())


if __name__ == "__main__":
    unittest.main()

"""`/clear`와 세션 종료 때도 handover가 남는지 지킨다.

이게 없던 동안 자동 기록은 **compact 직전 하나뿐**이었다. `/clear`는 대화를
요약해 이어가는 게 아니라 통째로 버리는 것이라 정작 기록이 제일 필요한
쪽인데 아무것도 안 남았다. 여기서 지키는 것은 세 가지다:

  1. 건질 게 있으면 남긴다 (기능)
  2. 빈 세션에는 아무것도 안 쓴다 (`/clear`는 열자마자 칠 수 있다)
  3. 방금 compact이 남긴 것을 또 쓰지 않는다 (compact → clear 흐름)

2·3이 없으면 기능이 도는 대신 handover가 쓰레기로 찬다. 그러면 사람이
안 읽고, 안 읽히는 기록은 없는 것과 같다.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOKS = os.path.join(REPO, "hooks", "scripts")
sys.path.insert(0, HOOKS)

import _common  # noqa: E402

SESSION_END = os.path.join(HOOKS, "session_end.py")
PRE_COMPACT = os.path.join(HOOKS, "pre_compact.py")


def _transcript(entries):
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")
    return path


def _user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def _edit(path):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Edit", "input": {"file_path": path}}]}}


def _run(script, payload):
    return subprocess.run([sys.executable, script], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=30)


class SessionEndHandoverTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory(prefix="vibe-sessend-")
        self.root = self._dir.name
        os.makedirs(os.path.join(self.root, ".hi-vibe"))
        self.tr = None

    def tearDown(self):
        if self.tr and os.path.exists(self.tr):
            os.unlink(self.tr)
        self._dir.cleanup()

    def _handover(self):
        path = os.path.join(self.root, "handover.md")
        if not os.path.isfile(path):
            return ""
        with open(path, encoding="utf-8") as f:
            return f.read()

    def _payload(self, reason="clear", sid="abc12345"):
        return {"cwd": self.root, "transcript_path": self.tr or "",
                "hook_event_name": "SessionEnd", "reason": reason, "session_id": sid}

    def test_clear_leaves_a_record(self):
        """핵심 — /clear로 버려도 무엇을 하던 중이었는지 남는다."""
        self.tr = _transcript([_user("로그인 폼 만들어줘"), _edit("app/login.py")])
        r = _run(SESSION_END, self._payload())
        self.assertEqual(r.returncode, 0, r.stderr)
        text = self._handover()
        self.assertIn("/clear 직전", text)
        self.assertIn("로그인 폼", text)
        self.assertIn("app/login.py", text)

    def test_exit_leaves_a_record_with_its_own_label(self):
        """창을 닫고 나가는 것도 같은 구멍이었다 — 제목만 다르다."""
        self.tr = _transcript([_user("차트 색 바꿔줘"), _edit("web/chart.js")])
        _run(SESSION_END, self._payload(reason="prompt_input_exit"))
        text = self._handover()
        self.assertIn("세션 종료", text)
        self.assertNotIn("/clear", text)

    def test_empty_session_writes_nothing(self):
        """열자마자 /clear를 쳐도 빈 항목이 쌓이면 안 된다.

        compact은 대화가 길어야 일어나지만 `/clear`는 아무 때나 칠 수 있다.
        PreCompact를 그대로 붙였으면 여기서 빈 항목이 남았을 것이다."""
        self.tr = _transcript([])
        r = _run(SESSION_END, self._payload())
        self.assertEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(self.root, "handover.md")),
                         "빈 세션인데 handover를 만들었다")

    def test_compact_then_clear_writes_once(self):
        """`/compact` 하고 바로 `/clear`를 치는 흐름 — 두 번 남기지 않는다."""
        self.tr = _transcript([_user("결제 붙여줘"), _edit("pay.py")])
        _run(PRE_COMPACT, {"cwd": self.root, "transcript_path": self.tr,
                           "hook_event_name": "PreCompact", "trigger": "manual",
                           "session_id": "abc12345"})
        _run(SESSION_END, self._payload())
        self.assertEqual(self._handover().count("결제 붙여줘"), 1,
                         "compact과 clear가 같은 내용을 두 번 남겼다")

    def test_more_work_after_compact_is_recorded(self):
        """중복을 막다가 **진짜 새 작업**까지 버리면 그게 더 나쁘다."""
        self.tr = _transcript([_user("결제 붙여줘"), _edit("pay.py")])
        _run(PRE_COMPACT, {"cwd": self.root, "transcript_path": self.tr,
                           "hook_event_name": "PreCompact", "trigger": "manual",
                           "session_id": "abc12345"})
        os.unlink(self.tr)
        self.tr = _transcript([_user("결제 붙여줘"), _edit("pay.py"),
                               _user("환불도"), _edit("refund.py")])
        _run(SESSION_END, self._payload())
        self.assertIn("refund.py", self._handover(),
                      "compact 뒤에 한 일이 사라졌다")

    def test_other_session_is_not_deduped(self):
        """세션이 다르면 남겨야 한다 — 표식은 세션마다다."""
        self.tr = _transcript([_user("첫 세션"), _edit("a.py")])
        _run(PRE_COMPACT, {"cwd": self.root, "transcript_path": self.tr,
                           "hook_event_name": "PreCompact", "trigger": "auto",
                           "session_id": "session-one"})
        os.unlink(self.tr)
        self.tr = _transcript([_user("둘째 세션"), _edit("b.py")])
        _run(SESSION_END, self._payload(sid="session-two"))
        self.assertIn("둘째 세션", self._handover())

    def test_project_gate(self):
        """`.hi-vibe/`가 없는 폴더에는 아무것도 만들지 않는다 (opt-in)."""
        self.tr = _transcript([_user("뭐 해줘"), _edit("x.py")])
        with tempfile.TemporaryDirectory(prefix="vibe-nogate-") as other:
            r = _run(SESSION_END, {"cwd": other, "transcript_path": self.tr,
                                   "hook_event_name": "SessionEnd", "reason": "clear",
                                   "session_id": "s"})
            self.assertEqual(r.returncode, 0)
            self.assertEqual(os.listdir(other), [], "opt-in 안 한 폴더를 건드렸다")

    def test_broken_input_is_silent(self):
        """나가는 길에 도는 훅이다 — 어떤 입력에도 죽거나 떠들면 안 된다."""
        for payload in ('', 'not json', '{"cwd": null}',
                        '{"cwd": "%s", "transcript_path": "/nope.jsonl"}' % self.root):
            r = subprocess.run([sys.executable, SESSION_END], input=payload,
                               capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, f"{payload!r} → exit {r.returncode}")

    def test_heartbeat_is_recorded(self):
        """스킬 층이 '이 훅이 살아있나'를 볼 수 있어야 한다."""
        self.tr = _transcript([_user("뭐 해줘"), _edit("x.py")])
        _run(SESSION_END, self._payload())
        self.assertIn("SessionEnd", _common.read_heartbeat(self.root))


class SharedFormatTest(unittest.TestCase):
    """두 훅이 같은 형식을 쓰는지 — 갈리면 handover가 뒤죽박죽이 된다."""

    def test_both_hooks_use_the_shared_builder(self):
        for name in ("pre_compact.py", "session_end.py"):
            with open(os.path.join(HOOKS, name), encoding="utf-8") as f:
                src = f.read()
            self.assertIn("_common.handover_body", src,
                          f"{name}이 항목 형식을 따로 만들고 있다 (SSOT)")


class HookWiringTest(unittest.TestCase):
    def test_session_end_is_wired(self):
        with open(os.path.join(REPO, "hooks", "hooks.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        groups = cfg["hooks"].get("SessionEnd")
        self.assertTrue(groups, "hooks.json에 SessionEnd가 없다 — 스크립트만 있고 안 걸린다")
        matcher = groups[0]["matcher"]
        self.assertIn("clear", matcher)
        self.assertIn("prompt_input_exit", matcher)
        # SessionEnd 훅은 전체가 1.5초 예산을 나눠 쓴다. 길게 잡으면 나갈 때
        # 사용자를 기다리게 한다 — 실측 0.03초짜리 일에 여유만 준다.
        self.assertLessEqual(groups[0]["hooks"][0].get("timeout", 600), 10)


if __name__ == "__main__":
    unittest.main()

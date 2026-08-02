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
        # **실제 git 저장소로 만든다.** 처음엔 그냥 임시 폴더로 두었더니
        # "빈 세션엔 안 쓴다"가 거짓 통과했다 — git 저장소에서는
        # `git_status`가 늘 값을 돌려줘 모든 빈 세션이 "활동 있음"이 됐는데,
        # 비-git 폴더에서는 None이라 테스트만 통과했다. 사용자의 프로젝트는
        # 거의 항상 git 저장소다. 테스트 환경이 실제와 다르면 통과는 거짓이다.
        subprocess.run(["git", "init", "-q"], cwd=self.root,
                       capture_output=True, timeout=30)
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
        self.assertTrue(os.path.isdir(os.path.join(self.root, ".git")),
                        "이 테스트는 git 저장소에서 돌아야 의미가 있다")
        self.tr = _transcript([])
        r = _run(SESSION_END, self._payload())
        self.assertEqual(r.returncode, 0)
        self.assertFalse(os.path.exists(os.path.join(self.root, "handover.md")),
                         "빈 세션인데 handover를 만들었다 — Git 상태를 활동으로 세지 마라")

    def test_compact_then_clear_writes_once(self):
        """`/compact` 하고 바로 `/clear`를 치는 흐름 — 두 번 남기지 않는다."""
        self.tr = _transcript([_user("결제 붙여줘"), _edit("pay.py")])
        _run(PRE_COMPACT, {"cwd": self.root, "transcript_path": self.tr,
                           "hook_event_name": "PreCompact", "trigger": "manual",
                           "session_id": "abc12345"})
        _run(SESSION_END, self._payload())
        self.assertEqual(self._handover().count("결제 붙여줘"), 1,
                         "compact과 clear가 같은 내용을 두 번 남겼다")

    def _compact_then_more(self, extra):
        """compact 한 번 → `extra`만큼 더 일함 → /clear."""
        base = [_user("결제 붙여줘"), _edit("pay.py")]
        self.tr = _transcript(base)
        _run(PRE_COMPACT, {"cwd": self.root, "transcript_path": self.tr,
                           "hook_event_name": "PreCompact", "trigger": "manual",
                           "session_id": "abc12345"})
        os.unlink(self.tr)
        self.tr = _transcript(base + extra)
        _run(SESSION_END, self._payload())
        return self._handover()

    def test_more_work_after_compact_is_recorded(self):
        """중복을 막다가 **진짜 새 작업**까지 버리면 그게 더 나쁘다.

        처음엔 "수정 파일 개수"로 중복을 판정했다. 그래서 아래 세 경우가
        전부 조용히 사라졌다 — 개수가 안 늘었기 때문이다. 실제로 겪은
        결함이라 세 가지를 각각 고정한다."""
        with self.subTest("새 파일까지 고친 경우"):
            self.assertIn("refund.py",
                          self._compact_then_more([_user("환불도"), _edit("refund.py")]))
        with self.subTest("같은 파일을 또 고친 경우 — 개수가 안 는다"):
            self.assertIn("환불 정책은 30일",
                          self._compact_then_more([_user("환불 정책은 30일로 하자"),
                                                   _edit("pay.py")]))
        with self.subTest("파일은 안 건드리고 결정만 논의한 경우"):
            self.assertIn("결제 방식은 PG로 가자",
                          self._compact_then_more([_user("결제 방식은 PG로 가자")]))

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

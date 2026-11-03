"""컨텍스트 사용률 안내(`context_nudge.py`)를 지킨다.

모델은 자기 컨텍스트가 몇 %인지 못 본다. 이 훅이 숫자를 넣어야만
"/compact·/clear 할 때"를 판단할 수 있다. 여기서 지키는 것:

  1. 기준 근처(warn-5%)부터 안내하고, 그 전엔 조용하다 (알림이 쌓이면 신호가 아니다)
  2. `.hi-vibe/context`의 off·warn·window를 따른다 (사용자마다 기준이 다르다)
  3. 한도를 모르면 20만으로 보되, 20만을 넘긴 사용량이면 100만으로 본다
  4. 기준을 넘어도 "중요한 작업 중이면 끊지 말라"는 지시가 같이 간다
  5. init 안 한 프로젝트·깨진 입력에서 조용히 exit 0
  7. 같은 구간에선 세션당 한 번만, compact 직후엔 조용히 (compact 전 값을 읽지 않는다)
  6. 한도를 모르면 사용자에게 화면 %를 **세션당 한 번** 묻게 한다 (2만 토큰 이상일 때)
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(REPO, "hooks", "scripts", "context_nudge.py")


def _transcript(tokens):
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}) + "\n")
        f.write(json.dumps({"type": "assistant", "message": {
            "role": "assistant", "content": [{"type": "text", "text": "ok"}],
            "usage": {"input_tokens": 4, "cache_read_input_tokens": tokens - 4,
                      "cache_creation_input_tokens": 0}}}) + "\n")
    return path


class ContextNudgeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, ".hi-vibe"))

    def tearDown(self):
        self.tmp.cleanup()

    def _config(self, text):
        with open(os.path.join(self.root, ".hi-vibe", "context"), "w", encoding="utf-8") as f:
            f.write(text)

    def _run(self, tokens=None, payload=None):
        if payload is None:
            payload = {"cwd": self.root, "session_id": "t",
                       "transcript_path": _transcript(tokens)}
        p = subprocess.run([sys.executable, HOOK], input=json.dumps(payload),
                           capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stderr)
        if not p.stdout.strip():
            return None
        return json.loads(p.stdout)["hookSpecificOutput"]["additionalContext"]

    def test_quiet_below_lead(self):
        self._config("window=200000\n")
        self.assertIsNone(self._run(40_000))          # 20% of 200K, 기본 기준 30%

    def test_nudges_near_threshold(self):
        text = self._run(52_000)                      # 26% — 30%의 5% 앞
        self.assertIn("26%", text)
        self.assertIn("근접", text)

    def test_past_threshold_keeps_do_not_interrupt(self):
        text = self._run(90_000)                      # 45%
        self.assertIn("초과", text)
        self.assertIn("/clear", text)
        self.assertIn("/compact", text)
        self.assertIn("권하지 말고 계속하라", text)

    def test_off(self):
        self._config("off\n")
        self.assertIsNone(self._run(150_000))

    def test_custom_warn_and_window(self):
        self._config("warn=50 window=1000000\n")
        self.assertIsNone(self._run(300_000))         # 30% < 45%
        self.assertIn("50%", self._run(460_000))      # 46%

    def test_unknown_window_upgrades_past_200k(self):
        text = self._run(250_000)                     # 20만 창이면 불가능한 값
        self.assertIn("/ 1000K", text)                # 25% of 1M — 근접

    def test_asks_window_once_per_session(self):
        self.assertIsNone(self._run(15_000))          # 2만 미만 — 아직 안 묻는다
        first = self._run(40_000)
        self.assertIn("컨텍스트 %가 몇인가요", first)
        self.assertIn("window=", first)
        self.assertIsNone(self._run(40_000))          # 같은 세션 두 번째 — 조용

    def test_no_ask_when_window_known(self):
        self._config("window=1000000\n")
        self.assertIsNone(self._run(40_000))

    def test_once_per_band_then_again_after_drop(self):
        self._config("window=200000\n")
        self.assertIn("근접", self._run(52_000))      # 26% — 근접 구간 진입
        self.assertIsNone(self._run(54_000))          # 27% — 같은 구간, 조용
        self.assertIn("초과", self._run(62_000))      # 31% — 기준 구간 진입
        self.assertIsNone(self._run(70_000))          # 35% — 같은 구간
        self.assertIn("초과", self._run(82_000))      # 41% — +10% 구간
        self.assertIsNone(self._run(20_000))          # compact로 10% — 조용, 기록은 내려감
        self.assertIn("근접", self._run(52_000))      # 다시 차오르면 또 알린다

    def test_quiet_right_after_compact(self):
        """compact 직후엔 boundary 뒤에 usage가 없다 — compact 전 값을 읽으면 안 된다."""
        path = _transcript(90_000)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"type": "system", "subtype": "compact_boundary"}) + "\n")
            f.write(json.dumps({"type": "user", "message": {"role": "user", "content": "요약"}}) + "\n")
        self._config("window=200000\n")
        self.assertIsNone(self._run(payload={"cwd": self.root, "session_id": "t",
                                             "transcript_path": path}))

    def test_bad_config_values_fall_back(self):
        self._config("warn=abc window=-5 # 메모\n")
        self.assertIn("근접", self._run(52_000))

    def test_not_initialized_is_silent(self):
        os.rmdir(os.path.join(self.root, ".hi-vibe"))
        self.assertIsNone(self._run(150_000))

    def test_no_transcript_or_bad_stdin(self):
        self.assertIsNone(self._run(payload={"cwd": self.root, "transcript_path": "/nope"}))
        p = subprocess.run([sys.executable, HOOK], input="not json",
                           capture_output=True, text=True, timeout=20)
        self.assertEqual((p.returncode, p.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()

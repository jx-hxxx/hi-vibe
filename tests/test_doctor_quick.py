"""`doctor --quick`의 생존 판정이 스스로 모순되지 않게 지킨다.

이 판정은 **스킬이 세션당 한 번 자동으로 부르는** 값싼 검사다. 사람이 치는
`/hi-vibe:doctor`와 달리 훅을 실제로 실행하지 않고 heartbeat 파일만 읽는다.

실사용에서 이런 출력이 나왔다:

    {"state": "stale", "fresh_hooks": ["PostToolUse", "Stop"], "last_seen_hours": 0.0}

`stale`인데 마지막 실행이 **0.0시간 전**이고 살아있는 훅이 둘이다. 그걸 본
AI는 경고를 그냥 무시했다 — 말이 안 되니까. **건강검진이 늑대소년이 되면
진짜 고장도 같이 묻힌다.**

원인은 `SessionStart`가 신선한지만 보고 판정한 것이었다. 세션 도중에
플러그인을 켜거나 업데이트하면 `SessionStart`는 이번 세션에서 안 돈다.
그동안 `PostToolUse`·`Stop`은 멀쩡히 돈다.
"""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCTOR = os.path.join(REPO, "scripts", "doctor.py")


def quick(root):
    r = subprocess.run([sys.executable, DOCTOR, "--root", root, "--quick"],
                       capture_output=True, text=True, timeout=60)
    return json.loads(r.stdout.strip().splitlines()[-1])


class DoctorQuickTest(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory(prefix="vibe-doctor-quick-")
        self.root = self._dir.name
        self.state = os.path.join(self.root, ".hi-vibe", "state")
        os.makedirs(self.state)

    def tearDown(self):
        self._dir.cleanup()

    def _beats(self, **hooks):
        with open(os.path.join(self.state, "heartbeat.json"), "w",
                  encoding="utf-8") as f:
            json.dump(hooks, f)

    def test_never_contradicts_itself(self):
        """살아있는 훅이 있는데 `stale`이라고 하면 안 된다.

        이 한 줄이 실사용에서 무너진 계약이다. 어떤 조합이든
        `fresh_hooks`가 비어 있지 않으면 `stale`일 수 없다."""
        now = int(time.time())
        old = now - 99999
        for name, beats in {
            "세션 도중 켬 (SessionStart만 아직)": {"PostToolUse": now, "Stop": now},
            "Stop만 돎": {"Stop": now},
            "SessionStart는 낡고 나머지는 신선": {"SessionStart": old, "Stop": now},
            "전부 신선": {"SessionStart": now, "PostToolUse": now, "Stop": now},
        }.items():
            with self.subTest(name):
                self._beats(**beats)
                out = quick(self.root)
                if out["fresh_hooks"]:
                    self.assertEqual(
                        out["state"], "alive",
                        f"{name}: 살아있는 훅 {out['fresh_hooks']}이 있는데 "
                        f"{out['state']}로 보고했다 — 자기모순이다")

    def test_really_dead_is_still_stale(self):
        """느슨하게 바꾸다 진짜 고장을 놓치면 그게 더 나쁘다."""
        old = int(time.time()) - 99999
        self._beats(SessionStart=old, PostToolUse=old, Stop=old)
        out = quick(self.root)
        self.assertEqual(out["state"], "stale")
        self.assertEqual(out["fresh_hooks"], [])
        self.assertGreater(out["last_seen_hours"], 1)

    def test_never_ran_and_gates(self):
        self.assertEqual(quick(self.root)["state"], "never-ran")   # heartbeat 없음
        open(os.path.join(self.root, ".hi-vibe", "optout"), "w").close()
        self.assertEqual(quick(self.root)["state"], "optout")
        with tempfile.TemporaryDirectory(prefix="vibe-nogate-") as other:
            self.assertEqual(quick(other)["state"], "not-initialized")

    def test_state_is_one_of_the_documented_values(self):
        """스킬이 분기하는 값 밖으로 새 상태를 흘리면 분기가 조용히 깨진다."""
        known = {"alive", "stale", "never-ran", "optout", "not-initialized"}
        self._beats(Stop=int(time.time()))
        self.assertIn(quick(self.root)["state"], known)


if __name__ == "__main__":
    unittest.main()

"""커밋 직전 게이트 — fresh-eyes 없이 커밋이 지나가지 않는지.

이 훅이 생긴 이유는 **fresh-eyes를 Stop 훅에 걸어 두면 고리가 생기기 때문**
이다(2026-09-12 실측, 2시간 세션 5회 차단 · 서브에이전트 9개 중 7개):

    구현 → 차단 → fresh-eyes → 리뷰가 파일을 고침 → 내용이 달라짐 → 또 차단

내용 지문으로 "같은 변경은 두 번 막지 않기"를 해도 지문이 내용에서 나오므로
소용이 없다. 그래서 강제를 **사용자가 "커밋해줘"라고 말한 지점**으로 옮겼다 —
작업의 끝을 근사하지 않고 사용자가 직접 찍는 자리다.

여기서 지키는 경계:
  - 막는다: **안 커밋한** 코드 파일이 있고 fresh-eyes가 안 돌았을 때.
    stage 여부를 안 본다 — `git add -A && git commit`은 스테이징이 커밋과
    같은 Bash 한 줄이라, 훅이 걸리는 시점의 인덱스는 비어 있다
    (2026-09-13 실측: 한 프로젝트 커밋 8개 중 7개가 이 형태라 한 번도 안 걸렸다).
  - 안 막는다: 문서만 건드림 · 커밋이 아닌 명령 · `--dry-run` · 마커 없는 프로젝트
  - **한 커밋 경계에서 한 번만** 막는다 (에이전트 호출이 막힌 환경에서
    커밋이 영구히 불가능해지면 못 막는 것보다 나쁘다 — 2026-08-07)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(REPO, "hooks", "scripts", "pre_commit_gate.py")


def rec(*blocks):
    return json.dumps({"type": "assistant",
                       "message": {"role": "assistant", "content": list(blocks)}})


def agent(kind):
    return {"type": "tool_use", "name": "Agent",
            "input": {"subagent_type": kind, "description": "review"}}


class CommitGateTest(unittest.TestCase):

    def setUp(self):
        self._d = tempfile.TemporaryDirectory(prefix="vibe-commit-gate-")
        self.root = self._d.name
        os.makedirs(os.path.join(self.root, ".hi-vibe"))
        self.git("init", "-q")
        self.git("config", "user.email", "t@t")
        self.git("config", "user.name", "t")
        self.t = os.path.join(self.root, "t.jsonl")
        self.write_transcript()          # 기본: fresh-eyes 흔적 없음

    def tearDown(self):
        self._d.cleanup()

    def git(self, *args):
        subprocess.run(["git"] + list(args), cwd=self.root, check=False,
                       capture_output=True, timeout=30)

    def write_transcript(self, *lines, mode="w"):
        with open(self.t, mode, encoding="utf-8") as f:
            f.write("".join(ln + "\n" for ln in lines) or "\n")

    def edit(self, name="feat.py", body="def a():\n    return 1\n"):
        """stage하지 않고 파일만 쓴다 — 실제 커밋의 흔한 모습이다."""
        path = os.path.join(self.root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        return path

    def stage(self, name="feat.py", body="def a():\n    return 1\n"):
        path = os.path.join(self.root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        self.git("add", name)

    def gate(self, command="git commit -m 'x'", root=None, transcript=None):
        """훅 한 번. 반환 = 훅이 낸 JSON(dict). 아무것도 안 내면 통과."""
        r = subprocess.run(
            [sys.executable, GATE],
            input=json.dumps({
                "cwd": root if root is not None else self.root,
                "session_id": "s1",
                "transcript_path": transcript if transcript is not None else self.t,
                "tool_name": "Bash", "tool_input": {"command": command},
            }),
            capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, f"훅이 호스트를 깼다: {r.stderr}")
        try:
            return json.loads(r.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            return {}

    def denied(self, out):
        return out.get("hookSpecificOutput", {}).get("permissionDecision")

    def reason(self, out):
        return out.get("hookSpecificOutput", {}).get("permissionDecisionReason", "")

    # --- 막는 자리 ---------------------------------------------------------

    def test_denies_commit_without_fresh_eyes(self):
        self.stage()
        out = self.gate()
        self.assertEqual(self.denied(out), "deny", f"안 막았다: {out}")
        self.assertIn("fresh-eyes", self.reason(out))

    def test_denies_when_staging_is_in_the_same_command(self):
        """**이 구멍 때문에 범위를 넓혔다.** `git add -A && git commit`은
        스테이징이 커밋과 같은 명령에 있어, PreToolUse가 걸리는 시점의 인덱스는
        비어 있다. stage된 것만 보면 여기서 통째로 샌다."""
        self.edit()
        out = self.gate("git add -A && git commit -m x")
        self.assertEqual(self.denied(out), "deny", f"안 막았다: {out}")
        self.assertIn("feat.py", self.reason(out))

    def test_dirty_code_blocks_a_docs_only_commit(self):
        """**알고 고른 대가다.** 문서만 stage해도 작업하다 만 코드가 남아 있으면
        막는다. 억울하면 "그냥 커밋해"로 지나간다(같은 커밋은 두 번 안 막는다)."""
        self.edit()                       # 커밋에 안 넣을 지저분한 코드
        self.stage("README.md", "# hi\n")
        self.assertEqual(self.denied(self.gate()), "deny")

    def test_reason_names_the_files_to_review(self):
        """무엇을 리뷰해야 하는지가 사유에 있어야 한다."""
        self.stage("web/app.js", "export const a = 1;\n")
        self.stage("feat.py")
        reason = self.reason(self.gate())
        self.assertIn("feat.py", reason)
        self.assertIn("web/app.js", reason)

    # --- 안 막는 자리 ------------------------------------------------------

    def test_lets_it_pass_when_fresh_eyes_ran(self):
        self.stage()
        self.write_transcript(rec(agent("hi-vibe:fresh-eyes")))
        self.assertNotEqual(self.denied(self.gate()), "deny",
                            "제대로 리뷰했는데 막았다")

    def test_denies_only_once_per_commit_boundary(self):
        """에이전트 호출이 실제로 막힌 환경에서 커밋이 영구 불가능해지면
        **못 막는 것보다 나쁘다.** 두 번째 시도는 통과시킨다."""
        self.stage()
        self.assertEqual(self.denied(self.gate()), "deny")
        self.assertNotEqual(self.denied(self.gate()), "deny", "두 번 막았다")

    def test_docs_only_commit_is_not_touched(self):
        """바뀐 것이 문서뿐이면 (stage됐든 아니든) 막지 않는다."""
        self.stage("README.md", "# hi\n")
        self.edit("NOTES.md", "just prose\n")
        self.assertNotEqual(self.denied(self.gate()), "deny")

    def test_not_a_commit_command(self):
        self.stage()
        for cmd in ("git status", "git add -A", 'echo "git commit"',
                    "git commit --dry-run -m x"):
            self.assertNotEqual(self.denied(self.gate(cmd)), "deny",
                                f"커밋이 아닌데 막았다: {cmd}")

    def test_chained_and_flagged_commit_still_caught(self):
        """`git add -A && git commit -m x`·`git -C . commit`은 커밋이다."""
        self.stage()
        self.assertEqual(self.denied(self.gate("git add -A && git commit -m x")),
                         "deny")
        self.write_transcript()
        os.remove(os.path.join(self.root, ".hi-vibe", "state", "commit-gate.json"))
        self.assertEqual(self.denied(self.gate("git -C . commit -m x")), "deny")

    def test_no_marker_no_gate(self):
        """opt-in — `.hi-vibe/`가 없는 프로젝트에서는 아무것도 하지 않는다."""
        self.stage()
        shutil.rmtree(os.path.join(self.root, ".hi-vibe"))
        self.assertNotEqual(self.denied(self.gate()), "deny")

    def test_no_transcript_does_not_block(self):
        """셀 수 없으면 막지 않는다 (fail-open)."""
        self.stage()
        self.assertNotEqual(self.denied(self.gate(transcript="")), "deny")

    # --- 예산 회계 ---------------------------------------------------------

    def test_second_commit_does_not_reuse_the_first_review(self):
        """한 세션에서 커밋을 두 번 하면 두 번째가 첫 번째의 fresh-eyes를
        당겨쓰면 안 된다 — 통과시킬 때 읽은 위치를 기록해 그 이후만 센다."""
        self.stage()
        self.write_transcript(rec(agent("hi-vibe:fresh-eyes")))
        self.assertNotEqual(self.denied(self.gate()), "deny")
        self.stage("second.py", "def b():\n    return 2\n")
        self.assertEqual(self.denied(self.gate()), "deny",
                         "앞 커밋의 리뷰로 다음 커밋이 통과했다")


if __name__ == "__main__":
    unittest.main()

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


def _bash(cmd):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Bash", "input": {"command": cmd}}]}}


def _edit(path):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": "Edit", "input": {"file_path": path}}]}}


def _race_worker(barrier, root, transcript, idx):
    """동시 종료 재현용 — 모듈 최상단에 있어야 프로세스로 넘길 수 있다."""
    barrier.wait()
    _run(SESSION_END, {"cwd": root, "transcript_path": transcript,
                       "reason": "clear", "session_id": "race-%d" % idx})


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
        with self.subTest("새 사용자 메시지 없이 Bash로만 작업한 경우"):
            # auto-compact은 같은 턴 중간에 일어난다. 그 뒤 Claude가 이어서
            # Bash로만 파일을 만들면 prompts도 edited도 그대로다 — 서명에
            # Bash를 안 넣었을 때 이 턴이 통째로 사라졌다.
            before = self._compact_then_more([])
            self.assertNotIn("build.sh", before)
            self.assertIn("build.sh", self._compact_then_more(
                [_bash("cat > build.sh <<'EOF'\nmake all\nEOF")]))

    def test_marker_survives_other_sessions(self):
        """다른 세션이 표식을 덮어써 중복 방지가 풀리면 안 된다.

        같은 프로젝트에 창을 두 개 띄우면 실제로 난다. 표식을 슬롯 하나로
        두었을 때, 세션 B가 기록한 뒤 세션 A가 끝나면 A의 compact 항목이
        한 번 더 들어갔다."""
        self.tr = _transcript([_user("A 작업"), _edit("a.py")])
        _run(PRE_COMPACT, {"cwd": self.root, "transcript_path": self.tr,
                           "hook_event_name": "PreCompact", "trigger": "manual",
                           "session_id": "sess-A"})
        other = _transcript([_user("B 작업"), _edit("b.py")])
        try:   # 다른 세션(창)이 끼어들어 기록
            _run(SESSION_END, {"cwd": self.root, "transcript_path": other,
                               "reason": "clear", "session_id": "sess-B"})
        finally:
            os.unlink(other)
        _run(SESSION_END, self._payload(sid="sess-A"))
        self.assertEqual(self._handover().count("A 작업"), 1,
                         "다른 세션이 표식을 덮어써 A가 두 번 기록됐다")

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


# 비밀키 탐지기가 실제로 잡는 모양의 가짜 키. 저장소 스캔에도 걸리므로 마커를 단다.
FAKE_KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"  # hi-vibe: allow-secret


class SecretLeakTest(unittest.TestCase):
    """handover가 비밀키 유출 통로가 되면 안 된다.

    처음 만들 때 Bash 명령 **원문**을 200자까지 들고 있다가 100자를 실었다.
    `printf 'API_KEY = "…"' > cfg.py` 하나면 트랜스크립트에만 있던 키가
    프로젝트 루트 파일로 복제되고, 다음 세션 컨텍스트에 다시 주입되고,
    아카이브에 장기 보존된다. 비밀키 안전장치를 내세우는 도구에서 날 일이
    아니다. 정규식으로 가리는 건 새 패턴을 놓치므로 **원문을 아예 갖지
    않는 쪽**으로 고쳤다 — 남기는 것은 대상 파일과 작업 종류뿐이다."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory(prefix="vibe-leak-")
        self.root = self._dir.name
        os.makedirs(os.path.join(self.root, ".hi-vibe"))
        subprocess.run(["git", "init", "-q"], cwd=self.root,
                       capture_output=True, timeout=30)

    def tearDown(self):
        self._dir.cleanup()

    def _run_end(self, entries):
        tr = _transcript(entries)
        try:
            _run(SESSION_END, {"cwd": self.root, "transcript_path": tr,
                               "reason": "clear", "session_id": "leak"})
        finally:
            os.unlink(tr)
        out = {}
        for rel in ("handover.md", os.path.join(".hi-vibe", "state",
                                                "handover-written.json")):
            path = os.path.join(self.root, rel)
            if os.path.isfile(path):
                with open(path, encoding="utf-8") as f:
                    out[rel] = f.read()
        return out

    def test_bash_command_body_never_reaches_handover(self):
        files = self._run_end([
            _user("설정 파일 만들어줘"),
            _bash("printf 'API_KEY = \"%s\"' > generated.py" % FAKE_KEY)])
        self.assertTrue(files.get("handover.md"), "기록 자체는 남아야 한다")
        for rel, text in files.items():
            self.assertNotIn(FAKE_KEY, text, f"{rel}에 비밀키가 복제됐다")
            self.assertNotIn("printf", text, f"{rel}에 명령 원문이 남았다")
        # 무엇을 했는지는 남아야 한다 — 안 남기면 기록이 아니라 침묵이다
        self.assertIn("generated.py", files["handover.md"])
        self.assertIn("redirect", files["handover.md"])

    def test_secrets_in_user_requests_are_masked(self):
        """요청 원문은 안 남길 수 없으므로 가린다(훅과 같은 판정 규칙)."""
        files = self._run_end([_user("내 키는 %s 야, 이걸로 설정해줘" % FAKE_KEY),
                               _edit("cfg.py")])
        self.assertNotIn(FAKE_KEY, files["handover.md"])
        self.assertIn("비밀키 가림", files["handover.md"])
        self.assertIn("이걸로 설정해줘", files["handover.md"])


class MaskingBoundaryTest(unittest.TestCase):
    """가림 처리의 **경계**를 지킨다 — 덜 지워도, 더 지워도 사고다.

    처음엔 `시작 + len(정규화된 조각)`으로 끝을 추정했다. 정규화는 공백을
    접으므로 공백이 많으면 추정한 끝이 실제보다 앞이었다:

        API_KEY     =     "ABCDEFGHIJKLMNOPQRSTUVWX"   (hi-vibe: allow-secret)
        → [비밀키 가림]RSTUVWX"          ← 키 꼬리가 남았다

    반대로 두 패턴이 같은 자리를 잡으면(키 자체 + 할당문) 겹친 구간을
    안 합친 채 뒤에서부터 차례로 치환해 **키 뒤의 멀쩡한 문장까지** 날렸다.
    가리기가 문장을 먹으면 사람이 기록을 안 믿게 된다."""

    KEY = "sk-proj-abcdefghijklmnopqrstuvwxyz1234567890"   # hi-vibe: allow-secret
    AWS = "AKIA1234567890ABCDEF"                            # hi-vibe: allow-secret

    def _masked(self, text):
        return _common.safe_text(text)

    def test_no_tail_survives_when_spacing_is_wide(self):
        for text in ('API_KEY     =     "ABCDEFGHIJKLMNOPQRSTUVWX"',  # hi-vibe: allow-secret
                     'API_KEY =\n  "ABCDEFGHIJKLMNOPQRSTUVWX"',
                     'API_KEY\t=\t"ABCDEFGHIJKLMNOPQRSTUVWX"'):
            got = self._masked(text)
            self.assertNotIn("RSTUVWX", got, f"키 꼬리가 남았다: {got!r}")
            self.assertIn("비밀키 가림", got)

    def test_text_after_the_secret_survives(self):
        got = self._masked('API_KEY = "%s" 뒤 문장' % self.KEY)
        self.assertNotIn(self.KEY, got)
        self.assertIn("뒤 문장", got, f"키 뒤의 문장까지 지웠다: {got!r}")

    def test_several_secrets_on_one_line(self):
        got = self._masked("A키 %s 와 B키 %s 둘 다" % (self.KEY, self.AWS))
        self.assertNotIn(self.KEY, got)
        self.assertNotIn(self.AWS, got)
        self.assertEqual(got.count("비밀키 가림"), 2, got)
        for keep in ("A키", "와 B키", "둘 다"):
            self.assertIn(keep, got)

    def test_clean_text_is_untouched(self):
        for text in ("비밀 없는 평범한 문장입니다",
                     "이 값은 os.environ['API_KEY']로 읽어요", ""):
            self.assertEqual(self._masked(text), text)


class ConcurrentEndTest(unittest.TestCase):
    """두 세션이 **정확히 동시에** 끝나도 표식이 유실되면 안 된다.

    표식 파일은 읽고-고치고-쓰는 구조다. 확인·기록·표식을 한 락 안에 넣기
    전에는, 둘이 동시에 빈 표식을 읽어 둘 다 쓰고 **뒤에 쓴 쪽만 남았다.**
    그러면 앞 세션의 표식이 사라져 다음 종료 때 중복 항목이 생긴다.

    **아래 동시 실행 테스트만으로는 부족하다** — 락을 빼고 돌려봤더니 세 번
    다 통과했다. 프로세스를 띄우는 시간차 때문에 실제로는 거의 겹치지
    않는다. 그래서 "겹쳐도 살아남는가"(기능)와 "표식이 락 안에서 쓰이는가"
    (구조)를 **둘 다** 본다. 재현이 안 되는 타이밍 테스트 하나만 두면
    안전장치가 아니라 장식이다."""

    def test_simultaneous_ends_keep_both_markers(self):
        import multiprocessing
        with tempfile.TemporaryDirectory(prefix="vibe-race-") as root:
            os.makedirs(os.path.join(root, ".hi-vibe"))
            subprocess.run(["git", "init", "-q"], cwd=root,
                           capture_output=True, timeout=30)
            trs = [_transcript([_user(f"세션 {n} 작업"), _edit(f"{n}.py")])
                   for n in ("A", "B")]
            try:
                barrier = multiprocessing.Barrier(2)
                procs = [multiprocessing.Process(
                    target=_race_worker, args=(barrier, root, trs[i], i))
                    for i in (0, 1)]
                for pr in procs:
                    pr.start()
                for pr in procs:
                    pr.join(60)
            finally:
                for t in trs:
                    os.unlink(t)
            with open(os.path.join(root, ".hi-vibe", "state",
                                   "handover-written.json"), encoding="utf-8") as f:
                marks = json.load(f)
        self.assertEqual(sorted(marks), ["race-0", "race-1"],
                         "동시에 끝났더니 한쪽 표식이 사라졌다: %s" % marks)

    def test_marker_is_written_inside_the_lock(self):
        """표식 쓰기가 락 블록 **안**에 있는가 (구조로 고정).

        타이밍 테스트가 못 잡는 회귀를 여기서 잡는다 — 누군가
        `note_handover_written`을 락 밖으로 옮기면 즉시 실패한다."""
        for name in ("session_end.py", "pre_compact.py"):
            with open(os.path.join(HOOKS, name), encoding="utf-8") as f:
                src = f.read()
            after_lock = src.split("with _common.file_lock(")[1]
            block = after_lock.split("\n\n")[0]     # 락 with-블록
            self.assertIn("note_handover_written", block,
                          f"{name}: 표식 쓰기가 락 밖에 있다 — 동시에 끝나는 "
                          f"다른 세션이 이 세션의 표식을 덮어쓴다")


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

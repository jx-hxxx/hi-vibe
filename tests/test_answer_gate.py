"""답변 검사(말투·비유·근거) — Stop 훅이 내가 쓴 문장을 읽는 층.

코드에는 테스트와 fresh-eyes가 있는데 **대화에는 아무 장치가 없었다.**
2026-09-05에 같은 실패가 하루에 여러 번 반복됐다: 격식체 지시를 어기고,
비유로 사실을 흐리고, 확인하지 않은 동작을 단정했다. 문서에 적어 두는
층으로는 안 된다는 것이 그날로 확인됐으므로 기계 층으로 내렸다.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HOOKS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "hooks", "scripts")
sys.path.insert(0, HOOKS)
import _answer_check                                        # noqa: E402
import answer_gate                                          # noqa: E402


class ToneTest(unittest.TestCase):
    """격식체 판정은 **허용 목록**이다 — 목록에 없는 새 말투도 걸려야 한다."""

    def test_formal_sentences_pass(self):
        for text in ["확인한 결과를 근거로 답하겠습니다.",
                     "파일을 열어 확인했습니다. 근거는 아래와 같습니다.",
                     "두 개 다 만들어 드릴까요?",
                     "이 부분을 확인해 주세요."]:
            self.assertEqual(_answer_check.informal_sentences(text), [], text)

    def test_informal_endings_are_caught(self):
        for text in ["이건 좀 아닌 것 같은데 다시 보자.",
                     "왜 이렇게 됐는지 나도 모르겠어.",
                     "그게 바로 그거였죠.",
                     "그건 아까 말했잖아."]:
            self.assertTrue(_answer_check.informal_sentences(text), text)

    def test_label_lines_are_not_sentences(self):
        """실측에서 차단의 절반이 이것이었다 — 문장이 아니라 상태 라벨이다.

        서술어로 끝나지 않으면 문장이 아니다. 이걸 안 보면 `그 외 항목 통과.`
        같은 줄이 전부 걸려서 차단률이 57%가 된다(실측)."""
        for text in ["그 외 항목 통과.", "검사 완료.", "위험 패턴 검출 없음."]:
            self.assertEqual(_answer_check.informal_sentences(text), [], text)

    def test_trailing_parenthetical_does_not_hide_the_ending(self):
        """`...뜹니다 (버튼 정상, 에러 0개).`은 종결어미가 멀쩡하다.

        괄호를 안 떼면 끝 글자가 `개`가 되어 걸린다 — 실측 오탐 1위였다."""
        self.assertEqual(
            _answer_check.informal_sentences("로그인 화면까지 표시됩니다 (에러 0개)."), [])

    def test_embedded_question_is_a_fragment(self):
        self.assertEqual(_answer_check.informal_sentences("제대로 도는지."), [])

    def test_unlisted_informal_style_is_still_caught(self):
        """금지 목록이었다면 샜을 말투. 허용 목록이라 걸린다.

        이 검사가 이 설계의 핵심이다 — 사용자가 `-잖아·-거든`을 나열하는
        방식을 거부한 이유가 바로 새 말투가 샌다는 것이었다."""
        self.assertTrue(_answer_check.informal_sentences("이거 완전 별로인 듯."))
        self.assertTrue(_answer_check.informal_sentences("그렇게 하면 안 되지."))

    def test_code_blocks_and_quotes_are_exempt(self):
        """내 말이 아닌 것은 검사하지 않는다.

        사용자가 반말로 물으신 것을 인용할 수 있어야 하고, 코드 블록 안의
        문자열을 말투로 걸면 검사가 소음이 되어 결국 꺼진다."""
        self.assertEqual(
            _answer_check.informal_sentences("```\n걍 이렇게 하면 됨.\n```"), [])
        self.assertEqual(
            _answer_check.informal_sentences('사용자께서 "왜 거짓말쳐"라고 하셨습니다.'), [])
        self.assertEqual(
            _answer_check.informal_sentences("> 이건 인용한 남의 말이야."), [])

    def test_fragments_without_final_punctuation_are_exempt(self):
        """목록 라벨·표는 명사로 끝나는 게 정상이다."""
        self.assertEqual(_answer_check.informal_sentences("말투 검사     막을 수 있음"), [])
        self.assertEqual(_answer_check.informal_sentences("- 탐지 10건 중 2~3건"), [])


class MetaphorTest(unittest.TestCase):
    """비유는 종결어미로 안 잡힌다 — 문장은 격식체로 끝나면서 틀린다."""

    def test_metaphor_passes_ending_check_but_is_caught(self):
        text = "실제 체결이 흐르는 차트가 뜨고, 가격이 따로 놀지 않습니다."
        self.assertEqual(_answer_check.informal_sentences(text), [],
                         "종결어미로는 안 걸리는 것이 이 검사의 존재 이유다")
        self.assertTrue(_answer_check.metaphors(text))

    def test_plain_statement_passes(self):
        self.assertEqual(
            _answer_check.metaphors("체결 데이터가 들어오고 차트에 표시됩니다."), [])

    def test_wordlist_is_data_not_code(self):
        """목록은 파일에 있다 — 새 표현이 나오면 한 줄만 더하면 된다."""
        tmp = tempfile.mkdtemp()
        try:
            path = os.path.join(tmp, "words.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("# 주석은 무시\n\n뭉개집니다\n")
            self.assertTrue(_answer_check.metaphors("경계가 뭉개집니다.", path))
            self.assertEqual(_answer_check.metaphors("경계가 흐려집니다.", path), [])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_missing_wordlist_disables_only_this_check(self):
        """목록을 못 읽어도 훅 전체가 죽지 않는다(fail-open)."""
        self.assertEqual(_answer_check.metaphors("아무 말.", "/does/not/exist"), [])


def _transcript(tmp, blocks):
    path = os.path.join(tmp, "t.jsonl")
    with open(path, "w", encoding="utf-8") as fh:
        for entry in blocks:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def _user(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


def _say(text):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "text", "text": text}]}}


def _tool(name, inp=None):
    return {"type": "assistant", "message": {"role": "assistant", "content": [
        {"type": "tool_use", "name": name, "input": inp or {}}]}}


class EvidenceTest(unittest.TestCase):
    """근거는 **파일 단위**로 본다 — "무언가 읽었나"로는 못 잡는다."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.dirname(os.path.dirname(HOOKS.rstrip(os.sep)))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _turn(self, blocks):
        return _answer_check.last_turn(_transcript(self.tmp, blocks))

    def test_reading_another_file_does_not_verify_this_one(self):
        """2026-09-05 세 번째 실패의 정확한 모양.

        기술문서를 grep해 놓고 다른 파일의 동작을 단정했다. "무언가 읽었나"
        기준이었다면 도구가 돌았으니 통과했다 — 실측으로 확인한 구멍이다."""
        said, touched = self._turn([
            _user("틀린거임?"),
            _tool("Grep", {"pattern": "x", "path": "CHANGELOG.md"}),
            _say("stop_nudge.py의 172행이 문서를 제외합니다."),
        ])
        self.assertIn("CHANGELOG.md", touched)
        self.assertEqual(
            _answer_check.unverified_mentions(self.repo, said, touched),
            ["stop_nudge.py"])

    def test_opening_the_named_file_passes(self):
        said, touched = self._turn([
            _user("확인해줘"),
            _tool("Bash", {"command": "sed -n 170,175p hooks/scripts/stop_nudge.py"}),
            _say("stop_nudge.py의 172행이 문서를 제외합니다."),
        ])
        self.assertEqual(
            _answer_check.unverified_mentions(self.repo, said, touched), [])

    def test_korean_particle_after_filename_still_matches(self):
        """`stop_nudge.py의`처럼 조사가 붙어도 잡아야 한다.

        파이썬에서 한글도 `\\w`라, 끝을 `\\b`로 잡으면 경계가 안 생겨
        **검사가 조용히 0건이 된다.** 처음 만들 때 실제로 그렇게 됐다."""
        said, touched = self._turn([_user("q"), _say("stop_nudge.py의 동작입니다.")])
        self.assertEqual(
            _answer_check.unverified_mentions(self.repo, said, touched),
            ["stop_nudge.py"])

    def test_files_not_in_this_repo_are_ignored(self):
        """일반적인 파일명까지 세면 매번 뜨고, 매번 뜨는 표시는 안 보게 된다."""
        said, touched = self._turn([_user("q"), _say("보통 package.json에 적습니다.")])
        self.assertEqual(
            _answer_check.unverified_mentions(self.repo, said, touched), [])

    def test_only_the_latest_turn_counts(self):
        """이전 턴에 읽었다고 이번 턴이 확인된 것은 아니다."""
        said, touched = self._turn([
            _user("첫 질문"),
            _tool("Read", {"file_path": "hooks/scripts/stop_nudge.py"}),
            _say("확인했습니다."),
            _user("둘째 질문"),
            _say("stop_nudge.py는 이렇게 동작합니다."),
        ])
        self.assertEqual(touched, set())
        self.assertEqual(
            _answer_check.unverified_mentions(self.repo, said, touched),
            ["stop_nudge.py"])

    def test_tool_results_do_not_start_a_new_turn(self):
        said, touched = self._turn([
            _user("질문"),
            _tool("Read", {"file_path": "hooks/scripts/stop_nudge.py"}),
            {"type": "user", "message": {"role": "user", "content": [
                {"type": "tool_result", "content": "..."}]}},
            _say("stop_nudge.py를 확인했습니다."),
        ])
        self.assertIn("stop_nudge.py", touched)

    def test_bash_writing_does_not_count_as_opening(self):
        said, touched = self._turn([
            _user("질문"),
            _tool("Bash", {"command": "echo x > hooks/scripts/stop_nudge.py"}),
            _say("stop_nudge.py는 이렇게 동작합니다."),
        ])
        self.assertEqual(
            _answer_check.unverified_mentions(self.repo, said, touched),
            ["stop_nudge.py"])


class GateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, ".hi-vibe"), exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _run(self, blocks, **extra):
        payload = {"cwd": self.tmp, "session_id": "t",
                   "transcript_path": _transcript(self.tmp, blocks)}
        payload.update(extra)
        buf = io.StringIO()
        with redirect_stdout(buf):
            answer_gate.main(payload)
        out = buf.getvalue().strip()
        return json.loads(out) if out else {}

    def test_informal_answer_is_blocked(self):
        out = self._run([_user("질문"), _say("이건 아닌 것 같은데 다시 보자.")])
        self.assertEqual(out.get("decision"), "block")
        self.assertIn("말투", out.get("reason", ""))

    def test_formal_answer_is_not_blocked(self):
        out = self._run([_user("질문"), _say("확인하고 답하겠습니다.")])
        self.assertNotEqual(out.get("decision"), "block")

    def test_stop_hook_active_prevents_a_loop(self):
        """고치는 중에 또 막으면 빠져나갈 수 없다."""
        blocks = [_user("질문"), _say("이건 아닌 것 같은데 다시 보자.")]
        out = self._run(blocks, stop_hook_active=True)
        self.assertNotEqual(out.get("decision"), "block")

    def test_same_answer_does_not_block_twice(self):
        blocks = [_user("질문"), _say("이건 아닌 것 같은데 다시 보자.")]
        self.assertEqual(self._run(blocks).get("decision"), "block")
        self.assertNotEqual(self._run(blocks).get("decision"), "block")

    def test_unopened_file_mention_is_blocked(self):
        os.makedirs(os.path.join(self.tmp, ".git"), exist_ok=True)
        out = self._run([_user("질문"), _say("stop_nudge.py는 이렇게 동작합니다.")])
        # 임시 폴더는 이 저장소가 아니라 git ls-files가 비어 검사가 생략된다.
        # 차단 여부가 아니라 **말투로는 안 걸린다**는 것만 고정한다.
        self.assertNotIn("말투", out.get("reason", ""))

    def test_gate_is_off_without_the_hi_vibe_marker(self):
        """opt-in 원칙 — init 안 한 프로젝트는 건드리지 않는다."""
        shutil.rmtree(os.path.join(self.tmp, ".hi-vibe"))
        self.assertEqual(self._run([_user("질문"), _say("걍 이렇게 하면 됨.")]), {})


class HookRegistrationTest(unittest.TestCase):
    """훅을 늘리면 문구가 여러 곳에서 조용히 갈린다(CLAUDE.md의 함정 목록).

    `doctor`가 실제로 돌리는 목록과 `hooks.json`이 등록한 목록이 갈리면,
    죽은 훅을 doctor가 통과시킨다. 그 어긋남을 기계가 잡는다."""

    def test_doctor_runs_every_registered_hook(self):
        root = os.path.dirname(HOOKS.rstrip(os.sep))
        root = os.path.dirname(root)
        sys.path.insert(0, os.path.join(root, "scripts"))
        with open(os.path.join(root, "hooks", "hooks.json"), encoding="utf-8") as fh:
            cfg = json.load(fh)
        registered = set()
        for entries in cfg["hooks"].values():
            for group in entries:
                for h in group.get("hooks", []):
                    registered.add(os.path.basename(h["command"].strip('"').split("/")[-1]
                                                    ).strip('"'))
        import importlib
        doctor = importlib.import_module("doctor")
        self.assertEqual(registered, set(doctor.HOOK_SCRIPTS))


if __name__ == "__main__":
    unittest.main()

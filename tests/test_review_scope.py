"""review_scope 동작 검증 — /hi-vibe:review 의 범위 계산.

임시 git 저장소에서 실제로 돌려 확인한다: 바뀐 코드 파일만 잡히는지,
mark 후 안 바뀐 파일은 skipped로 빠지는지, 다시 바뀌면 재등장하는지,
문서 파일은 제외되는지.
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
    "skills", "write-gate", "scripts"))
import review_scope


def _git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True,
                   capture_output=True, text=True)


def _write(root, rel, text):
    path = os.path.join(root, rel)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def _list(root):
    buf = io.StringIO()
    with redirect_stdout(buf):
        review_scope.cmd_list(root)
    return json.loads(buf.getvalue())


class ReviewScopeTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp()
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "t@t.t")
        _git(self.root, "config", "user.name", "t")
        _write(self.root, "base.py", "x = 1\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "init")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def test_deleted_file_is_reported(self):
        """지운 파일도 리뷰 대상이다.

        예전엔 "지금 존재하는 파일"만 봐서 삭제가 리뷰를 그냥 통과했다.
        AI가 파일을 통째로 지운 경우가 오히려 위험한데(호출부가 남아 있으면
        런타임에 터진다) 아무도 안 봤다."""
        os.remove(os.path.join(self.root, "base.py"))
        out = _list(self.root)
        self.assertEqual(out["deleted"], ["base.py"])
        self.assertEqual(out["deleted_count"], 1)

    def test_deletion_only_still_has_a_fingerprint(self):
        """지문이 비면 Stop 훅이 아예 막지 못한다 — 삭제만 있는 변경의 함정."""
        os.remove(os.path.join(self.root, "base.py"))
        out = _list(self.root)
        self.assertEqual(out["to_review"], [])
        self.assertTrue(out["fingerprint"], "삭제만 있는데 지문이 비었다")

    def test_deleting_more_changes_the_fingerprint(self):
        """지운 파일이 늘면 다른 변경이므로 다시 막아야 한다."""
        _write(self.root, "second.py", "y = 2\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "second")
        os.remove(os.path.join(self.root, "base.py"))
        one = _list(self.root)["fingerprint"]
        os.remove(os.path.join(self.root, "second.py"))
        two = _list(self.root)["fingerprint"]
        self.assertNotEqual(one, two)

    def test_deleted_non_code_file_is_ignored(self):
        """문서를 지운 건 코드 리뷰 대상이 아니다."""
        _write(self.root, "notes.md", "hi\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "doc")
        os.remove(os.path.join(self.root, "notes.md"))
        self.assertEqual(_list(self.root)["deleted"], [])

    def test_new_code_file_needs_review(self):
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        out = _list(self.root)
        self.assertIn("feat.py", out["to_review"])
        self.assertEqual(out["skipped"], [])

    def test_marked_unchanged_file_is_skipped(self):
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        review_scope.cmd_mark(self.root, ["feat.py"])
        out = _list(self.root)
        self.assertEqual(out["to_review"], [])
        self.assertIn("feat.py", out["skipped"])

    def test_changed_after_mark_reappears(self):
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        review_scope.cmd_mark(self.root, ["feat.py"])
        _write(self.root, "feat.py", "def a():\n    return 2\n")  # 다시 수정
        out = _list(self.root)
        self.assertIn("feat.py", out["to_review"])
        self.assertEqual(out["skipped"], [])

    def test_doc_files_excluded(self):
        _write(self.root, "notes.md", "# just docs\n")
        out = _list(self.root)
        self.assertNotIn("notes.md", out["to_review"])

    def test_state_written_under_hi_vibe(self):
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        review_scope.cmd_mark(self.root, ["feat.py"])
        self.assertTrue(os.path.isfile(
            os.path.join(self.root, ".hi-vibe", "reviewed.json")))

    def test_list_reports_sizes_and_total(self):
        _write(self.root, "big.py", "\n".join("x%d=%d" % (i, i) for i in range(40)))
        _write(self.root, "small.py", "def a():\n    return 1\n")
        out = _list(self.root)
        self.assertEqual(out["file_count"], 2)
        self.assertGreater(out["sizes"]["big.py"], out["sizes"]["small.py"])
        self.assertEqual(out["total_changed_lines"],
                         sum(out["sizes"].values()))

    def test_uncommitted_is_the_default_tier(self):
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        out = _list(self.root)
        self.assertEqual(out["scope"], "uncommitted")

    def test_falls_back_to_last_commit_after_committing(self):
        """커밋하면 리뷰가 '볼 게 없다'로 죽어버리던 문제 — 마지막 커밋으로
        내려가 계속 볼 수 있어야 한다."""
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "feat")
        out = _list(self.root)
        self.assertEqual(out["scope"], "last_commit")
        self.assertIn("feat.py", out["to_review"])
        self.assertGreater(out["total_changed_lines"], 0)

    def test_finished_review_does_not_drag_in_older_commits(self):
        """계단은 '바뀐 파일이 있느냐'로 고른다 — 리뷰를 마쳐서 to_review가
        빈 것과, 그 단계에 애초에 변경이 없는 것을 구분해야 한다."""
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        review_scope.cmd_mark(self.root, ["feat.py"])
        out = _list(self.root)
        self.assertEqual(out["scope"], "uncommitted")   # 아래로 안 내려감
        self.assertEqual(out["to_review"], [])
        self.assertNotIn("base.py", out["to_review"])

    def test_fingerprint_tracks_content(self):
        _write(self.root, "feat.py", "def a():\n    return 1\n")
        first = _list(self.root)["fingerprint"]
        self.assertTrue(first)
        self.assertEqual(first, _list(self.root)["fingerprint"])  # 그대로면 같음
        _write(self.root, "feat.py", "def a():\n    return 2\n")
        self.assertNotEqual(first, _list(self.root)["fingerprint"])

    def _chunk(self, n):
        buf = io.StringIO()
        with redirect_stdout(buf):
            review_scope.cmd_chunk(self.root, n)
        return json.loads(buf.getvalue())["buckets"]

    def test_chunk_balances_by_line_count(self):
        _write(self.root, "big.py", "\n".join("x%d=%d" % (i, i) for i in range(60)))
        _write(self.root, "mid.py", "\n".join("y%d=%d" % (i, i) for i in range(25)))
        _write(self.root, "small.py", "def a():\n    return 1\n")
        buckets = self._chunk(2)
        self.assertEqual(len(buckets), 2)
        # 모든 파일이 정확히 한 번씩 배치되고, 큰 파일은 홀로 균형을 맞춤
        placed = sorted(f for b in buckets for f in b["files"])
        self.assertEqual(placed, ["big.py", "mid.py", "small.py"])
        loads = sorted(b["lines"] for b in buckets)
        self.assertLessEqual(loads[1] - loads[0], 60)  # greedy 균형

    def test_chunk_never_exceeds_file_count(self):
        _write(self.root, "only.py", "def a():\n    return 1\n")
        buckets = self._chunk(5)  # 파일 1개인데 5버킷 요청
        self.assertEqual(len(buckets), 1)  # 빈 버킷은 안 나온다


class MultipleCommitsTest(unittest.TestCase):
    """커밋을 여러 번 하면 **직전 커밋이 영영 안 보이던 것** (2026-08-07).

    훅은 커밋과 무관하게 매 턴 돈다. 문제는 트리거가 아니라 **범위**였다.
    한 턴에 커밋을 두 번 하고 푸시하면 `uncommitted`·`unpushed`가 비어
    `HEAD~1..HEAD` 하나만 남는데, 그 직전 커밋의 파일은 범위 밖이 된다.

    실측(2026-08-06 한 프로젝트): 커밋된 코드 35개 중 4개가 이렇게 샜다.
    `sec_client.py`는 12:48에 커밋됐고 12:55 커밋에서 리뷰가 걸렸는데,
    그때 범위는 12:55 커밋 하나뿐이었다."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "t@t.t")
        _git(self.root, "config", "user.name", "t")
        _write(self.root, "base.py", "x = 1\n")
        self._commit("init")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _commit(self, msg):
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", msg)

    def test_earlier_commit_is_not_lost(self):
        """**이게 실측으로 잡힌 결함이다.** 7분 전 커밋이 통째로 빠졌다."""
        _write(self.root, "sec_client.py", "def shares():\n    return 1\n")
        self._commit("feat: SEC")
        _write(self.root, "livefeed.py", "def poll():\n    return 2\n")
        self._commit("refactor: livefeed")
        got = _list(self.root)["to_review"]
        self.assertIn("livefeed.py", got)
        self.assertIn("sec_client.py", got, "직전 커밋이 범위에서 빠졌다")

    def test_docs_commit_does_not_hide_older_work(self):
        """**이건 배포 전에 잡은 두 번째 결함이다.**

        처음엔 `한 단계 더 가도 안 늘어나면 멈춤`으로 만들었는데, 중간에
        낀 문서 커밋 하나가 **그 뒤 이력을 통째로 가렸다**(이 저장소에서
        실제로 HEAD~3 이후가 안 보였다). 문서 커밋은 코드 이력의 일부가
        아니라 그냥 건너뛸 대상이다."""
        _write(self.root, "old.py", "a = 1\n")
        self._commit("old code")
        _write(self.root, "notes.md", "# doc\n")
        self._commit("docs only")
        _write(self.root, "new.py", "b = 2\n")
        self._commit("new code")
        got = _list(self.root)["to_review"]
        self.assertIn("new.py", got)
        self.assertIn("old.py", got, "문서 커밋이 그 뒤를 가렸다")

    def test_reviewed_file_is_filtered_even_if_in_range(self):
        """좁히는 일은 범위가 아니라 `_split_reviewed`가 한다 — 그래야
        중간에서 멈출 필요가 없다."""
        _write(self.root, "old.py", "a = 1\n")
        self._commit("old code")
        review_scope.cmd_mark(self.root, ["old.py"])
        _write(self.root, "new.py", "b = 2\n")
        self._commit("new code")
        got = _list(self.root)["to_review"]
        self.assertIn("new.py", got)
        self.assertNotIn("old.py", got, "이미 본 파일이 다시 나왔다")

    def test_reviewed_commits_are_not_dragged_back(self):
        """리뷰를 마친 뒤 같은 걸 또 보게 되면 리뷰가 영원히 안 끝난다."""
        _write(self.root, "a.py", "a = 1\n")
        self._commit("a")
        _write(self.root, "b.py", "b = 2\n")
        self._commit("b")
        review_scope.cmd_mark(self.root, ["a.py", "b.py", "base.py"])
        self.assertEqual(_list(self.root)["to_review"], [])

    def test_older_unreviewed_survives_marking_the_newer(self):
        """새 것만 마크했다고 옛 것이 사라지면 안 된다 — 아직 안 봤으니까."""
        _write(self.root, "old.py", "a = 1\n")
        self._commit("old")
        _write(self.root, "new.py", "b = 2\n")
        self._commit("new")
        review_scope.cmd_mark(self.root, ["new.py"])
        self.assertIn("old.py", _list(self.root)["to_review"])

    def test_lookback_is_capped(self):
        """상한이 없으면 처음 켠 저장소에서 전체 이력을 리뷰하라고 한다."""
        for i in range(review_scope.MAX_LOOKBACK + 5):
            _write(self.root, "f%d.py" % i, "x = %d\n" % i)
            self._commit("c%d" % i)
        self.assertLessEqual(len(_list(self.root)["to_review"]),
                             review_scope.MAX_LOOKBACK)


class OversizedTest(unittest.TestCase):
    """"크다"는 사실이 아니라 **커지고 있다**를 준다 (2026-08-07).

    실사용에서 같은 파일의 같은 경고가 리뷰마다 똑같이 펼쳐졌다
    (`kis_client.py 686줄`, `livefeed.py 511·559줄`). 이 저장소 원칙은
    `알림은 쌓이면 신호가 아니다`인데 정면으로 어긋난 자리였다.

    그런데 `changed_lines`는 추가+삭제라 **방향이 없다** — 559줄을 389줄로
    쪼갠 리팩터링도 `383줄 변경`으로 보여서 또 짚였다. 그래서 순증을 따로 준다."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "t@t.t")
        _git(self.root, "config", "user.name", "t")
        _write(self.root, "base.py", "x = 1\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "init")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _lines(self, rel, n):
        _write(self.root, rel, "".join("x%d = %d\n" % (i, i) for i in range(n)))

    def _commit(self, msg):
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", msg)

    def test_small_files_are_absent(self):
        self._lines("small.py", 50)
        self.assertEqual(_list(self.root)["oversized"], {})

    def test_reports_lines_and_growth(self):
        self._lines("big.py", 500)
        got = _list(self.root)["oversized"]["big.py"]
        self.assertGreater(got["lines"], 400)
        self.assertGreater(got["growth"], 0)

    def test_first_crossing_is_derivable(self):
        """`lines - growth <= 400`이면 이번에 처음 넘긴 것 — 스킬이 이걸로 가른다."""
        self._lines("grow.py", 380)
        self._commit("under")
        self._lines("grow.py", 460)
        got = _list(self.root)["oversized"]["grow.py"]
        self.assertLessEqual(got["lines"] - got["growth"], 400,
                             "처음 넘긴 것으로 안 읽힌다")

    def test_already_over_is_not_a_first_crossing(self):
        self._lines("big.py", 660)
        self._commit("already big")
        self._lines("big.py", 686)
        got = _list(self.root)["oversized"]["big.py"]
        self.assertGreater(got["lines"] - got["growth"], 400,
                           "원래 넘어 있었는데 처음 넘긴 것처럼 읽힌다")

    def test_shrinking_shows_negative_growth(self):
        """**이게 오늘 실제로 헛짚은 경우다** — 559줄을 389줄로 쪼갠 리팩터링."""
        self._lines("live.py", 559)
        self._commit("big")
        self._lines("live.py", 500)      # 줄였지만 아직 400 초과
        got = _list(self.root)["oversized"]["live.py"]
        self.assertLess(got["growth"], 0, "줄였는데 늘어난 것으로 보인다")

    def test_dropping_under_the_limit_disappears(self):
        self._lines("live.py", 559)
        self._commit("big")
        self._lines("live.py", 389)
        self.assertNotIn("live.py", _list(self.root)["oversized"])


class FrontendAndVendorTest(unittest.TestCase):
    """프론트 파일은 보고, 사람이 안 읽는 파일은 뺀다 (2026-08-07).

    실사용에서 프론트 버그가 잦은 프로젝트인데 `.html`·`.css`가 확장자
    목록에 없어 **리뷰가 한 번도 안 걸렸다.** 로직이 `index.html` 안에
    있어도 마찬가지였다.

    넓히는 김에 빼는 쪽도 좁게 정했다: 사용자의 세 저장소가 전부
    `three.min.js`(600KB 미니파이)를 갖고 있는데 그건 이미 `.js`라 리뷰
    대상이었다. 반대로 `vendor/cube.js`는 **사용자가 직접 쓴 코드**라
    `vendor/`를 통째로 빼면 진짜 코드가 검사에서 사라진다."""

    def setUp(self):
        self.root = tempfile.mkdtemp()
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.email", "t@t.t")
        _git(self.root, "config", "user.name", "t")
        _write(self.root, "base.py", "x = 1\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "init")

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _add(self, rel, text="x\n"):
        path = os.path.join(self.root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def test_html_and_css_are_reviewed(self):
        self._add("frontend/index.html", "<script>boot()</script>\n")
        self._add("frontend/style.css", ".a{color:red}\n")
        got = _list(self.root)["to_review"]
        self.assertIn("frontend/index.html", got)
        self.assertIn("frontend/style.css", got)

    def test_minified_files_are_skipped(self):
        """600KB 미니파이 파일을 사람에게 읽으라고 하면 리뷰가 조롱거리가 된다."""
        self._add("cube/three.min.js", "!function(){}();\n")
        self._add("site/app.min.css", ".a{color:red}\n")
        got = _list(self.root)["to_review"]
        self.assertNotIn("cube/three.min.js", got)
        self.assertNotIn("site/app.min.css", got)

    def test_node_modules_is_skipped(self):
        self._add("node_modules/left-pad/index.js", "module.exports=1\n")
        self.assertNotIn("node_modules/left-pad/index.js",
                         _list(self.root)["to_review"])

    def test_vendor_folder_is_not_skipped(self):
        """`vendor/`를 빼면 사용자가 **직접 쓴** 코드가 조용히 검사 밖으로 간다.

        실제 저장소에 손으로 쓴 `vendor/cube.js`가 있었다. 이름 규칙이
        아니라 파일의 성격으로 갈라야 하는데, 그건 기계가 모른다 —
        그래서 논란 없는 것만 뺀다."""
        self._add("vendor/cube.js", "export function cube(){}\n")
        self.assertIn("vendor/cube.js", _list(self.root)["to_review"])

    def test_deleted_html_is_reported(self):
        self._add("page.html", "<p>hi</p>\n")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-qm", "add page")
        os.remove(os.path.join(self.root, "page.html"))
        self.assertIn("page.html", _list(self.root)["deleted"])

    def test_docs_are_still_excluded(self):
        """넓히면서 문서까지 딸려 들어오면 커밋마다 리뷰가 걸린다."""
        self._add("README.md", "# hi\n")
        self._add("notes.txt", "hi\n")
        got = _list(self.root)["to_review"]
        self.assertNotIn("README.md", got)
        self.assertNotIn("notes.txt", got)


if __name__ == "__main__":
    unittest.main()

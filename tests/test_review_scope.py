"""review_scope 동작 검증 — /hi-vibe:review --all 의 범위 계산.

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


if __name__ == "__main__":
    unittest.main()

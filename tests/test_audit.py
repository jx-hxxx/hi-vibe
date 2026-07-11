"""repo-xray 스캐너(audit.py) 동작 검증.

고정된 임시 저장소를 만들어 scan/find를 실제로 돌리고, 보고서가
계약대로 나오는지 확인한다: dead 후보, 문서 언급 분리(doc_mentions),
변수명만 다른 완전 중복, 90% 유사 중복, TS/TSX 심볼, 데코레이터 분리.
"""
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "repo-xray", "scripts"))
import audit


PY_A = '''\
import os


def used_helper(path):
    return os.path.basename(path)


def totally_dead_fn(x):
    return x * 2


def calc_fee_a(amount, rate):
    """수수료 계산."""
    if amount <= 0:
        return 0
    fee = amount * rate
    if fee < 100:
        fee = 100
    return round(fee)


def near_dup_source(items):
    out = []
    for item in items:
        if item is None:
            continue
        value = item.strip().lower()
        if value:
            out.append(value)
    total = len(out)
    return out, total
'''

PY_B = '''\
from a import used_helper


def run():
    return used_helper("/tmp/x")


def calc_fee_b(money, ratio):
    """같은 로직, 변수명만 다름."""
    if money <= 0:
        return 0
    charge = money * ratio
    if charge < 100:
        charge = 100
    return round(charge)


def near_dup_variant(items):
    out = []
    for item in items:
        if item is None:
            continue
        value = item.strip().upper()
        if value:
            out.append(value)
    total = len(out)
    return out, total


def route_handler():
    return "framework calls me by registration"


route_handler = __import__("functools").wraps(run)(route_handler)
'''

PY_DECORATED = '''\
import functools


@functools.lru_cache()
def unreferenced_route():
    return 1
'''

TS_MAIN = '''\
export const fetchQuotes = async (url: string): Promise<string> => {
  return url;
};

export function formatPrice(value: number): string {
  return value.toFixed(2);
}

interface QuoteProps {
  symbol: string;
}

type QuoteHandler = string;

export class QuoteStore {
}

const unusedTsHelper = (x: number) => x + 1;
'''

TSX_APP = '''\
import { fetchQuotes, formatPrice, QuoteStore } from "./quotes";

export default function App() {
  const p: QuoteProps = { symbol: "AAPL" };
  const h: QuoteHandler = "h";
  fetchQuotes("u");
  formatPrice(1);
  new QuoteStore();
  return p && h;
}
'''

DOC_MD = '''\
# MODULE

`totally_dead_fn` 은 수수료 재계산에 쓰려고 만든 함수다.
`used_helper` 도 여기 언급된다.
'''


def make_repo():
    root = tempfile.mkdtemp(prefix="xray-test-")
    files = {
        "a.py": PY_A, "b.py": PY_B, "routes.py": PY_DECORATED,
        "quotes.ts": TS_MAIN, "App.tsx": TSX_APP, "MODULE.md": DOC_MD,
        "types.d.ts": "export declare function ambientOnly(): void;\n",
        "test_stuff.py": (
            "import unittest\n\n\n"
            "class UnreferencedSuite(unittest.TestCase):\n"
            "    def test_x(self):\n        pass\n\n\n"
            "def test_lonely_case():\n    assert True\n"
        ),
    }
    for name, body in files.items():
        with open(os.path.join(root, name), "w", encoding="utf-8") as f:
            f.write(body)
    return root


class ScanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = make_repo()
        with redirect_stdout(io.StringIO()):
            audit.cmd_scan(cls.root)
        with open(os.path.join(cls.root, ".repo-xray", "report.json"), encoding="utf-8") as f:
            cls.report = json.load(f)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def dead_names(self):
        return {d["name"] for d in self.report["dead_candidates"]}

    def test_dead_candidate_found(self):
        self.assertIn("totally_dead_fn", self.dead_names())

    def test_used_symbol_not_dead(self):
        self.assertNotIn("used_helper", self.dead_names())

    def test_doc_mention_does_not_rescue(self):
        """MODULE.md에 언급돼도 죽은 후보에서 빠지면 안 된다 (문서 오염 버그)."""
        entry = next(d for d in self.report["dead_candidates"]
                     if d["name"] == "totally_dead_fn")
        self.assertEqual(entry["doc_mentions"], ["MODULE.md"])
        self.assertEqual(entry["appears_in"], ["a.py"])

    def test_decorated_reported_separately(self):
        decorated = {d["name"] for d in self.report["decorated_unreferenced"]}
        self.assertIn("unreferenced_route", decorated)
        self.assertNotIn("unreferenced_route", self.dead_names())

    def test_exact_duplicate_ignores_variable_names(self):
        groups = [
            {fn["name"] for fn in g["functions"]}
            for g in self.report["duplicate_functions"]
        ]
        self.assertIn({"calc_fee_a", "calc_fee_b"}, groups)

    def test_near_duplicate_detected(self):
        pairs = [
            {fn["name"] for fn in nd["functions"]}
            for nd in self.report["near_duplicate_functions"]
        ]
        self.assertIn({"near_dup_source", "near_dup_variant"}, pairs)
        nd = next(x for x in self.report["near_duplicate_functions"]
                  if {fn["name"] for fn in x["functions"]}
                  == {"near_dup_source", "near_dup_variant"})
        self.assertGreaterEqual(nd["similarity"], 0.9)
        self.assertLess(nd["similarity"], 1.0)

    def test_ts_symbols_extracted(self):
        symbols, _ = audit.analyze_js(
            self.root, [os.path.join(self.root, "quotes.ts"),
                        os.path.join(self.root, "App.tsx")])
        by_name = {s["name"]: s["kind"] for s in symbols}
        self.assertEqual(by_name.get("fetchQuotes"), "js-function")
        self.assertEqual(by_name.get("formatPrice"), "js-function")
        self.assertEqual(by_name.get("App"), "js-function")
        self.assertEqual(by_name.get("QuoteStore"), "js-class")
        self.assertEqual(by_name.get("QuoteProps"), "ts-type")
        self.assertEqual(by_name.get("QuoteHandler"), "ts-type")

    def test_unused_ts_helper_is_dead_candidate(self):
        self.assertIn("unusedTsHelper", self.dead_names())

    def test_dts_symbols_not_extracted(self):
        self.assertNotIn("ambientOnly", self.dead_names())

    def test_ts_files_counted_in_scan_range(self):
        self.assertGreaterEqual(self.report["scan"]["files_scanned"]["js"], 2)

    def test_test_file_symbols_not_dead(self):
        """unittest/pytest는 이름 규칙으로 심볼을 호출한다 — 죽은 후보 제외."""
        self.assertNotIn("UnreferencedSuite", self.dead_names())
        self.assertNotIn("test_lonely_case", self.dead_names())


class FindTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = make_repo()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def run_find(self, query):
        buf = io.StringIO()
        with redirect_stdout(buf):
            audit.cmd_find(self.root, query)
        return json.loads(buf.getvalue())

    def test_exact_hit_with_scan_range(self):
        result = self.run_find("fetchQuotes")
        self.assertGreaterEqual(len(result["exact_hits"]), 2)  # 정의 + 사용
        self.assertGreater(result["scan_range"]["files_scanned"], 0)

    def test_similar_names_for_absence(self):
        result = self.run_find("calc_fee")
        self.assertEqual(result["exact_hits"], [])
        self.assertTrue(any("calc_fee" in n for n in result["similar_symbol_names"]))


class EmptyRepoTest(unittest.TestCase):
    def test_scan_empty_repo(self):
        root = tempfile.mkdtemp(prefix="xray-empty-")
        try:
            with redirect_stdout(io.StringIO()):
                code = audit.cmd_scan(root)
            self.assertEqual(code, 0)
            with open(os.path.join(root, ".repo-xray", "report.json"), encoding="utf-8") as f:
                report = json.load(f)
            self.assertEqual(report["dead_candidates"], [])
            self.assertEqual(report["near_duplicate_functions"], [])
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

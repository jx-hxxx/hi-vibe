"""repo-xray 스캐너(audit.py) 동작 검증.

고정된 임시 저장소를 만들어 scan/find를 실제로 돌리고, 보고서가
계약대로 나오는지 확인한다: dead 후보, 문서 언급 분리(doc_mentions),
변수명만 다른 완전 중복, 90% 유사 중복, TS/TSX 심볼, 데코레이터 분리.
"""
import ast
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


def wip_not_implemented():
    raise NotImplementedError  # 아직 구현 전


def wip_todo():
    pass  # TODO: 여기 채우기


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


def dead_only_in_comment(x):
    # NOTE: dead_only_in_comment 은 나중에 dead_url("http://x") 처럼 쓸 예정
    return x


def string_ref_target(x):
    return x + 1
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


def dispatch(name):
    # 동적 호출: 문자열로 심볼을 부른다 (FP-03) — 문자열은 참조로 세야 한다
    table = {"string_ref_target": "app.a:string_ref_target"}
    return table[name]


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

    def test_wip_functions_flagged_not_dead_looking(self):
        """미완성(NotImplementedError/pass+TODO) 함수는 참조 0이라 dead
        후보에 잡히더라도 looks_wip=True로 표시돼야 한다 — '죽은 코드'가
        아니라 '아직 안 만든 것'일 수 있으므로 삭제 제안 전 조심하게."""
        by_name = {d["name"]: d for d in self.report["dead_candidates"]}
        self.assertTrue(by_name["wip_not_implemented"]["looks_wip"])
        self.assertTrue(by_name["wip_todo"]["looks_wip"])
        # 진짜 본문이 있는 dead는 WIP 아님
        self.assertFalse(by_name["totally_dead_fn"]["looks_wip"])

    def test_used_symbol_not_dead(self):
        self.assertNotIn("used_helper", self.dead_names())

    def test_comment_only_mention_does_not_rescue(self):
        """이름이 자기 주석에만 또 나오는 함수는 여전히 dead 후보여야 한다 —
        주석은 참조가 아니다. (.md 구제는 막았지만 코드 주석 경로가 뚫려
        있던 버그: 주석 하나로 죽은 코드가 은폐됐다.)"""
        self.assertIn("dead_only_in_comment", self.dead_names())

    def test_string_mention_still_rescues(self):
        """반대로 문자열 속 이름은 참조로 세야 한다 (FP-03 동적 호출) — 주석만
        지우고 문자열은 보존했는지 확인. b.py의 dispatch 테이블 문자열이
        string_ref_target를 살려야 한다."""
        self.assertNotIn("string_ref_target", self.dead_names())

    def test_default_export_not_dead_candidate(self):
        """`export default function App()`은 임포트 측에서 아무 이름으로나
        받으므로 이름 참조가 0 — 죽은 코드가 아니다 (FP-08). React 컴포넌트가
        전부 죽은 후보로 뜨던 오탐을 막는다."""
        self.assertNotIn("App", self.dead_names())

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

    def test_is_test_file_classification(self):
        self.assertTrue(audit._is_test_file("tests/test_hooks.py"))
        self.assertTrue(audit._is_test_file("foo/test_x.py"))
        self.assertTrue(audit._is_test_file("foo/x_test.py"))
        self.assertFalse(audit._is_test_file("src/app.py"))
        self.assertFalse(audit._is_test_file("lib/util.py"))

    def test_test_pairs_split_into_separate_bucket(self):
        """테스트끼리 유사한 쌍은 near_duplicate_test_functions로 분리되어,
        기본 near_duplicate_functions(진짜 봐야 할 code<->code)를 오염시키지
        않는다 — 스캐너 신호 대 잡음비."""
        code_pairs = self.report["near_duplicate_functions"]
        # 기본 버킷엔 test<->test 쌍이 들어오면 안 된다.
        for nd in code_pairs:
            files = [fn["file"] for fn in nd["functions"]]
            self.assertFalse(all(audit._is_test_file(f) for f in files),
                             f"test<->test 쌍이 코드 버킷에 샜다: {files}")
        # 분리 버킷 키가 존재해야 한다(값이 0이어도 키는 있어야 함).
        self.assertIn("near_duplicate_test_functions", self.report)
        self.assertIn("near_duplicate_test_total", self.report)

    def test_near_duplicate_is_scan_order_independent(self):
        """near-dup 탐지는 파일 스캔 순서(OS마다 다름)에 의존하면 안 된다.
        과거 difflib autojunk 비대칭 + os.walk 순서 차이로 CI만 실패했던
        회귀를 막는다."""
        py = [os.path.join(self.root, f)
              for f in ("a.py", "b.py", "routes.py", "test_stuff.py")]

        def pairs_for(order):
            _, _, near, _, _ = audit.analyze_python(self.root, order)
            return sorted(tuple(sorted(fn["name"] for fn in nd["functions"]))
                          for nd in near)

        self.assertEqual(pairs_for(py), pairs_for(list(reversed(py))))
        self.assertIn(("near_dup_source", "near_dup_variant"), pairs_for(py))

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


class NearDupPrefilterTest(unittest.TestCase):
    """near-dup 탐지는 O(L^2) difflib.ratio()를 쌍마다 부르면 중간 규모
    저장소에서 수 분이 걸린다. 그래서 shingle 지문 Jaccard로 먼저 걸러
    소수만 ratio()에 넘긴다(성능). 이 최적화의 계약은 하나다:
    **선필터는 완전탐색이 찾을 near-dup을 절대 떨어뜨리면 안 된다.**
    jaccard_floor를 너무 높이거나 덤프 길이로 자르면 이 계약이 깨지고
    스캔이 조용히 near-dup을 놓친다 — 아래 테스트가 그 회귀를 막는다."""

    @staticmethod
    def _fn(nstmts, tweak=None):
        lines = ["def f(a):"]
        for i in range(nstmts):
            lines.append("    v%d = a + %d" % (i, i))
        if tweak == "op":            # 연산자 하나만 다름 -> 90%+ 유사(near-dup)
            lines[2] = "    v1 = a - 1"
        elif tweak == "extra":       # 문장 하나 추가 -> 크기 살짝 다른 무관 함수
            lines.append("    v = v0 * 2")
        lines.append("    return a")
        return "\n".join(lines)

    @classmethod
    def _entry(cls, src, line):
        node = ast.parse(src).body[0]
        end = getattr(node, "end_lineno", node.lineno)
        return {"meta": {"name": "f", "file": "t.py", "line": line,
                         "length": end - node.lineno + 1},
                "dump": audit.normalized_dump(node)}

    def _corpus(self, sizes):
        srcs = []
        for n in sizes:                       # 각 크기마다 near-dup 쌍 하나
            srcs.append(self._fn(n))
            srcs.append(self._fn(n, tweak="op"))
        for n in (7, 22, 85):                 # 크기 다른 무관 함수(잡음)
            srcs.append(self._fn(n, tweak="extra"))
        return [self._entry(s, i * 10 + 1) for i, s in enumerate(srcs)]

    @staticmethod
    def _pairs(results):
        return sorted(tuple(sorted(f["line"] for f in r["functions"]))
                      for r in results)

    def test_prefilter_matches_bruteforce(self):
        # 완전탐색(floor=0, 모든 쌍이 ratio())과 기본 선필터가 '똑같은' near-dup을
        # 내야 한다. 작은/중간 함수로 충분 — 계약은 크기와 무관하다.
        entries = self._corpus(sizes=(10, 40))
        filtered, _ = audit.find_near_duplicates(entries)
        brute, _ = audit.find_near_duplicates(entries, jaccard_floor=0.0)
        self.assertTrue(brute, "코퍼스가 near-dup을 만들어야 테스트가 유효하다")
        self.assertEqual(self._pairs(filtered), self._pairs(brute),
                         "선필터가 완전탐색과 다른 결과 -> 진짜 near-dup을 놓친 것")

    def test_detection_is_not_capped(self):
        """탐지(find_near_duplicates)는 전체를 반환해야 한다 — 상위 N개로 자르는
        것은 리포트 표시 층(cmd_scan)의 책임이다. 그래야 리포트가 near_duplicate_total로
        '20 of 24'처럼 정직하게 말할 수 있다(조용히 버리지 않음)."""
        # 같은 뼈대 + 변형마다 다른 문장 1개 => 서로 ~0.95 유사(near-dup) 7개
        entries = []
        for k in range(7):
            lines = ["def f(a):"] + ["    v%d = a + %d" % (i, i) for i in range(20)]
            lines += ["    u = a * %d" % (k + 2), "    return a"]  # 변형별 상수 1개만 다름
            entries.append(self._entry("\n".join(lines), k * 100 + 1))
        results, _ = audit.find_near_duplicates(entries)
        self.assertEqual(len(results), 21)  # C(7,2)=21쌍 전부, 20에서 안 잘림

    def test_large_near_dups_are_not_size_capped(self):
        """큰 함수끼리도 진짜 near-dup이 실재하므로(계측: 20k자 near-dup 확인)
        덤프 길이로 ratio()를 잘라선 안 된다. 큰 near-dup 쌍이 기본 선필터로
        잡히는지 못박는다."""
        entries = self._corpus(sizes=(250,))
        big_lines = {e["meta"]["line"] for e in entries if len(e["dump"]) > 10000}
        self.assertGreaterEqual(len(big_lines), 2, "덤프 1만자+ 함수가 코퍼스에 있어야 한다")
        results, _ = audit.find_near_duplicates(entries)
        found_big = any(all(f["line"] in big_lines for f in r["functions"])
                        for r in results)
        self.assertTrue(found_big, "큰 함수 near-dup 쌍이 리포트돼야 한다(size-cap 금지)")


if __name__ == "__main__":
    unittest.main()

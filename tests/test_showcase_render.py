"""CHANGELOG의 `show:` 주석이 랜딩으로 나갈 때 **글자 그대로 새지 않는지.**

`build-showcase.py`는 오래도록 `**굵게**`만 변환했다. 그래서 백틱을 쓰면
`` `_common.py` `` 가 백틱째로 페이지에 나갔는데, 아무도 안 썼기 때문에
드러나지 않았다 — 즉 **"show: 주석엔 백틱 쓰지 말 것"이라는 적힌 적 없는
규칙**에 기대고 있었다. 2026-08-08에 처음 쓰자마자 8개가 그대로 나갔다.

CHANGELOG는 마크다운이고 코드 이름에 백틱을 쓰는 게 자연스럽다. 사람이
참는 대신 기계가 변환한다. 이 파일은 그 변환이 ①실제로 일어나고
②이스케이프를 깨뜨리지 않는지를 지킨다.
"""
import os
import re
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import importlib.util                                  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "build_showcase", os.path.join(REPO, "scripts", "build-showcase.py"))
build_showcase = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_showcase)

LANDING = os.path.join(REPO, "docs", "index.html")
BLOCK_RE = re.compile(
    r"<!--\s*SHOWCASE:[a-z]+-start\s*-->(.*?)<!--\s*SHOWCASE:[a-z]+-end\s*-->", re.S)


def blocks():
    with open(LANDING, encoding="utf-8") as f:
        return BLOCK_RE.findall(f.read())


class RenderTest(unittest.TestCase):
    def test_backticks_become_code(self):
        out = build_showcase.render_body("**제목** `foo.py`를 고쳤다")
        self.assertIn("<code>foo.py</code>", out)
        self.assertNotIn("`", out)

    def test_escaping_still_happens_first(self):
        """순서가 바뀌면 본문의 `<`가 태그가 된다 — 저자 글이 마크업이 되면 안 된다."""
        out = build_showcase.render_body("**제목** `a<b>c` 그리고 <script>x</script>")
        self.assertIn("&lt;b&gt;", out, "백틱 안의 <>가 태그로 새어나갔다")
        self.assertNotIn("<script>", out)

    def test_inline_bold_becomes_a_tag(self):
        """**두 번째 결함**: 맨 앞 볼드만 바꿔서 문장 안쪽 별표가 그대로 나갔다."""
        out = build_showcase.render_body("**제목** 그리고 **강조**가 문장 안에")
        self.assertIn("<strong>강조</strong>", out)
        self.assertNotIn("**", out)

    def test_bold_only_body_still_works(self):
        """맨 앞 볼드가 없는 항목도 안쪽 볼드를 처리해야 한다."""
        self.assertIn("<strong>강조</strong>",
                      build_showcase.render_body("제목 없이 **강조**만"))

    def test_author_br_still_works(self):
        self.assertIn("<br>", build_showcase.render_body("**제목** 한 줄<br>두 줄"))

    def test_unpaired_backtick_is_left_alone(self):
        """홀수 개는 코드가 아니다 — 억지로 닫으면 문장이 망가진다."""
        out = build_showcase.render_body("**제목** 백틱 하나 ` 만 있음")
        self.assertNotIn("<code>", out)


class LandingTest(unittest.TestCase):
    def test_no_raw_backticks_reach_the_page(self):
        """**이게 실제로 새어나간 결함이다.** 8개가 페이지에 그대로 있었다."""
        stray = [b for b in blocks() if "`" in b or "**" in b]
        self.assertEqual(stray, [], "타임라인에 마크다운 기호(백틱·별표)가 글자 "
                                    "그대로 남았다 — build-showcase.py를 다시 돌려라")

    def test_only_safe_tags_inside_the_body(self):
        """저자 텍스트가 들어가는 자리는 <code>·<br>·<strong>만 허용한다."""
        for body in re.findall(r"<span>(.*?)</span>", " ".join(blocks()), re.S):
            bad = re.findall(r"<(?!/?(?:code|br|strong)\b)[^>]*>", body)
            self.assertEqual(bad, [], f"본문에 허용 외 태그가 들어갔다: {bad[:2]}")

    def test_styles_exist_for_generated_tags(self):
        """태그를 만들어놓고 스타일이 없으면 글자 크기·색이 튄다."""
        with open(LANDING, encoding="utf-8") as f:
            page = f.read()
        for sel in (".rel .h code", ".rel .h strong"):
            self.assertIn(sel, page, f"{sel} 스타일이 없다")


if __name__ == "__main__":
    unittest.main()

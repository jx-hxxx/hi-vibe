"""설치 전 평가 프롬프트가 **네 곳에 같은 내용으로** 있는지 지킨다.

이 프롬프트는 랜딩(`docs/index.html`) · README 한 · README 영 ·
`docs/internal/eval-prompt.md` 네 곳에 산다. 사람이 붙여넣어 쓰는 글이라
한 곳만 고치면 **다른 데서 옛 질문을 복사해 간다** — 실제로 랜딩만 고치고
README를 몇 릴리스 동안 방치했다.

`docs/internal/eval-prompt.md` 첫머리가 이렇게 적어두고 있었다:

    페이지가 바뀌면 여기도 같이 고친다 — 두 벌이 갈리면 이 파일이 거짓말이 된다.

그 약속을 사람 눈이 아니라 기계가 지킨다. 랜딩을 원본으로 삼는 이유는
거기가 **복사 버튼이 달린 자리**라 실제로 가장 많이 쓰이기 때문이다.
"""
import html
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANDING = os.path.join(REPO, "docs", "index.html")
ARCHIVE = os.path.join(REPO, "docs", "internal", "eval-prompt.md")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def landing_prompt(lang):
    """랜딩의 `<pre id="audit-prompt-…">` 안쪽 텍스트 (태그·엔티티 제거)."""
    m = re.search(r'<pre id="audit-prompt-%s">(.*?)</pre>' % lang,
                  _read(LANDING), re.S)
    assert m, f"랜딩에서 audit-prompt-{lang}를 못 찾았다"
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()


def fenced_block(path, heading):
    """`heading` 아래 첫 번째 ```text 블록."""
    text = _read(path)
    start = text.index(heading)
    a = text.index("```text", start)
    b = text.index("```", a + 7)
    return text[a + 7:b].strip()


class EvalPromptSyncTest(unittest.TestCase):
    def test_readmes_match_the_landing(self):
        for path, heading, lang in (
            ("README.ko.md", "## 직접 검증해 보세요", "ko"),
            ("README.md", "## Verify it yourself", "en"),
        ):
            with self.subTest(path):
                self.assertEqual(
                    fenced_block(os.path.join(REPO, path), heading),
                    landing_prompt(lang),
                    f"{path}의 평가 프롬프트가 랜딩과 다르다 — 한 곳만 고쳤다. "
                    f"랜딩(docs/index.html)이 원본이다.")

    def test_archive_matches_the_landing(self):
        blocks = [b.strip() for b in
                  re.findall(r"```text\n(.*?)```", _read(ARCHIVE), re.S)]
        self.assertEqual(len(blocks), 2,
                         "아카이브에 한·영 두 블록이 있어야 한다")
        self.assertEqual(blocks[0], landing_prompt("ko"),
                         "아카이브 한국어 블록이 랜딩과 다르다")
        self.assertEqual(blocks[1], landing_prompt("en"),
                         "아카이브 영어 블록이 랜딩과 다르다")

    def test_the_placeholder_survives(self):
        """자리표시자가 사라지면 AI가 hi-vibe만 보고 답한다.

        이 질문의 값어치는 **내 프로젝트와 같이 보게 하는 것**에 있다.
        누가 다듬다가 이 줄을 지우면 질문이 반쪽이 된다."""
        self.assertIn("[내 프로젝트 GitHub 링크]", landing_prompt("ko"))
        self.assertIn("[my project's GitHub link]", landing_prompt("en"))


if __name__ == "__main__":
    unittest.main()

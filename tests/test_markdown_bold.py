"""닫는 `**` 앞에 문장부호가 오면 볼드가 안 먹는 것을 막는다.

CommonMark에서 닫는 구분자는 **오른쪽 접함**(right-flanking)이어야 한다.
앞이 문장부호(`"` `)` `]`)이고 뒤가 글자면 그 조건을 못 채워서, `**`가
그대로 화면에 보인다:

    **"내 프로젝트에 맞는지 물어보는 질문"**까지   →  별표가 그대로 노출
    "**내 프로젝트에 맞는지 물어보는 질문**"까지   →  정상

한국어는 조사가 바로 붙어서 **유독 자주 걸린다**(`"…"**를`, `)**이다`).

이 검사가 있는 이유는 **재발**이다. 2026-07-28에 같은 문제를 고치면서
"같은 패턴이 더 있는지 정규식으로 전수 확인했다"고 CHANGELOG에 적었는데,
그 뒤로 여덟 건이 다시 쌓였다. 사람이 한 번 훑는 것으로는 안 되는 종류라
기계로 옮긴다. 게다가 `show:` 주석은 랜딩으로 그대로 나가므로
(`build-showcase.py`는 맨 앞 볼드만 `<b>`로 바꾼다) 페이지에도 별표가 보인다.
"""
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 앞이 문장부호이고 뒤가 글자인 닫는 `**`.
BROKEN_CLOSE = re.compile(r'[^\s*][”"\')\]]\*\*(?=[^\s\W])')

# 백틱 안은 "이렇게 쓰면 깨진다"고 **인용하는** 자리라 검사에서 뺀다.
INLINE_CODE = re.compile(r"`[^`\n]*`")
FENCED = re.compile(r"```.*?```", re.S)

TARGETS = ["README.md", "README.ko.md", "CHANGELOG.md",
           os.path.join(".claude", "CLAUDE.md")]


def _scrubbed(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return INLINE_CODE.sub("``", FENCED.sub("```", text))


class MarkdownBoldTest(unittest.TestCase):
    def test_no_broken_bold_in_docs(self):
        hits = []
        for rel in TARGETS:
            text = _scrubbed(os.path.join(REPO, rel))
            for m in BROKEN_CLOSE.finditer(text):
                line = text[:m.start()].count("\n") + 1
                hits.append(f"{rel}:{line}  …{text[max(0, m.start() - 30):m.end() + 10]}…")
        self.assertEqual(
            hits, [],
            "닫는 `**` 앞이 문장부호라 볼드가 안 먹는다. 따옴표·괄호를 볼드 "
            "**밖으로** 빼라 (`\"**굵게**\"를`):\n" + "\n".join(hits))

    def test_the_check_actually_fires(self):
        """정규식이 무력해지는 것을 막는다 — 실제로 있었던 문장으로 확인."""
        broken = [
            '그리고 **"내 프로젝트에 맞는지 물어보는 질문"**까지 사이트에 있습니다.',
            '**유일본은 랜딩(docs/index.html)**이다.',
            '우리 저장소를 검사하면 **"비밀키 11건"**이 떴습니다.',
            '**새 서브에이전트(fresh-eyes)**가 봅니다.',
        ]
        for t in broken:
            self.assertTrue(BROKEN_CLOSE.search(t), f"못 잡는다: {t}")

    def test_correct_bold_is_not_flagged(self):
        """멀쩡한 볼드까지 잡으면 검사가 잔소리가 된다."""
        fine = [
            '그리고 "**내 프로젝트에 맞는지 물어보는 질문**"까지 사이트에 있습니다.',
            '**유일본은 랜딩**(docs/index.html)이다.',
            '**설치는 전역 한 번, init은 프로젝트마다.**',
            '이 말은 **정확히** 그런 뜻입니다.',
            '**Bold at end of line**',
        ]
        for t in fine:
            self.assertIsNone(BROKEN_CLOSE.search(t), f"오탐: {t}")


if __name__ == "__main__":
    unittest.main()

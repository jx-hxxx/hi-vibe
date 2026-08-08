#!/usr/bin/env python3
"""Build the showcase timeline in docs/index.html from CHANGELOG.md.

This is hi-vibe eating its own dog food: the promo page's release list is
NOT hand-maintained — it is generated from the same CHANGELOG the plugin
keeps current. The page staying fresh is itself proof the doc-sync works.

Each released version carries two one-line summaries as HTML comments right
under its header (invisible on GitHub, parsed here):

    ## [0.6.0] - 2026-07-12
    <!-- show:ko **굵은 헤드라인.** 상세 설명 -->
    <!-- show:en **Bold headline.** detail -->

The newest MAX_ITEMS versions that have those comments are rendered into the
KO / EN timelines between the SHOWCASE markers in docs/index.html.
`**bold**` becomes <b>bold</b>; the remaining text becomes <span>.

No third-party dependencies. Run by CI on every CHANGELOG change
(.github/workflows/showcase.yml), or by hand: `python3 scripts/build-showcase.py`.
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(ROOT, "CHANGELOG.md")
PAGE = os.path.join(ROOT, "docs", "index.html")
MAX_ITEMS = 3

VER_RE = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})\s*$")
SHOW_RE = re.compile(r"<!--\s*show:(ko|en)\s+(.*?)\s*-->")


def parse_changelog(text):
    """Return [{ver, date, ko, en}, ...] in file order (newest first)."""
    items, cur = [], None
    for line in text.splitlines():
        m = VER_RE.match(line)
        if m:
            cur = {"ver": m.group(1), "date": m.group(2), "ko": None, "en": None}
            items.append(cur)
            continue
        if cur is None:
            continue
        s = SHOW_RE.search(line)
        if s:
            cur[s.group(1)] = s.group(2).strip()
    return items


def render_body(raw):
    """Escape, then turn a leading **bold** into <b>bold</b> + <span>rest</span>.

    `백틱`은 <code>로 바꾼다. 예전엔 안 바꿔서 **백틱이 글자 그대로 페이지에
    나갔다**(v0.43.3에서 8개). CHANGELOG는 마크다운이라 코드 이름에 백틱을
    쓰는 게 자연스러운데, 여기만 안 바뀌니 "백틱 쓰지 말 것"이라는 적힌
    적 없는 규칙에 기대고 있었다. 기계가 처리하는 쪽이 맞다.

    이스케이프 **뒤에** 바꾼다 — 순서가 바뀌면 본문의 `<`가 태그가 된다."""
    esc = html.escape(raw, quote=False)
    esc = esc.replace("&lt;br&gt;", "<br>")  # 저자가 넣은 <br>만 실제 줄바꿈으로 (나머지는 이스케이프 유지)
    esc = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", esc)
    m = re.match(r"\*\*(.+?)\*\*\s*(.*)$", esc)
    if not m:
        return "<span>{}</span>".format(_inline(esc))
    bold, rest = m.group(1), _inline(m.group(2).strip())
    return "<b>{}</b> <span>{}</span>".format(bold, rest) if rest else "<b>{}</b>".format(bold)


def _inline(text):
    """문장 **안쪽** 볼드도 태그로. 맨 앞 볼드만 바꾸던 시절엔 **여기 별표가
    화면에 그대로 나갔다**(v0.43.1 항목에서 4개). CHANGELOG는 마크다운이라
    강조를 문장 중간에 쓰는 게 자연스럽고, 백틱과 같은 종류의 누수였다."""
    return re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", text)


def rels(items, lang):
    lines = []
    for it in items:
        if not it.get(lang):
            continue
        lines.append(
            '        <div class="rel"><div class="v">v{ver}<small>{date}</small></div>'
            '<div class="h">{body}</div></div>'.format(
                ver=it["ver"], date=it["date"], body=render_body(it[lang])))
        if len(lines) >= MAX_ITEMS:
            break
    return "\n".join(lines)


def replace_between(page, lang, block):
    start = "<!--SHOWCASE:{}-start-->".format(lang)
    end = "<!--SHOWCASE:{}-end-->".format(lang)
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(page):
        raise SystemExit("SHOWCASE markers for '{}' not found in docs/index.html".format(lang))
    return pat.sub(lambda _m: "{}\n{}\n{}".format(start, block, end), page)


def main():
    items = parse_changelog(open(CHANGELOG, encoding="utf-8").read())
    page = open(PAGE, encoding="utf-8").read()
    for lang in ("ko", "en"):
        page = replace_between(page, lang, rels(items, lang))
    open(PAGE, "w", encoding="utf-8").write(page)
    ko = min(MAX_ITEMS, sum(1 for i in items if i["ko"]))
    en = min(MAX_ITEMS, sum(1 for i in items if i["en"]))
    print("showcase built: ko={} en={} (from {} versions in CHANGELOG)".format(ko, en, len(items)))


if __name__ == "__main__":
    main()

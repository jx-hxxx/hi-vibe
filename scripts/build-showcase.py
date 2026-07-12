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
    """Escape, then turn a leading **bold** into <b>bold</b> + <span>rest</span>."""
    esc = html.escape(raw, quote=False)
    m = re.match(r"\*\*(.+?)\*\*\s*(.*)$", esc)
    if not m:
        return "<span>{}</span>".format(esc)
    bold, rest = m.group(1), m.group(2).strip()
    return "<b>{}</b> <span>{}</span>".format(bold, rest) if rest else "<b>{}</b>".format(bold)


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
    # header version badge — the latest released version, kept in sync
    if items:
        ver = "v" + items[0]["ver"]
        page = re.sub(r"<!--VER-->.*?<!--/VER-->",
                      lambda _m: "<!--VER-->{}<!--/VER-->".format(ver), page)
    open(PAGE, "w", encoding="utf-8").write(page)
    ko = min(MAX_ITEMS, sum(1 for i in items if i["ko"]))
    en = min(MAX_ITEMS, sum(1 for i in items if i["en"]))
    print("showcase built: ko={} en={} (from {} versions in CHANGELOG)".format(ko, en, len(items)))


if __name__ == "__main__":
    main()

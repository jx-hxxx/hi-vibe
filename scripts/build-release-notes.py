#!/usr/bin/env python3
"""Build a GitHub Release title + body for a version from CHANGELOG.md.

hi-vibe dogfooding again: release notes are NOT hand-written per release — they
are extracted from the same CHANGELOG the plugin already maintains, so the git
tag / GitHub Release, plugin.json, and the landing timeline all stay in sync
from one source of truth.

Usage:
    python3 scripts/build-release-notes.py <version> <body_out_path>

Writes the release BODY to <body_out_path> and prints the release TITLE to
stdout. Body = the `show:ko` promo blurb (if present) followed by the version's
`### ...` sections. Title = "v<version> — <first bold phrase of show:ko>", or
just "v<version>" when no blurb exists.
"""
import re
import sys
from pathlib import Path


def extract(changelog, version):
    lines = changelog.splitlines()
    # Locate "## [<version>]" ... up to the next "## [".
    start = next(
        (i for i, ln in enumerate(lines)
         if re.match(r"^##\s*\[" + re.escape(version) + r"\]", ln)),
        None,
    )
    if start is None:
        return None, None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^##\s*\[", lines[j]):
            end = j
            break
    section = lines[start + 1:end]

    # The Korean promo blurb lives in an HTML comment: <!-- show:ko ... -->
    show_ko = ""
    for ln in section:
        m = re.match(r"^\s*<!--\s*show:ko\s*(.*?)\s*-->\s*$", ln)
        if m:
            show_ko = m.group(1).strip()
            break

    # Body sections = everything except the show:ko / show:en comment lines.
    kept = [ln for ln in section
            if not re.match(r"^\s*<!--\s*show:(ko|en)\b", ln)]
    while kept and not kept[0].strip():
        kept.pop(0)
    while kept and not kept[-1].strip():
        kept.pop()

    parts = []
    if show_ko:
        parts.append(show_ko)
    if kept:
        parts.append("\n".join(kept))
    body = ("\n\n".join(parts).strip() + "\n") if parts else f"Release v{version}.\n"

    title = f"v{version}"
    if show_ko:
        bold = re.search(r"\*\*(.+?)\*\*", show_ko)
        if bold:
            headline = bold.group(1).strip().rstrip(".。")
            title = f"v{version} — {headline}"
    return title, body


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: build-release-notes.py <version> <body_out_path>")
    version = sys.argv[1]
    body_out = Path(sys.argv[2])
    changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
    title, body = extract(changelog, version)
    if title is None:
        # No CHANGELOG section — still ship a minimal, honest note.
        title, body = f"v{version}", f"Release v{version}.\n"
    body_out.write_text(body, encoding="utf-8")
    print(title)


if __name__ == "__main__":
    main()

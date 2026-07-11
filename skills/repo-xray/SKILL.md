---
name: repo-xray
description: >-
  Evidence-based repository structure analysis for Python and
  JavaScript/TypeScript (js/jsx/ts/tsx) projects. Runs a bundled scanner
  script and answers only from its JSON output — never from guessing. Use this skill whenever the user asks about
  duplicate code, unused/dead code, "does function X already exist?",
  cleaning up or refactoring the codebase, oversized files, or repo
  structure health — including Korean phrasings like "중복 코드 찾아줘",
  "안 쓰는 코드/죽은 코드 정리", "이런 함수 이미 있어?", "구조 분석해줘",
  "정리할 거 알려줘", "리팩토링 뭐부터 해?". Also use it before writing a
  new helper function when there is a real chance an equivalent one
  already exists in the repo.
---

# repo-xray

A repo evidence engine: a script produces machine evidence, and you turn
that evidence into short, kind, actionable advice. The reader may be new
to coding — plain words, no tool jargon, at most three suggestions at a
time unless they ask for a full report.

<HARD-GATE>
## Core Contract — the line that must not blur

```
NO STRUCTURAL CLAIM WITHOUT RUNNING THE SCRIPT
NO ABSENCE CLAIM WITHOUT STATING THE SCAN RANGE
A DEAD "CANDIDATE" IS NOT A VERDICT
```

If you have not run the script in this session, do not state counts
("unused functions: 12") or absence ("that function doesn't exist").
Run it first, read the JSON, then make the smallest true claim the
evidence supports. Cross this line and the tool becomes a confident
guesser — exactly the failure it exists to prevent.
</HARD-GATE>

## Commands

Run from anywhere; point `--root` at the repo being analyzed.

```bash
# Full structure scan -> writes <root>/.repo-xray/report.json
python3 <skill-path>/scripts/audit.py scan --root <repo>

# "Does X exist anywhere?" -> exact hits + similar names, prints JSON
python3 <skill-path>/scripts/audit.py find <name> --root <repo>
```

`<skill-path>` is this skill's directory — in plugin installs that is
`${CLAUDE_PLUGIN_ROOT}/skills/repo-xray`. The scan needs only Python 3
(stdlib) — no installs. Suggest adding `.repo-xray/` to `.gitignore`
once, the first time a scan runs in a repo.

## Which command for which question

- "중복 코드 있어?", "정리할 것 알려줘", "구조 어때?", "안 쓰는 코드?"
  → `scan`, then read `report.json`.
- "X라는 함수/기능 이미 있어?", "어디서 쓰여?" → `find X`. If the user
  describes a behavior rather than a name ("환율 바꾸는 거"), run `find`
  on 2-3 plausible names (e.g. `exchange`, `usd_to_krw`, `convertRate`)
  and also check `similar_symbol_names` in the output.
- Before writing a new helper the repo might already have → `find` first.

## Reading the evidence honestly

The scanner counts name references across all scanned text files. That
means dynamic uses are invisible to it — and you must say so instead of
pretending certainty:

- `dead_candidates` means "no reference found in the scanned CODE files",
  never "safe to delete". Check each candidate's `decorated` flag:
  decorated Python functions are usually route handlers or hooks that
  frameworks call by registration, not by name — do not suggest deleting
  those; at most mention they *look* unreferenced.
- Doc mentions don't rescue: a name that appears only in `.md`/`.css`
  files stays a dead candidate, with those files listed in
  `doc_mentions`. If the user deletes the code, remind them to fix the
  listed docs in the same turn (docs-keeper contract).
- Names built dynamically (`getattr`, string keys, template strings,
  event names in HTML attributes outside scanned files) will not show up
  as references. When recommending deletion, always phrase it as "the
  scan found no references in N files — worth double-checking X before
  removing".
- `duplicate_functions` matches identical logic (same AST with function
  name AND local variable names normalized away). These are strong
  evidence — safe to present as real duplicates.
- `near_duplicate_functions` are pairs ≥90% similar after the same
  normalization — the typical AI failure of re-implementing something
  "almost the same". WEAKER evidence: read both functions before
  claiming duplication; present as "비슷한 구현 의심 — 두 함수를 같이
  보세요", never as a verdict.
- JS/TS symbol extraction is regex-based (no parser): class methods and
  exotic declaration forms may be missed. Say so when a TS-heavy repo
  question depends on completeness.
- For absence answers, quote the scan range from the JSON:
  "backend/frontend의 N개 파일을 스캔했는데 없었어요" — not "없어요".

Before presenting any dead/duplicate/collision finding, screen it against
`references/false-positive-index.md` — known ways this scanner gets
fooled, each with the softer phrasing to use. Translate matches into
plain-language reasons **in the user's language**; don't cite FP ids
unless asked for proof.

Full field-by-field JSON guide: read `references/report-format.md` when
you need to interpret a field not covered above.

## Answer shape

Default voice: everyday words, headline-level compression, file:line
kept visible. Lead with the direct answer, then up to three concrete
next steps, each backed by evidence (`file:line`, counts, scan range).
Offer the full list ("전체 목록 보여드릴까요?") instead of dumping it.
Expand raw JSON only when the user asks for proof or detail.

## Red flags — stop and re-run instead

- about to state a count without a scan in this session
- about to say "없어요/no such function" without naming the scan range
- about to recommend deleting a `decorated` candidate
- about to present a finding without screening it against
  `references/false-positive-index.md`
- reusing a stale `report.json` after the code has changed this session

# report.json field guide

Written by `scripts/audit.py scan` to `<root>/.repo-xray/report.json`.

## scan

- `root` — absolute path that was analyzed.
- `files_scanned` — counts by group (`python`, `js`, `all_text`).
  `all_text` includes html/css/json/md/yml, which also count as
  reference sources (a function used only in an HTML `onclick` still
  shows a reference).
- `excluded_dirs` — directories never entered (node_modules, venv, …).
  Minified files (`*.min.js`) and files over 2 MB are also skipped.
- `note` — the standing caveat about name-based counting. Repeat its
  substance whenever you recommend deletion.

## dead_candidates

Symbols whose name appears nowhere outside their own definitions.
Decorated ones are moved out into `decorated_unreferenced`.

- `kind` — `function` | `class` | `js-function`. Python methods are
  deliberately excluded (instance calls make name counting too noisy).
- `refs_found` / `appears_in` — reference count outside definitions and
  which files mention the name at all.
- Names starting with `_` and `main` are skipped by design.

Known false-positive sources: `getattr`/string dispatch, template
strings, config-driven wiring, names used only in files outside the
scanned extensions.

## decorated_unreferenced

Same shape as `dead_candidates`, but every entry has decorators
(routes, hooks, event handlers). Frameworks call these by registration,
not by name — treat as "probably alive" and never recommend deletion.
Only worth mentioning if the user asks for an exhaustive audit.

## duplicate_functions

Groups of functions with byte-identical logic (AST equality, function
name and decorators ignored; bodies shorter than 4 lines skipped).
High confidence — present these as genuine duplicates. `length` is the
line count of each copy.

## js_name_collisions

The same function name defined in two or more different JS files. Not
necessarily a bug (modules scope names), but in browser-global vanilla
JS the later `<script>` silently wins — worth flagging when both files
are loaded by the same HTML page.

## oversized_files / oversized_functions

Python/JS files over 400 lines (top 15) and Python functions/methods
over 60 lines (top 15). Size alone is not a defect; use as "where to
look first" guidance, not as a verdict.

## python_parse_errors

Files the AST parser could not read. Their symbols are missing from
every other section — mention this if the user asks about code in one
of these files.

## find output (stdout JSON)

- `exact_hits` — word-boundary matches, `file`/`line`/`text`, capped at
  80. At the cap, say "80개 이상" rather than an exact count.
- `similar_symbol_names` — fuzzy matches against every defined symbol
  name; check before declaring something doesn't exist.
- `scan_range.files_scanned` — quote this number in absence answers.

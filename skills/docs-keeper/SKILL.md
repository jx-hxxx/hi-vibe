---
name: docs-keeper
description: >-
  Maintains the four living documents of a vibe-check project: CLAUDE.md
  (lean project map), per-folder MODULE.md (detailed design), handover.md
  (session-to-session context log), CHANGELOG.md (substantive change
  history, Keep a Changelog). Use for /vibe-check:init, :handover, :log,
  :welcome, and whenever the user asks to 문서 정리, 인수인계 기록,
  체인지로그 작성, CLAUDE.md 갱신, "이 폴더 문서 만들어줘", or after a
  structural change that must be reflected in docs.
---

# docs-keeper

You maintain four documents. Each has one job — never blur them:

| 문서 | 한 줄 정의 | 갱신 시점 |
|---|---|---|
| `CLAUDE.md` | 프로젝트 지도 (얇게!) | 폴더/요구사항이 바뀔 때 |
| `<folder>/MODULE.md` | 그 폴더의 상세 설계 | 폴더 내용이 바뀔 때 |
| `handover.md` | 세션 맥락 (왜/어디까지 했나) | 세션 끝·compact 직전 |
| `CHANGELOG.md` | 결과 (무엇이 바뀌었나) | 실질 변경 직후 |

Templates: `templates/*.tpl` in this skill's directory.
All user-facing prose you write into these docs is Korean.

## Token budget (hard rule)

CLAUDE.md is loaded into EVERY session — every line costs tokens forever.
Keep it ≤ 120 lines. Detail always goes DOWN into MODULE.md, never up.
Never paste MODULE.md content, code, or long lists into CLAUDE.md.

## Mode: init

1. Detect state: does the project root have CLAUDE.md / handover.md /
   CHANGELOG.md? Which top-level folders look like feature folders
   (contain source files; skip `node_modules`, `.git`, `dist`, `venv`,
   `__pycache__`, build output)?
2. If a file already exists, NEVER overwrite silently — show what is
   missing versus the template and ask before touching it
   (AskUserQuestion). `--audit` mode: only report drift, change nothing.
3. Scaffold missing docs from templates:
   - CLAUDE.md: fill 개요/요구사항/실행 방법 by asking the user if not
     inferable; generate the 폴더 지도 by scanning 2 levels deep — one
     line per folder + `→ 상세: <folder>/MODULE.md`.
   - MODULE.md: propose the feature-folder list, confirm with the user
     (one AskUserQuestion, multiSelect), then create one per confirmed
     folder, pre-filling 주요 파일 from a directory listing and leaving
     설계 sections as short TODO prompts for the user.
   - handover.md + CHANGELOG.md from templates.
4. Ensure `.vibe-check/` and `.repo-xray/` are in `.gitignore`.
5. Tell the user the hooks are now active for this project (they gate on
   handover.md existing) and what will happen automatically.

## Mode: handover

Write ONE new entry at the TOP of handover.md (below the file header,
above older entries — newest first, append-only, never rewrite old
entries, never delete the `⚠️ 자동 생성` entries the PreCompact hook
made — refine the newest auto entry in place instead, keeping its
timestamp and marking it `(다듬음)`).

Get the timestamp by running `date '+%Y-%m-%d %H:%M'` — never guess it.

Entry format:

```markdown
## YYYY-MM-DD HH:MM (manual)

- 한 일: …
- 진행 중: …
- 다음에 할 일: …
- 주의/함정: …
```

Write what the NEXT session needs to continue: decisions made and WHY,
dead ends already tried, exact file paths in progress. Not a diary —
an instruction to your future self.

Rotation: if the file has more than 20 entries, move the older half to
`handover-archive.md` (create if missing) and say you did.

## Mode: log

1. Determine what actually changed: prefer `git diff --stat` /
   `git log` since the last CHANGELOG timestamp; otherwise use this
   session's edits. If `$ARGUMENTS` describes the change, trust it but
   still verify against the diff.
2. Filter: substantive = behavior, API, schema, dependency, or config
   changes. Typos, formatting, comments, pure refactors with identical
   behavior → do NOT log (say so instead of logging filler).
3. Append under `## [Unreleased]` in the right category (Added /
   Changed / Fixed / Removed), one bullet per change, each bullet
   prefixed `YYYY-MM-DD HH:MM` (run `date`, never guess).
4. Do not renumber or edit released sections.

## Mode: welcome

Explain in kind, plain Korean (짧게!): the 4 documents table above, the
command map (init → 평소엔 pre-write/post-write → 세션 끝 handover →
변경 후 log → 가끔 audit/guards), and that hooks auto-record handover
before every compact. If CLAUDE.md or handover.md is missing here,
offer `/vibe-check:init`.

## Doc-sync contract (applies everywhere)

Structure changed (file added/moved/renamed, folder responsibility
changed) → the matching MODULE.md AND the CLAUDE.md 폴더 지도 must be
updated in the same turn. A doc that lies is worse than no doc.

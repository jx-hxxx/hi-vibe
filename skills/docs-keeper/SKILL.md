---
name: docs-keeper
description: >-
  Maintains the four living documents of a hi-vibe project: CLAUDE.md
  (lean project map), per-folder MODULE.md (detailed design), handover.md
  (session-to-session context log), CHANGELOG.md (substantive change
  history, Keep a Changelog). Use for /hi-vibe:init, :handover, :log,
  :recall, :welcome, and whenever the user asks to 문서 정리, 인수인계
  기록, 체인지로그 작성, CLAUDE.md 갱신, "이 폴더 문서 만들어줘", or after
  a structural change that must be reflected in docs. Also use (mode:
  recall) when the user asks about PAST decisions or work — "예전에 왜
  이렇게 했지?", "저번에 뭐까지 했더라", "이거 언제 바꿨지", "왜 이
  방식으로 결정했었지", why did we choose X — search the handover/archive/
  CHANGELOG records instead of guessing from memory.
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
All user-facing prose you write into these docs follows the **user's
conversation language** — write in Korean if the user talks to you in
Korean, English if in English, and so on. Match the language they are
actually using with you; do not default to any single language. (An
existing doc's language wins: if the project's docs are already in one
language, keep writing in that one for consistency.)

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
4. **Create the `.hi-vibe/` marker directory** — this is what turns the
   hooks ON for this project (the gate). Write `.hi-vibe/initialized`
   with a one-line note (date + "hi-vibe initialized"), which also
   creates the dir. **The gate is `.hi-vibe/`, NOT handover.md** — a user
   may already have their own `handover.md`, so we must not key on it
   (that would misfire and could let a hook overwrite their file). Do not
   consider init complete until `.hi-vibe/` exists.
5. Ensure `.hi-vibe/`, `.repo-xray/`, `handover.md`,
   `handover-archive.md`, and `handover.md.lock` (the transient write-lock
   file for concurrent sessions) are in `.gitignore`. The two dirs are caches;
   `handover*` is a personal session log kept local (not shared to
   GitHub). The other three docs — CLAUDE.md / MODULE.md / CHANGELOG.md —
   ARE committed.
6. Tell the user the hooks are now active for this project (they gate on
   the `.hi-vibe/` directory existing) and what will happen automatically.

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

## Mode: recall

"예전에 왜/뭐까지/언제" 질문에 기억이 아니라 **기록**으로 답한다.

1. 검색 대상: `handover.md`, `handover-archive.md`, `CHANGELOG.md`
   (구조 질문이면 해당 폴더 `MODULE.md`도).
2. 질문에서 검색어 2~4개를 뽑는다 — 한국어·영어·코드 명칭 변형을
   섞어서 (예: 시세 → 주가, price, quote, 폴링). Grep으로 찾고, 안
   걸리면 다른 변형으로 2~3회 재시도한다.
3. 걸린 위치는 그 **항목 전체**(해당 `## ` 섹션)를 읽는다 — 한 줄만
   보고 답하지 않는다. 여러 기록이 얽히면 시간순으로 재구성한다.
4. 답변에는 출처 필수: 날짜와 파일 ("2026-05-12 handover 기록에 따르면
   …"). 기록에 없는 부분을 상상으로 잇지 않는다.
5. 못 찾으면 못 찾았다고 말하되, 어느 파일을 어떤 검색어로 뒤졌는지
   함께 말한다 (repo-xray의 부재 계약과 동일). 그 후 "기억나는 대로
   추정"을 덧붙일 땐 추정 라벨을 명확히 붙인다.
6. 기록이 현재 코드와 어긋나 보이면 그 사실도 알린다 — 기록은 그
   시점의 사실이지 현재의 보증이 아니다.

## Mode: welcome

**Keep it SHORT — a greeting, not a manual.** No docs table, no full
command list, no hook internals. Just a few lines, in the **user's
language** (Korean if they speak Korean, English if English):

1. A warm one-line 👋 greeting (Korean "👋 안녕하세요, hi-vibe예요!" /
   English "👋 Hi, I'm hi-vibe!").
2. One line on what hi-vibe is — a **vibe-coding seatbelt** that keeps
   the repo clean while you code with AI.
3. **Check whether the `.hi-vibe/` directory exists in the current
   project** (that is hi-vibe's init marker) and say the right one:
   - **MISSING (`.hi-vibe/` absent)** → hi-vibe is NOT set up here yet.
     Say clearly, e.g. "이 프로젝트에서 hi-vibe를 쓰려면 먼저
     `/hi-vibe:init`을 입력해 주세요." Do NOT be fooled by an existing
     `CLAUDE.md` or `handover.md` (the user may already have their own
     for other reasons) — the marker is `.hi-vibe/`, so if that directory
     is absent, init is still needed.
   - **EXISTS** → say they can just code normally; it's already on.
4. **Always paste the GitHub URL as a real link** and tell them to read
   the README there — never just say "the plugin README":
   "자세한 건 https://github.com/jx-hxxx/hi-vibe 의 README.md를
   읽어보세요." / "For details, read the README at
   https://github.com/jx-hxxx/hi-vibe".

That's the whole welcome — a few lines, nothing more.

## Doc-sync contract (applies everywhere)

Structure changed (file added/moved/renamed, folder responsibility
changed) → the matching MODULE.md AND the CLAUDE.md 폴더 지도 must be
updated in the same turn. A doc that lies is worse than no doc.

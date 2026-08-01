---
name: docs-keeper
description: >-
  Maintains the four living documents of a hi-vibe project: CLAUDE.md
  (lean project context — constraints, pitfalls, rationale), per-folder
  MODULE.md (detailed design), handover.md
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
| `CLAUDE.md` | 코드만 봐선 모를 것 — 제약·함정·결정 (얇게!) | 그것들이 바뀔 때 (파일 이동은 해당 없음) |
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
3. Scaffold the LEAN default only — do NOT create every doc up front. A
   toy project must not start with more management docs than code.
   - CLAUDE.md: fill 개요/요구사항/실행 방법/함정/결정 기록 by asking the
     user when not inferable. **Write only what the code cannot tell you.**
     Do NOT generate a folder listing, a dependency list, or an
     architecture overview — Claude can get those from `ls`/`grep` in one
     second, they go stale immediately, and they cost context every
     session. (Claude Code's own `/doctor` trims exactly that kind of
     derivable content and keeps pitfalls, rationale and conventions —
     don't generate what the platform will delete.)
     `상세 문서` lists only MODULE.md files that actually exist — never
     write a pointer to a file you didn't create. It stays empty at init.
   - handover.md from its template.
   - `CHANGELOG.md` from `templates/CHANGELOG.md.tpl` (skip if it already
     exists — never overwrite). 트러블슈팅 기록이 이 플러그인의 핵심이라
     CLAUDE.md·handover.md와 같은 급으로 처음부터 만든다. 지연 생성은
     "첫 실질 변경 전까진 필요 없다"는 이유였지만, 그 결과 **doctor는
     없다고 경고하는데 init을 다시 쳐도 안 생기는** 막다른 길이 됐다.
   - Do NOT create MODULE.md at init. 폴더별 상세 설계는 그 폴더가 실제로
     복잡해졌을 때 생긴다 (step 3a). 처음부터 빈 MODULE.md를 뿌리면
     아무도 안 채운 껍데기만 남는다.
3a. Lazy docs — create each one the moment it is first needed, not before:
   - `<folder>/MODULE.md`: create when that folder's design first needs
     recording — a structural change lands in it, `review` finds it has
     grown complex, or the user asks "이 폴더 문서 만들어줘". Pre-fill
     주요 파일 from a directory listing, leave 설계 as short TODO prompts,
     and add a line for it under CLAUDE.md's `상세 문서` in the SAME turn
     (per the doc-sync contract below). A file listing belongs HERE, next
     to the design it explains — not in CLAUDE.md, which every session
     pays for.
   (`CHANGELOG.md`는 더 이상 여기 없다 — init이 만든다. 이미 있는 프로젝트를
   위해 log 모드는 여전히 없으면 만들지만, 정상 경로에서는 그럴 일이 없다.)
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
   ARE committed. CLAUDE.md and CHANGELOG.md exist from init; MODULE.md
   arrives later, per step 3a.
6. Tell the user the hooks are now active for this project (they gate on
   the `.hi-vibe/` directory existing) and what will happen automatically.
   Say the start is intentionally lean — CLAUDE.md + handover.md +
   CHANGELOG.md, nothing else — and that per-folder MODULE.md appears on
   its own once a folder grows complex enough to need it. Do not frame
   this as a missing step the user must complete.

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
3. `CHANGELOG.md`는 init이 만들므로 보통 이미 있다. hi-vibe를 깔기 전부터
   있던 프로젝트라 없으면 `templates/CHANGELOG.md.tpl`로 만든다. 그 다음
   append under `## [Unreleased]` in the right category (Added / Changed /
   Fixed / Removed), one bullet per change, each bullet prefixed
   `YYYY-MM-DD HH:MM` (run `date`, never guess).
4. **`Fixed`는 증상과 원인을 같이 적는다.** 나머지 칸(Added/Changed/Removed)은
   "무엇이 바뀌었나"로 충분하지만, 버그 기록은 그것만으론 쓸모가 없다 —
   나중에 `recall`로 찾는 사람이 궁금한 건 "고쳤다"가 아니라 **"왜 그랬더라"**다.
   한 줄이라도 이 세 가지가 들어가게 쓴다:

   - **증상** — 무엇이 어떻게 잘못 보였나 (에러 메시지·재현 조건)
   - **원인** — 실제로 뭐가 문제였나. 증상과 원인이 다른 곳인 경우가 많다.
   - **왜 이 방법으로** — 다른 길을 버렸다면 그 이유. 없으면 생략해도 된다.

   예: `- 2026-07-29 14:20 로그인 후 새로고침하면 로그아웃됨 — 쿠키는 남아
   있는데 세션 검증이 UTC 기준이라 KST 자정 직후 만료로 판정. 서버 TZ를
   바꾸는 대신 검증 시점에 ZoneInfo를 명시(다른 곳도 같은 함정).`

   **원인을 모른 채 고쳤으면 모른다고 적는다.** 추측을 원인으로 쓰지 마라 —
   틀린 원인은 기록이 없느니만 못하다(다음 사람이 그걸 믿고 엉뚱한 데를 판다).
5. Do not renumber or edit released sections.

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
3. **Check whether the `.hi-vibe/` directory exists** — this is YOUR
   internal init check; do NOT lecture the user about the marker or the
   logic behind it.
   - **MISSING** → tell them in ONE short, plain sentence, in their
     language: "이 프로젝트엔 아직 hi-vibe가 설정 안 됐어요 —
     `/hi-vibe:init`을 한 번 돌려주세요." Nothing more — no "the marker
     is `.hi-vibe/`", no "CLAUDE.md/handover.md don't count". (Internally:
     an existing `CLAUDE.md` or the user's own `handover.md` does NOT mean
     initialized; only `.hi-vibe/` does — but the user never needs to hear
     this reasoning.)
   - **EXISTS** → say they can just code normally; it's already on.
4. **Always paste the GitHub URL as a real link** and tell them to read
   the README there — never just say "the plugin README":
   "자세한 건 https://github.com/jx-hxxx/hi-vibe 의 README.md를
   읽어보세요." / "For details, read the README at
   https://github.com/jx-hxxx/hi-vibe".

That's the whole welcome — a few lines, nothing more.

## Doc-sync contract (applies everywhere)

Structure changed (file added/moved/renamed, folder responsibility
changed) → the matching MODULE.md must be updated in the same turn.
A doc that lies is worse than no doc.

CLAUDE.md is touched only when something **not derivable from the code**
changed — a new constraint, a new pitfall, a decision worth recording, or
a new MODULE.md to point at. Moving a file is not one of those. Keeping a
folder listing in CLAUDE.md would mean editing it on every structural
change, which is exactly how it ends up lying.

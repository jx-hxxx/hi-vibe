<h1><img src="docs/images/hi-vibe-logo-v4.png" alt="hi-vibe" height="34"> &nbsp;👋</h1>

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇰🇷 **한국어로 읽기 → [README.ko.md](./README.ko.md)** · 🇬🇧 English continues below.

> **AI moves fast. Your project doesn't drift.**

A **vibe-coding seatbelt** that keeps Claude Code from rebuilding code that
already exists, papering over errors, and forgetting yesterday's decisions.

- **Before writing** — search for the existing implementation first
- **When Claude writes code** — flag common swallowed-error / secret patterns
- **Between sessions** — auto-record & restore requests, edited files, Git & test state
- **After finishing** — review the code and sync the docs

> **New here? Just remember these 3 things.**
> 1. Run the commands in [1-Minute Install](#1-minute-install), in order
> 2. Then code with Claude as usual
> 3. If something seems off, run `/hi-vibe:doctor`

> **Read this first:** hi-vibe is not a tool that automatically finds every bug.
> It's a set of working disciplines plus automatic safeguards that make the AI
> search for evidence, leave records, and verify — at the moments it tends to
> gloss over.

> **hi-vibe is built for Python projects.** All hooks, the scanner, and the tests
> are designed and validated for Python. JS/TS (`.js`·`.jsx`·`.ts`·`.tsx`) has only
> **limited (partial) support** — symbol / name-collision detection and oversized-file
> checks; core analysis like duplicate / near-duplicate detection is **Python-only**.
> **If JS/TS is your primary language, you'll get much less out of this tool.**

<details>
<summary><strong>Why is it built this way? (technical background)</strong></summary>

It's not just a prompt pack. With **5 real Claude Code hooks · 191 regression
tests · per-project activation · standard-library-only core features**, it puts
the checks, records, and verification that AI often skips right into your
workflow. See [Why is it trustworthy?](#why-is-it-trustworthy) for the details.

</details>

<details>
<summary><strong>Table of contents</strong></summary>

- [1-Minute Install](#1-minute-install)
- [What changes after install?](#what-changes-after-install)
- [How is this different from a prompt pack?](#how-is-this-different-from-a-prompt-pack)
- [Why is it trustworthy?](#why-is-it-trustworthy)
- [Docs it creates in your project](#docs-it-creates-in-your-project)
- [Structure check: check](#structure-check-check)
- [Optional quality gate: gate](#optional-quality-gate-gate)
- [Verify before and after writing code](#verify-before-and-after-writing-code)
- [Commands at a glance](#commands-at-a-glance)
- [Optional integrations](#optional-integrations)
- [Updates](#updates)
- [FAQ](#faq)
- [Verify it yourself](#verify-it-yourself)
- [Credits and license](#credits-and-license)

</details>

---

## 1-Minute Install

Run these commands in order inside Claude Code.

```text
/plugin marketplace add jx-hxxx/hi-vibe
/plugin install hi-vibe@hi-vibe-marketplace
/reload-plugins
```

Once installed, in each project folder where you want to use hi-vibe:

```text
/hi-vibe:init
/hi-vibe:doctor
```

That's it. From now on, code with Claude as usual in that project.

> **Install once (global); `init` per project.**
> `/plugin install` defaults to **user scope (global)**, so a single install makes
> the `/hi-vibe:` commands available in every project (no per-project reinstall).
> But the automatic features (error/secret detection, auto-handover, etc.) only run
> in folders where `/hi-vibe:init` created the `.hi-vibe/` marker.
> **It never touches other projects you didn't init** — even with a global install,
> that's the safety guard against hooks running where you don't want them. (So to use
> it in a new project, just `/hi-vibe:init` once in that folder.)

> Be sure to run `/reload-plugins`. Installing the plugin alone does not activate
> its commands and hooks in the current session.

### When do I run what?

| Situation | What to run | How often |
|---|---|---:|
| First install on your machine | marketplace → install → reload | Once |
| Start using it in a new project | `/hi-vibe:init` | Once per project |
| Confirm the init worked | `/hi-vibe:doctor` | Right after init, or when something's off |
| Curious about the structure | `/hi-vibe:check` | Whenever you need it |
| Need a lint / CI gate | `/hi-vibe:gate` | Optional, once per project |
| Everyday coding | Ask in natural language | Automatic, or a command when needed |

**Requirements:** Python 3.8+ and a `python3` command. On Windows, if there's no
`python3` command, create a `python` alias.

---

## What changes after install?

| When | What hi-vibe does | Guaranteed by |
|---|---|---|
| “Build me this feature” | Searches existing functions / files / types first | 🤖 AI |
| When Claude writes code via Write/Edit/MultiEdit | Detects new swallowed errors / hardcoded secrets | ⚙️ Machine |
| When the chat compacts | Auto-records recent requests, edited files, Git & test state into handover | ⚙️ Machine |
| Right after session start / compact / clear | Restores recent handover and working discipline | ⚙️ Machine |
| Session start (only when something's wrong) | Says so if hooks aren't running or CI keeps failing | ⚙️ Machine |
| “I'm done / review it” | Reviews code, edge cases, and doc sync | 🤖 AI |
| When a turn ends with unreviewed code | Holds the turn open and demands a review — you don't type anything | ⚙️ Machine detects + 🤖 AI performs |
| “Why did we do it this way before?” | Searches decision records in handover and archive | 🤖 AI |

**⚙️ Machine** is actually executed by Python hooks. It works regardless of
whether the AI remembers the instructions.

**🤖 AI** is Claude recognizing natural-language intent and running a skill.
**You don't type these day to day.** They aren't 100% guaranteed, though, so
it's worth knowing you *can* latch one by hand — `/hi-vibe:find` — when you
notice it didn't fire. That's an emergency handle, not a habit to build.

`review` doesn't even need the handle. The AI can trigger it from what you say,
but if it doesn't, the **Stop hook holds the turn open and demands one.**
A safeguard you have to remember isn't a safeguard.

To be exact: what the machine guarantees is **when a review gets demanded**;
the review itself is Claude's work. The hook can't tell whether it finished —
and since it won't block twice on the same change, an interrupted review just
passes. (Deliberate: repeating the same nag is how a guard gets ignored.)

---

## How is this different from a prompt pack?

> **Claude Code already has powerful built-ins — docs, memory, review, hooks.
> hi-vibe doesn't replace them.** It's a complementary layer that ties the
> steps Python vibe-coders often skip — searching for existing code, verifying
> runs, recording docs — into one lightweight workflow, and reinforces some of
> them with deterministic scripts (hooks, scanner).

Text rules can be forgotten or skipped by the AI. So hi-vibe splits its
safeguards into three layers.

1. **Docs automation** — records project structure and session context.
2. **AI discipline** — search before building, debug from the root cause, verify claims.
3. **Machine enforcement** — hooks and optional lint/CI run regardless of the AI's memory.

```text
Claude Code events
├─ PostToolUse ── swallowed-error / secret detection
├─ PreCompact ─── auto-record handover (just before a compact)
├─ SessionEnd ─── auto-record handover (/clear · closing the window)
├─ SessionStart ─ restore memory & discipline + flag dead hooks/CI
└─ Stop ───────── hold the turn and demand a review of unreviewed changes

Natural-language requests
├─ “build it” ─── search existing implementations
├─ “I'm done” ─── code & doc review
└─ “why?” ─────── search decision records

Optional machine gate
└─ gate ────────── lint · type · cyclic deps · CI
```

### Can't I just use CLAUDE.md or a linter?

Both are good tools, but they cover different ground.

| Approach | What it's good at | What's left uncovered |
|---|---|---|
| `CLAUDE.md` | Passing project rules to the AI | No session records, no instant code detection, no CI enforcement |
| Linter | Mechanically checks fixed code rules | Doesn't know design intent, past decisions, or existing features |
| hi-vibe | Connects docs · AI discipline · hooks · optional CI | Does not automatically detect every bug |

### Doesn't this overlap with Claude Code's built-ins?

**Quite a bit, yes.**

| Claude Code built-in | hi-vibe | What's different |
|---|---|---|
| `/init` (writes CLAUDE.md) | `init` | **Overlaps.** hi-vibe also creates `handover.md` and `CHANGELOG.md`, and turns the hooks on |
| auto memory | `handover.md` | Built-in memory is **Claude deciding what to keep**, stored under your Claude config. handover is **a script writing a fixed set** into the project right before a compact, on `/clear`, and when you close the window — readable by you, shareable with your team if you want |
| `/code-review` | `review` | **The purpose overlaps; the implementation does not** — hi-vibe never calls `/code-review`; it runs its own checklist and the `fresh-eyes` agent. See below |
| `/verify` | the run-verification checklist item | Overlaps. hi-vibe's side is closer to a rule: "don't claim it works because the tests passed" |
| `/doctor` | `/hi-vibe:doctor` | **Same name, different subject.** The built-in checks your CLI install and settings; this one checks hi-vibe's own hooks and scanner |
| (none) | instant swallowed-error / secret detection | You can write the hooks yourself, but it isn't built in |
| (none) | repo-wide duplicate / unreferenced scan | Python AST based. `check` |
| (none) | symptom-and-cause CHANGELOG | Claude will write one if you ask; there's no dedicated flow |

**The real difference is when things run.** From Claude Code's own docs:

> `/verify` and `/code-review` **run only when you invoke them.**
> Before v2.1.215, Claude could also run them on its own.

That automatic run is the thing that went away. With hi-vibe, **once a feature
is finished the conversation does not end until it has been through a review.**
Code that has already been reviewed is not examined again. Catching what you
forgot to run is the whole point of this plugin.

**The second difference is who does the looking.** The review has two layers.
First a checklist sweeps for **what got skipped** — errors swallowed in silence,
code never actually run, docs left stale — and whatever it finds is fixed on the
spot and re-checked. Then **a subagent that never wrote this code**
(`fresh-eyes`) judges **how well it was built**: over-engineering, simpler
routes, hidden coupling.

**hi-vibe does not press the built-in `/code-review` for you.** Nothing in this
repository calls it — the same purpose is served by **hi-vibe's own checklist and
its own agent**, because a Claude that has been in the conversation all along
does not properly doubt the code it just wrote. Holding the turn is where
hi-vibe's part ends; reading the code and judging is Claude's.

---

## Why is it trustworthy?

### 191 automated tests

They test handover recording / rotation / concurrent writes, the SessionStart ·
PreCompact · PostToolUse · Stop hooks, secret and swallowed-error detection,
Python / JS-TS symbol lookup, identical & near-duplicate functions, review-scope
caching, and false-positive regressions.

Tests run on GitHub Actions with Python 3.8, 3.9, and 3.12 — so the minimum
supported version (3.8) the README states is actually validated in CI.

### A doctor that doesn't just check files

Hooks fail silently so they never interrupt Claude Code. The downside: if Python
is missing or something is misconfigured, a disabled feature can go unnoticed.

Instead of only checking whether files exist, `/hi-vibe:doctor` actually runs the
5 hooks and the scanner and shows the result as ✅/❌.

**The automatic check is shallower than this.** What runs by itself when you
start coding only looks at three things: whether hi-vibe is on here, whether
the SessionStart hook's heartbeat is recent, and whether any `.env` is tracked
by Git. If SessionStart is alive, a broken PostToolUse or Stop hook can still
read as fine. **Run `/hi-vibe:doctor` yourself right after install, and
whenever something feels off.**

### Per-project opt-in

Installing hi-vibe doesn't make it intervene in every repository. Automatic
features only work in projects where you ran `/hi-vibe:init` and a `.hi-vibe/`
folder was created. Everywhere else it quietly does nothing.

### False positives managed as test assets

It won't tell you to delete code just because “there's no reference.”

- Framework entry points with decorators
- Test functions
- `export default` components
- Work-in-progress code still under development
- Symbols referenced by strings and dynamic calls

It distinguishes these false-positive cases, and when a new one is found it's
captured as a rule and a regression test. “Dead code” in a structure scan is
treated as a **candidate** to check — never a delete verdict.

### It doesn't overwrite your existing config

The optional `gate` feature first reads your existing eslint · ruff · mypy ·
import-linter config. It asks you, then merges only the missing settings — it
never arbitrarily replaces your existing thresholds and rules.

---

## Docs it creates in your project

`/hi-vibe:init` **starts lean** — it creates just three files: `CLAUDE.md`,
`handover.md`, and `CHANGELOG.md`. The rest appear on their own when they're actually needed, so a small
project never ends up with more management docs than code. (There's no
`--lite`/`--full` to pick — the docs simply grow with the code.)

| Doc | Role | When it's created |
|---|---|---|
| `CLAUDE.md` | What the code can't tell you — overview, constraints, pitfalls, rationale, commands (no folder listing) | at `init` |
| `handover.md` | Progress (auto-recorded) + decisions/context (you or the AI fill in) for the next session | at `init` |
| `folder/MODULE.md` | That folder's features, models, design, and caveats | when the folder grows complex / "document this folder" |
| `CHANGELOG.md` | Substantive changes and their reasons. For bug fixes, the **symptom and the cause** too | at init |

It doesn't cram everything into one file. `CLAUDE.md` stays thin project guidance,
and details live in each folder's `MODULE.md`.

### What's committed vs. gitignored

**Committed by default**

- `CLAUDE.md`
- `MODULE.md`
- `CHANGELOG.md`

**Added to `.gitignore` by default**

- `handover.md`, `handover-archive.md` — personal session records
- `.hi-vibe/` — hook and review state
- `.repo-xray/` — structure-scan cache

If you want to share handover with your team, remove those lines from `.gitignore`.

---

## Structure check: `check`

```text
/hi-vibe:check
```

A diagnostic command you run as often as you like once code has piled up.

**To clean up**

- Exactly identical functions **(Python only)**
- Function pairs ~90% similar in implementation **(Python only)**
- Symbols with no references found
- Name collisions **(JS/TS)**
- Oversized files

**Hardcoded secrets** (surfaced first when present; values are never shown)

The hook only sees code written through Write/Edit. Anything that arrives via
Bash slips past it, so **this scan is the only net**. Claude Code's hook
contract means we can't see every file change made inside a Bash call (we only
recognise the common writing commands), so the design is **don't trust the
real-time catch — let this repo-wide scan be the backstop**. You get the file, the line and the kind — never the value, not
even in the report. If it's intentional, mark that line with a
`hi-vibe: allow-secret` comment and both the hook and the scan skip it.

**"The only net" means the only one inside hi-vibe.** It matches common key
shapes with regexes; it is **not a replacement for a dedicated secret scanner**
like `gitleaks` or `trufflehog`. If a leaked key would really hurt, run one of
those as well — what this catches is the unmistakable case, and a clean result
here is not proof that the repo is clean.

**Left unfinished** (not to delete — to finish)

- Swallowed errors across the whole repo — the hook only sees code as it's
  written, so code from before you installed it, and code someone else wrote,
  is checked here for the first time
- Leftover TODO / FIXME
- Test files vs. modules (a summary, not a per-file list)

**And it doesn't just hand you the candidate list.** After the scan, the
`proof-eyes` subagent **opens the real code at each candidate**, rules on which
ones are real, filters out the false positives, and gives a one-line cleanup
direction. You get "3 real out of 12, 9 false positives" instead of "12 found".
It never deletes anything — the final call is yours.

It scans Python and JS/TS (`.js`, `.jsx`, `.ts`, `.tsx`) files, and shows the
actual scan scope whenever it says "not found".

> **Identical / near-duplicate function detection is currently Python-only (AST).**
> JS/TS support is limited to symbol / name-collision detection and oversized-file
> checks — it does not include duplicate or near-duplicate analysis.

It won't make structural claims without the scanner's JSON output. Near-duplicate
functions and unreferenced symbols are review leads — not a verdict that they're
semantically identical or safe to delete. Short, naturally similar functions — like
test setup boilerplate — can show up as "near-duplicate" even when they're fine, so
treat them as review leads, not reimplementation bugs.

> 💡 For example, this repo's own `audit.py` (the scanner) shows up as an
> oversized candidate under the 400-line threshold. But it's a cohesive
> single-responsibility file (scanning repo structure), so we chose to keep it.
> The scanner offers "take a look" candidates, not "delete this" verdicts — the
> judgment call is yours.

---

## Optional quality gate: `gate`

```text
/hi-vibe:gate
```

Run it once. It installs the local checkers and, **when the project is on
GitHub**, offers a push-time gate as well — there's no flag to choose between
them.

`check` is a **diagnostic** you run when needed; `gate` is a **standing gate**
you install once per project.

It checks the project's language and existing config, then lets you pick which
items you need.

- Python: ruff, mypy, import-linter
- JS/TS: eslint, TypeScript strict check, cyclic-dependency check
- GitHub Actions: block the build when checks fail on push and pull requests

It never forces you to turn everything on. For beginners it recommends starting
with local complexity and cyclic-dependency checks, and leaves strict types and
CI up to your project's situation.

---

## Verify before and after writing code

**You don't type these.** They fire while you code. The commands exist only as
a "run it right now" button.

### Before building: `find` — automatic

Triggered when you say "build me this feature". Before a new function / file /
type is created, it searches for an existing implementation first.

### After writing: `review` — automatic

When a turn ends with code you changed, the Stop hook holds the turn open and
asks Claude to review right there. It never nags twice for the same change.

**No flags.** Scope, depth and parallelism are decided from what actually
changed — a flag you have to remember is a feature that never runs.

- **Scope** — uncommitted Python/JS·TS code files (config/doc files and
  deletions excluded). Committed everything already? It steps down to your
  unpushed commits, then to the last commit, and tells you which it's looking
  at. Files you already reviewed and haven't touched since are skipped.
- **Depth** — a **new subagent** (fresh-eyes) that never wrote the code reviews
  the design with clean, unbiased eyes. This runs by **default**, not behind a
  flag. It's skipped only for changes too small to have a design (and it says so
  when it skips).
- **Parallelism** — for a large change it measures file count and changed lines,
  then splits the work across parallel reviewers, telling you it's doing so and
  that it costs more tokens. It doesn't stop to ask.

fresh-eyes looks for over-engineering, unnecessary features, hidden coupling,
and excessive abstraction that a checklist alone struggles to catch.

**To dial it back or narrow it, just say so** — "keep it light", "only the
login part". Nothing to memorise.

<details>
<summary>If you want to call them yourself</summary>

```text
/hi-vibe:find
/hi-vibe:review
```

Only needed when you want another look after committing everything, or in a
folder without `.hi-vibe/` where the hooks don't run.

</details>

---

## Commands at a glance

It looks like a lot, but **you only type three during setup and one day to day.**

**Once, during setup**

| Command | When | How often |
|---|---|---|
| `/hi-vibe:welcome` | You're unsure what any of this is | Optional |
| `/hi-vibe:init` | Start using it in this project | Once per project |
| `/hi-vibe:doctor` | Confirm the init worked | Once per project |
| `/hi-vibe:gate` | Install lint / type / cyclic-dep checks (optional) | Once per project |

**Day to day**

| Command | When |
|---|---|
| `/hi-vibe:check` | The codebase feels messy |

**Runs on its own** (the command is just a "run it right now" button)

| Command | What calls it |
|---|---|
| `/hi-vibe:review` | The Stop hook, when you have unreviewed code changes |
| `/hi-vibe:find` | The skill fires when you say "build me X" |
| `/hi-vibe:log` | The review checklist writes the CHANGELOG entry itself |
| `/hi-vibe:handover` | The PreCompact hook, just before the chat compacts |
| `/hi-vibe:recall` | Fires when you ask "why did we do it this way?" |

**Three moments write it automatically** — just before a compact (`PreCompact`),
on `/clear`, and when you close the window (`SessionEnd`). `/clear` throws the
conversation away rather than summarising it, so it is where a record matters
most; before v0.31.0 nothing was written there.

**Still not covered** — a hard kill, a crash, or a logout. Call
`/hi-vibe:handover` yourself if you need certainty. **Empty sessions write
nothing**, so hitting `/clear` right after opening does not pile up blank entries.

### Internal skill composition

Commands are easy buttons; the actual work is done by these skills.

| Skill | Linked commands | Role |
|---|---|---|
| `repo-xray` | `check` | Evidence-based repo structure analysis |
| `write-gate` | `find`, `review` | Pre- and post-write verification |
| `docs-keeper` | `init`, `handover`, `log`, `recall`, `welcome` | Docs & session-memory management |
| `guards-setup` | `gate` | lint · type · cyclic-deps · CI setup |
| `grounded-answers` | Auto-triggered from natural language | Prevents asserting external API · pricing · versions without checking |
| `root-cause-first` | Auto-triggered on bug work | Find the root cause before hiding it with a fallback |

---

## Optional integrations

hi-vibe's core features don't need the tools below. Add them only when you need them.

<details>
<summary><strong>context7 MCP — look up the latest official docs</strong></summary>

Helps look up the latest official docs instead of Claude's stale memory when
using an external library's API. Without context7 it falls back to web search,
and if it can't secure evidence it's instructed to flag the answer as an estimate.

A free API key is required. See the [context7 official guide](https://context7.com)
for details.

```text
claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key <your_key>
```

</details>

<details>
<summary><strong>claude-hud — show remaining context in the status line</strong></summary>

Shows remaining context and tokens in the status line. Pairs well with hi-vibe:
when context grows long and you run `/compact`, hi-vibe records handover just
before it.

```text
/plugin marketplace add jarrodwatts/claude-hud
/plugin install claude-hud@claude-hud
/reload-plugins
/claude-hud:setup
```

</details>

---

## Updates

### Auto-update recommended

`/plugin` → **Marketplaces** → `hi-vibe-marketplace` → **Enable auto-update**

New versions download automatically when Claude Code starts. To apply them, run
`/reload-plugins` or restart Claude Code.

<p align="center">
  <img src="docs/images/enable-auto-update.png" alt="Enable hi-vibe marketplace auto-update" width="640">
</p>

### Manual update

```text
/plugin marketplace update hi-vibe-marketplace
/plugin update hi-vibe@hi-vibe-marketplace
/reload-plugins
```

Updating the marketplace listing and replacing the plugin are separate steps. Run
the three commands in order, then check `/plugin` → Installed to confirm the
version bumped.

---

## FAQ

### I changed a hook setting but it didn't take effect

Hooks load at session start. Restart Claude Code. You can see the current load
state with `/hooks`.

### How do I confirm the hooks actually work?

Run `/hi-vibe:doctor`. It actually runs the SessionStart, PreCompact, PostToolUse,
Stop hooks and the repo-xray scanner and shows the result.

### Does it work automatically in other projects too?

No. It only works in projects where you ran `/hi-vibe:init` and a `.hi-vibe/`
folder exists.

### Won't handover.md keep growing?

When it passes 20 entries, the older half moves to `handover-archive.md`.
`/hi-vibe:recall` searches the current handover and the archive together.

It uses file locking so entries aren't lost when multiple Claude Code terminals
write at the same time. On Windows (no `fcntl`), the lock degrades to best-effort,
so concurrent-write safety is weaker.

### What if a detection is intentional code — how does it pass?

hi-vibe hook exceptions are marked as a code comment so the reason stays on that line.

```python
except OptionalDependencyError:
    pass  # hi-vibe: allow-swallow
```

```javascript
const token = "test-token-value"; // hi-vibe: allow-secret
```

Linter exceptions use each tool's standard way.

- ruff: `# noqa: RULE_CODE`
- eslint: `// eslint-disable-next-line rule-name`
- A rule that doesn't fit the whole project: disable it explicitly in the config file

Just telling the AI “this is fine” doesn't change a machine check's result. You
have to leave the exception in the code and config so the next session and your
teammates understand the intent.

### Does it overwrite my existing CLAUDE.md or CHANGELOG.md?

No. If a file already exists, it reads it first and confirms how to apply.
(For how `gate` handles existing lint config, see
[Why is it trustworthy?](#why-is-it-trustworthy).)

### Can I share handover with my team?

Yes. By default it's treated as a personal session record and added to
`.gitignore`, but to share it with your team, remove that ignore entry and commit.

---

## Verify it yourself

hi-vibe is a plugin that stops ungrounded claims. The project itself should be
verifiable through its public code and tests.

Paste the question and repo link below into Claude, Codex, or Gemini.

```text
https://github.com/jx-hxxx/hi-vibe

hi-vibe is a personal plugin an individual developer uses inside Claude Code.
Please judge it centered on whether hi-vibe actually helps MY project.

My repo (please inspect the real code if you can): [my project's GitHub link — if public, scan the real code and spell out concretely what hi-vibe finds in my project]

Judge how faithfully the scope the README promises is actually delivered in the real implementation.
Separate the confirmed strengths from the limits, and spell out what actually helps a core target like my project.

Evaluate:
1. Help for vibe coding
2. Product / technical design
3. Fit with my project, and who it fits less
4. Key strengths and limits
5. Test / automation reliability
6. Current maturity

- Install value for my project: /10
- Current maturity as a personal Claude Code plugin: /10
- Overall: /10

Judge fairly based on the actual implementation you verified, and say so for anything you couldn't verify directly.
```

---

## Credits and license

- Design inspiration: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) — the evidence-based principle of “no structural claims without a scan”
- License: [MIT](./LICENSE)

<h1><img src="docs/images/hi-vibe.png" alt="hi-vibe" height="34"> &nbsp;👋</h1>

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇰🇷 **한국어로 읽기 → [README.ko.md](./README.ko.md)** · 🇬🇧 English continues below.

> **AI moves fast. Your project doesn't drift.**

A **vibe-coding seatbelt** that keeps Claude Code from rebuilding code that
already exists, papering over errors, and forgetting yesterday's decisions.

- **Before writing** — search for the existing implementation first
- **While coding** — catch swallowed errors and hardcoded secrets on the spot
- **Between sessions** — record and restore progress automatically
- **After finishing** — review the code and sync the docs

It's not just a prompt pack. With **4 real Claude Code hooks · 75 regression
tests · per-project activation · standard-library-only core features**, it puts
the checks, records, and verification that AI often skips right into your
workflow.

> **Read this first:** hi-vibe is not a tool that automatically finds every bug.
> It's a set of working disciplines plus automatic safeguards that make the AI
> search for evidence, leave records, and verify — at the moments it tends to
> gloss over.

> **The primary language is Python.** The hooks, scanner, and tests are designed
> and validated around Python first. JS/TS (`.js`·`.jsx`·`.ts`·`.tsx`) is also
> supported via scanning, `gate`, and symbol lookup, but with narrower coverage
> and shallower validation than Python.

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
/hi-vibe:doctor
/hi-vibe:init
```

That's it. From now on, code with Claude as usual in that project.

> Be sure to run `/reload-plugins`. Installing the plugin alone does not activate
> its commands and hooks in the current session.

### When do I run what?

| Situation | What to run | How often |
|---|---|---:|
| First install on your machine | marketplace → install → reload | Once |
| Confirm the install worked | `/hi-vibe:doctor` | Right after install, or when something's off |
| Start using it in a new project | `/hi-vibe:init` | Once per project |
| Curious about the structure | `/hi-vibe:check` | Whenever you need it |
| Need a lint / CI gate | `/hi-vibe:gate --ci` | Optional, once per project |
| Everyday coding | Ask in natural language | Automatic, or a command when needed |

**Requirements:** Python 3.8+ and a `python3` command. On Windows, if there's no
`python3` command, create a `python` alias.

---

## What changes after install?

| When | What hi-vibe does | Guaranteed by |
|---|---|---|
| “Build me this feature” | Searches existing functions / files / types first | 🤖 AI |
| The moment code is written | Detects new swallowed errors / hardcoded secrets | ⚙️ Machine |
| When the chat compacts | Auto-records current progress into handover | ⚙️ Machine |
| Right after session start / compact / clear | Restores recent handover and working discipline | ⚙️ Machine |
| “I'm done / review it” | Reviews code, edge cases, and doc sync | 🤖 AI |
| When a session ends after real changes | Reminds you of a missing CHANGELOG entry | ⚙️ Machine |
| “Why did we do it this way before?” | Searches decision records in handover and archive | 🤖 AI |

**⚙️ Machine** is actually executed by Python hooks. It works regardless of
whether the AI remembers the instructions.

**🤖 AI** is Claude recognizing natural-language intent and running a skill.
Powerful, but not 100% guaranteed. If you want it for sure, call the command
directly — e.g. `/hi-vibe:find`, `/hi-vibe:review`.

---

## How is this different from a prompt pack?

Text rules can be forgotten or skipped by the AI. So hi-vibe splits its
safeguards into three layers.

1. **Docs automation** — records project structure and session context.
2. **AI discipline** — search before building, debug from the root cause, verify claims.
3. **Machine enforcement** — hooks and optional lint/CI run regardless of the AI's memory.

```text
Claude Code events
├─ PostToolUse ── swallowed-error / secret detection
├─ PreCompact ─── auto-record handover
├─ SessionStart ─ restore memory & working discipline
└─ Stop ───────── CHANGELOG / review reminder

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

---

## Why is it trustworthy?

### 75 automated tests

They test handover recording / rotation / concurrent writes, the SessionStart ·
PreCompact · PostToolUse · Stop hooks, secret and swallowed-error detection,
Python / JS-TS symbol lookup, identical & near-duplicate functions, review-scope
caching, and false-positive regressions.

Tests run on GitHub Actions with Python 3.9 and 3.12. (Supported version is
Python 3.8+; CI validates against 3.9 and 3.12.)

### A doctor that doesn't just check files

Hooks fail silently so they never interrupt Claude Code. The downside: if Python
is missing or something is misconfigured, a disabled feature can go unnoticed.

Instead of only checking whether files exist, `/hi-vibe:doctor` actually runs the
4 hooks and the scanner and shows the result as ✅/❌.

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

Running `/hi-vibe:init` installs this documentation system.

| Doc | Role |
|---|---|
| `CLAUDE.md` | Whole-project map — overview, requirements, folder structure |
| `folder/MODULE.md` | That folder's features, models, design, and caveats |
| `handover.md` | Progress and decisions for the next session |
| `CHANGELOG.md` | Substantive changes and their reasons |

It doesn't cram everything into one file. `CLAUDE.md` stays a thin overall map,
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

- Scans Python and JS/TS (`.js`, `.jsx`, `.ts`, `.tsx`) files
- Finds exactly identical functions **(Python only)**
- Finds function pairs that are ~90% similar in implementation **(Python only)**
- Symbol candidates with no references found
- Name collisions **(JS/TS)**
- Files that grew too large, and structural issues
- Shows the actual scan scope when it says “not found”

> **Identical / near-duplicate function detection is currently Python-only (AST).**
> JS/TS support is limited to symbol / name-collision detection and oversized-file
> checks — it does not include duplicate or near-duplicate analysis.

It won't make structural claims without the scanner's JSON output. Near-duplicate
functions and unreferenced symbols are review leads — not a verdict that they're
semantically identical or safe to delete. Short, naturally similar functions — like
test setup boilerplate — can show up as "near-duplicate" even when they're fine, so
treat them as review leads, not reimplementation bugs.

---

## Optional quality gate: `gate`

```text
/hi-vibe:gate       # install local checkers
/hi-vibe:gate --ci  # local + GitHub Actions gate
```

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

### Before building: `find`

```text
/hi-vibe:find
```

Before you make a new function / file / type, it searches for an existing
implementation. The AI can run it automatically when you naturally ask “build me
this feature,” and you can call the command directly when you want to be sure.

### After writing: `review`

```text
/hi-vibe:review
/hi-vibe:review --all
/hi-vibe:review --deep
/hi-vibe:review --all --deep
```

- `review` — review the single feature you just built
- `review --all` — review everything that changed this session
- `review --deep` — a separate Claude that didn't write the code does a fresh-eyes review
- `review --all --deep` — review all changes through a separate Claude's eyes

`--all` skips files already reviewed and unchanged since. If the change is large,
it measures the file count and changed lines, then asks whether to review
sequentially or split in parallel.

`--deep` looks for over-engineering, unnecessary features, hidden coupling, and
excessive abstraction that a checklist alone struggles to catch — in a fresh
context.

---

## Commands at a glance

| Command | When to use it | Default trigger |
|---|---|---|
| `/hi-vibe:welcome` | You're new or unsure what to use | 🖐 Manual |
| `/hi-vibe:doctor` | Right after install, or when a hook seems off | 🖐 Manual |
| `/hi-vibe:init` | Activate docs & hooks in a new project | 🖐 Manual |
| `/hi-vibe:find` | Search existing implementations before a new feature | 🤖 AI / manual |
| `/hi-vibe:review` | Review code & docs after implementing | 🤖 AI / manual |
| `/hi-vibe:handover` | Hand off session progress | 🤖 AI / hook |
| `/hi-vibe:log` | Record substantive changes in CHANGELOG | 🤖 AI |
| `/hi-vibe:recall` | Search past decisions and reasons | 🤖 AI |
| `/hi-vibe:check` | Structure check: duplicates, unreferenced candidates, large files | 🖐 Manual |
| `/hi-vibe:gate` | Install lint · type · cyclic-deps · CI gates | 🖐 Manual |

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

Don't just summarize the README — inspect the actual hooks, scanner, skills, and tests on the current main branch to evaluate this Claude Code plugin.
If possible, run the tests yourself and report the results. For anything you couldn't verify directly, say so instead of guessing.

hi-vibe does not claim to be a professional static analyzer that catches every bug, or an enterprise quality platform.
It's a "seatbelt" plugin that backfills the habits vibe coders on personal / small projects with Claude Code tend to skip: searching for existing code, root-cause debugging, session handover, doc sync, and verification.

Judge it mainly on how well it implements the scope the README actually promises.
Conversely, clearly dock points where the real implementation is weaker than the README claims.

Evaluate the following, and give scores with reasons for any deductions:
1. Help for vibe coding
2. Product / technical design difficulty
3. Core target vs. who it fits less
4. Strengths and weaknesses
5. Test / automation reliability
6. Current maturity

- Install value for the core target: /10
- Current maturity as a dev tool: /10
- Overall: /10

This is not an evaluation meant to praise or criticize — judge fairly, based on the actual implementation.
```

---

## Credits and license

- Design inspiration: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) — the evidence-based principle of “no structural claims without a scan”
- License: [MIT](./LICENSE)

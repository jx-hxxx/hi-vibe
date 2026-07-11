# 👋 hi-vibe

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇰🇷 **한국어로 읽으시려면 → [README.ko.md](./README.ko.md)** &nbsp;·&nbsp; 🇬🇧 English continues below.

> **Floor it with AI — hi-vibe is your seatbelt.**

Vibe-coding is convenient, but AI-written code keeps repeating the same problems:

- 😵 Loses memory across sessions and **re-creates functions that already exist**
- 🩹 On errors, **band-aids with fallbacks** instead of finding the cause (so bugs hide silently)
- 🤷 Makes ambiguous decisions **on its own, without asking**
- 📊 States unverified numbers **as if they were official specs**
- 🗿 Dumps everything into one file, and **docs drift away from the code**

`hi-vibe` blocks all of these with three layers: **doc automation + AI discipline + machine enforcement.**

---

## Install

Run these three lines in order, inside Claude Code:

```
/plugin marketplace add jx-hxxx/hi-vibe        ← 1) register the marketplace
/plugin install hi-vibe@hi-vibe-marketplace    ← 2) install the plugin
/reload-plugins                                ← 3) apply it (required!)
```

> **Don't skip step 3, `/reload-plugins`.** Installing alone does NOT turn on
> the commands and hooks yet — this line activates them in the current session
> (no full Claude Code restart needed).

> **Requirement**: Python 3.8+ (the hooks need a `python3` command).
> On Windows without `python3`, create a `python` alias.

> **(Optional) context7 MCP — more accurate when present.** When your code
> touches an external library's API, `pre-write` fetches the **latest official
> docs** instead of relying on the AI's stale memory, preventing outdated code.
> **Not required** — without it, hi-vibe falls back to web search, and if that
> fails too, labels the answer as an estimate. To install it (free API key
> needed) follow the official guide → https://context7.com · Claude Code:
> `claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key <your_key>`

> **(Optional) claude-hud — if you want to watch your context usage.** It shows
> **remaining context / tokens** live in the status line. It pairs well with
> hi-vibe: watch how much context is left, and when there's room run `/compact`
> — hi-vibe auto-records handover right before that (so "keep context short +
> handover often" becomes visible). Install:
> ```
> /plugin marketplace add jarrodwatts/claude-hud
> /plugin install claude-hud@claude-hud
> /reload-plugins
> ```
> Then run `/claude-hud:setup` to enable the status line.

## First run

Once installed and applied, in order:

```
/hi-vibe:welcome   ← start here if you're not sure what to do
/hi-vibe:doctor    ← once after install: actually runs the hooks to verify they work
/hi-vibe:init      ← once per new project: installs the doc system + activates hooks
```

Run `init` **once per project (folder)** — inside the app folder where you want
to use hi-vibe. The marketplace/install/apply steps (the three lines above) are
done just once on your machine.

> Hooks are designed to **"fail silently"** so they never block Claude Code.
> The trade-off: if `python3` is missing they can be **silently off** — which is
> exactly why `doctor` runs the 4 hooks and the scanner for real to confirm.

Running `init` creates these 4 documents and activates the hooks for this project:

| Document | Role |
|---|---|
| `CLAUDE.md` | Project map — overview, requirements, folder map (keep it lean) |
| `<folder>/MODULE.md` | Per-folder design — features, models, gotchas |
| `handover.md` | Session handover — so the next session doesn't lose context |
| `CHANGELOG.md` | Substantive change history — what changed, and when |

## Occasionally, only when needed (optional)

```
/hi-vibe:audit          ← for repos with lots of existing code: find duplicates / god-files
/hi-vibe:guards --ci    ← install a linter (auto code checker) to machine-enforce quality
```

- **`audit`** — never guesses. It speaks only from the scanner's JSON evidence,
  and when saying "not found" it states the scan range. Scans Python + JS/TS
  (`.ts`/`.tsx`/`.jsx` included), and catches not just exact duplicates but
  also **"reimplemented ~90% the same"** function pairs (a classic AI mistake).
- **`guards`** — installs a linter (auto code checker) **after asking** (never
  overwrites existing config). Add `--ci` to also enforce it on GitHub (CI).

## After `init`, everything is automatic

In a project where you ran **`init`** (from "First run" above), everything below
runs on its own (hooks and doc automation are switched on by `init`). No need to
type commands in order — **just talk normally:**

| When you… | …this happens automatically |
|---|---|
| "make me this function" | **pre-write** — searches first for an existing one (prevents duplicate reimplementation) |
| "done / review it" | **post-write** — quality checklist + doc sync |
| "review the design" | **post-write --deep** — a clean-context AI (no memory of writing it) catches over-engineering / unneeded features |
| the moment code is written | **instant detection** of error-swallowing / hardcoded secrets |
| every compaction | **handover** auto-recorded (context preserved) |
| on a substantive change | **CHANGELOG** auto-recorded |
| session start / after compaction | latest handover + discipline auto-injected |

> The commands (`/hi-vibe:pre-write` etc.) are just "buttons for when you want to
> be explicit". Most of it fires on natural language.
> If a detected error-swallow / secret is **intentional**, add a
> `hi-vibe: allow-swallow` / `hi-vibe: allow-secret` comment on that line to pass.

> **(Optional) to auto-compact earlier** — Claude Code's built-in auto-compact
> fires when context is nearly full. Add `"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "30"`
> to the `env` in `~/.claude/settings.json` to auto-compact at 30% instead — and
> the handover auto-record above runs at that moment too. Note: this env var's
> effect **varies by model/environment** (per the official docs); after enabling,
> check that it actually fires at 30%.

## Commands at a glance

| Command | When | Fires |
|---|---|---|
| `/hi-vibe:welcome` | first time, or when unsure what to use | 🖐 manual |
| `/hi-vibe:doctor` | right after install, or when unsure hooks are running | 🖐 manual |
| `/hi-vibe:init` | once per project (installs the doc system) | 🖐 manual |
| `/hi-vibe:pre-write` | **before** creating a new function/file | ⚡ auto |
| `/hi-vibe:post-write` | **after** writing code (`--deep` = clean-eyes design review) | ⚡ auto |
| `/hi-vibe:handover` | session-end handover | ⚡ auto |
| `/hi-vibe:log` | record a substantive change in CHANGELOG | ⚡ auto |
| `/hi-vibe:recall` | "why did we do it this way before?" — search the records | ⚡ auto |
| `/hi-vibe:audit` | full structure checkup | 🖐 manual |
| `/hi-vibe:guards` | install a linter (auto code checker) — machine blocks bad code | 🖐 manual |

> **⚡ auto** = fires on its own from natural language ("make me…" / "done")
> or hooks (e.g. compaction). The command is just a button for when you want
> to be explicit.
>
> **🖐 manual** = you run the command yourself when needed (install / setup / diagnosis).

## Updating (when a new version ships)

**✅ Easiest — turn on auto-update once, then forget it:**

`/plugin` → **Marketplaces** tab → `hi-vibe-marketplace` → **Enable
auto-update**. After that, new versions are fetched automatically on every
start. You only run `/reload-plugins` (or just restart Claude Code) to apply
them — no need to type anything below.

**Manual (if auto-update is off)** — three steps **in order**. ①② are
separate: refreshing the list without swapping the plugin leaves you on the
old version (the most confusing part!).

```
/plugin marketplace update hi-vibe-marketplace   ← ① refresh the latest list
/plugin update hi-vibe@hi-vibe-marketplace       ← ② swap in the new plugin
/reload-plugins                                  ← ③ apply to the current session
```

- Verify: `/plugin` → Installed tab → check the **Version** bumped

## FAQ

**Q. I changed hook settings but nothing happened.**
Hooks load at session start. Restart Claude Code. Use `/hooks` to see load status.

**Q. How do I know hooks are actually running?**
`/hi-vibe:doctor` — it actually runs the 4 hooks and the scanner and shows ✅/❌.
Since hooks fail silently by design, this command is the only reliable check.

**Q. Do hooks run in other projects too?**
No. They only run in a project that has `handover.md` (= where you ran `init`);
elsewhere they quietly do nothing.

**Q. Won't handover.md grow forever?**
Past 20 entries, the older half auto-moves to `handover-archive.md`. Those
memories aren't lost — `/hi-vibe:recall` (or just asking "why did we do this
before?") searches the archive too and answers with date + source.

**Q. What gets created in my project?**
**Committed to GitHub**: `CLAUDE.md` / `MODULE.md` / `CHANGELOG.md` (project docs).
**Not committed**: `handover.md` · `handover-archive.md` (personal session log),
`.hi-vibe/` (hook state), `.repo-xray/` (scan cache). `init` adds these to
`.gitignore` automatically. (To share handover with a team, just remove that line
from `.gitignore`.)

## Credits / License

- Design inspiration: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) (MIT) — the prototype of evidence-based discipline ("no claim without a scan")
- License: [MIT](./LICENSE)

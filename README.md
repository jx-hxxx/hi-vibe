<h1><img src="docs/images/hi-vibe-logo-v4.png" alt="hi-vibe" height="34"> &nbsp;👋</h1>

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇰🇷 **한국어로 읽기 → [README.ko.md](./README.ko.md)** · 🇬🇧 English below.

A vibe-coding seatbelt that stops Claude Code from **rebuilding what already
exists, papering over errors, and forgetting yesterday's decisions.**

### 👉 [See what it does on the site](https://jx-hxxx.github.io/hi-vibe/)

Every command, how it works, the FAQ, and **the question you can paste into an
AI to check whether it fits your project** all live there. This file covers
**installing and using it**, nothing more.

---

## Install

Run these inside Claude Code, in order.

```text
/plugin marketplace add jx-hxxx/hi-vibe
/plugin install hi-vibe@hi-vibe-marketplace
/reload-plugins
```

Don't skip `/reload-plugins`. Installing alone does not attach the commands and
hooks to your current session.

## After installing, this is all of it

In the project folder where you want it:

```text
/hi-vibe:init      # turn it on for this project — once
/hi-vibe:doctor    # confirm it actually runs — once
/hi-vibe:check     # sweep the existing codebase — only when you want it
```

**After that there is nothing to memorise.** Build the way you already do, and
the review, the records and the search for existing code fire on their own.

> **Install once globally; `init` per project.** `/plugin install` defaults to
> user scope, so one install makes the `/hi-vibe:` commands available
> everywhere. The automatic features (hooks) only run in folders where `init`
> created the `.hi-vibe/` marker. **Projects you never ran `init` in are left
> completely alone.**

## What runs on its own

| When | What |
|---|---|
| Before you build | Say "build me X" and it **searches for an existing implementation first** |
| While Claude writes code | Flags errors swallowed in silence and secrets left in the source |
| Once a feature is done | **The conversation doesn't end until it has been reviewed** — a checklist plus a second Claude that never wrote the code |
| On compact, `/clear`, or closing | Leaves the next chat enough to pick up from in `handover.md` |
| When a new session starts | Reads that back, along with the project's own rules |

## Worth knowing

- **Built around Python and Claude Code.** For JS/TS it only checks symbols,
  name collisions and file size; the core analysis, like duplicate and
  near-duplicate detection, is Python-only.
- **hi-vibe sends nothing to a server of its own.** It makes no network calls at
  all (how Claude Code itself handles your data is Anthropic's policy, not this
  plugin's). That said, your last 5 requests (120 characters each) and the files
  you edited are written **in plain text** into `handover.md` inside the project
  (gitignored by default). Anything that looks like a secret is masked; ordinary
  sensitive information is not.
- **You can turn it off per project.** Tell Claude "turn hi-vibe off in this
  project", or `touch .hi-vibe/optout`. To remove it entirely,
  `rm -rf .hi-vibe .repo-xray` — **the documents it created stay.**
- **It does not replace a real security tool.** The secret check is a regex over
  common key shapes; if a leaked key would really hurt, run `gitleaks` too.
- **It does not find every bug.** It catches some of what you would otherwise
  have missed.

## More

- **[The site](https://jx-hxxx.github.io/hi-vibe/)** — every command · how it works · what gets recorded · FAQ · the fit-check question
- **[CHANGELOG.md](./CHANGELOG.md)** — what changed and why
- **If something breaks**, run `/hi-vibe:doctor` first. It actually executes the
  hooks and the scanner and tells you where it stopped.

## Credits & license

- Design inspiration: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) — the evidence-first principle of "no structural claims without a scan"
- License: [MIT](./LICENSE)

---
description: "hi-vibe 첫 안내. 뭘 써야 할지 모를 때 여기부터."
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/docs-keeper/SKILL.md`.

Mode: `welcome`
Arguments: $ARGUMENTS

Follow that mode exactly — **keep it short**: a 👋 greeting, one line on
what hi-vibe is, the one action (`/hi-vibe:init` in a new project, then
just code), and a README link for details — all in the **user's
language**. Do NOT enumerate the docs table, the full command list, or
hook internals (that overwhelms). If the current project has no CLAUDE.md
or handover.md yet, offer to run `/hi-vibe:init`.

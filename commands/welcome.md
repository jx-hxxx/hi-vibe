---
description: "hi-vibe first guide — start here when unsure what to use."
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/docs-keeper/SKILL.md`.

Mode: `welcome`
Arguments: $ARGUMENTS

Follow that mode exactly — **keep it short**, in the **user's language**:
a 👋 greeting, one line on what hi-vibe is, then two must-haves:
(1) if the `.hi-vibe/` directory is absent in this project (that's the
init marker), tell the user to run `/hi-vibe:init` — don't be fooled by an
existing CLAUDE.md or the user's own handover.md; (2) **paste the real
GitHub URL**
https://github.com/jx-hxxx/hi-vibe and ask them to read its README.md for
details. Do NOT dump the docs table, full command list, or hook internals.

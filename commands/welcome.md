---
description: "hi-vibe 첫 안내. 뭘 써야 할지 모를 때 여기부터."
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/docs-keeper/SKILL.md`.

Mode: `welcome`
Arguments: $ARGUMENTS

Follow that mode exactly — **keep it short**, in the **user's language**:
a 👋 greeting, one line on what hi-vibe is, then two must-haves:
(1) if `handover.md` (lowercase) is absent in this project, tell the user
to run `/hi-vibe:init` (don't be fooled by CLAUDE.md or uppercase
HANDOVER.md); (2) **paste the real GitHub URL**
https://github.com/jx-hxxx/hi-vibe and ask them to read its README.md for
details. Do NOT dump the docs table, full command list, or hook internals.

---
description: "Post-write review — checklist, clean-eyes design review, doc sync. No flags: scope, depth and parallelism are decided for you."
argument-hint: "[범위를 좁히고 싶을 때만: 예 \"로그인 쪽만\"]"
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/write-gate/SKILL.md`.

Mode: `review`
Arguments: $ARGUMENTS

Follow that mode exactly. There are no `--all` / `--deep` flags any more — the
skill decides scope, whether to spawn fresh-eyes, and whether to parallelize,
from what actually changed. If $ARGUMENTS names a narrower target
(e.g. "로그인 쪽만", "3일치"), honour it as the review scope.

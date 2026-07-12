---
description: "Post-write review checklist + doc sync (--all: batch-review the whole session's changes; --deep: clean-eyes design review)"
argument-hint: "[--all] [--deep]"
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/write-gate/SKILL.md`.

Mode: `review`.
- If `--all` is in $ARGUMENTS: run **`review --all`** mode — batch-review every
  changed area of this session, skipping files already reviewed and unchanged.
- If `--deep` is in $ARGUMENTS: after the checklist, also run `review --deep`
  (spawn the fresh-eyes agent).

Arguments: $ARGUMENTS

Follow that mode exactly.

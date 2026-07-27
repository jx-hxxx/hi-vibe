---
description: "Full repo scan — duplicates / unused / oversized / unfinished work, then a subagent verifies every candidate"
argument-hint: "[--root <repo>]"
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/SKILL.md`.

Run a full scan with
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/scripts/audit.py" scan --root <repo>`
(default `--root` = current project; honor `--root` in $ARGUMENTS if given),
then follow that skill's evidence contract — including spawning the
`proof-eyes` agent to open the real code at each candidate and rule on it
before anything reaches the user. Report what was filtered out, not just what
survived.

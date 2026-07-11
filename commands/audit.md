---
description: "Full repo structure scan — duplicates / unused candidates / oversized files, evidence-based"
argument-hint: "[--root <repo>]"
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/SKILL.md`.

Run a full scan with
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/scripts/audit.py" scan --root <repo>`
(default `--root` = current project; honor `--root` in $ARGUMENTS if given),
then answer strictly per that skill's evidence contract.

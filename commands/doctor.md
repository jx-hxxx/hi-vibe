---
description: "설치 자가진단 — 훅·스캐너가 실제로 작동하는지 실행으로 확인 (침묵 실패 탐지)"
argument-hint: "[--root <project>]"
---

Run:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py" --root <project>
```

(default `--root` = current project; honor `--root` in $ARGUMENTS if given)

Then relay the report to the user in kind, plain Korean — what works, what
is broken, and the exact next step for each ⚠️/❌ line.

Special case — if the command itself fails with "python3: command not
found" (or similar), that IS the diagnosis: every vibe-check hook is
silently disabled on this machine. Explain that, then guide the fix:

- macOS: `xcode-select --install` or `brew install python`
- Windows: install Python from python.org, then make a `python3` alias
  (e.g. PowerShell profile: `Set-Alias python3 python`), restart Claude Code
- Verify afterwards by running `/vibe-check:doctor` again

Never say "설정 완료" without the doctor actually passing — report the real
output (grounded-answers contract).

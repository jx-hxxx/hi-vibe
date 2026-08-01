---
description: "hi-vibe's own health check — actually runs hi-vibe's 4 hooks & scanner to catch silent failure. Not Claude Code's built-in /doctor (that one checks your CLI install)"
argument-hint: "[--root <project>]"
---

Run:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py" --root <project>
```

(default `--root` = current project; honor `--root` in $ARGUMENTS if given)

Then relay the report to the user in kind, plain language — **in whatever
language the user is speaking** (Korean if they use Korean, English if English).

**If the user seems to have meant Claude Code's built-in `/doctor`** — they ask
about the CLI install, auto-update failures, PATH problems, or CLAUDE.md
hygiene — say so in one line and point them there. This command only knows
about hi-vibe's own hooks and scanner. Two different commands with the same
name is confusing enough without us pretending otherwise.
**LEAD WITH THE CONCLUSION, not a wall of warnings:**

1. First line: is hi-vibe ITSELF healthy? (python3 + 훅 4종 + 스캐너가
   ✅면 "hi-vibe는 정상이에요"로 단언). ❌(실패)가 있을 때만 그걸 먼저.
2. Then the single next action in one line — usually just
   "이 프로젝트에서 쓰려면 /hi-vibe:init 하면 됩니다".
3. THEN, briefly and separately, list only what genuinely needs the
   user's DECISION (e.g. "gitignore 정비할까요?"). Frame "이 프로젝트"
   경고 as next-step guidance, NOT as defects — hi-vibe being fine and the
   project just needing init is the normal, expected result. Don't dump
   every ⚠️ line as a paragraph; keep it short and end with a clear
   "그래서 지금 /hi-vibe:init 하면 돼요" (or the relevant one action).

Special case — if the command itself fails with "python3: command not
found" (or similar), that IS the diagnosis: every hi-vibe hook is
silently disabled on this machine. Explain that, then guide the fix:

- macOS: `xcode-select --install` or `brew install python`
- Windows: install Python from python.org, then make a `python3` alias
  (e.g. PowerShell profile: `Set-Alias python3 python`), restart Claude Code
- Verify afterwards by running `/hi-vibe:doctor` again

Never say "설정 완료" without the doctor actually passing — report the real
output (grounded-answers contract).

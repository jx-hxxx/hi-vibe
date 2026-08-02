---
description: "hi-vibe's own health check — actually runs hi-vibe's 5 hooks & scanner to catch silent failure. Not Claude Code's built-in /doctor (that one checks your CLI install)"
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

이 명령은 보통 **`/hi-vibe:init` 다음에** 실행된다 — init으로 이 프로젝트에
hi-vibe를 켠 뒤, 그게 실제로 도는지 확인하는 자리다. 그러니 정상 결과는
"전부 ✅"이고, 그때는 **짧게 끝내라.**

1. First line: 이 프로젝트에서 hi-vibe가 제대로 도나? (python3 + 훅 5종 +
   스캐너 + 이 프로젝트 항목이 ✅면 "잘 돌고 있어요"로 단언). ❌가 있을
   때만 그걸 먼저.
2. **아직 init을 안 한 폴더라면** — 그건 결함이 아니라 순서가 바뀐 것이다.
   "이 폴더는 아직 안 켰어요. `/hi-vibe:init` 하면 됩니다" 한 줄로 끝내고,
   그 상태에서 나오는 다른 경고(gitignore·문서 누락)는 **init이 해결할
   것들이므로 나열하지 마라** — 겁줄 이유가 없다.
3. THEN, briefly and separately, list only what genuinely needs the
   user's DECISION (예: 추적 중인 `.env`가 있을 때). Don't dump every ⚠️
   line as a paragraph; keep it short and end with one clear next action.

Special case — if the command itself fails with "python3: command not
found" (or similar), that IS the diagnosis: every hi-vibe hook is
silently disabled on this machine. Explain that, then guide the fix:

- macOS: `xcode-select --install` or `brew install python`
- Windows: install Python from python.org, then make a `python3` alias
  (e.g. PowerShell profile: `Set-Alias python3 python`), restart Claude Code
- Verify afterwards by running `/hi-vibe:doctor` again

Never say "설정 완료" without the doctor actually passing — report the real
output (grounded-answers contract).

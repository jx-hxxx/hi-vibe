---
description: "저장소 구조 전체 스캔 — 중복/미사용 후보/비대 파일을 증거 기반으로"
argument-hint: "[--root <repo>]"
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/SKILL.md`.

Run a full scan with
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/scripts/audit.py" scan --root <repo>`
(default `--root` = current project; honor `--root` in $ARGUMENTS if given),
then answer strictly per that skill's evidence contract.

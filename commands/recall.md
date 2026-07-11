---
description: "기억 검색 — 과거 결정/작업을 handover·CHANGELOG 기록에서 찾아 출처와 함께 답한다"
argument-hint: "[궁금한 것: 예) 시세 API 왜 폴링으로 바꿨지]"
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/docs-keeper/SKILL.md`.

Mode: `recall`
Arguments: $ARGUMENTS

Follow that mode exactly. If $ARGUMENTS is empty, ask the user what past
decision or work they want to look up (one short question).

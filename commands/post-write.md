---
description: "코드 작성 후 리뷰 체크리스트 + 문서 동기화 검사 (--deep: 깨끗한 눈의 설계 리뷰 추가)"
argument-hint: "[--deep]"
---

Read `${CLAUDE_PLUGIN_ROOT}/skills/write-gate/SKILL.md`.

Mode: `post-write` (if `--deep` is in $ARGUMENTS, also run the
`post-write --deep` mode afterwards: spawn the fresh-eyes agent)
Arguments: $ARGUMENTS

Follow that mode exactly.

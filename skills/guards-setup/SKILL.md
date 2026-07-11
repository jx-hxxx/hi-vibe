---
name: guards-setup
description: >-
  Machine-enforced quality guards installer. Use for /hi-vibe:guards
  or when the user asks to 린트 설정, 타입 체크 강제, 순환의존 검사,
  CI 세팅, eslint/ruff/mypy 설정, complexity limit. Detects project
  language(s) and installs lint/type/cycle guards and optional CI —
  always asking before writing, always merging with existing configs.
---

# guards-setup

텍스트 규칙은 잊히지만 기계 게이트는 잊히지 않는다. 이 스킬은 규율의
절반을 린트/CI로 내려보낸다. 스니펫은 이 스킬의 `templates/`에 있다.

## 절차 (순서 엄수)

1. **감지**: `pyproject.toml`/`requirements*.txt`/`*.py` → Python;
   `package.json`/`tsconfig.json` → JS/TS; 둘 다면 둘 다.
2. **기존 설정 읽기**: ruff/mypy/eslint/import-linter 설정이 이미
   있으면 먼저 읽는다. 절대 덮어쓰지 않는다.
3. **묻기 (AskUserQuestion, 필수)**: 설치할 가드를 multiSelect로
   고르게 한다 — 항목별 효과를 한 줄씩. `--ci` 인자가 있거나 CI를
   원하면 워크플로 선택지도 포함.
4. **병합**: 스니펫의 키를 기존 설정에 정중히 병합. 사용자가 이미
   정한 값(예: 기존 max-complexity)은 유지하고 차이만 보고.
5. **실측 검증 (grounded-answers 계약)**: 설치 후 도구를 실제로 한 번
   실행해 실제 출력을 보여준다. "될 겁니다"가 아니라 실행 결과로 보고.
   위반이 쏟아지면 — 기준을 낮추지 말고, 상위 N개 위반을 보여주고
   점진 적용(기존 코드는 경고, 새 코드는 에러)을 제안한다.

## 가드 목록

**Python** (`templates/ruff-snippet.toml`, `mypy-snippet.toml`,
`importlinter-snippet.toml`):
- ruff: C901 복잡도 ≤10, PLR0913 인자 수, E/F 기본
- mypy: strict (입문자 프로젝트면 단계 적용 제안)
- import-linter: 레이어 계약 — CLAUDE.md 폴더 지도에서 레이어를
  추론해 초안을 만들고 사용자와 확인. 순환·경계 위반 시 실패.

**JS/TS** (`templates/eslint-snippet.jsonc`,
`package-scripts-snippet.json`):
- eslint: complexity 10, max-depth 3, max-lines-per-function 60,
  max-params 4
- dpdm: `npm run check:cycles` — 순환 의존 발견 시 exit 1
- TS면 tsconfig `strict: true` 확인, `as any` 금지 규칙

**CI** (`templates/github-actions-vibe-guards.yml`):
- push/PR마다 위 가드 전부 실행. 순환·경계 위반 = 빌드 실패 (d-2).

**정기 감사** (`templates/github-actions-biweekly-audit.yml`):
- 격주 cron. 직전 `audit/*` 태그 이후 코드 변경(문서 제외)이 없으면
  스킵. 변경이 있으면 CI에서 Claude Code가 repo-xray 스캔 + 구조
  리뷰 체크리스트를 돌려 보고서를 만들고 GitHub 이슈로 게시.
- 설치 시 안내할 것: ① `claude setup-token`으로 구독 OAuth 토큰 발급
  → 저장소 Settings > Secrets에 `CLAUDE_CODE_OAUTH_TOKEN` 등록
  ② Settings > Actions > Workflow permissions를 "Read and write"로.

## Red Flags

- 사용자 확인 없이 설정 파일을 쓰는 것
- 기존 설정 값을 스니펫 값으로 덮는 것
- 도구를 실행해보지 않고 "설정 완료"라고 보고하는 것
- 위반이 많다고 임계값을 올려서 통과시키는 것 (root-cause-first 위반)

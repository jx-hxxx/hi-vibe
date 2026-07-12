---
name: guards-setup
description: >-
  Machine-enforced quality guards installer. Use for /hi-vibe:gate
  or when the user asks to 린트 설정, 타입 체크 강제, 순환의존 검사,
  CI 세팅, eslint/ruff/mypy 설정, complexity limit. Detects project
  language(s) and installs lint/type/cycle guards and optional CI —
  always asking before writing, always merging with existing configs.
---

# guards-setup

> **답변 언어**: 이 지침은 한국어로 쓰였지만, **출력은 항상 사용자가 대화에서 쓰는 언어**를 따른다 (한국어→한국어, 영어→영어). 기존 문서·코드에 언어가 있으면 그쪽을 우선한다.

텍스트 규칙은 잊히지만 기계 게이트는 잊히지 않는다. 이 스킬은 규율의
절반을 린트/CI로 내려보낸다. 스니펫은 이 스킬의 `templates/`에 있다.

## 절차 (순서 엄수)

1. **감지**: `pyproject.toml`/`requirements*.txt`/`*.py` → Python;
   `package.json`/`tsconfig.json` → JS/TS; 둘 다면 둘 다.
2. **기존 설정 읽기**: ruff/mypy/eslint/import-linter 설정이 이미
   있으면 먼저 읽는다. 절대 덮어쓰지 않는다.
3. **묻기 (AskUserQuestion, 필수)**: 설치할 가드를 multiSelect로 고르게
   한다. 사용자는 대개 입문자다 — 아래를 지켜라.
   - **쉬운 말로.** 전문용어(complexity·max-depth·dpdm·exit 1·no-any·
     OAuth 등)를 앞세우지 말고, "이게 나한테 뭘 해주는지"를 한 줄로 먼저
     쓴다. 정확한 규칙값은 괄호로 뒤에 짧게. 예: "코드가 너무 길고
     복잡해지면 빨간불로 알려줘요 (함수 60줄·복잡도 10 넘으면)".
   - **추천 표시.** 로컬에서 외부 설정 없이 바로 되는 가드(복잡도 린트 +
     순환 의존 검사)를 **맨 앞에 두고 label에 "(추천)"**을 붙인다. 입문자
     기본값은 이 둘이면 충분하다 — GitHub도 토큰도 필요 없는 순수 이득.
   - **CI 가드**는 **GitHub 리모트(`git remote`)가 있을 때만** 추천으로
     올린다 — "GitHub에 올릴 때마다 자동 검문, 통과 못 하면 못 올려요
     (초반엔 답답할 수 있어요)". 리모트가 없으면 목록에서 빼거나 "나중에"로.
   - **격주 구조 감사**는 label에 "(고급)"을 붙이고, **켜기 전에 OAuth
     토큰 등록·Actions 권한 설정이 필요**하다고 설명에 미리 밝힌다. 처음이면
     나중에 해도 된다고 안내.
   - **"다 켜라"고 밀지 마라.** 4개 전부 체크된 기본값처럼 몰아가지 말고,
     입문자에겐 로컬 2종을 권하고 나머지는 필요해지면 그때 켜라고 말한다.
   - `--ci` 인자가 있으면 CI 선택지를 포함하되, 위 추천 원칙은 그대로.
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

## unused/dead 정리 주의 (미완성 코드 보호)

린트는 기본적으로 **검사만** 한다 — 코드를 자동으로 지우지 않는다. `--fix`
자동 수정도 보통 안 쓰는 import·지역 변수 수준이지, 함수 정의를 지우지
않는다. 그래도 lint의 unused나 audit의 dead 결과를 보고 코드를 **정리·삭제
하려 할 때는**, 먼저 그게 **미완성(WIP)** 코드인지 확인한다 — `pass`/`...`/
`NotImplementedError`/빈 본문/TODO·FIXME 주석. 미완성이면 "안 쓰는 것"이
아니라 "아직 안 만든 것"이므로 **지우지 말고 사용자에게 물어라**. 삭제는
언제나 사용자 확인 후 (repo-xray `looks_wip` 플래그·FP-07 참고).

## Red Flags

- 사용자 확인 없이 설정 파일을 쓰는 것
- 기존 설정 값을 스니펫 값으로 덮는 것
- 도구를 실행해보지 않고 "설정 완료"라고 보고하는 것
- 위반이 많다고 임계값을 올려서 통과시키는 것 (root-cause-first 위반)
- lint unused / audit dead를 보고 **미완성 코드를 확인 없이 지우는 것**

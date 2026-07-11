# Changelog

이 파일은 hi-vibe 플러그인 자체의 변경 이력입니다.
형식: [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) · 버전: [Semantic Versioning](https://semver.org/lang/ko/)

## [Unreleased]

### Fixed
- repo-xray 유사 중복 탐지가 파일 스캔 순서에 의존하던 비결정성 버그 (CI Linux에서만 실패, 로컬 macOS 통과). 원인: `difflib.SequenceMatcher`의 autojunk 휴리스틱이 두 번째 인자 기준이라 `ratio(a,b) ≠ ratio(b,a)`였고, `os.walk`의 OS별 파일 순서로 인자 순서가 뒤바뀌면 유사도가 0.997↔0.706으로 요동쳐 탐지 여부가 갈림. `autojunk=False`로 대칭성 확보 + 정렬 키를 `(길이, 파일, 줄번호)`로 완전 결정화. 순서 독립성 회귀 테스트 추가(44개).

### Changed
- 브랜딩: 👋를 인사·시작·환영 맥락에 도입 (README/문서 제목, doctor 출력 헤더, welcome 인사, 세션 시작 시 AI 인사). 경고 메시지엔 톤 유지 위해 미적용. README에 CI(GitHub Actions)·MIT·Python 배지 추가.

## [0.2.0] - 2026-07-10

### Added
- **PostToolUse 훅 `post_write_guard.py`**: Write/Edit/MultiEdit 직후 에러 삼킴 패턴(빈 except/pass, 빈 catch, 빈 `.catch()`)을 정규식으로 기계 감지해 Claude에게 root-cause-first 계약을 상기 — 규율의 기계 층. 의도된 삼킴은 `hi-vibe: allow-swallow` 주석으로 통과. Edit은 old_string 대비 "새로 늘어난" 삼킴만 경고.
- **비밀키 하드코딩 감지** (같은 훅): Anthropic/OpenAI/AWS/GitHub/Google/Slack/Stripe 키 형식 + 일반 시크릿 할당(`api_key = "..."` 류)을 코드·설정 파일(json/yml/toml 포함)에서 감지 — .env 이동과 (이미 커밋된 키는) 재발급 안내를 주입. `.env*` 파일은 올바른 위치이므로 검사 제외, 자리표시자(`YOUR_...`)·환경변수 참조 줄 제외, 가짜 키는 `hi-vibe: allow-secret` 주석으로 통과. 입문자 최다 보안 사고(키 커밋→과금 폭탄) 하나만 정조준하고 나머지 보안 분석은 관할 밖.
- **`/hi-vibe:doctor`** (`scripts/doctor.py`): 훅 4종·스캐너를 실제로 실행해 보는 자가진단 — "조용히 꺼진 안전벨트"(python3 부재 등 침묵 실패)를 드러냄.
- **repo-xray TypeScript 지원**: `.ts`/`.tsx`/`.jsx`/`.mts`/`.cts` 심볼 추출(함수·화살표 함수·class·interface·type·enum). `.d.ts`는 참조 텍스트로만 취급.
- **repo-xray 유사 중복 탐지** (`near_duplicate_functions`): 정규화 AST(함수명·데코레이터·docstring·지역 변수명 제거) 기준 90% 이상 유사한 함수 쌍 — "90% 비슷하게 재구현"하는 전형적 AI 실수를 포착. 완전 중복 탐지도 변수명이 달라도 잡도록 개선.
- **기억 검색 `/hi-vibe:recall`** (docs-keeper의 5번째 모드): "예전에 왜 이렇게 했지?" 질문에 기억이 아니라 기록으로 답함 — handover/아카이브/CHANGELOG를 검색어 변형(한/영/코드명) 2~3회로 Grep, 걸린 항목 전체를 읽고 날짜·출처 인용 필수, 못 찾으면 검색 범위 명시(부재 계약). 명령어 없이 "저번에 뭐까지 했더라" 같은 질문에도 자동 발동.
- **fresh-eyes 에이전트 ("남의 눈" 설계 리뷰)**: `/hi-vibe:post-write --deep` 시 깨끗한 컨텍스트의 서브에이전트를 소환 — 과잉 설계·스코프 크립·더 단순한 대안·숨은 결합 등 정규식/체크리스트가 못 잡는 판단 영역만 검토. 작성자 편향 차단을 위해 설계 이유는 전달하지 않고 요구사항+변경 파일만 전달. 근거(file:line) 없는 지적 금지, 최대 5건, "남의 눈 판정: 통과/재고 권장 N건" 형식. 별도 API·비용 없이 세션 내 서브에이전트로 동작.
- **repo-xray 오탐 인덱스** (`references/false-positive-index.md`): 스캐너가 속는 알려진 방식 9종(프레임워크 등록, 동적 호출, 미스캔 파일, 공개 API, 테스트 유사중복 등)과 각각의 완화 화법을 문서화. 판정 제시 전 필수 경유지로 SKILL에 배선, 새 오탐 확인 시 "항목+회귀 테스트 추가" 규칙 포함. (구조는 lumin-repo-lens(MIT)에서 차용, 내용은 자체)
- **테스트 스위트** (`tests/`, 34개): 스캐너 계약(dead/doc_mentions/중복/TS)과 훅 4종의 동작·엣지케이스를 stdlib unittest로 검증. GitHub Actions CI (`.github/workflows/test.yml`, Python 3.9/3.12).

### Changed
- **repo-xray 테스트 파일 오탐 제거**: `test_*.py`/`*_test.py`/`conftest.py`/`*.test.ts` 등의 심볼은 dead 후보에서 제외 — 테스트 러너가 이름 규칙으로 호출하므로 참조 0이어도 살아 있음 (플러그인 저장소 자기 스캔에서 발견된 오탐).
- **repo-xray 문서/코드 참조 분리**: `.md`/`.css`의 이름 언급은 더 이상 dead 후보를 구제하지 못함(문서가 죽은 코드를 가리는 자기 간섭 버그 수정). 문서 언급은 `doc_mentions` 필드로 별도 보고 — 코드 삭제 시 함께 고칠 문서 목록으로 사용.
- **write-gate post-write 체크리스트 확장** (8→10항목): ⑦ 숨은 결합(전역 상태·초기화 순서·import 부수효과·fan-in 쏠림) 점검, ⑨ 실행 검증 필수("될 겁니다" 금지 — 실행해 관찰했거나, 못 했으면 그 사실과 이유 명시). 마지막 줄 계약이 "실행 검증 + 문서 동기화" 두 줄로. 비례 원칙 추가: 무관한 항목은 "해당 없음" 한 마디로 통과(필수 2개는 항상 답변) — 형식적 도배·통째 생략 방지.
- write-gate pre-write: "외부 API 근거 확인" 단계 추가 (2단계, 총 5→6단계) — 외부 라이브러리 API를 쓰는 코드는 기억이 아니라 context7 MCP(연결 시) 또는 공식 문서(WebFetch)로 확인 후 작성, 둘 다 불가하면 추정임을 명시.

## [0.1.0] - 2026-07-10

### Added
- 최초 릴리스: 문서 시스템(init/handover/log), 규율 스킬(root-cause-first, grounded-answers, write-gate), repo-xray 증거 스캐너, guards 기계 강제, PreCompact/SessionStart/Stop 훅.

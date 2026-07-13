# Changelog

이 파일은 hi-vibe 플러그인 자체의 변경 이력입니다.
형식: [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) · 버전: [Semantic Versioning](https://semver.org/lang/ko/)

## [Unreleased]

## [0.14.3] - 2026-07-13
<!-- show:ko **검증 강도가 이제 변경 크기에 비례해요 — 작은 일에 12분 안 걸려요.** 리뷰 체크리스트의 "실행 검증(필수)"이 변경 크기와 상관없이 늘 앱 구동·브라우저 실행을 요구하던 걸, 세 등급으로 나눴어요: 문서·포맷은 검증 없이 통과 / 패턴 복제·설정 한 줄 같은 작은 변경은 구문·서빙 확인만 / 로직·API·버그 수정만 실제 실행 관찰. 여기에 "최소 충분" 원칙을 못박아, 같은 걸 여러 화면폭·반복으로 다시 확인하거나 요청 범위 밖까지 파고드는 과잉검증을 금지했어요. hi-vibe가 작은 작업을 무겁게 만들던 지연의 근본 원인 제거. -->
<!-- show:en **Verification strength now scales with change size — small tasks don't take 12 minutes.** The review checklist's "run-verification (required)" used to demand running the app / a browser regardless of change size; it's now tiered: docs/formatting pass with no verification, small changes (pattern copies, one-line config) need only a syntax/serving check, and only behavior changes (logic/API/bug fixes) require observing a real run. A "minimum sufficient" rule forbids re-checking the same thing across widths/repeats or digging outside the request's scope. Removes the root cause of hi-vibe making small tasks slow. -->

### Changed
- **실행 검증을 등급제로** (write-gate `Mode: review` 9번) — 변경의 런타임 표면·크기에 비례해 검증한다. ①런타임 표면 없음(문서·주석·포맷·동작 동일 설정/이름변경) → 검증 불필요 ②작은·국소 변경(검증된 패턴 복제·script/설정 한 줄) → 구문·서빙 확인만 ③동작 변경(로직·API·스키마·새 기능·버그) → 실제 실행 관찰. "최소 충분 원칙"으로 여러 조건(화면폭·브라우저·반복) 재확인·범위 밖 검증을 명시 금지. 마지막 요약 줄도 "가벼운 검증"·"런타임 표면 없음" 종결 상태를 허용. 이전엔 크기 무관 "실행 검증(필수)"이라 3줄짜리 변경에도 앱·브라우저를 띄우게 만들던 지연의 근본 원인.
<!-- show:ko **첫 화면이 가벼워지고, 문서가 코드와 함께 자라요.** 초보자용 3줄 안내(설치→평소처럼 코딩→이상하면 doctor)를 README 맨 위로, "실제 훅 4종·84 tests·표준 라이브러리" 신뢰 문단은 접이식(왜 이렇게 만들었나요?)으로 내렸어요. init은 이제 CLAUDE.md·handover.md만 만들고 시작하고, MODULE.md는 폴더가 복잡해질 때·CHANGELOG.md는 첫 /hi-vibe:log 때 알아서 생겨요 — 작은 프로젝트가 코드보다 관리 문서가 많아지지 않게, 그것도 --lite/--full 같은 선택지 없이. 감지 범위 문구도 "저장하는 순간"→"Claude가 Write/Edit로 코드 쓸 때"로 좁혀 기대치를 정확히 맞췄어요. -->
<!-- show:en **The first screen got lighter, and docs grow with the code.** A 3-line beginner intro (install → code as usual → doctor if something's off) now sits at the top of the README; the "4 hooks · 84 tests · stdlib-only" trust paragraph folds into a details block. init now starts with just CLAUDE.md + handover.md — MODULE.md appears when a folder grows complex, CHANGELOG.md on the first /hi-vibe:log — so a small project never has more management docs than code, and with no --lite/--full to choose. Detection wording narrowed from "the moment you save code" to "when Claude writes code via Write/Edit," matching the real scope. -->

### Changed
- **init 지연 생성** — init이 문서를 한 번에 다 만들지 않고 `CLAUDE.md`·`handover.md`만 생성한다. `MODULE.md`는 그 폴더 설계가 처음 기록될 때(구조 변경 / `review`가 복잡하다고 판단 / 사용자 요청), `CHANGELOG.md`는 첫 `/hi-vibe:log` 때 생성. `--lite`/`--full` 플래그를 두지 않고 기본을 가볍게 — 초보자가 선택하지 않아도 문서가 코드와 함께 자란다. (docs-keeper SKILL init/log 모드, `CLAUDE.md` 템플릿의 없는 MODULE.md로의 dangling 포인터 방지.)

### Docs
- **첫 화면 경량화** — README(KO/EN) 맨 위에 초보자용 3줄. "실제 훅 4종·84 tests·표준 라이브러리" 신뢰 문단을 `<details> 왜 이렇게 만들었나요?`로 접음. Python 한정·"모든 버그를 자동으로 찾지 않음" 기대치 문구는 그대로 노출 유지.
- **감지 범위 문구 정직화** — "코딩 중 즉시 감지 / the moment you save code" → "Claude가 Write/Edit로 코드를 쓸 때 대표적인 에러 삼킴·비밀키 패턴 경고"로 좁힘(README·랜딩 KO/EN). 외부 에디터·터미널 저장까지 잡는 것처럼 읽히던 과장 제거.
- **랜딩 동기화** — `docs/index.html`의 문서 지도(지연 생성)와 기계 보장 목록(감지 범위)을 위 변경에 맞춤(KO/EN).

## [0.14.1] - 2026-07-13
<!-- show:ko **스캐너 신호가 깨끗해지고, README 문구가 구현에 딱 맞아졌어요.** 외부 감사 후속 다듬기: near-dup 리포트에서 테스트끼리 유사한 쌍(공통 setup·assert 보일러플레이트라 거의 재구현 버그 아님)을 별도 버킷으로 분리 — 요약이 "code N · test M"으로 나와 진짜 봐야 할 code↔code에 집중하게. 그리고 과장 소지가 있던 문구 4곳을 구현 범위에 맞게 좁힘(작성 순간→Write/Edit/MultiEdit, 진행상황→요청·파일·Git·테스트 상태, review --all 범위, Stop 메시지 코드→코드·설정). doctor의 Stop 판정 문구도 정직하게. -->
<!-- show:en **The scanner's signal got cleaner and the README now matches the implementation exactly.** Post-audit polish: near-dup pairs where both functions are tests (shared setup/assert boilerplate — almost never a real reimplementation bug) are split into a separate bucket, so the summary reads "code N · test M" and you focus on the code<->code pairs that matter. Four possibly-overstated phrases were narrowed to the real scope (moment written -> Write/Edit/MultiEdit, progress -> requests/files/Git/test state, review --all scope, Stop message code -> code/config). doctor's Stop wording is now honest too. -->

### Changed
- **near-dup 리포트: test↔test 쌍 분리** — 자기 스캔에서 near-dup 84개 중 상위 20개가 전부 테스트 함수끼리 유사(공통 보일러플레이트)라 초보자에게 "문제 84개" 인상을 줄 수 있었다. 이제 `_is_test_file` 기준으로 test↔test 쌍을 `near_duplicate_test_functions`(+`_total`) 버킷으로 분리하고, 요약을 `code N · test M`으로 출력. 숨기지 않고 우선순위만 낮춘다.
- **doctor Stop 문구 정직화** — "정상 종료 확인" → "실행 가능 확인 (빈 입력에 exit 0)". doctor는 Stop 훅에 빈 transcript를 넘겨 exit 0만 보므로, 실제 CHANGELOG 알림 발생까지 검증하지 않음을 정확히 표기.
- **Stop 알림 문구** — "코드 변경" → "코드·설정 변경"(.md/.txt/.rst 외 수정은 설정 파일도 포함되므로).

### Docs
- 과장 소지 문구를 구현에 맞게 좁힘 — "코드가 작성되는 순간"→"Write/Edit/MultiEdit으로 작성할 때", "진행상황 자동 기록"→"요청·수정 파일·Git·테스트 상태", `review --all` "변경 전체"→"미커밋 Python/JS·TS 코드 파일(설정·삭제 제외)" (KO/EN).

### Tests
- +3 (`_is_test_file` 분류 / test↔test 분리 버킷 / doctor Stop). run_guard 중복 정의 2개를 TempProject 부모로 통합(스캐너 exact-dup도 해소). 82→84.

## [0.14.0] - 2026-07-13
<!-- show:ko **handover에 이제 "다음 세션이 재개할 객관적 상태"가 남아요.** 자동 인수인계가 최근 요청·수정 파일만 적던 걸, git 상태(브랜치·수정/신규/삭제 개수)와 transcript에서 명확히 식별되는 테스트 결과(통과/실패 N)까지 기계로 추출해 남깁니다. "미해결 오류를 AI가 판정"하는 건 일부러 안 함 — 애매하면 조용히 생략(fail-open). 외부 감사가 반복 지적한 "핵심 약속(세션 사이 자동 기록)의 정보 밀도"를 정체성 안 깨고 보강. README엔 "Claude Code 내장 기능을 대체하지 않고 보완한다"는 포지셔닝도 명시. -->
<!-- show:en **handover now carries "objective state the next session can resume from."** The auto-handover used to record only recent requests and edited files; it now also mechanically extracts git state (branch, modified/new/deleted counts) and, when clearly identifiable in the transcript, the last test result (pass/fail N). It deliberately does NOT have the AI judge "unresolved errors" — if ambiguous, it's silently omitted (fail-open). This strengthens the info density of the core promise (auto-record between sessions) that audits repeatedly flagged, without breaking identity. README also states the positioning: hi-vibe complements Claude Code's built-ins, it doesn't replace them. -->

### Added
- **handover 자동 기록에 git·테스트 상태 추가** — PreCompact가 `_common.git_status()`(브랜치 + `git status --short` 요약)와 `_common.last_test_result()`(transcript의 테스트 명령·결과에서 명확한 pass/fail만)를 추출해 handover 항목에 남긴다. git 저장소가 아니거나 결과가 애매하면 조용히 생략(fail-open). 의미 판정 없이 재개용 객관적 상태만.
- **CI 매트릭스에 Python 3.8** — README 최소 지원(3.8)을 CI가 실제 검증(외부 감사 3회 지적).

### Docs
- **포지셔닝 명시** — README에 "Claude Code 내장 기능(문서·기억·리뷰·훅)을 대체하지 않고, Python 바이브 코딩 작업 흐름으로 묶어 보완한다"는 문단 추가(KO/EN).
- CI 테스트 버전 표기 3.9·3.12 → 3.8·3.9·3.12, audit.py oversized 자기 인정 한 줄, 저장소 CLAUDE.md 추가.

### Tests
- +4 (`last_test_result` 2 / handover의 git·테스트 상태 기록 / 비-git 생략). 78→82.

## [0.13.4] - 2026-07-13
<!-- show:ko **자기 검증 규율을 자기 저장소에 마저 지켜요.** 외부 AI 감사가 main이 red(테스트 1개 실패)임을 짚었어요. 두 가지 사각지대를 근본적으로 막음: (1) 무결성 테스트가 랜딩의 릴리스 타임라인(CHANGELOG 자동 복사본, 즉 역사 서술)까지 명령 참조로 오인하던 걸, SHOWCASE 마커 영역을 도려내 해결 — 실제 명령어 안내는 계속 검사. (2) showcase 봇 커밋의 [skip ci]를 제거해, 봇이 생성한 docs가 테스트를 깨도 CI가 잡게 함(무한루프 없음 확인). -->
<!-- show:en **The self-verification discipline now holds on our own repo too.** An external AI audit caught main being red (1 failing test). Two blind spots fixed at the root: (1) the integrity test was mis-reading the landing's release timeline (an auto-copied CHANGELOG history) as live command references — now the SHOWCASE-marked region is excised, while real command guidance is still checked. (2) Removed [skip ci] from the showcase bot commit so a bot-generated docs change that breaks tests is caught by CI (verified: no trigger loop). -->

### Fixed
- **main red — 무결성 테스트 오탐** — `test_all_command_references_exist`가 랜딩(`docs/index.html`)의 SHOWCASE 타임라인(CHANGELOG에서 자동 복사된 역사 서술)에 남은 옛 `/hi-vibe:audit` 문자열을 현재 명령 참조로 오인해 실패. 명령 참조 검사에서 `<!--SHOWCASE:*-start/end-->` 영역을 제외(역사 서술이므로). 명령어 표 등 실제 안내는 그대로 검사 — 가짜 명령은 여전히 잡힌다(테스트로 확인).
- **CI 사각지대 — showcase 봇 커밋의 `[skip ci]`** — 봇이 생성한 `docs/index.html`이 테스트를 깨도 그 커밋에서 CI가 안 돌던 문제. `[skip ci]` 제거. showcase는 `CHANGELOG.md`/`build-showcase.py`에만, release는 `plugin.json`에만 트리거되므로 docs-only 봇 커밋은 test.yml만 추가로 돌리고 재트리거 루프는 없다.

## [0.13.3] - 2026-07-13
<!-- show:ko **깨진 명령 참조를 잡고, 문서-현실 어긋남을 테스트로 막아요.** 외부 AI 감사가 찾은 실제 결함: 선택형 격주 감사 템플릿이 존재하지 않는 `/hi-vibe:audit`을 호출했어요(→ `/hi-vibe:check`로 수정). 재발 방지로 무결성 테스트 2개 추가 — 모든 `/hi-vibe:<명령>` 참조가 실재하는지, README·랜딩이 광고하는 "자동 테스트 N개"가 실제 개수와 같은지 CI에서 강제. 테스트 수도 75→78로 동기화. -->
<!-- show:en **Broken command reference fixed, and doc-vs-reality drift is now caught by tests.** A real defect found by an external AI audit: the optional biweekly-audit template invoked a non-existent `/hi-vibe:audit` (fixed to `/hi-vibe:check`). Two integrity tests now enforce in CI that every `/hi-vibe:<command>` reference resolves to a real command, and that the "N automated tests" advertised in the README/landing matches the actual count. Test count synced 75→78. -->

### Fixed
- **격주 감사 템플릿의 존재하지 않는 명령 참조** — `guards-setup`의 `github-actions-biweekly-audit.yml`이 `/hi-vibe:audit`(미존재)를 호출하던 것을 `/hi-vibe:check`로 수정. (감사 지적: 이 옵션 기능은 그대로 설치하면 신뢰 불가였음)

### Added
- **저장소 무결성 테스트(`test_integrity.py`)** — (1) 활성 파일의 모든 `/hi-vibe:<명령>` 참조가 `commands/`에 실재하는지 검증(옛 `audit` 오타류 재발 차단), (2) README·랜딩의 광고 테스트 수가 실제 `def test_` 수와 일치하는지 강제(숫자가 조용히 낡는 것 방지). 문서-코드 동기화 철학을 자기 저장소에 기계로 적용.

### Docs
- README·랜딩 테스트 수 75 → 78 동기화.

### Tests
- +2 (명령 참조 무결성 / 광고 테스트 수 동기화). 76→78.

## [0.13.2] - 2026-07-13
<!-- show:ko **비밀키를 다른 비밀키로 바꿔치기해도 이제 잡아요.** 외부 AI 감사가 재현한 탐지 공백: PostToolUse 가드가 old/new의 위험 패턴 "개수"만 비교해서, 기존 하드코딩 시크릿 하나를 다른 시크릿 하나로 교체하면(1→1, 개수 같음) 경고가 안 났어요. 비교를 개수→실제 매치 값(Counter 차집합)으로 바꿔 값이 다르면 잡게 함. 에러 삼킴 패턴도 같은 로직이라 함께 개선하고 회귀 테스트 추가. -->
<!-- show:en **Swapping one secret for a different one is now caught.** A detection gap reproduced by an external AI audit: the PostToolUse guard compared only the *count* of risky patterns in old vs new, so replacing one hardcoded secret with a different one (1→1, same count) produced no warning. The comparison is now value-based (Counter difference), so a different value is flagged. The swallowed-error path shares the logic and got the same fix, with a regression test. -->

### Fixed
- **비밀키·에러삼킴 스왑을 놓치던 탐지 공백** — `post_write_guard.py`가 `len(new) > len(old)` 개수 비교라, 기존 시크릿 1개를 다른 시크릿 1개로 교체하면(개수 1→1) 경고가 안 났다(감사 재현: `token="…OLD"` → `password="…NEW"` = exit 0, 무경고). `find_secrets`/`find_swallows`가 정규화된 매치 값을 반환하게 하고, 비교를 `Counter(new) - Counter(old)` 차집합으로 변경 — 값이 다르면(개수가 같아도) 새 위험으로 잡는다. 기존 시크릿을 그대로 옮기는 편집은 여전히 재경고 안 함.

### Tests
- +1 (시크릿 스왑=경고 회귀 테스트). 75→76.

## [0.13.1] - 2026-07-13
<!-- show:ko **MultiEdit로 편집해도 이제 진행상황에 기록돼요.** 외부 AI 감사에서 발견한 진짜 버그: PostToolUse 훅엔 MultiEdit가 등록돼 있어 에러·비밀키 감지는 됐는데, handover·Stop의 "변경 파일" 집계가 Write/Edit/NotebookEdit만 세서 MultiEdit로만 편집한 세션이 기록·CHANGELOG 알림에서 빠졌어요. 한 줄 수정 + 회귀 테스트로 막음. README도 review --all 범위(uncommitted)와 Python 전용/JS·TS 한정 지원을 더 정확히 명시. -->
<!-- show:en **MultiEdit changes now show up in progress records.** A real bug found via external AI audit: MultiEdit is registered on the PostToolUse hook (so error/secret detection worked), but the handover/Stop changed-file tally only counted Write/Edit/NotebookEdit — so a session edited only via MultiEdit fell out of the records and the CHANGELOG nudge. Fixed in one line + a regression test. README also clarifies review --all scope (uncommitted) and the Python-only / limited-JS·TS scope. -->

### Fixed
- **MultiEdit가 handover·Stop 변경 추적에서 누락되던 버그** — `_common.py`의 수정 tool 집계가 `("Write","Edit","NotebookEdit")`만 봐서 MultiEdit 편집이 빠졌다. `hooks.json`엔 MultiEdit가 PostToolUse로 등록돼 있어 에러·비밀키 감지는 됐지만, PreCompact handover 기록과 Stop CHANGELOG 알림의 "변경 파일" 판정에서 누락. `MultiEdit`를 집계 대상에 추가.

### Docs
- **`review --all` 범위 정정** — "이번 세션 전체" → "아직 커밋하지 않은(uncommitted) 변경 전체(커밋하면 범위에서 빠짐)". 실제 `review_scope.py` 동작(git diff vs HEAD)과 일치.
- **주 대상 언어 = Python 단정 명시 + JS/TS 한정 지원** — 중복·유사 함수 탐지는 Python(AST) 전용, JS/TS는 심볼·이름 충돌·파일 크기 점검만. 외부 AI 감사의 "JS/TS 과장" 지적 반영.
- 검증 프롬프트 통일(랜딩·README), 테스트 수 72→**75** 정정, 윈도우 파일잠금 best-effort 각주, near-dup 보일러플레이트 기대치, README 종합 개편(목차 등).

### Tests
- +0 (`test_parse_transcript`에 MultiEdit 케이스 추가). 75 유지.

## [0.13.0] - 2026-07-13
<!-- show:ko **repo-xray near-dup이 이제 몇 분이 아니라 몇십 초.** 함수 쌍마다 O(L²) 유사도 비교를 돌리던 걸 지문(shingle) 선필터로 바꿔, 완전탐색과 '똑같은' 결과를 훨씬 빠르게(측정: 14분→30초, ratio 호출 5750→213). 상위 20개만 보여주던 near-dup 리포트도 총 개수를 함께 알려 정직하게. 그리고 "느리다=고장"이라 단정하고 죽였다 다시 돌리는 실패를 막는 규율을 grounded-answers에 추가 — 실제로 이 규칙을 어긴 사례에서 나온 개선. -->
<!-- show:en **repo-xray near-dup now takes tens of seconds, not minutes.** The O(L^2) similarity call that ran on every function pair is now gated by a shingle fingerprint prefilter — identical results to the exhaustive scan, far faster (measured: 14min→30s, ratio() calls 5750→213). The near-dup report, which showed only the top pairs, now also reports the true total so nothing is hidden. And a discipline was added to grounded-answers against the "slow == broken, kill-and-retry" failure — born from a real case of breaking that very rule. -->

### Fixed
- **repo-xray near-dup 성능 근본 수정** — 함수 쌍마다 O(L²) `difflib.ratio()`를 부르던 게 중간 규모 저장소(수백 함수)에서 수 분~수십 분. 각 함수를 shingle(k=9) k-gram으로 **1회 지문화**하고 Jaccard로 선필터(`jaccard_floor=0.45` — 완전탐색 대비 진짜 near-dup 최소 유사도 0.71에 여유), 통과한 소수만 정확 `ratio()`로 확인. 측정: ratio() 호출 5750→213, 완전탐색과 **결과 동일**(정답 대조: 가짜 0·놓침 0). near-dup에 60초 wall-clock backstop을 둬 어떤 입력에도 폭주 불가(넘으면 `truncated` 표시).

### Changed
- **near-dup 리포트 정직한 캡** — 탐지(`find_near_duplicates`)는 전체를 반환하고 리포트는 상위 20개만 **표시**하되, `near_duplicate_total`로 실제 총 개수를 노출(요약도 "20 of 24"). 상위 N개로 자르는 것과 조용히 버리는 것을 분리.
- **grounded-answers: 진단·상태 판단도 근거 필요(Part 3)** — "멈췄다/무한/고장"은 1회 실측 없이 단정 금지, 확인 전 파괴적 재시도(죽이고 재시작·프로세스 겹치기) 금지, 성능은 계측으로 원인 특정 후 수정. (실제로 repo-xray가 느릴 때 이 규율을 어겨 상황을 키운 사례에서 나온 개선.)
- **repo-xray 실행 시간 안내** — SKILL에 "느린 것≠멈춘 것: 수십 초 걸릴 수 있으니 백그라운드로 기다려라, 타임아웃으로 끊고 재실행 금지" 추가. 큰 함수끼리도 진짜 near-dup이 있어 **size-cap이 아니라** 지문 선필터로 비용을 줄이는 이유도 명시.

### Tests
- +3 (선필터=완전탐색 등가 / 탐지 비-캡: 21쌍 전부 반환 / 큰 함수 near-dup은 size-cap 금지). 72→75.

## [0.12.0] - 2026-07-12
<!-- show:ko **`review --all`이 큰 변경엔 "쪼개서 병렬"을 물어봐요.** 세션 변경이 크면(파일 여러 개 + 수백 줄) 순차 리뷰는 얕거나 느려요. 이제 규모를 기계가 재서, 크면 "쪼개서 병렬로 볼까요?"라고 묻고 — 예 하면 줄 수 균형이 맞은 그룹으로 나눠 리뷰어를 병렬 소환해요. 작으면 그대로 순차. (항상 병렬 아님 — 토큰·복잡도 방지.) -->
<!-- show:en **`review --all` now offers to split large diffs into parallel reviews.** When a session's changes are big (many files + hundreds of lines), sequential review goes shallow or slow. The machine now measures the size, and if it's large it asks "split into parallel reviews?" — yes fans out balanced groups to parallel reviewers; small stays sequential. (Not always parallel — avoids token/complexity blowup.) -->

### Added
- **`review --all` 대용량 병렬 옵션** — 세션 변경이 크면 순차 리뷰가 얕아지는 문제. 이제 `review_scope.py list`가 `sizes`(파일별 변경 줄 수)·`total_changed_lines`·`file_count`를 함께 주고, 규모가 크면 스킬이 **AskUserQuestion으로 "순차 vs 병렬"을 묻는다**. 병렬 선택 시 `review_scope.py chunk <N>`이 줄 수 기준 **균형 잡힌 파일 그룹 N개**를 만들고, 각 그룹마다 리뷰어를 병렬 소환해 결과를 통합.
- **임계값은 코드에 박지 않음** — 기계는 규모(숫자)만 주고, 병렬 여부 판단은 AI+사용자에게. (하드코딩 가드레일 금지 원칙.)

### Tests
- +3 (list의 sizes/total 보고 / chunk의 줄 수 균형 분할 / 파일 수보다 많은 버킷 요청 시 빈 버킷 없음). 69→72.

## [0.11.0] - 2026-07-12
<!-- show:ko **"확인 안 하고 단정" 방지를 더 강하게.** 라이브러리·API뿐 아니라 GitHub·npm 같은 외부 플랫폼의 "왜 이렇게 동작하나/정책 바뀌었나"도 근거 필요한 사실로 명시하고, context7(공식 문서 조회)를 근거 사다리 맨 앞에 못박음. 잡담·트러블슈팅이어도 예외 없음. (실제로 이 규율을 어긴 사례에서 나온 개선.) -->
<!-- show:en **Stronger "don't assert without checking".** Not just library/API facts — how an external platform (GitHub, npm) currently behaves or why (recent policy changes) now counts as a claim that needs evidence, with context7 (official-docs lookup) pinned as the first source. Applies in casual chat and troubleshooting too. (Came from a real case of breaking this very rule.) -->

### Changed
- **grounded-answers 범위 확장** — "라이브러리/API 동작"에 더해 **외부 플랫폼·서비스의 현재 동작·정책·제약**(예: GitHub·npm·클라우드 콘솔이 "왜 이렇게 동작하나", "정책이 바뀌었나")도 근거가 필요한 사실 주장으로 명시. 훈련 데이터로 단정 금지.
- **근거 사다리에 context7 명시** — 근거 확보 순서를 ①직접 실행 → ②**context7 MCP(공식 문서 질의)** → ③웹 검색/문서 fetch → ④"추정" 라벨로 구체화. 라이브러리·API·플랫폼 사실은 context7부터 확인하도록 못박음 (전엔 "공식 문서를 읽어라"만 있고 도구를 안 짚었음).
- **잡담·트러블슈팅에도 적용 명시** — 코딩 작업이 아니어도 사실 주장이면 예외 없음. Red Flags에 "외부 플랫폼 동작을 문서 확인 없이 추측", "context7 있는데 기억으로 답" 추가.

## [0.10.0] - 2026-07-12
<!-- show:ko **외국인이 써도 자연스럽게.** 출력 언어를 사용자가 대화에서 쓰는 언어에 맞춰요 — `review --deep`·`doctor`·세션 알림이 한국어에 고정돼 있던 걸 풀었고, 세션 알림은 한/영 병기로. (스킬 프롬프트는 한국어 그대로 — Claude가 한국어를 완벽히 읽어 실행하니 런타임 손해가 없어요.) -->
<!-- show:en **Natural for non-Korean users too.** Output now follows the language you speak — `review --deep`, `doctor`, and the session nudge no longer force Korean, and the nudge is bilingual. (Skill prompts stay Korean — Claude reads Korean at full fidelity, so there's no runtime cost.) -->

### Changed
- **언어 적응형 출력** — `write-gate`·`grounded-answers`·`root-cause-first`·`guards-setup` 스킬에 "출력은 사용자가 대화에서 쓰는 언어를 따른다(기존 문서 언어 우선)" 지침 한 줄씩 추가. 프롬프트 본문은 한국어 유지 — Claude가 그대로 실행하므로 번역 불필요.
- **fresh-eyes(`review --deep`) 출력 언어** — "출력 (한국어)" 고정 → 사용자 언어에 맞춰 라벨까지 번역.
- **`doctor` 리포트 언어** — "plain Korean" 고정 → 사용자 언어.
- **세션 알림 한/영 병기** — `stop_nudge`는 사용자에게 직접 보이는(`systemMessage`) 유일한 훅이라, 한국어 + 영어를 함께 표시. (나머지 훅은 `additional_context`라 Claude가 읽고 사용자 언어로 전달 — 이미 문제없음.)

### Tests
- 세션 알림 테스트에 한/영 병기 검증 추가. 69개 유지.

## [0.9.0] - 2026-07-12
<!-- show:ko **여러 기능을 한 번에 리뷰하는 `review --all`.** 한 세션에 기능을 여러 개 만들어도 "전체 리뷰해줘" 한 번으로 다 점검해요.<br>이미 봤고 그 뒤로 안 바뀐 코드는 자동으로 건너뛰고요. 세션당 1회 알림에서 이 기능을 살짝 알려줍니다. -->
<!-- show:en **New `review --all` reviews a whole session at once.** Build several features, then review them all with one command. Code you already reviewed and haven't changed since is skipped automatically. The once-a-session nudge quietly surfaces it. -->

### Added
- **`review --all` (세션 전체 일괄 리뷰)** — "이번 변경" 하나가 아니라, 세션에서 바뀐 코드 전체를 기능별로 한 번에 점검한다. 한 세션에 기능을 여러 개 만들어도 이 한 번으로 커버.
- **이미 리뷰한 것 건너뛰기** — 리뷰한 파일의 내용 해시를 `.hi-vibe/reviewed.json`에 저장해, 그 뒤로 안 바뀐 파일은 다음 `review --all`에서 자동으로 건너뛴다. 바뀌면 다시 걸린다. 커밋하면 자연히 범위에서 빠진다.
- **`review_scope.py` 헬퍼** — "무엇을 볼지·이미 본 것을 건너뛸지"를 코드로 정확히 계산(git diff + 해시 비교). AI가 해시를 세지 않는다 — 기계가 잘하는 건 기계에게.

### Changed
- **세션당 1회 넛지에 `review --all` 발견성 추가** — 코드 변경이 있었으면 CHANGELOG 안내와 함께 "전체 리뷰해줄까요?"를 딱 한 번 곁들인다. 강제 발동이 아니라, 기능이 있다는 걸 알려주는 것.

### Tests
- +5 (review_scope: 새 파일 감지 / mark 후 skip / 재수정 시 재등장 / 문서 제외 / 상태 파일 기록). 64→69.

## [0.8.0] - 2026-07-12
<!-- show:ko **명령어 이름을 쉬운 동사로.** pre-write→find, post-write→review, audit→check, guards→gate.<br>자동 명령어엔 "이 함수 만들어줘" 같은 트리거 예시를 표에 넣고, gate는 로컬/--ci 차이를 쉽게 설명. -->
<!-- show:en **Commands renamed to plain verbs.** pre-write→find, post-write→review, audit→check, guards→gate. Auto commands now show a trigger example, and gate explains local vs --ci clearly. -->

### Changed
- **명령어 이름 변경 (BREAKING)** — `pre-write`→**`find`**, `post-write`→**`review`**, `audit`→**`check`**, `guards`→**`gate`**. pre-write/post-write는 lumin-repo-lens와 겹치고 관례도 아니라, 전반을 "쉬운 동사"로 통일해 입문자 친화성을 높임. 내부 스캐너(`audit.py`)·스킬(`guards-setup`)은 그대로 유지.
- **명령어 표에 트리거 예시 추가** — 자동 명령어가 어떤 말에 발동되는지 표시. 예: `find` = "이 함수 만들어줘" 할 때, `review` = "다 했어 / 리뷰해줘" 할 때.
- **gate 설명 쉽게** — `gate`(로컬에 검사기 설치, 에디터가 표시) vs `gate --ci`(GitHub에도 관문 — 위반이면 빌드 실패, 통과 못 하면 못 올림)를 README·쇼케이스에 명확히.

## [0.7.0] - 2026-07-12
<!-- show:ko **경고에 "왜 위험한지" 교육 추가.** 비밀키는 위험한 이유를 항상 한 줄로 알려주고, 잦은 에러 삼킴은 짧게 짚되 자세한 설명은 물어볼 때만. 세션 시작엔 컨텍스트 관리 팁 한 줄. -->
<!-- show:en **Warnings now teach the "why".** Secrets always get a one-line reason; the frequent error-swallow stays terse and explains only when asked. Sessions open with a one-line context-management tip. -->

### Added
- **경고 교육 (혼합)** — 위험 코드 경고에 "왜 위험한지"를 상황에 맞게 붙인다. **비밀키**(드물고 치명적)는 왜 위험한지 한 줄을 **항상** 알리고, **에러 삼킴**(잦음)은 짧게 짚되 자세한 이유는 **사용자가 물어볼 때만**. 잔소리 없이 배우게 하는 게 목적.
- **컨텍스트 관리 팁** — 세션 시작 규율 주입에 "컨텍스트가 길어지면 /compact 권유 (직전에 handover 자동 기록)" 한 줄 추가. 자체 상태줄은 claude-hud와 중복이라 넣지 않음.

### Changed
- `post_write_guard`의 에러 삼킴 메시지: 장황한 처방 → 짧은 알림 + 온디맨드 설명으로.

### Tests
- +3 (온디맨드 삼킴 경고 / 항상-이유 비밀키 경고 / 컨텍스트 팁 주입). 61→64.

## [0.6.0] - 2026-07-12
<!-- show:ko **숨어있던 버그들 수정 + 검사 정확도 개선.** 실제로 써보다 발견한 것들을 고치고, 아직 만드는 중인 코드나 화면 컴포넌트를 "안 쓰는 코드"로 오해하지 않게 다듬었어요. -->
<!-- show:en **Squashed hidden bugs + sharper detection.** Fixed things found in real use, and stopped mistaking work-in-progress code or UI components for "dead code". -->

깨끗한 눈(fresh-eyes) 자가 리뷰에서 나온 재현 버그와 커버리지 구멍을 정리. 모두 기계층(파이썬 코드) 수정이라 상주 컨텍스트·프롬프트 길이에는 영향 없음.

### Fixed
- **JS/TS `allow-swallow` 마커가 무시되던 버그** — `catch (e) {} // hi-vibe: allow-swallow`처럼 플러그인이 직접 안내한 해결법이 JS에서 안 먹혔다. 정규식 매치(`}`)가 뒤 주석을 포함 안 해서 마커를 못 봤던 것. 이제 매치가 걸친 **줄 전체**에서 마커를 찾는다 (`post_write_guard.py` `_match_region`). 회귀 테스트 추가(JS 빈 catch·빈 .catch 둘 다).
- **JSX 줄의 진짜 비밀키를 삼키던 오탐 억제** — 오탐 억제 패턴의 맨 `<` 하나가 JSX(`<div>`)나 비교(`a < b`)가 섞인 모든 줄을 억제해 실제 `sk-ant-…` 키를 놓쳤다. `<YOUR_KEY>` 형태의 자리표시자(`<[..]>`)만 억제하도록 좁힘. `xxx`→`xxxx`.
- **주석이 죽은 코드를 구제하던 버그** — 스캐너가 참조를 셀 때 주석·코드를 구분 안 해서, `# TODO: dead_fn() 나중에` 같은 주석 한 줄이 죽은 코드를 은폐했다(.md 구제는 막혀 있었지만 코드 주석 경로가 뚫려 있던 비대칭). 이제 참조 카운트 전에 주석을 제거한다 — Python은 stdlib `tokenize`로, JS/TS는 `//`·`/* */`, YAML/TOML은 `#`, HTML은 `<!-- -->`. **문자열은 일부러 보존**(문자열 속 이름은 동적 호출로 진짜 참조일 수 있음, FP-03). 애매하면 안 지우는 쪽으로 보수적.
- **`/clear` 직후 훅이 안 돌던 문제** — SessionStart matcher에 `clear`가 없었다. 컨텍스트를 통째로 비운 직후가 규율·인수인계 재주입이 가장 필요한 순간인데 빠져 있었음. `clear` 추가(hooks.json + session_start.py).

### Added
- **`export default` 함수/컴포넌트 오탐 방지 (FP-08)** — `export default function App()`은 임포트 측에서 아무 이름으로나 받아 이름 참조가 항상 0 → React 페이지·컴포넌트가 전부 죽은 후보로 뜨던 오탐. 스캐너가 `default_export` 플래그로 감지해 dead 후보에서 제외하고, 오탐 인덱스에 FP-08 계열 추가.
- **`.hi-vibe/state/` 세션 플래그 무한 누적 방지** — Stop 훅의 `.nudged` 플래그가 세션당 1개씩 쌓이던 것을 상한(200개) 넘으면 오래된 것부터 정리.
- **테스트 +12** (49→61) — 위 회귀 전부에 대한 테스트, 그리고 그간 유일하게 미테스트였던 SessionStart 훅 테스트(startup/compact/clear/gate).

### Docs
- README(한/영) "init한 뒤엔 전부 자동" 표를 **⚙️ 기계(훅이 보장) vs 🤖 AI(발동, 100% 보장 아님)** 로 정직하게 구분 — 프롬프트 의존을 "자동"으로 뭉뚱그려 안전벨트가 다 채워진 것처럼 오해시키던 부분을 바로잡음.

## [0.5.1] - 2026-07-12
<!-- show:ko **설치 화면을 입문자가 알아보기 쉽게.** 추천 표시를 넣고, 어려운 용어 대신 쉬운 말로 바꿨어요. -->
<!-- show:en **Made the install screen beginner-friendly.** Added recommendations and swapped jargon for plain words. -->

### Changed
- **guards 선택 화면을 입문자 친화적으로** — 가드 선택지가 (1) 추천 표시가 없어 4개 다 켜야 하는 것처럼 보였고 (2) `complexity≤10`·`max-depth`·`dpdm`·`exit 1`·`OAuth` 같은 전문용어라 입문자가 못 알아들었다. guards-setup SKILL에 지침 추가: 쉬운 말로 "이게 나한테 뭘 해주는지"를 먼저 쓰고 규칙값은 괄호로, 로컬 2종(복잡도 린트+순환 의존)에 "(추천)"을 붙여 맨 앞에, CI는 GitHub 리모트 있을 때만 추천, 격주 감사는 "(고급)"+토큰 설정 필요 명시, "다 켜라"고 밀지 않기.

## [0.5.0] - 2026-07-12
<!-- show:ko **아직 만드는 중인 코드 보호.** 개발 중이라 비워둔 코드를 "안 쓰는 코드"로 오해해서 지우지 않도록. -->
<!-- show:en **Protects work-in-progress code.** So code left blank mid-build isn't mistaken for "unused" and deleted. -->

### Added
- **미완성(WIP) 코드 감지** — 스캐너가 함수/메서드의 본문을 보고 "아직 안 만든 것"을 `looks_wip` 플래그로 표시한다. 감지 신호: `pass`만 있는 본문, `...`, `raise NotImplementedError`, 빈 본문, 스코프 안 TODO·FIXME·WIP·XXX 주석. 참조가 0이라 dead 후보로 잡히더라도 이 플래그가 켜져 있으면 "죽은 코드"가 아니라 "아직 안 만든 코드"이므로 삭제 제안 대상에서 뺀다. (audit.py `_looks_wip`, 파이썬 한정 — JS/TS는 정규식 스캐너라 본문이 없음.)

### Why
- audit은 제안에서 멈추지만 **guards가 미완성 코드를 "안 쓰는 코드"로 간주해 정리하면** 개발 중이던 코드가 사라진다. 스캔은 참조만으로 "죽은 코드 vs 아직 안 만든 코드"를 구분할 수 없어서, 본문 신호를 보는 이 플래그가 유일한 가드다.

### Changed
- repo-xray SKILL·report-format: dead 후보 볼 때 `looks_wip`부터 확인하도록 지침 추가.
- false-positive-index: **FP-07 (work-in-progress)** 계열 신설 — `looks_wip` 심볼은 절대 삭제 제안하지 않고 "아직 미완성으로 보여요, 나중에 쓰실 거면 그대로 두세요"로 안내.
- guards-setup SKILL: 린트는 기본 검사만 하고 `--fix`도 import·지역변수 수준이지 함수 정의를 지우지 않음을 명시. lint unused / audit dead를 보고 정리할 때 미완성 여부를 먼저 확인하고 삭제는 사용자 확인 후로 못박음 (Red Flags에 항목 추가).

## [0.4.2] - 2026-07-11

### Changed
- welcome의 init 안내를 한 문장으로 축소 — 기존엔 "(CLAUDE.md·HANDOVER.md가 있어도 초기화 전)" 같은 내부 판단 로직을 사용자에게 그대로 노출했다. 그건 AI 내부 판단(어떤 파일에 속지 말지)이지 사용자가 들을 얘기가 아니므로, 출력은 "아직 설정 안 됐어요 — /hi-vibe:init 돌려주세요" 한 문장만. 판단 근거는 지침에만 남김.

## [0.4.1] - 2026-07-11

### Changed
- 명령어 10종의 `description`을 영문화 — Claude Code 명령어 목록·자동완성에 뜨는 한 줄 설명이 한국어 고정이라, 영어 사용자에게도 한국어로만 보이던 문제(스킬 description은 이미 영문). About·README·plugin.json 영문 국제화와 일치. (스킬의 한국어 트리거 문구는 한국어 사용자 발동용이라 유지)

## [0.4.0] - 2026-07-11

### Changed
- **init 마커를 `handover.md` → `.hi-vibe/` 디렉토리로 (동작 변경).** `handover.md`는 흔한 파일명이라 사용자가 자기 목적으로 이미 만들어 쓸 수 있는데, 그걸 gate로 삼으면 (1) welcome·doctor가 "이미 init됨"으로 **오판**하고 (2) PreCompact 훅이 **남의 handover.md에 기록을 끼워넣어 오염**시킬 수 있었다. 이제 hi-vibe 전용 `.hi-vibe/` 디렉토리 존재로 판단한다(init이 `.hi-vibe/initialized`를 생성). project_gate·doctor·welcome 전부 이 마커 기준. "사용자 handover.md만으론 gate가 안 켜진다" 회귀 테스트 추가(48개).
  - **마이그레이션**: 기존에 init했지만 `.hi-vibe/`가 없는 프로젝트는 `/hi-vibe:init`을 한 번 재실행하면 마커가 생겨 훅이 다시 켜진다(기존 문서는 안 덮어씀).

## [0.3.6] - 2026-07-11

### Changed
- welcome에 두 가지 필수 못박음: ① GitHub URL을 **실제 링크로** 붙이고 README.md를 읽어보라고 안내(기존엔 "플러그인 README"라고만 뭉뚱그려 링크가 없었음). ② 현재 프로젝트에 `handover.md`(소문자)가 없으면 "먼저 /hi-vibe:init 입력"을 명확히 요청 — CLAUDE.md나 대문자 HANDOVER.md에 속아 "이미 됐다"고 오판하지 않도록.

## [0.3.5] - 2026-07-11

### Changed
- plugin.json·marketplace.json의 `description`을 영문화 — Claude Code의 Installed·Discover 화면에 뜨는 소개글이 기존 한국어 고정이라, 영어 사용자에게도 한국어로만 보이던 문제. About·README 영문 국제화와 일치시킴.

## [0.3.4] - 2026-07-11

### Changed
- **welcome 대폭 간소화**: 기존 welcome이 문서 4종 표 + 명령어 전체 목록 + 훅 세부를 다 쏟아내 "첫인상부터 부담"이던 문제. 이제 👋 인사 + hi-vibe 한 줄 소개 + 할 일 하나(새 프로젝트면 init, 그다음 평소처럼) + README 링크(github.com/jx-hxxx/hi-vibe)로 몇 줄만. 자세한 건 README로 위임. docs-keeper welcome 모드 + welcome 커맨드 양쪽 지침 수정.

## [0.3.3] - 2026-07-11

### Changed
- **생성 문서 언어를 "사용자 대화 언어"로**: 기존엔 docs-keeper가 문서를 무조건 한국어로 쓰게 고정(`prose ... is Korean`)돼 있어, 영어로 대화하는 사용자도 CLAUDE.md·handover가 한국어로 생성되던 문제. 이제 사용자가 한국어면 한국어, 영어면 영어로 문서를 만든다(docs-keeper 문서 언어 + welcome 인사, repo-xray 오탐 설명). 이미 한 언어로 쓰인 문서가 있으면 그 언어를 유지. README/About을 영문 기본으로 국제화한 것과 일관.

## [0.3.2] - 2026-07-11

### Added
- **handover 파일 잠금** (`_common.file_lock`): 여러 터미널(프론트/백엔드 등)이 같은 프로젝트에서 동시에 컴팩트할 때, PreCompact 훅이 handover.md에 동시 기록하며 발생하던 read-modify-write race(항목 유실)를 방지. Unix는 `fcntl.flock`, 그 외는 best-effort(락 실패해도 호스트 안 깨짐). init이 `handover.md.lock`도 gitignore에 추가. 동시 16-프로세스 쓰기 무손실 회귀 테스트 추가.

### Changed
- **CHANGELOG 자동 기록**: write-gate post-write가 실질 변경 감지 시 `/hi-vibe:log`를 기다리지 않고 그 자리에서 `CHANGELOG.md [Unreleased]`에 직접 기록(date로 실제 시각, 실질 변경만 — 오타·포맷·순수 리팩토링 제외). "왜 이건 손으로 쳐야 해?" 피드백 반영, handover처럼 자동화.
- **doctor 전달 말투**: 경고를 벽처럼 나열하지 말고 "결론(hi-vibe 정상 여부 + 한 줄 다음 단계) 먼저, 결정 필요한 것만 따로" 하도록 커맨드 지침 개선.
- **README 재구성**: "평소 흐름"을 ①처음 1회(doctor/init) ②그 다음 자동 ③선택(audit/guards)으로 나눠 "매번 명령어 쳐야 하나?" 오해 제거. 린트·CI 등 개발 용어에 괄호 설명 추가(입문자 대상).

### Changed
- doctor "이 프로젝트" 경고 메시지 명확화 — "init 하라는 건지 말라는 건지" 애매하던 문구를 **다음 단계 명시**(지금 /hi-vibe:init, 기존 파일 안 건드림) + **무시해도 되는 경우 명시**(CHANGELOG를 이미 handover 등으로 관리 중이면)로 개선. 실사용자가 겪은 혼란을 반영.

### Added
- README: claude-hud(상태줄) 함께 쓰기 추천 — 컨텍스트 % 보며 관리 → 컴팩트 시 handover 자동 기록과 궁합. 업데이트 3단계 안내 섹션(marketplace update → plugin update → reload, ①②가 별개임 강조).

## [0.3.0] - 2026-07-11

### Added
- README에 context7 MCP **선택** 설치 안내: `pre-write`가 외부 라이브러리 API를 다룰 때 최신 공식 문서를 자동 조회(무료 API 키 필요). 필수 아님 — 없으면 WebFetch 폴백.

### Changed
- init이 `handover.md`/`handover-archive.md`도 `.gitignore`에 추가 — 개인 세션 로그는 로컬에만 두고 GitHub엔 안 올림(문서 3종 CLAUDE/MODULE/CHANGELOG는 계속 커밋). 훅 게이트는 파일이 디스크에 존재하는지로 판단하므로 gitignore돼도 정상 작동. 공유 원하면 .gitignore에서 그 줄만 제거.
- **플러그인 이름 변경: vibe-check → hi-vibe.** 동명의 MCP 서버 2종(PV-Bhat, kesslerio)과의 검색·발견 충돌 회피. 명령어(`/hi-vibe:*`), 마켓/플러그인명, 상태 디렉토리(`.hi-vibe/`), 마커 주석, GitHub 저장소명까지 전량 통일. GitHub이 구 주소를 자동 리다이렉트.
- **설치 절차에 `/reload-plugins` 추가** (3단계): `/plugin install`만으로는 명령어·훅이 활성화되지 않음 — 공식 문서 확인. 없으면 설치해도 안 켜지던 문제.
- 프롬프트 기법 벤치마킹 (plan-driven-app-development의 프롬프트 설계에서 기법만 차용): ① **HARD-GATE** — root-cause-first와 repo-xray의 절대 계약을 `<HARD-GATE>` 태그로 격리하고 "이 선을 넘으면 도구가 무의미해진다"는 위반 결과를 명시(준수율 강화). ② **자기 점검 루프** — write-gate post-write는 ⚠️를 보고로 끝내지 말고 고쳐서 ✅될 때까지 반복하도록, fresh-eyes는 출력 전 4단계 자기 검열(근거 없는 항목 폐기)을 거치도록. grounded-answers는 판단 뉘앙스 보존을 위해 의도적으로 미적용.
- 브랜딩: 👋를 인사·시작·환영 맥락에 도입 (README/문서 제목, doctor 출력 헤더, welcome 인사, 세션 시작 시 AI 인사). 경고 메시지엔 톤 유지 위해 미적용. README에 CI(GitHub Actions)·MIT·Python 배지 추가.

### Fixed
- repo-xray 유사 중복 탐지가 파일 스캔 순서에 의존하던 비결정성 버그 (CI Linux에서만 실패, 로컬 macOS 통과). 원인: `difflib.SequenceMatcher`의 autojunk 휴리스틱이 두 번째 인자 기준이라 `ratio(a,b) ≠ ratio(b,a)`였고, `os.walk`의 OS별 파일 순서로 인자 순서가 뒤바뀌면 유사도가 0.997↔0.706으로 요동쳐 탐지 여부가 갈림. `autojunk=False`로 대칭성 확보 + 정렬 키를 `(길이, 파일, 줄번호)`로 완전 결정화. 순서 독립성 회귀 테스트 추가(테스트 44개).

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

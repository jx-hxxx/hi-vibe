---
name: write-gate
description: >-
  Pre-write and post-write gates for code changes. Pre-write: before
  creating any new function, helper, type, or file — 만들어줘, 추가해줘,
  구현해줘, 새 파일, 리팩토링, new helper/component. Post-write: after
  finishing a change — 다 했어, 리뷰해줘, 검토, review my change.
  Prevents duplicate reimplementation and enforces the review checklist
  including doc sync.
---

# write-gate

## Mode: pre-write (코드 작성 전)

새 function/helper/type/파일을 만들기 전에, 순서대로:

1. **존재 확인**: repo-xray로 그럴듯한 이름 2~3개를 검색한다.
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/repo-xray/scripts/audit.py" find <name> --root <repo>`
   결과의 스캔 범위를 인용해 판정한다 (repo-xray 계약).
2. **위치 확인**: 대상 폴더의 `MODULE.md`를 읽는다 — 이 코드가 그
   폴더의 책임에 맞는가? 안 맞으면 맞는 폴더를 찾거나 사용자에게 묻는다.
3. **SSOT**: 공용 유틸/타입/shape은 지정된 공용 위치에 한 번만.
   로컬 복사본을 만들지 않는다.
4. **배치**: 새 파일은 위계(도메인/레이어)에 맞게. 루트에 평탄하게
   쌓지 않는다. 처음부터 파일을 나눈다 — 한 파일에 몰지 않는다.
5. **경계 선언**: 이 코드가 import해도 되는 것 / 이 코드를 import해도
   되는 곳을 한 줄로 선언하고 시작한다.

판정은 셋 중 하나: **재사용** (기존 것 그대로) / **확장** (기존 것
수정) / **신규** (근거: 스캔 범위 내 없음).

## Mode: post-write (코드 작성 후)

각 항목을 ✅/⚠️로 보고한다. ⚠️는 이유와 수정 방법을 붙인다.

1. 에러 삼킴을 새로 추가하지 않았는가 (root-cause-first 금지 패턴)
2. 중첩 ≤ 3단계 (넘으면 early return / guard clause로 평탄화)
3. 크기 상한: 함수 ~50줄, 파일 ~400줄 (넘으면 분리 제안)
4. 중복 생성 vs 교체: 기존 코드를 대체했다면 옛 버전을 지웠는가,
   호출부를 옮겼는가, 죽은 코드/주석 처리 코드가 남지 않았는가
5. 안 쓰는 re-export/import 잔재가 없는가
6. 순환 의존을 새로 만들지 않았는가 (의심되면 repo-xray scan)
7. 테스트: 문자열 비교가 아니라 동작을 검증하는가, mock은 외부
   경계에서만인가, 엣지케이스(빈 값/None/0/경계값/실패 경로)를
   먼저 다뤘는가, 테스트 통과용 방어코드를 프로덕션에 넣지 않았는가
8. **문서 동기화 (필수)**: 파일 추가·이동·이름변경 또는 폴더 책임
   변화가 있었으면 → 해당 `MODULE.md` + `CLAUDE.md` 폴더 지도를 같은
   턴에 갱신. 실질 변경이면 → CHANGELOG 항목 (`/vibe-check:log`).

마지막 줄은 반드시 문서 동기화 상태로 끝낸다:
"문서 갱신함: <목록>" 또는 "문서 영향 없음 — <이유>".

---
name: root-cause-first
description: >-
  Root-cause discipline for debugging and error handling. Use whenever
  fixing a bug or error, writing try/except/catch, adding a fallback or
  default value, or the user says 에러 나, 버그, 고쳐줘, 왜 안 되지,
  fallback, 방어코드, "일단 돌아가게", error, crash, exception. Prevents
  symptom-masking fixes that silently swallow failures.
---

# root-cause-first

## Core Contract

```
증상을 가리는 코드는 수정이 아니다
원인을 모르면 "모른다"고 말한다
fallback은 설계 결정이지 응급처치가 아니다
```

에러를 조용히 삼키면 코드가 "돌아가는 척"하게 되고, 사용자는 문제가
있다는 사실조차 모르게 된다. 이것이 피드백 루프를 죽이는 방식이다.

## 금지 패턴

작성하려는 코드에 아래가 들어가면 멈추고 원인을 먼저 찾아라:

- 빈 `except:` / `except Exception: pass` / `catch (e) {}`
- 실패를 숨기는 `|| defaultValue`, `?? fallback`, `or 0`, `or ""`
- 크래시만 멎게 하려고 추가하는 가드 (`if not x: return`)
- 로그 없는 retry 루프
- 테스트를 통과시키려고 프로덕션 코드에 더하는 방어 코드
- 호출부마다 반복되는 중복 방어 — 처리는 경계(핸들러/미들웨어)에서 한 번

## fallback 허용 기준 (셋 다 만족해야 함)

1. 요구사항이 "우아한 저하"를 명시한다 (예: 시세 API 죽어도 화면은 뜬다)
2. 실패가 외부적·예상 가능하다 (네트워크, 외부 API, 사용자 입력)
3. 실패가 여전히 드러난다 (로그 + 가능하면 사용자에게 표시)

하나라도 아니면 에러를 전파하라. 에러 메시지는 "무엇이 어떤 입력으로
실패했는지"를 담는다.

## 버그 수정 루프

1. 재현한다 (재현 못 하면 재현 조건부터 찾는다)
2. 스택트레이스/로그로 원인 위치를 특정한다 — 추측으로 고치지 않는다
3. 원인을 고친다 (증상 지점이 아니라)
4. 진단용 임시 로깅을 제거한다
5. 원래 재현 케이스로 검증한다

원인 규명 시도가 2번 실패하면: try/except로 감싸서 "일단 되나 보자"
하지 말고, 멈추고 사용자에게 솔직하게 말하라 — 지금까지 확인한 것,
배제한 가설, 다음으로 확인할 것.

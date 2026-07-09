# ✅ vibe-check

> **바이브코딩 안전벨트.** AI랑 신나게 코딩하되, 저장소는 깨끗하게.

바이브코딩은 편리하지만, AI가 만든 코드에는 반복되는 문제가 있어요:

- 😵 세션이 바뀌면 기억을 잃고 **있던 함수를 또 만들어요**
- 🩹 에러가 나면 원인 대신 **fallback으로 임시방편 땜빵**을 해요 (그래서 버그가 조용히 숨어요)
- 🤷 헷갈리는 결정을 **묻지도 않고 마음대로** 진행해요
- 📊 확인도 안 한 수치를 **공식 스펙처럼** 말해요
- 🗿 한 파일에 다 몰아넣고, 문서는 코드와 **따로 놀아요**

`vibe-check`는 이 문제들을 **문서 자동화 + AI 규율 + 기계 강제** 세 겹으로 막습니다.

---

## 설치

```
/plugin marketplace add jx-hxxx/vibe-check
/plugin install vibe-check@vibe-check-marketplace
```

> 요구사항: Python 3.8+ (`python3` 명령이 있어야 훅이 동작해요).
> Windows에서 `python3`가 없다면 `python` 별칭을 만들어 주세요.

## 첫 사용

```
/vibe-check:welcome   ← 뭐부터 할지 모르겠으면 여기
/vibe-check:init      ← 프로젝트에 문서 시스템 설치 (1회)
```

`init`을 하면 이 4개 문서가 생기고, 훅이 이 프로젝트에서 활성화돼요:

| 문서 | 역할 |
|---|---|
| `CLAUDE.md` | 프로젝트 지도 — 개요·요구사항·폴더 지도 (얇게 유지) |
| `폴더/MODULE.md` | 각 폴더의 상세 설계 — 기능, 모델, 주의사항 |
| `handover.md` | 세션 인수인계 — 다음 세션이 맥락을 잃지 않게 |
| `CHANGELOG.md` | 실질 변경 이력 — 무엇이 언제 바뀌었나 |

## 평소 흐름

```
/vibe-check:pre-write 지정가 주문 헬퍼   ← 만들기 전: 이미 있는지 검색
   (코드 작성)
/vibe-check:post-write                  ← 만든 후: 체크리스트 + 문서 동기화
/vibe-check:log                         ← 실질 변경이면 CHANGELOG 기록
/vibe-check:handover                    ← 세션 마칠 때 인수인계 남기기
```

## 자동으로 해주는 것 (훅)

- **compact 직전**: 이번 세션의 요청·수정 파일을 `handover.md`에 자동 기록 — 컨텍스트가 압축돼도 맥락이 살아남아요
- **세션 시작/압축 직후**: 최근 인수인계 + 규율 한 줄을 자동 주입
- **세션 종료 시**: 코드는 바꿨는데 CHANGELOG를 안 썼으면 한 번만 알림

## 가끔 쓰는 것

```
/vibe-check:audit    ← 저장소 전체 스캔: 중복/미사용 후보/비대 파일 (증거 기반)
/vibe-check:guards   ← 린트/타입/순환의존 기계 게이트 설치 (물어보고 설치)
/vibe-check:guards --ci  ← push/PR 검사 + 격주 자동 감사 CI까지
```

`audit`은 추측하지 않아요 — 스캐너가 뽑은 JSON 증거로만 말하고,
"없다"고 할 때는 스캔 범위를 함께 말합니다.

## 명령어 한눈에

| 명령 | 언제 |
|---|---|
| `/vibe-check:welcome` | 처음, 또는 뭐 쓸지 모를 때 |
| `/vibe-check:init` | 프로젝트마다 1회 (문서 시스템 설치) |
| `/vibe-check:pre-write` | 새 함수/파일 만들기 **전** |
| `/vibe-check:post-write` | 코드 작성 **후** 리뷰 |
| `/vibe-check:handover` | 세션 마무리 인수인계 |
| `/vibe-check:log` | 실질 변경 CHANGELOG 기록 |
| `/vibe-check:audit` | 전체 구조 점검 |
| `/vibe-check:guards` | 린트/CI 기계 강제 설치 |

## FAQ

**Q. 훅 설정을 바꿨는데 반영이 안 돼요.**
훅은 세션 시작 시 로드돼요. Claude Code를 재시작하세요. `/hooks`로 로드 상태를 볼 수 있어요.

**Q. 다른 프로젝트에서도 훅이 동작하나요?**
아니요. `handover.md`가 있는(= `init`을 한) 프로젝트에서만 동작하고, 나머지에선 조용히 아무것도 안 해요.

**Q. handover.md가 무한정 커지지 않나요?**
20개 항목이 넘으면 오래된 절반이 `handover-archive.md`로 자동 이동돼요.

**Q. 프로젝트에 뭐가 생기나요?**
문서 4종 + `.vibe-check/`(훅 상태), `.repo-xray/`(스캔 결과). 뒤의 둘은 `init`이 `.gitignore`에 추가해요.

## 크레딧 / 라이선스

- 설계 영감: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) (MIT) — 증거 기반 규율("스캔 없이 주장 금지")의 원형
- 라이선스: [MIT](./LICENSE)

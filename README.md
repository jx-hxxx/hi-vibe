# 👋 hi-vibe

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> **바이브코딩 안전벨트.** AI랑 신나게 코딩하되, 저장소는 깨끗하게.

바이브코딩은 편리하지만, AI가 만든 코드에는 반복되는 문제가 있어요:

- 😵 세션이 바뀌면 기억을 잃고 **있던 함수를 또 만들어요**
- 🩹 에러가 나면 원인 대신 **fallback으로 임시방편 땜빵**을 해요 (그래서 버그가 조용히 숨어요)
- 🤷 헷갈리는 결정을 **묻지도 않고 마음대로** 진행해요
- 📊 확인도 안 한 수치를 **공식 스펙처럼** 말해요
- 🗿 한 파일에 다 몰아넣고, 문서는 코드와 **따로 놀아요**

`hi-vibe`는 이 문제들을 **문서 자동화 + AI 규율 + 기계 강제** 세 겹으로 막습니다.

---

## 설치

Claude Code 안에서 아래 세 줄을 차례로 실행하세요.

```
/plugin marketplace add jx-hxxx/hi-vibe        ← 1) 마켓플레이스 등록
/plugin install hi-vibe@hi-vibe-marketplace    ← 2) 플러그인 설치
/reload-plugins                                ← 3) 설치 후 적용 (필수!)
```

> **3번 `/reload-plugins`를 꼭 실행하세요.** 설치만 하면 명령어·훅이
> 아직 안 켜져요. 이 줄을 쳐야 이번 세션에서 바로 활성화됩니다
> (Claude Code 전체 재시작은 필요 없어요).

> **필수 요구사항**: Python 3.8+ (`python3` 명령이 있어야 훅이 동작해요).
> Windows에서 `python3`가 없다면 `python` 별칭을 만들어 주세요.

> **(선택) context7 MCP — 있으면 더 정확해져요.** 코드가 외부
> 라이브러리 API를 쓸 때, `pre-write`가 AI의 오래된 기억 대신 **최신
> 공식 문서**를 자동 조회해서 "옛날 방식 코드"를 막아줘요. **필수는
> 아니에요** — 없으면 자동으로 웹 검색으로 대체하고, 그마저 안 되면
> "추정입니다"라고 밝혀요. 깔고 싶다면(무료 API 키 필요) 공식 안내를
> 따르세요 → https://context7.com · Claude Code 예시:
> `claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key <발급받은_키>`

## 첫 사용

설치·적용이 끝나면 순서대로:

```
/hi-vibe:welcome   ← 뭐부터 할지 모르겠으면 여기
/hi-vibe:doctor    ← 설치 직후 1회: 훅이 진짜 작동하는지 실행으로 확인
/hi-vibe:init      ← 새 프로젝트에서 1회: 문서 시스템 설치 + 훅 활성화
```

`init`은 **프로젝트(폴더)마다 한 번씩** 실행해요 — hi-vibe를 쓰려는 그
앱 폴더 안에서요. 마켓플레이스 등록·설치·적용(위 3줄)은 컴퓨터에서
딱 한 번만 하면 됩니다.

> 훅은 어떤 경우에도 Claude Code를 방해하지 않도록 "조용히 실패"하게
> 설계돼 있어요. 그 대가로 python3가 없으면 **티 안 나게 꺼진 상태**가
> 될 수 있는데, `doctor`가 훅 4종과 스캐너를 실제로 돌려서 확인해 줍니다.

`init`을 하면 이 4개 문서가 생기고, 훅이 이 프로젝트에서 활성화돼요:

| 문서 | 역할 |
|---|---|
| `CLAUDE.md` | 프로젝트 지도 — 개요·요구사항·폴더 지도 (얇게 유지) |
| `폴더/MODULE.md` | 각 폴더의 상세 설계 — 기능, 모델, 주의사항 |
| `handover.md` | 세션 인수인계 — 다음 세션이 맥락을 잃지 않게 |
| `CHANGELOG.md` | 실질 변경 이력 — 무엇이 언제 바뀌었나 |

## 평소 흐름

```
/hi-vibe:pre-write 지정가 주문 헬퍼   ← 만들기 전: 이미 있는지 검색
   (코드 작성)
/hi-vibe:post-write                  ← 만든 후: 체크리스트 + 문서 동기화
/hi-vibe:post-write --deep           ← 큰 변경이면: "남의 눈" 설계 리뷰까지
/hi-vibe:log                         ← 실질 변경이면 CHANGELOG 기록
/hi-vibe:handover                    ← 세션 마칠 때 인수인계 남기기
```

`--deep`은 **이 코드를 쓴 기억이 없는 깨끗한 AI(서브에이전트)**를 불러
설계를 다시 보게 해요 — 과잉 설계, 요청 안 한 기능, 더 단순한 길처럼
체크리스트(빠뜨림 검사)가 못 잡는 **판단 착오**를 잡아요. 별도 결제나
API 키 없이 지금 쓰는 Claude Code 안에서 돌아갑니다.

## 자동으로 해주는 것 (훅)

- **코드 작성 직후**: 방금 쓴 코드에 ①에러 삼킴(빈 except/catch)이나 ②하드코딩된 API 키/비밀키가 새로 생기면 즉시 감지 — 삼킴은 원인 우선 수정을, 키는 .env 이동(+이미 푸시했다면 키 재발급)을 AI에게 요구해요. 규율을 말이 아니라 기계가 지켜요. 의도된 경우는 그 줄에 `hi-vibe: allow-swallow` / `hi-vibe: allow-secret` 주석으로 통과
- **compact 직전**: 이번 세션의 요청·수정 파일을 `handover.md`에 자동 기록 — 컨텍스트가 압축돼도 맥락이 살아남아요
- **세션 시작/압축 직후**: 최근 인수인계 + 규율 한 줄을 자동 주입
- **세션 종료 시**: 코드는 바꿨는데 CHANGELOG를 안 썼으면 한 번만 알림

## 가끔 쓰는 것

```
/hi-vibe:audit    ← 저장소 전체 스캔: 중복/미사용 후보/비대 파일 (증거 기반)
/hi-vibe:guards   ← 린트/타입/순환의존 기계 게이트 설치 (물어보고 설치)
/hi-vibe:guards --ci  ← push/PR 검사 + 격주 자동 감사 CI까지
```

`audit`은 추측하지 않아요 — 스캐너가 뽑은 JSON 증거로만 말하고,
"없다"고 할 때는 스캔 범위를 함께 말합니다.
Python + JS/TS(`.ts`/`.tsx`/`.jsx` 포함)를 스캔하고, 똑같은 중복만이
아니라 **"90% 비슷하게 또 만든"** 함수 쌍(AI의 단골 실수)도 찾아내요.

## 명령어 한눈에

| 명령 | 언제 |
|---|---|
| `/hi-vibe:welcome` | 처음, 또는 뭐 쓸지 모를 때 |
| `/hi-vibe:doctor` | 설치 직후, 또는 훅이 도는지 의심될 때 |
| `/hi-vibe:init` | 프로젝트마다 1회 (문서 시스템 설치) |
| `/hi-vibe:pre-write` | 새 함수/파일 만들기 **전** |
| `/hi-vibe:post-write` | 코드 작성 **후** 리뷰 (`--deep` = 남의 눈 설계 리뷰) |
| `/hi-vibe:handover` | 세션 마무리 인수인계 |
| `/hi-vibe:log` | 실질 변경 CHANGELOG 기록 |
| `/hi-vibe:recall` | "예전에 왜 이렇게 했지?" — 기록에서 검색 |
| `/hi-vibe:audit` | 전체 구조 점검 |
| `/hi-vibe:guards` | 린트/CI 기계 강제 설치 |

## FAQ

**Q. 훅 설정을 바꿨는데 반영이 안 돼요.**
훅은 세션 시작 시 로드돼요. Claude Code를 재시작하세요. `/hooks`로 로드 상태를 볼 수 있어요.

**Q. 훅이 진짜 돌고 있는지 어떻게 알아요?**
`/hi-vibe:doctor` — 훅 4종과 스캐너를 실제로 실행해서 ✅/❌로 보여줘요.
훅은 실패해도 조용히 넘어가도록 설계돼 있어서, 이 명령이 유일한 확인 수단이에요.

**Q. 다른 프로젝트에서도 훅이 동작하나요?**
아니요. `handover.md`가 있는(= `init`을 한) 프로젝트에서만 동작하고, 나머지에선 조용히 아무것도 안 해요.

**Q. handover.md가 무한정 커지지 않나요?**
20개 항목이 넘으면 오래된 절반이 `handover-archive.md`로 자동 이동돼요.
옮겨진 기억도 사라지는 게 아니에요 — `/hi-vibe:recall`(또는 그냥
"예전에 왜 이렇게 했지?"라고 질문)이 아카이브까지 뒤져서 날짜·출처와
함께 답해줘요.

**Q. 프로젝트에 뭐가 생기나요?**
문서 4종 + `.hi-vibe/`(훅 상태), `.repo-xray/`(스캔 결과). 뒤의 둘은 `init`이 `.gitignore`에 추가해요.

## 크레딧 / 라이선스

- 설계 영감: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) (MIT) — 증거 기반 규율("스캔 없이 주장 금지")의 원형
- 라이선스: [MIT](./LICENSE)

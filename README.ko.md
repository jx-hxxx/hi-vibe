# 👋 hi-vibe

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇬🇧 **Read in English → [README.md](./README.md)** &nbsp;·&nbsp; 🇰🇷 한국어로 계속됩니다.

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

> **(선택) claude-hud — 컨텍스트를 눈으로 보며 관리하고 싶다면.**
> 상태줄에 **남은 컨텍스트·토큰**을 실시간으로 보여줘요. hi-vibe와 궁합이
> 좋아요 — 컨텍스트가 얼마 남았는지 보다가 여유 있을 때 `/compact` 하면,
> 그 직전에 hi-vibe가 handover를 자동 기록하거든요("컨텍스트 짧게 유지 +
> 핸드오버 자주"가 눈으로 관리돼요). 설치:
> ```
> /plugin marketplace add jarrodwatts/claude-hud
> /plugin install claude-hud@claude-hud
> /reload-plugins
> ```
> 설치 후 `/claude-hud:setup`으로 상태줄을 켜세요.

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

## 가끔, 필요할 때만 (선택)

```
/hi-vibe:audit          ← 이미 코드가 많은 프로젝트: 중복·갓파일 진단
/hi-vibe:guards --ci    ← 린트(코드 자동 검사기)로 품질을 기계가 강제하게
```

- **`audit`** — 추측하지 않아요. 스캐너가 뽑은 JSON 증거로만 말하고,
  "없다"고 할 땐 스캔 범위를 함께 말해요. Python + JS/TS(`.ts`/`.tsx`/`.jsx`
  포함)를 스캔하고, 똑같은 중복만이 아니라 **"90% 비슷하게 또 만든"** 함수
  쌍(AI의 단골 실수)도 찾아내요.
- **`guards`** — 린트(코드 자동 검사기)를 **물어보고** 설치해요(기존 설정은
  안 건드림). `--ci`를 붙이면 GitHub에서도 자동 검문(CI)하게 돼요.

## init한 뒤엔 전부 자동이에요

위 "첫 사용"에서 **`init`을 한 프로젝트**에서는, 아래가 전부 알아서
돌아가요 (훅과 문서 자동화는 `init`으로 켜지거든요). 명령어를 순서대로
칠 필요 없어요 — **평소처럼 말하면 됩니다:**

| 이럴 때 | 자동으로 |
|---|---|
| "이 함수 만들어줘" | **pre-write** — 이미 있는지 먼저 검색 (중복 재구현 방지) |
| "다 했어 / 리뷰해줘" | **post-write** — 품질 체크리스트 + 문서 동기화 |
| "설계도 봐줘" | **post-write --deep** — 코드를 쓴 기억 없는 깨끗한 AI가 과잉 설계·불필요한 기능 잡기 |
| 코드 쓰는 순간 | 에러 삼킴·비밀키 하드코딩 **즉시 감지** |
| 컴팩트할 때마다 | **handover** 자동 기록 (맥락 보존) |
| 실질 변경하면 | **CHANGELOG** 자동 기록 |
| 세션 시작/압축 직후 | 최근 인수인계 + 규율 자동 주입 |

> 명령어(`/hi-vibe:pre-write` 등)는 "확실하게 하고 싶을 때 누르는 버튼"일 뿐이에요. 대부분 자연어에 알아서 발동해요.
> 감지된 에러 삼킴·비밀키가 **의도된 것**이면 그 줄에 `hi-vibe: allow-swallow` / `hi-vibe: allow-secret` 주석을 달면 통과돼요.

> **(선택) 컨텍스트를 일찍 자동 정리하고 싶다면** — Claude Code 기본
> auto-compact는 컨텍스트가 거의 다 찼을 때 발동해요. `~/.claude/settings.json`의
> `env`에 `"CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "30"`을 넣으면 30%에서 미리
> 자동 컴팩트가 돌고, **그때 위 handover 자동 기록도 같이 실행**돼요.
> 단, 이 환경변수는 **모델·환경에 따라 효과가 제한**될 수 있어요(공식 문서
> 기준). 켠 뒤 실제로 30%에서 도는지 한 번 확인하세요.

## 명령어 한눈에

| 명령 | 언제 | 발동 |
|---|---|---|
| `/hi-vibe:welcome` | 처음, 또는 뭐 쓸지 모를 때 | 🖐 직접 |
| `/hi-vibe:doctor` | 설치 직후, 또는 훅이 도는지 의심될 때 | 🖐 직접 |
| `/hi-vibe:init` | 프로젝트마다 1회 (문서 시스템 설치) | 🖐 직접 |
| `/hi-vibe:pre-write` | 새 함수/파일 만들기 **전** | ⚡ 자동 |
| `/hi-vibe:post-write` | 코드 작성 **후** 리뷰 (`--deep` = 남의 눈 설계 리뷰) | ⚡ 자동 |
| `/hi-vibe:handover` | 세션 마무리 인수인계 | ⚡ 자동 |
| `/hi-vibe:log` | 실질 변경 CHANGELOG 기록 | ⚡ 자동 |
| `/hi-vibe:recall` | "예전에 왜 이렇게 했지?" — 기록에서 검색 | ⚡ 자동 |
| `/hi-vibe:audit` | 전체 구조 점검 | 🖐 직접 |
| `/hi-vibe:guards` | 린트(코드 자동 검사기) 설치 — 안 좋은 코드를 기계가 막음 | 🖐 직접 |

> **⚡ 자동** = 평소 자연어("만들어줘"·"다 했어")나 훅(컴팩트 등)으로 알아서 발동해요. 명령어는 확실하게 하고 싶을 때 누르는 버튼일 뿐이에요.
>
> **🖐 직접** = 필요할 때 직접 명령어를 쳐서 실행해요 (설치·점검·진단처럼 내가 원할 때).

## 업데이트 (새 버전 나왔을 때)

**✅ 제일 편한 방법 — auto-update를 한 번만 켜두세요:**

`/plugin` → **Marketplaces** 탭 → `hi-vibe-marketplace` → **Enable
auto-update**. 이러면 새 버전이 나올 때마다 **켤 때 자동으로 받아와요.**
그다음엔 `/reload-plugins`(또는 그냥 Claude Code 재시작)만 하면 적용돼요 —
아래 명령어를 손으로 칠 필요가 없어요.

**수동 (auto-update를 안 켰다면)** — **순서대로** 세 단계. **①②는 별개예요**
— 목록만 갱신하고 플러그인 교체를 안 하면 옛 버전 그대로예요(제일 헷갈리는
지점!).

```
/plugin marketplace update hi-vibe-marketplace   ← ① 최신 목록 갱신
/plugin update hi-vibe@hi-vibe-marketplace       ← ② 플러그인 교체
/reload-plugins                                  ← ③ 지금 세션에 적용
```

- 확인: `/plugin` → Installed 탭에서 **Version**이 올라갔는지 보기

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
**GitHub에 올라가는 것**: `CLAUDE.md` / `MODULE.md` / `CHANGELOG.md` (프로젝트 문서).
**안 올라가는 것**: `handover.md`·`handover-archive.md`(개인 세션 로그), `.hi-vibe/`(훅 상태), `.repo-xray/`(스캔 캐시). 이것들은 `init`이 `.gitignore`에 자동 추가해요. (handover를 팀과 공유하고 싶으면 `.gitignore`에서 그 줄만 빼면 돼요.)

## 크레딧 / 라이선스

- 설계 영감: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) (MIT) — 증거 기반 규율("스캔 없이 주장 금지")의 원형
- 라이선스: [MIT](./LICENSE)

<h1><img src="docs/images/hi-vibe.png" alt="hi-vibe" height="34"> &nbsp;👋</h1>

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇬🇧 **Read in English → [README.md](./README.md)** &nbsp;·&nbsp; 🇰🇷 한국어로 계속됩니다.

> **AI랑 과속해도, 안전벨트는 hi-vibe가.**

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
> 라이브러리 API를 쓸 때, `find`가 AI의 오래된 기억 대신 **최신
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
/hi-vibe:check          ← 구조 진단 (언제든 반복 OK): 중복·갓파일 찾기
/hi-vibe:gate --ci      ← 품질 관문 설치 (한 번이면 끝 → 이후 push마다 자동)
```

이 둘은 **쓰는 리듬이 반대**예요 — `check`는 **내가 돌리는 진단**(원할 때마다
반복), `gate`는 **한 번 깔아두면 알아서 지키는 관문**(설치는 1회, 이후 자동).

- **`check`** — 추측하지 않아요. 스캐너가 뽑은 JSON 증거로만 말하고,
  "없다"고 할 땐 스캔 범위를 함께 말해요. Python + JS/TS(`.ts`/`.tsx`/`.jsx`
  포함)를 스캔하고, 똑같은 중복만이 아니라 **"90% 비슷하게 또 만든"** 함수
  쌍(AI의 단골 실수)도 찾아내요. **언제든 몇 번이든 반복 실행** — 코드가 쌓일
  때마다 다시 돌려 구조를 점검하는, 그때그때 켜는 진단 도구예요.
- **`gate`** — 코드 자동 검사기(린트)를 **물어보고** 설치해요(기존 설정은 안
  건드림). 그냥 `gate`면 **로컬**에 검사기만 깔려 에디터가 빨간 줄로 표시하고,
  `--ci`를 붙이면 **GitHub에도 관문**을 세워 push마다 검문 — **위반이면 빌드
  실패**(통과 못 하면 못 올려요). **설치는 한 번이면 끝** — `--ci`를 깔면 그
  뒤론 명령어를 다시 칠 필요 없이 push마다 GitHub이 자동으로 검문해요. (규칙을
  바꾸고 싶을 때만 다시 돌리면 됩니다.)

## init한 뒤엔 전부 자동이에요

위 "첫 사용"에서 **`init`을 한 프로젝트**에서는, 아래가 전부 알아서
돌아가요 (훅과 문서 자동화는 `init`으로 켜지거든요). 명령어를 순서대로
칠 필요 없어요 — **평소처럼 말하면 됩니다:**

| 이럴 때 | 무엇이 | 종류 |
|---|---|---|
| 코드 쓰는 순간 | 에러 삼킴·비밀키 하드코딩 **즉시 감지** | ⚙️ 기계 |
| 컴팩트할 때마다 | **handover** 자동 기록 (맥락 보존) | ⚙️ 기계 |
| 세션 시작/압축/clear 직후 | 최근 인수인계 + 규율 자동 주입 | ⚙️ 기계 |
| 실질 변경 후 세션 끝 | **CHANGELOG** 안 남겼으면 알림 (세션당 1회) | ⚙️ 기계 |
| "이 기능 만들어줘" | **find** — 이미 있는지 먼저 검색 (중복 재구현 방지) | 🤖 AI |
| "다 했어 / 리뷰해줘" | **review** — 품질 체크리스트 + 문서 동기화 | 🤖 AI |
| "전체 리뷰해줘" | **review --all** — 세션 전체를 기능별로 한 번에 (이미 본 건 skip) | 🤖 AI |
| "설계도 봐줘" | **review --deep** — 깨끗한 AI가 과잉 설계 잡기 | 🤖 AI |

> **⚙️ 기계** = 훅(파이썬)이 **보장**해요 — AI 기분과 무관하게 실제로 돌아요.
> **🤖 AI** = 스킬 지침으로 **AI가 알아서 발동**해요("만들어줘"·"다 했어" 같은
> 자연어에 반응). 강력하지만 100% 보장은 아니에요 — AI가 그냥 넘어갈 수도
> 있어요. 그럴 때 확실히 하려면 명령어(`/hi-vibe:find` 등)를 직접 누르세요.
> 그래서 명령어는 "AI가 놓쳤을 때 내가 직접 채우는 안전벨트 수동 잠금"이에요.
> 감지된 에러 삼킴·비밀키가 **의도된 것**이면 그 줄에 `hi-vibe: allow-swallow` / `hi-vibe: allow-secret` 주석을 달면 통과돼요.

> **review 3가지 (범위 × 깊이).** 하나의 `review`에 옵션을 붙여 쓰는 구조예요.
> `review`는 **방금 만든 변경 하나**를 품질 체크리스트로. `review --all`은
> **세션에서 바뀐 것 전체**를 기능별로 한 번에(이미 리뷰했고 안 바뀐 파일은
> 자동으로 건너뜀 — 여러 개 몰아 만든 뒤 "전체 리뷰해줘"에 좋아요).
> `review --deep`은 **깨끗한 눈**(fresh-eyes)을 불러 과잉설계·숨은 결합처럼
> 체크리스트가 못 잡는 설계 판단을. `--all`은 "얼마나 넓게", `--deep`은 "얼마나
> 깊이"라 서로 독립이에요 — `review --all --deep`도 됩니다.

## 명령어 한눈에

| 명령 | 언제 | 발동 |
|---|---|---|
| `/hi-vibe:welcome` | 처음, 또는 뭐 쓸지 모를 때 | 🖐 직접 |
| `/hi-vibe:doctor` | 설치 직후, 또는 훅이 도는지 의심될 때 | 🖐 직접 |
| `/hi-vibe:init` | 프로젝트마다 1회 (문서 시스템 설치) | 🖐 직접 |
| `/hi-vibe:find` | **"이 기능 만들어줘"** 할 때 — 만들기 전 있는지 검색 | ⚡ 자동 |
| `/hi-vibe:review` | **"다 했어 / 리뷰해줘"** 할 때 — 점검 + 문서 동기화 (`--all` 세션 전체 · `--deep` 남의 눈) | ⚡ 자동 |
| `/hi-vibe:handover` | 세션 마무리 인수인계 | ⚡ 자동 |
| `/hi-vibe:log` | 실질 변경 CHANGELOG 기록 | ⚡ 자동 |
| `/hi-vibe:recall` | "예전에 왜 이렇게 했지?" — 기록에서 검색 | ⚡ 자동 |
| `/hi-vibe:check` | 전체 구조 점검 — **언제든 반복** | 🖐 직접 |
| `/hi-vibe:gate` | 린트(코드 자동 검사기) 설치 — 안 좋은 코드를 기계가 막음 (**1회 설치 → 자동**) | 🖐 직접 |

> **⚡ 자동** = 평소 자연어("만들어줘"·"다 했어")나 훅(컴팩트 등)으로 알아서 발동해요. 명령어는 확실하게 하고 싶을 때 누르는 버튼일 뿐이에요.
>
> **🖐 직접** = 필요할 때 직접 명령어를 쳐서 실행해요 (설치·점검·진단처럼 내가 원할 때).

## 업데이트 (새 버전 나왔을 때)

**✅ 제일 편한 방법 — auto-update를 한 번만 켜두세요:**

`/plugin` → **Marketplaces** 탭 → `hi-vibe-marketplace` → **Enable
auto-update**. 이러면 새 버전이 나올 때마다 **켤 때 자동으로 받아와요.**
그다음엔 `/reload-plugins`(또는 그냥 Claude Code 재시작)만 하면 적용돼요 —
아래 명령어를 손으로 칠 필요가 없어요.

<p align="center">
  <img src="docs/images/enable-auto-update.png" alt="/plugin → Marketplaces 탭 → hi-vibe-marketplace → Enable auto-update" width="640">
</p>

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
아니요. `.hi-vibe/` 폴더가 있는(= `init`을 한) 프로젝트에서만 동작하고, 나머지에선 조용히 아무것도 안 해요.

**Q. handover.md가 무한정 커지지 않나요?**
20개 항목이 넘으면 오래된 절반이 `handover-archive.md`로 자동 이동돼요.
옮겨진 기억도 사라지는 게 아니에요 — `/hi-vibe:recall`(또는 그냥
"예전에 왜 이렇게 했지?"라고 질문)이 아카이브까지 뒤져서 날짜·출처와
함께 답해줘요.

**Q. gate 빨간불(린트 경고·CI 실패)이 떴는데, 이건 문제가 아니에요. 어떻게 넘기죠?**
AI한테 "괜찮아"라고 **말로 해도 안 없어져요** — 린트는 매번 설정과 코드만
보고 새로 판단하지, "사용자가 괜찮다고 했다"를 기억하지 않거든요. 그래서
예외는 **코드에 남겨야** 지속돼요:
- **그 한 줄만** 봐주기: ruff는 `# noqa: 규칙코드`, eslint는
  `// eslint-disable-next-line 규칙명`
- **규칙 자체가 이 프로젝트엔 안 맞으면**: 설정 파일(`pyproject.toml`의
  `[tool.ruff]` 등)에서 그 규칙을 꺼요 (프로젝트 전체 적용)
- **hi-vibe가 감지한 에러 삼킴·비밀키**면: 그 줄에 `hi-vibe: allow-swallow`
  / `hi-vibe: allow-secret` 주석
일부러 이렇게 만들었어요 — 말 한마디로 꺼지면 다음 세션 AI가 까먹어서
규칙이 흐물흐물해져요. 예외를 코드에 남기면 유지되고, 팀원도 "여긴 일부러
예외구나"라고 알 수 있어요.

**Q. 프로젝트에 뭐가 생기나요?**
**GitHub에 올라가는 것**: `CLAUDE.md` / `MODULE.md` / `CHANGELOG.md` (프로젝트 문서).
**안 올라가는 것**: `handover.md`·`handover-archive.md`(개인 세션 로그), `.hi-vibe/`(훅 상태), `.repo-xray/`(스캔 캐시). 이것들은 `init`이 `.gitignore`에 자동 추가해요. (handover를 팀과 공유하고 싶으면 `.gitignore`에서 그 줄만 빼면 돼요.)

## 크레딧 / 라이선스

- 설계 영감: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) (MIT) — 증거 기반 규율("스캔 없이 주장 금지")의 원형
- 라이선스: [MIT](./LICENSE)

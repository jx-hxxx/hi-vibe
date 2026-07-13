<h1><img src="docs/images/hi-vibe.png" alt="hi-vibe" height="34"> &nbsp;👋</h1>

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇬🇧 **Read in English → [README.md](./README.md)** · 🇰🇷 한국어로 계속됩니다.

> **AI는 빠르게. 프로젝트는 흐트러지지 않게.**

Claude Code가 이미 있는 코드를 또 만들고, 에러를 덮고, 어제의 결정을
잊는 일을 줄여주는 **바이브 코딩 안전벨트**입니다.

- **만들기 전** — 기존 구현부터 검색
- **코딩 중** — 에러 삼킴과 하드코딩 비밀키 즉시 감지
- **세션 사이** — 진행상황 자동 기록·복원
- **완료 후** — 코드 리뷰와 문서 동기화

단순한 프롬프트 묶음이 아닙니다. **실제 Claude Code 훅 4종 · 회귀 테스트
75개 · 프로젝트별 활성화 · Python 표준 라이브러리 기반 핵심 기능**으로
AI가 자주 생략하는 확인·기록·검증을 작업 흐름 안에 넣습니다.

> **먼저 알아둘 점:** hi-vibe는 모든 버그를 자동으로 찾아주는 도구가
> 아닙니다. AI가 대충 넘어가기 쉬운 순간에 근거를 찾고, 기록을 남기고,
> 검증하도록 만드는 작업 규율 + 자동 안전장치입니다.

> **주 대상 언어는 Python입니다.** 훅·스캐너·테스트는 Python을 1차 대상으로
> 설계·검증했습니다. JS/TS(`.js`·`.jsx`·`.ts`·`.tsx`)도 스캔·`gate`·심볼 탐색으로
> 지원하지만 커버리지와 검증 깊이는 Python보다 얕습니다.

<details>
<summary><strong>목차</strong></summary>

- [1분 설치](#1분-설치)
- [설치하면 무엇이 달라지나요?](#설치하면-무엇이-달라지나요)
- [프롬프트 묶음과 무엇이 다른가요?](#프롬프트-묶음과-무엇이-다른가요)
- [왜 믿을 만한가요?](#왜-믿을-만한가요)
- [프로젝트에 만들어지는 문서](#프로젝트에-만들어지는-문서)
- [구조 점검: check](#구조-점검-check)
- [선택형 품질 관문: gate](#선택형-품질-관문-gate)
- [코드 작성 전·후 검증](#코드-작성-전후-검증)
- [명령어 한눈에](#명령어-한눈에)
- [선택 연동](#선택-연동)
- [업데이트](#업데이트)
- [FAQ](#faq)
- [직접 검증해 보세요](#직접-검증해-보세요)
- [크레딧 및 라이선스](#크레딧-및-라이선스)

</details>

---

## 1분 설치

Claude Code 안에서 아래 명령을 차례대로 실행하세요.

```text
/plugin marketplace add jx-hxxx/hi-vibe
/plugin install hi-vibe@hi-vibe-marketplace
/reload-plugins
```

설치가 끝나면 hi-vibe를 사용할 프로젝트 폴더에서:

```text
/hi-vibe:doctor
/hi-vibe:init
```

끝입니다. 이제 이 프로젝트에서는 평소처럼 Claude와 코딩하면 됩니다.

> `/reload-plugins`를 꼭 실행하세요. 플러그인을 설치하는 것만으로는 현재
> 세션의 명령어와 훅이 활성화되지 않습니다.

### 언제 무엇을 실행하나요?

| 상황 | 실행할 것 | 횟수 |
|---|---|---:|
| 내 컴퓨터에 처음 설치 | marketplace → install → reload | 한 번 |
| 설치가 제대로 됐는지 확인 | `/hi-vibe:doctor` | 설치 직후 또는 문제 있을 때 |
| 새 프로젝트에서 사용 시작 | `/hi-vibe:init` | 프로젝트마다 한 번 |
| 구조가 궁금할 때 | `/hi-vibe:check` | 필요할 때마다 |
| lint·CI 관문이 필요할 때 | `/hi-vibe:gate --ci` | 선택, 프로젝트마다 한 번 |
| 평소 코딩 | 자연어로 요청 | 자동 또는 필요 시 명령어 |

**필수 요구사항:** Python 3.8+와 `python3` 명령이 필요합니다. Windows에서
`python3` 명령이 없다면 `python` 별칭을 만들어 주세요.

---

## 설치하면 무엇이 달라지나요?

| 이럴 때 | hi-vibe가 하는 일 | 보장 방식 |
|---|---|---|
| “이 기능 만들어줘” | 기존 함수·파일·타입부터 검색 | 🤖 AI |
| 코드가 작성되는 순간 | 새 에러 삼킴·하드코딩 비밀키 감지 | ⚙️ 기계 |
| 대화가 compact될 때 | 현재 진행상황을 handover에 자동 기록 | ⚙️ 기계 |
| 세션 시작·compact·clear 직후 | 최근 handover와 작업 규율 복원 | ⚙️ 기계 |
| “다 했어 / 리뷰해줘” | 코드·엣지케이스·문서 동기화 검토 | 🤖 AI |
| 실질 변경 후 세션이 끝날 때 | CHANGELOG 누락 알림 | ⚙️ 기계 |
| “예전에 왜 이렇게 했지?” | handover와 아카이브에서 결정 기록 검색 | 🤖 AI |

**⚙️ 기계**는 Python 훅이 실제로 실행합니다. AI가 지침을 기억하는지와
관계없이 작동합니다.

**🤖 AI**는 Claude가 자연어 의도를 알아보고 스킬을 실행합니다. 강력하지만
100% 보장되지는 않습니다. 확실히 실행하고 싶다면 `/hi-vibe:find`,
`/hi-vibe:review`처럼 해당 명령을 직접 호출하세요.

---

## 프롬프트 묶음과 무엇이 다른가요?

텍스트 규칙은 AI가 잊거나 건너뛸 수 있습니다. 그래서 hi-vibe는 안전장치를
세 단계로 나눕니다.

1. **문서 자동화** — 프로젝트 구조와 세션 맥락을 기록합니다.
2. **AI 규율** — 만들기 전 검색하고, 원인부터 디버깅하고, 근거를 확인합니다.
3. **기계 강제** — 훅과 선택형 lint·CI가 AI의 기억과 무관하게 실행됩니다.

```text
Claude Code 이벤트
├─ PostToolUse ── 에러 삼킴·비밀키 감지
├─ PreCompact ─── handover 자동 기록
├─ SessionStart ─ 기억·작업 규율 복원
└─ Stop ───────── CHANGELOG·리뷰 알림

자연어 요청
├─ “만들어줘” ─── 기존 구현 검색
├─ “다 했어” ──── 코드·문서 리뷰
└─ “왜 그랬지?” ─ 결정 기록 검색

선택형 기계 관문
└─ gate ────────── lint · type · 순환 의존 · CI
```

### CLAUDE.md나 린터만 사용하면 안 되나요?

둘 다 좋은 도구지만 담당하는 범위가 다릅니다.

| 방법 | 잘하는 일 | 남는 빈틈 |
|---|---|---|
| `CLAUDE.md` | AI에게 프로젝트 규칙 전달 | 세션 기록·코드 즉시 감지·CI 강제는 하지 않음 |
| 린터 | 정해진 코드 규칙을 기계적으로 검사 | 설계 이유·이전 결정·기존 기능을 모름 |
| hi-vibe | 문서·AI 규율·훅·선택형 CI를 연결 | 모든 버그를 자동으로 탐지하지는 않음 |

---

## 왜 믿을 만한가요?

### 75개의 자동 테스트

handover 기록·회전·동시 쓰기, SessionStart·PreCompact·PostToolUse·Stop
훅, 비밀키와 에러 삼킴 감지, Python·JS/TS 심볼 탐색, 동일·유사 함수,
리뷰 범위 캐시와 오탐 회귀를 테스트합니다.

테스트는 GitHub Actions에서 Python 3.9와 3.12로 실행됩니다. (지원 버전은
Python 3.8+이며, CI는 3.9·3.12 두 버전으로 검증합니다.)

### 파일만 확인하지 않는 doctor

훅은 Claude Code를 방해하지 않도록 실패해도 조용히 넘어갑니다. 그 대신
Python이 없거나 설정이 잘못되면 기능이 꺼진 사실이 눈에 띄지 않을 수 있습니다.

`/hi-vibe:doctor`는 파일 존재 여부만 보는 대신 훅 4종과 스캐너를 실제로
실행하여 ✅/❌로 결과를 보여줍니다.

### 프로젝트별 opt-in

hi-vibe는 설치했다고 모든 저장소에 개입하지 않습니다. `/hi-vibe:init`을
실행해 `.hi-vibe/`가 만들어진 프로젝트에서만 자동 기능이 동작합니다.
다른 폴더에서는 조용히 아무것도 하지 않습니다.

### 오탐을 테스트 자산으로 관리

“참조가 없다”는 이유만으로 코드를 삭제하라고 하지 않습니다.

- decorator가 붙은 프레임워크 진입점
- 테스트 함수
- `export default` 컴포넌트
- 아직 개발 중인 WIP 코드
- 문자열과 동적 호출로 참조되는 심볼

같은 오탐 가능성을 구분하고, 새 오탐이 발견되면 규칙과 회귀 테스트로
남깁니다. 구조 스캔 결과의 “죽은 코드”는 삭제 판결이 아니라 확인할
**후보**로만 다룹니다.

### 기존 설정을 덮어쓰지 않음

선택 기능인 `gate`는 기존 eslint·ruff·mypy·import-linter 설정을 먼저
읽습니다. 사용자에게 물어본 뒤 없는 설정만 병합하며 기존 임계값과 규칙을
임의로 교체하지 않습니다.

---

## 프로젝트에 만들어지는 문서

`/hi-vibe:init`을 실행하면 다음 문서 체계가 설치됩니다.

| 문서 | 역할 |
|---|---|
| `CLAUDE.md` | 프로젝트 전체 지도 — 개요·요구사항·폴더 구조 |
| `폴더/MODULE.md` | 해당 폴더의 기능·모델·설계·주의사항 |
| `handover.md` | 다음 세션을 위한 진행상황과 결정 기록 |
| `CHANGELOG.md` | 실질적인 변경 내용과 이유 |

문서를 한 파일에 전부 몰아넣지 않습니다. `CLAUDE.md`는 얇은 전체 지도로
유지하고, 세부 내용은 각 폴더의 `MODULE.md`에 둡니다.

### Git에 올라가는 파일과 올라가지 않는 파일

**기본적으로 커밋되는 파일**

- `CLAUDE.md`
- `MODULE.md`
- `CHANGELOG.md`

**기본적으로 `.gitignore`에 추가되는 파일**

- `handover.md`, `handover-archive.md` — 개인 세션 기록
- `.hi-vibe/` — 훅과 리뷰 상태
- `.repo-xray/` — 구조 스캔 캐시

handover를 팀과 공유하고 싶다면 `.gitignore`에서 해당 줄을 제거하면 됩니다.

---

## 구조 점검: `check`

```text
/hi-vibe:check
```

코드가 쌓였을 때 원하는 만큼 반복해서 실행하는 진단 명령입니다.

- Python과 JS/TS(`.js`, `.jsx`, `.ts`, `.tsx`) 파일 스캔
- 정확히 동일한 함수 탐색 **(Python 전용)**
- 구현이 약 90% 비슷한 함수 쌍 탐색 **(Python 전용)**
- 참조가 발견되지 않은 심볼 후보
- 이름 충돌 **(JS/TS)**
- 너무 커진 파일과 구조적 문제
- “없다”고 답할 때 실제 스캔 범위 표시

> **중복·유사 함수 탐지는 현재 Python(AST) 전용입니다.** JS/TS는 심볼·이름
> 충돌과 파일 크기 점검만 제공하는 제한적 지원이며, 중복/유사 함수 분석은
> 포함하지 않습니다.

스캐너의 JSON 결과 없이 구조적 주장을 하지 않습니다. 유사 함수와 미참조
심볼은 검토 단서이며, 의미적으로 완전히 같거나 안전하게 삭제할 수 있다는
판결이 아닙니다. 특히 테스트 준비 코드처럼 짧고 비슷한 함수는 정상인데도
“유사”로 잡힐 수 있으니, 재구현 버그가 아니라 검토 단서로 보세요.

---

## 선택형 품질 관문: `gate`

```text
/hi-vibe:gate       # 로컬 검사기 설치
/hi-vibe:gate --ci  # 로컬 + GitHub Actions 관문
```

`check`는 필요할 때마다 돌리는 **진단**이고, `gate`는 프로젝트마다 한 번
설치하는 **지속 관문**입니다.

프로젝트 언어와 기존 설정을 확인한 뒤 필요한 항목을 사용자에게 고르게 합니다.

- Python: ruff, mypy, import-linter
- JS/TS: eslint, TypeScript strict 확인, 순환 의존 검사
- GitHub Actions: push와 pull request에서 검사 실패 시 빌드 차단

모두 켜도록 강요하지 않습니다. 입문자에게는 로컬 복잡도 검사와 순환 의존
검사부터 권하고, strict type과 CI는 프로젝트 상황에 맞게 선택하게 합니다.

---

## 코드 작성 전·후 검증

### 만들기 전: `find`

```text
/hi-vibe:find
```

새 함수·파일·타입을 만들기 전에 기존 구현을 찾습니다. 사용자가 “이 기능
만들어줘”라고 자연스럽게 요청할 때 AI가 자동으로 실행할 수 있고, 반드시
확인하고 싶다면 명령어로 직접 호출할 수 있습니다.

### 작성 후: `review`

```text
/hi-vibe:review
/hi-vibe:review --all
/hi-vibe:review --deep
/hi-vibe:review --all --deep
```

- `review` — 방금 만든 기능 하나 검토
- `review --all` — 이번 세션에서 바뀐 코드 전체 검토
- `review --deep` — 코드를 작성하지 않은 별도 Claude가 fresh-eyes 검토
- `review --all --deep` — 전체 변경을 별도 Claude의 시선으로 검토

`--all`은 이미 리뷰했고 그 뒤로 변경되지 않은 파일을 건너뜁니다. 변경량이
크면 파일 수와 변경 줄 수를 측정한 뒤 순차 검토와 병렬 분할 중 무엇을
사용할지 묻습니다.

`--deep`은 체크리스트만으로 잡기 어려운 과잉설계, 불필요한 기능, 숨은 결합,
지나친 추상화를 새로운 컨텍스트에서 살펴봅니다.

---

## 명령어 한눈에

| 명령 | 언제 사용하나요? | 기본 발동 |
|---|---|---|
| `/hi-vibe:welcome` | 처음이거나 무엇을 사용할지 모를 때 | 🖐 직접 |
| `/hi-vibe:doctor` | 설치 직후 또는 훅이 의심될 때 | 🖐 직접 |
| `/hi-vibe:init` | 새 프로젝트에서 문서·훅 활성화 | 🖐 직접 |
| `/hi-vibe:find` | 새 기능을 만들기 전 기존 구현 탐색 | 🤖 AI / 직접 |
| `/hi-vibe:review` | 구현 후 코드·문서 검토 | 🤖 AI / 직접 |
| `/hi-vibe:handover` | 세션 진행상황 인수인계 | 🤖 AI / 훅 |
| `/hi-vibe:log` | 실질 변경을 CHANGELOG에 기록 | 🤖 AI |
| `/hi-vibe:recall` | 과거 결정과 이유 검색 | 🤖 AI |
| `/hi-vibe:check` | 중복·미참조 후보·큰 파일 구조 점검 | 🖐 직접 |
| `/hi-vibe:gate` | lint·type·순환 의존·CI 관문 설치 | 🖐 직접 |

### 내부 스킬 구성

명령어는 사용하기 쉬운 버튼이고, 실제 작업은 다음 스킬이 담당합니다.

| 스킬 | 연결 명령 | 역할 |
|---|---|---|
| `repo-xray` | `check` | 근거 기반 저장소 구조 분석 |
| `write-gate` | `find`, `review` | 코드 작성 전·후 검증 |
| `docs-keeper` | `init`, `handover`, `log`, `recall`, `welcome` | 문서·세션 기억 관리 |
| `guards-setup` | `gate` | lint·type·순환 의존·CI 설정 |
| `grounded-answers` | 자연어 자동 발동 | 외부 API·가격·버전을 확인 없이 단정하는 것 방지 |
| `root-cause-first` | 버그 작업에서 자동 발동 | fallback으로 숨기기 전 원인 규명 |

---

## 선택 연동

hi-vibe의 핵심 기능에는 아래 도구가 필요하지 않습니다. 필요할 때만
추가하세요.

<details>
<summary><strong>context7 MCP — 최신 공식 문서 조회</strong></summary>

외부 라이브러리 API를 사용할 때 Claude의 오래된 기억 대신 최신 공식 문서를
조회하는 데 도움이 됩니다. context7이 없으면 웹 검색으로 대체하고, 근거를
확보하지 못하면 추정임을 표시하도록 지시합니다.

무료 API 키가 필요합니다. 자세한 내용은 [context7 공식 안내](https://context7.com)를
확인하세요.

```text
claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key <발급받은_키>
```

</details>

<details>
<summary><strong>claude-hud — 남은 컨텍스트를 상태줄에 표시</strong></summary>

남은 컨텍스트와 토큰을 상태줄에서 확인할 수 있습니다. 컨텍스트가 길어질 때
`/compact`를 실행하면 hi-vibe가 직전에 handover를 기록하므로 함께 사용하기
좋습니다.

```text
/plugin marketplace add jarrodwatts/claude-hud
/plugin install claude-hud@claude-hud
/reload-plugins
/claude-hud:setup
```

</details>

---

## 업데이트

### 자동 업데이트 권장

`/plugin` → **Marketplaces** → `hi-vibe-marketplace` → **Enable auto-update**

새 버전은 Claude Code를 시작할 때 자동으로 내려받습니다. 적용하려면
`/reload-plugins`를 실행하거나 Claude Code를 재시작하세요.

<p align="center">
  <img src="docs/images/enable-auto-update.png" alt="hi-vibe marketplace 자동 업데이트 활성화" width="640">
</p>

### 수동 업데이트

```text
/plugin marketplace update hi-vibe-marketplace
/plugin update hi-vibe@hi-vibe-marketplace
/reload-plugins
```

목록 갱신과 플러그인 교체는 별개입니다. 세 명령을 순서대로 실행한 뒤
`/plugin` → Installed에서 버전이 올라갔는지 확인하세요.

---

## FAQ

### 훅 설정을 바꿨는데 반영되지 않아요

훅은 세션 시작 시 로드됩니다. Claude Code를 재시작하세요. `/hooks`에서 현재
로드 상태를 볼 수 있습니다.

### 훅이 실제로 작동하는지 어떻게 확인하나요?

`/hi-vibe:doctor`를 실행하세요. SessionStart, PreCompact, PostToolUse, Stop
훅과 repo-xray 스캐너를 실제로 실행하여 결과를 보여줍니다.

### 다른 프로젝트에서도 자동으로 작동하나요?

아니요. `/hi-vibe:init`을 실행해 `.hi-vibe/` 폴더가 있는 프로젝트에서만
작동합니다.

### handover.md가 계속 커지지 않나요?

20개 항목을 넘으면 오래된 절반이 `handover-archive.md`로 이동합니다.
`/hi-vibe:recall`은 현재 handover와 아카이브를 함께 검색합니다.

여러 Claude Code 터미널이 동시에 기록할 때 항목이 유실되지 않도록 파일
잠금을 사용합니다. 단, Windows(`fcntl` 미지원)에서는 잠금이 best-effort로
내려가 동시 쓰기 안전성이 약해집니다.

### 감지 결과가 의도한 코드라면 어떻게 통과하나요?

hi-vibe 훅의 예외는 해당 줄에 이유가 남도록 코드 주석으로 표시합니다.

```python
except OptionalDependencyError:
    pass  # hi-vibe: allow-swallow
```

```javascript
const token = "test-token-value"; // hi-vibe: allow-secret
```

린터 예외는 해당 도구의 표준 방식을 사용합니다.

- ruff: `# noqa: 규칙코드`
- eslint: `// eslint-disable-next-line 규칙명`
- 프로젝트 전체에 맞지 않는 규칙: 설정 파일에서 명시적으로 비활성화

AI에게 “이건 괜찮아”라고 말하는 것만으로는 기계 검사 결과가 바뀌지 않습니다.
예외를 코드와 설정에 남겨야 다음 세션과 팀원도 의도를 알 수 있습니다.

### 기존 CLAUDE.md나 CHANGELOG.md를 덮어쓰나요?

덮어쓰지 않습니다. 기존 파일이 있으면 먼저 읽고 어떻게 적용할지 확인합니다.
(`gate`가 기존 lint 설정을 다루는 방식은 [왜 믿을 만한가요?](#왜-믿을-만한가요)를
참고하세요.)

### handover를 팀과 공유할 수 있나요?

가능합니다. 기본값은 개인 세션 기록으로 취급해 `.gitignore`에 넣지만,
팀과 공유하려면 해당 ignore 항목을 제거하고 커밋하면 됩니다.

---

## 직접 검증해 보세요

hi-vibe는 근거 없는 주장을 막는 플러그인입니다. 프로젝트 자체도 공개된
코드와 테스트로 검증할 수 있어야 합니다.

아래 질문과 저장소 링크를 Claude·Codex·Gemini에 붙여 넣어보세요.

```text
https://github.com/jx-hxxx/hi-vibe

README의 주장만 요약하지 말고, 현재 main의 실제 훅·스캐너·스킬·테스트를 직접 확인해서 이 Claude Code 플러그인을 평가해줘.
가능하다면 테스트를 직접 실행하고 실행 결과도 적어줘. 직접 확인하지 못한 항목은 추측하지 말고 확인 불가라고 밝혀줘.

hi-vibe는 모든 버그를 찾아내는 전문 정적 분석기나 엔터프라이즈 품질 플랫폼을 표방하지 않아.
Claude Code로 개인·소규모 프로젝트를 만드는 바이브 코더가 자주 생략하는 기존 코드 탐색, 원인 중심 디버깅, 세션 인수인계, 문서 동기화와 검증 습관을 보완하는 "안전벨트" 플러그인이야.

평가할 때 README가 실제로 약속한 범위를 얼마나 잘 구현했는지를 중심으로 판단해줘.
반대로 README의 주장보다 실제 구현이 약한 부분은 분명하게 감점해줘.

다음을 평가하고, 점수와 감점 사유도 말해줘.
1. 바이브 코딩에 주는 도움
2. 제품·기술 설계 난이도
3. 핵심 타깃과 덜 맞는 사용자
4. 장점과 단점 요소
5. 테스트·자동화 신뢰도
6. 현재 완성도

- 핵심 타깃 기준 설치 가치: /10
- 개발 도구로서 현재 성숙도: /10
- 종합점수: /10

칭찬이나 비판을 위한 평가가 아닌, 실제 구현에 근거해 공정하게 평가해줘.
```

---

## 크레딧 및 라이선스

- 설계 영감: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) — “스캔 없이 구조적 주장 금지”라는 증거 기반 원칙
- 라이선스: [MIT](./LICENSE)

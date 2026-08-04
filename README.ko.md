<h1><img src="docs/images/hi-vibe-logo-v4.png" alt="hi-vibe" height="34"> &nbsp;👋</h1>

[![hi-vibe tests](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml/badge.svg)](https://github.com/jx-hxxx/hi-vibe/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
![python: 3.8+](https://img.shields.io/badge/python-3.8%2B-green.svg)

> 🇬🇧 **Read in English → [README.md](./README.md)** · 🇰🇷 한국어로 계속됩니다.

Claude Code가 **이미 있는 코드를 또 만들고, 에러를 덮고, 어제의 결정을 잊는**
일을 줄여주는 바이브 코딩 안전벨트입니다.

### 👉 [무엇을 해주는지 소개 사이트에서 보기](https://jx-hxxx.github.io/hi-vibe/)

전체 명령어, 작동 원리, 자주 묻는 질문, 그리고 **"내 프로젝트에 맞는지 AI에게
물어보는 질문"**까지 사이트에 있습니다. 이 문서는 **설치하고 쓰는 법**만 담습니다.

---

## 설치

Claude Code 안에서 차례대로 실행하세요.

```text
/plugin marketplace add jx-hxxx/hi-vibe
/plugin install hi-vibe@hi-vibe-marketplace
/reload-plugins
```

`/reload-plugins`를 꼭 실행하세요. 설치만으로는 현재 세션에 명령어와 훅이
붙지 않습니다.

## 설치 후엔 이게 전부입니다

hi-vibe를 쓸 프로젝트 폴더에서:

```text
/hi-vibe:init      # 이 프로젝트에 켜기 — 한 번
/hi-vibe:doctor    # 제대로 도는지 확인 — 한 번
/hi-vibe:check     # 기존 코드 전체 점검 — 필요할 때만
```

**그다음엔 아무것도 외울 필요가 없습니다.** 평소처럼 개발하면 리뷰·기록·기존
구현 검색이 알아서 걸립니다.

> **설치는 전역 한 번, `init`은 프로젝트마다.** `/plugin install`은 기본이
> 유저 스코프(전역)라 한 번 설치하면 모든 프로젝트에서 `/hi-vibe:` 명령어를
> 쓸 수 있어요. 하지만 자동 기능(훅)은 `init`으로 `.hi-vibe/` 마커가 만들어진
> 폴더에서만 돕니다. **init 안 한 프로젝트엔 전혀 개입하지 않습니다.**

## 알아서 해주는 것

| 언제 | 무엇 |
|---|---|
| 만들기 전 | "만들어줘"라고 하면 **기존 구현부터 검색** |
| Claude가 코드를 쓸 때 | 에러를 조용히 넘기는 코드·비밀키 패턴 경고 |
| 기능을 다 만들면 | **리뷰를 거치기 전엔 대화가 안 끝남** — 체크리스트 + 코드를 짠 기억이 없는 딴 클로드 |
| 대화가 압축·`/clear`·종료될 때 | 이어갈 단서를 `handover.md`에 자동 기록 |
| 새 세션이 열릴 때 | 그 기록과 프로젝트 규율을 다시 읽힘 |

## 알아둘 점

- **Python + Claude Code 중심입니다.** JS/TS는 심볼·이름 충돌·파일 크기 정도만
  보고, 중복·유사 함수 탐지 같은 핵심 분석은 Python에서만 동작합니다.
- **대화 내용은 이 컴퓨터를 벗어나지 않습니다.** 다만 최근 요청 5개(각 120자)와
  수정 파일 목록이 프로젝트 안 `handover.md`에 **평문으로** 남습니다(기본
  `.gitignore`). 비밀키로 보이는 부분은 가리지만 일반 민감 정보는 그대로예요.
- **프로젝트별로 끌 수 있습니다.** Claude에게 "이 프로젝트에선 hi-vibe 꺼줘"라고
  하거나 `touch .hi-vibe/optout`. 완전히 빼려면 `rm -rf .hi-vibe .repo-xray` —
  **만들어진 문서는 그대로 남습니다.**
- **전문 보안 도구를 대체하지 않습니다.** 비밀키 검사는 대표적인 형태를 잡는
  정규식이라, 키가 새면 곤란한 프로젝트라면 `gitleaks` 같은 도구를 따로 두세요.
- **모든 버그를 자동으로 찾아주지 않습니다.** 원래라면 놓쳤을 것 중 일부를
  잡는 도구입니다.

## 더 보기

- **[소개 사이트](https://jx-hxxx.github.io/hi-vibe/)** — 전체 명령어 · 작동 원리 · 기록되는 것 · FAQ · 적합성 평가 질문
- **[CHANGELOG.md](./CHANGELOG.md)** — 무엇이 왜 바뀌었는지
- **문제가 생기면** `/hi-vibe:doctor`를 먼저 실행하세요. 훅과 스캐너를 실제로
  돌려보고 어디가 막혔는지 알려줍니다.

## 크레딧 및 라이선스

- 설계 영감: [lumin-repo-lens](https://github.com/annyeong844/lumin-repo-lens) — "스캔 없이 구조적 주장 금지"라는 증거 기반 원칙
- 라이선스: [MIT](./LICENSE)

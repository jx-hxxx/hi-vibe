# hi-vibe

## 개요
Claude Code용 "바이브 코딩 안전벨트" 플러그인. AI가 자주 생략하는 검색·기록·
검증 습관을 **문서 자동화 + AI 규율 + 기계 강제(훅·선택형 lint/CI)** 3층으로
워크플로에 끼워 넣는다. 주 대상은 **Python 개인·소규모 프로젝트**. 이 저장소는
그 플러그인 자체의 소스이며, hi-vibe 문서 시스템으로 스스로를 관리한다(dogfooding).

## 핵심 요구사항
- **핵심 훅·스캐너는 Python 표준 라이브러리만** 쓴다 (외부 패키지 0). 이걸 깨면 설치 부담 약속이 무너진다.
- **훅은 항상 fail-open(exit 0)** — 어떤 예외도 호스트(Claude Code)를 중단시키면 안 된다.
- **프로젝트별 opt-in** — 훅은 `.hi-vibe/`가 있는 프로젝트에서만 동작한다.
- **과장 금지** — README·랜딩은 구현이 실제로 하는 것만 말한다. 기계 강제와 AI 규율을 뭉뚱그리지 않는다.
- **중복·유사 함수 탐지는 Python(AST) 전용.** JS/TS는 심볼·이름 충돌·파일 크기만. 이 경계를 넓게 읽히게 쓰지 말 것.
- **임계값 하드코딩으로 자기 편하게 만들지 말 것** — 스캐너 기준(400줄/60줄 등)은 근본 원인 판단용이지 무르게 조정하는 가드레일이 아니다.
- 버전을 올릴 땐 `plugin.json` version + CHANGELOG를 같은 커밋에. showcase(랜딩)·release(GitHub Release)는 거기서 자동 파생된다.

## 실행 방법
```bash
python3 -m unittest discover -s tests   # 전체 테스트 (CI: Python 3.8·3.9·3.12)
python3 scripts/doctor.py --root .      # 훅·스캐너 실제 실행 자가진단
python3 skills/repo-xray/scripts/audit.py scan --root .   # 구조 스캔
```

## 폴더 지도
<!-- 한 폴더 = 한 줄. 상세 설계는 각 폴더의 MODULE.md에. -->
- `hooks/` — Claude Code 생명주기 훅 4종(PostToolUse·PreCompact·SessionStart·Stop)과 공용 `_common.py`. 기계 강제 층.
- `skills/` — 6개 스킬(repo-xray·write-gate·docs-keeper·guards-setup·grounded-answers·root-cause-first). 명령의 실제 동작 담당.
- `commands/` — 10개 슬래시 명령(사용자용 버튼). 각 명령이 스킬을 호출.
- `agents/` — `fresh-eyes`(clean-context 설계 리뷰어, `review --deep`용).
- `scripts/` — 저장소 자동화(doctor·build-showcase·build-release-notes). 플러그인 런타임 아님.
- `tests/` — 회귀 테스트(훅·스캐너·리뷰범위·무결성). CI가 3.8·3.9·3.12로 실행.
- `docs/` — 랜딩 페이지(`index.html`). 업데이트 타임라인은 CHANGELOG에서 자동 생성.

## 결정 기록
- **`audit.py`(스캐너)가 자기 스캔에서 oversized 후보(668줄, 기준 400줄)로 잡히지만 유지한다.** 응집도 높은 단일 책임(저장소 구조 스캔) 파일이고, 60줄 초과 함수는 `find_near_duplicates`(알고리즘)·`cmd_scan` 둘뿐이다. 스캐너는 "삭제 판정"이 아니라 "검토 후보"를 줄 뿐이며 판단은 사람이 한다 — 이건 그 철학의 dogfooding 예다. (테스트 파일 2개도 같은 이유로 후보에 잡히지만 유지.) **다음에 또 "쪼개자"고 하지 말 것.**

## 문서 규칙
이 프로젝트는 hi-vibe 문서 시스템을 씁니다. 구조가 바뀌면 해당
`MODULE.md`와 위 폴더 지도를 같은 턴에 갱신하세요. 세션 맥락은
`handover.md`, 실질 변경 이력은 `CHANGELOG.md`에 기록합니다.
CLAUDE.md는 120줄을 넘기지 않습니다 — 상세는 항상 MODULE.md로.

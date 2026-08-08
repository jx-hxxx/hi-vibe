# Changelog

이 파일은 hi-vibe 플러그인 자체의 변경 이력입니다.
형식: [Keep a Changelog](https://keepachangelog.com/ko/1.1.0/) · 버전: [Semantic Versioning](https://semver.org/lang/ko/)

## [Unreleased]

## [0.45.1] - 2026-08-09
<!-- show:ko **폰에서 "이런 분께" 표가 거꾸로 읽히던 것을 고쳤어요.** 좌우 두 칸짜리 표라 위에 "혹시 이런 적 있나요?"와 "hi-vibe는 이렇게 도와줍니다" 머리글이 나란히 있었는데, 폰에서는 한 줄로 쌓이니까 **"hi-vibe는 이렇게 도와줍니다" 바로 아래에 문제 문장이 오는** 모양이 됐습니다. 머리글을 숨기고 문제와 해결 한 쌍을 카드 하나로 묶었어요. 겸사겸사 영문판에서 창을 761~803px로 줄이면 오른쪽 GitHub 버튼이 잘리던 것도 찾아서 고쳤습니다. -->
<!-- show:en **The pain/fix table read backwards on a phone.** Its two column headers sat side by side, but once the columns stack, "here is how hi-vibe helps" ends up directly above a problem sentence. The headers are now hidden on small screens and each pain/fix couple is one card. Also fixed while measuring: in English, between 761 and 803px the GitHub button was cut off by the longer nav labels. -->

### Fixed
- **폰에서 대응표의 열 머리글이 뜻을 잃었다** (2026-08-09, 760px 이하) — 한 줄로 쌓이면 "hi-vibe는 이렇게 도와줍니다" 바로 아래에 **문제** 문장이 온다. 머리글을 숨기고 한 짝(문제 → 해결)을 카드 하나로 묶었다. 바깥 테두리·배경을 카드로 내려보내고 짝 사이를 12px 띄웠다 — 어디까지가 한 짝인지가 선이 아니라 **간격**으로 보인다.
  - 전환 지점을 실측으로 확인했다: 761px 표(3칸)·머리글 보임 / 760px 카드(1칸)·머리글 숨김.
- **영문판 761~803px에서 헤더 오른쪽이 잘렸다** (2026-08-09) — 영문 메뉴 라벨이 길어 필요한 폭이 788인데 화면은 746이었다. **이번 변경과 무관한 기존 문제**로, 폭을 훑다가 걸렸다.
  - 메뉴 간격을 20 → 12로 좁혀도 40px밖에 못 벌어 2px이 모자란다. 그래서 **메뉴를 숨기는 지점을 760 → 860px**로, 히어로가 한 줄로 쌓이는 지점과 같게 맞췄다. **끊는 자리를 하나로 모아야 "이 구간만 깨지는" 틈이 안 생긴다.**
  - 한·영 x 37개 폭(320~1440px) 재확인 — 넘치는 요소 0.

### 알고 남긴 것
- **창 1081~1095px에서 어두운 띠 안쪽 글이 최대 7.5px 왼쪽으로 어긋난다** — 미디어쿼리는 스크롤바를 **포함한** 창 폭으로 재고 `clientWidth`는 빼고 재기 때문이다. 자리를 차지하는 옛날식 스크롤바에서만 나타나고, 맥처럼 떠 있는 스크롤바에서는 어긋나지 않는다. 경계를 반대로 올리면 그쪽에서 좌우에 흰 틈이 생긴다 — 어느 쪽이든 15px짜리 한 뼘 구간이라 지금 값을 뒀다. 없애려면 `.band`를 `main.wrap` 밖으로 빼야 한다.

## [0.45.0] - 2026-08-09
<!-- show:ko **카톡에 링크를 붙이면 소개 화면이 그대로 뜹니다.** 예전엔 작은 정사각 아이콘만 나왔어요. 그리고 폰에서 읽기 불편하던 것들을 고쳤습니다. 카드 글자가 데스크톱과 같은 크기라 한 줄에 열몇 자밖에 안 들어갔고, 표 가운데를 초록 세로줄이 가로지르고 있었어요(화살표를 돌렸더니 글자만이 아니라 상자째 돌아간 것이었습니다). 긴 명령어는 오른쪽이 잘려 읽을 수가 없었고요. 메뉴 이름 "나한테 맞나"는 번역투라 "이런 분께"로, "문제점"은 hi-vibe 단점처럼 읽혀서 "AI 실수"로 바꿨습니다. 320px부터 1440px까지 한·영 양쪽을 재서 넘치는 곳이 없는 걸 확인했어요. -->
<!-- show:en **Sharing the link now shows the actual landing page, not a small square icon.** Alongside that, the phone layout got fixed: card text was still at desktop size, a green vertical stripe cut through the middle of the pain/fix table (rotating the arrow rotated its whole box, not just the glyph), and long commands were clipped at the right edge and unreadable. Two Korean nav labels were reworded. Measured across 320px to 1440px in both languages with nothing overflowing. -->

### Added
- **링크 미리보기 카드** (2026-08-09, `docs/images/og-cover.png` 1200x630) — 카톡·슬랙에 링크를 붙이면 랜딩 첫 화면이 그대로 뜬다. 예전엔 `og:image`가 파비콘(정사각)이고 `twitter:card`도 `summary`라 작은 아이콘만 나왔다.
  - **손으로 그린 게 아니라 페이지를 1200x630으로 띄워 찍은 것이다.** 큐브가 계속 도는 데다 스크램블 중이라 아무 때나 찍으면 조각이 어긋난 채로 잡힌다 — 첫 스크램블이 시작되는 `0.6초` 전에 `spinSpeed:0`으로 다시 올려 완성·정지 상태에서 찍었다.
  - **첫 화면이 바뀌면 다시 찍어야 한다.** 카톡은 미리보기를 오래 캐시하므로 `?v=` 숫자도 같이 올려야 새 그림이 나간다.
- **미리보기 재발 방지 검사 5종** (2026-08-09, `test_integrity.py`) — `og:image`가 **실제로 있는 파일**을 가리키는지 · 1200x630인지 · 선언한 크기가 실제 파일과 같은지 · 카드가 큰 이미지형인지 · og와 twitter가 같은 그림인지.
  - 이 자리를 기계에 맡기는 이유: **깨져도 우리 화면에는 안 보인다.** 남한테 보낸 링크에서만 보인다.

### Fixed
- **표 한가운데를 세로로 가로지르던 초록 띠** (2026-08-09, 760px 이하) — `.pairs .pair .arrow`에 `transform:rotate(90deg)`가 걸려 있었다. **글자만 도는 게 아니라 상자째 돈다** — 635x30짜리 초록 칸이 30x635가 되어 표 전체를 세로로 관통했다(실측). 회전을 빼고 글자를 `→`에서 `↓`로 바꿔 끼웠다.
- **폰에서 카드 글자가 데스크톱 크기 그대로였다** (2026-08-09, 560px 이하) — 본문이 16px이라 카드 한 줄에 열몇 자밖에 안 들어갔다. 제목·본문·여백을 줄이고 좌우 여백을 24 → 16px로.
  - **축소 규칙은 전부 스타일 맨 끝 한 블록에 모았다.** 같은 특정도면 나중에 나온 규칙이 이기는데, 위쪽 미디어쿼리에 흩어 놓으면 아래 기본 규칙에 조용히 덮인다 — 0.44.1에서 큐브 크기로 이미 한 번 당했다(250을 썼는데 327로 그려졌다).
- **긴 명령어의 오른쪽이 잘려 읽을 수 없었다** (2026-08-09) — `/plugin uninstall hi-vibe@hi-vibe-marketplace`가 546px 화면에서 칸 306 대 글자 353이었다. `white-space:nowrap`을 `overflow-wrap:anywhere`로. **넘칠 때만 끊으므로 넓은 화면에서는 그대로 한 줄이다.**
  - 처음엔 폰(560px 이하)에만 걸었다가 **561~700px 구간이 그대로 남는 것을 폭을 훑다가 잡았다.** 폭 제한 없이 걸었다.
- **기능 카드 제목 옆 꼬리표가 아랫줄 오른쪽 끝에 혼자 떨어졌다** (2026-08-09, 560px 이하) — "기억·인수인계·검색"처럼 제목이 길면 `handover · recall`이 밀려 나는데 `margin-left:auto` 때문에 빈 칸을 두고 오른쪽에 붙었다. 폰에선 제목 뒤에 그대로 잇는다.
- **어두운 띠(`.band`)가 화면보다 넓어 좌우가 잘렸다** (2026-08-09) — `width:100vw`는 **세로 스크롤바 폭까지 포함한다.** 375px 화면에서 띠가 390이 되어 7.5px씩 밀렸다. 부모(`main.wrap`)의 좌우 여백만큼만 빼내는 방식으로 바꾸고, 부모가 최대폭에 걸리는 1080px 위에서만 `vw`를 쓴다.
  - **경계를 1128(=1080+48)로 잡았다가 1113px 화면에서 좌우 17px씩 떴다.** `box-sizing:border-box`라 최대폭 1080 **안에** 여백이 들어 있다. 폭을 훑어서 잡았다.

### Changed
- **한국어 메뉴 이름 둘** (2026-08-09) — `나한테 맞나` → `이런 분께`(영문 `Good fit?`을 그대로 옮긴 번역투였다), `문제점` → `AI 실수`(hi-vibe의 단점처럼 읽혔는데, 실제 내용은 AI가 하는 실수다).

### 앞 릴리스 기록 정정
- **0.44.1에 "360px에서 가로 스크롤이 생긴다"고 적었는데 틀렸다.** `html`에 `overflow-x:clip`이 이미 있어 **화면은 밀리지 않는다**(실제로 `scrollTo(400)`을 걸어 보니 0). 문서 폭이 화면보다 넓었던 것은 맞지만, 증상은 스크롤이 아니라 **삐져나온 부분이 잘려 나가는 것**이었다 — GitHub 버튼 오른쪽 끝과 긴 명령어가 그래서 안 보였다. `scrollWidth`만 보고 스크롤이라 단정한 실수다.
  - 원인 셋(헤더 묶음 183px · 긴 명령어 · `.band`의 `100vw`)을 전부 고쳐 **문서 폭 401 → 375**가 됐다. 320~1080px 전 구간에서 넘치는 요소 0(한·영 각 19개 폭 실측).

## [0.44.1] - 2026-08-08
<!-- show:ko **폰에서 큐브를 첫 화면으로 올렸어요.** 넓은 화면에서는 글 옆에 큐브가 나란히 보이는데, 좁아지면 한 줄로 쌓이면서 큐브가 글 아래로 밀려 스크롤해야 보였습니다. 이게 뭔지 한눈에 알려주는 게 큐브라 위로 올렸어요. 크기도 250px로 줄여서 큐브·제목·설치 버튼이 한 화면에 들어옵니다. HTML 순서는 안 건드렸어요 — 읽는 순서와 스크린리더에는 제목이 먼저인 게 맞으니까요. -->
<!-- show:en **The cube now comes first on a phone.** On a wide screen it sits beside the text; once the layout stacks, it was pushed below the copy and needed a scroll to see. The cube is what tells you at a glance what this is, so it moves to the top, and shrinking it to 250px fits the cube, the headline and the install button on one screen. The HTML order is untouched — for reading order and screen readers the heading still comes first. -->

### Changed
- **모바일 히어로에서 큐브를 맨 위로** (2026-08-08, 860px 이하) — `.clcol`에 `order:-1`. **HTML 순서는 그대로 두고 표시 순서만 바꿨다** — 읽는 순서·스크린리더에는 제목이 먼저인 게 맞다.
  - 큐브를 250px로 줄이고 간격을 40 → 26px로. 안 줄이면 제목이 화면 절반 아래로 밀린다(390px에서 실측).
  - **크기 규칙을 `.hero-cube` 정의 옆에 뒀다.** 처음엔 위쪽 `.hero-grid` 미디어쿼리에 같이 썼는데, **아래에 있는 기본 `.hero-cube { max-width:460px }`가 나중에 나와서 덮어썼다**(같은 특정도라 순서로 진다). 실측으로 잡았다 — 화면은 그럴듯했는데 큐브가 안 줄어 있었다.
  - 실측: 390·360px에서 큐브 위·제목 아래 확인, 한·영 양쪽, 데스크톱(1440px)은 글 왼쪽·큐브 오른쪽 460px 그대로.

### 기록만 하고 안 고친 것
- **좁은 화면(360px)에서 가로 스크롤이 생긴다** — 문서 폭 401px. **이번 변경과 무관한 기존 문제**로, 커밋된 버전에서도 똑같이 재현된다(확인함). 원인은 헤더 오른쪽 묶음(`.hdr-right` 183px, `flex-wrap:nowrap`)과 터미널 블록이 좁은 폭에서 안 접히는 것. 히어로와 별개 자리라 이번 변경에 섞지 않았다.

## [0.44.0] - 2026-08-08
<!-- show:ko **영문 README에서 사이트를 열면 한국어 페이지가 뜨던 것을 고쳤어요.** 랜딩은 한·영이 한 파일에 있고 전에 고른 언어를 기억하는데, 링크에 언어 표시가 없어서 **한 번이라도 한국어로 본 사람은 영문 README를 눌러도 한국어가 나왔습니다.** 이제 각 README가 자기 언어를 링크에 실어 보내고, 랜딩은 그걸 저장된 선택보다 먼저 봅니다. 링크를 눌렀다는 건 지금 이 방문에서 가장 분명한 신호니까요. 저장된 선택이 있는 상태로 반대 언어 링크를 눌러 실제로 바뀌는 것까지 브라우저로 확인했어요. -->
<!-- show:en **Opening the site from the English README could land you on the Korean page.** Both languages live in one page and it remembers your last choice, so anyone who had ever viewed it in Korean got Korean even from the English README. Each README now carries its own language in the link, and the page reads that before the stored preference — clicking a language-specific link is the clearest signal for that visit. Verified in a browser, including the case where a stored choice had to be overridden. -->

### Added
- **랜딩이 `?lang=ko` / `?lang=en`을 받는다** (2026-08-08) — 언어 결정 순서가 `URL → 저장된 선택 → 브라우저 언어`가 됐다. 예전엔 저장된 선택이 맨 앞이라 **링크로 언어를 지정할 방법이 아예 없었다.**
  - **URL을 맨 앞에 둔 이유**: 언어가 명시된 링크를 눌렀다면 그게 이번 방문의 가장 강한 신호다. 저장된 선택이 이기면 링크가 무의미해진다.
  - 잘못된 값(`?lang=xx`)·다른 이름(`?mylang=en`)은 무시하고 기존 순서로 떨어진다. 다른 파라미터와 섞여도(`?a=1&lang=ko`) 잡는다.

### Changed
- **README의 사이트 링크 4곳에 언어를 실었다** (2026-08-08) — `README.md`는 `?lang=en`, `README.ko.md`는 `?lang=ko`(각 2곳).

### Fixed
- **재발 방지 검사 3종** (2026-08-08, `test_integrity.py`) — ①각 README가 자기 언어를 가리키는지 ②랜딩이 그 파라미터를 실제로 처리하는지 ③**URL을 저장된 선택보다 먼저 읽는지**(순서가 뒤집히면 링크가 무시된다). 셋 다 되돌리면 실패하는 것을 확인했다.
  - 이 저장소는 **한쪽만 고치고 반대쪽을 안 보는 사고**를 여러 번 겪었다(FAQ 답·평가 프롬프트·히어로 문구·강제 개행). 링크도 같은 유형이라 사람 눈이 아니라 기계에 맡긴다.

## [0.43.6] - 2026-08-08
<!-- show:ko **바로 앞에서 켠 유리 흡수색을 도로 껐어요.** 몇 달간 안 켜져 있던 설정이라 켜 보니 정작 **유리 안쪽에 색이 배어나오는 게 원하는 그림이 아니었습니다.** 눈으로 보고 나서야 알 수 있는 종류였어요. 번들은 되돌리고(r129 → r128, git에서 꺼내 바이트까지 원본과 동일) 속성은 아예 지웠습니다 — 조건부로 남겨두면 나중에 번들 올리는 순간 그 색이 도로 켜지니까요. 안 쓰게 된 변수와 테마 설정도 같이 지웠습니다. 원래 모습·경고 0으로 돌아온 것을 브라우저로 확인했어요. -->
<!-- show:en **The glass absorption turned on in the previous release is off again.** The setting had been dormant for months, and once actually visible it turned out that colour bleeding through the inside of the glass was not the look wanted — something only judgeable by eye. The bundle is reverted (r129 back to r128, restored from git so it is byte-identical) and the properties are deleted outright: leaving them behind a version check would switch the colour back on the moment anyone upgrades the bundle. The now-unused variable and theme entry went with them, and the original look with zero warnings was confirmed in a browser. -->

### Removed
- **유리 부피 속성 3종을 코드에서 삭제** (2026-08-08) — `thickness`·`attenuationColor`·`attenuationDistance`. v0.43.5에서 실제로 켜 보니 **의도한 그림이 아니었다.** 설정에 적혀만 있고 몇 달간 안 켜져 있었기 때문에, 눈으로 보기 전에는 판단할 수 없던 종류다.
  - **조건 분기(`'thickness' in m`)째로 지웠다.** 남겨두면 나중에 번들을 올리는 순간 그 색이 도로 켜진다 — 지금 "별로"라고 판단한 것을 미래에 지뢰로 심어두는 셈이다.
  - 딸려 죽은 것도 같이: `cube.js`의 `ATTEN` 변수, 랜딩 테마의 `attenuationColor: 0x7a4a06`. **쓰지 않는 설정을 남기면 다음 사람이 "이게 왜 안 먹지"를 다시 겪는다.**
- **번들 three.js r129 → r128** (2026-08-08) — 올린 이유(그 속성)가 사라졌으므로 되돌린다. 7,518바이트 작아지고, `cube.js`를 복사해 쓰는 **다른 프로젝트 네 곳과 같은 버전**으로 돌아온다. **git에서 꺼내 복원했다** — 내 사본이 아니라 원본이어야 바이트까지 같다(SHA-256 대조 확인).
  - **결과적으로 디스코드 회의봇이 먼저 내린 결론과 같아졌다** — 거기선 이미 `콘솔 경고만 190여 개 찍고 무시되던 무해 no-op → 제거`로 정리돼 있었다.

### 남은 상태
- 브라우저 실측: `THREE.REVISION` 128 · 테마에 `attenuationColor` 없음 · **콘솔 경고 0 · 에러 0** · 큐브 원래 밝은 금색 유리로 렌더.

## [0.43.5] - 2026-08-08
<!-- show:ko **큐브 유리에 의도했던 흡수색이 드디어 켜졌어요.** 설정에 짙은 갈금색이 적혀 있었는데 번들된 three.js가 그 기능이 생기기 직전 버전이라 몇 달간 아무 데도 안 쓰이고 있었습니다. 한 단계만 올려서(r128 → r129, 7KB) 원래 의도한 모습이 됐어요. 조건 분기는 남겨뒀습니다 — 이 큐브 코드를 복사해 쓰는 다른 프로젝트 네 곳이 아직 옛 버전이라, 거기서도 경고 없이 돌아야 하거든요. 브라우저로 버전·적용값·경고를 전부 확인했습니다. -->
<!-- show:en **The glass cube finally has the absorption colour it was configured for.** A deep amber was set in the theme, but the bundled three.js was one release short of supporting it, so the setting sat unused for months. A single-step upgrade (r128 to r129, 7KB) turns it on. The version guard stays: four other projects copy this cube code and still ship the older bundle, and they must keep running without warnings. Version, applied values and console output were all verified in a real browser. -->

### Changed
- **번들 three.js r128 → r129** (2026-08-08, `docs/cube/three.min.js`, +7,518바이트) — `thickness`·`attenuationColor`·`attenuationDistance`가 **r129에서 생긴** 속성이라, 랜딩 테마에 적힌 `attenuationColor: 0x7a4a06`이 여태 아무 데도 안 쓰이고 있었다. 한 단계만 올려 켰다 — 그 이상 올리면 색 관리 기본값이 바뀌어 큐브 전체 톤이 달라진다.
  - **조건 분기(`'thickness' in m`)는 지웠다가 되돌리지 않고 남겼다.** 이 저장소 번들은 r129지만, `cube.js`를 복사해 쓰는 다른 프로젝트 **네 곳이 전부 r128**이다(실측). 분기를 빼면 거기서 경고가 되살아난다. 재사용 모듈이라 번들 버전이 제각각인 것을 전제로 둔다.
  - **브라우저 실측**: `THREE.REVISION` 129 · 속성 지원 true · 적용값 `1.5 / 7a4a06 / 0.8` 유지 · 콘솔 경고 0 · 에러 0 · 캔버스 정상 렌더.
  - **처음 확인은 틀렸다** — 파일만 바꾸고 같은 포트로 재접속해 `경고 0`을 봤는데, 브라우저가 옛 `three.min.js`를 캐시하고 있어 **여전히 r128을 보고 있었다.** 새 포트로 붙어 `THREE.REVISION`을 직접 읽고서야 실제 확인이 됐다. 눈에 보이는 결과가 같아 그냥 넘어갈 뻔했다.

## [0.43.4] - 2026-08-08
<!-- show:ko **업데이트 타임라인에 마크다운 기호가 글자 그대로 나가고 있었어요.** CHANGELOG를 랜딩으로 옮기는 변환기가 **맨 앞 굵은 글씨 하나만** 처리하고 나머지는 그냥 통과시켰습니다. 그래서 코드 이름을 감싼 백틱과 문장 안쪽 강조 별표가 페이지에 보였어요. 아무도 그 기호를 안 써서 몇 달간 안 드러났던 것뿐이고, 사실은 **"타임라인 글엔 마크다운 쓰지 말 것"이라는 적힌 적 없는 규칙**에 기대고 있었습니다. 이제 백틱은 코드로, 별표는 강조로 바뀝니다. 브라우저로 직접 보고 고쳤어요. -->
<!-- show:en **Markdown markers were reaching the update timeline as literal characters.** The converter that moves CHANGELOG entries onto the landing page handled only the leading bold and passed everything else through, so backticks around code names and inline emphasis asterisks showed up on the page. It had gone unnoticed for months only because nobody used those markers — the page was really relying on an unwritten "don't use markdown here" rule. Backticks now become code and asterisks become emphasis, verified in a real browser. -->

### Fixed
- **랜딩 타임라인에 백틱·별표가 글자 그대로 나가던 것** (2026-08-08) — `build-showcase.py`의 `render_body`가 **맨 앞 `**굵게**` 하나만** 변환하고 나머지 본문은 이스케이프만 해서 넘겼다. 실측: 페이지에 생백틱 8개 · 생별표 4개.
  - **적힌 적 없는 규칙에 기대고 있었다.** CHANGELOG는 마크다운이라 코드 이름에 백틱, 문장 중간에 강조를 쓰는 게 자연스러운데, 여태 안 드러난 건 **아무도 안 썼기 때문**이지 안전해서가 아니었다. 사람이 참는 대신 기계가 변환한다.
  - `` `코드` `` → `<code>`, 문장 안쪽 `**강조**` → `<strong>`. **이스케이프 뒤에** 변환한다 — 순서가 바뀌면 본문의 `<`가 태그가 된다(그 경우도 테스트로 고정).
  - 두 태그의 CSS를 같이 넣었다. **만들어놓고 스타일이 없으면 글자 크기·색이 튄다** — 그것도 검사가 지킨다.
  - **브라우저로 확인하고 고쳤다.** 백틱을 고친 뒤 화면을 다시 보다가 별표 누수를 발견했다 — 같은 뿌리인데 한 번에 안 보였다.

### Added
- **`test_showcase_render.py`** (2026-08-08) — 변환이 ①실제로 일어나는지 ②이스케이프를 깨뜨리지 않는지 ③페이지에 생기호가 남지 않았는지 ④본문에 허용 외 태그가 안 들어가는지 ⑤만든 태그에 스타일이 있는지. 변환을 되돌리면 실패하는 것을 확인했다.

## [0.43.3] - 2026-08-08
<!-- show:ko **927줄이 된 훅 공용 파일을 책임별로 쪼갰어요.** `_common.py` 하나에 배관·CI·대화 기록 읽기·리뷰 감시·handover 쓰기가 다 살았습니다. 이번 주에 기능이 붙으면서 자기 기준(400줄)의 두 배를 넘겼어요. 다섯 모듈로 나누고, `_common`은 이름만 지키는 표면으로 남겼습니다 — 훅·테스트가 부르는 이름 25개가 전부 그대로라 호출부는 한 곳도 안 바뀌었어요. 동작 변화 없음: 테스트 246개 그대로 통과, 훅 실측 속도 동일, 실제 21MB 세션 기록으로 세는 값까지 손 grep과 대조했습니다. -->
<!-- show:en **The shared hook file had grown to 927 lines and is now split by responsibility.** Plumbing, CI health, transcript reading, review watching and handover writing all lived in one `_common.py` — more than double its own 400-line guideline after this week's additions. It is now five modules, with `_common` kept as a stable name surface: all 25 names that hooks and tests call are unchanged, so no call site moved. No behavior change — all 246 tests pass, hook timing is identical, and counts against a real 21MB transcript match a manual grep. -->

### Changed
- **`_common.py` 927줄 → 책임별 5모듈 + 표면 52줄** (2026-08-08) — `_base`(배관 190줄) · `_ci`(CI 124줄) · `_transcript`(대화 기록 읽기 331줄) · `_agent_watch`(리뷰 감시 146줄) · `_handover`(handover 쓰기 182줄). 전부 400줄 아래.
  - **`_common`은 재수출 표면으로 남겼다.** 훅 5종·테스트·스킬이 `_common.X`로 부르는 이름 25개를 grep으로 뽑아 전부 유지 — **호출부는 한 곳도 안 바뀌었다.** 내부를 나중에 또 옮겨도 호출부가 안 흔들린다.
  - **의존 방향은 한쪽뿐이다**: `_base`가 뿌리이고 형제를 임포트하지 않는다. 순환이 생기면 훅 전체가 조용히 죽는다(fail-open이라 에러도 안 뜬다).
  - **바꿔치기(patch)는 정의된 모듈에** — `_common._run_gh_json`을 바꿔도 `_ci` 안의 호출은 원본을 본다. 실제로 테스트 4개가 이걸로 깨져 patch 대상을 `_ci`로 옮겼다. 같은 함정을 CLAUDE.md에 적었다.
  - **기계적 이동 검증**: 소비자 계약 25개 이름 전부 존재 · 246 테스트 통과 · 새 파일 6개 안 쓰는 임포트 0(AST) · doctor 훅 5종 실행 통과 · Stop 훅 실측 0.20초(동일) · 실제 21MB 트랜스크립트 카운트를 손 grep과 대조(fresh-eyes 3 · mark 5 일치).

## [0.43.2] - 2026-08-08
<!-- show:ko **"대화 내용은 이 컴퓨터를 벗어나지 않습니다"를 고쳤어요.** hi-vibe 얘기로 쓴 문장인데, 범위를 안 밝히면 Claude Code 전체에 대한 약속으로 읽힙니다 — 그리고 Claude Code는 대화를 Anthropic으로 보내니 그 약속은 사실이 아니에요. "hi-vibe는 대화나 코드를 별도 서버로 보내지 않습니다"로 주어를 못박고, 이 문장이 다시 못 돌아오게 과장 재발 방지 검사에 등록했습니다. 랜딩 큐브의 콘솔 경고 3종도 잡았어요 — 번들된 three.js(r128)에 없는 속성을 넘기고 있던 것이라, 있는 버전에서만 켜지게 바꿨습니다. 화면은 그대로고 경고만 사라집니다. -->
<!-- show:en **"Your conversation never leaves this machine" is fixed.** The sentence was written about hi-vibe, but without naming its subject it reads as a promise about Claude Code as a whole — and Claude Code does send conversations to Anthropic, so that promise was false. It now says "hi-vibe sends nothing to a server of its own", and the old sentence is registered in the overclaim regression test so it cannot return. The landing cube's three console warnings are also gone — properties that don't exist in the bundled three.js (r128) were being passed in; they now apply only where supported. The cube looks exactly the same. -->

### Fixed
- **README 보안 문구가 범위 없이 약속하던 것** (2026-08-08, 한·영) — `대화 내용은 이 컴퓨터를 벗어나지 않습니다`는 hi-vibe 얘기지만, **주어가 없으면 시스템 전체에 대한 약속으로 읽힌다.** Claude Code 자체는 대화를 Anthropic으로 보내므로 그 약속은 사실이 아니다. `hi-vibe는 대화나 코드를 별도 서버로 보내지 않습니다(Claude Code의 데이터 처리는 Anthropic 정책)`로 바꿨다. `handover.md` 평문 기록 경고는 그대로 유지.
  - **`test_no_overclaim.py`의 BANNED에 등록했다** — 보안 주장이라 다른 항목보다 무겁다. 옛 문장이 잡히고 새 문장이 오탐 안 나는 것을 양방향으로 확인했다. 외부 리뷰가 짚은 항목이다.
- **랜딩 큐브의 콘솔 경고 3종** (2026-08-08) — `thickness`·`attenuationColor`·`attenuationDistance`는 three.js **r129**에서 생겼는데 번들은 **r128**이라, 생성자에 넘기면 경고를 내고 버린다. **경고만이 아니라 기능이 죽어 있었다** — `cube.js:51`의 `유리 두께 흡수색` 설정이 아무 데도 안 쓰이고 있었다.
  - 있는 버전에서만 직접 대입하게 바꿨다(`'thickness' in m`). r128에선 지금 모습 그대로 경고 없이 돌고, 번들을 올리면 흡수색이 자동으로 살아난다. 의도를 지우지 않고 경고를 없앤 것이다.
  - **실측**: 로컬 서버에 띄워 브라우저 콘솔 확인 — 경고 0 · 에러 0, 큐브 렌더 정상.

## [0.43.1] - 2026-08-07
<!-- show:ko **바로 앞 버전에서 낸 결함 두 개를 다시 확인하다 잡았어요.** 하나는 리뷰 범위가 **중간에 낀 문서 커밋에서 끊기던 것**입니다. "더 가도 새로 나올 게 없으면 멈춘다"로 만들었는데, 문서만 고친 커밋이 하나 끼면 그 뒤가 통째로 안 보였어요. 이 저장소에서 실제로 그랬습니다. 멈추는 기준을 "이미 리뷰한 커밋"으로 바꿔봤더니 **똑같은 함정**에 빠졌고요. 중간에서 멈추는 규칙은 무엇을 기준으로 하든 그 뒤를 가립니다. 그래서 안 멈춥니다. 다른 하나는 속도예요 — git을 스무 번 부르고 마지막 결과만 쓰고 있어서 2.1초 걸리던 걸 0.19초로 줄였습니다. -->
<!-- show:en **Two defects in the version just shipped, caught while re-checking it.** The review range stopped at any docs-only commit sitting in the middle: the rule was "stop once nothing new appears", and a commit touching only documentation hid everything behind it — which happened in this very repository. Switching the boundary to "stop at an already-reviewed commit" fell into exactly the same trap. Any mid-walk stop rule hides what lies beyond it, so there is no longer one. The second fix is speed: the walk called git twenty times and used only the last result, taking 2.1s; it now takes 0.19s. -->

### Fixed
- **문서 커밋 하나가 그 뒤 이력을 통째로 가리던 것** (2026-08-07) — v0.43.0의 종료 조건이 `한 단계 더 가도 안 본 게 안 늘어나면 멈춤`이었다. 문서·설정만 고친 커밋은 코드 파일을 하나도 안 더하므로 **거기서 걸음이 멈춘다.** 이 저장소에서 실측: `HEAD~1`·`HEAD~2` 모두 3개였고 `HEAD~3`(4개)·`HEAD~4`(7개)는 **안 보였다.** 2026-08-06 모의투자 사례가 통과한 건 커밋 순서가 우연히 맞았기 때문이다.
  - **두 번째 시도도 같은 함정이었다**: `이미 리뷰한 커밋을 만나면 멈춤`으로 바꿨더니, 이번엔 **리뷰한 커밋**이 그 뒤의 안 본 작업을 가렸다(새 커밋만 마크하면 옛 커밋이 사라짐).
  - **결론: 중간에서 멈추는 규칙은 기준이 무엇이든 "그 뒤"를 가린다.** 최근 구간을 통째로 후보로 주고 좁히는 일은 `_split_reviewed`에 맡긴다 — 파일 내용 해시로 거르므로 이미 본 것은 어차피 빠진다. **범위를 넓히는 것과 볼 일이 늘어나는 것은 별개다.**
  - 남는 비용은 **처음 켠 저장소의 첫 리뷰**가 최대 10커밋만큼 커질 수 있다는 것이고, 상한이 그것만 막는다. 그 이상은 `check`가 할 일이지 리뷰가 아니다.
- **범위 계산이 2.1초 걸리던 것** (2026-08-07) — `HEAD~1`부터 하나씩 `rev-parse`+`diff`를 돌려 **git을 스무 번 부르고 마지막 결과만** 썼다. Stop 훅 예산이 8초라 통과는 했지만 매 턴 무는 비용이다. 커밋 목록을 한 번에 받아 가장 오래된 것 하나로 diff하면 두 번이면 된다 — 실측 **2.1초 → 0.19초**, 결과는 동일.

### Changed
- `write-gate/SKILL.md` 334 → 350줄 (오늘 누계 +16). 성장 억제 대상이라 기록해 둔다 — 다음에 규칙을 더할 땐 뺄 것을 먼저 찾는다.

## [0.43.0] - 2026-08-07
<!-- show:ko **커밋을 여러 번 하면 직전 커밋이 리뷰에서 통째로 빠졌어요.** 리뷰가 걸리는 건 기능마다인데(커밋과 무관), **무엇을 볼지**는 git에서 계산합니다. 커밋하고 푸시까지 하면 `마지막 커밋 하나`만 남아서, 몇 분 전 커밋은 영영 범위 밖이었어요. 실제로 세어보니 하루에 커밋된 코드 35개 중 4개가 이렇게 샜습니다. 이제 **아직 안 본 게 나오는 데까지 거슬러 올라갑니다.** 이미 본 파일은 원래 자동으로 빠지니까 같은 걸 두 번 보지는 않아요. -->
<!-- show:en **With more than one commit, the earlier one dropped out of review entirely.** Reviews fire per piece of work, not per commit, but *what* they look at is computed from git. Once you commit and push, only the last commit remains in range, so a commit from minutes earlier was never seen. Counting one real day: 4 of 35 committed code files slipped through this way. The scope now walks back until nothing unreviewed turns up. Files already reviewed were always filtered out, so nothing gets looked at twice. -->

### Fixed
- **직전 커밋이 리뷰 범위에서 빠지던 것** (2026-08-07) — 계단 3단계가 `HEAD~1..HEAD` **하나**였다. 한 턴에 커밋을 두 번 하고 푸시하면 1·2단계가 비어 3단계로 내려오는데, 거기서 직전 커밋은 이미 범위 밖이다.
  - **실측이 근거다**: 2026-08-06 한 프로젝트에서 커밋된 코드 35개 중 **12개가 리뷰 표시 없이 남았다.** 8개는 `.html`(v0.41.0에서 해결), **나머지 4개가 이 건**이다. `sec_client.py`·`test_sec_shares.py`는 12:48에 커밋됐고 12:55 커밋에서 리뷰가 걸렸는데 그때 범위는 12:55 하나뿐이었다.
  - **처음엔 "근거 1건"으로 보고 미뤘던 항목이다.** 세어보니 4건이었다 — 표본을 세지 않고 약하다고 판단한 것이 틀렸다.
  - 멈추는 조건은 **한 단계 더 가도 안 본 게 안 늘어날 때**다. 리뷰를 마친 뒤 옛 커밋이 도로 끌려오지 않는 성질(이 계단 설계의 전제)은 그대로 유지되고, 테스트가 양쪽을 지킨다.
  - 상한 10커밋 — 없으면 처음 켠 저장소에서 전체 이력을 리뷰하라고 한다.
  - **넓게 잡아도 안전한 이유**: `reviewed.json`이 파일 내용 해시를 갖고 있어 이미 본 것은 `_split_reviewed`가 뺀다. 범위를 넓히는 것과 일이 늘어나는 것은 별개다.

## [0.42.0] - 2026-08-07
<!-- show:ko **같은 파일에 같은 크기 경고가 리뷰마다 똑같이 떴어요.** `이 파일 686줄입니다`를 이미 알고 넘어가기로 한 뒤에도 계속 펼쳐졌습니다. 이 저장소 원칙이 `알림은 쌓이면 신호가 아니다`인데 정면으로 어긋난 자리였어요. 이제 **처음 400줄을 넘긴 것만 크게 짚고**, 원래 넘어 있던 파일은 한 줄로 줄입니다. 그리고 리뷰가 파일이 **커졌는지 줄었는지**를 이제 압니다 — 예전엔 559줄을 389줄로 쪼갠 리팩터링도 `383줄 변경`으로만 보여서 또 `크다`고 짚었거든요. 기준 400은 그대로예요. 무르게 한 게 아니라 같은 말을 반복하지 않게 한 겁니다. -->
<!-- show:en **The same size warning was reprinted in full at every review.** "This file is 686 lines" kept expanding even after it had been raised and consciously deferred. This repository's own rule is that alerts which pile up stop being signal. Now only a file that has *just* crossed 400 lines gets the full warning; one that was already over gets a single line. The review can also tell whether a file grew or shrank — a refactor that split 559 lines down to 389 previously showed up only as "383 lines changed" and got flagged as oversized again. The 400 threshold is unchanged; what changed is the repetition. -->

### Added
- **`review_scope list`에 `oversized`** (2026-08-07) — `{파일: {lines, growth}}`로 400줄 초과 파일만. `growth`는 **순증**(추가 − 삭제)이다.
  - **`changed_lines`에는 방향이 없다.** 추가+삭제라서 **559줄을 389줄로 쪼갠 리팩터링도 `383줄 변경`으로 보인다** — 리뷰가 그걸 보고 또 `크다`고 짚었다. 늘린 것과 줄인 것은 정반대 이야기다.
  - **처음 넘긴 것인지는 `lines - growth`로 나온다** — 400 이하면 이번에 넘긴 것이다. 상태 파일을 새로 두지 않고 판정할 수 있어 그렇게 했다.
  - 숫자를 AI가 눈으로 세던 것을 기계로 옮겼다(세션마다 말이 달랐다).

### Changed
- **크기 경고를 반복해 펼치지 않는다** (2026-08-07, `write-gate` 체크리스트 3번) — **처음 400을 넘긴 파일만 ⚠️로 펼쳐 분리를 제안**하고, 원래 넘어 있던 파일은 한 줄로 축약한다(`kis_client.py 686줄, 이번 +26`). `growth`가 음수면 아예 짚지 않는다.
  - **기준 400은 그대로다.** CLAUDE.md의 `임계값을 무르게 조정하지 말 것`은 유효하다 — 바뀐 것은 탐지 기준이 아니라 **같은 사실을 몇 번 되풀이하느냐**다.
  - **없애지 않고 축약만 한 이유**: 반복이 소음이기만 한 건 아니었다. `livefeed.py`가 475→511→559로 커지는 동안 세 번 울렸고 그게 실제로 분리를 이끌었다. 계속 보이되 자리를 덜 차지하게 했다.

## [0.41.0] - 2026-08-07
<!-- show:ko **프론트 파일이 리뷰 대상에서 통째로 빠져 있었어요.** `.html`·`.css`가 확장자 목록에 없어서, 로직이 `index.html` 안에 있어도 레이아웃이 깨져도 리뷰가 **한 번도 안 걸렸습니다.** 프론트 버그가 잦은 프로젝트일수록 손해가 컸어요. 이제 봅니다. 대신 사람이 읽을 파일이 아닌 것(`node_modules/`, `*.min.*`)은 뺐어요 — 600KB짜리 미니파이 파일을 읽으라고 하면 리뷰가 조롱거리가 되니까요. 그리고 **`남의 눈`을 안 부르는 이유**도 못박았습니다. `요청 없으면 서브에이전트 부르지 마라` 같은 세션 지시를 보고 건너뛰는 일이 있었는데, `init`으로 켠 것 자체가 요청이라 부르는 게 맞아요. -->
<!-- show:en **Front-end files were entirely outside the review.** `.html` and `.css` were missing from the extension list, so a review never fired even when the logic lived inside `index.html` or the layout broke. Projects with frequent front-end bugs lost the most. They are covered now, minus files no human reads (`node_modules/`, `*.min.*`) — asking someone to review a 600KB minified bundle makes the review a joke. Also pinned down **why fresh-eyes was being skipped**: a session instruction saying not to call subagents unless the user asked was read as a block, but enabling hi-vibe with `init` is the request. -->

### Added
- **`.html`·`.css`가 리뷰 범위에 들어온다** (2026-08-07) — `CODE_EXT`에 없어서 **프론트 변경은 Stop 훅이 아예 안 막았다.** 실사용 프로젝트에서 `bootFetch` 로직 전체가 `index.html` 안에 있는데도 리뷰가 안 걸렸고, 레이아웃이 깨진 `style.css`도 그냥 나갔다.
  - **`write-gate` 체크리스트는 안 건드렸다.** 9번에 이미 `UI·CSS·레이아웃 변경 → 사용자가 검증 루프` 특례가 있어, 시각적 변경은 브라우저 자가검증을 요구하지 않고 동작을 바꾸는 변경만 실행 검증으로 간다. **확장자만 늘리면 자연히 그쪽으로 간다.**
- **사람이 안 읽는 파일 제외** (2026-08-07) — `node_modules/`와 `*.min.*`. 사용자의 저장소 **세 곳 전부** `three.min.js`(600KB)를 갖고 있었고 그건 이미 `.js`라 리뷰 대상이었다.
  - **`vendor/`·`dist/`·`build/`는 일부러 안 뺐다.** 실제 저장소에 사용자가 **직접 쓴** `vendor/cube.js`가 있다 — 이름 규칙으로 빼면 진짜 코드가 조용히 검사 밖으로 간다. 넓게 빼는 것이 좁게 빼는 것보다 위험하다.

### Fixed
- **`남의 눈`을 "요청 안 했으니 안 부른다"고 건너뛰던 것** (2026-08-07) — 세션에 `사용자가 요청하지 않으면 서브에이전트를 부르지 마라`는 지시가 있는데, 그 지시의 예외(`요청했으면`)를 **세션마다 다르게 판단**했다. 실측: 같은 지시 아래 어떤 프로젝트는 6회 부르고 어떤 세션은 하루 종일 0회였다.
  - `write-gate`에 **`init`으로 켠 것 자체가 그 요청**이라고 못박았다. 세션 지시를 무시하라는 게 아니라, 그 지시가 묻는 `사용자가 요청했나`에 답을 준 것이다.
  - **`안 부른 것`과 `못 부른 것`을 구분해 적게** 했다 — 사용자가 고칠 수 있는지가 갈린다. `막혀 있어서`로 뭉뚱그리지 말라고 명시했다(실제로 그렇게 보고된 적이 있는데, 확인해 보니 막힌 게 아니었다).
  - `doctor` 문구도 같이 고쳤다: `설정이 막고 있는지 확인하세요` → `대개 막혀서가 아니라 AI가 안 부른 것`.

## [0.40.0] - 2026-08-07
<!-- show:ko **리뷰의 절반이 조용히 안 돌고 있어도 아무도 몰랐어요.** 리뷰는 두 겹입니다 — 체크리스트가 빠뜨림을 잡고, 남의 눈(fresh-eyes)이 판단 착오를 잡아요. 그런데 세션 설정이 서브에이전트 호출을 막으면 뒤쪽 절반이 그냥 안 돕니다. 실제로 한 세션이 **하루 종일** 그 상태로 돌았는데 어디에도 안 남았어요. 훅이 죽는 건 이미 감시하고 있었는데 에이전트가 죽는 건 아무도 안 보고 있었던 겁니다. 이제 훅이 대화 기록에서 **직접 세고**, `doctor`가 `리뷰 8회 중 0회`처럼 알려줘요. AI가 신고해 주기를 기다리지 않습니다. -->
<!-- show:en **Half the review could be silently missing and nothing said so.** A review has two layers: the checklist catches omissions, and fresh-eyes catches misjudgements. When a session's settings block subagent calls, the second layer simply does not run. One real session spent an entire day like that with no trace anywhere. Dead hooks were already watched; a dead agent was watched by no one. The hook now counts the calls straight out of the transcript and `doctor` reports it as "0 of 8 reviews", rather than waiting for the AI to volunteer it. -->

### Added
- **남의 눈(fresh-eyes)이 안 도는 것을 훅이 감지** (2026-08-07) — `_common.review_activity()`가 트랜스크립트에서 `subagent_type: hi-vibe:fresh-eyes` 호출과 `review_scope … mark` 호출을 **직접 센다.** Stop 훅이 `.hi-vibe/state/agents.json`에 누적하고, `doctor`가 `리뷰 N회 중 M회 실행`으로 보고한다. 리뷰 3회 미만이면 판단을 보류한다(늑대소년 방지).
  - **AI에게 묻지 않는 것이 핵심이다.** `write-gate`는 이미 `생략했으면 한 줄로 밝혀라`고 지시하고 있었는데, **정확히 그 층이 조용히 빠진 사건**이었다. 이 저장소 기준(`증거가 파일 안에 있으면 기계가 잡는다`)의 앞쪽이라 기계로 옮겼다.
  - **막지는 않는다.** 에이전트가 못 도는 건 그 세션 환경 때문인 경우가 많아, 막으면 사용자가 어쩌지 못하는 잔소리 루프가 된다. 기록하고 `doctor`에서만 보여준다.
  - `proof-eyes`는 안 센다 — `check`가 쓰는 다른 에이전트이지 리뷰의 절반이 아니다.

### Fixed
- **긴 세션일수록 못 세던 것** (2026-08-07, 배포 전에 잡음) — 첫 구현은 매번 트랜스크립트 **전체**를 세고 세션별 누계와 비교해 델타를 구했다. 그런데 그 전체 읽기가 `tail_lines`(끝 512KB)여서, 세션이 커지면 예전 호출이 창 밖으로 밀려 **누계가 줄어든 것처럼 보이고** 델타 계산이 멈춘다. **긴 세션일수록 안 세는데 하필 긴 세션이 제일 중요하다.**
  - **실제 16MB 세션에 돌려 보고 잡았다** — 손으로 grep하면 3건인데 함수는 0건을 냈다. 픽스처가 작아 테스트는 전부 통과하고 있었다.
  - 읽은 **바이트 위치를 세션별로 기억**하고 그 뒤만 읽게 바꿨다. 정확하고 더 싸다. 반쯤 쓰인 마지막 줄은 소비하지 않는다(훅이 기록 도중에 돌 수 있다).
- **랜딩의 광고 테스트 수** (2026-08-07) — 211 → 228. `test_integrity`가 잡았다.

## [0.39.2] - 2026-08-07
<!-- show:ko **랜딩 문구를 다듬었어요.** 한 줄에 들어갈 문장이 두 줄로 넘어가 꼬리만 덩그러니 남던 자리 두 곳을 줄여서 한 줄에 앉혔습니다. 비용을 설명하는 칸은 말이 좀 셌어요 — `공짜는 아니에요`를 `시간과 토큰을 조금 씁니다`로 바꾸고, 뒷부분은 줄을 나눠 읽기 쉽게 했습니다. 드는 비용을 감추지는 않았어요. 그리고 `init`과 `gate`가 같은 뜻을 서로 다른 말로 적고 있어서(`새 프로젝트마다 한 번` / `프로젝트마다 1회`) 한쪽으로 맞췄습니다. -->
<!-- show:en **Landing copy cleanup.** Two sentences were spilling a few characters onto a second line, leaving an orphan tail; both are now trimmed to fit one line. The section about cost was blunter than it needed to be, so "It is not free" became "It costs a little time and a few tokens", with the trailing thought on its own line. The cost itself is still stated plainly. And `init` and `gate` described the same thing two different ways, so they now use one wording. -->

### Changed
- **한 줄에 안 들어가 꼬리가 넘어가던 문구 2곳** (2026-08-07, 한·영) — 하드 개행이 아니라 **자연 줄바꿈**이었다. 컨테이너 폭을 건드리면 다른 카드가 같이 흔들리므로 **문장을 줄였다**. ①`AI가 깜빡할 수도 있어요` → `AI도 깜빡해요`, `훑어서` → `훑어`. ②`기본이 유저 스코프(전역)라` → `유저 스코프(전역)라`, `(프로젝트마다 재설치 X)` → `(재설치 X)` — 바로 앞에 `모든 프로젝트에서`가 이미 있어 중복이었다.
  - **좁은 창에서는 여전히 줄이 넘어간다.** 반응형이라 모든 폭에서 한 줄을 보장할 수는 없고, 데스크톱 기준으로 맞춘 것이다.
- **비용 설명 카드의 어조** (2026-08-07, 한·영) — `공짜는 아니에요` → `시간과 토큰을 조금 씁니다`, `딴 클로드까지 불러요` → `딴 클로드도 한 번 봐요`, `값을 치르는 건 맞아요` → `시간이 드는 건 맞아요`. **비용을 감추지 않는다는 원칙은 그대로**이고 문장이 세게 읽히던 것만 낮췄다. 마지막 두 문장은 `<br>`로 내려 세 덩어리로 읽히게 했다.
- **`init`·`gate`의 주기 표기 통일** (2026-08-07) — 명령어 표에서 `init`은 `새 프로젝트마다 한 번`, `gate`는 `프로젝트마다 1회`였다. **같은 뜻을 다른 말로 적으면 둘이 다른 주기인 줄 읽힌다.** `프로젝트마다 1회`로 맞췄다(영문은 이미 `once per project`로 같았다).
- **`gate`의 빠른 시작 라벨** (2026-08-07, 한·영) — `검사 자동화(선택)` → `코드 검사기 설치(선택)`. 명령어 표는 이미 `코드 자동 검사기 설치`라 **한 명령을 두 이름으로 부르고 있었다.** `CI 자동화`로 바꾸자는 안은 **택하지 않았다** — `gate`가 실제로 까는 건 lint·타입·순환참조 가드이고 CI는 GitHub을 쓸 때만 덤으로 제안하는 것이라, CI를 제목에 올리면 **GitHub을 안 쓰는 사람이 자기와 무관하다고 읽는다**.
- **문장이 문장 한가운데서 잘리던 곳 3곳에 `<br>`** (2026-08-07, 한·영) — `check vs review` 카드의 `의심하는 대상이 …` 두 줄과, `doctor는 스킬 없이 훅·스캐너를 직접 돌려요`. **자연 줄바꿈이 하필 주어와 서술어 사이를 갈랐다.** 문장 앞에 개행을 넣어 **한 문장이 한 줄에** 오게 했다(짧아서 어느 폭에서도 안 넘친다). 영문도 같은 자리.

## [0.39.1] - 2026-08-06
<!-- show:ko **잡아놓고 말을 안 하던 것을 고쳤어요.** hi-vibe가 뭔가 잡으면 답변 끝에 `👋 hi-vibe가 방금 …을 잡았어요` 한 줄을 남기게 돼 있습니다. 그게 나중에 "몇 건 잡았나"를 셀 수 있는 유일한 표시예요. 그런데 바로 위 문단이 그 줄을 **"중복 설명"** 목록에 넣어놔서, 체크리스트에 이미 적었으면 생략하게 돼 있었습니다. 실사용에서 리뷰가 여덟 번 돌고 진짜 결함도 나왔는데 이 줄은 **한 번도 안 붙었어요.** 설명은 한 곳에만, 세는 표시는 항상. 이 둘을 갈라놨습니다. -->
<!-- show:en **It was catching things and not saying so.** When hi-vibe catches something it is supposed to close the reply with one line, `👋 hi-vibe caught …`, which is the only marker that makes later counting possible. The paragraph above it listed that line among things not to repeat, so once the checklist covered the defect the line was dropped. In real use a session ran eight reviews, found real defects, and emitted the line zero times. Explanations belong in one place; the counter always gets written. -->

### Fixed
- **`👋` catch 줄이 "중복 설명 금지"에 걸려 사라지던 것** (2026-08-06) — `write-gate/SKILL.md:277`이 체크리스트 ⚠️ · `👋` 줄 · 마무리 요약을 나란히 두고 **한 곳에만 쓰라**고 했는데, `325`는 조건이 맞으면 **붙이라**고 한다. 같은 파일이 반대를 시켰고, 실제로는 더 구체적인 체크리스트가 이겨서 줄이 안 붙었다.
  - **실사용 근거**: 2026-08-06 한 프로젝트에서 Stop 훅이 리뷰를 8회 강제했고 실질 결함(되살아난 회귀 1건·숨은 전제 1건·안 쓰는 import 2건·낡은 docstring 3건)이 나왔는데, 그날 `👋 hi-vibe가 방금` 줄은 **0건**이었다. 같은 기간 다른 프로젝트들에서는 붙었다.
  - **왜 중요한가**: 이 접두사는 `나중에 세션에서 grep 가능하게` 고정한 것이다(같은 파일 324행). 안 붙으면 "잡은 건수"를 셀 방법이 없어져, 지금 모으는 중인 깔때기 수치(리뷰 발동 → 실제 결함)가 실제보다 작게 잡힌다.
  - **`👋`는 설명이 아니라 세는 표시**라고 그 자리에 못박았다. 설명 중복 금지는 체크리스트·요약 사이에만 적용된다.
  - **이번이 세 번째 자기모순이다** (v0.39.0의 `107 vs 288`, `SessionStart charter`에 이어). 한 파일 안에서 두 문단이 반대를 시키는 것이 이 스킬의 재발 유형이라 CLAUDE.md 함정에 적었다.

## [0.39.0] - 2026-08-04
<!-- show:ko **실사용에서 처음으로 결함이 나왔어요.** 다른 프로젝트에서 쓰다가 `doctor`가 스스로 모순되는 진단을 냈습니다 — "훅이 안 돈다(stale)"면서 같은 줄에 "마지막 실행 0.0시간 전"이고 살아있는 훅이 둘이었어요. 세션 도중에 플러그인을 켜거나 업데이트하면 `SessionStart`만 이번 세션에서 안 도는데, 그것 하나로 전체를 판정하고 있었습니다. 그걸 본 AI는 경고를 그냥 무시했고요 — **건강검진이 늑대소년이 되면 진짜 고장도 같이 묻힙니다.** 그리고 리뷰 지침이 서로 반대를 시키던 것도 고쳤어요. -->
<!-- show:en **The first defect found in real use.** While using it on another project, `doctor` produced a self-contradictory diagnosis: it reported the hooks as stale while the same line said the last run was 0.0 hours ago, with two hooks listed as alive. Enabling or updating the plugin mid-session means only `SessionStart` misses that session, and the whole verdict hung on that one hook. The AI reading it simply ignored the warning — a health check that cries wolf buries the real failures with it. A contradiction inside the review instructions was fixed at the same time. -->

### Fixed
- **`doctor --quick`이 스스로 모순되는 진단을 내던 것** (2026-08-04) — 실제로 나온 출력: `{"state": "stale", "fresh_hooks": ["PostToolUse", "Stop"], "last_seen_hours": 0.0}`. 판정이 **`SessionStart`가 신선한지만** 봤는데(`세션마다 반드시 돈다`는 전제), **세션 도중에 플러그인을 켜거나 업데이트하면 그 훅은 다음 세션에나 돈다.** 그동안 `PostToolUse`·`Stop`은 멀쩡히 돈다.
  - **결과가 나쁘다**: 그 출력을 본 AI는 스킬 지침대로 `훅이 안 돌고 있습니다`를 알려야 했지만 **말이 안 돼서 무시했다.** 다음에 진짜로 훅이 죽어도 똑같이 무시하게 된다.
  - 훅이 **하나라도** 최근에 돌았으면 `alive`로 본다. `Stop`은 매 턴 도므로 정말 죽었으면 `fresh_hooks`가 빈다. 진짜 낡은 경우가 여전히 `stale`로 잡히는지도 같이 고정했다.
- **리뷰 지침이 서로 반대를 시키던 것** (2026-08-04) — `SKILL.md:107`은 `사용자에게 고르라고 묻지 않는다`인데 `SKILL.md:288`은 `"가볍게 봐줘"라고 하시면 됩니다를 덧붙인다`였다. 실사용에서 AI가 **"리뷰가 값어치 있었냐"는 질문에 이 문장을 답 대신 내놓았다** — 판단을 사용자에게 떠넘긴 것이다. 안내 자체는 남기되(끄는 법을 모르면 마찰이 불만이 된다), **깊이 판단은 여전히 AI가 하고 되묻지 않는다**를 같은 자리에 못박았다.

### Added
- **`test_doctor_quick.py`** (2026-08-04) — **살아있는 훅이 있는데 `stale`이라고 하면 실패**한다(자기모순 금지). 세션 도중 켠 경우·`Stop`만 돈 경우 등 네 조합으로 확인하고, 반대로 **진짜 낡았을 때는 여전히 `stale`**인지도 고정했다. 상태 값이 스킬이 분기하는 다섯 개 밖으로 새지 않는지도 본다. 고치기 전 코드로 되돌리면 3건이 실패하는 것을 확인했다.

### 기록만 하고 안 고친 것
- **`fresh-eyes`가 변경 크기와 무관하게 붙는다** — 실사용 측정: 273줄 렌더링 재작성에 5분 50초·69,386토큰(실질 결함 2건), 37줄 데이터 추가에 3분 4초·38,404토큰(0건). `review_scope`가 이미 `total_changed_lines`·`file_count`를 주는데 병렬 여부에만 쓰고 깊이에는 안 쓴다. **다만 표본이 둘이다** — 빈손 한 번을 근거로 임계값을 박으면 "10번 중 2~3건" 기준과 어긋난다. 사례를 더 모은 뒤에 정한다.

## [0.38.1] - 2026-08-04
<!-- show:ko **질문 마지막 줄을 조건형으로 바꿨어요.** `설치 후 권장 사용 순서`는 설치를 이미 정한 것처럼 읽혔습니다. 이 자리는 설치 전에 보는 미리보기니까 `설치한다면`으로 여지를 뒀어요. 묻는 내용은 그대로입니다. -->
<!-- show:en **The closing line of the question is now conditional.** "A suggested order of use after installing" read as though the decision had already been made; this section is a preview seen before installing, so it now says "if you do install it". Nothing else changed. -->

### Changed
- **프롬프트 마지막 줄** (2026-08-04, 랜딩 한·영 + 아카이브) — `설치 후 권장 사용 순서` → `설치한다면 권장하는 첫 사용 순서`. **답을 강요하지 않으면서 설치를 전제하지도 않는다.** 영문도 `If you do install it, a suggested order to start with`로.

## [0.38.0] - 2026-08-04
<!-- show:ko **"내 프로젝트에서는 무엇을 도와줄까요?"의 질문을 다시 썼어요.** 예전 질문은 "설치할 가치가 있는지 평가해 달라"였는데, 이 자리의 목적은 심사가 아니라 **내 프로젝트 어디에 쓸지 미리 보는 것**입니다. 이제 다섯 가지를 실제 파일과 함께 짚어달라고 하고, 마지막에 도움이 될 지점 3가지·관련 파일·설치 후 사용 순서만 정리하게 해요. "비슷한 파일이 있다는 이유만으로 같은 기능이라고 단정하지 말라"는 줄도 넣었습니다. -->
<!-- show:en **The question in "What would it do in your project?" has been rewritten.** The old one asked for a verdict on whether installing was worth it; the purpose of this section is not a verdict but a preview of where it would fit in your own code. It now asks for five specific things backed by real files, and closes with three places it would help, the files involved, and a suggested order of use. It also warns against concluding two things are the same because their filenames look alike. -->

### Changed
- **적합성 평가 프롬프트를 활용 미리보기로** (2026-08-04, 랜딩 한·영 + 아카이브) — 예전 질문은 `설치를 추천하는지와 그 이유`·`활용도가 낮은 기능`을 물었다. **이 자리의 목적은 심사가 아니다** — 한계와 안 맞는 사용자는 사이트의 다른 섹션이 이미 밝힌다. 이제 다섯 항목(중복 방지·리뷰가 잡을 것·세션 기록·전체 점검·기존 도구와의 병행)을 **실제 파일과 함께** 답하게 한다.
  - **`필요 없어 보이는 기능`을 묻지 않는 이유**: 그렇게 물으면 AI가 제일 쉬운 출구로 간다 — 저장소에 `handover.md`가 하나 있는 걸 보고 "이미 있으니 필요 없다"고 결론짓는 식이다. 같은 프롬프트에 `비슷한 파일이 있다는 이유만으로 기능이 같다고 단정하지 말라`를 넣어놓고 반대 방향의 질문을 하면 모순이다.
  - **정직함은 `실제 동작을 확인할 수 없다면 확인 불가라고 밝혀 주세요`가 담보한다.** 긍정적 활용점을 묻는 것이 거짓말을 유도하는 것은 아니다 — 근거가 없으면 없다고 말하게 돼 있다.
- **왼쪽 카드 설명도 같이** (2026-08-04, 한·영) — `활용도가 높은 기능과 필요성이 낮은 기능을 구분해서`는 프롬프트가 더 이상 묻지 않는 것이었다. **카드가 지키지 못할 약속을 하고 있었다.** `어느 자리에서 무엇이 도움이 될지 파일 단위로 짚어줘요`로 바꿨다.

## [0.37.3] - 2026-08-04
<!-- show:ko **`favicon.ico`를 추가했어요.** 페이지에는 원래 로고 파비콘이 선언돼 있었지만, 일부 도구는 HTML을 안 읽고 `/favicon.ico` 경로부터 찾습니다. 그때 404가 나서 아이콘이 안 보이거나 엉뚱한 게 나올 수 있었어요. 16·32·48px을 한 파일에 담아 7KB로 만들었습니다. -->
<!-- show:en **Added a `favicon.ico`.** The page already declared a PNG icon, but some tools skip the HTML and go straight to `/favicon.ico`, which returned 404. The new file packs 16, 32 and 48 pixel versions into 7KB. -->

### Added
- **`docs/favicon.ico`** (2026-08-04) — `<link rel="icon">`으로 PNG를 선언해 두었지만 **`/favicon.ico`는 404**였다. HTML을 파싱하지 않고 그 경로부터 찾는 도구(일부 크롤러·리더·구형 클라이언트)에서는 아이콘이 안 뜬다. 16·32·48px을 한 파일에 담았다(7KB) — 256px까지 넣으면 60KB가 되는데, 고해상도는 이미 PNG 선언이 담당하므로 넣지 않았다.
  - **완전한 해결은 아니다.** 이 사이트는 `jx-hxxx.github.io/hi-vibe/` 아래라, **도메인 루트**(`jx-hxxx.github.io/favicon.ico`)를 찾는 도구에는 여전히 안 잡힌다. 그건 이 저장소가 어쩔 수 없는 자리다.

## [0.37.2] - 2026-08-04
<!-- show:ko **"이 저장소는 스스로를 관리한다(dogfooding)"가 절반만 사실이었어요.** 문서 체계는 hi-vibe 방식을 쓰지만 훅은 이 저장소에서 켠 적이 없습니다. 그런데 그렇게 적어두니, `doctor`가 매번 "아직 init 안 함"이라고 알려주는 걸 정상으로 읽고 넘겼어요. 켜면 안 되는 이유가 분명한데(만드는 중인 버전이 만드는 곳에 파일을 쓴다) 그 이유가 어디에도 없었습니다. 이제 적혀 있어요. -->
<!-- show:en **"This repository manages itself with hi-vibe" was only half true.** The document system follows hi-vibe's conventions, but the hooks have never been enabled here. Because the file said otherwise, the `doctor` line reporting "not initialised" was read as normal noise every time. There is a good reason not to enable them — a version under development would be writing into the place it is being developed — and that reason was written down nowhere. Now it is. -->

### Fixed
- **`.claude/CLAUDE.md`의 dogfooding 서술** (2026-08-04) — `hi-vibe 문서 시스템으로 스스로를 관리한다`고만 적혀 있어 **훅도 도는 것처럼 읽혔다.** 실제로는 `.hi-vibe/` 마커가 없어 훅이 한 번도 안 돌았다. 그 결과 오늘 `doctor`를 여러 번 돌리면서 `아직 init 안 함` 경고를 **매번 정상으로 읽고 넘겼다** — 문서가 신호를 무디게 만든 사례다.
  - 켜지 않는 이유를 같이 적었다: ①만드는 중인 버전이 만드는 곳에 파일을 쓴다(2026-08-02에 Bash 명령 원문이 handover로 복사되는 유출이 있었다 — 켜져 있었으면 이 저장소에 남았다) ②훅은 **설치된 캐시 버전**에서 돌므로 지금 고치는 소스가 아니라 옛 버전이 검사한다.
  - **`doctor`의 "아직 init 안 함"은 정상이고 의도한 상태**라고 못박았다. 안 적으면 다음에 또 누가 켠다.

## [0.37.1] - 2026-08-04
<!-- show:ko **별표가 그대로 보이던 자리를 여덟 곳 고쳤어요.** 닫는 `**` 바로 앞에 따옴표나 괄호가 오면 마크다운이 굵게로 안 읽습니다. 한국어는 조사가 바로 붙어서 유독 자주 걸려요. 이 문제는 7월 28일에 이미 한 번 고치면서 "전수 확인했다"고 적었는데 그 뒤로 여덟 건이 다시 쌓였습니다. 사람이 한 번 훑는 걸로는 안 되는 종류라 검사를 붙였어요. -->
<!-- show:en **Eight places where the asterisks were showing literally are fixed.** A closing `**` preceded by a quote or a bracket is not read as bold, and Korean particles attach directly, so it happens constantly. This was already fixed once in July, with a note saying every occurrence had been checked — eight more accumulated afterwards. A one-time sweep clearly is not enough, so it is a test now. -->

### Fixed
- **볼드가 깨져 별표가 노출되던 것 8곳** (2026-08-04) — 닫는 `**` 앞이 문장부호(`"` `)`)이고 뒤가 글자면 CommonMark가 **닫는 표시로 인정하지 않는다**. 따옴표·괄호를 볼드 밖으로 뺐다(`"**굵게**"를`). README 한 1곳 · `.claude/CLAUDE.md` 2곳 · CHANGELOG 7곳.
  - **`show:` 주석 안의 것은 랜딩에도 그대로 나갔다** — `build-showcase.py`는 맨 앞 볼드만 `<b>`로 바꾸고 나머지는 `<span>`에 그대로 넣기 때문이다.

### Added
- **`test_markdown_bold.py`** (2026-08-04) — **이건 재발이다.** 2026-07-28 항목에 같은 문제를 고치며 `같은 패턴이 더 있는지 정규식으로 전수 확인했다`고 적었는데, 그 뒤로 여덟 건이 쌓였다. **한 번 훑는 것으로는 안 되는 종류**라 기계로 옮겼다. 백틱 안(이렇게 쓰면 깨진다고 인용하는 자리)은 제외하고, 잡아야 할 4문장·놓치면 안 될 5문장으로 양쪽을 고정했다.

## [0.37.0] - 2026-08-04
<!-- show:ko **README를 766줄에서 85줄로 줄였어요.** 소개 사이트가 이미 전체 명령어·작동 원리·FAQ·적합성 평가 질문을 다 갖고 있는데, README가 같은 설명을 한 번 더 하고 있었습니다. 오늘 하루에 난 문서 사고가 전부 "같은 말이 두 곳에 있어서" 생긴 것이었어요. 이제 사이트는 "왜 설치하지?", README는 "어떻게 설치하고 쓰지?"만 답합니다. 설치·첫 실행·알아둘 점(기록되는 것·끄는 법·한계)만 남기고 나머지는 사이트로 보냈어요. -->
<!-- show:en **The README went from 766 lines to 85.** The site already carries every command, how it works, the FAQ and the fit-check prompt, and the README was repeating all of it. Every documentation defect today came from the same sentence living in two places. The site now answers "why install this?" and the README answers "how do I install and use it?" — install, first run, and the things worth knowing (what gets recorded, how to turn it off, the limits) stay; everything else moved. -->

### Changed
- **README를 설치 안내로 축소** (2026-08-04, 한 766→85줄 · 영 789→89줄) — 사이트와 README가 **같은 설명을 두 번** 하고 있었다. 오늘 난 문서 사고(FAQ 답 불일치 · 평가 프롬프트 네 버전 뒤처짐 · "훅 4종"이 열 곳 · 히어로 문구 어긋남)가 **전부 중복이 갈린 것**이었다. 남긴 것: 한 줄 소개 + 사이트 링크 · 설치 · `init`→`doctor`→평소처럼 · 알아서 해주는 것 5줄 · 알아둘 점 5개 · 더 보기 · 라이선스.
  - **`check`를 필수처럼 쓰지 않았다.** `init`·`doctor` 한 번씩이면 끝이고 `check`는 "기존 코드 전체 점검 — 필요할 때만"이다. **그다음엔 아무것도 외울 필요가 없다**가 이 도구의 약속이다.
  - 뺀 것(전부 사이트에 있음): 프롬프트 묶음과의 비교 80줄 · 왜 믿을 만한가 53줄 · `check` 상세 61줄 · 작성 전후 검증 50줄 · FAQ 61줄 · 명령어 표 66줄 · 선택 연동 39줄 · 평가 프롬프트 37줄.
- **검사가 보는 자리를 옮겼다** (2026-08-04) — `test_command_modes`·`test_eval_prompt_sync`가 README를 읽고 있어서 **테스트가 README의 모양을 붙잡고 있었다.** 도구가 제품을 인질로 잡는 구조다. 두 검사 모두 **랜딩과 `commands/`만** 보게 하고, README에는 그 주장이 **다시 들어오지 않는지**를 지킨다.
  - **이건 검사 범위를 몰래 좁힌 게 아니다.** 그 원칙은 *주장은 남아 있는데 검사만 뺄 때* 적용된다. 여기서는 주장 자체를 지웠으므로 검사할 것이 없고, 대신 "없는 상태"를 새로 지킨다 — 슬그머니 돌아오면 검사받지 않는 사본이 되기 때문이다.
- **`.claude/CLAUDE.md`에 단일본 규칙 기록** (2026-08-04) — 명령어 분류표·평가 프롬프트·기능 설명의 **유일본은 랜딩**이다. 그 대가로 **랜딩이 죽으면 README만으로는 알 수 없다**는 것도 적어뒀다 — 알고 감수한 것과 모르고 당하는 것은 다르다.

## [0.36.1] - 2026-08-04
<!-- show:ko **README의 평가 프롬프트가 랜딩보다 몇 버전 뒤처져 있었어요.** 같은 질문이 네 곳(랜딩·README 한·README 영·내부 아카이브)에 있는데, 랜딩만 고치고 나머지를 안 봤습니다. 넷을 다 맞추고, **다음부터는 기계가 지키게** 검사를 붙였어요. 한 곳이라도 달라지면 테스트가 실패합니다. 아카이브 파일 첫머리에 "두 벌이 갈리면 이 파일이 거짓말이 된다"고 적어놓고 정작 사람 눈에 맡기고 있었거든요. -->
<!-- show:en **The README's evaluation prompt had fallen several versions behind the landing page.** The same question lives in four places, and only the landing was kept current. All four now match, and a test enforces it from here on. The archive file opened by saying that a divergence would make it a lie, and then relied on someone noticing. -->

### Fixed
- **README의 평가 프롬프트가 옛 버전** (2026-08-04, 한·영) — 랜딩(`docs/index.html`)의 `audit-prompt-*`가 원본인데 README는 v0.27 무렵 문구를 그대로 갖고 있었다. **사람이 복사해 쓰는 글**이라 옛 질문이 그대로 퍼진다. 랜딩 내용으로 교체했다.

### Added
- **`test_eval_prompt_sync.py`** (2026-08-04) — 네 곳(랜딩·README 한·README 영·`docs/internal/eval-prompt.md`)이 **글자까지 같은지** 확인한다. 랜딩을 원본으로 삼는 이유는 거기가 **복사 버튼이 달린 자리**라 실제로 가장 많이 쓰이기 때문이다. `[내 프로젝트 GitHub 링크]` 자리표시자가 살아 있는지도 본다 — 그게 없으면 AI가 hi-vibe만 보고 답해서 질문이 반쪽이 된다.
  - 아카이브 파일은 첫머리에 `페이지가 바뀌면 여기도 같이 고친다 — 두 벌이 갈리면 이 파일이 거짓말이 된다`고 적어두고 **사람 눈에 맡기고 있었다.** 그 약속을 기계로 옮겼다.

## [0.36.0] - 2026-08-04
<!-- show:ko **README에 "fresh-eyes는 hi-vibe가 직접 만든 것"이라는 말이 어디에도 없었어요.** 스킬 6개는 표로 정리돼 있는데 에이전트 2개는 본문에 흩어져만 있어서, `fresh-eyes 에이전트`라고만 보면 Claude Code 기본 기능으로 읽힐 수 있었습니다. 에이전트 표를 새로 넣고 **둘 다 hi-vibe가 만들어 함께 배포한다**고 적었어요. 그리고 `fresh-eyes`는 코드를 의심하고 `proof-eyes`는 스캐너를 의심한다는 차이도 같이요 — 이름만 보고 바꿔 쓰면 리뷰가 헛돕니다. -->
<!-- show:en **Nowhere did the README say that `fresh-eyes` is an agent hi-vibe wrote.** The six skills had a table; the two agents were only mentioned in passing, so "the `fresh-eyes` agent" could read as a Claude Code built-in. There is now an agent table stating that **both ship with hi-vibe**, along with the distinction that `fresh-eyes` doubts the code while `proof-eyes` doubts the scanner. -->

### Added
- **"내부 에이전트 구성" 표** (2026-08-04, README 한·영) — 스킬 6개는 표로 있는데 **에이전트 2개는 표가 없었다.** `fresh-eyes`·`proof-eyes`가 `agents/` 폴더에 들어 있는 **hi-vibe 소유물**이라는 사실이 README 어디에도 없어, Claude Code 기본 기능으로 읽힐 여지가 있었다. 언제 불리는지와 **무엇을 의심하는지**(코드 ↔ 스캐너)를 같이 적었다 — 이 구분은 CLAUDE.md에 함정으로 적혀 있는데 정작 사용자 문서에는 없었다.

### Changed
- **겹침 표의 `review` 행** (2026-08-04, 한·영) — `자기 체크리스트와 fresh-eyes 에이전트로 봅니다` → `자기 체크리스트와 **hi-vibe가 직접 만든 fresh-eyes 서브에이전트**로 봅니다`. 이 표는 "겹치나?"를 묻는 사람이 제일 먼저 보는 자리다.

## [0.35.2] - 2026-08-04
<!-- show:ko **README의 "겹치지 않나요?" 답을 한 문장으로 끝냈어요.** "꽤 겹칩니다."만 있으면 질문에 "네"만 하고 멈춘 셈이라, 랜딩과 같이 "하지만 다른 점도 많아요"를 붙였습니다. -->
<!-- show:en **The README answer to "doesn't this overlap?" now finishes the thought.** "Quite a bit" alone answered yes and stopped; it now says what the landing page says — plenty is different, too. -->

### Changed
- **README FAQ 첫 줄** (2026-08-04, 한·영) — `꽤 겹칩니다.` → `꽤 겹칩니다. 하지만 다른 점도 많아요.` 랜딩은 v0.29.7에서 이미 이렇게 고쳤는데 **README만 옛 문장이었다.** 질문이 "겹치지 않나요"인데 "네"만 하고 멈추면 답이 완결되지 않는다.

## [0.35.1] - 2026-08-04
<!-- show:ko **영문 제목 두 개에 남아 있던 강제 줄바꿈을 뺐어요.** 한국어는 v0.29.1에서 이미 뺐는데 영문만 그대로였습니다. 이제 화면 너비에 맞춰 자연스럽게 흐르고, 넓은 화면에서는 한 줄로 나와요. -->
<!-- show:en **Two English headings no longer carry a hard line break.** The Korean side lost these in v0.29.1 and the English side was missed. They now flow with the viewport and sit on one line where there is room. -->

### Fixed
- **영문 제목의 강제 줄바꿈** (2026-08-04) — `If any of this<br>sounds familiar`, `What would it do<br>in your project?`. 한국어는 v0.29.1에서 뺐는데 **영문만 남아 있었다** — 한쪽만 고치고 반대쪽을 안 본 그 패턴이 또 나왔다. `h2`에 이미 `text-wrap:balance`가 있어 줄바꿈은 브라우저가 알아서 한다.
  - `여기까진 기계가.<br>여기서부턴 AI가.`와 영문 짝은 **그대로 뒀다** — 문장이 둘이고 대비가 구조라서 붙이면 뜻이 흐려진다.

## [0.35.0] - 2026-08-04
<!-- show:ko **헤더의 "설치"와 "명령어"가 사실상 같은 데로 가고 있었어요.** 설치 터미널이 명령어 섹션 **안에** 있어서, 두 메뉴를 눌러도 화면이 거의 안 움직였습니다. "명령어"를 "설치 & 명령어"로 합치고, 빈자리를 "나한테 맞나"로 채워 "이런 불편을 겪고 있다면" 섹션으로 보냅니다. 처음 온 사람이 제일 먼저 궁금한 건 설치법이 아니라 **이게 나한테 필요한가**니까요. -->
<!-- show:en **"Install" and "Commands" in the header led to almost the same place.** The install terminal sits inside the commands section, so both links landed within a screen of each other. They are merged into "Install & commands", and the freed slot became "Good fit?", pointing at the section that helps you decide whether this is for you — which is the first thing a newcomer actually wants to know. -->

### Changed
- **헤더 메뉴 정리** (2026-08-04) — `#install-ko`는 **`#commands-ko` 섹션 안의 터미널 상자**다. 두 메뉴가 사실상 같은 자리로 가고 있었다. `명령어` → `설치 & 명령어`로 합치고, 첫 항목을 `나한테 맞나`(`#audit-ko`)로 바꿨다. **처음 온 사람의 첫 질문은 "어떻게 설치하나"가 아니라 "이게 나한테 필요한가"다.** 영문도 `Good fit?` / `Install & commands`로.
- **중간 너비에서 메뉴 간격 축소** (2026-08-04) — 라벨이 길어져 1080px 부근에서 좁아진다. 760px 아래로는 어차피 숨기므로 그 위 구간만 `gap:30px→20px`, `13px→12.5px`.

## [0.34.5] - 2026-08-04
<!-- show:ko **"설치는 전역 한 번" 안내에서 마지막 한마디가 줄을 넘어가던 것을 고쳤어요.** 92자를 79자로 줄여 한 줄에 담았습니다. 같은 칸의 다른 줄이 84자로 한 줄에 들어가니 이제 안 넘어가요. 뜻은 그대로고 군더더기만 뺐습니다. -->
<!-- show:en **The last clause of the install note no longer spills onto a second line.** The sentence was tightened from 92 to 79 characters; a neighbouring line at 84 characters fits on one line, so this now does too. The meaning is unchanged. -->

### Fixed
- **`폴더에서만 돌거든요.`가 줄을 넘어가던 것** (2026-08-04) — `쓰고 싶은 프로젝트마다, 그 최상위 폴더에서` → `쓸 프로젝트마다 최상위 폴더에서`, `.hi-vibe/ 마커가 만들어진 폴더에서만 돌거든요` → `.hi-vibe/가 있는 폴더에서만 돌아요`. 92자 → 79자. **줄바꿈을 강제하지 않고 문장을 줄였다** — 같은 칸의 다른 줄(84자)이 한 줄에 들어가는 것을 재서 기준으로 삼았다.

## [0.34.4] - 2026-08-04
<!-- show:ko **"아니면 16개가 떠요" 한마디를 지웠어요.** 줄바꿈 때문에 문장을 줄였는데, 다시 보니 그 절 자체가 없어도 되는 말이었습니다. 스킬을 왜 숨겼는지는 앞 문장이 이미 말하고 있어요. 영문도 같이 지웠습니다. -->
<!-- show:en **Dropped the "otherwise you'd see 16 entries" aside.** It was trimmed for line-wrapping reasons, and on a second look the clause was not carrying anything the preceding sentence had not already said. Removed in both languages. -->

### Changed
- **`아니면 16개가 떠요.` 삭제** (2026-08-04, 한·영) — v0.34.3에서 줄바꿈 때문에 문장을 줄였는데, **그 절 자체가 없어도 되는 말이었다.** 왜 숨겼는지(엔진이라서)는 앞 문장이 이미 말한다. 줄을 맞추려고 문장을 깎는 것보다 **안 필요한 문장을 지우는 게 먼저다.**

## [0.34.3] - 2026-08-04
<!-- show:ko **"안 그러면 16개가 떠요"가 혼자 다음 줄로 넘어가던 것을 고쳤어요.** 문장을 11자 줄여 한 줄에 담았습니다. 덜어낸 건 "엔진이지 버튼이 아니라서"인데, 바로 위 소제목이 이미 "스킬(엔진) ↔ 명령어(버튼)"이라 같은 말을 두 번 하고 있었어요. -->
<!-- show:en **A short trailing clause no longer falls onto its own line.** The sentence was shortened by trimming the engine-versus-button contrast, which the heading directly above it already makes. -->

### Fixed
- **짧은 뒷절이 혼자 줄바꿈되던 것** (2026-08-04) — `안 그러면 16개가 떠요.`만 다음 줄로 떨어졌다. 69자 → 58자로 줄여 한 줄에 넣었다. **덜어낸 건 중복이다** — `엔진이지 버튼이 아니라서`는 바로 위 소제목(`뒤에서 뭐가 도나 — 스킬(엔진) ↔ 명령어(버튼)`)이 이미 말한다. 줄바꿈을 강제하는 대신 **같은 말을 두 번 하는 쪽을 지웠다.**

## [0.34.2] - 2026-08-04
<!-- show:ko **첫 화면의 "Python 3.8+프로젝트에 최적화"가 붙어 보이던 것을 고쳤어요.** 원인이 좀 뜻밖이었는데, 그 줄이 flex 배치라서 태그 사이의 공백이 통째로 버려지고 있었습니다. 영문에서는 공백 두 개가 사라지고 있었어요. 그리고 문장 끝이 "합니다"와 "해요"로 섞여 있던 것도 맞췄습니다 — 공식 문서 인용과 AI에 붙여넣는 프롬프트는 원래 말투 그대로 뒀고요. "중복 찾아줘"가 줄 끝에서 잘려 두 줄로 나뉘던 것도 붙였습니다. -->
<!-- show:en **"Python 3.8+ projects" was rendering with the space missing.** The cause was less obvious than it looked: that line is a flex row, and whitespace between elements inside a flex container is discarded entirely — the English version was losing two spaces. Sentence endings that mixed formal and casual Korean were also unified, leaving the official-docs quote and the copy-paste prompt in their original register. A quoted phrase that broke across two lines was pinned back together. -->

### Fixed
- **`display:inline-flex`가 태그 사이 공백을 먹던 것** (2026-08-04) — `.hero .micro span`이 inline-flex라 `<b>Python 3.8+</b> 프로젝트에`의 공백이 **flex 항목 경계로 취급돼 사라졌다**(`3.8+프로젝트에`). 영문 `Built for <b>…</b> projects`는 **공백 두 개**를 잃고 있었다. 체크 표시는 `::before`라 `inline-block`으로도 그대로 붙으므로 그렇게 바꿨다. `gap` 없는 나머지 flex 규칙 7개도 같이 확인했다 — 자식이 전부 태그라 해당 없음.
- **인용구가 줄 끝에서 갈리던 것** (2026-08-04) — `② “중복 찾아줘”라고 말하기`가 두 줄로 쪼개졌다. 두 경로를 각각 `white-space:nowrap`으로 묶고, 앞 문장과도 줄을 나눴다.

### Changed
- **한국어 랜딩의 말투 통일** (2026-08-04) — `습니다`와 `해요`가 섞여 있었다. 본문 8곳을 `해요`로 맞추고, **Claude Code 공식 문서 인용**과 **AI에 붙여넣는 프롬프트 본문**은 그대로 뒀다 — 인용은 원문이 맞고, 프롬프트는 사용자가 보내는 글이라 격식체가 자연스럽다.

## [0.34.1] - 2026-08-04
<!-- show:ko **첫 화면에도 "빼는 법"을 넣었어요.** README에만 있던 걸 랜딩 명령어 섹션의 빠른 시작 바로 아래로 올렸습니다. 자동만 잠깐 끄기(Claude에게 "이 프로젝트에선 꺼줘"라고 말하거나 파일 하나 만들기), 이 프로젝트에서 빼기, 플러그인 자체 지우기, 그리고 만들어진 문서는 어떻게 되는지까지 네 줄이에요. **빼는 전용 명령어는 만들지 않았습니다** — 외울 게 하나 더 느는 대신, 이미 있는 방법을 보이게만 했어요. -->
<!-- show:en **The landing page now shows how to remove it, too.** What was only in the README moved up next to the quick-start rows in the commands section: silence the automation (say so to Claude, or create one file), remove it from this project, uninstall the plugin, and what happens to the documents. **No dedicated command was added** — that would be one more thing to remember; the existing routes were simply made visible. -->

### Added
- **랜딩에 "이 프로젝트에서 빼고 싶다면"** (2026-08-04, 한·영) — v0.34.0에서 README에 적었지만 **첫 화면에서는 여전히 안 보였다.** 빠른 시작과 같은 `.quickstart` 구조를 재사용해 새 CSS 없이 넣었다. 네 줄: `optout`(말로 하거나 파일 하나) · `.hi-vibe/` 삭제 · 플러그인 제거 · **문서는 남는다**.
  - **`/hi-vibe:optout` 명령은 만들지 않았다.** 명령이 11개가 되고, 랜딩이 내세우는 "명령어 10개 — 외울 게 적다"가 깨진다. `optout`은 이미 스킬이 말로 처리하고 파일 하나면 되는 일이라 **새 표면을 늘릴 값이 없다.**
  - 마지막 줄(문서는 남는다)을 굵게 둔 이유: "지우면 다 날아가나?"가 실제로 제일 큰 걱정이고, 그게 안 보이면 나머지를 읽어도 불안하다.

## [0.34.0] - 2026-08-03
<!-- show:ko **무엇을 읽고 무엇을 남기는지, 그리고 어떻게 끄는지를 README에 한곳으로 모았어요.** 기능은 그대로입니다. 어제 기록 시점을 네 배로 늘리고(`/clear`·창 닫기·resume·로그아웃) Bash 항목까지 추가했는데 고지는 어제 문장 그대로였거든요. 읽는 범위(대화 기록 마지막 512KB), 남기는 항목(요청 5개·각 120자, 파일 경로, Bash는 대상 이름만), 저장 위치, 그리고 **비밀키는 가리지만 일반 민감 정보는 안 가린다**는 한계까지 적었습니다. 끄는 방법도 네 가지로 나눠 적었어요 — 잠깐 끄기, 프로젝트에서 빼기, 플러그인 지우기, 그리고 만들어진 문서는 어떻게 되나. -->
<!-- show:en **The README now states, in one place, what is read, what is written down, and how to turn it off.** No behaviour changed. Yesterday the number of moments that write a record went from one to four and a Bash field was added, while the disclosure stayed as it was. It now covers the read window (last 512KB of the transcript), every stored field (5 requests at 120 characters each, file paths, and for Bash only the target name), where it is stored, and the limit that **secrets are masked but ordinary sensitive information is not**. Turning it off is split into four distinct things, including what happens to the documents. -->

### Added
- **"무엇을 읽고 무엇을 남기나요?" 섹션** (2026-08-03, README 한·영) — 자동 기록이 있는 도구인데 **읽는 범위·저장 항목·저장 위치·중지 방법이 한곳에 없었다.** 어제 기록 시점을 넷으로 늘리고(`/clear`·`prompt_input_exit`·`resume`·`logout`) Bash 항목을 더하면서 **고지만 그대로 뒀다** — 밀린 빚이었다.
  - **"모든 처리는 로컬"이라고 쓰지 않았다.** `ci_health()`가 `gh` CLI로 GitHub에 현재 브랜치의 워크플로 결과를 조회한다(브랜치 이름이 나간다). 대화 내용은 안 나가지만 **네트워크는 탄다** — 신뢰를 올리려는 문장이 과장이 되면 안 된다.
  - **비밀키 가림의 한계를 명시했다** — 정규식 판정이라 사람 이름·주소·사내 용어 같은 일반 민감 정보는 그대로 남는다. "사용자 요청은 평문으로 저장된다고 보시는 게 맞습니다"라고 적었다.
- **"끄기와 지우기" 섹션** (2026-08-03, README 한·영) — `.hi-vibe/optout`은 v0.20대부터 있었지만 **`write-gate` 스킬 파일 안에만** 적혀 있었다. 사용자가 볼 일이 없는 자리다. 네 가지를 구분했다: ①`optout`으로 잠깐 끄기(명령어는 그대로 동작) ②`.hi-vibe/` 삭제로 프로젝트에서 빼기 ③플러그인 제거 ④**만들어진 문서는 남는다**(전부 사용자 파일이다). **나갈 때가 들어올 때보다 쉬워야 한다.**

### 확인
- 사실 대조: 512KB(`tail_lines`) · 요청 5개·120자(`parse_transcript`) · 파일 15개·Bash 5개(`handover_body`) · 회전 20개 초과 시 아카이브(`rotate`) · `.gitignore` 항목(docs-keeper 5단계) · `optout`이 훅만 끄고 명령은 안 막는 것 — **적기 전에 전부 소스에서 확인했다.**

## [0.33.2] - 2026-08-03
<!-- show:ko **변수 이름에 `example`·`your`·`dummy`가 들어 있으면 진짜 키를 놓치고 있었어요.** 자리표시자인지 판정하는 범위를 어제 "줄 전체"에서 "매치 전체"로 좁혔는데, 매치에는 값뿐 아니라 **변수 이름도 들어갑니다.** 그래서 `EXAMPLE_API_KEY`·`YOURCOMPANY_API_KEY`·`DUMMY_SERVICE_TOKEN`이 전부 통과했어요. 회사 이름이 YourCompany인 곳에서는 멀쩡한 키가 전부 새는 셈입니다. 이제 따옴표 안의 **값만** 보고 판정해요. 이름은 자리표시자 여부와 아무 상관이 없습니다. -->
<!-- show:en **A real key was missed whenever the variable name contained `example`, `your` or `dummy`.** The placeholder check was narrowed yesterday from the whole line to the whole match — but a match includes the variable name as well as the value, so `EXAMPLE_API_KEY`, `YOURCOMPANY_API_KEY` and `DUMMY_SERVICE_TOKEN` all slipped through. At a company literally named YourCompany, every key would leak. The judgment now looks only at the quoted value; the name has nothing to do with whether something is a placeholder. -->

### Security
- **변수명 속 자리표시자 단어가 진짜 값을 가리던 것** (2026-08-03) — 자리표시자 판정 범위를 **두 번** 좁혔다. ①줄 전체 → `example = "demo"; API_KEY = "진짜키"`가 통과 ②매치 전체 → **매치에 변수명이 포함되어** `EXAMPLE_API_KEY = "진짜키"`가 통과. 할당 정규식에 `(?P<value>…)`를 두고 **값에만** 판정한다. 값 그룹이 없는 패턴(`sk-ant-`·`AKIA`·`ghp_` 등)은 매치 자체가 값이므로 그대로 쓴다.
  - 좁히면서 잃은 게 없는지 같이 고정했다: 값이 자리표시자면 여전히 억제(`your_key_here_placeholder`·`example_value_1234567`·`xxxx_…`), 환경변수 참조도 여전히 무시(`os.environ[...]`·`${…}`·`process.env.…`).

### Added
- **탐지 경계 테스트 3개** (2026-08-03) — 이름에 자리표시자 단어가 든 5종을 잡는지 · 값이 자리표시자인 5종을 안 잡는지 · 환경변수 참조 3종을 안 잡는지. **범위를 좁힐 때마다 반대편이 깨진다** — 이 항목만 세 번째 조정이라 양쪽을 같이 본다.

### 확인
- 자기 저장소 스캔 비밀키 **0건** — 세 번째로 좁혔는데도 오탐이 늘지 않았다.

## [0.33.1] - 2026-08-03
<!-- show:ko **플러그인 검증(`--strict`)이 실패하던 것을 고쳤어요.** 저장소 루트의 `CLAUDE.md`가 "플러그인 루트에 두면 플러그인 컨텍스트로 로드되지 않는다"는 경고를 내고 있었습니다. 이 파일은 배포용이 아니라 이 저장소가 자기를 hi-vibe로 관리하는 파일이라 스킬로 바꿀 수 없는데, 공식 문서를 보니 `./CLAUDE.md`와 `./.claude/CLAUDE.md` **둘 다 프로젝트 지침으로 자동 로드**됩니다. `.claude/` 안으로 옮겨 자기 규율은 그대로 두고 검증도 통과시켰어요. 옮기자마자 과장 검사가 이 파일을 놓치기 시작했는데(점으로 시작하는 폴더를 건너뜁니다) 그건 테스트가 잡아줬습니다. -->
<!-- show:en **`claude plugin validate --strict` no longer fails.** The repository's root `CLAUDE.md` triggered a warning: a CLAUDE.md at the plugin root is not loaded as plugin context. That file is not shipped context — it is how this repository manages itself with hi-vibe — so converting it to a skill was wrong. The official docs list `./CLAUDE.md` and `./.claude/CLAUDE.md` as equally auto-loaded project instructions, so moving it satisfies both. The move immediately dropped the file out of the overclaim scan (dot-directories are skipped); the test caught that. -->

### Fixed
- **`claude plugin validate --strict` 실패** (2026-08-03) — 경고: `CLAUDE.md at the plugin root is not loaded as project context. To ship context with your plugin, use a skill instead.` **검증기가 의도를 구분하지 못한다** — 이 파일은 배포물이 아니라 이 저장소의 자기 규율이다. 공식 문서가 `./CLAUDE.md` **또는** `./.claude/CLAUDE.md`를 프로젝트 지침 위치로 명시하므로 후자로 옮겼다. 스킬로 바꾸면 **항상 걸려야 할 규율이 조건부**가 되므로 그 길은 택하지 않았다. 왜 여기 있는지를 파일 안에 주석으로 남겼다(루트로 되돌리지 말 것).
- **옮기자 과장 검사가 이 파일을 놓치던 것** (2026-08-03) — `_surfaces()`가 점으로 시작하는 폴더를 건너뛰어 **가장 중요한 문서가 조용히 검사 밖으로 나갔다.** `test_scan_covers_the_real_surfaces`가 즉시 실패해 알려줬다 — "검사 범위가 조용히 좁아지는 것도 막는다"고 만들어 둔 테스트가 실제로 값을 했다. `.claude`만 예외로 훑는다.

### Added
- **같은 줄 자리표시자 오탐 억제 회귀 사례 확대** (2026-08-03) — 표현이 다른 6가지(주석 안의 `example`, 딕셔너리 키 `"example"`, `EXAMPLE_MODE` 환경변수, 한국어 문장 속 `your`…)로 넓혔다. **한 형태만 막으면 나머지로 그대로 빠져나간다** — 이 저장소가 `runs it` → `Stop ── run the review` → `리뷰를 돌린 뒤`로 세 번 겪은 방식이다.

## [0.33.0] - 2026-08-03
<!-- show:ko **비밀키를 "찾는 단계"가 생각보다 좁았어요.** `OPENAI_API_KEY`·`DJANGO_SECRET_KEY`·`ACCESS_TOKEN`·`DATABASE_PASSWORD`·`"client_secret"` 전부 못 잡고 있었습니다. 정규식이 키워드 바로 뒤에 `=`가 오기를 기대해서, 이름 앞에 뭐가 붙거나 뒤에 `_KEY`가 붙으면 빠져나갔어요. 예외적인 이름이 아니라 관례에 가까운 것들이라 지금 고쳤습니다. 그리고 더 나빴던 건 자리표시자 판정을 **줄 전체**에서 하던 것 — `example = "demo"; API_KEY = "진짜키"`처럼 같은 줄에 `example`이 있다는 이유로 진짜 키가 통과했습니다. 오탐을 줄이려다 놓치면 그건 개선이 아니라 구멍이에요. -->
<!-- show:en **The step that finds secrets was narrower than it looked.** `OPENAI_API_KEY`, `DJANGO_SECRET_KEY`, `ACCESS_TOKEN`, `DATABASE_PASSWORD` and `"client_secret"` were all missed: the pattern expected `=` immediately after the keyword, so anything prefixed or suffixed slipped through. These are conventions, not exotic names, so they are handled now. Worse, placeholder suppression looked at the whole line — `example = "demo"; API_KEY = "realkey"` passed because `example` appeared somewhere on it. Reducing false positives by creating a hole is not an improvement. -->

### Security
- **흔한 변수명을 못 잡던 것** (2026-08-03) — 할당 패턴이 `\b(?:api[_-]?key|secret|token|…)` 바로 뒤에 `["']?\s*[:=]`를 요구했다. 그래서 **앞에 붙는 것**(`OPENAI_`·`DATABASE_`)과 **뒤에 붙는 것**(`SECRET_KEY`)이 전부 빠져나갔다. 식별자 앞부분(`[A-Za-z0-9_.\-]*`)을 허용하고 `secret[_-]?key`·`private[_-]?key`를 더했다. **키워드가 식별자 끝일 때만** 잡으므로 `TOKENIZER = "…"`·`TOKEN_EXPIRY = "…"`·`SECRET_KEY_LENGTH = "…"`는 여전히 안 걸린다 — 넓히되 아무 데나 넓히지 않는 지점이 여기다.
- **자리표시자 판정 범위** (2026-08-03) — `example`·`your`·`dummy` 같은 단어를 **줄 전체**에서 찾아 억제했다. `example = "demo"; API_KEY = "진짜키"` 한 줄이면 진짜 키가 통과한다. 이제 **매치 안에서만** 본다(`API_KEY = "your_key_here"`는 그대로 억제). `allow-secret` 표시만 줄 전체에서 찾는다 — 그건 매치 밖(닫는 괄호 뒤)에 다는 게 정상이라서다.

### Added
- **탐지 범위 회귀 테스트 4개** (2026-08-03) — 흔한 이름 9종을 잡는지 · 평범한 변수 5종을 안 잡는지 · 같은 줄의 자리표시자 단어에 속지 않는지 · **값 안의** 자리표시자는 여전히 억제하는지. 넓히기만 하면 잔소리가 되므로 양쪽을 같이 고정한다.

### 확인
- 저장소 자기 스캔 비밀키 **0건** — 넓히고도 오탐이 늘지 않았다.

## [0.32.4] - 2026-08-03
<!-- show:ko **비밀키 가림 처리가 경계에서 어긋나던 것을 고쳤어요.** 두 방향으로 틀렸습니다. ①`API_KEY     =     "..."`처럼 공백이 많으면 키 꼬리가 남았어요 — 끝 위치를 "정규화된 조각 길이"로 추정했는데 정규화가 공백을 접기 때문입니다. ②반대로 두 패턴이 같은 자리를 잡으면 겹친 구간을 안 합친 채 차례로 지워서, 키 뒤의 멀쩡한 문장까지 날아갔어요. 이제 실제 끝 위치를 받아 겹친 구간을 합친 뒤 한 번에 가립니다. 넓은 공백·줄바꿈 할당·한 줄 복수 키·겹친 패턴을 각각 테스트로 고정했어요. -->
<!-- show:en **Secret masking was off at the boundaries, in both directions.** (1) With wide spacing like `API_KEY     =     "..."` the tail of the key survived, because the end position was estimated from the length of the whitespace-normalised snippet. (2) Conversely, when two patterns covered the same place, the overlapping ranges were replaced one by one and swallowed the ordinary sentence after the key. Real end offsets are now returned, overlapping ranges merged, and the replacement done once. Wide spacing, newline assignments, several keys on one line and overlapping patterns are each pinned by a test. -->

### Fixed
- **가림 처리가 키 꼬리를 남기던 것** (2026-08-03) — `safe_text()`가 끝을 `시작 + len(정규화된 조각)`으로 추정했다. `iter_secrets`는 공백을 접은 조각을 주므로, 원문에 공백이 많으면 **추정한 끝이 실제보다 앞**이다: `API_KEY     =     "ABCDEFGHIJKLMNOPQRSTUVWX"` → `[비밀키 가림]RSTUVWX"`. `iter_secret_spans()`를 새로 두어 **원문 기준 실제 `m.start()`·`m.end()`**를 돌려준다. 기존 `iter_secrets`는 그걸로 파생시켜 판정 규칙은 여전히 한 곳이다.
- **가림 처리가 뒤 문장까지 지우던 것** (2026-08-03) — 키 자체 패턴과 할당문 패턴이 **같은 자리를 겹쳐 잡는다.** 겹친 구간을 안 합치고 뒤에서부터 차례로 치환하면, 바깥 구간을 먼저 지운 뒤 안쪽 구간의 **옛 좌표**로 또 자른다. `API_KEY = "sk-proj-…" 뒤 문장` → `[비밀키 가림]`으로 문장이 통째로 사라졌다. 구간을 먼저 병합한다. **가리기가 문장을 먹으면 사람이 기록을 안 믿는다.**

### Added
- **가림 경계 테스트 4개** (2026-08-03) — 넓은 공백·줄바꿈·탭 할당에서 꼬리가 안 남는지 · 키 뒤 문장이 살아남는지 · 한 줄에 키 둘이면 둘 다 가려지고 사이 글자는 남는지 · 비밀키 없는 글은 **한 글자도 안 바뀌는지**. 덜 지워도 더 지워도 사고라 양쪽을 다 본다.

### 알려진 한계 (안 고침)
- **`SECRET_KEY`·`ACCESS_TOKEN` 같은 이름은 할당 패턴이 못 잡는다.** 정규식이 `secret`·`token` 바로 뒤에 `=`를 기대하는데 `_KEY`가 끼어 경계가 깨진다. 오늘 만든 결함이 아니라 탐지기의 기존 범위 문제이고, `\w*`로 넓히면 `TOKENIZER = "…"` 같은 오탐이 생긴다. **키 자체 형태 패턴(`sk-`·`AKIA`·`ghp_`…)은 이름과 무관하게 잡으므로** 실제 키 대부분은 여전히 걸린다. 실사용에서 놓친 사례가 나오면 그때 근거를 갖고 넓힌다.

## [0.32.3] - 2026-08-03
<!-- show:ko **handover가 비밀키 유출 통로가 될 수 있었어요. 오늘 제가 만든 결함입니다.** 몇 시간 전 "Bash로 쓴 것"을 기록에 싣게 했는데, 명령 원문을 그대로 넣었습니다. `printf 'API_KEY = "…"' > cfg.py` 하나면 트랜스크립트에만 있던 키가 프로젝트 파일로 복제되고, 다음 세션에 다시 주입되고, 아카이브에 오래 남습니다. 게다가 handover는 `.md`라 `check`의 비밀키 스캔 대상도 아니었어요. 정규식으로 가리는 건 새 패턴을 놓치니, **원문을 아예 저장하지 않도록** 고쳤습니다. 이제 대상 파일과 작업 종류만 남아요. 사용자 요청은 글 자체가 내용이라 안 남길 수 없어서 훅과 같은 규칙으로 가리고, `check`가 handover도 훑게 했습니다. -->
<!-- show:en **handover could have leaked secrets — a defect introduced earlier today.** When "written via Bash" was added to the record a few hours ago, it stored the raw command. One `printf 'API_KEY = "…"' > cfg.py` copies a key that lived only in the transcript into a project file, re-injects it into the next session, and preserves it in the archive. handover is a `.md` file, so the secret scan did not cover it either. Masking with regexes misses new patterns, so the raw text is simply never stored now: only the target file and the kind of write. User requests are content by nature, so those are masked with the same rule the hook uses, and `check` now scans handover as well. -->

### Security
- **Bash 명령 원문이 handover로 복제되던 것** (2026-08-03) — `bash_write_commands()`가 원문을 200자까지 보관하고 100자를 기록에 실었다. `printf 'API_KEY = "…"' > cfg.py` 같은 명령이 그대로 남아, **트랜스크립트에만 있던 값이 프로젝트 루트 파일·다음 세션 컨텍스트·`handover-archive.md`로 퍼진다.** `.gitignore` 덕에 즉시 커밋되지는 않지만, 공유 옵션을 켜면 커밋될 수 있다. **비밀키 안전장치를 내세우는 도구에서 날 일이 아니다.**
  - 정규식으로 가리는 방식은 **새 패턴을 놓친다.** 그래서 `bash_write_summary()`로 바꿔 **원문을 아예 갖지 않는다** — 보여주는 것은 `` `generated.py` — redirect ``처럼 대상과 종류뿐이고, 변화 감지에 필요한 것은 SHA-256 지문이면 충분하다. 표식 파일에도 원문이 안 남는다.
  - 대상 후보 토큰에 따옴표·`=`·공백·`$`가 있으면 **파일 이름이 아니라 내용일 수 있으므로 버린다**(`_SAFE_PATH_RE`). 그게 값이 새는 경로다.
- **사용자 요청·테스트 명령의 비밀키 가림** (2026-08-03) — 이쪽은 글 자체가 내용이라 안 남길 수가 없다. `safe_text()`가 훅의 `iter_secrets`(SSOT)로 판정해 `[비밀키 가림]`으로 바꾼다. Bash처럼 구조적으로 막는 게 아니라 **차선책**이라는 점은 분명히 해둔다.
- **`check`가 handover를 안 보던 것** (2026-08-03) — 비밀키 스캔 대상 확장자에 `.md`가 없어 **여기 복제된 키는 전체 스캔에도 안 걸렸다.** handover는 사람이 쓴 글이 아니라 기계가 트랜스크립트에서 뽑아 적는 파일이라, 뽑는 쪽이 실수하면 여기로 온다. `handover.md`·`handover-archive.md`는 확장자와 무관하게 훑는다(일반 `.md`는 그대로 제외 — 예시 코드가 많아 시끄러워진다).

### Added
- **유출 회귀 테스트 3개** (2026-08-03) — ①Bash 명령 원문이 handover·표식 어디에도 안 남고 **대상 파일 이름은 남는지**(안 남기면 기록이 아니라 침묵이다) ②요청 속 비밀키가 가려지고 나머지 문장은 살아남는지 ③`check`가 handover는 잡고 일반 `.md`는 안 잡는지.

## [0.32.2] - 2026-08-02
<!-- show:ko **auto-compact 뒤 Bash로만 작업한 구간이 여전히 사라지고 있었어요.** 어제 "Bash 수정도 서명으로 해결했다"고 적었는데 사실이 아니었습니다 — 서명에는 요청·Write/Edit 파일·테스트 결과만 들어 있었고 Bash는 빠져 있었어요. 새 사용자 메시지 없이 Claude가 같은 턴에서 Bash로만 파일을 만들면 서명이 그대로라 건너뛰었습니다. 이제 Bash 쓰기 명령을 서명에 넣고, 기록 본문에도 "Bash로 쓴 것(추정)"으로 싣습니다. 그리고 표식 파일을 읽고-고치고-쓰는 구간이 락 밖에 있어서, 두 세션이 정확히 동시에 끝나면 한쪽 표식이 사라질 수 있었어요. -->
<!-- show:en **Work done only through Bash after an auto-compact was still being dropped.** Yesterday's note claimed the content signature covered Bash edits; it did not — the signature held requests, Write/Edit files and test results, and nothing from Bash. When Claude continued the same turn with only Bash writes, the signature was unchanged and the entry was skipped. Bash write commands are now part of the signature and appear in the record itself. Separately, the marker file's read-modify-write sat outside the lock, so two sessions ending at the same instant could lose one marker. -->

### Fixed
- **auto-compact 뒤 Bash 전용 작업이 사라지던 것** (2026-08-02) — 서명이 `[prompts, edited, test]`였다. `edited`는 `Write|Edit|MultiEdit`만 모으므로 **Bash로 만든 파일은 어디에도 안 들어간다.** `사용자 요청 → Edit → auto compact → 같은 턴에서 Bash로 파일 생성 → /clear` 흐름에서 서명이 그대로라 통째로 건너뛰었다. `bash_write_commands()`(판정 규칙은 `bash_wrote_files`와 공유)를 서명에 넣었다. **있다/없다 불리언으로는 부족하다** — compact 전에도 Bash를 썼으면 둘 다 참이라 "그 뒤로 새 게 있나"에 답하지 못한다.
- **기록에 Bash 작업이 안 보이던 것** (2026-08-02) — 서명만 고쳤을 때는 항목이 **생기기는 하나 내용이 compact 때와 똑같았다**(빈 껍데기). 본문에 `- Bash로 쓴 것(추정):`을 추가해 최근 5개를 싣는다. `(추정)`을 붙인 이유는 `_BASH_WRITE_RE`가 대표적인 쓰기 명령만 잡기 때문이다.
- **표식 파일의 동시 쓰기 경쟁** (2026-08-02) — `handover-written.json`은 읽고-고치고-쓰는 구조인데 `note_handover_written()`이 **락 밖에서** 불렸다. 두 세션이 동시에 끝나면 한쪽 표식이 통째로 덮여 다음 종료에서 중복 항목이 생긴다. **확인 → 기록 → 표식**을 한 `file_lock` 안으로 넣었다(`pre_compact`도 같이).
- **어제 CHANGELOG의 과장 정정** (2026-08-02) — v0.32.0 항목에 "Bash 수정"을 고친 사례로 적었으나 사실이 아니었다. 그 줄에 정정을 달았다.

### Added
- **Bash 전용 작업 테스트 + 동시 종료 테스트** (2026-08-02) — 기존 테스트는 "새 파일 Edit · 같은 파일 Edit · 새 사용자 결정"뿐이라 Bash 경로가 없었다. **동시 종료는 타이밍 테스트만으로 부족하다** — 락을 빼고 세 번 돌렸더니 전부 통과했다(프로세스 기동 시간차로 실제로 겹치지 않는다). 그래서 "겹쳐도 살아남는가"(기능)와 "**표식이 락 블록 안에서 쓰이는가**"(구조)를 둘 다 본다. 구조 검사는 락 밖으로 옮기면 즉시 실패하는 것을 확인했다.

## [0.32.1] - 2026-08-02
<!-- show:ko **중복 방지 표식이 슬롯 하나뿐이라 다른 세션이 덮어쓰고 있었어요.** 같은 프로젝트에 Claude Code 창을 두 개 띄우면 실제로 납니다. 세션 B가 기록하면 세션 A의 표식이 사라져서, A가 끝날 때 compact이 이미 남긴 내용이 한 번 더 들어갔어요. 이제 세션별로 표식을 둡니다(최근 10개까지). 실제 21MB 트랜스크립트로 네 가지 종료 이유를 다 돌려 확인했습니다. -->
<!-- show:en **The duplicate-suppression marker was a single slot, so another session overwrote it.** Two Claude Code windows on one project is enough to trigger it: once session B records, session A's marker is gone, and A's ending re-adds what the compact had already written. Markers are now kept per session (the last ten). Verified against a real 21MB transcript across all four end reasons. -->

### Fixed
- **중복 방지 표식을 다른 세션이 덮어쓰던 것** (2026-08-02) — `handover-written.json`이 `{session, sig}` 한 벌이었다. 같은 프로젝트에서 세션이 겹치면(창 두 개) 뒤에 쓴 세션이 앞 세션의 표식을 지워, 앞 세션 종료 때 compact 항목이 한 번 더 들어갔다. `{세션: 서명}` 맵으로 바꾸고 최근 10개까지 보관한다. **실제 21MB 트랜스크립트로 재현하고 고친 뒤 다시 확인했다** — 네 종료 이유(clear·prompt_input_exit·resume·logout) 각각 0.05~0.12초.

## [0.32.0] - 2026-08-02
<!-- show:ko **어제 만든 `/clear` 기록 기능에 결함 두 개가 있었어요. 제 테스트가 거짓으로 통과시켰습니다.** ①"빈 세션엔 안 쓴다"가 git 저장소에서는 안 먹혔습니다. Git 상태를 "활동 있음"으로 세고 있었는데 git 프로젝트에서는 그 값이 늘 있어서, 열자마자 `/clear`를 쳐도 `- Git: master, 변경 없음` 한 줄짜리 항목이 쌓였어요. 테스트를 git 아닌 임시 폴더에서 돌려서 못 봤습니다. ②중복 방지가 "수정 파일 개수"만 비교해서, compact 뒤에 같은 파일을 또 고치거나 파일 없이 중요한 결정만 논의하면 그게 통째로 사라졌습니다. 이제 내용 서명으로 비교해요. 그리고 나가는 길의 Git 조회를 0.3초로 묶었고, `/resume`·로그아웃도 기록 대상에 넣었습니다. -->
<!-- show:en **Two defects in yesterday's `/clear` recording, both of which my tests passed falsely.** (1) "Empty sessions write nothing" did not hold in a git repository: Git status counted as activity, and in a git project that value is always present, so hitting `/clear` right after opening still left a one-line entry. The test ran in a non-git temp folder, which hid it. (2) Duplicate suppression compared only the *number* of edited files, so work after a compact vanished whenever the count did not grow — re-editing the same file, or discussing a decision without touching one. It now compares a content signature. Git lookups on the way out are capped at 0.3s, and `/resume` and logout are covered too. -->

### Fixed
- **git 저장소에서 빈 세션이 기록되던 것** (2026-08-02) — `handover_body`가 `git_status`를 활동 판정에 넣었다. **git 프로젝트에서는 항상 문자열이 나오므로 모든 빈 세션이 "활동 있음"이 된다.** 활동은 대화에서 나온 것(요청·수정·검증)만으로 판단하고 Git은 부가정보로만 싣는다. **제 테스트는 비-git 임시 폴더에서 돌아 거짓 통과했다** — 사용자 프로젝트는 거의 항상 git 저장소다. 테스트 픽스처를 `git init`으로 바꾸고, git 저장소인지 확인하는 단언을 넣었다.
- **중복 방지가 compact 이후의 새 작업을 버리던 것** (2026-08-02) — 판정 기준이 `session_id + 수정 파일 **개수**`였다. 개수가 안 느는 경우가 흔하다: 같은 파일 재수정 · 파일 없이 결정만 논의 · 테스트만 실행. (**이때 "Bash 수정"도 고쳤다고 적었으나 사실이 아니었다** — 서명에 Bash가 없었다. v0.32.2에서 실제로 고쳤다.) 그 세션의 새 요청이 통째로 사라졌다. **중복을 막다 진짜 작업을 버리는 쪽이 훨씬 나쁘다.** 이제 본문 내용의 SHA1 서명으로 비교한다 — 요청 한 줄만 늘어도 서명이 달라진다. 실제로 사라졌던 세 경우를 각각 테스트로 고정했다.
- **`SessionEnd`에서 Git 조회가 예산을 넘길 수 있던 것** (2026-08-02) — `_run_git` 기본 타임아웃이 3초인데 `SessionEnd`는 **훅 전체가 1.5초 예산을 나눠 쓴다.** 느린 저장소·네트워크 파일시스템에서 handover를 쓰기도 전에 죽을 수 있었다. `git_status(cwd, timeout)`로 호출부가 줄일 수 있게 하고 `session_end.py`는 0.3초를 쓴다. Git은 부가정보라 못 얻어도 기록은 남는다.
- **랜딩·README에 남은 옛 설명 다섯 곳** (2026-08-02) — `handover.md` 문서 카드(한·영)·명령어 표(한·영)·README auto memory 비교(한·영)가 아직 compact만 말했다. 그리고 랜딩 AI 영역의 `훅이 리뷰를 돌린 뒤`(영문 `after the hook ran the review`)는 **이번에 막으려던 바로 그 주장**이었다.

### Changed
- **`SessionEnd` 매처에 `resume`·`logout` 추가** (2026-08-02) — `clear|prompt_input_exit`만 받고 있었다. 랜딩이 "세션이 바뀌며 맥락을 잃는 문제"를 다룬다고 말하는 이상 `/resume`으로 넘어가는 경로도 덮는 게 맞다. `other`는 어떤 경우인지 문서에 없어 제목을 정할 수 없으므로 계속 제외.
- **과장 검사를 문구 차단에서 주장 모델로** (2026-08-02) — 이 항목만 세 번 뚫렸다: `runs it`(대명사) → `└─ Stop ── run the review`(훅 이름이 주어) → `훅이 리뷰를 돌린 뒤`(`직접`이 없음). **문구를 하나씩 막는 구조라 표현이 조금만 바뀌면 계속 빠져나간다.** 이제 **주어(훅·hook·Stop) + 수행 동사**(돌리다·실행·수행·runs·ran·performs)로 잡고, 정확한 표현(지시·시키다·hold·demand)과 **수행자를 밝힌 문장**(`…수행하는 건 Claude다`, `수행은 AI`)은 부정 조건으로 뺀다. 한국어는 목적어→동사, 영어는 동사→목적어라 어순별로 나눠 썼다(`\b`가 한글 앞에서 경계로 안 잡히는 것도 여기서 드러났다). 잡아야 할 9문장·놓치면 안 될 7문장으로 양쪽을 고정했다.

## [0.31.3] - 2026-08-02
<!-- show:ko **"이제 옛 문장 없나?"를 주장별로 전수 확인해 여섯 군데를 더 고쳤어요.** 영문 README와 랜딩 신뢰 바에 "훅 4종"이 남아 있었고(제 검색이 `4 hooks`만 찾아서 `4 real Claude Code hooks`를 놓쳤습니다), 영문 훅 다이어그램에는 새 훅이 아예 빠져 있었어요. 기계가 하는 일 목록의 "진행상황 저장" 시점도 compact만 적혀 있어 `/clear`와 창 닫기가 빠져 있었고요. 그리고 한·영 다이어그램의 Stop 줄이 "훅이 리뷰를 직접 한다"로 읽혀서, 이 형태도 금지 목록에 넣었습니다. -->
<!-- show:en **A claim-by-claim sweep for stale sentences turned up six more.** The English README and the landing trust bar still said four hooks (a search for "4 hooks" missed "4 real Claude Code hooks"), and the English hook diagram was missing the new hook entirely. The machine-guarantees list still named only compact as the moment progress is saved. The Stop line in both diagrams read as though the hook performs the review, so that shape is now in the regression list too. -->

### Fixed
- **영문 표면에 남아 있던 "훅 4종"** (2026-08-02) — `README.md`의 `4 real Claude Code hooks`와 랜딩 영문 신뢰 바 `<b>4</b> real lifecycle hooks`. **`4 hooks`로 검색해서 놓쳤다** — CLAUDE.md에 적힌 "문구가 아니라 주장으로 찾아라"를 그대로 어겼다.
- **영문 훅 다이어그램에 `SessionEnd` 누락** (2026-08-02) — 한국어에만 넣었다. `PreCompact` 설명도 언제인지(compact 직전)를 빠뜨리고 있었다.
- **"기계가 하는 일"의 저장 시점** (2026-08-02) — `자동 정리·/compact 직전`만 적혀 있었다. `/clear`·창 닫을 때를 더했다(한·영).
- **영문 README가 스킬이 모르는 문구를 안내** (2026-08-02) — `just a light pass`라고 적혀 있었는데 `write-gate`가 아는 영어 표현은 `keep it light`·`light review`다. 랜딩에서 같은 문제를 고치면서 README를 안 봤다.
- **`stop_nudge.py` 첫 줄의 애매한 표현** (2026-08-02) — `그 자리에서 리뷰하게 한다`는 뜻은 맞지만, **여기서 문구가 문서로 여러 번 새어 나갔다**. `턴을 막고 리뷰를 지시한다`로 고치고 구분을 한 줄 덧붙였다.
- **`CLAUDE.md`의 자기모순** (2026-08-02) — 같은 줄에서 `열 곳까지 산다`고 해놓고 `이 여덟 곳을 다 봐야 한다`로 끝났다. 앞 숫자만 고치고 뒤를 놓쳤다.

### Added
- **다이어그램 형태의 "훅이 리뷰를 직접 한다"를 금지 목록에** (2026-08-02) — `└─ Stop ── run the review on unreviewed changes`는 앞 25자 안에 `훅`·`hook`이라는 낱말이 없어 기존 정규식을 빠져나갔다. **훅 이름이 주어인 형태**를 추가했다. 지운 두 문장으로 실제 탐지를, 고친 두 문장으로 무오탐을 확인했다.

### 전수 확인 결과 (2026-08-02 기준)
- 훅 5(hooks.json=스크립트=doctor 실행 목록) · 명령 10 · 스킬 6 · 에이전트 2 · 테스트 185 — 문서 주장과 전부 일치.
- 랜딩 한·영 구성요소 대칭: 기능 카드 9 · 정직함 노트 6 · 펼침 노트 4 · 빠른시작 7 · 3단 3 · 대응표 4행.
- `doctor` 실행: 실패 0 · 통과 9.

## [0.31.2] - 2026-08-02
<!-- show:ko **랜딩에서 고친 사실 오류가 README에 그대로 남아 있었어요.** v0.29.7에서 "hi-vibe는 기본 /code-review를 대신 불러준다"가 사실이 아니라고 고쳤는데, 같은 말이 README 한·영 FAQ에 남아 있었습니다. 하루 만에 같은 문장에 두 번 걸린 셈이라, 이번엔 사람 눈에 다시 맡기지 않고 재발 방지 목록에 등록했습니다. 이제 이 문장이 어느 문서에든 다시 들어오면 테스트가 실패합니다. README FAQ도 랜딩과 같은 내용으로 맞췄어요 — 리뷰가 두 겹이라는 것과, 딴 클로드를 새로 부르는 이유까지. -->
<!-- show:en **A factual error fixed on the landing page was still sitting in the README.** v0.29.7 corrected the claim that hi-vibe "wires the built-in features for you"; the same sentence survived in both README FAQs. Getting caught twice in one day by the same sentence is a sign not to rely on reading carefully, so it is now in the regression list — the test fails if it reappears in any document. The README FAQ now matches the landing, including the two layers of the review and why a fresh subagent is brought in. -->

### Fixed
- **README FAQ에 남아 있던 사실 오류** (2026-08-02) — v0.29.7이 랜딩에서만 고쳤다. README 한·영에 `이미 있는 좋은 기능을 놓치기 쉬운 순간에 자동으로 연결한다`·`리뷰 품질은 앞으로도 기본 /code-review가 더 좋아질 것`이 그대로 있었다. **저장소 어디에도 `/code-review`를 호출하는 코드가 없다.** 겹치는 표의 해당 행도 `리뷰 내용은 겹친다` → `목적이 겹치고 구현은 다르다`로 고쳤다.
- **README FAQ를 랜딩과 같은 내용으로** (2026-08-02) — `차이 둘 — 누가 보느냐`(체크리스트=빠뜨림 / `fresh-eyes`=판단)와 새로 부르는 이유(`같은 대화를 이어온 Claude는 자기가 쓴 코드를 제대로 의심하지 않는다`)가 README에는 없었다.

### Added
- **이 문장을 `test_no_overclaim` 금지 목록에 등록** (2026-08-02) — 하루에 같은 주장으로 두 번 걸렸다(랜딩 → README). **이 목록이 있는 이유가 정확히 이런 경우다** — 상상으로 만든 금지어가 아니라 실제로 있었고 사실이 아니어서 고친 문장만 넣는다. 지운 문장 4개로 실제로 잡히는지 확인했고, 지금 쓰는 표현이 오탐으로 걸리지 않는 것도 같이 고정했다.

## [0.31.1] - 2026-08-02
<!-- show:ko **handover의 "최근 검증" 줄에 돌린 적 없는 명령이 적히던 것을 고쳤어요.** 명령을 이어 붙여 치면(예: 문서 고치는 파이썬 다음 줄에 테스트) 판정은 뒤쪽 테스트 명령을 보고 하면서 기록은 맨 앞 80자를 적었습니다. 그래서 "이 명령으로 검증했다"고 남는데 실제로는 그 명령을 돌린 적이 없었어요. 결과("통과")는 맞아서 딱 봐서는 안 이상한 게 더 나쁩니다 — 다음 세션이 그걸 믿으니까요. 이제 실제로 돌린 구간만 잘라서 적습니다. -->
<!-- show:en **Fixed the "last verified" line in handover naming a command that was never run.** When commands are chained (say, a Python heredoc that edits docs, then a test run on the next line), the match was found in the later test command while the recorded text was the first 80 characters of the whole thing. The record claimed a verification command that had not been executed — and since the result ("passed") was correct, nothing looked wrong. The segment that actually ran is now the one recorded. -->

### Fixed
- **`last_test_result`가 엉뚱한 명령을 기록하던 것** (2026-08-02) — `pending_cmd = " ".join(cmd.split())[:80]`이 **명령 전체의 앞 80자**를 적었다. 테스트를 뒤에 붙이는 일이 흔한데(`python3 - <<'PY' … PY` 다음 줄에 unittest, `cd x && pytest`, `ruff check . ; pytest`), 그러면 **판정은 뒤를 보고 기록은 앞을 적는다.** handover는 다음 세션이 읽는 기록이라 "이 명령으로 검증했다"를 그대로 믿는다. `test_command_segment()`로 매치가 속한 구간만(`\n`·`;`·`&&`·`||`·`|` 기준) 잘라 적는다. 파이프 뒤(`| grep …`)가 잘리는 건 덤이다.
  - 단독 명령(`pytest`, `npm test`)이 깎이지 않는지도 같이 고정했다 — **오탐을 줄이다 멀쩡한 걸 망가뜨리면 개선이 아니다.**

## [0.31.0] - 2026-08-02
<!-- show:ko **`/clear`를 쳐도 이제 무엇을 하던 중이었는지 남습니다.** 지금까지 자동 기록은 compact 직전 하나뿐이었어요. 그런데 `/clear`는 대화를 요약해 이어가는 게 아니라 **통째로 버리는** 것이라, 정작 기록이 제일 필요한 쪽인데 아무것도 안 남았습니다. Anthropic 공식 권장이 "관련 없는 작업 사이에는 `/clear`"라서, 권장대로 쓰는 사람일수록 더 많이 잃는 구조였고요. 창을 닫고 나갈 때도 같이 남습니다. 대신 조심한 게 둘 있어요 — 열자마자 `/clear`를 쳐도 **빈 항목은 안 쌓이고**, `/compact` 하고 바로 `/clear`를 쳐도 **같은 내용을 두 번 안 씁니다.** -->
<!-- show:en **`/clear` no longer throws away what you were in the middle of.** Until now the only automatic writer was the one that runs just before a compact. But `/clear` discards the conversation instead of summarising it, so it is exactly where a record matters most — and nothing was written. Anthropic's own guidance is to run `/clear` between unrelated tasks, so following best practice cost you the most. Closing the window is covered too. Two things were guarded: an empty session writes nothing, and a `/compact` followed by `/clear` does not record the same work twice. -->

### Added
- **`SessionEnd` 훅 — `/clear`·세션 종료 때 handover 자동 기록** (2026-08-02) — 자동 기록이 `PreCompact` 하나뿐이라 **`/clear`로 버리면 아무것도 안 남았다.** `/compact`는 요약해 이어가지만 `/clear`는 통째로 버리므로 오히려 기록이 더 필요한 쪽이다. 매처는 `clear|prompt_input_exit`. 나머지 이유(`logout`·`other`)는 안 받는다 — 실제로 아쉬운 경우가 나오면 그때.
  - **빈 세션엔 안 쓴다.** compact은 대화가 길어야 일어나지만 `/clear`는 열자마자 칠 수 있다. `PreCompact`를 그대로 붙였으면 `(추출된 내용 없음)` 항목만 쌓였을 것이다.
  - **같은 세션에서 이미 남겼으면 건너뛴다.** `.hi-vibe/state/handover-written.json`에 세션과 진행량을 적어, `/compact` → `/clear` 흐름에서 같은 내용이 두 번 들어가지 않게 한다. 다만 **그 뒤에 한 일은 반드시 남긴다** — 중복을 막다 진짜 작업을 버리면 그게 더 나쁘다(테스트로 고정).
- **`doctor`가 `SessionEnd`도 실제로 돌려본다** (2026-08-02) — 파일 존재만 보면 "있는데 안 도는" 상태를 놓친다.

### Changed
- **항목 형식을 `_common.handover_body` 한 벌로** (2026-08-02) — `PreCompact`와 `SessionEnd`가 같은 모양이어야 한다. 두 벌로 두면 한쪽만 고쳐져 handover가 뒤죽박죽이 된다(이 저장소가 문서에서 여러 번 겪은 일). 테스트가 두 훅이 같은 함수를 쓰는지 확인한다.
- **"훅 4종" → "5종"을 열 곳에서** (2026-08-02) — README 한/영 · 랜딩 한·영 · `commands/doctor.md` 2곳 · `scripts/doctor.py` 3곳. CLAUDE.md의 "한 동작이 8곳에 산다"를 **열 곳으로** 고쳤다 — `doctor.py`는 문구와 실행 목록 양쪽에 있어서 빠뜨리기 쉽다.
- **오늘 아침 적은 handover 한계를 갱신** (2026-08-02) — v0.30.0에서 "압축 없이 창을 닫으면 기록이 없다"고 한계로 적었는데, 그 한계가 없어졌다. 남은 것은 크래시·`kill`·로그아웃뿐이다.

### 확인한 계약
- `SessionEnd`는 `transcript_path`·`cwd`를 받고, **무엇도 막지 못한다**(exit 2도 stderr만). 나가는 길을 붙잡을 수 없다는 뜻이라 fail-open과 어긋나지 않는다.
- **훅 전체가 1.5초 예산을 나눠 쓴다.** 21MB·4916줄 트랜스크립트로 실측 **0.03초**. `timeout: 5`로 여유만 뒀다. CLAUDE.md에 제약으로 기록.

## [0.30.0] - 2026-08-02
<!-- show:ko **바깥에서 온 리뷰가 짚은 구멍 세 개를 메웠어요. 전부 "안 적어놨다"는 문제였습니다.** ①자동 리뷰는 대화를 한 번 더 돌리고 딴 클로드까지 부르니 답이 늦어지고 토큰을 더 쓰는데, 그 값을 어디에도 안 적었습니다. 이제 첫 화면 아래 정직함 칸에 적혀 있고, 급할 땐 "가볍게 봐줘"로 체크리스트만 돌릴 수 있다는 것도 같이 안내해요. ②handover는 압축 직전에만 자동으로 남습니다. 압축 없이 창을 닫으면 그 세션은 기록이 없어요. ③비밀키 검사는 대표 패턴 정규식이라 gitleaks 같은 전문 도구를 대신하지 않습니다. 안 걸렸다고 깨끗한 게 아니에요. -->
<!-- show:en **Three gaps an outside review found are now filled. All three were things that were simply never written down.** (1) An automatic review runs an extra turn and calls in a second Claude, which costs latency and tokens — that price appeared nowhere. It is now stated plainly, along with the fact that saying "keep it light" runs only the checklist. (2) handover is written automatically only just before a compact, so a session that closes without one leaves no record. (3) The secret check is a regex over common key shapes and does not replace a dedicated scanner like gitleaks — a clean result is not proof of a clean repo. -->

### Added
- **비용 고지** (2026-08-02) — 랜딩 정직함 칸에 `공짜는 아니에요` 노트 추가. 자동 리뷰는 **턴을 한 번 더 돌리고 `fresh-eyes`까지 소환**하므로 응답 지연과 토큰 사용이 늘어난다. 정직함 노트가 셋이나 있으면서 **사용자가 실제로 치르는 값은 어디에도 없었다.** escape hatch(`가볍게 봐줘` → 체크리스트만)를 같이 안내해 경고가 아니라 선택지가 되게 했다.
- **`write-gate`가 영어 escape hatch를 받는다** (2026-08-02) — `keep it light` / `light review`. 영문 랜딩에 안내를 넣으려면 스킬이 그 말을 알아야 한다. **안내만 넣고 스킬을 안 고치면 영문 사이트가 거짓말이 된다.**

### Fixed
- **handover의 한계가 문서에 없던 것** (2026-08-02) — 자동 기록은 `pre_compact.py` 하나뿐이다(`Stop` 훅은 리뷰만 한다). **압축이 일어나지 않은 채 창을 닫으면 그 세션은 기록이 없다** — 짧게 쓰고 끝낸 세션이 정확히 이 경우인데 어디에도 안 적혀 있었다. README 한·영에 한계 문단, 랜딩 3단 설명에 한 마디.
- **"이 스캔이 유일한 그물"의 범위** (2026-08-02) — hi-vibe **안에서** 유일하다는 뜻인데 앞뒤 없이 읽으면 "이거면 충분"으로 읽힌다. **`gitleaks`·`trufflehog` 같은 전문 스캐너를 대신하지 않으며, 안 걸렸다고 깨끗한 게 아니라는 것**을 README 한·영에 명시했다.

## [0.29.9] - 2026-08-02
<!-- show:ko **"설치는 전역 한 번, init은 프로젝트마다" 안내의 줄바꿈을 고쳤어요.** 한 문장 한가운데에 강제 줄바꿈이 들어가 있어서, 뒷부분이 새 항목처럼 다음 줄에서 시작했습니다. 일곱 조각으로 흩어져 보이던 것이 네 문장으로 정리됐어요. 글은 그대로고 줄이 끊기는 자리만 바뀝니다. -->
<!-- show:en **Fixed the line breaks in the "install once, init per project" note.** A hard break sat in the middle of a sentence, so the second half started on its own line and read like a separate item. What looked like seven fragments is now four sentences. The wording is unchanged; only where the lines break.  -->

### Fixed
- **전역/프로젝트 안내의 줄바꿈** (2026-08-02) — `…init을 해야 켜져요<br>— .hi-vibe/ 마커가 만들어진 폴더에서만 돌아요.` 처럼 **한 문장 중간에 `<br>`**이 있었다. 뒤 절이 새 항목처럼 보여 일곱 조각으로 읽혔다. `<br>`을 빼고 마침표로 끊어 네 문장으로 만들었다. 한·영 모두.

## [0.29.8] - 2026-08-02
<!-- show:ko **"겹치지 않나요?" 답에서 핵심이 맨 아래 흐린 글씨에 있었어요.** 기본 `/code-review`가 아니라 hi-vibe가 직접 만든 서브에이전트가 본다는 것 — 그게 이 질문의 진짜 답인데 곁들이는 말 자리에 있었습니다. 차이를 둘로 나눠 나란히 세웠어요. 하나는 "언제 도느냐", 둘은 "누가 보느냐". 그리고 리뷰가 두 겹이라는 것도 처음 적었습니다. 체크리스트가 빠뜨린 것을 훑고(에러를 조용히 넘겼는지, 실제로 돌려는 봤는지), 그다음 코드를 짠 기억이 없는 딴 클로드가 잘 만들었는지를 봐요. 이 둘은 담당이 다릅니다. -->
<!-- show:en **The real answer to "doesn't this overlap?" was sitting in the faint text at the bottom.** That the review is done by an agent hi-vibe wrote, not the built-in `/code-review`, is the actual answer to that question — it was placed as an aside. The answer now names two differences side by side: when it runs, and who does the looking. It also says for the first time that the review has two layers with different jobs: a checklist for what got skipped, then a second Claude that never wrote the code judging how well it was built. -->

### Changed
- **FAQ 구조: 차이를 둘로 분리** (2026-08-02) — `가장 큰 차이는 "언제 도느냐"` 하나만 굵게 세우고 **누가 보느냐를 맨 아래 `dim`에** 뒀다. "기본 기능이 아니라 hi-vibe가 만든 에이전트가 본다"가 이 질문의 핵심인데 자리가 곁다리였다. `차이 하나 — 언제 도느냐` / `차이 둘 — 누가 보느냐`로 나란히 세웠다.
- **리뷰가 두 겹이라는 것을 처음 명시** (2026-08-02) — 체크리스트(빠뜨림: 에러 삼킴·실행 검증·문서 동기화, 자기 점검 루프로 그 자리에서 고침)와 `fresh-eyes`(판단: 과잉설계·더 단순한 길)는 **담당이 다르다**. `agents/fresh-eyes.md`에 `Not for ... bug hunting (tests and the checklist own those)`로 명시돼 있는데, 랜딩은 이 구분을 어디에도 안 적어 "서브에이전트가 에러를 잡는다"로 읽힐 여지가 있었다.
- **왜 새로 부르는지를 한 줄 추가** (2026-08-02) — `같은 대화를 이어온 Claude는 자기가 쓴 코드를 제대로 의심하지 않거든요.` 이 이유가 없으면 fresh-eyes가 자랑거리가 아니라 군더더기로 읽힌다. (`잘 못 의심한다`는 능력 부족으로 읽혀 `제대로 의심하지 않는다`로.)

## [0.29.7] - 2026-08-02
<!-- show:ko **"겹치지 않나요?" 답에 사실이 아닌 문장이 있었어요.** "이미 있는 좋은 기능을 놓치기 쉬운 순간에 연결한다"고 적혀 있었는데, 확인해 보니 hi-vibe의 리뷰는 Claude Code 기본 `/code-review`를 부르지 않습니다. 자기 체크리스트를 돌리고, 코드를 짠 기억이 없는 딴 클로드(fresh-eyes)를 새로 불러 설계를 다시 보게 해요. 겹치는 건 "리뷰를 한다"는 목적이지 구현이 아니었습니다. 그 자리에 실제로 하는 일을 적었어요. 나머지 문장들도 "기계가 보장하는 시점" 같은 말을 쉬운 말로 풀고, 방문자에게 필요 없는 로드맵 얘기는 뺐습니다. -->
<!-- show:en **The "doesn't this overlap?" answer contained a claim that wasn't true.** It said hi-vibe "wires the good features you already have into the moments they're easiest to skip" — but hi-vibe's review never calls the built-in `/code-review`. It runs its own checklist and brings in a second Claude (fresh-eyes) that never wrote the code. What overlaps is the purpose, not the implementation. The answer now says what actually happens, in plainer words, and drops a roadmap aside that visitors did not need. -->

### Fixed
- **FAQ의 사실 오류: "기본 기능을 대신 불러준다"** (2026-08-02) — 저장소 전체에 `/code-review`를 호출하는 코드가 없다. `write-gate` SKILL.md:246은 체크리스트 후 **`fresh-eyes` 에이전트를 Agent 도구로 소환**한다. 겹치는 것은 목적이지 구현이 아니다. **에이전트를 띄우는 수단은 Claude Code 것이지만 무엇을 보라고 시키는 내용은 hi-vibe가 쓴 것** — 이 구분을 답에 적었다. fresh-eyes는 랜딩 세 곳(669·677·678줄)과 README에 이미 설명돼 있는데 정작 이 FAQ에는 없었다.

### Changed
- **FAQ 문장을 쉬운 말로** (2026-08-02) — `꽤 겹쳐요.` 한 줄만 뜬 채 끝나 답이 완결되지 않았다 → `꽤 겹치지만, 다른 점도 많습니다.` / `기계가 보장하는 건 리뷰를 요구하는 시점` → `막는 데까지가 hi-vibe가 하는 일` / `같은 변경으로 두 번 막진 않아요` → `이미 리뷰한 코드는 다시 보고 검사하지 않습니다` / 목록의 `저장소 전체 중복·미참조 스캔`·`증상과 원인 중심 CHANGELOG`도 풀어 썼다. **`opt-in`과 명령어 이름·`훅`은 그대로 둔다** — 쓰다 보면 실제로 만나는 말이라 바꾸면 오히려 못 찾는다.
- **로드맵 문장 삭제** (2026-08-02) — "리뷰 품질은 앞으로도 기본 `/code-review`가 더 좋아질 것"은 만드는 사람끼리 할 얘기다. 방문자는 "겹치나?"가 궁금해서 연 것이고, 바로 앞 문장이 이미 같은 포지셔닝을 말한다.

## [0.29.6] - 2026-08-02
<!-- show:ko **첫 화면의 "평소처럼 말만 하면 돼요"를 "평소처럼 개발하면 돼요"로 바꿨어요.** 달라지는 건 명령어를 외울 필요가 없다는 것뿐이고 개발은 그대로 하는 건데, "말만 하면"은 개발자가 하는 일을 말하는 것으로 줄여 버립니다. README는 처음부터 "평소처럼 Claude와 코딩하면 됩니다"였으니, 첫 화면만 혼자 어긋나 있던 셈이에요. -->
<!-- show:en **The hero line "just talk normally" became "just build the way you already do".** The only thing that changes is not having to memorize commands; the development itself is unchanged, and "just talk" shrinks the developer's work down to talking. The README had said it correctly all along, so the hero was the one surface out of step. -->

### Changed
- **히어로 문장: "평소처럼 말만 하면" → "평소처럼 개발하면"** (2026-08-02) — hi-vibe가 바꾸는 건 **명령어를 외울 필요가 없다**는 것뿐이다. "말만 하면"은 그걸 넘어 개발 행위 자체를 말하기로 축소한다. README 한국어는 이미 "평소처럼 Claude와 코딩하면 됩니다"(83줄)라 랜딩 히어로만 어긋나 있었다. 영문도 `just talk normally` → `just build the way you already do`. **3단 설명과 빠른 시작의 "평소처럼 말하면"은 그대로 둔다** — 거기서는 실제로 *말이 스킬을 걸리게 한다*는 다른 주장이라 정확한 표현이다.

## [0.29.5] - 2026-08-02
<!-- show:ko **"훅 4종이 돌아요"라고 해놓고 둘만 설명하고 있었어요.** 코드 쓸 때 검사하는 것과 리뷰를 붙잡는 것만 적혀 있고, 대화가 compact되기 직전에 handover를 남기는 것과 새 세션에서 그걸 다시 읽는 것은 이름조차 안 나왔습니다. 둘 다 넣었어요. 그리고 리뷰는 훅으로만 걸리는 것처럼 써놨는데, 실제로는 "다 했어" 한마디에도 걸립니다 — 훅은 말 안 했을 때의 마지막 그물이지 유일한 통로가 아니에요. 마지막으로 "AI가 깜빡하면 명령어를 직접 누르세요"를 "평소에 치는 건 check 하나면 돼요"로 바꿨습니다. 뭘 쳐야 하는지가 이제 하나로 좁혀져요. -->
<!-- show:en **The note said "4 hooks run automatically" and then described two of them.** Writing the handover just before a compact, and reading it back into a new session, were not mentioned at all. Both are in now. Review was also presented as hook-only when a plain "done" triggers it just as well — the hook is the net for when you say nothing, not the only route. And "press a command yourself when the AI forgets" became "day to day, check is the one you type", which narrows the answer to a single command. -->

### Fixed
- **훅 4종 중 둘이 설명에서 빠져 있던 것** (2026-08-02) — PreCompact(handover 기록)와 SessionStart(새 세션에 다시 읽힘)가 3단 설명에 없었다. "4종이 돌아요"라고 써놓고 PostToolUse·Stop만 설명하니, 숫자와 내용이 어긋난다. 둘 다 1단에 넣었다.
- **리뷰가 훅 전용인 것처럼 읽히던 것** (2026-08-02) — `write-gate` 스킬 설명에 트리거로 `다 했어, 리뷰해줘, 검토, review my change`가 명시돼 있다. 말해도 걸리고, **말 안 해도** 훅이 붙잡는다. 2단 목록에 `review`를 넣고 그 관계를 한 줄로 적었다.

### Changed
- **"AI가 깜빡하면 직접 누르세요" → "평소에 치는 건 check 하나"** (2026-08-02) — `/hi-vibe:find`를 예로 들면 바로 아래 "칠 일이 없어요"와 부딪혀 보이고, 뭘 쳐야 하는지도 안 좁혀진다. 3단의 "평소에 내가 치는 것"과 답을 하나로 맞췄다.
- **랜딩에서 Bash 사각지대 주석 제거** (2026-08-02) — 바로 앞 문장이 이미 "**Write/Edit로** 코드를 쓸 때마다"로 범위를 좁히므로 빼도 과장이 되지 않는다. 마지막 줄이 `check`(저장소 전체 스캔)를 가리키면서 같은 정보를 쉬운 말로 전달한다. **상세 설명은 README 한·영에 그대로 있다** — 랜딩에서 지운 것이지 감춘 것이 아니다.

## [0.29.4] - 2026-08-02
<!-- show:ko **"켜지는 방식이 3단이에요" 설명이 글자 벽처럼 읽히던 것을 고쳤어요.** 세 항목이 줄바꿈으로만 나뉘어 있어서, 앞 항목이 길어 넘어간 줄이 다음 항목의 아이콘 자리와 똑같은 왼쪽 끝에서 시작했습니다. 그래서 어디가 새 항목이고 어디가 이어지는 줄인지 눈으로 구분이 안 됐어요. 넘어간 줄을 아이콘 너비만큼 안쪽으로 밀어 넣어, 맨 왼쪽에서 시작하는 건 항상 새 항목이 되게 했습니다. 그리고 "내가 치는 것"을 "평소에 내가 치는 것"으로 고쳤어요 — 아래 명령어 표에는 직접 치는 게 다섯 개인데 여기는 둘이라 어긋나 보였거든요. "침습적"이라는 말도 뜻이 드러나게 풀었습니다. -->
<!-- show:en **The "three tiers" note no longer reads as a wall of text.** The three items were separated by line breaks alone, so a wrapped line began at exactly the same left edge as the next item's icon — there was no way to see where one item ended and the next began. Wrapped lines are now indented past the icon, so anything starting at the far left is a new item. "What you type" became "What you type day to day", since the command table below lists five commands you type and this note named two. "Invasive" was replaced with what it actually means. -->

### Fixed
- **3단 설명이 글자 벽으로 읽히던 것** (2026-08-02) — 증상: 여섯 줄이 한 덩어리로 보이고 항목 경계가 안 보인다. 원인: 항목 구분이 `<br>` 하나뿐이라 **넘어간 줄이 다음 항목의 아이콘 자리와 같은 왼쪽 끝에서 시작**했다. `.tiers`/`.tier` 그리드로 행잉 인덴트를 줘서 맨 왼쪽 시작 = 새 항목이 되게 했다. 글은 그대로. 한·영 모두.

### Changed
- **"내가 치는 것" → "평소에 내가 치는 것"** (2026-08-02) — 직접 치는 명령은 SSOT(`COMMAND_MODE`) 기준 다섯 개(welcome·init·doctor·check·gate)인데 이 문장은 둘(check·gate)만 든다. 틀린 말은 아니지만(설치 후 평소에 치는 건 check 하나) 바로 아래 명령어 표와 나란히 보면 어긋나 보인다. 다섯 개를 나열하면 "칠 게 많네"로 읽혀 손해라, **범위를 좁히는 한 단어**를 붙였다.
- **"침습적"을 쉬운 말로** (2026-08-02) — 입문자 대상 문장의 용어. `gate`가 왜 한 번만인지가 드러나게 "프로젝트 설정 파일에 손을 대니"로 풀었다.

## [0.29.3] - 2026-08-02
<!-- show:ko **방금 만든 대응표에 엉뚱한 스타일이 얹혀 있던 것을 고쳤어요.** 행마다 빨간 세로 막대와 흰 카드 테두리가 생겨 표가 아니라 부서진 목록처럼 보였습니다. 원인은 이름이었어요 — 행에 붙인 `prow`라는 이름을 페이지 아래쪽 "AI에게 코딩을 맡기면" 섹션이 이미 쓰고 있었고, 그쪽 스타일이 그대로 딸려 왔습니다. 이름을 바꾸고, 새 이름은 전부 표 안쪽으로 묶었어요. 한 페이지에 섹션이 열여덟 개라 또 겪을 일이라, 그 이유를 코드에 적어 뒀습니다. -->
<!-- show:en **The new comparison table was picking up styling that didn't belong to it.** Every row had a red left bar and a white card border, so it read as a broken list rather than a table. The cause was a name: the row class `prow` was already in use by a section further down the page, and that section's styling came along with it. The class is renamed, and every new name is now scoped inside the table. With eighteen sections on one page this will come up again, so the reason is written into the code. -->

### Fixed
- **대응표가 아래 섹션 스타일을 뒤집어쓰던 것** (2026-08-02) — 증상: 행마다 빨간 왼쪽 막대·흰 카드 테두리·둥근 모서리. 원인: 행 클래스 `prow`가 `#problem-*` 섹션의 홑클래스 `.prow`와 이름이 같았다. 내 규칙은 `.pairs .prow`(0,2,0)라 `display`·`align-items`만 덮었고 **`background`·`border`·`border-left:3px solid var(--danger)`·`border-radius`·`padding`은 그대로 살아남았다**. `.pair`로 바꾸고 `.l`/`.mid`/`.r`도 뜻이 드러나는 `.pain`/`.arrow`/`.fix`로 바꿔 전부 `.pairs` 아래로 묶었다. **한 페이지에 섹션이 열여덟 개다 — 홑클래스 이름을 새로 만들지 말 것.** 이유를 CSS 주석에 남겼다.

## [0.29.2] - 2026-08-02
<!-- show:ko **"이런 불편을 겪고 있다면" 섹션을 대응표로 바꿨어요.** 원래 왼쪽 불편 4개와 오른쪽 해결 4개가 순서대로 짝이었는데, 회색 상자 두 개로 갈라놔서 그게 안 보였습니다. 같은 줄에 붙이니 "이 문제는 이게 푼다"가 바로 읽혀요. 덤으로 행 높이가 저절로 맞아서, 글자 수를 세어가며 맞추던 열 높이 문제가 구조적으로 사라졌습니다. 그리고 "내 프로젝트에서는 무엇을 도와줄까요?"에는 1·2·3 단계를 붙였어요 — 링크를 넣고, 질문을 복사하고, 쓰는 AI에 붙여넣는 흐름이 글로만 적혀 있어서 처음 온 사람은 한 번에 안 읽혔거든요. 두 섹션 설명문에는 형광펜을 한 구절씩 그었습니다. -->
<!-- show:en **The "if any of this sounds familiar" section is now a table of pairs.** The four problems on the left and the four answers on the right were always in matching order, but splitting them into two grey boxes hid that. On one row, "this problem is solved by this" reads immediately — and row heights now match on their own, so the column-balancing problem is gone structurally rather than by counting characters. The preview section gained numbered steps: drop in the link, copy the question, paste it into your AI. That sequence was previously prose only. Both section intros got one highlighted phrase. -->

### Changed
- **불편↔해결을 대응표로** (2026-08-02) — `.fitgrid`/`.fitcard` 2열 카드를 `.pairs` 대응표로 교체. 좌우 항목이 **원래 1:1로 짝**인데 상자 두 개로 갈라져 짝이 안 보였다. 같은 행에 붙이면 대응이 읽히고, **행 높이가 자동으로 맞아** 0.29.1에서 글자 수를 세어 맞췄던 열 높이 문제가 구조적으로 사라진다. 좁은 화면에서는 세로로 떨어지고 화살표가 90° 돌아간다. 한·영 모두.
- **미리보기 섹션에 1·2·3 단계** (2026-08-02) — "링크 넣기 → 질문 복사 → 쓰는 AI에 붙여넣기"가 글로만 적혀 있어 흐름이 한 번에 안 읽혔다. `.steps`로 순서를 드러냈다. **번호는 진짜 순서가 있을 때만 쓴다** — 여기는 링크를 넣어야 질문에 반영되므로 순서가 실제 의미를 갖는다. 폼 라벨은 단계 제목과 겹쳐 `sr-only`로 내렸다(스크린리더에는 남는다).
- **두 섹션 설명문에 형광펜 한 구절씩** (2026-08-02) — 히어로에 이미 있는 `b.hlx`를 재사용(새 CSS 없음). 카드 소제목까지 그으면 한 화면에 노란색이 네 군데가 돼 오히려 안 보이므로 설명문만.

### Fixed
- **대응표가 행 단위로 떠오르며 겹치던 것** (2026-08-02) — 스크롤 등장 애니메이션의 `GROUP_SEL`에 `.fitgrid`가 있었다. 그대로 `.pairs`로 바꾸면 테두리 안의 행이 각자 밀려 올라와 서로 겹치고 `overflow:hidden`에 잘린다. 표는 **한 덩어리**로 떠오르게 뒀다.

## [0.29.1] - 2026-08-01
<!-- show:ko **기능 카드 세 열의 높이가 안 맞던 것을 고쳤어요.** 가운데 열만 아래로 길게 내려가고 좌우는 비어 보였는데, 원인은 레이아웃이 아니라 **카드 하나가 너무 길어서**였습니다. 짧은 카드는 95자인데 긴 건 213자였어요. 한 카드에 네 가지를 설명하고 있어서, 다른 데 이미 적힌 것들을 덜어냈습니다. 이제 세 열이 288·330·330자로 비슷해요. 히어로 문장과 제목 두 개의 줄바꿈도 같이 다듬었습니다. -->
<!-- show:en **The three feature columns no longer end at wildly different heights.** The middle one ran far past the others, and the cause wasn't the layout — one card was simply too long (213 characters against 95 for the short ones). It was explaining four separate things, so the parts already covered elsewhere were cut. The columns now sit at comparable lengths. Hero and two headings had their line breaks tidied at the same time. -->

### Fixed
- **기능 카드 열 높이 불균형** (2026-08-01) — 증상: 가운데 열만 아래로 길게 내려가 좌우가 비어 보였다. 원인: CSS가 아니라 **본문 길이**였다 — `안전벨트가 풀리면 알려줘요` 213자, `딴 클로드가 설계 재검토` 190자, `구조 점검` 180자 대 나머지 91~111자. 긴 카드들이 **한 자리에서 네 가지를 설명**하고 있었다(fail-open·heartbeat·CI·doctor). 다른 데 이미 적힌 것(doctor 동작, "GitHub 알림함은 쌓이면 신호가 못 된다"는 이유, "붙잡는 건 기계" 단서)을 덜어 117·122·119자로 줄였다. 열 합계 288·330·330자. **카드는 요약이고 상세는 아래 섹션에 있다** — 카드에 다 넣으려 하면 이렇게 된다. 영문도 같이(573·710·600).
- **히어로 문장이 어중간하게 끊기던 것** (2026-08-01) — `…입문자·1인 개발자를 / 위한 안전벨트예요.`로 넘어가 마지막 조각만 남았다. `만드는 / 입문자·1인 개발자를 위한 안전벨트예요.`로 끊었다. 한·영 모두.
- **제목 두 개를 한 줄로** (2026-08-01) — `이런 불편을<br>겪고 있다면`, `내 프로젝트에서는<br>무엇을 도와줄까요?`의 강제 줄바꿈 제거.

## [0.29.0] - 2026-08-01
<!-- show:ko **남의 실제 저장소에서 처음으로 오탐 두 가지가 드러났어요.** Python 파일 301개짜리 프로젝트에 돌려본 결과인데, ①셸 스크립트에서만 불리는 진입점이 전부 "안 쓰는 코드"로 잡혔고 ②`Protocol` 인터페이스 선언이 "중복 구현"으로 잡혔습니다. 둘 다 스캐너가 헛짚은 것이고, 이유가 뻔한 종류라 고쳤어요. 후보가 시끄러우면 사용자가 전부 무시하고, 그러면 진짜도 같이 묻힙니다. 그리고 `gate`가 `basedpyright`를 몰라서 이미 타입체커가 있는 프로젝트에 mypy를 또 권하던 것도 고쳤습니다. -->
<!-- show:en **Two false positives showed up the first time someone ran this on a real outside repository.** On a project with 301 Python files: (1) entry points only ever called from shell scripts were all reported as unused code, and (2) `Protocol` interface declarations were reported as duplicate implementations. Both are the scanner guessing wrong for an obvious reason, so both are fixed — noisy candidates get ignored wholesale, and the real ones get buried with them. `gate` also learned about `basedpyright`, so it stops offering mypy to projects that already type-check. -->

### Fixed
- **셸·Makefile에서만 불리는 코드를 죽은 코드로 오판** (2026-08-01) — 증상: 배포·데모 스크립트가 문자열로 호출하는 진입점이 미참조 후보로 잡혔다. 원인: 참조를 세는 파일 목록(`TEXT_EXT`)에 `.sh`가 없었다 — 파이썬이 아니라서 심볼은 못 뽑지만 **이름이 나오면 그건 진짜 참조**다. `REFERENCE_ONLY_EXT`(`.sh`·`.bash`·`.zsh`·`.fish`·`.mk`·`.sql`·`.cfg`·`.ini`·`.txt`)와 `REFERENCE_ONLY_NAMES`(`Makefile`·`Dockerfile`·`Procfile`·`justfile`)를 추가했다. **참조로만 세고 크기·비밀키 검사 대상에는 넣지 않는다** — 긴 배포 스크립트를 "정리 후보"로 올릴 이유가 없다. `find`(이미 있나 검색)도 같이 본다: 거기서만 불리는 걸 못 찾으면 "없다"고 답하고 같은 걸 또 만들게 된다.
- **`Protocol`·ABC 선언을 중복 구현으로 오판** (2026-08-01) — 증상: 인터페이스가 많은 저장소일수록 중복 후보가 쏟아졌다. 원인: 스텁(`...`·`pass`·`raise NotImplementedError`)도 정규화 AST가 같으면 중복으로 셌다. **선언은 구현이 아니다** — 스텁 둘이 같은 건 당연하다. 이미 있던 `_looks_wip()` 판정을 중복 탐지에서도 재사용한다(규칙을 두 벌 두지 않는다). 진짜 중복은 그대로 잡히는지 회귀 테스트로 고정했다.
- **`gate`가 `basedpyright`를 모름** (2026-08-01) — 스킬은 "기존 설정을 먼저 읽는다"고 하면서 타입체커는 mypy만 봤다. `basedpyright`·`pyright` 설정(`[tool.basedpyright]`·`pyrightconfig.json` 등)이 있으면 **mypy를 목록에서 빼고 이유를 밝힌다** — 타입체커 둘을 돌리면 서로 다른 소리를 한다. 비밀키도 `gitleaks`·`detect-secrets`가 있으면 같다. **겹치는 걸 또 깔아주는 건 도움이 아니라 짐이다.**

### Added
- **실제 저장소에서 나온 오탐 회귀 테스트 5개** (2026-08-01) — 셸/Makefile 참조가 dead 판정을 구제하는지, 셸 스크립트가 크기 검사에는 안 걸리는지, Protocol 스텁이 중복에서 빠지는지, **그리고 진짜 중복은 여전히 잡히는지**. 마지막 게 중요하다 — 오탐을 줄이다 놓치는 게 늘면 그건 개선이 아니다.

## [0.28.3] - 2026-08-01
<!-- show:ko **새로 쓴 문구가 가르치는 말투였어요.** "안 맞는 분을 붙잡아 두는 것보다 여기서 걸러지는 게 서로 낫습니다" — 방문자를 걸러낼 대상으로 부르고, 뭐가 나은지까지 제가 단정하고 있었습니다. "제 말 말고, 코드를 보고 판단하세요"도 방어적이고 명령조였고요. 페이지 나머지는 "…돼요", "…잡아 줘요"처럼 부드러운데 이 둘만 튀었어요. 같은 말투로 맞췄습니다. -->
<!-- show:en **The new copy came out lecturing.** "Better you rule it out here than find out three days in" cast the reader as something to be filtered, and decided for them what's better. "Don't take my word for it. Read the code." was defensive and commanding. The rest of the page is warm and explanatory; these two lines stuck out. They now match. -->

### Changed
- **새 섹션 두 곳의 말투를 페이지에 맞춤** (2026-08-01) — `나한테 맞는 도구인지 먼저 보세요` → `이 도구가 나한테 맞을까요?`(명령 → 질문), `안 맞는 분을 붙잡아 두는 것보다 여기서 걸러지는 게 서로 낫습니다` → `도움이 되는 경우와 그렇지 않은 경우를 먼저 적어뒀어요`, `그래도 확실히 하고 싶다면 / 제 말 말고, 코드를 보고 판단하세요` → `더 확인하고 싶다면 / AI에게 대신 확인시켜 보세요`. 한·영 모두. **읽는 사람을 걸러낼 대상으로 부르거나, 무엇이 나은지 대신 정해주지 않는다.**

## [0.28.2] - 2026-08-01
<!-- show:ko **평가 질문 자리를 원래 화면으로 되돌렸어요.** 직전 릴리스에서 프롬프트만 덩그러니 놓인 형태로 다시 넣었는데, 보기에도 나빴고 **GitHub 링크 입력칸이 빠져 있었습니다**. 그 칸에 저장소 주소를 넣고 버튼을 누르면 질문 안의 `[내 프로젝트 GitHub 링크]` 자리가 자동으로 채워지는데, 그게 없으면 AI가 hi-vibe만 보고 답해요. 원래의 2단 화면(왼쪽 안내 카드 + 오른쪽 질문)으로 되돌렸고, 질문 내용은 새로 쓴 것을 그대로 씁니다. -->
<!-- show:en **Put the evaluation section back to its original layout.** The previous release re-added it as a bare prompt block — it looked worse, and it **dropped the GitHub link field**. Typing your repository there and pressing the button fills the `[my project's GitHub link]` slot inside the question; without it the AI answers about hi-vibe alone. The two-column layout (guide card on the left, question on the right) is back, with the rewritten question. -->

### Fixed
- **평가 섹션 레이아웃과 입력칸 복원** (2026-08-01) — v0.28.1에서 섹션을 되살리면서 **복사 버튼 JS만** 넣고 저장소 링크 폼(`js-fit`)과 높이 동기화(`syncAuditHeights`)는 뺐다. "링크는 프롬프트 안에서 직접 채우면 된다"는 판단이었는데, 그건 **화면에서 한 단계를 없애 놓고 사용자에게 떠넘긴 것**이다. 원래의 `.audit` 2단 레이아웃·`.fitform` 입력칸·CSS·JS를 v0.27.2 기준으로 전부 되돌리고, 질문 내용만 새로 쓴 것으로 유지했다. 섹션 id가 `audit-*` → `verify-*`로 바뀌었으므로 높이 동기화가 찾는 id와 스크롤 애니메이션 대상(`GROUP_SEL`)도 같이 맞췄다.

## [0.28.1] - 2026-08-01
<!-- show:ko **평가 질문을 다시 넣었어요 — 자리와 내용을 바꿔서.** 직전 릴리스에서 통째로 뺐는데, 설치 직전에 "말 말고 코드를 보라"고 할 수 있는 건 그대로 두는 게 낫습니다. 대신 **"이런 분께 맞아요" 뒤로** 옮겨서, 방문자가 hi-vibe가 뭔지 알고 난 다음에 만나게 했어요. 질문 내용도 새로 썼습니다 — 예전엔 hi-vibe를 10점 만점으로 채점시켰는데, 그건 이 플러그인 평판을 묻는 거지 **내 프로젝트에 맞는지**를 묻는 게 아니었어요. 이제 "내 저장소에서 무엇을 찾아줄지"를 구체적 사례로 답하게 합니다. -->
<!-- show:en **The evaluation prompt is back — in a different place, with different content.** The previous release cut it entirely, but "don't take my word for it, read the code" is worth keeping right before someone installs. It now sits **after the fit section**, so visitors meet it once they know what hi-vibe is. The question itself was rewritten: it used to ask for scores out of 10, which measures the plugin's reputation rather than **whether it suits your project**. It now asks what hi-vibe would concretely find in your repository, with examples. -->

### Added
- **`verify` 섹션 — 적합성 판단 뒤에 검증 질문** (2026-08-01) — 새 질문은 채점(`/10`)을 없애고 여섯 가지를 묻는다: 중복 방지 도움 여부 · 자동 리뷰가 여기서 실제로 잡을 것 · 세션 맥락과 트러블슈팅 기록의 활용도 · 저장소 전체 점검이 필요한 규모인지 · 지금 쓰는 도구와 겹치는 부분 · 기대할 장점과 한계. **내 프로젝트의 실제 파일에서 사례를 들라**고 요구하고, 못 본 건 추측 말고 확인 불가라고 밝히라고 한다(grounded-answers와 같은 계약). 마지막에 가장 유용할 기능·필요 없을 기능·설치 추천 여부를 정리시킨다.
- **복사 버튼 복원** (2026-08-01) — v0.28.0에서 섹션과 함께 지웠던 클립보드 JS만 다시 넣었다. 없앤 폼(`js-fit`)과 높이 동기화(`syncAuditHeights`)는 복원하지 않는다 — 링크는 프롬프트 안의 `[내 프로젝트 GitHub 링크]` 자리를 직접 채우면 되고, 그게 코드도 짧다.
- **`docs/internal/eval-prompt.md`를 새 질문으로 갱신** (2026-08-01) — 랜딩과 같은 내용임을 파일 첫머리에 명시했다. 두 벌이 갈리면 그 파일이 거짓말이 된다.

## [0.28.0] - 2026-08-01
<!-- show:ko **첫 화면 다음 자리를 "AI한테 물어보세요"에서 "나한테 맞나 보세요"로 바꿨어요.** 거기엔 다른 AI에 붙여넣을 긴 평가 질문이 있었는데, 방문자가 hi-vibe가 뭔지 알기도 전에 자리를 떠나게 만드는 자리였습니다. 이제 **잘 맞는 경우 4개와 효과가 작은 경우 4개**를 나란히 놓습니다. JS/TS가 주력이거나 이미 리뷰·CI 절차가 있는 팀이면 여기서 걸러져요 — 붙잡아 두는 것보다 그게 서로 낫습니다. 평가 질문은 버리지 않고 저장소 안에 보관했어요. -->
<!-- show:en **The slot right after the hero changed from "go ask an AI" to "see if this fits you".** It used to hold a long evaluation prompt to paste into another AI — a section that sent visitors away before they knew what hi-vibe was. It now shows **four cases where it fits and four where it doesn't**, side by side. If JS/TS is your main language, or your team already has review and CI, you'll rule it out right there — better than being talked into it. The prompt itself is kept in the repo. -->

### Changed
- **`설치 전 적합성 확인` 섹션 → `이런 분께 맞아요 / 효과가 작아요`** (2026-08-01) — 평가 프롬프트는 방문자를 **다른 AI에게 보내는** 자리였다. 첫 화면 바로 다음이라 흐름이 끊기고, 무엇보다 **hi-vibe가 뭔지 알기 전에** 판단을 남에게 미루게 했다. 대신 10초 만에 스스로 판단할 기준을 준다: 맞는 경우(Python 입문자·리뷰 부탁할 동료 없는 1인·중복과 맥락 유실이 잦은 사람·테스트·문서를 알지만 못 챙기는 사람) / 안 맞는 경우(일회용 스크립트·이미 절차가 갖춰진 팀·JS/TS 주력·Claude Code를 주 도구로 안 씀). **안 맞는 사람을 먼저 돌려보내는 게 붙잡는 것보다 정직하다.**
- **평가 프롬프트는 `docs/internal/eval-prompt.md`에 보관** (2026-08-01) — 지우지 않았다. 실제로 이 프롬프트로 받은 외부 평가가 v0.22~v0.27의 상당수를 만들었다(`.env` 구멍, 삭제 파일 리뷰 누락, 리뷰의 스코프 크립). 공개 소개에서만 뺀다.

### Removed
- **딸려 있던 죽은 코드** (2026-08-01) — 섹션이 없어지면서 쓰이지 않게 된 JS 55줄(`js-fit` 폼 처리·`js-copy` 클립보드·`flashBtn`·`syncAuditHeights` 높이 동기화)과 CSS 19줄(`.audit`·`.promptbox`·`.fitform`)을 지웠다. 화면에서 사라진 기능의 코드를 남겨두면 다음 사람이 "이건 뭘 하는 거지" 하고 시간을 쓴다. 페이지 155k → 149k자.

## [0.27.2] - 2026-08-01
<!-- show:ko **줄바꿈이 지저분하던 것을 정리했어요.** 긴 문장이 넘어가면서 마지막에 단어 하나만 다음 줄에 덩그러니 남는 자리가 있었습니다("…약속과 정반대예요." / "…알아서."). 브라우저가 알아서 피하게 하는 설정(`text-wrap: pretty`)을 긴 글이 들어가는 자리에 전부 넣고, 문장 자체도 짧게 줄였어요. 스킬 숨김 안내는 다섯 줄에서 네 줄로 줄었습니다. -->
<!-- show:en **Cleaned up ragged line breaks.** Long sentences were wrapping so that a single word ended up alone on the last line. Every long-prose container now uses `text-wrap: pretty` so the browser avoids that, and the sentences themselves were shortened. The note about hidden skills went from five lines to four. -->

### Fixed
- **긴 문단 끝에 단어 하나만 남던 줄바꿈** (2026-08-01) — 원인 둘. ①문장이 길어 마지막 단어가 홀로 넘어갔다 ②고아 줄을 막는 설정이 일부 자리(`.rel .h span`·`.audit .card p`)에만 있었다. `.lead`·`.honest-note`·`.tbody`·`.fdesc`·`.qs-sub`·`.say`까지 `text-wrap:pretty`를 통일하고(구형 브라우저는 무시하므로 안전), 스킬 숨김 안내 문장을 한/영 모두 짧게 다듬었다(5줄 → 4줄).

## [0.27.1] - 2026-08-01
<!-- show:ko **명령어 표를 실제로 치는 순서대로 다시 놨어요.** 직전 릴리스에서 `init` → `doctor`로 순서를 뒤집었는데 표는 그대로여서, 표만 보면 여전히 `doctor`가 먼저였습니다. 이제 `welcome → init → doctor → gate → check` 순이에요 — 뭔지 모를 때 · 켜기 · 확인 · (선택) 관문 설치 · 평소 점검. 위에서 아래로 읽으면 그게 곧 순서입니다. -->
<!-- show:en **Reordered the command table to match the order you actually run things.** The previous release flipped setup to `init` → `doctor`, but the table still listed `doctor` first, so the table alone told you the opposite. It now reads `welcome → init → doctor → gate → check`: don't know where to start, turn it on, confirm it, optionally install the gate, then the everyday check. Top to bottom is the sequence. -->

### Changed
- **명령어 표 정렬을 사용 순서로** (2026-08-01) — 한/영 랜딩 표 모두 `welcome · init · doctor · gate · check`(직접) 다음에 `find · review · handover · log · recall`(자동) 순으로 재정렬. 직전 릴리스에서 `doctor`의 설명은 "`init` 직후, 제대로 도는지 확인"으로 바꿨는데 **표에서는 `init`보다 위에 있어** 서로 어긋나 있었다. `gate`(프로젝트당 1회)를 `check`(평소 반복)보다 앞에 둔 것도 같은 이유 — 세팅이 먼저다.

## [0.27.0] - 2026-08-01
<!-- show:ko **설치 순서를 뒤집었어요 — `init` 먼저, 그다음 `doctor`.** 여태 `doctor` → `init`로 안내했는데, `doctor`는 **이 프로젝트의 훅이 제대로 매여 있나**를 보는 명령입니다. `init`을 안 했으면 훅이 안 도는 게 정상이라, 켜지도 않은 걸 검사시키고 있었어요. 실제로 재보니 `doctor`를 먼저 치면 경고 2개가 뜨는데 **둘 다 `init`이 해결할 것들**이었습니다(아직 init 안 함 · .env가 gitignore에 없음). 처음 설치한 사람이 첫 화면에서 읽고 무시해야 할 경고를 보게 되죠. `init`을 먼저 하면 경고 0개, 통과 9개로 깨끗하게 끝납니다. -->
<!-- show:en **Flipped the setup order — `init` first, then `doctor`.** The docs said `doctor` → `init`, but `doctor` checks whether the hooks are actually armed *in this project*. Before `init` they legitimately aren't, so we were asking people to inspect something they hadn't switched on yet. Measured: running `doctor` first produces two warnings, and **both are things `init` fixes** (not initialised here; `.env` not in `.gitignore`). A first-time user meets two warnings they're told to ignore. Run `init` first and it comes back 0 warnings, 9 passes. -->

### Changed
- **`init` → `doctor` 순서로 통일** (2026-08-01) — 근거는 실측이다. `init` 전 `doctor`: **실패 0 · 경고 2 · 통과 7**, `init` 후: **실패 0 · 경고 0 · 통과 9**. 두 경고 모두 `init`이 없애는 것이라, 먼저 치면 "무시해도 되는 경고"를 굳이 보여주는 셈이었다. 검증은 셋업 **뒤**에 해야 한 번에 깨끗한 답이 나온다. README 한/영의 `1분 설치`·명령어 표·`언제 무엇을` 표, 랜딩 한/영의 설치 코드블록·명령어 표·빠른 시작 두 줄까지 **여덟 자리** 전부 바꿨다.
- **`doctor` 명령의 보고 규칙도 새 순서에 맞춤** (2026-08-01) — 이제 `init` 다음에 도는 것이 정상 경로이므로, **아직 init 안 한 폴더는 결함이 아니라 순서가 바뀐 것**으로 다루게 했다. 그 상태에서 딸려 나오는 경고(gitignore·문서 누락)는 init이 해결하므로 **나열하지 말라**고 명시 — 겁줄 이유가 없다.

## [0.26.6] - 2026-08-01
<!-- show:ko **빠른 시작의 두 줄이 서로 반대 순서였어요.** "내 컴퓨터에 방금 설치"는 `doctor → init`인데 바로 아래 "이미 만들던 프로젝트에 설치"는 `init → doctor`로 적혀 있었습니다. 맞는 건 `doctor → init`이에요 — `doctor`가 "아직 init 안 함 → 지금 `/hi-vibe:init` 실행하세요"라고 다음 단계를 알려주는 구조라, 순서가 뒤집히면 그 안내가 쓸모없어집니다. -->
<!-- show:en **Two rows in the quick start gave opposite orders.** "Just installed on your machine" said `doctor → init`, while the row right below it said `init → doctor`. `doctor → init` is the correct one: `doctor` reports "not initialised here → run `/hi-vibe:init` now", so reversing the order throws that guidance away. -->

### Fixed
- **빠른 시작의 설치 순서가 줄마다 달랐다** (2026-08-01) — 한/영 모두 `이미 만들던 프로젝트에 설치` 줄만 `init → doctor → check`로 뒤집혀 있었다. README의 `1분 설치`(`doctor` 다음 `init`)와도 어긋났다. `doctor → init → check`로 통일. 저장소 전체에 같은 어긋남이 더 없는지 훑어 0건 확인.

## [0.26.5] - 2026-08-01
<!-- show:ko **자기가 정직하다고 자랑하는 문장을 뺐어요.** "꽤 겹쳐요. **먼저 밝히는 게 맞다고 봅니다.**" — 뒷문장이 겹친다는 사실보다 그걸 밝히는 자신을 칭찬하고 있었습니다. 겹친다고 말하는 것 자체가 정직한 거지, 정직하다고 덧붙이는 건 오히려 약해져요. 그냥 "꽤 겹쳐요."로 끝냅니다. 섹션 눈썹 문구 `정직함이 곧 기능이에요`도 같은 종류라 `무엇이 보장되나`로 바꿨어요 — 다른 눈썹은 전부 중립적인 안내인데 이것만 튀었습니다. -->
<!-- show:en **Cut the lines that congratulate us for being honest.** "Quite a bit, yes. **Better to say so up front.**" — that second sentence praises the act of admitting rather than just admitting. Saying it overlaps *is* the honest part; announcing your honesty on top only weakens it. It now stops at "Quite a bit, yes." The section eyebrow "Honesty is the feature" was the same species and is now "What's guaranteed" — every other eyebrow on the page is a plain descriptor, and that one stuck out. -->

### Changed
- **자기 칭찬 문구 제거** (2026-08-01) — 랜딩·README 한/영 네 곳의 "먼저 밝히는 게 맞다고 봅니다 / Better to say so up front"를 뺐다. 겹침을 인정하는 문장 뒤에 그걸 인정하는 자신을 칭찬하는 문장이 붙어 있었다. **보여주는 게 말하는 것보다 세다.** 섹션 눈썹 `정직함이 곧 기능이에요` → `무엇이 보장되나`(영문 `Honesty is the feature` → `What's guaranteed`) — 바로 아래 제목 "여기까진 기계가. 여기서부턴 AI가."가 이미 그걸 증명하고 있어 덧붙일 필요가 없었다.

## [0.26.4] - 2026-08-01
<!-- show:ko **"옵션이 없어요"라는 설명을 걷어냈어요.** 예전에 `--deep` 같은 옵션이 있었고 그걸 없앤 건 맞지만, 처음 보는 사람은 그런 게 있었는지도 모릅니다. "옵션이 없다"고 굳이 말하면 오히려 **"무슨 옵션이 있었는데?"** 하고 헷갈려요. CHANGELOG에 있어야 할 말이 제품 설명에 새어 나온 겁니다. 이제 없는 걸 설명하지 않고 **하는 일만** 적습니다. 표의 `발동` 배지가 좁은 화면에서 잘려 보이던 것도 고쳤어요. -->
<!-- show:en **Removed the copy that explains what isn't there.** There used to be flags like `--deep`, and removing them was right — but a first-time reader never knew they existed. Telling them "there are no flags" only makes them wonder which flags they're missing. That's changelog material that leaked into product copy. The page now describes what review does, not what it lacks. The `trigger` badge that looked clipped in the command table is fixed too. -->

### Fixed
- **`발동` 배지가 잘려 보임** (2026-08-01) — 증상: 명령어 표 오른쪽 배지의 알약 배경이 오른쪽에서 잘렸다. 원인: `.fire`가 기본 `display:inline`이라 아이콘과 글자가 좁은 셀에서 줄바꿈되고, 그 지점에서 배경이 끊겼다. `inline-flex` + `white-space:nowrap`으로 한 줄에 묶고, 마지막 열이 줄지 않게 고정했다.
- **영문 3곳에 남아 있던 "훅이 리뷰를 직접 실행"** (2026-08-01) — `test_no_overclaim`의 정규식이 `runs the review`만 잡고 **`runs it`(목적어가 대명사)을 놓쳤다.** 정규식을 넓히자 바로 3곳이 나왔다 — README의 `review` 절, 랜딩 fresh-eyes 카드, 그리고 뜻이 흐리던 열 제목(`MACHINE · hooks run it` → `hooks execute these`). **금지 검사도 표현 하나에만 맞춰 두면 같은 주장이 다른 말로 빠져나간다**는 것을 또 확인했다.

### Changed
- **"옵션이 없다"는 설명 제거** (2026-08-01) — 명령어 표의 `(옵션 없음 — …)`, 펼침 노트 제목 `review는 옵션이 없어요`, 본문의 `옵션이 아니라 기본이에요`·`외울 옵션이 없어요`, `gate`의 `옵션 없이 알아서 판단`을 전부 걷어냈다. 없앤 기능을 설명하는 건 **그 기능을 알던 사람에게만 의미**가 있고, 새 사용자에게는 없는 옵션을 찾게 만든다. 노트 제목은 `review가 알아서 정하는 것들`로, 내용은 그대로 두되 **하는 일**만 말한다. "가볍게 봐줘"로 조절할 수 있다는 안내는 유용하므로 유지.

## [0.26.3] - 2026-08-01
<!-- show:ko **공유하기 전에 랜딩을 마지막으로 손봤어요.** 링크 미리보기 태그(og·twitter)가 아예 없어서, 카카오톡이나 슬랙에 붙이면 제목만 덩그러니 나왔습니다. 그리고 첫 화면만 보면 범용 AI 코딩 도구처럼 읽혔어요 — 실제로는 Python 프로젝트를 만드는 입문자·1인 개발자용인데 "python3만 있으면 돼요"가 지원 대상이 아니라 설치 조건처럼 보였거든요. 사실과 다른 문구 넷도 같이 고쳤습니다. -->
<!-- show:en **Last pass on the landing page before sharing it.** There were no link-preview tags at all (og / twitter), so pasting the URL into KakaoTalk or Slack showed a bare title. The hero also read like a general-purpose AI coding tool — it's for beginners and solo devs building Python projects, but "just needs python3" looked like an install requirement rather than the target audience. Four inaccurate lines were fixed alongside. -->

### Added
- **링크 미리보기 태그** (2026-08-01) — `og:title`·`og:description`·`og:image`·`og:url`·`og:type`·`og:site_name`·`og:locale`과 `twitter:card` 일습. 크롤러가 상대경로를 못 읽는 경우가 있어 이미지는 절대 URL로 뒀다. `<title>`도 `hi-vibe`에서 `hi-vibe — Python 바이브 코딩 안전벨트`로 바꿨다(검색 결과·탭·공유에 모두 쓰인다).

### Fixed
- **명령어 표의 `review` 설명** (2026-08-01) — "훅이 직접 돌려요"가 남아 있었다. v0.26.1에서 여러 곳을 고쳤는데 이 표를 빠뜨렸다. "훅이 대화를 붙잡고 Claude에게 리뷰를 시켜요"로 교체.
- **`handover` 발동 시점이 틀림** (2026-08-01) — "세션 끝"이라고 적혀 있었지만 PreCompact 훅은 **대화가 정리(compact)되기 직전**에 돈다. 세션이 그냥 끝날 땐 안 돈다.
- **"코드가 바뀌면 자동으로 따라 갱신"** (2026-08-01) — 기계가 항상 보장하는 것처럼 읽힌다. 실제로는 리뷰(AI)가 어떤 문서를 고쳐야 하는지 확인하는 것이다. "문서를 역할별로 나눠 두고, 코드를 바꾸면 리뷰가 같이 확인한다"로.
- **"이 페이지가 안 낡는다는 게 증거예요"** (2026-08-01) — 자동 생성되는 건 업데이트 목록뿐이고 페이지의 나머지는 손으로 쓴다. 제목을 "업데이트 기록은 CHANGELOG에서 자동으로 가져와요"로 바꾸고, 본문에 "**자동인 건 이 목록이고 나머지는 손으로 쓴다**"를 명시했다.

### Changed
- **첫 화면에서 대상을 밝힘** (2026-08-01) — "hi-vibe가 AI가 대충 못 하게 잡아 줘요"는 언어·규모를 안 밝혀 범용 도구로 읽혔다. "Claude Code로 **Python** 프로젝트를 만드는 **입문자·1인 개발자**를 위한 안전벨트"로 바꾸고, 배지도 "python3만 있으면 돼요"(설치 조건) → "**Python 3.8+ 프로젝트에 최적화**"(지원 대상)로. JS/TS 부분 지원은 이미 아래에 밝혀져 있다.

## [0.26.2] - 2026-08-01
<!-- show:ko **직전 릴리스에서 규칙 하나를 잘못 넣었습니다.** "걸린 시간을 해명하지 마라"고 썼는데, 문제가 됐던 그 답변은 사용자가 **"15분이나 걸렸는데 뭐 때문이냐"고 직접 물어서** 실제 시각을 재서 답한 것이었어요. 추측 안 하고 측정한 좋은 답변인데 제가 반대로 막아버렸습니다. 이제 "안 물으면 말하지 말고, 물으면 재서 답하라"로 바로잡았어요. 그리고 그 대화에서 15분의 진짜 원인이 드러났습니다 — 리뷰가 아니라 **만들 때 범위가 커진 것**이었어요. "사이트에 적어줘"로 시작해 봇 기능 신설까지 번졌거든요. 요청 밖에서 발견한 건 고치지 말고 물어보게 했습니다. -->
<!-- show:en **The previous release added one rule that was simply wrong.** It said "don't account for how long things took" — but the answer that prompted it came from the user asking directly, "it took 15 minutes; was that hi-vibe or the feature?" The reply measured real timestamps instead of guessing, which is exactly right, and the new rule discouraged it. It now reads: don't volunteer timing, but if asked, measure and answer. That same conversation also revealed where the 15 minutes actually went — not the review, but scope growing during the build: a request to "write it on the site" turned into shipping a new bot feature. Findings outside the request are now reported, not fixed. -->

### Fixed
- **"시간을 해명하지 마라"가 과했다** (2026-08-01) — 증상: 도그푸딩 피드백을 확인 없이 받아, 소요 시간 설명 자체를 노이즈로 규정했다. 실제로는 사용자가 **"15분이나 걸렸는데 hi-vibe 때문이냐"고 먼저 물었고**, 답변은 `git` 시각으로 구간을 실측해 "리뷰 1분 22초, 나머지는 버그 수정"이라고 답한 것이었다 — 추측을 금지하는 `grounded-answers`가 제대로 작동한 자리다. "**안 물으면 붙이지 말고, 물으면 재서 답하라**"로 고쳤다. 일을 키운 쪽이 자신이면 그렇게 말하고 리뷰 탓으로 돌리지 말라는 것도 같이 적었다. (같은 결함을 두 번 설명하지 말라는 규칙은 유효해 유지 — 그 대화에서 실제로 두 번 설명됐다.)

### Added
- **요청 범위 밖 발견은 고치지 말고 묻는다 (`find` 모드)** (2026-08-01) — v0.26.1은 **리뷰 단계**의 스코프 크립만 막았는데, 실제 15분의 원인은 **만들 때** 번진 것이었다: "사이트에 적어줘"라는 요청으로 시작해 코드를 보다가 다른 문제를 발견하고 기능 신설까지 갔고, 그 새 기능의 버그를 잡느라 작업이 배로 늘었다. 이제 요청 밖에서 발견한 것은 **한 줄로 보고하고 사용자가 정한다**. 예외는 요청한 것을 하려면 반드시 통과해야 하는 경우뿐. **발견하지 말라는 게 아니라, 범위를 넓히는 결정이 사용자 것**이라는 규칙이다.

## [0.26.1] - 2026-08-01
<!-- show:ko **리뷰가 스스로 스코프 크립을 만들고 있었어요.** 자기 점검 루프가 "⚠️는 그 자리에서 고쳐라"라고만 해서, 명백한 버그든 새로운 정책이든 가리지 않고 다 고쳤습니다. 실제 사용에서 "권한이 없으면 회의당 한 번 안내 메시지를 보내자"처럼 **사용자가 요청한 적 없는 동작**을 리뷰가 만들어 넣었어요. 이 플러그인이 막으려는 증상("헷갈리는 결정을 묻지 않고 임의 진행")을 리뷰가 직접 저지른 겁니다. 이제 고치기 전에 "이걸 고치면 여태 없던 화면·메시지·규칙이 생기는가"를 묻고, 생기면 확인받습니다. 보고가 길어지던 것도 같이 줄였어요. -->
<!-- show:en **The review was generating its own scope creep.** The self-fix loop just said "fix every ⚠️ on the spot", so it made no distinction between a plain bug and a brand-new product policy. In real use it invented behaviour nobody asked for — "send one notice per meeting when permissions are missing". That is precisely the symptom this plugin exists to prevent (deciding something ambiguous without asking), committed by the review itself. It now asks first: does fixing this create a screen, message or rule the user has never seen? If so, it reports and waits. Report length is trimmed too. -->

### Fixed
- **자동 수정 루프가 기능 확장으로 번짐** (2026-08-01) — 증상: 디스코드 봇 도그푸딩에서, 리뷰가 버그 수정과 함께 **새 사용자 알림 정책**까지 만들어 넣었다. 원인: 자기 점검 루프 지시가 "⚠️는 그 자리에서 고쳐 ✅로 만든다"뿐이라 **결함과 새 정책을 가르는 기준이 없었다.** 이제 고치기 전에 둘로 나눈다 — ①원래 요구사항을 어긴 결함(예: 일부만 저장됐는데 전부 성공으로 표시) → 바로 수정 ②새 동작·알림·정책이 필요한 것(예: 권한 없을 때 안내 메시지 신설) → 발견 사실과 대안을 보고하고 확인. 기준 한 줄: **"이걸 고치면 사용자가 여태 못 보던 화면·메시지·규칙이 새로 생기는가"**. `fresh-eyes`가 잡으라고 있는 스코프 크립을 같은 리뷰가 만들어내던 자기모순을 끊었다.

### Changed
- **리뷰 보고 길이** (2026-08-01) — 같은 결함이 체크리스트·`👋` 줄·요약에서 반복 설명되고, **묻지도 않은 소요 시간 해명**이 붙었다(스킬에 없는 지시인데 에이전트가 스스로 변명한 것). 규칙을 넣었다: 같은 내용은 가장 구체적인 자리 한 곳에만 · ✅는 나열하지 말고 "그 외 항목 통과"로 묶기 · 시간은 변명 말고 사실 한 줄 · 끝에 "가볍게 봐줘" 안내 한 번. **줄이는 건 중복과 변명이지 내용이 아니다** — ⚠️가 많거나 fresh-eyes가 재고를 권하면 당연히 길어진다. `👋` catch 줄은 남긴다(뒤에서 조용히 잡으면 체감이 안 된다는 이유로 넣은 것이라, 짧게 만든다고 없앨 자리가 아니다).

## [0.26.0] - 2026-08-01
<!-- show:ko **파일을 통째로 지운 변경이 리뷰를 그냥 통과했어요.** 리뷰 범위를 "지금 존재하는 파일"로만 잡고 있어서, AI가 파일을 삭제하면 아무것도 안 걸렸습니다. 부르던 곳이 남아 있으면 런타임에 터지는데도요. 이제 지운 파일도 범위에 넣고, "이 파일들을 부르던 곳이 남아 있는지 확인하라"고 리뷰에 지시합니다. 그리고 슬래시 메뉴에 hi-vibe 항목이 16개 나오던 것을 10개로 줄였어요 — 내부 스킬 6개는 엔진이지 버튼이 아니라서 숨겼습니다(Claude는 여전히 알아서 부릅니다). -->
<!-- show:en **Deleting a file whole slipped past the review entirely.** Review scope only ever looked at files that currently exist, so when the AI removed one, nothing caught it — even though leftover callers blow up at runtime. Deleted files are now part of the scope, and the review is told to go looking for callers that survived. Also, hi-vibe was showing 16 entries in the slash menu; it's 10 now — the 6 internal skills are engines, not buttons, so they're hidden (Claude still loads them on its own). -->

### Fixed
- **삭제된 파일이 리뷰 범위에서 빠짐** (2026-08-01) — 증상: AI가 `lib.py`를 지워도 Stop 훅이 안 막았다. 원인: `_code_files`가 `os.path.isfile`로 **존재하는 파일만** 걸렀고(주석에 "삭제분 제외"라고 명시돼 있었다), 삭제만 있는 변경은 지문까지 비어 훅이 판단할 근거가 없었다. `_deleted_code_files`를 만들어 `scope`가 삭제분도 돌려주고, 지문에도 넣는다(안 넣으면 "파일만 지운 변경"이 영영 안 막힌다). Stop 훅의 차단 사유에 "**이 파일들을 부르던 곳이 남아 있는지 반드시 확인하라**"를 넣었고, `write-gate`도 지운 파일은 열 수 없으니 **남은 호출부를 찾으라**고 지시한다. `rm`도 Bash 쓰기 신호에 추가했다. 회귀 테스트 4개.
- **`gate` 예시가 같은 명령 두 줄** (2026-08-01) — 한/영 README 모두 `--ci` 시절 잔재로 두 줄이 동일했다. 한 줄로 합치고 "GitHub 프로젝트면 push 관문까지 같이 제안한다(고를 플래그 없음)"로 설명했다.
- **미사용 호환 함수 제거** (2026-08-01) — `changed_code_files()`.

### Changed
- **내부 스킬 6개를 슬래시 메뉴에서 숨김** (2026-08-01) — 명령 10개 + 스킬 6개가 전부 노출돼 메뉴에 hi-vibe 항목이 **16개** 보였다. "외울 게 적다"는 약속과 정반대라, 스킬에 `user-invocable: false`를 넣었다(Claude의 자동 호출은 그대로). 랜딩의 "같은 엔진을 세 갈래로 부를 수 있다"도 실제와 맞게 두 갈래로 고쳤다 — 숨긴 뒤에도 그 문장을 두면 그게 거짓말이 된다.
- **자동 확인과 전체 doctor의 경계를 문서에 명시** (2026-08-01) — 자동으로 도는 `--quick`은 ①hi-vibe 활성 ②SessionStart heartbeat ③추적된 `.env` 셋만 본다. **SessionStart가 살아 있으면 나머지 훅이 고장 나도 "정상"으로 보인다.** 설치 직후와 이상할 때는 `/hi-vibe:doctor`를 직접 돌려야 한다는 것을 한/영 README에 적었다.
- 테스트 163 → 167개.

## [0.25.1] - 2026-08-01
<!-- show:ko **어제 넣은 `.env` 검사가 경계에서 틀렸어요.** `.env`로 시작하는 이름을 전부 잡느라 direnv 설정 파일인 `.envrc`까지 "키를 폐기하세요"라고 했고, `.gitignore`에서는 `.env`라는 글자만 찾아서 주석(`# .env`)이나 무시 해제(`!.env`)까지 안전하다고 판정했습니다. 둘 다 실제로는 정반대예요. 이제 파일명은 정확히 `.env`이거나 `.env.`으로 시작하는 것만 보고, 무시 여부 판정은 **Git에게 직접 물어봅니다**. 테스트가 없어서 들어온 버그라 경계값 17개를 고정했어요. 그리고 이 검사는 전체 doctor에서만 돌아서 **이미 쓰던 프로젝트는 영영 모를 수 있었는데**, 이제 세션 시작 때 자동으로 확인합니다. -->
<!-- show:en **The `.env` check added yesterday was wrong at the edges.** It matched anything starting with `.env`, so direnv's `.envrc` got told to rotate its keys, and it looked for the literal string `.env` in `.gitignore`, so a comment (`# .env`) or an un-ignore rule (`!.env`) both read as safe. Both are the exact opposite of safe. Filenames are now matched as exactly `.env` or a `.env.` prefix, and whether Git ignores it is a question **asked of Git itself**. These slipped in because there were no tests, so 17 edge cases are now pinned. The check also only ran in the full doctor, meaning **an existing project could never find out** — it now runs automatically at session start. -->

### Fixed
- **`.envrc`를 유출로 오인** (2026-08-01) — 증상: direnv 설정 파일 `.envrc`가 추적되면 "키를 폐기하라"는 FAIL이 떴다. 원인: `name.startswith(".env")`가 `.envrc`·`.environment`·`.envoy`까지 잡았다. 정확히 `.env`이거나 `.env.`으로 시작하는 것만 본다(`is_env_secret_file`).
- **`.gitignore` 판정이 문자열 검색** (2026-08-01) — 증상: `# TODO: 나중에 .env 추가`(주석)와 `!.env`(무시 **해제**) 둘 다 "안전함"으로 나왔다. 원인: 파일 내용에 `".env"`가 있는지만 봤다. 주석·negate·우선순위·전역 설정을 다 아는 건 Git뿐이므로 **`git check-ignore`에 판정을 맡긴다**. 저장소가 아니면 판정 불가로 두고 아무 말도 하지 않는다(없는 경고를 만들지 않는다).
- **`commands/handover.md`의 handover 과장** (2026-08-01) — "so the next session keeps context". 과장 검사의 대상 파일을 손으로 나열하고 있어서 이 파일이 빠져 있었다 — 아래 변경으로 잡혔다.

### Added
- **`.env` 검사 회귀 테스트 17개** (2026-08-01) — 위 두 버그는 "주요 경로는 잘 도는데 경계에서 틀리는" 종류라 사람 눈에 안 보인다. 실제 비밀 파일 5종·견본 4종·닮은 이름 7종, `.gitignore`의 평범한 규칙/주석/negate/없음/저장소 아님, 중첩 폴더(`config/.env`), FAIL·WARN·OK·침묵 판정을 전부 고정했다.
- **세션 시작 때 자동 확인** (2026-08-01) — `doctor --quick`에 `tracked_env`를 실었다. 전체 `doctor`에만 두면 **이미 hi-vibe를 쓰던 프로젝트가 업데이트만 받았을 때 영영 모른다**(init을 다시 칠 일도, doctor를 칠 일도 없다). `write-gate` 스킬이 세션당 한 번 알리게 했다 — 파일은 열지 말고, 지우지도 말고, 알리기만.

### Changed
- **과장 검사가 활성 문서를 동적으로 수집** (2026-08-01) — 손으로 나열하면 목록에 없는 파일로 문구가 들어갈 때 조용히 통과한다. `commands/`·`agents/`·`skills/`를 포함해 그때그때 모으고(테스트와 CHANGELOG는 제외), 검사 범위가 좁아지면 그것도 실패로 잡는다. 바꾸자마자 위 `commands/handover.md` 한 건을 찾아냈다.
- 테스트 145 → 163개.

## [0.25.0] - 2026-08-01
<!-- show:ko **`.env`가 Git에 올라가면 아무도 못 잡던 구멍을 막았어요.** 비밀키 검사는 `.env`를 "키를 둬도 되는 자리"로 보고 검사에서 뺍니다. 그런데 그 파일을 `.gitignore`에 안 넣고 커밋해버리면 훅도 스캐너도 안 봐요 — 입문자가 실제로 자주 밟는 자리인데 검사망 자체가 없었습니다. 이제 `doctor`가 추적 중인 `.env`를 찾아 실패로 알리고(이미 push했으면 키를 폐기하라고 함께), `init`이 `.gitignore`에 넣습니다. 파일 내용은 읽지 않아요 — 이름만 봅니다. 그리고 **한 번 과장으로 판명된 문장이 다시 못 들어오게** 테스트로 막았습니다. -->
<!-- show:en **Closed the gap where a committed `.env` was invisible to everything.** The secret scan treats `.env` as a legitimate place to keep keys, so it skips it. But if that file never makes it into `.gitignore` and gets committed, neither the hook nor the scanner ever looks at it — a mistake beginners actually make, with no net under it at all. `doctor` now reports tracked `.env` files as a failure (and says to rotate the keys if you already pushed), and `init` adds them to `.gitignore`. It never reads the contents — only the names. Also: sentences already found to be overstatements are now blocked by a test. -->

### Added
- **`.env` 유출 검사 (`doctor`)** (2026-08-01) — 증상: `.env`에 키를 두고 `.gitignore`에 안 넣은 채 커밋하면 훅도 `check`도 그 파일을 안 본다. 원인: 비밀키 검사가 `.env*`를 **의도적으로 제외**하기 때문 — 구멍이 아니라 검사 대상 밖이라 영영 안 걸린다. `git ls-files`로 추적 중인 `.env` 계열을 찾아 **FAIL**로 알리고, 없으면 `.gitignore`에 있는지까지 본다. **파일 내용은 읽지 않는다** (읽으면 doctor 출력이 유출 통로가 된다). `.env.example`·`.sample`·`.template`·`.dist`는 견본이라 예외. 이미 push했다면 히스토리에 남으므로 **키 폐기(rotate)가 필요하다**는 것도 같이 알린다. 대신 지워주지는 않는다.
- **`init`이 `.env*`를 `.gitignore`에 추가** (2026-08-01) — 이미 추적 중이면 `git rm --cached`가 필요하다는 것과 rotate 필요성을 알리게 했다.
- **과장 재발 방지 테스트** (2026-08-01) — `tests/test_no_overclaim.py`. 상상으로 만든 금지어가 아니라 **실제로 문서에 있었고 사실이 아니어서 고친 문장 7종**만 담는다(handover 맥락 보존 · "항상 작동" · 훅이 리뷰를 직접 실행 · 코드 쓸 때마다 감지 · Bash 전수 검사 · CLAUDE.md 폴더 지도 · CHANGELOG 지연 생성). 각 항목에 **왜 과장이고 실제 동작이 무엇인지**를 실패 메시지로 붙였다. 금지 문구를 인용해 금지하는 줄은 `hi-vibe: allow-overclaim` 마커로 뺀다. 옛 문장을 못 잡게 되면 그 자체로 실패하는 자기검사와, 지금 쓰는 정직한 표현을 오탐하지 않는지 보는 검사도 함께 넣었다.

### Fixed
- **"항상 작동하는 안전벨트"** (2026-08-01) — 훅은 fail-open이라 조용히 죽을 수 있고, 죽었는지는 heartbeat를 보는 스킬 층이 돌아야 안다. "자동으로 매여 있고, 풀리면 알려주는 안전벨트"로 교체. **v0.24.4에서 "절대 표현을 전수 검토했다"고 밝혔는데 이걸 놓쳤다** — 그래서 이번엔 테스트로 고정했다.
- **"훅이 리뷰를 직접 돌린다"** (2026-08-01) — `stop_nudge.py`는 `decision:block`으로 턴을 막고 reason으로 리뷰를 **지시**할 뿐, 수행하는 건 Claude다. 8곳을 "대화를 붙잡고 리뷰를 시킨다"로 고치고, 기계/AI 표의 보장 방식을 `⚙️ 기계 감지 + 🤖 AI 수행`으로 나눴다. 훅은 리뷰가 **끝났는지까지는 못 본다**는 것도 밝혔다 — 같은 변경으로 두 번 막지 않으므로 중간에 끊기면 그 변경은 넘어간다(잔소리 반복을 피하려는 의도적 선택).

## [0.24.4] - 2026-08-01
<!-- show:ko **문서를 주장 단위로 한 번에 훑었어요.** 지금까지는 틀린 걸 발견할 때마다 하나씩 고쳤고, 그래서 계속 나왔습니다. 이번엔 hi-vibe가 하는 주장(handover는 무엇을 남기나 · CHANGELOG는 언제 생기나 · 훅은 무엇을 보나 …)을 목록으로 만들어, 각 주장이 적힌 자리를 전부 모아 코드와 대조했어요. 마지막 과장 하나가 나왔습니다 — "코드 쓸 때마다 에러 삼킴·비밀키를 잡아요"는 사실이 아닙니다. 훅은 Write/Edit만 보고, Bash로 쓴 파일은 못 봐요. -->
<!-- show:en **Swept the docs one claim at a time, in a single pass.** Until now each wrong line was fixed as it surfaced, which is why they kept surfacing. This time every claim hi-vibe makes (what handover records, when CHANGELOG appears, what the hooks see, …) was listed, every place it is stated was gathered, and each was checked against the code. One last overstatement fell out: "every code write is checked for swallowed errors and secrets" isn't true. The hook only sees Write/Edit; files written through Bash are invisible to it. -->

### Fixed
- **"코드 쓸 때마다 잡는다"는 과장** (2026-08-01) — 랜딩의 3단 설명(한/영)이 `init` 후 "every code write is checked" / "코드 쓸 때마다 잡고"라고 했다. PostToolUse는 `Write|Edit|MultiEdit`만 보므로 Bash로 쓴 파일은 검사되지 않는다. "Write/Edit로 쓸 때마다"로 좁히고, Bash로 쓴 것은 `check`가 저장소 전체를 훑어 받는다는 것을 같은 자리에 밝혔다.

### Added
- **주장이 사는 자리를 CLAUDE.md에 명시** (2026-08-01) — 동작 하나를 설명하는 문장은 **최대 8곳**에 산다(README 한/영 · 랜딩 한/영 · 스킬 · 템플릿 · **훅 안의 문자열 상수** · 명령 `.md`). `handover`가 무엇을 남기나 하나를 고치는 데 세 릴리스가 걸린 이유가 이것이다. 함께 적었다: **문구가 아니라 주장으로 찾아라** — 같은 주장이 자리마다 다른 말로 적혀 있어("맥락 안 잃게"/"까먹지 않아요"/"맥락이 안 끊긴다"/"never loses the thread"), 방금 고친 문구로 grep하면 나머지가 안 걸린다.

### Verified
- **전 주장 대조** (2026-08-01) — 20개 표면(문서 4 · 스킬 4 · 템플릿 2 · 에이전트 2 · 명령 6 · 훅 2)에서 주장을 주어별로 모아 코드와 대조했다. handover(무엇을 기록하나)·CHANGELOG(언제 생기나)·CLAUDE.md(무엇을 담나)·훅 대상 도구·`gate` 설치 항목·두 에이전트 역할 전부 일치. 없앤 플래그(`--all`·`--deep`·`--ci`)는 "이제 없다"는 설명 외에 잔존 0건. 구조 개수(명령 10·스킬 6·에이전트 2·훅 4·테스트 142) 실제와 일치. 절대 표현(모든·전부·항상·never·always·every) 전수 검토 — 위 1건 외 과장 없음. 한/영 대칭·앵커·목차·HTML 태그 균형 정상.

## [0.24.3] - 2026-08-01
<!-- show:ko **handover 과장의 마지막 한 군데와 "전체 지도"라는 옛 이름을 정리했어요.** 세션마다 주입되는 규율에 아직 "handover가 자동 기록되니 맥락이 안 끊긴다"가 남아 있었습니다. 실제로 남는 건 최근 요청·수정 파일·Git·테스트 상태라, 이제 그것을 그대로 적습니다. 그리고 CLAUDE.md에서 폴더 목록을 뺐는데도 여전히 "얇은 전체 지도"라고 부르고 있었어요 — 지도가 아니라 지침이라 "얇은 프로젝트 지침"으로 바꿨습니다. -->
<!-- show:en **The last handover overstatement and the outdated "map" wording are gone.** The discipline injected at every session start still said handover keeps your context unbroken. What it actually keeps is your recent requests, edited files, Git and test state — so that's what it says now. And although the folder listing was removed from CLAUDE.md, the docs still called it a "thin overall map." It isn't a map, it's guidance, so it now reads "thin project guidance." -->

### Fixed
- **SessionStart 규율의 handover 과장** (2026-08-01) — "직전에 handover가 자동 기록되니 **맥락이 안 끊긴다**"가 남아 있었다. 자동 기록은 최근 요청 5개(각 120자)·수정 파일·Git·테스트 상태이며 설계 이유나 실패한 접근까지 보존하지 않는다. "handover에 **이어갈 단서**(최근 요청·수정 파일·Git·테스트 상태)가 자동 기록된다"로 교체 — 매 세션 주입되는 문장이라 여기가 가장 오래 남는 과장이었다.
- **CLAUDE.md를 여전히 "전체 지도"라 부름** (2026-08-01) — v0.24.0에서 폴더 목록을 뺐는데 이름은 그대로였다. 표에서는 "폴더 목록을 넣지 않는다"고 하면서 바로 아래 문단은 "얇은 전체 지도"라 불러 서로 어긋났다. README 한/영과 docs-keeper 스킬 설명을 "얇은 프로젝트 지침 / thin project guidance"로 통일했다.

## [0.24.2] - 2026-08-01
<!-- show:ko **랜딩 "세 겹" 설명에 handover 과장이 한 군데 남아 있었어요.** 앞 릴리스에서 "맥락을 안 잃게 해준다"를 "이어갈 단서를 남긴다"로 고쳤는데, 세 겹 설명 안의 "대화가 새로 시작돼도 앞 내용을 까먹지 않아요"는 그대로였습니다. 자동 기록은 최근 요청 5개(각 120자)와 파일·Git·테스트 상태라 "안 까먹는다"는 사실이 아니에요. -->
<!-- show:en **One handover overstatement was still sitting in the landing page's three-layer section.** The previous release changed "never loses your context" to "leaves enough to pick up from," but the three-layer copy still said "a fresh chat never loses the thread." What's auto-recorded is your last 5 requests (120 chars each) plus file, Git and test state — "never loses" isn't true. -->

### Fixed
- **랜딩 세 겹 설명의 handover 과장** (2026-08-01) — 한국어 "대화가 새로 시작돼도 앞 내용을 까먹지 않아요", 영어 "a fresh chat never loses the thread"가 남아 있었다. v0.23.0에서 문서 설명은 고쳤지만 이 섹션은 다른 문구라 검색에 안 걸렸다. "이어갈 단서가 남아 있어요" / "has enough to pick up from"으로 교체.

### Verified
- **README·랜딩 전면 재점검** (2026-08-01) — 오늘 제거한 것들의 잔재 0건: CLAUDE.md 폴더 지도, CHANGELOG 지연 생성, 없앤 플래그(`--all`·`--deep`·`--ci`), 옛 에이전트 이름. 구조 개수(명령 10·스킬 6·에이전트 2·훅 4) 실제와 일치. 한/영 대칭 전 항목 동일(기능 카드 9·빠른시작 7·정직함 노트 5·펼침 노트 4·카드 그룹 3·계층 3·자동 배지 5·직접 배지 5), README 헤딩 35개 동일. 카드 그룹별 성격 대조에서 AUTO 그룹의 `직접` 0건·MANUAL 그룹의 `자동` 0건. 목차 링크·랜딩 앵커·표 행 깨짐 0건, HTML 태그 균형 정상, 테스트 142개 통과.

## [0.24.1] - 2026-08-01
<!-- show:ko **문서 정합성을 내세우는 플러그인이 자기 문서에서 모순을 냈어요.** 앞 릴리스에서 CLAUDE.md의 폴더 지도를 없앴는데, **세션마다 주입되는 규율 문구**에는 "구조가 바뀌면 CLAUDE.md 지도 동기화"가 그대로 남아 있었습니다. 없앤 기능을 훅이 매 세션 다시 요구하고 있었던 거예요. README·랜딩의 CLAUDE.md 설명도 여전히 "폴더 구조"라고 적혀 있었고요. 그리고 우리 도구로 우리 저장소를 검사하면 "**비밀키 11건**"이 떴습니다 — 전부 테스트용 가짜 키인데, 한 줄이 두 패턴에 걸려 6곳이 11건으로 부풀려진 것이었어요. 이제 0건입니다. -->
<!-- show:en **A plugin that sells doc consistency contradicted its own docs.** The previous release dropped the folder map from CLAUDE.md, but the discipline text injected at every session start still said "keep the CLAUDE.md map in sync when structure changes" — a hook asking, every session, for the thing we just removed. The README and landing page still described CLAUDE.md as holding the folder structure too. And scanning our own repo with our own tool reported **11 hardcoded secrets** — all test fixtures, and 6 real locations inflated to 11 because a single line matched two patterns. It reports 0 now. -->

### Fixed
- **SessionStart charter가 없앤 기능을 다시 요구함** (2026-08-01) — 증상: v0.24.0에서 CLAUDE.md 폴더 지도를 제거했는데, 매 세션 주입되는 규율에 "구조가 바뀌면 MODULE.md와 CLAUDE.md 지도 동기화"가 남아 있었다. 원인: 스킬·템플릿·README만 고치고 **훅 안의 문자열 상수**를 빠뜨렸다. 문서 정합성을 강제하는 플러그인이 정작 자기 지시문을 놓친 자리다. "폴더 책임이 바뀌면 MODULE.md, CLAUDE.md는 코드만 봐선 모를 것이 바뀔 때만"으로 교체.
- **docs-keeper에 남은 CHANGELOG 지연 생성 설명** (2026-08-01) — v0.23.0에서 init이 만들도록 바꿨는데 `.gitignore` 안내와 init 완료 메시지, log 모드 3번에 옛 설명이 남아 있었다. 문서 정의 표의 CLAUDE.md 행도 "폴더/요구사항이 바뀔 때"로 낡아 있었다.
- **README·랜딩의 CLAUDE.md 설명이 옛 구조** (2026-08-01) — 한/영 모두 "프로젝트 전체 지도 — 개요·요구사항·폴더 구조"였다. 폴더 목록을 넣지 않는다는 것과 그 이유를 명시했다.
- **자기 저장소 스캔에서 비밀키 11건** (2026-08-01) — 증상: `check` 스캐너를 hi-vibe 자신에게 돌리면 `hardcoded secrets: 11`이 떴다. 원인 두 가지 — ①테스트 픽스처의 가짜 키에 `allow-secret` 마커가 없었다 ②**한 줄이 여러 패턴에 걸리면 그만큼 중복 집계**돼서 고유 위치 6곳이 11건이 됐다. 세는 단위를 "키가 있는 자리"로 바꾸고(종류는 합쳐서 표시), 픽스처는 마커 붙인 상수 하나로 모았다. **부풀린 숫자는 검사 자체의 신뢰도를 깎는다.** 이제 0건.
- **테스트에서 닫히지 않은 파일** (2026-08-01) — `test_audit.py`의 `open(...).read()`가 `ResourceWarning`을 냈다. `with`로 감쌌다. `python3 -W error::ResourceWarning`로 0건 확인.

### Added
- **자기 저장소 비밀키 0건 회귀 테스트** (2026-08-01) — "우리 도구로 우리를 검사하면 11건"은 그 자체로 신뢰 문제라 기계로 고정했다. 한 줄이 여러 패턴에 걸려도 한 건으로 세는 것도 같이 검사한다.

### Changed
- **Bash 대응 범위를 정확하게 표현** (2026-08-01) — `bash_wrote_files`는 대표적인 쓰기 명령(리다이렉트·heredoc·`sed -i`·`cp`/`mv`/`tee`·`python -c`)을 **추정할 뿐 완전하지 않다**. `perl -pi`·`git apply`·빌드 도구·프로젝트 전용 CLI는 빠진다. 문서를 "Bash 수정도 전부 즉시 검사한다"가 아니라 "대표적인 것은 Stop 리뷰로 보완하고, 비밀키 전수는 `check`가 받는다"로 고쳤고, CLAUDE.md에 그렇게 쓰지 말라고 못 박았다.
- 테스트 140 → 142개.

## [0.24.0] - 2026-08-01
<!-- show:ko **Claude Code 기본 기능과 부딪히던 자리를 정리했어요.** ①CLAUDE.md에 폴더 지도를 만들어 넣고 있었는데, Claude Code의 기본 `/doctor`는 그런 내용(디렉터리 목록·의존성 목록·아키텍처 개요)을 "코드에서 알 수 있는 것"이라며 정리 대상으로 봅니다. 플랫폼이 지울 걸 계속 만들 이유가 없어서, 이제 함정·결정 이유·실행 명령만 남깁니다. ②`/hi-vibe:doctor`와 기본 `/doctor`가 이름만 같고 하는 일이 다른데 구분이 없었어요. 첫 줄에 명시하고, 사용자가 기본 doctor를 찾는 것 같으면 그쪽을 알려주게 했습니다. ③README와 랜딩에 기본 기능과 뭐가 겹치고 뭐가 다른지 표로 넣었어요. 겹치는 게 꽤 있고, 먼저 밝히는 게 맞습니다. -->
<!-- show:en **Cleaned up where this collided with Claude Code's own features.** (1) We were generating a folder map into CLAUDE.md, but Claude Code's built-in `/doctor` treats exactly that (directory layouts, dependency lists, architecture overviews) as derivable content to trim. No reason to keep producing what the platform deletes, so CLAUDE.md now holds only pitfalls, rationale and commands. (2) `/hi-vibe:doctor` and the built-in `/doctor` share a name but check different things, with nothing saying so. The first line now spells it out, and if you seem to want the built-in one, it points you there. (3) The README and landing page now carry a table of what overlaps with the built-ins and what doesn't. A fair amount overlaps, and saying so first is the honest move. -->

### Changed
- **CLAUDE.md에서 폴더 지도를 뺐다** (2026-08-01) — Claude Code 공식 문서상 기본 `/doctor`는 checked-in CLAUDE.md에서 *derivable content (directory layouts, dependency lists, architecture overviews)* 를 잘라내고 *pitfalls, rationale, conventions* 만 남긴다. hi-vibe는 정확히 그 잘릴 내용을 생성하고 있었다. 템플릿을 `함정`·`결정 기록`·`상세 문서`(실제 존재하는 MODULE.md만) 구조로 바꾸고, `docs-keeper`가 폴더를 훑어 나열하지 않게 했다. 파일 목록은 그 설계를 설명하는 MODULE.md 옆에 둔다 — CLAUDE.md는 매 세션 컨텍스트를 낸다. 문서 동기화 계약도 "구조가 바뀌면 CLAUDE.md 갱신"에서 "**코드만 봐서는 모를 것**이 바뀌었을 때만"으로 바꿨다. 파일을 옮길 때마다 고치게 만드는 문서가 결국 거짓말하는 문서가 된다.
- **`import-linter` 레이어 추론 근거 변경** (2026-08-01) — CLAUDE.md 폴더 지도에서 읽던 것을 실제 디렉터리·import 관계에서 읽도록 바꿨다(폴더 지도가 없어졌으므로).

### Added
- **`/hi-vibe:doctor`와 기본 `/doctor` 구분** (2026-08-01) — 이름이 같아 실제로 혼동이 있었다. 출력 첫 줄을 "hi-vibe의 훅·스캐너만 검사합니다 (Claude Code 설치 상태는 기본 `/doctor`가 따로 봅니다)"로 바꾸고, 명령 설명과 안내 규칙에도 넣었다. 사용자가 CLI 설치·자동 업데이트·CLAUDE.md 정리를 물으면 기본 쪽을 알려준다.
- **기본 기능과의 겹침·차이 표** (2026-08-01) — README 한/영과 랜딩 한/영에 추가. 겹치는 것(`/init`·auto memory·`/code-review`·`/verify`·`/doctor`)과 hi-vibe만 하는 것(즉시 감지·전체 스캔·증상/원인 CHANGELOG·프로젝트별 opt-in)을 갈라 적었다. **가장 큰 차이는 실행 시점**이라는 것도 공식 문서 인용으로 밝혔다 — `/verify`·`/code-review`는 직접 부를 때만 돌고, v2.1.215 전에는 자동 실행이 있었다가 빠졌다. hi-vibe의 Stop 훅이 서 있는 자리가 거기다.

## [0.23.0] - 2026-08-01
<!-- show:ko **외부 리뷰에서 나온 구멍 세 개를 막았어요.** ①`doctor`는 CHANGELOG가 없다고 `init`을 안내하는데 `init`은 그 파일을 안 만들었습니다. 몇 번을 다시 쳐도 경고가 안 없어지는 막다른 길이었고, 정작 중요하게 여긴 트러블슈팅 기록이 시작조차 안 됐어요. 이제 `init`이 만듭니다. ②Bash로 쓴 파일이 안전망을 통째로 빠져나갔습니다. 훅이 Write/Edit만 보는 건 Claude Code 계약이라 어쩔 수 없지만, 그 탓에 **리뷰까지 건너뛰고** 비밀키는 전체 스캔에도 없어서 영영 안 잡혔어요. Stop 훅이 Bash 명령까지 보게 하고, `check`에 저장소 전체 비밀키 검사를 붙였습니다. ③handover가 "맥락을 안 잃게 해준다"고 쓰여 있었는데, 실제로는 최근 요청 5개(각 120자)와 파일·Git·테스트 상태입니다. "이어갈 단서를 남긴다"로 고쳤어요. -->
<!-- show:en **Three gaps an outside review found are now closed.** (1) `doctor` warned that CHANGELOG.md was missing and told you to run `init` — but `init` never created it. Re-running it changed nothing, and the troubleshooting log this plugin cares most about never even started. `init` creates it now. (2) Files written through Bash slipped past everything. The hook only seeing Write/Edit is Claude Code's contract, but the knock-on effect was that **the review was skipped too**, and hardcoded secrets were absent from the repo-wide scan as well, so they were never caught at all. The Stop hook now reads Bash commands, and `check` scans the whole repo for secrets. (3) The docs said handover keeps your context from being lost; what it actually keeps is your last 5 requests (120 chars each) plus file, Git and test state. It now says "leaves the next chat enough to pick up from." -->

### Fixed
- **CHANGELOG가 생기지 않는 막다른 길** (2026-08-01) — 증상: 새로 설치한 사용자가 `doctor` → `init`만 실행하면 CHANGELOG.md가 생기지 않고, `doctor`는 계속 "문서 누락 → init 실행"이라고 안내했다. 원인: `docs-keeper`가 `Do NOT create MODULE.md or CHANGELOG.md at init`으로 지연 생성을 택했는데, `doctor`의 검사 목록에는 CHANGELOG가 있었고 자동 리뷰도 "없으면 만들지 말라"였다. 세 곳이 서로를 기대하며 아무도 안 만들었다. 트러블슈팅 기록은 CLAUDE.md·handover와 같은 급이라 판단해 **`init`이 만드는 쪽**으로 정리했다(MODULE.md는 그대로 지연 생성 — 빈 껍데기가 남으므로).
- **Bash로 쓴 코드가 리뷰를 통째로 건너뜀** (2026-08-01) — 증상: Claude가 heredoc이나 `sed -i`로 파일을 만들면 Stop 훅이 그 턴을 "코드 안 건드림"으로 보고 리뷰를 안 돌렸다. 원인: `parse_transcript`가 `Write|Edit|MultiEdit|NotebookEdit` tool_use만 세는데, 그 목록을 Stop 훅이 차단 조건으로 그대로 썼다. `_common.bash_wrote_files`로 Bash 명령의 쓰기 신호(리다이렉트·heredoc·`sed -i`·`cp`/`mv`/`tee`·`python -c`)까지 본다. 느슨하게 잡아도 안전하다 — 실제 차단은 git이 본 리뷰 안 받은 코드 변경이 있어야 하므로 없는 변경을 만들어내지 않는다.

### Added
- **`check`에 저장소 전체 비밀키 스캔** (2026-08-01) — 훅은 새로 쓰는 코드만 보므로 Bash로 들어온 키는 **어디에서도 안 잡혔다**. 판정 규칙은 PostToolUse 훅과 공유한다(`iter_secrets` — 에러 삼킴과 같은 SSOT 방식). `.env*`는 제외하고, `hi-vibe: allow-secret` 마커도 그대로 통한다. **값은 리포트에도 담지 않는다** — 파일·줄·종류만. 리포트가 키 유출 통로가 되면 안 되므로, 스킬에도 값 출력 금지를 명시했다.
- **Bash 경로 회귀 테스트 11개** (2026-08-01) — `tests/test_bash_coverage.py`. 쓰기 명령 8종은 잡고 조회 명령 7종은 안 잡는 것, 비밀키가 실제 `check` 경로(`cmd_scan` → `report.json`)까지 실리는 것, 리포트에 값이 절대 안 담기는 것, 0건일 때 없는 경고를 만들지 않는 것을 고정한다.
- **doctor-init 정합성 검사** (2026-08-01) — `doctor`가 "없으니 init 하라"고 안내하는 문서는 `init`이 실제로 만들어야 한다. 이번 막다른 길을 되살려 잡히는 것을 확인했다.

### Changed
- **handover 설명을 실제 동작에 맞춤** (2026-08-01) — "다음 대화가 맥락 안 잃게"는 과장이었다. 자동 기록은 최근 요청 5개(각 120자)·수정 파일·Git·테스트 상태이며, 설계 이유나 실패한 접근까지 자동 보존하지는 않는다. README 한/영·랜딩을 "이어갈 단서를 남긴다"로 고쳤다.
- 테스트 128 → 140개. PostToolUse가 Bash를 못 본다는 제약과 그 대응을 CLAUDE.md 핵심 요구사항에 적었다(훅에만 의존하는 안전장치를 새로 만들지 않도록).

## [0.22.0] - 2026-08-01
<!-- show:ko **CHANGELOG가 "고쳤다"만 남기고 있었어요.** 이 파일은 원래 트러블슈팅을 기록하려고 넣은 건데, `log`가 시키는 건 "무엇이 바뀌었나"까지였습니다. 나중에 `recall`로 찾는 사람이 궁금한 건 고쳤다는 사실이 아니라 "**왜 그랬더라**"인데 그게 안 남았어요. 이제 `Fixed`에는 증상과 원인을 같이 적습니다. 원인을 모른 채 고쳤으면 모른다고 적게 했어요 — 틀린 원인은 기록이 없느니만 못하니까요(다음 사람이 그걸 믿고 엉뚱한 데를 팝니다). -->
<!-- show:en **The CHANGELOG was only recording "fixed it."** This file exists to capture troubleshooting, but `log` only ever asked for *what changed*. What someone actually wants when they come back with `recall` isn't that it was fixed — it's **why it broke**, and that wasn't being kept. `Fixed` entries now carry the symptom and the cause. If the cause was never found, it says so: a wrong cause is worse than no record, because the next person trusts it and digs in the wrong place. -->

### Changed
- **`log`의 `Fixed` 항목에 증상·원인 요구** (2026-08-01) — Added/Changed/Removed는 "무엇이 바뀌었나"로 충분하지만 버그 기록은 그것만으론 쓸모가 없다. 증상(무엇이 어떻게 잘못 보였나) · 원인(실제로 뭐가 문제였나 — 증상과 다른 곳인 경우가 많다) · 왜 이 방법으로(다른 길을 버렸다면 그 이유)를 한 줄에 담게 했고, 예시를 붙였다. **원인을 모른 채 고쳤으면 모른다고 적는다** — 추측을 원인으로 쓰면 다음 사람이 그걸 믿고 엉뚱한 데를 판다.
- **CHANGELOG 템플릿·문서에 그 역할 명시** (2026-08-01) — 새 프로젝트가 받는 템플릿 머리말과 README 한/영·랜딩의 파일 설명이 전부 "변경 이력"이라고만 했다. 이 파일이 왜 있는지가 안 적혀 있으면 첫 줄부터 "고쳤음"으로 채워진다.

## [0.21.0] - 2026-07-29
<!-- show:ko **같은 실수를 세 번 놓쳐서, 이번엔 기계가 막게 했어요.** `review`를 훅이 직접 실행하도록 바꾼 뒤로 "이 명령은 자동인가 직접 치는 건가"가 문서마다 어긋났는데, 세 번 다 사람 눈으로는 뒤늦게 발견했습니다. 문장 하나만 보고 그 문장이 속한 분류를 안 봤기 때문이에요. 이제 명령별 자동/직접이 코드 한 곳에 적혀 있고, README 한/영과 랜딩 한/영이 그것과 어긋나면 CI가 실패합니다. 자동으로 도는 명령을 "직접 치세요"라고 권하는 문장도 잡아요. 과거 실수 세 개를 실제로 되살려 전부 잡히는 것까지 확인했습니다. -->
<!-- show:en **The same mistake slipped through three times, so a machine now blocks it.** Ever since the hook started running `review` itself, "is this command automatic or something you type?" drifted apart across the docs — and all three times a human caught it late. Each time the fix looked at one sentence without looking at the category that sentence belonged to. Now each command's mode lives in one place in code, and CI fails if either README or either half of the landing page disagrees. It also catches sentences urging you to run an automatic command yourself. All three past mistakes were resurrected and verified to be caught. -->

### Added
- **명령 자동/직접 분류 무결성 검사** (2026-07-29) — `tests/test_command_modes.py`. `COMMAND_MODE`가 단일 기준이고, README 한/영의 명령어 표와 랜딩 한/영의 `발동` 열이 전부 그것과 맞는지 대조한다. 랜딩 기능 카드가 자기 그룹(AUTO/MANUAL)과 반대 성격인 것도 잡는다. **과거 재발 3건을 실제로 되살려 셋 다 실패하는 것을 확인**했다.
- **자동 명령 권유 문구 금지 검사** (2026-07-29) — 자동으로 도는 명령을 "직접 호출하세요" 식으로 권하면 실패한다. 놓쳤을 때 쓰는 비상 손잡이라는 단서가 같은 문장에 있으면 통과 — **오탐이 나면 검사 자체가 무시당하고, 무시당하는 알림은 안전장치가 아니기 때문**에 좁게 잡았다. 옛 문장을 못 잡게 되는 것을 막는 자기검사도 같이 넣었다.

### Changed
- 테스트 122 → 128개. `COMMAND_MODE`가 자동/직접의 단일 기준이라는 것을 CLAUDE.md 폴더 지도에 적었다.

## [0.20.7] - 2026-07-29
<!-- show:ko **`find`를 치라고 권하는 문장이 README에 남아 있었어요.** 앞 릴리스에서 `review`를 예시에서 뺐는데, 같은 문장의 `find`가 "확실히 하려면 직접 호출하세요"라는 권유형 그대로였습니다. 랜딩은 "칠 일이 없어요"라고 적어둔 자리라 두 문서가 어긋나 있었어요. `find`의 실제 위치는 평소 습관이 아니라 **AI가 놓친 게 눈에 보일 때만 쓰는 비상 손잡이**라서, 그렇게 다시 썼습니다. -->
<!-- show:en **A sentence still urging you to run `find` was left in the README.** The previous release dropped `review` from that example, but `find` in the same sentence still read "call the command directly if you want to be sure." The landing page says "you never type these," so the two disagreed. `find`'s real place is an emergency handle for when you notice it didn't fire — not a habit to build — so it now says that. -->

### Fixed
- **README가 `find`를 권장 습관처럼 안내** (2026-07-29) — "확실히 실행하고 싶다면 `/hi-vibe:find`처럼 직접 호출하세요"는 평소에 치라는 말로 읽힌다. 랜딩(`말하면 걸리는 것 — 칠 일이 없어요`)과 어긋나 있었다. **평소엔 안 친다**를 먼저 말하고, 명령은 "안 걸린 게 보일 때 쓰는 비상 손잡이"로 위치를 낮췄다. `review`는 그 손잡이조차 필요 없다는 것(Stop 훅이 받침)도 같은 자리에서 밝힌다. 한·영 양쪽.

## [0.20.6] - 2026-07-29
<!-- show:ko **"뭘 치면 되나"를 말하는 자리를 전부 다시 맞췄어요.** 앞 릴리스에서 `review`만 자동으로 옮겼는데, `find`도 치는 게 아니었습니다. 랜딩의 3단 설명이 "켜지는 방식"으로 나눈 목록인데 한 칸에 AI가 알아서 거는 것(`find`)과 사람이 직접 치는 것(`check`)이 섞여 있었어요. 이제 훅 / 말하면 걸리는 것 / 내가 치는 것으로 갈라서, **평소에 치는 건 `check` 하나**가 그 목록에서도 바로 읽힙니다. 두 README도 `review`를 "AI라 보장이 안 되니 직접 치세요" 예시로 들고 있어서 고쳤고, 기능 카드 하나가 자동인데 "직접 점검" 칸에 들어가 있던 것도 바로잡았어요. -->
<!-- show:en **Every place that says what you actually type is now consistent.** The last release moved only `review` to automatic, but `find` isn't something you type either. The landing page's three tiers are meant to split things by *how they turn on*, yet one tier mixed what the AI triggers for you (`find`) with what you type yourself (`check`). They're now split into hooks / triggered by talking / what you type, so "day to day it's just `check`" reads straight off the list. Both READMEs also cited `review` as an example of "the AI might miss it, so run it yourself" — fixed. And one feature card marked automatic was sitting under the "manual checks" heading. -->

### Fixed
- **3단 설명의 분류 기준이 어긋남** (2026-07-29) — "켜지는 방식"으로 나눈 목록인데 둘째 칸에 `find`(AI가 발동)와 `check`(사람이 입력)가 섞여 있었다. `깔면 자동(훅)` / `말하면 걸리는 것(find·recall·log)` / `내가 치는 것(check·gate)`으로 재분류. 평소 표면이 `check` 하나라는 사실이 이 목록에서도 드러난다.
- **두 README가 `review`를 "AI 보장 없음" 예시로 인용** (2026-07-29) — 🤖 AI 설명이 "100% 보장 안 되니 `/hi-vibe:find`, `/hi-vibe:review`를 직접 호출하라"였다. `review`는 Stop 훅이 뒤를 받치므로 예시에서 빼고, 예외라는 것을 한 문단으로 명시했다.
- **자동 기능 카드가 "직접 점검" 칸에 있었음** (2026-07-29) — `안전벨트가 풀리면 알려줘요`는 카드 태그가 `자동`인데 MANUAL 그룹에 있었다. 자동 그룹으로 옮기고(그룹명 `기억·검토·감시`), 대신 `오탐 방지`를 `check`와 같은 칸으로 내렸다. 이제 어느 그룹에도 성격이 반대인 카드가 없다.
- **명령어 표의 `check` 설명이 카드와 불일치** (2026-07-29) — "하다 만 것"에 테스트 커버리지가 빠져 있었다.

### Verified
- **한/영 대칭 재확인** (2026-07-29) — 기능 카드 9·빠른시작 7·정직함 노트 5·카드 그룹 3으로 양쪽 동일. 그룹별 카드 성격 대조에서 AUTO 그룹의 `직접` 카드 0건, MANUAL 그룹의 `자동` 카드 0건. README 헤딩 34개 동일, 목차 링크·랜딩 앵커 깨짐 0개, HTML 태그 균형 정상, 테스트 122개 통과.

## [0.20.5] - 2026-07-29
<!-- show:ko **랜딩 본문이 아직 옛날 동작을 설명하고 있었어요.** 앞 릴리스에서 빠른 시작 표만 고쳤는데, 전면 재점검해 보니 본문 네 군데가 더 낡아 있었습니다. 제일 심한 건 정반대로 적힌 문장이었어요 — "부르면 도는 것(find·review·check), 강력하지만 AI가 놓치면 안 걸려요". `review`는 이제 훅이 강제하니 놓쳐도 걸립니다. 기계가 하는 일 목록에도 Stop 훅이 아직 "기록 안 하면 알려주기"로 남아 있었고, `check` 카드에는 새로 붙은 "하다 만 것"과 proof-eyes 검증이 통째로 빠져 있었어요. 한·영 양쪽 다 고쳤습니다. -->
<!-- show:en **The landing page's body copy was still describing the old behaviour.** The previous release fixed only the quick-start table; a full re-audit turned up four more stale spots. The worst said the exact opposite of what ships today: "on demand (find · review · check) — powerful, but the AI can skip them." `review` is enforced by a hook now, so skipping it isn't possible. The machine-guarantees list still described the Stop hook as nudging you to log things, and the `check` card was missing both the new half-finished-work buckets and the proof-eyes verification pass. Fixed in both languages. -->

### Fixed
- **랜딩이 `review`를 "AI가 놓치면 안 걸리는 것"으로 설명** (2026-07-29) — v0.17.0에서 Stop 훅이 리뷰를 직접 실행하도록 바꾼 것이 README에는 반영됐지만 랜딩 본문에는 들어가지 않았다. 3단 설명에서 `review`를 빼고 "놓쳐도 훅이 잡는다"를 명시.
- **기계가 하는 일 목록의 Stop 훅 설명이 옛날 것** (2026-07-29) — "뭔가 바꿨는데 기록 안 하면 알려주기"는 안내(nudge) 시절 동작이다. "아무도 안 본 코드 변경이 있으면 리뷰를 직접 돌리기"로 교체하고, AI 쪽 목록의 `review` 항목은 "돌아온 결과를 읽고 판단하기"로 옮겼다.
- **`check` 카드에 v0.17.0 기능이 빠져 있음** (2026-07-29) — "하다 만 것"(에러 삼킴·TODO·테스트 없는 모듈) 버킷과 proof-eyes 검증("12건 중 진짜 3건")이 명령어 표에만 있고 기능 카드에는 없었다.
- **`check` vs `review` 설명에서 proof-eyes 누락** (2026-07-29) — `check`를 "기계(스캐너)만"으로 설명하고 있었다. 두 에이전트의 실제 차이(fresh-eyes는 코드를 의심해 의도가 필요, proof-eyes는 스캐너를 의심해 증거가 필요)를 그대로 적었다.

### Verified
- **문서 전면 재점검** (2026-07-29) — 회귀 테스트 122개 실제와 일치. 구조 개수(명령 10 · 스킬 6 · 에이전트 2 · 훅 4) 실제와 일치. 없앤 플래그(`--all`·`--deep`·`--ci`)와 옛 에이전트 이름 잔존 0건. 한/영 README 헤딩 34개로 동일, 랜딩 구성요소도 한/영 대칭(기능 카드 9·빠른시작 7·정직함 노트 5·펼침 노트 3). 목차 링크·랜딩 앵커 깨진 것 0개, HTML 태그 균형 정상. `doctor`가 훅 4종을 실제로 실행하는 것도 소스에서 확인(Stop 훅 포함).

## [0.20.4] - 2026-07-29
<!-- show:ko **랜딩의 "상황별 빠른 시작"만 옛날 그대로였어요.** README는 치는 명령과 자동으로 도는 것을 나눠놨는데, 랜딩의 이 표는 `review`·`find`를 여전히 "치세요" 칸에 넣어둬서 칠 게 일곱 개처럼 보였습니다. 둘 다 "칠 것 없어요"로 바꿨어요. 같은 표에 사실이 틀린 줄도 있었습니다 — 이미 만들던 프로젝트에 설치하면 `review`를 치라고 했는데, `review`는 마지막 커밋까지만 봅니다. 쌓인 코드 전체를 보는 건 `check`라서 그렇게 고쳤어요. -->
<!-- show:en **The landing page's "quick start by situation" was the one place still showing the old surface.** The README already separates what you type from what runs on its own, but this table still listed `review` and `find` under "run this", making it look like seven commands. Both now say "nothing to type". One row was also factually wrong: it told you to run `review` after installing on an existing project, but `review` only ever looks back as far as the last commit. Scanning everything you've already built is `check`, so that's what it says now. -->

### Fixed
- **랜딩 빠른 시작이 자동 동작을 수동 명령으로 보여줌** (2026-07-29) — v0.20.1에서 README를 세팅/평소/자동으로 나눴는데 랜딩의 `상황별 빠른 시작` 블록은 같이 고쳐지지 않았다. 한 화면 안에서 "실제로 치는 건 넷"과 "일곱 개를 치세요"가 동시에 보이던 상태. 한·영 모두 수정.
- **"이미 만들던 프로젝트엔 review" 안내가 사실과 다름** (2026-07-29) — `review_scope.py`의 범위 계단은 안 커밋 → 안 푸시 → **마지막 커밋**이라, 히스토리가 있는 저장소에서 `review`는 마지막 커밋 하나만 본다. "지금까지 쌓인 코드를 처음 보는 눈으로 검토"는 저장소 전체를 스캔하고 proof-eyes가 후보를 열어보는 `check`의 동작이므로 그쪽으로 바꿨다.

## [0.20.3] - 2026-07-28
<!-- show:ko **공개 README에 저자 이름이 또 들어갔던 것.** 예전에 한 번 빼놓고, 문서를 다시 쓰면서 똑같이 또 들어갔어요. 사람이 눈으로 잡는 걸론 두 번 다 놓쳤으니 이번엔 기계가 막습니다 — 공개 문서에 개인 이름이 있으면 테스트가 실패해요. 실제로 이름을 심어보고 잡히는 것까지 확인했습니다. -->
<!-- show:en **The author's name slipped into the public README again.** It had been removed once before, then came back while the docs were rewritten. Human review missed it both times, so a machine now blocks it: the test suite fails if a personal name appears in public docs. Verified by planting one and watching it get caught. -->

### Fixed
- **공개 README에 저자 개인 이름** (2026-07-28) — `README.ko.md`의 리뷰 절에 개인 호칭이 들어가 있었다. 커밋 `9ce720f`에서 같은 이유로 한 번 제거했던 것이 문서를 다시 쓰며 재발했다. 일반 표현으로 교체.

### Added
- **개인 이름 유출 검사** (2026-07-28) — 활성 문서 전체에서 저자 이름·호칭을 찾아 있으면 테스트를 실패시킨다(`jx-hxxx` GitHub 핸들은 예외). **두 번 일어난 실수는 사람이 아니라 기계가 막아야 한다** — 이 저장소의 원칙(안전장치를 사람 주의력에 기대지 않는다)을 문서 검사에도 적용한 것. 이름을 실제로 심어 잡히는 것을 확인했다.

### Verified
- **전면 재점검** (2026-07-28) — 섹션을 통째로 갈아끼운 자리에서 내용 유실 없음(삭제된 헤딩은 전부 이름만 바뀐 것). 목차 링크 한/영 모두 깨진 것 0개. 랜딩 HTML 태그 균형 정상. 다른 개인정보(로컬 절대경로·이메일·전화번호) 흔적 없음.

## [0.20.2] - 2026-07-28
<!-- show:ko **문서에 빠져 있던 새 기능들을 채웠어요.** 어제오늘 만든 "훅이 죽으면 알려줌"·"CI가 연속 실패하면 알려줌"이 CHANGELOG에만 있고 README와 랜딩에는 없었어요. 세션 시작 훅이 하는 일 목록과 랜딩 카드에 반영했습니다. 회귀 테스트 숫자는 6곳 전부 실제와 맞는 것을 확인했고, 한/영 문서 섹션 수와 랜딩 HTML 태그 균형도 같이 점검했어요. -->
<!-- show:en **Filled in the features the docs had missed.** The "we tell you when a hook dies" and "we tell you when CI keeps failing" work from the last two releases lived only in the CHANGELOG — the README and landing page never mentioned it. Both now list it under what the session-start hook does. The regression-test count was verified against reality in all six places, and KO/EN section parity plus landing HTML tag balance were checked too. -->

### Fixed
- **README·랜딩에 빠져 있던 새 기능** (2026-07-28) — v0.18(CI 사망 알림)·v0.19(훅 사망 알림, init 안 한 폴더 안내)가 CHANGELOG에만 있었다. 사용자 문서에 없으면 **없는 기능**이다. 두 README의 기능 표·훅 다이어그램에 SessionStart가 하는 일로 추가하고, 랜딩의 `자가진단` 카드를 "안전벨트가 풀리면 알려줘요"로 바꿨다(doctor를 직접 치는 것에서 자동 감지로 무게 이동).

### Verified
- **전면 점검** (2026-07-28) — 회귀 테스트 수: 실제 121개, 문서 6곳 전부 121로 일치. 구조 개수 주장(훅 4종·스킬 6개·명령 10개) 실제와 일치. 없앤 플래그(`--all`·`--deep`·`--ci`)가 활성 문서에 남아 있지 않음(SHOWCASE 타임라인은 역사 기록이라 제외). 한/영 README 섹션 14개로 동일. 랜딩 HTML 태그 균형 이상 없음.

## [0.20.1] - 2026-07-28
<!-- show:ko **README가 실제 동작과 어긋나 있던 것.** `find`·`review`를 직접 치는 명령처럼 큰 코드 블록으로 먼저 보여줬는데, 둘 다 알아서 도는 것들이라 안 쳐도 됩니다. "직접 칠 일 없다"는 맨 아래 묻혀 있었어요. 이제 자동이라고 먼저 밝히고, 명령어는 접어뒀습니다. 명령어 표도 10개를 평평하게 늘어놓던 걸 세팅용·평소용·자동으로 나눴어요. 볼드 문법이 깨져 별표가 그대로 보이던 것도 고쳤습니다. -->
<!-- show:en **The README no longer contradicts the behaviour.** `find` and `review` were presented as commands to type, leading with a big code block — but both fire on their own. The line saying "you don't type this" was buried at the bottom. Now the automatic part comes first and the commands are folded away. The command table, previously ten flat rows, is split into setup / day-to-day / automatic. A broken bold that rendered literal asterisks is fixed too. -->

### Fixed
- **README가 자동 동작을 수동 명령처럼 보여주던 것** (2026-07-28) — `find`·`review` 절이 명령어 코드 블록으로 시작해 "이걸 쳐라"로 읽혔다. 실제로는 훅과 스킬이 알아서 부르고, 그 사실은 절 맨 아래에 한 줄로 묻혀 있었다. 자동이라는 것을 먼저 밝히고 명령어는 `<details>`로 접었다. **문서가 구현과 어긋나면 그것도 과장이다.**
- **볼드가 깨져 별표가 그대로 보이던 것** (2026-07-28) — `**새 서브에이전트(fresh-eyes)**가`처럼 닫는 `**` 앞이 문장부호이고 뒤가 글자면 마크다운이 닫는 표시로 인정하지 않는다. 괄호를 볼드 밖으로 빼서 해결하고, 같은 패턴이 더 있는지 정규식으로 전수 확인해 CHANGELOG의 한 건도 같이 고쳤다.

### Changed
- **명령어 표를 세 덩어리로** (2026-07-28) — 10개를 평평하게 나열하니 전부 외워야 할 것처럼 보였다. `세팅할 때 한 번씩`(welcome·doctor·init·gate) / `평소에`(check) / `알아서 도는 것`(review·find·log·handover·recall)으로 나눴다. **실제로 치는 건 세팅 때 셋, 평소엔 하나**라는 것이 표에서 바로 보인다.

## [0.20.0] - 2026-07-28
<!-- show:ko **`gate`도 옵션이 사라졌어요.** GitHub에 올리는 프로젝트인지 알아서 확인하고 CI 관문을 제안합니다. 예전엔 `--ci`를 외워서 쳐야 목록에 떴어요. 그리고 처음엔 GitHub 없이 시작했다가 나중에 연결하면 아무도 안 알려주던 것도 고쳤어요 — 이제 세션 시작할 때 한 번 짚어줍니다. 이미 다 만든 프로젝트에 켜서 위반이 수백 개 쏟아질 때도, 하나하나 묻지 않고 종류별로 세어 보여준 뒤 **질문 한 번**으로 기존 코드는 덮고 새 코드부터 봅니다. -->
<!-- show:en **`gate` lost its flag too.** It now checks whether the project is on GitHub and offers the CI guard accordingly — you used to have to know to type `--ci`. And if you started without GitHub and connected it later, nothing told you the guard was now possible; the session start now mentions it once. When switching it on for a mature codebase floods you with hundreds of violations, it no longer asks about them one by one: it counts them by kind and asks a **single** question, then baselines the old code and gates only what you write next. -->

### Changed
- **`gate --ci` 플래그 제거** (2026-07-28) — CI를 목록에 넣을지는 `git remote`로 직접 확인해 정한다. 외워서 쳐야 보이는 옵션은 모르는 사람에겐 없는 기능이다(`review --deep`과 같은 실패). 리모트가 없으면 빼고 **왜 뺐는지 한 줄** — GitHub에 안 올리는 프로젝트에 워크플로 파일만 깔면 **안 도는 안전장치**가 되어 보호받는다는 착각만 준다.
- **위반이 쏟아질 때 하나씩 묻지 않는다** (2026-07-28) — 기존 프로젝트에 켜면 수백 개가 정상인데, "이거 의도한 거예요?"를 수백 번 물으면 그 자체가 실패다(사용자도 코드를 다시 열기 전엔 답할 수 없다). 이제 ①종류별로 세어 4~5줄로 압축하고 ②**질문은 한 번** ③JS/TS는 `eslint --suppress-all`로 기존 위반을 `eslint-suppressions.json`에 한 번에 덮는다(소스 미변경). Python은 `--add-noqa`를 **금지** — 소스 수백 군데에 이유 없는 `# noqa`가 영구히 남는다. ④개별 판단은 **그 코드를 실제로 건드릴 때** 한다(그때는 review·fresh-eyes가 이미 붙는다). ⑤순환 의존만 지금 본다.

### Added
- **나중에 GitHub에 연결하면 한 번 알린다** (2026-07-28) — gate를 칠 때 리모트가 없었으면 CI는 목록에서 빠지는데, 그 판단이 **한 번 내려지고 다시 안 보였다.** 나중에 저장소를 만들어 연결해도 "이제 켤 수 있다"고 아무도 말해주지 않았다. 이제 SessionStart가 리모트 유무와 가드 파일 유무를 보고 딱 한 번 짚는다. **깔아주지는 않는다** — 설정 파일을 쓰는 건 사용자가 정한다.

## [0.19.0] - 2026-07-28
<!-- show:ko **안전벨트가 풀렸으면 이제 알려줘요.** 훅은 호스트를 안 깨뜨리려고 조용히 실패하게 만들어져 있어요. 그 대가로 훅이 망가져도 **에러조차 안 뜨고**, `/hi-vibe:doctor`를 직접 치기 전엔 몰랐습니다. 이제 훅이 돌 때마다 흔적을 남기고, 훅과 무관하게 도는 스킬이 그 흔적이 낡은 걸 보면 알려줘요. init 안 한 폴더에서 조용히 아무것도 안 하던 것도 한 번은 알려주고요 — 안 쓰실 거면 그렇다고 말씀만 하면 다시 안 묻습니다. -->
<!-- show:en **You'll now know when the seatbelt came undone.** Hooks are built to fail silently so they never break the host. The cost: when a hook breaks there's **no error at all**, and you wouldn't know until you happened to run `/hi-vibe:doctor`. Now every hook leaves a heartbeat, and the skill layer — which runs independently of hooks — tells you when that heartbeat goes stale. A folder where hi-vibe was never initialized used to be silently inert; now it says so once, and you can opt out for good with a word. -->

### Added
- **훅 생존 신호(heartbeat) + 스킬이 그걸 확인** (2026-07-28) — 훅 4종이 돌 때마다 `.hi-vibe/state/heartbeat.json`에 시각을 남긴다. "훅이 죽었나"는 **훅으로 확인할 수 없다**(자기가 안 도니까). 확인할 수 있는 건 훅과 무관하게 도는 스킬 층뿐이라, write-gate가 세션당 한 번 `doctor.py --quick`으로 흔적을 보고 낡았으면 알린다. doctor를 안 쳐도 고장을 안다.
- **`doctor.py --quick`** (2026-07-28) — 훅을 실제로 실행하는 전체 진단은 느려서 자동으로 자주 부를 수 없다. 파일만 읽어 `alive`/`stale`/`never-ran`/`not-initialized`/`optout`을 JSON 한 줄로 준다. **건강 확인 창구를 새로 만들지 않고 doctor에 깊이만 하나 더했다** — 같은 질문에 두 개의 답이 생기면 갈린다.
- **`.hi-vibe/optout`** (2026-07-28) — "이 폴더에선 안 쓴다"를 기록할 자리. 마커가 있어도 훅을 끄고, 다시 묻지 않는다. 기록할 곳이 없으면 계속 물어보게 되고, 그건 잔소리다.

### Changed
- **init 안 한 폴더에서 조용히 아무것도 안 하던 것** (2026-07-28) — `.hi-vibe/`가 없으면 훅이 통째로 빠져나가서, "켜져 있고 깨끗함"과 "아예 꺼져 있음"이 구분되지 않았다. 지인이 설치하고 init을 안 했으면 **보호받고 있다고 믿으면서 아무 보호도 못 받는다.** 이제 스킬이 한 번만 알리고, 사용자가 안 쓴다고 하면 opt-out으로 조용해진다. **마음대로 init하지는 않는다** — opt-in은 사용자가 정한다.
- **CLAUDE.md에 설계 원칙 명문화** (2026-07-28) — "안전장치를 사람 주의력에 기대지 않는다". 오늘 세 건(리뷰 자동 실행·CI 사망 알림·훅 사망 알림)이 전부 같은 원칙에서 나왔다. 기록(CHANGELOG)에만 두면 다음에 뭘 만들 때 안 읽히므로, 새 기능마다 읽히는 자리로 옮겼다 — **원칙을 기록에만 두는 것도 사람 주의력에 기대는 것**이다.

## [0.18.0] - 2026-07-28
<!-- show:ko **세워둔 관문이 죽으면 이제 알려줘요.** `gate --ci`로 CI를 깔아주고는 그게 깨져도 알려주는 경로가 없었어요. 실제로 한 프로젝트에서 CI가 나흘간 죽어 있었는데(최근 60번 중 47번 실패) GitHub 알림함에 68개가 쌓여 아무도 못 봤습니다. 깨진 CI는 '빨간불'이 아니라 **검사가 아예 안 도는 상태**라, 그동안 lint가 한 번도 안 돌았어요. 이제 세션을 시작할 때 '이 저장소 CI가 N번 연속 실패 중'이라고 대화창에서 알려줍니다. 원인이었던 `npm ci` lock 불일치도 템플릿에 경고로 남겼어요. -->
<!-- show:en **When a guard you installed dies, you'll now hear about it.** `gate --ci` set up CI and then had no way to tell you it broke. In one project CI was dead for four days (47 of the last 60 runs failed) while 68 unread GitHub notifications piled up. A broken CI isn't a red light, it means **the checks aren't running at all** — lint hadn't run once in that window. Now the session start tells you right in the chat: "CI has failed N times in a row." The `npm ci` lockfile mismatch that caused it is documented in the template too. -->

### Added
- **세션 시작 시 CI 건강 상태 알림** (2026-07-28) — 현재 브랜치의 CI가 **연속 2회 이상** 실패 중이면 세션 첫머리에 알린다(워크플로 이름·연속 실패 수·마지막 성공일). 1회 실패는 흔해서 세지 않는다 — 잔소리가 되면 무시되고, 그러면 이 기능을 만든 이유와 정반대가 된다. `gh` CLI는 **선택 의존성**이라 없거나 미인증·오프라인이면 조용히 생략하고(fail-open), 결과는 20분 캐시해 세션마다 네트워크를 때리지 않는다.

### Fixed
- **CI 캐시가 `.hi-vibe/` 마커를 만들어버리던 문제** (2026-07-28) — 캐시를 쓰려고 `makedirs`를 하면서 **hi-vibe를 켜는 마커**를 생성했다. init한 적 없는 저장소에 훅이 돌기 시작하는 경로였다("init 안 한 프로젝트에는 전혀 개입하지 않는다"가 깨짐). 마커가 이미 있을 때만 캐시하도록 고치고 회귀 테스트로 고정. 구현 중 실제로 이 저장소에 `.hi-vibe/`가 생겨서 발견했다.

### Changed
- **`gate --ci`가 깔고 끝내지 않는다** (2026-07-28) — ①기존 워크플로의 의존성 설치 명령을 먼저 읽고 맞춘다(`npm ci` vs `npm install`). 플랫폼별 optional 의존성(wasm이 끌어오는 `@emnapi/*` 등)은 맥에서 만든 lock에 안 들어가 리눅스 러너에서 거부되는데, 배포 워크플로만 `npm install`이고 가드만 `npm ci`여서 나흘간 CI가 죽어 있던 실사례가 있다. ②설치 후 "푸시하고 실제 통과를 한 번 확인하라"고 안내한다 — 첫 실행이 깨진 채 방치되면 관문은 세운 적 없는 것과 같다.

## [0.17.0] - 2026-07-27
<!-- show:ko **이제 리뷰를 직접 안 쳐도 돼요 — 끝날 때 알아서 돌아가요.** 제일 잘 잡는 남의 눈 리뷰(fresh-eyes)가 `--deep` 뒤에 숨어 있어서 대부분 안 켜졌어요. 이제 옵션이 아예 없어졌고, 코드를 고친 채로 턴이 끝나면 훅이 그 자리에서 리뷰를 돌려요 (같은 변경으로 두 번 잔소리하진 않아요). 커밋·푸시한 뒤에도 '안 푸시한 커밋 → 마지막 커밋' 순으로 내려가 계속 봐줍니다. `check`도 후보 목록만 던지지 않고 딴 클로드(proof-eyes)가 코드를 열어 진짜만 골라주고, 에러 삼킴·TODO 같은 '하다 만 것'까지 찾아줘요. -->
<!-- show:en **You don't type review any more — it runs itself when a turn ends.** The sharpest reviewer (fresh-eyes) was hidden behind `--deep`, so most reviews never got it. Flags are gone entirely, and when a turn ends with unreviewed code the hook runs the review right there (never nagging twice for the same change). Already committed and pushed? It steps down to unpushed commits, then the last commit, instead of giving up. `check` no longer dumps a candidate list either: a fresh Claude (proof-eyes) opens the real code and keeps only what's real, and now also finds unfinished work — swallowed errors, TODOs. -->

### Fixed
- **광고 테스트 수가 조용히 낡던 구멍** (2026-07-27 18:03) — 무결성 검사가 (파일, 정규식) **6쌍만** 보고 있어서, 문구를 새 문단·새 파일에 하나 더 쓰면 그 숫자는 아무도 안 보고 낡았다(실제로 겪은 실패 모드). 이제 위치가 아니라 **표현**으로 잡아 활성 문서 전체를 훑는다 — 어디에 써도 검사 대상이 된다. 표현을 통째로 바꿔 검사가 0건이 되는 것도 하한(6곳)으로 막았다. 낡은 숫자를 새 문단에 심어 실제로 걸리는 것까지 확인.
- **`test`로 시작하는 평범한 파일이 테스트로 분류되던 버그** (2026-07-27 17:41) — 테스트 파일 판별이 `base.startswith("test")`까지 참으로 봐서 `testimonials.py`·`testing_utils.py`·`testbed.js`가 테스트로 잡혔다. 그 파일 안의 **진짜 중복 함수 쌍이 "테스트끼리 유사" 버킷으로 밀려나 사용자가 읽는 code↔code 목록에서 사라졌다**(닮은 게 정상인 테스트라고 우선순위를 낮추는 버킷이므로). 접두사 규칙을 제거하고 재현 케이스를 회귀 테스트로 고정.

### Changed
- **테스트 판별 함수 두 개를 각자 이름으로 분리** (2026-07-27 17:41) — `is_test_file`과 `_is_test_file`이 이름은 같은 일을 하는 듯한데 기준이 달라(전자는 `conftest.py`·`*.spec.ts`를 잡고 후자는 `tests/` 아래를 잡음) 중복으로 보였다. 합치지 않았다 — **다른 질문**이기 때문이다: dead 판정은 "러너가 이름으로 부르나"(좁게)를, near-dup 버킷은 "닮은 게 정상인 코드냐"(넓게, 픽스처·헬퍼 포함)를 묻는다. 합쳤다면 `tests/helpers.py`의 안 쓰는 헬퍼가 dead 후보에서 빠졌을 것이다(FP-02). 대신 `is_test_file`(이름 규칙) / `is_test_code`(= 이름 규칙 + `tests/` 아래)로 이름을 각자 하는 일에 맞추고, **규칙 정의는 `is_test_file` 한 곳에만 두고 넓은 쪽이 재사용**하게 했다.
- **`review`에서 `--all`·`--deep` 제거 — 옵션 0개** (2026-07-27 16:52) — 제일 잘 잡는 fresh-eyes가 `--deep` 뒤에 숨어 있어 대부분의 리뷰에서 안 돌았다. 외워야 켜지는 옵션은 결국 안 켜진다. 이제 범위·깊이·병렬을 **기계가 준 숫자를 보고 스킬이 판단**한다: fresh-eyes는 기본으로 소환(작은 변경일 때만 생략하고 생략 사실을 밝힘), 규모가 크면 순차/병렬을 **묻지 않고** 알리고 병렬 진행. 끄는 건 플래그가 아니라 말("가볍게 봐줘")로 한다. `review --all` 모드는 기본 동작에 흡수됐다.
- **Stop 훅: 안내 → 실행 (`decision: block`)** (2026-07-27 16:52) — "리뷰하세요" 안내는 무시된다. 사용자는 기능마다 명령어를 치지 않고, 애초에 코드를 쓰는 건 에이전트다. 이제 리뷰 안 받은 코드 변경이 있으면 Stop을 막고 그 자리에서 `Mode: review`를 수행시킨다. 잔소리가 되지 않도록: 코드를 안 건드린 턴엔 안 걸리고, **같은 변경으로는 두 번 막지 않으며**(내용 지문), mark되면 조용해지고, 범위 계산이 실패하면 막지 않는다(fail-open). 기존 CHANGELOG 잔소리는 삭제 — 리뷰 체크리스트 10번이 자동으로 기록하므로 중복이다.

### Added
- **`proof-eyes` 에이전트 — check도 후보를 던지지 않고 검증한다** (2026-07-27 17:24) — 스캐너는 놓치지 않는 대신 헛짚어서, 후보 20건을 그대로 내밀면 사용자는 뭐가 진짜인지 몰라 전부 무시했다. 이제 스캔이 끝나면 **후보 자리의 실제 코드를 열어보는** 서브에이전트를 기본으로 소환해 진짜/오탐/애매를 가르고 정리 방향까지 준다. **버린 것도 숫자로 밝힌다**("12건 중 진짜 3건, 오탐 9건") — 조용히 줄이면 스캐너가 못 찾은 것처럼 읽힌다. 지우지는 않는다(최종 결정은 사람). fresh-eyes와 역할이 다르다: fresh-eyes는 **코드**를 의심하고(의도 필요), proof-eyes는 **스캐너**를 의심한다(증거 필요).
- **스캐너에 "하다 만 것" 버킷** (2026-07-27 17:24) — 정리 대상(지울 것)과 성격이 다른 **마저 할 것**을 따로 준다: `swallowed_errors`(저장소 전체 에러 삼킴 — 훅은 새로 쓰는 코드만 보므로 훅 설치 전 코드·남이 짠 코드는 여기서 처음 검사된다), `todos`(남겨둔 TODO/FIXME), `test_coverage`(모듈 대비 테스트 파일 수 **요약만** — 파일별로 나열하면 테스트 없는 프로젝트에서 전부가 후보가 되어 소음이다). 판정 규칙은 PostToolUse 훅과 **같은 정의를 공유**한다(`iter_swallows`) — 두 벌 두면 한쪽만 고쳐져 "훅은 잡는데 스캔은 못 잡는" 상태가 된다. 훅 파일을 못 읽으면 대체 구현을 만들지 않고 `scan.unavailable`에 밝힌다.
- **기능 제안은 넣지 않기로 함** (2026-07-27 17:24) — "로그인은 있는데 비밀번호 찾기가 없네요" 류. 근거가 코드 안에 없고, 같은 플러그인의 fresh-eyes가 잡는 스코프 크립을 우리가 조장하게 된다. 대신 코드 안에 근거가 있는 **"하다 만 흔적"** 만 발견한다.
- **리뷰 범위 계단** (2026-07-27 16:52) — 커밋·푸시하고 나면 `review`가 "볼 게 없습니다"로 죽던 문제. 이제 `안 커밋한 변경 → 안 푸시한 커밋 → 마지막 커밋` 순으로 내려가고, `scope`·`scope_label`로 지금 무엇을 보는지 밝힌다. 계단은 "그 단계에 바뀐 파일이 있느냐"로 고르므로, 리뷰를 마쳐서 비는 것과 구분되어 옛날 커밋이 도로 끌려오지 않는다.
- **`review_scope.py`의 `fingerprint`** (2026-07-27 16:52) — 리뷰 대상의 내용 지문. Stop 훅이 "한 번 넘긴 변경으로 또 막지 않기"에 쓴다.
- **회귀 테스트 17건** (2026-07-27 17:41) — 범위 계단(커밋 후 폴백·리뷰 완료가 옛 커밋을 안 끌어옴)·지문·Stop 차단(막는다/두 번은 안 막는다/코드가 바뀌면 다시 막는다/mark되면 조용/범위 실패 시 fail-open)·에러 삼킴 전체 스캔(언어별 탐지·줄 번호 정확도·`allow-swallow` 존중·훅 있으면 unavailable 비어 있음)·TODO 수집·테스트 커버리지가 목록이 아닌 요약·테스트 판별(`test` 접두사 오분류 재현 케이스 포함). 87 → 104개.

### Decided against
- **범용 병렬 서브에이전트 오케스트레이션은 여전히 미도입 — 다만 "유일한 fit"은 이번에 도입** — 원래 판단은 전면 보류였다. ①hi-vibe는 안전벨트(제약)지 생산성 액셀러레이터가 아니다 — "설계 빨리 병렬로"는 Claude Code 기본 Task 도구로 이미 되며, 우리가 또 싸면 잡화점이 된다. ②병렬은 벽시계 시간만 줄이고 **총 토큰은 오히려 늘어난다**(시스템프롬프트·파일재독 N배). ③fresh-eyes가 잡을 전형적 과잉설계다. **이 세 근거는 그대로 유효하고, 범용 오케스트레이션은 앞으로도 안 만든다.** 다만 당시 "유일한 fit"으로 지목했던 리뷰 팬아웃은 이번 릴리스에서 도입했다 — 보류 조건이 "속도 실측"이었는데, 실제 문제는 속도가 아니라 **품질**로 드러났기 때문이다: 변경이 크면 순차 리뷰가 뒤로 갈수록 얕아지고, 사용자에게 순차/병렬을 물어봐야 켜지는 구조라 결국 안 켜졌다. 같은 이유로 `check`의 proof-eyes도 후보가 많으면 나눠 띄운다. **적용 범위는 리뷰·검증 두 곳뿐이며, 토큰이 더 든다는 사실은 사용자에게 그때그때 밝힌다.**

## [0.16.0] - 2026-07-22
<!-- show:ko **이제 hi-vibe가 뒤에서 뭘 잡으면 티가 나요 — 명령어 없이도.** 지금까진 너무 조용히 잡아서 "정말 돌고 있나?"가 안 보였어요. 이제 훅이 코드 쓸 때마다 자동으로 에러 삼킴·비밀키를 잡으면 그 자리에서 `👋 hi-vibe가 방금 <무엇>을 잡았어요` 한 줄이 붙고, 세션 끝엔 "이번 세션: 코드쓰기 N회 검사 · 👋 M건 잡음(잡을 게 없으면 0건)" 요약이 한 번 떠요 — 잡은 게 없어도 조용히 돌고 있었다는 증명. 마커도 낚싯대(🎣)에서 인사 손짓(👋 "hi"-vibe)으로, 문구도 "없었으면 놓쳤을 것"에서 "방금 잡았어요/고쳤어요"로 능동형으로 바꿨어요. 붙이는 조건(진짜 결함일 때만·통과엔 안 붙임)은 그대로. -->
<!-- show:en **Now you can see hi-vibe working in the background — without typing a command.** It used to catch things so quietly you couldn't tell it was running. Now, whenever the always-on hook auto-catches a swallowed error or a secret as you write code, it appends a `👋 hi-vibe just caught <what>` line on the spot, and at session end you get a one-time summary: "this session: N code writes checked, M caught by hi-vibe (0 if nothing to catch)" — proof it ran even when clean. The marker also changed from a fishing rod (🎣) to a friendly wave (👋 "hi"-vibe), and the wording shifted from "you'd have missed it" to the active "just caught/fixed it." When it attaches (real defects only, never on passes) is unchanged. -->

### Added
- **훅 자동 catch 표기** — `post_write_guard`가 명령어 없이 에러 삼킴·비밀키를 자동으로 잡으면, 응답 끝에 `👋 hi-vibe가 방금 …을 잡았어요` 한 줄을 남기라고 지시한다. 항상 도는 기계 강제 층의 성과가 명령어 없이도 보인다.
- **세션 활동 요약(Stop)** — 세션 끝에 "코드쓰기 N회 검사 · 👋 M건 잡음" 한 줄(세션당 1회). 잡은 게 0건이어도 "검사 N회 · 위험 0건(깨끗)"으로 조용히 돌고 있었음을 증명. `_common.session_activity()`가 트랜스크립트에서 코드 쓰기 수와 `👋 hi-vibe` 마커 수를 집계(상태 파일 없이 트랜스크립트 파생, fail-open). CHANGELOG를 이미 만졌으면 로그 잔소리는 침묵하되 요약은 유지.

### Changed
- **catch 마커 🎣 → 👋 + 능동형 문구** — 낚싯대에서 인사 손짓(👋 — "hi"-vibe와 맞음)으로. 문구도 "hi-vibe 없었으면 놓쳤을 것"(반사실) → "👋 hi-vibe가 방금 …을 잡았어요/고쳤어요"(능동). write-gate·repo-xray·root-cause-first·fresh-eyes 네 표면 + 훅에 동일 적용. **붙이는 조건(세 조건·과장 금지)은 불변** — 통과·스타일·기지 항목엔 여전히 안 붙는다. grep 접두사는 `👋 hi-vibe`로 고정.

### Tests
- +3 (훅 자동 catch가 👋 마커 지시 / 세션 요약의 쓰기·catch 집계 / 0건도 요약 표시). CHANGELOG 만졌을 때 로그 잔소리는 침묵하되 요약 유지하도록 기존 테스트 갱신. 84→87.

## [0.15.0] - 2026-07-14
<!-- show:ko **hi-vibe가 조용히 뭔가를 살렸을 때, 이제 한 줄로 티가 나요.** hi-vibe는 티 안 나게 뒤에서 잡아주는 게 설계라, 잘 작동할수록 정작 "이거 플러그인 덕에 산 거였네"를 모르고 지나가요. 그래서 세 조건을 모두 만족할 때 — ①hi-vibe가 찾았고 ②진짜 결함·판단이고 ③그 스킬 돌기 전엔 몰랐던 것 — 보고 맨 끝에 `🎣 hi-vibe catch — <무엇>을 <어느 스킬>이 잡음` 한 줄을 답니다. 리뷰 체크리스트·남의 눈·구조 스캔·원인 규율 네 곳에 들어갔어요. 핵심은 과장 금지: 통과·스타일 지적·이미 알던 것엔 절대 안 붙어요(자화자찬이 되면 신뢰가 깨지니까). 접두사가 고정이라 나중에 세션에서 grep해 "이 플러그인이 실제로 뭘 잡았나"를 모아볼 수도 있어요. -->
<!-- show:en **When hi-vibe quietly saves you, now you see it — one line.** hi-vibe is built to work invisibly in the background, so the better it works, the more you miss the "oh, the plugin caught that" moment. Now, when all three conditions hold — ① hi-vibe found it ② it's a real defect/judgment ③ it wasn't on your radar before the skill ran — the report ends with `🎣 hi-vibe catch — <what> caught by <which skill>`. It's wired into the review checklist, fresh-eyes, the structure scan, and the root-cause discipline. The key is no overclaiming: it never attaches to passes, style nits, or things you already knew (self-congratulation would break trust). The fixed prefix lets you grep past sessions to see what the plugin actually caught. -->

### Added
- **`🎣 hi-vibe catch` 반사실적 발견 표기** — hi-vibe 스킬/에이전트가 *사용자가 그냥 지나쳤을 것*을 붙잡았을 때만, 보고 맨 끝에 고정 접두사로 한 줄 공을 밝힌다. 판정은 세 조건 모두 충족 시: ①hi-vibe가 찾음(사용자·메인 흐름이 자발적으로 짚은 게 아님) ②진짜 결함·판단(스타일·취향 아님) ③스킬 실행 전 레이더 밖. write-gate(`Mode: review`)·fresh-eyes 에이전트·repo-xray(`Answer shape`)·root-cause-first 네 표면에 동일 규약 삽입. "과장 금지" 가드로 통과·스타일·기지(旣知) 항목엔 붙이지 않는다. 접두사 고정으로 세션 grep 집계 가능. (프롬프트 규약 — 코드·테스트 추가 없음.)

## [0.14.4] - 2026-07-13
<!-- show:ko **프론트엔드·CSS·레이아웃 수정은 이제 사용자가 검증해요 — 에이전트가 브라우저를 안 띄웁니다.** 시각적 변경(생김새·간격·정렬·색·반응형)은 앱을 직접 보고 있는 사용자가 검증 루프예요. 그래서 이런 변경은 에이전트가 Playwright로 자가 검증하는 대신, 변경하고 "⌘⇧R 후 무엇을 볼지" 한 줄만 알려주고 넘깁니다(레이아웃이 어긋나면 사용자가 즉시 봄 — 딴 브라우저 또 띄우는 건 이중일). 같은 화면을 여러 모드·폭·로딩상태로 반복 렌더하는 것도 금지. CSS 값도 브라우저로 픽셀 실측해 상수로 박지 말고 콘텐츠 기반으로 잡아요(실측 상수는 행 높이 바뀌면 깨지는 땜빵). v0.14.3 등급제로도 안 잡히던 "프론트 한 줄 바꾸는 데 브라우저 10번" 지연의 실제 원인 제거. -->
<!-- show:en **Frontend/CSS/layout tweaks are now verified by you — the agent won't spin up a browser.** For visual changes (looks, spacing, alignment, color, responsive), the user watching the app IS the verification loop. So instead of self-verifying with Playwright, the agent makes the change and just tells you "after ⌘⇧R, here's what to look at," then hands off — if the layout is off you see it instantly, and a second headless browser is double work. Re-rendering the same view across modes/widths/loading states is also banned, and CSS values should be content-based rather than pixel-measured constants (a measured constant breaks when row height changes). Removes the real cause of the "one frontend line → ten browser renders" slowness that even v0.14.3's tiering didn't catch. -->

### Changed
- **UI·CSS·레이아웃 변경은 사용자 검증 특례** (write-gate `Mode: review` 9번) — 시각적 변경은 등급과 별개로 에이전트가 브라우저(Playwright)를 띄워 자가 검증하지 않는다. 변경 + 캐시버스팅 + "⌘⇧R 후 확인할 것" 한 줄을 사용자에게 넘긴다. 같은 화면을 여러 상태(모드·폭·로딩중)로 반복 렌더 금지, CSS 값은 픽셀 실측 상수 대신 콘텐츠 기반으로. 예외: 사용자가 "브라우저로 확인" 명시 / 특정 폭에서만 깨지는 회귀 등 렌더로만 재현되는 경우. 마지막 요약 줄에 "화면 확인 요청" 종결 상태 추가. 등급제(9번 tier)가 레이아웃을 tier 3으로 보고 여전히 자가 렌더시키던 틈을 메움.

## [0.14.3] - 2026-07-13
<!-- show:ko **검증 강도가 이제 변경 크기에 비례해요 — 작은 일에 12분 안 걸려요.** 리뷰 체크리스트의 "실행 검증(필수)"이 변경 크기와 상관없이 늘 앱 구동·브라우저 실행을 요구하던 걸, 세 등급으로 나눴어요: 문서·포맷은 검증 없이 통과 / 패턴 복제·설정 한 줄 같은 작은 변경은 구문·서빙 확인만 / 로직·API·버그 수정만 실제 실행 관찰. 여기에 "최소 충분" 원칙을 못박아, 같은 걸 여러 화면폭·반복으로 다시 확인하거나 요청 범위 밖까지 파고드는 과잉검증을 금지했어요. hi-vibe가 작은 작업을 무겁게 만들던 지연의 근본 원인 제거. -->
<!-- show:en **Verification strength now scales with change size — small tasks don't take 12 minutes.** The review checklist's "run-verification (required)" used to demand running the app / a browser regardless of change size; it's now tiered: docs/formatting pass with no verification, small changes (pattern copies, one-line config) need only a syntax/serving check, and only behavior changes (logic/API/bug fixes) require observing a real run. A "minimum sufficient" rule forbids re-checking the same thing across widths/repeats or digging outside the request's scope. Removes the root cause of hi-vibe making small tasks slow. -->

### Changed
- **실행 검증을 등급제로** (write-gate `Mode: review` 9번) — 변경의 런타임 표면·크기에 비례해 검증한다. ①런타임 표면 없음(문서·주석·포맷·동작 동일 설정/이름변경) → 검증 불필요 ②작은·국소 변경(검증된 패턴 복제·script/설정 한 줄) → 구문·서빙 확인만 ③동작 변경(로직·API·스키마·새 기능·버그) → 실제 실행 관찰. "최소 충분 원칙"으로 여러 조건(화면폭·브라우저·반복) 재확인·범위 밖 검증을 명시 금지. 마지막 요약 줄도 "가벼운 검증"·"런타임 표면 없음" 종결 상태를 허용. 이전엔 크기 무관 "실행 검증(필수)"이라 3줄짜리 변경에도 앱·브라우저를 띄우게 만들던 지연의 근본 원인.

## [0.14.2] - 2026-07-13
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

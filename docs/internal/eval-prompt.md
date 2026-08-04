# 설치 전 적합성 평가 프롬프트

랜딩 페이지(`docs/index.html`)의 `verify-ko` / `verify-en` 섹션과 같은
내용이다. 페이지가 바뀌면 여기도 같이 고친다 — 두 벌이 갈리면 이 파일이
거짓말이 된다.

**쓰임**: 외부 AI(Claude·Codex·Gemini)에 붙여넣어 hi-vibe와 내 프로젝트를
같이 보게 하는 질문. 실제로 이 방식으로 받은 평가가 v0.22~v0.28의 상당수를
만들었다 — `.env` 유출 구멍, 삭제된 파일이 리뷰를 통과하던 것, 리뷰의
자동 수정이 기능 확장으로 번지던 것.

**주의**: `[내 프로젝트 GitHub 링크]` 자리를 채우지 않으면 AI가 hi-vibe만
보고 답한다 — 그러면 "내 프로젝트에 맞나"가 아니라 "이 플러그인 어때"가 된다.
랜딩에서는 입력칸에 링크를 넣고 버튼을 누르면 그 자리가 자동으로 채워진다.

## 한국어

```text
https://github.com/jx-hxxx/hi-vibe

hi-vibe의 실제 구현과 아래 프로젝트의 코드를 확인하고,
이 프로젝트에서 hi-vibe를 어떻게 활용하면 좋을지 알려주세요.

제 프로젝트:
[내 프로젝트 GitHub 링크]

다음을 실제 파일이나 코드 사례와 함께 살펴봐 주세요.

1. 기존 구현 탐색과 중복 작업 방지가 도움이 될 부분
2. 구현 후 리뷰가 오류나 누락을 발견할 수 있는 부분
3. 세션 간 작업 맥락과 트러블슈팅 기록 관리가 특히 도움이 될 부분
4. 중복 코드·안 쓰는 코드·비밀키 등 전체 점검이 유용할 부분
5. 기존 테스트·lint·CI·문서와 함께 적용하는 방법

비슷한 파일이 있다는 이유만으로 기능이 같다고 단정하지 말고,
실제 동작을 확인할 수 없다면 확인 불가라고 밝혀 주세요.

마지막에는 다음만 간단히 정리해 주세요.

- 가장 도움이 될 지점 3가지
- 관련된 실제 파일
- 설치한다면 권장하는 첫 사용 순서
```

## English

```text
https://github.com/jx-hxxx/hi-vibe

Look at hi-vibe's actual implementation and at the code of the project below,
then tell me how I could put hi-vibe to use in this project.

My project:
[my project's GitHub link]

Go through the following, citing real files or code from my project.

1. Where searching for existing implementations would prevent duplicated work
2. Where a post-implementation review would catch errors or omissions
3. Where carrying working context and troubleshooting records between sessions would help most
4. Where a repo-wide sweep for duplicate code, unused code and secrets would be useful
5. How to fit it alongside the tests, lint, CI and docs that already exist here

Do not conclude that two things do the same job just because the filenames look alike,
and if you cannot verify actual behaviour, say so plainly.

Close with just these.

- The 3 places it would help most
- The real files involved
- If you do install it, a suggested order to start with
```

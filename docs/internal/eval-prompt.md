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

hi-vibe는 Python 프로젝트를 Claude Code로 개발하는 개인 개발자를 위한 플러그인입니다.

아래 프로젝트 저장소를 가능하면 실제 코드까지 확인하고, hi-vibe가 제 프로젝트의 개발 과정에 실질적으로 도움이 될지 분석해 주세요.

제 프로젝트:
[내 프로젝트 GitHub 링크]

README의 설명뿐만 아니라 hi-vibe의 실제 구현도 함께 살펴보고, 다음 내용을 평가해 주세요.

1. 기존 구현 탐색과 중복 작업 방지에 도움이 되는지
2. 기능 구현 후 자동 리뷰가 발견할 수 있는 문제
3. 세션 간 작업 맥락과 트러블슈팅 기록 관리의 활용도
4. 프로젝트 전체 점검 기능이 필요한 규모와 구조인지
5. 현재 사용 중인 도구나 작업 방식과 겹치는 부분
6. 이 프로젝트에서 기대할 수 있는 장점과 한계

가능하면 제 프로젝트의 실제 파일이나 코드에서 확인한 구체적인 사례를 들어 설명해 주세요. 직접 확인하지 못한 내용은 추측하지 말고 확인 불가라고 밝혀 주세요.

마지막에는 다음 내용을 간단히 정리해 주세요.

- 가장 유용할 것으로 예상되는 기능
- 활용도가 낮거나 필요하지 않은 기능
- 이 프로젝트에 설치를 추천하는지와 그 이유
```

## English

```text
https://github.com/jx-hxxx/hi-vibe

hi-vibe is a plugin for solo developers building Python projects with Claude Code.

Please look at the repository below — the actual code where you can — and analyse whether hi-vibe would genuinely help how I develop this project.

My project:
[my project's GitHub link]

Read hi-vibe's real implementation, not just what the README claims, and assess:

1. Whether it helps find existing implementations and avoid duplicate work
2. What the automatic post-change review would realistically catch here
3. How useful cross-session context and troubleshooting records would be
4. Whether this project is large or structured enough to need the repo-wide check
5. What overlaps with tools or habits I already use
6. The concrete benefits and limits I should expect in this project

Cite specific files or code from my project wherever you can. If you could not verify something, say so rather than guessing.

Finish with a short summary:

- The feature likely to be most useful
- Features I probably don't need
- Whether you'd recommend installing it here, and why
```

# 설치 전 적합성 평가 프롬프트 (내부 보관)

랜딩 페이지에서 뺀 것(v0.28.0). 방문자가 hi-vibe를 이해하기도 전에
다른 AI에게 보내는 자리라 흐름을 끊었다. 공개 소개에는 없지만,
**외부 평가를 받고 싶을 때 그대로 복사해 쓰라고** 남겨둔다.

실제로 이 프롬프트로 코덱스 평가를 여러 번 받았고, 거기서 나온 지적이
v0.22~v0.27의 상당수를 만들었다 (.env 구멍, 삭제 파일 리뷰 누락,
리뷰의 스코프 크립 등).

## 한국어

```text
https://github.com/jx-hxxx/hi-vibe

hi-vibe는 개인 개발자가 Claude Code에서 사용하는 개인용 플러그인입니다.
제 프로젝트에 hi-vibe가 실질적인 도움이 되는지 중심으로 평가해 주세요.

제 저장소(가능하면 실제 코드를 확인해 주세요): [내 프로젝트 GitHub 링크 — 공개 저장소면 실제 코드를 스캔해 제 프로젝트에서 hi-vibe가 무엇을 찾아주는지 구체적으로 봐 주세요]

평가할 때 README가 약속한 범위가 실제 구현에서 얼마나 충실하게 제공되는지를 중심으로 판단해 주세요.
확인된 장점과 한계, 제 프로젝트 같은 핵심 타깃에게 실제로 도움이 되는 부분을 구분해서 설명해 주세요.

다음을 평가해 주세요.
1. 바이브 코딩에 주는 도움
2. 제품·기술 설계
3. 제 프로젝트와의 적합성, 덜 맞는 사용자
4. 주요 장점과 한계
5. 테스트·자동화 신뢰도
6. 현재 완성도

- 제 프로젝트 기준 설치 가치: /10
- 개인용 Claude Code 플러그인으로서 현재 성숙도: /10
- 종합점수: /10

확인한 실제 구현에 근거해 공정하게 평가하고, 직접 확인하지 못한 내용은 확인 불가라고 밝혀 주세요.
```

## English

```text
https://github.com/jx-hxxx/hi-vibe

hi-vibe is a personal plugin an individual developer uses inside Claude Code.
Please judge it centered on whether hi-vibe actually helps MY project.

My repo (please inspect the real code if you can): [my project's GitHub link — if public, scan the real code and spell out concretely what hi-vibe finds in my project]

Judge how faithfully the scope the README promises is actually delivered in the real implementation.
Separate the confirmed strengths from the limits, and spell out what actually helps a core target like my project.

Evaluate:
1. Help for vibe coding
2. Product / technical design
3. Fit with my project, and who it fits less
4. Key strengths and limits
5. Test / automation reliability
6. Current maturity

- Install value for my project: /10
- Current maturity as a personal Claude Code plugin: /10
- Overall: /10

Judge fairly based on the actual implementation you verified, and say so for anything you couldn't verify directly.
```

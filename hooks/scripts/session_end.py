"""SessionEnd: `/clear`로 컨텍스트를 통째로 버리거나 창을 닫고 나갈 때
handover.md에 자동 항목을 남긴다.

이게 없던 동안 **자동 기록은 compact 직전 하나뿐**이었다. 그런데 `/clear`는
대화를 요약해 이어가는 게 아니라 통째로 버리는 것이라, 정작 기록이 제일
필요한 쪽인데 아무것도 안 남았다. Anthropic 공식 권장이 "관련 없는 작업
사이에는 `/clear`"이므로, **권장대로 쓰는 사람일수록 더 많이 잃는** 구조였다.

PreCompact와 다른 점 둘:

  1. **건질 게 없으면 아무것도 안 쓴다.** compact은 대화가 길어야 일어나지만
     `/clear`는 열자마자 칠 수도 있다. 그대로 남기면 빈 항목만 쌓인다.
     활동 판정에 **Git 상태는 넣지 않는다** — git 저장소에서는 늘 값이 있어
     모든 빈 세션이 "활동 있음"이 된다.
  2. **같은 세션에서 똑같은 내용이면 건너뛴다.** `/compact` 하고 바로
     `/clear`를 치는 흐름이 흔한데, 그때 같은 내용이 두 번 들어간다.
     비교는 **개수가 아니라 본문 서명**으로 한다 — 개수로 비교하면 같은
     파일 재수정·Bash 수정·"파일은 안 건드린 중요한 논의"가 통째로 사라진다.

SessionEnd는 무엇도 막지 못한다(exit 2도 stderr만 보인다). 나가는 길을
붙잡을 수 없다는 뜻이라 fail-open 원칙과 어긋나지 않는다. 다만 **훅 전체가
1.5초 예산을 나눠 쓰므로** 여기서 무거운 일을 하면 안 된다 — 지금 하는 일은
트랜스크립트 파싱과 파일 한 줄 쓰기뿐이다.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

# 왜 끝났는지에 따라 사람이 읽을 제목이 달라진다. `other`는 안 받는다 —
# 어떤 경우인지 문서에 안 나와 있어 제목을 정할 수 없다.
REASON_LABEL = {
    "clear": "/clear 직전",
    "prompt_input_exit": "세션 종료",
    "resume": "다른 곳에서 이어받기 직전",
    "logout": "로그아웃 직전",
}


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    _common.touch_heartbeat(cwd, "SessionEnd")
    transcript = payload.get("transcript_path", "")
    sid = payload.get("session_id", "")

    # Git 조회는 0.3초로 묶는다 — SessionEnd는 훅 전체가 1.5초 예산을
    # 나눠 쓰므로, 느린 저장소에서 기본 3초를 기다리면 handover를 쓰기도
    # 전에 죽는다. Git은 부가정보라 못 얻어도 기록은 남는 편이 낫다.
    body, active, sig = _common.handover_body(cwd, transcript, git_timeout=0.3)
    if not active:
        return  # 빈 세션 — 남길 게 없으면 조용히 넘어간다
    if _common.handover_already_written(cwd, sid, sig):
        return  # 방금 compact이 똑같은 내용을 남겼다

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    reason = payload.get("reason", "other")
    label = REASON_LABEL.get(reason, "세션 종료")
    lines = [f"## {now} ({label}, session {str(sid)[:8]})", ""]
    lines += body
    lines += ["", f"⚠️ 자동 생성({label}) — 다음 세션에서 이 항목을 다듬어 주세요."]

    handover = os.path.join(cwd, "handover.md")
    with _common.file_lock(handover):
        _common.prepend_entry(handover, "\n".join(lines))
        _common.rotate(handover)
    _common.note_handover_written(cwd, sid, sig)


if __name__ == "__main__":
    _common.run(main)

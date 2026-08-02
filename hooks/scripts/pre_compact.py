"""PreCompact: compact 직전, 트랜스크립트를 파싱해 handover.md에
자동 항목을 확정적으로 기록한다 (모델 의존 없음). 절대 compact를
막지 않는다 — 어떤 경우에도 exit 0.

항목 형식은 `_common.handover_body`가 한 벌로 갖고 있다 — SessionEnd와
같은 모양이어야 하므로 여기서 다시 만들지 않는다.
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    _common.touch_heartbeat(cwd, "PreCompact")
    transcript = payload.get("transcript_path", "")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    trigger = payload.get("trigger", "auto")
    sid = str(payload.get("session_id", ""))[:8]

    body, found, n_edited = _common.handover_body(cwd, transcript)
    lines = [f"## {now} ({trigger} compact 직전, session {sid})", ""]
    lines += body
    # compact은 대화가 길어야 일어난다 — 건질 게 없으면 왜 비었는지라도
    # 남기는 편이 낫다. (SessionEnd는 반대로 조용히 넘어간다.)
    if not found:
        lines.append("- (트랜스크립트에서 추출된 내용 없음)")
    lines += ["", f"⚠️ 자동 생성({trigger} compact) — 세션이 이어지면 이 항목을 다듬어 주세요."]

    handover = os.path.join(cwd, "handover.md")
    with _common.file_lock(handover):
        _common.prepend_entry(handover, "\n".join(lines))
        _common.rotate(handover)
    _common.note_handover_written(cwd, payload.get("session_id", ""), n_edited)


if __name__ == "__main__":
    _common.run(main)

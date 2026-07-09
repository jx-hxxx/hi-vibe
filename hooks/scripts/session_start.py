"""SessionStart: 세션이 시작되거나 compact 직후에 가장 최근 handover
항목과 vibe-check 규율 한 줄을 컨텍스트로 주입한다. 주입량은 작게
유지한다 (프롬프트 비대화 방지).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


CHARTER = (
    "vibe-check 규율: 에러는 fallback으로 가리지 말고 원인부터. "
    "근거 없는 수치 단정 금지. 새 함수를 만들기 전에 기존 것부터 검색"
    "(/vibe-check:pre-write). 구조가 바뀌면 MODULE.md와 CLAUDE.md 지도 동기화."
)


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    source = payload.get("source", "startup")
    handover = os.path.join(cwd, "handover.md")

    if source == "compact":
        entry = _common.latest_entry(handover, max_chars=1200)
        ctx = (
            "방금 컨텍스트 압축(compact) 직전에 handover.md에 자동 항목이 "
            "추가되었습니다. 아래 항목을 확인하고, 이 세션에서 알고 있는 "
            "맥락으로 한 번 다듬은 뒤(타임스탬프 유지, '(다듬음)' 표시) "
            "진행 중이던 작업을 이어가세요.\n\n" + entry
        )
        _common.emit("SessionStart", additional_context=ctx[:1500])
    elif source in ("startup", "resume"):
        entry = _common.latest_entry(handover, max_chars=400)
        parts = [CHARTER]
        if entry:
            head = "\n".join(entry.splitlines()[:4])
            parts.append("직전 인수인계(handover.md 최신 항목):\n" + head)
        _common.emit("SessionStart", additional_context="\n\n".join(parts)[:800])


if __name__ == "__main__":
    _common.run(main)

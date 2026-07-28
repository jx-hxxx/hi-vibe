"""SessionStart: 세션이 시작되거나 compact 직후에 가장 최근 handover
항목과 hi-vibe 규율 한 줄을 컨텍스트로 주입한다. 주입량은 작게
유지한다 (프롬프트 비대화 방지).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


CHARTER = (
    "hi-vibe 규율: 에러는 fallback으로 가리지 말고 원인부터. "
    "근거 없는 수치 단정 금지. 새 함수를 만들기 전에 기존 것부터 검색"
    "(/hi-vibe:find). 구조가 바뀌면 MODULE.md와 CLAUDE.md 지도 동기화. "
    "컨텍스트가 길어지면 여유 있을 때 사용자에게 /compact를 권하라 — 직전에 "
    "handover가 자동 기록되니 맥락이 안 끊긴다."
)


# 1회 실패는 흔하다(일시적 장애·재시도). 연속 2회부터가 "관문이 죽었다"에
# 가깝다 — 잔소리로 만들지 않으려는 하한.
CI_FAILURE_THRESHOLD = 2


def _ci_warning(ci):
    """관문이 열려 있다는 사실을 사용자에게 먼저 알리게 한다.

    깨진 CI는 "빨간불"이 아니라 **검사가 아예 안 돌고 있는 상태**다. 그걸
    모르고 며칠 더 밀어넣는 게 진짜 손해이므로, 세션 첫머리에서 알린다."""
    last = f"마지막 성공 {ci['last_success']}" if ci["last_success"] else "최근 성공 기록 없음"
    name = ci["workflow"] or "CI"
    return (
        f"⚠️ 이 저장소의 `{name}`가 `{ci['branch']}`에서 {ci['failures']}번 연속 "
        f"실패 중입니다 ({last}). 검사가 통과한 게 아니라 **아예 안 돌고 있는** "
        "상태일 수 있습니다. 사용자에게 이 사실을 먼저 한 줄로 알리고, 고칠지 "
        "물어보세요 (`gh run view --log-failed`로 원인 확인)."
    )


def _suggest_gate_once(cwd):
    """CI 가드를 켤 수 있게 됐다고 딱 한 번만 알린다.

    한 번 말하고 플래그를 남긴다 — 매 세션 반복하면 잔소리가 되고, 잔소리는
    무시된다. 깔아주지는 않는다: 설정 파일을 쓰는 건 사용자가 정한다."""
    if not _common.ci_guard_missing(cwd):
        return False
    flag = os.path.join(cwd, ".hi-vibe", "state", "gate_suggested")
    if os.path.isfile(flag):
        return False
    try:
        os.makedirs(os.path.dirname(flag), exist_ok=True)
        with open(flag, "w", encoding="utf-8") as f:
            f.write("suggested\n")
    except OSError:
        return False   # 기록 못 하면 알리지 않는다 — 매번 반복하느니 침묵
    return True


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    _common.touch_heartbeat(cwd, "SessionStart")
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
    elif source in ("startup", "resume", "clear"):
        # clear = 컨텍스트를 통째로 비운 직후 → handover 재주입이 가장 필요한
        # 순간이므로 startup과 동일하게 규율+최신 인수인계를 다시 넣는다.
        entry = _common.latest_entry(handover, max_chars=400)
        parts = ["이 세션은 hi-vibe가 켜져 있습니다. 사용자에게 첫 응답을 "
                 "👋로 가볍게 인사하며 시작하세요.", CHARTER]
        if entry:
            head = "\n".join(entry.splitlines()[:4])
            parts.append("직전 인수인계(handover.md 최신 항목):\n" + head)
        ci = _common.ci_health(cwd)
        if ci and ci["failures"] >= CI_FAILURE_THRESHOLD:
            parts.append(_ci_warning(ci))
        elif _suggest_gate_once(cwd):
            parts.append(
                "이 프로젝트가 GitHub에 연결돼 있는데 hi-vibe CI 가드가 "
                "없습니다. 사용자에게 **한 줄로만** 알리세요: `/hi-vibe:gate`로 "
                "푸시할 때마다 자동 검사(복잡도·타입·순환 의존)를 켤 수 있다고. "
                "**켜라고 밀지 말고**, 이미 만든 코드가 많으면 위반이 쏟아질 수 "
                "있다는 것도 같이 짚으세요. 이 안내는 한 번만 나갑니다."
            )
        _common.emit("SessionStart", additional_context="\n\n".join(parts)[:1100])


if __name__ == "__main__":
    _common.run(main)

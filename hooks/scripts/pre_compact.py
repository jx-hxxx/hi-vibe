"""PreCompact: compact 직전, 트랜스크립트를 파싱해 handover.md에
자동 항목을 확정적으로 기록한다 (모델 의존 없음). 절대 compact를
막지 않는다 — 어떤 경우에도 exit 0.
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
    transcript = payload.get("transcript_path", "")
    prompts, edited = _common.parse_transcript(transcript) if transcript else ([], [])
    git = _common.git_status(cwd)
    test = _common.last_test_result(transcript) if transcript else None

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    trigger = payload.get("trigger", "auto")
    sid = str(payload.get("session_id", ""))[:8]

    lines = [f"## {now} ({trigger} compact 직전, session {sid})", ""]
    # 다음 세션이 재개할 수 있는 객관적 상태(있을 때만 — fail-open)
    if git:
        lines.append(f"- Git: {git}")
    if test:
        cmd, res = test
        lines.append(f"- 최근 검증: `{cmd}` → {res}")
    if prompts:
        lines.append("- 사용자 요청(최근):")
        lines += [f"  - {p}" for p in prompts]
    if edited:
        lines.append("- 수정 파일:")
        lines += [f"  - `{fp}`" for fp in edited[:15]]
        if len(edited) > 15:
            lines.append(f"  - …외 {len(edited) - 15}개")
    if not prompts and not edited and not git and not test:
        lines.append("- (트랜스크립트에서 추출된 내용 없음)")
    lines += ["", f"⚠️ 자동 생성({trigger} compact) — 세션이 이어지면 이 항목을 다듬어 주세요."]

    handover = os.path.join(cwd, "handover.md")
    with _common.file_lock(handover):
        _common.prepend_entry(handover, "\n".join(lines))
        _common.rotate(handover)


if __name__ == "__main__":
    _common.run(main)

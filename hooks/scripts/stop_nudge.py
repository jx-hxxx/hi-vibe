"""Stop: 이번 세션에 실질 코드 변경이 있었는데 CHANGELOG.md가 안
갱신됐으면 사용자에게 한 번만 알린다. 절대 턴을 막지(block) 않는다 —
잔소리 훅은 플러그인 삭제로 이어지는 지름길이다.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

DOC_SUFFIXES = (".md", ".txt", ".rst")
MAX_FLAGS = 200  # 세션당 1개씩 쌓이는 .nudged 플래그의 상한


def _prune_flags(flag_dir):
    """오래된 .nudged 플래그를 상한 이하로 정리 (무한 누적 방지)."""
    try:
        flags = [os.path.join(flag_dir, f) for f in os.listdir(flag_dir)
                 if f.endswith(".nudged")]
        if len(flags) <= MAX_FLAGS:
            return
        flags.sort(key=os.path.getmtime)  # 오래된 것부터
        for old in flags[:len(flags) - MAX_FLAGS]:
            os.remove(old)
    except OSError:
        pass  # best-effort 청소 — 실패해도 훅 동작에 영향 없음


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    sid = str(payload.get("session_id", "unknown"))
    flag_dir = os.path.join(cwd, ".hi-vibe", "state")
    flag = os.path.join(flag_dir, f"{sid}.nudged")
    if os.path.isfile(flag):
        return

    transcript = payload.get("transcript_path", "")
    if not transcript:
        return
    _, edited = _common.parse_transcript(transcript)
    code_edits = [f for f in edited if not f.endswith(DOC_SUFFIXES)]
    changelog_touched = any(os.path.basename(f) == "CHANGELOG.md" for f in edited)
    if not code_edits or changelog_touched:
        return

    os.makedirs(flag_dir, exist_ok=True)
    with open(flag, "w", encoding="utf-8") as f:
        f.write("nudged\n")
    _prune_flags(flag_dir)
    _common.emit(
        "Stop",
        system_message=(
            "hi-vibe: 이번 세션에 코드 변경이 있었어요. 실질 변경이면 "
            "/hi-vibe:log 로 CHANGELOG에 남기고, /hi-vibe:review --all "
            "(\"전체 리뷰해줘\")로 이번 작업 전체를 품질·문서까지 점검받을 수 "
            "있어요 — 이미 본 건 건너뜁니다. 세션당 1회 · 사소하면 무시 OK.\n"
            "— You changed code this session. Log it with /hi-vibe:log, and run "
            "/hi-vibe:review --all to review the whole session at once "
            "(already-reviewed files are skipped). Once per session; "
            "ignore if trivial."
        ),
    )


if __name__ == "__main__":
    _common.run(main)

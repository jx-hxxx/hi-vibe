"""Stop: 아직 리뷰 안 받은 코드 변경이 있으면 턴을 막고 리뷰를 지시한다.

   막는 것까지가 이 훅의 일이고 리뷰를 수행하는 건 Claude다. 이 구분이
   흐려진 문장이 여기서 문서로 여러 번 새어 나갔다.

예전엔 "리뷰하세요" 안내만 띄웠다. 안내는 무시된다 — 사용자는 기능을 만들
때마다 명령어를 치지 않고, 애초에 코드를 쓰는 건 에이전트이기 때문이다.
그래서 안내를 강제로 바꿨다(decision: block).

"잔소리 훅은 플러그인 삭제로 이어진다"는 원래 우려는 유효하므로, 막는
조건을 좁게 지킨다:

  - 코드를 안 건드린 턴에는 아예 안 걸린다
  - 같은 변경으로는 두 번 막지 않는다 (내용 지문으로 판단)
  - 리뷰가 끝나 mark되면 자동으로 조용해진다
  - 범위 계산이 조금이라도 실패하면 막지 않는다 (fail-open)
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

DOC_SUFFIXES = (".md", ".txt", ".rst")
MAX_FLAGS = 200  # 세션당 1개씩 쌓이는 .nudged 플래그의 상한
SCOPE_TIMEOUT = 8  # 훅 자체 제한(10초)보다 짧게 — 넘기면 막지 않고 통과

REVIEW_SCOPE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "skills", "write-gate", "scripts", "review_scope.py")


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


def review_scope(cwd):
    """review_scope list 결과(dict). 어떤 실패에서도 None → 막지 않는다."""
    if not os.path.isfile(REVIEW_SCOPE):
        return None
    try:
        r = subprocess.run([sys.executable or "python3", REVIEW_SCOPE,
                            "list", "--root", cwd],
                           capture_output=True, text=True, timeout=SCOPE_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def _block_flag(flag_dir):
    return os.path.join(flag_dir, "last_block")


def _already_blocked(flag_dir, fingerprint):
    """같은 내용으로 이미 막은 적이 있나 — 한 번 넘긴 변경으로 또 막지 않는다."""
    try:
        with open(_block_flag(flag_dir), encoding="utf-8") as fh:
            return fh.read().strip() == fingerprint
    except OSError:
        return False


def _remember_block(flag_dir, fingerprint):
    try:
        os.makedirs(flag_dir, exist_ok=True)
        with open(_block_flag(flag_dir), "w", encoding="utf-8") as fh:
            fh.write(fingerprint + "\n")
    except OSError:
        pass  # 기록 못 해도 막는 것 자체는 유효 — 다음 턴에 한 번 더 걸릴 뿐


def review_reason(scope):
    """차단 사유 = 에이전트가 받을 지시. 무엇을·왜·어떻게 끝내는지까지 담는다."""
    files = scope.get("to_review", [])
    gone = scope.get("deleted", [])
    shown = ", ".join(files[:8]) if files else "(수정된 파일 없음)"
    more = "" if len(files) <= 8 else f" 외 {len(files) - 8}개"
    deleted_line = ""
    if gone:
        # 지운 파일은 열어볼 수 없다 — 남은 호출부가 진짜 위험이다.
        deleted_line = ("삭제된 코드 파일: " + ", ".join(gone[:8]) +
                        ("" if len(gone) <= 8 else f" 외 {len(gone) - 8}개") +
                        ". 이 파일들을 부르던 곳이 남아 있는지 반드시 확인하세요.\n")
    return (
        "hi-vibe: 아직 리뷰 안 받은 코드 변경이 있습니다 "
        f"({scope.get('scope_label', '')}, {scope.get('file_count', 0)}파일 "
        f"{scope.get('total_changed_lines', 0)}줄): {shown}{more}.\n"
        + deleted_line
        + "지금 write-gate 스킬의 `Mode: review`를 그대로 수행하세요 "
        "(범위 계산 → 체크리스트 → fresh-eyes → mark).\n"
        "리뷰를 마치면 review_scope.py mark 로 표시해야 이 알림이 멈춥니다.\n"
        "단, 사용자가 방금 '넘어가'/'나중에'/'가볍게'라고 했으면 그 뜻을 "
        "따르세요 — 같은 변경으로는 다시 막지 않습니다."
    )


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    _common.touch_heartbeat(cwd, "Stop")
    transcript = payload.get("transcript_path", "")
    if not transcript:
        return

    # 리뷰가 돌 때 **fresh-eyes까지 같이 도는지**를 기록해 둔다. 여기서 세는
    # 이유는 훅만이 트랜스크립트를 볼 수 있어서다 — `review_scope mark`는
    # AI가 Bash로 부르는 별도 프로세스라 대화 기록에 접근하지 못한다.
    sid = str(payload.get("session_id", "unknown"))
    off = _common.agent_offset(cwd, sid)
    fe, mk, off2 = _common.review_activity(transcript, off)
    _common.note_agent_activity(cwd, sid, fe, mk, off2)

    _, edited = _common.parse_transcript(transcript)
    writes, catches = _common.session_activity(transcript)
    code_edits = [f for f in edited if not f.endswith(DOC_SUFFIXES)]
    flag_dir = os.path.join(cwd, ".hi-vibe", "state")

    # 1) 리뷰 안 받은 코드 변경이 있으면 → 안내가 아니라 실행으로 넘긴다.
    #    이 세션에 실제로 코드를 썼을 때만 — 남이 남긴 오래된 변경으로
    #    남의 세션을 붙잡지 않는다.
    #
    #    Bash도 함께 본다: heredoc·`sed -i`·생성 스크립트로 쓴 파일은
    #    Write/Edit 목록에 안 남아서, 예전엔 그런 턴이 통째로 "코드 안 건드림"
    #    으로 지나갔다 (리뷰도, 삼킨 에러·비밀키 감지도 전부 건너뜀).
    if code_edits or _common.bash_wrote_files(transcript):
        scope = review_scope(cwd)
        if scope and (scope.get("to_review") or scope.get("deleted")):
            fingerprint = scope.get("fingerprint") or ""
            if fingerprint and not _already_blocked(flag_dir, fingerprint):
                _remember_block(flag_dir, fingerprint)
                _common.emit("Stop", decision="block",
                             reason=review_reason(scope))
                return

    # 2) 막을 게 없을 때만, 살아있음 요약을 세션당 한 번 남긴다.
    #    잡은 게 0건이어도 "검사 N회"로 조용히 돌고 있었음을 증명한다.
    if writes <= 0:
        return
    sid = str(payload.get("session_id", "unknown"))
    flag = os.path.join(flag_dir, f"{sid}.nudged")
    if os.path.isfile(flag):
        return
    if catches > 0:
        summary = (f"hi-vibe 이번 세션: 코드쓰기 {writes}회 검사 · 👋 {catches}건 잡음.\n"
                   f"— This session: hi-vibe checked {writes} code write(s), "
                   f"caught {catches}.")
    else:
        summary = (f"hi-vibe 이번 세션: 코드쓰기 {writes}회 검사 · 위험 패턴 0건(깨끗).\n"
                   f"— This session: hi-vibe checked {writes} code write(s), "
                   f"0 risky patterns.")
    os.makedirs(flag_dir, exist_ok=True)
    with open(flag, "w", encoding="utf-8") as f:
        f.write("nudged\n")
    _prune_flags(flag_dir)
    _common.emit("Stop", system_message=summary + "\n세션당 1회 · once per session.")


if __name__ == "__main__":
    _common.run(main)

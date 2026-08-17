"""Stop: 리뷰가 안 끝난 채로 턴이 끝나려 하면 막고 리뷰를 지시한다.

   막는 사유는 둘이다:
     1) 아직 리뷰 안 받은 코드 변경이 남아 있다
     2) 리뷰를 끝냈다고 표시(mark)했는데 **fresh-eyes는 안 돌았다**

   2)가 있는 이유: 1)만 있을 때는 mark가 잠금을 푸는 유일한 열쇠였다. 즉
   체크리스트만 돌리고 표시해도 훅은 만족했고, 남의 눈을 부르라는 지시는
   `.md` 문장 하나뿐이었다. 그 층이 조용히 빠지는 걸 이미 겪었다(2026-08-07).
   세고만 있던 숫자를 판단에 넣은 것이 2)다.

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

# fresh-eyes 없이 리뷰를 끝냈다고 표시했을 때 **몇 개 파일부터 막을 것인가.**
# 2인 이유는 임의의 값이 아니다: fresh-eyes 1번 항목이 "고친 파일을 가리키는
# 다른 파일이 같이 바뀌었나"인데, 그 어긋남은 **파일이 둘 이상일 때만 존재**
# 한다. 한 파일짜리 변경은 계속 write-gate의 판단에 맡긴다(기계로 안 막는다).
FRESH_EYES_MIN_FILES = 2

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


def _block_flag(flag_dir, name="last_block"):
    return os.path.join(flag_dir, name)


def _already_blocked(flag_dir, fingerprint, name="last_block"):
    """같은 내용으로 이미 막은 적이 있나 — 한 번 넘긴 변경으로 또 막지 않는다.

    사유마다 파일을 따로 쓴다. 한 파일을 돌려쓰면 뒤에 막은 사유가 앞의
    기억을 덮어써서, 같은 변경에 두 번 걸리게 된다."""
    try:
        with open(_block_flag(flag_dir, name), encoding="utf-8") as fh:
            return fh.read().strip() == fingerprint
    except OSError:
        return False


def _remember_block(flag_dir, fingerprint, name="last_block"):
    try:
        os.makedirs(flag_dir, exist_ok=True)
        with open(_block_flag(flag_dir, name), "w", encoding="utf-8") as fh:
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


def fresh_eyes_reason(files):
    """리뷰를 마쳤다고 표시했는데 fresh-eyes가 안 돈 경우의 지시."""
    shown = ", ".join(files[:8])
    more = "" if len(files) <= 8 else f" 외 {len(files) - 8}개"
    return (
        f"hi-vibe: 방금 리뷰 완료로 표시한 {len(files)}개 파일({shown}{more})에 "
        "**fresh-eyes가 안 돌았습니다.** 체크리스트만 돌고 설계 검토는 빠진 "
        "상태입니다 — 리뷰는 두 겹인데 뒤쪽 절반이 없습니다.\n"
        "지금 fresh-eyes 에이전트를 소환하세요(Agent 도구, subagent_type "
        "`hi-vibe:fresh-eyes`). 전달할 것은 ①사용자의 원래 요구사항 한 줄 "
        "②이번에 바꾼 파일 목록뿐입니다 — **설계 이유나 변명은 전달하지 "
        "마세요.** 작성자의 착각을 물려주면 깨끗한 눈이 사라집니다.\n"
        "돌고 나면 review_scope.py mark 를 같은 파일들로 한 번 더 실행하세요 "
        "(표시는 여러 번 해도 안전하고, 그래야 다음 리뷰가 이 실행분을 "
        "당겨쓰지 않습니다).\n"
        "이 판정은 AI 신고가 아니라 대화 기록을 훅이 직접 세어 나온 것입니다. "
        "단, Agent 호출이 **실제로 실패**하거나 사용자가 '넘어가'라고 했으면 "
        "그 사실을 한 줄로 밝히고 진행하세요 — 같은 파일로는 다시 막지 않습니다."
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
    fe, mk, off2, marked = _common.review_activity(transcript, off)
    fresh_eyes_skipped = _common.note_agent_activity(cwd, sid, fe, mk, off2)

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

    # 2) 리뷰를 끝냈다고 **표시했는데 fresh-eyes는 안 돈** 경우.
    #    1)만 있을 때는 표시(mark)가 잠금을 푸는 유일한 열쇠였다 — 즉
    #    체크리스트만 돌리고 표시해도 훅은 만족했고, 남의 눈을 부르라는
    #    지시는 `.md` 문장 하나뿐이었다. 그 층이 조용히 빠지는 걸 이미
    #    겪었으므로(2026-08-07) 세고만 있던 숫자를 판단에 넣는다.
    #
    #    파일 2개 이상일 때만 막는다 (FRESH_EYES_MIN_FILES 주석 참고).
    #    "표시했는데 안 돌았다"는 사실 자체가 새 mark가 있을 때만 생기므로,
    #    사용자가 넘어가라고 해서 그냥 멈추면 다음 턴엔 안 걸린다.
    #    같은 파일을 두 번 표시한 것을 두 파일로 세면 안 된다 — 한 파일짜리
    #    리뷰를 재시도한 것뿐인데 문턱을 넘어버린다. 중복을 먼저 접는다.
    files = sorted(set(marked))
    if fresh_eyes_skipped and len(files) >= FRESH_EYES_MIN_FILES:
        fingerprint = "fe:" + "|".join(files)
        if not _already_blocked(flag_dir, fingerprint, "last_fe_block"):
            _remember_block(flag_dir, fingerprint, "last_fe_block")
            _common.emit("Stop", decision="block",
                         reason=fresh_eyes_reason(files))
            return

    # 3) 막을 게 없을 때만, 살아있음 요약을 세션당 한 번 남긴다.
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

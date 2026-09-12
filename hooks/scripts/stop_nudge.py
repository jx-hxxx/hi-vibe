"""Stop: 리뷰가 안 끝난 채로 턴이 끝나려 하면 막고 리뷰를 지시한다.

   막는 사유는 하나다: **아직 리뷰(체크리스트) 안 받은 코드 변경이 남아 있다.**

   예전엔 "mark했는데 fresh-eyes는 안 돌았다"도 여기서 막았다. 그 강제는
   2026-09-13에 `pre_commit_gate.py`(커밋 직전)로 옮겼다 — 턴마다 걸리는 자리에
   두면 **리뷰가 파일을 고쳐 다음 차단을 스스로 만드는 고리**가 생긴다(실측
   2시간 세션 5회). 이 훅은 싼 검사(체크리스트)만 세우고, 비싼 서브에이전트
   검토는 사용자가 "커밋해줘"라고 말한 지점에서 한 번 선다.

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
MAX_FLAGS = 200  # 세션당 1개씩 쌓이는 세션 플래그(.nudged·.blocked)의 상한
SCOPE_TIMEOUT = 8  # 훅 자체 제한(10초)보다 짧게 — 넘기면 막지 않고 통과

REVIEW_SCOPE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "skills", "write-gate", "scripts", "review_scope.py")


def _prune_flags(flag_dir):
    """오래된 세션 플래그를 상한 이하로 정리 (무한 누적 방지).

    확장자를 늘릴 땐 여기 목록도 같이 늘려야 한다 — `.blocked`를 만들 때
    이 자리를 빠뜨려서 한쪽만 무한히 쌓일 뻔했다."""
    try:
        flags = [os.path.join(flag_dir, f) for f in os.listdir(flag_dir)
                 if f.endswith((".nudged", ".blocked"))]
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


def _session_blocked(flag_dir, sid):
    """이 세션에서 이미 한 번 막았나.

    지문(fingerprint) 중복 방지만으로는 루프를 못 막는다는 것이 실측으로
    드러났다(MoToo 2026-09-12, 2시간 세션에서 **5회** 차단). 이유는 단순하다:
    막으면 리뷰가 돌고, **리뷰가 파일을 고치면 새 변경이 생겨** 지문이 달라진다.
    그래서 "같은 변경으로 두 번 막지 않는다"는 방어가 통째로 무력해진다.
      막힘 → 리뷰 → 리뷰가 수정 → 새 지문 → 또 막힘 → …
    그 세션은 사용자 요청 3건에 서브에이전트 9개 중 7개를 이 고리에서 썼다.

    비싼 절반(fresh-eyes)은 `pre_commit_gate.py`로 옮겼고, 남은 체크리스트도
    같은 고리를 탄다 — 싸긴 하지만 매 턴 붙잡을 이유는 없다. 훅은 '턴이
    끝났다'만 알 뿐 '작업이 끝났다'를 모르므로, 세션당 1회로 예산을 고정한다."""
    return os.path.isfile(os.path.join(flag_dir, f"{sid}.blocked"))


def _remember_session_block(flag_dir, sid):
    try:
        os.makedirs(flag_dir, exist_ok=True)
        open(os.path.join(flag_dir, f"{sid}.blocked"), "w").close()
    except OSError:
        pass          # 못 남겨도 지문 중복 방지가 남는다 — 최악이 예전 동작


def _remember_block(flag_dir, fingerprint):
    try:
        os.makedirs(flag_dir, exist_ok=True)
        with open(_block_flag(flag_dir), "w", encoding="utf-8") as fh:
            fh.write(fingerprint + "\n")
    except OSError:
        pass  # 기록 못 해도 막는 것 자체는 유효 — 다음 턴에 한 번 더 걸릴 뿐


def review_reason(scope):
    """차단 사유 = 에이전트가 받을 지시.

    **짧게 유지한다.** 이 문자열은 모델에게만 가는 게 아니라 사용자 터미널에
    그대로 찍힌다 — 절차를 여기 다 옮겨 적으면 매 턴 화면을 덮는다. 절차의
    유일본은 `write-gate/SKILL.md`의 `Mode: review`이고, 여기서는 무엇이·
    어떻게 멈추는지·빠져나가는 길만 말한다."""
    files = scope.get("to_review", [])
    gone = scope.get("deleted", [])
    shown = ", ".join(files[:5]) if files else "(수정된 파일 없음)"
    more = "" if len(files) <= 5 else f" 외 {len(files) - 5}개"
    deleted_line = ""
    if gone:
        # 지운 파일은 열어볼 수 없다 — 남은 호출부가 진짜 위험이다.
        deleted_line = ("삭제됨: " + ", ".join(gone[:5]) +
                        ("" if len(gone) <= 5 else f" 외 {len(gone) - 5}개") +
                        " — 남은 호출부 확인.\n")
    return (
        f"hi-vibe: 리뷰 안 받은 코드 변경 {scope.get('file_count', 0)}파일 "
        f"{scope.get('total_changed_lines', 0)}줄"
        f"({scope.get('scope_label', '')}): {shown}{more}.\n"
        + deleted_line
        + "write-gate `Mode: review` 수행 → 끝나면 `review_scope.py mark`. "
        "사용자가 '넘어가'/'나중에'라고 했으면 그 뜻을 따르세요."
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
    fe, mk, off2, _ = _common.review_activity(transcript, off)
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
            if (fingerprint and not _already_blocked(flag_dir, fingerprint)
                    and not _session_blocked(flag_dir, sid)):
                _remember_block(flag_dir, fingerprint)
                _remember_session_block(flag_dir, sid)
                _common.emit("Stop", decision="block",
                             reason=review_reason(scope))
                return

    # fresh-eyes(설계 검토) 강제는 여기 없다 — `pre_commit_gate.py`가 커밋
    # 직전에 세운다. 세는 일은 계속 한다(`note_agent_activity`): doctor가
    # "리뷰는 도는데 에이전트만 안 돈다"를 보려면 그 숫자가 필요하다.
    # 2) 막을 게 없을 때만, 살아있음 요약을 세션당 한 번 남긴다.
    #    잡은 게 0건이어도 "검사 N회"로 조용히 돌고 있었음을 증명한다.
    if writes <= 0:
        return
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

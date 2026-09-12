"""PreToolUse: `git commit` 직전에 fresh-eyes(설계 검토)를 세운다.

왜 여기인가 — **"구현이 끝났다"를 훅이 알 수 있는 유일한 지점이기 때문이다.**
Stop 훅은 '턴이 끝났다'만 알고 '작업이 끝났다'는 모른다. 그래서 fresh-eyes를
Stop에 걸어 두면 자기참조 고리가 생겼다(2026-09-12 실측, 2시간 세션에서 5회):

    구현 → 차단 → fresh-eyes → **리뷰가 파일을 고침** → 내용이 달라짐
         → 또 차단 → fresh-eyes → …

리뷰가 자기 일을 해낼수록 다음 차단의 조건을 스스로 만든다. 내용 지문으로
"같은 변경은 두 번 막지 않기"를 해도 소용이 없다 — 지문도 내용에서 나온다.
사용자가 "커밋해줘"라고 말한 시점은 사용자가 직접 찍는 작업의 끝이라, 근사할
필요가 없고 고리도 원리적으로 생기지 않는다(커밋 시도는 한 번이다).

범위도 여기서 정확해진다: 미커밋 전체가 아니라 **staged 파일만** 본다.

계약 차이에 주의 — Stop의 `decision="block"`은 턴을 못 끝내게 하고, 여기서
쓰는 PreToolUse deny는 **그 도구 호출을 취소한다**. 커밋은 일어나지 않는다.

체크리스트는 여기로 안 옮겼다. 그쪽은 메인 세션이 직접 읽는 것이라 싸고,
매 턴 도는 편이 낫다(Stop 훅이 계속 담당한다). 비싼 것은 fresh-eyes 하나다.

막는 조건을 좁게 지킨다:
  - `.hi-vibe/`가 없으면 아예 안 걸린다 (project_gate)
  - stage된 **코드 파일**이 없으면 안 걸린다 (문서만 커밋하는 경우)
  - fresh-eyes가 이미 돌았으면 안 걸린다
  - **한 커밋 경계에서 한 번만 막는다** — 에이전트 호출이 실제로 막힌 환경
    (Agent 도구 금지 세션을 겪었다, 2026-08-07)에서 커밋이 영구히 불가능해
    지면 안 된다. 못 막는 것보다 나쁘다.
  - 무엇이 실패해도 통과시킨다 (fail-open)
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

SCOPE_TIMEOUT = 8  # 훅 제한(10초)보다 짧게 — 넘기면 막지 않고 통과

REVIEW_SCOPE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "skills", "write-gate", "scripts", "review_scope.py")

# `git commit`을 **추정한다**. 완전하지 않다 — 별칭(`git ci`)·래퍼 스크립트·
# `eval`로 감싼 것은 빠진다. `_common.bash_wrote_files`와 같은 성격의 근사이며,
# 문서에 "모든 커밋을 검사한다"고 쓰지 말 것.
#   - 줄 시작이나 `;`·`&&`·`||` 뒤만 본다: `echo "git commit"`에 안 걸린다
#   - `git -C dir commit`·`git --no-pager commit`처럼 사이에 옵션이 와도 잡는다.
#     **값을 받는 옵션을 짝으로 먼저** 먹어야 한다 — 안 그러면 `-C`만 소비하고
#     그 값(`.`)에서 멈춘다. 옵션이 아닌 부명령은 안 먹으므로
#     `git config commit.template`은 안 걸린다.
_PAIRED = r"-C|-c|--git-dir|--work-tree|--namespace|--exec-path"
_COMMIT_RE = re.compile(
    r"(?:^|[;&|]\s*|\n\s*)git\s+"
    r"(?:(?:" + _PAIRED + r")\s+\S+\s+|-{1,2}\S+\s+)*commit\b")
# 커밋을 만들지 않는 것들 — 막을 이유가 없다.
_DRY_RE = re.compile(r"--dry-run\b")


def is_git_commit(command):
    return bool(command) and bool(_COMMIT_RE.search(command)) \
        and not _DRY_RE.search(command)


def staged_scope(cwd):
    """review_scope.py staged 결과(dict). 어떤 실패에서도 None → 안 막는다.

    스캐너를 별도 프로세스로 부르는 이유는 stop_nudge와 같다 — 확장자 목록·
    제외 규칙의 유일본이 그 스크립트이고, 여기에 사본을 만들면 조용히 갈린다."""
    if not os.path.isfile(REVIEW_SCOPE):
        return None
    try:
        r = subprocess.run([sys.executable or "python3", REVIEW_SCOPE,
                            "staged", "--root", cwd],
                           capture_output=True, text=True, timeout=SCOPE_TIMEOUT)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def _state_path(cwd):
    return os.path.join(cwd, ".hi-vibe", "state", "commit-gate.json")


def load_state(cwd):
    try:
        with open(_state_path(cwd), encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save_state(cwd, data):
    try:
        os.makedirs(os.path.dirname(_state_path(cwd)), exist_ok=True)
        with open(_state_path(cwd), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, sort_keys=True)
    except OSError:
        pass    # 못 남겨도 커밋은 통과 — 최악이 "다음 커밋에 한 번 더 걸림"


def reason(info):
    """취소 이유 = 에이전트가 받을 지시. **짧게 유지한다** — 이 문자열은
    사용자 터미널에도 그대로 찍힌다(2026-09-11에 사유가 화면을 덮었다).
    절차의 유일본은 `write-gate/SKILL.md`다."""
    files = info.get("files", [])
    shown = ", ".join(files[:5])
    more = "" if len(files) <= 5 else f" 외 {len(files) - 5}개"
    return (
        f"hi-vibe: 커밋 직전 설계 검토가 안 돌았습니다 — staged "
        f"{len(files)}파일 {info.get('total_changed_lines', 0)}줄"
        f": {shown}{more}.\n"
        "Agent 도구로 `hi-vibe:fresh-eyes` 소환 — 전달은 사용자 요구사항 한 "
        "줄과 위 파일 목록뿐(설계 이유·변명은 전달 금지). 지적을 고치고 다시 "
        "stage한 뒤 커밋을 재시도하세요.\n"
        "Agent 호출이 실제로 실패했거나 사용자가 '그냥 커밋해'라고 했으면 한 "
        "줄로 밝히고 그대로 재시도하세요 — 같은 커밋을 두 번 막지 않습니다."
    )


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    if payload.get("tool_name") != "Bash":
        return
    tool_input = payload.get("tool_input") or {}
    if not is_git_commit(tool_input.get("command", "")):
        return

    _common.touch_heartbeat(cwd, "PreToolUse")

    info = staged_scope(cwd)
    if not info or not info.get("files"):
        return          # stage된 코드 파일이 없다 — 문서·설정만 커밋하는 경우

    transcript = payload.get("transcript_path", "")
    if not transcript or not os.path.isfile(transcript):
        return          # 셀 수 없으면 안 막는다

    head = info.get("head", "")
    state = load_state(cwd)
    offset = state.get("offset", 0)
    fresh_eyes, _, next_offset, _ = _common.review_activity(transcript, offset)

    # fresh-eyes가 이미 돌았다 → 통과. 다음 커밋은 **이 지점 이후**만 센다
    # (한 세션에서 커밋을 두 번 하면 두 번째가 첫 번째의 리뷰를 당겨쓰면 안 된다).
    if fresh_eyes > 0:
        save_state(cwd, {"offset": next_offset})
        return

    # 이 커밋 경계에서 이미 한 번 막았다 → 통과시킨다. 위 docstring 참고 —
    # 막을 수 없는 환경에서 커밋이 영구히 불가능해지는 쪽이 더 나쁘다.
    if state.get("denied_head") == head:
        save_state(cwd, {"offset": next_offset})
        return

    save_state(cwd, {"offset": offset, "denied_head": head})
    _common.emit_deny(reason(info))


if __name__ == "__main__":
    _common.run(main)     # fail-open: 어떤 예외도 호스트를 멈추지 않는다

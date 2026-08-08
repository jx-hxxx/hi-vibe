"""CI 건강 상태 — gh CLI로 연속 실패를 감지해 대화창으로 가져온다."""
import json
import os
import subprocess
import time

from _base import _run_git


# ---------- CI 건강 상태 ----------
#
# gate가 CI를 깔아주고 손을 떼면, 그 관문이 죽어도 아무도 모른다. GitHub
# 알림은 쌓이면 신호 역할을 못 하기 때문이다(실제로 47/60 실패가 4일간
# 방치된 적이 있다). 그래서 사용자가 **실제로 있는 자리**(대화창)로 가져온다.
#
# gh CLI는 선택 의존성이다 — 없거나 로그인 안 됐거나 느리면 조용히 생략한다.
# 세션 시작을 붙잡는 것이 CI 상태를 아는 것보다 나쁘다.

CI_CACHE_TTL = 1200      # 20분. 세션마다 네트워크를 때리지 않게.
CI_QUERY_TIMEOUT = 4     # 훅 제한(10초)보다 짧게.


def _ci_cache_path(cwd):
    return os.path.join(cwd, ".hi-vibe", "state", "ci.json")


def _read_ci_cache(cwd):
    try:
        with open(_ci_cache_path(cwd), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    if time.time() - data.get("fetched_at", 0) > CI_CACHE_TTL:
        return None
    return data.get("result")


def _write_ci_cache(cwd, result):
    """캐시는 **이미 init된 프로젝트에만** 쓴다.

    `.hi-vibe/`는 단순한 캐시 폴더가 아니라 hi-vibe를 켜는 마커다. 캐시를
    쓰겠다고 이걸 만들어버리면, init한 적 없는 저장소에 훅이 돌기 시작한다
    ("init 안 한 프로젝트에는 전혀 개입하지 않는다"가 깨진다). 그래서
    makedirs로 마커까지 만들지 않고, 없으면 캐시를 포기한다."""
    if not os.path.isdir(os.path.join(cwd, ".hi-vibe")):
        return
    try:
        os.makedirs(os.path.dirname(_ci_cache_path(cwd)), exist_ok=True)
        with open(_ci_cache_path(cwd), "w", encoding="utf-8") as fh:
            json.dump({"fetched_at": time.time(), "result": result}, fh)
    except OSError:
        pass  # 캐시 실패는 다음에 한 번 더 조회할 뿐 — 동작에 영향 없음


def _run_gh_json(args, cwd):
    try:
        r = subprocess.run(["gh"] + args, cwd=cwd, capture_output=True,
                           text=True, timeout=CI_QUERY_TIMEOUT)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def ci_guard_missing(cwd):
    """GitHub 리모트는 생겼는데 CI 가드가 없는 상태인가.

    gate를 칠 때 리모트가 없었으면 CI는 목록에서 빠진다. 문제는 그 판단이
    **그때 한 번 내려지고 다시 안 보인다**는 것 — 나중에 GitHub에 연결해도
    아무도 "이제 켤 수 있다"고 알려주지 않는다. 판단 시점 이후의 변화를
    잡아주는 자리다."""
    if not _run_git(["remote"], cwd):
        return False
    wf_dir = os.path.join(cwd, ".github", "workflows")
    try:
        names = os.listdir(wf_dir)
    except OSError:
        return True     # 워크플로 폴더 자체가 없음 = 가드 없음
    for name in names:
        if "vibe-guards" in name:
            return False
    return True


def ci_health(cwd, limit=15):
    """현재 브랜치의 연속 CI 실패 수 → {"failures": N, "workflow": ..., "last_success": ...}.

    실패가 없거나, gh가 없거나, 조회에 실패하면 None — 호출부는 조용히 생략한다."""
    cached = _read_ci_cache(cwd)
    if cached is not None:
        return cached or None

    branch = (_run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd) or "").strip()
    if not branch or branch == "HEAD":
        return None
    runs = _run_gh_json(
        ["run", "list", "--branch", branch, "--limit", str(limit),
         "--json", "conclusion,status,createdAt,workflowName"], cwd)
    if not isinstance(runs, list):
        return None   # gh 없음/미인증/오프라인 — 캐시하지 않고 다음에 재시도

    failures, workflow, last_success = 0, "", ""
    for run in runs:
        if run.get("status") != "completed":
            continue          # 아직 도는 중인 것은 판정 보류
        if run.get("conclusion") == "failure":
            failures += 1
            workflow = workflow or run.get("workflowName", "")
        elif run.get("conclusion") == "success":
            last_success = (run.get("createdAt") or "")[:10]
            break             # 연속 실패는 여기서 끊긴다
        else:
            break             # cancelled/skipped 등은 연속으로 세지 않는다

    result = ({"failures": failures, "workflow": workflow,
               "last_success": last_success, "branch": branch}
              if failures else {})
    _write_ci_cache(cwd, result)
    return result or None

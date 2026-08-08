"""훅 배관(plumbing) — 입출력·게이트·심박·git·잠금. stdlib만 사용.

훅은 조언자다: 어떤 실패도 호스트(Claude Code)를 막으면 안 되므로
run()이 모든 예외를 삼키고 exit 0 한다. 넓은 except는 원칙적으로
금지(root-cause-first)지만, "호스트를 절대 깨지 않는다"가 더 상위
계약인 유일한 지점이 여기다.

이 모듈은 의존 그래프의 뿌리다 — 형제 모듈을 임포트하지 않는다.
(형제들이 여기서 가져다 쓴다. 순환이 생기면 훅 전체가 조용히 죽는다.)
"""
import contextlib
import json
import os
import subprocess
import sys
import time


def read_payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_gate(cwd):
    """hi-vibe가 init된 프로젝트에서만 동작한다. handover.md는 흔한
    파일명이라 사용자가 자기 목적으로 이미 가질 수 있으므로, 그 존재로
    판단하면 오판(+ 남의 handover.md 오염) 위험이 있다. 대신 hi-vibe
    전용 마커 `.hi-vibe/` 디렉토리로 판단한다 — init이 만들며, 사용자가
    우연히 가질 확률이 거의 없다.

    `optout` 파일이 있으면 마커가 있어도 끈다 — "여기선 안 쓸래"라고
    말한 사용자에게 다시 묻지 않기 위한 자리다(그 기록을 남길 곳이
    있어야 조용해질 수 있다)."""
    if not cwd or not os.path.isdir(os.path.join(cwd, ".hi-vibe")):
        return False
    return not os.path.isfile(os.path.join(cwd, ".hi-vibe", "optout"))


HEARTBEAT_FILE = "heartbeat.json"


def touch_heartbeat(cwd, hook_name):
    """이 훅이 실제로 돌았다는 흔적을 남긴다.

    훅은 설계상 조용히 실패한다(fail-open) — 망가져도 에러조차 안 뜬다.
    그래서 "훅이 죽었나"를 훅으로는 확인할 수 없다(자기가 안 도니까).
    대신 살아있을 때 흔적을 남겨두면, **훅과 무관하게 도는 스킬 층**이
    그 흔적이 낡은 것을 보고 죽음을 알아챌 수 있다.

    CI 캐시와 같은 이유로 `.hi-vibe/`를 만들지 않는다 — 그건 hi-vibe를
    켜는 마커라, 없는 곳에 만들면 opt-in 원칙이 깨진다."""
    if not os.path.isdir(os.path.join(cwd or "", ".hi-vibe")):
        return
    path = os.path.join(cwd, ".hi-vibe", "state", HEARTBEAT_FILE)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        data[hook_name] = int(time.time())
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
    except OSError:
        pass  # 흔적 남기기 실패가 훅 본업을 막으면 안 된다


def read_heartbeat(cwd):
    """{훅 이름: 마지막 실행 epoch}. 없으면 {}."""
    try:
        with open(os.path.join(cwd, ".hi-vibe", "state", HEARTBEAT_FILE),
                  encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _run_git(args, cwd, timeout=3):
    """git 명령 실행 후 stdout(성공) 또는 None(실패/git 없음/타임아웃).
    handover 보강은 부가 정보이므로 어떤 실패도 조용히 생략(fail-open).

    `timeout`은 호출부가 줄일 수 있다 — SessionEnd 훅은 **전체가 1.5초
    예산을 나눠 쓰므로** 여기서 3초를 기다리면 handover를 쓰기도 전에
    죽는다. 느린 저장소·네트워크 파일시스템에서 실제로 위험하다."""
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                           text=True, timeout=timeout)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def git_status(cwd, timeout=3):
    """현재 브랜치 + 작업트리 요약(수정/신규/삭제 개수)을 한 줄로.
    git 저장소가 아니거나 실패하면 None — 호출부가 조용히 생략한다.
    다음 세션이 재개할 수 있는 '객관적 상태'만 남긴다(의미 판정 없음)."""
    # status --short 로 git 저장소인지 판별(빈 출력도 유효 — 변경 없음).
    porcelain = _run_git(["status", "--short"], cwd, timeout)
    if porcelain is None:
        return None
    # 브랜치: 커밋이 아직 없으면 rev-parse가 실패하므로 symbolic-ref로 폴백.
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd, timeout)
    if not branch or branch.strip() == "HEAD":
        sym = _run_git(["symbolic-ref", "--short", "HEAD"], cwd, timeout)
        branch = sym if sym else "(detached)"
    branch = branch.strip() or "(detached)"
    mod = new = deleted = 0
    for ln in porcelain.splitlines():
        code = ln[:2]
        if "D" in code:
            deleted += 1
        elif "?" in code or "A" in code:
            new += 1
        elif code.strip():
            mod += 1
    parts = []
    if mod:
        parts.append(f"수정 {mod}")
    if new:
        parts.append(f"신규 {new}")
    if deleted:
        parts.append(f"삭제 {deleted}")
    summary = " · ".join(parts) if parts else "변경 없음"
    return f"{branch}, {summary}"


def emit(event_name, additional_context=None, system_message=None,
         decision=None, reason=None):
    """훅 출력 JSON. decision="block"은 Stop에서만 쓰며, 턴을 멈추지 않고
    reason을 지시로 실어 계속 일하게 한다 — 조언(additionalContext)과 달리
    무시되지 않는 유일한 경로다. 호출부가 "언제 막을지"를 좁게 지키는 게
    전제이며, 여기서는 형식만 책임진다."""
    out = {}
    if additional_context:
        out["hookSpecificOutput"] = {
            "hookEventName": event_name,
            "additionalContext": additional_context[:9500],
        }
    if system_message:
        out["systemMessage"] = system_message[:1000]
    if decision:
        out["decision"] = decision
        if reason:
            out["reason"] = reason[:4000]
    if out:
        print(json.dumps(out, ensure_ascii=False))


@contextlib.contextmanager
def file_lock(target_path):
    """target_path 쓰기를 프로세스 간 직렬화한다. 여러 세션(터미널)이
    같은 handover.md에 동시에 기록할 때 read-modify-write race로 항목이
    유실되는 것을 막는다. Unix는 fcntl.flock, 그 외(Windows 등)는
    best-effort(락 없이 진행). 락 획득 자체가 실패해도 호스트를 깨지
    않는다 — 최악이라도 락 없이 쓰는 것뿐이고, 그건 기존 동작과 같다."""
    lock_f = None
    try:
        lock_f = open(target_path + ".lock", "w")
        try:
            import fcntl
            fcntl.flock(lock_f.fileno(), fcntl.LOCK_EX)
        except Exception:
            pass  # Windows 등 flock 불가: best-effort로 진행
    except Exception:
        lock_f = None
    try:
        yield
    finally:
        if lock_f is not None:
            try:
                lock_f.close()  # close 시 flock 자동 해제
            except Exception:
                pass


def run(fn):
    try:
        fn(read_payload())
    except Exception:
        pass
    sys.exit(0)

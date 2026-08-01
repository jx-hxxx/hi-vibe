"""hi-vibe 훅 공용 유틸. stdlib만 사용.

훅은 조언자다: 어떤 실패도 호스트(Claude Code)를 막으면 안 되므로
run()이 모든 예외를 삼키고 exit 0 한다. 넓은 except는 원칙적으로
금지(root-cause-first)지만, "호스트를 절대 깨지 않는다"가 더 상위
계약인 유일한 지점이 여기다.
"""
import contextlib
import json
import os
import re
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


def _run_git(args, cwd):
    """git 명령 실행 후 stdout(성공) 또는 None(실패/git 없음/타임아웃).
    handover 보강은 부가 정보이므로 어떤 실패도 조용히 생략(fail-open)."""
    try:
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True,
                           text=True, timeout=3)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    return r.stdout


def git_status(cwd):
    """현재 브랜치 + 작업트리 요약(수정/신규/삭제 개수)을 한 줄로.
    git 저장소가 아니거나 실패하면 None — 호출부가 조용히 생략한다.
    다음 세션이 재개할 수 있는 '객관적 상태'만 남긴다(의미 판정 없음)."""
    # status --short 로 git 저장소인지 판별(빈 출력도 유효 — 변경 없음).
    porcelain = _run_git(["status", "--short"], cwd)
    if porcelain is None:
        return None
    # 브랜치: 커밋이 아직 없으면 rev-parse가 실패하므로 symbolic-ref로 폴백.
    branch = _run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    if not branch or branch.strip() == "HEAD":
        sym = _run_git(["symbolic-ref", "--short", "HEAD"], cwd)
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


def tail_lines(path, max_bytes=512 * 1024):
    """트랜스크립트 JSONL의 마지막 max_bytes만 읽어 라인 리스트로."""
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            if size > max_bytes:
                f.seek(size - max_bytes)
                f.readline()  # 잘린 첫 라인 버림
            return f.read().decode("utf-8", errors="replace").splitlines()
    except Exception:
        return []


def parse_transcript(path):
    """(최근 사용자 요청 목록, 수정한 파일 경로 집합) 반환."""
    prompts, edited = [], []
    for line in tail_lines(path):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        msg = entry.get("message") or {}
        content = msg.get("content")
        if entry.get("type") == "user" and msg.get("role") == "user":
            if isinstance(content, str):
                text = content
            elif isinstance(content, list):
                text = " ".join(
                    c.get("text", "") for c in content
                    if isinstance(c, dict) and c.get("type") == "text"
                )
            else:
                text = ""
            text = " ".join(text.split())
            # 훅/시스템 주입은 제외
            if text and not text.startswith("<") and "tool_result" not in text:
                prompts.append(text[:120])
        elif isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_use" \
                        and c.get("name") in ("Write", "Edit", "MultiEdit", "NotebookEdit"):
                    inp = c.get("input") or {}
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if fp and fp not in edited:
                        edited.append(fp)
    return prompts[-5:], edited


# Bash 안에서 파일을 쓰는 흔한 방법들. PostToolUse 훅은 Write/Edit만 보므로
# heredoc·리다이렉트·`sed -i`로 들어온 코드는 훅에 안 잡힌다 — 그런 턴을
# "코드 안 건드린 턴"으로 오해하면 리뷰까지 통째로 건너뛴다.
# 진단용 리다이렉트는 먼저 지운다 — `2>&1`, `>/dev/null`은 파일 쓰기가 아니다.
_BASH_NOISE_RE = re.compile(r"\d?>&\d|>\s*/dev/null")
_BASH_WRITE_RE = re.compile(
    r">>?\s*[^\s|&]"                     # > file, >> file
    r"|\btee\b|\bsed\b[^|]*\s-i"
    r"|\b(?:cp|mv|touch|install)\b"
    r"|<<-?\s*['\"]?\w+"                 # heredoc
    r"|\b(?:python3?|node|deno)\b[^|]*\s-[ce]\b"
)

_DOC_SUFFIXES = (".md", ".txt", ".rst")
_CATCH_MARK = "👋 hi-vibe"  # 마커 접두사(고정) — 세션에서 이 문자열로 grep


def bash_wrote_files(path):
    """이 세션이 Bash로 파일을 썼을 가능성이 있나.

    PostToolUse 훅은 `Write|Edit|MultiEdit`만 본다. Claude가 heredoc이나
    `sed -i`, 생성 스크립트로 파일을 만들면 훅에도 안 잡히고 트랜스크립트의
    `edited` 목록에도 안 남는다. 그 턴을 "코드 안 건드림"으로 보면 리뷰까지
    통째로 건너뛴다 — 이 함수는 그 구멍을 막는다.

    느슨하게 잡아도 안전하다: 실제로 막을지는 git이 본 **리뷰 안 받은 코드
    변경**이 있느냐로 정해지므로, 여기서 조금 넓게 봐도 없는 변경을 만들어
    내지는 않는다."""
    for line in tail_lines(path):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict) or c.get("type") != "tool_use":
                continue
            if c.get("name") != "Bash":
                continue
            cmd = (c.get("input") or {}).get("command") or ""
            if _BASH_WRITE_RE.search(_BASH_NOISE_RE.sub("", cmd)):
                return True
    return False


def session_activity(path):
    """(코드 쓰기 tool_use 횟수, 어시스턴트가 남긴 `👋 hi-vibe` 마커 수).

    - 코드 쓰기: Write/Edit/MultiEdit/NotebookEdit 중 대상이 문서(.md/.txt/.rst)가
      아닌 것만 센다(훅이 실제로 위험 패턴을 검사한 쓰기).
    - 마커: 어시스턴트 텍스트에 남은 `👋 hi-vibe` 개수 = 이번 세션에 hi-vibe가
      드러낸 발견 수(훅·스킬·에이전트 합산). 세지 못해도 훅 동작엔 무해."""
    writes = 0
    catches = 0
    for line in tail_lines(path):
        try:
            entry = json.loads(line)
        except Exception:
            continue
        content = (entry.get("message") or {}).get("content")
        if isinstance(content, str):
            catches += content.count(_CATCH_MARK)
            continue
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use" and c.get("name") in (
                    "Write", "Edit", "MultiEdit", "NotebookEdit"):
                inp = c.get("input") or {}
                fp = inp.get("file_path") or inp.get("notebook_path") or ""
                if not fp.endswith(_DOC_SUFFIXES):
                    writes += 1
            elif c.get("type") == "text":
                catches += c.get("text", "").count(_CATCH_MARK)
    return writes, catches


# 테스트 실행으로 보이는 Bash 명령 (pytest/unittest/jest/vitest/go test/cargo test 등)
_TEST_CMD_RE = re.compile(
    r"\b(pytest|python[0-9.]*\s+-m\s+(?:unittest|pytest)|unittest|jest|vitest|"
    r"npm\s+(?:run\s+)?test|yarn\s+test|pnpm\s+test|go\s+test|cargo\s+test)\b")
def _result_from_output(text):
    """테스트 출력 텍스트에서 명확한 결과 한 줄. 없으면 None."""
    if not text:
        return None
    fail = re.search(r"(\d+)\s+failed", text, re.I) or \
        re.search(r"FAILED\s*\(.*?(?:failures|errors)=(\d+)", text, re.I) or \
        re.search(r"Tests:\s+(\d+)\s+failed", text, re.I)
    if fail:
        return f"실패 {fail.group(1)}"
    ok = re.search(r"Ran\s+\d+\s+tests?.*?\bOK\b", text, re.I | re.S) or \
        re.search(r"(\d+)\s+passed", text, re.I)
    if ok:
        return "통과"
    return None


def last_test_result(path):
    """트랜스크립트에서 마지막 테스트 실행의 (명령, 결과 요약)을 찾는다.
    명확히 식별될 때만 반환하고, 애매하면 None (의미 판정하지 않음)."""
    lines = tail_lines(path)
    pending_cmd = None      # 아직 결과를 못 만난 테스트 명령
    found = None            # (cmd, result)
    for line in lines:
        try:
            entry = json.loads(line)
        except Exception:
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "tool_use" and c.get("name") == "Bash":
                cmd = (c.get("input") or {}).get("command", "")
                m = _TEST_CMD_RE.search(cmd)
                if m:
                    pending_cmd = " ".join(cmd.split())[:80]
            elif c.get("type") == "tool_result" and pending_cmd:
                out = c.get("content")
                if isinstance(out, list):
                    out = " ".join(x.get("text", "") for x in out
                                   if isinstance(x, dict))
                res = _result_from_output(out if isinstance(out, str) else "")
                if res:
                    found = (pending_cmd, res)
                pending_cmd = None
    return found


def prepend_entry(handover_path, entry_text):
    """헤더(첫 '## ' 전까지)를 보존하고 그 뒤, 기존 항목들 앞에 삽입."""
    header, body = "", ""
    if os.path.isfile(handover_path):
        with open(handover_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        idx = content.find("\n## ")
        if idx == -1:
            header, body = content.rstrip() + "\n", ""
        else:
            header, body = content[: idx + 1], content[idx + 1:]
    else:
        header = "# Handover — 세션 인수인계\n"
    with open(handover_path, "w", encoding="utf-8") as f:
        f.write(header + "\n" + entry_text.rstrip() + "\n\n" + body.lstrip("\n"))


def rotate(handover_path, keep=10, limit=20):
    """항목이 limit 초과면 오래된 것들을 handover-archive.md로 이동."""
    try:
        with open(handover_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        idx = content.find("\n## ")
        if idx == -1:
            return
        header, body = content[: idx + 1], content[idx + 1:]
        parts = ("\n" + body).split("\n## ")
        entries = ["## " + p for p in parts if p.strip()]
        if len(entries) <= limit:
            return
        keep_entries, old = entries[:keep], entries[keep:]
        with open(handover_path, "w", encoding="utf-8") as f:
            f.write(header + "\n" + "\n".join(keep_entries))
        archive = os.path.join(os.path.dirname(handover_path), "handover-archive.md")
        prev = ""
        if os.path.isfile(archive):
            with open(archive, encoding="utf-8", errors="replace") as f:
                prev = f.read()
        if not prev.strip():
            prev = "# Handover Archive\n"
        with open(archive, "w", encoding="utf-8") as f:
            f.write(prev.rstrip() + "\n\n" + "\n".join(old) + "\n")
    except Exception:
        pass


def latest_entry(handover_path, max_chars=1200):
    """가장 최근 항목(첫 '## ' 섹션) 텍스트."""
    try:
        with open(handover_path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        idx = content.find("\n## ")
        if idx == -1:
            return ""
        rest = content[idx + 1:]
        nxt = rest.find("\n## ")
        entry = rest if nxt == -1 else rest[:nxt]
        return entry.strip()[:max_chars]
    except Exception:
        return ""


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

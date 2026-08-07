"""hi-vibe 훅 공용 유틸. stdlib만 사용.

훅은 조언자다: 어떤 실패도 호스트(Claude Code)를 막으면 안 되므로
run()이 모든 예외를 삼키고 exit 0 한다. 넓은 except는 원칙적으로
금지(root-cause-first)지만, "호스트를 절대 깨지 않는다"가 더 상위
계약인 유일한 지점이 여기다.
"""
import contextlib
import hashlib
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
    r"|\brm\b"                          # 삭제도 코드 변경이다
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


# 명령 원문을 기록에 남기지 않기 위한 것들. 종류와 대상 파일만 뽑는다.
_BASH_KINDS = [
    (re.compile(r"<<-?\s*['\"]?\w+"), "heredoc"),
    (re.compile(r">>\s*[^\s|&]"), "append"),
    (re.compile(r"\btee\b"), "tee"),
    (re.compile(r"\bsed\b[^|]*\s-i"), "sed -i"),
    (re.compile(r"\b(?:cp|mv|install)\b"), "copy/move"),
    (re.compile(r"\btouch\b"), "touch"),
    (re.compile(r"\brm\b"), "delete"),
    (re.compile(r"\b(?:python3?|node|deno)\b[^|]*\s-[ce]\b"), "script"),
    (re.compile(r">\s*[^\s|&]"), "redirect"),
]
# 대상 후보로 받아들일 토큰. 따옴표·`=`·공백·`$`가 있으면 **파일 이름이
# 아니라 내용일 수 있으므로** 버린다 — 그게 비밀키가 새는 경로다.
_SAFE_PATH_RE = re.compile(r"^[\w./~@+-]{1,80}$")
_REDIRECT_TARGET_RE = re.compile(r">>?\s*([^\s|&;]+)")
_TEE_TARGET_RE = re.compile(r"\btee\b(?:\s+-\w+)*\s+([^\s|&;]+)")


def _bash_target(cmd, kind):
    """명령에서 **대상 파일 이름만** 뽑는다. 확실하지 않으면 None."""
    m = None
    if kind in ("redirect", "append", "heredoc"):
        m = _REDIRECT_TARGET_RE.search(cmd)
    elif kind == "tee":
        m = _TEE_TARGET_RE.search(cmd)
    elif kind in ("sed -i", "copy/move", "touch", "delete"):
        parts = [t for t in cmd.split() if not t.startswith("-")]
        cand = parts[-1] if parts else ""
        return cand if _SAFE_PATH_RE.match(cand) else None
    if not m:
        return None
    cand = m.group(1).strip("'\"")
    return cand if _SAFE_PATH_RE.match(cand) else None


def bash_write_summary(path):
    """Bash 쓰기 흔적을 `(요약 목록, 지문)`으로. **명령 원문은 남기지 않는다.**

    처음엔 명령 원문을 200자까지 저장해 handover에 100자를 실었다. 그런데
    `printf 'API_KEY = "…"' > cfg.py` 같은 명령이 그대로 복제됐다 —
    **트랜스크립트에만 있던 비밀키가 프로젝트 루트 파일로 옮겨지고, 다음
    세션 컨텍스트에 다시 주입되고, 아카이브에 장기 보존된다.** 비밀키
    안전장치를 내세우는 플러그인에서 날 일이 아니다.

    정규식으로 가리는 방법은 새 패턴을 놓친다. 그래서 **원문을 아예 갖고
    있지 않는다** — 보여줄 것은 대상 파일과 작업 종류뿐이고, 변화 감지에
    필요한 것은 지문(해시)이면 충분하다.

    판정 규칙(`_BASH_WRITE_RE`)은 `bash_wrote_files`와 공유한다."""
    seen, out, norm = set(), [], []
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
            clean = _BASH_NOISE_RE.sub("", cmd)
            if not _BASH_WRITE_RE.search(clean):
                continue
            norm.append(" ".join(cmd.split()))
            kind = next((k for rx, k in _BASH_KINDS if rx.search(clean)), "write")
            target = _bash_target(clean, kind)
            item = "`%s` — %s" % (target, kind) if target else "(대상 미상) — %s" % kind
            if item not in seen:
                seen.add(item)
                out.append(item)
    fingerprint = hashlib.sha256(
        "\n".join(norm).encode("utf-8")).hexdigest() if norm else ""
    return out, fingerprint


def safe_text(text):
    """기록에 남기기 전 비밀키로 보이는 부분을 가린다.

    Bash는 원문을 아예 안 남기지만 **사용자 요청과 테스트 명령은 글 자체가
    내용**이라 안 남길 수가 없다. 그쪽은 가리는 수밖에 없고, 판정은 훅과
    같은 규칙을 쓴다(규칙을 두 벌 두면 한쪽만 고쳐진다)."""
    if not text:
        return text
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import post_write_guard          # 지연 임포트 — 순환 임포트 방지
        raw = post_write_guard.iter_secret_spans(text)
    except Exception:
        return text
    # 겹치는 구간을 먼저 합친다. 안 합치고 뒤에서부터 하나씩 바꾸면 **바깥
    # 구간을 먼저 지운 뒤 안쪽 구간의 옛 좌표로 또 자르게 되어**, 키 뒤의
    # 멀쩡한 문장까지 날아간다(실제로 `… 뒤 문장`이 통째로 사라졌다).
    merged = []
    for _label, start, end in sorted((sp for sp in raw), key=lambda sp: (sp[1], sp[2])):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    for start, end in reversed(merged):
        text = text[:start] + "[비밀키 가림]" + text[end:]
    return text


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


FRESH_EYES_TYPE = "hi-vibe:fresh-eyes"
AGENTS_FILE = "agents.json"
AGENT_SESSIONS_KEEP = 20
# `review_scope.py mark` 실제 호출만 — 커밋 메시지에 섞인 "mark"는 안 센다.
_MARK_RE = re.compile(r"""review_scope(?:\.py)?["']?\s+mark\b""")


def review_activity(path, offset=0):
    """`offset` 이후에 새로 생긴 (fresh-eyes 실행 수, mark 수, 다음 offset).

    왜 AI에게 안 묻나: `write-gate`는 fresh-eyes를 생략하면 한 줄로 밝히라고
    지시하지만, 그건 **AI 주의력에 기대는 층**이라 조용히 빠질 수 있다.
    실제로 한 세션이 **하루 종일** 에이전트 호출이 막힌 채 돌았는데(세션
    설정이 Agent 도구를 금지), 리뷰는 계속 돌고 "남의 눈"만 빠져 있었고
    그 사실이 **어디에도 안 남았다**(2026-08-07). 훅 죽음은 heartbeat로
    잡으면서 에이전트 죽음은 아무도 안 보고 있었던 것이다.

    호출 자체는 트랜스크립트에 `subagent_type`으로 남으므로, 기계가 세면
    **AI의 협조가 필요 없다** — 이 저장소의 "증거가 파일 안에 있으면 기계가
    잡는다" 기준의 앞쪽에 해당한다.

    **왜 전체를 다시 안 세고 이어 읽나:** 처음엔 `tail_lines`로 매번 전체를
    세고 세션별 누계와 비교해 델타를 구했다. 그런데 `tail_lines`는 끝
    512KB만 읽는다 — 트랜스크립트가 수십 MB로 자라면 예전 호출이 창 밖으로
    밀려 **누계가 줄어든 것처럼 보이고**, 그러면 델타가 음수라 계산이 멈춘다.
    긴 세션일수록 안 세는 셈인데 하필 긴 세션이 제일 중요하다(실측: 16MB
    세션에서 0회). 지난번 읽은 바이트 위치부터만 읽으면 정확하고 더 싸다.

    반쯤 쓰인 마지막 줄은 넘기지 않는다 — 마지막 개행까지만 소비한다."""
    fresh_eyes = marks = 0
    try:
        if offset > os.path.getsize(path):
            offset = 0          # 파일이 갈렸다(같은 경로를 새 세션이 쓴 경우)
        with open(path, "rb") as fh:
            fh.seek(offset)
            chunk = fh.read()
    except OSError:
        return 0, 0, offset
    cut = chunk.rfind(b"\n")
    if cut < 0:
        return 0, 0, offset     # 아직 완결된 줄이 없다
    new_offset = offset + cut + 1
    for raw in chunk[:cut + 1].splitlines():
        try:
            entry = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            if not isinstance(c, dict) or c.get("type") != "tool_use":
                continue
            inp = c.get("input") or {}
            if c.get("name") in ("Agent", "Task"):
                if inp.get("subagent_type") == FRESH_EYES_TYPE:
                    fresh_eyes += 1
            elif c.get("name") == "Bash":
                if _MARK_RE.search(inp.get("command") or ""):
                    marks += 1
    return fresh_eyes, marks, new_offset


def agent_offset(cwd, session_id):
    """이 세션 트랜스크립트를 어디까지 읽었나 (없으면 0 — 처음부터)."""
    seen = read_agent_activity(cwd).get("sessions")
    if not isinstance(seen, dict):
        return 0
    entry = seen.get(str(session_id))
    return int(entry.get("offset") or 0) if isinstance(entry, dict) else 0


def note_agent_activity(cwd, session_id, fresh_eyes, marks, offset=0):
    """새로 센 만큼을 `.hi-vibe/state/agents.json`에 더하고 읽은 위치를 남긴다.

    Stop 훅은 한 세션에서 여러 번 돈다. `review_activity`가 **이미 새 구간만**
    세어 주므로 여기서는 그대로 더하면 된다 — 겹쳐 세지 않는 책임은 offset이
    진다.

    `.hi-vibe/`가 없으면 아무것도 만들지 않는다 — 마커를 훅이 만들면
    opt-in 원칙이 깨진다(heartbeat와 같은 이유)."""
    if not os.path.isdir(os.path.join(cwd or "", ".hi-vibe")):
        return
    state_dir = os.path.join(cwd, ".hi-vibe", "state")
    path = os.path.join(state_dir, AGENTS_FILE)
    sid = str(session_id)
    try:
        os.makedirs(state_dir, exist_ok=True)
        with file_lock(path):
            data = {}
            try:
                with open(path, encoding="utf-8") as fh:
                    loaded = json.load(fh)
                if isinstance(loaded, dict):
                    data = loaded
            except (OSError, ValueError):
                data = {}
            seen = data.get("sessions")
            if not isinstance(seen, dict):
                seen = {}
            prev = seen.get(sid) if isinstance(seen.get(sid), dict) else {}
            if not fresh_eyes and not marks and offset <= int(prev.get("offset") or 0):
                return                       # 새로 읽은 것도, 새로 센 것도 없다
            now = int(time.time())
            data["fresh_eyes"] = int(data.get("fresh_eyes") or 0) + max(0, fresh_eyes)
            data["marks"] = int(data.get("marks") or 0) + max(0, marks)
            if fresh_eyes:
                data["fresh_eyes_last"] = now
            seen[sid] = {"offset": int(offset), "t": now}
            if len(seen) > AGENT_SESSIONS_KEEP:
                # 시각순으로 오래된 것부터 버린다 — 파일 순서에 기대지 않는다.
                old = sorted(seen, key=lambda k: (seen[k] or {}).get("t", 0))
                for k in old[:len(seen) - AGENT_SESSIONS_KEEP]:
                    seen.pop(k, None)
            data["sessions"] = seen
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)
            os.replace(tmp, path)
    except OSError:
        pass    # 기록 실패는 리뷰 동작과 무관 — 다음 턴에 다시 시도된다


def read_agent_activity(cwd):
    try:
        with open(os.path.join(cwd or "", ".hi-vibe", "state", AGENTS_FILE),
                  encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


# 테스트 실행으로 보이는 Bash 명령 (pytest/unittest/jest/vitest/go test/cargo test 등)
_TEST_CMD_RE = re.compile(
    r"\b(pytest|python[0-9.]*\s+-m\s+(?:unittest|pytest)|unittest|jest|vitest|"
    r"npm\s+(?:run\s+)?test|yarn\s+test|pnpm\s+test|go\s+test|cargo\s+test)\b")

# 명령을 이어 붙이는 경계. 여기서 잘라야 "무엇을 돌렸나"가 정확해진다.
_CMD_SPLIT_RE = re.compile(r"\n|&&|\|\||[;|]")


def test_command_segment(cmd, at):
    """`at` 위치가 속한 명령 구간만 잘라낸다.

    예전엔 명령 **전체의 앞 80자**를 적었다. 그런데 테스트를 뒤에 붙이는 일이
    흔하다 — `python3 - <<'PY' … PY` 다음 줄에 `python3 -m unittest …`처럼.
    그러면 정규식은 뒤쪽을 보고 "테스트 맞다"고 판정하는데 기록은 앞부분이
    들어가, **돌린 적 없는 명령이 handover에 검증 기록으로 남았다.**
    결과("통과")는 맞아서 딱 봐서는 안 이상한 게 더 나쁘다.

    파이프 뒤(`| grep …`)가 잘리는 것은 덤이다 — 무엇을 돌렸는지만 남는다."""
    start = 0
    for m in _CMD_SPLIT_RE.finditer(cmd):
        if m.end() > at:
            break
        start = m.end()
    end = len(cmd)
    for m in _CMD_SPLIT_RE.finditer(cmd, at):
        end = m.start()
        break
    return cmd[start:end]


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
                    seg = test_command_segment(cmd, m.start())
                    pending_cmd = " ".join(seg.split())[:80]
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


def handover_body(cwd, transcript, git_timeout=3):
    """handover 자동 항목의 본문 줄, "이 세션에 활동이 있었나", 활동 서명.

    PreCompact와 SessionEnd가 **같은 형식**을 써야 한다. 두 벌로 두면
    한쪽만 고쳐져 항목 모양이 갈린다(이 저장소가 문서에서 여러 번 겪은 일).

    **Git 상태는 활동으로 세지 않는다.** 세어봤더니 git 저장소에서는
    `git_status`가 늘 문자열을 돌려주므로 **모든 빈 세션이 "활동 있음"이
    됐다** — 열자마자 `/clear`를 쳐도 `- Git: master, 변경 없음` 한 줄짜리
    항목이 쌓였다. 그 줄은 이 세션이 뭘 했는지 말해주지 않는다. 활동은
    **대화에서 나온 것**(요청·수정·검증)만으로 판단하고, Git은 부가정보로만
    싣는다. (비-git 임시 폴더에서만 테스트해서 이 결함을 놓쳤었다.)

    세 번째 값은 **본문 서명**이다 — 같은 내용을 두 번 쓰지 않기 위한 것으로,
    개수가 아니라 내용이라야 한다(뒤의 `handover_already_written` 참고)."""
    prompts, edited = parse_transcript(transcript) if transcript else ([], [])
    git = git_status(cwd, git_timeout)
    test = last_test_result(transcript) if transcript else None
    # Bash 쓰기는 `edited`에 안 잡힌다(PostToolUse가 Write/Edit만 보므로).
    # 기록에도 안 실으면 "Bash로만 일한 구간"은 남아도 빈 껍데기가 된다.
    bash_writes, bash_fp = bash_write_summary(transcript) if transcript else ([], "")

    lines = []
    if git:
        lines.append("- Git: %s" % git)
    if test:
        cmd, res = test
        lines.append("- 최근 검증: `%s` → %s" % (safe_text(cmd), res))
    if prompts:
        lines.append("- 사용자 요청(최근):")
        lines += ["  - %s" % safe_text(p) for p in prompts]
    if edited:
        lines.append("- 수정 파일:")
        lines += ["  - `%s`" % fp for fp in edited[:15]]
        if len(edited) > 15:
            lines.append("  - …외 %d개" % (len(edited) - 15))
    if bash_writes:
        lines.append("- Bash로 쓴 것(추정):")
        lines += ["  - %s" % w for w in bash_writes[-5:]]
        if len(bash_writes) > 5:
            lines.append("  - …외 %d개" % (len(bash_writes) - 5))
    # 서명에서 Bash를 빠뜨렸더니 **auto-compact 뒤 같은 턴에서 Bash로만
    # 작업한 경우**가 통째로 사라졌다 — 새 사용자 메시지가 없으면 prompts도
    # 그대로여서 "새 게 없다"로 읽혔다.
    active = bool(prompts or edited or test or bash_writes)  # Git은 활동이 아니다
    # 서명에는 Bash **지문**만 넣는다 — 원문을 넣으면 표식 파일에도 남는다.
    sig = hashlib.sha1(
        json.dumps([prompts, edited, test, bash_fp], ensure_ascii=False,
                   sort_keys=True).encode("utf-8")).hexdigest()
    return lines, active, sig


WRITTEN_FILE = "handover-written.json"
# 표식을 슬롯 하나로 두면 **다른 세션이 덮어쓴다** — 같은 프로젝트에 창을
# 두 개 띄우면 앞 세션의 표식이 사라져 중복 방지가 풀린다. 세션별로 둔다.
WRITTEN_KEEP = 10


def note_handover_written(cwd, session_id, signature):
    """이 세션에서 **무엇을** 남겼는지 서명으로 적어둔다.

    `/compact` 직후 `/clear`를 치면 거의 같은 내용이 두 번 들어간다.

    표식은 **세션별로** 둔다(슬롯 하나면 다른 세션이 덮어쓴다).

    처음엔 "수정 파일 **개수**"로 비교했는데, 그러면 compact 뒤에 한 일이
    통째로 사라졌다 — 같은 파일을 또 고치거나, Bash로 고치거나, 파일은
    안 건드리고 중요한 결정만 논의한 경우 개수가 그대로여서 "새 게 없다"로
    읽혔다. **중복을 막다 진짜 작업을 버리는 쪽이 훨씬 나쁘다.** 그래서
    본문 내용의 서명으로 비교한다 — 요청 한 줄만 늘어도 서명이 달라진다."""
    if not os.path.isdir(os.path.join(cwd or "", ".hi-vibe")):
        return
    path = os.path.join(cwd, ".hi-vibe", "state", WRITTEN_FILE)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        data[str(session_id or "")] = str(signature)
        # 세션마다 한 칸씩 쌓이므로 오래된 것은 버린다. 창을 여러 개 띄워도
        # 최근 몇 개는 남는다.
        if len(data) > WRITTEN_KEEP:
            for key in list(data)[:-WRITTEN_KEEP]:
                del data[key]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
    except OSError:
        pass


def handover_already_written(cwd, session_id, signature):
    """같은 세션에서 **똑같은 내용**을 이미 남겼나."""
    try:
        with open(os.path.join(cwd, ".hi-vibe", "state", WRITTEN_FILE),
                  encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    return data.get(str(session_id or "")) == str(signature)


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

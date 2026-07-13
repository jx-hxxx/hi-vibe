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
    우연히 가질 확률이 거의 없다."""
    return bool(cwd) and os.path.isdir(os.path.join(cwd, ".hi-vibe"))


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


def emit(event_name, additional_context=None, system_message=None):
    out = {}
    if additional_context:
        out["hookSpecificOutput"] = {
            "hookEventName": event_name,
            "additionalContext": additional_context[:9500],
        }
    if system_message:
        out["systemMessage"] = system_message[:1000]
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

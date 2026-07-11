"""hi-vibe 훅 공용 유틸. stdlib만 사용.

훅은 조언자다: 어떤 실패도 호스트(Claude Code)를 막으면 안 되므로
run()이 모든 예외를 삼키고 exit 0 한다. 넓은 except는 원칙적으로
금지(root-cause-first)지만, "호스트를 절대 깨지 않는다"가 더 상위
계약인 유일한 지점이 여기다.
"""
import json
import os
import sys


def read_payload():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_gate(cwd):
    """hi-vibe가 init된 프로젝트에서만 동작 (handover.md 존재 여부)."""
    return bool(cwd) and os.path.isfile(os.path.join(cwd, "handover.md"))


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
                        and c.get("name") in ("Write", "Edit", "NotebookEdit"):
                    inp = c.get("input") or {}
                    fp = inp.get("file_path") or inp.get("notebook_path")
                    if fp and fp not in edited:
                        edited.append(fp)
    return prompts[-5:], edited


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


def run(fn):
    try:
        fn(read_payload())
    except Exception:
        pass
    sys.exit(0)

"""리뷰 활동 감시 — fresh-eyes가 실제로 도는지 기계가 센다.

AI에게 "생략했으면 밝혀라"는 이미 지시돼 있었는데 정확히 그 층이 조용히
빠진 사건(2026-08-07)이 있었다. 그래서 트랜스크립트에 남는 호출 흔적을
훅이 직접 세고 `.hi-vibe/state/agents.json`에 누적한다. doctor가 읽는다.
"""
import json
import os
import re
import time

from _base import file_lock


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

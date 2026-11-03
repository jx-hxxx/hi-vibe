"""UserPromptSubmit: 컨텍스트 사용률을 모델에게 알려 /compact·/clear 안내 시점을 판단하게 한다.

모델은 자기 컨텍스트가 몇 %인지 볼 수 없다 — 상태 표시줄의 %는 사용자 화면에만
있다. 그래서 숫자는 훅이 넣는다(모델이 매 턴 기록 파일을 열어 보게 하면 잊는다).

- 사용량: 트랜스크립트의 마지막 assistant `usage`(input + cache_read + cache_creation).
  훅 입력에는 컨텍스트 정보가 없다(2026-11-03 실측: cwd·hook_event_name·
  permission_mode·prompt·prompt_id·scratchpad_dir·session_id·transcript_path뿐).
- 한도: 훅이 알 길이 없다(모델 이름도 단서가 못 된다 — `[1m]` 없이 100만인 모델이 있다).
  `.hi-vibe/context`의 `window=`를 쓰고, 없으면 **대화 중 한 번 사용자에게 묻게 한다**:
  사용량이 ASK_MIN을 넘으면 "화면의 컨텍스트 %"를 물어 토큰÷%로 한도를 계산해 저장하게
  지시한다(세션당 한 번). 답을 받기 전에는 20만으로 보되 20만을 넘으면 100만으로 본다.
- 설정: `.hi-vibe/context` — 없으면 기본(켜짐, warn=30). `off` 한 단어면 꺼짐.
  `warn=<정수 %>` `window=<토큰>` (공백·줄바꿈 구분). init이 사용자에게 묻고 쓴다.
- 알림은 warn-5%부터, 같은 구간에선 세션당 한 번(근접 → 기준 → 이후 10%마다). 기준을 넘어도 **중요한 작업 중이면 끊지 말라**고 함께 지시한다 —
  흐름 한가운데의 compact가 문턱을 넘는 것보다 나쁘다(사용자 결정 2026-11-03).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

CONFIG = os.path.join(".hi-vibe", "context")
DEFAULT_WARN = 30
DEFAULT_WINDOW = 200_000
LARGE_WINDOW = 1_000_000
LEAD = 5  # 기준보다 이만큼 앞에서 알리기 시작한다 ("가까워졌을 때")
BAND = 10  # 기준을 넘긴 뒤엔 이만큼 더 찰 때마다 한 번씩만 다시 알린다
ASK_MIN = 20_000  # 이보다 적으면 화면 %가 0~2%라 20만/100만을 가르기 어렵다


def read_config(cwd):
    """(enabled, warn_pct, window_or_None). 파일이 없으면 기본값으로 켜짐."""
    try:
        with open(os.path.join(cwd, CONFIG), encoding="utf-8") as fh:
            words = fh.read().split()
    except OSError:
        return True, DEFAULT_WARN, None
    if "off" in (w.lower() for w in words):
        return False, DEFAULT_WARN, None
    warn, window = DEFAULT_WARN, None
    for w in words:
        key, _, val = w.partition("=")
        if not val.isdigit():
            continue  # 주석·오타는 무시하고 기본값 유지
        if key == "warn" and 1 <= int(val) <= 100:
            warn = int(val)
        elif key == "window" and int(val) > 0:
            window = int(val)
    return True, warn, window


def used_tokens(transcript):
    """마지막 assistant 응답이 받은 입력 토큰 = 지금 컨텍스트 크기. 못 찾으면 None.

    compact 직후엔 boundary 뒤에 assistant usage가 아직 없다 — 그 너머의 값은
    **compact 전** 크기라, 읽으면 방금 compact한 사용자에게 또 compact를 권한다.
    그래서 assistant usage보다 boundary를 먼저 만나면 None(이번 턴은 조용히)."""
    for line in reversed(_common.tail_lines(transcript)):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
            return None
        msg = entry.get("message")
        usage = msg.get("usage") if isinstance(msg, dict) else None
        if entry.get("type") == "assistant" and isinstance(usage, dict):
            return sum(int(usage.get(k) or 0) for k in (
                "input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    return None


def level(pct, warn):
    """안내 구간. 0=조용, 1=근접(warn-5), 2=기준, 이후 10%마다 하나씩."""
    if pct < max(1, warn - LEAD):
        return 0
    if pct < warn:
        return 1
    return 2 + int((pct - warn) // BAND)


def nudge(tokens, warn, window):
    """알릴 문구. 알릴 때가 아니면 None."""
    if window is None:
        window = LARGE_WINDOW if tokens > DEFAULT_WINDOW else DEFAULT_WINDOW
    pct = tokens * 100 / window
    if not level(pct, warn):
        return None
    where = "근접" if pct < warn else "초과"
    return (
        f"hi-vibe 컨텍스트 {pct:.0f}% ({tokens // 1000}K / {window // 1000}K) — "
        f"사용자 기준 {warn}% {where}. 이번 턴 끝에 한 줄로 안내하라: "
        "기능 하나가 완전히 끝났으면(구현·검증·보고까지) /clear + 새 세션 첫 마디, "
        "같은 기능을 개선 중이고 한 단계가 끝난 지점이면 /compact + 이어서 할 말. "
        f"여러 단계 변경의 한가운데이거나 중요한 작업이 이어지는 중이면 권하지 말고 계속하라"
        f"({warn}%를 넘어도 된다) — 다음 끊기 좋은 지점에서 권한다. "
        "/clear 전에는 CHANGELOG(자동 아님)에 남길 것을 먼저 남긴다."
    )


def ask_window(cwd, sid, tokens):
    """한도를 모를 때 사용자에게 한 번 물으라는 지시. 세션당 한 번만(표식 파일)."""
    flag = os.path.join(cwd, ".hi-vibe", "state", f"context-ask-{sid or 'nosid'}")
    if tokens < ASK_MIN or os.path.exists(flag):
        return None
    try:
        os.makedirs(os.path.dirname(flag), exist_ok=True)
        open(flag, "w").close()
    except OSError:
        return None  # 표식을 못 남기면 매 턴 묻게 된다 — 차라리 묻지 않는다
    return (
        f"hi-vibe: 이 프로젝트는 모델 컨텍스트 한도를 모른다(지금 {tokens:,} 토큰). "
        "이번 턴 끝에 한 줄로 사용자에게 물어라: \"상태 표시줄이나 /context에 보이는 "
        "컨텍스트 %가 몇인가요? (정리 시점 안내를 정확히 하려고 한 번만 여쭤요)\". "
        f"답을 받으면 {tokens:,} ÷ (답%/100)에 가까운 값(200000 또는 1000000)을 "
        "`.hi-vibe/context`에 `window=<값>`으로 저장하라(파일의 다른 설정은 유지). "
        "작업 중이면 작업을 먼저 끝내고 물어라."
    )


def new_level(cwd, sid, tokens, warn, window):
    """같은 구간에선 세션당 한 번만 알린다 — 매 턴 붙으면 신호가 아니다.
    사용량이 줄면(compact) 구간 기록도 내려가서, 다시 차오를 때 또 알린다."""
    w = window or (LARGE_WINDOW if tokens > DEFAULT_WINDOW else DEFAULT_WINDOW)
    cur = level(tokens * 100 / w, warn)
    path = os.path.join(cwd, ".hi-vibe", "state", f"context-level-{sid or 'nosid'}")
    try:
        with open(path, encoding="utf-8") as fh:
            last = int(fh.read().strip() or 0)
    except (OSError, ValueError):
        last = 0
    if cur != last:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(str(cur))
        except OSError:
            return False  # 기록을 못 남기면 매 턴 알리게 된다 — 차라리 조용히
    return cur > last


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    _common.touch_heartbeat(cwd, "UserPromptSubmit")
    enabled, warn, window = read_config(cwd)
    if not enabled:
        return
    tokens = used_tokens(payload.get("transcript_path", ""))
    if not tokens:
        return
    sid = payload.get("session_id", "")
    parts = [nudge(tokens, warn, window) if new_level(cwd, sid, tokens, warn, window) else None]
    if window is None:
        parts.append(ask_window(cwd, sid, tokens))
    text = "\n".join(t for t in parts if t)
    if text:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text,
        }}, ensure_ascii=False))


if __name__ == "__main__":
    _common.run(main)

"""PostToolUse(Write/Edit/MultiEdit): 방금 쓰인 코드에서 두 가지를
기계적으로 감지해 Claude에게 알린다 — 규율의 기계 층.

1. 에러 삼킴 패턴 (root-cause-first): 빈 except/catch.
   의도된 삼킴은 그 줄에 `hi-vibe: allow-swallow` 주석.
2. 하드코딩된 비밀키: API 키/토큰이 코드·설정 파일에 박히는 것.
   테스트용 가짜 키는 그 줄에 `hi-vibe: allow-secret` 주석.
   (.env* 파일은 키의 올바른 위치이므로 검사하지 않는다.)

경고만 한다: 도구 실행을 막지도, 호스트를 깨지도 않는다 (항상 exit 0).
Edit/MultiEdit은 old_string과 비교해 '새로 늘어난' 것만 경고한다 —
기존 코드를 다시 만질 때마다 잔소리하지 않기 위해서다. 비교는 개수가
아니라 실제 매치 값 기준(Counter 차집합)이라, 기존 시크릿 하나를 다른
시크릿으로 바꿔치기해도(개수는 같아도) 새 값으로 잡는다.
"""
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

CODE_EXT = (".py", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".mts", ".cts")
# 비밀키는 커밋되는 설정 파일에도 자주 박힌다
SECRET_EXT = CODE_EXT + (".json", ".yml", ".yaml", ".toml")
ALLOW_MARK = "allow-swallow"
ALLOW_SECRET_MARK = "allow-secret"

PY_PATTERNS = [
    ("빈 except (한 줄)", re.compile(r"^[ \t]*except\b[^\n]*:[ \t]*pass\b[^\n]*$", re.M)),
    ("except 후 pass만", re.compile(
        r"^[ \t]*except\b[^\n]*:[ \t]*(?:#[^\n]*)?\n[ \t]*pass[ \t]*(?:#[^\n]*)?$", re.M)),
]
JS_PATTERNS = [
    ("빈 catch 블록", re.compile(r"\bcatch\s*(?:\([^)]*\))?\s*\{[ \t]*\}")),
    ("빈 .catch()", re.compile(
        r"\.catch\(\s*(?:\([^)]*\)|[\w$]+)\s*=>\s*(?:\{[ \t]*\}|null|undefined)\s*\)")),
]

SECRET_PATTERNS = [
    ("Anthropic API 키", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI류 API 키", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{20,}")),
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub 토큰", re.compile(
        r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("Google API 키", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Slack 토큰", re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("Stripe 시크릿 키", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{10,}")),
    ("하드코딩된 시크릿 할당", re.compile(
        r"""(?i)\b(?:api[_-]?key|secret|token|password|passwd)["']?\s*[:=]\s*["'][A-Za-z0-9+/_\-]{16,}["']""")),
]
# 자리표시자/환경변수 참조가 있는 줄은 진짜 키가 아니다.
# `<...>`는 `<YOUR_KEY>` 같은 자리표시자만 억제한다 — 예전엔 맨 `<` 하나라
# JSX(`<div>`)나 비교(`a < b`)가 섞인 줄의 *진짜* 키까지 삼켰다. `xxxx`도
# 자리표시자 신호로 4자 이상만(진짜 키에 우연히 든 "xxx" 오억제 방지).
SECRET_FALSE_ALARM_RE = re.compile(
    r"(?i)your|example|dummy|placeholder|changeme|xxxx|<[A-Za-z0-9_.\-]{1,40}>"
    r"|\$\{|process\.env|os\.environ|getenv")


def _match_region(text, m):
    """매치가 걸친 줄 전체 (매치 시작 줄머리 ~ 끝 줄 끝). allow 주석은 보통
    매치 밖(닫는 `}` 뒤나 except 줄)에 달리므로, m.group(0)이 아니라 이
    영역에서 마커를 찾아야 한다 — JS `catch(e){} // allow-swallow`의 주석은
    `}` 매치 밖이라 group(0)엔 안 잡혔다 (과거 버그)."""
    start = text.rfind("\n", 0, m.start()) + 1
    end = text.find("\n", m.end())
    return text[start: end if end != -1 else len(text)]


def find_swallows(text, path):
    """(라벨, 정규화된 매치 텍스트) 리스트. allow-swallow 표시된 매치는 제외."""
    if not text:
        return []
    patterns = PY_PATTERNS if path.endswith(".py") else JS_PATTERNS
    found = []
    for label, rx in patterns:
        for m in rx.finditer(text):
            if ALLOW_MARK in _match_region(text, m):
                continue
            found.append((label, " ".join(m.group(0).split())))
    return found


def find_secrets(text):
    """(라벨, 정규화된 매치 텍스트) 리스트. allow-secret 표시·자리표시자 줄 제외."""
    if not text:
        return []
    found = []
    for label, rx in SECRET_PATTERNS:
        for m in rx.finditer(text):
            start = text.rfind("\n", 0, m.start()) + 1
            end = text.find("\n", m.end())
            line = text[start: end if end != -1 else len(text)]
            if ALLOW_SECRET_MARK in line or SECRET_FALSE_ALARM_RE.search(line):
                continue
            found.append((label, " ".join(m.group(0).split())))
    return found


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    tool = payload.get("tool_name", "")
    inp = payload.get("tool_input") or {}
    fp = inp.get("file_path") or ""

    if tool == "Write":
        pairs = [(inp.get("content", ""), "")]
    elif tool == "Edit":
        pairs = [(inp.get("new_string", ""), inp.get("old_string", ""))]
    elif tool == "MultiEdit":
        pairs = [(e.get("new_string", ""), e.get("old_string", ""))
                 for e in inp.get("edits") or []]
    else:
        return

    messages = []

    if fp.endswith(CODE_EXT):
        new_hits, old_hits = [], []
        for new, old in pairs:
            new_hits += find_swallows(new, fp)
            old_hits += find_swallows(old, fp)
        new_swallows = Counter(new_hits) - Counter(old_hits)
        if new_swallows:
            labels = ", ".join(sorted({label for (label, _) in new_swallows}))
            messages.append(
                f"hi-vibe 감지: 방금 `{os.path.basename(fp)}`에 에러 삼킴 패턴이 "
                f"추가됐다 — {labels}. 사용자에게 **한 줄로** 짚어라(길게 설명하지 "
                "말 것): '에러를 삼키면 버그가 조용히 숨어요 — 원인부터 볼까요?' 정도. "
                "왜 위험한지 더 자세한 설명은 **사용자가 물어볼 때만** 하라 "
                "(root-cause-first 계약: 삼키지 말고 전파하거나 fallback 3조건을 "
                "채운다). 정말 의도된 삼킴이면 그 줄에 `hi-vibe: allow-swallow` "
                "주석으로 통과."
            )

    if fp.endswith(SECRET_EXT) and not os.path.basename(fp).startswith(".env"):
        new_sec, old_sec = [], []
        for new, old in pairs:
            new_sec += find_secrets(new)
            old_sec += find_secrets(old)
        new_secrets = Counter(new_sec) - Counter(old_sec)
        if new_secrets:
            labels = ", ".join(sorted({label for (label, _) in new_secrets}))
            messages.append(
                f"hi-vibe 감지: 방금 `{os.path.basename(fp)}`에 실제 비밀키로 보이는 "
                f"문자열이 들어갔다 — {labels}. 이건 드물지만 치명적이라 **왜 위험한지 "
                "한 줄은 항상** 알려라: 코드에 박힌 키는 git 이력에 영구히 남고, 공개 "
                "저장소면 봇이 몇 분 안에 수집해 악용한다. 지금 즉시: (1) 키를 .env로 "
                "옮기고 코드는 환경변수로 읽게 바꿔라 (.env가 .gitignore에 있는지 확인). "
                "(2) 이미 커밋/푸시된 키라면 지우는 것으로는 부족하다 — 서비스에서 키를 "
                "폐기·재발급(rotate)해야 한다고 알려라. 테스트용 가짜 키라면 그 줄에 "
                "`hi-vibe: allow-secret` 주석을 남겨라."
            )

    if messages:
        _common.emit("PostToolUse", additional_context="\n\n".join(messages))


if __name__ == "__main__":
    _common.run(main)

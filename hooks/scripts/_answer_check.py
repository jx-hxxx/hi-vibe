"""답변 검사 — 훅이 **내가 쓴 문장**을 읽는다.

코드에는 검사(테스트·fresh-eyes)가 있지만 **대화에는 아무 장치가 없었다.**
2026-09-05에 그 구멍이 드러났다: 폴백 경로를 평상시 동작으로 착각한 설명을
확인 없이 단정했고, 사용자가 직접 코드를 열어 반박할 때까지 정정되지 않았다.
같은 날 말투 지시(격식체)도 여러 번 어겼다.

두 실패의 성격이 다르므로 다루는 방법도 다르다:

  말투  — 기계가 **판정할 수 있다**. 막으면 실제로 고쳐진다(다시 쓰면 되고,
          올바른 문장을 만들 능력은 이미 있다).
  근거  — 기계가 "이 문장이 단정인가"를 **판정할 수 없다.** 막으면 형식만
          채우게 된다(아무 파일이나 한 번 열어 통과). 그래서 막지 않고
          **드러낸다** — 판단은 사람에게 넘긴다.

이 모듈은 읽고 판정만 한다. 막을지 말지는 `answer_gate.py`가 정한다.
"""
import json
import os
import re
import subprocess

import _transcript


# ── 말투 ──────────────────────────────────────────────────────────────
#
# **금지 목록이 아니라 허용 목록이다.** "-잖아·-거든"을 나열하는 방식은 새
# 말투가 하나 나올 때마다 샌다(사용자 지적, 2026-09-05). 반대로 "격식체로
# 끝났는가"만 보면 목록에 없는 말투도 전부 걸린다 — 빠져나갈 구멍이 없다.
#
# 하십시오체(니다·니까·십시오)와 해요체(세요·까요)를 함께 허용한다. 질문과
# 권유는 해요체가 자연스럽고("말씀해주세요"), 사용자가 문제 삼은 것은
# 반말·축약체(-잖아, -더라고, -임)이지 해요체가 아니다.
_FORMAL_TAIL = re.compile(r"(?:니다|니까|십시오|세요|셔요|까요|줄까요)$")

_HANGUL = re.compile(r"[가-힣]")
# 문장 경계: 마침표·물음표 **뒤에 공백이나 끝**이 와야 한다. 숫자 사이의
# 마침표(0.14%)나 파일명(app.py)에서 자르지 않기 위한 조건이다.
_SENT_SPLIT = re.compile(r"(?<=[.?!])(?=\s|$)")
_TRAIL_PUNCT = re.compile(r'[.?!\s"\'”’」』)\]]+$')


def _strip_uncheckable(text):
    """검사 대상이 아닌 것을 먼저 지운다.

    코드 블록·인용·표는 내 말투가 아니다. 사용자의 말을 그대로 옮긴
    인용까지 걸면, 반말로 물어보신 것을 인용할 수 없게 된다."""
    text = re.sub(r"```.*?```", " ", text, flags=re.S)     # 코드 블록
    text = re.sub(r"`[^`\n]*`", " ", text)                 # 인라인 코드
    text = re.sub(r'"[^"\n]*"', " ", text)                 # 큰따옴표 인용
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith((">", "#", "|", "---", "===")):    # 인용·제목·표·구분선
            continue
        out.append(ln)
    return "\n".join(out)


def informal_sentences(text):
    """격식체로 끝나지 않은 문장들. 없으면 빈 리스트.

    **마침표·물음표로 끝나는 것만 본다.** 목록 항목이나 표의 라벨은 명사로
    끝나는 게 정상이고("탐지 10건 중 2~3건"), 그것까지 걸면 검사가 소음이
    되어 결국 꺼진다."""
    bad = []
    for raw in _SENT_SPLIT.split(_strip_uncheckable(text)):
        s = " ".join(raw.split())
        if not s or s[-1] not in ".?!":
            continue                       # 문장이 아니라 조각 — 대상 아님
        if not _HANGUL.search(s):
            continue                       # 영문·코드 문장은 대상 아님
        core = _TRAIL_PUNCT.sub("", s)
        if not core or not _HANGUL.search(core[-1:]):
            continue                       # 숫자·기호로 끝남 — 판정 보류
        if not _FORMAL_TAIL.search(core):
            bad.append(s[:80])
    return bad


# ── 비유 ──────────────────────────────────────────────────────────────
#
# 종결어미 검사로는 안 잡히는 실패다. "체결이 흐르는 차트가 뜨고"는 문장이
# `않습니다`로 멀쩡히 끝나지만, 데이터는 흐르지 않고 화면은 뜨지 않는다.
# 사용자가 세 번 연속 지적한 자리다(2026-09-05).
#
# **여기만 금지 목록이다.** 종결어미는 닫힌 집합이라 허용 목록이 성립하는데,
# 비유는 닫히지 않는다 — 사실 서술 동사를 전부 나열할 수 없다. 그래서 새는
# 것을 전제로 하고, 대신 **목록을 코드 밖 파일에 뒀다.** 새로 나오면
# `informal_words.txt`에 한 줄만 더하면 된다.

WORDLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "informal_words.txt")


def _banned_words(path=WORDLIST):
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return []          # 목록을 못 읽으면 이 검사만 건너뛴다(fail-open)
    return [w.strip() for w in lines
            if w.strip() and not w.lstrip().startswith("#")]


def metaphors(text, path=WORDLIST):
    """비유 표현이 들어간 문장들. 없으면 빈 리스트."""
    words = _banned_words(path)
    if not words:
        return []
    body = _strip_uncheckable(text)
    hits = []
    for raw in _SENT_SPLIT.split(body):
        s = " ".join(raw.split())
        if not s:
            continue
        found = [w for w in words if w in s]
        if found:
            hits.append((s[:80], found[0]))
    return hits


# ── 근거 ──────────────────────────────────────────────────────────────

# Bash로 읽는 흔한 방법. 이 저장소 작업은 Bash로 파일을 읽는 일이 많아서
# Bash를 통째로 빼면 "읽었는데 안 읽었다"고 잘못 표시한다.
_BASH_READ_RE = re.compile(
    r"\b(?:cat|head|tail|sed|grep|rg|ugrep|less|awk|find|ls|git\s+(?:show|log|diff|blame))\b")

# 끝을 `\b`로 잡으면 **한글 조사가 붙었을 때 안 걸린다** — 파이썬에서 한글도
# `\w`라서 `stop_nudge.py의`에는 경계가 생기지 않는다. 실제로 이 검사를
# 처음 돌렸을 때 조용히 0건이 나왔다. ASCII 낱말 문자만 배제한다.
_FILEISH = re.compile(
    r"[\w./-]*\w+\.(?:py|js|mjs|cjs|jsx|ts|tsx|html|css|json|ya?ml|md|sh|toml)"
    r"(?![A-Za-z0-9_])")


def last_turn(path):
    """(이번 턴에 내가 쓴 텍스트, 이번 턴에 **실제로 건드린 파일** basename 집합).

    '이번 턴'은 **마지막 사용자 메시지 이후**다. 도구 결과로 들어온 user
    항목과 훅이 주입한 것은 사용자 메시지가 아니므로 경계로 세지 않는다."""
    entries = []
    for line in _transcript.tail_lines(path):
        try:
            entries.append(json.loads(line))
        except Exception:
            continue

    start = -1
    for i, e in enumerate(entries):
        if e.get("type") != "user":
            continue
        msg = e.get("message") or {}
        if msg.get("role") != "user":
            continue
        c = msg.get("content")
        if isinstance(c, list) and any(
                isinstance(b, dict) and b.get("type") == "tool_result" for b in c):
            continue                       # 도구 결과 — 사람이 보낸 게 아니다
        if isinstance(c, str) and c.lstrip().startswith("<"):
            continue                       # 훅·시스템 주입
        start = i

    said, touched = [], set()
    for e in entries[start + 1:]:
        if e.get("type") != "assistant":
            continue
        content = (e.get("message") or {}).get("content")
        if isinstance(content, str):
            said.append(content)
            continue
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text":
                said.append(b.get("text", ""))
            elif b.get("type") == "tool_use":
                touched |= _touched_by(b.get("name", ""), b.get("input") or {})
    return "\n".join(said), touched


def _touched_by(name, inp):
    """이 도구 호출이 **어느 파일을** 열었나(basename 집합).

    "무언가 읽었나"로는 부족하다는 것이 2026-09-05 세 번째 실패로 드러났다.
    그때 나는 기술문서를 grep해 놓고 `ai_replay.py`의 동작을 단정했다.
    도구는 돌았으니 "읽음"으로 통과했지만, 정작 말한 파일은 안 열었다.
    그래서 **말한 파일과 연 파일을 맞춰 본다.**"""
    hits = set()
    for key in ("file_path", "notebook_path", "path"):
        v = inp.get(key)
        if isinstance(v, str) and v:
            hits.add(os.path.basename(v.rstrip("/")))
    if name == "Bash":
        cmd = inp.get("command", "")
        if _BASH_READ_RE.search(cmd):
            for m in _FILEISH.finditer(cmd):
                hits.add(os.path.basename(m.group(0)))
    return {h for h in hits if h}


def _repo_files(cwd):
    """git이 아는 파일의 basename 집합. git이 없으면 빈 집합(검사 생략)."""
    try:
        r = subprocess.run(["git", "ls-files"], cwd=cwd, capture_output=True,
                           text=True, timeout=5)
    except Exception:
        return set()
    if r.returncode != 0:
        return set()
    return {os.path.basename(p) for p in r.stdout.split()}


def unverified_mentions(cwd, said, touched):
    """답변이 동작을 설명한 파일 중 **이번 턴에 열지 않은** 것들.

    왜 저장소에 실재하는 것만 세나: 일반적인 파일명(`package.json`)이나
    예시까지 세면 매번 뜨고, 매번 뜨는 표시는 아무도 안 본다.

    왜 파일 단위인가: "무언가 읽었나"는 통과시키기 너무 쉽다. 다른 파일을
    열어 놓고 이 파일을 설명해도 통과했다(2026-09-05 실측). 반대로 파일
    단위면 통과하는 유일한 방법이 **그 파일을 여는 것**이라, 빠져나가는
    행동과 올바른 행동이 같아진다."""
    known = _repo_files(cwd)
    if not known:
        return []
    hits = []
    for m in _FILEISH.finditer(said):
        base = os.path.basename(m.group(0))
        if base in known and base not in touched and base not in hits:
            hits.append(base)
    return hits

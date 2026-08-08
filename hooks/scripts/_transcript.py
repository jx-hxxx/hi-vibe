"""트랜스크립트(대화 기록 JSONL) 읽기 — 요청·수정 파일·Bash 흔적·테스트 결과.

여기 있는 것은 전부 **읽기**다. 기록 원문에서 무엇을 뽑아 어디까지만
남기는지(비밀키를 갖지 않기, 원문 대신 지문)가 이 모듈의 책임이다.
"""
import hashlib
import json
import os
import re
import sys


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

"""handover 쓰기 — 세션이 끝나기 전에 이어갈 단서를 남긴다.

PreCompact와 SessionEnd가 같은 본문 형식을 써야 하므로 조립은 여기
한 곳에만 있다. 회전(rotate)·중복 방지 표식도 같은 생애주기라 함께 산다.
"""
import hashlib
import json
import os

from _base import git_status
from _transcript import (bash_write_summary, last_test_result,
                         parse_transcript, safe_text)


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

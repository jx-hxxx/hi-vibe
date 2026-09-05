"""Stop 훅 — 내가 쓴 답변 자체를 검사한다.

두 가지를 본다. **다루는 방법이 다르다는 것이 이 훅의 핵심이다.**

  1) 말투 — 격식체로 끝나지 않은 문장, 또는 비유 표현이 있으면 **막는다.**
     기계가 판정할 수 있고, 막으면 실제로 고쳐진다(다시 쓰면 되며 올바른
     문장을 만들 능력은 이미 있다). 사용자가 여러 번 지적했는데도 반복된
     실패라, 문서에 적어 두는 층으로는 안 된다는 것이 이미 확인됐다.

  2) 근거 — 저장소에 실재하는 파일을 지목해 설명하면서 이번 턴에 아무것도
     열어 보지 않았으면 **한 줄 표시만 남긴다. 막지 않는다.**

**왜 2)는 안 막나.** 막으면 통과하는 가장 싼 방법이 "아무 파일이나 한 번
여는 것"이 된다. 이 저장소는 이미 그 함정에 빠진 적이 있다 — 리뷰를 하지
않고 "리뷰 끝" 표시만 해서 통과하던 것을 v0.48.0에서 막아야 했다. 형식만
채우게 만드는 강제는 검사가 아니라 검사처럼 보이는 것이다.

그리고 "이 문장이 동작을 단정하는가"는 기계가 판정할 수 없다. 판정할 수
없는 것을 막으면 오탐이 쌓이고, 오탐이 쌓이면 사람이 검사를 끈다. 그래서
판정 대신 **사실만 드러내고** 판단은 사람에게 넘긴다 — 읽은 것이 없다는
사실은 기록에 그대로 있으므로 이 표시에는 추측이 없다.
"""
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _answer_check
import _common


def tone_reason(bad, figs):
    """차단 사유 = 다시 쓰라는 지시. 무엇이 걸렸는지 그대로 보여준다."""
    parts = ["hi-vibe 말투 검사에 걸렸다."]
    if bad:
        shown = "\n".join(f"  - {s}" for s in bad[:5])
        more = f"\n  (그 밖 {len(bad) - 5}개)" if len(bad) > 5 else ""
        parts.append(
            "\n[격식체로 끝나지 않은 문장]\n" + shown + more +
            "\n판정 기준은 `니다·니까·십시오·세요·까요`로 끝나는가다. "
            "금지어 목록이 아니라 **허용 목록**이라 새 말투도 걸린다."
        )
    if figs:
        shown = "\n".join(f"  - {s}   ← `{w}`" for s, w in figs[:5])
        more = f"\n  (그 밖 {len(figs) - 5}개)" if len(figs) > 5 else ""
        parts.append(
            "\n[비유 표현]\n" + shown + more +
            "\n데이터는 흐르지 않고 들어온다. 화면은 뜨지 않고 표시된다. "
            "**사실 서술로 바꿔라.** 목록은 `hooks/scripts/informal_words.txt`에 "
            "있고, 새로 지적받은 표현은 거기 한 줄 더하면 된다."
        )
    parts.append(
        "\n사용자에게 하는 모든 말은 격식체로 쓴다. 위를 고쳐서 **답변을 다시 "
        "써라** — 사과·해명 없이 고친 답만 내라. 그 자리에서 지어낸 축약어가 "
        "있으면 함께 풀어 써라(기계가 못 잡는 종류다).\n"
        "코드 블록·인용부호 안·목록 라벨은 검사 대상이 아니므로 그대로 둬라."
    )
    return "\n".join(parts)


def evidence_note(hits):
    return (
        "hi-vibe: 이번 답변은 "
        + ", ".join(hits[:4])
        + ("등을" if len(hits) > 4 else "을")
        + " 언급했지만 파일을 한 번도 열지 않았습니다.\n"
        "동작 설명이라면 확인 후 답한 것인지 확인해 보세요."
    )


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    _common.touch_heartbeat(cwd, "Stop:answer")
    transcript = payload.get("transcript_path", "")
    if not transcript:
        return

    said, tools = _answer_check.last_turn(transcript)
    if not said.strip():
        return

    flag_dir = os.path.join(cwd, ".hi-vibe", "state")

    # 1) 말투 — 막는다. 단 **같은 답변으로 두 번 막지 않는다.**
    #    `stop_hook_active`는 이 훅 때문에 턴이 이어진 상태라는 뜻이다.
    #    그때 또 막으면 고치는 중에 무한히 걸린다.
    bad = _answer_check.informal_sentences(said)
    figs = _answer_check.metaphors(said)
    if (bad or figs) and not payload.get("stop_hook_active"):
        fingerprint = hashlib.sha1(
            ("\n".join(bad) + "\n" + "\n".join(s for s, _ in figs)
             ).encode("utf-8")).hexdigest()
        if not _already_blocked(flag_dir, fingerprint):
            _remember_block(flag_dir, fingerprint)
            _common.emit("Stop", decision="block",
                         reason=tone_reason(bad, figs))
            return

    # 2) 근거 — 막지 않고 표시만.
    hits = _answer_check.unverified_mentions(cwd, said, tools)
    if hits:
        _common.emit("Stop", system_message=evidence_note(hits))


def _flag(flag_dir):
    return os.path.join(flag_dir, "last_tone_block")


def _already_blocked(flag_dir, fingerprint):
    try:
        with open(_flag(flag_dir), encoding="utf-8") as fh:
            return fh.read().strip() == fingerprint
    except OSError:
        return False


def _remember_block(flag_dir, fingerprint):
    try:
        os.makedirs(flag_dir, exist_ok=True)
        with open(_flag(flag_dir), "w", encoding="utf-8") as fh:
            fh.write(fingerprint + "\n")
    except OSError:
        pass  # 기록 못 해도 막는 것 자체는 유효 — 다음 턴에 한 번 더 걸릴 뿐


if __name__ == "__main__":
    _common.run(main)

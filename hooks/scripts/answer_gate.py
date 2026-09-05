"""Stop 훅 — 내가 쓴 답변 자체를 검사한다.

두 가지를 본다. **다루는 방법이 다르다는 것이 이 훅의 핵심이다.**

  1) 말투 — 격식체로 끝나지 않은 문장, 또는 비유 표현이 있으면 **막는다.**
     기계가 판정할 수 있고, 막으면 실제로 고쳐진다(다시 쓰면 되며 올바른
     문장을 만들 능력은 이미 있다). 사용자가 여러 번 지적했는데도 반복된
     실패라, 문서에 적어 두는 층으로는 안 된다는 것이 이미 확인됐다.

  2) 근거 — 저장소에 실재하는 파일을 지목해 설명하면서 **그 파일을** 이번
     턴에 열지 않았으면 **막는다.**

**왜 파일 단위인가.** 처음에는 "이번 턴에 무언가 읽었나"로 만들었고, 그러면
막을 수 없다고 봤다 — 통과하는 가장 싼 방법이 "아무 파일이나 한 번 여는
것"이 되기 때문이다. 이 저장소는 그 함정을 이미 겪었다(리뷰 없이 `mark`만
해서 통과하던 것을 v0.48.0에서 막았다).

그런데 그 설계로는 **정작 잡아야 할 실패를 못 잡았다.** 2026-09-05 세 번째
실패에서 나는 기술문서를 grep해 놓고 `ai_replay.py`의 동작을 단정했다.
도구는 돌았으니 "읽음"으로 통과한다. 실측으로 확인했다.

**말한 파일과 연 파일을 맞춰 보면 그 문제가 사라진다.** 통과하는 유일한
방법이 "그 파일을 여는 것"이 되므로, 빠져나가는 행동과 올바른 행동이 같다.
형식만 채우는 통과가 성립하지 않으니 막아도 된다.

남는 한계: "이 문장이 동작을 단정하는가"는 여전히 기계가 못 가린다. 그래서
파일 이름을 스치듯 언급만 해도 걸릴 수 있다. 그 대가로 세 번 반복된 실패를
막는다 — 헛걸림은 파일 한 번 여는 비용이고, 놓침은 사용자가 틀린 설명을
믿는 비용이다.
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


def evidence_reason(hits):
    """차단 사유 = 열어 보라는 지시. 어느 파일인지 그대로 준다."""
    shown = ", ".join(f"`{h}`" for h in hits[:6])
    more = f" (그 밖 {len(hits) - 6}개)" if len(hits) > 6 else ""
    return (
        f"hi-vibe 근거 검사: {shown}{more}를 설명하면서 **이번 턴에 그 파일을 "
        "열지 않았다.**\n\n"
        "기억으로 쓴 설명은 확인한 설명과 똑같이 확신에 차서 나온다 — 틀렸다는 "
        "신호가 안 뜬다. 그래서 사람이 아니라 기계가 센다.\n"
        "**지금 그 파일을 열고, 본 것과 답이 같은지 확인한 뒤 답하라.** 다르면 "
        "고쳐 쓰고, 같으면 그대로 두되 근거가 된 줄을 밝혀라.\n"
        "설명이 아니라 스치듯 언급한 것뿐이면 그 이름을 빼고 다시 써라 — "
        "이 검사는 '동작을 단정하는가'를 가리지 못하므로 그 판단은 네가 한다."
    )


def main(payload):
    cwd = payload.get("cwd", "")
    if not _common.project_gate(cwd):
        return
    _common.touch_heartbeat(cwd, "Stop:answer")
    transcript = payload.get("transcript_path", "")
    if not transcript:
        return

    said, touched = _answer_check.last_turn(transcript)
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

    # 2) 근거 — 말한 파일을 안 열었으면 막는다. 말투와 같은 이유로 한 번만.
    hits = _answer_check.unverified_mentions(cwd, said, touched)
    if hits and not payload.get("stop_hook_active"):
        fingerprint = "ev:" + hashlib.sha1(
            "\n".join(hits).encode("utf-8")).hexdigest()
        if not _already_blocked(flag_dir, fingerprint, "last_evidence_block"):
            _remember_block(flag_dir, fingerprint, "last_evidence_block")
            _common.emit("Stop", decision="block",
                         reason=evidence_reason(hits))


def _already_blocked(flag_dir, fingerprint, name="last_tone_block"):
    """사유마다 파일을 따로 쓴다 — 한 파일을 돌려쓰면 뒤에 막은 사유가 앞의
    기억을 덮어써서, 같은 답변에 두 번 걸린다(stop_nudge와 같은 이유)."""
    try:
        with open(os.path.join(flag_dir, name), encoding="utf-8") as fh:
            return fh.read().strip() == fingerprint
    except OSError:
        return False


def _remember_block(flag_dir, fingerprint, name="last_tone_block"):
    try:
        os.makedirs(flag_dir, exist_ok=True)
        with open(os.path.join(flag_dir, name), "w", encoding="utf-8") as fh:
            fh.write(fingerprint + "\n")
    except OSError:
        pass  # 기록 못 해도 막는 것 자체는 유효 — 다음 턴에 한 번 더 걸릴 뿐


if __name__ == "__main__":
    _common.run(main)

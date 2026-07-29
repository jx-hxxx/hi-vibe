"""명령이 "자동"인지 "직접 치는 것"인지를 문서들이 서로 다르게 말하지 않게 한다.

이 검사가 생긴 이유는 실제 재발이다. `review`를 Stop 훅이 직접 실행하도록
바꾼 뒤(v0.17.0), 문서 곳곳에 흩어진 분류를 한 번에 못 고쳐서 **세 번**에
걸쳐 뒤늦게 발견했다:

  1. 랜딩 빠른 시작이 `review`·`find`를 여전히 "치세요" 칸에 두고 있었다
  2. 랜딩 3단 설명이 `find`(AI가 발동)와 `check`(사람이 입력)를 한 칸에 섞었다
  3. README가 `review`·`find`를 "확실히 하려면 직접 호출하세요"로 권했다

셋 다 문장 하나만 보고 그 문장이 속한 **분류**를 안 봐서 생겼다. 사람 눈으로
세 번 놓친 종류이므로 기계가 막는다 (안전장치를 사람 주의력에 기대지 않는다).

여기서 강제하는 것:
  - 명령별 자동/직접 분류가 README 한/영·랜딩 한/영에서 모두 일치
  - 랜딩 기능 카드가 자기 그룹(AUTO/MANUAL)과 반대 성격이 아님
  - 자동으로 도는 명령을 "직접 치세요"라고 권하지 않음
    (놓쳤을 때 쓰는 비상 손잡이라는 단서가 같은 문장에 있으면 통과)
"""
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AUTO, MANUAL = "auto", "manual"

# 단일 기준(SSOT). "사용자가 아닌 무언가가 부르는가"로만 가른다.
COMMAND_MODE = {
    # 사람이 친다 — 설치·진단·켜기는 사람 결정이고, check는 평소에 유일하게
    # 치는 명령이다.
    "welcome": MANUAL,
    "doctor": MANUAL,
    "init": MANUAL,
    "check": MANUAL,
    "gate": MANUAL,
    # 사람이 아닌 것이 부른다.
    "review": AUTO,     # Stop 훅이 직접 실행 (hooks/scripts/stop_nudge.py)
    "handover": AUTO,   # PreCompact 훅 (hooks/scripts/pre_compact.py)
    "find": AUTO,       # "만들어줘"에 write-gate 스킬이 걸림
    "log": AUTO,        # review 체크리스트가 CHANGELOG에 직접 기록
    "recall": AUTO,     # "예전에 왜 이렇게 했지?"에 docs-keeper가 걸림
}

READMES = ("README.md", "README.ko.md")
LANDING = "docs/index.html"


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def _strip_tags(html):
    html = re.sub(r"<svg.*?</svg>", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


# ── 문서에서 분류를 읽어내는 부분 ──────────────────────────────────────────

def _readme_modes(rel):
    """README `명령어 한눈에`의 표들에서 (명령, 분류)를 읽는다.

    자동 표는 **"무엇이 부르나 / What calls it" 열을 가진 표**로 알아본다 —
    소제목 문구가 바뀌어도 따라오게 하려고 열 이름을 기준으로 삼았다."""
    text = _read(rel)
    m = re.search(r"^##\s+(명령어 한눈에|Commands at a glance)\s*$",
                  text, re.M)
    assert m, f"{rel}: `명령어 한눈에` 절을 찾지 못했다 (제목이 바뀌었나?)"
    body = text[m.end():]
    nxt = re.search(r"^##\s+", body, re.M)
    if nxt:
        body = body[:nxt.start()]

    modes, mode = {}, None
    for line in body.splitlines():
        if not line.startswith("|"):
            mode = None          # 표가 끝났다 — 다음 `|`가 새 표의 헤더
            continue
        if mode is None:         # 이 줄이 그 표의 헤더
            mode = AUTO if re.search(r"무엇이 부르나|What calls it", line) else MANUAL
            continue
        for cmd in re.findall(r"`/hi-vibe:([a-z][a-z0-9-]*)`", line):
            modes[cmd] = mode
    return modes


def _landing_modes():
    """랜딩 명령어 표의 `발동` 열(class="fire auto|man")을 읽는다.

    한국어 표와 영어 표를 따로 돌려주므로 둘이 어긋나는 것도 잡힌다."""
    html = _read(LANDING)
    rows = re.findall(
        r"<code>/hi-vibe:([a-z][a-z0-9-]*)</code>\s*</td>\s*<td>.*?"
        r"<span class=\"fire (auto|man)\"",
        html, re.S)
    tables = ({}, {})
    seen = set()
    for cmd, mode in rows:
        # 같은 명령이 두 번째로 나오면 그건 영어 표다.
        idx = 1 if cmd in seen else 0
        seen.add(cmd)
        tables[idx][cmd] = AUTO if mode == "auto" else MANUAL
    return tables


def _landing_card_groups():
    """(그룹 성격, 그룹 이름, [카드 태그...]) 목록."""
    html = _read(LANDING)
    out = []
    for block in html.split('<div class="featcol">')[1:]:
        head = re.search(r'class="ct">([^<]+)</span>\s*<span class="cn">(.*?)</span>',
                         block, re.S)
        if not head:
            continue
        kind = _strip_tags(head.group(2)).strip().upper()
        tags = [t.strip() for t in re.findall(r'class="ftag"><b>([^<]+)', block)]
        out.append((kind, head.group(1).strip(), tags))
    return out


# ── 검사 ──────────────────────────────────────────────────────────────────

class CommandModeConsistencyTest(unittest.TestCase):
    def test_ssot_covers_every_command(self):
        """분류표에 빠진 명령이 없어야 한다 — 새 명령을 추가하면 여기서 걸린다."""
        actual = {os.path.splitext(f)[0]
                  for f in os.listdir(os.path.join(REPO, "commands"))
                  if f.endswith(".md")}
        self.assertEqual(
            sorted(actual), sorted(COMMAND_MODE),
            "commands/와 COMMAND_MODE가 어긋난다 — 새 명령을 만들었으면 "
            "이 파일의 COMMAND_MODE에 자동/직접을 적어라.")

    def test_readmes_agree_with_ssot(self):
        for rel in READMES:
            modes = _readme_modes(rel)
            self.assertEqual(
                sorted(modes), sorted(COMMAND_MODE),
                f"{rel}: 명령어 표가 다루는 명령이 실제 명령 목록과 다르다.")
            wrong = {c: m for c, m in modes.items() if m != COMMAND_MODE[c]}
            self.assertEqual(
                wrong, {},
                f"{rel}: 자동/직접 분류가 실제와 다르다 (기대 "
                f"{ {c: COMMAND_MODE[c] for c in wrong} }). 자동으로 도는 명령을 "
                f"'치는 것' 표에 넣지 마라.")

    def test_landing_agrees_with_ssot(self):
        for i, modes in enumerate(_landing_modes()):
            label = "한국어" if i == 0 else "영어"
            self.assertEqual(
                sorted(modes), sorted(COMMAND_MODE),
                f"랜딩 {label} 명령어 표가 다루는 명령이 실제와 다르다.")
            wrong = {c: m for c, m in modes.items() if m != COMMAND_MODE[c]}
            self.assertEqual(
                wrong, {},
                f"랜딩 {label} 표의 `발동` 열이 실제와 다르다 (기대 "
                f"{ {c: COMMAND_MODE[c] for c in wrong} }).")

    def test_landing_cards_match_their_group(self):
        """AUTO 그룹에 `직접` 카드가, MANUAL 그룹에 `자동` 카드가 있으면 안 된다.

        실제로 `안전벨트가 풀리면 알려줘요`(자동)가 `직접 점검` 칸에 있었다."""
        auto_tag = re.compile(r"^(자동|automatic)$", re.I)
        man_tag = re.compile(r"^(직접|manual)$", re.I)
        bad = []
        for kind, name, tags in _landing_card_groups():
            for tag in tags:
                if kind == "AUTO" and man_tag.match(tag):
                    bad.append(f"AUTO 그룹 '{name}'에 '{tag}' 카드")
                if kind == "MANUAL" and auto_tag.match(tag):
                    bad.append(f"MANUAL 그룹 '{name}'에 '{tag}' 카드")
        self.assertEqual(
            sorted(bad), [],
            "기능 카드가 자기 그룹과 반대 성격이다:\n" + "\n".join(sorted(bad)))


# 자동으로 도는 명령을 "치라"고 시키는 말투. 좁게 잡는다 — 오탐이 나면
# 검사 자체가 무시당하고, 무시당하는 알림은 안전장치가 아니다.
_URGE = re.compile(
    r"직접 호출하세요|직접 호출하시|호출하세요|직접 치세요|직접 실행하세요"
    r"|직접 눌러|call the command|run the command", re.I)

# "평소에 치는 게 아니라 놓쳤을 때 쓰는 손잡이"라는 단서. 같은 문장에 있으면
# 권유가 아니라 안내이므로 통과시킨다.
_FALLBACK = re.compile(
    r"놓친|놓치|안 걸린|못 걸|깜빡|빠뜨|비상|손잡이|보일 때"
    r"|missed|miss it|skip|forget|forgot|didn't fire|latch|emergency", re.I)


class AutoCommandNotUrgedTest(unittest.TestCase):
    """자동으로 도는 명령을 습관처럼 치라고 권하지 않는다.

    권하는 순간 "이건 내가 챙겨야 하는 것"이 되고, 사람이 챙겨야 하는
    안전장치는 안전장치가 아니다. 놓쳤을 때 쓰는 비상 손잡이로 소개하는 건
    괜찮다 — 그 단서가 같은 문장에 있으면 통과한다."""

    @staticmethod
    def offenders(text):
        auto = [c for c, m in COMMAND_MODE.items() if m == AUTO]
        hits = []
        for raw in re.split(r"(?<=[.!?])\s+|\n|<br\s*/?>", text):
            s = " ".join(_strip_tags(raw).split())
            if not s or not _URGE.search(s) or _FALLBACK.search(s):
                continue
            for cmd in auto:
                if re.search(r"/hi-vibe:%s\b" % cmd, s):
                    hits.append((cmd, s[:150]))
        return hits

    def test_docs_do_not_urge_auto_commands(self):
        bad = []
        for rel in READMES + (LANDING,):
            for cmd, sentence in self.offenders(_read(rel)):
                bad.append(f"{rel} ({cmd}): {sentence}")
        self.assertEqual(
            sorted(bad), [],
            "자동으로 도는 명령을 직접 치라고 권한다 — 평소엔 안 친다는 것을 "
            "먼저 말하고, 명령은 '놓쳤을 때 쓰는 비상 손잡이'로 소개하라:\n"
            + "\n".join(sorted(bad)))

    def test_guard_actually_fires(self):
        """실제로 저장소에 있었던 문장을 되살려 잡히는지 확인한다.

        검사가 조용히 아무것도 안 잡게 되는 것을 막는다."""
        old = ("강력하지만 100% 보장되지는 않습니다. 확실히 실행하고 싶다면 "
               "`/hi-vibe:find`, `/hi-vibe:review`처럼 해당 명령을 직접 호출하세요.")
        self.assertTrue(self.offenders(old),
                        "옛날 권유 문장을 못 잡는다 — 검사가 무력해졌다.")
        now = ("평소에 이걸 직접 칠 일은 없습니다. 안 걸린 게 눈에 보일 때 "
               "`/hi-vibe:find`로 손수 채울 수 있다는 것만 알아두세요.")
        self.assertEqual(self.offenders(now), [],
                         "현재 문장을 오탐으로 잡는다.")


if __name__ == "__main__":
    unittest.main()

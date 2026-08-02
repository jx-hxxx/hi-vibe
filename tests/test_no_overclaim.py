"""이미 한 번 과장으로 판명된 주장이 다시 들어오는 것을 막는다.

자연어를 통째로 검증할 수는 없다. 그래서 여기 있는 건 **실제로 문서에
있었고, 사실이 아니어서 고친 문장들**뿐이다 — 상상으로 만든 금지어가
아니라 재발 방지 목록이다. 각 항목에 왜 과장인지와 실제 동작을 적어둔다.

좁게 잡는다: 멀쩡한 문장까지 잡으면 검사가 무시당하고, 무시당하는 검사는
안전장치가 아니다. 대신 여기 걸린 것은 예외 없이 사실이 아니다.
"""
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 검사 대상을 손으로 나열하면, 금지 문구가 목록에 없는 파일로 들어갈 때
# 조용히 통과한다. 그래서 **활성 문서를 그때그때 모은다** — 새 명령·새
# 에이전트·새 스킬을 추가해도 자동으로 검사 범위에 들어온다.
_SKIP_DIRS = {".git", "__pycache__", ".repo-xray", ".hi-vibe", "node_modules",
              ".pytest_cache", "tests"}   # tests/ = 금지 문구를 인용하는 자리
_SKIP_FILES = {"CHANGELOG.md"}            # 과거 릴리스 서술이라 옛 표현을 인용한다
_SCAN_EXT = (".md", ".html", ".tpl", ".py")


def _surfaces():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if name in _SKIP_FILES or not name.endswith(_SCAN_EXT):
                continue
            yield os.path.relpath(os.path.join(root, name), REPO)

# 랜딩 타임라인은 CHANGELOG에서 자동 생성된 *과거 서술*이라 옛 표현을 인용한다.
_SHOWCASE = re.compile(r"<!--\s*SHOWCASE:[a-z]+-start\s*-->.*?"
                       r"<!--\s*SHOWCASE:[a-z]+-end\s*-->", re.S)

# (정규식, 왜 과장인가 / 실제 동작)
BANNED = [
    (r"맥락(이|을)?\s*안\s*(끊|잃)|앞 내용을 까먹지 않|never loses? the thread"
     r"|keeps? (your )?context\b(?!.*enough)",
     "handover가 보존하는 건 최근 요청 5개(각 120자)·수정 파일·Git·테스트 "
     "상태다. 설계 이유나 실패한 접근까지 남기지 않는다 → '이어갈 단서를 "
     "남긴다'로 쓸 것."),

    (r"항상 작동하는 안전벨트|seatbelt that'?s always working|always[- ]on seatbelt",
     "훅은 fail-open이라 조용히 죽을 수 있고, 죽었는지는 heartbeat를 보는 "
     "스킬 층이 돌아야 알 수 있다 → '자동으로 매여 있고, 풀리면 알려주는'."),

    # "runs the review"만 잡다가 **"the hook runs it"을 놓쳤다** — 목적어를
    # 대명사로 쓰면 빠져나간다. 대명사까지 포함한다.
    (r"(훅|hook)[^.\n]{0,40}"
     r"((리뷰|review)를?\s*직접\s*(돌|실행)"
     r"|runs? (the )?(review|it)\b(?![^.\n]{0,20}\bhold)|runs? it right there)"
     # 훅 이름이 주어일 때도 같은 주장이다. 다이어그램의
     # `└─ Stop ── run the review on unreviewed changes`가 이 형태로
     # 살아남았다 — 앞뒤 25자 안에 "훅/hook"이라는 낱말이 없었다.
     r"|Stop[^.\n]{0,25}(그 자리에서\s*리뷰|runs? the review)",
     "Stop 훅은 `decision:block`으로 턴을 막고 reason으로 리뷰를 지시할 뿐, "
     "리뷰를 수행하는 건 Claude다 → '턴을 막고 리뷰를 지시한다'."),

    (r"코드 쓸 때마다[^.\n]{0,30}(잡|감지)|every code write is checked",
     "PostToolUse는 `Write|Edit|MultiEdit`만 본다. Bash로 쓴 파일은 훅에 "
     "안 잡힌다 → 'Write/Edit로 쓸 때마다'로 좁힐 것."),

    (r"Bash[^.\n]{0,30}(전부|모두|다)\s*(즉시\s*)?(검사|감지)"
     r"|all Bash (writes|changes) are (checked|detected)",
     "`bash_wrote_files`는 대표적인 쓰기 명령을 추정할 뿐이다 "
     "(`perl -pi`·`git apply`·빌드 도구는 빠진다)."),

    # 표 셀(`| CLAUDE.md | 프로젝트 전체 지도 |`) 형태였으므로 `|`를 허용한다.
    (r"CLAUDE\.md[^.\n]{0,30}(전체 지도|폴더 지도|folder map|folder structure)",
     "v0.24.0에서 폴더 목록을 뺐다. CLAUDE.md는 코드만 봐서는 모를 것"
     "(제약·함정·결정)만 담는다."),

    (r"첫\s*`?/hi-vibe:log`?\s*때\s*(생|만들)|CHANGELOG[^.\n|]{0,40}lazil",
     "v0.23.0부터 CHANGELOG.md는 init이 만든다."),

    # 랜딩에서 고친 뒤 README에 그대로 남아 하루에 두 번 걸렸다. 손으로 훑는
    # 대신 여기 등록한다 — 이 목록이 있는 이유가 정확히 이런 경우다.
    (r"(이미 있는|원래 있던)\s*좋은 기능[^.\n]{0,30}(연결|불러)"
     r"|wires? the good features"
     r"|리뷰 품질[^.\n]{0,30}(`?/code-review`?|기본)[^.\n]{0,20}(더 )?좋아질"
     r"|[Rr]eview quality[^.\n]{0,40}keep improving",
     "hi-vibe는 `/code-review`를 호출하지 않는다(저장소에 그런 코드가 없다). "
     "자기 체크리스트와 `fresh-eyes` 에이전트로 돈다 → 겹치는 건 목적이지 "
     "구현이 아니다. 로드맵 문장도 방문자용이 아니라 뺐다."),
]


# 금지 문구를 **인용해서 금지하는** 줄(예: CLAUDE.md의 "이렇게 쓰지 말 것")은
# 주장이 아니다. 다른 검사들과 같은 방식으로 그 줄에 마커를 달아 뺀다.
# 정상 문장을 봐주라고 붙이는 용도가 아니다 — 인용일 때만.
ALLOW_MARK = "hi-vibe: allow-overclaim"


def _read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return _SHOWCASE.sub("", f.read())


def _line_at(text, offset):
    start = text.rfind("\n", 0, offset) + 1
    end = text.find("\n", offset)
    return text[start: end if end != -1 else len(text)]


class NoOverclaimTest(unittest.TestCase):
    def test_no_known_overclaim_returns(self):
        hits = []
        for rel in _surfaces():
            text = _read(rel)
            for pattern, why in BANNED:
                for m in re.finditer(pattern, text, re.I):
                    if ALLOW_MARK in _line_at(text, m.start()):
                        continue
                    line = text[:m.start()].count("\n") + 1
                    hits.append(f"{rel}:{line}  {m.group(0)[:70]!r}\n      → {why}")
        self.assertEqual(
            sorted(hits), [],
            "예전에 고쳤던 과장이 다시 들어왔다:\n" + "\n".join(sorted(hits)))

    def test_scan_covers_the_real_surfaces(self):
        """검사 범위가 조용히 좁아지는 것도 막는다.

        손으로 나열하던 시절엔 목록에 없는 파일로 문구가 들어가면 그냥
        통과했다. 이제 동적으로 모으므로, 대표 파일이 빠지면 실패한다."""
        found = set(_surfaces())
        for must in ["README.md", "README.ko.md", os.path.join("docs", "index.html"),
                     "CLAUDE.md", os.path.join("commands", "review.md"),
                     os.path.join("agents", "fresh-eyes.md"),
                     os.path.join("hooks", "scripts", "session_start.py"),
                     os.path.join("skills", "write-gate", "SKILL.md")]:
            self.assertIn(must, found, f"검사 범위에서 빠졌다: {must}")
        self.assertGreater(len(found), 25, f"검사 대상이 {len(found)}개뿐이다")

    def test_guard_actually_fires(self):
        """금지 목록이 조용히 무력해지는 것을 막는다.

        정규식을 잘못 건드려 아무것도 안 잡게 되면 테스트는 계속 통과한다 —
        그게 제일 위험하므로, 실제로 저장소에 있었던 문장으로 확인한다."""
        past = [
            "handover가 자동 기록되니 맥락이 안 끊긴다.",
            "대화가 새로 시작돼도 앞 내용을 까먹지 않아요.",
            "so a fresh chat never loses the thread.",
            "항상 작동하는 안전벨트.",
            "A seatbelt that's always working.",
            "리뷰 안 받은 변경이 있으면 훅이 그 자리에서 review를 직접 돌려요.",
            "the hook runs review itself.",
            "코드 쓸 때마다 에러 삼킴·비밀키를 잡아요.",
            "every code write is checked for error-swallowing",
            "CLAUDE.md | 프로젝트 전체 지도 — 개요·요구사항·폴더 구조",
            "CHANGELOG.md는 첫 /hi-vibe:log 때 생깁니다",
            "이미 있는 좋은 기능을 놓치기 쉬운 순간에 자동으로 연결하고",
            "it wires the good features you already have into the moments",
            "리뷰 품질 자체는 앞으로도 기본 /code-review가 더 좋아질 겁니다",
            "Review quality itself will keep improving in /code-review",
            "└─ Stop ───────── run the review on unreviewed changes",
            "└─ Stop ───────── 리뷰 안 받은 변경을 그 자리에서 리뷰",
        ]
        for sentence in past:
            caught = any(re.search(p, sentence, re.I) for p, _ in BANNED)
            self.assertTrue(
                caught,
                f"실제로 있었던 과장을 못 잡는다 — 검사가 무력해졌다: {sentence!r}")

    def test_current_wording_is_not_flagged(self):
        """지금 쓰는 정직한 표현까지 잡으면 검사가 잔소리가 된다."""
        fine = [
            "handover에 이어갈 단서(최근 요청·수정 파일·Git·테스트 상태)가 자동 기록된다.",
            "it leaves the next chat enough to pick up from",
            "자동으로 매여 있고, 풀리면 알려주는 안전벨트.",
            "훅이 대화를 못 끝내게 붙잡고 그 자리에서 리뷰를 시켜요.",
            "the hook holds the turn open and demands a review.",
            "Claude가 Write/Edit로 코드를 쓸 때마다 에러 삼킴·비밀키를 잡고",
            "CLAUDE.md는 코드만 봐서는 모를 것 — 개요·제약·함정·결정 이유·실행 명령",
            "CHANGELOG.md는 init이 만든다.",
            "같은 목적의 검사를 자기 체크리스트와 자기 에이전트로 돌립니다.",
            "hi-vibe does not press the built-in /code-review for you.",
            "└─ Stop ───────── hold the turn and demand a review of unreviewed changes",
            "└─ Stop ───────── 리뷰 안 받은 변경이 있으면 대화를 붙잡고 리뷰를 지시",
        ]
        for sentence in fine:
            hit = [why for p, why in BANNED if re.search(p, sentence, re.I)]
            self.assertEqual(hit, [], f"정상 문장을 오탐으로 잡는다: {sentence!r}")


if __name__ == "__main__":
    unittest.main()

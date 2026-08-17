"""저장소 무결성 — 문서·템플릿이 실제와 어긋나지 않게 기계로 강제한다.

hi-vibe가 스스로에게 문서-코드 동기화 규율을 적용하는 자리:
1. 활성 파일이 참조하는 `/hi-vibe:<명령>`은 전부 실제 존재해야 한다
   (과거 `/hi-vibe:audit` 오타 같은 깨진 참조를 CI에서 잡는다).
2. README·랜딩이 광고하는 "자동 테스트 N개"는 실제 테스트 함수 수와 같아야
   한다 (숫자가 조용히 낡는 것을 막는다).
"""
import os
import re
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_SKIP_DIRS = {".git", "__pycache__", ".repo-xray", ".hi-vibe",
             ".pytest_cache", "node_modules"}
# CHANGELOG는 과거 릴리스 기록이라 이름이 바뀐 옛 명령을 언급할 수 있다 — 제외.
_SKIP_FILES = {"CHANGELOG.md"}
_SCAN_EXT = (".md", ".yml", ".yaml", ".html", ".json")


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# SHOWCASE 마커 안(랜딩 타임라인)은 CHANGELOG에서 자동 생성된 *역사 서술*이라
# 이름이 바뀐 옛 명령을 언급할 수 있다 — 명령 참조 검사에서 제외한다.
# (CHANGELOG 자체를 제외하는 것과 같은 이유. 그 CHANGELOG가 랜딩에 복사되므로
#  랜딩에서도 같은 영역을 도려내야 한다.)
_SHOWCASE_RE = re.compile(r"<!--\s*SHOWCASE:[a-z]+-start\s*-->.*?"
                          r"<!--\s*SHOWCASE:[a-z]+-end\s*-->", re.S)


def _read_active(path):
    """명령 참조 검사용: 역사 서술(SHOWCASE 타임라인)을 뺀 본문."""
    return _SHOWCASE_RE.sub("", _read(path))


def _active_files():
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS]
        for name in files:
            if name in _SKIP_FILES or not name.endswith(_SCAN_EXT):
                continue
            yield os.path.join(root, name)


# 저자 개인 이름·호칭. `jx-hxxx`(GitHub 핸들)는 공개 정보라 대상이 아니다.
_PERSONAL_NAME_RE = re.compile(r"지현|(?<![\w/-])jihyun(?![\w-])", re.I)

# "자동 테스트 N개"를 광고하는 표현들. 위치가 아니라 **표현**으로 잡으므로,
# 문구를 새 파일·새 문단에 추가해도 자동으로 검사 대상이 된다.
_ADVERTISED_COUNT_RES = [
    re.compile(r"(\d+)\s*(?:automated|regression)\s+tests?\b"),
    re.compile(r"·\s*(\d+)\s+regression\b"),
    re.compile(r"(\d+)\s*개의?\s*자동\s*테스트"),
    re.compile(r"회귀\s*테스트\s*\n?\s*(\d+)\s*개"),
    re.compile(r"<b>(\d+)</b>\s*<span>[^<]*(?:테스트|tests)"),
]
# 표현을 통째로 갈아엎어 검사가 0건이 되는 것을 막는 하한.
# v0.37.0에서 README를 설치 안내만 남기고 줄이면서 **테스트 수 광고가
# 랜딩 한·영 두 곳으로 줄었다** — 숫자를 여러 곳에 쓰지 않는 게 원래 목표라
# 하한을 낮춘다. 0이 되면 검사가 무의미해지므로 2는 지킨다.
_MIN_ADVERTISED_SPOTS = 2


def _actual_test_count():
    tests_dir = os.path.join(REPO, "tests")
    n = 0
    for name in os.listdir(tests_dir):
        if name.startswith("test_") and name.endswith(".py"):
            n += len(re.findall(r"^\s*def test_", _read(os.path.join(tests_dir, name)), re.M))
    return n


class RepoIntegrityTest(unittest.TestCase):
    def test_all_command_references_exist(self):
        cmd_dir = os.path.join(REPO, "commands")
        commands = {os.path.splitext(f)[0] for f in os.listdir(cmd_dir)
                    if f.endswith(".md")}
        ref = re.compile(r"/hi-vibe:([a-z][a-z0-9-]*)")
        bad = set()
        for path in _active_files():
            for m in ref.finditer(_read_active(path)):
                if m.group(1) not in commands:
                    bad.add(f"{os.path.relpath(path, REPO)} → /hi-vibe:{m.group(1)}")
        self.assertEqual(
            sorted(bad), [],
            "존재하지 않는 명령을 참조한다:\n" + "\n".join(sorted(bad)))

    def test_no_personal_names_in_public_docs(self):
        """공개 문서에 저자 개인 이름·호칭이 들어가면 안 된다.

        두 번 일어났다 — 한 번 고치고, 나중에 문서를 다시 쓰면서 또 들어갔다.
        사람이 눈으로 잡는 걸론 두 번 다 놓쳤으므로 기계가 막는다
        (안전장치를 사람 주의력에 기대지 않는다).

        `jx-hxxx`(GitHub 핸들)와 저장소 URL은 공개 정보라 예외."""
        leaked = []
        for path in _active_files():
            text = _read(path)
            for m in _PERSONAL_NAME_RE.finditer(text):
                line = text[:m.start()].count("\n") + 1
                leaked.append(f"{os.path.relpath(path, REPO)}:{line} → {m.group(0)}")
        self.assertEqual(
            sorted(leaked), [],
            "공개 문서에 개인 이름이 들어갔다 (일반 표현으로 바꿔라):\n"
            + "\n".join(sorted(leaked)))

    def test_doctor_only_points_at_docs_init_creates(self):
        """doctor가 "없으니 init 하라"고 안내하는 문서는 init이 실제로 만들어야 한다.

        실제로 깨졌던 자리다: doctor는 `CHANGELOG.md`가 없다고 경고하면서
        `/hi-vibe:init`을 안내했는데, docs-keeper는 init에서 CHANGELOG를
        만들지 않았다. **몇 번을 다시 쳐도 경고가 안 없어지는 막다른 길**이
        됐고, 정작 중요하게 여긴 트러블슈팅 기록이 시작되지 않았다."""
        doctor = _read(os.path.join(REPO, "scripts", "doctor.py"))
        m = re.search(r'docs\s*=\s*\[d for d in \(([^)]*)\)', doctor)
        self.assertIsNotNone(
            m, "doctor.py에서 문서 검사 목록을 찾지 못했다 — 코드가 바뀌었으면 "
               "이 테스트의 추출 방식도 같이 고쳐라(조용히 통과시키지 말 것).")
        checked = re.findall(r'"([^"]+\.md)"', m.group(1))
        self.assertTrue(checked, "doctor가 검사하는 문서 이름을 못 읽었다")

        skill = _read(os.path.join(REPO, "skills", "docs-keeper", "SKILL.md"))
        bad = [d for d in checked
               if re.search(r"Do NOT create[^\n]*\b%s\b" % re.escape(d), skill)]
        self.assertEqual(
            bad, [],
            "doctor는 이 문서가 없다고 init을 안내하는데, docs-keeper는 init에서 "
            "만들지 않는다 (다시 쳐도 안 생기는 막다른 길): " + ", ".join(bad))

    def test_advertised_test_count_matches_reality(self):
        """정해진 몇 곳이 아니라 **활성 문서 전체**를 훑는다.

        예전엔 (파일, 정규식) 6쌍만 검사해서, 문구를 새로 하나 더 추가하면
        그 숫자는 아무도 안 보고 조용히 낡았다 — 실제로 겪은 실패 모드다.
        이제 "테스트 수를 광고하는 표현"을 문서 어디에 써도 걸린다."""
        actual = _actual_test_count()
        advertised, seen_files = [], set()
        for path in _active_files():
            text = _read_active(path)   # 랜딩 타임라인(과거 릴리스 서술)은 제외
            for pat in _ADVERTISED_COUNT_RES:
                for m in pat.finditer(text):
                    rel = os.path.relpath(path, REPO)
                    advertised.append((rel, int(m.group(1))))
                    seen_files.add(rel)

        # 표현을 통째로 바꿔 검사가 조용히 0건이 되는 것도 실패로 본다.
        self.assertGreaterEqual(
            len(advertised), _MIN_ADVERTISED_SPOTS,
            f"테스트 수 광고 문구를 {len(advertised)}곳에서만 찾았다 "
            f"(최소 {_MIN_ADVERTISED_SPOTS}곳 기대) — 문구가 바뀌었으면 "
            f"_ADVERTISED_COUNT_RES에 패턴을 추가하라. 찾은 파일: "
            f"{sorted(seen_files)}")

        wrong = sorted({(rel, n) for rel, n in advertised if n != actual})
        self.assertEqual(
            wrong, [],
            f"광고 테스트 수 != 실제({actual}개): {wrong} — README/랜딩 숫자를 갱신하라.")


class SiteLinkLanguageTest(unittest.TestCase):
    """README의 사이트 링크가 **자기 언어의** 랜딩을 열어야 한다.

    랜딩은 한/영이 한 파일 안에 있고 `localStorage`에 저장된 선택이 우선이라,
    링크에 아무것도 안 붙이면 **영문 README에서 눌러도 한국어 페이지가 뜬다**
    (전에 한국어로 본 적이 있으면). 그래서 `?lang=`으로 명시한다.

    이 저장소는 한쪽만 고치고 반대쪽을 안 보는 사고를 여러 번 겪었다
    (FAQ 답·평가 프롬프트·히어로 문구·강제 개행). 링크도 같은 유형이라
    사람 눈이 아니라 기계가 지킨다."""

    SITE = "https://jx-hxxx.github.io/hi-vibe/"

    def _links(self, name):
        return re.findall(re.escape(self.SITE) + r"[^)\s]*", _read(os.path.join(REPO, name)))

    def test_each_readme_points_at_its_own_language(self):
        for name, lang in (("README.md", "en"), ("README.ko.md", "ko")):
            links = self._links(name)
            self.assertTrue(links, f"{name}에 사이트 링크가 없다")
            for url in links:
                self.assertIn(f"?lang={lang}", url,
                              f"{name}의 링크가 {lang} 페이지를 안 연다: {url}")

    def test_landing_actually_honours_the_parameter(self):
        """링크만 고치고 랜딩이 안 받으면 파라미터는 장식이 된다."""
        page = _read(os.path.join(REPO, "docs", "index.html"))
        self.assertIn("lang=(ko|en)", page,
                      "랜딩에 ?lang= 처리가 없다 — README 링크가 무시된다")

    def test_url_parameter_wins_over_the_saved_choice(self):
        """저장된 선택이 이기면 링크를 눌러도 엉뚱한 언어가 나온다.

        순서가 뒤집히는 것을 막는다: urlLang을 먼저 넣고, 그게 없을 때만
        localStorage를 본다."""
        page = _read(os.path.join(REPO, "docs", "index.html"))
        url_at = page.find("var savedLang = urlLang")
        saved_at = page.find("localStorage.getItem('hv-lang')")
        self.assertGreater(url_at, 0, "urlLang을 먼저 쓰는 코드가 없다")
        self.assertLess(url_at, saved_at,
                        "저장된 선택을 URL보다 먼저 읽는다 — 순서가 뒤집혔다")


class NoteLineBreakTest(unittest.TestCase):
    """안내 상자의 문장은 `<br>`이 아니라 `<span class="ln">`으로 나눈다.

    `<br>`로 나누면 **줄바꿈으로 나눈 문장**과 **길어서 접힌 줄**이 똑같이
    왼쪽 끝에서 시작해 구분이 안 된다. 내어쓰기(`text-indent`)는 블록의
    첫 줄에만 걸리므로 줄마다 블록이 있어야 한다.

    이 저장소에서 같은 실수를 두 번 했다(`.tiers` 한 번, `.honest-note`
    한 번). 셋째 번을 막는다 — 화면을 좁혀 보기 전에는 안 보이는 종류다.
    상자 구조 자체를 바꾸게 되면 이 검사도 같이 떠나야 한다."""

    TAG = re.compile(r"<(/?)(\w+)([^>]*?)(/?)>")
    OPENERS = ('<div class="honest-note">', '<div class="tbody">')

    def _blocks(self):
        """여는 태그부터 **짝이 맞는** </div>까지. 처음엔 "다음 상자까지"로
        잘랐다가 옆 블록을 같이 물어 엉뚱한 곳을 지적했다 — 태그 깊이를 센다."""
        page = _read(os.path.join(REPO, "docs", "index.html"))
        found = []
        for opener in self.OPENERS:
            pos = 0
            while True:
                i = page.find(opener, pos)
                if i < 0:
                    break
                depth, end = 0, None
                for m in self.TAG.finditer(page, i):
                    if m.group(2).lower() != "div":
                        continue
                    depth += -1 if m.group(1) == "/" else 1
                    if depth == 0:
                        end = m.end()
                        break
                self.assertIsNotNone(end, "짝 없는 div: %s" % opener)
                found.append(page[i:end])
                pos = end
        return found

    def test_notes_exist(self):
        self.assertGreater(len(self._blocks()), 8, "안내 상자를 못 찾았다 — 검사가 헛돈다")

    def test_no_bare_br_inside_notes(self):
        offenders = [re.sub(r"<svg.*?</svg>", "", n, flags=re.S)[:70]
                     for n in self._blocks() if "<br>" in n]
        self.assertEqual(offenders, [],
                         "안내 상자 안에 <br>가 있다 — 접힌 줄과 구분이 안 된다. "
                         '<span class="ln">으로 감싸라.')

    def test_line_blocks_get_the_hanging_indent(self):
        page = _read(os.path.join(REPO, "docs", "index.html"))
        m = re.search(r"\.honest-note \.ln[^{]*\{([^}]*)\}", page)
        self.assertTrue(m, ".honest-note .ln 규칙이 없다 — 감싸기만 하고 스타일이 없으면 헛일이다")
        rule = m.group(1)
        self.assertIn("display:block", rule.replace(" ", ""), ".ln이 블록이 아니면 내어쓰기가 안 걸린다")
        self.assertIn("text-indent:-", rule.replace(" ", ""), "내어쓰기가 없다")

    def test_heading_lines_are_wholly_bold(self):
        """`.hd`(앞을 더 띄우는 소제목)는 **줄 전체가 굵은 것**만이다.

        처음엔 CSS `:has(> b:only-child)`로 골라내려 했는데, "굵은 머리말 +
        일반 글" 줄까지 잡혀서 나란한 항목 둘이 다른 간격을 받았다. 판정을
        표시로 옮긴 이상, 표시가 실제와 맞는지는 기계가 봐야 한다."""
        page = _read(os.path.join(REPO, "docs", "index.html"))
        wrong = []
        for inner in re.findall(r'<span class="ln hd">(.*?)</span>\s*(?=<span|</div>)', page, re.S):
            t = inner.strip()
            if not (t.startswith("<b>") and t.endswith("</b>") and t.count("<b>") == 1):
                wrong.append(re.sub(r"<[^>]+>", "", t)[:40])
        self.assertEqual(wrong, [], "줄 전체가 굵지 않은데 소제목(.hd)으로 표시됐다")


class LinkPreviewTest(unittest.TestCase):
    """카톡·슬랙에 링크를 붙였을 때 뜨는 미리보기 카드를 지킨다.

    `og:image`가 없는 파일을 가리켜도 페이지는 멀쩡히 열린다 — 깨진 건
    **남한테 보낸 링크에서만** 보인다. 우리가 볼 일이 없는 자리라 기계가
    지켜야 한다. 예전엔 파비콘(정사각)을 걸고 `twitter:card`도 `summary`라
    작은 아이콘만 떴다."""

    def _head(self):
        page = _read(os.path.join(REPO, "docs", "index.html"))
        return page[:page.find("<style>")]

    def test_preview_image_file_actually_exists(self):
        m = re.search(r'property="og:image"\s+content="([^"]+)"', self._head())
        self.assertTrue(m, "og:image 태그가 없다 — 미리보기에 그림이 안 뜬다")
        name = m.group(1).split("?")[0].rsplit("/", 1)[-1]
        path = os.path.join(REPO, "docs", "images", name)
        self.assertTrue(os.path.exists(path), f"og:image가 없는 파일을 가리킨다: {name}")

    def test_preview_image_is_the_wide_card_shape(self):
        """1.91:1이 아니면 카톡이 제멋대로 잘라낸다."""
        import struct
        head = self._head()
        name = re.search(r'property="og:image"\s+content="([^"]+)"', head).group(1)
        name = name.split("?")[0].rsplit("/", 1)[-1]
        with open(os.path.join(REPO, "docs", "images", name), "rb") as fh:
            w, h = struct.unpack(">II", fh.read(24)[16:24])
        self.assertAlmostEqual(w / h, 1.91, delta=0.05,
                               msg=f"미리보기 그림이 와이드 카드 비율이 아니다: {w}x{h}")
        self.assertEqual((w, h), (1200, 630), "권장 크기 1200x630에서 벗어났다")

    def test_declared_size_matches_the_real_file(self):
        """og:image:width/height가 실제와 다르면 크롤러가 잘못 자른다."""
        import struct
        head = self._head()
        name = re.search(r'property="og:image"\s+content="([^"]+)"', head).group(1)
        name = name.split("?")[0].rsplit("/", 1)[-1]
        with open(os.path.join(REPO, "docs", "images", name), "rb") as fh:
            w, h = struct.unpack(">II", fh.read(24)[16:24])
        for prop, real in (("og:image:width", w), ("og:image:height", h)):
            m = re.search(r'property="%s"\s+content="(\d+)"' % re.escape(prop), head)
            self.assertTrue(m, f"{prop} 태그가 없다")
            self.assertEqual(int(m.group(1)), real, f"{prop}가 실제 그림과 다르다")

    def test_card_is_the_large_image_kind(self):
        self.assertIn('name="twitter:card" content="summary_large_image"', self._head(),
                      "카드가 작은 아이콘형(summary)이면 첫 화면이 안 보인다")

    def test_both_preview_images_point_at_the_same_picture(self):
        head = self._head()
        og = re.search(r'property="og:image"\s+content="([^"]+)"', head).group(1)
        tw = re.search(r'name="twitter:image"\s+content="([^"]+)"', head).group(1)
        self.assertEqual(og, tw, "og와 twitter가 서로 다른 그림을 가리킨다")


class AgentIsCalledFreshEyesTest(unittest.TestCase):
    """에이전트를 사용자에게 부르는 이름은 `fresh-eyes` 하나여야 한다.

    별명("남의 눈")이 섞이면 사용자가 세션 기록에서 무엇이 돌았는지 못 찾는다.
    이건 취향이 아니라 사용자가 직접 요청한 것이고(2026-08-17), 프롬프트에
    적기만 한 규칙은 조용히 되돌아가므로 여기서 기계로 붙잡는다.

    두 자리만 예외다 — ①사용자가 여전히 "남의 눈으로 봐줘"라고 부를 수 있어야
    하므로 **트리거 문구**는 남긴다 ②금지어 자체를 인용하는 규칙 문장.
    둘 다 아래 마커로 식별한다.
    """
    BANNED = "남의 눈"
    # 이 문자열이 같은 줄에 있으면 의도된 예외다.
    ALLOWED_ON_LINE = ("남의 눈으로 봐줘",   # 트리거 문구 (호출 경로 보존)
                       "바꿔 부르지 마라")   # 금지어를 인용하는 규칙 문장
    # 사용자 눈에 닿는 글이 나오는 곳. CHANGELOG는 과거 기록이라 뺀다
    # (랜딩 타임라인은 최신 3개만 렌더링하므로 옛 이름이 화면에 안 나온다).
    FILES = ("agents/fresh-eyes.md",
             "skills/write-gate/SKILL.md",
             "scripts/doctor.py",
             "docs/index.html")

    def test_no_nickname_in_user_facing_text(self):
        offenders = []
        for rel in self.FILES:
            path = os.path.join(REPO, *rel.split("/"))
            for n, line in enumerate(_read(path).splitlines(), 1):
                if self.BANNED not in line:
                    continue
                if any(ok in line for ok in self.ALLOWED_ON_LINE):
                    continue
                offenders.append(f"{rel}:{n}  {line.strip()[:70]}")
        self.assertEqual(offenders, [],
                         "'남의 눈' 대신 'fresh-eyes'로 부를 것:\n" +
                         "\n".join(offenders))

    def test_verdict_line_uses_the_real_name(self):
        """판정 첫 줄은 사용자가 가장 많이 보는 문장이다."""
        agent = _read(os.path.join(REPO, "agents", "fresh-eyes.md"))
        self.assertIn("fresh-eyes 판정: 통과", agent,
                      "판정 형식이 바뀌었다 — 첫 줄이 fresh-eyes로 시작해야 한다")

    def test_trigger_phrase_still_works(self):
        """이름을 바꾸느라 호출 경로를 잃으면 안 된다."""
        agent = _read(os.path.join(REPO, "agents", "fresh-eyes.md"))
        self.assertIn("남의 눈으로 봐줘", agent,
                      "옛 이름으로 부르던 사용자가 에이전트를 못 부르게 된다")


class ReviewLayersDoNotOverlapTest(unittest.TestCase):
    """리뷰 두 겹이 **같은 것을 두 번 보지 않는지.**

    체크리스트(write-gate)는 이 파일 안의 빠뜨림을, fresh-eyes는 파일 사이
    어긋남과 판단 착오를 본다. 2026-08-17에 `숨은 결합`이 양쪽에 **같은
    문장으로** 들어 있는 걸 발견해 fresh-eyes 쪽을 뺐다. 항목 개수를 세지
    않는 이유는 문서 모양을 붙잡지 않기 위해서다 — 겹침만 본다.
    """
    AGENT = os.path.join("agents", "fresh-eyes.md")
    GATE = os.path.join("skills", "write-gate", "SKILL.md")
    NOT_MY_JOB = "## 판단하지 않을 것"

    def _agent(self):
        return _read(os.path.join(REPO, self.AGENT))

    def test_hidden_coupling_belongs_to_the_checklist_alone(self):
        gate = _read(os.path.join(REPO, self.GATE))
        self.assertIn("숨은 결합을 새로 만들지 않았는가", gate,
                      "체크리스트에서 숨은 결합이 사라졌다 — 그럼 아무도 안 본다")
        text = self._agent()
        split = text.find(self.NOT_MY_JOB)
        self.assertGreater(split, 0, f"{self.AGENT}에 '판단하지 않을 것' 절이 없다")
        self.assertNotIn("숨은 결합", text[:split],
                         "숨은 결합이 fresh-eyes의 판단 항목으로 돌아왔다 — "
                         "체크리스트 7번과 겹쳐 사용자가 같은 지적을 두 번 읽는다")

    def test_findings_must_state_concrete_damage(self):
        """값 낮은 항목을 거르는 문이다. 이게 빠지면 '고쳐서 나쁠 건 없다'가 돌아온다."""
        self.assertIn("안 고치면", self._agent(),
                      "재고 항목에서 '안 고치면 무슨 일이 나는가' 요구가 사라졌다")

    def test_cross_file_drift_is_the_first_item(self):
        """제일 잘 잡는 것을 1번에 둔 것이 이번 재배치의 핵심이다."""
        text = self._agent()
        head = text[text.find("## 판단할 것"):]
        self.assertRegex(head[:400], r"1\.\s*\*\*끝까지 갔나",
                         "'끝까지 갔나'가 1번이 아니다")


if __name__ == "__main__":
    unittest.main()

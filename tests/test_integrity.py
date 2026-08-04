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


if __name__ == "__main__":
    unittest.main()

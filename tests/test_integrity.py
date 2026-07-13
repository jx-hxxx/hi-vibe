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

    def test_advertised_test_count_matches_reality(self):
        actual = _actual_test_count()
        # README·랜딩이 광고하는 테스트 수(안정적인 위치들).
        advertised = []
        for rel, pat in [
            ("README.md", r"### (\d+) automated tests"),
            ("README.md", r"·\s*(\d+) regression"),
            ("README.ko.md", r"### (\d+)개의 자동 테스트"),
            ("README.ko.md", r"·\s*회귀 테스트\s*\n(\d+)개"),
            ("docs/index.html", r"<b>(\d+)</b><span>자동 회귀 테스트"),
            ("docs/index.html", r"<b>(\d+)</b><span>automated regression tests"),
        ]:
            found = re.findall(pat, _read(os.path.join(REPO, rel)))
            self.assertTrue(found, f"{rel}: 광고 테스트 수를 못 찾음 (패턴 낡음?)")
            advertised += [(rel, int(x)) for x in found]
        wrong = [(rel, n) for rel, n in advertised if n != actual]
        self.assertEqual(
            wrong, [],
            f"광고 테스트 수 != 실제({actual}개): {wrong} — README/랜딩 숫자를 갱신하라.")


if __name__ == "__main__":
    unittest.main()

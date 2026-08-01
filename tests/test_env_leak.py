"""`.env`가 Git에 올라간 것을 잡는 검사 — 경계값 고정.

비밀키 검사는 `.env*`를 "키를 둬도 되는 자리"로 보고 **검사에서 뺀다**.
그래서 그 파일이 커밋되면 훅도 스캐너도 안 본다 — 구멍이 아니라 검사 대상
밖이라 영영 안 걸린다. 그 하나를 doctor가 대신 본다.

이 파일이 생긴 이유: 처음 구현은 테스트 없이 들어갔고, 곧바로 두 가지가
틀렸다.
  1. `name.startswith(".env")` — direnv의 `.envrc`까지 유출로 몰았다
  2. `.gitignore`에서 `".env"` 문자열만 찾음 — 주석 `# .env`와 무시 해제
     `!.env`까지 "안전함"으로 읽었다 (둘 다 실제로는 정반대)

둘 다 "주요 경로는 잘 도는데 경계에서 틀리는" 종류라 사람 눈으로는 안
보인다. 그래서 경계값을 여기 고정한다.
"""
import os
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import doctor  # noqa: E402


def _git(root, *args):
    return subprocess.run(["git"] + list(args), cwd=root,
                          capture_output=True, text=True, timeout=20)


class EnvFileNameTest(unittest.TestCase):
    """어떤 파일명이 '비밀이 든 .env'인가 — 넓게 잡으면 멀쩡한 파일을 잡는다."""

    def test_real_secret_files(self):
        for name in [".env", ".env.local", ".env.production", ".env.development",
                     ".env.test.local"]:
            self.assertTrue(doctor.is_env_secret_file(name), name)

    def test_samples_are_not_secrets(self):
        """견본은 값이 아니라 형식이라 커밋하는 게 맞다."""
        for name in [".env.example", ".env.sample", ".env.template", ".env.dist"]:
            self.assertFalse(doctor.is_env_secret_file(name), name)

    def test_lookalikes_are_not_secrets(self):
        """`.envrc`(direnv 설정)는 커밋해도 되는 파일이다 — 실제 오탐이었다."""
        for name in [".envrc", ".environment", ".envoy", "env", ".e", "env.py",
                     "environment.yml"]:
            self.assertFalse(doctor.is_env_secret_file(name), name)


class EnvIgnoreTest(unittest.TestCase):
    """`.gitignore` 판정은 Git에게 시킨다 — 문자열 검색으로는 못 맞춘다."""

    def _repo(self, gitignore=None, files=None, commit=True):
        root = tempfile.mkdtemp(prefix="vibe-env-")
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        if gitignore is not None:
            with open(os.path.join(root, ".gitignore"), "w", encoding="utf-8") as f:
                f.write(gitignore)
        for rel in (files or []):
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write("KEY=abc\n")
        if commit:
            _git(root, "add", "-A", "-f")
            _git(root, "commit", "-qm", "x")
        return root

    def test_plain_rule_is_ignored(self):
        self.assertIs(doctor.env_is_ignored(self._repo(gitignore=".env\n")), True)

    def test_comment_is_not_a_rule(self):
        """`# TODO: .env 추가`는 아무 효과가 없다 — 예전엔 OK로 읽혔다."""
        self.assertIs(
            doctor.env_is_ignored(self._repo(gitignore="# TODO: 나중에 .env 추가\n")),
            False)

    def test_negation_is_not_protection(self):
        """`!.env`는 오히려 무시를 **푸는** 규칙이다 — 예전엔 OK로 읽혔다."""
        self.assertIs(
            doctor.env_is_ignored(self._repo(gitignore="*\n!.env\n")), False)

    def test_no_gitignore(self):
        self.assertIs(doctor.env_is_ignored(self._repo()), False)

    def test_not_a_git_repo(self):
        """git 저장소가 아니면 판정 불가 — 없는 경고를 만들지 않는다."""
        with tempfile.TemporaryDirectory(prefix="vibe-nogit-") as root:
            self.assertIsNone(doctor.env_is_ignored(root))


class TrackedEnvTest(unittest.TestCase):
    def setUp(self):
        doctor.results.clear()

    def _repo(self, files, gitignore=None):
        root = tempfile.mkdtemp(prefix="vibe-track-")
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        if gitignore:
            with open(os.path.join(root, ".gitignore"), "w", encoding="utf-8") as f:
                f.write(gitignore)
        for rel in files:
            path = os.path.join(root, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write("KEY=abc\n")
        _git(root, "add", "-A", "-f")
        _git(root, "commit", "-qm", "x")
        return root

    def test_tracked_env_is_found(self):
        root = self._repo([".env"])
        self.assertEqual(doctor.tracked_env_files(root), [".env"])

    def test_env_local_is_found(self):
        root = self._repo([".env.local"])
        self.assertEqual(doctor.tracked_env_files(root), [".env.local"])

    def test_nested_env_is_found(self):
        """루트에만 있는 게 아니다 — `config/.env`도 유출이다."""
        root = self._repo(["config/.env"])
        self.assertEqual(doctor.tracked_env_files(root), ["config/.env"])

    def test_example_and_envrc_are_left_alone(self):
        root = self._repo([".env.example", ".envrc"])
        self.assertEqual(doctor.tracked_env_files(root), [])

    def test_not_a_git_repo_is_quiet(self):
        with tempfile.TemporaryDirectory(prefix="vibe-nogit-") as root:
            self.assertEqual(doctor.tracked_env_files(root), [])

    def _status(self, root):
        doctor.results.clear()
        doctor.check_env_secrets(root)
        return [(s, label) for s, label, _ in doctor.results]

    def test_reports_fail_when_tracked(self):
        self.assertEqual(self._status(self._repo([".env"])),
                         [("FAIL", ".env 유출")])

    def test_reports_ok_when_ignored(self):
        self.assertEqual(self._status(self._repo(["a.py"], gitignore=".env\n")),
                         [("OK", ".env 유출")])

    def test_reports_warn_when_only_a_comment(self):
        """주석만 있는데 OK가 나오면 사용자는 안전하다고 믿는다."""
        self.assertEqual(self._status(self._repo(["a.py"], gitignore="# .env\n")),
                         [("WARN", ".env 유출")])

    def test_says_nothing_outside_a_repo(self):
        with tempfile.TemporaryDirectory(prefix="vibe-nogit-") as root:
            self.assertEqual(self._status(root), [])


if __name__ == "__main__":
    unittest.main()

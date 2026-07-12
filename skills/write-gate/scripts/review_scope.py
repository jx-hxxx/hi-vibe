#!/usr/bin/env python3
"""review_scope — what still needs reviewing, and mark things reviewed.

Powers `/hi-vibe:review --all` (batch review of a whole session's changes):
a session may build several features, so one review should cover them all —
and code that was already reviewed AND hasn't changed since should be skipped.

The "what changed" and "did it change since I reviewed it" judgments are done
here in code (deterministic), NOT by the AI — the AI is unreliable at hashing.

  list  [--root R]        -> JSON {"to_review":[...], "skipped":[...]}
  mark  <file...> [--root R]  -> record those files' current hashes as reviewed

Scope = uncommitted code changes (git diff vs HEAD + untracked files). Once you
commit, changes drop out of scope naturally. No third-party dependencies.
"""
import hashlib
import json
import os
import subprocess
import sys

CODE_EXT = (".py", ".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".mts", ".cts")


def _git(args, root):
    try:
        r = subprocess.run(["git"] + args, cwd=root, capture_output=True,
                           text=True, timeout=15)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def changed_code_files(root):
    """Uncommitted code files: modified-vs-HEAD + untracked-new (deletions excluded)."""
    names = set()
    for line in _git(["diff", "--name-only", "HEAD"], root).splitlines():
        names.add(line.strip())
    for line in _git(["ls-files", "--others", "--exclude-standard"], root).splitlines():
        names.add(line.strip())
    out = []
    for f in names:
        if f and f.lower().endswith(CODE_EXT) and os.path.isfile(os.path.join(root, f)):
            out.append(f)
    return sorted(out)


def content_hash(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha1(fh.read()).hexdigest()
    except OSError:
        return ""


def _state_path(root):
    return os.path.join(root, ".hi-vibe", "reviewed.json")


def load_state(root):
    try:
        with open(_state_path(root), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def save_state(root, data):
    os.makedirs(os.path.dirname(_state_path(root)), exist_ok=True)
    with open(_state_path(root), "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2, sort_keys=True)


def cmd_list(root):
    state = load_state(root)
    to_review, skipped = [], []
    for f in changed_code_files(root):
        h = content_hash(os.path.join(root, f))
        if h and state.get(f) == h:
            skipped.append(f)          # reviewed before, unchanged since -> skip
        else:
            to_review.append(f)
    print(json.dumps({"to_review": to_review, "skipped": skipped},
                     ensure_ascii=False, indent=2))
    return 0


def cmd_mark(root, files):
    state = load_state(root)
    n = 0
    for f in files:
        h = content_hash(os.path.join(root, f))
        if h:
            state[f] = h
            n += 1
    save_state(root, state)
    print("marked reviewed:", n)
    return 0


def main():
    args = sys.argv[1:]
    root = "."
    if "--root" in args:
        i = args.index("--root")
        if i + 1 < len(args):
            root = args[i + 1]
            del args[i:i + 2]
    if not args:
        print("usage: review_scope.py list | mark <file...> [--root R]")
        return 1
    if args[0] == "list":
        return cmd_list(root)
    if args[0] == "mark":
        return cmd_mark(root, args[1:])
    print("unknown command:", args[0])
    return 1


if __name__ == "__main__":
    sys.exit(main())

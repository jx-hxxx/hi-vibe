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


def changed_lines(root, files):
    """{file: 변경된 줄 수}. 추적 중 파일은 git diff --numstat(추가+삭제),
    untracked 새 파일은 전체 줄 수. 크기는 여기서 재고(기계), 병렬 여부
    판단은 스킬이 한다(AI). 바이너리는 0."""
    counts = {}
    seen = set()
    for line in _git(["diff", "--numstat", "HEAD"], root).splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added, deleted, path = parts[0], parts[1], parts[2]
        if path not in files:
            continue
        if added == "-" or deleted == "-":
            n = 0  # 바이너리
        else:
            try:
                n = int(added) + int(deleted)
            except ValueError:
                n = 0
        counts[path] = n
        seen.add(path)
    for f in files:  # numstat에 없던 것(주로 untracked 새 파일) = 전체 줄 수
        if f in seen:
            continue
        try:
            with open(os.path.join(root, f), "rb") as fh:
                counts[f] = fh.read().count(b"\n") + 1
        except OSError:
            counts[f] = 0
    return counts


def _pending(root):
    """아직/다시 봐야 할 코드 파일 (안 바뀐 리뷰 완료분은 제외)."""
    state = load_state(root)
    out = []
    for f in changed_code_files(root):
        h = content_hash(os.path.join(root, f))
        if not (h and state.get(f) == h):
            out.append(f)
    return out


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
    sizes = changed_lines(root, set(to_review))
    print(json.dumps({
        "to_review": to_review,        # 파일명 배열 (하위호환 유지)
        "skipped": skipped,
        "sizes": sizes,                # {파일: 변경 줄 수} — 병렬 판단 근거
        "total_changed_lines": sum(sizes.values()),
        "file_count": len(to_review),
    }, ensure_ascii=False, indent=2))
    return 0


def cmd_chunk(root, n):
    """to_review를 줄 수 기준 균형 있게 N등분 (병렬 리뷰용). greedy: 큰 파일부터
    가장 덜 찬 버킷에 넣어 버킷별 부하를 고르게 한다."""
    pending = _pending(root)
    sizes = changed_lines(root, set(pending))
    n = max(1, min(n, len(pending))) if pending else 1
    buckets = [[] for _ in range(n)]
    loads = [0] * n
    for f in sorted(pending, key=lambda x: -sizes.get(x, 0)):
        i = min(range(n), key=lambda k: loads[k])
        buckets[i].append(f)
        loads[i] += sizes.get(f, 0)
    result = [{"files": b, "lines": ld}
              for b, ld in zip(buckets, loads) if b]
    print(json.dumps({"buckets": result}, ensure_ascii=False, indent=2))
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
        print("usage: review_scope.py list | chunk <N> | mark <file...> [--root R]")
        return 1
    if args[0] == "list":
        return cmd_list(root)
    if args[0] == "chunk":
        try:
            n = int(args[1])
        except (IndexError, ValueError):
            n = 4
        return cmd_chunk(root, n)
    if args[0] == "mark":
        return cmd_mark(root, args[1:])
    print("unknown command:", args[0])
    return 1


if __name__ == "__main__":
    sys.exit(main())

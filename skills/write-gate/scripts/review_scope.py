#!/usr/bin/env python3
"""review_scope — what still needs reviewing, and mark things reviewed.

Powers `/hi-vibe:review`: a session may build several features, so one review
should cover them all — and code that was already reviewed AND hasn't changed
since should be skipped.

The "what changed" and "did it change since I reviewed it" judgments are done
here in code (deterministic), NOT by the AI — the AI is unreliable at hashing.

  list  [--root R]        -> JSON {"scope":..., "to_review":[...], "skipped":[...]}
  mark  <file...> [--root R]  -> record those files' current hashes as reviewed

Scope is a ladder, so committing or pushing never leaves review with nothing
to look at:

  1) uncommitted  — 안 커밋한 변경 (평소 경로)
  2) unpushed     — 커밋했지만 아직 안 푸시한 것
  3) last_commit  — 마지막 커밋 하나
  4) none         — git 저장소가 아니거나 볼 게 없음

The tier is picked by which one actually has changed code files; the
already-reviewed filter is then applied *within* that tier (so finishing a
review doesn't drag older commits back in). No third-party dependencies.
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


SCOPE_LABELS = {
    "uncommitted": "안 커밋한 변경",
    "unpushed": "커밋했지만 안 푸시한 것",
    "last_commit": "마지막 커밋",
    "none": "볼 변경 없음",
}


def _code_files(root, names):
    """이름 집합에서 실제로 존재하는 코드 파일만 (삭제분 제외)."""
    out = []
    for f in names:
        if f and f.lower().endswith(CODE_EXT) and os.path.isfile(os.path.join(root, f)):
            out.append(f)
    return sorted(out)


def _diff_names(root, base):
    return {ln.strip() for ln in _git(["diff", "--name-only", base], root).splitlines()}


def _rev_exists(root, ref):
    return bool(_git(["rev-parse", "--verify", "--quiet", ref], root).strip())


def scope(root):
    """리뷰 범위를 계단으로 고른다 → (tier, base, files).

    base는 줄 수를 셀 때 쓸 diff 기준점이며, None이면 "파일 전체가 새 것"
    (첫 커밋뿐인 저장소)이라는 뜻이다. 계단을 내려갈지는 그 단계에 바뀐
    코드 파일이 있느냐로만 정한다 — 리뷰를 마쳐서 비는 것과 구분해야
    옛날 커밋이 도로 끌려오지 않는다."""
    names = _diff_names(root, "HEAD")
    for line in _git(["ls-files", "--others", "--exclude-standard"], root).splitlines():
        names.add(line.strip())
    files = _code_files(root, names)
    if files:
        return "uncommitted", "HEAD", files

    if _rev_exists(root, "@{upstream}"):
        files = _code_files(root, _diff_names(root, "@{upstream}"))
        if files:
            return "unpushed", "@{upstream}", files

    if _rev_exists(root, "HEAD~1"):
        files = _code_files(root, _diff_names(root, "HEAD~1"))
        if files:
            return "last_commit", "HEAD~1", files
    elif _rev_exists(root, "HEAD"):
        # 커밋이 하나뿐 = 그 커밋이 저장소 전체다 (비교 대상이 없음).
        tracked = {ln.strip() for ln in _git(["ls-files"], root).splitlines()}
        files = _code_files(root, tracked)
        if files:
            return "last_commit", None, files

    return "none", None, []


def changed_code_files(root):
    """현재 계단에서 리뷰 대상이 되는 코드 파일 (하위호환 진입점)."""
    return scope(root)[2]


def content_hash(path):
    try:
        with open(path, "rb") as fh:
            return hashlib.sha1(fh.read()).hexdigest()
    except OSError:
        return ""


def changed_lines(root, files, base="HEAD"):
    """{file: 변경된 줄 수}. diff에 잡히는 파일은 --numstat(추가+삭제),
    그 밖(새 파일·첫 커밋뿐인 저장소)은 전체 줄 수. 크기는 여기서 재고(기계),
    병렬 여부 판단은 스킬이 한다(AI). 바이너리는 0."""
    counts = {}
    seen = set()
    for line in (_git(["diff", "--numstat", base], root).splitlines() if base else []):
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


def _split_reviewed(root, files):
    """현재 계단의 파일을 (아직 봐야 할 것, 이미 봤고 안 바뀐 것)으로 나눈다."""
    state = load_state(root)
    to_review, skipped = [], []
    for f in files:
        h = content_hash(os.path.join(root, f))
        if h and state.get(f) == h:
            skipped.append(f)
        else:
            to_review.append(f)
    return to_review, skipped


def _pending(root):
    """아직/다시 봐야 할 코드 파일 + 줄 수를 셀 기준점."""
    _, base, files = scope(root)
    return _split_reviewed(root, files)[0], base


def _fingerprint(root, files):
    """리뷰 대상의 내용 지문. Stop 훅이 "같은 변경으로 두 번 막지 않기"에
    쓴다 — 사용자가 한 번 넘겼으면 코드가 실제로 바뀌기 전엔 조용해야 한다."""
    if not files:
        return ""
    h = hashlib.sha1()
    for f in sorted(files):
        h.update(f.encode("utf-8"))
        h.update(content_hash(os.path.join(root, f)).encode("utf-8"))
    return h.hexdigest()


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
    tier, base, files = scope(root)
    to_review, skipped = _split_reviewed(root, files)
    sizes = changed_lines(root, set(to_review), base)
    print(json.dumps({
        "scope": tier,                 # 어느 계단에서 잡았나
        "scope_label": SCOPE_LABELS[tier],   # 사용자에게 그대로 보여줄 말
        "fingerprint": _fingerprint(root, to_review),  # 훅의 재차단 방지용
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
    pending, base = _pending(root)
    sizes = changed_lines(root, set(pending), base)
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

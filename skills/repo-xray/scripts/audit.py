#!/usr/bin/env python3
"""repo-xray: evidence-based structure analyzer for Python + JS/TS repos.

Usage:
  python3 audit.py scan [--root <repo>]          full analysis -> .repo-xray/report.json
  python3 audit.py find <name> [--root <repo>]   "does X exist?" symbol/text search

No third-party dependencies. Python 3.8+.
"""
import argparse
import ast
import copy
import difflib
import hashlib
import io
import json
import os
import re
import sys
import time
import tokenize
from collections import Counter, defaultdict

EXCLUDE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__",
    "dist", "build", ".repo-xray", ".audit", ".next", "coverage",
    ".mypy_cache", ".pytest_cache", "site-packages",
}
PY_EXT = {".py"}
JS_EXT = {".js", ".mjs", ".cjs", ".jsx", ".ts", ".tsx", ".mts", ".cts"}
TEXT_EXT = PY_EXT | JS_EXT | {".html", ".htm", ".css", ".json", ".md", ".yml", ".yaml", ".toml"}
# Prose/style files. A mention here is documentation, not a call site — it
# must never rescue a symbol from dead candidacy (otherwise the MODULE.md /
# CHANGELOG.md this plugin mandates would mask dead code forever).
DOC_EXT = {".md", ".css"}

WORD_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")

# JS/TS declarations: function foo(...), const/let/var foo[: Type] =
# function / (…)[: Ret] => / async …  (regex heuristic, not a parser)
JS_DECL_RE = re.compile(
    r"""(?:^|[^.\w$])
        (?:
            function\s+(?P<fn>[A-Za-z_$][\w$]*)
          | (?:const|let|var)\s+(?P<var>[A-Za-z_$][\w$]*)
                (?:\s*:\s*[^=\n]+?)?\s*=\s*
                (?:async\s+)?
                (?:function\b|\([^)\n]*\)\s*(?::\s*[^=\n]*?)?\s*=>|[A-Za-z_$][\w$]*\s*=>)
        )""",
    re.VERBOSE,
)

# TS/JS type-level declarations: class Foo, interface Foo, enum Foo, type Foo =
JS_TYPE_RE = re.compile(
    r"""(?:^|[^.\w$])
        (?:
            (?:abstract\s+)?class\s+(?P<cls>[A-Za-z_$][\w$]*)
          | (?:interface|enum)\s+(?P<iface>[A-Za-z_$][\w$]*)
          | type\s+(?P<alias>[A-Za-z_$][\w$]*)\s*=
        )""",
    re.VERBOSE,
)

# Python names that are referenced implicitly; never report as dead
PY_IMPLICIT = {"main"}

# Test files: unittest/pytest discover symbols by naming convention, not by
# reference — their "unreferenced" classes/functions are alive by design
TEST_FILE_RE = re.compile(r"(^|[/\\])(test_[^/\\]*|[^/\\]*_test)\.(py|js|mjs|cjs|jsx|ts|tsx|mts|cts)$|(^|[/\\])conftest\.py$|(^|[/\\])[^/\\]*\.(test|spec)\.(js|jsx|ts|tsx)$")


def is_test_file(relpath):
    return bool(TEST_FILE_RE.search(relpath))


def is_minified(path):
    return path.endswith(".min.js") or path.endswith(".min.css")


def collect_files(root):
    """Walk repo, return {ext_group: [paths]} and the full list of text files."""
    py_files, js_files, text_files = [], [], []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn)[1].lower()
            if ext not in TEXT_EXT or is_minified(path):
                continue
            try:
                if os.path.getsize(path) > 2_000_000:  # skip huge data blobs
                    continue
            except OSError:
                continue
            text_files.append(path)
            if ext in PY_EXT:
                py_files.append(path)
            elif ext in JS_EXT and not fn.endswith(".d.ts"):
                # .d.ts are ambient declarations (often generated) — count
                # them as reference text but don't extract symbols from them
                js_files.append(path)
    return py_files, js_files, text_files


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def rel(root, path):
    return os.path.relpath(path, root)


def _strip_py_comments(text):
    """Blank out `#` comments via the stdlib tokenizer (handles strings,
    triple-quotes and escapes correctly). Falls back to the raw text on any
    tokenizer error — never risk dropping a real reference."""
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return text
    lines = text.splitlines(keepends=True)
    for tok in toks:
        if tok.type == tokenize.COMMENT:
            (sr, sc), (er, ec) = tok.start, tok.end
            if sr == er and 1 <= sr <= len(lines):  # comments are single-line
                ln = lines[sr - 1]
                lines[sr - 1] = ln[:sc] + " " * (ec - sc) + ln[ec:]
    return "".join(lines)


def _strip_c_comments(text):
    """Remove `//` and `/* */` comments while preserving string/template
    literals. `//` and `/*` are never valid operators in JS, so outside a
    string they are unambiguously comments (regex literals starting with
    `//`/`/*` are invalid). String contents are kept on purpose (FP-03)."""
    out = []
    i, n, quote = 0, len(text), None
    while i < n:
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1]); i += 2; continue
            if ch == quote:
                quote = None
            i += 1; continue
        two = text[i:i + 2]
        if two == "//":
            j = text.find("\n", i)
            i = n if j == -1 else j; continue
        if two == "/*":
            j = text.find("*/", i + 2)
            i = n if j == -1 else j + 2; continue
        if ch in ("'", '"', "`"):
            quote = ch; out.append(ch); i += 1; continue
        out.append(ch); i += 1
    return "".join(out)


def _strip_hash_comments(text):
    """Remove `#` comments (YAML/TOML) while preserving quoted strings."""
    out = []
    i, n, quote = 0, len(text), None
    while i < n:
        ch = text[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1]); i += 2; continue
            if ch == quote:
                quote = None
            i += 1; continue
        if ch == "#":
            j = text.find("\n", i)
            i = n if j == -1 else j; continue
        if ch in ("'", '"'):
            quote = ch; out.append(ch); i += 1; continue
        out.append(ch); i += 1
    return "".join(out)


def strip_comments(text, ext):
    """Drop comment text so a symbol named only inside a comment does not
    count as a reference (a comment must not rescue a dead candidate — the
    most common AI residue is exactly a commented-out call or a TODO
    mention). String literals are deliberately preserved: a name built into
    a string can be a real dynamic-dispatch reference (FP-03)."""
    ext = ext.lower()
    if ext == ".py":
        return _strip_py_comments(text)
    if ext in JS_EXT:
        return _strip_c_comments(text)
    if ext in (".yml", ".yaml", ".toml"):
        return _strip_hash_comments(text)
    if ext in (".html", ".htm"):
        return re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    return text  # .json (no comments), .md/.css (prose — excluded from rescue)


def build_word_index(root, text_files):
    """Token counts per file — the evidence base for reference counting.
    Comments are stripped first so they can't rescue a dead candidate."""
    per_file = {}
    total = Counter()
    for path in text_files:
        text = strip_comments(read_text(path), os.path.splitext(path)[1])
        c = Counter(WORD_RE.findall(text))
        per_file[rel(root, path)] = c
        total.update(c)
    return per_file, total


def is_doc_file(relpath):
    return os.path.splitext(relpath)[1].lower() in DOC_EXT


def code_counts(per_file):
    """Token counts from code-capable files only (doc files excluded)."""
    total = Counter()
    for f, c in per_file.items():
        if not is_doc_file(f):
            total.update(c)
    return total


# ---------- Python analysis ----------

def _bound_names(fn):
    """Names bound locally inside a function: args, assignment/for/with
    targets, comprehension vars, except aliases, imports, inner defs."""
    bound = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
        elif isinstance(node, ast.alias):
            bound.add(node.asname or node.name.split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node is not fn:
            bound.add(node.name)
    return bound


def normalized_dump(fn_node):
    """AST dump with function name, decorators, docstring stripped and every
    locally-bound name replaced by a positional placeholder. Two functions
    that differ only in naming produce the same dump; near-identical logic
    produces highly similar dumps. Global/imported call targets keep their
    real names, so calling a *different* helper still distinguishes them."""
    n = copy.deepcopy(fn_node)
    n.name = "_"
    n.decorator_list = []
    body = list(n.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:] or [ast.Pass()]
    n.body = body
    bound = _bound_names(n)
    mapping = {}

    def canon(name):
        if name not in mapping:
            mapping[name] = "v{}".format(len(mapping))
        return mapping[name]

    for node in ast.walk(n):
        if isinstance(node, ast.Name) and node.id in bound:
            node.id = canon(node.id)
        elif isinstance(node, ast.arg) and node.arg in bound:
            node.arg = canon(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                and node is not n and node.name in bound:
            node.name = canon(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name and node.name in bound:
            node.name = canon(node.name)
        elif isinstance(node, ast.alias) and node.asname and node.asname in bound:
            node.asname = canon(node.asname)
    return ast.dump(n)


def _shingles(dump, k=9):
    """Character k-gram set of an AST dump — a cheap O(L) fingerprint computed
    ONCE per function. The Jaccard overlap of two fingerprints lower-bounds
    how similar the functions can be, so it prefilters pairs before the exact
    but O(L^2) difflib ratio(). Dumps shorter than k fingerprint whole."""
    if len(dump) <= k:
        return frozenset((dump,))
    return frozenset(dump[i:i + k] for i in range(len(dump) - k + 1))


def _is_test_file(path):
    """테스트 파일 판별: tests/ 경로이거나 test_*/​*_test 파일명."""
    base = os.path.basename(path or "")
    if "/tests/" in "/" + (path or "").replace(os.sep, "/") or (path or "").replace(os.sep, "/").startswith("tests/"):
        return True
    stem = base.rsplit(".", 1)[0]
    return stem.startswith("test_") or stem.endswith("_test") or base.startswith("test")


def _all_test_files(pair):
    """near-dup 쌍의 두 함수가 모두 테스트 파일에 있으면 True."""
    fns = pair.get("functions", [])
    return bool(fns) and all(_is_test_file(f.get("file", "")) for f in fns)


def find_near_duplicates(norm_entries, threshold=0.9, min_length=6, max_pairs=20000,
                         shingle_k=9, jaccard_floor=0.45, time_budget=60.0):
    """Pairs of functions whose normalized ASTs are >= threshold similar but
    not identical — the typical AI failure: a 90%-same reimplementation.
    Weaker evidence than exact duplicates; the reader must open both.

    The exact score is difflib's `SequenceMatcher.ratio()`, which is O(L^2)
    per pair — calling it on every size-window pair made a mid-size repo take
    *minutes* (thousands of ~2.6k-char dumps). So each function is fingerprinted
    once (`_shingles`, O(L)) and a pair only reaches ratio() if its shingle
    Jaccard clears `jaccard_floor`. This turns O(pairs * L^2) into
    O(pairs * shingles) + O(survivors * L^2), where survivors is tiny.

    `jaccard_floor` sits well below `threshold` on purpose: a few scattered
    edits break several k-grams, so a genuine 0.9-ratio pair can have much
    lower shingle overlap. It was calibrated against a full unbounded scan
    (see scripts/tests): across every true near-duplicate the *minimum*
    observed shingle Jaccard was ~0.71, so 0.45 keeps them all with a wide
    margin while dropping ~98% of doomed pairs before the expensive check.
    NOTE — do NOT instead cap by dump length to bound ratio() cost: real
    near-duplicates exist between large functions too (20k-char dumps in the
    calibration set), so a size cap silently drops true positives. The
    fingerprint prefilter is the safe way to cut cost.

    `time_budget` is a wall-clock backstop for pathological inputs only; with
    the prefilter it should never trip. If it (or max_pairs) does, `truncated`
    is set so the report says the scan was partial instead of under-reporting."""
    # Sort by dump length, then file/line — a fully deterministic order so
    # the result never depends on os.walk's OS-specific file ordering.
    entries = sorted(
        (e for e in norm_entries if e["meta"]["length"] >= min_length),
        key=lambda e: (len(e["dump"]), e["meta"]["file"], e["meta"]["line"]),
    )
    fps = [_shingles(e["dump"], shingle_k) for e in entries]
    results, pairs, truncated = [], 0, False
    start = time.monotonic()
    for i, a in enumerate(entries):
        # Backstop only — the prefilter keeps each inner pass cheap, so this
        # never overshoots the budget by more than one function's pairs.
        if time.monotonic() - start > time_budget:
            truncated = True
            break
        fa, la = fps[i], len(a["dump"])
        for j in range(i + 1, len(entries)):
            b = entries[j]
            if len(b["dump"]) > la * 1.25:
                break  # sorted by size; the rest only get longer
            if a["dump"] == b["dump"]:
                continue  # exact duplicate, reported elsewhere
            pairs += 1
            if pairs > max_pairs:
                truncated = True
                break
            # Cheap Jaccard prefilter (O(shingles)) drops the ~99% of pairs
            # that cannot reach `threshold`, so the O(L^2) ratio() below runs
            # only on genuine candidates — this is the whole speedup.
            fb = fps[j]
            inter = len(fa & fb)
            if inter == 0 or inter / (len(fa) + len(fb) - inter) < jaccard_floor:
                continue
            # autojunk=False: the default heuristic drops "popular" chars
            # from the SECOND sequence only, making ratio() asymmetric — so
            # the score would depend on which function came first in the
            # scan (an OS-dependent order). Disabling it keeps ratio(a,b)
            # == ratio(b,a) and the result deterministic.
            sm = difflib.SequenceMatcher(None, a["dump"], b["dump"], autojunk=False)
            if sm.real_quick_ratio() < threshold or sm.quick_ratio() < threshold:
                continue
            ratio = sm.ratio()
            if ratio >= threshold:
                results.append({
                    "similarity": round(ratio, 3),
                    "functions": [a["meta"], b["meta"]],
                })
        if truncated:
            break
    # Return ALL pairs (most-similar first); the report layer decides how many
    # to SHOW. Detection and presentation are separate so the report can say
    # "showing N of M" instead of silently dropping the rest.
    results.sort(key=lambda r: -r["similarity"])
    return results, truncated


def _looks_wip(node, src_lines):
    """함수/클래스가 '아직 안 만든(WIP)'으로 보이나 — 그렇다면 참조가 0이어도
    '죽은 코드'가 아니라 '개발 중이라 아직 안 쓰이는 것'일 수 있으므로 삭제
    후보로 다룰 때 조심해야 한다. 신호: docstring만/빈 본문, 본문이 `pass`
    하나 또는 `...` 하나, `raise NotImplementedError`, 또는 함수 범위에
    TODO/FIXME/WIP/XXX 주석."""
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]  # docstring 제외
    if not body:
        return True
    if len(body) == 1:
        only = body[0]
        if isinstance(only, ast.Pass):
            return True
        if isinstance(only, ast.Expr) and isinstance(getattr(only, "value", None), ast.Constant) \
                and only.value.value is ...:
            return True
    for n in ast.walk(node):
        if isinstance(n, ast.Raise) and n.exc is not None:
            exc = n.exc.func if isinstance(n.exc, ast.Call) else n.exc
            if isinstance(exc, ast.Name) and exc.id in ("NotImplementedError", "NotImplemented"):
                return True
    end = getattr(node, "end_lineno", node.lineno)
    scope = "\n".join(src_lines[node.lineno - 1:end])
    return bool(re.search(r"#.*\b(TODO|FIXME|WIP|XXX)\b", scope, re.I))


def analyze_python(root, py_files):
    symbols = []   # {name, file, line, end_line, kind, decorated, is_method, length}
    dup_index = defaultdict(list)
    norm_entries = []
    parse_errors = []

    for path in py_files:
        src = read_text(path)
        src_lines = src.splitlines()
        try:
            tree = ast.parse(src)
        except SyntaxError as e:
            parse_errors.append({"file": rel(root, path), "error": str(e)})
            continue

        # mark parents to distinguish methods from top-level functions
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                child._parent = node

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                parent = getattr(node, "_parent", None)
                is_method = isinstance(parent, ast.ClassDef)
                kind = "class" if isinstance(node, ast.ClassDef) else ("method" if is_method else "function")
                length = (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno + 1
                decorated = bool(getattr(node, "decorator_list", []))
                symbols.append({
                    "name": node.name,
                    "file": rel(root, path),
                    "line": node.lineno,
                    "kind": kind,
                    "decorated": decorated,
                    "length": length,
                    "looks_wip": _looks_wip(node, src_lines),
                })
                # duplicate detection: same AST shape ignoring the function
                # name AND local variable names (normalized dump)
                if kind != "class" and length >= 4:
                    dump = normalized_dump(node)
                    meta = {
                        "name": node.name, "file": rel(root, path),
                        "line": node.lineno, "length": length,
                    }
                    key = hashlib.md5(dump.encode()).hexdigest()
                    dup_index[key].append(meta)
                    norm_entries.append({"meta": meta, "dump": dump})

    duplicates = [
        {"functions": group, "length": group[0]["length"]}
        for group in dup_index.values() if len(group) > 1
    ]
    duplicates.sort(key=lambda g: -g["length"])
    near_dups, near_truncated = find_near_duplicates(norm_entries)
    return symbols, duplicates, near_dups, near_truncated, parse_errors


# ---------- JS analysis ----------

def analyze_js(root, js_files):
    symbols = []
    defs_by_name = defaultdict(list)
    for path in js_files:
        src = read_text(path)
        for i, line in enumerate(src.splitlines(), 1):
            # `export default function App()` is imported under an arbitrary
            # name by consumers, so its own name has zero references by
            # design — flag it so find_dead never calls it a dead candidate.
            is_default = "export default" in line
            decls = [
                (m.group("fn") or m.group("var"), "js-function")
                for m in JS_DECL_RE.finditer(line)
            ] + [
                (m.group("cls") or m.group("iface") or m.group("alias"),
                 "js-class" if m.group("cls") else "ts-type")
                for m in JS_TYPE_RE.finditer(line)
            ]
            for name, kind in decls:
                if not name:
                    continue
                top_level = not line[:1].isspace()
                entry = {"name": name, "file": rel(root, path), "line": i,
                         "kind": kind, "default_export": is_default}
                symbols.append(entry)
                if top_level:  # indented = local scope, collisions there are normal
                    defs_by_name[name].append(entry)

    collisions = [
        {"name": name, "definitions": defs}
        for name, defs in defs_by_name.items()
        if len({d["file"] for d in defs}) > 1
    ]
    collisions.sort(key=lambda c: -len(c["definitions"]))
    return symbols, collisions


# ---------- dead-code candidates ----------

def find_dead(symbols, per_file, code_totals, def_counts):
    """A symbol is a dead candidate when its name appears nowhere in CODE
    files except its own definitions. Mentions in doc files (.md/.css) are
    reported separately as `doc_mentions` and never rescue a candidate —
    docs describe code, they don't call it. Name-based — dynamic uses
    (getattr, string routes, templates) are invisible, so these are
    CANDIDATES, not verdicts."""
    dead = []
    for s in symbols:
        name = s["name"]
        if name.startswith("__") or name.startswith("_") or name in PY_IMPLICIT:
            continue
        if s.get("kind") == "method":
            continue  # methods are called via self/instance; too noisy for name counting
        if s.get("default_export"):
            continue  # imported under an arbitrary name; name-ref count is meaningless (FP-08)
        if is_test_file(s["file"]):
            continue  # test runners invoke these by naming convention
        refs = code_totals.get(name, 0) - def_counts.get(name, 0)
        if refs <= 0:
            ref_files = [f for f, c in per_file.items() if c.get(name) and not is_doc_file(f)]
            doc_files = [f for f, c in per_file.items() if c.get(name) and is_doc_file(f)]
            dead.append({
                **s, "refs_found": max(refs, 0),
                "appears_in": ref_files, "doc_mentions": doc_files,
            })
    return dead


# ---------- oversized ----------

def oversized_report(root, text_files, symbols):
    big_files = []
    for path in text_files:
        ext = os.path.splitext(path)[1].lower()
        if ext not in PY_EXT | JS_EXT:
            continue
        n = read_text(path).count("\n") + 1
        if n > 400:
            big_files.append({"file": rel(root, path), "lines": n})
    big_files.sort(key=lambda f: -f["lines"])

    big_functions = sorted(
        [s for s in symbols if s.get("length", 0) > 60 and s["kind"] != "class"],
        key=lambda s: -s["length"],
    )
    return big_files[:15], big_functions[:15]


# ---------- commands ----------

def cmd_scan(root):
    py_files, js_files, text_files = collect_files(root)
    per_file, _total_counts = build_word_index(root, text_files)
    code_totals = code_counts(per_file)

    py_symbols, duplicates, near_dups, near_truncated, parse_errors = analyze_python(root, py_files)
    js_symbols, collisions = analyze_js(root, js_files)

    # near-dup is weak evidence (the reader must open both functions), so the
    # report SHOWS only the most-similar few — but never hides the rest
    # silently: near_duplicate_total tells the reader how many were actually
    # found, so `total > len(shown)` means "there are more, ranked lower".
    #
    # Test functions naturally look alike (shared setup/assert boilerplate), so a
    # test<->test pair is almost never a real reimplementation bug. We split those
    # into a separate, lower-priority bucket instead of hiding them — the reader
    # sees "code N · test M" and can focus on the code<->code pairs first.
    NEAR_DUP_SHOWN = 20
    near_total = len(near_dups)
    code_pairs = [p for p in near_dups if not _all_test_files(p)]
    test_pairs = [p for p in near_dups if _all_test_files(p)]
    near_shown = code_pairs[:NEAR_DUP_SHOWN]
    test_near_shown = test_pairs[:NEAR_DUP_SHOWN]

    all_symbols = py_symbols + js_symbols
    def_counts = Counter(s["name"] for s in all_symbols)
    dead_all = find_dead(all_symbols, per_file, code_totals, def_counts)
    # decorated = usually framework-registered (routes/hooks): report separately
    dead = [d for d in dead_all if not d.get("decorated")]
    decorated_unref = [d for d in dead_all if d.get("decorated")]
    big_files, big_functions = oversized_report(root, text_files, py_symbols)

    report = {
        "tool": "repo-xray",
        "scan": {
            "root": os.path.abspath(root),
            "files_scanned": {
                "python": len(py_files), "js": len(js_files), "all_text": len(text_files),
            },
            "excluded_dirs": sorted(EXCLUDE_DIRS),
            "note": (
                "reference counting is name-based; dynamic uses (getattr, string "
                "routes, HTML templates outside scanned files) are not visible. "
                "doc files (.md/.css) never count as references — see doc_mentions."
            ),
            "near_duplicate_scan_truncated": near_truncated,
        },
        "dead_candidates": sorted(dead, key=lambda s: (s["file"], s["line"])),
        "decorated_unreferenced": sorted(decorated_unref, key=lambda s: (s["file"], s["line"])),
        "duplicate_functions": duplicates,
        "near_duplicate_functions": near_shown,
        "near_duplicate_total": len(code_pairs),
        "near_duplicate_test_functions": test_near_shown,
        "near_duplicate_test_total": len(test_pairs),
        "js_name_collisions": collisions,
        "oversized_files": big_files,
        "oversized_functions": big_functions,
        "python_parse_errors": parse_errors,
        "symbol_count": {"python": len(py_symbols), "js": len(js_symbols)},
    }

    out_dir = os.path.join(root, ".repo-xray")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"scanned: {len(py_files)} py / {len(js_files)} js+ts / {len(text_files)} text files")
    code_n, test_n = len(code_pairs), len(test_pairs)
    near_str = f"code {code_n} · test {test_n}"
    if code_n > NEAR_DUP_SHOWN:
        near_str = f"code {NEAR_DUP_SHOWN} of {code_n} · test {test_n}"
    print(f"dead candidates: {len(dead)} (+{len(decorated_unref)} decorated)  "
          f"duplicates: {len(duplicates)}  near-duplicates: {near_str}  "
          f"js collisions: {len(collisions)}  oversized files: {len(big_files)}")
    print(f"report: {out_path}")
    return 0


def cmd_find(root, query):
    py_files, js_files, text_files = collect_files(root)
    pattern = re.compile(r"\b" + re.escape(query) + r"\b")
    hits = []
    for path in text_files:
        for i, line in enumerate(read_text(path).splitlines(), 1):
            if pattern.search(line):
                hits.append({"file": rel(root, path), "line": i, "text": line.strip()[:160]})
                if len(hits) >= 80:
                    break
        if len(hits) >= 80:
            break

    py_symbols, _, _, _, _ = analyze_python(root, py_files)
    js_symbols, _ = analyze_js(root, js_files)
    names = sorted({s["name"] for s in py_symbols + js_symbols})
    similar = difflib.get_close_matches(query, names, n=8, cutoff=0.6)

    result = {
        "query": query,
        "scan_range": {"files_scanned": len(text_files), "root": os.path.abspath(root)},
        "exact_hits": hits,
        "similar_symbol_names": similar,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def main():
    p = argparse.ArgumentParser(description="repo-xray analyzer")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("scan"); s.add_argument("--root", default=".")
    f = sub.add_parser("find"); f.add_argument("query"); f.add_argument("--root", default=".")
    args = p.parse_args()
    if args.cmd == "scan":
        return cmd_scan(args.root)
    if args.cmd == "find":
        return cmd_find(args.root, args.query)
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

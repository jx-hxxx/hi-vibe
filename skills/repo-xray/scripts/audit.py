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
import json
import os
import re
import sys
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


def build_word_index(root, text_files):
    """Token counts per file — the evidence base for reference counting."""
    per_file = {}
    total = Counter()
    for path in text_files:
        c = Counter(WORD_RE.findall(read_text(path)))
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


def find_near_duplicates(norm_entries, threshold=0.9, min_length=6, max_pairs=20000):
    """Pairs of functions whose normalized ASTs are >= threshold similar but
    not identical — the typical AI failure: a 90%-same reimplementation.
    Weaker evidence than exact duplicates; the reader must open both."""
    entries = sorted(
        (e for e in norm_entries if e["meta"]["length"] >= min_length),
        key=lambda e: len(e["dump"]),
    )
    results, pairs, truncated = [], 0, False
    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            if len(b["dump"]) > len(a["dump"]) * 1.25:
                break  # sorted by size; the rest only get longer
            if a["dump"] == b["dump"]:
                continue  # exact duplicate, reported elsewhere
            pairs += 1
            if pairs > max_pairs:
                truncated = True
                break
            sm = difflib.SequenceMatcher(None, a["dump"], b["dump"])
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
    results.sort(key=lambda r: -r["similarity"])
    return results[:20], truncated


def analyze_python(root, py_files):
    symbols = []   # {name, file, line, end_line, kind, decorated, is_method, length}
    dup_index = defaultdict(list)
    norm_entries = []
    parse_errors = []

    for path in py_files:
        src = read_text(path)
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
                entry = {"name": name, "file": rel(root, path), "line": i, "kind": kind}
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
        "near_duplicate_functions": near_dups,
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
    print(f"dead candidates: {len(dead)} (+{len(decorated_unref)} decorated)  "
          f"duplicates: {len(duplicates)}  near-duplicates: {len(near_dups)}  "
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

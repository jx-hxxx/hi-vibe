#!/usr/bin/env python3
"""repo-xray: evidence-based structure analyzer for Python + JavaScript repos.

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
JS_EXT = {".js", ".mjs", ".cjs"}
TEXT_EXT = PY_EXT | JS_EXT | {".html", ".htm", ".css", ".json", ".md", ".yml", ".yaml", ".toml"}

WORD_RE = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")

# JS declarations: function foo(...), const/let/var foo = function / (…) => / async …
JS_DECL_RE = re.compile(
    r"""(?:^|[^.\w$])
        (?:
            function\s+(?P<fn>[A-Za-z_$][\w$]*)
          | (?:const|let|var)\s+(?P<var>[A-Za-z_$][\w$]*)\s*=\s*
                (?:async\s+)?(?:function\b|\([^)\n]*\)\s*=>|[A-Za-z_$][\w$]*\s*=>)
        )""",
    re.VERBOSE,
)

# Python names that are referenced implicitly; never report as dead
PY_IMPLICIT = {"main"}


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
            elif ext in JS_EXT:
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


# ---------- Python analysis ----------

def analyze_python(root, py_files):
    symbols = []   # {name, file, line, end_line, kind, decorated, is_method, length}
    dup_index = defaultdict(list)
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
                # duplicate detection: same AST shape ignoring the name
                if kind != "class" and length >= 4:
                    n2 = copy.deepcopy(node)
                    n2.name = "_"
                    n2.decorator_list = []
                    key = hashlib.md5(ast.dump(n2).encode()).hexdigest()
                    dup_index[key].append({
                        "name": node.name, "file": rel(root, path),
                        "line": node.lineno, "length": length,
                    })

    duplicates = [
        {"functions": group, "length": group[0]["length"]}
        for group in dup_index.values() if len(group) > 1
    ]
    duplicates.sort(key=lambda g: -g["length"])
    return symbols, duplicates, parse_errors


# ---------- JS analysis ----------

def analyze_js(root, js_files):
    symbols = []
    defs_by_name = defaultdict(list)
    for path in js_files:
        src = read_text(path)
        for i, line in enumerate(src.splitlines(), 1):
            for m in JS_DECL_RE.finditer(line):
                name = m.group("fn") or m.group("var")
                if not name:
                    continue
                top_level = not line[:1].isspace()
                entry = {"name": name, "file": rel(root, path), "line": i, "kind": "js-function"}
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

def find_dead(symbols, per_file, total_counts, def_counts):
    """A symbol is a dead candidate when its name appears nowhere except its
    own definitions. Name-based — dynamic uses (getattr, string routes,
    templates) are invisible, so these are CANDIDATES, not verdicts."""
    dead = []
    for s in symbols:
        name = s["name"]
        if name.startswith("__") or name.startswith("_") or name in PY_IMPLICIT:
            continue
        if s.get("kind") == "method":
            continue  # methods are called via self/instance; too noisy for name counting
        refs = total_counts.get(name, 0) - def_counts.get(name, 0)
        if refs <= 0:
            ref_files = [f for f, c in per_file.items() if c.get(name)]
            dead.append({**s, "refs_found": max(refs, 0), "appears_in": ref_files})
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
    per_file, total_counts = build_word_index(root, text_files)

    py_symbols, duplicates, parse_errors = analyze_python(root, py_files)
    js_symbols, collisions = analyze_js(root, js_files)

    all_symbols = py_symbols + js_symbols
    def_counts = Counter(s["name"] for s in all_symbols)
    dead_all = find_dead(all_symbols, per_file, total_counts, def_counts)
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
            "note": "reference counting is name-based; dynamic uses (getattr, string routes, HTML templates outside scanned files) are not visible",
        },
        "dead_candidates": sorted(dead, key=lambda s: (s["file"], s["line"])),
        "decorated_unreferenced": sorted(decorated_unref, key=lambda s: (s["file"], s["line"])),
        "duplicate_functions": duplicates,
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

    print(f"scanned: {len(py_files)} py / {len(js_files)} js / {len(text_files)} text files")
    print(f"dead candidates: {len(dead)} (+{len(decorated_unref)} decorated)  "
          f"duplicates: {len(duplicates)}  js collisions: {len(collisions)}  "
          f"oversized files: {len(big_files)}")
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

    py_symbols, _, _ = analyze_python(root, py_files)
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

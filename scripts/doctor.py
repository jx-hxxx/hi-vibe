#!/usr/bin/env python3
"""vibe-check doctor: 안전벨트가 진짜 매여 있는지 자가진단.

훅은 어떤 실패에도 호스트를 깨지 않도록 침묵하게 설계되어 있다.
그 대가로 "조용히 꺼진 상태"가 생길 수 있는데, 그걸 이 스크립트가
실제 실행으로 드러낸다. stdlib만 사용, 항상 사람이 읽는 보고서를 출력.

Usage: python3 doctor.py [--root <project>]
Exit code: 0 = 모두 통과(경고 포함), 1 = 실패 항목 있음.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_SCRIPTS = ["session_start.py", "pre_compact.py", "stop_nudge.py", "post_write_guard.py"]

results = []  # (status, label, detail)  status: OK | WARN | FAIL


def add(status, label, detail=""):
    results.append((status, label, detail))


def run_hook(python3, script, payload, project):
    """훅을 실제 호출 방식(python3 + stdin JSON)으로 실행."""
    path = os.path.join(PLUGIN_ROOT, "hooks", "scripts", script)
    return subprocess.run(
        [python3, path], input=json.dumps(payload), capture_output=True,
        text=True, timeout=20, cwd=project,
    )


def check_python3():
    python3 = shutil.which("python3")
    if not python3:
        add("FAIL", "python3 실행 파일",
            "PATH에 python3가 없음 — 훅 4종이 전부 조용히 비활성 상태. "
            "macOS: `xcode-select --install` 또는 brew install python. "
            "Windows: python.org 설치 후 python3 별칭 필요.")
        return None
    proc = subprocess.run([python3, "-c", "import sys; print(sys.version.split()[0])"],
                          capture_output=True, text=True, timeout=10)
    ver = proc.stdout.strip()
    major, minor = (int(x) for x in ver.split(".")[:2])
    if (major, minor) < (3, 8):
        add("FAIL", "python3 버전", f"{ver} — 3.8 이상 필요")
        return None
    add("OK", "python3", f"{ver} ({python3})")
    return python3


def check_plugin_files():
    missing = []
    for p in (["hooks/hooks.json", "skills/repo-xray/scripts/audit.py"]
              + ["hooks/scripts/" + s for s in HOOK_SCRIPTS]):
        if not os.path.isfile(os.path.join(PLUGIN_ROOT, p)):
            missing.append(p)
    if missing:
        add("FAIL", "플러그인 파일", "누락: " + ", ".join(missing) + " — 재설치 필요")
        return False
    add("OK", "플러그인 파일", "훅 4종 + hooks.json + 스캐너 모두 존재")
    return True


def check_hooks_live(python3):
    """임시 init 프로젝트를 만들어 훅 4종을 끝까지 실제로 돌려본다."""
    with tempfile.TemporaryDirectory(prefix="vibe-doctor-") as tmp:
        with open(os.path.join(tmp, "handover.md"), "w", encoding="utf-8") as f:
            f.write("# Handover — 세션 인수인계\n\n## 2026-01-01 00:00 (manual)\n\n- 한 일: doctor 자가진단\n")

        p = run_hook(python3, "session_start.py", {"cwd": tmp, "source": "startup"}, tmp)
        if p.returncode == 0 and "vibe-check" in p.stdout:
            add("OK", "SessionStart 훅", "컨텍스트 주입 확인")
        else:
            add("FAIL", "SessionStart 훅", f"exit {p.returncode}, stderr: {p.stderr.strip()[:200]}")

        p = run_hook(python3, "pre_compact.py",
                     {"cwd": tmp, "transcript_path": "", "trigger": "manual", "session_id": "doctor"}, tmp)
        with open(os.path.join(tmp, "handover.md"), encoding="utf-8") as f:
            wrote = "compact 직전" in f.read()
        if p.returncode == 0 and wrote:
            add("OK", "PreCompact 훅", "handover.md 자동 기록 확인")
        else:
            add("FAIL", "PreCompact 훅", f"exit {p.returncode}, 기록됨: {wrote}")

        p = run_hook(python3, "post_write_guard.py", {
            "cwd": tmp, "tool_name": "Write",
            "tool_input": {"file_path": os.path.join(tmp, "x.py"),
                           "content": "try:\n    f()\nexcept:\n    pass\n"},
        }, tmp)
        if p.returncode == 0 and "에러 삼킴" in p.stdout:
            add("OK", "PostToolUse 훅", "에러 삼킴 패턴 감지 확인")
        else:
            add("FAIL", "PostToolUse 훅", f"exit {p.returncode}, 감지 실패")

        p = run_hook(python3, "stop_nudge.py", {"cwd": tmp, "session_id": "doctor", "transcript_path": ""}, tmp)
        if p.returncode == 0:
            add("OK", "Stop 훅", "정상 종료 확인")
        else:
            add("FAIL", "Stop 훅", f"exit {p.returncode}")


def check_scanner(python3):
    audit = os.path.join(PLUGIN_ROOT, "skills", "repo-xray", "scripts", "audit.py")
    with tempfile.TemporaryDirectory(prefix="vibe-doctor-scan-") as tmp:
        with open(os.path.join(tmp, "a.py"), "w", encoding="utf-8") as f:
            f.write("def truly_unused_fn():\n    return 1\n")
        with open(os.path.join(tmp, "b.ts"), "w", encoding="utf-8") as f:
            f.write("export const fetchThing = async (url: string) => url;\n")
        p = subprocess.run([python3, audit, "scan", "--root", tmp],
                           capture_output=True, text=True, timeout=60)
        report_path = os.path.join(tmp, ".repo-xray", "report.json")
        if p.returncode != 0 or not os.path.isfile(report_path):
            add("FAIL", "repo-xray 스캐너", f"exit {p.returncode}: {p.stderr.strip()[:200]}")
            return
        with open(report_path, encoding="utf-8") as f:
            report = json.load(f)
        dead_names = {d["name"] for d in report.get("dead_candidates", [])}
        ts_seen = report["scan"]["files_scanned"]["js"] >= 1
        if "truly_unused_fn" in dead_names and ts_seen:
            add("OK", "repo-xray 스캐너", "dead 후보 탐지 + TS 파일 스캔 확인")
        else:
            add("FAIL", "repo-xray 스캐너",
                f"dead 탐지: {'truly_unused_fn' in dead_names}, TS 스캔: {ts_seen}")


def check_project(root):
    if not os.path.isfile(os.path.join(root, "handover.md")):
        add("WARN", "이 프로젝트", f"{root} 는 아직 init 전 — 훅이 여기서는 비활성. "
            "/vibe-check:init 으로 설치하세요.")
        return
    docs = [d for d in ("CLAUDE.md", "CHANGELOG.md") if not os.path.isfile(os.path.join(root, d))]
    gi = os.path.join(root, ".gitignore")
    gi_text = ""
    if os.path.isfile(gi):
        with open(gi, encoding="utf-8", errors="replace") as f:
            gi_text = f.read()
    missing_gi = [d for d in (".vibe-check", ".repo-xray") if d not in gi_text]
    if not docs and not missing_gi:
        add("OK", "이 프로젝트", "init 완료 (문서 + .gitignore) — 훅 활성")
    else:
        detail = []
        if docs:
            detail.append("문서 누락: " + ", ".join(docs))
        if missing_gi:
            detail.append(".gitignore에 없음: " + ", ".join(missing_gi))
        add("WARN", "이 프로젝트", "; ".join(detail) + " — /vibe-check:init --audit 로 점검")


def main():
    parser = argparse.ArgumentParser(description="vibe-check self-diagnosis")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = os.path.abspath(args.root)

    python3 = check_python3()
    files_ok = check_plugin_files()
    if python3 and files_ok:
        check_hooks_live(python3)
        check_scanner(python3)
    check_project(root)

    icon = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌"}
    print("vibe-check doctor 결과")
    print("=" * 40)
    for status, label, detail in results:
        line = f"{icon[status]} {label}"
        if detail:
            line += f" — {detail}"
        print(line)
    fails = sum(1 for s, _, _ in results if s == "FAIL")
    warns = sum(1 for s, _, _ in results if s == "WARN")
    print("=" * 40)
    print(f"실패 {fails} · 경고 {warns} · 통과 {len(results) - fails - warns}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())

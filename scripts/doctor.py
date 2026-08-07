#!/usr/bin/env python3
"""hi-vibe doctor: 안전벨트가 진짜 매여 있는지 자가진단.

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
import time

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_SCRIPTS = ["session_start.py", "pre_compact.py", "session_end.py",
                "stop_nudge.py", "post_write_guard.py"]

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
            "PATH에 python3가 없음 — 훅 5종이 전부 조용히 비활성 상태. "
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
    add("OK", "플러그인 파일", "훅 5종 + hooks.json + 스캐너 모두 존재")
    return True


def check_hooks_live(python3):
    """임시 init 프로젝트를 만들어 훅 5종을 끝까지 실제로 돌려본다."""
    with tempfile.TemporaryDirectory(prefix="vibe-doctor-") as tmp:
        os.makedirs(os.path.join(tmp, ".hi-vibe"), exist_ok=True)  # init 마커(gate)
        with open(os.path.join(tmp, "handover.md"), "w", encoding="utf-8") as f:
            f.write("# Handover — 세션 인수인계\n\n## 2026-01-01 00:00 (manual)\n\n- 한 일: doctor 자가진단\n")

        p = run_hook(python3, "session_start.py", {"cwd": tmp, "source": "startup"}, tmp)
        if p.returncode == 0 and "hi-vibe" in p.stdout:
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

        p = run_hook(python3, "session_end.py",
                     {"cwd": tmp, "transcript_path": "", "reason": "clear",
                      "session_id": "doctor-end"}, tmp)
        if p.returncode == 0:
            add("OK", "SessionEnd 훅", "/clear·세션 종료 시 기록 가능 확인")
        else:
            add("FAIL", "SessionEnd 훅", f"exit {p.returncode}, stderr: {p.stderr.strip()[:200]}")

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
            add("OK", "Stop 훅", "실행 가능 확인 (빈 입력에 exit 0)")
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


# 견본 파일은 값이 아니라 형식이라 커밋하는 게 맞다 — 경고 대상이 아니다.
ENV_SAMPLE_SUFFIXES = (".example", ".sample", ".template", ".dist")


def is_env_secret_file(name):
    """비밀값이 들어 있을 만한 `.env` 파일인가 (파일명만 보고 판단).

    `startswith(".env")`로 잡으면 **direnv의 `.envrc`처럼 커밋해도 되는
    파일까지** 유출로 몰아붙인다(`.environment`·`.envoy`도 마찬가지).
    실제 비밀 파일은 정확히 `.env`이거나 `.env.local`처럼 `.env.`으로
    시작한다 — 그 둘만 본다."""
    if not (name == ".env" or name.startswith(".env.")):
        return False
    return not name.endswith(ENV_SAMPLE_SUFFIXES)


def tracked_env_files(root):
    """Git이 추적 중인 `.env` 계열 (견본 제외). git이 없거나 저장소가 아니면 []."""
    try:
        r = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True,
                           text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return []
    if r.returncode != 0:
        return []
    return [ln.strip() for ln in r.stdout.splitlines()
            if ln.strip() and is_env_secret_file(os.path.basename(ln.strip()))]


def env_is_ignored(root):
    """`.env`가 정말로 무시되는가 — **판정은 Git에게 시킨다**.

    `.gitignore` 본문에서 `".env"` 문자열만 찾으면 `# TODO: .env 추가`(주석)나
    `!.env`(무시 해제)까지 "안전함"으로 읽는다. 둘 다 실제로는 정반대다.
    `git check-ignore`는 주석·negate·우선순위·전역 설정까지 Git 규칙 그대로
    판정하므로 여기에 맡긴다. git이 없으면 판정 불가(None)."""
    try:
        r = subprocess.run(["git", "check-ignore", "-q", "--no-index", ".env"],
                           cwd=root, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode == 0:
        return True
    if r.returncode == 1:
        return False
    return None   # 128 = 저장소 아님 등


def check_env_secrets(root):
    """`.env`가 Git에 올라가 있는지 본다.

    비밀키 검사는 `.env`를 "키를 둬도 되는 자리"로 보고 **제외**한다. 그래서
    그 파일이 커밋되면 훅도 스캐너도 못 잡는다 — 검사망에 뚫린 구멍이 아니라
    검사 대상 밖이라 영영 안 걸린다. 입문자가 실제로 자주 밟는 자리라
    여기서 따로 본다. **파일 내용은 읽지 않는다** (읽으면 doctor 출력이
    유출 통로가 된다). 이름만 본다."""
    tracked = tracked_env_files(root)
    if tracked:
        add("FAIL", ".env 유출", ", ".join(tracked[:5]) +
            (f" 외 {len(tracked)-5}개" if len(tracked) > 5 else "") +
            " 가 Git에 추적되고 있습니다. 비밀키 검사는 .env를 검사하지 "
            "않으므로 이건 아무도 안 잡습니다. `git rm --cached <파일>` 후 "
            ".gitignore에 넣으세요. **이미 push했다면 히스토리에 남아 있으니 "
            "그 키는 폐기(rotate)해야 합니다.**")
        return
    ignored = env_is_ignored(root)
    if ignored is None:
        return   # git 저장소가 아니면 할 말이 없다 — 없는 경고를 만들지 않는다
    if ignored:
        add("OK", ".env 유출", "추적 안 됨 + Git이 실제로 무시함")
        return
    add("WARN", ".env 유출", "추적 중인 .env는 없지만 Git이 무시하지도 않습니다 "
        "— 나중에 만들면 그대로 커밋될 수 있습니다. `.gitignore`에 `.env` 한 "
        "줄만 넣어두세요 (`.env.example`은 커밋해도 됩니다). 주석(`# .env`)이나 "
        "`!.env`는 효과가 없습니다.")


def check_project(root):
    if not os.path.isdir(os.path.join(root, ".hi-vibe")):
        add("WARN", "이 프로젝트", "아직 init 안 함(정상 상태). 여기서 hi-vibe "
            "자동 기능(에러/비밀키 감지·자동 handover)을 쓸 거면 → 지금 "
            "/hi-vibe:init 실행하세요(기존 파일은 안 덮어씀). 이 폴더에서 "
            "hi-vibe를 안 쓸 거면 이 줄은 그냥 무시하면 됩니다.")
        return
    docs = [d for d in ("CLAUDE.md", "CHANGELOG.md") if not os.path.isfile(os.path.join(root, d))]
    gi = os.path.join(root, ".gitignore")
    gi_text = ""
    if os.path.isfile(gi):
        with open(gi, encoding="utf-8", errors="replace") as f:
            gi_text = f.read()
    missing_gi = [d for d in (".hi-vibe", ".repo-xray") if d not in gi_text]
    if not docs and not missing_gi:
        add("OK", "이 프로젝트", "init 완료 (문서 + .gitignore) — 훅 활성")
    else:
        detail = []
        if docs:
            detail.append("문서 누락: " + ", ".join(docs))
        if missing_gi:
            detail.append(".gitignore에 없음: " + ", ".join(missing_gi))
        add("WARN", "이 프로젝트", "; ".join(detail) + " → 다음 단계: 지금 "
            "/hi-vibe:init 실행(없는 것만 채우고 기존 파일은 안 건드림). "
            "단, CHANGELOG를 이미 다른 방식(예: handover에 버전 로그)으로 "
            "관리 중이면 그 항목은 무시해도 됩니다.")


FRESH_EYES_MIN_REVIEWS = 3   # 이만큼 리뷰가 돌기 전엔 0회여도 판단하지 않는다


def check_fresh_eyes(root):
    """리뷰는 도는데 **남의 눈(fresh-eyes)만 계속 빠지고 있지 않은지.**

    설계상 리뷰는 두 겹이다 — 체크리스트가 "빠뜨림"을, fresh-eyes가 "판단
    착오"를 본다. 그런데 세션 설정이 에이전트 호출을 막으면 **뒤쪽 절반이
    조용히 안 돈다.** 실제로 한 세션이 하루 종일 그 상태로 돌았고 아무 데도
    안 남았다. 훅 죽음은 heartbeat가 잡는데 에이전트 죽음은 아무도 안 봤다.

    숫자는 Stop 훅이 트랜스크립트에서 직접 센 것이라 AI 신고에 안 기댄다."""
    if not os.path.isdir(os.path.join(root, ".hi-vibe")):
        return
    data = {}
    try:
        with open(os.path.join(root, ".hi-vibe", "state", "agents.json"),
                  encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            data = loaded
    except (OSError, ValueError):
        data = {}
    fe = int(data.get("fresh_eyes") or 0)
    marks = int(data.get("marks") or 0)
    if marks == 0 and fe == 0:
        add("OK", "남의 눈(fresh-eyes)", "아직 리뷰 기록이 없어요 (판단 보류)")
        return
    detail = f"리뷰 {marks}회 중 {fe}회 실행"
    if fe == 0 and marks >= FRESH_EYES_MIN_REVIEWS:
        add("WARN", "남의 눈(fresh-eyes)",
            f"{detail} — **리뷰의 절반이 계속 빠지고 있습니다.** 체크리스트만 "
            "돌고 설계 검토(과잉 설계·더 단순한 길·숨은 결합)는 한 번도 안 "
            "돌았어요. 대개는 막혀서가 아니라 **AI가 안 부른 것**입니다 — "
            "`요청이 없으면 서브에이전트를 부르지 마라` 같은 세션 지시를 "
            "보고 건너뛰는 경우가 흔한데, init으로 켠 것 자체가 요청이라 "
            "부르는 게 맞습니다. 다음 리뷰 때 `남의 눈도 돌려줘`라고 한 번 "
            "말해 보세요. 정말 호출이 실패하는 환경이면 그건 그대로 괜찮지만, "
            "모르고 반쪽만 쓰는 것과는 다릅니다.")
    else:
        add("OK", "남의 눈(fresh-eyes)", detail)


STALE_AFTER = 6 * 3600   # 훅 흔적이 이만큼 낡으면 "이 세션엔 안 돌았다"로 본다


def cmd_quick(root):
    """훅이 실제로 도는지만 값싸게 판정한다 (JSON 한 줄, 훅 실행 없음).

    훅은 조용히 실패한다(fail-open) — 망가져도 에러조차 안 뜬다. 그래서
    "훅이 죽었나"를 훅으로는 알 수 없다. 대신 살아있을 때 남긴 흔적을
    **훅과 무관하게 도는 스킬 층**이 확인한다. 전체 doctor는 훅을 실제로
    실행해 느리므로, 자동으로 자주 부를 이 경로는 파일만 읽는다."""
    marker = os.path.join(root, ".hi-vibe")
    if not os.path.isdir(marker):
        print(json.dumps({"state": "not-initialized"}, ensure_ascii=False))
        return 0
    if os.path.isfile(os.path.join(marker, "optout")):
        print(json.dumps({"state": "optout"}, ensure_ascii=False))
        return 0

    beats = {}
    try:
        with open(os.path.join(marker, "state", "heartbeat.json"),
                  encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(loaded, dict):
            beats = loaded
    except (OSError, ValueError):
        beats = {}

    now = time.time()
    fresh = sorted(k for k, v in beats.items()
                   if isinstance(v, (int, float)) and now - v < STALE_AFTER)
    # 예전엔 `SessionStart`가 신선한지만 봤다("세션마다 반드시 돈다"는 전제).
    # 그런데 **세션 도중에 플러그인을 켜거나 업데이트하면** SessionStart는 이번
    # 세션에서 안 돈다 — 다음 세션에나 돈다. 그동안 PostToolUse·Stop은 멀쩡히
    # 도는데도 `stale`이 나왔고, 같은 JSON에 `last_seen_hours: 0.0`이 함께
    # 실려 **스스로 모순되는 진단**이 됐다. 실제로 그걸 본 AI는 경고를 무시했다.
    # 건강검진이 늑대소년이 되면 진짜 고장도 같이 묻힌다.
    #
    # 훅이 **하나라도** 최근에 돌았으면 훅 계층은 살아 있는 것이다. Stop 훅은
    # 매 턴 돌므로, 정말 죽었으면 `fresh`가 비어 있다.
    state = "alive" if fresh else ("stale" if beats else "never-ran")
    last = max((v for v in beats.values() if isinstance(v, (int, float))), default=0)
    # 추적 중인 `.env`도 여기서 본다. 전체 doctor에만 두면 **이미 쓰던
    # 프로젝트가 업데이트만 받았을 때 영영 모른다** — init을 다시 칠 일도,
    # doctor를 칠 일도 없기 때문이다. 파일명만 보는 검사라 값이 거의 안 든다
    # (파일 내용은 읽지 않는다).
    print(json.dumps({
        "state": state,
        "fresh_hooks": fresh,
        "last_seen_hours": round((now - last) / 3600, 1) if last else None,
        "tracked_env": tracked_env_files(root)[:5],
    }, ensure_ascii=False))
    return 0


def main():
    parser = argparse.ArgumentParser(description="hi-vibe self-diagnosis")
    parser.add_argument("--root", default=".")
    parser.add_argument("--quick", action="store_true",
                        help="훅 생존 여부만 JSON 한 줄로 (훅 실행 없음)")
    args = parser.parse_args()
    root = os.path.abspath(args.root)
    if args.quick:
        return cmd_quick(root)

    python3 = check_python3()
    files_ok = check_plugin_files()
    if python3 and files_ok:
        check_hooks_live(python3)
        check_scanner(python3)
    check_project(root)
    check_fresh_eyes(root)
    check_env_secrets(root)

    icon = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌"}
    print("👋 hi-vibe doctor — hi-vibe의 훅·스캐너만 검사합니다")
    print("   (Claude Code 설치 상태는 기본 `/doctor`가 따로 봅니다)")
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

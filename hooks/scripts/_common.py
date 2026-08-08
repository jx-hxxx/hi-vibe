"""hi-vibe 훅 공용 표면 — 정의는 주제 모듈에, 이름은 여기서 안정되게.

927줄짜리 단일 파일을 2026-08-08에 책임별로 쪼갰다:

    _base.py         훅 배관 — 입출력·게이트·심박·git·잠금 (의존 그래프의 뿌리)
    _ci.py           CI 건강 — 연속 실패를 대화창으로
    _transcript.py   대화 기록 읽기 — 요청·수정 파일·Bash 흔적·테스트 결과
    _agent_watch.py  리뷰 활동 감시 — fresh-eyes가 실제로 도는지
    _handover.py     handover 쓰기 — 이어갈 단서 남기기·회전·중복 방지

이 파일이 남아 있는 이유: 훅 5종·테스트·스킬이 전부 `_common.X`로 부른다.
그 호출부를 전부 고치는 것보다 이름의 자리를 지키는 쪽이 기계적이고,
나중에 내부를 또 옮겨도 호출부가 안 흔들린다.

두 가지 규칙:
  - **새 함수는 주제 모듈에 정의하고 여기 임포트 한 줄을 더한다.**
    여기 직접 정의하면 쪼갠 의미가 도로 사라진다.
  - **테스트에서 함수를 바꿔치기(patch)할 땐 정의된 모듈을 patch한다.**
    예: `ci_health` 내부의 `_run_gh_json`을 바꾸려면 `_ci._run_gh_json`.
    `_common._run_gh_json`을 바꿔도 `_ci` 안의 호출은 원본을 본다 —
    같은 함수의 이름표가 두 장이기 때문이다. (겉으로 부르는 이름을 바꿀
    땐 `_common.X` patch가 여전히 맞다 — 훅이 그 이름으로 부르니까.)
"""
import os
import sys

# 형제 모듈은 같은 폴더에 산다. 훅·테스트가 이미 이 폴더를 sys.path에
# 넣지만, 임포트 순서에 기대지 않도록 여기서도 보장한다.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _base import (                                    # noqa: E402
    HEARTBEAT_FILE, emit, file_lock, git_status, project_gate, read_heartbeat,
    read_payload, run, touch_heartbeat, _run_git,
)
from _ci import (                                      # noqa: E402
    CI_CACHE_TTL, CI_QUERY_TIMEOUT, ci_guard_missing, ci_health,
    _ci_cache_path, _read_ci_cache, _run_gh_json, _write_ci_cache,
)
from _transcript import (                              # noqa: E402
    bash_write_summary, bash_wrote_files, last_test_result, parse_transcript,
    safe_text, session_activity, tail_lines, test_command_segment,
    _CATCH_MARK, _DOC_SUFFIXES, _result_from_output,
)
from _agent_watch import (                             # noqa: E402
    AGENT_SESSIONS_KEEP, AGENTS_FILE, FRESH_EYES_TYPE, agent_offset,
    note_agent_activity, read_agent_activity, review_activity,
)
from _handover import (                                # noqa: E402
    WRITTEN_FILE, WRITTEN_KEEP, handover_already_written, handover_body,
    latest_entry, note_handover_written, prepend_entry, rotate,
)

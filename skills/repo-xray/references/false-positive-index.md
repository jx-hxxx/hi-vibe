# False-Positive Index

First stop BEFORE presenting any dead-candidate, duplicate, or collision
finding to the user. Match the finding against the families below; if it
matches, either soften the claim as instructed or drop it. Keep this file
compact — it ships in the skill's context budget.

Chat rule: translate a matched family into a plain-Korean reason
("프레임워크가 이름 없이 호출하는 함수예요", "테스트 러너가 알아서 불러요").
Never show FP ids to the user unless they ask for exact proof.

Structure inspired by lumin-repo-lens (MIT) — the families are our own.

## Quick map

| Finding smells like... | Family |
| --- | --- |
| decorator 붙은 파이썬 함수가 미사용 | FP-01 |
| 테스트 파일 속 심볼이 미사용 | FP-02 |
| getattr / 문자열 키 / 이벤트 이름으로 호출됨 | FP-03 |
| 스캔 안 되는 파일(.vue/.svelte/.j2/.ipynb 등)에서만 사용 | FP-04 |
| 라이브러리/패키지의 공개 API (외부 소비자용) | FP-05 |
| CLI 스크립트 / 배포 설정이 문자열 조립으로 참조 | FP-06 |
| 테스트끼리 90% 유사 (near-duplicate) | FP-D1 |
| 짧은 보일러플레이트끼리 유사 (thin wrapper, 마이그레이션) | FP-D2 |
| ESM 모듈 간 같은 함수 이름 (js_name_collisions) | FP-C1 |

## Dead-candidate families

- **FP-01 — framework registration.** Decorated Python functions (FastAPI
  routes, pytest fixtures, celery tasks, click commands) are called by the
  framework, never by name. The scanner already separates these into
  `decorated_unreferenced` — NEVER recommend deleting them. (Scanner-handled
  since v0.1.0.)
- **FP-02 — test files.** unittest/pytest/jest discover `test_*` symbols by
  naming convention. Excluded from dead candidates since v0.2.0
  (`test_*.py`, `*_test.py`, `conftest.py`, `*.test.ts` …). If a candidate
  still looks test-like (e.g. `tests/helpers.py` fixtures), say so.
- **FP-03 — dynamic dispatch.** Names built at runtime: `getattr(obj, name)`,
  handler dicts keyed by strings built via concatenation/f-string, event
  names emitted from data. Whole strings containing the identifier DO count
  as references, but constructed names are invisible. Always phrase deletion
  as "스캔한 N개 파일에서 참조를 못 찾았어요 — 동적 호출만 확인해 보세요".
- **FP-04 — unscanned surfaces.** Only `.py .js .ts .tsx .jsx .mjs .cjs
  .html .json .yml .toml .md .css` are scanned. Usage that lives only in
  `.vue`, `.svelte`, `.j2`/`.jinja`, `.ipynb`, DB-stored templates, or files
  over 2 MB is invisible. If the repo contains such files, name this blind
  spot when presenting dead candidates.
- **FP-05 — public API.** In a library/package repo (has `pyproject.toml`
  with a build backend, or `package.json` without `private: true`), exported
  symbols may have zero internal callers by design — their callers are other
  people's code. Ask what the repo ships before calling exports dead.
- **FP-06 — string-wired entry points.** Deploy/config wiring like
  `"handler": "app.main:serve"` usually still yields a token match (strings
  are tokenized), but split or templated paths do not. Check `appears_in`
  for config files before concluding.

## Duplicate / near-duplicate families

- **FP-D1 — similar tests are normal.** Near-duplicate pairs inside test
  files are usually healthy (parallel cases). Mention last, if at all;
  never lead the report with them.
- **FP-D2 — boilerplate look-alikes.** Thin wrappers, property accessors,
  migration steps, DTO builders legitimately share shape. Before suggesting
  a merge, check the two functions serve the same DOMAIN purpose, not just
  the same syntax.

## Collision families

- **FP-C1 — module scope is not a collision.** The same name defined in two
  ESM/CommonJS modules is namespaced and fine. Only browser-global scripts
  loaded by the same HTML page actually collide (later `<script>` wins).

## Living-document rule

When a finding is confirmed to be a false positive NOT covered above:
tell the user plainly, and — if you are working in the vibe-check plugin
repo itself — add a family here AND a regression test in `tests/`
(that is how FP-02 was born: the plugin's self-scan flagged its own test
classes). A false positive that gets fixed silently will return.

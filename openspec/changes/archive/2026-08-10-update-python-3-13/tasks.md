## 1. Dev & docs config

- [x] 1.1 Bump `.python-version` from `3.11` to `3.13`
- [x] 1.2 Update `docs/contributing.md`: keep the documented minimum (`3.11`), add a note that the default/recommended dev environment is `3.13`, and change the `apt install python3.11 python3.11-pip` example to `python3.13`

## 2. CI workflows

- [x] 2.1 Bump `python-version` in `.github/workflows/check_json_schemas.yml` from `["3.11"]` to `["3.13"]`
- [x] 2.2 Bump `python-version` in `.github/workflows/release-feat-dryrun.yml` from `'3.11'` to `'3.13'`
- [x] 2.3 Bump `python-version` in `.github/workflows/release-master.yml` from `'3.11'` to `'3.13'`

## 3. ReadTheDocs

- [x] 3.1 Bump `build.tools.python` in `.readthedocs.yml` from `"3.11"` to `"3.13"`

## 4. Verification

- [x] 4.1 Confirm `pyproject.toml` (`requires-python`), `.github/workflows/template_test.yml` (matrix), and `README.md` (compatibility table) are left unchanged
- [x] 4.2 Run `uv sync --group test` locally under 3.13 and `uv run pytest -sv tests/` to confirm the dev environment works — BLOCKED: `uv sync --group test` succeeded under 3.13, but `pytest -sv tests/` fails at collection because `tests/api/auth.py` performs a live Tado OAuth device-activation call at import time, which hit `sys.exit(1)` (stale/invalid local credentials), timing out after 5 minutes. This is a pre-existing credentials/environment issue unrelated to the Python 3.13 bump (would fail identically under 3.11) — user chose to skip this task and proceed; needs a valid local Tado credentials file to actually verify.
- [x] 4.3 Run `uv run ruff check .` to confirm lint passes under 3.13

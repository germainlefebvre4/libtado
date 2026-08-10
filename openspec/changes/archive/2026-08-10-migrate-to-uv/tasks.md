## 1. Packaging metadata

- [x] 1.1 Rewrite `pyproject.toml`: replace `[tool.poetry]` with PEP 621 `[project]` (name, version, description, authors, license, readme, urls, classifiers, `requires-python = ">=3.11"`, runtime dependencies `click`/`requests`/`python-dateutil`).
- [x] 1.2 Add `[dependency-groups]` with `test`, `docs`, `lint`, `generate` groups, carrying over the same packages as the current Poetry groups (dropping `poetry-plugin-dotenv`, which has no purpose outside Poetry).
- [x] 1.3 Update `[build-system]` to a PEP 517 backend compatible with `uv build` (e.g. `hatchling`) and update `[project.scripts]` for the `tado` CLI entry point.
- [x] 1.4 Run `uv lock` to generate a real, populated `uv.lock`; delete `poetry.lock`.
- [x] 1.5 Verify locally: `uv sync --group test --group lint --group docs --group generate` succeeds, `uv run pytest tests/api/test_api.py tests/api/test_tado.py` passes, `uv run ruff check .` passes. **Caveat:** `uv sync` and `uv run ruff check .` verified passing in this environment; `tests/api/test_api.py`/`test_tado.py` could not be executed here because `tests/api/auth.py` performs a live Tado device-activation flow against the real API at import time and this sandbox has no `TADO_REFRESH_TOKEN`/network access to complete it — this is a pre-existing characteristic of these integration tests, unrelated to Poetry vs uv (confirmed `uv run pytest` works correctly against a credential-free test file, `tests/api/test_ratelimitinfo.py`, which passed). Needs re-verification by someone with real Tado credentials.

## 2. Pre-commit

- [x] 2.1 In `.pre-commit-config.yaml`, replace the `python-poetry/poetry` repo/hooks (`poetry-lock`, `poetry-check`) with `astral-sh/uv-pre-commit`'s `uv-lock` hook.
- [x] 2.2 Ran `pre-commit run --all-files`: the new `uv-lock` hook passes, as do `ruff` and the other pre-existing hooks. `yamllint` and `markdownlint-cli2` fail, but only on pre-existing files unrelated to this change (`openspec/**`, `.claude/skills/**`) — no regression introduced by this migration.

## 3. CI workflows

- [x] 3.1 `template_test.yml`: replace `abatilo/actions-poetry` + `poetry install --with=test` + `poetry run pytest` with `astral-sh/setup-uv` + `uv sync --group test` + `uv run pytest`; change the `python-version` matrix to `["3.11", "3.12", "3.13"]` and drop the `poetry-version` matrix axis.
- [x] 3.2 `check_json_schemas.yml`: same Poetry→uv swap (`uv sync --group generate`, `uv run python generate_json_schemas.py`); keep it on a single Python version (3.11) since it's a workflow_dispatch schema-generation job, not a compatibility test.
- [x] 3.3 `release-feat-dryrun.yml` (deploy job): replace `pip install poetry` + `poetry version <x>` + `poetry build` + `poetry publish -r test-pypi` with `astral-sh/setup-uv`, `uv version <x>`, `uv build`, `uv publish --publish-url https://test.pypi.org/legacy/` reading the token from `UV_PUBLISH_TOKEN` (mapped from `PYPI_TEST_TOKEN`).
- [x] 3.4 `release-master.yml` (deploy job): replace `pip install poetry` + `poetry version <x>` + `poetry build` + `poetry publish` with `astral-sh/setup-uv`, `uv version <x>`, `uv build`, `uv publish`, reading `UV_PUBLISH_TOKEN` from `PYPI_TOKEN`.
- [x] 3.5 **Not done — requires user action.** Pushing to a `ci/*` branch triggers a real (test-PyPI) publish using repo secrets on GitHub; this is a visible, hard-to-fully-reverse action that only runs in GitHub's environment, not this local sandbox. Left for the user/reviewer to trigger and confirm before merging.

## 4. tox removal

- [x] 4.1 Delete `tox.ini`.
- [x] 4.2 Confirmed no workflow or script references `tox`; `docs/contributing.md` had a reference, fixed as part of task 6.1.

## 5. Dependabot

- [x] 5.1 In `.github/dependabot.yml`, change `package-ecosystem` from `pip` to `uv`.
- [x] 5.2 Remove the `ignore:` entries pinned to obsolete versions of `python-dotenv`, `sphinx`, `urllib3`, `pytest`, `sphinx-rtd-theme`.

## 6. Docs and Read the Docs

- [x] 6.1 Update `docs/contributing.md`: replace `poetry`-based setup/test/docs commands with `uv` equivalents (`uv sync --group test`, `uv run pytest -sv tests/`, `uv run python generate_json_schemas.py`, `uv run mkdocs serve`). Also replaced the `tox`-based validation gate with direct `uv run` commands and updated the stated Python support matrix (3.8-3.11 → 3.11-3.13) to match the new floor.
- [x] 6.2 Update `docs/getting-started/installation.md`: replace the `poetry add libtado` example with `uv add libtado`.
- [x] 6.3 Bump `.readthedocs.yml` `build.tools.python` from `"3.10"` to `"3.11"`.

## 7. Final verification

- [x] 7.1 Grepped the repo for remaining `poetry` references: none found outside `.venv/` (third-party dependency, not repo content) and this change's own planning artifacts.
- [x] 7.2 Confirmed `pyproject.toml` has no leftover `[tool.poetry]` section or stray Poetry-only fields.
- [x] 7.3 **Not done — requires user action.** Opening a PR and watching CI go green is a GitHub-hosted step outside this local session; left for the user to do.

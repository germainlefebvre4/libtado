## 1. Packaging metadata

- [ ] 1.1 Rewrite `pyproject.toml`: replace `[tool.poetry]` with PEP 621 `[project]` (name, version, description, authors, license, readme, urls, classifiers, `requires-python = ">=3.11"`, runtime dependencies `click`/`requests`/`python-dateutil`).
- [ ] 1.2 Add `[dependency-groups]` with `test`, `docs`, `lint`, `generate` groups, carrying over the same packages as the current Poetry groups (dropping `poetry-plugin-dotenv`, which has no purpose outside Poetry).
- [ ] 1.3 Update `[build-system]` to a PEP 517 backend compatible with `uv build` (e.g. `hatchling`) and update `[project.scripts]` for the `tado` CLI entry point.
- [ ] 1.4 Run `uv lock` to generate a real, populated `uv.lock`; delete `poetry.lock`.
- [ ] 1.5 Verify locally: `uv sync --group test --group lint --group docs --group generate` succeeds, `uv run pytest tests/api/test_api.py tests/api/test_tado.py` passes, `uv run ruff check .` passes.

## 2. Pre-commit

- [ ] 2.1 In `.pre-commit-config.yaml`, replace the `python-poetry/poetry` repo/hooks (`poetry-lock`, `poetry-check`) with `astral-sh/uv-pre-commit`'s `uv-lock` hook.
- [ ] 2.2 Run `pre-commit run --all-files` and confirm it passes (including the new `uv-lock` hook) with no unrelated regressions.

## 3. CI workflows

- [ ] 3.1 `template_test.yml`: replace `abatilo/actions-poetry` + `poetry install --with=test` + `poetry run pytest` with `astral-sh/setup-uv` + `uv sync --group test` + `uv run pytest`; change the `python-version` matrix to `["3.11", "3.12", "3.13"]` and drop the `poetry-version` matrix axis.
- [ ] 3.2 `check_json_schemas.yml`: same Poetry→uv swap (`uv sync --group generate`, `uv run python generate_json_schemas.py`); keep it on a single Python version (3.11) since it's a workflow_dispatch schema-generation job, not a compatibility test.
- [ ] 3.3 `release-feat-dryrun.yml` (deploy job): replace `pip install poetry` + `poetry version <x>` + `poetry build` + `poetry publish -r test-pypi` with `astral-sh/setup-uv`, `uv version <x>`, `uv build`, `uv publish --publish-url https://test.pypi.org/legacy/` reading the token from `UV_PUBLISH_TOKEN` (mapped from `PYPI_TEST_TOKEN`).
- [ ] 3.4 `release-master.yml` (deploy job): replace `pip install poetry` + `poetry version <x>` + `poetry build` + `poetry publish` with `astral-sh/setup-uv`, `uv version <x>`, `uv build`, `uv publish`, reading `UV_PUBLISH_TOKEN` from `PYPI_TOKEN`.
- [ ] 3.5 Push to a `ci/*` branch to exercise `release-feat-dryrun.yml` end-to-end (dry-run publish to test PyPI) and confirm it succeeds before merging.

## 4. tox removal

- [ ] 4.1 Delete `tox.ini`.
- [ ] 4.2 Confirm no workflow, doc, or script still references `tox`.

## 5. Dependabot

- [ ] 5.1 In `.github/dependabot.yml`, change `package-ecosystem` from `pip` to `uv`.
- [ ] 5.2 Remove the `ignore:` entries pinned to obsolete versions of `python-dotenv`, `sphinx`, `urllib3`, `pytest`, `sphinx-rtd-theme`.

## 6. Docs and Read the Docs

- [ ] 6.1 Update `docs/contributing.md`: replace `poetry`-based setup/test/docs commands with `uv` equivalents (`uv sync --group test`, `uv run pytest -sv tests/`, `uv run python generate_json_schemas.py`, `uv run mkdocs serve`).
- [ ] 6.2 Update `docs/getting-started/installation.md`: replace the `poetry add libtado` example with `uv add libtado`.
- [ ] 6.3 Bump `.readthedocs.yml` `build.tools.python` from `"3.10"` to `"3.11"`.

## 7. Final verification

- [ ] 7.1 Grep the repo for remaining `poetry` references (excluding CHANGELOG/history) and resolve or consciously leave each one.
- [ ] 7.2 Confirm `pyproject.toml` has no leftover `[tool.poetry]` section and no stray Poetry-only fields.
- [ ] 7.3 Open a PR and confirm `lint.yml`, `template_test.yml` (via whichever trigger applies), and `conventional-commit.yml` all pass green.

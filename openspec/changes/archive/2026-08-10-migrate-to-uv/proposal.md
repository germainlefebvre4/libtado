## Why

Poetry is the current dependency and packaging manager, but the repo already contains an abandoned `uv.lock`/`.python-version` experiment, and the real Python support matrix (CI only runs 3.11, tox lists 3.8-3.12 without actually installing/running them) has drifted from what `pyproject.toml` declares (`>=3.8.1,<4.0`). Moving to `uv` removes this drift, speeds up CI (native Rust resolver/installer vs Poetry), and lets us drop `tox` since `uv` can run multi-Python matrices natively without it.

## What Changes

- **BREAKING**: Drop Poetry as the project's package manager; replace `[tool.poetry]` in `pyproject.toml` with PEP 621 `[project]` metadata and `uv`-native dependency groups.
- **BREAKING**: Raise minimum supported Python to `>=3.11` (aligns with the existing but unused `uv.lock`/`.python-version`); drop the (already-untested) 3.8-3.10 claims.
- Replace the four Poetry dependency groups (`test`, `docs`, `lint`, `generate`) with `[dependency-groups]` (PEP 735).
- Replace `poetry.lock` with a real, populated `uv.lock` (the current one is an empty stub).
- Remove `tox.ini`; CI runs `uv run` directly across a real Python matrix: 3.11, 3.12, 3.13.
- Update `.pre-commit-config.yaml`: replace the `python-poetry/poetry` hooks (`poetry-lock`, `poetry-check`) with `astral-sh/uv-pre-commit` equivalents.
- Update CI workflows (`.github/workflows/template_test.yml`, `check_json_schemas.yml`, `release-feat-dryrun.yml`, `release-master.yml`): replace `abatilo/actions-poetry` + `poetry install/run/version/build/publish` with `astral-sh/setup-uv` + `uv sync`/`uv run`/`uv version`/`uv build`/`uv publish`.
- Update `.github/dependabot.yml`: change `package-ecosystem` from `pip` to `uv`, and clean out the `ignore:` entries pinned to long-obsolete dependency versions.
- Update contributor docs (`docs/contributing.md`, `docs/getting-started/installation.md`) to reference `uv` commands instead of `poetry`.

## Capabilities

No spec-level behavior of the `libtado` library or CLI changes — this is packaging, CI, and tooling only. `skip_specs: true` is set in `.openspec.yaml`.

### New Capabilities
(none)

### Modified Capabilities
(none)

## Impact

- **Code**: `pyproject.toml`, `poetry.lock` (removed) / `uv.lock` (populated), `.python-version` (unchanged, already 3.11), `tox.ini` (removed).
- **CI**: `.github/workflows/template_test.yml`, `check_json_schemas.yml`, `release-feat-dryrun.yml`, `release-master.yml`.
- **Dependabot**: `.github/dependabot.yml`.
- **Pre-commit**: `.pre-commit-config.yaml`.
- **Docs**: `docs/contributing.md`, `docs/getting-started/installation.md`.
- **Contributors**: local dev setup instructions change from `poetry install`/`poetry run` to `uv sync`/`uv run`; anyone on Python 3.8-3.10 can no longer use the dev environment.
- **Release process**: PyPI publish steps (test and prod) switch from `poetry build`/`poetry publish` to `uv build`/`uv publish`.

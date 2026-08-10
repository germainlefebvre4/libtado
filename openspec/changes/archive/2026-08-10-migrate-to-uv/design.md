## Context

See proposal.md for motivation. Current state relevant to the approach:

- Poetry drives dependency resolution (`poetry.lock`), packaging (`[tool.poetry]`, `poetry build/publish`), and four dependency groups (`test`, `docs`, `lint`, `generate`).
- A stray `uv.lock` (empty stub, `requires-python = ">=3.11"`) and `.python-version` (`3.11`) already exist, unreferenced by any tooling — treated here as the intended target state, not leftover cruft to revert.
- CI (`template_test.yml`, `check_json_schemas.yml`) installs Poetry via `abatilo/actions-poetry` and runs a single-Python (3.11) matrix; the wider `python-version` matrix is already commented out.
- `tox.ini` declares a `py38..312` env list that is never actually exercised (`skip_install = true`, hardcoded `deps`), so removing it drops no real coverage.
- Release workflows (`release-feat-dryrun.yml`, `release-master.yml`) use `poetry version`, `poetry build`, `poetry publish` with token-based auth (`PYPI_TEST_TOKEN`, `PYPI_TOKEN`).
- `.readthedocs.yml` pins `python: "3.10"` for docs builds via a plain `docs/requirements.txt` (no Poetry/uv involved) — inconsistent with the new `>=3.11` floor.

## Goals / Non-Goals

**Goals:**
- Single source of truth for dependencies/lockfile: `uv` + `uv.lock`, no Poetry artifacts left behind.
- CI, pre-commit, dependabot, and release all drive installs/builds/publishes through `uv`.
- Python support matrix in CI matches what's actually declared and tested: 3.11, 3.12, 3.13.
- No functional regression in what CI currently verifies (lint, tests, JSON schema generation, releases).

**Non-Goals:**
- No change to `libtado`'s runtime behavior, public API, or CLI.
- No change to the semantic-release / cocogitto versioning strategy itself (only the commands that consume the resulting version).
- Not attempting real 3.8-3.10 support — that claim was already fictional (untested) and is dropped, not preserved.

## Decisions

**Dependency declaration: PEP 621 `[project]` + PEP 735 `[dependency-groups]`**
`uv` natively supports both. Runtime deps (`click`, `requests`, `python-dateutil`) move to `[project.dependencies]`; the four Poetry groups become `[dependency-groups]` entries of the same names (`test`, `docs`, `lint`, `generate`), preserving `uv sync --group <name>` / `uv run --group <name>` as the direct replacement for `poetry install --with <name>` / `poetry run`. Alternative considered: `[tool.uv.dev-dependencies]` (single flat dev group) — rejected because it collapses the existing test/docs/lint/generate separation that CI and contributors rely on independently.

**Lockfile: regenerate `uv.lock` from scratch**
The existing `uv.lock` is an empty stub (no resolved deps). It gets regenerated via `uv lock` once `[project]`/`[dependency-groups]` are in place, rather than hand-edited.

**Python floor: `>=3.11`, matrix 3.11/3.12/3.13**
Matches the already-present `.python-version` and `uv.lock` `requires-python`. CI matrix in `template_test.yml` becomes a real `matrix.python-version: ["3.11", "3.12", "3.13"]` using `astral-sh/setup-uv`'s `python-version` passthrough (or `uv python install` + `uv run --python`), replacing the single hardcoded 3.11 job.

**Drop `tox.ini` entirely**
`tox` added no real coverage (see Context). `uv run --python <version> pytest ...` inside the CI matrix replaces it; local contributors get the same effect via `uv run pytest`. No tox-equivalent wrapper is reintroduced.

**CI action: `astral-sh/setup-uv` replaces `abatilo/actions-poetry`**
Official Astral action; supports pinning a `uv` version, Python installation, and caching. `poetry install [--with X]` → `uv sync [--group X]`; `poetry run <cmd>` → `uv run <cmd>`.

**Pre-commit: `astral-sh/uv-pre-commit` replaces `python-poetry/poetry` hooks**
The `uv-lock` hook (fails/fixes when `uv.lock` is out of sync with `pyproject.toml`) covers what `poetry-lock` + `poetry-check` did together — no separate "check" hook is needed since `uv lock --check`-style validation is what the hook runs.

**Release: `uv version` / `uv build` / `uv publish` replace the Poetry equivalents**
`uv version <x>` sets the version in `pyproject.toml` (same role as `poetry version <x>`); `uv build` produces sdist/wheel; `uv publish` uploads, reading a token from `UV_PUBLISH_TOKEN` (mapped from the existing `PYPI_TEST_TOKEN`/`PYPI_TOKEN` secrets) instead of `poetry config pypi-token.<repo>`. Trusted publishing (OIDC, no stored token) was considered but is out of scope here — it would change the security model of releases beyond a mechanical tool swap; can be a follow-up change.

**`.readthedocs.yml` Python bump: 3.10 → 3.11**
Not strictly a package-manager concern, but leaving docs builds on a Python version below the project's new floor would be an inconsistency introduced by this change, so it's bumped alongside. `docs/requirements.txt` (plain pip) is left as-is — Read the Docs' own build environment doesn't consume `uv`/`pyproject.toml` here, so there's no further migration surface on that path.

**Dependabot: `pip` → `uv` ecosystem, stale `ignore:` entries dropped**
GitHub Dependabot has native `package-ecosystem: uv` support (resolves `pyproject.toml` + `uv.lock` directly, no Poetry-specific handling needed). The current `ignore:` list pins versions of `python-dotenv`, `sphinx`, `urllib3`, `pytest`, `sphinx-rtd-theme` that predate the current dependency set by multiple major versions (dead weight from years of accumulation) — removed rather than translated.

## Risks / Trade-offs

- **Dropping 3.8-3.10 is a real, user-facing floor change for library consumers** (not just CI/dev tooling) since `requires-python` in `pyproject.toml` governs what `pip install libtado` accepts → Mitigation: called out as **BREAKING** in the proposal; ship as a minor/major version bump per the project's semantic-release conventions, not silently.
- **`uv publish` token/env var behavior differs from `poetry config pypi-token.*`** (uv expects `UV_PUBLISH_TOKEN` env rather than a persisted config file) → Mitigation: set the env var directly from the existing GitHub secrets in the workflow step; no new secrets need to be created.
- **Real 3.12/3.13 testing may surface latent incompatibilities** the fictional tox matrix never caught → Mitigation: this is the point of the change (turning theoretical support into tested support); any failures found are legitimate bugs to fix as part of this change's tasks, not a reason to revert to a narrower matrix.
- **`uv-pre-commit`'s `uv-lock` hook may behave slightly differently from the combined `poetry-lock`+`poetry-check` pair** (e.g., exact autofix vs check-only semantics) → Mitigation: verify hook behavior locally (`pre-commit run uv-lock --all-files`) before merging.

## Migration Plan

1. Rewrite `pyproject.toml`: `[project]` + `[dependency-groups]`, `requires-python = ">=3.11"`.
2. Run `uv lock` to generate a real `uv.lock`; delete `poetry.lock`.
3. Update `.pre-commit-config.yaml` (swap Poetry hooks for `uv-pre-commit`); run `pre-commit run --all-files` to confirm.
4. Update CI workflows one at a time (`lint.yml` unaffected — no Poetry there; `template_test.yml`, `check_json_schemas.yml`, `release-feat-dryrun.yml`, `release-master.yml`), verifying each via a dry-run branch push before merging (the repo already has `ci/*` and `feat/*` branches wired to `release-feat-dryrun.yml` for exactly this).
5. Delete `tox.ini`.
6. Update `.github/dependabot.yml` (ecosystem + ignore cleanup).
7. Bump `.readthedocs.yml` Python to 3.11.
8. Update `docs/contributing.md` and `docs/getting-started/installation.md`.
9. Merge; first real dependabot `uv` PR and first real release-dryrun run serve as end-to-end validation.

Rollback: since Poetry and uv artifacts are mutually exclusive in `pyproject.toml` (single `[project]`/`[tool.poetry]` block), rollback is a straight `git revert` of the migration commit(s); no data migration or irreversible external state is involved.

## Open Questions

None — all decisions needed to write specs/tasks are resolved above.

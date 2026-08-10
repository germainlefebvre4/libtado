## Why

The project's default development/CI/docs Python version is pinned to 3.11, while the test matrix already covers 3.11, 3.12, and 3.13. Python 3.11 nears its later maintenance stages and 3.13 is the current stable release; aligning the default tooling with 3.13 keeps local dev, lint/release CI jobs, and ReadTheDocs builds on a version that matches where the ecosystem is heading, without dropping support for older versions.

## What Changes

- Bump the pinned dev Python version in `.python-version` from `3.11` to `3.13`.
- Bump the ReadTheDocs build Python version in `.readthedocs.yml` from `3.11` to `3.13`.
- Bump the single-version CI jobs (`check_json_schemas.yml`, `release-feat-dryrun.yml`, `release-master.yml`) from `3.11` to `3.13`.
- Update `docs/contributing.md`: keep the documented minimum (`3.11`) unchanged, add a note that the default/recommended dev environment now uses `3.13`, and update the `apt install` example command to `python3.13`.
- No change to `pyproject.toml` (`requires-python` stays `>=3.11`), no change to the `template_test.yml` test matrix (stays `3.11`/`3.12`/`3.13`), no change to `README.md`'s compatibility table (already lists 3.13 as supported).

This is a pure tooling/CI/docs change: **no behavior of the library changes and no breaking change for consumers of `libtado`**. A prior codebase check found no usage of modules removed in Python 3.13 (PEP 594 "dead batteries", e.g. `cgi`, `telnetlib`, `nntplib`) or deprecated APIs (`datetime.utcnow()`, `locale.getdefaultlocale()`), so there is no runtime migration work needed in `libtado/`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None — this change touches only tooling configuration and documentation, not library behavior. `skip_specs: true` is set in `.openspec.yaml`.

## Impact

- **Config files**: `.python-version`, `.readthedocs.yml`
- **CI workflows**: `.github/workflows/check_json_schemas.yml`, `.github/workflows/release-feat-dryrun.yml`, `.github/workflows/release-master.yml`
- **Docs**: `docs/contributing.md`
- **Unaffected**: `pyproject.toml`, `.github/workflows/template_test.yml`, `README.md`, `libtado/` source code

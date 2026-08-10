## Why

`mkdocs.yml` sets `show_if_no_docstring: false` for mkdocstrings, and `docs/api/reference.md` renders the `Tado` class as-is (`::: libtado.api.Tado`). Twelve public methods on `Tado` have no docstring — including the entire OAuth2 device-code flow (`__init__`, `login_device_flow`, `check_device_activation`, `device_activation`, `device_ready`, `refresh_auth`, `save_token`, `load_token`, `set_oauth_token`, `get_device_activation_status`, `get_device_verification_url`) plus the deprecated `set_schedule_block_by_day_type`. These methods are silently absent from the published API Reference page — not a style nitpick, a real coverage gap on the trickiest part of the API for a new user. This was already flagged as an explicit follow-up in `fix-docs-code-examples` (out of scope there, tracked for later).

## What Changes

- Add docstrings to the 12 currently-undocumented public methods on `Tado` in `libtado/api.py`, following the existing Google-style convention (`Parameters:` / `Returns:`, `??? info "Result example"` blocks where a JSON response exists). The auth/device-flow methods get a flow-oriented description (when to call what, side effects on `self.refresh_token`/`self.device_code`/etc.) rather than a JSON example, since there's no API JSON payload to show for most of them. `set_schedule_block_by_day_type` gets a one-line deprecation notice pointing to `set_schedule_blocks()`.
- Add a class-level docstring to `Tado` and to `RateLimitInfo`.
- Split the generated API docs into two pages so technical/auth plumbing doesn't clutter the functional reference:
  - New `docs/api/authentication.md`: `::: libtado.api.Tado` scoped via mkdocstrings' `members:` option to the ~11 auth/device-flow methods. Linked from the mkdocs nav and cross-referenced from `docs/getting-started/usage.md`.
  - `docs/api/reference.md`: same `::: libtado.api.Tado` block, `members:` option scoped to the ~53 functional (home/zone/schedule/energy) methods, so it stays focused on "control your thermostat" usage.
  - No change to `libtado/api.py`'s class structure — `Tado` stays a single class. The split is a documentation-rendering concern only, implemented via mkdocstrings' explicit member list.
- Add a non-blocking docstring-coverage check to CI: enable ruff's `D` (pydocstyle) rule set and run it as a step with `continue-on-error: true` in `.github/workflows/lint.yml`, so missing docstrings are reported on future PRs without failing the build. Ruff is already a dev dependency and already wired into that workflow, so this adds no new tooling.

No behavior of the library changes — this is documentation, docstrings, and CI lint configuration only.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None — no spec-level behavior changes. `skip_specs: true` is set in this change's `.openspec.yaml`.

## Impact

- **Affected files**: `libtado/api.py` (docstrings only, no logic changes), `docs/api/reference.md`, `docs/api/authentication.md` (new), `docs/getting-started/usage.md` (cross-reference link), `mkdocs.yml` (nav entry + `members:` options), `.github/workflows/lint.yml` (new non-blocking lint step), `pyproject.toml` (ruff `D` rule selection, if not already broad-selected).
- **Dependencies**: none new — reuses the existing ruff dev dependency.
- **Out of scope**: `RateLimitInfo`'s private `_parse_header`, the private `_api_*_call` helpers, `libtado/cli_utils.py`, and the nested helper functions inside `libtado/__main__.py`'s `status` command — none of these are rendered by mkdocstrings (private, or not exposed in a `:::` block) so leaving them undocumented has no doc-visibility impact. Could be picked up in a later pass if the ruff `D` report highlights them as worth closing anyway.

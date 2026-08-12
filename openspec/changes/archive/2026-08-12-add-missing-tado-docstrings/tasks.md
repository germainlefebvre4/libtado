## 1. Docstrings in `libtado/api.py`

- [x] 1.1 Add a class docstring to `RateLimitInfo` (summarize what it tracks: granted/remaining calls, reset time, parsed from the `ratelimit`/`ratelimit-policy` headers).
- [x] 1.2 Add a class docstring to `Tado` (summarize: binds to the Tado API v2, handles OAuth2 device-code auth, exposes home/zone/schedule/energy methods).
- [x] 1.3 Add a docstring to `__init__` covering `saved_refresh_token`/`token_file_path` params and the auth branch it triggers (resume via refresh token vs. start `login_device_flow`).
- [x] 1.4 Add a docstring to `get_device_activation_status` (what it returns, when it's non-`NOT_STARTED`).
- [x] 1.5 Add a docstring to `get_device_verification_url` (what it returns, when it's populated vs. `None`).
- [x] 1.6 Add a docstring to `set_oauth_token` covering the `response` param shape, what it mutates on `self`, and its return value.
- [x] 1.7 Add a docstring to `load_token` (side effect on `self.refresh_token`, return meaning, `token_file_path` requirement).
- [x] 1.8 Add a docstring to `refresh_auth` covering `refresh_token`/`force_refresh` params, the early-return condition, and return meaning.
- [x] 1.9 Add a docstring to `save_token` (no-op conditions, side effect of writing `token_file_path`).
- [x] 1.10 Add a docstring to `login_device_flow` covering preconditions (raises if already started), side effects on `self`, and the returned `DeviceActivationStatus`.
- [x] 1.11 Add a docstring to `check_device_activation` covering polling behavior, the exception on expiry, and return meaning (`True`/`False`).
- [x] 1.12 Add a docstring to `device_activation` (blocking loop until activation, what it calls on success).
- [x] 1.13 Add a docstring to `device_ready` (what it finalizes: `self.id`, clearing `user_code`/`device_verification_url`, setting `COMPLETED`).
- [x] 1.14 Add a one-line deprecation docstring to `set_schedule_block_by_day_type` pointing to `set_schedule_blocks()`.
- [x] 1.15 Run `ruff check libtado/api.py` locally to confirm no unrelated lint regressions from the new docstrings (indentation, line length).

## 2. Documentation restructuring

- [x] 2.1 Create `docs/api/authentication.md` with a `::: libtado.api.Tado` block scoped via `options.members` to: `__init__`, `login_device_flow`, `check_device_activation`, `device_activation`, `device_ready`, `refresh_auth`, `save_token`, `load_token`, `set_oauth_token`, `get_device_activation_status`, `get_device_verification_url`, `get_rate_limit_info`.
- [x] 2.2 Update `docs/api/reference.md`'s `::: libtado.api.Tado` block with `options.members` listing the remaining ~53 functional methods (everything except the 12 in 2.1 and the private `_`-prefixed helpers).
- [x] 2.3 Add `docs/api/authentication.md` to the `nav` section of `mkdocs.yml`, alongside `docs/api/usage.md` and `docs/api/reference.md`.
- [x] 2.4 Add a one-line cross-reference link to `docs/api/authentication.md` from `docs/getting-started/usage.md`'s existing token/auth section.
- [x] 2.5 Run `mkdocs build --strict` (or `mkdocs serve` and inspect manually) to confirm both pages render the intended members and no method is missing from both pages or duplicated across them.

## 3. Non-blocking docstring-coverage check

- [x] 3.1 ~~Add a `[tool.ruff.lint]` `select` entry in `pyproject.toml` enabling `D100`-`D107`~~ **Skipped** - `pyproject.toml` isn't the active ruff config (the repo has a root `.ruff.toml`, which ruff reads instead and ignores `pyproject.toml`'s `[tool.ruff]`); editing `.ruff.toml` was tried and reverted because it made the existing *blocking* `ruff` CI step fail (129 new errors repo-wide). See design.md "Implementation Deviation". Task 3.2's explicit `--select` flag delivers the coverage signal without this edit.
- [x] 3.2 Add a step to `.github/workflows/lint.yml` running `ruff check --select D100,D101,D102,D103,D104,D105,D106,D107` with `continue-on-error: true`, separate from the existing blocking ruff step.
- [x] 3.3 Run the new ruff selection locally against the full `libtado/` tree and confirm it reports the intentionally-out-of-scope gaps (private helpers, `cli_utils.py`, `__main__.py` nested functions) without failing, and reports zero missing docstrings on `Tado`'s public methods.

## 4. Verification

- [x] 4.1 Re-run the full test suite (`pytest`) to confirm the docstring-only changes to `libtado/api.py` introduced no behavior change.
- [x] 4.2 Review the rendered `docs/api/reference.md` and `docs/api/authentication.md` output side by side against the method lists in design.md Decision 2/3 to confirm the split matches intent.

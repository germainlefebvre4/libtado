# Proposal

## Why

`libtado/api.py` talks to five Tado hosts through five near-identical `_api_*_call` helpers (~160 lines of copy-pasted `call_get/put/post/delete` closures), none of which reuses a connection (`requests.get/put/...` per call) or reacts to HTTP 429. Since Tado introduced strict API rate limits, a 429 surfaces as a bare `HTTPError` that callers cannot distinguish from any other failure, and the library already knows the reset time (`RateLimitInfo`) but never uses it. On top of that, the library reports problems by `print()`ing to stdout, calling `sys.exit(1)` from inside library code, and raising bare `Exception`, which makes it unsafe to embed (Home Assistant-style integrations, long-running scripts, services).

## What Changes

- Replace the five `_api_call`, `_api_acme_call`, `_api_minder_call`, `_api_energy_insights_call` and `_api_energy_bob_call` bodies with a single request pipeline (`_request(base_url, cmd, data, method)`); the five helpers remain as thin wrappers that only pick the base URL, so every existing endpoint method keeps its current call site and return value.
- Route all API traffic through one lazily-created `requests.Session` per `Tado` instance (connection reuse, shared default headers/timeout).
- Handle HTTP 429: record the response's rate-limit headers, then wait for the advertised reset time (`ratelimit` `t=`, documented by Tado; `Retry-After` as fallback) and retry, bounded by a configurable maximum number of retries and a maximum acceptable wait; when the wait would exceed that bound (e.g. a daily quota that resets in hours), fail fast with a dedicated exception instead of blocking the caller.
- Introduce a `TadoError` exception hierarchy: `TadoHTTPError` (subclass of `requests.exceptions.HTTPError`, so existing `except requests.HTTPError` code keeps working), `TadoRateLimitError`, and `TadoAuthError` for OAuth device-flow problems.
- Replace library-side `print()` with the standard `logging` module (`logging.getLogger("libtado")`), replace `sys.exit(1)` in `check_device_activation()` with a raised `TadoAuthError`, replace bare `Exception(...)` with `TadoAuthError`, replace the schedule `print` error paths with `ValueError` / a logged warning, and emit a real `DeprecationWarning` for `set_schedule_block_by_day_type()`.
- The CLI (`libtado/__main__.py`) takes over the user-facing login prompt and converts `TadoError` into a clean `click.ClickException`, so interactive use keeps working without the library writing to stdout.
- **BREAKING** (behavioral, no signature change): code that relied on `Tado.login_device_flow()` / `check_device_activation()` printing the verification URL to stdout must now read `get_device_verification_url()` (already documented in the README) or enable `logging` at INFO; code catching `SystemExit` from the device flow must catch `TadoAuthError`; `set_schedule_blocks()` with an invalid `schedule` now raises `ValueError` instead of printing and returning `None`.
- New optional constructor arguments on `Tado` (`max_retries`, `max_retry_wait`), additive and defaulted.

## Capabilities

### New Capabilities
- `api-http-transport`: how every Tado API call is sent: one shared request pipeline across all five Tado hosts, a reused session, and bounded automatic handling of HTTP 429 using `Retry-After`.
- `api-error-reporting`: how the library reports failures and progress to its callers: a typed exception hierarchy compatible with `requests` HTTP errors, and diagnostics through `logging` instead of stdout / process exit.

### Modified Capabilities
_(none — `openspec/specs/` only contains the API-drift specs, which are unaffected.)_

## Impact

- Changed: `libtado/api.py` (request helpers, `__init__`, device-flow methods, `set_schedule_blocks`, `set_schedule_block_by_day_type`), `libtado/__main__.py` (login prompt, error conversion), `libtado/cli_utils.py` untouched.
- Added: exception classes (in `libtado/api.py`, or a `libtado/exceptions.py` re-exported from `libtado.api`; decided in design.md).
- Tests: `tests/api/test_tado.py` (new 429/retry/session/exception coverage; `capsys`-based schedule test updated), `tests/api/test_tado_auth.py` (the `SystemExit` and bare `Exception` assertions updated), `tests/cli/test_cli.py` (currently an empty placeholder, gains login-prompt and error-conversion tests). The `tado_unauthenticated` fixture builds the client with `Tado.__new__`, so the session must be created lazily rather than only in `__init__`.
- Docs: `docs/faq.md` (429 entry), `docs/api/usage.md` / `docs/api/authentication.md` (exceptions, logging, retry options).
- No new runtime dependency; `requests` and the standard library are sufficient. No change to endpoint method signatures or return shapes.
- Interacts with the in-flight `tado-api-drift-detection` change only through `requests` mocking (`responses`/`vcrpy` both patch at the `requests` adapter level, so a `Session` is transparent to them).

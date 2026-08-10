## Why

`tests/api/test_api.py` and `tests/cli/test_cli.py` are not unit tests: `tests/api/auth.py` builds a real, live-authenticated `Tado` client from environment credentials at import time (and can trigger the OAuth device flow), and every test in `test_api.py` exercises the real Tado cloud API with assertions no stronger than `isinstance(response, dict)`. `Tado.__init__` itself performs a network call unconditionally, so the class cannot even be instantiated in isolation today. On top of that, `.github/workflows/test.yml` and `scheduled.yml` are both fully commented out, so none of this runs automatically — the ~55-method public surface of `libtado/api.py`, including every mutating `set_*`/`delete_*` method and the OAuth/token lifecycle, has no enforced regression protection at all. `tests/cli/test_cli.py` is an empty stub, leaving the ~20 Click commands in `libtado/__main__.py` and `libtado/cli_utils.py` untested too.

## What Changes

- Add `responses` as a test dependency for declarative HTTP mocking.
- Add a fixture/helper that constructs a `Tado` client for unit tests without performing real network I/O (bypassing the network calls in `__init__`), so `get_*`/`set_*`/`delete_*` methods can be tested in isolation.
- Add unit tests covering the OAuth/token lifecycle in isolation (`refresh_auth`, `login_device_flow`, `check_device_activation`, `device_activation`, `set_oauth_token`, `load_token`/`save_token`), mocking the `login.tado.com` endpoints with `responses`.
- Add unit tests for every public method on `Tado` (all `get_*`, `set_*`, `delete_*`), covering success responses, request construction (URL, headers, JSON payload), and HTTP error handling (4xx/5xx) across all five `_api_*_call` families (`_api_call`, `_api_acme_call`, `_api_minder_call`, `_api_energy_insights_call`, `_api_energy_bob_call`).
- Move the existing live-API tests (`tests/api/test_api.py`, `tests/api/utils.py`, `tests/api/auth.py`) into a dedicated live suite, marked with a `live` pytest marker, and exclude that marker from the default `pytest` run.
- Update `pytest.ini` to register the `live` marker and exclude it by default.
- Re-enable `.github/workflows/test.yml` to run the mocked unit suite on every PR (no secrets required).

## Capabilities

### New Capabilities
<!-- none: this change adds test coverage and CI wiring for the existing libtado client; it does not change any observable behavior of the library -->

### Modified Capabilities
<!-- none -->

## Impact

- **Affected code**: `libtado/api.py` (test subject, no behavior change expected unless tests surface real bugs, e.g. the inconsistent DELETE response handling between `_api_call` and `_api_acme_call`), `tests/api/*`, `tests/cli/*`, `pytest.ini`.
- **Dependencies**: adds `responses` to the `test` dependency group in `pyproject.toml`.
- **CI**: `.github/workflows/test.yml` goes from fully disabled to running on every PR; `scheduled.yml` remains the intended home for the relocated live suite (wiring its secrets back up is out of scope for this change).
- **Existing live tests**: preserved and relocated, not deleted — they remain the regression signal against the real Tado API, just no longer run by default.

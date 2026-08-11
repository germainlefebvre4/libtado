## Why

The `pytest` job on every PR fails after ~5 minutes with a pytest `INTERNALERROR` (exit code 3, "no tests ran"), e.g. https://github.com/germainlefebvre4/libtado/actions/runs/31461591824/job/93686012769. `tests/api/live/auth.py` builds a real `Tado` client and, if no cached token is found, runs the OAuth device-activation flow (prints a login URL, polls for up to ~5 minutes, then `sys.exit(1)` on timeout) **at module import time**. `tests/api/live/test_api.py` and `tests/api/live/utils.py` both import that module. Because pytest must import a test module to discover its tests before it can apply marker filters, `addopts = -m "not live"` never gets a chance to run: the live auth side effect fires during collection regardless of the marker, and the resulting `SystemExit` escapes uncaught since it happens outside any test, corrupting the whole run.

## What Changes

- Move the live-client construction and device-activation flow out of module-level code in `tests/api/live/auth.py` into a `scope="session"` pytest fixture (in a new `tests/api/live/conftest.py`), so it only runs when a test that actually requests it is selected for execution — never during collection.
- The fixture skips immediately (`pytest.skip(...)`) if no live credentials are configured (no `TADO_REFRESH_TOKEN` and no usable `TADO_CREDENTIALS_FILE`), instead of attempting the OAuth device flow and blocking for minutes before failing.
- Update `tests/api/live/test_api.py` to receive the client via the `tado` fixture parameter instead of a module-level import.
- Delete `tests/api/live/auth.py` (logic absorbed into the fixture) and `tests/api/live/utils.py` (dead code: defines a `TestApi` class whose methods are never called anywhere in the repo; its only effect today is re-importing `auth.py` and re-triggering the same side effect).

## Capabilities

### New Capabilities
<!-- none: this fixes a test-suite/CI defect; it does not add or change any observable behavior of the libtado library -->

### Modified Capabilities
<!-- none: no spec-level behavior of the library changes -->

## Impact

- **Affected code**: `tests/api/live/auth.py` (deleted), `tests/api/live/utils.py` (deleted), `tests/api/live/test_api.py` (fixture-based `tado` parameter instead of module import), `tests/api/live/conftest.py` (new).
- **CI**: unblocks `.github/workflows/test.yml` (`pytest` job) on every PR — the default `pytest` run will no longer touch the network or the live Tado credentials at all.
- **Live suite behavior**: running `pytest -m live` without credentials now skips cleanly and immediately instead of hanging for minutes and crashing; running it with valid credentials behaves as before (OAuth device flow only when no cached token is valid).
- **No dependency or library behavior changes.**

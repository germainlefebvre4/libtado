## 1. Live-test fixture

- [x] 1.1 Create `tests/api/live/conftest.py` with a `scope="session"` `tado` fixture: check for `TADO_REFRESH_TOKEN` env var or a usable `TADO_CREDENTIALS_FILE` (exists, valid JSON, non-empty `refresh_token`); call `pytest.skip("no Tado live credentials configured")` immediately if neither is present.
- [x] 1.2 In the fixture, when credentials are present, construct `Tado(refresh_token, credentials_file)` and, if `get_device_activation_status()` is `PENDING`, call `device_activation()` before returning the client.

## 2. Wire tests to the fixture

- [x] 2.1 In `tests/api/live/test_api.py`, remove `from tests.api.live.auth import tado` and `from tests.api.live import utils`.
- [x] 2.2 Add `tado` as a parameter to every `TestApi` test method that references the module-level `tado`, replacing the closure reference with the injected fixture argument.

## 3. Remove dead/moved code

- [x] 3.1 Delete `tests/api/live/auth.py` (logic now lives in the `conftest.py` fixture).
- [x] 3.2 Delete `tests/api/live/utils.py` (unused `TestApi` helper class with no callers in the repo).

## 4. Verify

- [x] 4.1 Run `uv run pytest` (default addopts, no live credentials in env) and confirm it collects and completes with zero network calls and no reference to `tests/api/live/auth.py` or `utils.py`.
- [x] 4.2 Run `uv run pytest -m live` with no `TADO_REFRESH_TOKEN`/`TADO_CREDENTIALS_FILE` set and confirm every live test is skipped immediately (no ~5 minute hang, no `INTERNALERROR`).
- [x] 4.3 If a local cached token or `TADO_REFRESH_TOKEN` is available, run `uv run pytest -m live` and confirm the live suite still exercises the real API as before.

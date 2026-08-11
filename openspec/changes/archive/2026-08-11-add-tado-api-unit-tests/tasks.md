## 1. Test Infrastructure Setup

- [x] 1.1 Add `responses` to the `test` dependency group in `pyproject.toml` and update the lockfile (`uv sync --group test`)
- [x] 1.2 Add `tests/api/conftest.py` with a fixture that builds a `Tado` instance via `Tado.__new__(Tado)`, bypassing `__init__`, setting `access_headers` and a far-future `refresh_at` so `refresh_auth()` is a no-op
- [x] 1.3 Add a shared `responses`-registration helper/fixture usable across method tests

## 2. Auth / Token Lifecycle Tests (`tests/api/test_tado_auth.py`)

- [x] 2.1 Test `Tado(...)` construction success path with `responses` mocking `login.tado.com/oauth2/token`
- [x] 2.2 Test `refresh_auth`: no-op when `refresh_at` is in the future; refresh path when expired or `force_refresh=True`; failure path when `force_refresh=True` and the token endpoint returns non-200
- [x] 2.3 Test `login_device_flow`: success (returns `PENDING`, sets `device_verification_url`/`user_code`), and the "already started" exception on double-start
- [x] 2.4 Test `check_device_activation`: success (sets tokens, returns `True`), `authorization_pending` (returns `False`), `expired_token` (exits), and a generic HTTP error (raises)
- [x] 2.5 Test `device_activation` end-to-end polling loop against a mocked sequence of `check_device_activation` responses
- [x] 2.6 Test `set_oauth_token`, `load_token` (missing file, empty file, existing token), and `save_token` (no `token_file_path`, no `refresh_token`, normal write)

## 3. `_api_call` Family Method Tests (`tests/api/test_tado.py`)

- [x] 3.1 Test every `get_*` method routed through `_api_call` (capabilities, devices, device_usage, early_start, home, home_state, invitations, me, mobile_devices, schedule_timetables, schedule, schedule_blocks, schedule_block_by_day_type, state, measuring_device, default_overlay, users, weather, zones, away_configuration, report, heating_circuits, installations, temperature_offset) for success response shape, URL, and query params
- [x] 3.2 Test every `set_*`/`delete_*` method routed through `_api_call` (set_home_state, set_invitation, delete_invitation, set_schedule, set_schedule_blocks, set_schedule_block_by_day_type, set_zone_name, set_early_start, set_temperature, end_manual_control, set_away_configuration, set_open_window_detection, set_incident_detection, set_temperature_offset, set_heating_system_boiler, set_zone_order) for JSON payload construction and 204-vs-200 response handling
- [x] 3.3 Test `_api_call` error handling (4xx, 5xx) and rate-limit header propagation (`_update_rate_limit_info`) for at least one representative GET, PUT, POST, and DELETE call

## 4. Other HTTP Family Method Tests (`tests/api/test_tado.py`)

- [x] 4.1 Test `get_air_comfort_geoloc` (`_api_acme_call`): success and error handling
- [x] 4.2 Test `get_incidents` and `get_running_times` (`_api_minder_call`): success and error handling
- [x] 4.3 Test `get_energy_consumption`, `set_cost_simulation`, `get_consumption_overview`, `get_consumption_details`, `get_energy_settings`, `get_energy_insights` (`_api_energy_insights_call`): success and error handling
- [x] 4.4 Test the method routed through `_api_energy_bob_call`: success and error handling
- [x] 4.5 Test `get_air_comfort`, `get_heating_system`, `get_zone_states`, and any other public method not covered by 3.1-3.2 or 4.1-4.4

## 5. Live Suite Relocation

- [x] 5.1 Create `tests/api/live/` and move `auth.py`, `utils.py`, and `test_api.py` there unchanged
- [x] 5.2 Mark the moved `TestApi` class (or its module) with `@pytest.mark.live`
- [x] 5.3 Fix imports/paths in the moved files to match the new `tests/api/live/` location

## 6. Pytest & CI Wiring

- [x] 6.1 Register the `live` marker in `pytest.ini` and set the default run to exclude it (e.g. `addopts = -m "not live"`)
- [x] 6.2 Verify `pytest -m live` still discovers the relocated suite structurally (it requires real credentials to actually pass)
- [x] 6.3 Re-enable `.github/workflows/test.yml` to trigger on `pull_request` and run the default (mocked-only) `pytest`

## 7. Findings

- [x] 7.1 Record every behavioral inconsistency discovered between the `_api_*_call` families (e.g. DELETE handling differing between `_api_call` and `_api_acme_call`) as a documented finding for a follow-up change, asserting current behavior as-is rather than fixing it here — see `findings.md`

# Tasks

## 1. Exception hierarchy

- [x] 1.1 Create `libtado/exceptions.py` with `TadoError`, `TadoAuthError`, `TadoHTTPError(TadoError, requests.exceptions.HTTPError)` (exposes `status_code` and `response`) and `TadoRateLimitError(TadoHTTPError)` (exposes `retry_after`), and re-export them from `libtado/api.py`; verify `from libtado.api import TadoError, TadoHTTPError, TadoRateLimitError, TadoAuthError` works.
- [x] 1.2 Add a response-to-exception helper (non-success `Response` -> `TadoHTTPError`, status 429 -> `TadoRateLimitError`) and verify with unit tests in a new `tests/api/test_exceptions.py` covering: catchable as `TadoError`, catchable as `requests.exceptions.HTTPError`, `status_code` / `response` populated, `isinstance(TadoRateLimitError, TadoHTTPError)`.

## 2. Single request pipeline and session

- [x] 2.1 Add `Tado._request(base_url, cmd, data=None, method='GET')` implementing token refresh, URL building, per-call auth headers, rate-limit bookkeeping (`_update_rate_limit_info`), error mapping via the helper from 1.2, and the uniform decoding rule (204 / empty body -> `None`, else JSON); keep today's "PUT/POST with falsy `data` sends nothing and returns `None`" behavior and log a warning for it.
- [x] 2.2 Reduce `_api_call`, `_api_acme_call`, `_api_minder_call`, `_api_energy_insights_call` and `_api_energy_bob_call` to thin wrappers over `_request`, deleting the duplicated `call_get/put/post/delete` closures; verify the full existing mocked suite (`make test`) still passes with only assertions on intentionally changed behavior touched.
- [x] 2.3 Route `refresh_auth()`, `login_device_flow()` and `check_device_activation()` HTTP calls through the same session and error-mapping helper (no 429 retry loop for them); verify `tests/api/test_tado_auth.py` still passes.
- [x] 2.4 Add a lazily-created per-instance `requests.Session` (`_get_session()`, stored on the instance, never on the class) used by `_request`; add tests proving: several calls share one session object, a client built with `Tado.__new__` (the `tado_unauthenticated` fixture) works with no `__init__`, and two `Tado` instances do not share a session.
- [x] 2.5 Add tests that fix the uniform behavior across hosts: rate-limit headers update `get_rate_limit_info()` for acme / minder / energy-insights / energy-bob calls, error responses on each secondary host raise `TadoHTTPError`, POST 204 and DELETE return `None`, and 200 JSON responses are returned unchanged.

## 3. 429 handling

- [x] 3.1 Add a pure wait-parsing function (the `t=` seconds of the `ratelimit` header first, falling back to `Retry-After` as integer seconds or HTTP-date, `None` when neither is usable or the value is garbage) and unit-test it for each of those inputs, including both headers present (`t=` wins).
- [x] 3.2 Add keyword-only constructor arguments `max_retries` (default 2) and `max_retry_wait` (default 30 seconds) to `Tado.__init__`, with class-level defaults so `Tado.__new__` instances behave identically; verify `max_retries=0` disables retrying.
- [x] 3.3 Implement the retry loop in `_request`: call `_update_rate_limit_info` on every response (including 429) before raising or retrying, so `get_rate_limit_info()` is never stale after a throttled call; then on 429 with a known wait `<= max_retry_wait` and retries left, log at WARNING on the `libtado` logger, `time.sleep(wait)` and resend; otherwise raise `TadoRateLimitError(retry_after=...)` without sleeping; never retry non-429 statuses or connection errors.
- [x] 3.4 Add tests (with `time.sleep` monkeypatched, `responses` sequences) for: 429 then 200 returns the result and slept the advertised time, wait taken from the `ratelimit` header `t=`, HTTP-date `Retry-After` fallback, `get_rate_limit_info()` reflecting a 429 response's headers, retries exhausted -> `TadoRateLimitError`, `Retry-After` of hours -> immediate error with `retry_after == 3600` and no sleep, 429 with no wait info -> immediate error, `max_retries=0`, a 500 sent exactly once, and a throttled PUT succeeding on retry with the body replayed.
- [x] 3.5 Update `docs/faq.md` (the 429 entry, which should also mention the documented 100 / 20,000 calls-per-day quotas) and the API usage docs with the retry behavior, the two new constructor options and the `TadoRateLimitError` handling pattern; verify `mkdocs build` (or `make docs`) renders without warnings.

## 4. Logging and auth errors

- [x] 4.1 Add `logger = logging.getLogger("libtado")` in `libtado/api.py`; replace the `print` calls in `login_device_flow()` and `check_device_activation()` with INFO log records (verification URL, expiry, completion) and drop the progress dots; verify `rtk proxy grep -n "print(" libtado/api.py` only matches docstring examples.
- [x] 4.2 Replace `raise Exception(...)` in `login_device_flow()`, `check_device_activation()` and `device_activation()` with `TadoAuthError` keeping the existing message texts, and replace the `sys.exit(1)` on `expired_token` with `raise TadoAuthError(...)`; drop the now-unused `sys` import.
- [x] 4.3 In `set_schedule_blocks()`, raise `ValueError` for a `schedule` outside 0/1/2 (before any request) and log inapplicable day types at WARNING instead of printing; in `set_schedule_block_by_day_type()`, replace the `print` with `warnings.warn(..., DeprecationWarning, stacklevel=2)`.
- [x] 4.4 Update tests: `tests/api/test_tado_auth.py` (`SystemExit` -> `TadoAuthError`, bare `Exception` matches -> `TadoAuthError`), `tests/api/test_tado.py::test_set_schedule_blocks_invalid_schedule` (`capsys` -> `pytest.raises(ValueError)` with no request sent); add tests using `caplog` for the verification-URL INFO record, the inapplicable-day-types WARNING, the retry WARNING, the `DeprecationWarning` (`pytest.warns`), and a `capsys` check that ordinary API calls and a retry write nothing to stdout.
- [x] 4.5 Document logging (`logging.getLogger("libtado")`, how to enable it), the exception hierarchy and the changed device-flow behavior (URL via `get_device_verification_url()` or INFO logs) in `docs/api/usage.md` and `docs/api/authentication.md`; verify the documented snippets run against the mocked client.

## 5. Command line client

- [x] 5.1 In `libtado/__main__.py`, when the client status is `PENDING` after construction, print the verification URL and the expiry time with `click.echo`, then call `device_activation()`; verify with a `CliRunner` test that the URL appears in the output when the flow is pending (HTTP mocked with `responses`).
- [x] 5.2 Convert `TadoError` and `requests.RequestException` raised during command execution into `click.ClickException` (one-line message, exit code 1), with the wait included for `TadoRateLimitError` when `retry_after` is known; verify with `CliRunner` tests for a rate-limited command and a 404, asserting a non-zero exit code and no traceback in the output (replaces the empty `TestCli` placeholder in `tests/cli/test_cli.py`).
- [x] 5.3 Update `docs/cli/usage.md` (or `docs/cli/configuration.md`) with the login prompt and error behavior; verify `make docs` builds cleanly.

## 6. Integration checks

- [x] 6.1 Run `make lint` and `make test` on Python 3.11 and 3.14 (`uv run --python`), and confirm zero `print(` / `sys.exit` / `raise Exception(` remain in `libtado/api.py` outside docstrings.
- [x] 6.2 With real credentials, run `make test-live` once and confirm no behavior regression (mind the daily quota: 100 calls for standard accounts, so do not loop it).
- [x] 6.3 Prepare the commit(s) with conventional-commit types so release-please reflects the breaking behavior change (`feat!:` or a `BREAKING CHANGE:` footer for the device-flow print / `SystemExit` removal); verify `.github/workflows/conventional-commit.yml` rules accept the message.

## Workflow follow-up

- Archive the change once implementation and review are done (`/opsx:archive`).
- Candidates left out on purpose, for a later change: token-file permissions (0600, atomic write), splitting `api.py` into a package, typed response models.

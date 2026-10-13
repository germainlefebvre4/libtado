# Design

## Context

See proposal.md - Why. Relevant current state in `libtado/api.py`:

- Five helpers (`_api_call` at l.442, `_api_acme_call`, `_api_minder_call`, `_api_energy_insights_call`, `_api_energy_bob_call`) each redefine `call_get/put/post/delete` and differ only by base URL and a few return-value quirks:
  - the main API unwraps `204 -> None` for DELETE/PUT but not POST;
  - the secondary hosts return the raw `Response` for DELETE (no endpoint uses it);
  - PUT/POST with a falsy `data` silently sends nothing and returns `None` (reached today only by `set_cost_simulation(payload=None)`).
- Secondary hosts are GET-only, except one POST (`set_cost_simulation`).
- Class-level attributes hold mutable client state (`access_headers`, `ratelimit_info`, `refresh_at`, ...). The test fixture `tado_unauthenticated` (`tests/api/conftest.py`) builds clients with `Tado.__new__(Tado)`, bypassing `__init__`: anything new must work with attributes that `__init__` never set.
- Tests mock HTTP with `responses`, which patches the `requests` adapter; a `requests.Session` is transparent to it. Existing tests assert `pytest.raises(requests.exceptions.HTTPError)` for all error paths, `pytest.raises(Exception, match="started already")`, `pytest.raises(SystemExit)` for the expired device code, and `capsys` for the invalid-schedule message.
- `RateLimitInfo` already parses `ratelimit` / `ratelimit-policy` (including `t=` seconds until reset). Tado's help article ("Limitation for REST API usage") documents only the `ratelimit` header, e.g. `"perday";r=0;t=123` = quota used up, refills in 123 s; it does not document `Retry-After` or the status code. Documented quota is 100 requests/day for standard accounts and 20,000/day with Auto-/AI-Assist (community reports suggest 20,000 for everyone: unconfirmed). The design therefore treats the `ratelimit` `t=` value as the primary wait source and `Retry-After` as a defensive fallback.
- Today `_update_rate_limit_info` runs only after `raise_for_status()`, so the headers of a 429 response are never recorded: `get_rate_limit_info()` is stale exactly when it matters.
- Python >= 3.11, runtime deps: `click`, `requests`, `python-dateutil`.

## Goals / Non-Goals

**Goals:**
- One request pipeline; adding retry, logging or error mapping happens in exactly one place.
- Library code never writes to stdout and never exits the process.
- Strict backward compatibility for `except requests.exceptions.HTTPError` and `except Exception`, and for every endpoint method's signature and return value.

**Non-Goals:**
- Splitting `api.py` into a package (candidate "F" in the exploration) and typed response models: this change leaves file layout alone beyond adding one small module.
- Async support, generic retry of 5xx / network errors, exponential backoff, or client-side throttling based on `remaining_calls`.
- Changing how authentication tokens are stored (token-file permissions is a separate, small change).

## Decisions

### D1. Single `_request()`, existing helpers become thin wrappers
`_request(base_url, cmd, data=None, method='GET')` implements: refresh auth, build URL, send via session with per-call headers, 429 handling, rate-limit bookkeeping, error mapping, response decoding. `_api_call`, `_api_acme_call`, `_api_minder_call`, `_api_energy_insights_call`, `_api_energy_bob_call` are kept as one-line wrappers passing their base URL. Rationale: the ~43 call sites and the existing test suite's per-host test classes stay untouched, so the diff is reviewable and behavior-preserving. Alternative: remove the wrappers and call `_request` directly everywhere, rejected as pure churn.

Unified decoding rule: HTTP 204 or an empty body returns `None`, otherwise `response.json()`. This differs from today only where no endpoint is affected (POST on 204, DELETE on secondary hosts). Falsy `data` on PUT/POST keeps today's "send nothing, return `None`" behavior, but now logs a warning (the silent no-op is a latent bug, flagged for a follow-up rather than changed here, to keep this change a refactor).

### D2. Lazily-created `requests.Session`, auth headers passed per call
A class-level `_http_session = None` plus a `_get_session()` method creates the session on first use. It works for `Tado.__new__` instances (no `__init__` dependency) and keeps construction free of extra I/O. `access_headers` is passed on each request rather than stored in `session.headers`, because it is replaced on every token refresh. The device-flow and token endpoints (`login.tado.com`) go through the same session but not through the 429 retry loop, and get the same error mapping. Alternative: build the session in `__init__`, rejected because it breaks the `__new__`-based fixture and any subclass that skips `super().__init__`.

### D3. 429 policy: honor the advertised wait, bounded, otherwise fail fast
On HTTP 429, the rate-limit headers of the response are first recorded (`_update_rate_limit_info`, before any raising), then `wait` = the `t=` reset seconds of the `ratelimit` header (the documented source), falling back to `Retry-After` (integer seconds or HTTP-date, standard HTTP but undocumented by Tado). If a wait is known, `wait <= max_retry_wait`, and retries remain (`max_retries`), the client logs at WARNING, sleeps, and resends; otherwise it raises `TadoRateLimitError` carrying `retry_after` (seconds or `None`). Defaults: `max_retries=2`, `max_retry_wait=30` seconds (worst case ~60 s blocked), configurable through new keyword-only constructor arguments; `max_retries=0` disables retrying. Rationale: Tado's quota is daily (100 or 20,000 calls), so a typical 429 means "come back in hours"; sleeping for that would hang the caller, whereas short waits are worth absorbing. Honest expectation: for most users the practical gain is the fast, typed `TadoRateLimitError` with the reset time (callers can schedule around it) rather than the retry itself, which only triggers on short waits. A 429 means the request was not processed, so replaying PUT/POST/DELETE is safe. Alternatives: exponential backoff with no server hint (rejected: guesses against a daily quota just burns calls that also count against the limit); making retry opt-in (rejected: bounded defaults are low-risk and the point is robustness out of the box). 5xx and network errors are deliberately not retried (see Non-Goals).

### D4. Exception hierarchy in `libtado/exceptions.py`, re-exported from `libtado.api`
```
Exception
 +-- TadoError
      +-- TadoAuthError                      (device-flow state / expiry; no HTTP response)
      +-- TadoHTTPError(TadoError, requests.exceptions.HTTPError)   .status_code, .response
           +-- TadoRateLimitError            .retry_after
```
`TadoHTTPError` multiply inherits so every existing `except requests.exceptions.HTTPError` keeps working and `response` / `request` are populated the same way `raise_for_status()` does. A single helper maps a failed `Response` to `TadoHTTPError` (or `TadoRateLimitError` for 429); it replaces every `raise_for_status()` in the pipeline and in the auth calls. A separate module avoids bloating the already 3.4k-line `api.py` and allows `from libtado.exceptions import ...`; `libtado.api` re-exports the names so `from libtado.api import TadoError` also works. Alternative: `TadoAuthError` also covering HTTP 401/403, rejected for now: it would need a second multiple-inheritance class and 401 can come from any host; `status_code` on `TadoHTTPError` already lets callers branch.

`login_device_flow()` ("started already"), `device_activation()` ("not yet started"), `check_device_activation()` (URL deadline exceeded, `expired_token`) raise `TadoAuthError` with the existing message texts, so `match="started already"` style assertions keep passing; only the `SystemExit` expectation changes.

### D5. Logging instead of `print`, CLI owns user interaction
The library uses `logger = logging.getLogger("libtado")` and no handler (library best practice: silent unless the host configures logging). Mapping: verification URL and expiry, login completion: INFO; 429 wait/retry: WARNING; inapplicable schedule day types: WARNING; polling dots are dropped. `set_schedule_blocks` with an invalid `schedule` raises `ValueError`; `set_schedule_block_by_day_type` uses `warnings.warn(..., DeprecationWarning, stacklevel=2)`. The CLI (`libtado/__main__.py`) prints the verification URL and a "waiting for login until ..." line with `click.echo` after construction when the status is `PENDING`, then calls `device_activation()`, and wraps command execution so `TadoError` / `requests.RequestException` become `click.ClickException` (one line, exit code 1; a `TadoRateLimitError` message includes the wait when known). Alternative: keep printing the URL in the library at INFO via a default handler, rejected: a library installing a handler is the very problem being fixed. The README already shows `get_device_verification_url()` for scripts.

### D6. Testing approach
Retry tests monkeypatch `time.sleep` (no real waiting) and use `responses` sequences (429 then 200). Wait-parsing is a small pure function tested directly (seconds, HTTP-date, missing, garbage). The fixture-created (`__new__`) client covers lazy session creation. Existing assertions are adapted only where behavior intentionally changed (`SystemExit` -> `TadoAuthError`, `capsys` -> `ValueError`).

## Risks / Trade-offs

- [Callers relying on `print`ed login URL or on `SystemExit`] -> Called out as **BREAKING** in the proposal; documented in docs and CHANGELOG via the release-please commit (`feat!` / `BREAKING CHANGE:` footer), README example already uses `get_device_verification_url()`.
- [The exact 429 header set is only partly documented] -> Both `ratelimit` `t=` and `Retry-After` are accepted; with neither, the call fails fast exactly as before (with a better exception), so the worst case is no improvement, not a regression.
- [Blocking a synchronous caller up to ~60 s by default] -> Small bounded defaults, `max_retries=0` opt-out, documented in the FAQ.
- [Replaying a throttled non-idempotent request] -> A 429 is returned before the request is processed, so it cannot double-apply; documented as the reason retries are limited to 429.
- [Behavior difference on the 204/POST and secondary-host DELETE paths] -> No existing endpoint reaches those paths; covered by unit tests that fix the new uniform rule.
- [Lazily created class-level session shared state] -> Stored on the instance (`self._http_session = ...`), never on the class, so instances do not share connections or cookies.

## Migration Plan

1. Land the refactor (D1, D2) first with all existing tests green and no intended behavior change.
2. Add exceptions + error mapping (D4), then retry (D3), then logging / CLI changes (D5), each as its own commit so a regression can be bisected.
3. Update docs and tests; release as a minor-or-major bump decided by release-please from the commit types (the print / `SystemExit` removal is a breaking change).
4. Rollback: revert the commits; nothing persisted (token file format, schemas, CI) is touched.

## Resolved Questions

- **Which header carries the 429 wait?** Resolved from Tado's help article: `ratelimit` with `t=` is the documented one; `Retry-After` is not. Design and tasks use `t=` first and `Retry-After` as fallback. Whether Tado also sends `Retry-After` stays unknown and does not matter for correctness.
- **Expose `max_retries` / `max_retry_wait` as CLI options or env vars?** No, out of scope. The CLI uses library defaults; with a daily quota most 429s fail fast anyway, so the options would add surface without changing outcomes. Revisit only if users ask; adding them later touches neither the specs nor the library API.

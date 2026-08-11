## Context

See proposal.md - Why. Two additional facts shape the approach:

- `Tado.__init__` (`libtado/api.py`) itself is not side-effect-free: if no valid cached refresh token is supplied or found via `load_token()`, it unconditionally calls `login_device_flow()`, which POSTs to `login.tado.com/oauth2/device_authorize` and prints a login URL. So it is not enough to defer only the `device_activation()` call in `auth.py` - the `Tado(...)` construction itself must be deferred too.
- `tests/api/live/utils.py` is dead code: it defines a `TestApi` class (methods without `self`) that duplicates the name of the real test class in `test_api.py`, and nothing in the repo calls any of its methods. Its only live effect is `from tests.api.live.auth import tado`, which re-triggers the same import-time side effect. It can be deleted outright rather than migrated.
- `.github/workflows/template_test.yml` never sets `TADO_REFRESH_TOKEN` / `TADO_CREDENTIALS_FILE` as job env vars even though `test.yml` does `secrets: inherit` - so today, running `-m live` in CI would have no credentials available regardless of this fix. Wiring CI secrets for the live suite is out of scope here (this proposal only makes the default, non-live run safe and makes a credential-less live run fail fast instead of hanging).

## Goals / Non-Goals

**Goals:**
- Default `pytest` run never imports code that talks to the network or the real Tado account, regardless of the `live` marker filter.
- Running `pytest -m live` without credentials fails fast and clearly (`pytest.skip`) instead of blocking for ~5 minutes and crashing the whole session with an `INTERNALERROR`.
- Running `pytest -m live` with valid credentials keeps working exactly as before (cached token fast-path, or OAuth device flow when no valid token exists).

**Non-Goals:**
- Wiring real Tado credentials into CI (`scheduled.yml` / `template_test.yml`) for the live suite - out of scope, tracked as a separate concern.
- Changing anything about `Tado.__init__`, `login_device_flow`, or `device_activation` in `libtado/api.py` itself - the bug is in test wiring, not library behavior.
- Adding coverage for the `utils.py` helpers - they are unused and being deleted, not preserved.

## Decisions

- **Fixture over collection-ignore hooks**: fix this by moving the client construction and activation into a `scope="session"` pytest fixture in a new `tests/api/live/conftest.py`, rather than adding a `pytest_ignore_collect` hook to skip the `live/` directory during default collection.
  - Why: the fixture is the more direct fix - pytest already defers fixture evaluation to point-of-use, so a test deselected by `-m "not live"` never triggers it, with no custom collection hook to maintain. A `pytest_ignore_collect` hook would be a second, independent safety net solving the same problem differently; it was considered and rejected as unnecessary duplication once the module-level side effect is gone. If a future test file reintroduces an import-time side effect, that is a code-review concern the fixture pattern already establishes as the norm for this directory.
- **`session` scope, not `function`**: matches the current implicit behavior (one `tado` module-level singleton shared across every test in `TestApi`). Function-scoped would rebuild/reauthenticate per test, which is unnecessary and would multiply real API calls against the live account.
- **Skip immediately when no credentials, rather than preserving the blocking OAuth flow**: the fixture checks for `TADO_REFRESH_TOKEN` or a usable `TADO_CREDENTIALS_FILE` *before* constructing `Tado(...)`, and calls `pytest.skip("no Tado live credentials configured")` if neither is present. Considered keeping today's blocking device-flow-then-timeout behavior (only reachable now behind `-m live`, no longer a default-run risk) - rejected because a contributor who runs `-m live` by mistake, or a CI job with `secrets: inherit` but no env wiring (see Context), would still hang for minutes for no benefit; a skip is unambiguous and immediate.
- **Delete `auth.py` and `utils.py` instead of refactoring in place**: `auth.py`'s logic moves into the `conftest.py` fixture, so the file becomes empty; `utils.py` has no callers, so migrating its methods to accept an injected `tado` fixture parameter would preserve dead code for no reason. Both are deleted.

## Risks / Trade-offs

- [The credential-presence check in the fixture must exactly mirror `Tado.load_token()`'s notion of "usable" (file exists, valid JSON, contains a non-empty `refresh_token`), or the fixture could skip when a real run would have succeeded, or vice versa attempt construction when it shouldn't] → Mitigation: implement the check as "env var set, or credentials file exists and parses with a non-empty `refresh_token` key" and add a small unit test for the fixture's skip/no-skip decision itself if practical, or keep the check deliberately conservative (skip unless clearly usable).
- [Session-scoped fixture means a stale/expired cached token discovered mid-run only fails once per session, same as today's module-level singleton] → Mitigation: none needed, this matches current behavior and is not a regression.

## Migration Plan

1. Add `tests/api/live/conftest.py` with the `tado` session fixture (credential check → skip, or construct + activate-if-pending).
2. Update `tests/api/live/test_api.py`: remove `from tests.api.live.auth import tado` and `from tests.api.live import utils`; add `tado` as a parameter on every `TestApi` test method that currently uses the module-level `tado`.
3. Delete `tests/api/live/auth.py` and `tests/api/live/utils.py`.
4. Verify locally: `uv run pytest` (default) collects and runs cleanly with zero network calls; `uv run pytest -m live` with no credentials set skips every live test immediately; if a cached token/`TADO_REFRESH_TOKEN` is available locally, `uv run pytest -m live` still exercises the real API as before.
5. No rollback concerns beyond a normal revert - no data migration, no deployed state.

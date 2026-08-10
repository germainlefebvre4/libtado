## Context

See proposal.md - Why/What Changes. Two constraints shape this design:

- `Tado.__init__` performs a network call unconditionally (`load_token()` + `refresh_auth(force_refresh=True)`, or `login_device_flow()`), so no `Tado` instance can exist in a test without either mocking that path or bypassing `__init__` entirely.
- The HTTP layer is not one code path but five near-duplicate families (`_api_call`, `_api_acme_call`, `_api_minder_call`, `_api_energy_insights_call`, `_api_energy_bob_call`), each with its own `call_get`/`call_put`/`call_post`/`call_delete` closures, and they are not behaviorally identical (e.g. DELETE handling differs between `_api_call` and `_api_acme_call`).

## Goals / Non-Goals

**Goals:**
- Make `Tado` constructible in tests with zero real network I/O.
- Cover the OAuth/token lifecycle and all public `Tado` methods with `responses`-mocked HTTP, across all five call families.
- Keep the existing live tests intact and runnable, but out of the default `pytest` run.
- Re-enable CI on the new mocked suite without requiring secrets.

**Non-Goals:**
- Fixing behavioral inconsistencies uncovered between the five `_api_*_call` families (e.g. DELETE handling) - per the confirmed decision, tests assert *current* behavior and any inconsistency found is documented as a finding for a separate change, not fixed here.
- Refactoring the five duplicated `_api_*_call` families into a shared implementation.
- Wiring `scheduled.yml` secrets back up to run the live suite in CI.
- Adding test coverage for `libtado/__main__.py` or `libtado/cli_utils.py` (separate future change).

## Decisions

**1. Two distinct fixture strategies, not one.**
- For the ~55 `get_*`/`set_*`/`delete_*` method tests: bypass `__init__` via `Tado.__new__(Tado)` plus manually setting the minimal instance state needed (`access_headers`, `refresh_at` set far in the future so `refresh_auth()` is a no-op, and any other attribute a method depends on). Centralized in a single `conftest.py` fixture.
- For the OAuth/token lifecycle tests (`refresh_auth`, `login_device_flow`, `check_device_activation`, `device_activation`, `set_oauth_token`, `load_token`/`save_token`): construct through the real `Tado(...)` constructor, with `responses` mocking `login.tado.com/oauth2/token` and `login.tado.com/oauth2/device_authorize`.
  - *Alternative considered*: mock the OAuth call for every one of the ~55 method tests and always go through the real constructor. Rejected as the default - it triples per-test setup for no added signal, since the auth path already gets dedicated coverage under strategy 2.

**2. Mocking library: `responses`** (new `test` dependency group entry in `pyproject.toml`), per the earlier explore-mode decision. Declarative route registration scales better than `unittest.mock.patch` across ~55 methods x success/error variants, and it asserts against the real `requests` call surface (URL, headers, JSON body) rather than a hand-built mock.

**3. Test file layout:**
```
tests/api/
├── conftest.py           # tado_unauthenticated fixture (bypass __init__)
├── test_tado_auth.py     # NEW - OAuth/token lifecycle, real __init__ + responses
├── test_tado.py          # NEW - one test group per public method, keyed to
│                          #   the _api_*_call family it exercises
├── test_ratelimitinfo.py # unchanged
└── live/
    ├── auth.py            # moved as-is
    ├── utils.py            # moved as-is
    └── test_api.py         # moved, marked @pytest.mark.live
```
`test_tado.py` is organized by `_api_*_call` family (not just method name), so that each family's success/204/4xx/5xx behavior is exercised at least once, and each individual public method additionally gets its own URL/payload construction test.

**4. Default test run excludes `live`.** Register `live` as a marker in `pytest.ini` and set `addopts = -m "not live"` (or equivalent) so plain `pytest` only runs the mocked suite. The live suite still runs explicitly via `pytest -m live` when real credentials are available.

**5. CI: re-enable `.github/workflows/test.yml`** to trigger on `pull_request` and run the default (mocked-only) `pytest` - no secrets needed. `scheduled.yml` stays disabled; re-wiring it to run the relocated live suite is explicitly out of scope (proposal.md - Impact).

**6. Findings, not fixes.** Any behavioral inconsistency the new tests surface between the five `_api_*_call` families gets asserted as-is (characterization test) and listed as a finding in tasks.md, not corrected in this change.

## Risks / Trade-offs

- [Risk] Bypassing `__init__` couples tests to `Tado`'s internal attribute names (`access_headers`, `refresh_at`, ...) - a rename breaks the fixture even with no behavior change. → Mitigation: centralize the bypass in exactly one `conftest.py` fixture so a rename is a one-line fix.
- [Risk] Asserting current, possibly-buggy behavior (per Decision 6) risks encoding a bug as a "spec" that later looks intentional. → Mitigation: every characterization test for a known inconsistency gets a comment pointing at the tasks.md finding, and the finding itself stays visible until a follow-up change addresses it.
- [Risk] Large upfront scope (~55 methods) risks a stalled, half-migrated state if work is interrupted. → Mitigation: tasks.md sequences work so each `_api_*_call` family is independently completable and mergeable on its own.
- [Risk] New dependency (`responses`) adds a maintenance surface. → Mitigation: test-only (dev dependency group), not shipped in the published package.

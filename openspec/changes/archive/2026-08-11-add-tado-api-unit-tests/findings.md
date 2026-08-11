## Findings

Behavioral inconsistencies discovered while writing characterization tests for the five
`_api_*_call` families in `libtado/api.py`. Per design.md Decision 6, these are asserted
as-is (current behavior) in the test suite, not fixed here. Listed as input for a follow-up
change.

### 1. `DELETE` response handling differs between families

- `_api_call`'s `DELETE` branch returns `None` on a `204` response, or `res.json()` otherwise.
- `_api_acme_call`, `_api_minder_call`, `_api_energy_insights_call`, and `_api_energy_bob_call`
  all implement `DELETE` as `return call_delete(url)`, i.e. they return the raw
  `requests.Response` object unconditionally - no `204` handling, no JSON parsing.

No public method currently issues a `DELETE` through the four non-`_api_call` families, so this
is only observable by inspection today, not through any existing public method's return value.

### 2. `POST` is only supported by two of the five families

- `_api_call` and `_api_energy_insights_call` implement a `method == 'POST'` branch.
- `_api_acme_call`, `_api_minder_call`, and `_api_energy_bob_call` have no `POST` handling at
  all. Calling any of them with `method='POST'` silently falls through every `if`/`elif` branch
  and returns `None` - no exception, no request made.

### 3. Falsy payloads silently skip `PUT`/`POST` requests in every family

Every family guards its `PUT` (and, where present, `POST`) branch with `and data:`
(e.g. `elif method == 'PUT' and data:`). Passing an empty/falsy payload (`{}`, `[]`, `None`,
`False`) with `method='PUT'` or `method='POST'` matches no branch, so the call silently returns
`None` without making any HTTP request and without raising - this is easy to trigger
accidentally (e.g. `set_cost_simulation(..., payload={})`).

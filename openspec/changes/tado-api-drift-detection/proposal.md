## Why

`generate_json_schemas.py` is a manual, one-shot script: it overwrites `schemas/*.json` from a single live sample, nothing validates responses against those schemas (`tests/api/test_jsonschema.py` is fully commented out and `jsonschema` isn't even a declared dependency), and the only CI workflow that touches it (`check_json_schemas.yml`) is `workflow_dispatch`-only, so nobody runs it. `test.yml` and `scheduled.yml` are also fully commented out, apparently because they require live Tado credentials that GitHub Actions withholds from fork PRs. As a result, there is currently no mechanism that detects when the real Tado API changes shape, and no PR-time safety net that doesn't depend on live credentials.

## What Changes

- Replace `generate_json_schemas.py` with a "discover" mechanism that calls the live Tado API for all `get_*` endpoints, builds a **cumulative** JSON Schema per endpoint (union of every field ever observed, via `genson`'s `add_schema` + `add_object`, instead of overwriting from a single sample), and records the live request/response as a replayable cassette.
- Anonymize every cassette before it touches disk: real values (geolocation, device serials, installation/home IDs, names, emails) are substituted with **deterministic** Faker-generated fakes (seeded per field path) so no personal data is ever written to a versioned file, and re-running discovery against unchanged real data does not produce spurious diffs.
- Reactivate PR-time tests (`test.yml`) to run against the committed cassettes instead of the live API, so they need no live credentials and can safely run on fork PRs.
- Add a scheduled CI job (weekly) that runs discovery against `get_*` endpoints only, compares the result to what's committed, and opens an automated PR with the updated schemas/cassettes when a drift is detected. `set_*` (mutating) endpoints are only exercised via manual `workflow_dispatch`, never on the unattended schedule, since they write to the real Tado account.
- **BREAKING** (internal tooling only, no library API impact): `generate_json_schemas.py` is deleted; `schemas/*.json` changes from single-sample to cumulative/union schemas, which may be structurally different (e.g., previously-required fields becoming optional).
- Add a `Makefile` with local-dev-only convenience targets (discover, check-drift, test, test-live, lint) — not referenced by CI, which invokes the underlying commands directly.

## Capabilities

### New Capabilities
- `api-contract-discovery`: capturing live Tado API responses into cumulative, anonymized schemas and cassettes, with mutating endpoints excluded from unattended runs.
- `api-drift-automation`: CI triggers (scheduled + manual) that run discovery, detect drift, and open an automated PR; PR-time tests that validate against committed cassettes without live credentials.

### Modified Capabilities
_(none — no existing spec files in `openspec/specs/`)_

## Impact

- Removed: `generate_json_schemas.py`.
- Changed: `schemas/*.json` (regenerated as cumulative schemas), `tests/api/test_jsonschema.py` (reactivated against cassettes), `tests/api/utils.py` (mutating calls separated from read-only discovery), `.github/workflows/check_json_schemas.yml`, `.github/workflows/test.yml`, `.github/workflows/scheduled.yml`, `.github/workflows/template_test.yml`.
- Added: cassette fixtures directory, scrubbing/anonymization utility, `Makefile`.
- New dependencies (dev/test only): `jsonschema`, a cassette library (e.g. `vcrpy`), `Faker`.
- No change to the public library API in `libtado/api.py`.

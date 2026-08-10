## 1. Dependencies

- [ ] 1.1 Add `jsonschema`, `vcrpy`, and `Faker` to the `test`/`generate` dependency groups in `pyproject.toml` as appropriate, and update `uv.lock`.

## 2. Anonymization utility

- [ ] 2.1 Define the explicit list of sensitive field paths per endpoint (geolocation, device/installation serials and IDs, names, emails, addresses) by reviewing every schema currently in `schemas/`.
- [ ] 2.2 Implement a scrubbing function that, given a field path and value, returns a `Faker`-generated fake seeded deterministically from the field path (never from the real value).
- [ ] 2.3 Implement a generic type-based fallback scrub for any field not in the explicit list, so no unclassified field is ever passed through raw.
- [ ] 2.4 Add unit tests proving determinism (same field path -> same fake across runs) and proving no raw sensitive value survives scrubbing on sample fixtures.

## 3. Discover script

- [ ] 3.1 Remove `generate_json_schemas.py`.
- [ ] 3.2 Implement a discover script that iterates read-only (`get_*`) endpoint wrappers by default, with an explicit opt-in flag/argument to also include mutating (`set_*`) wrappers.
- [ ] 3.3 For each endpoint call, capture the live request/response with `vcrpy`, scrub the response via the anonymization utility from section 2, and write the resulting cassette.
- [ ] 3.4 For each endpoint call, load the existing committed schema (if present), merge it with the newly captured (scrubbed) response via `genson` (`add_schema` + `add_object`), and write the updated cumulative schema to `schemas/`.
- [ ] 3.5 Separate `tests/api/utils.py` endpoint wrappers into read-only vs. mutating groups so the discover script can select the correct subset.

## 4. Cassette-based PR tests

- [ ] 4.1 Uncomment and adapt `tests/api/test_jsonschema.py` to validate each committed cassette's response against its corresponding `schemas/*.json` file using `jsonschema.validate`.
- [ ] 4.2 Configure `vcrpy` in strict replay mode (`record_mode="none"`) for the PR-time test run, so tests fail loudly if a request doesn't match any committed cassette instead of silently hitting the network.
- [ ] 4.3 Run the initial discover pass (manually, with real credentials, read-only endpoints) to populate the first generation of cumulative schemas and cassettes, and commit them.

## 5. CI workflows

- [ ] 5.1 Rewrite `.github/workflows/test.yml` to run the cassette-based tests on `pull_request`, without live Tado secrets.
- [ ] 5.2 Delete `.github/workflows/check_json_schemas.yml`.
- [ ] 5.3 Add a new discovery workflow with two triggers: `schedule` (weekly, read-only endpoints only) and `workflow_dispatch` (manual, with an opt-in input to include mutating endpoints).
- [ ] 5.4 In the discovery workflow, after running the discover script, detect whether `schemas/` or the cassette directory changed; if so, open a pull request with those changes (e.g. via `peter-evans/create-pull-request`), without auto-merging.
- [ ] 5.5 Re-enable `.github/workflows/scheduled.yml` pointing at the new discovery workflow (not `template_test.yml`).
- [ ] 5.6 Update `.github/workflows/template_test.yml` if still needed for anything beyond what `test.yml`/discovery now cover; remove it if it becomes unused.

## 6. Local developer convenience

- [ ] 6.1 Add a `Makefile` with targets: `discover` (run discovery against the live account, read-only), `discover-all` (include mutating endpoints), `check-drift` (run discovery to a temp location and diff against committed artifacts without writing them), `test` (cassette-based tests), `test-live` (tests against the live API), `lint`.
- [ ] 6.2 Document the new workflow (discover/check-drift/test targets, how anonymization works, how automated drift PRs are handled) in `docs/contributing.md`.

## 7. Verification

- [ ] 7.1 Confirm a full `make test` run passes offline (no network access) using only committed cassettes.
- [ ] 7.2 Confirm none of the committed cassette or schema files contain real personal data (manual review pass against the sensitive-field list from 2.1).
- [ ] 7.3 Confirm re-running `make discover` twice against the same live account produces zero diff.

## Why

Verifying the uv migration (`migrate-to-uv`, task 3.5/7.3) on `chore/migrate-to-uv` triggered `release-feat-dryrun.yml`. The run failed: `semantic-release` correctly determined there was nothing to release (`new_release_version=""`, `new_release_published=false`), but the `Update package version` step ran anyway (no `if` guard), computed `bump_version=".dev122"`, and `uv version .dev122` crashed with "expected version to start with a number". This is a pre-existing bug in `release-feat-dryrun.yml` — unlike `release-master.yml`, whose `deploy` job guards every step with `if: needs.release.outputs.new_release_published == 'true'`, `release-feat-dryrun.yml` only guards the final `Build and publish` step. It was never triggered before because prior test pushes always contained a releasable `feat:`/`fix:` commit.

Separately, the branch trigger was temporarily narrowed from `chore/*` to `chore/migrate-to-uv` to force this verification run. That needs to be reverted, but only once the guard fix lands — otherwise every `chore/*` push pays for a full `deploy` job attempt (and crashes) instead of exiting cheaply after the `release` job's dry-run analysis.

## What Changes

- In `.github/workflows/release-feat-dryrun.yml`, add `if: needs.release.outputs.new_release_published == 'true'` to the `Install uv` and `Update package version` steps of the `deploy` job, mirroring `release-master.yml`.
- Revert the `deploy` job's branch trigger from `chore/migrate-to-uv` back to `chore/*`.

## Capabilities

No spec-level behavior of the library changes — this is a CI workflow fix. `skip_specs: true` is set in `.openspec.yaml`.

## Impact

- `.github/workflows/release-feat-dryrun.yml` only.
- No change to package code, `pyproject.toml`, or published artifacts.
- Reduces wasted CI minutes on `chore/*` pushes that don't produce a release.

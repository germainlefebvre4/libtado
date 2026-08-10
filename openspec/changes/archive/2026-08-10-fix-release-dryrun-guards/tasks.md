## 1. Guard the deploy job steps

- [x] 1.1 In `.github/workflows/release-feat-dryrun.yml`, add `if: needs.release.outputs.new_release_published == 'true'` to the `Install uv` step of the `deploy` job.
- [x] 1.2 In the same file, add `if: needs.release.outputs.new_release_published == 'true'` to the `Update package version` step of the `deploy` job.

## 2. Restore the branch trigger

- [x] 2.1 In `.github/workflows/release-feat-dryrun.yml`, revert the `deploy`-triggering `on.push.branches` entry from `chore/migrate-to-uv` back to `chore/*`.

## 3. Verify

- [x] 3.1 Push a `chore/*` branch with only non-releasable commits (e.g. `chore:`/`ci:`) and confirm the `deploy` job's `Install uv` and `Update package version` steps are skipped (job succeeds without reaching `uv version`).
- [x] 3.2 Confirm `release-master.yml` is unaffected (not touched by this change).

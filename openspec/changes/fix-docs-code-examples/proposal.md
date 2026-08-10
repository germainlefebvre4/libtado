## Why

The library's own onboarding example is broken in three different ways across three files. `libtado/api.py`'s module docstring shows a constructor signature (`tado.api('Username', 'Password', 'ClientSecret')`) that was removed when the OAuth2 device-code flow replaced username/password auth. `docs/getting-started/usage.md` and `docs/api/usage.md` both copy a variant of that stale pattern (`import libtado.api; t = tado.api(token_file_path=...)`) that never worked — `tado` is never imported and `libtado.api` has no callable `api()`. Only `README.md` has the correct, current pattern (`from libtado.api import Tado; t = Tado(token_file_path=...)`). A new user following the docs' own "Getting started" page hits a `NameError` on the first example. `getting-started/usage.md` also contains a leftover Sphinx/RST cross-reference (`` `all available API methods <api>` ``) that renders as plain text, not a link, under mkdocs.

Alongside this, a few small doc-quality issues are cheap to fix in the same pass: `docs/getting-started/references.md` adds no content beyond what the mkdocs nav sidebar already shows, and there are a couple of typos in `docs/contributing.md` and `docs/getting-started/references.md`.

## What Changes

- Fix `libtado/api.py`'s module docstring example to use the current `Tado` constructor (`from libtado.api import Tado`, `saved_refresh_token`/`token_file_path`), matching the real `__init__` signature.
- Fix the broken example in `docs/getting-started/usage.md` to use the same corrected pattern, and replace the leftover Sphinx-style cross-reference with a working markdown link to the API usage page.
- Fix the broken example in `docs/api/usage.md` to use the same corrected pattern.
- Remove `docs/getting-started/references.md` (pure duplicate of the mkdocs nav) and drop its nav entry from `mkdocs.yml`.
- Fix typos: "librairy" (currently in `references.md`; relocate the fix or drop with the file removal) and "developement"/"strenghtness" in `docs/contributing.md`.

No behavior of the library changes — this is documentation and docstring text only.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None — no spec-level behavior changes. `skip_specs: true` is set in this change's `.openspec.yaml`.

## Impact

- **Affected files**: `libtado/api.py` (module docstring only), `docs/getting-started/usage.md`, `docs/api/usage.md`, `docs/getting-started/references.md` (removed), `docs/contributing.md`, `mkdocs.yml` (nav entry removal).
- **Dependencies**: none.
- **Out of scope**: filling in the ~31 missing docstrings on `Tado`'s public methods (including `__init__` and the OAuth device-flow methods) — tracked as a follow-up iteration, not part of this change.

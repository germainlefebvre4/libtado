## 1. Fix the broken constructor example

- [ ] 1.1 Update the module docstring example in `libtado/api.py` (top of file) to use `from libtado.api import Tado` and call `Tado(token_file_path=...)` (or `saved_refresh_token=...`), matching the real `Tado.__init__` signature — drop the removed `Username`/`Password`/`ClientSecret` args.
- [ ] 1.2 Update the example in `docs/getting-started/usage.md` to the same corrected pattern (`from libtado.api import Tado`, `t = Tado(token_file_path=...)`).
- [ ] 1.3 Replace the leftover Sphinx-style cross-reference in `docs/getting-started/usage.md` (`` `all available API methods <api>` ``) with a working markdown link to `../api/usage.md`.
- [ ] 1.4 Update the example in `docs/api/usage.md` to the same corrected pattern (`from libtado.api import Tado`, `api = Tado(token_file_path=...)`).

## 2. Remove the redundant references page

- [ ] 2.1 Delete `docs/getting-started/references.md`.
- [ ] 2.2 Remove its `References: getting-started/references.md` entry from the `"Getting started"` section of `mkdocs.yml`'s `nav`.
- [ ] 2.3 Check for and fix any remaining links to `getting-started/references.md` elsewhere in `docs/` (e.g. `index.md`), pointing them at the CLI/API usage pages directly if needed.

## 3. Fix typos

- [ ] 3.1 Fix "developement" → "development" and "strenghtness" → "strength" in `docs/contributing.md`.

## 4. Verify

- [ ] 4.1 Run `uv run mkdocs build --strict` (or `uv run mkdocs serve` and manually check) to confirm no broken nav references remain after removing `references.md`.
- [ ] 4.2 Manually copy-paste the corrected examples from `docs/getting-started/usage.md`, `docs/api/usage.md`, and the `libtado/api.py` docstring into a Python shell/script to confirm they run without `NameError` (up to the point of needing real Tado credentials).

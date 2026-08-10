## Context

See `proposal.md` - Why. Current state relevant to the approach:

- `mkdocs.yml`'s mkdocstrings config sets `show_if_no_docstring: false` and has no `merge_init_into_class` option (defaults to `false`), so `__init__` is treated like any other method for rendering purposes.
- `docs/api/reference.md` is a single `::: libtado.api.Tado` block with no `members:`/`filters:` option, so it currently renders every documented public method in declaration order.
- Existing docstrings follow a house style, not strict pydocstyle: Google-ish `Parameters:`/`Returns:` sections, 2-space indentation (matches the file's indentation, not PEP 8's 4), and `??? info "Result example"` mkdocs-material admonitions with JSON payloads for methods that hit the API.
- `.github/workflows/lint.yml` already runs `chartboost/ruff-action@v1` with no project-level `[tool.ruff]` config in `pyproject.toml` (ruff runs on its own defaults, no `D` rules selected).

## Goals / Non-Goals

**Goals:**
- Give every currently-undocumented public `Tado` method a docstring in the existing house style.
- Make `docs/api/reference.md` show only the functional (home/zone/schedule/energy) surface, with the auth/device-flow and rate-limit-infra methods rendered on a separate page instead.
- Add a non-blocking signal for future missing docstrings, reusing the existing ruff setup.

**Non-Goals:**
- No change to `libtado/api.py`'s class structure (no splitting `Tado` into multiple classes/mixins). The technical/functional split is a documentation-rendering concern only.
- No full pydocstyle-convention enforcement (formatting, imperative mood, punctuation) - only presence.
- No change to any runtime behavior, including the deprecated `set_schedule_block_by_day_type`.

## Decisions

**1. Split via mkdocstrings `members:`, not a code refactor.**
Two `::: libtado.api.Tado` blocks (one per page), each scoped with an explicit `members:` list. mkdocstrings' `members` option, when set, renders exactly the listed names regardless of the default `!^_`-style filters - so the private `_api_*_call` / `_update_rate_limit_info` / `_parse_header` helpers stay invisible on both pages without extra filter config, and `__init__` can be listed explicitly even though dunder methods are normally hidden by default filters.
*Alternative considered*: extract auth/device-flow logic into a separate `TadoAuth` class or mixin. Rejected - this change is declared `skip_specs: true` (no behavior change); a class split is a code-architecture change that belongs in its own proposal with its own risk/test surface, not bundled into a docstring-completeness pass.

**2. New page `docs/api/authentication.md` for technical/plumbing methods.**
Holds: `__init__`, `login_device_flow`, `check_device_activation`, `device_activation`, `device_ready`, `refresh_auth`, `save_token`, `load_token`, `set_oauth_token`, `get_device_activation_status`, `get_device_verification_url`, and `get_rate_limit_info` (12 methods - the 11 auth/device-flow methods plus rate-limit introspection, since it's an infrastructure concern rather than home-automation functionality, not "control your thermostat"). Linked from the mkdocs nav under API, and cross-referenced with a one-line pointer from `docs/getting-started/usage.md`'s existing token/auth section.
*Alternative considered*: fold this content into `docs/getting-started/usage.md`. Rejected - that page is narrative onboarding prose; these methods need the same mkdocstrings-rendered signature/parameter treatment as the functional reference, which a `:::` block gives for free.

**3. `docs/api/reference.md`'s `members:` list becomes the remaining ~53 functional methods** (everything on `Tado` except the 12 above and the 6 private `_`-prefixed helpers, which stay unlisted/hidden on both pages).

**4. Docstring content for auth/device-flow methods is flow-oriented, not JSON-example-oriented.**
Most of these methods return `bool`/`None`/plain strings, not API JSON payloads, so `??? info "Result example"` blocks don't apply. Each docstring instead states: when it's called (e.g. during `__init__`, or polled by `device_activation`), what it mutates on `self` (`refresh_token`, `device_code`, `access_headers`, `device_activation_status`, ...), and what calling it out of order does (e.g. `login_device_flow` raises if activation already started). `set_schedule_block_by_day_type` gets a one-line deprecation notice pointing to `set_schedule_blocks()`, matching how deprecation is already communicated at runtime (it prints a message before delegating).

**5. Ruff `D1xx` (docstring-presence only), not the full `google` convention, added as a non-blocking CI step.**
Add `[tool.ruff.lint] select = [... existing defaults ..., "D100", "D101", "D102", "D103", "D104", "D105", "D106", "D107"]` (module/class/method/function/package/magic-method/nested-class/`__init__` presence checks) without setting `[tool.ruff.lint.pydocstyle] convention`. In `.github/workflows/lint.yml`, add this as its own step (or job) with `continue-on-error: true`.
*Alternative considered*: select the full `D` rule set or set `convention = "google"`. Rejected - the existing docstrings' house style (2-space indent, custom `Parameters:`/`Returns:` headers, embedded JSON admonitions) doesn't conform to pydocstyle's stricter formatting/convention rules, so enabling those would immediately report on ~100+ pre-existing, intentionally-styled docstrings - noise that defeats the "coverage signal" purpose and that "check but don't block" was meant to avoid, not paper over.
*Alternative considered*: `interrogate`. Rejected per earlier decision - no new dev dependency, reuse the ruff step already wired into CI.

## Risks / Trade-offs

- **Explicit `members:` lists are a manual maintenance point** → a future new method that nobody adds to either list simply doesn't render anywhere (silent, same failure mode this change is fixing). Mitigation: the new ruff `D1xx` step flags missing docstrings on the method itself, which is the more common miss; there's no automated check for "docstring present but forgot to add to a page's `members:` list" - accepted as a manual review cost, small given the API surface changes rarely.
- **Two pages for one class** could read as two classes to someone skimming the nav without context. Mitigation: cross-link the pages (reference.md ↔ authentication.md) and keep both under the same "API" nav section.
- **`D1xx`-only CI check doesn't assess docstring quality**, just presence - a placeholder one-liner satisfies it. Accepted: matches the "check but don't block" request: a coverage signal, not a quality gate.

## Migration Plan

Docs/lint-only change, no runtime migration or rollback concerns beyond reverting the commit:
1. Add the 12 missing docstrings + 2 class docstrings (`Tado`, `RateLimitInfo`) in `libtado/api.py`.
2. Add `docs/api/authentication.md`, update `docs/api/reference.md`'s and the new page's `members:` options in `mkdocs.yml`'s nav, add the cross-link from `docs/getting-started/usage.md`.
3. Add the `D1xx` ruff selection to `pyproject.toml` and the non-blocking step to `.github/workflows/lint.yml`.
4. Build the mkdocs site locally (`mkdocs build` or `mkdocs serve`) to confirm both pages render the intended member lists and nothing functional disappeared.

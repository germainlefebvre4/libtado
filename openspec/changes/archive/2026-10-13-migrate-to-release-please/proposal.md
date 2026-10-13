# Proposal

## Why

La release est aujourd'hui pilotée par `semantic-release` 21.1.1, lancé via `cycjimmy/semantic-release-action` avec un `.releaserc` généré à la volée dans deux workflows. Il publie automatiquement à chaque push sur `master`, sans étape de relecture, et ne laisse aucune trace dans le dépôt : le `CHANGELOG.md` n'existe pas, et `pyproject.toml` / `uv.lock` indiquent `3.7.13` alors que la dernière release est `4.3.0` (la version n'est posée qu'en CI par `uv version`, sans être committée). Release Please rend la release explicite (une PR de release relue puis mergée), versionne le dépôt lui-même et produit un changelog, tout en conservant SemVer et Conventional Commits.

## What Changes

- Remplacer `release-master.yml` (semantic-release) par un workflow `release-please.yml` : `googleapis/release-please-action` sur `master`, puis un job de publication PyPI (`uv build` / `uv publish`) conditionné par `release_created`.
- Ajouter `release-please-config.json` (type `python`, `include-v-in-tag: false` pour conserver les tags `4.3.0`, `changelog-sections` alignées sur les types qui déclenchent une release aujourd'hui (`feat`, `fix`, `perf`), `extra-files` TOML pour `uv.lock`) et `.release-please-manifest.json` amorcé à `4.3.0`.
- Convertir `release-feat-dryrun.yml` en `publish-testpypi.yml` déclenché uniquement par `workflow_dispatch` : publication sur TestPyPI en `<version du manifest>.dev<run_id>`, sans dépendance à semantic-release.
- Ajouter un workflow de contrôle du titre de PR (Conventional Commit), car seul le squash est autorisé et Release Please lira le titre de PR comme message de commit sur `master`.
- Conserver `conventional-commit.yml` (cocogitto) et `cog.toml` tels quels.
- Mettre à jour la documentation : section TestPyPI de `docs/contributing.md` (plus de publication à chaque push de branche) et badge du `README.md` qui référence le workflow `Release Management`.
- Supprimer toute trace de `semantic-release` (workflows, `.releaserc` généré).
- Le `CHANGELOG.md` est créé par la première PR de release.

Aucun **BREAKING** : les tags, le schéma de version et les règles de bump (`feat` = minor, `fix` = patch, `!` / `BREAKING CHANGE` = major) sont inchangés. Le seul changement de comportement est humain : une release n'est publiée qu'après merge de la PR de release.

## Capabilities

### New Capabilities

Aucune. Il s'agit d'outillage CI/release, sans comportement spécifié au niveau de la bibliothèque (`skip_specs: true`, comme `fix-release-dryrun-guards`).

### Modified Capabilities

Aucune. `openspec/specs/` est vide.

## Impact

- `.github/workflows/` : `release-master.yml` remplacé, `release-feat-dryrun.yml` renommé et simplifié, nouveau workflow de contrôle du titre de PR.
- Nouveaux fichiers racine : `release-please-config.json`, `.release-please-manifest.json`, puis `CHANGELOG.md` créé par la première PR de release.
- `pyproject.toml` et `uv.lock` : la version devient mise à jour par la PR de release (aujourd'hui `3.7.13`, périmée).
- `docs/contributing.md`, `README.md`.
- Secrets `PYPI_TOKEN` et `PYPI_TEST_TOKEN` : inchangés. Les permissions du dépôt autorisent déjà la création de PR par `GITHUB_TOKEN`.
- Aucun changement dans `libtado/` ni dans les artefacts publiés, hormis la version.

# Tasks

## 1. Configuration Release Please

- [x] 1.1 Créer `.release-please-manifest.json` (`{ ".": "4.3.0" }`) et vérifier que `check-json` (pre-commit) passe sur le fichier
- [x] 1.2 Créer `release-please-config.json` (`release-type: python`, `include-v-in-tag: false`, `include-component-in-tag: false`, `changelog-sections` : `feat` / `fix` / `perf` visibles, `refactor` / `chore` / `docs` / `test` / `ci` / `build` / `style` cachés, `extra-files` TOML sur `uv.lock` avec le jsonpath du package `libtado`) et vérifier que `check-json` passe
- [x] 1.3 Pousser la branche `ci/migrate-release-please`, lancer `npx release-please release-pr --dry-run` avec cette branche comme `--target-branch`, et vérifier que le tag `4.3.0` est retrouvé, que la version proposée est cohérente avec les commits depuis ce tag, et que `pyproject.toml`, `uv.lock` et `CHANGELOG.md` figurent dans les fichiers mis à jour (sinon, noter le résultat pour le repli de la tâche 2.3)

## 2. Workflow de release

- [x] 2.1 Créer `.github/workflows/release-please.yml` : déclencheur push `master`, permissions `contents: write` et `pull-requests: write`, job `release-please` (`googleapis/release-please-action` v4 avec config et manifest) exposant `release_created` et `tag_name`, et vérifier que `uv run --with yamllint yamllint --strict --config-file .yamllint .github/workflows/release-please.yml` passe
- [x] 2.2 Ajouter le job `publish` (`needs: release-please`, `if: release_created == 'true'`, checkout, `setup-uv`, `uv build`, `uv publish` avec `PYPI_TOKEN`, sans `uv version`) et vérifier avec `yamllint --strict` que chaque step est bien gardé par la condition
- [x] 2.3 Si la tâche 1.3 montre que `uv.lock` n'est pas mis à jour par `extra-files` : remplacer l'entrée `uv.lock` de `release-please-config.json` par un step `uv lock` qui committe sur `pr.headBranchName`, et vérifier le résultat sur la première PR de release (tâche 6.2) ; sinon, marquer cette tâche comme sans objet
- [x] 2.4 Supprimer `.github/workflows/release-master.yml` et vérifier avec `grep -ri "semantic" .github` qu'il ne reste aucune référence à semantic-release dans les workflows

## 3. Workflow TestPyPI manuel

- [x] 3.1 Renommer `release-feat-dryrun.yml` en `publish-testpypi.yml` (`git mv`) et remplacer le déclencheur par `workflow_dispatch`, sans job `release` ni semantic-release, et vérifier avec `yamllint --strict` que le fichier est valide et que `on:` ne contient que `workflow_dispatch`
- [x] 3.2 Calculer la version dans le workflow avec `jq -r '."."' .release-please-manifest.json`, la poser avec `uv version "<manifest>.dev${{ github.run_id }}"`, puis `uv build` et `uv publish --publish-url https://test.pypi.org/legacy/ --check-url https://test.pypi.org/simple/` avec `PYPI_TEST_TOKEN`, et vérifier le calcul en local en exécutant les commandes `jq` et `uv version` sur une copie jetable du dépôt (résultat attendu : `4.3.0.dev<N>`)

## 4. Contrôle du titre de PR

- [x] 4.1 Créer `.github/workflows/pr-title.yml` (`pull_request` sur `opened`, `edited`, `synchronize`, `reopened`, `amannn/action-semantic-pull-request` avec les types `feat`, `fix`, `perf`, `refactor`, `chore`, `docs`, `test`, `ci`, `build`, `style`, `revert`) et vérifier avec `yamllint --strict` que le fichier est valide
- [x] 4.2 Vérifier sur la PR de migration qu'un titre non conforme (par exemple `Migrate release`) fait échouer le check, puis qu'un titre conforme (`ci: Migrate to Release Please`) le fait passer

## 5. Documentation

- [x] 5.1 Mettre à jour `docs/contributing.md` : remplacer la phrase sur la publication TestPyPI à chaque commit de branche par la procédure manuelle (`workflow_dispatch`, forme de la version `<dernière release>.dev<run_id>`), et décrire le flux PR de release et la règle du titre de PR ; vérifier avec `markdownlint-cli2 docs/contributing.md` (config `.markdownlint-cli2.yaml`)
- [x] 5.2 Remplacer le badge `Release Management` du `README.md` par le badge du workflow `release-please.yml` et vérifier que l'URL du badge pointe vers le nouveau nom de workflow

## 6. Intégration de bout en bout

- [x] 6.1 Ouvrir la PR de migration avec un titre `ci: …`, vérifier que tous les checks (cocogitto, lint, titre de PR) passent, que `release-master.yml` n'existe plus, et que le merge en squash sur `master` ne déclenche aucune release
- [x] 6.2 Vérifier que la première exécution de `release-please.yml` sur `master` ouvre une PR de release, puis relire sa version, son changelog et son diff de `pyproject.toml` et `uv.lock` (appliquer 2.3 si `uv.lock` est incorrect)
- [x] 6.3 Merger la PR de release et vérifier que le tag `X.Y.Z` (sans `v`) et la GitHub Release existent, que `publish` a publié sur PyPI (`pip index versions libtado`), et que `pyproject.toml` et `uv.lock` sur `master` portent la nouvelle version
- [x] 6.4 Lancer `publish-testpypi.yml` depuis une branche via `workflow_dispatch` et vérifier que la version `X.Y.Z.dev<run_id>` apparaît sur TestPyPI

## Workflow follow-up

- Archiver le change une fois la première release publiée via Release Please.
- Optionnel, hors de ce change : ajouter le check « titre de PR » comme obligatoire dans la protection de `master`.

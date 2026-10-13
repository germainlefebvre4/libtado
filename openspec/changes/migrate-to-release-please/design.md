# Design

## Context

Voir `proposal.md` pour la motivation. État actuel observé :

- `release-master.yml` : `semantic-release` 21.1.1 (preset angular par défaut) génère le tag `X.Y.Z` (sans `v`) et la GitHub Release, puis le job `deploy` pose la version avec `uv version` et publie sur PyPI. Rien n'est committé.
- `release-feat-dryrun.yml` : sur push de `develop`, `feat/*`, `fix/*`, `ci/*`, `chore/*`, un dry-run semantic-release calcule la prochaine version, puis `deploy` publie `X.Y.Z.dev<run_number>` sur TestPyPI.
- `conventional-commit.yml` : cocogitto vérifie les commits des PR. Il ne voit pas le titre de PR.
- Seul le squash est autorisé (titre de commit = titre de PR). Le dernier tag est `4.3.0`. `pyproject.toml` et `uv.lock` disent `3.7.13`.
- `GITHUB_TOKEN` a les droits `write` et peut créer des PR. La CI n'utilise pas `uv sync --locked`.

Contrainte : conserver SemVer, Conventional Commits, le format des tags et les secrets existants.

## Goals / Non-Goals

**Goals:**
- Mêmes règles de bump qu'aujourd'hui, et seuls `feat`, `fix`, `perf` et les breaking changes déclenchent une release.
- Version du dépôt (`pyproject.toml`, `uv.lock`) et `CHANGELOG.md` committés via la PR de release.
- Publication PyPI dans le workflow qui crée la release.
- Test de publication TestPyPI conservé, mais lancé à la main.

**Non-Goals:**
- Pas de monorepo ni de multi-packages : un seul package racine.
- Pas de migration vers le trusted publishing PyPI : les tokens restent.
- Pas de pré-release ni de canaux (`develop`, `next`) côté Release Please.
- Pas de changement dans `libtado/`.

## Decisions

### 1. Release Please en mode manifest, un package racine

`release-please-config.json` : `release-type: python`, `include-v-in-tag: false`, `include-component-in-tag: false` (sinon le tag devient `libtado-4.4.0`). `.release-please-manifest.json` : `{ ".": "4.3.0" }`. Le manifest sert de point de départ : la première PR de release calcule le bump à partir des commits postérieurs au tag `4.3.0`, et réécrit `pyproject.toml` (aujourd'hui `3.7.13`) à la bonne valeur.

*Alternative écartée* : mode sans manifest (`release-type` en input de l'action). Plus court, mais l'`extra-files`, les sections de changelog et la lecture de la version par le workflow TestPyPI passent plus proprement par un fichier de config et un manifest versionnés.

### 2. Sections de changelog : calquées sur `cog.toml`, sauf `chore` et `refactor` qui restent cachés

Release Please ne crée une PR que si le changelog contient au moins une entrée visible. Rendre `chore` visible, comme dans `cog.toml`, ferait donc ouvrir une PR de release (patch) pour chaque bump Dependabot. Pour reproduire le comportement de semantic-release :
- visibles : `feat` (Features), `fix` (Bugfix), `perf` (Performance) ;
- cachés : `refactor`, `chore`, `docs`, `test`, `ci`, `build`, `style`.

Les types `doc` de `cog.toml` correspondent à `docs` dans l'usage réel du dépôt. `cog.toml` reste inchangé (il ne sert qu'à cocogitto).

### 3. `uv.lock` mis à jour par `extra-files` TOML, avec repli

`extra-files` : `{ "type": "toml", "path": "uv.lock", "jsonpath": "$.package[?(@.name=='libtado')].version" }`. La PR de release met alors à jour `pyproject.toml` et `uv.lock` ensemble.

Repli, si la PR de release ne contient pas la bonne modification de `uv.lock` : un step `uv lock` dans `release-please.yml`, qui checkout la branche de la PR de release (`pr.headBranchName`), relance `uv lock` et committe.

*Alternative écartée* : ne rien faire. Le diff parasite de `uv.lock` reviendrait à chaque release (`uv sync` local, hook `uv-lock`).

### 4. `release-please.yml` : un job release, un job publish

- Déclencheur : push sur `master`. Permissions : `contents: write`, `pull-requests: write`.
- Job `release-please` : `googleapis/release-please-action` (v4) avec la config et le manifest. Outputs exposés : `release_created`, `tag_name`.
- Job `publish` : `needs: release-please`, `if: release_created == 'true'`. Checkout du commit de merge (qui contient déjà la bonne version dans `pyproject.toml`), donc plus de `uv version`, puis `uv build` et `uv publish` avec `PYPI_TOKEN`.

La publication reste dans le même workflow car les événements créés avec `GITHUB_TOKEN` (la GitHub Release) ne déclenchent pas d'autres workflows.

### 5. `publish-testpypi.yml` : `workflow_dispatch` uniquement, version dérivée du manifest

- Déclencheur : `workflow_dispatch`, depuis n'importe quelle branche.
- Version : `<manifest>.dev<run_id>`, où `<manifest>` vient de `jq -r '."."' .release-please-manifest.json`. Pas besoin de `fetch-depth: 0` ni de `git describe`.
- Étapes : `setup-uv`, `uv version`, `uv build`, `uv publish --publish-url https://test.pypi.org/legacy/` avec `PYPI_TEST_TOKEN`.

La version n'est pas la prochaine version (Release Please ne sait pas la prédire hors de `master`) ; elle est inférieure à la dernière release (`4.3.0.dev…` < `4.3.0`), ce qui est sans conséquence sur TestPyPI.

*Pourquoi `run_id` plutôt que `run_number` (annoncé dans la proposition)* : renommer le workflow le fait repartir de `run_number = 1`, avec un risque de collision avec des versions `4.3.0.devN` déjà présentes sur TestPyPI (qui refuse l'écrasement). `run_id` est unique et croissant.

*Alternative écartée* : garder le déclenchement sur push de branches. Le dry-run semantic-release disparaît, et le calcul de version n'a plus de source fiable.

### 6. Contrôle du titre de PR : `amannn/action-semantic-pull-request`

Workflow sur `pull_request` (`opened`, `edited`, `synchronize`, `reopened`). Types autorisés : `feat`, `fix`, `perf`, `refactor`, `chore`, `docs`, `test`, `ci`, `build`, `style`, `revert`. Le titre `chore(master): release X.Y.Z` de la PR de release et les titres Dependabot (`chore(deps): …`) sont conformes. `conventional-commit.yml` (cocogitto) est conservé : il contrôle les commits, le nouveau workflow contrôle ce qui sera lu sur `master`.

*Alternative écartée* : étendre cocogitto au titre. Il n'a pas de mode « titre de PR ».

### 7. Documentation et nettoyage

- `docs/contributing.md` : remplacer la section « chaque commit sur une branche génère une release sur PyPI Test » par la procédure manuelle (`workflow_dispatch`) et décrire le flux PR de release.
- `README.md` : le badge `Release Management` pointe vers un workflow qui disparaît, à remplacer par le badge de `release-please.yml`.

## Risks / Trade-offs

- **Les PR créées avec `GITHUB_TOKEN` ne déclenchent pas les checks** (lint, tests, cocogitto, titre) → la PR de release n'aura pas de statuts. Vérifié : la protection de `master` n'impose aucun check obligatoire (PR requise, 0 approbation, aucun ruleset), donc la PR de release reste mergeable sans PAT. Si des checks obligatoires sont ajoutés plus tard, fournir un PAT ou un token d'App GitHub via l'input `token` de l'action.
- **Le filtre jsonpath sur `uv.lock` peut ne pas fonctionner** (structure `[[package]]`) → Mitigation : validation sur la première PR de release, qui est relue avant merge, avec repli `uv lock` (décision 3).
- **Un titre de PR non conforme masque un `feat`** (le squash prend le titre) → Mitigation : le contrôle du titre. Il n'est pas bloquant tant que la protection de `master` n'exige pas ce check ; l'ajouter comme check obligatoire est une action manuelle hors de ce change.
- **Première PR de release imprévisible** : elle agrège tous les commits depuis `4.3.0` → relire le bump proposé avant de merger. Si Release Please ne retrouve pas le tag `4.3.0`, ajouter `bootstrap-sha`.
- **Perte du test de publication automatique sur chaque branche** → accepté : le test devient manuel, et la PR de release exerce le chemin de publication réel à chaque release.
- **Re-run d'une même exécution du workflow TestPyPI** : même `run_id`, donc même version, rejetée par TestPyPI → ajouter `--check-url` à `uv publish` ou relancer un nouveau dispatch.

## Migration Plan

1. Valider la config en dry-run du CLI `release-please` (`release-pr --dry-run`, avec la branche poussée comme `--target-branch`) : tag `4.3.0` retrouvé, version proposée plausible, `uv.lock` listé dans les fichiers mis à jour.
2. Dans une seule PR : ajouter la config et le manifest, remplacer `release-master.yml`, convertir le workflow TestPyPI, ajouter le contrôle du titre, mettre à jour la doc. Le titre de la PR sera de type `ci:` (caché, aucune release n'est déclenchée par le merge).
3. Au merge, la première exécution de `release-please.yml` ouvre la PR de release : relire la version, le changelog et le diff de `pyproject.toml` / `uv.lock`, appliquer le repli si besoin, puis merger.
4. Vérifier la publication PyPI et la GitHub Release `X.Y.Z`.
5. Lancer une fois `publish-testpypi.yml` à la main pour valider le workflow.

**Rollback** : revert de la PR de migration. Les tags et les releases ne sont pas modifiés, et semantic-release repart des tags existants. Si une release Release Please a déjà été publiée, semantic-release continue depuis ce tag.

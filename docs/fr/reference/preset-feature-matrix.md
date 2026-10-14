# Matrice des préréglages d'architecture et fonctionnalités

L'interactif `fastkit init --interactive` demande un **préréglage d'architecture** ([issue #44](https://github.com/bnbong/FastAPI-fastkit/issues/44)) avant de collecter les sélections de fonctionnalités. Le préréglage façonne la disposition du projet généré — chaque préréglage embarque un modèle de base différent et place les fichiers de configuration générés à des emplacements différents, pour qu'ils cohabitent avec la structure existante plutôt qu'au sein d'une arborescence parallèle `src/config/`.

Cette page sert de référence pour comprendre ce que fait chaque préréglage, où les fichiers sont écrits et quelles combinaisons de fonctionnalités demandent encore un câblage manuel.

## Préréglage → modèle de base

| Préréglage | Modèle de base | Description |
|---|---|---|
| `minimal` | `fastapi-empty` | L'application FastAPI minimale viable — le `main.py` d'amorçage est régénéré à partir de vos sélections de fonctionnalités. |
| `single-module` | `fastapi-single-module` | Application FastAPI monofichier — `main.py` est régénéré. |
| `classic-layered` | `fastapi-default` | Découpe en couches (`api/routes`, `crud`, `schemas`, `core`). Le `main.py` livré est préservé. |
| `domain-starter` | `fastapi-domain-starter` | Orienté domaine (`src/app/domains/<concept>/`). Le `main.py` livré est préservé. **Valeur par défaut recommandée.** |

## Emplacements des fichiers générés

| Préréglage | Gestion de `main.py` | Cible de config base de données | Cible de config auth |
|---|---|---|---|
| `minimal` | régénéré à `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `single-module` | régénéré à `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `classic-layered` | préservé (livré par le modèle) | `src/core/database.py` | `src/core/auth.py` |
| `domain-starter` | préservé (livré par le modèle) | `src/app/core/database.py` | `src/app/core/auth.py` |

## Prise en charge des fonctionnalités base de données / authentification par préréglage

Ces fonctionnalités sont prises en charge dans **tous** les préréglages — l'installation du paquet réussit toujours ; la différence est de savoir si la superposition dynamique de `main.py` les câble également automatiquement.

| Fonctionnalité | `minimal` / `single-module` | `classic-layered` / `domain-starter` |
|---|---|---|
| **Base de données** (PostgreSQL, MySQL, SQLite, MongoDB) | Génère le module de configuration **et** insère des appels `await init_db()` dans le `main.py` régénéré. | Génère le module de configuration au chemin du préréglage. Le `main.py` livré est **préservé**, câblez donc manuellement `get_db()` dans les routeurs. |
| **Authentification** (JWT, FastAPI-Users, OAuth2, basée sur session) | Génère le module de configuration d'authentification ; JWT importe `HTTPBearer`, et OAuth2 ainsi que l'authentification basée sur session ajoutent aussi leur configuration de middleware dans `main.py`. | Génère le module de configuration d'authentification au chemin du préréglage. Aucun import n'est ajouté à `main.py` — câblez les dépendances manuellement. |
| **Tâches en arrière-plan** (Celery, Dramatiq) | Génère `worker.py` et `features/tasks.py`, et monte le routeur de tâches dans le `main.py` régénéré. | Génère `worker.py` et `features/tasks.py`, mais le `main.py` livré est **préservé** — montez le routeur manuellement. |
| **Mise en cache** (Redis) | Génère `features/cache.py` et le monte / l'initialise dans le `main.py` régénéré. | Génère `features/cache.py` ; montez-le manuellement. |
| **Utilitaires : Pagination / WebSocket** | Génère `features/pagination.py` / `features/websocket.py` et monte le routeur dans le `main.py` régénéré. | Génère le même module ; montez-le manuellement. |
| **Supervision : OpenTelemetry** | Aucun fichier autonome — la configuration du traçage est ajoutée directement au `main.py` régénéré. | Aucun fichier autonome. Le `main.py` livré est préservé, le traçage n'est donc **pas câblé** — ajoutez la configuration manuellement. |
| **Migrations** (Alembic) | Génère `alembic.ini`, `alembic/env.py`, une révision de référence et `scripts/migrate.sh` pour toute sélection de base de données SQL — indépendamment de la superposition de `main.py`. | Idem — la génération Alembic ne dépend pas de la préservation de `main.py`. |
| **Outillage** (ruff, pre-commit, github-actions, devcontainer, makefile) | Génère le ou les fichiers de configuration correspondants, indépendamment de la superposition de `main.py`. | Idem. |
| **Journalisation** (structured) | Génère `logging_config.py` et câble le middleware d'identifiant de requête dans le `main.py` régénéré. | Génère `logging_config.py` ; le `main.py` livré est préservé, câblez donc le middleware manuellement. |
| **CORS** (utilitaire) | `CORSMiddleware` est ajouté au `main.py` régénéré avec `allow_origins=['*']`. | **Déjà câblé** dans le `main.py` livré (conditionné par `settings.all_cors_origins`). Activez-le en définissant `BACKEND_CORS_ORIGINS` dans `.env` — aucune modification de code nécessaire. |
| **Tests** (Basic / Coverage / Advanced) | `pytest.ini` est généré à la racine du projet ; Advanced ajoute aussi `tests/factories.py` et `tests/test_factories.py`. | Idem. |
| **Déploiement** (Docker, docker-compose) | `Dockerfile` et/ou `docker-compose.yml` écrits à la racine du projet. | Idem. |
| **`/health` / `/ready`** | Toujours présents dans le `main.py` régénéré. | Déjà présents dans le `main.py` préservé, livré par le modèle. |

## Quand un avertissement « Préréglage compatibilité » apparaît

Pour les préréglages qui **préservent le `main.py` livré** (`classic-layered`, `domain-starter`), certaines sélections de fonctionnalités ne seront pas câblées automatiquement dans l'application. Le CLI affiche un avertissement ponctuel à la fin de la génération listant les sélections qui nécessitent un câblage manuel :

| Fonctionnalité sélectionnée | Déclenche un avertissement sous `classic-layered` / `domain-starter` ? |
|---|---|
| `CORS` (utilitaire) | ❌ — déjà câblé dans le `main.py` livré. Renseignez simplement `BACKEND_CORS_ORIGINS` dans `.env`. |
| `Rate-Limiting` (utilitaire) | ✅ — la configuration du limiteur `slowapi` n'est pas ajoutée |
| `Pagination` / `WebSocket` (utilitaire) | ✅ — le routeur généré (`features/pagination.py` / `features/websocket.py`) n'est pas monté |
| `Celery` / `Dramatiq` (async_tasks) | ✅ — le routeur généré `worker.py` / `features/tasks.py` n'est pas monté |
| `Redis` (mise en cache) | ✅ — le `features/cache.py` généré n'est ni monté ni initialisé |
| `Prometheus` / `OpenTelemetry` (supervision) | ✅ — la configuration de l'instrumentation n'est pas ajoutée à `main.py` |
| `structured` (journalisation) | ✅ — `logging_config.py` est généré, mais le middleware d'identifiant de requête n'est pas ajouté à `main.py` |
| `Alembic` (migrations), sélections d'outillage | ❌ — ces fichiers sont générés et utilisables quel que soit le préréglage ; rien ne dépend de `main.py` |
| Toute sélection base de données / authentification | ⚠️ — les fichiers de configuration sont générés, mais vous devez les passer en `Depends()` dans vos routeurs |

Pour les préréglages `minimal` et `single-module`, la superposition dynamique de `main.py` gère automatiquement chacun des axes ci-dessus ; aucun avertissement n'est émis.

## Combinaisons non prises en charge (rester prudent)

Le stratège n'essaie **délibérément pas** d'injecter du code généré dans un `main.py` livré par le modèle. Le faire risquerait de produire des imports cassés ou des routeurs dupliqués. Le contrat est :

- Les paquets sélectionnés sont toujours installés (afin que `pip freeze` corresponde à l'intention de l'utilisateur).
- Les modules de configuration générés atterrissent toujours au chemin approprié au préréglage.
- Pour les préréglages qui préservent main, l'utilisateur est informé des sélections qui nécessitent encore un câblage manuel, plutôt que de recevoir silencieusement du code cassé.

Si vous avez besoin du câblage automatique complet de toutes les fonctionnalités, choisissez `minimal` ou `single-module` — ils régénèrent `main.py` à partir des drapeaux de fonctionnalités.

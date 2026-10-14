# Référence CLI

Référence complète de toutes les commandes de l'interface en ligne de commande de FastAPI-fastkit.

## Options globales

Toutes les commandes acceptent ces options globales :

```console
$ fastkit [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Options globales

| Option | Description |
|--------|-------------|
| `--version` | Afficher la version de FastAPI-fastkit |
| `--help` | Afficher le message d'aide |

### Exemples

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0

$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## Commandes

### `init`

Créer un nouveau projet FastAPI avec une configuration interactive.

#### Syntaxe

```console
$ fastkit init [OPTIONS]
```

#### Options

| Option | Description | Défaut |
|--------|-------------|---------|
| `--interactive` | Configuration guidée : préréglage d'architecture, puis sélection des fonctionnalités | désactivé |
| `--config <path>` | Créer le projet à partir d'un fichier de configuration enregistré, sans aucune question | - |
| `--save-config <path>` | Avec `--interactive`, écrire la configuration répondue à ce chemin | - |
| `--project-name` | Nom du projet (demandé s'il est omis) | - |
| `--author` | Nom de l'auteur (demandé s'il est omis) | - |
| `--author-email` | E-mail de l'auteur (demandé s'il est omis) | - |
| `--description` | Description du projet (demandée si elle est omise) | - |
| `--package-manager` | Gestionnaire de paquets à utiliser (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Afficher les fichiers et paquets qui seraient créés, sans rien écrire | désactivé |
| `--no-venv` | Ignorer la création de l'environnement virtuel (implique `--no-install`) | désactivé |
| `--no-install` | Ignorer l'installation des dépendances | désactivé |
| `--yes` / `-y` | Ne pas demander de confirmation avant d'écraser des fichiers existants lors d'un déploiement du projet sur place | désactivé |
| `--help` | Afficher l'aide de la commande | - |

#### Fichiers de configuration (`--config` / `--save-config`)

Les réponses d'une session interactive forment un simple mapping, et ce mapping peut transiter par un fichier. La création de projet devient ainsi quelque chose que vous pouvez committer, relire et rejouer.

```console
# enregistrer une session interactive
$ fastkit init --interactive --save-config fastkit.config.json

# la rejouer plus tard, sans aucune question
$ fastkit init --config fastkit.config.json
```

Si vous ne passez pas `--save-config`, une exécution interactive menée à son terme demande s'il faut enregistrer les sélections et où les placer. Cette question n'apparaît que lorsqu'une personne est devant le terminal — les exécutions redirigées ou en CI restent silencieuses et s'y abonnent plutôt avec l'option.

**Les formats pris en charge** sont choisis d'après l'extension du fichier :

| Extension | Disponibilité |
|---|---|
| `.json` | Toujours (bibliothèque standard) |
| `.toml` | Toujours (bibliothèque standard) |
| `.yaml` / `.yml` | Uniquement lorsque PyYAML est installé — fastkit ne l'ajoute pas comme dépendance d'exécution |

Un fichier chargé doit contenir un mapping au niveau supérieur avec au moins `project_name`, `author` et `author_email`. Il est ensuite validé avec les mêmes règles que celles des invites interactives (forme du nom de projet, format de l'e-mail, `all_dependencies` doit être une liste), et chaque problème est signalé avant que quoi que ce soit ne soit écrit. Un fichier qui ne liste que des sélections de fonctionnalités — sans `all_dependencies` — est développé par le constructeur interactif, si bien qu'une configuration écrite à la main et une session de l'assistant aboutissent au même ensemble de paquets.

Un exemple minimal :

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv"
}
```

#### Schéma du fichier de configuration

Chaque fichier de configuration — écrit à la main ou produit par `--save-config` — passe par le même normaliseur avant d'atteindre le générateur (`normalize_project_config` dans `backend/project_builder/config_schema.py`). Une clé inconnue, un choix inconnu pour un axe connu ou une valeur du mauvais type est rejeté avec le nom fautif et la liste des valeurs réellement autorisées, au lieu d'être ignoré silencieusement.

| Clé | Forme | Remarques |
|---|---|---|
| `project_name`, `author`, `author_email` | chaîne | Requis |
| `description` | chaîne | Requis |
| `architecture_preset` (alias `preset`) | `"minimal"` \| `"single-module"` \| `"classic-layered"` \| `"domain-starter"` | Les deux graphies doivent concorder si elles sont toutes deux présentes |
| `package_manager` | `"pip"` \| `"uv"` \| `"pdm"` \| `"poetry"` | |
| `database` | chaîne, ou `{"type": <choice>}` | `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `SQLite`, `None` |
| `authentication`, `async_tasks`, `testing`, `caching`, `monitoring`, `migrations`, `logging` | chaîne, ou `{"type": <choice>}` | Axes à sélection unique — consultez le [catalogue de fonctionnalités](#catalogue-de-fonctionnalites-du-constructeur-interactif-interactive) ci-dessus pour les choix de chaque axe |
| `utilities`, `tooling` | liste de chaînes | Axes à sélection multiple — même catalogue pour les choix |
| `deployment` | liste de chaînes | Sous-ensemble de `Docker`, `docker-compose` ; choisir `docker-compose` ajoute automatiquement `Docker` |
| `custom_packages` | liste de chaînes | Paquets supplémentaires à installer tels quels |

Chaque axe accepte soit son choix brut (`"authentication": "JWT"`), soit la forme de mapping `{"type": ...}` qu'utilisent `database` et les propres métadonnées `[tool.fastapi-fastkit]` d'un projet (`"authentication": {"type": "JWT"}`) — les deux se normalisent vers la même forme canonique, et `--save-config` réécrit toujours la forme canonique en chaîne brute.

Une configuration qui exerce la plupart des axes :

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv",
  "database": "PostgreSQL",
  "authentication": "JWT",
  "async_tasks": "Celery",
  "caching": "Redis",
  "migrations": "Alembic",
  "tooling": ["ruff", "makefile"],
  "deployment": ["Docker"]
}
```

La même configuration en TOML :

```toml
project_name = "orders-api"
author = "Developer Kim"
author_email = "developer@example.com"
description = "Domain-oriented orders service"
architecture_preset = "domain-starter"
package_manager = "uv"
database = "PostgreSQL"
authentication = "JWT"
async_tasks = "Celery"
caching = "Redis"
migrations = "Alembic"
tooling = ["ruff", "makefile"]
deployment = ["Docker"]
```

#### Prévisualiser et ignorer des étapes

`--dry-run` affiche l'arborescence qui serait créée et les paquets qui seraient installés — avec le gestionnaire de paquets qui les installerait — puis se termine sans toucher au disque :

```console
$ fastkit init --config fastkit.config.json --dry-run
```

`--no-install` s'arrête après la création de l'environnement virtuel ; `--no-venv` ignore également l'environnement (et donc l'installation). Les deux sont utiles dans les conteneurs, en CI et partout où l'environnement est géré en dehors de fastkit.

#### Déploiement sur place et confirmation d'écrasement (`--yes` / `-y`)

Lorsqu'un projet est déployé sur place — dans l'espace de travail courant plutôt que dans un nouveau dossier de projet — fastkit demande « Overwrite these files? » avant de remplacer tout fichier déjà existant. `--yes` (ou sa forme courte `-y`) ignore cette confirmation et procède à l'écrasement. Cela n'affecte pas la question distincte « Do you want to proceed with project creation? », qui reste affichée. Dans un environnement non interactif (stdin n'est pas un TTY, comme en CI ou lors d'une exécution redirigée), la confirmation d'écrasement est ignorée automatiquement, même sans `--yes`.

#### Invites interactives

La commande `init` vous demandera :

1. **Nom du projet** : nom de répertoire et nom du paquet
2. **Nom de l'auteur** : informations sur l'auteur du paquet
3. **E-mail de l'auteur** : adresse de contact du paquet
4. **Description du projet** : brève description du projet
5. **Sélection de la pile** : choisir parmi minimal, standard ou full
6. **Sélection du gestionnaire de paquets** : choisir parmi pip, uv, pdm ou poetry (à moins de l'avoir spécifié avec `--package-manager`)

#### Options de pile

**Pile MINIMAL :**

- `fastapi` — framework FastAPI
- `uvicorn` — serveur ASGI
- `pydantic` — validation des données
- `pydantic-settings` — gestion de la configuration

**Pile STANDARD :**

- Tous les paquets de la pile MINIMAL
- `sqlalchemy` — boîte à outils SQL et ORM
- `alembic` — outil de migration de base de données
- `pytest` — framework de test

**Pile FULL :**

- Tous les paquets de la pile STANDARD
- `redis` — stockage de données en mémoire
- `celery` — file de tâches distribuée

#### Catalogue de fonctionnalités du constructeur interactif (`--interactive`)

`fastkit init --interactive` parcourt un catalogue différent, organisé par axes, au lieu des piles minimal/standard/full ci-dessus (source de vérité : `FastkitConfig.PACKAGE_CATALOG` dans `core/settings.py`, et `DynamicConfigGenerator.build_artifacts()` pour ce que génère chaque choix). Chaque axe vaut `None` (ignoré) par défaut ; `utilities` et `tooling` sont à sélection multiple.

Chaque sélection génère désormais du code réel, et pas seulement des paquets installés — consultez la [matrice préréglages d'architecture / fonctionnalités](../reference/preset-feature-matrix.md) pour voir en quoi `minimal` / `single-module` (`main.py` régénéré) et `classic-layered` / `domain-starter` (`main.py` préservé, avertissements de câblage manuel) diffèrent.

| Axe | Choix | Paquets installés | Fichiers générés |
|---|---|---|---|
| `database` | PostgreSQL, MySQL, MongoDB, Redis, SQLite, None | PostgreSQL : `asyncpg`, `sqlalchemy` · MySQL : `aiomysql`, `sqlalchemy` · MongoDB : `motor` · Redis : `redis[hiredis]` · SQLite : `sqlalchemy`, `aiosqlite` | Un module de configuration de base de données au chemin du préréglage (par ex. `src/config/database.py`) |
| `authentication` | JWT, OAuth2, FastAPI-Users, Session-based, None | JWT : `pyjwt[crypto]`, `pwdlib[argon2]` · OAuth2 : `authlib`, `itsdangerous`, `httpx` · FastAPI-Users : `fastapi-users[sqlalchemy]`, `pyjwt[crypto]`, `pwdlib[argon2]` · Session-based : `itsdangerous` | Un module de configuration d'authentification au chemin du préréglage ; OAuth2 et Session-based ajoutent aussi une configuration de middleware dans `main.py` |
| `async_tasks` | Celery, Dramatiq, None | Celery : `celery[redis]`, `redis[hiredis]` · Dramatiq : `dramatiq[redis]`, `redis[hiredis]` | `<pkg>/worker.py` (worker d'arrière-plan) + `<pkg>/features/tasks.py` (routes de tâches) |
| `testing` | Basic, Coverage, Advanced, None | Basic : `pytest`, `pytest-asyncio`, `httpx` · Coverage : + `pytest-cov` · Advanced : + `faker`, `factory-boy` | `pytest.ini` ; Advanced ajoute aussi `tests/factories.py` et `tests/test_factories.py` |
| `caching` | Redis, None | Redis : `redis[hiredis]`, `fastapi-cache2`, `jinja2` | `<pkg>/features/cache.py` (points d'extrémité mis en cache) |
| `monitoring` | Loguru, OpenTelemetry, Prometheus, None | Loguru : `loguru` · OpenTelemetry : `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp-proto-http` · Prometheus : `prometheus-client`, `prometheus-fastapi-instrumentator` | Aucun fichier autonome — câblé directement dans `main.py` (import / lifespan / configuration) |
| `utilities` (sélection multiple) | CORS, Rate-Limiting, Pagination, WebSocket, None | CORS : aucun (intégré à FastAPI) · Rate-Limiting : `slowapi` · Pagination : `fastapi-pagination` · WebSocket : `websockets` | CORS et Rate-Limiting sont câblés directement dans `main.py` ; Pagination ajoute `<pkg>/features/pagination.py`, WebSocket ajoute `<pkg>/features/websocket.py` |
| `migrations` | Alembic, None | Alembic : `alembic` | `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, une révision de référence `alembic/versions/<id>_initial.py`, `scripts/migrate.sh` — uniquement lorsque l'axe base de données est une base SQL |
| `tooling` (sélection multiple) | ruff, pre-commit, github-actions, devcontainer, makefile, None | ruff : `ruff` · pre-commit : `pre-commit` · github-actions / devcontainer / makefile : aucun | ruff fusionne un bloc `[tool.ruff]` dans `pyproject.toml` (ou écrit `ruff.toml` pour les projets `pip`) ; pre-commit écrit `.pre-commit-config.yaml` ; github-actions écrit `.github/workflows/test.yml` ; devcontainer écrit `.devcontainer/devcontainer.json` ; makefile écrit `Makefile` |
| `logging` | structured, None | Aucun (uniquement `logging` + `json` de la bibliothèque standard) | `<pkg>/logging_config.py` (journalisation JSON structurée + middleware d'identifiant de requête), câblé dans `main.py` |

Quelle que soit la sélection, chaque projet généré reçoit les points d'extrémité `/health` et `/ready` dans `main.py`, et `--dry-run` affiche exactement cet ensemble de fichiers avant toute écriture.

#### Exemples

<div class="termy">

```console
$ fastkit init
Enter the project name: my-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome API

Select stack (minimal, standard, full): standard
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-api' has been created successfully!
```

</div>

#### Structure générée

Crée un projet avec cette structure :

```
my-api/
├── .venv/                    # Environnement virtuel
├── src/
│   ├── __init__.py
│   ├── main.py              # Application FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # Regroupement des routeurs API
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── items.py     # Exemple de route
│   ├── crud/
│   │   ├── __init__.py
│   │   └── items.py         # Opérations CRUD
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── items.py         # Schémas Pydantic
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Données de test
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

### `addroute`

Ajouter une nouvelle route d'API à un projet FastAPI existant.

#### Syntaxe

```console
$ fastkit addroute ROUTE_NAME [PROJECT_DIR] [OPTIONS]
```

#### Arguments

| Argument | Description | Requis |
|----------|-------------|----------|
| `ROUTE_NAME` | Nom de la nouvelle route (pluriel recommandé) | Oui |
| `PROJECT_DIR` | Répertoire du projet sous votre espace de travail (par défaut `.`, le répertoire courant) | Non |

#### Options

| Option | Description | Défaut |
|--------|-------------|---------|
| `--help` | Afficher l'aide de la commande | - |

#### Exemples

<div class="termy">

```console
$ cd my-api
$ fastkit addroute users
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-api                                   │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-api                                 │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-api'
```

</div>

Vous pouvez aussi cibler un projet sous votre espace de travail par son nom sans vous déplacer avec `cd` :

<div class="termy">

```console
$ fastkit addroute users my-api
```

</div>

#### Fichiers générés

Crée ces fichiers dans le projet :

- `src/api/routes/users.py` — gestionnaires de route
- `src/crud/users.py` — opérations CRUD
- `src/schemas/users.py` — schémas Pydantic

Met aussi à jour `src/api/api.py` pour inclure le nouveau routeur.

#### Points d'extrémité générés

Crée des points d'extrémité CRUD complets :

| Méthode | Point d'extrémité | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | Récupérer tous les utilisateurs |
| `POST` | `/api/v1/users/` | Créer un nouvel utilisateur |
| `GET` | `/api/v1/users/{user_id}` | Récupérer un utilisateur précis |
| `PUT` | `/api/v1/users/{user_id}` | Mettre à jour un utilisateur |
| `DELETE` | `/api/v1/users/{user_id}` | Supprimer un utilisateur |

#### Où le code est inséré

`addroute` a besoin de deux informations sur le projet : où placer les nouveaux imports et où enregistrer le routeur. Les modèles et les points d'entrée générés marquent ces deux emplacements par des commentaires d'ancrage :

```python
# src/app/api/router.py
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

Conservez ces commentaires lorsque vous modifiez le fichier — `addroute` insère directement au-dessus de `# fastkit:imports` et de `# fastkit:routes`. Un projet qui les a perdus (ou qui a été généré avant l'existence des ancres) fonctionne toujours : fastkit se rabat sur une insertion fondée sur l'AST qui repère elle-même le bloc d'imports et les enregistrements de routeurs. Les ancres rendent simplement le résultat prévisible.

`addroute` lit aussi le bloc `[tool.fastapi-fastkit]` du projet pour localiser le point d'entrée : il fonctionne donc sur des dispositions que la seule analyse du disque classerait mal.

### `startdemo`

Créer un projet FastAPI à partir d'un modèle prêt à l'emploi.

#### Syntaxe

```console
$ fastkit startdemo [OPTIONS]
```

#### Options

| Option | Description | Défaut |
|--------|-------------|---------|
| `--project-name` | Nom du projet (demandé s'il est omis) | - |
| `--author` | Nom de l'auteur (demandé s'il est omis) | - |
| `--author-email` | E-mail de l'auteur (demandé s'il est omis) | - |
| `--description` | Description du projet (demandée si elle est omise) | - |
| `--package-manager` | Gestionnaire de paquets à utiliser (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Afficher les fichiers et paquets qui seraient créés, sans rien écrire | désactivé |
| `--no-venv` | Ignorer la création de l'environnement virtuel (implique `--no-install`) | désactivé |
| `--no-install` | Ignorer l'installation des dépendances | désactivé |
| `--yes` / `-y` | Ne pas demander de confirmation avant d'écraser des fichiers existants lors d'un déploiement du projet sur place | désactivé |
| `--help` | Afficher l'aide de la commande | - |

Comme `init`, `startdemo` refuse de s'exécuter lorsque le répertoire du projet cible existe déjà (`Error: Project '{name}' already exists.`). `--dry-run` fait exception : comme il n'écrit jamais sur le disque, il peut toujours viser un nom qui possède déjà un répertoire. Consultez [Déploiement sur place et confirmation d'écrasement](#deploiement-sur-place-et-confirmation-decrasement-yes-y) ci-dessus pour savoir ce que fait `--yes` lors d'un déploiement dans l'espace de travail courant.

#### Invites interactives

La commande `startdemo` vous demandera :

1. **Nom du projet** : nom de répertoire pour le nouveau projet
2. **Nom de l'auteur** : informations sur l'auteur du paquet
3. **E-mail de l'auteur** : adresse de contact
4. **Description du projet** : brève description
5. **Sélection du gestionnaire de paquets** : choisir parmi pip, uv, pdm ou poetry (à moins de l'avoir spécifié avec `--package-manager`)

#### Modèles disponibles

| Modèle | Description | Fonctionnalités |
|----------|-------------|----------|
| `fastapi-default` | Projet FastAPI simple | CRUD basique, données factices |
| `fastapi-domain-starter` | Starter orienté domaine | Un dossier par concept métier, `/health` |
| `fastapi-auth-jwt` | Authentification JWT | Rotation accès/rafraîchissement, argon2id, rôles et portées, Alembic |
| `fastapi-sqlmodel` | Persistance asynchrone SQLModel | SQLModel + SQLAlchemy asynchrone, Alembic, CRUD générique, pagination |
| `fastapi-llm-agent` | Agent Claude en streaming | Streaming SSE, boucle d'appels d'outils, mémoire de conversation |
| `fastapi-custom-response` | Système de réponses personnalisées | Réponses personnalisées, pagination |
| `fastapi-psql-orm` | API FastAPI avec PostgreSQL | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-mcp` | Serveur Model Context Protocol | Intégration MCP |
| `fastapi-single-module` | Bac à sable monofichier | Un seul module, sans frontières de package |
| `fastapi-empty` | Projet FastAPI minimal | Configuration minimale |
| `fastapi-async-crud` | *(obsolète)* API asynchrone de gestion d'items | Remplacé par `fastapi-sqlmodel` |
| `fastapi-dockerized` | *(obsolète)* API FastAPI dockerisée | L'outillage Docker est désormais fourni avec les modèles plus récents |

Les modèles obsolètes génèrent toujours des projets fonctionnels ; ils ne sont simplement plus des points de départ recommandés. Consultez [Quel starter choisir ?](choosing-a-starter.md).

#### Exemples

<div class="termy">

```console
$ fastkit startdemo fastapi-psql-orm
Enter the project name: my-blog
Enter the author name: Jane Smith
Enter the author email: jane@example.com
Enter the project description: Blog API with PostgreSQL

Select package manager (pip, uv, pdm, poetry) [uv]: poetry
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog' from 'fastapi-psql-orm' has been created!
```

</div>

### `runserver`

Démarrer le serveur de développement FastAPI.

#### Syntaxe

```console
$ fastkit runserver [OPTIONS]
```

#### Options

| Option | Court | Description | Défaut |
|--------|-------|-------------|---------|
| `--host` | `-h` | Hôte sur lequel se lier | `127.0.0.1` |
| `--port` | `-p` | Port sur lequel se lier | `8000` |
| `--reload` | `-r` | Activer le rechargement automatique | `True` |
| `--workers` | `-w` | Nombre de workers | `1` |
| `--help` | | Afficher l'aide de la commande | - |

#### Exemples

<div class="termy">

```console
# Utilisation de base (paramètres par défaut)
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000

# Hôte et port personnalisés
$ fastkit runserver --host 0.0.0.0 --port 8080
INFO:     Uvicorn running on http://0.0.0.0:8080

# Désactiver le rechargement automatique
$ fastkit runserver --no-reload
INFO:     Uvicorn running on http://127.0.0.1:8000

# Plusieurs workers (production)
$ fastkit runserver --workers 4
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

#### Prérequis

- Doit être exécuté depuis un répertoire de projet FastAPI
- Le projet doit exposer une app FastAPI — résolue à partir de `[tool.fastapi-fastkit].app_module` lorsqu'il est présent, sinon découverte en recherchant `main.py`
- L'environnement virtuel doit être activé

Si ni le point d'entrée enregistré ni la recherche ne trouvent de module, `runserver` signale qu'il n'a pas trouvé `main.py` et s'arrête.

### `list-templates`

Lister tous les modèles de projet FastAPI disponibles.

#### Syntaxe

```console
$ fastkit list-templates [OPTIONS]
```

#### Options

| Option | Description | Défaut |
|--------|-------------|---------|
| `--help` | Afficher l'aide de la commande | - |

#### Exemples

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-custom-response │ Async Item Management API with    │
│                         │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI Item           │
│                         │ Management API                    │
│ fastapi-empty           │ No description                    │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-psql-orm        │ Dockerized FastAPI Item           │
│                         │ Management API with PostgreSQL    │
│ fastapi-default         │ Simple FastAPI Project            │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

## Métadonnées du projet (`[tool.fastapi-fastkit]`)

Chaque projet généré par fastkit enregistre la façon dont il a été produit, dans son propre `pyproject.toml` :

```toml
[tool.fastapi-fastkit]
managed = true
version = "1.4.0"
template = "fastapi-domain-starter"
preset = "domain-starter"
package_manager = "uv"
app_module = "src.app.main:app"
features = ["database:PostgreSQL", "authentication:JWT"]
```

| Clé | Signification |
|---|---|
| `managed` | Toujours `true` ; marque le projet comme géré par fastkit |
| `version` | La version de fastkit qui a généré le projet |
| `template` | Le modèle `startdemo`, ou le modèle de base du préréglage |
| `preset` | Le préréglage d'architecture de `init --interactive` (omis sinon) |
| `package_manager` | Le gestionnaire utilisé pour construire l'environnement |
| `app_module` | Le point d'entrée uvicorn `module:attr` |
| `features` | Liste plate `"<category>:<choice>"` des sélections interactives |

Ce bloc est l'unique source de vérité pour le point d'entrée du projet : `fastkit runserver` y lit `app_module` avant de se rabattre sur l'analyse de l'arborescence, `fastkit addroute` l'utilise pour localiser l'application, et les Dockerfiles générés utilisent la même valeur dans leur `CMD`.

Le bloc est écrit à la toute fin de la génération — les gestionnaires de paquets réécrivent `pyproject.toml` pendant la résolution des dépendances, il doit donc être apposé après — et une régénération ultérieure le remplace au lieu d'en ajouter une seconde copie. Modifier `app_module` à la main est la manière prise en charge d'indiquer à fastkit une disposition que vous avez vous-même réorganisée.

## Variables d'environnement

FastAPI-fastkit prend en compte ces variables d'environnement :

| Variable | Description | Défaut |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | Répertoire de configuration | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Répertoire de modèles personnalisés | Modèles intégrés |
| `FASTKIT_LOG_LEVEL` | Niveau de journalisation | `INFO` |
| `FASTKIT_SUBPROCESS_TIMEOUT` | Remplace tous les délais d'expiration des sous-processus du gestionnaire de paquets, en secondes | par opération (30 / 120 / 900) |

Les appels au gestionnaire de paquets sont bornés individuellement afin qu'un processus enfant bloqué ne puisse jamais figer le CLI : 30 secondes pour une vérification de disponibilité, 120 pour la création d'un environnement virtuel, 900 pour l'installation des dépendances. `FASTKIT_SUBPROCESS_TIMEOUT` remplace ces trois valeurs par une seule — utile sur un réseau lent, ou pour échouer rapidement en CI. Une valeur qui n'est pas un entier positif est ignorée.

```console
$ export FASTKIT_SUBPROCESS_TIMEOUT=1800
$ fastkit startdemo fastapi-sqlmodel
```

### Exemples

<div class="termy">

```console
# Répertoire de configuration personnalisé
$ export FASTKIT_CONFIG_DIR=~/my-fastkit-config
$ fastkit init

# Répertoire de templates personnalisé
$ export FASTKIT_TEMPLATES_DIR=~/my-templates
$ fastkit list-templates

# Journalisation en mode debug
$ export FASTKIT_LOG_LEVEL=DEBUG
$ fastkit init
```

</div>

## Fichiers de configuration

FastAPI-fastkit peut utiliser des fichiers de configuration pour les paramètres par défaut.

### Emplacement du fichier de configuration

1. `$FASTKIT_CONFIG_DIR/config.yaml` (si `FASTKIT_CONFIG_DIR` est défini)
2. `~/.fastkit/config.yaml` (par défaut)
3. `./fastkit.yaml` (spécifique au projet)

### Format de la configuration

```yaml
# ~/.fastkit/config.yaml
default:
  author:
    name: "Votre nom"
    email: "your.email@example.com"

  project:
    stack: "standard"
    create_venv: true
    install_deps: true

  server:
    host: "127.0.0.1"
    port: 8000
    reload: true

templates:
  custom_dir: "~/my-templates"

logging:
  level: "INFO"
  file: "~/.fastkit/logs/fastkit.log"
```

## Flux de travail courants

### 1. Créer un nouveau projet

<div class="termy">

```console
# Créer un nouveau projet
$ fastkit init
# Suivez les invites...

# Aller dans le projet
$ cd my-awesome-api

# Activer l'environnement virtuel
$ source .venv/bin/activate

# Démarrer le serveur de développement
$ fastkit runserver
```

</div>

### 2. Ajouter des fonctionnalités à un projet existant

<div class="termy">

```console
# Ajouter plusieurs routes (le nom du projet en deuxième argument positionnel vise le projet de l'espace de travail)
$ fastkit addroute users my-api
$ fastkit addroute products my-api
$ fastkit addroute orders my-api

# Tester l'API
$ fastkit runserver
# Ouvrir ensuite http://127.0.0.1:8000/docs
```

</div>

### 3. Utiliser des modèles pour des projets complexes

<div class="termy">

```console
# Lister les templates disponibles
$ fastkit list-templates

# Créer un projet à partir d'un template
$ fastkit startdemo
# Choisir fastapi-psql-orm pour un projet avec base de données

# Préparer la base de données (pour le template PostgreSQL)
$ cd my-project
$ docker-compose up -d postgres
$ source .venv/bin/activate
$ alembic upgrade head
$ fastkit runserver
```

</div>

## Dépannage

### Commande introuvable

Si la commande `fastkit` est introuvable :

1. **Vérifiez l'installation :**
   <div class="termy">
   ```console
   $ pip show fastapi-fastkit
   ```
   </div>

2. **Réinstallez si nécessaire :**
   <div class="termy">
   ```console
   $ pip uninstall fastapi-fastkit
   $ pip install fastapi-fastkit
   ```
   </div>

3. **Vérifiez le PATH :**
   <div class="termy">
   ```console
   $ which fastkit
   ```
   </div>

### Problèmes d'environnement virtuel

Si la création de l'environnement virtuel échoue :

1. **Vérifiez la version de Python :**
   <div class="termy">
   ```console
   $ python --version  # Doit être en 3.12+
   ```
   </div>

2. **Vérifiez le module venv :**
   <div class="termy">
   ```console
   $ python -m venv --help
   ```
   </div>

3. **Environnement virtuel manuel :**
   <div class="termy">
   ```console
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ```
   </div>

### Le serveur ne démarre pas

Si `fastkit runserver` échoue :

1. **Vérifiez que vous êtes dans le répertoire du projet**
2. **Vérifiez que `src/main.py` existe**
3. **Activez l'environnement virtuel :**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

4. **Recherchez les erreurs de syntaxe :**
   <div class="termy">
   ```console
   $ python -c "from src.main import app"
   ```
   </div>

### Port déjà utilisé

Si le port 8000 est occupé :

<div class="termy">

```console
# Utiliser un autre port
$ fastkit runserver --port 8080

# Ou arrêter le processus déjà en cours
$ lsof -ti:8000 | xargs kill -9
```

</div>

## Utilisation avancée

### Modèles personnalisés

Vous pouvez créer des modèles personnalisés en :

1. **Créant un répertoire de modèle :**
   ```
   my-template/
   ├── src/
   │   └── main.py-tpl
   ├── requirements.txt-tpl
   └── setup.py-tpl
   ```

2. **Définissant la variable d'environnement :**
   <div class="termy">
   ```console
   $ export FASTKIT_TEMPLATES_DIR=~/my-templates
   ```
   </div>

3. **Utilisant le modèle personnalisé :**
   <div class="termy">
   ```console
   $ fastkit startdemo
   # Your custom templates will appear in the list
   ```
   </div>

### Scripts avec FastAPI-fastkit

Vous pouvez utiliser FastAPI-fastkit dans des scripts :

```bash
#!/bin/bash
# create-microservices.sh

for service in users products orders; do
    echo "Creating $service service..."
    fastkit init <<EOF
$service-service
Company Team
team@company.com
$service microservice
minimal
y
EOF

    cd "$service-service"
    fastkit addroute "$service"
    cd ..
done
```

### Intégration avec CI/CD

Exemple de flux GitHub Actions :

```yaml
name: Test FastAPI-fastkit Project

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install FastAPI-fastkit
      run: pip install fastapi-fastkit

    - name: Create test project
      run: |
        fastkit init <<EOF
        test-project
        CI
        ci@example.com
        Test project
        standard
        y
        EOF

    - name: Test project
      run: |
        cd test-project
        source .venv/bin/activate
        python -m pytest
```

## Prise en charge des gestionnaires de paquets

FastAPI-fastkit prend en charge plusieurs gestionnaires de paquets Python, ce qui vous permet de choisir celui qui correspond le mieux à votre flux de travail.

### Gestionnaires de paquets pris en charge

| Gestionnaire | Description | Fichier de dépendances | Idéal pour |
|---------|-------------|----------------|----------|
| **UV** (par défaut) | Gestionnaire de paquets Python rapide | `pyproject.toml` | La vitesse et la performance |
| **PDM** | Gestion moderne des dépendances Python | `pyproject.toml` | La résolution avancée des dépendances |
| **Poetry** | Gestion des dépendances et packaging Python | `pyproject.toml` | Les flux de travail basés sur Poetry |
| **PIP** | Gestionnaire de paquets Python standard | `requirements.txt` | Le développement Python traditionnel |

### Spécifier le gestionnaire de paquets

#### Configuration globale

Vous pouvez définir votre gestionnaire de paquets préféré pour tous les projets :

```console
# En passant par les options de ligne de commande
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

#### Sélection spécifique au projet

Chaque projet peut utiliser un gestionnaire de paquets différent. Le choix est fait pendant la création du projet et affecte :

- **Le format du fichier de dépendances** : chaque gestionnaire crée les fichiers appropriés
- **La gestion de l'environnement virtuel** : différentes méthodes d'activation
- **L'installation des dépendances** : commandes spécifiques au gestionnaire

### Fonctionnalités des gestionnaires de paquets

#### UV (par défaut)
- **Rapide** : basé sur Rust, résolution de dépendances extrêmement rapide
- **Compatible** : remplacement direct pour pip et pip-tools
- **Moderne** : prise en charge des métadonnées de projet PEP 621

<div class="termy">

```console
$ fastkit init --package-manager uv
# Crée un `pyproject.toml` configuré pour UV
```

</div>

#### PDM
- **Moderne** : prise en charge de PEP 582 et PEP 621
- **Avancé** : résolution sophistiquée des dépendances
- **Flexible** : multiples dispositions de projet

<div class="termy">

```console
$ fastkit init --package-manager pdm
# Crée un `pyproject.toml` configuré pour PDM
```

</div>

#### Poetry
- **Établi** : mature et largement adopté
- **Intégré** : prise en charge du build et de la publication
- **Lockfile** : poetry.lock pour des builds reproductibles

<div class="termy">

```console
$ fastkit init --package-manager poetry
# Crée un `pyproject.toml` configuré pour Poetry
```

</div>

#### PIP
- **Standard** : intégré à Python
- **Compatible** : fonctionne partout
- **Simple** : gestion directe des dépendances

<div class="termy">

```console
$ fastkit init --package-manager pip
# Crée un `requirements.txt`
```

</div>

### Travailler avec les projets

Après avoir créé un projet avec un gestionnaire de paquets spécifique :

#### Projets UV
```console
cd my-project
uv sync         # Installer les dépendances
uv add requests # Ajouter une nouvelle dépendance
uv run pytest   # Exécuter des commandes dans l'environnement
```

#### Projets PDM
```console
cd my-project
pdm install      # Installer les dépendances
pdm add requests # Ajouter une nouvelle dépendance
pdm run pytest   # Exécuter des commandes dans l'environnement
```

#### Projets Poetry
```console
cd my-project
poetry install      # Installer les dépendances
poetry add requests # Ajouter une nouvelle dépendance
poetry run pytest   # Exécuter des commandes dans l'environnement
```

#### Projets PIP
```console
cd my-project
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install requests
pytest
```

## Étapes suivantes

Maintenant que vous comprenez le CLI :

1. **[Démarrage rapide](quick-start.md)** : essayer les commandes en pratique
2. **[Votre premier projet](../tutorial/first-project.md)** : construire une application complète
3. **[Contribution](../contributing/development-setup.md)** : contribuer à FastAPI-fastkit

!!! tip "Astuces CLI"
    - Utilisez `--help` avec n'importe quelle commande pour une aide détaillée
    - Configurez les paramètres par défaut pour accélérer la création de projet
    - Utilisez les modèles pour des configurations de projet complexes
    - Combinez les commandes pour créer des flux de travail puissants

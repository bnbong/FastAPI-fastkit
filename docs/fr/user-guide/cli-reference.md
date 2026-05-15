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
| `--package-manager` | Gestionnaire de paquets à utiliser (pip, uv, pdm, poetry) | uv |
| `--help` | Afficher l'aide de la commande | - |

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

### `startdemo`

Créer un projet FastAPI à partir d'un modèle prêt à l'emploi.

#### Syntaxe

```console
$ fastkit startdemo [OPTIONS]
```

#### Options

| Option | Description | Défaut |
|--------|-------------|---------|
| `--package-manager` | Gestionnaire de paquets à utiliser (pip, uv, pdm, poetry) | uv |
| `--help` | Afficher l'aide de la commande | - |

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
| `fastapi-async-crud` | API asynchrone de gestion d'items | Async/await, performance |
| `fastapi-custom-response` | Système de réponses personnalisées | Réponses personnalisées, pagination |
| `fastapi-dockerized` | API FastAPI dockerisée | Docker, prêt pour la production |
| `fastapi-psql-orm` | API FastAPI avec PostgreSQL | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-empty` | Projet FastAPI minimal | Configuration minimale |

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
- Le projet doit avoir `src/main.py` avec une app FastAPI
- L'environnement virtuel doit être activé

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

## Variables d'environnement

FastAPI-fastkit prend en compte ces variables d'environnement :

| Variable | Description | Défaut |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | Répertoire de configuration | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Répertoire de modèles personnalisés | Modèles intégrés |
| `FASTKIT_LOG_LEVEL` | Niveau de journalisation | `INFO` |

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

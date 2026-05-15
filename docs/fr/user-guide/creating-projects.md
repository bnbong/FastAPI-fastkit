# Créer des projets

Un guide détaillé sur la création de différents types de projets FastAPI avec FastAPI-fastkit.

## Création de projet basique

### 1. Création de projet en mode interactif

La façon la plus basique de créer un projet en mode interactif :

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Awesome FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-api          │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ Awesome FastAPI project │
└──────────────┴─────────────────────────┘
```

</div>

### 2. Sélection de la pile

Choisissez la pile de dépendances à inclure dans votre projet :

#### Pile MINIMAL (par défaut)

Le projet FastAPI le plus basique :

- `fastapi` — framework FastAPI
- `uvicorn` — serveur ASGI
- `pydantic` — validation des données
- `pydantic-settings` — gestion des paramètres

**Idéal pour :**

- Apprendre FastAPI
- API simples
- Prototypes
- Microservices

#### Pile STANDARD

Inclut la prise en charge des bases de données et des tests :

- Toutes les dépendances MINIMAL
- `sqlalchemy` — ORM pour les opérations en base de données
- `alembic` — migrations de base de données
- `pytest` — framework de test

**Idéal pour :**

- La plupart des applications web
- API avec stockage en base de données
- Applications prêtes pour la production
- Projets en équipe

#### Pile FULL

Environnement de développement complet :

- Toutes les dépendances STANDARD
- `redis` — cache et stockage de session
- `celery` — traitement des tâches en arrière-plan

**Idéal pour :**

- Applications de grande taille
- Exigences de haute performance
- Logique métier complexe
- Applications d'entreprise

## Options de projet avancées

### Configuration personnalisée du projet

Vous pouvez personnaliser votre projet lors de la création :

<div class="termy">

```console
$ fastkit init
Enter the project name: advanced-api
Enter the author name: Development Team
Enter the author email: dev@company.com
Enter the project description: Advanced FastAPI application with custom features

# Choisissez la pile STANDARD pour le support de base de données
Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Explication de la structure du projet

Lorsque vous créez un projet, FastAPI-fastkit génère cette structure :

```
my-awesome-api/
├── .venv/                      # Environnement virtuel
├── src/                        # Code source
│   ├── __init__.py
│   ├── main.py                # Point d'entrée de l'application
│   ├── core/                  # Configuration centrale
│   │   ├── __init__.py
│   │   └── config.py         # Paramètres et configuration
│   ├── api/                   # Couche API
│   │   ├── __init__.py
│   │   ├── api.py            # Routeur principal de l'API
│   │   └── routes/           # Modules de routes individuels
│   │       ├── __init__.py
│   │       └── items.py      # Endpoints d'exemple pour items
│   ├── crud/                  # Opérations sur les données
│   │   ├── __init__.py
│   │   └── items.py          # Opérations CRUD pour items
│   ├── schemas/               # Modèles Pydantic
│   │   ├── __init__.py
│   │   └── items.py          # Schémas de validation des données
│   └── mocks/                 # Données de test
│       ├── __init__.py
│       └── mock_items.json   # Données d'exemple pour le développement
├── tests/                     # Suite de tests
│   ├── __init__.py
│   ├── conftest.py           # Configuration des tests
│   └── test_items.py         # Tests d'exemple
├── scripts/                   # Scripts utilitaires
│   ├── test.sh               # Lancer les tests
│   ├── coverage.sh           # Couverture de tests
│   └── lint.sh               # Vérification du code
├── requirements.txt           # Dépendances Python
├── setup.py                  # Configuration du paquet
└── README.md                 # Documentation du projet
```

### 3. Sélection du gestionnaire de paquets

FastAPI-fastkit prend en charge plusieurs gestionnaires de paquets Python. Choisissez celui qui correspond le mieux à votre flux de développement :

#### Gestionnaires de paquets disponibles

<div class="termy">

```console
Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

Chaque gestionnaire de paquets a ses atouts :

#### UV (par défaut — recommandé)

**Gestionnaire de paquets rapide basé sur Rust**

- ⚡ **Ultra-rapide** : 10 à 100 fois plus rapide que pip
- 🔧 **Remplacement direct** : compatible avec les flux pip
- 📦 **Moderne** : prise en charge complète de PEP 621
- 🛠️ **Fiable** : résolution déterministe

**Fichiers générés :**

- `pyproject.toml` (format PEP 621)
- `uv.lock` (fichier de verrouillage)

**Utilisation après création :**
```console
cd my-project
uv sync              # Installer les dépendances
uv add requests      # Ajouter une dépendance
uv run pytest       # Lancer les tests
```

#### PDM

**Gestion moderne des dépendances Python**

- 🚀 **Moderne** : prise en charge de PEP 582 et PEP 621
- 🧠 **Intelligent** : résolution avancée des dépendances
- 💼 **Professionnel** : prise en charge des espaces de travail et des projets multiples
- 📊 **Analytique** : outils d'analyse des dépendances

**Fichiers générés :**

- `pyproject.toml` (format PEP 621)
- `pdm.lock` (fichier de verrouillage)

**Utilisation après création :**
```console
cd my-project
pdm install          # Installer les dépendances
pdm add requests     # Ajouter une dépendance
pdm run pytest      # Lancer les tests
```

#### Poetry

**Gestion mature des dépendances et packaging**

- ✅ **Établi** : mature et largement adopté
- 📦 **Intégré** : prise en charge du build et de la publication
- 🔒 **Reproductible** : poetry.lock pour des versions exactes
- 🏗️ **Complet** : gestion complète du cycle de vie d'un projet

**Fichiers générés :**

- `pyproject.toml` (format Poetry)
- `poetry.lock` (fichier de verrouillage)

**Utilisation après création :**
```console
cd my-project
poetry install       # Installer les dépendances
poetry add requests  # Ajouter une dépendance
poetry run pytest   # Lancer les tests
```

#### PIP

**Gestionnaire de paquets Python standard**

- 🏠 **Intégré** : livré avec Python
- 🌍 **Universel** : fonctionne partout
- 📚 **Familier** : la plupart des développeurs le connaissent
- 🔧 **Simple** : flux de travail direct

**Fichiers générés :**

- `requirements.txt`

**Utilisation après création :**
```console
cd my-project
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install requests
pytest
```

#### Spécifier le gestionnaire de paquets

Vous pouvez indiquer votre gestionnaire de paquets préféré :

**Sélection interactive (par défaut) :**
```console
$ fastkit init
# ... invite de sélection du gestionnaire de paquets
```

**Option en ligne de commande :**
```console
$ fastkit init --package-manager poetry
$ fastkit init --package-manager pdm
$ fastkit init --package-manager uv
$ fastkit init --package-manager pip
```

### Comprendre chaque répertoire

#### Répertoire `src/`

Contient tout le code source de votre application selon une **organisation en `src/`**, une bonne pratique courante pour le packaging Python.

#### Module `core/`

- **config.py** : paramètres de l'application, variables d'environnement et configuration
- Centralise toute la gestion de la configuration
- Prend en charge le fichier `.env` pour les paramètres spécifiques à l'environnement

#### Module `api/`

- **api.py** : routeur principal d'API qui regroupe tous les sous-routeurs
- **routes/** : modules de routes individuels pour différentes ressources
- Séparation propre des préoccupations pour les différents points d'extrémité de l'API

#### Module `crud/`

- Opérations de base de données et logique métier
- Opérations **C**reate, **R**ead, **U**pdate, **D**elete
- Couche d'abstraction entre les routes d'API et le stockage des données

#### Module `schemas/`

- Modèles Pydantic pour la validation des données
- Schémas de requête / réponse
- Définitions de types et modèles de données

#### Répertoire `tests/`

- Suite de tests complète pour votre application
- Inclut des tests unitaires et d'intégration
- Préconfiguré avec pytest

## Comparaison des piles

| Fonctionnalité | MINIMAL | STANDARD | FULL |
|---------|---------|----------|------|
| FastAPI & Uvicorn | ✅ | ✅ | ✅ |
| Validation des données | ✅ | ✅ | ✅ |
| Prise en charge des bases de données | ❌ | ✅ | ✅ |
| Migrations | ❌ | ✅ | ✅ |
| Framework de test | ❌ | ✅ | ✅ |
| Mise en cache (Redis) | ❌ | ❌ | ✅ |
| Tâches en arrière-plan | ❌ | ❌ | ✅ |
| **Idéal pour** | Apprentissage, API simples | La plupart des applications | Entreprise, applications complexes |

## Exemples de création de projet

### Exemple 1 : projet d'apprentissage

<div class="termy">

```console
$ fastkit init
Enter the project name: fastapi-learning
Enter the author name: Student
Enter the author email: student@example.com
Enter the project description: Learning FastAPI basics

Select stack (minimal, standard, full): minimal
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Exemple 2 : API e-commerce

<div class="termy">

```console
$ fastkit init
Enter the project name: ecommerce-api
Enter the author name: E-commerce Team
Enter the author email: team@ecommerce.com
Enter the project description: E-commerce platform API

Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Exemple 3 : application haute performance

<div class="termy">

```console
$ fastkit init
Enter the project name: enterprise-api
Enter the author name: Enterprise Team
Enter the author email: enterprise@company.com
Enter the project description: High-performance enterprise API

Select stack (minimal, standard, full): full
Do you want to proceed with project creation? [y/N]: y
```

</div>

## Après la création du projet

### 1. Activer l'environnement virtuel

<div class="termy">

```console
$ cd my-awesome-api
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

### 2. Vérifier l'installation

<div class="termy">

```console
$ pip list
Package         Version
fastapi         0.104.1
uvicorn         0.24.0
pydantic        2.5.0
...
```

</div>

### 3. Démarrer le développement

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

## Gestion de la configuration

### Variables d'environnement

Votre projet prend en charge la configuration via des fichiers `.env` :

Créez un fichier `.env` à la racine de votre projet :

```env
# .env
APP_NAME=My Awesome API
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### Configuration dans le code

Le `src/core/config.py` généré charge automatiquement ces variables :

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Options de personnalisation

### Ajouter des dépendances personnalisées

Après la création du projet, vous pouvez ajouter d'autres dépendances :

<div class="termy">

```console
$ pip install requests httpx python-jose
$ pip freeze > requirements.txt
```

</div>

### Modifier la structure du projet

La structure générée suit les bonnes pratiques, mais vous pouvez l'adapter :

- Ajouter de nouveaux modules dans `src/`
- Créer des fichiers de routes supplémentaires dans `api/routes/`
- Étendre les opérations CRUD dans `crud/`
- Ajouter d'autres schémas dans `schemas/`

## Bonnes pratiques

### 1. Environnement virtuel

Utilisez toujours des environnements virtuels pour isoler les dépendances du projet :

```bash
# Create project with virtual environment
$ fastkit init  # Automatically creates .venv/

# Activate when working
$ source .venv/bin/activate
```

### 2. Gestion de versions

Initialisez un dépôt git après la création du projet :

<div class="termy">

```console
$ cd my-awesome-api
$ git init
$ git add .
$ git commit -m "Initial commit - FastAPI project setup"
```

</div>

### 3. Configuration de l'environnement

- Utilisez des fichiers `.env` pour le développement local
- Utilisez des variables d'environnement pour la production
- Ne committez jamais de données sensibles dans le contrôle de version

### 4. Tests

Profitez du framework de test inclus :

<div class="termy">

```console
$ python -m pytest
$ bash scripts/test.sh
```

</div>

## Étapes suivantes

Après avoir créé votre projet :

1. **[Ajouter des routes](adding-routes.md)** : apprenez à ajouter de nouveaux points d'extrémité d'API
2. **[Référence CLI](cli-reference.md)** : maîtrisez toutes les commandes disponibles
3. **[Tutoriel Votre premier projet](../tutorial/first-project.md)** : construire une application complète

!!! tip "Astuces pour la création de projet"
    - Choisissez la pile qui correspond aux besoins de votre projet
    - Commencez par MINIMAL pour apprendre, utilisez STANDARD pour la plupart des projets
    - La structure du projet est conçue pour l'évolutivité et la maintenabilité
    - Tout le code généré suit les bonnes pratiques de FastAPI

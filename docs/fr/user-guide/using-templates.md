# Utiliser les modèles

FastAPI-fastkit propose des modèles de projet prêts à l'emploi pour vous aider à démarrer rapidement avec différentes piles techniques.

## Modèles disponibles

Consultez les modèles disponibles avec la commande `list-templates` :

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

## Descriptions des modèles

### 1. `fastapi-default`

**Projet FastAPI simple**

- Configuration FastAPI basique avec les fonctionnalités essentielles
- Gestion d'items avec des données factices
- Idéal pour apprendre et pour les API simples
- Inclut les opérations CRUD de base

**Idéal pour :**

- Débutants en FastAPI
- API web simples
- Apprentissage et prototypage

### 2. `fastapi-async-crud`

**Serveur d'API asynchrone de gestion d'items**

- Application FastAPI entièrement asynchrone
- Opérations CRUD avancées avec async/await
- Meilleure performance pour les opérations d'E/S
- Stockage de données factices avec motifs asynchrones

**Idéal pour :**

- Applications haute performance
- Opérations intensives en E/S
- Développement Python asynchrone moderne

### 3. `fastapi-custom-response`

**API asynchrone de gestion d'items avec système de réponse personnalisé**

- Modèles de réponse personnalisés et formatage
- Gestion avancée des erreurs
- Prise en charge de la pagination
- Codes d'état HTTP et réponses personnalisés

**Idéal pour :**

- API nécessitant des formats de réponse spécifiques
- Besoins avancés en gestion d'erreurs
- Logique métier personnalisée dans les réponses

### 4. `fastapi-dockerized`

**API FastAPI de gestion d'items conteneurisée avec Docker**

- Conteneurisation Docker complète
- Configuration de déploiement prête pour la production
- Builds Docker multi-étapes
- Configuration basée sur l'environnement

**Idéal pour :**

- Déploiements en production
- Environnements conteneurisés
- Pipelines DevOps et CI/CD

### 5. `fastapi-psql-orm`

**API FastAPI conteneurisée de gestion d'items avec PostgreSQL**

- Intégration de la base de données PostgreSQL
- ORM SQLAlchemy avec migrations Alembic
- Docker Compose pour le développement local
- Opérations CRUD complètes en base de données

**Idéal pour :**

- Applications pilotées par une base de données
- Stockage de données de qualité production
- Relations de données complexes

### 6. `fastapi-empty`

**Projet FastAPI minimal**

- Configuration FastAPI minimale
- Aucune fonctionnalité ajoutée à l'avance
- Page blanche pour du développement personnalisé

**Idéal pour :**

- Démarrer de zéro
- Dépendances minimales
- Exigences d'architecture personnalisée

## Créer un projet à partir d'un modèle

Utilisez la commande `startdemo` pour créer un projet à partir d'un modèle :

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Blog API with PostgreSQL

Available Templates:
           fastapi-default
┌─────────────┬──────────────────────┐
│ Description │ Simple FastAPI       │
│             │ Project              │
│ Stack       │ FastAPI, Uvicorn     │
│ Database    │ Mock Data            │
│ Features    │ Basic CRUD           │
└─────────────┴──────────────────────┘

           fastapi-psql-orm
┌─────────────┬──────────────────────┐
│ Description │ Dockerized FastAPI   │
│             │ Item Management API  │
│             │ with PostgreSQL      │
│ Stack       │ FastAPI, PostgreSQL, │
│             │ SQLAlchemy, Docker   │
│ Database    │ PostgreSQL           │
│ Features    │ Full ORM, Migrations │
└─────────────┴──────────────────────┘

Select template (fastapi-default, fastapi-async-crud, fastapi-custom-response, fastapi-dockerized, fastapi-psql-orm, fastapi-empty): fastapi-psql-orm

           Project Information
┌──────────────┬─────────────────────┐
│ Project Name │ my-blog-api         │
│ Author       │ John Doe            │
│ Author Email │ john@example.com    │
│ Description  │ Blog API with       │
│              │ PostgreSQL          │
└──────────────┴─────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ psycopg2-binary   │
│ Dependency 6 │ python-dotenv     │
│ Dependency 7 │ pytest            │
└──────────────┴───────────────────┘

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## Comparaison des fonctionnalités des modèles

| Fonctionnalité | Default | Async CRUD | Custom Response | Dockerized | PostgreSQL ORM | Empty |
|---------|---------|------------|-----------------|------------|----------------|-------|
| **FastAPI de base** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Données factices** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Support asynchrone** | Basique | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Réponses personnalisées** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Base de données** | Factice | Factice | Factice | Factice | PostgreSQL | Aucune |
| **ORM** | ❌ | ❌ | ❌ | ❌ | SQLAlchemy | ❌ |
| **Migrations** | ❌ | ❌ | ❌ | ❌ | Alembic | ❌ |
| **Tests** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Idéal pour** | Apprentissage | Performance | API personnalisées | Production | Applications avec base de données | Personnalisé |

## Configuration spécifique à chaque modèle

### Utiliser `fastapi-psql-orm`

Ce modèle inclut une configuration PostgreSQL complète. Après la création :

1. **Démarrer PostgreSQL avec Docker :**

<div class="termy">

```console
$ cd my-blog-api
$ docker-compose up -d postgres
Starting my-blog-api_postgres_1 ... done
```

</div>

2. **Exécuter les migrations de base de données :**

<div class="termy">

```console
$ source .venv/bin/activate
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> bedcdc35b64a, first alembic
```

</div>

3. **Démarrer le serveur d'API :**

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Utiliser `fastapi-dockerized`

Ce modèle offre un support Docker complet :

1. **Construire l'image Docker :**

<div class="termy">

```console
$ cd my-dockerized-api
$ docker build -t my-dockerized-api .
Successfully built abc123def456
Successfully tagged my-dockerized-api:latest
```

</div>

2. **Exécuter le conteneur :**

<div class="termy">

```console
$ docker run -p 8000:8000 my-dockerized-api
INFO:     Uvicorn running on http://0.0.0.0:8000
```

</div>

### Utiliser `fastapi-custom-response`

Ce modèle inclut une gestion avancée des réponses :

1. **Modèles de réponse personnalisés :**

```python
from src.helper.pagination import PaginatedResponse
from src.schemas.base import StandardResponse

@router.get("/", response_model=PaginatedResponse[Item])
def read_items(skip: int = 0, limit: int = 10):
    items = items_crud.get_multi(skip=skip, limit=limit)
    total = items_crud.count()

    return PaginatedResponse(
        data=items,
        total=total,
        page=skip // limit + 1,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=StandardResponse[Item])
def create_item(item: ItemCreate):
    new_item = items_crud.create(item)
    return StandardResponse(
        data=new_item,
        message="Item created successfully",
        status_code=201
    )
```

2. **Gestion d'erreurs améliorée :**

```python
from src.helper.exceptions import ItemNotFoundError, ValidationError

@router.get("/{item_id}", response_model=StandardResponse[Item])
def read_item(item_id: int):
    try:
        item = items_crud.get(item_id)
        return StandardResponse(data=item)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )
```

## Structure des projets de modèle

Chaque modèle suit une structure cohérente mais adaptée :

### Structure de `fastapi-default`
```
my-project/
├── src/
│   ├── main.py
│   ├── core/config.py
│   ├── api/
│   │   ├── api.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   └── mocks/mock_items.json
├── tests/
├── scripts/
└── requirements.txt
```

### Structure de `fastapi-psql-orm`
```
my-project/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── db.py
│   ├── api/
│   │   ├── api.py
│   │   ├── deps.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   └── utils/
├── tests/
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── requirements.txt
```

## Personnaliser les modèles

Après avoir créé un projet à partir d'un modèle, vous pouvez le personnaliser :

### 1. Ajouter de nouvelles routes

<div class="termy">

```console
$ fastkit addroute posts my-blog-api
$ fastkit addroute users my-blog-api
$ fastkit addroute comments my-blog-api
```

</div>

### 2. Modifier la configuration

Modifiez `src/core/config.py` selon vos besoins :

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings (for PostgreSQL templates)
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Ajouter des variables d'environnement

Créez un fichier `.env` à la racine de votre projet :

```env
# .env
PROJECT_NAME=My Blog API
VERSION=1.0.0
DEBUG=True

# Database (for PostgreSQL templates)
DATABASE_URL=postgresql://user:password@localhost:5432/myblogdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=myblogdb

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Tests des modèles

Chaque modèle est livré avec des tests préconfigurés :

<div class="termy">

```console
$ cd my-blog-api
$ source .venv/bin/activate
$ python -m pytest

======================== test session starts ========================
tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED
======================== 5 passed in 0.23s ========================
```

</div>

## Flux de développement avec les modèles

### 1. Choisir le bon modèle

- **Apprentissage / API simples** : `fastapi-default`
- **Haute performance** : `fastapi-async-crud`
- **Formats de réponse personnalisés** : `fastapi-custom-response`
- **Déploiement en production** : `fastapi-dockerized`
- **Applications avec base de données** : `fastapi-psql-orm`
- **Architecture personnalisée** : `fastapi-empty`

### 2. Créer et configurer

<div class="termy">

```console
$ fastkit startdemo
# Follow the prompts
$ cd your-project
$ source .venv/bin/activate
```

</div>

### 3. Développement

<div class="termy">

```console
# Démarrer le serveur de développement
$ fastkit runserver

# Exécuter les tests
$ python -m pytest

# Ajouter de nouvelles fonctionnalités
$ fastkit addroute new-resource your-project
```

</div>

### 4. Déploiement

Pour les modèles destinés à la production (`fastapi-dockerized`, `fastapi-psql-orm`) :

<div class="termy">

```console
# Build for production
$ docker build -t your-app .

# Deploy with Docker Compose
$ docker-compose up -d
```

</div>

## Bonnes pratiques

### 1. Choisir les modèles judicieusement

- Commencez par les modèles plus simples pour apprendre
- Utilisez les modèles avec base de données pour les applications pilotées par les données
- Utilisez les modèles Docker pour les déploiements en production

### 2. Gestion de l'environnement

- Utilisez toujours des fichiers `.env` pour la configuration
- Ne committez jamais de données sensibles dans le contrôle de version
- Utilisez des environnements différents pour développement / production

### 3. Stratégie de personnalisation

- Ajoutez de nouvelles routes avec `fastkit addroute`
- Modifiez le code existant pour l'adapter à votre logique métier
- Gardez la structure du projet organisée

### 4. Tests

- Exécutez les tests régulièrement pendant le développement
- Ajoutez des tests pour les nouvelles fonctionnalités que vous implémentez
- Utilisez la structure de tests fournie comme guide

## Dépannage

### Problèmes de connexion à la base de données (modèles PostgreSQL)

Si vous n'arrivez pas à vous connecter à PostgreSQL :

1. **Vérifiez que Docker tourne :**

   <div class="termy">
   ```console
   $ docker ps
   ```
   </div>

2. **Vérifiez le conteneur PostgreSQL :**

   <div class="termy">
   ```console
   $ docker-compose logs postgres
   ```
   </div>

3. **Vérifiez les variables d'environnement :**

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Échecs de build Docker

Si le build Docker échoue :

1. **Vérifiez la syntaxe du Dockerfile**
2. **Vérifiez que tous les fichiers sont présents**
3. **Vérifiez que le démon Docker tourne**

### Dépendances manquantes

Si vous obtenez des erreurs d'import :

1. **Activez l'environnement virtuel :**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

2. **Installez les dépendances :**
   <div class="termy">
   ```console
   $ pip install -r requirements.txt
   ```
   </div>

## Étapes suivantes

Maintenant que vous comprenez les modèles :

1. **[Votre premier projet](../tutorial/first-project.md)** : construire une application complète
2. **[Ajouter des routes](adding-routes.md)** : étendre votre projet basé sur un modèle
3. **[Référence CLI](cli-reference.md)** : maîtriser toutes les commandes disponibles

!!! tip "Astuces sur les modèles"
    - Les modèles sont d'excellents points de départ, pas des solutions finales
    - Personnalisez les modèles pour qu'ils correspondent à vos besoins spécifiques
    - Étudiez le code des modèles pour apprendre les bonnes pratiques de FastAPI
    - Utilisez le contrôle de version pour suivre vos personnalisations

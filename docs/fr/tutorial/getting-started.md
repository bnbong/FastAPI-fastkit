# Prise en main

Un tutoriel complet et pas à pas pour démarrer avec FastAPI-fastkit. Ce guide vous mènera de l'installation à l'exécution de votre première API en 15 minutes environ.

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- **Python 3.12 ou supérieur** installé sur votre système
- **Une connaissance de base de Python** (variables, fonctions, classes)
- **L'accès au terminal / à la ligne de commande**
- **Un éditeur de texte ou un IDE** (VS Code, PyCharm, etc.)

## Étape 1 : Installation

Commençons par installer FastAPI-fastkit. Nous recommandons d'utiliser un environnement virtuel pour isoler vos projets.

### Option A : avec pip (traditionnel)

<div class="termy">

```console
$ pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### Option B : avec UV (recommandé — plus rapide)

UV est un gestionnaire de paquets Python rapide. Si vous n'avez pas UV installé :

<div class="termy">

```console
# Installez d'abord UV
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# Installez ensuite FastAPI-fastkit
$ uv pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### Option C : avec un environnement virtuel

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # On Windows: fastapi-env\Scripts\activate
$ pip install fastapi-fastkit
```

</div>

### Vérifier l'installation

Vérifiez que FastAPI-fastkit est correctement installé :

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

## Étape 2 : Créer votre premier projet

Créons maintenant votre premier projet FastAPI avec la commande interactive `init` :

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-api
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-first-api            │
│ Author       │ Your Name               │
│ Author Email │ your.email@example.com  │
│ Description  │ My first FastAPI project│
└──────────────┴─────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal

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

Creating virtual environment...
Installing dependencies...
✨ FastAPI project 'my-first-api' has been created successfully!
```

</div>

!!! note "Sélection de la pile"
    Nous avons choisi **MINIMAL** pour ce tutoriel afin de garder les choses simples. Pour de vrais projets, envisagez **STANDARD** (inclut la prise en charge des bases de données) ou **FULL** (inclut les tâches en arrière-plan).

## Étape 3 : Aller dans votre projet

Déplacez-vous dans le répertoire du projet nouvellement créé :

<div class="termy">

```console
$ cd my-first-api
$ ls -la
total 32
drwxr-xr-x  8 user user  256 Dec  7 10:30 .
drwxr-xr-x  3 user user   96 Dec  7 10:30 ..
drwxr-xr-x  5 user user  160 Dec  7 10:30 .venv
-rw-r--r--  1 user user  156 Dec  7 10:30 README.md
-rw-r--r--  1 user user  243 Dec  7 10:30 requirements.txt
drwxr-xr-x  3 user user   96 Dec  7 10:30 scripts
-rw-r--r--  1 user user 1245 Dec  7 10:30 setup.py
drwxr-xr-x  8 user user  256 Dec  7 10:30 src
drwxr-xr-x  3 user user   96 Dec  7 10:30 tests
```

</div>

## Étape 4 : Activer l'environnement virtuel

Votre projet est livré avec un environnement virtuel préconfiguré. Activez-le :

<div class="termy">

```console
$ source .venv/bin/activate  # Sous Windows : .venv\Scripts\activate
(my-first-api) $
```

</div>

Notez que votre invite de terminal affiche désormais `(my-first-api)`, ce qui indique que l'environnement virtuel est actif.

## Étape 5 : Démarrer le serveur de développement

Voici la partie excitante — démarrons votre serveur FastAPI :

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720] using StatReload
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

🎉 **Félicitations !** Votre serveur FastAPI tourne désormais.

## Étape 6 : Tester votre API

Testons votre API de plusieurs manières :

### Méthode 1 : navigateur

Ouvrez votre navigateur web et visitez :

- **Point d'extrémité principal de l'API** : [http://127.0.0.1:8000](http://127.0.0.1:8000)

Vous devriez voir :
```json
{"message": "Hello World"}
```

### Méthode 2 : documentation interactive de l'API

Visitez la documentation d'API générée automatiquement :

- **Swagger UI** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc** : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Swagger UI est particulièrement utile — vous pouvez :

- Voir tous les points d'extrémité disponibles
- Tester les points d'extrémité directement dans votre navigateur
- Consulter les schémas de requête / réponse
- Télécharger les spécifications OpenAPI

### Méthode 3 : ligne de commande

Ouvrez un nouveau terminal (gardez le serveur en marche) et testez avec curl :

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Hello World"}

$ curl http://127.0.0.1:8000/api/v1/items/
[]

$ curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Item", "description": "This is a test item"}'
{
  "id": 1,
  "title": "My First Item",
  "description": "This is a test item"
}
```

</div>

## Étape 7 : Comprendre la structure de votre projet

Explorons ce que FastAPI-fastkit a généré pour vous :

<div class="termy">

```console
$ tree src
src/
├── __init__.py
├── main.py                 # Point d'entrée de l'application FastAPI
├── core/
│   ├── __init__.py
│   └── config.py          # Configuration de l'application
├── api/
│   ├── __init__.py
│   ├── api.py             # Routeur API principal
│   └── routes/
│       ├── __init__.py
│       └── items.py       # Points d'extrémité de l'API des items
├── crud/
│   ├── __init__.py
│   └── items.py           # Logique métier des items
├── schemas/
│   ├── __init__.py
│   └── items.py           # Schémas de validation des données
└── mocks/
    ├── __init__.py
    └── mock_items.json    # Données d'exemple
```

</div>

### Fichiers clés expliqués

**`src/main.py`** — le cœur de votre application :
```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**`src/core/config.py`** — paramètres de l'application :
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "my-first-api"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

**`src/api/routes/items.py`** — points d'extrémité d'API :
```python
from typing import List
from fastapi import APIRouter, HTTPException
from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import items_crud

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items():
    """Get all items"""
    return items_crud.get_all()

@router.post("/", response_model=Item)
def create_item(item: ItemCreate):
    """Create a new item"""
    return items_crud.create(item)
```

## Étape 8 : Ajouter votre première route personnalisée

Ajoutons une nouvelle route d'API pour pratiquer ce que vous avez appris :

<div class="termy">

```console
$ fastkit addroute users my-first-api
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-api                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-first-api'
```

</div>

Le serveur va redémarrer automatiquement et vous disposez maintenant de nouveaux points d'extrémité :

- `GET /api/v1/users/` — récupérer tous les utilisateurs
- `POST /api/v1/users/` — créer un nouvel utilisateur
- `GET /api/v1/users/{user_id}` — récupérer un utilisateur précis
- Et plus encore…

### Tester votre nouvelle route

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}

$ curl http://127.0.0.1:8000/api/v1/users/
[
  {
    "id": 1,
    "title": "John Doe",
    "description": "Software Developer"
  }
]
```

</div>

## Étape 9 : Explorer et modifier le code

Faisons une petite modification pour comprendre comment fonctionne le code.

### Modifier le message d'accueil

Ouvrez `src/main.py` dans votre éditeur de texte et modifiez le point d'extrémité racine :

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!"}
```

Enregistrez le fichier. Grâce au rechargement automatique, votre serveur redémarre automatiquement.

### Tester la modification

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Welcome to my first FastAPI application!"}
```

</div>

### Ajouter un nouveau point d'extrémité

Ajoutons un point d'extrémité simple à `src/main.py` :

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### Tester le nouveau point d'extrémité

<div class="termy">

```console
$ curl http://127.0.0.1:8000/hello/World
{"message":"Hello, World!"}

$ curl http://127.0.0.1:8000/hello/FastAPI
{"message":"Hello, FastAPI!"}
```

</div>

## Étape 10 : Lancer les tests

Votre projet est livré avec des tests préconfigurés. Lançons-les :

<div class="termy">

```console
$ python -m pytest
======================== test session starts ========================
collected 5 items

tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED

======================== 5 passed in 0.45s ========================
```

</div>

## Comprendre les concepts clés

### 1. Structure de l'application FastAPI

FastAPI-fastkit suit une **architecture modulaire** :

- **`main.py`** : point d'entrée de l'application et points d'extrémité globaux
- **`api/`** : organisation des routes d'API
- **`core/`** : configuration et paramètres de l'application
- **`crud/`** : logique métier et opérations sur les données
- **`schemas/`** : validation et sérialisation des données
- **`tests/`** : tests automatisés

### 2. Gestion des dépendances

Votre projet utilise une gestion moderne des dépendances Python :

- **Environnement virtuel** : environnement Python isolé
- **requirements.txt** : liste toutes les dépendances
- **Installation automatique** : dépendances installées lors de la création du projet

### 3. Serveur de développement

FastAPI-fastkit utilise **Uvicorn** comme serveur ASGI :

- **Rechargement automatique** : redémarre automatiquement lors des changements de code
- **Démarrage rapide** : itération de développement rapide
- **Prêt pour la production** : même serveur que celui utilisé en production

### 4. Documentation d'API

FastAPI génère automatiquement :

- **Spécification OpenAPI** : documentation d'API conforme aux standards de l'industrie
- **Swagger UI** : interface de test interactive
- **ReDoc** : vue alternative de la documentation

## Étapes suivantes

Félicitations ! Vous avez :

✅ Installé FastAPI-fastkit
✅ Créé votre premier projet
✅ Démarré le serveur de développement
✅ Testé vos points d'extrémité d'API
✅ Ajouté une nouvelle route
✅ Modifié du code existant
✅ Lancé les tests

### Continuer à apprendre

1. **[Votre premier projet](first-project.md)** : construire une API de blog complète avec des fonctionnalités avancées
2. **[Ajouter des routes](../user-guide/adding-routes.md)** : apprendre à créer des points d'extrémité d'API complexes
3. **[Utiliser les modèles](../user-guide/using-templates.md)** : explorer les modèles de projet prêts à l'emploi

### Expérimenter davantage

Essayez ces défis :

1. **Ajouter de la validation** : modifier les schémas pour ajouter des règles de validation des données
2. **Réponses personnalisées** : changer les formats de réponse dans les routes
3. **Variables d'environnement** : utiliser des fichiers `.env` pour la configuration
4. **Ajouter un middleware** : implémenter CORS ou l'authentification
5. **Intégration de base de données** : passer à la pile STANDARD pour la prise en charge des bases de données

### Problèmes courants et solutions

**Le serveur ne démarre pas :**

- Vérifiez que vous êtes dans le répertoire du projet
- Assurez-vous que l'environnement virtuel est activé
- Vérifiez l'absence d'erreurs de syntaxe dans votre code

**Erreurs d'import :**

- Assurez-vous que tous les fichiers `__init__.py` existent
- Vérifiez que vos chemins d'import sont corrects
- Vérifiez que vous utilisez l'environnement virtuel

**Port déjà utilisé :**
```console
$ fastkit runserver --port 8080
```

## Bonnes pratiques que vous avez apprises

1. **Environnements virtuels** : toujours utiliser des environnements isolés
2. **Structure de projet** : suivre une architecture modulaire organisée
3. **Rechargement automatique** : utiliser le serveur de développement pour une itération rapide
4. **Documentation d'API** : exploiter la génération automatique de documentation
5. **Tests** : exécuter les tests régulièrement pendant le développement

!!! tip "Astuces de développement"
    - Gardez le serveur de développement en marche pendant que vous codez
    - Utilisez la documentation interactive (`/docs`) pour tester vos API
    - Consultez le terminal pour des messages d'erreur utiles
    - Committez votre code dans un système de contrôle de version régulièrement

Vous êtes maintenant prêt à construire de superbes API avec FastAPI-fastkit ! 🚀

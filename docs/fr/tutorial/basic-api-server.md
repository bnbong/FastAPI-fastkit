# Construire un serveur d'API basique

Apprenez à construire rapidement un serveur d'API REST simple avec FastAPI-fastkit. Ce tutoriel s'adresse aux débutants en FastAPI et couvre la création d'API CRUD basiques.

## Ce que vous apprendrez dans ce tutoriel

- Créer un serveur d'API basique avec la commande `fastkit startdemo`
- Comprendre la structure d'un projet FastAPI
- Utiliser des points d'extrémité CRUD basiques
- Tester et documenter l'API
- Méthodes d'extension du projet

## Prérequis

- Python 3.12 ou supérieur installé
- FastAPI-fastkit installé (`pip install fastapi-fastkit`)
- Connaissances de base de Python

## Étape 1 : Créer un projet d'API basique

Créons un serveur d'API basique avec le modèle `fastapi-default`.

<div class="termy">

```console
$ fastkit startdemo fastapi-default
Enter the project name: my-first-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: My first FastAPI server
Deploying FastAPI project using 'fastapi-default' template

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-first-api               │
│ Author       │ Developer Kim              │
│ Author Email │ developer@example.com      │
│ Description  │ My first FastAPI server    │
└──────────────┴────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-api' from 'fastapi-default' has been created successfully!
```

</div>

## Étape 2 : Comprendre la structure du projet généré

Examinons la structure du projet généré :

```
my-first-api/
├── README.md                 # Documentation du projet
├── requirements.txt          # Liste des dépendances
├── setup.py                  # Configuration du package
├── scripts/
│   └── run-server.sh        # Script de démarrage du serveur
├── src/                     # Code source principal
│   ├── main.py              # Point d'entrée de l'application FastAPI
│   ├── core/
│   │   └── config.py        # Gestion de la configuration
│   ├── api/
│   │   ├── api.py           # Regroupement des routeurs API
│   │   └── routes/
│   │       └── items.py     # Points d'extrémité liés aux items
│   ├── schemas/
│   │   └── items.py         # Définitions des modèles de données
│   ├── crud/
│   │   └── items.py         # Logique de traitement des données
│   └── mocks/
│       └── mock_items.json  # Données de test
└── tests/                   # Code de test
    ├── __init__.py
    ├── conftest.py
    └── test_items.py
```

### Description des fichiers clés

- **`src/main.py`** : point d'entrée de l'application FastAPI
- **`src/api/routes/items.py`** : définitions des points d'extrémité d'API relatifs aux items
- **`src/schemas/items.py`** : définitions des structures de données de requête / réponse
- **`src/crud/items.py`** : logique des opérations sur les données
- **`src/mocks/mock_items.json`** : données d'exemple pour le développement

## Étape 3 : Lancer le serveur

Déplaçons-nous dans le répertoire du projet généré et lançons le serveur.

<div class="termy">

```console
$ cd my-first-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Will watch for changes in these directories: ['/path/to/my-first-api']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

Une fois le serveur lancé avec succès, vous pouvez accéder aux URL suivantes dans votre navigateur :

- **Serveur d'API** : http://127.0.0.1:8000
- **Documentation Swagger UI** : http://127.0.0.1:8000/docs
- **Documentation ReDoc** : http://127.0.0.1:8000/redoc

## Étape 4 : Explorer les points d'extrémité de l'API

L'API générée fournit par défaut les points d'extrémité suivants :

| Méthode | Point d'extrémité | Description |
|--------|----------|-------------|
| GET | `/items/` | Récupérer tous les items |
| GET | `/items/{item_id}` | Récupérer un item précis |
| POST | `/items/` | Créer un nouvel item |
| PUT | `/items/{item_id}` | Mettre à jour un item |
| DELETE | `/items/{item_id}` | Supprimer un item |

### Tester l'API

**1. Récupérer tous les items**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/"
[
  {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  },
  {
    "id": 2,
    "name": "Mouse",
    "description": "Wireless mouse",
    "price": 29.99,
    "tax": 2.99
  }
]
```

</div>

**2. Créer un nouvel item**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Keyboard",
       "description": "Mechanical keyboard",
       "price": 150.00,
       "tax": 15.00
     }'

{
  "id": 3,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.0,
  "tax": 15.0
}
```

</div>

**3. Récupérer un item précis**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/1"
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "tax": 99.99
}
```

</div>

## Étape 5 : Tester l'API avec Swagger UI

Rendez-vous sur http://127.0.0.1:8000/docs dans votre navigateur pour voir la documentation d'API générée automatiquement.

Ce que vous pouvez faire avec Swagger UI :

1. **Voir les points d'extrémité d'API** : visualiser tous les points d'extrémité disponibles
2. **Consulter les schémas de requête / réponse** : voir les formats d'entrée / sortie pour chaque point d'extrémité
3. **Tester les API directement** : effectuer de vrais appels d'API avec le bouton « Try it out »
4. **Voir les données d'exemple** : consulter les données d'exemple de requête / réponse pour chaque point d'extrémité

### Comment utiliser Swagger UI

1. Cliquez sur le point d'extrémité GET `/items/`
2. Cliquez sur le bouton « Try it out »
3. Cliquez sur le bouton « Execute »
4. Consultez la réponse du serveur

## Étape 6 : Comprendre la structure du code

### Application principale (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### Schéma d'item (`src/schemas/items.py`)

```python
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
```

### Logique CRUD (`src/crud/items.py`)

```python
from typing import List, Optional
from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self):
        self.items: List[Item] = []
        self.next_id = 1

    def create_item(self, item: ItemCreate) -> Item:
        new_item = Item(id=self.next_id, **item.dict())
        self.items.append(new_item)
        self.next_id += 1
        return new_item

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)
```

## Étape 7 : Étendre le projet

### Ajouter de nouvelles routes

Vous pouvez ajouter de nouveaux points d'extrémité avec la commande `fastkit addroute` :

<div class="termy">

```console
$ fastkit addroute user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ user                                     │
│ Target Directory │ /path/to/my-first-api                   │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to the current project? [Y/n]: y

✨ Successfully added new route 'user' to the current project!
```

</div>

Cette commande crée les fichiers suivants :

- `src/api/routes/user.py` — points d'extrémité relatifs aux utilisateurs
- `src/schemas/user.py` — modèles de données utilisateur
- `src/crud/user.py` — logique de traitement des données utilisateur

### Personnaliser la configuration d'environnement

Vous pouvez modifier le fichier `src/core/config.py` pour changer les paramètres du projet :

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My First API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "My first FastAPI server"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Étape 8 : Lancer les tests

Le projet inclut des tests basiques :

<div class="termy">

```console
$ pytest tests/ -v
======================== test session starts ========================
collected 4 items

tests/test_items.py::test_create_item PASSED                   [ 25%]
tests/test_items.py::test_read_items PASSED                    [ 50%]
tests/test_items.py::test_read_item PASSED                     [ 75%]
tests/test_items.py::test_update_item PASSED                   [100%]

======================== 4 passed in 0.15s ========================
```

</div>

## Étapes suivantes

Vous avez terminé la construction d'un serveur d'API basique ! Étapes suivantes à essayer :

1. **[Construire des API CRUD asynchrones](async-crud-api.md)** — apprendre un traitement asynchrone plus complexe
2. **[Intégration de base de données](database-integration.md)** — utiliser PostgreSQL et SQLAlchemy
3. **[Conteneurisation Docker](docker-deployment.md)** — préparer un déploiement en production
4. **[Gestion des réponses personnalisées](custom-response-handling.md)** — configuration avancée des formats de réponse

## Dépannage

### Problèmes courants

**Q. Le serveur ne démarre pas**
R. Vérifiez que votre environnement virtuel est activé et que les dépendances sont correctement installées.

**Q. Impossible d'accéder aux points d'extrémité de l'API**
R. Vérifiez que le serveur tourne normalement et que le numéro de port (par défaut : 8000) est correct.

**Q. Les API n'apparaissent pas dans Swagger UI**
R. Vérifiez que le routeur est correctement inclus dans `src/main.py`.

## Résumé

Dans ce tutoriel, nous avons utilisé FastAPI-fastkit pour :

- ✅ Créer un projet FastAPI basique
- ✅ Comprendre la structure du projet
- ✅ Utiliser des points d'extrémité d'API CRUD
- ✅ Documenter et tester l'API
- ✅ Étendre le projet

Maintenant que vous avez appris les bases de FastAPI, lancez-vous dans des projets plus complexes !

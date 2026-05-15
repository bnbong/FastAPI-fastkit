# FastAPI orienté domaine avec `fastapi-domain-starter`

Construisez un service FastAPI de taille moyenne avec l'organisation moderne recommandée — **un dossier par concept métier** sous `src/app/domains/`. Ce tutoriel vous guide de bout en bout dans le modèle `fastapi-domain-starter` : comment le générer, à quoi sert chaque package de premier niveau, comment l'exemple `items` fourni est relié au reste de l'application, et comment ajouter votre prochain domaine.

## Ce que vous apprendrez

- Générer un projet avec `fastkit startdemo fastapi-domain-starter`
- Le rôle de `core`, `db`, `domains` et `tests` dans la disposition
- Comment un domaine s'organise en `router → service → repository → schemas → models`
- Le contrat pour ajouter un nouveau domaine (copier le dossier items, enregistrer le routeur)
- Comment le point d'extrémité `/health` fourni et le CRUD `/api/v1/items` s'intègrent à l'application

## Prérequis

- Python 3.12+
- FastAPI-fastkit installé (`pip install fastapi-fastkit`)
- À l'aise avec les concepts FastAPI de base (opérations de chemin, schémas pydantic, dépendances)

S'il s'agit de votre premier projet FastAPI, commencez plutôt par [Construire un serveur d'API basique](basic-api-server.md) — ce tutoriel utilise le modèle plus simple `fastapi-default`.

## Étape 1 : Générer le projet

```console
$ fastkit startdemo fastapi-domain-starter
Enter the project name: orders-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Domain-oriented orders service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

`fastkit` déploie le modèle, remplit les emplacements, crée un environnement virtuel et installe les dépendances. Une fois terminé, plongez-y :

```console
$ cd orders-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

La documentation de l'API est ensuite servie à <http://127.0.0.1:8000/docs>.

## Étape 2 : L'arborescence générée

```
orders-api/
├── README.md
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt            # pinned deps (template ships both files; you maintain them as you add packages)
├── .env                        # SECRET_KEY, ENVIRONMENT
├── .gitignore
├── scripts/
│   ├── format.sh               # black + isort
│   ├── lint.sh                 # black --check + isort --check + mypy
│   ├── run-server.sh           # uvicorn src.app.main:app --reload
│   └── test.sh                 # pytest
├── src/
│   ├── __init__.py
│   └── app/                    # le package applicatif
│       ├── __init__.py
│       ├── main.py             # FastAPI() + middleware + inclusion de api_router
│       ├── core/               # configuration transverse
│       │   ├── __init__.py
│       │   └── config.py       # pydantic-settings (PROJECT_NAME, CORS, ...)
│       ├── db/                 # abstractions de persistance
│       │   ├── __init__.py
│       │   └── memory.py       # stockage clé-valeur générique InMemoryStore[T]
│       ├── api/                # routage côté transport
│       │   ├── __init__.py
│       │   ├── health.py       # GET /health
│       │   └── router.py       # regroupe la santé et tous les routeurs de domaine
│       └── domains/            # concepts métier (un dossier chacun)
│           ├── __init__.py
│           └── items/          # le domaine d'exemple
│               ├── __init__.py
│               ├── models.py       # @dataclass Item (entité)
│               ├── schemas.py      # ItemCreate, ItemRead (Pydantic)
│               ├── repository.py   # ItemRepository au-dessus de InMemoryStore
│               ├── service.py      # ItemService + ItemNotFoundError
│               └── router.py       # APIRouter(prefix="/items")
└── tests/
    ├── __init__.py
    ├── conftest.py             # fixture TestClient, remise à zéro du store
    ├── test_health.py
    └── test_items.py
```

Les deux idées à intégrer :

1. **`src/app/`** est le **package applicatif** — tout ce que l'application charge à l'exécution se trouve ici. Les tests importent depuis ce package (`from src.app.main import app`). Le `src/` externe sert à rendre le projet installable via `pip install`.
2. **`src/app/domains/<concept>/`** représente une **découpe par concept** — chaque concept métier (items, orders, users, …) possède son propre `router / service / repository / schemas / models`, et rien de plus.

## Étape 3 : Le rôle de chaque package de premier niveau

### `src/app/core/` — configuration

Contient la configuration applicative transversale. Le `config.py` fourni expose une classe `Settings` basée sur pydantic-settings, lue depuis `.env` / les variables d'environnement :

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "<project_name>"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: ... = []
    ...

settings = Settings()
```

`main.py` lit `settings.PROJECT_NAME`, `settings.API_V1_PREFIX` et `settings.all_cors_origins` pour câbler l'application FastAPI.

**Quand ajouter dans `core/` :** tout ce qui n'est pas spécifique à un seul domaine — paramètres globaux, journalisation structurée, middlewares personnalisés, helpers de sécurité, etc.

### `src/app/db/` — frontière de persistance

Contient l'abstraction sur votre magasin de données. Le starter fournit `memory.py` — un `InMemoryStore[T]` local au processus, générique sur le type d'entité. Le repository de chaque domaine enveloppe un `InMemoryStore`, de sorte que basculer plus tard sur SQLAlchemy / un pilote asynchrone est un changement circonscrit : seuls les repositories doivent être réécrits.

```python
class InMemoryStore(Generic[T]):
    def list(self) -> Iterable[T]: ...
    def get(self, id_: int) -> Optional[T]: ...
    def add(self, item: T) -> int: ...
    def replace(self, id_: int, item: T) -> bool: ...
    def delete(self, id_: int) -> bool: ...
    def clear(self) -> None: ...
```

**Quand étoffer `db/` :** ajoutez un `session.py` avec votre vraie fabrique de sessions de base de données une fois que vous migrez hors d'`InMemoryStore`. Conservez la signature publique des méthodes (`list` / `get` / `add` / …) inchangée pour que les repositories des domaines n'aient pas à modifier leur contrat interne.

### `src/app/api/` — routage de transport

Deux pièces :

- `health.py` — un petit `APIRouter` exposant `GET /health` qui renvoie `{"status": "ok"}`. Sans effet de bord, idéal pour les sondes de vivacité.
- `router.py` — l'**agrégateur de premier niveau**. Il inclut le routeur de santé et le routeur de chaque domaine, et cet `api_router` combiné unique est monté sur l'application FastAPI sous `/api/v1` :

```python
# src/app/api/router.py
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items_router.router)
```

```python
# src/app/main.py
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
```

**Pourquoi agréger ici :** lorsque vous ajoutez un nouveau domaine, vous ne modifiez que `src/app/api/router.py` pour enregistrer son routeur. `main.py` ne change jamais.

### `src/app/domains/<concept>/` — tranches métier

C'est là que vit l'essentiel de votre code à mesure que le projet grossit. Chaque domaine possède cinq fichiers :

| Fichier | Rôle |
|---|---|
| `models.py` | Entité du domaine (un `@dataclass` dans le starter ; pourrait être SQLAlchemy / SQLModel plus tard). La forme interne — pas le format de transport. |
| `schemas.py` | Schémas d'E/S de l'API (pydantic). Séparés de l'entité pour que le format de transport puisse évoluer sans toucher à la logique du domaine. |
| `repository.py` | Accès aux données. Enveloppe le magasin avec des méthodes typées pour l'item. La couture où la persistance est échangée. |
| `service.py` | Logique métier. Les routeurs appellent le `service`, jamais directement le `repository`. Les exceptions spécifiques au domaine (par ex. `ItemNotFoundError`) vivent ici. |
| `router.py` | Transport HTTP. Traduit les schémas pydantic ↔ appels au service ; convertit les exceptions du domaine en `HTTPException`. |

Le **sens des dépendances** suit `router → service → repository → store`. Chaque couche ne dépend que de celle qui se trouve juste en dessous. Les schémas sont utilisés par le `router` et le `service` ; les `models` sont utilisés par le `repository` et le `service`.

### `tests/`

Le dossier reflète la structure de l'application à l'exécution : un module de test par surface de comportement importante. Le starter fournit :

- `conftest.py` — fixture autouse qui réinitialise le magasin d'items entre les tests, plus une fixture `client` qui enveloppe `TestClient(app)`.
- `test_health.py` — vérifie que `GET /api/v1/health` renvoie 200 + `{"status": "ok"}`.
- `test_items.py` — couverture CRUD complète des points d'extrémité items, y compris un 404 pour des ids inconnus et un 422 pour une charge utile invalide.

Lancez avec :

```console
$ bash scripts/test.sh         # or: pytest
```

## Étape 4 : Parcourir le domaine `items` fourni

Le domaine d'exemple est un CRUD sur une petite entité :

```python
# src/app/domains/items/models.py
@dataclass
class Item:
    id: int
    name: str
    price: float
    in_stock: bool = True
```

Les schémas d'API séparent la forme d'entrée de la forme de sortie afin de pouvoir ajouter des champs contrôlés par le serveur (`id`) et de la validation (price ≥ 0) :

```python
# src/app/domains/items/schemas.py
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(ge=0)
    in_stock: bool = True

class ItemRead(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool
    model_config = ConfigDict(from_attributes=True)
```

Le repository enveloppe le magasin en mémoire et attribue les ids à l'insertion :

```python
# src/app/domains/items/repository.py
class ItemRepository:
    def __init__(self, store: Optional[InMemoryStore[Item]] = None) -> None:
        self._store = store if store is not None else _store

    def add(self, name: str, price: float, in_stock: bool = True) -> Item:
        item = Item(id=0, name=name, price=price, in_stock=in_stock)
        new_id = self._store.add(item)
        item.id = new_id
        return item
    # list_all / get / replace / delete / reset elided
```

La couche service est l'endroit où s'accumulent les règles métier. Aujourd'hui, c'est un mince passe-plat avec une exception personnalisée, mais c'est ici que vivra la politique future (« on ne peut pas supprimer un item présent dans une commande ouverte », etc.) :

```python
# src/app/domains/items/service.py
class ItemNotFoundError(Exception): ...

class ItemService:
    def __init__(self, repository: Optional[ItemRepository] = None) -> None:
        self._repository = repository if repository is not None else ItemRepository()

    def get_item(self, item_id: int) -> Item:
        item = self._repository.get(item_id)
        if item is None:
            raise ItemNotFoundError(f"Item {item_id} does not exist")
        return item
    # list_items / create_item / replace_item / delete_item elided
```

Le routeur est la seule pièce qui connaît HTTP. Notez qu'il prend le service sous forme de `Depends(...)` FastAPI pour que les tests puissent le surcharger, et qu'il associe `ItemNotFoundError` → `HTTPException(404)` :

```python
# src/app/domains/items/router.py
router = APIRouter(prefix="/items", tags=["items"])

def get_item_service() -> ItemService:
    return ItemService()

@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, service: ItemService = Depends(get_item_service)) -> ItemRead:
    try:
        return ItemRead.model_validate(service.get_item(item_id))
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
```

Le routeur complet expose :

| Méthode | Chemin | Ce qu'il fait |
|---|---|---|
| `GET` | `/api/v1/items` | Lister les items |
| `GET` | `/api/v1/items/{item_id}` | Lire un item |
| `POST` | `/api/v1/items` | Créer (renvoie 201) |
| `PUT` | `/api/v1/items/{item_id}` | Remplacer |
| `DELETE` | `/api/v1/items/{item_id}` | Supprimer (renvoie 204) |
| `GET` | `/api/v1/health` | Sonde de vivacité |

Essayez :

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
       -H 'Content-Type: application/json' \
       -d '{"name":"Mug","price":9.5,"in_stock":true}'
{"id":1,"name":"Mug","price":9.5,"in_stock":true}

$ curl http://127.0.0.1:8000/api/v1/items
[{"id":1,"name":"Mug","price":9.5,"in_stock":true}]

$ curl http://127.0.0.1:8000/api/v1/items/999
{"detail":"Item 999 does not exist"}
```

## Étape 5 : Ajouter votre prochain domaine

Le starter est conçu pour que **l'ajout d'un domaine reste surtout une opération de copie puis de renommage**. Supposons que vous vouliez un domaine `users` aux côtés de `items` :

### 1. Copier le dossier `items/`

```console
$ cp -r src/app/domains/items src/app/domains/users
```

### 2. Réécrire l'entité, les schémas et les noms de classe de chaque fichier

```python
# src/app/domains/users/models.py
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    is_active: bool = True
```

```python
# src/app/domains/users/schemas.py
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    # Garder ``str`` permet de réutiliser l'exemple tel quel.
    # Si vous préférez la validation d'e-mail intégrée à Pydantic,
    # installez la dépendance optionnelle
    # (``pip install 'pydantic[email]'`` — qui ajoute ``email-validator``)
    # puis remplacez ``str`` par ``EmailStr``.
    email: str = Field(min_length=3, max_length=320)
    is_active: bool = True

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
```

Renommez `Item → User`, `ItemNotFoundError → UserNotFoundError`, `ItemRepository → UserRepository`, `ItemService → UserService` dans `models.py`, `schemas.py`, `repository.py`, `service.py` et `router.py`. N'oubliez pas `prefix="/items"` → `prefix="/users"` et `tags=["items"]` → `tags=["users"]` dans le routeur.

Le repository peut conserver le même motif appuyé sur `InMemoryStore` — il est générique sur le type d'entité :

```python
# src/app/domains/users/repository.py
_store: InMemoryStore[User] = InMemoryStore()

class UserRepository:
    def __init__(self, store: Optional[InMemoryStore[User]] = None) -> None:
        self._store = store if store is not None else _store
    # ... same shape as ItemRepository ...
```

### 3. Mettre à jour le `__init__.py` du domaine

Le domaine items réexporte ses modules pour que les appelants puissent écrire `from src.app.domains.items import service`. Faites pareil pour users :

```python
# src/app/domains/users/__init__.py
from src.app.domains.users import (  # noqa: F401
    models,
    repository,
    router,
    schemas,
    service,
)
```

### 4. Enregistrer le routeur dans l'agrégateur

C'est le **seul fichier en dehors de `domains/users/` que vous devez toucher** :

```python
# src/app/api/router.py
from src.app.api import health
from src.app.domains.items import router as items_router
from src.app.domains.users import router as users_router  # ← add

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items_router.router)
api_router.include_router(users_router.router)             # ← add
```

Après un redémarrage du serveur, vous verrez `/api/v1/users` monté dans `/docs`.

### 5. Ajouter des tests

Calquez `tests/test_items.py` en `tests/test_users.py` — même forme orientée client, pointant simplement sur les nouveaux points d'extrémité. La fixture autouse de réinitialisation du magasin dans `conftest.py` isole déjà chaque test.

Si vous ajoutez un deuxième domaine qui utilise aussi `InMemoryStore`, élargissez la fixture pour réinitialiser également son magasin, ou conservez une fixture par domaine.

## Étape 6 : Aller plus loin

- La [Matrice des préréglages d'architecture](../reference/preset-feature-matrix.md) montre ce que `fastkit init --interactive` génère pour chaque préréglage, y compris les sélections de fonctionnalités qui demandent encore un peu de câblage manuel avec `domain-starter`.
- Le [tutoriel `fastapi-default`](basic-api-server.md) couvre l'alternative en couches si vous souhaitez comparer les dispositions avant de vous engager.
- Pour l'intégration de base de données, le [tutoriel Intégration de base de données](database-integration.md) présente le motif PostgreSQL + SQLAlchemy + Alembic. On retrouve les mêmes idées dans `src/app/db/` et dans les fichiers `repository.py` de chaque domaine.

## Récapitulatif

- **Génération** : `fastkit startdemo fastapi-domain-starter` → `bash scripts/run-server.sh` → documentation à `/docs`.
- **Disposition** : `core/` pour la configuration, `db/` pour les abstractions de persistance, `domains/<concept>/` pour les tranches métier, `api/router.py` comme point d'agrégation unique, `tests/` qui reflète les modules d'exécution.
- **Ajouter un domaine** : copier `items/`, renommer entité / schémas / classes, mettre à jour les réexportations de `__init__.py`, enregistrer le routeur dans `src/app/api/router.py`, ajouter un module de test. Aucune édition dans `main.py`.

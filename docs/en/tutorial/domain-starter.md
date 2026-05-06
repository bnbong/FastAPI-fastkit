# Domain-oriented FastAPI with `fastapi-domain-starter`

Build a medium-sized FastAPI service with the recommended modern layout —
**one folder per business concept** under `src/app/domains/`. This
tutorial walks through the `fastapi-domain-starter` template end-to-end:
how to generate it, what each top-level package does, how the bundled
`items` example is wired, and how to add your next domain.

## What you'll learn

- Generating a project with `fastkit startdemo fastapi-domain-starter`
- The role of `core`, `db`, `domains`, and `tests` in the layout
- How a domain is split into router → service → repository → schemas → models
- The contract for adding a new domain (copy the items folder, register the router)
- How the bundled `/health` endpoint and `/api/v1/items` CRUD plug into the app

## Prerequisites

- Python 3.12+
- FastAPI-fastkit installed (`pip install fastapi-fastkit`)
- Comfort with basic FastAPI concepts (path operations, pydantic schemas, dependencies)

If this is your first FastAPI project, start with
[Building a Basic API Server](basic-api-server.md) instead — that
tutorial uses the simpler `fastapi-default` template.

## Step 1: Generate the project

```console
$ fastkit startdemo fastapi-domain-starter
Enter the project name: orders-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Domain-oriented orders service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

`fastkit` deploys the template, fills in placeholders, creates a virtual
environment, and installs dependencies. After it finishes, jump in:

```console
$ cd orders-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

API docs are then served at <http://127.0.0.1:8000/docs>.

## Step 2: The generated tree

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
│   └── app/                    # the application package
│       ├── __init__.py
│       ├── main.py             # FastAPI() + middleware + api_router include
│       ├── core/               # cross-cutting configuration
│       │   ├── __init__.py
│       │   └── config.py       # pydantic-settings (PROJECT_NAME, CORS, ...)
│       ├── db/                 # persistence abstractions
│       │   ├── __init__.py
│       │   └── memory.py       # InMemoryStore[T] generic key-value store
│       ├── api/                # transport-level routing
│       │   ├── __init__.py
│       │   ├── health.py       # GET /health
│       │   └── router.py       # aggregates health + every domain router
│       └── domains/            # business concepts (one folder each)
│           ├── __init__.py
│           └── items/          # the example domain
│               ├── __init__.py
│               ├── models.py       # @dataclass Item (entity)
│               ├── schemas.py      # ItemCreate, ItemRead (pydantic)
│               ├── repository.py   # ItemRepository over InMemoryStore
│               ├── service.py      # ItemService + ItemNotFoundError
│               └── router.py       # APIRouter(prefix="/items")
└── tests/
    ├── __init__.py
    ├── conftest.py             # TestClient fixture, store reset
    ├── test_health.py
    └── test_items.py
```

The two ideas to internalize:

1. **`src/app/`** is the **application package** — everything the runtime
   imports lives here. Tests import from it (`from src.app.main import
   app`). The outer `src/` exists so the project is `pip install`-able.
2. **`src/app/domains/<concept>/`** is the **per-concept slice** — each
   business concept (items, orders, users, ...) owns its own router /
   service / repository / schemas / models and only those.

## Step 3: What each top-level package does

### `src/app/core/` — configuration

Holds cross-cutting application configuration. The bundled `config.py`
exposes a pydantic-settings `Settings` class read from `.env` /
environment variables:

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

`main.py` reads `settings.PROJECT_NAME`, `settings.API_V1_PREFIX`, and
`settings.all_cors_origins` to wire the FastAPI app.

**When to add to `core/`:** anything not specific to one domain — global
settings, structured logging, custom middleware, security helpers, etc.

### `src/app/db/` — persistence boundary

Holds the abstraction over your data store. The starter ships
`memory.py` — a process-local `InMemoryStore[T]` generic over the entity
type. Each domain's repository wraps an `InMemoryStore`, so swapping in
SQLAlchemy / async drivers later is a contained change: only the
repositories need to be rewritten.

```python
class InMemoryStore(Generic[T]):
    def list(self) -> Iterable[T]: ...
    def get(self, id_: int) -> Optional[T]: ...
    def add(self, item: T) -> int: ...
    def replace(self, id_: int, item: T) -> bool: ...
    def delete(self, id_: int) -> bool: ...
    def clear(self) -> None: ...
```

**When to grow `db/`:** add a `session.py` with your real database
session factory once you migrate off `InMemoryStore`. Keep the
public method shape (`list` / `get` / `add` / ...) the same so the
domain repositories don't have to change their internal contract.

### `src/app/api/` — transport routing

Two pieces:

- `health.py` — a small `APIRouter` exposing `GET /health` returning
  `{"status": "ok"}`. Side-effect-free, ideal for liveness probes.
- `router.py` — the **top-level aggregator**. It includes the health
  router and every domain's router, and that single combined
  `api_router` is mounted on the FastAPI app under `/api/v1`:

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

**Why aggregate here:** when you add a new domain, you only edit
`src/app/api/router.py` to register its router. `main.py` never changes.

### `src/app/domains/<concept>/` — business slices

This is where most of your code lives as the project grows. Each domain
owns five files:

| File | Role |
|---|---|
| `models.py` | Domain entity (a `@dataclass` in the starter; could be SQLAlchemy / SQLModel later). The internal shape — not the wire format. |
| `schemas.py` | API I/O schemas (pydantic). Separate from the entity so the wire format can evolve without touching domain logic. |
| `repository.py` | Data access. Wraps the store with item-typed methods. The seam where persistence is swapped in/out. |
| `service.py` | Business logic. Routers call into `service`, never directly into `repository`. Domain-specific exceptions (e.g. `ItemNotFoundError`) live here. |
| `router.py` | HTTP transport. Translates pydantic schemas ↔ service calls; turns domain exceptions into `HTTPException`s. |

The **dependency direction** is `router → service → repository → store`.
Each layer only depends on the layer below it. Schemas are referenced by
the router and service; models are referenced by the repository and
service.

### `tests/`

Mirrors the runtime layout — one test module per surface that has
behavior worth pinning. The starter ships:

- `conftest.py` — autouse fixture that resets the items store between
  tests, plus a `client` fixture wrapping `TestClient(app)`.
- `test_health.py` — verifies `GET /api/v1/health` returns 200 +
  `{"status": "ok"}`.
- `test_items.py` — full CRUD coverage of the items endpoints,
  including a 404 for unknown ids and a 422 for an invalid payload.

Run with:

```console
$ bash scripts/test.sh         # or: pytest
```

## Step 4: Walk through the bundled `items` domain

The example domain is a CRUD over a tiny entity:

```python
# src/app/domains/items/models.py
@dataclass
class Item:
    id: int
    name: str
    price: float
    in_stock: bool = True
```

API schemas separate the input shape from the output shape so we can
add server-controlled fields (`id`) and validation (price ≥ 0):

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

The repository wraps the in-memory store and assigns ids on insert:

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

The service layer is where business rules accumulate. Today it's a
thin pass-through with one custom exception, but this is where future
policy lives ("can't delete an item that's in an open order", etc.):

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

The router is the only piece that knows about HTTP. Notice it takes the
service as a FastAPI `Depends(...)` so tests can override it, and it
maps `ItemNotFoundError` → `HTTPException(404)`:

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

The full router exposes:

| Method | Path | What it does |
|---|---|---|
| `GET` | `/api/v1/items` | List items |
| `GET` | `/api/v1/items/{item_id}` | Read one |
| `POST` | `/api/v1/items` | Create (returns 201) |
| `PUT` | `/api/v1/items/{item_id}` | Replace |
| `DELETE` | `/api/v1/items/{item_id}` | Delete (returns 204) |
| `GET` | `/api/v1/health` | Liveness probe |

Try it:

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

## Step 5: Add your next domain

The starter is designed so that **adding a domain is a copy-rename
operation**. Say you want a `users` domain alongside `items`:

### 1. Copy the `items/` folder

```console
$ cp -r src/app/domains/items src/app/domains/users
```

### 2. Rewrite the entity, schemas, and per-file class names

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
    # Plain ``str`` keeps the snippet drop-in safe. To use pydantic's
    # built-in email validation instead, install the optional dependency
    # (``pip install 'pydantic[email]'`` — pulls in ``email-validator``)
    # and switch ``str`` to ``EmailStr``.
    email: str = Field(min_length=3, max_length=320)
    is_active: bool = True

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
```

Rename `Item → User`, `ItemNotFoundError → UserNotFoundError`,
`ItemRepository → UserRepository`, `ItemService → UserService` across
`models.py`, `schemas.py`, `repository.py`, `service.py`, and
`router.py`. Don't forget `prefix="/items"` → `prefix="/users"` and
`tags=["items"]` → `tags=["users"]` in the router.

The repository can keep the same `InMemoryStore`-backed pattern — it's
generic over the entity type:

```python
# src/app/domains/users/repository.py
_store: InMemoryStore[User] = InMemoryStore()

class UserRepository:
    def __init__(self, store: Optional[InMemoryStore[User]] = None) -> None:
        self._store = store if store is not None else _store
    # ... same shape as ItemRepository ...
```

### 3. Update the domain `__init__.py`

The items domain re-exports its modules so callers can write
`from src.app.domains.items import service`. Mirror that for users:

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

### 4. Register the router in the aggregator

This is the **only file outside `domains/users/` you need to touch**:

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

After a server restart you'll see `/api/v1/users` mounted in `/docs`.

### 5. Add tests

Mirror `tests/test_items.py` as `tests/test_users.py` — same
client-driven shape, just hit the new endpoints. The autouse store-reset
fixture in `conftest.py` already keeps each test isolated.

If you add a second domain that also uses `InMemoryStore`, broaden the
fixture to reset its store too, or keep one fixture per domain.

## Step 6: Where to go next

- The [Architecture Preset Matrix](../reference/preset-feature-matrix.md)
  shows what `fastkit init --interactive` generates for each preset,
  including which feature selections need manual wiring under
  `domain-starter`.
- The [`fastapi-default` tutorial](basic-api-server.md) covers the
  layered alternative if you'd like to compare layouts before
  committing.
- For database integration, the
  [Database Integration tutorial](database-integration.md) shows the
  PostgreSQL + SQLAlchemy + Alembic pattern. The same ideas drop into
  `src/app/db/` and the per-domain `repository.py` files.

## Recap

- **Generation**: `fastkit startdemo fastapi-domain-starter` →
  `bash scripts/run-server.sh` → docs at `/docs`.
- **Layout**: `core/` for config, `db/` for persistence abstractions,
  `domains/<concept>/` for business slices, `api/router.py` as the
  single aggregation point, `tests/` mirroring runtime modules.
- **Adding a domain**: copy `items/`, rename entity / schemas / classes,
  update the `__init__.py` re-exports, register the router in
  `src/app/api/router.py`, add a test module. No edits to `main.py`.

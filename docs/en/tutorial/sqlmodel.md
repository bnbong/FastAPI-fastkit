# Async persistence with `fastapi-sqlmodel`

Build a database-backed API where each concept is defined **once**.
SQLModel classes are simultaneously the SQLAlchemy table and the pydantic
schema, so adding a column doesn't mean editing four files. This tutorial
walks through the `fastapi-sqlmodel` template: the model hierarchy, the
generic CRUD base, paginated responses, async Alembic migrations, and how
to add your own domain.

## What you'll learn

- Generating a project with `fastkit startdemo fastapi-sqlmodel`
- How `ItemBase` → `Item` / `ItemCreate` / `ItemUpdate` / `ItemPublic`
  removes schema duplication
- What `CRUDBase` gives you for free and where to extend it
- The `Page[T]` list envelope and where its limits are enforced
- Running async Alembic migrations and switching from SQLite to PostgreSQL

## Prerequisites

- Python 3.12+
- FastAPI-fastkit installed (`pip install fastapi-fastkit`)
- Familiarity with `async`/`await` and basic SQL concepts

If you want the synchronous, Compose-based PostgreSQL stack instead, see
[Integrating with a Database](database-integration.md), which uses
`fastapi-psql-orm`.

## Step 1: Generate and run

```console
$ fastkit startdemo fastapi-sqlmodel
Enter the project name: catalog-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Product catalog service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

```console
$ cd catalog-api
$ bash scripts/migrate.sh        # alembic upgrade head
$ bash scripts/run-server.sh     # or: uvicorn src.app.main:app --reload
```

The default `DATABASE_URL` is `sqlite+aiosqlite:///./app.db`, so there is
no database server to install. Docs are at <http://127.0.0.1:8000/docs>.

## Step 2: The generated tree

```
catalog-api/
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env
├── scripts/
│   ├── format.sh  lint.sh  migrate.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI app + lifespan
│       ├── core/config.py      # pydantic-settings
│       ├── db/
│       │   ├── session.py      # async engine, get_session dependency
│       │   └── base.py         # metadata aggregation for Alembic
│       ├── crud/
│       │   ├── base.py         # generic CRUDBase
│       │   └── pagination.py   # Page[T] envelope
│       ├── alembic/
│       │   ├── env.py          # async migration environment
│       │   └── versions/0001_create_items_table.py
│       ├── api/
│       │   ├── router.py       # aggregates health + domain routers
│       │   └── health.py       # GET /health
│       └── domains/items/      # the example domain
│           ├── models.py       # Item table + Create/Update/Public schemas
│           ├── crud.py         # ItemCRUD(CRUDBase)
│           └── router.py       # FastAPI router
└── tests/
    ├── conftest.py  test_health.py  test_items.py  test_crud_base.py
```

Note what a domain folder does *not* contain: no `schemas.py` separate
from `models.py`, and no per-domain repository boilerplate. Both
disappear into SQLModel and `CRUDBase` respectively.

## Step 3: One model definition per concept

Open `src/app/domains/items/models.py`. Everything derives from a single
base:

```python
class ItemBase(SQLModel):
    """Fields shared by the table and every request/response schema."""
    name: str = Field(min_length=1, max_length=128, index=True)
    description: str | None = Field(default=None, max_length=512)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemBase, table=True):        # the actual table
    __tablename__ = "items"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)


class ItemCreate(ItemBase): ...          # POST body — no server-assigned fields


class ItemUpdate(SQLModel):              # PATCH body — every field optional
    name: str | None = Field(default=None, min_length=1, max_length=128)
    ...


class ItemPublic(ItemBase):              # response — base + server-assigned
    id: int
    created_at: datetime
```

Four classes, four distinct jobs, one place where the fields live:

| Class        | Role                          | Why it's separate |
|--------------|-------------------------------|-------------------|
| `ItemBase`   | shared field definitions      | the single source of truth |
| `Item`       | the database table            | adds `id`, `created_at` |
| `ItemCreate` | request body for `POST`       | must not accept `id` |
| `ItemUpdate` | request body for `PATCH`      | every field optional |
| `ItemPublic` | response body                 | exposes server-assigned fields |

**The payoff:** adding a `sku` column means adding one line to
`ItemBase`. The table gets the column, the create body accepts it, and
the response returns it — with no other edits. `ItemUpdate` stays
explicit on purpose: partial-update semantics are a decision, not a
derivation.

## Step 4: CRUD you don't rewrite

`src/app/crud/base.py` is a generic class parameterized by the table
model and its two input schemas:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, session, obj_id) -> ModelType | None: ...
    async def list(self, session, *, offset=0, limit=20) -> Sequence[ModelType]: ...
    async def count(self, session) -> int: ...
    async def create(self, session, obj_in) -> ModelType: ...
    async def update(self, session, db_obj, obj_in) -> ModelType: ...
    async def delete(self, session, db_obj) -> None: ...
```

One detail worth internalizing — `update` uses `exclude_unset=True`:

```python
changes: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
```

That is what makes `PATCH` actually partial. A field the client didn't
send is absent from the dict, so it is never written; without
`exclude_unset` a `PATCH` would silently clobber untouched columns with
their schema defaults.

A domain subclasses the base and adds only what is specific to it:

```python
class ItemCRUD(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """CRUD for Item, extended with a name search."""

    async def search_by_name(self, session, term, *, limit=20):
        statement = select(Item).where(Item.name.like(f"%{term}%")).limit(limit)
        result = await session.exec(statement)
        return result.all()


item_crud = ItemCRUD(Item)
```

## Step 5: Paginated lists

List endpoints return a `Page[T]` envelope rather than a bare array:

```json
{"items": [...], "total": 42, "offset": 0, "limit": 20}
```

The clamping happens in the router, not in the client:

```python
limit: int = Query(default=settings.DEFAULT_PAGE_LIMIT, ge=1)
...
limit = min(limit, settings.MAX_PAGE_LIMIT)
```

So `?limit=100000` cannot turn one request into a full table scan.
`Page` also exposes a `has_next` property derived from `offset`,
`len(items)` and `total`, which is usually what a front end actually
wants.

The endpoints the items domain ships:

| Method | Endpoint                  | Description                    |
|--------|---------------------------|--------------------------------|
| GET    | `/api/v1/health`          | Liveness probe                 |
| GET    | `/api/v1/items`           | List items (`offset`, `limit`) |
| GET    | `/api/v1/items/{item_id}` | Read a single item             |
| POST   | `/api/v1/items`           | Create an item (`201`)         |
| PATCH  | `/api/v1/items/{item_id}` | Partially update an item       |
| DELETE | `/api/v1/items/{item_id}` | Delete an item (`204`)         |

Try it:

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
    -H 'Content-Type: application/json' \
    -d '{"name": "Keyboard", "price": 89.0}'

$ curl 'http://127.0.0.1:8000/api/v1/items?offset=0&limit=5'
```

## Step 6: Async all the way down

`src/app/db/session.py` builds one `AsyncEngine` per process and hands
out request-scoped sessions:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

Routers depend on it (`session: AsyncSession = Depends(get_session)`),
`CRUDBase` takes it as its first argument, and every database call is
awaited. Nothing in the request path blocks the event loop on I/O.

`create_db_and_tables()` also lives here and is called from the app's
`lifespan`. It is a convenience for the SQLite default and for tests —
once Alembic owns the schema, set `CREATE_TABLES_ON_STARTUP=false`.

## Step 7: Adding a domain

1. Create `src/app/domains/<your_domain>/` mirroring `items`
   (`models.py`, `crud.py`, `router.py`).
2. **Import the table model in `src/app/db/base.py`.** This is the step
   that is easy to forget and confusing to debug: Alembic autogenerate
   and `create_db_and_tables` only see models that have been imported,
   so a missing import shows up as an empty migration rather than an
   error.
3. Register the router in `src/app/api/router.py`. The
   `# fastkit:imports` and `# fastkit:routes` anchors mark where
   `fastkit addroute` inserts code — put yours in the same places.
4. Generate a migration:
   `alembic revision --autogenerate -m "add <domain>"`.
5. Add `tests/test_<your_domain>.py`, mirroring `tests/test_items.py`.

## Step 8: Migrations and PostgreSQL

The Alembic environment under `src/app/alembic/env.py` is async, so it
runs against the same driver stack as the app. Day-to-day:

```console
$ bash scripts/migrate.sh                                  # upgrade head
$ alembic revision --autogenerate -m "add sku to items"    # after a model change
```

Switching databases is a URL change plus a driver:

```console
$ uv pip install "asyncpg>=0.31.0"
$ export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/app"
$ bash scripts/migrate.sh
```

Nothing in the models, CRUD or routers changes — that is the point of
keeping the driver behind `create_engine`.

## Step 9: The tests

```console
$ bash scripts/test.sh    # or: pytest
```

Each test runs against a fresh in-memory SQLite database: no migrations,
no fixture files, no cleanup between tests. `test_crud_base.py` exercises
the generic base directly — worth reading before you extend it, since it
documents the `exclude_unset` behaviour and the count/offset contract
that your own domains inherit.

## Recap

- **Generation**: `fastkit startdemo fastapi-sqlmodel` →
  `bash scripts/migrate.sh` → `bash scripts/run-server.sh`.
- **Models**: `ItemBase` holds the fields; table and I/O schemas derive
  from it, so a new column is declared once.
- **CRUD**: `CRUDBase` supplies get / list / count / create / update /
  delete; domains subclass it for their own queries.
- **Lists**: `Page[T]` envelope with server-side limit clamping.
- **Schema**: async Alembic; remember to import new models in
  `src/app/db/base.py`.
- **Database**: SQLite by default, PostgreSQL by changing
  `DATABASE_URL` and installing `asyncpg`.

## Where to go next

- [JWT Authentication](auth-jwt.md) — put accounts and protected routes
  in front of this data layer.
- [Domain-oriented Project](domain-starter.md) — the layout both
  templates share, without a database.
- [Which starter should I choose?](../user-guide/choosing-a-starter.md)

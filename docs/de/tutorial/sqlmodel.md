# Asynchrone Persistenz mit `fastapi-sqlmodel`

Bauen Sie eine datenbankgestützte API, in der jedes Konzept **einmal** definiert wird. SQLModel-Klassen sind gleichzeitig die SQLAlchemy-Tabelle und das Pydantic-Schema, sodass das Hinzufügen einer Spalte nicht bedeutet, vier Dateien zu bearbeiten. Dieses Tutorial führt Sie durch die Vorlage `fastapi-sqlmodel`: die Modellhierarchie, die generische CRUD-Basis, paginierte Antworten, asynchrone Alembic-Migrationen und wie Sie Ihre eigene Domäne hinzufügen.

## Was Sie lernen werden

- Ein Projekt mit `fastkit startdemo fastapi-sqlmodel` generieren
- Wie `ItemBase` → `Item` / `ItemCreate` / `ItemUpdate` / `ItemPublic` doppelte Schemas beseitigt
- Was `CRUDBase` Ihnen ohne Aufwand bietet und wo Sie es erweitern
- Die Listenhülle `Page[T]` und wo ihre Grenzen durchgesetzt werden
- Asynchrone Alembic-Migrationen ausführen und von SQLite zu PostgreSQL wechseln

## Voraussetzungen

- Python 3.12+
- FastAPI-fastkit installiert (`pip install fastapi-fastkit`)
- Vertrautheit mit `async`/`await` und grundlegenden SQL-Konzepten

Wenn Sie stattdessen den synchronen, Compose-basierten PostgreSQL-Stack möchten, lesen Sie [Datenbankintegration](database-integration.md), das `fastapi-psql-orm` verwendet.

## Schritt 1: Generieren und ausführen

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

Die Standard-`DATABASE_URL` ist `sqlite+aiosqlite:///./app.db`, sodass Sie keinen Datenbankserver installieren müssen. Die Dokumentation finden Sie unter <http://127.0.0.1:8000/docs>.

## Schritt 2: Der generierte Baum

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

Beachten Sie, was ein Domänenordner *nicht* enthält: keine von `models.py` getrennte `schemas.py` und keinen Repository-Boilerplate pro Domäne. Beides geht in SQLModel bzw. in `CRUDBase` auf.

## Schritt 3: Eine Modelldefinition pro Konzept

Öffnen Sie `src/app/domains/items/models.py`. Alles leitet sich von einer einzigen Basis ab:

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

Vier Klassen, vier klar getrennte Aufgaben, ein Ort, an dem die Felder liegen:

| Klasse       | Rolle                           | Warum sie getrennt ist |
|--------------|---------------------------------|------------------------|
| `ItemBase`   | gemeinsame Felddefinitionen     | die einzige Quelle der Wahrheit |
| `Item`       | die Datenbanktabelle            | fügt `id`, `created_at` hinzu |
| `ItemCreate` | Request-Body für `POST`         | darf `id` nicht akzeptieren |
| `ItemUpdate` | Request-Body für `PATCH`        | jedes Feld optional |
| `ItemPublic` | Response-Body                   | gibt vom Server vergebene Felder aus |

**Der Gewinn:** Eine `sku`-Spalte hinzuzufügen bedeutet, eine Zeile in `ItemBase` zu ergänzen. Die Tabelle erhält die Spalte, der Create-Body akzeptiert sie und die Antwort gibt sie zurück — ohne weitere Änderungen. `ItemUpdate` bleibt absichtlich explizit: Die Semantik partieller Updates ist eine Entscheidung, keine Ableitung.

## Schritt 4: CRUD, das Sie nicht neu schreiben

`src/app/crud/base.py` ist eine generische Klasse, die über das Tabellenmodell und seine beiden Eingabeschemas parametrisiert ist:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, session, obj_id) -> ModelType | None: ...
    async def list(self, session, *, offset=0, limit=20) -> Sequence[ModelType]: ...
    async def count(self, session) -> int: ...
    async def create(self, session, obj_in) -> ModelType: ...
    async def update(self, session, db_obj, obj_in) -> ModelType: ...
    async def delete(self, session, db_obj) -> None: ...
```

Ein Detail, das Sie verinnerlichen sollten — `update` verwendet `exclude_unset=True`:

```python
changes: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
```

Genau das macht `PATCH` tatsächlich partiell. Ein Feld, das der Client nicht gesendet hat, fehlt im Dict und wird daher nie geschrieben. Ohne `exclude_unset` würde ein `PATCH` unberührte Spalten stillschweigend mit ihren Schema-Standardwerten überschreiben.

Eine Domäne leitet von der Basis ab und fügt nur hinzu, was für sie spezifisch ist:

```python
class ItemCRUD(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """CRUD for Item, extended with a name search."""

    async def search_by_name(self, session, term, *, limit=20):
        statement = select(Item).where(Item.name.like(f"%{term}%")).limit(limit)
        result = await session.exec(statement)
        return result.all()


item_crud = ItemCRUD(Item)
```

## Schritt 5: Paginierte Listen

Listen-Endpunkte geben statt eines nackten Arrays eine `Page[T]`-Hülle zurück:

```json
{"items": [...], "total": 42, "offset": 0, "limit": 20}
```

Die Begrenzung erfolgt im Router, nicht im Client:

```python
limit: int = Query(default=settings.DEFAULT_PAGE_LIMIT, ge=1)
...
limit = min(limit, settings.MAX_PAGE_LIMIT)
```

Daher kann `?limit=100000` aus einer Anfrage keinen vollständigen Tabellenscan machen. `Page` stellt außerdem eine Property `has_next` bereit, die aus `offset`, `len(items)` und `total` abgeleitet wird und meist genau das ist, was ein Frontend tatsächlich braucht.

Die Endpunkte, die die items-Domäne mitbringt:

| Methode | Endpunkt                  | Beschreibung                       |
|---------|---------------------------|------------------------------------|
| GET     | `/api/v1/health`          | Liveness-Probe                     |
| GET     | `/api/v1/items`           | Items auflisten (`offset`, `limit`) |
| GET     | `/api/v1/items/{item_id}` | Ein einzelnes Item lesen           |
| POST    | `/api/v1/items`           | Ein Item anlegen (`201`)           |
| PATCH   | `/api/v1/items/{item_id}` | Ein Item teilweise aktualisieren   |
| DELETE  | `/api/v1/items/{item_id}` | Ein Item löschen (`204`)           |

Probieren Sie es aus:

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
    -H 'Content-Type: application/json' \
    -d '{"name": "Keyboard", "price": 89.0}'

$ curl 'http://127.0.0.1:8000/api/v1/items?offset=0&limit=5'
```

## Schritt 6: Durchgehend asynchron

`src/app/db/session.py` erstellt eine `AsyncEngine` pro Prozess und gibt Sessions mit Request-Gültigkeitsbereich aus:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

Router hängen davon ab (`session: AsyncSession = Depends(get_session)`), `CRUDBase` nimmt sie als erstes Argument entgegen, und jeder Datenbankaufruf wird mit `await` ausgeführt. Nichts im Request-Pfad blockiert die Event-Loop durch I/O.

`create_db_and_tables()` liegt ebenfalls hier und wird aus dem `lifespan` der App aufgerufen. Es ist eine Erleichterung für den SQLite-Standard und für Tests — sobald Alembic das Schema verwaltet, setzen Sie `CREATE_TABLES_ON_STARTUP=false`.

## Schritt 7: Eine Domäne hinzufügen

1. Legen Sie `src/app/domains/<your_domain>/` nach dem Vorbild von `items` an (`models.py`, `crud.py`, `router.py`).
2. **Importieren Sie das Tabellenmodell in `src/app/db/base.py`.** Diesen Schritt vergisst man leicht, und er ist verwirrend zu debuggen: Alembic-Autogenerate und `create_db_and_tables` sehen nur Modelle, die importiert wurden, daher zeigt sich ein fehlender Import als leere Migration statt als Fehler.
3. Registrieren Sie den Router in `src/app/api/router.py`. Die Anker `# fastkit:imports` und `# fastkit:routes` markieren, wo `fastkit addroute` Code einfügt — setzen Sie Ihren Code an dieselben Stellen.
4. Generieren Sie eine Migration: `alembic revision --autogenerate -m "add <domain>"`.
5. Fügen Sie `tests/test_<your_domain>.py` nach dem Vorbild von `tests/test_items.py` hinzu.

## Schritt 8: Migrationen und PostgreSQL

Die Alembic-Umgebung unter `src/app/alembic/env.py` ist asynchron und läuft daher auf demselben Treiber-Stack wie die App. Im Alltag:

```console
$ bash scripts/migrate.sh                                  # upgrade head
$ alembic revision --autogenerate -m "add sku to items"    # after a model change
```

Ein Datenbankwechsel besteht aus einer geänderten URL und einem Treiber:

```console
$ uv pip install "asyncpg>=0.31.0"
$ export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/app"
$ bash scripts/migrate.sh
```

An Modellen, CRUD oder Routern ändert sich nichts — genau darum geht es, wenn der Treiber hinter `create_engine` bleibt.

## Schritt 9: Die Tests

```console
$ bash scripts/test.sh    # or: pytest
```

Jeder Test läuft gegen eine frische In-Memory-SQLite-Datenbank: keine Migrationen, keine Fixture-Dateien, kein Aufräumen zwischen Tests. `test_crud_base.py` testet die generische Basis direkt — es lohnt sich, die Datei zu lesen, bevor Sie die Basis erweitern, denn sie dokumentiert das `exclude_unset`-Verhalten und den count/offset-Vertrag, den Ihre eigenen Domänen erben.

## Rückblick

- **Generierung**: `fastkit startdemo fastapi-sqlmodel` → `bash scripts/migrate.sh` → `bash scripts/run-server.sh`.
- **Modelle**: `ItemBase` enthält die Felder; Tabelle und Ein-/Ausgabeschemas leiten sich davon ab, sodass eine neue Spalte nur einmal deklariert wird.
- **CRUD**: `CRUDBase` liefert get / list / count / create / update / delete; Domänen leiten davon ab, um eigene Abfragen hinzuzufügen.
- **Listen**: `Page[T]`-Hülle mit serverseitiger Begrenzung des Limits.
- **Schema**: asynchrones Alembic; denken Sie daran, neue Modelle in `src/app/db/base.py` zu importieren.
- **Datenbank**: standardmäßig SQLite, PostgreSQL durch Ändern von `DATABASE_URL` und Installieren von `asyncpg`.

## Wie es weitergeht

- [JWT-Authentifizierung](auth-jwt.md) — stellen Sie Konten und geschützte Routen vor diese Datenschicht.
- [Domänenorientiertes Projekt](domain-starter.md) — das Layout, das beide Vorlagen teilen, ohne Datenbank.
- [Welchen Starter soll ich wählen?](../user-guide/choosing-a-starter.md)

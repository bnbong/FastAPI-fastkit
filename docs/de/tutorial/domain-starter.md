# Domänenorientiertes FastAPI mit `fastapi-domain-starter`

Bauen Sie einen mittelgroßen FastAPI-Dienst mit dem empfohlenen modernen Layout — **ein Ordner pro Geschäftskonzept** unter `src/app/domains/`. Dieses Tutorial führt Sie Schritt für Schritt durch die Vorlage `fastapi-domain-starter`: wie Sie sie generieren, was jedes Top-Level-Paket übernimmt, wie das mitgelieferte `items`-Beispiel eingebunden ist und wie Sie Ihre nächste Domäne hinzufügen.

## Was Sie lernen werden

- Ein Projekt mit `fastkit startdemo fastapi-domain-starter` generieren
- Die Rolle von `core`, `db`, `domains` und `tests` im Layout
- Wie eine Domäne in router → service → repository → schemas → models aufgeteilt wird
- Den Vertrag zum Hinzufügen einer neuen Domäne (items-Ordner kopieren, Router registrieren)
- Wie der mitgelieferte `/health`-Endpunkt und das `/api/v1/items`-CRUD in die App eingebunden werden

## Voraussetzungen

- Python 3.12+
- FastAPI-fastkit installiert (`pip install fastapi-fastkit`)
- Vertrautheit mit grundlegenden FastAPI-Konzepten (Path-Operations, Pydantic-Schemas, Dependencies)

Wenn dies Ihr erstes FastAPI-Projekt ist, starten Sie stattdessen mit [Einen einfachen API-Server bauen](basic-api-server.md) — dieses Tutorial verwendet die einfachere Vorlage `fastapi-default`.

## Schritt 1: Das Projekt generieren

```console
$ fastkit startdemo fastapi-domain-starter
Enter the project name: orders-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Domain-oriented orders service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

`fastkit` legt die Vorlage ab, füllt Platzhalter, erstellt eine virtuelle Umgebung und installiert Abhängigkeiten. Nach Abschluss:

```console
$ cd orders-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

Die API-Dokumentation wird dann unter <http://127.0.0.1:8000/docs> bereitgestellt.

## Schritt 2: Der generierte Baum

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

Zwei zentrale Ideen zum Verinnerlichen:

1. **`src/app/`** ist das **Anwendungspaket** — alles, was die Laufzeit importiert, liegt hier. Tests importieren daraus (`from src.app.main import app`). Das äußere `src/` existiert, damit das Projekt per `pip install` installierbar ist.
2. **`src/app/domains/<concept>/`** ist die **Scheibe pro Konzept** — jedes Geschäftskonzept (items, orders, users, …) besitzt seinen eigenen Router / Service / Repository / Schemas / Models und nur diese.

## Schritt 3: Was jedes Top-Level-Paket tut

### `src/app/core/` — Konfiguration

Enthält die übergreifende Anwendungskonfiguration. Die mitgelieferte `config.py` stellt eine pydantic-settings-Klasse `Settings` bereit, die aus `.env` / Umgebungsvariablen gelesen wird:

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

`main.py` liest `settings.PROJECT_NAME`, `settings.API_V1_PREFIX` und `settings.all_cors_origins`, um die FastAPI-App zu verdrahten.

**Wann etwas in `core/` ergänzen:** alles, was nicht spezifisch für eine einzelne Domäne ist — globale Einstellungen, strukturiertes Logging, eigene Middleware, Sicherheits-Helfer usw.

### `src/app/db/` — Persistenzgrenze

Enthält die Abstraktion über Ihren Datenspeicher. Der Starter liefert `memory.py` — einen prozesslokalen `InMemoryStore[T]`, generisch über den Entity-Typ. Das Repository jeder Domäne wickelt einen `InMemoryStore` ein, sodass ein späterer Wechsel zu SQLAlchemy / asynchronen Treibern eine eingegrenzte Änderung ist: nur die Repositories müssen neu geschrieben werden.

```python
class InMemoryStore(Generic[T]):
    def list(self) -> Iterable[T]: ...
    def get(self, id_: int) -> Optional[T]: ...
    def add(self, item: T) -> int: ...
    def replace(self, id_: int, item: T) -> bool: ...
    def delete(self, id_: int) -> bool: ...
    def clear(self) -> None: ...
```

**Wann `db/` ausbauen:** Ergänzen Sie eine `session.py` mit Ihrer echten Datenbank-Session-Factory, sobald Sie weg von `InMemoryStore` migrieren. Behalten Sie die öffentliche Methodenform (`list` / `get` / `add` / …) bei, damit die Domain-Repositories ihren internen Vertrag nicht ändern müssen.

### `src/app/api/` — Transport-Routing

Zwei Teile:

- `health.py` — ein kleiner `APIRouter`, der `GET /health` mit `{"status": "ok"}` ausliefert. Nebenwirkungsfrei, ideal für Liveness-Probes.
- `router.py` — der **Top-Level-Aggregator**. Er bindet den Health-Router und den Router jeder Domäne ein, und dieser eine kombinierte `api_router` wird unter `/api/v1` auf der FastAPI-App montiert:

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

**Warum hier aggregieren:** Wenn Sie eine neue Domäne hinzufügen, bearbeiten Sie nur `src/app/api/router.py`, um deren Router zu registrieren. `main.py` ändert sich nie.

### `src/app/domains/<concept>/` — Geschäfts-Scheiben

Hier lebt der Großteil Ihres Codes, wenn das Projekt wächst. Jede Domäne besitzt fünf Dateien:

| Datei | Rolle |
|---|---|
| `models.py` | Domain-Entity (im Starter ein `@dataclass`; später ggf. SQLAlchemy / SQLModel). Die interne Form — nicht das Wire-Format. |
| `schemas.py` | API-Ein-/Ausgabeschemas (pydantic). Vom Entity getrennt, damit sich das Wire-Format ändern lässt, ohne die Domain-Logik anzufassen. |
| `repository.py` | Datenzugriff. Wickelt den Store mit item-typisierten Methoden ein. Die Naht, an der Persistenz ausgetauscht wird. |
| `service.py` | Geschäftslogik. Router rufen den `service` auf, niemals direkt das `repository`. Domain-spezifische Exceptions (z. B. `ItemNotFoundError`) leben hier. |
| `router.py` | HTTP-Transport. Übersetzt pydantic-Schemas ↔ Service-Aufrufe; wandelt Domain-Exceptions in `HTTPException`s. |

Die **Abhängigkeitsrichtung** ist `router → service → repository → store`. Jede Schicht hängt nur von der darunterliegenden ab. Schemas werden von Router und Service referenziert; Models von Repository und Service.

### `tests/`

Spiegelt das Laufzeit-Layout — pro Oberfläche, deren Verhalten festgepinnt werden soll, ein Testmodul. Der Starter liefert:

- `conftest.py` — autouse-Fixture, die den Items-Store zwischen Tests zurücksetzt, plus eine `client`-Fixture, die `TestClient(app)` umhüllt.
- `test_health.py` — prüft, dass `GET /api/v1/health` 200 + `{"status": "ok"}` liefert.
- `test_items.py` — vollständige CRUD-Abdeckung der Items-Endpunkte, inklusive eines 404 für unbekannte IDs und eines 422 für ungültige Payloads.

Ausführen mit:

```console
$ bash scripts/test.sh         # or: pytest
```

## Schritt 4: Die mitgelieferte `items`-Domäne durchgehen

Die Beispieldomäne ist ein CRUD über einer kleinen Entity:

```python
# src/app/domains/items/models.py
@dataclass
class Item:
    id: int
    name: str
    price: float
    in_stock: bool = True
```

Die API-Schemas trennen die Eingabeform von der Ausgabeform, sodass wir serverseitig kontrollierte Felder (`id`) und Validierung (`price` ≥ 0) hinzufügen können:

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

Das Repository umschließt den In-Memory-Store und vergibt IDs beim Einfügen:

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

In der Service-Schicht sammeln sich Geschäftsregeln. Heute ist es ein dünner Durchreicher mit einer benutzerdefinierten Exception, aber hier wird zukünftig Policy leben („darf ein Item nicht löschen, das in einer offenen Bestellung ist" usw.):

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

Der Router ist das einzige Stück, das HTTP kennt. Beachten Sie, dass er den Service als FastAPI-`Depends(...)` entgegennimmt, sodass Tests ihn überschreiben können, und er bildet `ItemNotFoundError` → `HTTPException(404)` ab:

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

Der vollständige Router stellt bereit:

| Methode | Pfad | Wirkung |
|---|---|---|
| `GET` | `/api/v1/items` | Items auflisten |
| `GET` | `/api/v1/items/{item_id}` | Ein Item lesen |
| `POST` | `/api/v1/items` | Anlegen (gibt 201 zurück) |
| `PUT` | `/api/v1/items/{item_id}` | Ersetzen |
| `DELETE` | `/api/v1/items/{item_id}` | Löschen (gibt 204 zurück) |
| `GET` | `/api/v1/health` | Liveness-Probe |

Probieren Sie es:

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

## Schritt 5: Ihre nächste Domäne hinzufügen

Der Starter ist so gestaltet, dass das **Hinzufügen einer Domäne eine Kopier-und-Umbenenn-Operation** ist. Angenommen, Sie möchten eine `users`-Domäne neben `items`:

### 1. Den `items/`-Ordner kopieren

```console
$ cp -r src/app/domains/items src/app/domains/users
```

### 2. Entity, Schemas und Klassennamen pro Datei umschreiben

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
    # Ein einfaches ``str`` sorgt dafür, dass das Beispiel direkt funktioniert.
    # Wenn Sie stattdessen Pydantics eingebaute E-Mail-Validierung nutzen möchten,
    # installieren Sie die optionale Abhängigkeit
    # (``pip install 'pydantic[email]'`` — dadurch wird ``email-validator`` mitinstalliert)
    # und ersetzen ``str`` durch ``EmailStr``.
    email: str = Field(min_length=3, max_length=320)
    is_active: bool = True

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
```

Benennen Sie `Item → User`, `ItemNotFoundError → UserNotFoundError`, `ItemRepository → UserRepository`, `ItemService → UserService` in `models.py`, `schemas.py`, `repository.py`, `service.py` und `router.py` um. Vergessen Sie nicht `prefix="/items"` → `prefix="/users"` und `tags=["items"]` → `tags=["users"]` im Router.

Das Repository kann dasselbe `InMemoryStore`-gestützte Muster behalten — es ist generisch über den Entity-Typ:

```python
# src/app/domains/users/repository.py
_store: InMemoryStore[User] = InMemoryStore()

class UserRepository:
    def __init__(self, store: Optional[InMemoryStore[User]] = None) -> None:
        self._store = store if store is not None else _store
    # ... same shape as ItemRepository ...
```

### 3. Die `__init__.py` der Domäne aktualisieren

Die items-Domäne re-exportiert ihre Module, sodass Aufrufer `from src.app.domains.items import service` schreiben können. Spiegeln Sie das für users:

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

### 4. Den Router im Aggregator registrieren

Dies ist die **einzige Datei außerhalb von `domains/users/`, die Sie anfassen müssen**:

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

Nach einem Server-Neustart sehen Sie `/api/v1/users` in `/docs` eingebunden.

### 5. Tests hinzufügen

Spiegeln Sie `tests/test_items.py` als `tests/test_users.py` — dieselbe client-getriebene Form, einfach gegen die neuen Endpunkte. Die autouse-Fixture zur Store-Reset in `conftest.py` hält jeden Test bereits isoliert.

Wenn Sie eine zweite Domäne hinzufügen, die ebenfalls `InMemoryStore` nutzt, erweitern Sie die Fixture, um auch deren Store zurückzusetzen, oder behalten Sie eine Fixture pro Domäne.

## Schritt 6: Wie es weitergeht

- Die [Architektur-Preset-Matrix](../reference/preset-feature-matrix.md) zeigt, was `fastkit init --interactive` für jedes Preset generiert, einschließlich der Funktionsauswahlen, die unter `domain-starter` manuelle Verdrahtung benötigen.
- Das [`fastapi-default`-Tutorial](basic-api-server.md) behandelt die geschichtete Alternative, falls Sie Layouts vergleichen möchten, bevor Sie sich festlegen.
- Für die Datenbankintegration zeigt das [Tutorial Datenbankintegration](database-integration.md) das Muster PostgreSQL + SQLAlchemy + Alembic. Dieselben Ideen passen in `src/app/db/` und die `repository.py`-Dateien je Domäne.

## Rückblick

- **Generierung**: `fastkit startdemo fastapi-domain-starter` → `bash scripts/run-server.sh` → Doku unter `/docs`.
- **Layout**: `core/` für Konfiguration, `db/` für Persistenz-Abstraktionen, `domains/<concept>/` für Geschäfts-Scheiben, `api/router.py` als zentrale Aggregationsstelle, `tests/` als Spiegel der Laufzeitmodule.
- **Domäne hinzufügen**: `items/` kopieren, Entity / Schemas / Klassen umbenennen, Re-Exports in `__init__.py` aktualisieren, Router in `src/app/api/router.py` registrieren, Testmodul ergänzen. Keine Änderung an `main.py`.

# FastAPI orientado a dominios con `fastapi-domain-starter`

Construye un servicio FastAPI de tamaño medio con la estructura moderna recomendada: **una carpeta por cada concepto de negocio** dentro de `src/app/domains/`. Este tutorial recorre la plantilla `fastapi-domain-starter` de principio a fin: cómo generarla, para qué sirve cada paquete principal, cómo se integra el ejemplo `items` incluido y cómo añadir tu siguiente dominio.

## Qué vas a aprender

- Generar un proyecto con `fastkit startdemo fastapi-domain-starter`
- El papel de `core`, `db`, `domains` y `tests` dentro de la estructura
- Cómo se divide un dominio en router → service → repository → schemas → models
- El contrato para añadir un dominio nuevo (copiar la carpeta items, registrar el router)
- Cómo se integran en la app el endpoint `/health` y el CRUD `/api/v1/items`

## Requisitos previos

- Python 3.12+
- FastAPI-fastkit instalado (`pip install fastapi-fastkit`)
- Familiaridad con los conceptos básicos de FastAPI (operaciones de ruta, esquemas pydantic, dependencias)

Si este es tu primer proyecto FastAPI, empieza mejor por [Construir un servidor API básico](basic-api-server.md) — ese tutorial usa la plantilla más simple `fastapi-default`.

## Paso 1: Generar el proyecto

```console
$ fastkit startdemo fastapi-domain-starter
Enter the project name: orders-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Domain-oriented orders service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

`fastkit` genera el proyecto a partir de la plantilla, rellena los marcadores, crea un entorno virtual e instala las dependencias. Cuando termine, entra en el directorio:

```console
$ cd orders-api
$ bash scripts/run-server.sh    # o: uvicorn src.app.main:app --reload
```

La documentación de la API se sirve entonces en <http://127.0.0.1:8000/docs>.

## Paso 2: El árbol generado

```
orders-api/
├── README.md
├── pyproject.toml              # Metadatos PEP 621 + [tool.fastapi-fastkit]
├── requirements.txt            # Dependencias fijadas (la plantilla incluye ambos archivos; si añades paquetes, tendrás que mantenerlos tú)
├── .env                        # SECRET_KEY, ENVIRONMENT
├── .gitignore
├── scripts/
│   ├── format.sh               # black + isort
│   ├── lint.sh                 # black --check + isort --check + mypy
│   ├── run-server.sh           # uvicorn src.app.main:app --reload
│   └── test.sh                 # pytest
├── src/
│   ├── __init__.py
│   └── app/                    # el paquete de la aplicación
│       ├── __init__.py
│       ├── main.py             # FastAPI() + middleware + include de api_router
│       ├── core/               # configuración transversal
│       │   ├── __init__.py
│       │   └── config.py       # pydantic-settings (PROJECT_NAME, CORS, ...)
│       ├── db/                 # abstracciones de persistencia
│       │   ├── __init__.py
│       │   └── memory.py       # InMemoryStore[T] almacén key-value genérico
│       ├── api/                # enrutamiento a nivel HTTP
│       │   ├── __init__.py
│       │   ├── health.py       # GET /health
│       │   └── router.py       # agrega health + el router de cada dominio
│       └── domains/            # conceptos de negocio (una carpeta cada uno)
│           ├── __init__.py
│           └── items/          # el dominio de ejemplo
│               ├── __init__.py
│               ├── models.py       # @dataclass Item (entidad)
│               ├── schemas.py      # ItemCreate, ItemRead (pydantic)
│               ├── repository.py   # ItemRepository sobre InMemoryStore
│               ├── service.py      # ItemService + ItemNotFoundError
│               └── router.py       # APIRouter(prefix="/items")
└── tests/
    ├── __init__.py
    ├── conftest.py             # fixture TestClient, reinicio del almacén en memoria
    ├── test_health.py
    └── test_items.py
```

Dos ideas clave:

1. **`src/app/`** es el **paquete principal de la aplicación**. Todo lo que usa la app en ejecución vive aquí. Los tests también importan desde aquí (`from src.app.main import app`). El `src/` exterior existe para que el proyecto pueda instalarse con `pip install`.
2. **`src/app/domains/<concept>/`** es el **bloque de cada concepto**. Cada concepto de negocio (items, orders, users, ...) mantiene su propio router / service / repository / schemas / models y no mezcla esa lógica con la de otros dominios.

## Paso 3: Qué hace cada paquete de nivel superior

### `src/app/core/` — configuración

Contiene la configuración transversal de la aplicación. El `config.py` incluido expone una clase `Settings` con pydantic-settings que lee de `.env` / variables de entorno:

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

`main.py` usa `settings.PROJECT_NAME`, `settings.API_V1_PREFIX` y `settings.all_cors_origins` para configurar la app FastAPI.

**Cuándo añadir a `core/`:** cualquier cosa no específica de un dominio — ajustes globales, logging estructurado, middleware personalizado, helpers de seguridad, etc.

### `src/app/db/` — frontera de persistencia

Contiene la abstracción sobre tu capa de persistencia. El starter trae `memory.py`, que define un `InMemoryStore[T]` genérico, local al proceso y parametrizado por el tipo de entidad. El repository de cada dominio envuelve un `InMemoryStore`, así que sustituirlo más adelante por SQLAlchemy o por drivers asíncronos es un cambio acotado: basta con reescribir los repositories.

```python
class InMemoryStore(Generic[T]):
    def list(self) -> Iterable[T]: ...
    def get(self, id_: int) -> Optional[T]: ...
    def add(self, item: T) -> int: ...
    def replace(self, id_: int, item: T) -> bool: ...
    def delete(self, id_: int) -> bool: ...
    def clear(self) -> None: ...
```

**Cuándo ampliar `db/`:** añade un `session.py` con tu fábrica real de sesiones de base de datos cuando dejes de usar `InMemoryStore`. Mantén la interfaz pública de los métodos (`list` / `get` / `add` / ...) para que los repositories de dominio no tengan que cambiar su contrato interno.

### `src/app/api/` — enrutamiento HTTP

Dos piezas:

- `health.py` — un `APIRouter` pequeño que expone `GET /health` devolviendo `{"status": "ok"}`. Sin efectos secundarios, ideal para probes de liveness.
- `router.py` — el **agregador de nivel superior**. Incluye el router de health y el router de cada dominio, y ese único `api_router` combinado se monta en la app FastAPI bajo `/api/v1`:

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

**Por qué se agrega aquí:** cuando añades un dominio nuevo, solo editas `src/app/api/router.py` para registrar su router. `main.py` no cambia.

### `src/app/domains/<concept>/` — bloques de negocio

Aquí es donde vivirá la mayor parte de tu código a medida que el proyecto crezca. Cada dominio mantiene cinco archivos principales:

| Archivo | Papel |
|---|---|
| `models.py` | Entidad de dominio (un `@dataclass` en el starter; podría ser SQLAlchemy / SQLModel más adelante). La forma interna — no el formato sobre la red. |
| `schemas.py` | Esquemas de E/S de la API (pydantic). Separados de la entidad para que el formato sobre la red pueda evolucionar sin tocar la lógica de dominio. |
| `repository.py` | Acceso a datos. Envuelve el almacén con métodos tipados por entidad. Es el punto donde cambiarás la persistencia si más adelante pasas a una base de datos real. |
| `service.py` | Lógica de negocio. Los routers llaman a `service`, nunca directamente al `repository`. Las excepciones específicas del dominio (p. ej. `ItemNotFoundError`) viven aquí. |
| `router.py` | Transporte HTTP. Traduce entre esquemas pydantic ↔ llamadas a service; convierte excepciones de dominio en `HTTPException`. |

La **dirección de las dependencias** es `router → service → repository → store`. Cada capa solo depende de la inmediatamente inferior. El router y el service usan los schemas; el repository y el service usan los models.

### `tests/`

Refleja la estructura de la aplicación en ejecución: un módulo de tests por cada superficie cuyo comportamiento conviene dejar cubierto. El starter trae:

- `conftest.py` — un fixture `autouse` que reinicia el almacén de items entre tests, además de un fixture `client` que envuelve `TestClient(app)`.
- `test_health.py` — verifica que `GET /api/v1/health` devuelve 200 y `{"status": "ok"}`.
- `test_items.py` — cobertura completa de CRUD de los endpoints de items, incluyendo 404 para ids desconocidos y 422 para un payload inválido.

Ejecútalos con:

```console
$ bash scripts/test.sh         # o: pytest
```

## Paso 4: Repaso del dominio `items` incluido

El dominio de ejemplo es un CRUD sobre una entidad pequeña:

```python
# src/app/domains/items/models.py
@dataclass
class Item:
    id: int
    name: str
    price: float
    in_stock: bool = True
```

Los esquemas de API separan la forma de entrada de la de salida para poder añadir campos controlados por el servidor (`id`) y validación (price ≥ 0):

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

El repository envuelve el almacén en memoria y asigna ids al insertar:

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
    # list_all / get / replace / delete / reset omitidos
```

La capa de service es donde se concentran las reglas de negocio. Hoy funciona como una capa ligera con una excepción específica, pero aquí es donde vivirá la lógica futura ("no puedes borrar un item que está en un pedido abierto", etc.):

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
    # list_items / create_item / replace_item / delete_item omitidos
```

El router es la única pieza que conoce HTTP. Fíjate en que recibe el service mediante un `Depends(...)` de FastAPI para que los tests puedan sustituirlo, y mapea `ItemNotFoundError` → `HTTPException(404)`:

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

El router completo expone:

| Método | Ruta | Qué hace |
|---|---|---|
| `GET` | `/api/v1/items` | Listar items |
| `GET` | `/api/v1/items/{item_id}` | Leer uno |
| `POST` | `/api/v1/items` | Crear (devuelve 201) |
| `PUT` | `/api/v1/items/{item_id}` | Reemplazar |
| `DELETE` | `/api/v1/items/{item_id}` | Eliminar (devuelve 204) |
| `GET` | `/api/v1/health` | Probe de liveness |

Pruébalo:

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

## Paso 5: Añadir tu siguiente dominio

El starter está pensado para que **añadir un dominio sea tan simple como copiar y renombrar**. Imagina que quieres un dominio `users` junto a `items`:

### 1. Copia la carpeta `items/`

```console
$ cp -r src/app/domains/items src/app/domains/users
```

### 2. Reescribe la entidad, los esquemas y los nombres de clase por archivo

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
    # Dejar ``str`` mantiene este snippet listo para usar sin dependencias
    # extra. Para usar la validación de email integrada de pydantic, instala
    # la dependencia opcional (``pip install 'pydantic[email]'`` — incluye
    # ``email-validator``) y cambia ``str`` por ``EmailStr``.
    email: str = Field(min_length=3, max_length=320)
    is_active: bool = True

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
```

Renombra `Item → User`, `ItemNotFoundError → UserNotFoundError`, `ItemRepository → UserRepository`, `ItemService → UserService` en `models.py`, `schemas.py`, `repository.py`, `service.py` y `router.py`. No olvides cambiar `prefix="/items"` → `prefix="/users"` y `tags=["items"]` → `tags=["users"]` en el router.

El repository puede mantener el mismo patrón respaldado por `InMemoryStore` — es genérico sobre el tipo de entidad:

```python
# src/app/domains/users/repository.py
_store: InMemoryStore[User] = InMemoryStore()

class UserRepository:
    def __init__(self, store: Optional[InMemoryStore[User]] = None) -> None:
        self._store = store if store is not None else _store
    # ... misma forma que ItemRepository ...
```

### 3. Actualiza el `__init__.py` del dominio

El dominio items reexporta sus módulos para que los llamantes puedan escribir `from src.app.domains.items import service`. Refleja eso en users:

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

### 4. Registra el router en el agregador

Este es el **único archivo fuera de `domains/users/` que necesitas tocar**:

```python
# src/app/api/router.py
from src.app.api import health
from src.app.domains.items import router as items_router
from src.app.domains.users import router as users_router  # ← añadir

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items_router.router)
api_router.include_router(users_router.router)             # ← añadir
```

Tras reiniciar el servidor verás `/api/v1/users` montado en `/docs`.

### 5. Añade tests

Usa `tests/test_items.py` como base para crear `tests/test_users.py`: sigue el mismo patrón con `client`, pero llamando a los nuevos endpoints. El fixture `autouse` que reinicia el almacén en `conftest.py` ya mantiene cada test aislado.

Si añades un segundo dominio que también use `InMemoryStore`, amplía el fixture para resetear también su store, o mantén un fixture por dominio.

## Paso 6: A dónde ir después

- La [Matriz de presets de arquitectura](../reference/preset-feature-matrix.md) muestra qué genera `fastkit init --interactive` para cada preset, incluidas las selecciones de funcionalidad que necesitan cableado manual bajo `domain-starter`.
- El [tutorial de `fastapi-default`](basic-api-server.md) cubre la alternativa en capas si quieres comparar estructuras antes de decidirte.
- Para integración con base de datos, el [tutorial de integración con base de datos](database-integration.md) muestra el patrón PostgreSQL + SQLAlchemy + Alembic. Las mismas ideas encajan en `src/app/db/` y en los `repository.py` por dominio.

## Recapitulación

- **Generación**: `fastkit startdemo fastapi-domain-starter` → `bash scripts/run-server.sh` → docs en `/docs`.
- **Estructura**: `core/` para la configuración, `db/` para las abstracciones de persistencia, `domains/<concept>/` para los bloques de negocio, `api/router.py` como único punto de agregación y `tests/` reflejando los módulos de la aplicación.
- **Añadir un dominio**: copia `items/`, renombra entidad / esquemas / clases, actualiza los re-exports de `__init__.py`, registra el router en `src/app/api/router.py`, añade un módulo de tests. Sin tocar `main.py`.

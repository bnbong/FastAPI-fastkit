# Persistencia asíncrona con `fastapi-sqlmodel`

Construye una API respaldada por una base de datos en la que cada concepto
se define **una sola vez**. Las clases de SQLModel son al mismo tiempo la
tabla de SQLAlchemy y el esquema pydantic, así que añadir una columna no
obliga a editar cuatro archivos. Este tutorial recorre la plantilla
`fastapi-sqlmodel`: la jerarquía de modelos, la base CRUD genérica, las
respuestas paginadas, las migraciones asíncronas de Alembic y cómo añadir tu
propio dominio.

## Qué vas a aprender

- Generar un proyecto con `fastkit startdemo fastapi-sqlmodel`
- Cómo `ItemBase` → `Item` / `ItemCreate` / `ItemUpdate` / `ItemPublic`
  elimina la duplicación de esquemas
- Qué te da `CRUDBase` sin coste y dónde ampliarlo
- El envoltorio de listas `Page[T]` y dónde se aplican sus límites
- Ejecutar migraciones asíncronas de Alembic y pasar de SQLite a PostgreSQL

## Requisitos previos

- Python 3.12+
- FastAPI-fastkit instalado (`pip install fastapi-fastkit`)
- Familiaridad con `async`/`await` y con los conceptos básicos de SQL

Si prefieres el stack síncrono de PostgreSQL basado en Compose, consulta
[Integración con base de datos](database-integration.md), que usa
`fastapi-psql-orm`.

## Paso 1: Generar y ejecutar

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
$ bash scripts/run-server.sh     # o: uvicorn src.app.main:app --reload
```

El `DATABASE_URL` por defecto es `sqlite+aiosqlite:///./app.db`, así que no
hay que instalar ningún servidor de base de datos. La documentación está en
<http://127.0.0.1:8000/docs>.

## Paso 2: El árbol generado

```
catalog-api/
├── pyproject.toml              # Metadatos PEP 621 + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env
├── scripts/
│   ├── format.sh  lint.sh  migrate.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # app FastAPI + lifespan
│       ├── core/config.py      # pydantic-settings
│       ├── db/
│       │   ├── session.py      # engine asíncrono, dependencia get_session
│       │   └── base.py         # agregación de metadata para Alembic
│       ├── crud/
│       │   ├── base.py         # CRUDBase genérico
│       │   └── pagination.py   # envoltorio Page[T]
│       ├── alembic/
│       │   ├── env.py          # entorno de migraciones asíncrono
│       │   └── versions/0001_create_items_table.py
│       ├── api/
│       │   ├── router.py       # agrega health + routers de dominio
│       │   └── health.py       # GET /health
│       └── domains/items/      # el dominio de ejemplo
│           ├── models.py       # tabla Item + esquemas Create/Update/Public
│           ├── crud.py         # ItemCRUD(CRUDBase)
│           └── router.py       # router de FastAPI
└── tests/
    ├── conftest.py  test_health.py  test_items.py  test_crud_base.py
```

Fíjate en lo que *no* contiene una carpeta de dominio: no hay un
`schemas.py` separado de `models.py`, ni código repetitivo de repository por
dominio. Ambos desaparecen dentro de SQLModel y de `CRUDBase`,
respectivamente.

## Paso 3: Una definición de modelo por concepto

Abre `src/app/domains/items/models.py`. Todo deriva de una única base:

```python
class ItemBase(SQLModel):
    """Fields shared by the table and every request/response schema."""
    name: str = Field(min_length=1, max_length=128, index=True)
    description: str | None = Field(default=None, max_length=512)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemBase, table=True):        # la tabla real
    __tablename__ = "items"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)


class ItemCreate(ItemBase): ...          # cuerpo de POST — sin campos asignados por el servidor


class ItemUpdate(SQLModel):              # cuerpo de PATCH — todos los campos opcionales
    name: str | None = Field(default=None, min_length=1, max_length=128)
    ...


class ItemPublic(ItemBase):              # respuesta — base + campos asignados por el servidor
    id: int
    created_at: datetime
```

Cuatro clases, cuatro funciones distintas, un único lugar donde viven los
campos:

| Clase        | Papel                              | Por qué está separada |
|--------------|------------------------------------|-----------------------|
| `ItemBase`   | definiciones de campos compartidas | la única fuente de verdad |
| `Item`       | la tabla de la base de datos       | añade `id`, `created_at` |
| `ItemCreate` | cuerpo de la petición `POST`       | no debe aceptar `id` |
| `ItemUpdate` | cuerpo de la petición `PATCH`      | todos los campos opcionales |
| `ItemPublic` | cuerpo de la respuesta             | expone los campos asignados por el servidor |

**La recompensa:** añadir una columna `sku` significa añadir una línea a
`ItemBase`. La tabla obtiene la columna, el cuerpo de creación la acepta y
la respuesta la devuelve — sin ninguna otra edición. `ItemUpdate` se
mantiene explícito a propósito: la semántica de actualización parcial es una
decisión, no una derivación.

## Paso 4: CRUD que no reescribes

`src/app/crud/base.py` es una clase genérica parametrizada por el modelo de
tabla y sus dos esquemas de entrada:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, session, obj_id) -> ModelType | None: ...
    async def list(self, session, *, offset=0, limit=20) -> Sequence[ModelType]: ...
    async def count(self, session) -> int: ...
    async def create(self, session, obj_in) -> ModelType: ...
    async def update(self, session, db_obj, obj_in) -> ModelType: ...
    async def delete(self, session, db_obj) -> None: ...
```

Un detalle que conviene interiorizar — `update` usa `exclude_unset=True`:

```python
changes: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
```

Eso es lo que hace que `PATCH` sea realmente parcial. Un campo que el
cliente no envió no aparece en el diccionario, así que nunca se escribe; sin
`exclude_unset`, un `PATCH` sobrescribiría en silencio las columnas no
tocadas con los valores por defecto del esquema.

Un dominio hereda de la base y añade solo lo que le es propio:

```python
class ItemCRUD(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """CRUD for Item, extended with a name search."""

    async def search_by_name(self, session, term, *, limit=20):
        statement = select(Item).where(Item.name.like(f"%{term}%")).limit(limit)
        result = await session.exec(statement)
        return result.all()


item_crud = ItemCRUD(Item)
```

## Paso 5: Listas paginadas

Los endpoints de listado devuelven un envoltorio `Page[T]` en lugar de un
array sin más:

```json
{"items": [...], "total": 42, "offset": 0, "limit": 20}
```

El acotamiento se hace en el router, no en el cliente:

```python
limit: int = Query(default=settings.DEFAULT_PAGE_LIMIT, ge=1)
...
limit = min(limit, settings.MAX_PAGE_LIMIT)
```

Así, `?limit=100000` no puede convertir una petición en un recorrido
completo de la tabla. `Page` también expone una propiedad `has_next`
derivada de `offset`, `len(items)` y `total`, que suele ser lo que de verdad
quiere un front-end.

Los endpoints que trae el dominio items:

| Método | Endpoint                  | Descripción                                |
|--------|---------------------------|--------------------------------------------|
| GET    | `/api/v1/health`          | Probe de liveness                          |
| GET    | `/api/v1/items`           | Listar items (`offset`, `limit`)           |
| GET    | `/api/v1/items/{item_id}` | Leer un item                               |
| POST   | `/api/v1/items`           | Crear un item (`201`)                      |
| PATCH  | `/api/v1/items/{item_id}` | Actualizar parcialmente un item            |
| DELETE | `/api/v1/items/{item_id}` | Eliminar un item (`204`)                   |

Pruébalo:

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
    -H 'Content-Type: application/json' \
    -d '{"name": "Keyboard", "price": 89.0}'

$ curl 'http://127.0.0.1:8000/api/v1/items?offset=0&limit=5'
```

## Paso 6: Asíncrono de principio a fin

`src/app/db/session.py` construye un `AsyncEngine` por proceso y entrega
sesiones con ámbito de petición:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

Los routers dependen de ella (`session: AsyncSession = Depends(get_session)`),
`CRUDBase` la recibe como primer argumento y cada llamada a la base de datos
se espera con `await`. Nada en el camino de la petición bloquea el event
loop por E/S.

`create_db_and_tables()` también vive aquí y se llama desde el `lifespan` de
la app. Es una comodidad para el SQLite por defecto y para los tests — en
cuanto Alembic se encargue del esquema, define
`CREATE_TABLES_ON_STARTUP=false`.

## Paso 7: Añadir un dominio

1. Crea `src/app/domains/<your_domain>/` imitando `items`
   (`models.py`, `crud.py`, `router.py`).
2. **Importa el modelo de tabla en `src/app/db/base.py`.** Este es el paso
   fácil de olvidar y confuso de depurar: el autogenerate de Alembic y
   `create_db_and_tables` solo ven los modelos que se han importado, así que
   una importación que falta aparece como una migración vacía en lugar de
   como un error.
3. Registra el router en `src/app/api/router.py`. Las anclas
   `# fastkit:imports` y `# fastkit:routes` marcan dónde inserta código
   `fastkit addroute` — pon el tuyo en los mismos lugares.
4. Genera una migración:
   `alembic revision --autogenerate -m "add <domain>"`.
5. Añade `tests/test_<your_domain>.py`, imitando `tests/test_items.py`.

## Paso 8: Migraciones y PostgreSQL

El entorno de Alembic en `src/app/alembic/env.py` es asíncrono, así que se
ejecuta sobre el mismo stack de drivers que la app. En el día a día:

```console
$ bash scripts/migrate.sh                                  # upgrade head
$ alembic revision --autogenerate -m "add sku to items"    # tras un cambio en los modelos
```

Cambiar de base de datos es cambiar una URL más un driver:

```console
$ uv pip install "asyncpg>=0.31.0"
$ export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/app"
$ bash scripts/migrate.sh
```

No cambia nada en los modelos, el CRUD ni los routers — ese es el sentido de
mantener el driver detrás de `create_engine`.

## Paso 9: Los tests

```console
$ bash scripts/test.sh    # o: pytest
```

Cada test se ejecuta contra una base de datos SQLite en memoria recién
creada: sin migraciones, sin archivos de fixtures, sin limpieza entre tests.
`test_crud_base.py` prueba directamente la base genérica — merece la pena
leerlo antes de ampliarla, porque documenta el comportamiento de
`exclude_unset` y el contrato de count/offset que heredan tus propios
dominios.

## Resumen

- **Generación**: `fastkit startdemo fastapi-sqlmodel` →
  `bash scripts/migrate.sh` → `bash scripts/run-server.sh`.
- **Modelos**: `ItemBase` contiene los campos; la tabla y los esquemas de
  E/S derivan de ella, así que una columna nueva se declara una sola vez.
- **CRUD**: `CRUDBase` proporciona get / list / count / create / update /
  delete; los dominios heredan de ella para sus propias consultas.
- **Listas**: envoltorio `Page[T]` con acotamiento del límite en el servidor.
- **Esquema**: Alembic asíncrono; recuerda importar los modelos nuevos en
  `src/app/db/base.py`.
- **Base de datos**: SQLite por defecto, PostgreSQL cambiando
  `DATABASE_URL` e instalando `asyncpg`.

## Siguientes pasos

- [Autenticación JWT](auth-jwt.md) — pon cuentas y rutas protegidas delante
  de esta capa de datos.
- [Proyecto orientado a dominios](domain-starter.md) — la estructura que
  comparten ambas plantillas, sin base de datos.
- [¿Qué starter elegir?](../user-guide/choosing-a-starter.md)

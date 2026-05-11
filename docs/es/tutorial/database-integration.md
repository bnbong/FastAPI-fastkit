# Integración con base de datos (PostgreSQL + SQLAlchemy)

Construye una aplicación FastAPI con base de datos PostgreSQL y SQLAlchemy ORM lista para usarse en producción. En este tutorial implementaremos un sistema completo de integración con base de datos usando la plantilla `fastapi-psql-orm`.

## Lo que aprenderás en este tutorial

- Configurar e integrar PostgreSQL
- Modelado de datos con SQLAlchemy ORM
- Migraciones de base de datos con Alembic
- Configurar el entorno de desarrollo con Docker Compose
- Gestión del pool de conexiones a la base de datos
- Procesamiento de transacciones e integridad de datos

## Requisitos previos

- Haber completado el [tutorial de APIs CRUD asíncronas](async-crud-api.md)
- Docker y Docker Compose instalados
- Conocimientos básicos de PostgreSQL
- Comprensión de los conceptos básicos de SQLAlchemy ORM

## Por qué PostgreSQL y SQLAlchemy

### Comparación: archivos JSON vs PostgreSQL

| Categoría | Archivos JSON | PostgreSQL |
|---|---|---|
| **Rendimiento** | Limitado | Indexación de alto rendimiento |
| **Concurrencia** | Problemas de bloqueo de archivos | Soporte de transacciones |
| **Escalabilidad** | Limitada por la memoria | Procesamiento de datos a gran escala |
| **Integridad** | No garantizada | Propiedades ACID garantizadas |
| **Consultas** | Hay que cargar todos los datos | Soporte de consultas complejas |
| **Copia de seguridad** | Copia de archivos | Backup / recuperación completos |

## Paso 1: Crear un proyecto PostgreSQL + ORM

Crea un proyecto usando la plantilla `fastapi-psql-orm`:

<div class="termy">

```console
$ fastkit startdemo fastapi-psql-orm
Enter the project name: todo-postgres-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Todo management API using PostgreSQL
Deploying FastAPI project using 'fastapi-psql-orm' template

           Project Information
┌──────────────┬─────────────────────────────────────────┐
│ Project Name │ todo-postgres-api                       │
│ Author       │ Developer Kim                           │
│ Author Email │ developer@example.com                   │
│ Description  │ Todo management API using PostgreSQL    │
└──────────────┴─────────────────────────────────────────┘

       Template Dependencies
┌──────────────┬────────────────┐
│ Dependency 1 │ fastapi        │
│ Dependency 2 │ uvicorn        │
│ Dependency 3 │ sqlalchemy     │
│ Dependency 4 │ alembic        │
│ Dependency 5 │ psycopg2       │
│ Dependency 6 │ asyncpg        │
│ Dependency 7 │ sqlmodel       │
└──────────────┴────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'todo-postgres-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## Paso 2: Analizar la estructura del proyecto

El proyecto generado ofrece un entorno completo de integración con base de datos:

```
todo-postgres-api/
├── docker-compose.yml           # Configuración del contenedor PostgreSQL
├── Dockerfile                   # Contenedor de la aplicación
├── alembic.ini                  # Configuración de Alembic
├── template-config.yml          # Configuración de la plantilla
├── scripts/
│   ├── pre-start.sh            # Inicialización previa al arranque
│   └── test.sh                 # Script de ejecución de pruebas
├── src/
│   ├── main.py                 # Aplicación FastAPI
│   ├── core/
│   │   ├── config.py           # Configuración de entorno
│   │   └── db.py               # Configuración de la conexión a la BD
│   ├── api/
│   │   ├── deps.py             # Inyección de dependencias
│   │   └── routes/
│   │       └── items.py        # Endpoints de la API
│   ├── crud/
│   │   └── items.py            # Operaciones de base de datos
│   ├── schemas/
│   │   └── items.py            # Modelos Pydantic
│   ├── utils/
│   │   ├── backend_pre_start.py # Inicialización del backend
│   │   ├── init_data.py        # Carga de datos iniciales
│   │   └── tests_pre_start.py  # Preparación de pruebas
│   └── alembic/
│       ├── env.py              # Configuración del entorno Alembic
│       └── versions/           # Archivos de migración
└── tests/
    ├── conftest.py             # Configuración de pruebas
    └── test_items.py           # Pruebas de la API
```

### Componentes principales

1. **SQLModel**: integración SQLAlchemy + Pydantic
2. **Alembic**: migraciones de esquema de base de datos
3. **asyncpg**: driver PostgreSQL asíncrono
4. **Docker Compose**: contenedorización del entorno de desarrollo

## Paso 3: Entender la configuración de la base de datos

### Configuración de la conexión (`src/core/db.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.core.config import settings

# Crear engine PostgreSQL asíncrono
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Mostrar logs de SQL
    pool_size=20,         # Tamaño del pool de conexiones
    max_overflow=0,       # Número de conexiones adicionales permitidas
    pool_pre_ping=True,   # Comprobar el estado de la conexión
)

# Factory de sesiones asíncronas
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_tables():
    """Crear las tablas de la base de datos"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """Proporcionar una sesión de base de datos (para inyección de dependencias)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### Configuración de entorno (`src/core/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Todo PostgreSQL API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Todo management API using PostgreSQL"

    # Configuración de base de datos
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "todoapp"
    POSTGRES_PORT: int = 5432

    # Base de datos de pruebas
    TEST_DATABASE_URL: Optional[str] = None

    # Modo debug
    DEBUG: bool = False

    @property
    def DATABASE_URL(self) -> str:
        """Generar la URL de conexión a PostgreSQL"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
```

## Paso 4: Definir el modelo de datos

### Modelo de datos con SQLModel (`src/schemas/items.py`)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Definir campos comunes
class ItemBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0, description="Price must be greater than 0")
    tax: Optional[float] = Field(default=None, ge=0)
    is_active: bool = Field(default=True)

# Modelo de tabla
class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Configuración del índice
    class Config:
        schema_extra = {
            "example": {
                "name": "notebook",
                "description": "High-performance gaming notebook",
                "price": 1500000.0,
                "tax": 150000.0,
                "is_active": True
            }
        }

# Modelos de petición / respuesta de la API
class ItemCreate(ItemBase):
    pass

class ItemUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[float] = Field(default=None, gt=0)
    tax: Optional[float] = Field(default=None, ge=0)
    is_active: Optional[bool] = Field(default=None)

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
```

## Paso 5: Implementar operaciones CRUD

### Lógica CRUD de base de datos (`src/crud/items.py`)

```python
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime

from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, item_create: ItemCreate) -> Item:
        """Crear un item nuevo"""
        db_item = Item(**item_create.dict())

        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)

        return db_item

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Obtener item por ID"""
        statement = select(Item).where(Item.id == item_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Item]:
        """Obtener varios items (con paginación)"""
        statement = select(Item)

        if active_only:
            statement = statement.where(Item.is_active == True)

        statement = statement.offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def update(self, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Actualizar un item"""
        # Preparar los datos de actualización
        update_data = item_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()

        # Ejecutar la actualización
        statement = (
            update(Item)
            .where(Item.id == item_id)
            .values(**update_data)
            .returning(Item)
        )

        result = await self.db.execute(statement)
        await self.db.commit()

        return result.scalar_one_or_none()

    async def delete(self, item_id: int) -> bool:
        """Eliminar item (soft delete)"""
        statement = (
            update(Item)
            .where(Item.id == item_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )

        result = await self.db.execute(statement)
        await self.db.commit()

        return result.rowcount > 0

    async def hard_delete(self, item_id: int) -> bool:
        """Eliminar un item por completo"""
        statement = delete(Item).where(Item.id == item_id)
        result = await self.db.execute(statement)
        await self.db.commit()

        return result.rowcount > 0

    async def search(self, query: str) -> List[Item]:
        """Buscar item (name, description)"""
        statement = select(Item).where(
            (Item.name.ilike(f"%{query}%")) |
            (Item.description.ilike(f"%{query}%"))
        ).where(Item.is_active == True)

        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_total_count(self, active_only: bool = True) -> int:
        """Obtener el total de items"""
        from sqlalchemy import func

        statement = select(func.count(Item.id))
        if active_only:
            statement = statement.where(Item.is_active == True)

        result = await self.db.execute(statement)
        return result.scalar()
```

## Paso 6: Implementar los endpoints de la API

### Configuración de inyección de dependencias (`src/api/deps.py`)

```python
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.crud.items import ItemCRUD

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de sesión de base de datos"""
    async for session in get_session():
        yield session

def get_item_crud(db: AsyncSession = Depends(get_db)) -> ItemCRUD:
    """Dependencia del CRUD de items"""
    return ItemCRUD(db)
```

### Implementación del router de la API (`src/api/routes/items.py`)

```python
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.deps import get_item_crud
from src.crud.items import ItemCRUD
from src.schemas.items import Item, ItemCreate, ItemUpdate, ItemResponse

router = APIRouter()

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_create: ItemCreate,
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Crear un item nuevo"""
    return await crud.create(item_create)

@router.get("/", response_model=List[ItemResponse])
async def read_items(
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to retrieve"),
    active_only: bool = Query(True, description="Only active items"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Obtener la lista de items (con paginación)"""
    return await crud.get_many(skip=skip, limit=limit, active_only=active_only)

@router.get("/search", response_model=List[ItemResponse])
async def search_items(
    q: str = Query(..., min_length=1, description="Search term"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Buscar item"""
    return await crud.search(q)

@router.get("/count")
async def get_items_count(
    active_only: bool = Query(True, description="Only active items"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Obtener el total de items"""
    count = await crud.get_total_count(active_only)
    return {"total": count}

@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Obtener un item concreto"""
    item = await crud.get_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item ID {item_id} not found"
        )
    return item

@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Actualizar un item"""
    updated_item = await crud.update(item_id, item_update)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item ID {item_id} not found"
        )
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    hard_delete: bool = Query(False, description="Complete delete"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Eliminar item"""
    if hard_delete:
        deleted = await crud.hard_delete(item_id)
    else:
        deleted = await crud.delete(item_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item ID {item_id} not found"
        )
```

## Paso 7: Ejecutar los contenedores de Docker

### Revisar la configuración de Docker Compose (`docker-compose.yml`)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_DB: todoapp
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    restart: always
    ports:
      - "8000:8000"
    environment:
      POSTGRES_SERVER: db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: todoapp
    depends_on:
      - db
    volumes:
      - ./src:/app/src

volumes:
  postgres_data:
```

### Ejecutar los contenedores

<div class="termy">

```console
$ cd todo-postgres-api

# Arrancar el servicio en segundo plano
$ docker-compose up -d
Creating network "todo-postgres-api_default" with the default driver
Creating volume "todo-postgres-api_postgres_data" with default driver
Pulling db (postgres:15)...
Creating todo-postgres-api_db_1 ... done
Building app
Creating todo-postgres-api_app_1 ... done

# Comprobar el estado del servicio
$ docker-compose ps
           Name                          Command              State           Ports
-------------------------------------------------------------------------------------
todo-postgres-api_app_1    uvicorn src.main:app --host=0.0.0.0 --port=8000   Up   0.0.0.0:8000->8000/tcp
todo-postgres-api_db_1     docker-entrypoint.sh postgres   Up   0.0.0.0:5432->5432/tcp

# Comprobar los logs
$ docker-compose logs app
```

</div>

## Paso 8: Migraciones de base de datos

### Crear la migración inicial con Alembic

<div class="termy">

```console
# Ejecutar la migración dentro del contenedor
$ docker-compose exec app alembic revision --autogenerate -m "Create items table"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'items'
Generating migration script /app/src/alembic/versions/001_create_items_table.py ... done

# Aplicar la migración
$ docker-compose exec app alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> 001, Create items table
```

</div>

### Revisar el archivo de migración

Comprueba el archivo de migración generado:

```python
# src/alembic/versions/001_create_items_table.py
"""Create items table

Revision ID: 001
Revises:
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('price', sa.Float(), nullable=False),
    sa.Column('tax', sa.Float(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_table('items')
    # ### end Alembic commands ###
```

## Paso 9: Probar la API

### Probar CRUD básico

<div class="termy">

```console
# Crear item nuevo
$ curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MacBook Pro",
    "description": "M2 chipset-equipped high-performance notebook",
    "price": 2500000,
    "tax": 250000
  }'

{
  "id": 1,
  "name": "MacBook Pro",
  "description": "M2 chipset-equipped high-performance notebook",
  "price": 2500000.0,
  "tax": 250000.0,
  "is_active": true,
  "created_at": "2024-01-01T12:00:00.123456",
  "updated_at": null
}

# Obtener lista de items
$ curl "http://localhost:8000/items/"

# Obtener lista con paginación
$ curl "http://localhost:8000/items/?skip=0&limit=10"

# Buscar item
$ curl "http://localhost:8000/items/search?q=MacBook"

# Obtener el total de items
$ curl "http://localhost:8000/items/count"
{"total": 1}
```

</div>

### Probar funcionalidades de consulta avanzadas

<div class="termy">

```console
# Listar incluyendo items inactivos
$ curl "http://localhost:8000/items/?active_only=false"

# Actualizar item
$ curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 2300000,
    "tax": 230000
  }'

# Soft delete del item
$ curl -X DELETE "http://localhost:8000/items/1"

# Hard delete del item
$ curl -X DELETE "http://localhost:8000/items/1?hard_delete=true"
```

</div>

## Paso 10: Funcionalidades avanzadas de base de datos

### Procesamiento de transacciones

```python
# Añadir a src/crud/items.py

from sqlalchemy.exc import SQLAlchemyError

async def create_items_batch(self, items_create: List[ItemCreate]) -> List[Item]:
    """Crear varios items dentro de una transacción"""
    created_items = []

    try:
        for item_create in items_create:
            db_item = Item(**item_create.dict())
            self.db.add(db_item)
            created_items.append(db_item)

        await self.db.commit()

        # Refrescar todos los items
        for item in created_items:
            await self.db.refresh(item)

        return created_items

    except SQLAlchemyError:
        await self.db.rollback()
        raise
```

### Modelado de datos relacional

```python
# Añadir a src/schemas/items.py

from sqlmodel import Relationship

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    description: Optional[str] = None

    # Definir la relación
    items: List["Item"] = Relationship(back_populates="category")

class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Añadir clave foránea
    category_id: Optional[int] = Field(foreign_key="categories.id")

    # Definir la relación
    category: Optional[Category] = Relationship(back_populates="items")
```

### Optimización de índices

```python
# Añadir a src/schemas/items.py

from sqlalchemy import Index

class Item(ItemBase, table=True):
    __tablename__ = "items"

    # ... campos existentes ...

    # Definir índices compuestos
    __table_args__ = (
        Index('ix_items_price_active', 'price', 'is_active'),
        Index('ix_items_created_at', 'created_at'),
        Index('ix_items_name_description', 'name', 'description'),  # Para búsqueda full text
    )
```

## Paso 11: Escribir pruebas

### Configuración de pruebas de base de datos (`tests/conftest.py`)

```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.main import app
from src.core.db import get_session
from src.core.config import settings

# Engine de base de datos de pruebas
test_engine = create_async_engine(
    settings.TEST_DATABASE_URL or "sqlite+aiosqlite:///./test.db",
    echo=False,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session():
    # Crear tabla de pruebas
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Proporcionar la sesión
    async with TestSessionLocal() as session:
        yield session

    # Eliminar la tabla tras el test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession):
    # Sobreescribir la dependencia
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

### Pruebas de integración (`tests/test_items.py`)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_read_item(client: AsyncClient):
    """Prueba de integración: crear y leer item"""
    # Crear item
    item_data = {
        "name": "Test Item",
        "description": "Database test",
        "price": 50000,
        "tax": 5000
    }

    response = await client.post("/items/", json=item_data)
    assert response.status_code == 201

    created_item = response.json()
    assert created_item["name"] == item_data["name"]
    assert "id" in created_item
    assert "created_at" in created_item

    # Leer el item creado
    item_id = created_item["id"]
    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200

    retrieved_item = response.json()
    assert retrieved_item["id"] == item_id
    assert retrieved_item["name"] == item_data["name"]

@pytest.mark.asyncio
async def test_item_pagination(client: AsyncClient):
    """Probar la paginación"""
    # Crear varios items
    for i in range(15):
        item_data = {
            "name": f"Item {i}",
            "description": f"Description {i}",
            "price": i * 1000,
            "tax": i * 100
        }
        await client.post("/items/", json=item_data)

    # Obtener primera página
    response = await client.get("/items/?skip=0&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 10

    # Obtener segunda página
    response = await client.get("/items/?skip=10&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 5

@pytest.mark.asyncio
async def test_item_search(client: AsyncClient):
    """Probar la búsqueda"""
    # Crear items de prueba
    items = [
        {"name": "iPhone 15", "description": "Latest smartphone", "price": 1200000, "tax": 120000},
        {"name": "Galaxy S24", "description": "Samsung flagship", "price": 1100000, "tax": 110000},
        {"name": "MacBook Air", "description": "Apple notebook", "price": 1500000, "tax": 150000},
    ]

    for item in items:
        await client.post("/items/", json=item)

    # Buscar "iPhone"
    response = await client.get("/items/search?q=iPhone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "iPhone 15"

    # Buscar "smartphone" (en descripción)
    response = await client.get("/items/search?q=smartphone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["description"] == "Latest smartphone"
```

### Ejecutar las pruebas

<div class="termy">

```console
# Ejecutar las pruebas dentro del contenedor
$ docker-compose exec app python -m pytest tests/ -v
======================== test session starts ========================
collected 12 items

tests/test_items.py::test_create_and_read_item PASSED         [ 8%]
tests/test_items.py::test_item_pagination PASSED             [16%]
tests/test_items.py::test_item_search PASSED                 [25%]
tests/test_items.py::test_update_item PASSED                 [33%]
tests/test_items.py::test_delete_item PASSED                 [41%]
tests/test_items.py::test_soft_delete PASSED                 [50%]
tests/test_items.py::test_item_not_found PASSED              [58%]
tests/test_items.py::test_invalid_item_data PASSED           [66%]
tests/test_items.py::test_database_transaction PASSED        [75%]
tests/test_items.py::test_concurrent_operations PASSED       [83%]
tests/test_items.py::test_item_count PASSED                  [91%]
tests/test_items.py::test_batch_operations PASSED           [100%]

======================== 12 passed in 2.34s ========================
```

</div>

## Paso 12: Consideraciones de despliegue a producción

### Optimizar el pool de conexiones

```python
# Añadir a src/core/config.py

class Settings(BaseSettings):
    # ... configuración existente ...

    # Configuración del pool de conexiones
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 300  # 5 minutos

    # Timeout de consulta
    DB_QUERY_TIMEOUT: int = 30

    # Reintentos de conexión
    DB_RETRY_ATTEMPTS: int = 3
    DB_RETRY_DELAY: int = 1
```

### Monitorización de la base de datos

```python
# Añadir a src/core/db.py

import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log antes de ejecutar la consulta"""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log tras ejecutar la consulta"""
    total = time.time() - context._query_start_time
    if total > 1.0:  # Log de consultas lentas (más de 1 segundo)
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")
```

## Próximos pasos

¡Has terminado la integración con PostgreSQL! Próximos pasos:

1. **[Contenedorización con Docker](docker-deployment.md)** - Construir un entorno de despliegue a producción
2. **[Manejo personalizado de respuestas](custom-response-handling.md)** - Formatos de respuesta avanzados
<!-- 3. **[Building Authentication Systems](authentication-system.md)** - JWT-based user authentication -->
<!-- 4. **[Building Caching Systems](caching-system.md)** - Performance optimization with Redis -->

## Resumen

En este tutorial hemos usado PostgreSQL y SQLAlchemy para:

- ✅ Integrar PostgreSQL
- ✅ Implementar ORM con SQLModel
- ✅ Configurar el sistema de migraciones con Alembic
- ✅ Operaciones CRUD avanzadas y optimización de consultas
- ✅ Transacciones e integridad de datos
- ✅ Paginación, búsqueda y ordenación
- ✅ Pruebas de integración y de base de datos
- ✅ Consideraciones de despliegue a producción

¡Ahora puedes construir APIs robustas basadas en base de datos listas para entornos de producción reales!

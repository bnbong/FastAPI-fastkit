# 数据库集成(PostgreSQL + SQLAlchemy)

使用 PostgreSQL 数据库与 SQLAlchemy ORM,构建一个可用于真实生产环境的 FastAPI 应用。本教程中我们将通过 `fastapi-psql-orm` 模板,实现完整的数据库集成。

## 您将学到的内容

- PostgreSQL 数据库的搭建与集成
- 用 SQLAlchemy ORM 做数据建模
- 使用 Alembic 做数据库迁移
- 通过 Docker Compose 搭建开发环境
- 数据库连接池管理
- 事务处理与数据一致性

## 前置条件

- 已完成 [异步 CRUD API 教程](async-crud-api.md)
- 已安装 Docker 与 Docker Compose
- 具备 PostgreSQL 基础知识
- 理解 SQLAlchemy ORM 的基本概念

## 为什么选择 PostgreSQL 与 SQLAlchemy?

### JSON 文件 vs PostgreSQL 对比

| 类别 | JSON 文件 | PostgreSQL |
|----------|------------|------------|
| **性能** | 受限 | 高性能索引 |
| **并发** | 文件锁问题 | 事务支持 |
| **可扩展性** | 受内存限制 | 大规模数据处理 |
| **一致性** | 无保证 | 保证 ACID 特性 |
| **查询** | 需加载全部数据 | 支持复杂查询 |
| **备份** | 复制文件 | 完整的备份 / 恢复 |

## 第 1 步:创建 PostgreSQL + ORM 项目

使用 `fastapi-psql-orm` 模板创建项目:

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

## 第 2 步:分析项目结构

生成的项目提供了完整的数据库集成环境:

```
todo-postgres-api/
├── docker-compose.yml           # PostgreSQL container configuration
├── Dockerfile                   # Application container
├── alembic.ini                  # Alembic configuration
├── template-config.yml          # Template configuration
├── scripts/
│   ├── pre-start.sh            # Pre-start initialization
│   └── test.sh                 # Test execution script
├── src/
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py           # Environment configuration
│   │   └── db.py               # 数据库连接配置
│   ├── api/
│   │   ├── deps.py             # 依赖注入
│   │   └── routes/
│   │       └── items.py        # API 端点
│   ├── crud/
│   │   └── items.py            # 数据库操作
│   ├── schemas/
│   │   └── items.py            # Pydantic 模型
│   ├── utils/
│   │   ├── backend_pre_start.py # 后端初始化
│   │   ├── init_data.py        # 初始数据加载
│   │   └── tests_pre_start.py  # 测试准备
│   └── alembic/
│       ├── env.py              # Alembic 环境配置
│       └── versions/           # 迁移文件
└── tests/
    ├── conftest.py             # 测试配置
    └── test_items.py           # API 测试
```

### 核心组件

1. **SQLModel**:SQLAlchemy 与 Pydantic 的融合
2. **Alembic**:数据库模式迁移
3. **asyncpg**:异步 PostgreSQL 驱动
4. **Docker Compose**:开发环境容器化

## 第 3 步:理解数据库配置

### 数据库连接设置(`src/core/db.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.core.config import settings

# 创建异步 PostgreSQL 引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 输出 SQL 日志
    pool_size=20,         # 连接池大小
    max_overflow=0,       # 允许额外创建的连接数
    pool_pre_ping=True,   # 预先检查连接状态
)

# 异步会话工厂
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_tables():
    """创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """提供数据库会话（用于依赖注入）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 环境配置(`src/core/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Todo PostgreSQL API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Todo management API using PostgreSQL"

    # Database configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "todoapp"
    POSTGRES_PORT: int = 5432

    # Test database
    TEST_DATABASE_URL: Optional[str] = None

    # Debug mode
    DEBUG: bool = False

    @property
    def DATABASE_URL(self) -> str:
        """Generate PostgreSQL connection URL"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
```

## 第 4 步:定义数据模型

### 使用 SQLModel 的数据模型(`src/schemas/items.py`)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Define common fields
class ItemBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0, description="Price must be greater than 0")
    tax: Optional[float] = Field(default=None, ge=0)
    is_active: bool = Field(default=True)

# Database table model
class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Set index
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

# API request/response model
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

## 第 5 步:实现 CRUD 操作

### 数据库 CRUD 逻辑(`src/crud/items.py`)

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
        """Create new item"""
        db_item = Item(**item_create.dict())

        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)

        return db_item

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """Get item by ID"""
        statement = select(Item).where(Item.id == item_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Item]:
        """Get multiple items (pagination supported)"""
        statement = select(Item)

        if active_only:
            statement = statement.where(Item.is_active == True)

        statement = statement.offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def update(self, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Update item"""
        # Prepare update data
        update_data = item_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()

        # Execute update
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
        """Delete item (soft delete)"""
        statement = (
            update(Item)
            .where(Item.id == item_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )

        result = await self.db.execute(statement)
        await self.db.commit()

        return result.rowcount > 0

    async def hard_delete(self, item_id: int) -> bool:
        """Delete item completely"""
        statement = delete(Item).where(Item.id == item_id)
        result = await self.db.execute(statement)
        await self.db.commit()

        return result.rowcount > 0

    async def search(self, query: str) -> List[Item]:
        """Search item (name, description)"""
        statement = select(Item).where(
            (Item.name.ilike(f"%{query}%")) |
            (Item.description.ilike(f"%{query}%"))
        ).where(Item.is_active == True)

        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_total_count(self, active_only: bool = True) -> int:
        """Get total item count"""
        from sqlalchemy import func

        statement = select(func.count(Item.id))
        if active_only:
            statement = statement.where(Item.is_active == True)

        result = await self.db.execute(statement)
        return result.scalar()
```

## 第 6 步:实现 API 端点

### 依赖注入设置(`src/api/deps.py`)

```python
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.crud.items import ItemCRUD

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async for session in get_session():
        yield session

def get_item_crud(db: AsyncSession = Depends(get_db)) -> ItemCRUD:
    """Item CRUD dependency"""
    return ItemCRUD(db)
```

### API 路由实现(`src/api/routes/items.py`)

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
    """Create new item"""
    return await crud.create(item_create)

@router.get("/", response_model=List[ItemResponse])
async def read_items(
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to retrieve"),
    active_only: bool = Query(True, description="Only active items"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Get item list (pagination supported)"""
    return await crud.get_many(skip=skip, limit=limit, active_only=active_only)

@router.get("/search", response_model=List[ItemResponse])
async def search_items(
    q: str = Query(..., min_length=1, description="Search term"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Search item"""
    return await crud.search(q)

@router.get("/count")
async def get_items_count(
    active_only: bool = Query(True, description="Only active items"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Get total item count"""
    count = await crud.get_total_count(active_only)
    return {"total": count}

@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    crud: ItemCRUD = Depends(get_item_crud)
):
    """Get specific item"""
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
    """Update item"""
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
    """Delete item"""
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

## 第 7 步:运行 Docker 容器

### 检查 Docker Compose 配置(`docker-compose.yml`)

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

### 运行容器

<div class="termy">

```console
$ cd todo-postgres-api

# Start service in background
$ docker-compose up -d
Creating network "todo-postgres-api_default" with the default driver
Creating volume "todo-postgres-api_postgres_data" with default driver
Pulling db (postgres:15)...
Creating todo-postgres-api_db_1 ... done
Building app
Creating todo-postgres-api_app_1 ... done

# Check service status
$ docker-compose ps
           Name                          Command              State           Ports
-------------------------------------------------------------------------------------
todo-postgres-api_app_1    uvicorn src.main:app --host=0.0.0.0 --port=8000   Up   0.0.0.0:8000->8000/tcp
todo-postgres-api_db_1     docker-entrypoint.sh postgres   Up   0.0.0.0:5432->5432/tcp

# Check log
$ docker-compose logs app
```

</div>

## 第 8 步:数据库迁移

### 使用 Alembic 创建初始迁移

<div class="termy">

```console
# Run migration inside container
$ docker-compose exec app alembic revision --autogenerate -m "Create items table"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'items'
Generating migration script /app/src/alembic/versions/001_create_items_table.py ... done

# Apply migration
$ docker-compose exec app alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> 001, Create items table
```

</div>

### 查看迁移文件

查看生成的迁移文件:

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

## 第 9 步:API 测试

### 基础 CRUD 测试

<div class="termy">

```console
# Create new item
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

# Get item list
$ curl "http://localhost:8000/items/"

# Get item list with pagination
$ curl "http://localhost:8000/items/?skip=0&limit=10"

# Search item
$ curl "http://localhost:8000/items/search?q=MacBook"

# Get item count
$ curl "http://localhost:8000/items/count"
{"total": 1}
```

</div>

### 进阶查询能力测试

<div class="termy">

```console
# Get item list with inactive items
$ curl "http://localhost:8000/items/?active_only=false"

# Update item
$ curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 2300000,
    "tax": 230000
  }'

# Soft delete item
$ curl -X DELETE "http://localhost:8000/items/1"

# Hard delete item
$ curl -X DELETE "http://localhost:8000/items/1?hard_delete=true"
```

</div>

## 第 10 步:进阶数据库特性

### 事务处理

```python
# Add to src/crud/items.py

from sqlalchemy.exc import SQLAlchemyError

async def create_items_batch(self, items_create: List[ItemCreate]) -> List[Item]:
    """Create multiple items in a transaction"""
    created_items = []

    try:
        for item_create in items_create:
            db_item = Item(**item_create.dict())
            self.db.add(db_item)
            created_items.append(db_item)

        await self.db.commit()

        # Refresh all items
        for item in created_items:
            await self.db.refresh(item)

        return created_items

    except SQLAlchemyError:
        await self.db.rollback()
        raise
```

### 关系型数据建模

```python
# Add to src/schemas/items.py

from sqlmodel import Relationship

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    description: Optional[str] = None

    # Set relationship
    items: List["Item"] = Relationship(back_populates="category")

class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # Add foreign key
    category_id: Optional[int] = Field(foreign_key="categories.id")

    # Set relationship
    category: Optional[Category] = Relationship(back_populates="items")
```

### 索引优化

```python
# Add to src/schemas/items.py

from sqlalchemy import Index

class Item(ItemBase, table=True):
    __tablename__ = "items"

    # ... existing fields ...

    # Set composite index
    __table_args__ = (
        Index('ix_items_price_active', 'price', 'is_active'),
        Index('ix_items_created_at', 'created_at'),
        Index('ix_items_name_description', 'name', 'description'),  # For full text search
    )
```

## 第 11 步:编写测试

### 数据库测试配置(`tests/conftest.py`)

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

# Test database engine
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
    # Create test table
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Provide session
    async with TestSessionLocal() as session:
        yield session

    # Delete table after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession):
    # Override dependency
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

### 集成测试(`tests/test_items.py`)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_read_item(client: AsyncClient):
    """Integration test for creating and reading item"""
    # Create item
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

    # Get created item
    item_id = created_item["id"]
    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200

    retrieved_item = response.json()
    assert retrieved_item["id"] == item_id
    assert retrieved_item["name"] == item_data["name"]

@pytest.mark.asyncio
async def test_item_pagination(client: AsyncClient):
    """Test pagination feature"""
    # Create multiple items
    for i in range(15):
        item_data = {
            "name": f"Item {i}",
            "description": f"Description {i}",
            "price": i * 1000,
            "tax": i * 100
        }
        await client.post("/items/", json=item_data)

    # Get first page
    response = await client.get("/items/?skip=0&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 10

    # Get second page
    response = await client.get("/items/?skip=10&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 5

@pytest.mark.asyncio
async def test_item_search(client: AsyncClient):
    """Test search feature"""
    # Create test items
    items = [
        {"name": "iPhone 15", "description": "Latest smartphone", "price": 1200000, "tax": 120000},
        {"name": "Galaxy S24", "description": "Samsung flagship", "price": 1100000, "tax": 110000},
        {"name": "MacBook Air", "description": "Apple notebook", "price": 1500000, "tax": 150000},
    ]

    for item in items:
        await client.post("/items/", json=item)

    # Search "iPhone"
    response = await client.get("/items/search?q=iPhone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "iPhone 15"

    # Search "smartphone" (description)
    response = await client.get("/items/search?q=smartphone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["description"] == "Latest smartphone"
```

### 运行测试

<div class="termy">

```console
# Run tests inside container
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

## 第 12 步:生产部署的考量

### 优化连接池

```python
# Add to src/core/config.py

class Settings(BaseSettings):
    # ... existing settings ...

    # Database connection pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 300  # 5 minutes

    # Query timeout
    DB_QUERY_TIMEOUT: int = 30

    # Connection retry settings
    DB_RETRY_ATTEMPTS: int = 3
    DB_RETRY_DELAY: int = 1
```

### 数据库监控

```python
# Add to src/core/db.py

import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log before query execution"""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Log after query execution"""
    total = time.time() - context._query_start_time
    if total > 1.0:  # Log slow queries (1 second or more)
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")
```

## 下一步

恭喜您完成了 PostgreSQL 数据库集成!接下来可以尝试:

1. **[Docker 容器化](docker-deployment.md)** —— 构建生产部署环境
2. **[自定义响应处理](custom-response-handling.md)** —— 进阶的 API 响应格式
<!-- 3. **[Building Authentication Systems](authentication-system.md)** - JWT-based user authentication -->
<!-- 4. **[Building Caching Systems](caching-system.md)** - Performance optimization with Redis -->

## 小结

在本教程中,我们用 PostgreSQL 与 SQLAlchemy 完成了:

- ✅ 集成 PostgreSQL 数据库
- ✅ 使用 SQLModel 实现 ORM
- ✅ 配置 Alembic 迁移系统
- ✅ 进阶的 CRUD 操作与查询优化
- ✅ 事务处理与数据一致性
- ✅ 分页、搜索与排序功能
- ✅ 集成测试与数据库测试
- ✅ 生产部署的考量

现在您可以构建出能在真实生产环境中使用的、稳健的、数据库驱动型 API!

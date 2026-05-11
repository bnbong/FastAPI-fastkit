# データベース統合 (PostgreSQL + SQLAlchemy)

PostgreSQL データベースと SQLAlchemy ORM を使い、本番環境で利用できる FastAPI アプリケーションを構築します。このチュートリアルでは `fastapi-psql-orm` テンプレートを使い、完全なデータベース統合システムを実装します。

## このチュートリアルで学ぶこと

- PostgreSQL データベースのセットアップと統合
- SQLAlchemy ORM によるデータモデリング
- Alembic を使ったデータベースマイグレーション
- Docker Compose による開発環境構築
- データベースのコネクションプール管理
- トランザクション処理とデータ整合性

## 前提条件

- [非同期 CRUD API チュートリアル](async-crud-api.md) を完了済み
- Docker と Docker Compose がインストール済み
- PostgreSQL の基礎知識
- SQLAlchemy ORM の基本概念の理解

## なぜ PostgreSQL と SQLAlchemy か

### JSON ファイルと PostgreSQL の比較

| 項目 | JSON ファイル | PostgreSQL |
|---|---|---|
| **パフォーマンス** | 限定的 | 高速なインデックス |
| **同時実行性** | ファイルロックの問題 | トランザクション対応 |
| **拡張性** | メモリ上限あり | 大規模データ処理 |
| **整合性** | 保証されない | ACID 保証 |
| **クエリ** | 全データ読込が必要 | 複雑なクエリに対応 |
| **バックアップ** | ファイルコピー | フルバックアップ / 復元 |

## ステップ 1: PostgreSQL + ORM プロジェクトの作成

`fastapi-psql-orm` テンプレートでプロジェクトを作成します:

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

## ステップ 2: プロジェクト構造の解析

生成されたプロジェクトは、完全なデータベース統合環境を提供します:

```
todo-postgres-api/
├── docker-compose.yml           # PostgreSQL コンテナの構成
├── Dockerfile                   # アプリケーションコンテナ
├── alembic.ini                  # Alembic 設定
├── template-config.yml          # テンプレート設定
├── scripts/
│   ├── pre-start.sh            # 起動前の初期化
│   └── test.sh                 # テスト実行スクリプト
├── src/
│   ├── main.py                 # FastAPI アプリ
│   ├── core/
│   │   ├── config.py           # 環境設定
│   │   └── db.py               # データベース接続設定
│   ├── api/
│   │   ├── deps.py             # 依存性注入
│   │   └── routes/
│   │       └── items.py        # API エンドポイント
│   ├── crud/
│   │   └── items.py            # データベース操作
│   ├── schemas/
│   │   └── items.py            # Pydantic モデル
│   ├── utils/
│   │   ├── backend_pre_start.py # バックエンド初期化
│   │   ├── init_data.py        # 初期データロード
│   │   └── tests_pre_start.py  # テスト準備
│   └── alembic/
│       ├── env.py              # Alembic 環境設定
│       └── versions/           # マイグレーションファイル
└── tests/
    ├── conftest.py             # テスト設定
    └── test_items.py           # API テスト
```

### 中核コンポーネント

1. **SQLModel**: SQLAlchemy + Pydantic 統合
2. **Alembic**: データベーススキーママイグレーション
3. **asyncpg**: 非同期 PostgreSQL ドライバ
4. **Docker Compose**: 開発環境のコンテナ化

## ステップ 3: データベース設定の理解

### データベース接続設定 (`src/core/db.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.core.config import settings

# 非同期 PostgreSQL エンジンの作成
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL ログを出力
    pool_size=20,         # コネクションプールのサイズ
    max_overflow=0,       # 追加で許可する接続数
    pool_pre_ping=True,   # 接続状態を確認
)

# 非同期セッションファクトリ
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_tables():
    """データベースのテーブルを作成"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """データベースセッションを提供 (依存性注入用)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 環境設定 (`src/core/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Todo PostgreSQL API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Todo management API using PostgreSQL"

    # データベース設定
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "todoapp"
    POSTGRES_PORT: int = 5432

    # テスト用データベース
    TEST_DATABASE_URL: Optional[str] = None

    # デバッグモード
    DEBUG: bool = False

    @property
    def DATABASE_URL(self) -> str:
        """PostgreSQL 接続 URL を生成"""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"

settings = Settings()
```

## ステップ 4: データモデルの定義

### SQLModel を使ったデータモデル (`src/schemas/items.py`)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# 共通フィールドの定義
class ItemBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0, description="Price must be greater than 0")
    tax: Optional[float] = Field(default=None, ge=0)
    is_active: bool = Field(default=True)

# データベーステーブルモデル
class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # インデックスの設定
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

# API リクエスト / レスポンスモデル
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

## ステップ 5: CRUD 操作の実装

### データベース CRUD ロジック (`src/crud/items.py`)

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
        """新しい item を作成"""
        db_item = Item(**item_create.dict())

        self.db.add(db_item)
        await self.db.commit()
        await self.db.refresh(db_item)

        return db_item

    async def get_by_id(self, item_id: int) -> Optional[Item]:
        """ID で item を取得"""
        statement = select(Item).where(Item.id == item_id)
        result = await self.db.execute(statement)
        return result.scalar_one_or_none()

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[Item]:
        """複数の item を取得 (ページネーション対応)"""
        statement = select(Item)

        if active_only:
            statement = statement.where(Item.is_active == True)

        statement = statement.offset(skip).limit(limit)
        result = await self.db.execute(statement)
        return result.scalars().all()

    async def update(self, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """item を更新"""
        # 更新データを準備
        update_data = item_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()

        # 更新を実行
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
        """item を削除 (論理削除)"""
        statement = (
            update(Item)
            .where(Item.id == item_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )

        result = await self.db.execute(statement)
        await self.db.commit()

        return result.rowcount > 0

    async def hard_delete(self, item_id: int) -> bool:
        """item を物理削除"""
        statement = delete(Item).where(Item.id == item_id)
        result = await self.db.execute(statement)
        await self.db.commit()

        return result.rowcount > 0

    async def search(self, query: str) -> List[Item]:
        """item を検索 (name、description)"""
        statement = select(Item).where(
            (Item.name.ilike(f"%{query}%")) |
            (Item.description.ilike(f"%{query}%"))
        ).where(Item.is_active == True)

        result = await self.db.execute(statement)
        return result.scalars().all()

    async def get_total_count(self, active_only: bool = True) -> int:
        """item の合計数を取得"""
        from sqlalchemy import func

        statement = select(func.count(Item.id))
        if active_only:
            statement = statement.where(Item.is_active == True)

        result = await self.db.execute(statement)
        return result.scalar()
```

## ステップ 6: API エンドポイントの実装

### 依存性注入の設定 (`src/api/deps.py`)

```python
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.crud.items import ItemCRUD

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """データベースセッションの依存性"""
    async for session in get_session():
        yield session

def get_item_crud(db: AsyncSession = Depends(get_db)) -> ItemCRUD:
    """Item CRUD の依存性"""
    return ItemCRUD(db)
```

### API ルーターの実装 (`src/api/routes/items.py`)

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
    """新しい item を作成"""
    return await crud.create(item_create)

@router.get("/", response_model=List[ItemResponse])
async def read_items(
    skip: int = Query(0, ge=0, description="Skip items"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum items to retrieve"),
    active_only: bool = Query(True, description="Only active items"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """item の一覧を取得 (ページネーション対応)"""
    return await crud.get_many(skip=skip, limit=limit, active_only=active_only)

@router.get("/search", response_model=List[ItemResponse])
async def search_items(
    q: str = Query(..., min_length=1, description="Search term"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """item を検索"""
    return await crud.search(q)

@router.get("/count")
async def get_items_count(
    active_only: bool = Query(True, description="Only active items"),
    crud: ItemCRUD = Depends(get_item_crud)
):
    """item の合計数を取得"""
    count = await crud.get_total_count(active_only)
    return {"total": count}

@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    crud: ItemCRUD = Depends(get_item_crud)
):
    """特定の item を取得"""
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
    """item を更新"""
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
    """item を削除"""
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

## ステップ 7: Docker コンテナの起動

### Docker Compose 設定の確認 (`docker-compose.yml`)

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

### コンテナの実行

<div class="termy">

```console
$ cd todo-postgres-api

# サービスをバックグラウンドで起動
$ docker-compose up -d
Creating network "todo-postgres-api_default" with the default driver
Creating volume "todo-postgres-api_postgres_data" with default driver
Pulling db (postgres:15)...
Creating todo-postgres-api_db_1 ... done
Building app
Creating todo-postgres-api_app_1 ... done

# サービス状態を確認
$ docker-compose ps
           Name                          Command              State           Ports
-------------------------------------------------------------------------------------
todo-postgres-api_app_1    uvicorn src.main:app --host=0.0.0.0 --port=8000   Up   0.0.0.0:8000->8000/tcp
todo-postgres-api_db_1     docker-entrypoint.sh postgres   Up   0.0.0.0:5432->5432/tcp

# ログを確認
$ docker-compose logs app
```

</div>

## ステップ 8: データベースマイグレーション

### Alembic で初回マイグレーションを作成

<div class="termy">

```console
# コンテナ内でマイグレーションを実行
$ docker-compose exec app alembic revision --autogenerate -m "Create items table"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'items'
Generating migration script /app/src/alembic/versions/001_create_items_table.py ... done

# マイグレーションを適用
$ docker-compose exec app alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> 001, Create items table
```

</div>

### マイグレーションファイルの確認

生成されたマイグレーションファイルを確認します:

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

## ステップ 9: API テスト

### 基本的な CRUD テスト

<div class="termy">

```console
# 新しい item を作成
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

# item の一覧を取得
$ curl "http://localhost:8000/items/"

# ページネーション付きで一覧を取得
$ curl "http://localhost:8000/items/?skip=0&limit=10"

# item を検索
$ curl "http://localhost:8000/items/search?q=MacBook"

# item の合計数を取得
$ curl "http://localhost:8000/items/count"
{"total": 1}
```

</div>

### 高度なクエリ機能のテスト

<div class="termy">

```console
# 非アクティブの item も含めて取得
$ curl "http://localhost:8000/items/?active_only=false"

# item を更新
$ curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 2300000,
    "tax": 230000
  }'

# item を論理削除
$ curl -X DELETE "http://localhost:8000/items/1"

# item を物理削除
$ curl -X DELETE "http://localhost:8000/items/1?hard_delete=true"
```

</div>

## ステップ 10: 高度なデータベース機能

### トランザクション処理

```python
# src/crud/items.py に追加

from sqlalchemy.exc import SQLAlchemyError

async def create_items_batch(self, items_create: List[ItemCreate]) -> List[Item]:
    """複数の item を 1 つのトランザクションで作成"""
    created_items = []

    try:
        for item_create in items_create:
            db_item = Item(**item_create.dict())
            self.db.add(db_item)
            created_items.append(db_item)

        await self.db.commit()

        # すべての item をリフレッシュ
        for item in created_items:
            await self.db.refresh(item)

        return created_items

    except SQLAlchemyError:
        await self.db.rollback()
        raise
```

### リレーショナルデータモデリング

```python
# src/schemas/items.py に追加

from sqlmodel import Relationship

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    description: Optional[str] = None

    # リレーションの設定
    items: List["Item"] = Relationship(back_populates="category")

class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # 外部キーの追加
    category_id: Optional[int] = Field(foreign_key="categories.id")

    # リレーションの設定
    category: Optional[Category] = Relationship(back_populates="items")
```

### インデックスの最適化

```python
# src/schemas/items.py に追加

from sqlalchemy import Index

class Item(ItemBase, table=True):
    __tablename__ = "items"

    # ... 既存フィールド ...

    # 複合インデックスの設定
    __table_args__ = (
        Index('ix_items_price_active', 'price', 'is_active'),
        Index('ix_items_created_at', 'created_at'),
        Index('ix_items_name_description', 'name', 'description'),  # 全文検索用
    )
```

## ステップ 11: テストの作成

### データベーステストの設定 (`tests/conftest.py`)

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

# テスト用データベースエンジン
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
    # テスト用テーブルを作成
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # セッションを提供
    async with TestSessionLocal() as session:
        yield session

    # テスト後にテーブルを削除
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession):
    # 依存性をオーバーライド
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

### 統合テスト (`tests/test_items.py`)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_read_item(client: AsyncClient):
    """item の作成と取得の統合テスト"""
    # item を作成
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

    # 作成した item を取得
    item_id = created_item["id"]
    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200

    retrieved_item = response.json()
    assert retrieved_item["id"] == item_id
    assert retrieved_item["name"] == item_data["name"]

@pytest.mark.asyncio
async def test_item_pagination(client: AsyncClient):
    """ページネーション機能のテスト"""
    # 複数の item を作成
    for i in range(15):
        item_data = {
            "name": f"Item {i}",
            "description": f"Description {i}",
            "price": i * 1000,
            "tax": i * 100
        }
        await client.post("/items/", json=item_data)

    # 最初のページを取得
    response = await client.get("/items/?skip=0&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 10

    # 2 ページ目を取得
    response = await client.get("/items/?skip=10&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 5

@pytest.mark.asyncio
async def test_item_search(client: AsyncClient):
    """検索機能のテスト"""
    # テスト用の item を作成
    items = [
        {"name": "iPhone 15", "description": "Latest smartphone", "price": 1200000, "tax": 120000},
        {"name": "Galaxy S24", "description": "Samsung flagship", "price": 1100000, "tax": 110000},
        {"name": "MacBook Air", "description": "Apple notebook", "price": 1500000, "tax": 150000},
    ]

    for item in items:
        await client.post("/items/", json=item)

    # 「iPhone」で検索
    response = await client.get("/items/search?q=iPhone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "iPhone 15"

    # 「smartphone」で検索 (description にヒット)
    response = await client.get("/items/search?q=smartphone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["description"] == "Latest smartphone"
```

### テストの実行

<div class="termy">

```console
# コンテナ内でテストを実行
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

## ステップ 12: 本番デプロイの考慮事項

### コネクションプールの最適化

```python
# src/core/config.py に追加

class Settings(BaseSettings):
    # ... 既存設定 ...

    # データベースコネクションプール設定
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 300  # 5 分

    # クエリタイムアウト
    DB_QUERY_TIMEOUT: int = 30

    # 接続リトライ設定
    DB_RETRY_ATTEMPTS: int = 3
    DB_RETRY_DELAY: int = 1
```

### データベース監視

```python
# src/core/db.py に追加

import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """クエリ実行前のログ"""
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """クエリ実行後のログ"""
    total = time.time() - context._query_start_time
    if total > 1.0:  # 遅いクエリをログ (1 秒以上)
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")
```

## 次のステップ

PostgreSQL データベース統合が完了しました! 次に試すこと:

1. **[Docker でのデプロイ](docker-deployment.md)** - 本番デプロイ環境の構築
2. **[カスタムレスポンス処理](custom-response-handling.md)** - 高度な API レスポンス形式
<!-- 3. **[Building Authentication Systems](authentication-system.md)** - JWT-based user authentication -->
<!-- 4. **[Building Caching Systems](caching-system.md)** - Performance optimization with Redis -->

## まとめ

このチュートリアルでは、PostgreSQL と SQLAlchemy を使って次を行いました:

- ✅ PostgreSQL データベースを統合
- ✅ SQLModel で ORM を実装
- ✅ Alembic マイグレーションシステムをセットアップ
- ✅ 高度な CRUD 操作とクエリ最適化
- ✅ トランザクション処理とデータ整合性
- ✅ ページネーション、検索、ソート機能
- ✅ 統合テストとデータベーステスト
- ✅ 本番デプロイの考慮事項

これで、本番環境でも使える堅牢なデータベース駆動 API を構築できます。

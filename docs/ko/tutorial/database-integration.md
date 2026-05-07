# 데이터베이스 통합 (PostgreSQL + SQLAlchemy)

PostgreSQL 데이터베이스와 SQLAlchemy ORM을 사용해 실제 운영 환경에서도 활용할 수 있는 FastAPI 애플리케이션을 구축합니다. 이 튜토리얼에서는 `fastapi-psql-orm` 템플릿으로 완전한 데이터베이스 통합 시스템을 구현합니다.

## 이 튜토리얼에서 배우는 내용

- PostgreSQL 데이터베이스 설정과 통합
- SQLAlchemy ORM으로 데이터 모델링
- Alembic으로 데이터베이스 마이그레이션
- Docker Compose로 개발 환경 구성
- 데이터베이스 커넥션 풀 관리
- 트랜잭션 처리와 데이터 무결성

## 사전 요구 사항

- [비동기 CRUD API 튜토리얼](async-crud-api.md) 완료
- Docker와 Docker Compose 설치
- PostgreSQL 기초 지식
- SQLAlchemy ORM 기본 개념 이해

## PostgreSQL과 SQLAlchemy가 필요한 이유

### JSON 파일 vs PostgreSQL 비교

| 항목 | JSON 파일 | PostgreSQL |
|----------|------------|------------|
| **성능** | 제한적 | 고성능 인덱싱 |
| **동시성** | 파일 잠금 문제 | 트랜잭션 지원 |
| **확장성** | 메모리 한계 | 대규모 데이터 처리 |
| **무결성** | 보장되지 않음 | ACID 속성 보장 |
| **쿼리** | 전체 데이터 로딩 필요 | 복잡한 쿼리 지원 |
| **백업** | 파일 복사 | 완전한 백업 / 복구 |

## 1단계: PostgreSQL + ORM 프로젝트 생성

`fastapi-psql-orm` 템플릿으로 프로젝트를 만듭니다:

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

## 2단계: 프로젝트 구조 분석

생성된 프로젝트는 완전한 데이터베이스 통합 환경을 제공합니다:

```
todo-postgres-api/
├── docker-compose.yml           # PostgreSQL 컨테이너 구성
├── Dockerfile                   # 애플리케이션 컨테이너
├── alembic.ini                  # Alembic 설정
├── template-config.yml          # 템플릿 설정
├── scripts/
│   ├── pre-start.sh            # 시작 전 초기화
│   └── test.sh                 # 테스트 실행 스크립트
├── src/
│   ├── main.py                 # FastAPI 애플리케이션
│   ├── core/
│   │   ├── config.py           # 환경 설정
│   │   └── db.py               # 데이터베이스 연결 설정
│   ├── api/
│   │   ├── deps.py             # 의존성 주입
│   │   └── routes/
│   │       └── items.py        # API 엔드포인트
│   ├── crud/
│   │   └── items.py            # 데이터베이스 작업
│   ├── schemas/
│   │   └── items.py            # Pydantic 모델
│   ├── utils/
│   │   ├── backend_pre_start.py # 백엔드 초기화
│   │   ├── init_data.py        # 초기 데이터 로딩
│   │   └── tests_pre_start.py  # 테스트 준비
│   └── alembic/
│       ├── env.py              # Alembic 환경 설정
│       └── versions/           # 마이그레이션 파일
└── tests/
    ├── conftest.py             # 테스트 구성
    └── test_items.py           # API 테스트
```

### 핵심 구성 요소

1. **SQLModel**: SQLAlchemy + Pydantic 통합
2. **Alembic**: 데이터베이스 스키마 마이그레이션
3. **asyncpg**: 비동기 PostgreSQL 드라이버
4. **Docker Compose**: 개발 환경 컨테이너화

## 3단계: 데이터베이스 설정 이해

### 데이터베이스 연결 설정 (`src/core/db.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.core.config import settings

# 비동기 PostgreSQL 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # SQL 로그 출력
    pool_size=20,         # 커넥션 풀 크기
    max_overflow=0,       # 추가 허용 커넥션 수
    pool_pre_ping=True,   # 연결 상태 확인
)

# 비동기 세션 팩토리
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_tables():
    """Create database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    """Provide database session (for dependency injection)"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 환경 설정 (`src/core/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Todo PostgreSQL API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Todo management API using PostgreSQL"

    # 데이터베이스 설정
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "todoapp"
    POSTGRES_PORT: int = 5432

    # 테스트 데이터베이스
    TEST_DATABASE_URL: Optional[str] = None

    # 디버그 모드
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

## 4단계: 데이터 모델 정의

### SQLModel 을 사용한 데이터 모델 (`src/schemas/items.py`)

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# 공통 필드 정의
class ItemBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0, description="Price must be greater than 0")
    tax: Optional[float] = Field(default=None, ge=0)
    is_active: bool = Field(default=True)

# 데이터베이스 테이블 모델
class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # 인덱스 설정
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

# API 요청 / 응답 모델
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

## 5단계: CRUD 작업 구현

### 데이터베이스 CRUD 로직 (`src/crud/items.py`)

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
        # 갱신 데이터 준비
        update_data = item_update.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()

        # 갱신 실행
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

## 6단계: API 엔드포인트 구현

### 의존성 주입 설정 (`src/api/deps.py`)

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

### API 라우터 구현 (`src/api/routes/items.py`)

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

## 7단계: Docker 컨테이너 실행

### Docker Compose 설정 확인 (`docker-compose.yml`)

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

### 컨테이너 실행

<div class="termy">

```console
$ cd todo-postgres-api

# 백그라운드로 서비스 시작
$ docker-compose up -d
Creating network "todo-postgres-api_default" with the default driver
Creating volume "todo-postgres-api_postgres_data" with default driver
Pulling db (postgres:15)...
Creating todo-postgres-api_db_1 ... done
Building app
Creating todo-postgres-api_app_1 ... done

# 서비스 상태 확인
$ docker-compose ps
           Name                          Command              State           Ports
-------------------------------------------------------------------------------------
todo-postgres-api_app_1    uvicorn src.main:app --host=0.0.0.0 --port=8000   Up   0.0.0.0:8000->8000/tcp
todo-postgres-api_db_1     docker-entrypoint.sh postgres   Up   0.0.0.0:5432->5432/tcp

# 로그 확인
$ docker-compose logs app
```

</div>

## 8단계: 데이터베이스 마이그레이션

### Alembic으로 초기 마이그레이션 생성

<div class="termy">

```console
# 컨테이너 내부에서 마이그레이션 실행
$ docker-compose exec app alembic revision --autogenerate -m "Create items table"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'items'
Generating migration script /app/src/alembic/versions/001_create_items_table.py ... done

# 마이그레이션 적용
$ docker-compose exec app alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> 001, Create items table
```

</div>

### 마이그레이션 파일 확인

생성된 마이그레이션 파일을 확인합니다:

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

## 9단계: API 테스트

### 기본 CRUD 테스트

<div class="termy">

```console
# 새 item 생성
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

# item 목록 조회
$ curl "http://localhost:8000/items/"

# 페이지네이션을 적용한 item 목록 조회
$ curl "http://localhost:8000/items/?skip=0&limit=10"

# item 검색
$ curl "http://localhost:8000/items/search?q=MacBook"

# item 개수 조회
$ curl "http://localhost:8000/items/count"
{"total": 1}
```

</div>

### 고급 쿼리 기능 테스트

<div class="termy">

```console
# 비활성 item 까지 포함해 목록 조회
$ curl "http://localhost:8000/items/?active_only=false"

# item 갱신
$ curl -X PUT "http://localhost:8000/items/1" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 2300000,
    "tax": 230000
  }'

# 소프트 삭제
$ curl -X DELETE "http://localhost:8000/items/1"

# 하드 삭제
$ curl -X DELETE "http://localhost:8000/items/1?hard_delete=true"
```

</div>

## 10단계: 고급 데이터베이스 기능

### 트랜잭션 처리

```python
# src/crud/items.py 에 추가

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

        # 모든 item 새로고침
        for item in created_items:
            await self.db.refresh(item)

        return created_items

    except SQLAlchemyError:
        await self.db.rollback()
        raise
```

### 관계형 데이터 모델링

```python
# src/schemas/items.py 에 추가

from sqlmodel import Relationship

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    description: Optional[str] = None

    # 관계 설정
    items: List["Item"] = Relationship(back_populates="category")

class Item(ItemBase, table=True):
    __tablename__ = "items"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    # 외래 키 추가
    category_id: Optional[int] = Field(foreign_key="categories.id")

    # 관계 설정
    category: Optional[Category] = Relationship(back_populates="items")
```

### 인덱스 최적화

```python
# src/schemas/items.py 에 추가

from sqlalchemy import Index

class Item(ItemBase, table=True):
    __tablename__ = "items"

    # ... 기존 필드 ...

    # 복합 인덱스 설정
    __table_args__ = (
        Index('ix_items_price_active', 'price', 'is_active'),
        Index('ix_items_created_at', 'created_at'),
        Index('ix_items_name_description', 'name', 'description'),  # 전문 검색용
    )
```

## 11단계: 테스트 작성

### 데이터베이스 테스트 구성 (`tests/conftest.py`)

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

# 테스트 데이터베이스 엔진
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
    # 테스트 테이블 생성
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # 세션 제공
    async with TestSessionLocal() as session:
        yield session

    # 테스트 후 테이블 삭제
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest.fixture
async def client(db_session: AsyncSession):
    # 의존성 오버라이드
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
```

### 통합 테스트 (`tests/test_items.py`)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_and_read_item(client: AsyncClient):
    """Integration test for creating and reading item"""
    # item 생성
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

    # 생성된 item 조회
    item_id = created_item["id"]
    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200

    retrieved_item = response.json()
    assert retrieved_item["id"] == item_id
    assert retrieved_item["name"] == item_data["name"]

@pytest.mark.asyncio
async def test_item_pagination(client: AsyncClient):
    """Test pagination feature"""
    # 여러 item 생성
    for i in range(15):
        item_data = {
            "name": f"Item {i}",
            "description": f"Description {i}",
            "price": i * 1000,
            "tax": i * 100
        }
        await client.post("/items/", json=item_data)

    # 첫 페이지 조회
    response = await client.get("/items/?skip=0&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 10

    # 두 번째 페이지 조회
    response = await client.get("/items/?skip=10&limit=10")
    assert response.status_code == 200

    items = response.json()
    assert len(items) == 5

@pytest.mark.asyncio
async def test_item_search(client: AsyncClient):
    """Test search feature"""
    # 테스트 item 생성
    items = [
        {"name": "iPhone 15", "description": "Latest smartphone", "price": 1200000, "tax": 120000},
        {"name": "Galaxy S24", "description": "Samsung flagship", "price": 1100000, "tax": 110000},
        {"name": "MacBook Air", "description": "Apple notebook", "price": 1500000, "tax": 150000},
    ]

    for item in items:
        await client.post("/items/", json=item)

    # "iPhone" 검색
    response = await client.get("/items/search?q=iPhone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "iPhone 15"

    # "smartphone" 검색 (description)
    response = await client.get("/items/search?q=smartphone")
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 1
    assert results[0]["description"] == "Latest smartphone"
```

### 테스트 실행

<div class="termy">

```console
# 컨테이너 내부에서 테스트 실행
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

## 12단계: 프로덕션 배포 고려 사항

### 커넥션 풀 최적화

```python
# src/core/config.py 에 추가

class Settings(BaseSettings):
    # ... 기존 설정 ...

    # 데이터베이스 커넥션 풀 설정
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0
    DB_POOL_PRE_PING: bool = True
    DB_POOL_RECYCLE: int = 300  # 5분

    # 쿼리 타임아웃
    DB_QUERY_TIMEOUT: int = 30

    # 커넥션 재시도 설정
    DB_RETRY_ATTEMPTS: int = 3
    DB_RETRY_DELAY: int = 1
```

### 데이터베이스 모니터링

```python
# src/core/db.py 에 추가

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
    if total > 1.0:  # 느린 쿼리 (1초 이상) 기록
        logger.warning(f"Slow query: {total:.2f}s - {statement[:100]}...")
```

## 다음 단계

PostgreSQL 데이터베이스 통합을 마쳤습니다! 다음으로 시도해 볼 만한 것들:

1. **[Docker 컨테이너화](docker-deployment.md)** — 프로덕션 배포 환경 구축
2. **[커스텀 응답 처리](custom-response-handling.md)** — 고급 API 응답 형식
<!-- 3. **[Building Authentication Systems](authentication-system.md)** - JWT-based user authentication -->
<!-- 4. **[Building Caching Systems](caching-system.md)** - Performance optimization with Redis -->

## 요약

이 튜토리얼에서는 PostgreSQL과 SQLAlchemy를 사용해 다음 작업을 진행했습니다:

- ✅ PostgreSQL 데이터베이스 통합
- ✅ SQLModel 로 ORM 구현
- ✅ Alembic 마이그레이션 시스템 구축
- ✅ 고급 CRUD 작업과 쿼리 최적화
- ✅ 트랜잭션 처리와 데이터 무결성
- ✅ 페이지네이션, 검색, 정렬 기능
- ✅ 통합 테스트와 데이터베이스 테스트
- ✅ 프로덕션 배포 고려 사항

이제 실제 운영 환경에서도 쓸 수 있는 견고한 데이터베이스 기반 API를 구축할 수 있습니다!

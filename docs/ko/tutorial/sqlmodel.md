# `fastapi-sqlmodel`로 비동기 영속성 구현

각 개념을 **한 번만** 정의하는, 데이터베이스 기반 API를 만들어 봅니다.
SQLModel 클래스는 SQLAlchemy 테이블이면서 동시에 pydantic 스키마이기도 하므로,
컬럼 하나를 추가하려고 파일 네 개를 고칠 필요가 없습니다. 이 튜토리얼에서는
`fastapi-sqlmodel` 템플릿을 따라가면서 모델 계층 구조, 제네릭 CRUD 베이스,
페이지네이션 응답, 비동기 Alembic 마이그레이션, 그리고 직접 도메인을 추가하는
방법을 살펴봅니다.

## 배우는 내용

- `fastkit startdemo fastapi-sqlmodel`로 프로젝트를 생성하는 방법
- `ItemBase` → `Item` / `ItemCreate` / `ItemUpdate` / `ItemPublic` 구조가
  스키마 중복을 없애는 방식
- `CRUDBase`가 기본으로 제공하는 기능과 이를 확장하는 위치
- `Page[T]` 목록 엔벨로프와 그 한도가 적용되는 위치
- 비동기 Alembic 마이그레이션 실행과 SQLite에서 PostgreSQL로 전환하는 방법

## 사전 요구 사항

- Python 3.12+
- FastAPI-fastkit 설치 (`pip install fastapi-fastkit`)
- `async`/`await`와 기본적인 SQL 개념에 익숙함

동기 방식의 Compose 기반 PostgreSQL 스택을 원한다면
`fastapi-psql-orm`을 사용하는 [데이터베이스 통합](database-integration.md)을
참고하세요.

## 1단계: 생성과 실행

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
$ bash scripts/run-server.sh     # 또는: uvicorn src.app.main:app --reload
```

기본 `DATABASE_URL`은 `sqlite+aiosqlite:///./app.db`이므로 데이터베이스
서버를 따로 설치할 필요가 없습니다. API 문서는
<http://127.0.0.1:8000/docs>에서 확인할 수 있습니다.

## 2단계: 생성된 트리

```
catalog-api/
├── pyproject.toml              # PEP 621 메타데이터 + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env
├── scripts/
│   ├── format.sh  lint.sh  migrate.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI 앱 + lifespan
│       ├── core/config.py      # pydantic-settings
│       ├── db/
│       │   ├── session.py      # 비동기 엔진, get_session 의존성
│       │   └── base.py         # Alembic용 메타데이터 집계
│       ├── crud/
│       │   ├── base.py         # 제네릭 CRUDBase
│       │   └── pagination.py   # Page[T] 엔벨로프
│       ├── alembic/
│       │   ├── env.py          # 비동기 마이그레이션 환경
│       │   └── versions/0001_create_items_table.py
│       ├── api/
│       │   ├── router.py       # health와 도메인 라우터를 집계
│       │   └── health.py       # GET /health
│       └── domains/items/      # 예제 도메인
│           ├── models.py       # Item 테이블 + Create/Update/Public 스키마
│           ├── crud.py         # ItemCRUD(CRUDBase)
│           └── router.py       # FastAPI 라우터
└── tests/
    ├── conftest.py  test_health.py  test_items.py  test_crud_base.py
```

도메인 폴더에 *없는* 것에 주목하세요. `models.py`와 분리된 `schemas.py`가
없고, 도메인마다 작성하는 repository 보일러플레이트도 없습니다. 앞의 것은
SQLModel이, 뒤의 것은 `CRUDBase`가 대신합니다.

## 3단계: 개념마다 모델 정의는 하나

`src/app/domains/items/models.py`를 열어 보세요. 모든 클래스가 하나의 베이스
클래스에서 파생됩니다:

```python
class ItemBase(SQLModel):
    """Fields shared by the table and every request/response schema."""
    name: str = Field(min_length=1, max_length=128, index=True)
    description: str | None = Field(default=None, max_length=512)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemBase, table=True):        # 실제 테이블
    __tablename__ = "items"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)


class ItemCreate(ItemBase): ...          # POST 본문: 서버가 부여하는 필드 없음


class ItemUpdate(SQLModel):              # PATCH 본문: 모든 필드가 선택 사항
    name: str | None = Field(default=None, min_length=1, max_length=128)
    ...


class ItemPublic(ItemBase):              # 응답: 베이스 + 서버가 부여하는 필드
    id: int
    created_at: datetime
```

클래스는 네 개이고 각자 맡은 일이 다르지만, 필드가 정의된 곳은 한 군데뿐입니다:

| 클래스       | 역할                          | 분리한 이유 |
|--------------|-------------------------------|-------------------|
| `ItemBase`   | 공통 필드 정의                | 단일 진실 공급원(single source of truth) |
| `Item`       | 데이터베이스 테이블           | `id`, `created_at` 추가 |
| `ItemCreate` | `POST` 요청 본문              | `id`를 받으면 안 됨 |
| `ItemUpdate` | `PATCH` 요청 본문             | 모든 필드가 선택 사항 |
| `ItemPublic` | 응답 본문                     | 서버가 부여한 필드를 노출 |

**얻는 이점:** `sku` 컬럼을 추가하려면 `ItemBase`에 한 줄만 추가하면 됩니다.
그러면 테이블에 컬럼이 생기고, 생성 요청 본문이 그 값을 받으며, 응답에도
그 값이 포함됩니다. 다른 곳은 고칠 필요가 없습니다. 다만 `ItemUpdate`는
의도적으로 명시적인 형태를 유지합니다. 부분 수정의 의미는 자동으로 파생되는
것이 아니라 직접 결정해야 하는 사항이기 때문입니다.

## 4단계: 다시 작성할 필요 없는 CRUD

`src/app/crud/base.py`는 테이블 모델과 두 입력 스키마를 타입 매개변수로 받는
제네릭 클래스입니다:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, session, obj_id) -> ModelType | None: ...
    async def list(self, session, *, offset=0, limit=20) -> Sequence[ModelType]: ...
    async def count(self, session) -> int: ...
    async def create(self, session, obj_in) -> ModelType: ...
    async def update(self, session, db_obj, obj_in) -> ModelType: ...
    async def delete(self, session, db_obj) -> None: ...
```

꼭 이해해 둘 세부 사항이 하나 있습니다. `update`는 `exclude_unset=True`를
사용합니다:

```python
changes: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
```

바로 이 설정 덕분에 `PATCH`가 실제로 부분 수정으로 동작합니다. 클라이언트가
보내지 않은 필드는 딕셔너리에 들어가지 않으므로 기록되지도 않습니다.
`exclude_unset`이 없다면 `PATCH`는 건드리지 않은 컬럼까지 스키마 기본값으로
조용히 덮어쓰게 됩니다.

도메인은 베이스를 상속하고, 그 도메인에만 필요한 기능만 추가합니다:

```python
class ItemCRUD(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """CRUD for Item, extended with a name search."""

    async def search_by_name(self, session, term, *, limit=20):
        statement = select(Item).where(Item.name.like(f"%{term}%")).limit(limit)
        result = await session.exec(statement)
        return result.all()


item_crud = ItemCRUD(Item)
```

## 5단계: 페이지네이션된 목록

목록 엔드포인트는 배열을 그대로 반환하지 않고 `Page[T]` 엔벨로프로 감싸서
반환합니다:

```json
{"items": [...], "total": 42, "offset": 0, "limit": 20}
```

한도를 제한하는 작업은 클라이언트가 아니라 라우터에서 이루어집니다:

```python
limit: int = Query(default=settings.DEFAULT_PAGE_LIMIT, ge=1)
...
limit = min(limit, settings.MAX_PAGE_LIMIT)
```

따라서 `?limit=100000`을 보내더라도 요청 하나가 전체 테이블 스캔으로 이어지지
않습니다. `Page`는 `offset`, `len(items)`, `total`로부터 계산되는 `has_next`
프로퍼티도 제공합니다. 대개 프런트엔드가 실제로 필요로 하는 값이 바로 이
값입니다.

items 도메인이 제공하는 엔드포인트는 다음과 같습니다:

| 메서드 | 엔드포인트                | 설명                           |
|--------|---------------------------|--------------------------------|
| GET    | `/api/v1/health`          | Liveness probe                 |
| GET    | `/api/v1/items`           | item 목록 조회 (`offset`, `limit`) |
| GET    | `/api/v1/items/{item_id}` | item 하나 조회                 |
| POST   | `/api/v1/items`           | item 생성 (`201`)              |
| PATCH  | `/api/v1/items/{item_id}` | item 부분 수정                 |
| DELETE | `/api/v1/items/{item_id}` | item 삭제 (`204`)              |

직접 호출해 보세요:

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
    -H 'Content-Type: application/json' \
    -d '{"name": "Keyboard", "price": 89.0}'

$ curl 'http://127.0.0.1:8000/api/v1/items?offset=0&limit=5'
```

## 6단계: 처음부터 끝까지 비동기

`src/app/db/session.py`는 프로세스마다 `AsyncEngine`을 하나 만들고, 요청
범위의 세션을 제공합니다:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

라우터는 이 함수에 의존하고(`session: AsyncSession = Depends(get_session)`),
`CRUDBase`는 세션을 첫 번째 인자로 받으며, 모든 데이터베이스 호출은
`await`로 실행됩니다. 요청 경로에서 I/O 때문에 이벤트 루프가 블로킹되는
곳은 없습니다.

`create_db_and_tables()`도 이 파일에 있으며 앱의 `lifespan`에서 호출됩니다.
이 함수는 기본 SQLite 구성과 테스트를 편하게 하려고 둔 것입니다. Alembic이
스키마를 관리하기 시작하면 `CREATE_TABLES_ON_STARTUP=false`로 설정하세요.

## 7단계: 도메인 추가

1. `items`와 같은 구조로 `src/app/domains/<your_domain>/`을 만듭니다
   (`models.py`, `crud.py`, `router.py`).
2. **`src/app/db/base.py`에서 테이블 모델을 import합니다.** 잊기 쉽고, 잊었을
   때 원인을 찾기 어려운 단계입니다. Alembic autogenerate와
   `create_db_and_tables`는 import된 모델만 인식하기 때문에, import를 빠뜨리면
   오류가 나는 대신 빈 마이그레이션이 생성됩니다.
3. `src/app/api/router.py`에 라우터를 등록합니다. `# fastkit:imports`와
   `# fastkit:routes` 앵커는 `fastkit addroute`가 코드를 삽입하는 위치를
   표시하므로, 직접 작성하는 코드도 같은 위치에 넣으세요.
4. 마이그레이션을 생성합니다:
   `alembic revision --autogenerate -m "add <domain>"`.
5. `tests/test_items.py`와 같은 형태로 `tests/test_<your_domain>.py`를 추가합니다.

## 8단계: 마이그레이션과 PostgreSQL

`src/app/alembic/env.py`에 있는 Alembic 환경은 비동기로 동작하므로, 앱과
같은 드라이버 스택을 사용해 실행됩니다. 평소에는 다음과 같이 사용합니다:

```console
$ bash scripts/migrate.sh                                  # upgrade head
$ alembic revision --autogenerate -m "add sku to items"    # 모델을 변경한 뒤
```

데이터베이스를 바꾸려면 URL을 변경하고 드라이버를 설치하면 됩니다:

```console
$ uv pip install "asyncpg>=0.31.0"
$ export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/app"
$ bash scripts/migrate.sh
```

모델, CRUD, 라우터는 전혀 바뀌지 않습니다. 드라이버를 `create_engine` 뒤에
감춰 두는 이유가 바로 이것입니다.

## 9단계: 테스트

```console
$ bash scripts/test.sh    # 또는: pytest
```

각 테스트는 새로 만든 인메모리 SQLite 데이터베이스에서 실행됩니다.
마이그레이션도, 픽스처 파일도, 테스트 사이의 정리 작업도 필요하지 않습니다.
`test_crud_base.py`는 제네릭 베이스를 직접 검증합니다. 베이스를 확장하기 전에
읽어 볼 만한 파일입니다. `exclude_unset` 동작과, 여러분의 도메인이 그대로
물려받는 count/offset 계약이 이 파일에 기록되어 있기 때문입니다.

## 정리

- **생성**: `fastkit startdemo fastapi-sqlmodel` →
  `bash scripts/migrate.sh` → `bash scripts/run-server.sh`.
- **모델**: `ItemBase`가 필드를 보유하고 테이블과 입출력 스키마가 이를
  상속하므로, 새 컬럼은 한 번만 선언합니다.
- **CRUD**: `CRUDBase`가 get / list / count / create / update / delete를
  제공하고, 도메인은 이를 상속해 자신만의 쿼리를 추가합니다.
- **목록**: `Page[T]` 엔벨로프를 사용하며, 한도는 서버에서 제한합니다.
- **스키마**: 비동기 Alembic을 사용합니다. 새 모델은 `src/app/db/base.py`에서
  import해야 한다는 점을 기억하세요.
- **데이터베이스**: 기본값은 SQLite이고, `DATABASE_URL`을 변경하고 `asyncpg`를
  설치하면 PostgreSQL을 사용할 수 있습니다.

## 다음 단계

- [JWT 인증](auth-jwt.md): 이 데이터 계층 앞에 계정과 보호된 라우트를
  추가합니다.
- [도메인 지향 프로젝트](domain-starter.md): 두 템플릿이 공유하는 레이아웃을
  데이터베이스 없이 다룹니다.
- [어떤 스타터를 선택해야 할까?](../user-guide/choosing-a-starter.md)

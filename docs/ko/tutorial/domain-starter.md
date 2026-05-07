# `fastapi-domain-starter`로 도메인 지향 FastAPI

권장 기본 레이아웃인 `src/app/domains/` 아래 **비즈니스 개념별 폴더 구조**를 사용해 중간 규모 FastAPI 서비스를 구축합니다. 이 튜토리얼에서는 `fastapi-domain-starter` 템플릿을 처음부터 끝까지 따라가며, 프로젝트 생성 방법과 각 최상위 패키지의 역할, 번들된 `items` 예제가 연결되는 방식, 다음 도메인을 추가하는 방법까지 살펴봅니다.

## 배우는 내용

- `fastkit startdemo fastapi-domain-starter`로 프로젝트 생성
- 레이아웃에서 `core`, `db`, `domains`, `tests`가 맡는 역할
- 한 도메인이 router → service → repository → schemas → models 로 분할되는 방식
- 새 도메인 추가의 계약 (items 폴더 복사, 라우터 등록)
- 번들된 `/health` 엔드포인트와 `/api/v1/items` CRUD 가 앱에 어떻게 연결되는지

## 사전 요구 사항

- Python 3.12+
- FastAPI-fastkit 설치 (`pip install fastapi-fastkit`)
- 기본적인 FastAPI 개념에 익숙함 (path operation, pydantic 스키마, 의존성)

처음 만드는 FastAPI 프로젝트라면 [기본 API 서버 구축](basic-api-server.md)부터 시작하세요. 그 튜토리얼은 더 단순한 `fastapi-default` 템플릿을 사용합니다.

## 1단계: 프로젝트 생성

```console
$ fastkit startdemo fastapi-domain-starter
Enter the project name: orders-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Domain-oriented orders service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

`fastkit`이 템플릿을 복사하고, 플레이스홀더를 채우고, 가상 환경을 만들고, 의존성을 설치합니다. 작업이 끝나면 바로 프로젝트 안으로 들어가 보세요:

```console
$ cd orders-api
$ bash scripts/run-server.sh    # 또는: uvicorn src.app.main:app --reload
```

API 문서는 <http://127.0.0.1:8000/docs>에서 확인할 수 있습니다.

## 2단계: 생성된 트리

```
orders-api/
├── README.md
├── pyproject.toml              # PEP 621 메타데이터 + [tool.fastapi-fastkit]
├── requirements.txt            # 핀 고정 의존성 (템플릿이 두 파일을 모두 제공하며, 패키지를 추가하면서 직접 유지보수)
├── .env                        # SECRET_KEY, ENVIRONMENT
├── .gitignore
├── scripts/
│   ├── format.sh               # black + isort
│   ├── lint.sh                 # black --check + isort --check + mypy
│   ├── run-server.sh           # uvicorn src.app.main:app --reload
│   └── test.sh                 # pytest
├── src/
│   ├── __init__.py
│   └── app/                    # 애플리케이션 패키지
│       ├── __init__.py
│       ├── main.py             # FastAPI() + 미들웨어 + api_router 포함
│       ├── core/               # 횡단 관심 설정
│       │   ├── __init__.py
│       │   └── config.py       # pydantic-settings (PROJECT_NAME, CORS, ...)
│       ├── db/                 # 영속성 추상화
│       │   ├── __init__.py
│       │   └── memory.py       # InMemoryStore[T] 제네릭 키-값 저장소
│       ├── api/                # 전송 계층 라우팅
│       │   ├── __init__.py
│       │   ├── health.py       # GET /health
│       │   └── router.py       # health + 모든 도메인 라우터 집계
│       └── domains/            # 비즈니스 개념 (각각 폴더 하나)
│           ├── __init__.py
│           └── items/          # 예제 도메인
│               ├── __init__.py
│               ├── models.py       # @dataclass Item (엔티티)
│               ├── schemas.py      # ItemCreate, ItemRead (pydantic)
│               ├── repository.py   # InMemoryStore 위의 ItemRepository
│               ├── service.py      # ItemService + ItemNotFoundError
│               └── router.py       # APIRouter(prefix="/items")
└── tests/
    ├── __init__.py
    ├── conftest.py             # TestClient 픽스처, 스토어 리셋
    ├── test_health.py
    └── test_items.py
```

먼저 기억해 둘 핵심은 두 가지입니다:

1. **`src/app/`**은 **애플리케이션 패키지**입니다. 런타임이 import하는 모든 것이 여기 있고, 테스트도 여기서 import합니다 (`from src.app.main import app`). 바깥쪽 `src/`는 프로젝트를 `pip install` 가능한 패키지로 유지하기 위해 존재합니다.
2. **`src/app/domains/<concept>/`**는 **개념별 슬라이스**입니다. 각 비즈니스 개념(items, orders, users, ...)이 자기만의 router / service / repository / schemas / models를 갖고, 해당 개념과 관련된 코드를 그 안에 모아 둡니다.

## 3단계: 각 최상위 패키지의 역할

### `src/app/core/` — 설정

여기에는 여러 도메인에서 공통으로 쓰는 애플리케이션 설정이 들어갑니다. 번들된 `config.py`는 `.env` / 환경 변수에서 값을 읽는 pydantic-settings `Settings` 클래스를 제공합니다:

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

`main.py`는 `settings.PROJECT_NAME`, `settings.API_V1_PREFIX`, `settings.all_cors_origins`를 읽어 FastAPI 앱을 구성합니다.

**`core/`에 추가할 대상:** 특정 도메인에 속하지 않는 모든 공통 요소입니다. 전역 설정, 구조화 로깅, 사용자 정의 미들웨어, 보안 헬퍼 등이 여기에 들어갑니다.

### `src/app/db/` — 영속성 경계

데이터 저장소에 대한 추상화를 담는 영역입니다. 스타터에는 `memory.py`가 함께 들어 있으며, 엔티티 타입별로 쓸 수 있는 프로세스 로컬 `InMemoryStore[T]`를 제공합니다. 각 도메인의 repository는 이 `InMemoryStore`를 감싸기 때문에, 나중에 SQLAlchemy나 비동기 드라이버로 바꾸더라도 repository만 다시 작성하면 됩니다.

```python
class InMemoryStore(Generic[T]):
    def list(self) -> Iterable[T]: ...
    def get(self, id_: int) -> Optional[T]: ...
    def add(self, item: T) -> int: ...
    def replace(self, id_: int, item: T) -> bool: ...
    def delete(self, id_: int) -> bool: ...
    def clear(self) -> None: ...
```

**`db/`를 확장할 시점:** `InMemoryStore` 대신 실제 데이터베이스를 쓸 때입니다. 이때는 데이터베이스 세션 팩토리가 들어 있는 `session.py`를 추가하세요. 도메인 repository의 외부 인터페이스가 바뀌지 않도록 공개 메서드 형태(`list` / `get` / `add` / ...)는 최대한 그대로 유지하는 편이 좋습니다.

### `src/app/api/` — 전송 라우팅

이 영역은 크게 두 부분으로 나뉩니다:

- `health.py` — `{"status": "ok"}`를 반환하는 `GET /health`를 제공하는 작은 `APIRouter`입니다. 부수 효과가 없어 liveness probe로 쓰기 좋습니다.
- `router.py` — **최상위 집계기**입니다. health 라우터와 모든 도메인 라우터를 한곳에 모으고, 합쳐진 `api_router`를 `/api/v1` 아래 FastAPI 앱에 마운트합니다:

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

**굳이 여기서 모으는 이유:** 새 도메인을 추가할 때 라우터 등록을 위해 `src/app/api/router.py`만 수정하면 되기 때문입니다. `main.py`는 건드릴 일이 거의 없어집니다.

### `src/app/domains/<concept>/` — 비즈니스 슬라이스

프로젝트가 자라면 대부분의 코드가 여기 살게 됩니다. 각 도메인은 다섯 개의 파일을 소유합니다:

| 파일 | 역할 |
|---|---|
| `models.py` | 도메인 엔티티 (스타터에서는 `@dataclass`; 추후 SQLAlchemy / SQLModel 가능). 와이어 포맷이 아닌 내부 모양. |
| `schemas.py` | API 입출력 스키마 (pydantic). 와이어 포맷이 도메인 로직을 건드리지 않고 진화할 수 있도록 엔티티와 분리. |
| `repository.py` | 데이터 접근. 스토어를 item 타입화된 메서드로 감쌈. 영속성을 갈아끼우는 봉합선. |
| `service.py` | 비즈니스 로직. 라우터는 `service` 를 호출하지, 절대 `repository` 를 직접 호출하지 않음. 도메인 고유 예외 (예: `ItemNotFoundError`) 도 여기 위치. |
| `router.py` | HTTP 전송. pydantic 스키마 ↔ service 호출을 변환; 도메인 예외를 `HTTPException` 으로 변환. |

**의존성 방향**은 `router → service → repository → store` 입니다. 각 계층은 자기 아래 계층에만 의존합니다. 스키마는 router 와 service 에서 참조하고, 모델은 repository 와 service 에서 참조합니다.

### `tests/`

런타임 레이아웃을 거울처럼 따라갑니다 — 동작을 고정할 가치가 있는 표면마다 테스트 모듈 하나. 스타터는 다음을 제공합니다:

- `conftest.py` — 테스트 사이에 items 스토어를 리셋하는 autouse 픽스처와 `TestClient(app)` 를 감싸는 `client` 픽스처.
- `test_health.py` — `GET /api/v1/health` 가 200 + `{"status": "ok"}` 를 반환하는지 검증.
- `test_items.py` — items 엔드포인트의 전체 CRUD 커버리지. 알 수 없는 id 의 404 와 잘못된 페이로드의 422 도 포함.

다음으로 실행:

```console
$ bash scripts/test.sh         # 또는: pytest
```

## 4단계: 번들된 `items` 도메인 살펴보기

예제 도메인은 작은 엔티티 위의 CRUD 입니다:

```python
# src/app/domains/items/models.py
@dataclass
class Item:
    id: int
    name: str
    price: float
    in_stock: bool = True
```

API 스키마는 입력 모양과 출력 모양을 분리해, 서버가 통제하는 필드 (`id`) 와 검증 (price ≥ 0) 을 추가할 수 있게 합니다:

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

repository 는 인메모리 스토어를 감싸고 삽입 시 id 를 부여합니다:

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
    # list_all / get / replace / delete / reset 생략
```

service 계층은 비즈니스 규칙이 쌓이는 자리입니다. 지금은 사용자 정의 예외 하나만 있는 얇은 패스스루에 가깝지만, 앞으로는 "열려 있는 주문 안의 item은 삭제할 수 없다" 같은 정책이 이 계층에 들어가게 됩니다:

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
    # list_items / create_item / replace_item / delete_item 생략
```

라우터는 HTTP를 직접 아는 유일한 계층입니다. 테스트에서 쉽게 오버라이드할 수 있도록 service를 FastAPI `Depends(...)`로 받고, `ItemNotFoundError`를 `HTTPException(404)`로 매핑합니다:

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

전체 라우터가 노출하는 것:

| 메서드 | 경로 | 동작 |
|---|---|---|
| `GET` | `/api/v1/items` | items 목록 |
| `GET` | `/api/v1/items/{item_id}` | 하나 조회 |
| `POST` | `/api/v1/items` | 생성 (201 반환) |
| `PUT` | `/api/v1/items/{item_id}` | 교체 |
| `DELETE` | `/api/v1/items/{item_id}` | 삭제 (204 반환) |
| `GET` | `/api/v1/health` | Liveness probe |

직접 시도:

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

## 5단계: 다음 도메인 추가

스타터는 **도메인 추가가 복사-이름변경 작업**이 되도록 설계됐습니다. `items` 옆에 `users` 도메인을 만들고 싶다고 가정해 봅시다:

### 1. `items/` 폴더 복사

```console
$ cp -r src/app/domains/items src/app/domains/users
```

### 2. 엔티티, 스키마, 파일별 클래스 이름 다시 쓰기

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
    # 평문 ``str`` 을 쓰면 그대로 붙여 넣어도 안전합니다. 대신 pydantic
    # 의 내장 이메일 검증을 사용하려면 선택 의존성
    # (``pip install 'pydantic[email]'`` — ``email-validator`` 를 끌어옴)
    # 을 설치하고 ``str`` 을 ``EmailStr`` 로 바꾸세요.
    email: str = Field(min_length=3, max_length=320)
    is_active: bool = True

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
```

`models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py` 전반에 걸쳐 `Item → User`, `ItemNotFoundError → UserNotFoundError`, `ItemRepository → UserRepository`, `ItemService → UserService` 로 이름을 바꾸세요. 라우터의 `prefix="/items"` → `prefix="/users"` 와 `tags=["items"]` → `tags=["users"]` 도 잊지 마세요.

repository 는 같은 `InMemoryStore` 기반 패턴을 유지할 수 있습니다 — 엔티티 타입에 대해 제네릭이기 때문입니다:

```python
# src/app/domains/users/repository.py
_store: InMemoryStore[User] = InMemoryStore()

class UserRepository:
    def __init__(self, store: Optional[InMemoryStore[User]] = None) -> None:
        self._store = store if store is not None else _store
    # ... ItemRepository 와 같은 모양 ...
```

### 3. 도메인 `__init__.py` 갱신

items 도메인은 호출자가 `from src.app.domains.items import service` 처럼 쓸 수 있도록 자기 모듈들을 다시 export 합니다. users 도 같은 방식으로:

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

### 4. 집계기에 라우터 등록

여기가 **`domains/users/` 바깥에서 손대야 하는 유일한 파일**입니다:

```python
# src/app/api/router.py
from src.app.api import health
from src.app.domains.items import router as items_router
from src.app.domains.users import router as users_router  # ← 추가

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items_router.router)
api_router.include_router(users_router.router)             # ← 추가
```

서버 재시작 후 `/docs` 에서 `/api/v1/users` 가 마운트된 것을 확인할 수 있습니다.

### 5. 테스트 추가

`tests/test_items.py` 를 거울처럼 옮긴 `tests/test_users.py` 를 만드세요 — 동일한 클라이언트 기반 모양으로 새 엔드포인트를 호출합니다. `conftest.py` 의 autouse 스토어 리셋 픽스처가 이미 각 테스트를 격리해 줍니다.

`InMemoryStore` 를 쓰는 두 번째 도메인을 추가한다면, 그 스토어도 리셋하도록 픽스처를 확장하거나, 도메인별로 픽스처 하나씩 두세요.

## 6단계: 다음 행선지

- [아키텍처 프리셋 매트릭스](../reference/preset-feature-matrix.md) 는 `fastkit init --interactive` 가 각 프리셋에 대해 무엇을 생성하는지 보여 줍니다. `domain-starter` 아래에서 어떤 기능 선택이 수동 연결을 필요로 하는지도 포함됩니다.
- [`fastapi-default` 튜토리얼](basic-api-server.md) 은 결정 전에 레이아웃을 비교해 보고 싶다면 계층형 대안을 다룹니다.
- 데이터베이스 통합은 [데이터베이스 통합 튜토리얼](database-integration.md) 이 PostgreSQL + SQLAlchemy + Alembic 패턴을 보여 줍니다. 같은 아이디어가 `src/app/db/` 와 도메인별 `repository.py` 파일들에 그대로 들어갑니다.

## 정리

- **생성**: `fastkit startdemo fastapi-domain-starter` → `bash scripts/run-server.sh` → `/docs` 에서 문서.
- **레이아웃**: 설정용 `core/`, 영속성 추상화용 `db/`, 비즈니스 슬라이스용 `domains/<concept>/`, 단일 집계 지점인 `api/router.py`, 런타임 모듈을 거울처럼 따라가는 `tests/`.
- **도메인 추가**: `items/` 복사 → 엔티티 / 스키마 / 클래스 이름 변경 → `__init__.py` 의 재export 갱신 → `src/app/api/router.py` 에 라우터 등록 → 테스트 모듈 추가. `main.py` 수정은 없습니다.

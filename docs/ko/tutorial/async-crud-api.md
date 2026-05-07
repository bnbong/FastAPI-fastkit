# 비동기 CRUD API 구축

FastAPI의 비동기 처리 능력을 활용해 고성능 CRUD API를 구축하는 방법을 배웁니다. 이 튜토리얼에서는 `fastapi-async-crud` 템플릿으로 비동기 파일 I/O와 효율적인 데이터 처리를 구현합니다.

## 이 튜토리얼에서 배우는 내용

- 비동기 FastAPI 애플리케이션 이해
- `async/await` 문법으로 비동기 CRUD 작업 수행
- aiofiles 로 비동기 파일 처리
- 비동기 테스트 작성과 실행
- 성능 최적화 기법

## 사전 요구 사항

- [기본 API 서버 튜토리얼](basic-api-server.md) 완료
- Python `async/await`의 기본 개념 이해
- FastAPI-fastkit 설치

## 비동기 처리가 필요한 이유

동기 처리와 비동기 처리의 차이를 이해해 봅시다:

### 동기 처리

```python
def process_items():
    item1 = read_file("item1.json")      # 2초 대기
    item2 = read_file("item2.json")      # 2초 대기
    item3 = read_file("item3.json")      # 2초 대기
    return [item1, item2, item3]         # 합계: 6초
```

### 비동기 처리

```python
async def process_items():
    item1_task = read_file_async("item1.json")  # 동시에 시작
    item2_task = read_file_async("item2.json")  # 동시에 시작
    item3_task = read_file_async("item3.json")  # 동시에 시작

    items = await asyncio.gather(item1_task, item2_task, item3_task)
    return items                                # 합계: 2초
```

## 1단계: 비동기 CRUD 프로젝트 생성

`fastapi-async-crud` 템플릿으로 프로젝트를 만듭니다:

<div class="termy">

```console
$ fastkit startdemo fastapi-async-crud
Enter the project name: async-todo-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Asynchronous todo management API
Deploying FastAPI project using 'fastapi-async-crud' template

           Project Information
┌──────────────┬─────────────────────────────────────────┐
│ Project Name │ async-todo-api                          │
│ Author       │ Developer Kim                           │
│ Author Email │ developer@example.com                   │
│ Description  │ Asynchronous todo management API        │
└──────────────┴─────────────────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ aiofiles          │
│ Dependency 6 │ pytest-asyncio    │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'async-todo-api' from 'fastapi-async-crud' has been created successfully!
```

</div>

## 2단계: 프로젝트 구조 분석

생성된 프로젝트의 주요 차이점을 살펴봅시다:

```
async-todo-api/
├── src/
│   ├── main.py                    # 비동기 FastAPI 애플리케이션
│   ├── api/
│   │   └── routes/
│   │       └── items.py          # 비동기 CRUD 엔드포인트
│   ├── crud/
│   │   └── items.py              # 비동기 데이터 처리 로직
│   ├── schemas/
│   │   └── items.py              # 데이터 모델 (동일)
│   ├── mocks/
│   │   └── mock_items.json       # JSON 파일 데이터베이스
│   └── core/
│       └── config.py             # 설정 파일
└── tests/
    ├── conftest.py               # 비동기 테스트 구성
    └── test_items.py             # 비동기 테스트 케이스
```

### 주요 차이점

1. **aiofiles**: 비동기 파일 I/O 처리
2. **pytest-asyncio**: 비동기 테스트 지원
3. **async/await 패턴**: 모든 CRUD 작업이 비동기로 구현됨

## 3단계: 비동기 CRUD 로직 이해

### 비동기 데이터 처리 (`src/crud/items.py`)

```python
import json
import asyncio
from typing import List, Optional
from aiofiles import open as aio_open
from pathlib import Path

from src.schemas.items import Item, ItemCreate, ItemUpdate

class AsyncItemCRUD:
    def __init__(self, data_file: str = "src/mocks/mock_items.json"):
        self.data_file = Path(data_file)

    async def _read_data(self) -> List[dict]:
        """Asynchronously read data from JSON file"""
        try:
            async with aio_open(self.data_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return []

    async def _write_data(self, data: List[dict]) -> None:
        """Asynchronously write data to JSON file"""
        async with aio_open(self.data_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    async def get_items(self) -> List[Item]:
        """Retrieve all items (asynchronous)"""
        data = await self._read_data()
        return [Item(**item) for item in data]

    async def get_item(self, item_id: int) -> Optional[Item]:
        """Retrieve specific item (asynchronous)"""
        data = await self._read_data()
        item_data = next((item for item in data if item["id"] == item_id), None)
        return Item(**item_data) if item_data else None

    async def create_item(self, item: ItemCreate) -> Item:
        """Create new item (asynchronous)"""
        data = await self._read_data()
        new_id = max([item["id"] for item in data], default=0) + 1

        new_item = Item(id=new_id, **item.dict())
        data.append(new_item.dict())

        await self._write_data(data)
        return new_item

    async def update_item(self, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Update item (asynchronous)"""
        data = await self._read_data()

        for i, item in enumerate(data):
            if item["id"] == item_id:
                update_data = item_update.dict(exclude_unset=True)
                data[i].update(update_data)
                await self._write_data(data)
                return Item(**data[i])

        return None

    async def delete_item(self, item_id: int) -> bool:
        """Delete item (asynchronous)"""
        data = await self._read_data()
        original_length = len(data)

        data = [item for item in data if item["id"] != item_id]

        if len(data) < original_length:
            await self._write_data(data)
            return True

        return False
```

### 비동기 API 엔드포인트 (`src/api/routes/items.py`)

```python
from typing import List
from fastapi import APIRouter, HTTPException, status

from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import AsyncItemCRUD

router = APIRouter()
crud = AsyncItemCRUD()

@router.get("/", response_model=List[Item])
async def read_items():
    """Retrieve all items (asynchronous)"""
    return await crud.get_items()

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    """Retrieve specific item (asynchronous)"""
    item = await crud.get_item(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """Create new item (asynchronous)"""
    return await crud.create_item(item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    """Update item (asynchronous)"""
    updated_item = await crud.update_item(item_id, item_update)
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """Delete item (asynchronous)"""
    deleted = await crud.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
```

## 4단계: 서버 실행과 테스트

프로젝트 디렉터리로 이동해 서버를 실행합니다:

<div class="termy">

```console
$ cd async-todo-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

### 성능 테스트

비동기 처리의 성능을 검증해 봅시다. 여러 요청을 동시에 보내 보세요:

**동시 요청 테스트 (Python 스크립트)**

```python
import asyncio
import aiohttp
import time

async def create_item(session, item_data):
    async with session.post("http://127.0.0.1:8000/items/", json=item_data) as response:
        return await response.json()

async def test_concurrent_requests():
    start_time = time.time()

    items_to_create = [
        {"name": f"Item {i}", "description": f"Description {i}", "price": i * 10, "tax": i}
        for i in range(1, 11)  # 10 개 item 을 동시에 생성
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [create_item(session, item) for item in items_to_create]
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Created 10 items in: {end_time - start_time:.2f} seconds")
    print(f"Number of items created: {len(results)}")

# 실행
# asyncio.run(test_concurrent_requests())
```

## 5단계: 비동기 테스트 작성

### 테스트 구성 (`tests/conftest.py`)

```python
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Event loop configuration"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """Asynchronous test client"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### 비동기 테스트 케이스 (`tests/test_items.py`)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_item_async(async_client: AsyncClient):
    """Asynchronous item creation test"""
    item_data = {
        "name": "Test Item",
        "description": "Item for asynchronous testing",
        "price": 100.0,
        "tax": 10.0
    }

    response = await async_client.post("/items/", json=item_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["price"] == item_data["price"]
    assert "id" in data

@pytest.mark.asyncio
async def test_read_items_async(async_client: AsyncClient):
    """Asynchronous item list retrieval test"""
    response = await async_client.get("/items/")

    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)

@pytest.mark.asyncio
async def test_concurrent_operations(async_client: AsyncClient):
    """Concurrent operations test"""
    import asyncio

    # 여러 item 을 동시에 생성
    tasks = []
    for i in range(5):
        item_data = {
            "name": f"ConcurrentItem{i}",
            "description": f"Description{i}",
            "price": i * 10,
            "tax": i
        }
        task = async_client.post("/items/", json=item_data)
        tasks.append(task)

    responses = await asyncio.gather(*tasks)

    # 모든 요청이 성공했는지 확인
    for response in responses:
        assert response.status_code == 201

    # 생성된 item 확인
    response = await async_client.get("/items/")
    items = response.json()
    assert len(items) >= 5
```

### 테스트 실행

<div class="termy">

```console
$ pytest tests/ -v --asyncio-mode=auto
======================== test session starts ========================
collected 8 items

tests/test_items.py::test_create_item_async PASSED            [ 12%]
tests/test_items.py::test_read_items_async PASSED             [ 25%]
tests/test_items.py::test_read_item_async PASSED              [ 37%]
tests/test_items.py::test_update_item_async PASSED            [ 50%]
tests/test_items.py::test_delete_item_async PASSED            [ 62%]
tests/test_items.py::test_concurrent_operations PASSED        [ 75%]
tests/test_items.py::test_item_not_found_async PASSED         [ 87%]
tests/test_items.py::test_invalid_item_data_async PASSED      [100%]

======================== 8 passed in 0.24s ========================
```

</div>

## 6단계: 성능 모니터링과 최적화

### 응답 시간 측정 미들웨어 추가

`src/main.py` 에 성능 모니터링을 추가해 봅시다:

```python
import time
from fastapi import FastAPI, Request
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(api_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Asynchronous Todo API!"}
```

### 비동기 배치 처리 구현

여러 item 을 한 번에 처리하는 배치 엔드포인트를 추가해 봅시다:

```python
# src/api/routes/items.py 에 추가

@router.post("/batch", response_model=List[Item])
async def create_items_batch(items: List[ItemCreate]):
    """Create multiple items concurrently (batch processing)"""
    import asyncio

    # 모든 item 생성 작업을 동시에 실행
    tasks = [crud.create_item(item) for item in items]
    created_items = await asyncio.gather(*tasks)

    return created_items

@router.get("/batch/{item_ids}")
async def read_items_batch(item_ids: str):
    """Retrieve multiple items concurrently (batch processing)"""
    import asyncio

    # 쉼표로 구분된 ID 파싱
    ids = [int(id.strip()) for id in item_ids.split(",")]

    # 모든 item 조회 작업을 동시에 실행
    tasks = [crud.get_item(item_id) for item_id in ids]
    items = await asyncio.gather(*tasks)

    # None 이 아닌 item 만 반환
    return [item for item in items if item is not None]
```

### 배치 처리 테스트

<div class="termy">

```console
# 배치 생성 테스트
$ curl -X POST "http://127.0.0.1:8000/items/batch" \
  -H "Content-Type: application/json" \
  -d '[
    {"name": "Item1", "description": "Description1", "price": 10.0, "tax": 1.0},
    {"name": "Item2", "description": "Description2", "price": 20.0, "tax": 2.0},
    {"name": "Item3", "description": "Description3", "price": 30.0, "tax": 3.0}
  ]'

# 배치 조회 테스트
$ curl -X GET "http://127.0.0.1:8000/items/batch/1,2,3"
```

</div>

## 7단계: 고급 비동기 패턴

### 레이트 제한 구현

```python
import asyncio
from collections import defaultdict
from fastapi import HTTPException, Request
from datetime import datetime, timedelta

class AsyncRateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)

    async def is_allowed(self, client_ip: str) -> bool:
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window_seconds)

        # 오래된 요청 기록 제거
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]

        # 현재 요청 수 확인
        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        # 현재 요청 기록 추가
        self.requests[client_ip].append(now)
        return True

# 전역 레이트 리미터 인스턴스
rate_limiter = AsyncRateLimiter()

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host

    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )

    response = await call_next(request)
    return response
```

### 비동기 캐싱 구현

```python
import asyncio
from typing import Optional, Any
from datetime import datetime, timedelta

class AsyncCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}

    async def get(self, key: str) -> Optional[Any]:
        # 만료된 항목 제거
        if key in self._expiry and datetime.now() > self._expiry[key]:
            del self._cache[key]
            del self._expiry[key]
            return None

        return self._cache.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._cache[key] = value
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)

    async def delete(self, key: str):
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

# 전역 캐시 인스턴스
cache = AsyncCache()

# CRUD 메서드를 캐시 사용하도록 수정
async def get_items_cached(self) -> List[Item]:
    """Retrieve items using cache"""
    cache_key = "all_items"
    cached_items = await cache.get(cache_key)

    if cached_items:
        return cached_items

    # 캐시가 없으면 파일에서 읽기
    items = await self.get_items()
    await cache.set(cache_key, items, ttl_seconds=60)  # 1분 캐시

    return items
```

## 8단계: 프로덕션 고려 사항

### 커넥션 풀 관리

```python
# src/core/config.py 에 추가
class Settings(BaseSettings):
    # ... 기존 설정 ...

    # 비동기 처리 관련 설정
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    CONNECTION_POOL_SIZE: int = 20

settings = Settings()
```

### 에러 처리 개선

```python
import logging
from fastapi import HTTPException
from typing import Union

logger = logging.getLogger(__name__)

async def safe_async_operation(operation, *args, **kwargs) -> Union[Any, None]:
    """Execute safe asynchronous operation"""
    try:
        return await operation(*args, **kwargs)
    except asyncio.TimeoutError:
        logger.error(f"Timeout in {operation.__name__}")
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error in {operation.__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 사용 예
@router.get("/safe/{item_id}")
async def read_item_safe(item_id: int):
    return await safe_async_operation(crud.get_item, item_id)
```

## 다음 단계

비동기 CRUD API 구축을 마쳤습니다! 다음으로 시도해 볼 만한 것들:

1. **[데이터베이스 통합](database-integration.md)** — 비동기 SQLAlchemy와 PostgreSQL 사용
2. **[Docker 컨테이너화](docker-deployment.md)** — 비동기 애플리케이션을 컨테이너화
3. **[커스텀 응답 처리](custom-response-handling.md)** — 고급 응답 형식과 에러 처리

<!-- 4. **[Building Real-time APIs](websocket-realtime-api.md)** - Real-time communication with WebSocket -->

## 요약

이 튜토리얼에서는 비동기 FastAPI로 다음 작업을 진행했습니다:

- ✅ 비동기 CRUD 작업 구현
- ✅ aiofiles 로 파일 I/O 최적화
- ✅ 동시 요청 처리와 성능 테스트
- ✅ 비동기 테스트 작성과 실행
- ✅ 배치 처리와 고급 비동기 패턴 구현
- ✅ 프로덕션 고려 사항 (캐싱, 에러 처리, 커넥션 관리) 반영

비동기 처리에 익숙해지면 고성능 API 서버를 훨씬 자신 있게 구축할 수 있습니다!

# 构建异步 CRUD API

学习如何利用 FastAPI 的异步处理能力构建高性能的 CRUD API。本教程中我们会使用 `fastapi-async-crud` 模板实现异步文件 I/O 与高效的数据处理。

## 您将学到的内容

- 理解异步 FastAPI 应用
- 使用 `async/await` 语法的异步 CRUD 操作
- 使用 aiofiles 处理异步文件
- 编写并运行异步测试
- 性能优化技巧

## 前置条件

- 完成 [基础 API 服务器教程](basic-api-server.md)
- 理解 Python `async/await` 的基本概念
- 已安装 FastAPI-fastkit

## 为什么需要异步处理

让我们先理解同步与异步处理之间的差异:

### 同步处理

```python
def process_items():
    item1 = read_file("item1.json")      # Wait 2 seconds
    item2 = read_file("item2.json")      # Wait 2 seconds
    item3 = read_file("item3.json")      # Wait 2 seconds
    return [item1, item2, item3]         # Total: 6 seconds
```

### 异步处理

```python
async def process_items():
    item1_task = read_file_async("item1.json")  # Start concurrently
    item2_task = read_file_async("item2.json")  # Start concurrently
    item3_task = read_file_async("item3.json")  # Start concurrently

    items = await asyncio.gather(item1_task, item2_task, item3_task)
    return items                                # Total: 2 seconds
```

## 第 1 步:创建异步 CRUD 项目

使用 `fastapi-async-crud` 模板创建项目:

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

## 第 2 步:分析项目结构

来看看生成后的项目有哪些关键差异：

```
async-todo-api/
├── src/
│   ├── main.py                    # 异步 FastAPI 应用入口
│   ├── api/
│   │   └── routes/
│   │       └── items.py          # 异步 CRUD 端点
│   ├── crud/
│   │   └── items.py              # 异步数据处理逻辑
│   ├── schemas/
│   │   └── items.py              # 数据模型（结构相同）
│   ├── mocks/
│   │   └── mock_items.json       # JSON 文件数据库
│   └── core/
│       └── config.py             # 配置文件
└── tests/
    ├── conftest.py               # 异步测试配置
    └── test_items.py             # 异步测试用例
```

### 关键差异

1. **aiofiles**:异步文件 I/O 处理
2. **pytest-asyncio**:对异步测试的支持
3. **async/await 模式**:所有 CRUD 操作都用异步方式实现

## 第 3 步:理解异步 CRUD 逻辑

### 异步数据处理(`src/crud/items.py`)

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
        """异步读取 JSON 文件中的数据"""
        try:
            async with aio_open(self.data_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return []

    async def _write_data(self, data: List[dict]) -> None:
        """异步将数据写入 JSON 文件"""
        async with aio_open(self.data_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    async def get_items(self) -> List[Item]:
        """异步获取所有 items"""
        data = await self._read_data()
        return [Item(**item) for item in data]

    async def get_item(self, item_id: int) -> Optional[Item]:
        """异步获取指定 item"""
        data = await self._read_data()
        item_data = next((item for item in data if item["id"] == item_id), None)
        return Item(**item_data) if item_data else None

    async def create_item(self, item: ItemCreate) -> Item:
        """异步创建新 item"""
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

### 异步 API 端点(`src/api/routes/items.py`)

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

## 第 4 步:运行服务器并测试

进入项目目录运行服务器:

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

### 性能测试

我们来验证异步处理的性能,尝试同时发出多个请求:

**并发请求测试(Python 脚本)**

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
        for i in range(1, 11)  # Create 10 items concurrently
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [create_item(session, item) for item in items_to_create]
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Created 10 items in: {end_time - start_time:.2f} seconds")
    print(f"Number of items created: {len(results)}")

# Run test
# asyncio.run(test_concurrent_requests())
```

## 第 5 步:编写异步测试

### 测试配置(`tests/conftest.py`)

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

### 异步测试用例(`tests/test_items.py`)

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

    # Create multiple items concurrently
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

    # Verify all requests succeeded
    for response in responses:
        assert response.status_code == 201

    # Verify created items
    response = await async_client.get("/items/")
    items = response.json()
    assert len(items) >= 5
```

### 运行测试

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

## 第 6 步:性能监控与优化

### 添加响应耗时测量中间件

在 `src/main.py` 中加入性能监控:

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

### 实现异步批量处理

我们加上批量端点,以便一次处理多个 item:

```python
# Add to src/api/routes/items.py

@router.post("/batch", response_model=List[Item])
async def create_items_batch(items: List[ItemCreate]):
    """Create multiple items concurrently (batch processing)"""
    import asyncio

    # Execute all item creation tasks concurrently
    tasks = [crud.create_item(item) for item in items]
    created_items = await asyncio.gather(*tasks)

    return created_items

@router.get("/batch/{item_ids}")
async def read_items_batch(item_ids: str):
    """Retrieve multiple items concurrently (batch processing)"""
    import asyncio

    # Parse comma-separated IDs
    ids = [int(id.strip()) for id in item_ids.split(",")]

    # Execute all item retrieval tasks concurrently
    tasks = [crud.get_item(item_id) for item_id in ids]
    items = await asyncio.gather(*tasks)

    # Return only non-None items
    return [item for item in items if item is not None]
```

### 批量处理测试

<div class="termy">

```console
# Batch creation test
$ curl -X POST "http://127.0.0.1:8000/items/batch" \
  -H "Content-Type: application/json" \
  -d '[
    {"name": "Item1", "description": "Description1", "price": 10.0, "tax": 1.0},
    {"name": "Item2", "description": "Description2", "price": 20.0, "tax": 2.0},
    {"name": "Item3", "description": "Description3", "price": 30.0, "tax": 3.0}
  ]'

# Batch retrieval test
$ curl -X GET "http://127.0.0.1:8000/items/batch/1,2,3"
```

</div>

## 第 7 步:进阶异步模式

### 实现限流

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

        # remove old request records
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]

        # check current request count
        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        # add current request record
        self.requests[client_ip].append(now)
        return True

# global rate limiter instance
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

### 实现异步缓存

```python
import asyncio
from typing import Optional, Any
from datetime import datetime, timedelta

class AsyncCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}

    async def get(self, key: str) -> Optional[Any]:
        # remove expired items
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

# global cache instance
cache = AsyncCache()

# modify CRUD methods to use cache
async def get_items_cached(self) -> List[Item]:
    """Retrieve items using cache"""
    cache_key = "all_items"
    cached_items = await cache.get(cache_key)

    if cached_items:
        return cached_items

    # if cache is not found, read from file
    items = await self.get_items()
    await cache.set(cache_key, items, ttl_seconds=60)  # 1 minute cache

    return items
```

## 第 8 步:生产环境考量

### 管理连接池

```python
# add to src/core/config.py
class Settings(BaseSettings):
    # ... existing settings ...

    # asynchronous processing related settings
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    CONNECTION_POOL_SIZE: int = 20

settings = Settings()
```

### 改进错误处理

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

# usage example
@router.get("/safe/{item_id}")
async def read_item_safe(item_id: int):
    return await safe_async_operation(crud.get_item, item_id)
```

## 下一步

恭喜您完成了异步 CRUD API 的构建!接下来可以尝试:

1. **[数据库集成](database-integration.md)** —— 使用 PostgreSQL 与异步 SQLAlchemy
2. **[Docker 容器化](docker-deployment.md)** —— 把异步应用容器化
3. **[自定义响应处理](custom-response-handling.md)** —— 进阶的响应格式与错误处理

<!-- 4. **[Building Real-time APIs](websocket-realtime-api.md)** - Real-time communication with WebSocket -->

## 小结

在本教程中,我们用异步 FastAPI 完成了:

- ✅ 实现异步 CRUD 操作
- ✅ 用 aiofiles 优化文件 I/O
- ✅ 处理并发请求并进行性能测试
- ✅ 编写并运行异步测试
- ✅ 实现批量处理与进阶异步模式
- ✅ 处理生产环境的考量(缓存、错误处理、连接管理)

掌握异步处理,您就能构建出高性能的 API 服务器!

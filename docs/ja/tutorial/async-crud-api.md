# 非同期 CRUD API の構築

FastAPI の非同期処理を使って高性能な CRUD API を構築する方法を学びます。このチュートリアルでは `fastapi-async-crud` テンプレートを使い、非同期ファイル I/O と効率的なデータ処理を実装します。

## このチュートリアルで学ぶこと

- 非同期 FastAPI アプリケーションの理解
- `async/await` 構文を用いた非同期 CRUD 操作
- aiofiles による非同期ファイル処理
- 非同期テストの書き方と実行
- パフォーマンス最適化の手法

## 前提条件

- [基本 API サーバーチュートリアル](basic-api-server.md) を完了済み
- Python の `async/await` の基礎を理解していること
- FastAPI-fastkit がインストール済み

## なぜ非同期処理が必要か

同期処理と非同期処理の違いを把握しておきましょう:

### 同期処理

```python
def process_items():
    item1 = read_file("item1.json")      # 2 秒待つ
    item2 = read_file("item2.json")      # 2 秒待つ
    item3 = read_file("item3.json")      # 2 秒待つ
    return [item1, item2, item3]         # 合計: 6 秒
```

### 非同期処理

```python
async def process_items():
    item1_task = read_file_async("item1.json")  # 同時に開始
    item2_task = read_file_async("item2.json")  # 同時に開始
    item3_task = read_file_async("item3.json")  # 同時に開始

    items = await asyncio.gather(item1_task, item2_task, item3_task)
    return items                                # 合計: 2 秒
```

## ステップ 1: 非同期 CRUD プロジェクトの作成

`fastapi-async-crud` テンプレートでプロジェクトを作成します:

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

## ステップ 2: プロジェクト構造の解析

生成プロジェクトの主な違いを確認しましょう:

```
async-todo-api/
├── src/
│   ├── main.py                    # 非同期 FastAPI アプリ
│   ├── api/
│   │   └── routes/
│   │       └── items.py          # 非同期 CRUD エンドポイント
│   ├── crud/
│   │   └── items.py              # 非同期データ処理ロジック
│   ├── schemas/
│   │   └── items.py              # データモデル (同じ)
│   ├── mocks/
│   │   └── mock_items.json       # JSON ファイルデータベース
│   └── core/
│       └── config.py             # 設定ファイル
└── tests/
    ├── conftest.py               # 非同期テスト設定
    └── test_items.py             # 非同期テストケース
```

### 主な違い

1. **aiofiles**: 非同期ファイル I/O 処理
2. **pytest-asyncio**: 非同期テストのサポート
3. **async/await パターン**: すべての CRUD 操作が非同期で実装

## ステップ 3: 非同期 CRUD ロジックの理解

### 非同期データ処理 (`src/crud/items.py`)

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
        """非同期に JSON ファイルからデータを読み込む"""
        try:
            async with aio_open(self.data_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return []

    async def _write_data(self, data: List[dict]) -> None:
        """非同期に JSON ファイルへデータを書き込む"""
        async with aio_open(self.data_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(data, indent=2, ensure_ascii=False))

    async def get_items(self) -> List[Item]:
        """すべての items を取得 (非同期)"""
        data = await self._read_data()
        return [Item(**item) for item in data]

    async def get_item(self, item_id: int) -> Optional[Item]:
        """特定の item を取得 (非同期)"""
        data = await self._read_data()
        item_data = next((item for item in data if item["id"] == item_id), None)
        return Item(**item_data) if item_data else None

    async def create_item(self, item: ItemCreate) -> Item:
        """新しい item を作成 (非同期)"""
        data = await self._read_data()
        new_id = max([item["id"] for item in data], default=0) + 1

        new_item = Item(id=new_id, **item.dict())
        data.append(new_item.dict())

        await self._write_data(data)
        return new_item

    async def update_item(self, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """item を更新 (非同期)"""
        data = await self._read_data()

        for i, item in enumerate(data):
            if item["id"] == item_id:
                update_data = item_update.dict(exclude_unset=True)
                data[i].update(update_data)
                await self._write_data(data)
                return Item(**data[i])

        return None

    async def delete_item(self, item_id: int) -> bool:
        """item を削除 (非同期)"""
        data = await self._read_data()
        original_length = len(data)

        data = [item for item in data if item["id"] != item_id]

        if len(data) < original_length:
            await self._write_data(data)
            return True

        return False
```

### 非同期 API エンドポイント (`src/api/routes/items.py`)

```python
from typing import List
from fastapi import APIRouter, HTTPException, status

from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import AsyncItemCRUD

router = APIRouter()
crud = AsyncItemCRUD()

@router.get("/", response_model=List[Item])
async def read_items():
    """すべての items を取得 (非同期)"""
    return await crud.get_items()

@router.get("/{item_id}", response_model=Item)
async def read_item(item_id: int):
    """特定の item を取得 (非同期)"""
    item = await crud.get_item(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return item

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemCreate):
    """新しい item を作成 (非同期)"""
    return await crud.create_item(item)

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, item_update: ItemUpdate):
    """item を更新 (非同期)"""
    updated_item = await crud.update_item(item_id, item_update)
    if updated_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    """item を削除 (非同期)"""
    deleted = await crud.delete_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
```

## ステップ 4: サーバーの起動とテスト

プロジェクトディレクトリへ移動してサーバーを起動します:

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

### パフォーマンステスト

非同期処理のパフォーマンスを確認しましょう。複数のリクエストを同時に送ってみます:

**同時リクエストテスト (Python スクリプト)**

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
        for i in range(1, 11)  # 10 件の item を同時生成
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [create_item(session, item) for item in items_to_create]
        results = await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Created 10 items in: {end_time - start_time:.2f} seconds")
    print(f"Number of items created: {len(results)}")

# 実行
# asyncio.run(test_concurrent_requests())
```

## ステップ 5: 非同期テストの作成

### テスト設定 (`tests/conftest.py`)

```python
import pytest
import asyncio
from httpx import AsyncClient
from src.main import app

@pytest.fixture(scope="session")
def event_loop():
    """イベントループの設定"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """非同期テストクライアント"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### 非同期テストケース (`tests/test_items.py`)

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_item_async(async_client: AsyncClient):
    """非同期 item 作成テスト"""
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
    """非同期 item 一覧取得テスト"""
    response = await async_client.get("/items/")

    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)

@pytest.mark.asyncio
async def test_concurrent_operations(async_client: AsyncClient):
    """同時操作テスト"""
    import asyncio

    # 複数の item を同時作成
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

    # すべてのリクエストが成功したか確認
    for response in responses:
        assert response.status_code == 201

    # 作成された item を確認
    response = await async_client.get("/items/")
    items = response.json()
    assert len(items) >= 5
```

### テスト実行

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

## ステップ 6: パフォーマンス監視と最適化

### レスポンス時間計測ミドルウェアの追加

`src/main.py` にパフォーマンス監視を追加しましょう:

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
    """リクエストの処理時間をヘッダーに追加"""
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

### 非同期バッチ処理の実装

複数の item を一度に処理するバッチエンドポイントを追加しましょう:

```python
# src/api/routes/items.py に追加

@router.post("/batch", response_model=List[Item])
async def create_items_batch(items: List[ItemCreate]):
    """複数の item を同時作成 (バッチ処理)"""
    import asyncio

    # すべての作成タスクを同時実行
    tasks = [crud.create_item(item) for item in items]
    created_items = await asyncio.gather(*tasks)

    return created_items

@router.get("/batch/{item_ids}")
async def read_items_batch(item_ids: str):
    """複数の item を同時取得 (バッチ処理)"""
    import asyncio

    # カンマ区切りの ID をパース
    ids = [int(id.strip()) for id in item_ids.split(",")]

    # すべての取得タスクを同時実行
    tasks = [crud.get_item(item_id) for item_id in ids]
    items = await asyncio.gather(*tasks)

    # None でない item のみ返す
    return [item for item in items if item is not None]
```

### バッチ処理のテスト

<div class="termy">

```console
# バッチ作成のテスト
$ curl -X POST "http://127.0.0.1:8000/items/batch" \
  -H "Content-Type: application/json" \
  -d '[
    {"name": "Item1", "description": "Description1", "price": 10.0, "tax": 1.0},
    {"name": "Item2", "description": "Description2", "price": 20.0, "tax": 2.0},
    {"name": "Item3", "description": "Description3", "price": 30.0, "tax": 3.0}
  ]'

# バッチ取得のテスト
$ curl -X GET "http://127.0.0.1:8000/items/batch/1,2,3"
```

</div>

## ステップ 7: 高度な非同期パターン

### レート制限の実装

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

        # 古いリクエスト履歴を削除
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > cutoff
        ]

        # 現在のリクエスト数を確認
        if len(self.requests[client_ip]) >= self.max_requests:
            return False

        # 現在のリクエストを記録
        self.requests[client_ip].append(now)
        return True

# グローバルなレートリミッタ
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

### 非同期キャッシュの実装

```python
import asyncio
from typing import Optional, Any
from datetime import datetime, timedelta

class AsyncCache:
    def __init__(self):
        self._cache = {}
        self._expiry = {}

    async def get(self, key: str) -> Optional[Any]:
        # 期限切れの項目を削除
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

# グローバルなキャッシュ
cache = AsyncCache()

# CRUD メソッドをキャッシュ利用に変更
async def get_items_cached(self) -> List[Item]:
    """キャッシュを利用した item 取得"""
    cache_key = "all_items"
    cached_items = await cache.get(cache_key)

    if cached_items:
        return cached_items

    # キャッシュがなければファイルから読み込む
    items = await self.get_items()
    await cache.set(cache_key, items, ttl_seconds=60)  # 1 分間キャッシュ

    return items
```

## ステップ 8: 本番運用での考慮事項

### コネクションプールの管理

```python
# src/core/config.py に追加
class Settings(BaseSettings):
    # ... 既存の設定 ...

    # 非同期処理関連の設定
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    CONNECTION_POOL_SIZE: int = 20

settings = Settings()
```

### エラーハンドリングの改善

```python
import logging
from fastapi import HTTPException
from typing import Union

logger = logging.getLogger(__name__)

async def safe_async_operation(operation, *args, **kwargs) -> Union[Any, None]:
    """安全な非同期操作の実行"""
    try:
        return await operation(*args, **kwargs)
    except asyncio.TimeoutError:
        logger.error(f"Timeout in {operation.__name__}")
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        logger.error(f"Error in {operation.__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 利用例
@router.get("/safe/{item_id}")
async def read_item_safe(item_id: int):
    return await safe_async_operation(crud.get_item, item_id)
```

## 次のステップ

非同期 CRUD API の構築が完了しました! 次に試すこと:

1. **[データベース統合](database-integration.md)** - 非同期 SQLAlchemy で PostgreSQL を利用
2. **[Docker でのデプロイ](docker-deployment.md)** - 非同期アプリケーションをコンテナ化
3. **[カスタムレスポンス処理](custom-response-handling.md)** - 高度なレスポンス形式とエラーハンドリング

<!-- 4. **[Building Real-time APIs](websocket-realtime-api.md)** - Real-time communication with WebSocket -->

## まとめ

このチュートリアルでは、非同期 FastAPI を使って次を行いました:

- ✅ 非同期 CRUD 操作の実装
- ✅ aiofiles によるファイル I/O の最適化
- ✅ 同時リクエストとパフォーマンステスト
- ✅ 非同期テストの作成と実行
- ✅ バッチ処理と高度な非同期パターンの実装
- ✅ 本番運用での考慮 (キャッシュ、エラーハンドリング、コネクション管理)

非同期処理を習得すれば、高性能な API サーバーを構築できます!

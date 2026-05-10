# 基本 API サーバーの構築

FastAPI-fastkit を使って、シンプルな REST API サーバーを素早く構築する方法を学びます。このチュートリアルは FastAPI 初心者向けで、基本的な CRUD API の作成を扱います。

## このチュートリアルで学ぶこと

- `fastkit startdemo` コマンドによる基本 API サーバーの作成
- FastAPI プロジェクト構造の理解
- 基本的な CRUD エンドポイントの利用
- API テストとドキュメント
- プロジェクトの拡張方法

## 前提条件

- Python 3.12 以上がインストール済み
- FastAPI-fastkit がインストール済み (`pip install fastapi-fastkit`)
- 基本的な Python の知識

## ステップ 1: 基本 API プロジェクトの作成

`fastapi-default` テンプレートで基本 API サーバーを作成しましょう。

<div class="termy">

```console
$ fastkit startdemo fastapi-default
Enter the project name: my-first-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: My first FastAPI server
Deploying FastAPI project using 'fastapi-default' template

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-first-api               │
│ Author       │ Developer Kim              │
│ Author Email │ developer@example.com      │
│ Description  │ My first FastAPI server    │
└──────────────┴────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-api' from 'fastapi-default' has been created successfully!
```

</div>

## ステップ 2: 生成されたプロジェクト構造の理解

生成されたプロジェクト構造を確認しましょう:

```
my-first-api/
├── README.md                 # プロジェクトドキュメント
├── requirements.txt          # 依存パッケージのリスト
├── setup.py                  # パッケージ設定
├── scripts/
│   └── run-server.sh        # サーバー起動スクリプト
├── src/                     # メインのソースコード
│   ├── main.py              # FastAPI アプリのエントリポイント
│   ├── core/
│   │   └── config.py        # 設定管理
│   ├── api/
│   │   ├── api.py           # API ルーター集約
│   │   └── routes/
│   │       └── items.py     # items 関連エンドポイント
│   ├── schemas/
│   │   └── items.py         # データモデル定義
│   ├── crud/
│   │   └── items.py         # データ処理ロジック
│   └── mocks/
│       └── mock_items.json  # テストデータ
└── tests/                   # テストコード
    ├── __init__.py
    ├── conftest.py
    └── test_items.py
```

### 主要ファイルの説明

- **`src/main.py`**: FastAPI アプリのエントリポイント
- **`src/api/routes/items.py`**: items 関連の API エンドポイント定義
- **`src/schemas/items.py`**: リクエスト / レスポンスのデータ構造定義
- **`src/crud/items.py`**: データベース操作のロジック
- **`src/mocks/mock_items.json`**: 開発用のサンプルデータ

## ステップ 3: サーバーの起動

生成されたプロジェクトディレクトリへ移動してサーバーを起動します。

<div class="termy">

```console
$ cd my-first-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Will watch for changes in these directories: ['/path/to/my-first-api']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

サーバーが起動したら、ブラウザで次の URL にアクセスできます:

- **API サーバー**: http://127.0.0.1:8000
- **Swagger UI ドキュメント**: http://127.0.0.1:8000/docs
- **ReDoc ドキュメント**: http://127.0.0.1:8000/redoc

## ステップ 4: API エンドポイントの確認

生成された API は標準で次のエンドポイントを提供します:

| メソッド | エンドポイント | 説明 |
|---|---|---|
| GET | `/items/` | すべての items を取得 |
| GET | `/items/{item_id}` | 特定の item を取得 |
| POST | `/items/` | 新しい item を作成 |
| PUT | `/items/{item_id}` | item を更新 |
| DELETE | `/items/{item_id}` | item を削除 |

### API のテスト

**1. すべての items を取得**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/"
[
  {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  },
  {
    "id": 2,
    "name": "Mouse",
    "description": "Wireless mouse",
    "price": 29.99,
    "tax": 2.99
  }
]
```

</div>

**2. 新しい item を作成**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Keyboard",
       "description": "Mechanical keyboard",
       "price": 150.00,
       "tax": 15.00
     }'

{
  "id": 3,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.0,
  "tax": 15.0
}
```

</div>

**3. 特定の item を取得**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/1"
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "tax": 99.99
}
```

</div>

## ステップ 5: Swagger UI で API をテスト

ブラウザで http://127.0.0.1:8000/docs に移動すると、自動生成された API ドキュメントを確認できます。

Swagger UI でできること:

1. **API エンドポイントの一覧表示**: 利用可能なすべてのエンドポイントを視覚的に確認
2. **リクエスト / レスポンススキーマの確認**: 各エンドポイントの入出力フォーマットを確認
3. **API を直接テスト**: 「Try it out」ボタンで実際に API を呼び出す
4. **サンプルデータの参照**: 各エンドポイントのリクエスト / レスポンス例を確認

### Swagger UI の使い方

1. `/items/` GET エンドポイントをクリック
2. 「Try it out」ボタンをクリック
3. 「Execute」ボタンをクリック
4. サーバーのレスポンスを確認

## ステップ 6: コード構造の理解

### メインアプリケーション (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### Item スキーマ (`src/schemas/items.py`)

```python
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
```

### CRUD ロジック (`src/crud/items.py`)

```python
from typing import List, Optional
from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self):
        self.items: List[Item] = []
        self.next_id = 1

    def create_item(self, item: ItemCreate) -> Item:
        new_item = Item(id=self.next_id, **item.dict())
        self.items.append(new_item)
        self.next_id += 1
        return new_item

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)
```

## ステップ 7: プロジェクトの拡張

### 新しいルートの追加

`fastkit addroute` コマンドで新しいエンドポイントを追加できます:

<div class="termy">

```console
$ fastkit addroute user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ user                                     │
│ Target Directory │ /path/to/my-first-api                   │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to the current project? [Y/n]: y

✨ Successfully added new route 'user' to the current project!
```

</div>

このコマンドは次のファイルを作成します:

- `src/api/routes/user.py` - user 関連エンドポイント
- `src/schemas/user.py` - user データモデル
- `src/crud/user.py` - user データ処理ロジック

### 設定のカスタマイズ

`src/core/config.py` を変更してプロジェクト設定を調整できます:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My First API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "My first FastAPI server"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## ステップ 8: テストの実行

プロジェクトには基本テストが含まれます:

<div class="termy">

```console
$ pytest tests/ -v
======================== test session starts ========================
collected 4 items

tests/test_items.py::test_create_item PASSED                   [ 25%]
tests/test_items.py::test_read_items PASSED                    [ 50%]
tests/test_items.py::test_read_item PASSED                     [ 75%]
tests/test_items.py::test_update_item PASSED                   [100%]

======================== 4 passed in 0.15s ========================
```

</div>

## 次のステップ

基本 API サーバーの構築が完了しました! 次に試すこと:

1. **[非同期 CRUD API の構築](async-crud-api.md)** - より複雑な非同期処理を学ぶ
2. **[データベース統合](database-integration.md)** - PostgreSQL と SQLAlchemy の利用
3. **[Docker でのデプロイ](docker-deployment.md)** - 本番デプロイの準備
4. **[カスタムレスポンス処理](custom-response-handling.md)** - 高度なレスポンス形式の構成

## トラブルシューティング

### よくある問題

**Q: サーバーが起動しない**
A: 仮想環境が有効化され、依存関係が正しくインストールされているか確認してください。

**Q: API エンドポイントにアクセスできない**
A: サーバーが正常に起動していること、ポート番号 (デフォルト: 8000) が正しいことを確認してください。

**Q: API が Swagger UI に表示されない**
A: ルーターが `src/main.py` に正しく取り込まれているか確認してください。

## まとめ

このチュートリアルでは、FastAPI-fastkit を使って次を行いました:

- ✅ 基本的な FastAPI プロジェクトの作成
- ✅ プロジェクト構造の理解
- ✅ CRUD API エンドポイントの利用
- ✅ API ドキュメントとテスト
- ✅ プロジェクトの拡張方法

FastAPI の基礎を理解できたら、より複雑なプロジェクトに挑戦してみましょう!

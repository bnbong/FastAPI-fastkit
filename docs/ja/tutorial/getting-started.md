# はじめに

FastAPI-fastkit を始めるための、包括的かつ段階的なチュートリアルです。インストールから最初の API の起動まで、約 15 分で進められます。

## 前提条件

開始前に、次が用意されているか確認してください:

- システムに **Python 3.12 以上** がインストールされていること
- **Python の基礎知識** (変数・関数・クラス)
- **ターミナル / コマンドライン** の利用
- **テキストエディタまたは IDE** (VS Code、PyCharm など)

## ステップ 1: インストール

まず FastAPI-fastkit をインストールしましょう。プロジェクトを分離するため、仮想環境の利用を推奨します。

### オプション A: pip を使う (従来型)

<div class="termy">

```console
$ pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### オプション B: UV を使う (推奨・高速)

UV は高速な Python パッケージマネージャーです。UV をまだ入れていない場合:

<div class="termy">

```console
# まず UV をインストール
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# 次に FastAPI-fastkit をインストール
$ uv pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### オプション C: 仮想環境を使う

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Windows の場合: fastapi-env\Scripts\activate
$ pip install fastapi-fastkit
```

</div>

### インストールの確認

FastAPI-fastkit が正しくインストールされたか確認します:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

## ステップ 2: 最初のプロジェクトを作成

対話型の `init` コマンドで、最初の FastAPI プロジェクトを作成しましょう:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-api
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-first-api            │
│ Author       │ Your Name               │
│ Author Email │ your.email@example.com  │
│ Description  │ My first FastAPI project│
└──────────────┴─────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

Creating virtual environment...
Installing dependencies...
✨ FastAPI project 'my-first-api' has been created successfully!
```

</div>

!!! note "スタックの選択"
    このチュートリアルでは話を簡潔に保つため **MINIMAL** を選びました。実プロジェクトでは、**STANDARD** (データベース対応を含む) や **FULL** (バックグラウンドタスクを含む) の利用も検討しましょう。

## ステップ 3: プロジェクトに移動

新しく作られたプロジェクトディレクトリへ移動します:

<div class="termy">

```console
$ cd my-first-api
$ ls -la
total 32
drwxr-xr-x  8 user user  256 Dec  7 10:30 .
drwxr-xr-x  3 user user   96 Dec  7 10:30 ..
drwxr-xr-x  5 user user  160 Dec  7 10:30 .venv
-rw-r--r--  1 user user  156 Dec  7 10:30 README.md
-rw-r--r--  1 user user  243 Dec  7 10:30 requirements.txt
drwxr-xr-x  3 user user   96 Dec  7 10:30 scripts
-rw-r--r--  1 user user 1245 Dec  7 10:30 setup.py
drwxr-xr-x  8 user user  256 Dec  7 10:30 src
drwxr-xr-x  3 user user   96 Dec  7 10:30 tests
```

</div>

## ステップ 4: 仮想環境を有効化

プロジェクトには、仮想環境があらかじめ用意されています。これを有効化しましょう:

<div class="termy">

```console
$ source .venv/bin/activate  # Windows の場合: .venv\Scripts\activate
(my-first-api) $
```

</div>

ターミナルのプロンプトに `(my-first-api)` と表示され、仮想環境が有効になっていることが分かります。

## ステップ 5: 開発サーバーを起動

ここからが楽しい部分です — FastAPI サーバーを起動しましょう:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720] using StatReload
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

🎉 **おめでとうございます!** あなたの FastAPI サーバーが起動しています。

## ステップ 6: API のテスト

API をいくつかの方法でテストしてみましょう:

### 方法 1: ブラウザ

Web ブラウザで次にアクセスします:

- **メイン API エンドポイント**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

次のように表示されるはずです:
```json
{"message": "Hello World"}
```

### 方法 2: 対話型 API ドキュメント

自動生成された API ドキュメントを開きます:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

特に Swagger UI は便利です。次のことができます:

- 利用可能なエンドポイントの一覧表示
- ブラウザから直接エンドポイントをテスト
- リクエスト / レスポンススキーマの確認
- OpenAPI 仕様のダウンロード

### 方法 3: コマンドライン

新しいターミナルを開いて (サーバーは起動したまま)、curl でテストします:

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Hello World"}

$ curl http://127.0.0.1:8000/api/v1/items/
[]

$ curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Item", "description": "This is a test item"}'
{
  "id": 1,
  "title": "My First Item",
  "description": "This is a test item"
}
```

</div>

## ステップ 7: プロジェクト構造の理解

FastAPI-fastkit が何を生成したかを確認しましょう:

<div class="termy">

```console
$ tree src
src/
├── __init__.py
├── main.py                 # FastAPI アプリケーションのエントリポイント
├── core/
│   ├── __init__.py
│   └── config.py          # アプリケーション設定
├── api/
│   ├── __init__.py
│   ├── api.py             # メインの API ルーター
│   └── routes/
│       ├── __init__.py
│       └── items.py       # Items API エンドポイント
├── crud/
│   ├── __init__.py
│   └── items.py           # items のビジネスロジック
├── schemas/
│   ├── __init__.py
│   └── items.py           # データ検証スキーマ
└── mocks/
    ├── __init__.py
    └── mock_items.json    # サンプルデータ
```

</div>

### 主要ファイルの解説

**`src/main.py`** — アプリケーションの中核:
```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**`src/core/config.py`** — アプリケーション設定:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "my-first-api"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

**`src/api/routes/items.py`** — API エンドポイント:
```python
from typing import List
from fastapi import APIRouter, HTTPException
from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import items_crud

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items():
    """Get all items"""
    return items_crud.get_all()

@router.post("/", response_model=Item)
def create_item(item: ItemCreate):
    """Create a new item"""
    return items_crud.create(item)
```

## ステップ 8: 最初のカスタムルートを追加

学んだことを実践するため、新しい API ルートを追加してみましょう:

<div class="termy">

```console
$ fastkit addroute users my-first-api
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-api                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-first-api'
```

</div>

サーバーは自動的に再起動し、新しいエンドポイントが使えるようになります:

- `GET /api/v1/users/` - すべてのユーザーを取得
- `POST /api/v1/users/` - 新しいユーザーを作成
- `GET /api/v1/users/{user_id}` - 特定のユーザーを取得
- ほか

### 新しいルートをテストする

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}

$ curl http://127.0.0.1:8000/api/v1/users/
[
  {
    "id": 1,
    "title": "John Doe",
    "description": "Software Developer"
  }
]
```

</div>

## ステップ 9: コードを読んで変更する

コードがどのように動くかを理解するため、小さな変更を加えてみましょう。

### ウェルカムメッセージの変更

エディタで `src/main.py` を開き、ルートエンドポイントを変更します:

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!"}
```

ファイルを保存します。自動リロードのおかげでサーバーは自動的に再起動します。

### 変更をテストする

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Welcome to my first FastAPI application!"}
```

</div>

### 新しいエンドポイントを追加する

`src/main.py` にシンプルなエンドポイントを追加します:

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### 新しいエンドポイントをテストする

<div class="termy">

```console
$ curl http://127.0.0.1:8000/hello/World
{"message":"Hello, World!"}

$ curl http://127.0.0.1:8000/hello/FastAPI
{"message":"Hello, FastAPI!"}
```

</div>

## ステップ 10: テストを実行

プロジェクトには事前構成済みのテストが含まれます。実行してみましょう:

<div class="termy">

```console
$ python -m pytest
======================== test session starts ========================
collected 5 items

tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED

======================== 5 passed in 0.45s ========================
```

</div>

## 中核となる概念

### 1. FastAPI アプリケーションの構造

FastAPI-fastkit は **モジュール型アーキテクチャ** に従います:

- **`main.py`**: アプリケーションのエントリポイントとグローバルエンドポイント
- **`api/`**: API ルートの整理
- **`core/`**: アプリケーション設定
- **`crud/`**: ビジネスロジックとデータ操作
- **`schemas/`**: データ検証とシリアライズ
- **`tests/`**: 自動テスト

### 2. 依存関係管理

プロジェクトはモダンな Python の依存関係管理を使います:

- **仮想環境**: 隔離された Python 環境
- **requirements.txt**: すべての依存関係をリスト
- **自動インストール**: プロジェクト作成時に依存関係が自動でインストールされる

### 3. 開発サーバー

FastAPI-fastkit は **Uvicorn** を ASGI サーバーとして利用します:

- **自動リロード**: コード変更時に自動再起動
- **高速起動**: 開発のイテレーションが速い
- **本番運用対応**: 本番でも同じサーバーを利用

### 4. API ドキュメント

FastAPI が次を自動生成します:

- **OpenAPI 仕様**: 業界標準の API ドキュメント
- **Swagger UI**: 対話型のテストインターフェイス
- **ReDoc**: 別形式のドキュメント表示

## 次のステップ

おめでとうございます! 以下を達成しました:

✅ FastAPI-fastkit のインストール
✅ 最初のプロジェクト作成
✅ 開発サーバーの起動
✅ API エンドポイントのテスト
✅ 新しいルートの追加
✅ 既存コードの変更
✅ テストの実行

### 学習を続ける

1. **[最初のプロジェクト](first-project.md)**: 高度な機能を含む完全なブログ API を構築
2. **[ルートの追加](../user-guide/adding-routes.md)**: より複雑な API エンドポイントを学ぶ
3. **[テンプレートの利用](../user-guide/using-templates.md)**: 事前構築済みテンプレートを試す

### さらに試す

次の課題に挑戦してみましょう:

1. **検証の追加**: スキーマにデータ検証ルールを追加
2. **カスタムレスポンス**: ルートのレスポンス形式を変更
3. **環境変数**: `.env` ファイルで設定
4. **ミドルウェアの追加**: CORS や認証を実装
5. **データベース統合**: STANDARD スタックにアップグレードしてデータベース対応

### よくある問題と解決法

**サーバーが起動しない:**

- プロジェクトディレクトリにいるか確認
- 仮想環境が有効化されているか確認
- コードに構文エラーがないか確認

**インポートエラー:**

- すべての `__init__.py` ファイルが存在するか確認
- インポートパスが正しいか確認
- 仮想環境を使っているか確認

**ポートが既に使用中:**
```console
$ fastkit runserver --port 8080
```

## 学んだベストプラクティス

1. **仮想環境**: 常に隔離された環境を使う
2. **プロジェクト構造**: 整理されたモジュール型アーキテクチャに従う
3. **自動リロード**: 開発サーバーで素早くイテレーション
4. **API ドキュメント**: 自動ドキュメント生成を活用
5. **テスト**: 開発中は定期的にテストを実行

!!! tip "開発のヒント"
    - コーディング中は開発サーバーを起動したままにする
    - 対話型ドキュメント (`/docs`) で API をテストする
    - 役立つエラーメッセージはターミナルに表示される
    - こまめにバージョン管理にコミットする

これで FastAPI-fastkit を使って素晴らしい API を構築する準備が整いました! 🚀

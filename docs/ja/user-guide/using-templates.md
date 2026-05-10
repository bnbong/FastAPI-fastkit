# テンプレートの利用

FastAPI-fastkit は、さまざまな技術スタックですばやく開発を始められるよう、あらかじめ用意されたプロジェクトテンプレートを提供しています。

## 利用可能なテンプレート

`list-templates` コマンドで利用可能なテンプレートを確認できます:

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-custom-response │ Async Item Management API with    │
│                         │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI Item           │
│                         │ Management API                    │
│ fastapi-empty           │ No description                    │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-psql-orm        │ Dockerized FastAPI Item           │
│                         │ Management API with PostgreSQL    │
│ fastapi-default         │ Simple FastAPI Project            │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

## テンプレートの説明

### 1. `fastapi-default`

**シンプルな FastAPI プロジェクト**

- 必要十分な機能を備えた基本的な FastAPI セットアップ
- モックデータを使ったアイテム管理
- 学習やシンプルな API に最適
- 基本的な CRUD 操作を含む

**適した用途:**

- FastAPI の初心者
- シンプルな Web API
- 学習やプロトタイピング

### 2. `fastapi-async-crud`

**非同期アイテム管理 API サーバー**

- 完全に非同期な FastAPI アプリケーション
- async / await を使った高度な CRUD 操作
- I/O 操作のパフォーマンス向上
- 非同期パターンを用いたモックデータストレージ

**適した用途:**

- 高パフォーマンスアプリケーション
- I/O 集約的な処理
- モダンな非同期 Python 開発

### 3. `fastapi-custom-response`

**カスタムレスポンス機構を備えた非同期アイテム管理 API**

- カスタムレスポンスモデルとフォーマット
- 高度なエラーハンドリング
- ページネーション対応
- カスタム HTTP ステータスコードとレスポンス

**適した用途:**

- 特定のレスポンス形式が要求される API
- 高度なエラーハンドリングが必要な場面
- レスポンスにカスタムビジネスロジックを含める場合

### 4. `fastapi-dockerized`

**Docker 化された FastAPI アイテム管理 API**

- 完全な Docker コンテナ化
- 本番運用向けのデプロイ構成
- マルチステージ Docker ビルド
- 環境ベースの設定

**適した用途:**

- 本番デプロイ
- コンテナ化された環境
- DevOps と CI/CD パイプライン

### 5. `fastapi-psql-orm`

**PostgreSQL 対応の Docker 化された FastAPI アイテム管理 API**

- PostgreSQL データベース統合
- SQLAlchemy ORM と Alembic マイグレーション
- ローカル開発のための Docker Compose
- フル機能のデータベース CRUD 操作

**適した用途:**

- データベース駆動のアプリケーション
- 本番品質のデータストレージ
- 複雑なデータリレーションシップ

### 6. `fastapi-empty`

**最小構成の FastAPI プロジェクト**

- 必要最小限の FastAPI セットアップ
- あらかじめ用意された機能はありません
- カスタム開発のためのまっさらなスタート

**適した用途:**

- ゼロから始める
- 最小限の依存関係
- 独自のアーキテクチャ要件

## テンプレートからプロジェクトを作成する

`startdemo` コマンドでテンプレートからプロジェクトを作成します:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Blog API with PostgreSQL

Available Templates:
           fastapi-default
┌─────────────┬──────────────────────┐
│ Description │ Simple FastAPI       │
│             │ Project              │
│ Stack       │ FastAPI, Uvicorn     │
│ Database    │ Mock Data            │
│ Features    │ Basic CRUD           │
└─────────────┴──────────────────────┘

           fastapi-psql-orm
┌─────────────┬──────────────────────┐
│ Description │ Dockerized FastAPI   │
│             │ Item Management API  │
│             │ with PostgreSQL      │
│ Stack       │ FastAPI, PostgreSQL, │
│             │ SQLAlchemy, Docker   │
│ Database    │ PostgreSQL           │
│ Features    │ Full ORM, Migrations │
└─────────────┴──────────────────────┘

Select template (fastapi-default, fastapi-async-crud, fastapi-custom-response, fastapi-dockerized, fastapi-psql-orm, fastapi-empty): fastapi-psql-orm

           Project Information
┌──────────────┬─────────────────────┐
│ Project Name │ my-blog-api         │
│ Author       │ John Doe            │
│ Author Email │ john@example.com    │
│ Description  │ Blog API with       │
│              │ PostgreSQL          │
└──────────────┴─────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ psycopg2-binary   │
│ Dependency 6 │ python-dotenv     │
│ Dependency 7 │ pytest            │
└──────────────┴───────────────────┘

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

✨ FastAPI project 'my-blog-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## テンプレートの機能比較

| 機能 | Default | Async CRUD | Custom Response | Dockerized | PostgreSQL ORM | Empty |
|---|---|---|---|---|---|---|
| **基本 FastAPI** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **モックデータ** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **非同期サポート** | 基本 | ✅ | ✅ | ✅ | ✅ | ❌ |
| **カスタムレスポンス** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **データベース** | モック | モック | モック | モック | PostgreSQL | なし |
| **ORM** | ❌ | ❌ | ❌ | ❌ | SQLAlchemy | ❌ |
| **マイグレーション** | ❌ | ❌ | ❌ | ❌ | Alembic | ❌ |
| **テスト** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **適した用途** | 学習 | パフォーマンス | カスタム API | 本番運用 | DB アプリ | カスタム |

## テンプレートごとのセットアップ

### `fastapi-psql-orm` を使う

このテンプレートは PostgreSQL のフルセットアップを含みます。作成後:

1. **Docker で PostgreSQL を起動:**

<div class="termy">

```console
$ cd my-blog-api
$ docker-compose up -d postgres
Starting my-blog-api_postgres_1 ... done
```

</div>

2. **データベースマイグレーションを実行:**

<div class="termy">

```console
$ source .venv/bin/activate
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> bedcdc35b64a, first alembic
```

</div>

3. **API サーバーを起動:**

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### `fastapi-dockerized` を使う

このテンプレートは Docker のフル機能を提供します:

1. **Docker イメージのビルド:**

<div class="termy">

```console
$ cd my-dockerized-api
$ docker build -t my-dockerized-api .
Successfully built abc123def456
Successfully tagged my-dockerized-api:latest
```

</div>

2. **コンテナの起動:**

<div class="termy">

```console
$ docker run -p 8000:8000 my-dockerized-api
INFO:     Uvicorn running on http://0.0.0.0:8000
```

</div>

### `fastapi-custom-response` を使う

このテンプレートには高度なレスポンス処理が含まれています:

1. **カスタムレスポンスモデル:**

```python
from src.helper.pagination import PaginatedResponse
from src.schemas.base import StandardResponse

@router.get("/", response_model=PaginatedResponse[Item])
def read_items(skip: int = 0, limit: int = 10):
    items = items_crud.get_multi(skip=skip, limit=limit)
    total = items_crud.count()

    return PaginatedResponse(
        data=items,
        total=total,
        page=skip // limit + 1,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=StandardResponse[Item])
def create_item(item: ItemCreate):
    new_item = items_crud.create(item)
    return StandardResponse(
        data=new_item,
        message="Item created successfully",
        status_code=201
    )
```

2. **拡張されたエラーハンドリング:**

```python
from src.helper.exceptions import ItemNotFoundError, ValidationError

@router.get("/{item_id}", response_model=StandardResponse[Item])
def read_item(item_id: int):
    try:
        item = items_crud.get(item_id)
        return StandardResponse(data=item)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )
```

## テンプレートのプロジェクト構造

各テンプレートは一貫した、しかしテンプレートごとに調整された構造を持ちます:

### `fastapi-default` の構造
```
my-project/
├── src/
│   ├── main.py
│   ├── core/config.py
│   ├── api/
│   │   ├── api.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   └── mocks/mock_items.json
├── tests/
├── scripts/
└── requirements.txt
```

### `fastapi-psql-orm` の構造
```
my-project/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── db.py
│   ├── api/
│   │   ├── api.py
│   │   ├── deps.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   └── utils/
├── tests/
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── requirements.txt
```

## テンプレートのカスタマイズ

テンプレートからプロジェクトを作成した後、必要に応じてカスタマイズできます:

### 1. 新しいルートを追加

<div class="termy">

```console
$ fastkit addroute posts my-blog-api
$ fastkit addroute users my-blog-api
$ fastkit addroute comments my-blog-api
```

</div>

### 2. 設定の変更

`src/core/config.py` を編集してニーズに合わせます:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings (for PostgreSQL templates)
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. 環境変数の追加

プロジェクトルートに `.env` ファイルを作成します:

```env
# .env
PROJECT_NAME=My Blog API
VERSION=1.0.0
DEBUG=True

# Database (for PostgreSQL templates)
DATABASE_URL=postgresql://user:password@localhost:5432/myblogdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=myblogdb

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## テンプレートのテスト

各テンプレートはあらかじめ構成されたテストを備えています:

<div class="termy">

```console
$ cd my-blog-api
$ source .venv/bin/activate
$ python -m pytest

======================== test session starts ========================
tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED
======================== 5 passed in 0.23s ========================
```

</div>

## テンプレート開発のワークフロー

### 1. 適切なテンプレートを選ぶ

- **学習 / シンプルな API**: `fastapi-default`
- **高パフォーマンス**: `fastapi-async-crud`
- **カスタムレスポンス形式**: `fastapi-custom-response`
- **本番デプロイ**: `fastapi-dockerized`
- **データベースアプリケーション**: `fastapi-psql-orm`
- **独自アーキテクチャ**: `fastapi-empty`

### 2. 作成とセットアップ

<div class="termy">

```console
$ fastkit startdemo
# プロンプトに従う
$ cd your-project
$ source .venv/bin/activate
```

</div>

### 3. 開発

<div class="termy">

```console
# 開発サーバーを起動
$ fastkit runserver

# テストを実行
$ python -m pytest

# 新機能を追加
$ fastkit addroute new-resource your-project
```

</div>

### 4. デプロイ

本番向けテンプレート (`fastapi-dockerized`、`fastapi-psql-orm`) の場合:

<div class="termy">

```console
# 本番ビルド
$ docker build -t your-app .

# Docker Compose でデプロイ
$ docker-compose up -d
```

</div>

## ベストプラクティス

### 1. テンプレートを賢く選ぶ

- 学習にはシンプルなテンプレートから始める
- データ駆動型アプリにはデータベース対応のテンプレート
- 本番デプロイには Docker 対応テンプレート

### 2. 環境管理

- 設定には常に `.env` ファイルを使う
- 機密データはバージョン管理にコミットしない
- 開発と本番で異なる環境を使う

### 3. カスタマイズの方針

- 新しいルートは `fastkit addroute` で追加
- 既存コードは自分のビジネスロジックに合わせて変更
- プロジェクト構造は整理された状態を維持

### 4. テスト

- 開発中は定期的にテストを実行
- 実装した新機能にはテストを追加
- 同梱のテスト構造をガイドとして活用

## トラブルシューティング

### データベース接続の問題 (PostgreSQL テンプレート)

PostgreSQL に接続できない場合:

1. **Docker が動作しているか確認:**

   <div class="termy">
   ```console
   $ docker ps
   ```
   </div>

2. **PostgreSQL コンテナを確認:**

   <div class="termy">
   ```console
   $ docker-compose logs postgres
   ```
   </div>

3. **環境変数を確認:**

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Docker ビルドの失敗

Docker ビルドに失敗する場合:

1. **Dockerfile の構文を確認**
2. **必要なファイルがすべて存在するか確認**
3. **Docker デーモンが動作しているか確認**

### 依存関係が見つからない

import エラーが出る場合:

1. **仮想環境を有効化:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

2. **依存関係をインストール:**
   <div class="termy">
   ```console
   $ pip install -r requirements.txt
   ```
   </div>

## 次のステップ

テンプレートを理解できたら:

1. **[最初のプロジェクト](../tutorial/first-project.md)**: 完全なアプリケーションを構築
2. **[ルートの追加](adding-routes.md)**: テンプレートベースのプロジェクトを拡張
3. **[CLI リファレンス](cli-reference.md)**: 利用可能なすべてのコマンドを習得

!!! tip "テンプレートのヒント"
    - テンプレートは出発点であって最終的な解ではありません
    - 自分の要件に合わせてテンプレートをカスタマイズしましょう
    - テンプレートのコードを読み、FastAPI のベストプラクティスを学びましょう
    - 自分のカスタマイズを追えるようバージョン管理を活用しましょう

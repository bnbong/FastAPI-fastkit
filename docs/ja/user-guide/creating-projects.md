# プロジェクトの作成

FastAPI-fastkit でさまざまな種類の FastAPI プロジェクトを作成する詳細ガイドです。

## 基本のプロジェクト作成

### 1. 対話型モードでのプロジェクト作成

最も基本的な方法は、対話型でプロジェクトを作成することです:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Awesome FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-api          │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ Awesome FastAPI project │
└──────────────┴─────────────────────────┘
```

</div>

### 2. スタックの選択

プロジェクトに含める依存関係スタックを選びます:

#### MINIMAL スタック (デフォルト)

最も基本的な FastAPI プロジェクトです:

- `fastapi` - FastAPI フレームワーク
- `uvicorn` - ASGI サーバー
- `pydantic` - データ検証
- `pydantic-settings` - 設定管理

**適した用途:**

- FastAPI の学習
- シンプルな API
- プロトタイプ
- マイクロサービス

#### STANDARD スタック

データベース対応とテストを含みます:

- MINIMAL のすべての依存関係
- `sqlalchemy` - データベース操作のための ORM
- `alembic` - データベースマイグレーション
- `pytest` - テストフレームワーク

**適した用途:**

- 多くの Web アプリケーション
- データベースを使う API
- 本番運用を見据えたアプリケーション
- チームプロジェクト

#### FULL スタック

完全な開発環境を提供します:

- STANDARD のすべての依存関係
- `redis` - キャッシュとセッションストレージ
- `celery` - バックグラウンドタスク処理

**適した用途:**

- 大規模アプリケーション
- 高パフォーマンスが要求される場面
- 複雑なビジネスロジック
- エンタープライズアプリケーション

## 高度なプロジェクトオプション

### プロジェクト構成のカスタマイズ

作成時にプロジェクトをカスタマイズできます:

<div class="termy">

```console
$ fastkit init
Enter the project name: advanced-api
Enter the author name: Development Team
Enter the author email: dev@company.com
Enter the project description: Advanced FastAPI application with custom features

# データベース対応のため STANDARD スタックを選択
Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### プロジェクト構造の説明

プロジェクトを作成すると、FastAPI-fastkit は次の構造を生成します:

```
my-awesome-api/
├── .venv/                      # 仮想環境
├── src/                        # ソースコード
│   ├── __init__.py
│   ├── main.py                # アプリケーションのエントリポイント
│   ├── core/                  # コア設定
│   │   ├── __init__.py
│   │   └── config.py         # 設定 / 環境変数
│   ├── api/                   # API レイヤー
│   │   ├── __init__.py
│   │   ├── api.py            # メインの API ルーター
│   │   └── routes/           # 個別のルートモジュール
│   │       ├── __init__.py
│   │       └── items.py      # サンプルの items エンドポイント
│   ├── crud/                  # データベース操作
│   │   ├── __init__.py
│   │   └── items.py          # items 用の CRUD 操作
│   ├── schemas/               # Pydantic モデル
│   │   ├── __init__.py
│   │   └── items.py          # データ検証スキーマ
│   └── mocks/                 # テストデータ
│       ├── __init__.py
│       └── mock_items.json   # 開発用のサンプルデータ
├── tests/                     # テストスイート
│   ├── __init__.py
│   ├── conftest.py           # テスト設定
│   └── test_items.py         # サンプルテスト
├── scripts/                   # ユーティリティスクリプト
│   ├── test.sh               # テスト実行
│   ├── coverage.sh           # カバレッジ測定
│   └── lint.sh               # コードリンティング
├── requirements.txt           # Python 依存関係
├── setup.py                  # パッケージ設定
└── README.md                 # プロジェクトドキュメント
```

### 3. パッケージマネージャーの選択

FastAPI-fastkit は複数の Python パッケージマネージャーをサポートしています。開発ワークフローに最も合うものを選んでください:

#### 利用可能なパッケージマネージャー

<div class="termy">

```console
Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

各パッケージマネージャーの利点は次のとおりです:

#### UV (デフォルト・推奨)

**Rust 製の高速パッケージマネージャー**

- ⚡ **超高速**: pip より 10〜100 倍高速
- 🔧 **そのまま置き換えやすい**: pip のワークフローとほぼ同じ感覚で使える
- 📦 **モダン**: PEP 621 を完全サポート
- 🛠️ **信頼性**: 再現性のある依存関係解決

**生成されるファイル:**

- `pyproject.toml` (PEP 621 形式)
- `uv.lock` (ロックファイル)

**作成後の使い方:**
```console
cd my-project
uv sync              # 依存関係をインストール
uv add requests      # 新しい依存関係を追加
uv run pytest       # テストを実行
```

#### PDM

**モダンな Python 依存関係管理**

- 🚀 **モダン**: PEP 582 / PEP 621 をサポート
- 🧠 **賢い**: 高度な依存関係解決
- 💼 **業務向け**: ワークスペースとマルチプロジェクト対応
- 📊 **解析**: 依存関係解析ツール

**生成されるファイル:**

- `pyproject.toml` (PEP 621 形式)
- `pdm.lock` (ロックファイル)

**作成後の使い方:**
```console
cd my-project
pdm install          # 依存関係をインストール
pdm add requests     # 新しい依存関係を追加
pdm run pytest      # テストを実行
```

#### Poetry

**成熟した依存関係管理とパッケージング**

- ✅ **定番**: 成熟しており広く採用されている
- 📦 **統合**: ビルド・公開までサポート
- 🔒 **再現可能**: poetry.lock により厳密なバージョン管理
- 🏗️ **包括的**: プロジェクトのライフサイクル全体を管理

**生成されるファイル:**

- `pyproject.toml` (Poetry 形式)
- `poetry.lock` (ロックファイル)

**作成後の使い方:**
```console
cd my-project
poetry install       # 依存関係をインストール
poetry add requests  # 新しい依存関係を追加
poetry run pytest   # テストを実行
```

#### PIP

**標準の Python パッケージマネージャー**

- 🏠 **同梱**: Python に標準で含まれる
- 🌍 **どこでも動く**: あらゆる環境で利用可能
- 📚 **慣れている**: 多くの開発者がすでに知っている
- 🔧 **シンプル**: 素直なワークフロー

**生成されるファイル:**

- `requirements.txt`

**作成後の使い方:**
```console
cd my-project
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install requests
pytest
```

#### パッケージマネージャーの指定

好みのパッケージマネージャーは次の方法で指定できます:

**対話型選択 (デフォルト):**
```console
$ fastkit init
# ... パッケージマネージャー選択のプロンプトに従う
```

**コマンドラインオプション:**
```console
$ fastkit init --package-manager poetry
$ fastkit init --package-manager pdm
$ fastkit init --package-manager uv
$ fastkit init --package-manager pip
```

### 各ディレクトリの役割

#### `src/` ディレクトリ

Python のパッケージングのベストプラクティスである **src レイアウト** に従って、アプリケーションのソースコードをすべて格納します。

#### `core/` モジュール

- **config.py**: アプリケーションの設定、環境変数、構成
- すべての設定管理を一元化
- 環境別設定のための `.env` ファイルをサポート

#### `api/` モジュール

- **api.py**: すべてのサブルーターをまとめるメインの API ルーター
- **routes/**: 各リソースに対応する個別のルートモジュール
- API エンドポイントごとに関心事を明確に分離

#### `crud/` モジュール

- データベース操作とビジネスロジック
- **C**reate、**R**ead、**U**pdate、**D**elete の操作
- API ルートとデータストレージの間の抽象化レイヤー

#### `schemas/` モジュール

- データ検証のための Pydantic モデル
- リクエスト / レスポンススキーマ
- 型定義とデータモデル

#### `tests/` ディレクトリ

- アプリケーションの完全なテストスイート
- ユニットテストと統合テストを含む
- pytest であらかじめ構成済み

## スタック比較

| 機能 | MINIMAL | STANDARD | FULL |
|---|---|---|---|
| FastAPI と Uvicorn | ✅ | ✅ | ✅ |
| データ検証 | ✅ | ✅ | ✅ |
| データベース対応 | ❌ | ✅ | ✅ |
| マイグレーション | ❌ | ✅ | ✅ |
| テストフレームワーク | ❌ | ✅ | ✅ |
| キャッシュ (Redis) | ❌ | ❌ | ✅ |
| バックグラウンドタスク | ❌ | ❌ | ✅ |
| **適した用途** | 学習 / シンプルな API | 多くのアプリケーション | エンタープライズ / 複雑なアプリ |

## プロジェクト作成の例

### 例 1: 学習用プロジェクト

<div class="termy">

```console
$ fastkit init
Enter the project name: fastapi-learning
Enter the author name: Student
Enter the author email: student@example.com
Enter the project description: Learning FastAPI basics

Select stack (minimal, standard, full): minimal
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 例 2: EC サイト API

<div class="termy">

```console
$ fastkit init
Enter the project name: ecommerce-api
Enter the author name: E-commerce Team
Enter the author email: team@ecommerce.com
Enter the project description: E-commerce platform API

Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 例 3: 高パフォーマンスアプリケーション

<div class="termy">

```console
$ fastkit init
Enter the project name: enterprise-api
Enter the author name: Enterprise Team
Enter the author email: enterprise@company.com
Enter the project description: High-performance enterprise API

Select stack (minimal, standard, full): full
Do you want to proceed with project creation? [y/N]: y
```

</div>

## プロジェクト作成後

### 1. 仮想環境の有効化

<div class="termy">

```console
$ cd my-awesome-api
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

### 2. インストールの確認

<div class="termy">

```console
$ pip list
Package         Version
fastapi         0.104.1
uvicorn         0.24.0
pydantic        2.5.0
...
```

</div>

### 3. 開発の開始

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

## 設定管理

### 環境変数

プロジェクトは `.env` ファイルによる環境ベースの設定をサポートしています。

プロジェクトルートに `.env` ファイルを作成しましょう:

```env
# .env
APP_NAME=My Awesome API
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### コードからの設定

生成された `src/core/config.py` がこれらの変数を自動で読み込みます:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key"

    class Config:
        env_file = ".env"

settings = Settings()
```

## カスタマイズ

### 依存関係の追加

プロジェクト作成後、追加の依存関係をインストールできます:

<div class="termy">

```console
$ pip install requests httpx python-jose
$ pip freeze > requirements.txt
```

</div>

### プロジェクト構造の変更

生成された構造はベストプラクティスに従っていますが、必要に応じて変更できます:

- `src/` に新しいモジュールを追加
- `api/routes/` にルートファイルを追加
- `crud/` で CRUD 操作を拡張
- `schemas/` にスキーマを追加

## ベストプラクティス

### 1. 仮想環境

プロジェクトの依存関係を分離するため、常に仮想環境を使いましょう:

```bash
# 仮想環境付きでプロジェクトを作成
$ fastkit init  # .venv/ が自動生成される

# 作業時に有効化
$ source .venv/bin/activate
```

### 2. バージョン管理

プロジェクト作成後に Git リポジトリを初期化しましょう:

<div class="termy">

```console
$ cd my-awesome-api
$ git init
$ git add .
$ git commit -m "Initial commit - FastAPI project setup"
```

</div>

### 3. 環境設定

- ローカル開発には `.env` ファイルを使用
- 本番環境では環境変数を利用
- 機密データはバージョン管理に決してコミットしない

### 4. テスト

同梱のテストフレームワークを活用しましょう:

<div class="termy">

```console
$ python -m pytest
$ bash scripts/test.sh
```

</div>

## 次のステップ

プロジェクトを作成したら:

1. **[ルートの追加](adding-routes.md)**: 新しい API エンドポイントの追加方法を学ぶ
2. **[CLI リファレンス](cli-reference.md)**: 利用可能なすべてのコマンドを習得
3. **[最初のプロジェクトのチュートリアル](../tutorial/first-project.md)**: 完全なアプリケーションを構築

!!! tip "プロジェクト作成のヒント"
    - プロジェクト要件にマッチするスタックを選びましょう
    - 学習なら MINIMAL、ほとんどのプロジェクトなら STANDARD から
    - プロジェクト構造は拡張性と保守性を意識した設計です
    - 生成されるコードはすべて FastAPI のベストプラクティスに従っています

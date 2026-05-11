# CLI リファレンス

FastAPI-fastkit の全 CLI コマンドを網羅したリファレンスです。

## グローバルオプション

すべてのコマンドは次のグローバルオプションをサポートしています:

```console
$ fastkit [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### グローバルオプション

| オプション | 説明 |
|---|---|
| `--version` | FastAPI-fastkit のバージョンを表示 |
| `--help` | ヘルプメッセージを表示 |

### 例

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0

$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## コマンド

### `init`

対話型セットアップで新しい FastAPI プロジェクトを作成します。

#### 構文

```console
$ fastkit init [OPTIONS]
```

#### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--package-manager` | 使用するパッケージマネージャー (pip, uv, pdm, poetry) | uv |
| `--help` | コマンドのヘルプを表示 | - |

#### 対話型プロンプト

`init` コマンドは以下を尋ねます:

1. **プロジェクト名**: ディレクトリ名およびパッケージ名
2. **作者名**: パッケージの作者情報
3. **作者メール**: パッケージの連絡先メール
4. **プロジェクト説明**: プロジェクトの概要
5. **スタック選択**: minimal、standard、full から選択
6. **パッケージマネージャー選択**: pip、uv、pdm、poetry から選択 (`--package-manager` で指定しない場合)

#### スタックオプション

**MINIMAL スタック:**

- `fastapi` - FastAPI フレームワーク
- `uvicorn` - ASGI サーバー
- `pydantic` - データ検証
- `pydantic-settings` - 設定管理

**STANDARD スタック:**

- MINIMAL スタックのすべてのパッケージ
- `sqlalchemy` - SQL ツールキットおよび ORM
- `alembic` - データベースマイグレーションツール
- `pytest` - テストフレームワーク

**FULL スタック:**

- STANDARD スタックのすべてのパッケージ
- `redis` - インメモリデータストア
- `celery` - 分散タスクキュー

#### 例

<div class="termy">

```console
$ fastkit init
Enter the project name: my-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome API

Select stack (minimal, standard, full): standard
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-api' has been created successfully!
```

</div>

#### 生成される構造

次の構造のプロジェクトが作成されます:

```
my-api/
├── .venv/                    # 仮想環境
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI アプリケーション
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # 設定
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API ルーター集約
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── items.py     # サンプルルート
│   ├── crud/
│   │   ├── __init__.py
│   │   └── items.py         # CRUD 操作
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── items.py         # Pydantic スキーマ
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # テストデータ
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

### `addroute`

既存の FastAPI プロジェクトに新しい API ルートを追加します。

#### 構文

```console
$ fastkit addroute ROUTE_NAME [PROJECT_DIR] [OPTIONS]
```

#### 引数

| 引数 | 説明 | 必須 |
|---|---|---|
| `ROUTE_NAME` | 新しいルート名 (複数形を推奨) | はい |
| `PROJECT_DIR` | 対象のプロジェクトディレクトリ (デフォルトは `.` (現在のディレクトリ)) | いいえ |

#### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--help` | コマンドのヘルプを表示 | - |

#### 例

<div class="termy">

```console
$ cd my-api
$ fastkit addroute users
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-api                                   │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-api                                 │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-api'
```

</div>

`cd` しなくても、対象のプロジェクトを名前で指定できます:

<div class="termy">

```console
$ fastkit addroute users my-api
```

</div>

#### 生成されるファイル

プロジェクトに次のファイルが作成されます:

- `src/api/routes/users.py` - ルートハンドラ
- `src/crud/users.py` - CRUD 操作
- `src/schemas/users.py` - Pydantic スキーマ

また、新しいルーターを取り込むよう `src/api/api.py` も自動更新されます。

#### 生成されるエンドポイント

完全な CRUD エンドポイントが作成されます:

| メソッド | エンドポイント | 説明 |
|---|---|---|
| `GET` | `/api/v1/users/` | すべてのユーザーを取得 |
| `POST` | `/api/v1/users/` | 新しいユーザーを作成 |
| `GET` | `/api/v1/users/{user_id}` | 特定のユーザーを取得 |
| `PUT` | `/api/v1/users/{user_id}` | ユーザーを更新 |
| `DELETE` | `/api/v1/users/{user_id}` | ユーザーを削除 |

### `startdemo`

あらかじめ用意されたテンプレートから FastAPI プロジェクトを作成します。

#### 構文

```console
$ fastkit startdemo [OPTIONS]
```

#### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--package-manager` | 使用するパッケージマネージャー (pip, uv, pdm, poetry) | uv |
| `--help` | コマンドのヘルプを表示 | - |

#### 対話型プロンプト

`startdemo` コマンドは以下を尋ねます:

1. **プロジェクト名**: 新しいプロジェクトのディレクトリ名
2. **作者名**: パッケージの作者情報
3. **作者メール**: 連絡先メール
4. **プロジェクト説明**: プロジェクトの概要
5. **パッケージマネージャー選択**: pip、uv、pdm、poetry から選択 (`--package-manager` で指定しない場合)

#### 利用可能なテンプレート

| テンプレート | 説明 | 機能 |
|---|---|---|
| `fastapi-default` | シンプルな FastAPI プロジェクト | 基本的な CRUD、モックデータ |
| `fastapi-async-crud` | 非同期アイテム管理 API | async/await、パフォーマンス重視 |
| `fastapi-custom-response` | カスタムレスポンス機構 | カスタムレスポンス、ページネーション |
| `fastapi-dockerized` | Docker 化された FastAPI API | Docker、本番運用対応 |
| `fastapi-psql-orm` | PostgreSQL 連携 FastAPI API | PostgreSQL、SQLAlchemy、Alembic |
| `fastapi-empty` | 最小構成 FastAPI プロジェクト | 必要最低限のセットアップ |

#### 例

<div class="termy">

```console
$ fastkit startdemo fastapi-psql-orm
Enter the project name: my-blog
Enter the author name: Jane Smith
Enter the author email: jane@example.com
Enter the project description: Blog API with PostgreSQL

Select package manager (pip, uv, pdm, poetry) [uv]: poetry
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog' from 'fastapi-psql-orm' has been created!
```

</div>

### `runserver`

FastAPI 開発サーバーを起動します。

#### 構文

```console
$ fastkit runserver [OPTIONS]
```

#### オプション

| オプション | 短縮形 | 説明 | デフォルト |
|---|---|---|---|
| `--host` | `-h` | バインドするホスト | `127.0.0.1` |
| `--port` | `-p` | バインドするポート | `8000` |
| `--reload` | `-r` | 自動リロードを有効化 | `True` |
| `--workers` | `-w` | ワーカー数 | `1` |
| `--help` | | コマンドのヘルプを表示 | - |

#### 例

<div class="termy">

```console
# 基本的な使い方 (デフォルト設定)
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000

# ホストとポートのカスタマイズ
$ fastkit runserver --host 0.0.0.0 --port 8080
INFO:     Uvicorn running on http://0.0.0.0:8080

# 自動リロードを無効化
$ fastkit runserver --no-reload
INFO:     Uvicorn running on http://127.0.0.1:8000

# 複数ワーカー (本番運用)
$ fastkit runserver --workers 4
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

#### 動作要件

- FastAPI プロジェクトのディレクトリで実行する必要がある
- プロジェクトに FastAPI アプリを含む `src/main.py` が存在する必要がある
- 仮想環境を有効化しておくこと

### `list-templates`

利用可能なすべての FastAPI プロジェクトテンプレートを一覧表示します。

#### 構文

```console
$ fastkit list-templates [OPTIONS]
```

#### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--help` | コマンドのヘルプを表示 | - |

#### 例

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

## 環境変数

FastAPI-fastkit は次の環境変数を尊重します:

| 変数 | 説明 | デフォルト |
|---|---|---|
| `FASTKIT_CONFIG_DIR` | 設定ディレクトリ | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | カスタムテンプレートのディレクトリ | 組み込みテンプレート |
| `FASTKIT_LOG_LEVEL` | ロギングレベル | `INFO` |

### 例

<div class="termy">

```console
# 設定ディレクトリのカスタマイズ
$ export FASTKIT_CONFIG_DIR=~/my-fastkit-config
$ fastkit init

# カスタムテンプレートディレクトリ
$ export FASTKIT_TEMPLATES_DIR=~/my-templates
$ fastkit list-templates

# デバッグログ
$ export FASTKIT_LOG_LEVEL=DEBUG
$ fastkit init
```

</div>

## 設定ファイル

FastAPI-fastkit はデフォルト設定として設定ファイルを利用できます。

### 設定ファイルの場所

1. `$FASTKIT_CONFIG_DIR/config.yaml` (`FASTKIT_CONFIG_DIR` が設定されている場合)
2. `~/.fastkit/config.yaml` (デフォルト)
3. `./fastkit.yaml` (プロジェクト固有)

### 設定ファイル形式

```yaml
# ~/.fastkit/config.yaml
default:
  author:
    name: "Your Name"
    email: "your.email@example.com"

  project:
    stack: "standard"
    create_venv: true
    install_deps: true

  server:
    host: "127.0.0.1"
    port: 8000
    reload: true

templates:
  custom_dir: "~/my-templates"

logging:
  level: "INFO"
  file: "~/.fastkit/logs/fastkit.log"
```

## よくあるワークフロー

### 1. 新しいプロジェクトを作成する

<div class="termy">

```console
# 新しいプロジェクトを作成
$ fastkit init
# プロンプトに従う ...

# プロジェクトに移動
$ cd my-awesome-api

# 仮想環境を有効化
$ source .venv/bin/activate

# 開発サーバーを起動
$ fastkit runserver
```

</div>

### 2. 既存プロジェクトに機能を追加する

<div class="termy">

```console
# 複数のルートを追加 (2 番目の位置引数 = 対象のプロジェクトディレクトリ)
$ fastkit addroute users my-api
$ fastkit addroute products my-api
$ fastkit addroute orders my-api

# API をテスト
$ fastkit runserver
# http://127.0.0.1:8000/docs を開く
```

</div>

### 3. 複雑なプロジェクトのためにテンプレートを利用する

<div class="termy">

```console
# 利用可能なテンプレートを表示
$ fastkit list-templates

# テンプレートから作成
$ fastkit startdemo
# データベースプロジェクトには fastapi-psql-orm を選択

# データベースのセットアップ (PostgreSQL テンプレートの場合)
$ cd my-project
$ docker-compose up -d postgres
$ source .venv/bin/activate
$ alembic upgrade head
$ fastkit runserver
```

</div>

## トラブルシューティング

### コマンドが見つからない

`fastkit` コマンドが見つからない場合:

1. **インストールを確認:**
   <div class="termy">
   ```console
   $ pip show fastapi-fastkit
   ```
   </div>

2. **必要に応じて再インストール:**
   <div class="termy">
   ```console
   $ pip uninstall fastapi-fastkit
   $ pip install fastapi-fastkit
   ```
   </div>

3. **PATH を確認:**
   <div class="termy">
   ```console
   $ which fastkit
   ```
   </div>

### 仮想環境の問題

仮想環境の作成に失敗する場合:

1. **Python のバージョンを確認:**
   <div class="termy">
   ```console
   $ python --version  # 3.12+ である必要があります
   ```
   </div>

2. **venv モジュールを確認:**
   <div class="termy">
   ```console
   $ python -m venv --help
   ```
   </div>

3. **手動で仮想環境を作成:**
   <div class="termy">
   ```console
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ```
   </div>

### サーバーが起動しない

`fastkit runserver` に失敗する場合:

1. **プロジェクトディレクトリにいるか確認**
2. **`src/main.py` が存在するか確認**
3. **仮想環境を有効化:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

4. **構文エラーを確認:**
   <div class="termy">
   ```console
   $ python -c "from src.main import app"
   ```
   </div>

### ポートが既に使われている

ポート 8000 がビジー状態の場合:

<div class="termy">

```console
# 別のポートを使う
$ fastkit runserver --port 8080

# あるいは既存プロセスを終了
$ lsof -ti:8000 | xargs kill -9
```

</div>

## 高度な使い方

### カスタムテンプレート

次の手順でカスタムテンプレートを作成できます:

1. **テンプレートディレクトリを作成:**
   ```
   my-template/
   ├── src/
   │   └── main.py-tpl
   ├── requirements.txt-tpl
   └── setup.py-tpl
   ```

2. **環境変数を設定:**
   <div class="termy">
   ```console
   $ export FASTKIT_TEMPLATES_DIR=~/my-templates
   ```
   </div>

3. **カスタムテンプレートを利用:**
   <div class="termy">
   ```console
   $ fastkit startdemo
   # 一覧にカスタムテンプレートが表示されます
   ```
   </div>

### FastAPI-fastkit をスクリプトから使う

FastAPI-fastkit はスクリプトから利用できます:

```bash
#!/bin/bash
# create-microservices.sh

for service in users products orders; do
    echo "Creating $service service..."
    fastkit init <<EOF
$service-service
Company Team
team@company.com
$service microservice
minimal
y
EOF

    cd "$service-service"
    fastkit addroute "$service"
    cd ..
done
```

### CI/CD との統合

GitHub Actions ワークフローの例:

```yaml
name: Test FastAPI-fastkit Project

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install FastAPI-fastkit
      run: pip install fastapi-fastkit

    - name: Create test project
      run: |
        fastkit init <<EOF
        test-project
        CI
        ci@example.com
        Test project
        standard
        y
        EOF

    - name: Test project
      run: |
        cd test-project
        source .venv/bin/activate
        python -m pytest
```

## パッケージマネージャーのサポート

FastAPI-fastkit は複数の Python パッケージマネージャーをサポートしており、ワークフローに最も合うものを選べます。

### サポートされるパッケージマネージャー

| マネージャー | 説明 | 依存関係ファイル | 適した用途 |
|---|---|---|---|
| **UV** (デフォルト) | 高速な Python パッケージマネージャー | `pyproject.toml` | 速度とパフォーマンス |
| **PDM** | モダンな Python 依存関係管理 | `pyproject.toml` | 高度な依存関係解決 |
| **Poetry** | Python の依存関係管理とパッケージング | `pyproject.toml` | Poetry 中心のワークフロー |
| **PIP** | 標準の Python パッケージマネージャー | `requirements.txt` | 伝統的な Python 開発 |

### パッケージマネージャーの指定

#### グローバル設定

すべてのプロジェクトで使うパッケージマネージャーを指定できます:

```console
# コマンドラインオプションで指定
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

#### プロジェクトごとの選択

各プロジェクトで異なるパッケージマネージャーを使えます。プロジェクト作成時に選択し、次に影響します:

- **依存関係ファイル形式**: 各マネージャーが適切なファイルを作成
- **仮想環境管理**: 有効化方法が異なる
- **依存関係のインストール**: マネージャー固有のコマンド

### パッケージマネージャーの特徴

#### UV (デフォルト)
- **高速**: Rust 製で非常に高速な依存関係解決
- **互換性**: pip・pip-tools をそのまま置き換えられる
- **モダン**: PEP 621 のプロジェクトメタデータをサポート

<div class="termy">

```console
$ fastkit init --package-manager uv
# UV 用設定の pyproject.toml を生成
```

</div>

#### PDM
- **モダン**: PEP 582 / PEP 621 をサポート
- **高度**: 洗練された依存関係解決
- **柔軟**: 複数のプロジェクトレイアウトに対応

<div class="termy">

```console
$ fastkit init --package-manager pdm
# PDM 用設定の pyproject.toml を生成
```

</div>

#### Poetry
- **定番**: 成熟しており広く採用
- **統合**: ビルド・公開までサポート
- **ロックファイル**: poetry.lock により再現可能なビルド

<div class="termy">

```console
$ fastkit init --package-manager poetry
# Poetry 用設定の pyproject.toml を生成
```

</div>

#### PIP
- **標準**: Python に標準で含まれる
- **互換性**: あらゆる環境で動作
- **シンプル**: 素直な依存関係管理

<div class="termy">

```console
$ fastkit init --package-manager pip
# requirements.txt を生成
```

</div>

### プロジェクトでの作業

特定のパッケージマネージャーでプロジェクトを作成した後は:

#### UV プロジェクト
```console
cd my-project
uv sync          # 依存関係をインストール
uv add requests  # 新しい依存関係を追加
uv run pytest   # 環境内でコマンドを実行
```

#### PDM プロジェクト
```console
cd my-project
pdm install      # 依存関係をインストール
pdm add requests # 新しい依存関係を追加
pdm run pytest  # 環境内でコマンドを実行
```

#### Poetry プロジェクト
```console
cd my-project
poetry install      # 依存関係をインストール
poetry add requests # 新しい依存関係を追加
poetry run pytest  # 環境内でコマンドを実行
```

#### PIP プロジェクト
```console
cd my-project
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install requests
pytest
```

## 次のステップ

CLI を理解できたら:

1. **[クイックスタート](quick-start.md)**: コマンドを実際に試す
2. **[最初のプロジェクト](../tutorial/first-project.md)**: 完全なアプリケーションを構築
3. **[コントリビュート](../contributing/development-setup.md)**: FastAPI-fastkit に貢献する

!!! tip "CLI のヒント"
    - 詳細なヘルプを得るには各コマンドに `--help` を付けましょう
    - 既定値を設定すると、プロジェクト作成を高速化できます
    - 構成が複雑なプロジェクトではテンプレートを活用しましょう
    - コマンドを組み合わせて強力なワークフローを作りましょう

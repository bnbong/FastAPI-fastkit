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
| `--interactive` | ガイド付きセットアップ: アーキテクチャプリセットを選び、続いて機能を選択 | off |
| `--config <path>` | 保存済みの設定ファイルから、プロンプトなしでプロジェクトを作成 | - |
| `--save-config <path>` | `--interactive` と併用し、回答した設定をこのパスに書き出す | - |
| `--project-name` | プロジェクト名 (省略時はプロンプトで入力) | - |
| `--author` | 作者名 (省略時はプロンプトで入力) | - |
| `--author-email` | 作者のメールアドレス (省略時はプロンプトで入力) | - |
| `--description` | プロジェクトの説明 (省略時はプロンプトで入力) | - |
| `--package-manager` | 使用するパッケージマネージャー (pip, uv, pdm, poetry) | uv |
| `--dry-run` | 何も書き込まずに、作成されるファイルとパッケージを表示 | off |
| `--no-venv` | 仮想環境の作成をスキップ (`--no-install` を含意) | off |
| `--no-install` | 依存関係のインストールをスキップ | off |
| `--yes` / `-y` | プロジェクトをその場にデプロイするとき、既存ファイルを上書きする前の確認を行わない | off |
| `--help` | コマンドのヘルプを表示 | - |

#### 設定ファイル (`--config` / `--save-config`)

対話型セッションの回答は単純なマッピングであり、そのマッピングはファイルとして持ち運べます。これにより、
プロジェクトの作成をコミットし、レビューし、再現できるものにできます。

```console
# 対話型セッションを記録する
$ fastkit init --interactive --save-config fastkit.config.json

# 後で、プロンプトを一切出さずに再現する
$ fastkit init --config fastkit.config.json
```

`--save-config` を渡さなかった場合、最後まで進んだ対話型の実行では、選択内容を保存するかどうかと保存先を
尋ねられます。このプロンプトは人間がターミナルの前にいる場合にだけ表示されます — パイプ経由や CI での実行
では何も表示されず、代わりにフラグでオプトインします。

**サポートされる形式** はファイルの拡張子で決まります:

| 拡張子 | 利用可否 |
|---|---|
| `.json` | 常に利用可能 (標準ライブラリ) |
| `.toml` | 常に利用可能 (標準ライブラリ) |
| `.yaml` / `.yml` | PyYAML がインストールされている場合のみ — fastkit はこれをランタイム依存関係として追加しません |

読み込まれるファイルは、トップレベルにマッピングを持ち、少なくとも `project_name`、`author`、`author_email`
を含んでいる必要があります。その後、対話型プロンプトと同じルール (プロジェクト名の形式、メールアドレスの
形式、`all_dependencies` がリストであること) で検証され、何かを書き込む前にすべての問題が報告されます。
機能の選択だけを列挙し、`all_dependencies` を含まないファイルは対話型ビルダーを通じて展開されるため、
手書きの設定とウィザードのセッションは同じパッケージセットに解決されます。

最小限の例:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv"
}
```

#### 設定ファイルのスキーマ

すべての設定ファイル — 手書きのものも `--save-config` で生成されたものも — は、ジェネレーターに渡される前に
同じノーマライザー (`backend/project_builder/config_schema.py` の `normalize_project_config`) を通ります。
未知のキー、既知の項目に対する未知の選択肢、型の誤った値は、黙って無視されるのではなく、問題のある名前と
実際に許可されている値の一覧とともに拒否されます。

| キー | 形式 | 備考 |
|---|---|---|
| `project_name`、`author`、`author_email` | 文字列 | 必須 |
| `description` | 文字列 | 必須 |
| `architecture_preset` (別名 `preset`) | `"minimal"` \| `"single-module"` \| `"classic-layered"` \| `"domain-starter"` | 両方の表記がある場合は一致している必要があります |
| `package_manager` | `"pip"` \| `"uv"` \| `"pdm"` \| `"poetry"` | |
| `database` | 文字列、または `{"type": <choice>}` | `PostgreSQL`、`MySQL`、`MongoDB`、`Redis`、`SQLite`、`None` |
| `authentication`、`async_tasks`、`testing`、`caching`、`monitoring`、`migrations`、`logging` | 文字列、または `{"type": <choice>}` | 単一選択の項目 — 各項目の選択肢は上記の [機能カタログ](#interactive-builder-feature-catalog-interactive) を参照 |
| `utilities`、`tooling` | 文字列のリスト | 複数選択の項目 — 選択肢は同じカタログを参照 |
| `deployment` | 文字列のリスト | `Docker`、`docker-compose` の部分集合。`docker-compose` を選ぶと `Docker` も自動的に含まれます |
| `custom_packages` | 文字列のリスト | そのままインストールされる追加パッケージ |

どの項目も、素の選択肢 (`"authentication": "JWT"`) と、`database` やプロジェクト自身の `[tool.fastapi-fastkit]`
メタデータが使う `{"type": ...}` のマッピング形式 (`"authentication": {"type": "JWT"}`) のどちらでも受け付けます
— どちらも同じ正規形に正規化され、`--save-config` は常に正規形である素の文字列の形式で書き出します。

ほとんどの項目を使った設定の例:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv",
  "database": "PostgreSQL",
  "authentication": "JWT",
  "async_tasks": "Celery",
  "caching": "Redis",
  "migrations": "Alembic",
  "tooling": ["ruff", "makefile"],
  "deployment": ["Docker"]
}
```

同じ設定を TOML で書いた場合:

```toml
project_name = "orders-api"
author = "Developer Kim"
author_email = "developer@example.com"
description = "Domain-oriented orders service"
architecture_preset = "domain-starter"
package_manager = "uv"
database = "PostgreSQL"
authentication = "JWT"
async_tasks = "Celery"
caching = "Redis"
migrations = "Alembic"
tooling = ["ruff", "makefile"]
deployment = ["Docker"]
```

#### プレビューとステップのスキップ

`--dry-run` は、作成されるツリーとインストールされるパッケージを — それをインストールするパッケージ
マネージャーとともに — 表示し、ディスクに一切触れずに終了します:

```console
$ fastkit init --config fastkit.config.json --dry-run
```

`--no-install` は仮想環境を作成した時点で停止します。`--no-venv` は仮想環境の作成も (したがって
インストールも) スキップします。どちらもコンテナ内、CI、そして環境が fastkit の外で管理されている
あらゆる場面で役立ちます。

#### その場へのデプロイと上書きの確認 (`--yes` / `-y`) { #in-place-deployment-and-overwrite-confirmation-yes-y }

プロジェクトをその場に — 新しいプロジェクトフォルダではなく現在のワークスペースに — デプロイする場合、
fastkit は既存のファイルを置き換える前に「Overwrite these files?」と尋ねます。`--yes` (または短縮形の `-y`)
はこの確認をスキップして上書きを進めます。別に表示される「Do you want to proceed with project creation?」の
プロンプトには影響せず、こちらは引き続き表示されます。非対話型の環境 (CI やパイプ経由の実行のように stdin
が TTY でない場合) では、`--yes` を指定しなくても上書きの確認は自動的にスキップされます。

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

#### 対話型ビルダーの機能カタログ (`--interactive`) { #interactive-builder-feature-catalog-interactive }

`fastkit init --interactive` は、上記の minimal/standard/full スタックではなく、項目ごとに構成された別の
カタログを順に進みます (情報源: `core/settings.py` の `FastkitConfig.PACKAGE_CATALOG`、および各選択肢が何を
生成するかについては `DynamicConfigGenerator.build_artifacts()`)。どの項目もデフォルトは `None` (スキップ)
で、`utilities` と `tooling` は複数選択です。

現在では、どの選択もパッケージをインストールするだけでなく実際のコードを生成します — `minimal` /
`single-module` (`main.py` を再生成) と `classic-layered` / `domain-starter` (`main.py` をそのまま残し、
手動配線の警告を出す) の違いについては
[アーキテクチャプリセット / 機能マトリクス](../reference/preset-feature-matrix.md) を参照してください。

| 項目 | 選択肢 | インストールされるパッケージ | 生成されるファイル |
|---|---|---|---|
| `database` | PostgreSQL, MySQL, MongoDB, Redis, SQLite, None | PostgreSQL: `asyncpg`, `sqlalchemy` · MySQL: `aiomysql`, `sqlalchemy` · MongoDB: `motor` · Redis: `redis[hiredis]` · SQLite: `sqlalchemy`, `aiosqlite` | プリセットのパスに置かれるデータベース設定モジュール (例: `src/config/database.py`) |
| `authentication` | JWT, OAuth2, FastAPI-Users, Session-based, None | JWT: `pyjwt[crypto]`, `pwdlib[argon2]` · OAuth2: `authlib`, `itsdangerous`, `httpx` · FastAPI-Users: `fastapi-users[sqlalchemy]`, `pyjwt[crypto]`, `pwdlib[argon2]` · Session-based: `itsdangerous` | プリセットのパスに置かれる認証設定モジュール。OAuth2 とセッションベースは `main.py` にミドルウェアのセットアップも追加 |
| `async_tasks` | Celery, Dramatiq, None | Celery: `celery[redis]`, `redis[hiredis]` · Dramatiq: `dramatiq[redis]`, `redis[hiredis]` | `<pkg>/worker.py` (バックグラウンドワーカー) + `<pkg>/features/tasks.py` (タスク用ルート) |
| `testing` | Basic, Coverage, Advanced, None | Basic: `pytest`, `pytest-asyncio`, `httpx` · Coverage: + `pytest-cov` · Advanced: + `faker`, `factory-boy` | `pytest.ini`。Advanced では `tests/factories.py` と `tests/test_factories.py` も追加 |
| `caching` | Redis, None | Redis: `redis[hiredis]`, `fastapi-cache2`, `jinja2` | `<pkg>/features/cache.py` (キャッシュされるエンドポイント) |
| `monitoring` | Loguru, OpenTelemetry, Prometheus, None | Loguru: `loguru` · OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp-proto-http` · Prometheus: `prometheus-client`, `prometheus-fastapi-instrumentator` | 独立したファイルはなし — `main.py` に直接配線 (import / lifespan / setup) |
| `utilities` (複数選択) | CORS, Rate-Limiting, Pagination, WebSocket, None | CORS: なし (FastAPI に組み込み) · Rate-Limiting: `slowapi` · Pagination: `fastapi-pagination` · WebSocket: `websockets` | CORS と Rate-Limiting は `main.py` に直接配線。Pagination は `<pkg>/features/pagination.py`、WebSocket は `<pkg>/features/websocket.py` を追加 |
| `migrations` | Alembic, None | Alembic: `alembic` | `alembic.ini`、`alembic/env.py`、`alembic/script.py.mako`、ベースラインの `alembic/versions/<id>_initial.py`、`scripts/migrate.sh` — database の項目が SQL データベースの場合のみ |
| `tooling` (複数選択) | ruff, pre-commit, github-actions, devcontainer, makefile, None | ruff: `ruff` · pre-commit: `pre-commit` · github-actions / devcontainer / makefile: なし | ruff は `pyproject.toml` に `[tool.ruff]` ブロックをマージ (`pip` プロジェクトでは `ruff.toml` を作成)。pre-commit は `.pre-commit-config.yaml`、github-actions は `.github/workflows/test.yml`、devcontainer は `.devcontainer/devcontainer.json`、makefile は `Makefile` を作成 |
| `logging` | structured, None | なし (標準ライブラリの `logging` + `json` のみ) | `<pkg>/logging_config.py` (構造化 JSON ロギング + request-id ミドルウェア)。`main.py` に配線 |

選択内容にかかわらず、生成されるすべてのプロジェクトの `main.py` には `/health` と `/ready` エンドポイントが
含まれます。また `--dry-run` は、何かを書き込む前にこのファイルセットをそのまま表示します。

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

#### コードが挿入される場所

`addroute` はプロジェクトから 2 つの情報を必要とします: 新しい import を置く場所と、ルーターを登録する場所です。
テンプレートと生成されたエントリポイントは、その両方をアンカーコメントで示しています:

```python
# src/app/api/router.py
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

ファイルを編集するときは、これらのコメントをそのまま残してください — `addroute` は `# fastkit:imports` と
`# fastkit:routes` の直上に挿入します。アンカーを失ったプロジェクト (またはアンカーが導入される前に生成された
プロジェクト) でも動作はします: fastkit は AST ベースの挿入にフォールバックし、import ブロックとルーター登録の
位置を自分で探します。アンカーは結果を予測可能にするためのものです。

`addroute` はエントリポイントを特定するためにプロジェクトの `[tool.fastapi-fastkit]` ブロックも読み取るため、
ディスク上のスキャンだけでは誤って順位付けされてしまうレイアウトでも動作します。

### `startdemo`

あらかじめ用意されたテンプレートから FastAPI プロジェクトを作成します。

#### 構文

```console
$ fastkit startdemo [OPTIONS]
```

#### オプション

| オプション | 説明 | デフォルト |
|---|---|---|
| `--project-name` | プロジェクト名 (省略時はプロンプトで入力) | - |
| `--author` | 作者名 (省略時はプロンプトで入力) | - |
| `--author-email` | 作者のメールアドレス (省略時はプロンプトで入力) | - |
| `--description` | プロジェクトの説明 (省略時はプロンプトで入力) | - |
| `--package-manager` | 使用するパッケージマネージャー (pip, uv, pdm, poetry) | uv |
| `--dry-run` | 何も書き込まずに、作成されるファイルとパッケージを表示 | off |
| `--no-venv` | 仮想環境の作成をスキップ (`--no-install` を含意) | off |
| `--no-install` | 依存関係のインストールをスキップ | off |
| `--yes` / `-y` | プロジェクトをその場にデプロイするとき、既存ファイルを上書きする前の確認を行わない | off |
| `--help` | コマンドのヘルプを表示 | - |

`init` と同様に、`startdemo` は対象のプロジェクトディレクトリがすでに存在する場合は実行を拒否します
(`Error: Project '{name}' already exists.`)。`--dry-run` は例外です: ディスクに一切書き込まないため、
すでにディレクトリが存在する名前を対象にすることも許可されています。現在のワークスペースにデプロイする
ときに `--yes` が何をするかは、上記の
[その場へのデプロイと上書きの確認](#in-place-deployment-and-overwrite-confirmation-yes-y) を参照してください。

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
| `fastapi-domain-starter` | ドメイン指向のスターター | ビジネス概念ごとに 1 フォルダ、`/health` |
| `fastapi-auth-jwt` | JWT 認証 | アクセス/リフレッシュトークンのローテーション、argon2id、ロールとスコープ、Alembic |
| `fastapi-sqlmodel` | 非同期 SQLModel 永続化 | SQLModel + 非同期 SQLAlchemy、Alembic、汎用 CRUD、ページネーション |
| `fastapi-llm-agent` | ストリーミング Claude エージェント | SSE ストリーミング、ツール呼び出しループ、会話メモリ |
| `fastapi-custom-response` | カスタムレスポンス機構 | カスタムレスポンス、ページネーション |
| `fastapi-psql-orm` | PostgreSQL 連携 FastAPI API | PostgreSQL、SQLAlchemy、Alembic |
| `fastapi-mcp` | Model Context Protocol サーバー | MCP 統合 |
| `fastapi-single-module` | 単一ファイルのサンドボックス | 1 モジュール、パッケージ境界なし |
| `fastapi-empty` | 最小構成 FastAPI プロジェクト | 必要最低限のセットアップ |
| `fastapi-async-crud` | *(非推奨)* 非同期アイテム管理 API | `fastapi-sqlmodel` に置き換え |
| `fastapi-dockerized` | *(非推奨)* Docker 化された FastAPI API | Docker 関連のツールは新しいテンプレートに同梱 |

非推奨のテンプレートも引き続き動作するプロジェクトを生成します。単に、推奨される出発点ではなくなったと
いうだけです。[どのスターターを選ぶべき?](choosing-a-starter.md) を参照してください。

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
- プロジェクトが FastAPI アプリを公開している必要がある — `[tool.fastapi-fastkit].app_module` があればそこから
  解決され、なければ `main.py` をスキャンして探索される
- 仮想環境を有効化しておくこと

記録されたエントリポイントでもスキャンでもモジュールが見つからない場合、`runserver` は `main.py` が見つから
なかったことを報告して停止します。

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

## プロジェクトのメタデータ (`[tool.fastapi-fastkit]`)

fastkit が生成するすべてのプロジェクトは、どのように生成されたかを自身の `pyproject.toml` に記録します:

```toml
[tool.fastapi-fastkit]
managed = true
version = "1.4.0"
template = "fastapi-domain-starter"
preset = "domain-starter"
package_manager = "uv"
app_module = "src.app.main:app"
features = ["database:PostgreSQL", "authentication:JWT"]
```

| キー | 意味 |
|---|---|
| `managed` | 常に `true`。プロジェクトが fastkit 管理下であることを示す |
| `version` | プロジェクトを生成した fastkit のバージョン |
| `template` | `startdemo` のテンプレート、またはプリセットのベーステンプレート |
| `preset` | `init --interactive` のアーキテクチャプリセット (それ以外の場合は省略) |
| `package_manager` | 環境の構築に使われたパッケージマネージャー |
| `app_module` | uvicorn の `module:attr` 形式のエントリポイント |
| `features` | 対話型での選択を `"<category>:<choice>"` 形式で並べたフラットなリスト |

このブロックは、プロジェクトのエントリポイントに関する唯一の情報源です: `fastkit runserver` はツリーの
スキャンにフォールバックする前にここから `app_module` を読み取り、`fastkit addroute` はアプリケーションの
特定にこれを使い、生成される Dockerfile も `CMD` で同じ値を使います。

このブロックは生成の最後に書き込まれます — パッケージマネージャーは依存関係を解決する際に `pyproject.toml`
を書き換えるため、その後に記録する必要があるからです — また、後で再生成した場合は 2 つ目のコピーを追加する
のではなく置き換えます。自分でレイアウトを再編成したことを fastkit に伝える方法としては、`app_module` を
手で編集するのが正式にサポートされた方法です。

## 環境変数

FastAPI-fastkit は次の環境変数を尊重します:

| 変数 | 説明 | デフォルト |
|---|---|---|
| `FASTKIT_CONFIG_DIR` | 設定ディレクトリ | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | カスタムテンプレートのディレクトリ | 組み込みテンプレート |
| `FASTKIT_LOG_LEVEL` | ロギングレベル | `INFO` |
| `FASTKIT_SUBPROCESS_TIMEOUT` | すべてのパッケージマネージャーのサブプロセスのタイムアウトを秒単位で上書き | 操作ごと (30 / 120 / 900) |

パッケージマネージャーの呼び出しにはそれぞれ上限が設けられているため、ハングした子プロセスが CLI をブロック
し続けることはありません: 利用可否のチェックは 30 秒、仮想環境の作成は 120 秒、依存関係のインストールは
900 秒です。`FASTKIT_SUBPROCESS_TIMEOUT` はこの 3 つすべてを 1 つの値で置き換えます — 遅いネットワーク上で、
あるいは CI で早めに失敗させたいときに便利です。正の整数でない値は無視されます。

```console
$ export FASTKIT_SUBPROCESS_TIMEOUT=1800
$ fastkit startdemo fastapi-sqlmodel
```

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

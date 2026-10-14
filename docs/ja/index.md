<p align="center">
    <img align="top" width="70%" src="img/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>: Python と FastAPI を初めて使う方のための、速くて使いやすいスターターキット</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-fastkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-fastkit" alt="PyPI - Version">
</a>
<a href="https://github.com/bnbong/FastAPI-fastkit/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/bnbong/FastAPI-fastkit" alt="GitHub Release">
</a>
<a href="https://pepy.tech/project/fastapi-fastkit">
    <img src="https://static.pepy.tech/personalized-badge/fastapi-fastkit?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
</a>
</p>

---

このプロジェクトは、Python と [FastAPI](https://github.com/fastapi/fastapi) を初めて使う方が、Python ベースの Web アプリ開発をより早く始められるように作られました。

このプロジェクトは `SpringBoot initializer` と Python Django の `django-admin` CLI から着想を得ています。

!!! info "翻訳ステータス"
    このドキュメントの **原典は英語 (`en`)** です。言語切替メニューに表示される他のロケールは部分翻訳の状態であったり、ページ単位で英語にフォールバックする場合があります。各ロケールの実際の翻訳進捗は [翻訳ステータス](reference/translation-status.md) を参照してください。

## 主な機能

- **⚡ FastAPI プロジェクトを即座に作成**: [Python Django](https://github.com/django/django) の `django-admin` 機能から着想を得て、CLI から FastAPI のワークスペースとプロジェクトを高速生成
- **✨ 対話型プロジェクトビルダー**: データベース、認証、キャッシュ、モニタリングなどを段階的に選択し、選択内容を反映したコードを自動生成
- **🎨 見やすい CLI 出力**: [rich library](https://github.com/Textualize/rich) を使った読みやすい CLI 体験
- **📋 標準準拠の FastAPI プロジェクトテンプレート**: FastAPI-fastkit のすべてのテンプレートは Python の標準と FastAPI の一般的な利用パターンに基づいて構成
- **🔍 自動化されたテンプレート品質保証**: 週次の自動テストですべてのテンプレートが動作し最新であることを保証
- **🚀 多彩なプロジェクトテンプレート**: async CRUD、Docker、PostgreSQL など、ユースケース別の事前構成テンプレートを用意
- **📦 複数のパッケージマネージャーに対応**: 好みの Python パッケージマネージャー (pip、uv、pdm、poetry) を選択可能
- **🧾 再現可能なプロジェクト設定**: 対話型セッションを `--save-config` で保存し、後で `fastkit init --config` で再現 — プロンプトなしで同じプロジェクトを作成
- **🏷️ 自己記述的なプロジェクト**: 生成されるすべてのプロジェクトが、テンプレート、プリセット、パッケージマネージャー、エントリポイント、選択した機能を `[tool.fastapi-fastkit]` ブロックに記録し、`runserver` と `addroute` がそれを読み取る

## インストール

Python 環境に `FastAPI-fastkit` をインストールしましょう。

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## 使い方

### 新しい FastAPI プロジェクトの開発環境をすぐに作成

FastAPI-fastkit を使えば、新しい FastAPI プロジェクトをすばやく開始できます。

次のコマンドで、新しい FastAPI プロジェクトの開発環境をすぐに作成できます:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI project

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-awesome-project         │
│ Author       │ John Doe                   │
│ Author Email │ john@example.com           │
│ Description  │ My awesome FastAPI project │
└──────────────┴────────────────────────────┘

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

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
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
FastAPI project will deploy at '~your-project-path~'

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into pyproject.toml              │
╰──────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into config file                 │
╰──────────────────────────────────────────────────────╯

        Creating Project:
       my-awesome-project
┌───────────────────┬───────────┐
│ Component         │ Collected │
│ fastapi           │ ✓         │
│ uvicorn           │ ✓         │
│ pydantic          │ ✓         │
│ pydantic-settings │ ✓         │
└───────────────────┴───────────┘

Creating virtual environment...

╭──────────────────────── Info ────────────────────────╮
│ ℹ venv created at                                    │
│ ~your-project-path~/my-awesome-project/.venv         │
│ To activate the virtual environment, run:            │
│                                                      │
│     source                                           │
│ ~your-project-path~/my-awesome-project/.venv/bin/act │
│ ivate                                                │
╰──────────────────────────────────────────────────────╯

Installing dependencies...
⠙ Setting up project environment...Collecting <packages~>

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-project' has been      │
│ created successfully and saved to                     │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ To start your project, run 'fastkit runserver' at  │
│ newly created FastAPI project directory              │
╰──────────────────────────────────────────────────────╯
```

</div>

このコマンドは、Python の仮想環境を含む新しい FastAPI プロジェクトの開発環境を作成します。

- 主なオプション:
  - `--project-name`、`--author`、`--author-email`、`--description`
  - `--package-manager` [pip|uv|pdm|poetry]
  - `--config <path>`: 保存済みの設定ファイル (`.json` / `.toml`、PyYAML がインストールされていれば `.yaml` も) から、プロンプトなしでプロジェクトを作成
  - `--save-config <path>`: `--interactive` と併用し、回答を後で再利用できるよう記録
  - `--dry-run`: 作成されるファイルとパッケージを表示するだけで、何も書き込まない
  - `--no-venv`: 仮想環境の作成をスキップ (`--no-install` を含意)
  - `--no-install`: 依存関係のインストールをスキップ
  - `--yes` / `-y`: その場にデプロイするとき、「Overwrite these files?」の確認をスキップ

### 対話型モードでプロジェクトを作成 ✨ NEW!

より複雑なプロジェクトには、**対話型モード** を使って、賢い機能選択とともに段階的に FastAPI アプリケーションを組み立てましょう:

<div class="termy">

```console
$ fastkit init --interactive

⚡ FastAPI-fastkit Interactive Project Setup ⚡

📋 Basic Project Information
Enter the project name: my-fullstack-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Full-stack FastAPI project with PostgreSQL and JWT

🧱 Architecture Preset
Pick a project layout. Press Enter to accept the recommended default.
  1. minimal           - Smallest viable FastAPI app
  2. single-module     - Everything in one module (prototypes / scripts)
  3. classic-layered   - api/routes + crud + schemas + core (à la fastapi-default)
  4. domain-starter    - Domain-oriented src/app/domains/<concept>/ (recommended)

Select architecture preset: [4]

🗄️ Database Selection
Select database (PostgreSQL, MySQL, MongoDB, Redis, SQLite, None):
  1. PostgreSQL - PostgreSQL database with SQLAlchemy
  2. MySQL - MySQL database with SQLAlchemy
  3. MongoDB - MongoDB with motor async driver
  4. Redis - Redis for caching and session storage
  5. SQLite - SQLite database for development
  6. None - No database

Select database: 1

🔐 Authentication Selection
Select authentication (JWT, OAuth2, FastAPI-Users, Session-based, None):
  1. JWT - JSON Web Token authentication
  2. OAuth2 - OAuth2 with password flow
  3. FastAPI-Users - Full featured user management
  4. Session-based - Cookie-based sessions
  5. None - No authentication

Select authentication: 1

⚙️ Background Tasks Selection
Select background tasks (Celery, Dramatiq, None):
  1. Celery - Distributed task queue
  2. Dramatiq - Fast and reliable task processing
  3. None - No background tasks

Select background tasks: 1

💾 Caching Selection
Select caching (Redis, fastapi-cache2, None):
  1. Redis - Redis caching
  2. fastapi-cache2 - Simple caching for FastAPI
  3. None - No caching

Select caching: 1

📊 Monitoring Selection
Select monitoring (Loguru, OpenTelemetry, Prometheus, None):
  1. Loguru - Simple and powerful logging
  2. OpenTelemetry - Observability framework
  3. Prometheus - Metrics and monitoring
  4. None - No monitoring

Select monitoring: 3

🧪 Testing Framework Selection
Select testing framework (Basic, Coverage, Advanced, None):
  1. Basic - pytest + httpx for API testing
  2. Coverage - Basic + code coverage
  3. Advanced - Coverage + faker + factory-boy for fixtures
  4. None - No testing framework

Select testing framework: 2

🛠️ Additional Utilities
Select utilities (comma-separated numbers, e.g., 1,3,4):
  1. CORS - Cross-Origin Resource Sharing
  2. Rate-Limiting - Request rate limiting
  3. Pagination - Pagination support
  4. WebSocket - WebSocket support

Select utilities: 1

🪵 Logging Format
Select logging format:
  1. structured - JSON logs + X-Request-ID correlation middleware (stdlib only)
  2. None - Uvicorn's default plain-text logging

Select logging format [2]: 1

🧬 Database Migrations
Select migration tool:
  1. Alembic - alembic.ini + async alembic/env.py + scripts/migrate.sh (recommended for SQL databases)
  2. None - No migration tooling

Select migration tool [1]: 1

🧰 Developer Tooling
Select tooling to generate (comma-separated numbers, e.g., 1,3)
  1. ruff ruff + ruff-format config in pyproject.toml (replaces black/isort)
  2. pre-commit .pre-commit-config.yaml
  3. github-actions .github/workflows/test.yml (Python 3.12)
  4. devcontainer .devcontainer/devcontainer.json
  5. makefile Makefile with install/test/lint/format/run

Your choice (or press Enter to skip): 1,2

🚀 Deployment Configuration
Select deployment option:
  1. Docker - Generate Dockerfile
  2. docker-compose - Generate docker-compose.yml (includes Docker)
  3. None - No deployment configuration

Select deployment option: 2

📦 Package Manager Selection
Select package manager (pip, uv, pdm, poetry): uv

📝 Custom Packages (optional)
Enter custom package names (comma-separated, press Enter to skip):

📋 Project Configuration Summary
┌─────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Setting             │ Value                                                                     │
├─────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ Project Name        │ my-fullstack-project                                                      │
│ Author              │ John Doe                                                                  │
│ Email               │ john@example.com                                                          │
│ Description         │ Full-stack FastAPI project with PostgreSQL and JWT                        │
│ Architecture Preset │ domain-starter — Domain-oriented: src/app/domains/<concept>/ (recommended)│
│ Database            │ PostgreSQL                                                                │
│ Authentication      │ JWT                                                                       │
│ Async Tasks         │ Celery                                                                    │
│ Caching             │ Redis                                                                     │
│ Monitoring          │ Prometheus                                                                │
│ Testing             │ Coverage                                                                  │
│ Utilities           │ CORS                                                                      │
│ Logging             │ structured                                                                │
│ Migrations          │ Alembic                                                                   │
│ Tooling             │ ruff, pre-commit                                                          │
│ Package Manager     │ uv                                                                        │
└─────────────────────┴───────────────────────────────────────────────────────────────────────────┘

Total dependencies to install: 18

Proceed with project creation? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into pyproject.toml              │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated dependency file with 18 packages         │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Preserving template-shipped main.py for preset     │
│ 'domain-starter'.                                    │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated Docker deployment files                  │
╰───────────────────────────────────────────────────────╯
╭────────────────────── Warning ────────────────────────╮
│ ⚠ Preset compatibility                               │
│ fastapi-domain-starter's shipped src/app/main.py is  │
│ preserved. The selections below need manual wiring   │
│ there (CORS is already wired — set                   │
│ BACKEND_CORS_ORIGINS in .env to activate it).        │
│ Affected selections (packages installed, but no      │
│ dynamic main.py edits applied for the                │
│ 'domain-starter' preset): Prometheus                 │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated configuration files for selected stack   │
╰───────────────────────────────────────────────────────╯

Creating virtual environment...
Installing dependencies...

----> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-fullstack-project' from        │
│ 'fastapi-domain-starter' has been created!            │
╰───────────────────────────────────────────────────────╯
```

</div>

対話型モードが提供する機能:

- **アーキテクチャプリセット選択** (`minimal` / `single-module` / `classic-layered` / `domain-starter`) — 適切なベーステンプレートとプロジェクトレイアウトを決定
- データベース、認証、バックグラウンドタスク、キャッシュ、モニタリングなどに対する **ガイド付き選択**
- 選択した機能向けの **コードの自動生成** — プリセットに応じて挙動が異なる (`minimal` / `single-module` は `main.py` を再生成、`classic-layered` / `domain-starter` はテンプレート同梱の `main.py` を保存し、設定モジュールのみ追加)
- **プリセット対応の Docker 生成** — 生成された `Dockerfile` の `CMD` がそのプリセットの実際のエントリポイント (`src.main:app` または `src.app.main:app`) を指す
- 自動 pip 互換性を備えた **スマートな依存関係管理**
- プリセットが自動配線できない選択について手動配線の警告を出力する **機能検証**
- 生成された `pyproject.toml` への **識別マーカー** 注入 (description マーカー + `[tool.fastapi-fastkit]` テーブル) — 後で `is_fastkit_project()` が生成済みプロジェクトを認識可能
- `[tool.fastapi-fastkit]` に記録される **プロジェクトメタデータ** — テンプレート、プリセット、パッケージマネージャー、`app_module`、選択した `features` — を `fastkit runserver` と `fastkit addroute` が読み取る
- **再現可能な実行**: `--save-config <path>` で回答を記録し、`--config <path>` でプロンプトを一切出さずに再現でき、`--dry-run` で何も書き込まずに結果をプレビュー可能

現在では、カタログのどの選択もパッケージをインストールするだけでなく、実際に動作するコードを生成します —
バックグラウンドタスク (Celery/Dramatiq)、Redis キャッシュ、WebSocket、ページネーション、OpenTelemetry
トレーシング、OAuth2 / セッションベース認証のすべてに、対応するモジュールと `main.py` の配線が付属します。
さらに 3 つの新しい項目がカタログを補完します:

- **ロギング**: `structured` は、標準ライブラリの `logging` + `json` による構造化出力と request-id ミドルウェアを追加 — 新しい依存関係は不要
- **マイグレーション**: `Alembic` は、SQL データベースを選択した場合に完全な非同期マイグレーション環境 (`alembic.ini`、`alembic/env.py`、ベースラインのリビジョン、`scripts/migrate.sh`) を生成
- **ツール** (複数選択): `ruff`、`pre-commit`、`github-actions`、`devcontainer`、`makefile` — それぞれが自身の設定ファイルを生成し、`ruff` は `pyproject.toml` に `[tool.ruff]` ブロックもマージ

生成されるすべてのプロジェクトには `/health` と `/ready` エンドポイントも含まれ、`--dry-run` はこれらの新しい
成果物を含め、実際の実行で書き込まれるのとまったく同じファイルセットを一覧表示します。`classic-layered` と
`domain-starter` はテンプレート同梱の `main.py` を保存するため、これらのいずれかの項目の選択に手動配線が必要な
場合は機能検証が警告を出します — 詳しくは [プリセット / 機能マトリクス](reference/preset-feature-matrix.md) を
参照してください。

### FastAPI プロジェクトに新しいルートを追加

`FastAPI-fastkit` は FastAPI プロジェクトの拡張を簡単にします。

次のコマンドで FastAPI プロジェクトに新しいルートエンドポイントを追加できます:

<div class="termy">

```console
$ fastkit addroute user my-awesome-project
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-awesome-project                       │
│ Route Name       │ user                                     │
│ Target Directory │ ~your-project-path~                      │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to project 'my-awesome-project'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'user' to project     │
│ `my-awesome-project`                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

### 構造化された FastAPI デモプロジェクトを即座に展開

構造化された FastAPI デモプロジェクトから始めることもできます。

デモプロジェクトはさまざまな技術スタックで構成されており、シンプルな item CRUD エンドポイントが実装されています。

次のコマンドで、構造化された FastAPI デモプロジェクトを即座に展開できます:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-awesome-demo
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI demo
Deploying FastAPI project using 'fastapi-default' template
Template path:
/~fastapi_fastkit-package-path~/fastapi_project_template/fastapi-default

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-demo         │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ My awesome FastAPI demo │
└──────────────┴─────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
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
FastAPI template project will deploy at '~your-project-path~'

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-demo' from             │
│ 'fastapi-default' has been created and saved to       │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

- 主なオプション:
  - `--project-name`、`--author`、`--author-email`、`--description`
  - `--package-manager` [pip|uv|pdm|poetry]
  - `--dry-run`、`--no-venv`、`--no-install`、`--yes`/`-y` — `init` と同じ意味
  - 対象のプロジェクトディレクトリがすでに存在する場合は実行を拒否 (`--dry-run` を除く)

利用可能な FastAPI デモの一覧を表示するには、次のコマンドを実行してください:

<div class="termy">

```console
$ fastkit list-templates
                              Available Templates
┌────────────────────────┬───────────────────────────────────────────────────────┐
│ fastapi-custom-response│ Async Item Management API with Custom Response System │
│ fastapi-mcp            │ FastAPI MCP Project                                   │
│ fastapi-domain-starter │ FastAPI Domain Starter                                │
│ fastapi-dockerized     │ Dockerized FastAPI Item Management API                │
│ fastapi-empty          │ Minimal FastAPI Template                              │
│ fastapi-async-crud     │ Async Item Management API Server                      │
│ fastapi-psql-orm       │ Dockerized FastAPI Item Management API with           │
│                        │ PostgreSQL                                            │
│ fastapi-default        │ Simple FastAPI Project                                │
│ fastapi-single-module  │ FastAPI Single Module Template                        │
│ fastapi-auth-jwt       │ FastAPI JWT Authentication                            │
│ fastapi-sqlmodel       │ FastAPI SQLModel                                      │
│ fastapi-llm-agent      │ FastAPI LLM Agent                                     │
└────────────────────────┴───────────────────────────────────────────────────────┘
```

</div>

利用可能なテンプレート:

| テンプレート | 説明 | 備考 |
|---|---|---|
| [`fastapi-default`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-default/README.md-tpl) | クラシックなレイヤー型レイアウトのシンプルな FastAPI プロジェクト | 最初の選択肢として最適 |
| [`fastapi-empty`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-empty/README.md-tpl) | 最小構成の FastAPI テンプレート | `minimal` プリセットのベース |
| [`fastapi-single-module`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-single-module/README.md-tpl) | 単一ファイルの FastAPI アプリ | `single-module` プリセットのベース |
| [`fastapi-domain-starter`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-domain-starter/README.md-tpl) | 中規模 API 向けの、ドメイン指向で pyproject を第一とするスターター | `domain-starter` プリセットのベース |
| [`fastapi-auth-jwt`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-auth-jwt/README.md-tpl) | リフレッシュトークンのローテーション、argon2 ハッシュ化、スコープを備えた JWT 認証 | v1.4.0 で追加 |
| [`fastapi-sqlmodel`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-sqlmodel/README.md-tpl) | 非同期 SQLModel + Alembic マイグレーション + ページネーション付きの汎用 CRUD | v1.4.0 で追加 |
| [`fastapi-llm-agent`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-llm-agent/README.md-tpl) | ツール呼び出しループを備えたストリーミング Claude チャットエージェント (SSE) | v1.4.0 で追加 |
| [`fastapi-mcp`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-mcp/README.md-tpl) | MCP サーバーとして公開される FastAPI アプリ | |
| [`fastapi-psql-orm`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-psql-orm/README.md-tpl) | PostgreSQL、SQLModel、Alembic、docker-compose を使うアイテム管理 API | Docker が必要 |
| [`fastapi-custom-response`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response/README.md-tpl) | カスタムレスポンスエンベロープ、エラー処理、ページネーションを備えたアイテム管理 API | |
| [`fastapi-async-crud`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud/README.md-tpl) | 非同期アイテム管理 API | **非推奨** — `fastapi-sqlmodel` を使用 |
| [`fastapi-dockerized`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-dockerized/README.md-tpl) | Docker 化されたアイテム管理 API | **非推奨** — `init --interactive` の Docker オプションと `fastapi-default` を使用 |

非推奨のテンプレートも引き続き動作しますが、推奨される出発点ではなくなりました。選び方のガイドは [どのスターターを選ぶべき?](user-guide/choosing-a-starter.md) を参照してください。

## ドキュメント

包括的なガイドと詳細な使い方は、ドキュメントを参照してください:

- 🧭 **[どのスターターを選ぶべき?](user-guide/choosing-a-starter.md)** - `startdemo` テンプレートと対話型プリセットを選ぶための初心者向けガイド
- 📚 **[ユーザーガイド](user-guide/quick-start.md)** - 詳細なインストール / 利用ガイド
- 🎯 **[チュートリアル](tutorial/getting-started.md)** - 初心者向けの段階的なチュートリアル
- 📖 **[CLI リファレンス](user-guide/cli-reference.md)** - コマンドの完全リファレンス
- 🧱 **[アーキテクチャプリセットマトリクス](reference/preset-feature-matrix.md)** - 対話型生成におけるプリセットごと / 機能ごとの仕様
- 🔍 **[テンプレート品質保証](reference/template-quality-assurance.md)** - 自動化されたテストと品質基準

## 🚀 テンプレート別チュートリアル

事前構築されたテンプレートを使った実践的なユースケースで、FastAPI 開発を学びましょう:

### 📖 コアチュートリアル

- **[基本 API サーバーの構築](tutorial/basic-api-server.md)** - `fastapi-default` テンプレートで初めての FastAPI サーバーを作成
- **[非同期 CRUD API の構築](tutorial/async-crud-api.md)** - `fastapi-async-crud` テンプレートで高パフォーマンスな非同期 API を開発
- **[ドメイン指向プロジェクト (Domain Starter)](tutorial/domain-starter.md)** - 推奨される現代的デフォルトである `fastapi-domain-starter` テンプレートで中規模 API を構築
- **[JWT 認証](tutorial/auth-jwt.md)** - `fastapi-auth-jwt` テンプレートで本物のアカウント機能を追加: ローテーションするリフレッシュトークン、argon2id ハッシュ化、ロールとスコープのガード

### 🗄️ データベースとインフラ

- **[データベース統合](tutorial/database-integration.md)** - `fastapi-psql-orm` テンプレートで PostgreSQL + SQLAlchemy を活用
- **[SQLModel による非同期永続化](tutorial/sqlmodel.md)** - `fastapi-sqlmodel` テンプレートで非同期 SQLModel、Alembic マイグレーション、汎用 CRUD ベース、ページネーションされたリストを活用
- **[Docker でのデプロイ](tutorial/docker-deployment.md)** - `fastapi-dockerized` テンプレートで本番デプロイ環境を構築 *(非推奨テンプレート — 既存ユーザーのために維持)*

### ⚡ 高度な機能

- **[カスタムレスポンス処理と高度な API 設計](tutorial/custom-response-handling.md)** - `fastapi-custom-response` テンプレートでエンタープライズグレードの API を構築
- **[MCP との統合](tutorial/mcp-integration.md)** - `fastapi-mcp` テンプレートで AI モデルと連携する API サーバーを作成
- **[ストリーミング LLM エージェント](tutorial/llm-agent.md)** - `fastapi-llm-agent` テンプレートで、本物のツール呼び出しループを備えたストリーミング Claude チャットバックエンドを構築

各チュートリアルが提供するもの:

- ✅ **実用的な例** - 実際のプロジェクトでそのまま使えるコード
- ✅ **段階的なガイド** - 初心者でも追えるよう詳しく解説
- ✅ **ベストプラクティス** - 業界標準のパターンとセキュリティ上の考慮
- ✅ **拡張のヒント** - プロジェクトを次のレベルへ進めるためのガイダンス

## コントリビュート

コミュニティからの貢献を歓迎します! FastAPI-fastkit は Python と FastAPI の入門者を支援するために設計されており、皆さんの貢献は大きな影響を生み出します。

### 貢献できること

- 🚀 **新しい FastAPI テンプレート** - さまざまなユースケース向けのテンプレート追加
- 🐛 **バグ修正** - 安定性と信頼性の向上に協力
- 📚 **ドキュメント** - ガイド、サンプル、翻訳の改善
- 🧪 **テスト** - テストカバレッジの拡大と統合テストの追加
- 💡 **機能** - 新しい CLI 機能の提案と実装

### コントリビュートを始める

FastAPI-fastkit へのコントリビュートを始めるには、次の包括的なガイドを参照してください:

- **[開発環境のセットアップ](contributing/development-setup.md)** - 開発環境を整えるための完全ガイド
- **[コードガイドライン](contributing/code-guidelines.md)** - コーディング標準とベストプラクティス
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** - 包括的なコントリビュートガイド
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** - プロジェクトの原則とコミュニティ基準
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** - セキュリティガイドラインと報告手順

## FastAPI-fastkit が目指すもの

FastAPI-fastkit は、Python と FastAPI を初めて使う方に対して、速くて使いやすいスターターキットを提供することを目標にしています。

このアイデアは、FastAPI 入門者が最初から段階的に学べるように支援したいという思いから生まれました。これは [FastAPI 0.111.0 のバージョンアップ](https://github.com/fastapi/fastapi/releases/tag/0.111.0) で追加された FastAPI-cli パッケージが持つ実践的な意義とも軌を一にしています。

長く FastAPI を愛用してきた者として、FastAPI 開発者 [tiangolo](https://github.com/tiangolo) が表明した [素晴らしい動機](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) を少しでも実現する手助けになるプロジェクトを作りたいと考えました。

FastAPI-fastkit は次の価値を提供することで、「最初の一歩」と「本番運用に耐えるアプリケーション」の間のギャップを埋めようとしています:

- **即座の生産性** - セットアップの複雑さに圧倒されがちな新規ユーザーに即時の生産性を提供
- **ベストプラクティス** - すべてのテンプレートにベストプラクティスが組み込まれており、利用者が正しい FastAPI のパターンを学べる
- **拡張可能な土台** - 初心者からエキスパートへ成長するに従って、共に拡張していける土台
- **コミュニティ駆動のテンプレート** - 実世界の FastAPI 利用パターンを反映したコミュニティ中心のテンプレート

## 次のステップ

FastAPI-fastkit を始める準備ができたら、次の流れで進めてみましょう:

### 🚀 クイックスタート

1. **[インストール](user-guide/installation.md)**: FastAPI-fastkit をインストール
2. **[クイックスタート](user-guide/quick-start.md)**: 5 分で最初のプロジェクトを作成
3. **[入門チュートリアル](tutorial/getting-started.md)**: 段階的な詳細チュートリアル

### 📚 さらに学ぶ

- **[プロジェクトの作成](user-guide/creating-projects.md)**: さまざまなスタックでプロジェクトを作成
- **[ルートの追加](user-guide/adding-routes.md)**: プロジェクトに API エンドポイントを追加
- **[テンプレートの利用](user-guide/using-templates.md)**: あらかじめ用意されたプロジェクトテンプレートを活用

### 🛠️ コントリビュート

FastAPI-fastkit に貢献したいですか?

- **[開発環境のセットアップ](contributing/development-setup.md)**: 開発環境を整える
- **[コードガイドライン](contributing/code-guidelines.md)**: コーディング標準とベストプラクティスに従う
- **[コントリビュートガイドライン](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)**: 包括的な貢献ガイド

### 🔍 リファレンス

- **[CLI リファレンス](user-guide/cli-reference.md)**: 全 CLI コマンドのリファレンス
- **[テンプレート品質保証](reference/template-quality-assurance.md)**: 自動化されたテストと品質基準
- **[FAQ](reference/faq.md)**: よくある質問
- **[GitHub リポジトリ](https://github.com/bnbong/FastAPI-fastkit)**: ソースコードと Issue トラッキング

## ライセンス

このプロジェクトは MIT ライセンスのもとで提供されます — 詳細は [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) ファイルを参照してください。

# アーキテクチャプリセット / 機能マトリクス

`fastkit init --interactive` は機能選択の前に **アーキテクチャプリセット** を尋ねます ([issue #44](https://github.com/bnbong/FastAPI-fastkit/issues/44))。プリセットは生成されるプロジェクトのレイアウトを決めます。プリセットごとに異なるベーステンプレートを使い、生成された設定ファイルを既存の構造に並べる形で配置します (並列の `src/config/` ツリーを作るのではなく)。

このページは、各プリセットの動作、ファイルの配置先、手動配線が必要な機能の組み合わせを確認するための基準ページです。

## プリセット → ベーステンプレート

| プリセット | ベーステンプレート | 説明 |
|---|---|---|
| `minimal` | `fastapi-empty` | 最小構成の動作可能な FastAPI アプリ — プレースホルダの `main.py` は機能選択から再生成されます。 |
| `single-module` | `fastapi-single-module` | 単一ファイル FastAPI アプリ — `main.py` は再生成されます。 |
| `classic-layered` | `fastapi-default` | レイヤー型分割 (`api/routes`、`crud`、`schemas`、`core`)。テンプレートに含まれる `main.py` はそのまま使われます。 |
| `domain-starter` | `fastapi-domain-starter` | ドメイン指向 (`src/app/domains/<concept>/`)。テンプレートに含まれる `main.py` はそのまま使われます。**推奨デフォルト。** |

## 生成ファイルの配置先

| プリセット | `main.py` オーバーレイ | データベース設定の配置先 | 認証設定の配置先 |
|---|---|---|---|
| `minimal` | `src/main.py` で再生成 | `src/config/database.py` | `src/config/auth.py` |
| `single-module` | `src/main.py` で再生成 | `src/config/database.py` | `src/config/auth.py` |
| `classic-layered` | 保存 (テンプレートに含まれるものをそのまま使用) | `src/core/database.py` | `src/core/auth.py` |
| `domain-starter` | 保存 (テンプレートに含まれるものをそのまま使用) | `src/app/core/database.py` | `src/app/core/auth.py` |

## プリセット別のデータベース / 認証機能サポート

これらの機能は **すべての** プリセットでサポートされます — パッケージインストールは常に成功します。違いは、動的な `main.py` オーバーレイが自動でそれらを配線するかどうかです。

| 機能 | `minimal` / `single-module` | `classic-layered` / `domain-starter` |
|---|---|---|
| **データベース** (PostgreSQL、MySQL、SQLite、MongoDB) | 設定モジュールを生成し、再生成された `main.py` に `await init_db()` 呼び出しのスタブも入ります。 | プリセットごとのパスに設定モジュールを生成します。テンプレートに含まれる `main.py` は **そのまま残る** ため、`get_db()` はルーター側で手動で配線してください。 |
| **認証** (JWT、FastAPI-Users、OAuth2、セッションベース) | 認証設定モジュールを生成します。JWT は `HTTPBearer` を import し、OAuth2 とセッションベースは `main.py` にミドルウェアのセットアップも追加します。 | プリセットのパスに認証設定モジュールを生成します。`main.py` への import は追加されません — 依存性は手動で配線してください。 |
| **バックグラウンドタスク** (Celery、Dramatiq) | `worker.py` と `features/tasks.py` を生成し、再生成された `main.py` にタスクルーターをマウントします。 | `worker.py` と `features/tasks.py` を生成しますが、テンプレートに含まれる `main.py` は **そのまま残る** ため、ルーターは手動でマウントしてください。 |
| **キャッシュ** (Redis) | `features/cache.py` を生成し、再生成された `main.py` でマウントと初期化を行います。 | `features/cache.py` を生成します。マウントは手動で行ってください。 |
| **ユーティリティ: ページネーション / WebSocket** | `features/pagination.py` / `features/websocket.py` を生成し、再生成された `main.py` にルーターをマウントします。 | 同じモジュールを生成します。マウントは手動で行ってください。 |
| **モニタリング: OpenTelemetry** | 独立したファイルはありません — トレーシングのセットアップは再生成された `main.py` に直接追加されます。 | 独立したファイルはありません。テンプレートに含まれる `main.py` はそのまま残るため、トレーシングは **配線されません** — セットアップを手動で追加してください。 |
| **マイグレーション** (Alembic) | SQL データベースを選択した場合は常に `alembic.ini`、`alembic/env.py`、ベースラインのリビジョン、`scripts/migrate.sh` を生成します — `main.py` オーバーレイとは独立しています。 | 同上 — Alembic の生成は `main.py` がそのまま残るかどうかに依存しません。 |
| **ツール** (ruff、pre-commit、github-actions、devcontainer、makefile) | 対応する設定ファイルを生成します。`main.py` オーバーレイとは独立しています。 | 同上。 |
| **ロギング** (構造化) | `logging_config.py` を生成し、再生成された `main.py` に request-id ミドルウェアを配線します。 | `logging_config.py` を生成します。テンプレートに含まれる `main.py` はそのまま残るため、ミドルウェアは手動で配線してください。 |
| **CORS** (ユーティリティ) | 再生成された `main.py` に `CORSMiddleware` が `allow_origins=['*']` で追加されます。 | テンプレートに含まれる `main.py` に **すでに組み込み済み** です (`settings.all_cors_origins` に応じて条件分岐)。`.env` の `BACKEND_CORS_ORIGINS` を設定すれば有効化されます — コード変更は不要です。 |
| **テスト** (Basic / Coverage / Advanced) | プロジェクトルートに `pytest.ini` を生成。Advanced では `tests/factories.py` と `tests/test_factories.py` も追加されます。 | 同上。 |
| **デプロイ** (Docker、docker-compose) | プロジェクトルートに `Dockerfile` または `docker-compose.yml` を作成。 | 同上。 |
| **`/health` / `/ready`** | 再生成された `main.py` に常に含まれます。 | テンプレートに含まれ、そのまま残る `main.py` にすでに含まれています。 |

## "Preset compatibility" 警告が出る場面

テンプレートに含まれる `main.py` を **そのまま使う** プリセット (`classic-layered`、`domain-starter`) では、一部の機能選択が自動配線されません。CLI は生成の最後に、手動配線が必要な選択を 1 回だけまとめて警告します:

| 選択した機能 | `classic-layered` / `domain-starter` で警告が出るか? |
|---|---|
| `CORS` (ユーティリティ) | ❌ — テンプレートに含まれる `main.py` で配線済み。`.env` の `BACKEND_CORS_ORIGINS` を埋めるだけ。 |
| `Rate-Limiting` (ユーティリティ) | ✅ — `slowapi` リミッタのセットアップは追加されない |
| `Pagination` / `WebSocket` (ユーティリティ) | ✅ — 生成されたルーター (`features/pagination.py` / `features/websocket.py`) はマウントされない |
| `Celery` / `Dramatiq` (async_tasks) | ✅ — 生成された `worker.py` / `features/tasks.py` のルーターはマウントされない |
| `Redis` (キャッシュ) | ✅ — 生成された `features/cache.py` はマウントも初期化もされない |
| `Prometheus` / `OpenTelemetry` (モニタリング) | ✅ — 計装のセットアップは `main.py` に追加されない |
| `structured` (ロギング) | ✅ — `logging_config.py` は生成されるが、request-id ミドルウェアは `main.py` に追加されない |
| `Alembic` (マイグレーション)、`tooling` の選択 | ❌ — これらのファイルはプリセットに関係なく生成され、そのまま使える。`main.py` に依存するものはない |
| 任意のデータベース / 認証選択 | ⚠️ — 設定ファイルは生成されますが、自分で `Depends()` をルーターに組み込む必要があります |

`minimal` と `single-module` プリセットでは、動的 `main.py` オーバーレイが上記のすべての項目を自動で扱います。警告は出ません。

## サポート外の組み合わせ (安全側に倒す)

ストラテジストはあえて **テンプレートに含まれる `main.py` に生成コードを差し込みません**。差し込むと import が壊れたり、ルーターが重複登録されたりするリスクがあるためです。現在の前提は次のとおりです:

- 選択されたパッケージは常にインストールされます (`pip freeze` がユーザーの意図と一致します)。
- 生成された設定モジュールは常にプリセットに応じた配置先へ作られます。
- main 保存型プリセットでは、コードが暗黙に壊れるのではなく、どの選択がまだ手動配線を要するかを利用者に明示します。

すべての機能を完全に自動配線したい場合は `minimal` または `single-module` を選んでください — それらは機能フラグから `main.py` を再生成します。

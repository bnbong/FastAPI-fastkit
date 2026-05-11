# よくある質問

FastAPI-fastkit に関するよくある質問とその回答です。

## インストールとセットアップ

### Q: 対応している Python バージョンは?

**A:** FastAPI-fastkit は **Python 3.12 以上** が必要です。最良の体験のため、最新の安定 Python バージョンの利用を推奨します。

<div class="termy">

```console
$ python --version
Python 3.12.1

$ pip install fastapi-fastkit
```

</div>

### Q: FastAPI-fastkit はどうインストールしますか?

**A:** pip でインストールできます:

<div class="termy">

```console
# 最新の安定版
$ pip install fastapi-fastkit

# GitHub からの開発版
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git

# 特定のバージョン
$ pip install fastapi-fastkit==1.0.0
```

</div>

### Q: パーミッションエラーでインストールに失敗します

**A:** 仮想環境内、またはユーザー権限でインストールしてください:

<div class="termy">

```console
# 仮想環境を作成
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Windows の場合: fastapi-env\Scripts\activate

# 仮想環境にインストール
$ pip install fastapi-fastkit

# あるいは現在のユーザーのみにインストール
$ pip install --user fastapi-fastkit
```

</div>

### Q: インストール後に `fastkit` コマンドが見つかりません

**A:** たいていは、インストール先が PATH に含まれていないことが原因です:

<div class="termy">

```console
# インストール済みか確認
$ pip show fastapi-fastkit

# インストール場所を確認
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__file__)"

# 直接実行を試す
$ python -m fastapi_fastkit --version

# PATH に追加 (Linux/macOS)
$ export PATH="$HOME/.local/bin:$PATH"
```

</div>

## プロジェクトの作成

### Q: 利用できる依存関係スタックは?

**A:** FastAPI-fastkit は 3 つの依存関係スタックを提供します:

- **MINIMAL**: FastAPI、Uvicorn、Pydantic、Pydantic-Settings (基本的な Web API)
- **STANDARD**: SQLAlchemy、Alembic、pytest を追加 (データベース対応)
- **FULL**: Redis、Celery を追加 (バックグラウンドタスク)

!!! tip "デフォルトのパッケージマネージャー"
    デフォルトのパッケージマネージャーは依存関係インストールが速い `uv` です。`pip`、`pdm`、`poetry` も選択できます。

<div class="termy">

```console
$ fastkit init
# プロジェクト作成中に好みのスタックを選択
```

</div>

### Q: プロジェクトテンプレートはカスタマイズできますか?

**A:** はい、次のいずれかの方法で:

1. **既存テンプレートを使う** — `fastkit startdemo`
2. **カスタムテンプレートを作る** — 既存をコピーして変更
3. **段階的にルートを追加** — `fastkit addroute`

<div class="termy">

```console
# あらかじめ用意されたテンプレートを使う
$ fastkit list-templates
$ fastkit startdemo

# 既存プロジェクトにルートを追加
$ fastkit addroute users .          # 現在のディレクトリに 'users' ルートを追加
$ fastkit addroute users my-project # 'my-project' に 'users' ルートを追加
```

</div>

### Q: プロジェクト名にはどんな形式が使えますか?

**A:** プロジェクト名は妥当な Python 識別子である必要があります:

- ✅ `my-api`、`blog_system`、`UserService`
- ❌ `my api`、`123project`、`project-name!`

<div class="termy">

```console
$ fastkit init
Enter the project name: my_awesome_api  # 妥当
Enter the project name: my-awesome-api  # 妥当 (ハイフンはアンダースコアに変換)
```

</div>

### Q: 「ディレクトリは既に存在する」というエラーで作成に失敗します

**A:** プロジェクトディレクトリが既に存在しています。次のいずれかで対処してください:

1. **別の名前を選ぶ**
2. **既存ディレクトリを削除** (安全な場合のみ)
3. **別の場所に作成**

<div class="termy">

```console
# ディレクトリの存在を確認
$ ls my-project

# 安全なら削除 (注意!)
$ rm -rf my-project

# あるいは別の場所に作成
$ mkdir projects
$ cd projects
$ fastkit init
```

</div>

### Q: 対話型モードでプロジェクトをセットアップするには?

**A:** `fastkit init --interactive` を使うと、賢い機能選択を伴うガイド付きの段階的なセットアップが可能です:

<div class="termy">

```console
$ fastkit init --interactive
```

</div>

対話型モードは次の順序で進みます:

1. **プロジェクト情報** — 名前、作者、メール、説明。
2. **アーキテクチャプリセット** — プロジェクトレイアウトを選択。推奨デフォルトは `domain-starter`。Enter で受け入れられます。各プリセットが生成する正確なレイアウトと、手動配線が必要な機能組み合わせは [プリセット / 機能マトリクス](preset-feature-matrix.md) を参照してください。
3. **機能選択** — データベース、認証、バックグラウンドタスク、キャッシュ、モニタリング、テスト、ユーティリティ、デプロイ。
4. **パッケージマネージャーとカスタムパッケージ** — pip / uv / pdm / poetry、および固定したい追加パッケージ。
5. **確認** — プロジェクト作成前に、すべての選択 (アーキテクチャプリセット含む) を表で表示します。

対話型モードでは、次の包括的な機能カタログから選べます:

| カテゴリ | 利用可能な選択肢 |
|---|---|
| **アーキテクチャ** | minimal、single-module、classic-layered、**domain-starter** (推奨デフォルト) |
| **データベース** | PostgreSQL、MySQL、MongoDB、Redis、SQLite |
| **認証** | JWT、OAuth2、FastAPI-Users、セッションベース |
| **バックグラウンドタスク** | Celery、Dramatiq |
| **テスト** | Basic (pytest)、Coverage、Advanced (faker、factory-boy 付き) |
| **キャッシュ** | Redis with fastapi-cache2 |
| **モニタリング** | Loguru、OpenTelemetry、Prometheus |
| **ユーティリティ** | CORS、レート制限、ページネーション、WebSocket |
| **デプロイ** | Docker、docker-compose (自動生成設定付き) |

対話型モードは次を自動生成します:

- 選択した機能を統合した `main.py`
- データベースおよび認証の設定ファイル (コード生成に対応する選択肢の場合 — 例: データベースの PostgreSQL/MySQL/SQLite/MongoDB、認証の JWT/FastAPI-Users。それ以外の選択肢は必要パッケージのインストールのみ)
- 選択したデプロイオプションに対応するデプロイファイル (`Docker` 選択時は `Dockerfile`、`docker-compose` 選択時は `docker-compose.yml`)
- 選択したテストオプションに応じたテスト設定 (カバレッジ設定は `Coverage` または `Advanced` を選んだ場合のみ含まれます)

### Q: 対話型モードで利用できる機能を確認するには?

**A:** `list-features` コマンドで、利用可能なすべての機能とパッケージを表示できます:

<div class="termy">

```console
$ fastkit list-features
# カテゴリ別に整理されたすべての機能と
# 関連パッケージが表示されます
```

</div>

これで、各機能を選んだ場合にどのパッケージがインストールされるかを把握できます。

## ルート開発

### Q: ルートに認証を追加するには?

**A:** 認証用の依存性を作成します:

```python
# src/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # トークンを検証してユーザーを返す
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return get_user_from_token(token)

# src/api/routes/users.py
@router.get("/me")
def get_current_user_profile(user = Depends(get_current_user)):
    return user
```

### Q: プロジェクトにデータベースモデルを追加するには?

**A:** STANDARD または FULL スタックで、SQLAlchemy モデルを作成します:

```python
# src/models/users.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### Q: リクエストデータの検証を追加するには?

**A:** スキーマで Pydantic モデルを使います:

```python
# src/schemas/users.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### Q: ファイルアップロードはどう扱いますか?

**A:** FastAPI の `UploadFile` を使います:

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    # ファイルを保存
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

## テンプレート

### Q: 利用できるテンプレートは?

**A:** FastAPI-fastkit には、あらかじめ用意されたテンプレートが複数含まれています:

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-default         │ Simple FastAPI Project            │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-custom-response │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI API            │
│ fastapi-empty           │ Minimal FastAPI Project           │
│ fastapi-mcp             │ MCP (Model Context Protocol) API  │
│ fastapi-psql-orm        │ PostgreSQL FastAPI API            │
│ fastapi-single-module   │ Single-file FastAPI Project       │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

### Q: 特定のテンプレートを使うには?

**A:** `startdemo` コマンドを使います:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Select template: fastapi-psql-orm
```

</div>

### Q: 自分でテンプレートを作れますか?

**A:** 作れます。ディレクトリ構造を用意し、テンプレート変数を使います:

```
my-template/
├── src/
│   └── main.py-tpl
├── requirements.txt-tpl
└── template.yaml
```

```python
# main.py-tpl
from fastapi import FastAPI

app = FastAPI(title="{{PROJECT_NAME}}")

@app.get("/")
def read_root():
    return {"message": "Hello from {{PROJECT_NAME}}!"}
```

### Q: 既存のテンプレートを変更するには?

**A:** テンプレートは `fastapi_project_template` ディレクトリにあります:

1. **リポジトリをフォーク** してテンプレートを変更
2. 既存をベースに **カスタムテンプレートを作成**
3. プロジェクト作成後に **特定のファイルを上書き**

## 開発サーバー

### Q: 開発サーバーを起動するには?

**A:** プロジェクトディレクトリで `runserver` コマンドを使います:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate  # 仮想環境を有効化
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Q: サーバーが起動しない — "Address already in use"

**A:** ポート 8000 がビジー状態です。別のポートを使うか、既存プロセスを終了してください:

<div class="termy">

```console
# 別のポートを使う
$ fastkit runserver --port 8080

# あるいは既存プロセスを特定して終了
$ lsof -ti:8000 | xargs kill -9

# Windows
$ netstat -ano | findstr :8000
$ taskkill /PID <PID> /F
```

</div>

### Q: 自動リロードが動きません

**A:** プロジェクトディレクトリにいて、仮想環境が有効化されているか確認してください:

<div class="termy">

```console
# 現在のディレクトリを確認
$ pwd
/path/to/my-project

# 仮想環境を確認
$ which python
/path/to/my-project/.venv/bin/python

# 明示的に reload を指定
$ fastkit runserver --reload
```

</div>

### Q: 本番運用向けにサーバーをどう設定すれば?

**A:** 本番では開発サーバーを使わないでください。次のようにします:

```python
# gunicorn などの WSGI サーバーを使う
$ pip install gunicorn
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# あるいは fastapi-dockerized テンプレートで Docker
$ fastkit startdemo  # fastapi-dockerized を選択
$ docker build -t my-app .
$ docker run -p 8000:8000 my-app
```

## パフォーマンスと最適化

### Q: API のパフォーマンスを向上させるには?

**A:** いくつかの最適化戦略があります:

1. I/O 操作には **async/await を使用**
2. 重い処理には **キャッシュを追加**
3. **データベースクエリを最適化**
4. 重い処理には **バックグラウンドタスクを使用**

```python
# 非同期エンドポイント
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await users_service.get_user_async(user_id)
    return user

# バックグラウンドタスク
from fastapi import BackgroundTasks

@router.post("/send-email")
def send_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(send_notification_email, email)
    return {"message": "Email will be sent in background"}
```

### Q: キャッシュを追加するには?

**A:** Redis でキャッシュします:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # キャッシュから取得を試みる
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # 関数を実行して結果をキャッシュ
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)
async def get_expensive_data():
    # 重い処理
    return complex_calculation()
```

### Q: 大量の同時リクエストはどう扱えば?

**A:** 適切なサーバー設定を使います:

<div class="termy">

```console
# 開発
$ fastkit runserver --workers 1  # 開発はシングルワーカー

# 本番
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
$ uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

</div>

## テスト

### Q: テストを実行するには?

**A:** プロジェクトディレクトリで pytest を使います:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate
$ python -m pytest

# カバレッジ付き
$ python -m pytest --cov=src

# 特定のテストファイル
$ python -m pytest tests/test_users.py

# 詳細出力
$ python -m pytest -v
```

</div>

### Q: API テストはどう書けば?

**A:** FastAPI のテストクライアントを使います:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user():
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
```

### Q: 外部依存をモックするには?

**A:** pytest フィクスチャとモックを使います:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    with patch('src.database.get_db') as mock_db:
        mock_db.return_value = Mock()
        yield mock_db

def test_user_creation_with_mock_db(mock_database):
    # モックされた DB でテスト
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
```

## コントリビュート

### Q: FastAPI-fastkit にどう貢献すれば?

**A:** 次の手順で進めてください:

1. GitHub で **リポジトリをフォーク**
2. **開発環境をセットアップ**
3. **機能ブランチを作成**
4. テスト付きで **変更を実装**
5. **プルリクエストを送信**

<div class="termy">

```console
$ git clone https://github.com/yourusername/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make dev-setup  # 開発環境をセットアップ
$ git checkout -b feature/my-feature
# 変更を実装 ...
$ make dev-check  # フォーマット、リント、テスト
$ git commit -m "feat: add new feature"
$ git push origin feature/my-feature
```

</div>

### Q: プルリクエストには何を含めるべき?

**A:** すべての PR に次を含めてください:

- [ ] **明確な変更内容の説明**
- [ ] 新機能には **テスト**
- [ ] 必要に応じて **ドキュメント更新**
- [ ] **コードガイドラインの遵守**
- [ ] **すべてのチェックを通過**

### Q: バグはどう報告すれば?

**A:** GitHub Issue を作成し、次を含めてください:

1. **バグの説明** と期待される挙動
2. **再現手順**
3. **環境情報** (OS、Python バージョンなど)
4. **エラーメッセージ** やログ
5. 可能なら **最小再現例**

### Q: 新機能はどうリクエストすれば?

**A:** 機能リクエスト Issue を開き、次を含めてください:

1. 機能の **明確な説明**
2. **ユースケース** と動機
3. **実装案** (任意)
4. 類似機能の **例**

## トラブルシューティング

### Q: import エラーが出ます

**A:** Python パスと仮想環境を確認してください:

<div class="termy">

```console
# 仮想環境が有効か確認
$ which python
/path/to/project/.venv/bin/python

# Python パスを確認
$ python -c "import sys; print(sys.path)"

# 開発時は editable モードで再インストール
$ pip install -e .
```

</div>

### Q: データベース接続の問題

**A:** データベーステンプレートでは、データベースが起動しているか確認してください:

<div class="termy">

```console
# PostgreSQL テンプレート
$ docker-compose up -d postgres  # データベース起動
$ alembic upgrade head            # マイグレーション実行

# 接続を確認
$ docker-compose logs postgres
```

</div>

### Q: テンプレートファイルが見つからない

**A:** テンプレートパスの問題が原因のことが多いです:

<div class="termy">

```console
# 利用可能なテンプレートを確認
$ fastkit list-templates

# テンプレートディレクトリを確認
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__path__)"

# テンプレートが欠けている場合は再インストール
$ pip uninstall fastapi-fastkit
$ pip install fastapi-fastkit
```

</div>

### Q: pre-commit フックが失敗します

**A:** フックをインストールして実行します:

<div class="termy">

```console
$ pip install pre-commit
$ pre-commit install
$ pre-commit run --all-files

# フォーマット問題を修正
$ black src/ tests/
$ isort src/ tests/
```

</div>

### Q: CI ではテストが落ちるのにローカルでは通る

**A:** よくある原因と対処:

1. **環境差**: Python バージョンが一致しているか確認
2. **依存関係不足**: テスト要件が入っているか確認
3. **パスの問題**: 絶対 import を使う
4. **タイミング問題**: 非同期テストに適切な待機を入れる

<div class="termy">

```console
# CI と同じ Python バージョンでテスト
$ python3.12 -m pytest

# 不足している依存関係を確認
$ pip install -r requirements-dev.txt

# 隔離環境でテストを実行
$ tox
```

</div>

## ヘルプ

### Q: どこでヘルプを得られますか?

**A:** いくつか方法があります:

- **GitHub Issues**: バグや機能リクエスト
- **GitHub Discussions**: 質問やコミュニティサポート
- **ドキュメント**: ユーザーガイドとチュートリアル
- **コード例**: 既存テンプレートとテスト

### Q: 最新情報を追うには?

**A:** プロジェクトの更新を追ってください:

- GitHub で **リポジトリを Watch**
- 新機能は **リリース** で確認
- 破壊的変更は **changelog** を読む
- ドキュメントの **ベストプラクティス** に従う

!!! tip "プロのコツ"
    - Python プロジェクトでは常に仮想環境を使う
    - FastAPI-fastkit を最新に保つ
    - 利用可能なコマンドは `fastkit --help` で確認
    - 困ったらドキュメントを見る
    - 質問は GitHub Discussions で気軽にどうぞ

# `fastapi-domain-starter` によるドメイン指向 FastAPI

推奨される現代的なレイアウト — `src/app/domains/` 配下に **ビジネス概念ごとに 1 フォルダ** — を使って、中規模の FastAPI サービスを構築します。このチュートリアルでは `fastapi-domain-starter` テンプレートを最初から最後まで取り上げます。生成方法、各トップレベルパッケージの役割、付属の `items` サンプルの配線、そして次のドメインを追加する手順まで順に確認します。

## 学べること

- `fastkit startdemo fastapi-domain-starter` でプロジェクトを生成する
- レイアウトにおける `core`、`db`、`domains`、`tests` の役割
- ドメインを router → service → repository → schemas → models に分割する考え方
- 新しいドメインを追加するための手順 (items フォルダをコピーし、ルーターを登録)
- 付属の `/health` エンドポイントと `/api/v1/items` CRUD が、どのようにアプリに組み込まれているか

## 前提条件

- Python 3.12 以上
- FastAPI-fastkit がインストール済み (`pip install fastapi-fastkit`)
- 基本的な FastAPI の概念 (パス操作、Pydantic スキーマ、依存性) に慣れていること

これが初めての FastAPI プロジェクトであれば、まず [基本 API サーバーの構築](basic-api-server.md) から始めましょう — そちらはよりシンプルな `fastapi-default` テンプレートを使います。

## ステップ 1: プロジェクトを生成

```console
$ fastkit startdemo fastapi-domain-starter
Enter the project name: orders-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Domain-oriented orders service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

`fastkit` がテンプレートを展開し、プレースホルダを埋め、仮想環境を作成し、依存関係をインストールします。完了したらプロジェクトに入りましょう:

```console
$ cd orders-api
$ bash scripts/run-server.sh    # または: uvicorn src.app.main:app --reload
```

API ドキュメントは <http://127.0.0.1:8000/docs> で提供されます。

## ステップ 2: 生成されるツリー

```
orders-api/
├── README.md
├── pyproject.toml              # PEP 621 メタデータ + [tool.fastapi-fastkit]
├── requirements.txt            # 固定された依存関係一覧 (テンプレートには両方が含まれます。パッケージを追加した場合は自分で更新)
├── .env                        # SECRET_KEY、ENVIRONMENT
├── .gitignore
├── scripts/
│   ├── format.sh               # black + isort
│   ├── lint.sh                 # black --check + isort --check + mypy
│   ├── run-server.sh           # uvicorn src.app.main:app --reload
│   └── test.sh                 # pytest
├── src/
│   ├── __init__.py
│   └── app/                    # アプリケーションパッケージ
│       ├── __init__.py
│       ├── main.py             # FastAPI() + ミドルウェア + api_router の取り込み
│       ├── core/               # 横断的な設定
│       │   ├── __init__.py
│       │   └── config.py       # pydantic-settings (PROJECT_NAME、CORS、...)
│       ├── db/                 # 永続化の抽象化
│       │   ├── __init__.py
│       │   └── memory.py       # InMemoryStore[T] ジェネリック KV ストア
│       ├── api/                # トランスポート層のルーティング
│       │   ├── __init__.py
│       │   ├── health.py       # GET /health
│       │   └── router.py       # health + 各ドメインルーターを集約
│       └── domains/            # ビジネス概念 (1 フォルダにつき 1 概念)
│           ├── __init__.py
│           └── items/          # 例題のドメイン
│               ├── __init__.py
│               ├── models.py       # @dataclass Item (エンティティ)
│               ├── schemas.py      # ItemCreate、ItemRead (pydantic)
│               ├── repository.py   # InMemoryStore を包む ItemRepository
│               ├── service.py      # ItemService + ItemNotFoundError
│               └── router.py       # APIRouter(prefix="/items")
└── tests/
    ├── __init__.py
    ├── conftest.py             # TestClient フィクスチャ、ストアリセット
    ├── test_health.py
    └── test_items.py
```

押さえておきたい 2 つの考え方:

1. **`src/app/`** が **アプリケーションパッケージ** です — ランタイムが import するものはすべてここに置かれます。テストもここから import します (`from src.app.main import app`)。外側の `src/` は、プロジェクトを `pip install` 可能にするために存在します。
2. **`src/app/domains/<concept>/`** が **概念ごとのスライス** です — 各ビジネス概念 (items、orders、users、...) が、自身の router / service / repository / schemas / models だけを所有します。

## ステップ 3: 各トップレベルパッケージの役割

### `src/app/core/` — 設定

横断的なアプリケーション設定をまとめる場所です。付属の `config.py` は `.env` / 環境変数から読み込まれる、pydantic-settings ベースの `Settings` クラスを公開します:

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "<project_name>"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: ... = []
    ...

settings = Settings()
```

`main.py` は `settings.PROJECT_NAME`、`settings.API_V1_PREFIX`、`settings.all_cors_origins` を読み取って FastAPI アプリを配線します。

**`core/` に追加するもの:** どの 1 つのドメインにも特有でないもの — グローバル設定、構造化ロギング、カスタムミドルウェア、セキュリティヘルパなど。

### `src/app/db/` — 永続化の境界

データストアに対する抽象化をまとめる場所です。スターターには `memory.py` が付属しており、エンティティ型に対してジェネリックなプロセスローカルの `InMemoryStore[T]` を提供します。各ドメインの repository は `InMemoryStore` を包むため、後で SQLAlchemy / 非同期ドライバに差し替える際の影響範囲を小さくできます。修正が必要になるのは基本的に repository だけです。

```python
class InMemoryStore(Generic[T]):
    def list(self) -> Iterable[T]: ...
    def get(self, id_: int) -> Optional[T]: ...
    def add(self, item: T) -> int: ...
    def replace(self, id_: int, item: T) -> bool: ...
    def delete(self, id_: int) -> bool: ...
    def clear(self) -> None: ...
```

**`db/` を育てるとき:** `InMemoryStore` から本物のデータベースへ移行したら、`session.py` を追加して実際のセッションファクトリを置きます。ドメイン側 repository の内部契約を変えなくて済むよう、公開メソッドの形 (`list` / `get` / `add` / ...) は揃えておきましょう。

### `src/app/api/` — トランスポートルーティング

2 つの要素から構成されます:

- `health.py` — `{"status": "ok"}` を返す `GET /health` を公開する小さな `APIRouter`。副作用がなく、liveness プローブに最適です。
- `router.py` — **トップレベル集約** です。health ルーターと各ドメインのルーターを取り込み、その単一の `api_router` を `/api/v1` の下にマウントします:

```python
# src/app/api/router.py
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items_router.router)
```

```python
# src/app/main.py
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
```

**ここで集約する理由:** 新しいドメインを追加するとき、`src/app/api/router.py` を編集してそのルーターを登録するだけで済みます。`main.py` は変更不要です。

### `src/app/domains/<concept>/` — ビジネススライス

プロジェクトが大きくなるにつれて、コードの大部分はここに集まります。各ドメインは 5 つのファイルを所有します:

| ファイル | 役割 |
|---|---|
| `models.py` | ドメインエンティティ (スターターでは `@dataclass`、後で SQLAlchemy / SQLModel に差し替え可能)。内部の形 — wire 形式ではない。 |
| `schemas.py` | API の入出力スキーマ (pydantic)。エンティティと分離されているため、ドメインロジックを触らずに wire 形式を進化させられる。 |
| `repository.py` | データアクセス。ストアをエンティティ型のメソッドで包む。永続化を入れ替える接合点。 |
| `service.py` | ビジネスロジック。router は `service` を呼び、`repository` を直接呼ばない。ドメイン固有の例外 (例: `ItemNotFoundError`) はここに置く。 |
| `router.py` | HTTP トランスポート。pydantic スキーマ ↔ サービス呼び出しの変換を行い、ドメイン例外を `HTTPException` に変換する。 |

**依存方向** は `router → service → repository → store` です。各層は自身より下の層にしか依存しません。schemas は router と service が参照し、models は repository と service が参照します。

### `tests/`

ランタイムのレイアウトを反映する形で、振る舞いを固定したいポイントごとに 1 つずつテストモジュールを置きます。スターターに含まれているものは次のとおりです:

- `conftest.py` — テストの間に items ストアをリセットする autouse フィクスチャ、および `TestClient(app)` をラップした `client` フィクスチャ。
- `test_health.py` — `GET /api/v1/health` が 200 と `{"status": "ok"}` を返すことを検証。
- `test_items.py` — items エンドポイントの完全な CRUD をカバー。未知の id に対する 404、不正なペイロードに対する 422 を含む。

実行方法:

```console
$ bash scripts/test.sh         # または: pytest
```

## ステップ 4: 付属の `items` ドメインを読む

例題ドメインは小さなエンティティに対する CRUD です:

```python
# src/app/domains/items/models.py
@dataclass
class Item:
    id: int
    name: str
    price: float
    in_stock: bool = True
```

API スキーマは入力形式と出力形式を分離し、サーバー制御のフィールド (`id`) と検証 (price ≥ 0) を加えられるようになっています:

```python
# src/app/domains/items/schemas.py
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    price: float = Field(ge=0)
    in_stock: bool = True

class ItemRead(BaseModel):
    id: int
    name: str
    price: float
    in_stock: bool
    model_config = ConfigDict(from_attributes=True)
```

repository はインメモリストアを包み、insert 時に id を割り当てます:

```python
# src/app/domains/items/repository.py
class ItemRepository:
    def __init__(self, store: Optional[InMemoryStore[Item]] = None) -> None:
        self._store = store if store is not None else _store

    def add(self, name: str, price: float, in_stock: bool = True) -> Item:
        item = Item(id=0, name=name, price=price, in_stock=in_stock)
        new_id = self._store.add(item)
        item.id = new_id
        return item
    # list_all / get / replace / delete / reset は省略
```

service 層はビジネスルールを集約する場所です。今は薄いパススルーにカスタム例外が 1 つあるだけですが、将来のポリシー (「未確定の注文に紐づく item は削除できない」など) はここに置かれます:

```python
# src/app/domains/items/service.py
class ItemNotFoundError(Exception): ...

class ItemService:
    def __init__(self, repository: Optional[ItemRepository] = None) -> None:
        self._repository = repository if repository is not None else ItemRepository()

    def get_item(self, item_id: int) -> Item:
        item = self._repository.get(item_id)
        if item is None:
            raise ItemNotFoundError(f"Item {item_id} does not exist")
        return item
    # list_items / create_item / replace_item / delete_item は省略
```

router だけが HTTP を知る部分です。FastAPI の `Depends(...)` を介して service を受け取るのでテストで差し替えやすく、`ItemNotFoundError` を `HTTPException(404)` にマップしている点に注目してください:

```python
# src/app/domains/items/router.py
router = APIRouter(prefix="/items", tags=["items"])

def get_item_service() -> ItemService:
    return ItemService()

@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, service: ItemService = Depends(get_item_service)) -> ItemRead:
    try:
        return ItemRead.model_validate(service.get_item(item_id))
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
```

完全な router は次を公開します:

| メソッド | パス | 動作 |
|---|---|---|
| `GET` | `/api/v1/items` | items の一覧 |
| `GET` | `/api/v1/items/{item_id}` | 1 件取得 |
| `POST` | `/api/v1/items` | 作成 (201 を返す) |
| `PUT` | `/api/v1/items/{item_id}` | 置換 |
| `DELETE` | `/api/v1/items/{item_id}` | 削除 (204 を返す) |
| `GET` | `/api/v1/health` | Liveness プローブ |

試してみましょう:

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
       -H 'Content-Type: application/json' \
       -d '{"name":"Mug","price":9.5,"in_stock":true}'
{"id":1,"name":"Mug","price":9.5,"in_stock":true}

$ curl http://127.0.0.1:8000/api/v1/items
[{"id":1,"name":"Mug","price":9.5,"in_stock":true}]

$ curl http://127.0.0.1:8000/api/v1/items/999
{"detail":"Item 999 does not exist"}
```

## ステップ 5: 次のドメインを追加する

スターターは **ドメインの追加がコピーとリネームの操作で済む** ように設計されています。たとえば `items` の隣に `users` ドメインを置きたい場合:

### 1. `items/` フォルダをコピー

```console
$ cp -r src/app/domains/items src/app/domains/users
```

### 2. エンティティ、スキーマ、各ファイルのクラス名を書き換える

```python
# src/app/domains/users/models.py
from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    is_active: bool = True
```

```python
# src/app/domains/users/schemas.py
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    # 単純な ``str`` のままにしておけば、このスニペットはそのまま動きます。
    # pydantic 組み込みのメール検証を使いたい場合は、オプション依存を追加で
    # 入れて (``pip install 'pydantic[email]'`` — ``email-validator`` が
    # 入ります)、``str`` を ``EmailStr`` に切り替えてください。
    email: str = Field(min_length=3, max_length=320)
    is_active: bool = True

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
```

`Item → User`、`ItemNotFoundError → UserNotFoundError`、`ItemRepository → UserRepository`、`ItemService → UserService` を `models.py`、`schemas.py`、`repository.py`、`service.py`、`router.py` の全体でリネームします。router 内の `prefix="/items"` を `prefix="/users"` に、`tags=["items"]` を `tags=["users"]` に変更するのも忘れずに。

repository は同じく `InMemoryStore` ベースのパターンをそのまま流用できます — エンティティ型に対してジェネリックだからです:

```python
# src/app/domains/users/repository.py
_store: InMemoryStore[User] = InMemoryStore()

class UserRepository:
    def __init__(self, store: Optional[InMemoryStore[User]] = None) -> None:
        self._store = store if store is not None else _store
    # ... ItemRepository と同じ形 ...
```

### 3. ドメインの `__init__.py` を更新する

items ドメインは、呼び出し側が `from src.app.domains.items import service` と書けるよう、自身のモジュールを再エクスポートしています。users でも同様にミラーします:

```python
# src/app/domains/users/__init__.py
from src.app.domains.users import (  # noqa: F401
    models,
    repository,
    router,
    schemas,
    service,
)
```

### 4. 集約点に router を登録する

これが **`domains/users/` の外で唯一触る必要のあるファイル** です:

```python
# src/app/api/router.py
from src.app.api import health
from src.app.domains.items import router as items_router
from src.app.domains.users import router as users_router  # ← 追加

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items_router.router)
api_router.include_router(users_router.router)             # ← 追加
```

サーバーを再起動すると、`/docs` に `/api/v1/users` がマウントされます。

### 5. テストを追加する

`tests/test_items.py` をミラーして `tests/test_users.py` を作成します — クライアント駆動の同じ形のまま、新しいエンドポイントを叩くだけです。`conftest.py` の autouse なストアリセットフィクスチャが、各テストを引き続き分離してくれます。

`InMemoryStore` を使う 2 つ目のドメインを追加する場合は、フィクスチャを拡張してそのストアもリセットするか、ドメインごとにフィクスチャを分けてください。

## ステップ 6: 次に学ぶこと

- [アーキテクチャプリセットマトリクス](../reference/preset-feature-matrix.md) は、`fastkit init --interactive` がプリセットごとに何を生成するかを示しています。`domain-starter` のもとで手動配線が必要な機能選択も確認できます。
- [`fastapi-default` チュートリアル](basic-api-server.md) は、レイアウトを比較した上でコミットしたい場合のレイヤー型オルタナティブをカバーします。
- データベース統合については、[データベース統合チュートリアル](database-integration.md) で PostgreSQL + SQLAlchemy + Alembic のパターンを示しています。同じ考え方が `src/app/db/` とドメインごとの `repository.py` に当てはまります。

## まとめ

- **生成**: `fastkit startdemo fastapi-domain-starter` → `bash scripts/run-server.sh` → ドキュメントは `/docs`。
- **レイアウト**: 設定は `core/`、永続化抽象化は `db/`、ビジネススライスは `domains/<concept>/`、唯一の集約点が `api/router.py`、`tests/` はランタイムモジュールをミラー。
- **ドメインの追加**: `items/` をコピー、エンティティ / スキーマ / クラスをリネーム、`__init__.py` の再エクスポートを更新、`src/app/api/router.py` で router を登録、テストモジュールを追加。`main.py` の編集は不要です。

# `fastapi-sqlmodel` による非同期永続化

各概念を **一度だけ** 定義するデータベース駆動の API を構築します。SQLModel のクラスは
SQLAlchemy のテーブルであると同時に pydantic のスキーマでもあるため、カラムを 1 つ追加するために
4 つのファイルを編集する必要はありません。このチュートリアルでは `fastapi-sqlmodel` テンプレートを
取り上げます。モデル階層、汎用 CRUD ベース、ページネーションされたレスポンス、非同期 Alembic
マイグレーション、そして独自のドメインを追加する方法を順に確認します。

## 学べること

- `fastkit startdemo fastapi-sqlmodel` でプロジェクトを生成する
- `ItemBase` → `Item` / `ItemCreate` / `ItemUpdate` / `ItemPublic` がスキーマの重複をなくす仕組み
- `CRUDBase` が標準で提供するものと、拡張すべき場所
- `Page[T]` のリスト用エンベロープと、その上限がどこで適用されるか
- 非同期 Alembic マイグレーションの実行と、SQLite から PostgreSQL への切り替え

## 前提条件

- Python 3.12 以上
- FastAPI-fastkit がインストール済み (`pip install fastapi-fastkit`)
- `async`/`await` と基本的な SQL の概念に慣れていること

同期型で Compose ベースの PostgreSQL スタックが必要な場合は、`fastapi-psql-orm` を使う
[データベース統合](database-integration.md) を参照してください。

## ステップ 1: 生成と実行

```console
$ fastkit startdemo fastapi-sqlmodel
Enter the project name: catalog-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Product catalog service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

```console
$ cd catalog-api
$ bash scripts/migrate.sh        # alembic upgrade head
$ bash scripts/run-server.sh     # または: uvicorn src.app.main:app --reload
```

デフォルトの `DATABASE_URL` は `sqlite+aiosqlite:///./app.db` なので、データベースサーバーを
インストールする必要はありません。ドキュメントは <http://127.0.0.1:8000/docs> で提供されます。

## ステップ 2: 生成されるツリー

```
catalog-api/
├── pyproject.toml              # PEP 621 メタデータ + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env
├── scripts/
│   ├── format.sh  lint.sh  migrate.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI アプリ + lifespan
│       ├── core/config.py      # pydantic-settings
│       ├── db/
│       │   ├── session.py      # 非同期エンジン、get_session 依存性
│       │   └── base.py         # Alembic 用のメタデータ集約
│       ├── crud/
│       │   ├── base.py         # 汎用 CRUDBase
│       │   └── pagination.py   # Page[T] エンベロープ
│       ├── alembic/
│       │   ├── env.py          # 非同期マイグレーション環境
│       │   └── versions/0001_create_items_table.py
│       ├── api/
│       │   ├── router.py       # health + ドメインルーターを集約
│       │   └── health.py       # GET /health
│       └── domains/items/      # 例題のドメイン
│           ├── models.py       # Item テーブル + Create/Update/Public スキーマ
│           ├── crud.py         # ItemCRUD(CRUDBase)
│           └── router.py       # FastAPI ルーター
└── tests/
    ├── conftest.py  test_health.py  test_items.py  test_crud_base.py
```

ドメインフォルダに *含まれていない* ものに注目してください: `models.py` とは別の `schemas.py` はなく、
ドメインごとの repository のボイラープレートもありません。前者は SQLModel に、後者は `CRUDBase` に
吸収されています。

## ステップ 3: 概念ごとに 1 つのモデル定義

`src/app/domains/items/models.py` を開きます。すべてが 1 つのベースから派生しています:

```python
class ItemBase(SQLModel):
    """テーブルとすべてのリクエスト/レスポンススキーマで共有されるフィールド。"""
    name: str = Field(min_length=1, max_length=128, index=True)
    description: str | None = Field(default=None, max_length=512)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemBase, table=True):        # 実際のテーブル
    __tablename__ = "items"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)


class ItemCreate(ItemBase): ...          # POST ボディ — サーバーが割り当てるフィールドなし


class ItemUpdate(SQLModel):              # PATCH ボディ — すべてのフィールドが任意
    name: str | None = Field(default=None, min_length=1, max_length=128)
    ...


class ItemPublic(ItemBase):              # レスポンス — ベース + サーバーが割り当てるフィールド
    id: int
    created_at: datetime
```

4 つのクラスがそれぞれ別の役割を持ち、フィールドが定義される場所は 1 か所だけです:

| クラス        | 役割                          | 分離されている理由 |
|--------------|-------------------------------|-------------------|
| `ItemBase`   | 共有フィールドの定義            | 唯一の情報源 |
| `Item`       | データベーステーブル            | `id`、`created_at` を追加 |
| `ItemCreate` | `POST` のリクエストボディ       | `id` を受け付けてはならない |
| `ItemUpdate` | `PATCH` のリクエストボディ      | すべてのフィールドが任意 |
| `ItemPublic` | レスポンスボディ                | サーバーが割り当てたフィールドを公開 |

**得られるもの:** `sku` カラムを追加するには、`ItemBase` に 1 行追加するだけです。テーブルにカラムが
追加され、作成用ボディがそれを受け付け、レスポンスがそれを返します — ほかの編集は不要です。
`ItemUpdate` は意図的に明示的なままにしています: 部分更新のセマンティクスは派生させるものではなく、
決めるべきものだからです。

## ステップ 4: 書き直さなくてよい CRUD

`src/app/crud/base.py` は、テーブルモデルとその 2 つの入力スキーマでパラメータ化された汎用クラスです:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, session, obj_id) -> ModelType | None: ...
    async def list(self, session, *, offset=0, limit=20) -> Sequence[ModelType]: ...
    async def count(self, session) -> int: ...
    async def create(self, session, obj_in) -> ModelType: ...
    async def update(self, session, db_obj, obj_in) -> ModelType: ...
    async def delete(self, session, db_obj) -> None: ...
```

しっかり理解しておきたい細部が 1 つあります — `update` は `exclude_unset=True` を使用します:

```python
changes: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
```

これが `PATCH` を本当の部分更新にしています。クライアントが送らなかったフィールドは dict に含まれない
ため、書き込まれることはありません。`exclude_unset` がなければ、`PATCH` は触れていないカラムを
スキーマのデフォルト値で黙って上書きしてしまいます。

ドメインはベースをサブクラス化し、そのドメイン固有のものだけを追加します:

```python
class ItemCRUD(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """名前検索を追加した Item 用の CRUD。"""

    async def search_by_name(self, session, term, *, limit=20):
        statement = select(Item).where(Item.name.like(f"%{term}%")).limit(limit)
        result = await session.exec(statement)
        return result.all()


item_crud = ItemCRUD(Item)
```

## ステップ 5: ページネーションされたリスト

リスト系エンドポイントは、素の配列ではなく `Page[T]` エンベロープを返します:

```json
{"items": [...], "total": 42, "offset": 0, "limit": 20}
```

上限の切り詰めはクライアントではなく router で行われます:

```python
limit: int = Query(default=settings.DEFAULT_PAGE_LIMIT, ge=1)
...
limit = min(limit, settings.MAX_PAGE_LIMIT)
```

そのため、`?limit=100000` で 1 回のリクエストをテーブル全体のスキャンに変えることはできません。
`Page` は `offset`、`len(items)`、`total` から導出される `has_next` プロパティも公開しており、
これはたいていフロントエンドが実際に必要とするものです。

items ドメインが提供するエンドポイント:

| メソッド | エンドポイント              | 説明                           |
|--------|---------------------------|--------------------------------|
| GET    | `/api/v1/health`          | Liveness プローブ               |
| GET    | `/api/v1/items`           | items の一覧 (`offset`、`limit`) |
| GET    | `/api/v1/items/{item_id}` | item を 1 件取得                |
| POST   | `/api/v1/items`           | item を作成 (`201`)             |
| PATCH  | `/api/v1/items/{item_id}` | item を部分更新                 |
| DELETE | `/api/v1/items/{item_id}` | item を削除 (`204`)             |

試してみましょう:

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
    -H 'Content-Type: application/json' \
    -d '{"name": "Keyboard", "price": 89.0}'

$ curl 'http://127.0.0.1:8000/api/v1/items?offset=0&limit=5'
```

## ステップ 6: 端から端まで非同期

`src/app/db/session.py` はプロセスごとに 1 つの `AsyncEngine` を構築し、リクエストスコープの
セッションを払い出します:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

router はこれに依存し (`session: AsyncSession = Depends(get_session)`)、`CRUDBase` はこれを第 1 引数と
して受け取り、すべてのデータベース呼び出しは await されます。リクエストパス上で I/O のためにイベント
ループをブロックするものはありません。

`create_db_and_tables()` もここにあり、アプリの `lifespan` から呼び出されます。これは SQLite の
デフォルトとテストのための便宜的な機能です — Alembic がスキーマを管理するようになったら、
`CREATE_TABLES_ON_STARTUP=false` を設定してください。

## ステップ 7: ドメインを追加する

1. `items` をミラーして `src/app/domains/<your_domain>/` を作成します
   (`models.py`、`crud.py`、`router.py`)。
2. **`src/app/db/base.py` でテーブルモデルを import します。** これは忘れやすく、デバッグで混乱しやすい
   ステップです: Alembic の autogenerate と `create_db_and_tables` は import 済みのモデルしか認識しない
   ため、import を忘れるとエラーにはならず、空のマイグレーションとして現れます。
3. `src/app/api/router.py` に router を登録します。`# fastkit:imports` と `# fastkit:routes` の
   アンカーは `fastkit addroute` がコードを挿入する場所を示しています — 自分のコードも同じ場所に置きましょう。
4. マイグレーションを生成します:
   `alembic revision --autogenerate -m "add <domain>"`。
5. `tests/test_items.py` をミラーして `tests/test_<your_domain>.py` を追加します。

## ステップ 8: マイグレーションと PostgreSQL

`src/app/alembic/env.py` 配下の Alembic 環境は非同期なので、アプリと同じドライバスタックで動作します。
日常的な操作:

```console
$ bash scripts/migrate.sh                                  # upgrade head
$ alembic revision --autogenerate -m "add sku to items"    # モデル変更後
```

データベースの切り替えは、URL の変更とドライバの追加だけです:

```console
$ uv pip install "asyncpg>=0.31.0"
$ export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/app"
$ bash scripts/migrate.sh
```

モデル、CRUD、router は何も変わりません — ドライバを `create_engine` の背後に置いておく目的はそこにあります。

## ステップ 9: テスト

```console
$ bash scripts/test.sh    # または: pytest
```

各テストは新しいインメモリの SQLite データベースに対して実行されます: マイグレーションも、フィクスチャ
ファイルも、テスト間のクリーンアップも不要です。`test_crud_base.py` は汎用ベースを直接検証します —
拡張する前に読んでおく価値があります。自分のドメインが継承する `exclude_unset` の振る舞いと
count/offset の契約がそこに記述されているからです。

## まとめ

- **生成**: `fastkit startdemo fastapi-sqlmodel` →
  `bash scripts/migrate.sh` → `bash scripts/run-server.sh`。
- **モデル**: `ItemBase` がフィールドを保持し、テーブルと入出力スキーマはそこから派生するため、
  新しいカラムは一度だけ宣言すれば済みます。
- **CRUD**: `CRUDBase` が get / list / count / create / update / delete を提供し、ドメインは独自の
  クエリのためにそれをサブクラス化します。
- **リスト**: サーバー側で上限を切り詰める `Page[T]` エンベロープ。
- **スキーマ**: 非同期 Alembic。新しいモデルは `src/app/db/base.py` で import するのを忘れずに。
- **データベース**: デフォルトは SQLite、`DATABASE_URL` を変更して `asyncpg` をインストールすれば PostgreSQL。

## 次に学ぶこと

- [JWT 認証](auth-jwt.md) — このデータ層の前にアカウントと保護されたルートを置きます。
- [ドメイン指向プロジェクト](domain-starter.md) — 両テンプレートが共有するレイアウトです
  (データベースは含みません)。
- [どのスターターを選ぶべき?](../user-guide/choosing-a-starter.md)

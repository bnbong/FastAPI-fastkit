# `fastapi-auth-jwt` による JWT 認証

最初のコミットから本物のアカウント機能を備えた API を構築します。このチュートリアルでは
`fastapi-auth-jwt` テンプレートを最初から最後まで取り上げます。トークンペアの発行とローテーションの仕組み、
再送されたリフレッシュトークンが拒否される理由、ロールとスコープのガードの配線、そして SQLite から
移行するときに何が変わるのかを順に確認します。

## 学べること

- `fastkit startdemo fastapi-auth-jwt` でプロジェクトを生成する
- アクセストークンとリフレッシュトークンの違い、そしてローテーションが重要な理由
- `get_current_user`、`get_current_active_superuser`、`require_scopes(...)` がルートを保護する方法
- パスワードのハッシュ化がどこで行われ、なぜ argon2id なのか
- 付属の SQLite ファイルから Alembic を使って PostgreSQL へ移行する

## 前提条件

- Python 3.12 以上
- FastAPI-fastkit がインストール済み (`pip install fastapi-fastkit`)
- FastAPI の依存性と pydantic スキーマに慣れていること

FastAPI アプリを一度も作ったことがない場合は、まず
[基本 API サーバーの構築](basic-api-server.md) を読んでから戻ってきてください — このテンプレートは
基本を理解していることを前提としています。

## ステップ 1: プロジェクトを生成

```console
$ fastkit startdemo fastapi-auth-jwt
Enter the project name: accounts-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Accounts and sessions service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

次に実行します:

```console
$ cd accounts-api
$ bash scripts/run-server.sh    # または: uvicorn src.app.main:app --reload
```

アプリは SQLite (`sqlite:///./app.db`) 上で起動し、起動時にテーブルを作成します。そのため、事前に
インストールや設定をする必要はありません。ドキュメントは <http://127.0.0.1:8000/docs> で提供されます。

!!! tip "コミットする前にプレビュー"
    `fastkit startdemo fastapi-auth-jwt --dry-run` は何も書き込まずに、ファイルツリーとパッケージ一覧を
    出力します — これから何が手に入るのかを確認するのに便利です。

## ステップ 2: 生成されるツリー

```
accounts-api/
├── pyproject.toml              # PEP 621 メタデータ + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env                        # SECRET_KEY、DATABASE_URL、トークンの有効期間
├── scripts/
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI() + lifespan + CORS + api_router
│       ├── core/
│       │   ├── config.py       # pydantic-settings
│       │   └── security.py     # argon2 ハッシュ化 + JWT エンコード/デコード
│       ├── db/session.py       # engine + get_session 依存性
│       ├── api/
│       │   ├── router.py       # health + 各ドメインルーターを集約
│       │   ├── health.py       # GET /health
│       │   └── deps.py         # セッション、現在のユーザー、ロール/スコープガード
│       ├── domains/
│       │   ├── auth/           # ログイン、リフレッシュのローテーション、ログアウト
│       │   └── users/          # 登録とプロフィール
│       └── alembic/            # マイグレーション環境 + versions/
└── tests/
    ├── conftest.py  test_health.py  test_auth.py  test_users.py
```

レイアウトは `domain-starter` と同じ形です。各ドメインは自身の `router.py` (トランスポート)、
`service.py` (ビジネスロジック)、`repository.py` (データアクセス)、`models.py` (テーブル)、
`schemas.py` (API の入出力) を所有します。認証に関する関心事は `auth/` に、アカウントに関する関心事は
`users/` に置かれ、どちらも相手の内部には踏み込みません。

## ステップ 3: 登録、ログイン、保護されたルートの呼び出し

```console
# 1. 登録
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email": "alice@example.com", "password": "s3cret-password"}'

# 2. ログイン — フォームエンコードである点に注意: これは OAuth2 パスワードフローです
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
    -d 'username=alice@example.com&password=s3cret-password'
{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# 3. 保護されたルートを呼び出す
$ curl http://127.0.0.1:8000/api/v1/users/me \
    -H "Authorization: Bearer $ACCESS_TOKEN"
```

Swagger の「Authorize」ボタンも同じフローを実行するので、ブラウザを離れずに `/docs` から
保護されたルートを試せます。

エンドポイントの全体像:

| メソッド | エンドポイント                | 認証        | 説明                               |
|--------|-----------------------------|-------------|-----------------------------------|
| GET    | `/api/v1/health`            | —           | Liveness プローブ                  |
| POST   | `/api/v1/auth/register`     | —           | アカウントを作成                    |
| POST   | `/api/v1/auth/login`        | —           | OAuth2 パスワードフォーム → トークンペア |
| POST   | `/api/v1/auth/refresh`      | リフレッシュトークン | 新しいトークンペアにローテーション |
| POST   | `/api/v1/auth/logout`       | リフレッシュトークン | リフレッシュトークンを 1 つ失効させる |
| POST   | `/api/v1/auth/logout-all`   | アクセストークン | ユーザーのすべてのセッションを失効させる |
| GET    | `/api/v1/users/me`          | アクセストークン | 現在のユーザーのプロフィール       |
| PATCH  | `/api/v1/users/me`          | アクセストークン | 現在のユーザーのプロフィールを更新 |
| GET    | `/api/v1/users/me/scopes`   | スコープ `me` | スコープで保護されたルートの例     |
| GET    | `/api/v1/users`             | スーパーユーザー | ロールで保護されたユーザー一覧     |

## ステップ 4: 2 つのトークンとその理由

ログインすると **ペア** が返されます:

- **アクセストークン** は短命 (`ACCESS_TOKEN_EXPIRE_MINUTES`、デフォルトは 30) で、すべてのリクエストに
  付けて送られます。短命なので、漏えいしてもすぐに使えなくなります。
- **リフレッシュトークン** は長命 (`REFRESH_TOKEN_EXPIRE_DAYS`、デフォルトは 14) で、用途はただ 1 つ、
  新しいペアを取得することだけです。

ここまでは珍しいことは何もありません。このテンプレートが一般的な JWT スニペットと異なるのは、
リフレッシュトークンを **追跡してローテーションする** 点です。発行されるすべてのリフレッシュトークンには
`jti` クレームが付与され、その `jti` がデータベースに書き込まれます:

```python
def issue_token_pair(self, user: User) -> TokenPair:
    scopes = user.scope_list
    access_token, _, _ = create_access_token(str(user.id), scopes)
    refresh_token, jti, expires_at = create_refresh_token(str(user.id), scopes)
    self.refresh_tokens.add(jti, user.id or 0, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

リフレッシュ時には、新しいペアを発行する **前に** 提示されたトークンが失効されます:

```python
def rotate(self, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token, REFRESH_TOKEN_TYPE)
    record = self.refresh_tokens.get_by_jti(str(payload.get("jti")))
    if record is None or record.revoked:
        raise TokenError("refresh token is no longer valid")
    ...
    self.refresh_tokens.revoke(record)
    return self.issue_token_pair(user)
```

試してみましょう: 一度リフレッシュしてから、*古い* リフレッシュトークンをもう一度送ります。

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 新しいペア

$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 401: トークンは使われた瞬間に失効しています
```

この 1 つの性質によって、盗まれたリフレッシュトークンは永続的なバックドアではなく、検出可能な
使い捨ての失敗に変わります。

ログアウトも同じ仕組みで動作します。これは素朴な JWT 構成では通常実現できないもう 1 つの点です:
`POST /auth/logout` はトークンを 1 つ失効させ、`POST /auth/logout-all` はそのユーザーに属する
すべてのリフレッシュトークンを失効させます。

## ステップ 5: パスワード

ハッシュ化は `src/app/core/security.py` にあり、`pwdlib` を通じて **argon2id** を使います — 旧来の
bcrypt 構成ではなく、現在推奨されているデフォルトです。router や service が平文のパスワードを目にするのは
検証する瞬間だけで、`hashed_password` がレスポンススキーマに含まれることもありません。

ここで設定する必要があるものはありません。唯一 *必ず* 設定しなければならないのは署名鍵です。

## ステップ 6: ロールとスコープ

3 つのガードが FastAPI の依存性として付属しています:

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

- **`get_current_user`** は bearer アクセストークンをデコードしてユーザーを読み込み、無効化された
  アカウントを `403` で拒否します。不正な形式のトークン、期限切れのトークン、削除済みユーザーを指す
  トークンはすべて `401` になります。
- **`get_current_active_superuser`** はその上に `is_superuser` のチェックを重ねます。
  `GET /api/v1/users` がこれを使用します。
- **`require_scopes(...)`** は特定のスコープを要求する依存性を構築します:

```python
from fastapi import Depends
from src.app.api.deps import require_scopes

@router.get("/reports", dependencies=[Depends(require_scopes("reports"))])
def read_reports() -> list[str]:
    ...
```

スコープはユーザー行にカンマ区切りの文字列 (`scopes: str`、`scope_list` プロパティで読み出し) として
保存され、発行されるすべてのトークンにコピーされます。これはスターターとして機能する最もシンプルな形を
意図的に選んだものです。権限モデルが文字列に収まらなくなったら、このカラムをロールテーブルに置き換え、
依存性のシグネチャはそのまま維持してください — router 側は何も変更する必要がありません。

## ステップ 7: 保護されたドメインを追加する

たとえば、ログイン済みのユーザーだけがアクセスできる `orders` ドメインを追加するには:

1. `users/` をミラーして `src/app/domains/orders/` を作成します
   (`models.py`、`schemas.py`、`repository.py`、`service.py`、`router.py`)。
2. アカウントが必要なルートでは `CurrentUser` を引数として受け取るか、router に
   `Depends(require_scopes("orders"))` を付けます。
3. `src/app/api/router.py` の `# fastkit:routes` アンカーの上に router を登録します。
   `fastkit addroute` も同じアンカーに書き込むので、手書きのルートと生成されたルートが 1 か所にまとまります。
4. マイグレーションを生成します: `alembic revision --autogenerate -m "add orders"`。
5. 新しいエンドポイント用に `tests/test_users.py` をミラーします。

## ステップ 8: 今は SQLite、後で PostgreSQL

デフォルトの `DATABASE_URL` はローカルの SQLite ファイルで、アプリは起動時に `create_db_and_tables()` を
呼び出します。そのため `pytest` も `uvicorn` も準備なしで動作します。ローカル開発以外の用途では、
代わりに Alembic にスキーマを管理させましょう:

```console
$ export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/app_db'
$ alembic upgrade head
```

モデルを変更したら:

```console
$ alembic revision --autogenerate -m "add profile fields"
```

## ステップ 9: デプロイの前に

`.env` の 2 つの設定が、これがデモなのか本物のサービスなのかを決めます:

- **`SECRET_KEY`** はすべてのトークンに署名します。未設定のままにすると、プロセスごとにランダムな鍵が
  生成されます — その結果、再起動のたびに全員がログアウトされ、複数のワーカー間でどのトークンが有効かの
  判断が食い違います。鍵を生成して固定してください:

  ```console
  $ python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **`DATABASE_URL`** はデータベースを選択します。SQLite のデフォルトは本番用のストアではありません。

必要に応じて `FIRST_SUPERUSER_EMAIL` と `FIRST_SUPERUSER_PASSWORD` を設定すると起動時にスーパーユーザーが
作成され、`BACKEND_CORS_ORIGINS` にフロントエンドのオリジンをカンマ区切りで設定することもできます。

## ステップ 10: テスト

```console
$ bash scripts/test.sh    # または: pytest
```

テストスイートはインメモリの SQLite データベースに対して `httpx.AsyncClient` を実行し、
登録 → ログイン → me → リフレッシュ → ログアウトという正常系全体をカバーします。さらに、実際に重要な
拒否パス — 誤ったパスワード、不正な形式のトークン、期限切れのトークン、そしてステップ 4 の再送された
リフレッシュトークン — も検証します。認証ルールを拡張するときは、まずこれらの拒否テストを拡張してください。
壊れたガードを捕まえてくれるのはこれらのテストです。

## まとめ

- **生成**: `fastkit startdemo fastapi-auth-jwt` →
  `bash scripts/run-server.sh` → ドキュメントは `/docs`。
- **トークン**: リクエストには短命のアクセストークン、リフレッシュトークンは `jti` で追跡してローテーション
  するため、再送は失敗し、ログアウトが実際に機能します。
- **ガード**: `get_current_user`、`get_current_active_superuser`、`require_scopes(...)` を
  通常の依存性として使用します。
- **ストレージ**: SQLite はそのまま使え、PostgreSQL は `DATABASE_URL` を設定して
  `alembic upgrade head` を実行するだけです。
- **デプロイ前に**: `SECRET_KEY` を固定し、`DATABASE_URL` を本物のデータベースに向けます。

## 次に学ぶこと

- [SQLModel による永続化](sqlmodel.md) — 同じドメインレイアウトで、非同期データアクセス、
  マイグレーション、汎用 CRUD に焦点を当てたチュートリアルです。
- [ドメイン指向プロジェクト](domain-starter.md) — このテンプレートの土台となるレイアウトです
  (認証の仕組みは含みません)。
- [どのスターターを選ぶべき?](../user-guide/choosing-a-starter.md) — このテンプレートを
  他のテンプレートと比較します。

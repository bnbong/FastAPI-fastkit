# 使用 `fastapi-auth-jwt` 实现 JWT 认证

构建一个从第一次提交起就拥有真实账户的 API。本教程会端到端走完 `fastapi-auth-jwt` 模板:令牌对如何签发与轮换、为什么被重放的刷新令牌会被拒绝、角色与作用域(scope)守卫如何接入,以及从 SQLite 迁移出去时需要改动什么。

## 您将学到的内容

- 使用 `fastkit startdemo fastapi-auth-jwt` 生成项目
- 访问令牌与刷新令牌的区别,以及轮换为何重要
- `get_current_user`、`get_current_active_superuser` 与 `require_scopes(...)` 如何保护路由
- 密码哈希在哪里进行,以及为什么使用 argon2id
- 从自带的 SQLite 文件迁移到配合 Alembic 的 PostgreSQL

## 前置条件

- Python 3.12+
- 已安装 FastAPI-fastkit(`pip install fastapi-fastkit`)
- 熟悉 FastAPI 依赖与 pydantic 模式

如果您从未构建过 FastAPI 应用,请先阅读 [构建基础 API 服务器](basic-api-server.md) 再回来 —— 本模板假定您已掌握基础知识。

## 第 1 步:生成项目

```console
$ fastkit startdemo fastapi-auth-jwt
Enter the project name: accounts-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Accounts and sessions service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

然后运行它:

```console
$ cd accounts-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

应用基于 SQLite(`sqlite:///./app.db`)启动,并在启动时创建数据表,因此无需事先安装或配置任何东西。文档位于 <http://127.0.0.1:8000/docs>。

!!! tip "提交前先预览"
    `fastkit startdemo fastapi-auth-jwt --dry-run` 会打印文件树和包列表,而不写入任何内容 —— 便于查看您即将得到什么。

## 第 2 步:生成的目录树

```
accounts-api/
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env                        # SECRET_KEY, DATABASE_URL, token lifetimes
├── scripts/
│   ├── format.sh  lint.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI() + lifespan + CORS + api_router
│       ├── core/
│       │   ├── config.py       # pydantic-settings
│       │   └── security.py     # argon2 hashing + JWT encode/decode
│       ├── db/session.py       # engine + get_session dependency
│       ├── api/
│       │   ├── router.py       # aggregates health + every domain router
│       │   ├── health.py       # GET /health
│       │   └── deps.py         # session, current user, role/scope guards
│       ├── domains/
│       │   ├── auth/           # login, refresh rotation, logout
│       │   └── users/          # registration and profiles
│       └── alembic/            # migration environment + versions/
└── tests/
    ├── conftest.py  test_health.py  test_auth.py  test_users.py
```

该布局采用 `domain-starter` 的结构:每个领域各自拥有 `router.py`(传输层)、`service.py`(业务逻辑)、`repository.py`(数据访问)、`models.py`(数据表)和 `schemas.py`(API 输入/输出)。认证相关的内容放在 `auth/`,账户相关的内容放在 `users/`,两者都不会深入对方的内部实现。

## 第 3 步:注册、登录并调用受保护的路由

```console
# 1. register
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
    -H 'Content-Type: application/json' \
    -d '{"email": "alice@example.com", "password": "s3cret-password"}'

# 2. log in — note the form encoding: this is the OAuth2 password flow
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
    -d 'username=alice@example.com&password=s3cret-password'
{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# 3. call a protected route
$ curl http://127.0.0.1:8000/api/v1/users/me \
    -H "Authorization: Bearer $ACCESS_TOKEN"
```

Swagger 的 "Authorize" 按钮驱动的是同一流程,因此您无需离开浏览器即可在 `/docs` 中调用受保护的路由。

完整的端点一览:

| 方法 | 端点                        | 认证        | 说明                              |
|--------|-----------------------------|-------------|-----------------------------------|
| GET    | `/api/v1/health`            | —           | 存活探针                          |
| POST   | `/api/v1/auth/register`     | —           | 创建账户                          |
| POST   | `/api/v1/auth/login`        | —           | OAuth2 密码表单 → 令牌对          |
| POST   | `/api/v1/auth/refresh`      | 刷新令牌    | 轮换为新的令牌对                  |
| POST   | `/api/v1/auth/logout`       | 刷新令牌    | 吊销一个刷新令牌                  |
| POST   | `/api/v1/auth/logout-all`   | 访问令牌    | 吊销该用户的所有会话              |
| GET    | `/api/v1/users/me`          | 访问令牌    | 当前用户的资料                    |
| PATCH  | `/api/v1/users/me`          | 访问令牌    | 更新当前用户的资料                |
| GET    | `/api/v1/users/me/scopes`   | 作用域 `me` | 受作用域限制的示例路由            |
| GET    | `/api/v1/users`             | 超级用户    | 受角色限制的用户列表              |

## 第 4 步:两个令牌,以及原因

登录会返回一个**令牌对**:

- **访问令牌**的有效期较短(`ACCESS_TOKEN_EXPIRE_MINUTES`,默认 30),随每个请求发送。由于有效期短,即使泄露也会很快失效。
- **刷新令牌**的有效期较长(`REFRESH_TOKEN_EXPIRE_DAYS`,默认 14),只用于一件事:获取新的令牌对。

以上并无特别之处。本模板与一般 JWT 代码片段的不同之处在于,刷新令牌会被**追踪并轮换**。每个签发的刷新令牌都带有 `jti` 声明,而该 `jti` 会被写入数据库:

```python
def issue_token_pair(self, user: User) -> TokenPair:
    scopes = user.scope_list
    access_token, _, _ = create_access_token(str(user.id), scopes)
    refresh_token, jti, expires_at = create_refresh_token(str(user.id), scopes)
    self.refresh_tokens.add(jti, user.id or 0, expires_at)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
```

刷新时,提交的令牌会在新令牌对签发**之前**被吊销:

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

动手试试:先刷新一次,然后再次发送*旧的*刷新令牌。

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → new pair

$ curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
    -H 'Content-Type: application/json' \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
# → 401: the token died the moment it was used
```

正是这一特性,让被盗的刷新令牌从一个永久后门变成了可被察觉的、只能使用一次的失败。

登出也以同样方式工作,这也是普通 JWT 配置通常做不到的另一件事:`POST /auth/logout` 吊销一个令牌,`POST /auth/logout-all` 吊销属于该用户的所有刷新令牌。

## 第 5 步:密码

哈希处理位于 `src/app/core/security.py`,通过 `pwdlib` 使用 **argon2id** —— 这是当前推荐的默认方案,而不是遗留的 bcrypt 配置。除了验证的那一刻,路由和服务中的任何代码都不会接触明文密码,`hashed_password` 也从不出现在任何响应模式中。

这里您无需配置任何东西。您*必须*配置的只有签名密钥。

## 第 6 步:角色与作用域

本模板以 FastAPI 依赖的形式提供了三个守卫:

```python
CurrentUser = Annotated[User, Depends(get_current_user)]
```

- **`get_current_user`** 解码 Bearer 访问令牌并加载用户,对未激活的账户返回 `403`。格式错误、已过期或指向已删除用户的令牌都会返回 `401`。
- **`get_current_active_superuser`** 在此之上叠加 `is_superuser` 检查。`GET /api/v1/users` 使用了它。
- **`require_scopes(...)`** 构建一个要求特定作用域的依赖:

```python
from fastapi import Depends
from src.app.api.deps import require_scopes

@router.get("/reports", dependencies=[Depends(require_scopes("reports"))])
def read_reports() -> list[str]:
    ...
```

作用域以逗号分隔字符串的形式存放在用户行上(`scopes: str`,通过 `scope_list` 属性读取),并会被复制到每个签发的令牌中。对于入门模板来说,这是刻意选择的最简单可行方案;当您的权限模型超出一个字符串的承载能力时,可以用角色表替换该列,同时保持依赖签名不变 —— 路由中的任何代码都无需改动。

## 第 7 步:添加受保护的领域

例如,要添加一个只有已登录用户才能访问的 `orders` 领域:

1. 参照 `users/` 创建 `src/app/domains/orders/`(`models.py`、`schemas.py`、`repository.py`、`service.py`、`router.py`)。
2. 在需要账户的路由中以参数形式接收 `CurrentUser`,或者为路由器附加 `Depends(require_scopes("orders"))`。
3. 在 `src/app/api/router.py` 中、`# fastkit:routes` 锚点之上注册路由器。`fastkit addroute` 会写入同样的锚点,因此手写的路由与生成的路由会保持在同一处。
4. 生成迁移:`alembic revision --autogenerate -m "add orders"`。
5. 参照 `tests/test_users.py` 为新端点编写测试。

## 第 8 步:现在用 SQLite,以后用 PostgreSQL

默认的 `DATABASE_URL` 是一个本地 SQLite 文件,应用会在启动时调用 `create_db_and_tables()`,这正是 `pytest` 和 `uvicorn` 无需任何配置即可运行的原因。对于本地开发以外的场景,请改由 Alembic 管理数据库模式:

```console
$ export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/app_db'
$ alembic upgrade head
```

修改模型之后:

```console
$ alembic revision --autogenerate -m "add profile fields"
```

## 第 9 步:部署之前

`.env` 中的两个设置决定了这是一个演示还是一个真正的服务:

- **`SECRET_KEY`** 为每个令牌签名。如果不设置,每个进程都会生成一个随机密钥 —— 这会导致每次重启都让所有人登出,并让多个 worker 对哪些令牌有效产生分歧。请生成一个并固定下来:

  ```console
  $ python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

- **`DATABASE_URL`** 选择数据库。默认的 SQLite 不适合作为生产存储。

还可以选择设置 `FIRST_SUPERUSER_EMAIL` 和 `FIRST_SUPERUSER_PASSWORD`,以便在启动时创建一个超级用户;并将 `BACKEND_CORS_ORIGINS` 设置为以逗号分隔的前端源列表。

## 第 10 步:测试

```console
$ bash scripts/test.sh    # or: pytest
```

测试套件使用 `httpx.AsyncClient` 针对内存中的 SQLite 数据库运行,覆盖了完整的正常路径 —— 注册 → 登录 → me → 刷新 → 登出 —— 以及真正重要的拒绝路径:错误密码、格式错误的令牌、过期令牌,以及第 4 步中被重放的刷新令牌。当您扩展认证规则时,请先扩展这些拒绝测试;能够发现守卫失效的正是它们。

## 回顾

- **生成**:`fastkit startdemo fastapi-auth-jwt` → `bash scripts/run-server.sh` → 在 `/docs` 查看文档。
- **令牌**:短期访问令牌用于请求,轮换式刷新令牌通过 `jti` 追踪,从而让重放失败、让登出真正生效。
- **守卫**:`get_current_user`、`get_current_active_superuser` 与 `require_scopes(...)` 都是普通的依赖。
- **存储**:SQLite 开箱即用;设置 `DATABASE_URL` 并运行 `alembic upgrade head` 即可使用 PostgreSQL。
- **部署之前**:固定 `SECRET_KEY`,并将 `DATABASE_URL` 指向真正的数据库。

## 接下来去哪里

- [SQLModel 持久化](sqlmodel.md) —— 同样的领域布局,侧重于异步数据访问、迁移与通用 CRUD。
- [领域驱动项目](domain-starter.md) —— 本模板所基于的布局,不含认证机制。
- [应该选择哪个 starter?](../user-guide/choosing-a-starter.md) —— 本模板与其他 starter 的对比。

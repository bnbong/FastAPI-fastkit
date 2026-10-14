# 使用 `fastapi-sqlmodel` 实现异步持久化

构建一个由数据库支撑、且每个概念只定义**一次**的 API。SQLModel 类同时是 SQLAlchemy 数据表和 pydantic 模式,因此添加一列并不意味着要修改四个文件。本教程会走完 `fastapi-sqlmodel` 模板:模型层级、通用 CRUD 基类、分页响应、异步 Alembic 迁移,以及如何添加您自己的领域。

## 您将学到的内容

- 使用 `fastkit startdemo fastapi-sqlmodel` 生成项目
- `ItemBase` → `Item` / `ItemCreate` / `ItemUpdate` / `ItemPublic` 如何消除模式重复
- `CRUDBase` 免费提供了什么,以及在哪里扩展它
- `Page[T]` 列表封装,以及其限制在哪里被强制执行
- 运行异步 Alembic 迁移,并从 SQLite 切换到 PostgreSQL

## 前置条件

- Python 3.12+
- 已安装 FastAPI-fastkit(`pip install fastapi-fastkit`)
- 熟悉 `async`/`await` 以及基本的 SQL 概念

如果您想要的是同步的、基于 Compose 的 PostgreSQL 技术栈,请参阅使用 `fastapi-psql-orm` 的 [数据库集成](database-integration.md)。

## 第 1 步:生成并运行

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
$ bash scripts/run-server.sh     # or: uvicorn src.app.main:app --reload
```

默认的 `DATABASE_URL` 是 `sqlite+aiosqlite:///./app.db`,因此无需安装数据库服务器。文档位于 <http://127.0.0.1:8000/docs>。

## 第 2 步:生成的目录树

```
catalog-api/
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── .env
├── scripts/
│   ├── format.sh  lint.sh  migrate.sh  run-server.sh  test.sh
├── src/
│   └── app/
│       ├── main.py             # FastAPI app + lifespan
│       ├── core/config.py      # pydantic-settings
│       ├── db/
│       │   ├── session.py      # async engine, get_session dependency
│       │   └── base.py         # metadata aggregation for Alembic
│       ├── crud/
│       │   ├── base.py         # generic CRUDBase
│       │   └── pagination.py   # Page[T] envelope
│       ├── alembic/
│       │   ├── env.py          # async migration environment
│       │   └── versions/0001_create_items_table.py
│       ├── api/
│       │   ├── router.py       # aggregates health + domain routers
│       │   └── health.py       # GET /health
│       └── domains/items/      # the example domain
│           ├── models.py       # Item table + Create/Update/Public schemas
│           ├── crud.py         # ItemCRUD(CRUDBase)
│           └── router.py       # FastAPI router
└── tests/
    ├── conftest.py  test_health.py  test_items.py  test_crud_base.py
```

请注意领域文件夹中*没有*的东西:没有独立于 `models.py` 的 `schemas.py`,也没有每个领域各自的 repository 样板代码。两者分别被 SQLModel 和 `CRUDBase` 吸收了。

## 第 3 步:每个概念一个模型定义

打开 `src/app/domains/items/models.py`。所有内容都派生自同一个基类:

```python
class ItemBase(SQLModel):
    """Fields shared by the table and every request/response schema."""
    name: str = Field(min_length=1, max_length=128, index=True)
    description: str | None = Field(default=None, max_length=512)
    price: float = Field(ge=0)
    in_stock: bool = True


class Item(ItemBase, table=True):        # the actual table
    __tablename__ = "items"
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utcnow)


class ItemCreate(ItemBase): ...          # POST body — no server-assigned fields


class ItemUpdate(SQLModel):              # PATCH body — every field optional
    name: str | None = Field(default=None, min_length=1, max_length=128)
    ...


class ItemPublic(ItemBase):              # response — base + server-assigned
    id: int
    created_at: datetime
```

四个类,四种不同的职责,字段只存在于一处:

| 类           | 角色                          | 为什么要单独定义 |
|--------------|-------------------------------|-------------------|
| `ItemBase`   | 共享的字段定义                | 唯一的事实来源 |
| `Item`       | 数据库表                      | 添加 `id`、`created_at` |
| `ItemCreate` | `POST` 的请求体               | 不得接受 `id` |
| `ItemUpdate` | `PATCH` 的请求体              | 所有字段均为可选 |
| `ItemPublic` | 响应体                        | 暴露由服务器分配的字段 |

**收益:**添加一个 `sku` 列只需在 `ItemBase` 中加一行。数据表获得该列,创建请求体接受它,响应返回它 —— 无需任何其他修改。`ItemUpdate` 则刻意保持显式:部分更新的语义是一项决策,而不是一种推导。

## 第 4 步:无需重写的 CRUD

`src/app/crud/base.py` 是一个以表模型及其两个输入模式为参数的泛型类:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    async def get(self, session, obj_id) -> ModelType | None: ...
    async def list(self, session, *, offset=0, limit=20) -> Sequence[ModelType]: ...
    async def count(self, session) -> int: ...
    async def create(self, session, obj_in) -> ModelType: ...
    async def update(self, session, db_obj, obj_in) -> ModelType: ...
    async def delete(self, session, db_obj) -> None: ...
```

有一个细节值得牢记 —— `update` 使用了 `exclude_unset=True`:

```python
changes: dict[str, Any] = obj_in.model_dump(exclude_unset=True)
```

正是这一点让 `PATCH` 真正成为部分更新。客户端没有发送的字段不会出现在字典中,因此永远不会被写入;如果没有 `exclude_unset`,`PATCH` 会悄无声息地用模式默认值覆盖未触及的列。

领域只需继承基类,并只添加它特有的部分:

```python
class ItemCRUD(CRUDBase[Item, ItemCreate, ItemUpdate]):
    """CRUD for Item, extended with a name search."""

    async def search_by_name(self, session, term, *, limit=20):
        statement = select(Item).where(Item.name.like(f"%{term}%")).limit(limit)
        result = await session.exec(statement)
        return result.all()


item_crud = ItemCRUD(Item)
```

## 第 5 步:分页列表

列表端点返回的是 `Page[T]` 封装,而不是裸数组:

```json
{"items": [...], "total": 42, "offset": 0, "limit": 20}
```

限制值的截断发生在路由中,而不是客户端:

```python
limit: int = Query(default=settings.DEFAULT_PAGE_LIMIT, ge=1)
...
limit = min(limit, settings.MAX_PAGE_LIMIT)
```

因此 `?limit=100000` 无法把一次请求变成全表扫描。`Page` 还提供一个由 `offset`、`len(items)` 和 `total` 推导出的 `has_next` 属性,这通常正是前端真正需要的。

items 领域自带的端点:

| 方法 | 端点                      | 说明                           |
|--------|---------------------------|--------------------------------|
| GET    | `/api/v1/health`          | 存活探针                       |
| GET    | `/api/v1/items`           | 列出项目(`offset`、`limit`)   |
| GET    | `/api/v1/items/{item_id}` | 读取单个项目                   |
| POST   | `/api/v1/items`           | 创建项目(`201`)               |
| PATCH  | `/api/v1/items/{item_id}` | 部分更新项目                   |
| DELETE | `/api/v1/items/{item_id}` | 删除项目(`204`)               |

动手试试:

```console
$ curl -X POST http://127.0.0.1:8000/api/v1/items \
    -H 'Content-Type: application/json' \
    -d '{"name": "Keyboard", "price": 89.0}'

$ curl 'http://127.0.0.1:8000/api/v1/items?offset=0&limit=5'
```

## 第 6 步:从头到尾都是异步

`src/app/db/session.py` 为每个进程构建一个 `AsyncEngine`,并分发请求作用域的会话:

```python
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
```

路由依赖它(`session: AsyncSession = Depends(get_session)`),`CRUDBase` 将它作为第一个参数,每个数据库调用都会被 await。请求路径中没有任何代码会因 I/O 阻塞事件循环。

`create_db_and_tables()` 也位于这里,并由应用的 `lifespan` 调用。它是为默认的 SQLite 和测试提供的便利功能 —— 一旦由 Alembic 管理数据库模式,请设置 `CREATE_TABLES_ON_STARTUP=false`。

## 第 7 步:添加领域

1. 参照 `items` 创建 `src/app/domains/<your_domain>/`(`models.py`、`crud.py`、`router.py`)。
2. **在 `src/app/db/base.py` 中导入表模型。**这一步很容易忘记,调试起来也很令人困惑:Alembic 自动生成和 `create_db_and_tables` 只能看到已被导入的模型,因此缺少导入时表现为一个空迁移,而不是报错。
3. 在 `src/app/api/router.py` 中注册路由器。`# fastkit:imports` 和 `# fastkit:routes` 锚点标记了 `fastkit addroute` 插入代码的位置 —— 请把您的代码放在同样的地方。
4. 生成迁移:`alembic revision --autogenerate -m "add <domain>"`。
5. 参照 `tests/test_items.py` 添加 `tests/test_<your_domain>.py`。

## 第 8 步:迁移与 PostgreSQL

`src/app/alembic/env.py` 下的 Alembic 环境是异步的,因此它与应用使用同一套驱动栈运行。日常使用:

```console
$ bash scripts/migrate.sh                                  # upgrade head
$ alembic revision --autogenerate -m "add sku to items"    # after a model change
```

切换数据库只需修改 URL 并添加一个驱动:

```console
$ uv pip install "asyncpg>=0.31.0"
$ export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/app"
$ bash scripts/migrate.sh
```

模型、CRUD 和路由都无需改动 —— 这正是把驱动隐藏在 `create_engine` 之后的意义所在。

## 第 9 步:测试

```console
$ bash scripts/test.sh    # or: pytest
```

每个测试都针对一个全新的内存 SQLite 数据库运行:无需迁移,无需 fixture 文件,测试之间也无需清理。`test_crud_base.py` 直接测试通用基类 —— 在扩展它之前值得一读,因为它记录了 `exclude_unset` 的行为以及您自己的领域所继承的 count/offset 契约。

## 回顾

- **生成**:`fastkit startdemo fastapi-sqlmodel` → `bash scripts/migrate.sh` → `bash scripts/run-server.sh`。
- **模型**:`ItemBase` 持有字段;数据表与输入/输出模式都派生自它,因此新列只需声明一次。
- **CRUD**:`CRUDBase` 提供 get / list / count / create / update / delete;领域通过继承它来添加自己的查询。
- **列表**:`Page[T]` 封装,并在服务器端截断限制值。
- **模式**:异步 Alembic;记得在 `src/app/db/base.py` 中导入新模型。
- **数据库**:默认使用 SQLite;修改 `DATABASE_URL` 并安装 `asyncpg` 即可使用 PostgreSQL。

## 接下来去哪里

- [JWT 认证](auth-jwt.md) —— 在这个数据层之前加上账户与受保护的路由。
- [领域驱动项目](domain-starter.md) —— 两个模板共享的布局,不含数据库。
- [应该选择哪个 starter?](../user-guide/choosing-a-starter.md)

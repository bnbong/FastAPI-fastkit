# 使用 `fastapi-domain-starter` 构建面向领域的 FastAPI

按推荐的现代布局构建一个中型 FastAPI 服务 —— **每个业务概念在 `src/app/domains/` 下对应一个文件夹**。本教程会端到端走完 `fastapi-domain-starter` 模板:如何生成、每个顶层包的职责、自带的 `items` 示例如何接入,以及如何添加下一个领域。

## 您将学到的内容

- 使用 `fastkit startdemo fastapi-domain-starter` 生成项目
- 布局中 `core`、`db`、`domains`、`tests` 各自的角色
- 一个领域如何拆分为 router → service → repository → schemas → models
- 添加新领域的契约(复制 items 文件夹,注册路由)
- 自带的 `/health` 端点与 `/api/v1/items` CRUD 如何接入应用

## 前置条件

- Python 3.12+
- 已安装 FastAPI-fastkit(`pip install fastapi-fastkit`)
- 熟悉 FastAPI 的基础概念(路径操作、pydantic 模式、依赖)

如果这是您的第一个 FastAPI 项目,请先从 [构建基础 API 服务器](basic-api-server.md) 开始 —— 那篇教程使用更简单的 `fastapi-default` 模板。

## 第 1 步:生成项目

```console
$ fastkit startdemo fastapi-domain-starter
Enter the project name: orders-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: Domain-oriented orders service
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
```

`fastkit` 会部署模板、填入占位符、创建虚拟环境并安装依赖。完成后即可进入项目:

```console
$ cd orders-api
$ bash scripts/run-server.sh    # or: uvicorn src.app.main:app --reload
```

随后可在 <http://127.0.0.1:8000/docs> 查看 API 文档。

## 第 2 步:生成的目录树

```
orders-api/
├── README.md
├── pyproject.toml              # PEP 621 metadata + [tool.fastapi-fastkit]
├── requirements.txt            # pinned deps (template ships both files; you maintain them as you add packages)
├── .env                        # SECRET_KEY, ENVIRONMENT
├── .gitignore
├── scripts/
│   ├── format.sh               # black + isort
│   ├── lint.sh                 # black --check + isort --check + mypy
│   ├── run-server.sh           # uvicorn src.app.main:app --reload
│   └── test.sh                 # pytest
├── src/
│   ├── __init__.py
│   └── app/                    # the application package
│       ├── __init__.py
│       ├── main.py             # FastAPI() + middleware + api_router include
│       ├── core/               # cross-cutting configuration
│       │   ├── __init__.py
│       │   └── config.py       # pydantic-settings (PROJECT_NAME, CORS, ...)
│       ├── db/                 # persistence abstractions
│       │   ├── __init__.py
│       │   └── memory.py       # InMemoryStore[T] generic key-value store
│       ├── api/                # transport-level routing
│       │   ├── __init__.py
│       │   ├── health.py       # GET /health
│       │   └── router.py       # aggregates health + every domain router
│       └── domains/            # business concepts (one folder each)
│           ├── __init__.py
│           └── items/          # the example domain
│               ├── __init__.py
│               ├── models.py       # @dataclass Item (entity)
│               ├── schemas.py      # ItemCreate, ItemRead (pydantic)
│               ├── repository.py   # ItemRepository over InMemoryStore
│               ├── service.py      # ItemService + ItemNotFoundError
│               └── router.py       # APIRouter(prefix="/items")
└── tests/
    ├── __init__.py
    ├── conftest.py             # TestClient fixture, store reset
    ├── test_health.py
    └── test_items.py
```

需要内化的两个概念:

1. **`src/app/`** 是 **应用包** —— 运行时导入的所有内容都在这里。测试也从这里导入(`from src.app.main import app`)。外层 `src/` 是为了让项目能 `pip install`。
2. **`src/app/domains/<concept>/`** 是 **每个概念的切片** —— 每个业务概念(items、orders、users……)拥有各自的 router / service / repository / schemas / models,且仅有这些。

## 第 3 步:每个顶层包的职责

### `src/app/core/` —— 配置

存放跨切面的应用配置。自带的 `config.py` 暴露一个 pydantic-settings 的 `Settings` 类,从 `.env` / 环境变量读取:

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

`main.py` 读取 `settings.PROJECT_NAME`、`settings.API_V1_PREFIX` 与 `settings.all_cors_origins` 来接入 FastAPI 应用。

**什么时候应往 `core/` 添加内容:** 任何与单个领域无关的内容 —— 全局设置、结构化日志、自定义中间件、安全工具等。

### `src/app/db/` —— 持久化边界

存放对数据存储的抽象。starter 自带 `memory.py` —— 一个进程内的 `InMemoryStore[T]`,对实体类型进行了泛化。每个领域的 repository 都封装一个 `InMemoryStore`,后续切换到 SQLAlchemy / 异步驱动也只是一次受控的变更:只需要重写 repository。

```python
class InMemoryStore(Generic[T]):
    def list(self) -> Iterable[T]: ...
    def get(self, id_: int) -> Optional[T]: ...
    def add(self, item: T) -> int: ...
    def replace(self, id_: int, item: T) -> bool: ...
    def delete(self, id_: int) -> bool: ...
    def clear(self) -> None: ...
```

**什么时候应扩展 `db/`:** 当您从 `InMemoryStore` 迁移走时,加上一个 `session.py`,放真实数据库的 session 工厂。保留同样的公共方法形状(`list` / `get` / `add` / ……),这样领域的 repository 不必修改其内部契约。

### `src/app/api/` —— 传输层路由

由两部分组成:

- `health.py` —— 一个小的 `APIRouter`,暴露 `GET /health` 并返回 `{"status": "ok"}`。无副作用,适合做存活探针。
- `router.py` —— **顶层聚合器**。它纳入健康检查路由器以及每个领域的路由器,再把这个合并后的 `api_router` 挂载在 FastAPI 应用的 `/api/v1` 下:

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

**为何要在这里聚合:** 添加新领域时,只需要编辑 `src/app/api/router.py` 来注册它的路由器,`main.py` 从不需要改动。

### `src/app/domains/<concept>/` —— 业务切片

随着项目成长,大多数代码会落在这里。每个领域拥有五个文件:

| 文件 | 角色 |
|---|---|
| `models.py` | 领域实体(starter 中是 `@dataclass`;以后可以换成 SQLAlchemy / SQLModel)。表示内部形状 —— 并非线上格式。 |
| `schemas.py` | API 输入输出模式(pydantic)。与实体分离,这样线上格式可以独立演进而不影响领域逻辑。 |
| `repository.py` | 数据访问层。用领域实体类型的方法封装存储,是切换持久化方案的接缝。 |
| `service.py` | 业务逻辑。Router 调用 `service`,绝不直接调用 `repository`。领域专属异常(如 `ItemNotFoundError`)放在这里。 |
| `router.py` | HTTP 传输。负责在 pydantic 模式 ↔ service 调用之间翻译,把领域异常转换为 `HTTPException`。 |

**依赖方向**是 `router → service → repository → store`。每层只依赖其下一层。Schema 由 router 与 service 引用;model 由 repository 与 service 引用。

### `tests/`

镜像运行时布局 —— 对每个值得固定行为的对外面都对应一个测试模块。starter 自带:

- `conftest.py` —— autouse fixture,在测试之间重置 items 存储;另外一个 `client` fixture 封装了 `TestClient(app)`。
- `test_health.py` —— 验证 `GET /api/v1/health` 返回 200 + `{"status": "ok"}`。
- `test_items.py` —— 对 items 端点做完整 CRUD 覆盖,包括对未知 id 返回 404、对无效负载返回 422。

运行测试:

```console
$ bash scripts/test.sh         # or: pytest
```

## 第 4 步:走读自带的 `items` 领域

这个示例领域是一个针对极小实体的 CRUD:

```python
# src/app/domains/items/models.py
@dataclass
class Item:
    id: int
    name: str
    price: float
    in_stock: bool = True
```

API 模式把输入形状与输出形状分开,这样可以加入服务端控制的字段(`id`)与校验(price ≥ 0):

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

Repository 封装内存存储,并在插入时分配 id:

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
    # list_all / get / replace / delete / reset elided
```

Service 层用于沉淀业务规则。现在它只是带一个自定义异常的薄包装,但未来的业务策略会落在这里(比如「不能删除已存在于未关闭订单中的商品」):

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
    # list_items / create_item / replace_item / delete_item elided
```

Router 是唯一了解 HTTP 的那一层。注意它通过 FastAPI 的 `Depends(...)` 接收 service,以便测试中覆盖;并把 `ItemNotFoundError` 映射成 `HTTPException(404)`:

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

完整的 router 暴露:

| 方法 | 路径 | 作用 |
|---|---|---|
| `GET` | `/api/v1/items` | 列出 item |
| `GET` | `/api/v1/items/{item_id}` | 读取单个 |
| `POST` | `/api/v1/items` | 创建(返回 201) |
| `PUT` | `/api/v1/items/{item_id}` | 替换 |
| `DELETE` | `/api/v1/items/{item_id}` | 删除(返回 204) |
| `GET` | `/api/v1/health` | 存活探针 |

试一下:

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

## 第 5 步:添加下一个领域

starter 的设计目标是**让添加领域变成一次复制 + 改名操作**。假设您想在 `items` 之外加一个 `users` 领域:

### 1. 复制 `items/` 文件夹

```console
$ cp -r src/app/domains/items src/app/domains/users
```

### 2. 重写实体、模式以及各文件中的类名

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
    # Plain ``str`` keeps the snippet drop-in safe. To use pydantic's
    # built-in email validation instead, install the optional dependency
    # (``pip install 'pydantic[email]'`` — pulls in ``email-validator``)
    # and switch ``str`` to ``EmailStr``.
    email: str = Field(min_length=3, max_length=320)
    is_active: bool = True

class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)
```

在 `models.py`、`schemas.py`、`repository.py`、`service.py` 与 `router.py` 中把 `Item → User`、`ItemNotFoundError → UserNotFoundError`、`ItemRepository → UserRepository`、`ItemService → UserService` 全部改名。别忘了 router 中的 `prefix="/items"` → `prefix="/users"`,以及 `tags=["items"]` → `tags=["users"]`。

Repository 仍可保留同样的 `InMemoryStore` 模式 —— 它本身就是基于实体类型的泛型:

```python
# src/app/domains/users/repository.py
_store: InMemoryStore[User] = InMemoryStore()

class UserRepository:
    def __init__(self, store: Optional[InMemoryStore[User]] = None) -> None:
        self._store = store if store is not None else _store
    # ... same shape as ItemRepository ...
```

### 3. 更新领域的 `__init__.py`

items 领域会重新导出其模块,以便调用方可以写 `from src.app.domains.items import service`。对 users 也照样做:

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

### 4. 在聚合器中注册路由

这是 **`domains/users/` 之外您唯一需要修改的文件**:

```python
# src/app/api/router.py
from src.app.api import health
from src.app.domains.items import router as items_router
from src.app.domains.users import router as users_router  # ← add

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(items_router.router)
api_router.include_router(users_router.router)             # ← add
```

重启服务器后,您会在 `/docs` 中看到挂载好的 `/api/v1/users`。

### 5. 添加测试

把 `tests/test_items.py` 镜像成 `tests/test_users.py` —— 同样基于 client 的结构,只是请求新端点。`conftest.py` 中 autouse 的存储重置 fixture 已经能保证每个测试的隔离。

如果第二个领域也使用 `InMemoryStore`,可以扩展该 fixture 让它也重置该存储,或者每个领域各保留一个 fixture。

## 第 6 步:接下来去哪里

- [架构预设矩阵](../reference/preset-feature-matrix.md) 展示了 `fastkit init --interactive` 对每种预设会生成什么,包括 `domain-starter` 下哪些功能选择需要手动接入。
- [`fastapi-default` 教程](basic-api-server.md) 介绍了分层备选方案,如果您想在选定之前比较一下布局,这里很有帮助。
- 对于数据库集成,[数据库集成教程](database-integration.md) 展示了 PostgreSQL + SQLAlchemy + Alembic 的模式。同样的思路可以套用到 `src/app/db/` 与各领域的 `repository.py`。

## 回顾

- **生成**:`fastkit startdemo fastapi-domain-starter` → `bash scripts/run-server.sh` → 在 `/docs` 查看文档。
- **布局**:`core/` 放配置,`db/` 放持久化抽象,`domains/<concept>/` 放业务切片,`api/router.py` 作为唯一聚合点,`tests/` 镜像运行时模块。
- **添加领域**:复制 `items/`,改实体 / 模式 / 类名,更新 `__init__.py` 的重新导出,在 `src/app/api/router.py` 注册路由,新增测试模块。`main.py` 完全不需要改动。

# 使用 `fastapi-domain-starter` 构建面向领域的 FastAPI

按推荐的现代布局构建一个中型 FastAPI 服务 —— **每个业务概念在 `src/app/domains/` 下对应一个文件夹**。本教程会端到端走完 `fastapi-domain-starter` 模板:如何生成、每个顶层包的职责、自带的 `items` 示例如何接入,以及如何添加下一个领域。

## 您将学到的内容

- 使用 `fastkit startdemo fastapi-domain-starter` 生成项目
- 布局中 `core`、`db`、`domains`、`tests` 各自的角色
- 一个领域如何拆分为 router → service → repository → schemas → models
- 使用 `fastkit addroute` 添加新领域,并在测试中隔离其存储
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
│               └── router.py       # APIRouter endpoints
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
api_router.include_router(items_router.router, prefix="/items", tags=["items"])
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

- `conftest.py` —— autouse fixture,在测试之间重置 items 存储,并对生成的领域调用 `service.reset_store()`;另外一个 `client` fixture 封装了 `TestClient(app)`。
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
router = APIRouter()

def get_item_service() -> ItemService:
    return ItemService()

@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: int, service: ItemService = Depends(get_item_service)) -> ItemRead:
    try:
        return ItemRead.model_validate(service.get_item(item_id))
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
```

共享的 API 路由器负责设置领域的前缀与标签:

```python
# src/app/api/router.py
api_router.include_router(items_router.router, prefix="/items", tags=["items"])
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

在生成项目的根目录下,添加一个 `users` 领域:

```console
$ fastkit addroute users
```

该命令读取 `[tool.fastapi-fastkit].preset`;当 `preset` 不存在时,会根据 `template` 推断。因此,通过 `startdemo`、交互式 `init` 或 `init --config` 创建的项目会为 domain-starter 选择 domain 布局。所选布局会在确认之前显示出来。您也可以显式指定:

```console
$ fastkit addroute users . --layout=domain
```

`--layout=classic-layer` 会生成传统的 `api/routes`、`crud` 与 `schemas` 结构。对于 `classic-layered`、`minimal`、`single-module` 以及没有 preset 或 template 元数据的项目,这也是默认值。未知的 preset 会回退到 `classic-layer` 并给出警告。该选项不会改变项目的 preset。

### 生成的领域

```text
src/app/domains/users/
├── __init__.py
├── models.py       # Users with id and name
├── schemas.py      # UsersCreate and UsersRead
├── repository.py   # UsersRepository: typed, in-memory CRUD
├── service.py      # UsersService and UsersNotFoundError
└── router.py       # endpoints and get_users_service dependency
```

新领域使用由路由名称派生的 PascalCase 类名,因此无需从 `users` 推断单数形式。请根据您的业务概念所需的字段与行为来定制这些文件。

路由器会自动注册到 `src/app/api/router.py`,并带有 `prefix="/users"` 与 `tags=["users"]`。领域路由器本身使用不带这些设置的 `APIRouter()`。应用已有的前缀保持不变,暴露以下端点:

| 方法 | 端点 | 结果 |
|--------|----------|--------|
| GET | `/api/v1/users` | 列出实体,200 |
| GET | `/api/v1/users/{entity_id}` | 读取实体,200 或 404 |
| POST | `/api/v1/users` | 创建实体,201 |
| PUT | `/api/v1/users/{entity_id}` | 替换实体,200 或 404 |
| DELETE | `/api/v1/users/{entity_id}` | 删除实体,空的 204 或 404 |

POST 与 PUT 接受 `{"name": "Alice"}`;`name` 的长度必须为 1–120 个字符。Repository 从 1 开始分配 ID,PUT 会保留该 ID。不会生成 PATCH 端点。

新的 repository 是自包含的;它不使用自带 items 领域的 `db.memory` 存储。每个显式创建的 repository 实例都有独立的存储,而默认实例在该领域与该进程内的请求之间共享。CRUD 操作受锁保护。数据会在重启后丢失,且不会在 worker 进程之间共享;需要持久化存储时,请替换该 repository。

### 添加隔离的测试

items 专用的重置 fixture 不会重置新领域。请为每个测试用一个全新的 repository 覆盖其 service 依赖:

```python
from src.app.domains.users.repository import UsersRepository
from src.app.domains.users.router import get_users_service
from src.app.domains.users.service import UsersService

def test_create_user(client):
    from src.app.main import app

    service = UsersService(repository=UsersRepository())
    app.dependency_overrides[get_users_service] = lambda: service
    try:
        response = client.post("/api/v1/users", json={"name": "Alice"})
        assert response.status_code == 201
        assert response.json() == {"id": 1, "name": "Alice"}
    finally:
        app.dependency_overrides.pop(get_users_service, None)
```

重新运行 `addroute` 会保留已有的领域文件、创建缺失的文件,并避免重复的导入与注册。同名的 classic 模块可以通过导入别名共存。生成的包会重新导出其模块,repository 提供 `reset()` 用于清空数据并重新从头分配 ID。starter 的 autouse fixture 会对生成的领域调用 `service.reset_store()`。在较旧的项目中,请把这一调用加入已有的重置 fixture,或通过依赖覆盖使用隔离的 repository。组合路由器时,请自行检查 HTTP 路径与方法;生成器不会检测重叠的端点。

## 第 6 步:接下来去哪里

- [架构预设矩阵](../reference/preset-feature-matrix.md) 展示了 `fastkit init --interactive` 对每种预设会生成什么,包括 `domain-starter` 下哪些功能选择需要手动接入。
- [`fastapi-default` 教程](basic-api-server.md) 介绍了分层备选方案,如果您想在选定之前比较一下布局,这里很有帮助。
- 对于数据库集成,[数据库集成教程](database-integration.md) 展示了 PostgreSQL + SQLAlchemy + Alembic 的模式。同样的思路可以套用到 `src/app/db/` 与各领域的 `repository.py`。

## 回顾

- **生成**:`fastkit startdemo fastapi-domain-starter` → `bash scripts/run-server.sh` → 在 `/docs` 查看文档。
- **布局**:`core/` 放配置,`db/` 放持久化抽象,`domains/<concept>/` 放业务切片,`api/router.py` 作为唯一聚合点,`tests/` 镜像运行时模块。
- **添加领域**:运行 `fastkit addroute users`,定制生成的 `Users*` CRUD 脚手架,并使用隔离的 repository 添加测试。路由器会自动注册。

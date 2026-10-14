# CLI 参考

FastAPI-fastkit 命令行接口的完整命令参考。

## 全局选项

所有命令都支持以下全局选项：

```console
$ fastkit [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### 全局选项

| 选项 | 描述 |
|--------|-------------|
| `--version` | 显示 FastAPI-fastkit 版本 |
| `--help` | 显示帮助信息 |

### 示例

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0

$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## 命令

### `init`

通过交互式流程创建一个新的 FastAPI 项目。

#### 语法

```console
$ fastkit init [OPTIONS]
```

#### 选项

| 选项 | 描述 | 默认值 |
|--------|-------------|---------|
| `--interactive` | 引导式设置:先选择架构预设,再选择功能 | off |
| `--config <path>` | 根据已保存的配置文件创建项目,不进行任何提示 | - |
| `--save-config <path>` | 与 `--interactive` 一起使用,将回答完成的配置写入此路径 | - |
| `--project-name` | 项目名称(省略时会提示输入) | - |
| `--author` | 作者名称(省略时会提示输入) | - |
| `--author-email` | 作者邮箱(省略时会提示输入) | - |
| `--description` | 项目描述(省略时会提示输入) | - |
| `--package-manager` | 要使用的包管理器(pip、uv、pdm、poetry) | uv |
| `--dry-run` | 显示将要创建的文件和包,但不写入任何内容 | off |
| `--no-venv` | 跳过虚拟环境创建(隐含 `--no-install`) | off |
| `--no-install` | 跳过依赖安装 | off |
| `--yes` / `-y` | 在原地部署项目时,覆盖已有文件之前不再询问确认 | off |
| `--help` | 显示命令帮助 | - |

#### 配置文件(`--config` / `--save-config`)

交互式会话的回答是一个普通的映射,而这个映射可以通过文件传递。这使得项目创建变成了可以提交、审查和重放的东西。

```console
# 记录一次交互式会话
$ fastkit init --interactive --save-config fastkit.config.json

# 之后重放它,完全不进行提示
$ fastkit init --config fastkit.config.json
```

如果您没有传入 `--save-config`,一次走到最后的交互式运行会询问是否保存所选内容以及保存位置。该提示只会在有人坐在终端前时出现 —— 通过管道或在 CI 中运行时保持静默,改为通过该选项显式开启。

**支持的格式**根据文件扩展名选择:

| 扩展名 | 可用性 |
|---|---|
| `.json` | 始终可用(标准库) |
| `.toml` | 始终可用(标准库) |
| `.yaml` / `.yml` | 仅在安装了 PyYAML 时可用 —— fastkit 不会将其作为运行时依赖添加 |

加载的文件顶层必须是一个映射,且至少包含 `project_name`、`author` 和 `author_email`。随后它会按照交互式提示所用的相同规则进行校验(项目名称格式、邮箱格式、`all_dependencies` 必须是列表),并在写入任何内容之前报告所有问题。只列出功能选择而没有 `all_dependencies` 的文件,会通过交互式构建器展开,因此手写的配置与向导会话会解析出相同的包集合。

一个最小示例:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv"
}
```

#### 配置文件模式

每个配置文件 —— 无论是手写的还是由 `--save-config` 生成的 —— 在到达生成器之前都会经过同一个规范化器(`backend/project_builder/config_schema.py` 中的 `normalize_project_config`)。未知的键、已知维度上的未知选项,或类型错误的值都会被拒绝,并给出出错的名称以及实际允许的值列表,而不是被悄悄忽略。

| 键 | 形式 | 说明 |
|---|---|---|
| `project_name`, `author`, `author_email` | 字符串 | 必填 |
| `description` | 字符串 | 必填 |
| `architecture_preset`(别名 `preset`) | `"minimal"` \| `"single-module"` \| `"classic-layered"` \| `"domain-starter"` | 如果两种写法同时出现,它们必须一致 |
| `package_manager` | `"pip"` \| `"uv"` \| `"pdm"` \| `"poetry"` | |
| `database` | 字符串,或 `{"type": <choice>}` | `PostgreSQL`、`MySQL`、`MongoDB`、`Redis`、`SQLite`、`None` |
| `authentication`, `async_tasks`, `testing`, `caching`, `monitoring`, `migrations`, `logging` | 字符串,或 `{"type": <choice>}` | 单选维度 —— 各维度的选项请参阅上文的[功能目录](#interactive-builder-feature-catalog-interactive) |
| `utilities`, `tooling` | 字符串列表 | 多选维度 —— 选项见同一目录 |
| `deployment` | 字符串列表 | `Docker`、`docker-compose` 的子集;选择 `docker-compose` 会自动带上 `Docker` |
| `custom_packages` | 字符串列表 | 按原样安装的额外包 |

每个维度都既接受单纯的选项(`"authentication": "JWT"`),也接受 `database` 和项目自身 `[tool.fastapi-fastkit]` 元数据所使用的 `{"type": ...}` 映射形式(`"authentication": {"type": "JWT"}`)—— 两者都会被规范化为相同的标准形式,而 `--save-config` 总是以标准的纯字符串形式写回。

一个覆盖了大多数维度的配置:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv",
  "database": "PostgreSQL",
  "authentication": "JWT",
  "async_tasks": "Celery",
  "caching": "Redis",
  "migrations": "Alembic",
  "tooling": ["ruff", "makefile"],
  "deployment": ["Docker"]
}
```

同样的配置写成 TOML:

```toml
project_name = "orders-api"
author = "Developer Kim"
author_email = "developer@example.com"
description = "Domain-oriented orders service"
architecture_preset = "domain-starter"
package_manager = "uv"
database = "PostgreSQL"
authentication = "JWT"
async_tasks = "Celery"
caching = "Redis"
migrations = "Alembic"
tooling = ["ruff", "makefile"]
deployment = ["Docker"]
```

#### 预览与跳过步骤

`--dry-run` 会打印将要创建的目录树以及将要安装的包 —— 连同将用来安装它们的包管理器 —— 然后在不触碰磁盘的情况下退出:

```console
$ fastkit init --config fastkit.config.json --dry-run
```

`--no-install` 会在虚拟环境创建后停止;`--no-venv` 则连环境也一并跳过(因此也不会安装)。两者在容器、CI 以及任何由 fastkit 之外的工具管理环境的场景中都很有用。

#### 原地部署与覆盖确认(`--yes` / `-y`) { #in-place-deployment-and-overwrite-confirmation-yes-y }

当项目以原地方式部署 —— 部署到当前工作区而不是新的项目文件夹 —— 时,fastkit 会在替换任何已存在的文件之前询问 "Overwrite these files?"。`--yes`(或其简写 `-y`)会跳过该确认并直接覆盖。它不影响另一个 "Do you want to proceed with project creation?" 提示,该提示仍会显示。在非交互环境中(stdin 不是 TTY,例如 CI 或通过管道运行),即使没有 `--yes`,覆盖确认也会被自动跳过。

#### 交互式提示

`init` 命令会依次提示您输入:

1. **项目名称**:目录与包的名称
2. **作者名称**:包的作者信息
3. **作者邮箱**:包的联系邮箱
4. **项目描述**:项目的简短描述
5. **栈选择**:在 minimal、standard、full 中选择
6. **包管理器选择**:在 pip、uv、pdm、poetry 中选择(除非用 `--package-manager` 指定)

#### 栈选项

**MINIMAL 栈:**

- `fastapi` —— FastAPI 框架
- `uvicorn` —— ASGI 服务器
- `pydantic` —— 数据校验
- `pydantic-settings` —— 配置管理

**STANDARD 栈:**

- 所有 MINIMAL 栈的依赖
- `sqlalchemy` —— SQL 工具包与 ORM
- `alembic` —— 数据库迁移工具
- `pytest` —— 测试框架

**FULL 栈:**

- 所有 STANDARD 栈的依赖
- `redis` —— 内存数据存储
- `celery` —— 分布式任务队列

#### 交互式构建器功能目录(`--interactive`) { #interactive-builder-feature-catalog-interactive }

`fastkit init --interactive` 使用的是另一套基于维度的目录,而不是上面的 minimal/standard/full 栈(事实来源:`core/settings.py` 中的 `FastkitConfig.PACKAGE_CATALOG`,以及决定每个选项生成什么的 `DynamicConfigGenerator.build_artifacts()`)。每个维度默认都是 `None`(跳过);`utilities` 与 `tooling` 为多选。

现在每个选择都会生成真正的代码,而不仅仅是安装包 —— `minimal` / `single-module`(重新生成 `main.py`)与 `classic-layered` / `domain-starter`(保留 `main.py`,并给出手动接入警告)之间有何不同,请参阅[架构预设 / 功能矩阵](../reference/preset-feature-matrix.md)。

| 维度 | 选项 | 安装的包 | 生成的文件 |
|---|---|---|---|
| `database` | PostgreSQL, MySQL, MongoDB, Redis, SQLite, None | PostgreSQL: `asyncpg`, `sqlalchemy` · MySQL: `aiomysql`, `sqlalchemy` · MongoDB: `motor` · Redis: `redis[hiredis]` · SQLite: `sqlalchemy`, `aiosqlite` | 位于预设对应路径的数据库配置模块(例如 `src/config/database.py`) |
| `authentication` | JWT, OAuth2, FastAPI-Users, Session-based, None | JWT: `pyjwt[crypto]`, `pwdlib[argon2]` · OAuth2: `authlib`, `itsdangerous`, `httpx` · FastAPI-Users: `fastapi-users[sqlalchemy]`, `pyjwt[crypto]`, `pwdlib[argon2]` · Session-based: `itsdangerous` | 位于预设对应路径的认证配置模块;OAuth2 与 Session-based 还会添加 `main.py` 中间件配置 |
| `async_tasks` | Celery, Dramatiq, None | Celery: `celery[redis]`, `redis[hiredis]` · Dramatiq: `dramatiq[redis]`, `redis[hiredis]` | `<pkg>/worker.py`(后台 worker)+ `<pkg>/features/tasks.py`(任务路由) |
| `testing` | Basic, Coverage, Advanced, None | Basic: `pytest`, `pytest-asyncio`, `httpx` · Coverage: + `pytest-cov` · Advanced: + `faker`, `factory-boy` | `pytest.ini`;Advanced 还会添加 `tests/factories.py` 与 `tests/test_factories.py` |
| `caching` | Redis, None | Redis: `redis[hiredis]`, `fastapi-cache2`, `jinja2` | `<pkg>/features/cache.py`(带缓存的端点) |
| `monitoring` | Loguru, OpenTelemetry, Prometheus, None | Loguru: `loguru` · OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp-proto-http` · Prometheus: `prometheus-client`, `prometheus-fastapi-instrumentator` | 不生成独立文件 —— 直接接入 `main.py`(import / lifespan / setup) |
| `utilities`(多选) | CORS, Rate-Limiting, Pagination, WebSocket, None | CORS: 无(FastAPI 内置) · Rate-Limiting: `slowapi` · Pagination: `fastapi-pagination` · WebSocket: `websockets` | CORS 与 Rate-Limiting 直接接入 `main.py`;Pagination 添加 `<pkg>/features/pagination.py`,WebSocket 添加 `<pkg>/features/websocket.py` |
| `migrations` | Alembic, None | Alembic: `alembic` | `alembic.ini`、`alembic/env.py`、`alembic/script.py.mako`、基线修订 `alembic/versions/<id>_initial.py`、`scripts/migrate.sh` —— 仅当数据库维度为 SQL 数据库时生成 |
| `tooling`(多选) | ruff, pre-commit, github-actions, devcontainer, makefile, None | ruff: `ruff` · pre-commit: `pre-commit` · github-actions / devcontainer / makefile: 无 | ruff 会把 `[tool.ruff]` 块合并进 `pyproject.toml`(`pip` 项目则写入 `ruff.toml`);pre-commit 写入 `.pre-commit-config.yaml`;github-actions 写入 `.github/workflows/test.yml`;devcontainer 写入 `.devcontainer/devcontainer.json`;makefile 写入 `Makefile` |
| `logging` | structured, None | 无(仅使用标准库 `logging` + `json`) | `<pkg>/logging_config.py`(结构化 JSON 日志 + request-id 中间件),并接入 `main.py` |

无论如何选择,每个生成的项目都会在 `main.py` 中获得 `/health` 与 `/ready` 端点,而 `--dry-run` 会在写入任何内容之前打印出这一组确切的文件。

#### 示例

<div class="termy">

```console
$ fastkit init
Enter the project name: my-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome API

Select stack (minimal, standard, full): standard
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-api' has been created successfully!
```

</div>

#### 生成的结构

创建出的项目结构如下：

```
my-api/
├── .venv/                    # 虚拟环境
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # 配置文件
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API 路由汇总
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── items.py     # 示例路由
│   ├── crud/
│   │   ├── __init__.py
│   │   └── items.py         # CRUD 操作
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── items.py         # Pydantic 模式
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # 测试数据
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

### `addroute`

向已有的 FastAPI 项目添加新的 API 路由。

#### 语法

```console
$ fastkit addroute ROUTE_NAME [PROJECT_DIR] [OPTIONS]
```

#### 参数

| 参数 | 描述 | 必填 |
|----------|-------------|----------|
| `ROUTE_NAME` | 新路由的名称(推荐使用复数) | 是 |
| `PROJECT_DIR` | 工作区下的项目目录(默认 `.`,即当前目录) | 否 |

#### 选项

| 选项 | 描述 | 默认值 |
|--------|-------------|---------|
| `--help` | 显示命令帮助 | - |

#### 示例

<div class="termy">

```console
$ cd my-api
$ fastkit addroute users
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-api                                   │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-api                                 │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-api'
```

</div>

您也可以通过名称定位工作区下的项目,无需先 `cd`:

<div class="termy">

```console
$ fastkit addroute users my-api
```

</div>

#### 生成的文件

会在项目中生成以下文件：

- `src/api/routes/users.py` —— 路由处理器
- `src/crud/users.py` —— CRUD 操作
- `src/schemas/users.py` —— Pydantic 模式

同时会更新 `src/api/api.py`,把新路由器纳入其中。

#### 生成的端点

会创建完整的一组 CRUD 端点：

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | 获取所有用户 |
| `POST` | `/api/v1/users/` | 创建新用户 |
| `GET` | `/api/v1/users/{user_id}` | 获取指定用户 |
| `PUT` | `/api/v1/users/{user_id}` | 更新用户 |
| `DELETE` | `/api/v1/users/{user_id}` | 删除用户 |

#### 代码插入的位置

`addroute` 需要从项目中得知两件事:新的 import 放在哪里,以及在哪里注册路由器。模板和生成的入口文件都用锚点注释标出了这两处:

```python
# src/app/api/router.py
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

编辑该文件时请保留这些注释 —— `addroute` 会直接插入到 `# fastkit:imports` 和 `# fastkit:routes` 的上方。丢失了这些锚点(或在锚点出现之前生成)的项目仍然可以工作:fastkit 会退回到基于 AST 的插入方式,自行找到 import 块和路由注册位置。锚点只是让结果变得可预测。

`addroute` 还会读取项目的 `[tool.fastapi-fastkit]` 块来定位入口文件,因此即使在仅凭磁盘扫描会判断错误的布局上也能正常工作。

### `startdemo`

基于预构建的模板创建 FastAPI 项目。

#### 语法

```console
$ fastkit startdemo [OPTIONS]
```

#### 选项

| 选项 | 描述 | 默认值 |
|--------|-------------|---------|
| `--project-name` | 项目名称(省略时会提示输入) | - |
| `--author` | 作者名称(省略时会提示输入) | - |
| `--author-email` | 作者邮箱(省略时会提示输入) | - |
| `--description` | 项目描述(省略时会提示输入) | - |
| `--package-manager` | 要使用的包管理器(pip、uv、pdm、poetry) | uv |
| `--dry-run` | 显示将要创建的文件和包,但不写入任何内容 | off |
| `--no-venv` | 跳过虚拟环境创建(隐含 `--no-install`) | off |
| `--no-install` | 跳过依赖安装 | off |
| `--yes` / `-y` | 在原地部署项目时,覆盖已有文件之前不再询问确认 | off |
| `--help` | 显示命令帮助 | - |

与 `init` 一样,当目标项目目录已经存在时,`startdemo` 会拒绝运行(`Error: Project '{name}' already exists.`)。`--dry-run` 是例外:由于它从不写入磁盘,因此仍然可以指定一个已有同名目录的名称。关于部署到当前工作区时 `--yes` 的作用,请参阅上文的[原地部署与覆盖确认](#in-place-deployment-and-overwrite-confirmation-yes-y)。

#### 交互式提示

`startdemo` 命令会依次提示您输入:

1. **项目名称**:新项目的目录名称
2. **作者名称**:包的作者信息
3. **作者邮箱**:联系邮箱
4. **项目描述**:简短描述
5. **包管理器选择**:在 pip、uv、pdm、poetry 中选择(除非用 `--package-manager` 指定)

#### 可用的模板

| 模板 | 描述 | 特性 |
|----------|-------------|----------|
| `fastapi-default` | 简单的 FastAPI 项目 | 基础 CRUD、mock 数据 |
| `fastapi-domain-starter` | 面向领域的 starter | 每个业务概念一个文件夹、`/health` |
| `fastapi-auth-jwt` | JWT 认证 | 访问/刷新令牌轮换、argon2id、角色与作用域、Alembic |
| `fastapi-sqlmodel` | 异步 SQLModel 持久化 | SQLModel + 异步 SQLAlchemy、Alembic、通用 CRUD、分页 |
| `fastapi-llm-agent` | 流式 Claude 智能体 | SSE 流式输出、工具调用循环、对话记忆 |
| `fastapi-custom-response` | 自定义响应系统 | 自定义响应、分页 |
| `fastapi-psql-orm` | 基于 PostgreSQL 的 FastAPI | PostgreSQL、SQLAlchemy、Alembic |
| `fastapi-mcp` | Model Context Protocol 服务器 | MCP 集成 |
| `fastapi-single-module` | 单文件沙盒 | 单个模块,没有包边界 |
| `fastapi-empty` | 最小化的 FastAPI 项目 | 极简骨架 |
| `fastapi-async-crud` | *(已弃用)* 异步 item 管理 API | 已被 `fastapi-sqlmodel` 取代 |
| `fastapi-dockerized` | *(已弃用)* 已 Docker 化的 FastAPI | Docker 工具链现已随较新的模板一同提供 |

已弃用的模板仍然可以生成可运行的项目;只是不再推荐作为起点。请参阅[应该选择哪个 starter?](choosing-a-starter.md)。

#### 示例

<div class="termy">

```console
$ fastkit startdemo fastapi-psql-orm
Enter the project name: my-blog
Enter the author name: Jane Smith
Enter the author email: jane@example.com
Enter the project description: Blog API with PostgreSQL

Select package manager (pip, uv, pdm, poetry) [uv]: poetry
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog' from 'fastapi-psql-orm' has been created!
```

</div>

### `runserver`

启动 FastAPI 开发服务器。

#### 语法

```console
$ fastkit runserver [OPTIONS]
```

#### 选项

| 选项 | 短选项 | 描述 | 默认值 |
|--------|-------|-------------|---------|
| `--host` | `-h` | 绑定的主机 | `127.0.0.1` |
| `--port` | `-p` | 绑定的端口 | `8000` |
| `--reload` | `-r` | 启用自动重载 | `True` |
| `--workers` | `-w` | worker 数量 | `1` |
| `--help` | | 显示命令帮助 | - |

#### 示例

<div class="termy">

```console
# 基本用法（默认设置）
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000

# 自定义主机与端口
$ fastkit runserver --host 0.0.0.0 --port 8080
INFO:     Uvicorn running on http://0.0.0.0:8080

# 关闭自动重载
$ fastkit runserver --no-reload
INFO:     Uvicorn running on http://127.0.0.1:8000

# 多 worker 运行（偏生产场景）
$ fastkit runserver --workers 4
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

#### 前置条件

- 必须在 FastAPI 项目目录中运行
- 项目必须暴露一个 FastAPI 应用 —— 如果存在 `[tool.fastapi-fastkit].app_module`,就从中解析,否则通过扫描 `main.py` 来发现
- 建议提前激活虚拟环境

如果记录的入口和扫描都找不到模块,`runserver` 会报告找不到 `main.py` 并停止。

### `list-templates`

列出所有可用的 FastAPI 项目模板。

#### 语法

```console
$ fastkit list-templates [OPTIONS]
```

#### 选项

| 选项 | 描述 | 默认值 |
|--------|-------------|---------|
| `--help` | 显示命令帮助 | - |

#### 示例

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-custom-response │ Async Item Management API with    │
│                         │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI Item           │
│                         │ Management API                    │
│ fastapi-empty           │ No description                    │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-psql-orm        │ Dockerized FastAPI Item           │
│                         │ Management API with PostgreSQL    │
│ fastapi-default         │ Simple FastAPI Project            │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

## 项目元数据(`[tool.fastapi-fastkit]`)

fastkit 生成的每个项目都会在自己的 `pyproject.toml` 中记录它是如何生成的:

```toml
[tool.fastapi-fastkit]
managed = true
version = "1.4.0"
template = "fastapi-domain-starter"
preset = "domain-starter"
package_manager = "uv"
app_module = "src.app.main:app"
features = ["database:PostgreSQL", "authentication:JWT"]
```

| 键 | 含义 |
|---|---|
| `managed` | 始终为 `true`;将项目标记为由 fastkit 管理 |
| `version` | 生成该项目的 fastkit 版本 |
| `template` | `startdemo` 模板,或预设的基础模板 |
| `preset` | `init --interactive` 的架构预设(其他情况下省略) |
| `package_manager` | 用于构建环境的包管理器 |
| `app_module` | uvicorn 的 `module:attr` 入口 |
| `features` | 交互式选择的扁平 `"<category>:<choice>"` 列表 |

这个块是项目入口的唯一事实来源:`fastkit runserver` 会先从中读取 `app_module`,然后才退回到扫描目录树;`fastkit addroute` 用它定位应用;生成的 Dockerfile 也在 `CMD` 中使用同一个值。

该块在生成的最后阶段写入 —— 包管理器在解析依赖时会重写 `pyproject.toml`,因此必须在那之后再写入 —— 之后的重新生成会替换它,而不是再追加一份。手动编辑 `app_module` 是告知 fastkit 您自行重组了布局的受支持方式。

## 环境变量

FastAPI-fastkit 会读取以下环境变量:

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | 配置目录 | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | 自定义模板目录 | 内置模板 |
| `FASTKIT_LOG_LEVEL` | 日志级别 | `INFO` |
| `FASTKIT_SUBPROCESS_TIMEOUT` | 覆盖所有包管理器子进程的超时时间,单位为秒 | 按操作区分(30 / 120 / 900) |

每次包管理器调用都有各自的时间上限,因此挂起的子进程永远不会阻塞 CLI:可用性检查为 30 秒,创建虚拟环境为 120 秒,安装依赖为 900 秒。`FASTKIT_SUBPROCESS_TIMEOUT` 会用一个值替换这三者 —— 在网络较慢时,或想在 CI 中快速失败时很有用。不是正整数的值会被忽略。

```console
$ export FASTKIT_SUBPROCESS_TIMEOUT=1800
$ fastkit startdemo fastapi-sqlmodel
```

### 示例

<div class="termy">

```console
# 自定义配置目录
$ export FASTKIT_CONFIG_DIR=~/my-fastkit-config
$ fastkit init

# 自定义模板目录
$ export FASTKIT_TEMPLATES_DIR=~/my-templates
$ fastkit list-templates

# 调试日志
$ export FASTKIT_LOG_LEVEL=DEBUG
$ fastkit init
```

</div>

## 配置文件

FastAPI-fastkit 可以使用配置文件存放默认设置。

### 配置文件位置

1. `$FASTKIT_CONFIG_DIR/config.yaml`(若设置了 `FASTKIT_CONFIG_DIR`)
2. `~/.fastkit/config.yaml`(默认)
3. `./fastkit.yaml`(项目级)

### 配置格式

```yaml
# ~/.fastkit/config.yaml
default:
  author:
    name: "Your Name"
    email: "your.email@example.com"

  project:
    stack: "standard"
    create_venv: true
    install_deps: true

  server:
    host: "127.0.0.1"
    port: 8000
    reload: true

templates:
  custom_dir: "~/my-templates"

logging:
  level: "INFO"
  file: "~/.fastkit/logs/fastkit.log"
```

## 常见工作流

### 1. 创建新项目

<div class="termy">

```console
# 创建新项目
$ fastkit init
# 按提示完成选择……

# 进入项目目录
$ cd my-awesome-api

# 激活虚拟环境
$ source .venv/bin/activate

# 启动开发服务器
$ fastkit runserver
```

</div>

### 2. 为已有项目添加功能

<div class="termy">

```console
# 添加多个路由（第二个位置参数为工作区中的项目名）
$ fastkit addroute users my-api
$ fastkit addroute products my-api
$ fastkit addroute orders my-api

# 测试 API
$ fastkit runserver
# 打开 http://127.0.0.1:8000/docs
```

</div>

### 3. 借助模板搭建复杂项目

<div class="termy">

```console
# 列出可用模板
$ fastkit list-templates

# 基于模板创建项目
$ fastkit startdemo
# 如果是数据库项目,可选择 fastapi-psql-orm

# 初始化数据库（适用于 PostgreSQL 模板）
$ cd my-project
$ docker-compose up -d postgres
$ source .venv/bin/activate
$ alembic upgrade head
$ fastkit runserver
```

</div>

## 故障排查

### 找不到命令

如果找不到 `fastkit` 命令:

1. **确认是否已安装:**
   <div class="termy">
   ```console
   $ pip show fastapi-fastkit
   ```
   </div>

2. **必要时重新安装:**
   <div class="termy">
   ```console
   $ pip uninstall fastapi-fastkit
   $ pip install fastapi-fastkit
   ```
   </div>

3. **检查 PATH:**
   <div class="termy">
   ```console
   $ which fastkit
   ```
   </div>

### 虚拟环境问题

如果虚拟环境创建失败:

1. **检查 Python 版本:**
   <div class="termy">
   ```console
   $ python --version  # Should be 3.12+
   ```
   </div>

2. **检查 venv 模块:**
   <div class="termy">
   ```console
   $ python -m venv --help
   ```
   </div>

3. **手动创建虚拟环境:**
   <div class="termy">
   ```console
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ```
   </div>

### 服务器无法启动

如果 `fastkit runserver` 失败:

1. **确认当前目录是项目根目录**
2. **确认 `src/main.py` 存在**
3. **激活虚拟环境:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

4. **检查语法错误:**
   <div class="termy">
   ```console
   $ python -c "from src.main import app"
   ```
   </div>

### 端口已被占用

如果 8000 端口被占用:

<div class="termy">

```console
# 换一个端口运行
$ fastkit runserver --port 8080

# 或结束当前占用端口的进程
$ lsof -ti:8000 | xargs kill -9
```

</div>

## 进阶用法

### 自定义模板

您可以这样创建自定义模板:

1. **创建模板目录:**
   ```
   my-template/
   ├── src/
   │   └── main.py-tpl
   ├── requirements.txt-tpl
   └── setup.py-tpl
   ```

2. **设置环境变量:**
   <div class="termy">
   ```console
   $ export FASTKIT_TEMPLATES_DIR=~/my-templates
   ```
   </div>

3. **使用自定义模板:**
   <div class="termy">
   ```console
   $ fastkit startdemo
   # 您的自定义模板会出现在列表中
   ```
   </div>

### 在脚本中使用 FastAPI-fastkit

可以将 FastAPI-fastkit 嵌入到脚本中：

```bash
#!/bin/bash
# create-microservices.sh

for service in users products orders; do
    echo "正在创建 $service 服务..."
    fastkit init <<EOF
$service-service
Company Team
team@company.com
$service microservice
minimal
y
EOF

    cd "$service-service"
    fastkit addroute "$service"
    cd ..
done
```

### 与 CI/CD 集成

GitHub Actions 工作流示例:

```yaml
name: Test FastAPI-fastkit Project

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install FastAPI-fastkit
      run: pip install fastapi-fastkit

    - name: Create test project
      run: |
        fastkit init <<EOF
        test-project
        CI
        ci@example.com
        Test project
        standard
        y
        EOF

    - name: Test project
      run: |
        cd test-project
        source .venv/bin/activate
        python -m pytest
```

## 包管理器支持

FastAPI-fastkit 支持多种 Python 包管理器,您可以选择最契合工作流的那一种。

### 支持的包管理器

| 管理器 | 描述 | 依赖文件 | 适用场景 |
|---------|-------------|----------------|----------|
| **UV**(默认) | 快速的 Python 包管理器 | `pyproject.toml` | 追求速度与性能 |
| **PDM** | 现代化的 Python 依赖管理 | `pyproject.toml` | 需要更强的依赖解析 |
| **Poetry** | Python 依赖管理与打包 | `pyproject.toml` | 基于 Poetry 的工作流 |
| **PIP** | 标准 Python 包管理器 | `requirements.txt` | 传统 Python 开发 |

### 指定包管理器

#### 全局配置

可以为所有项目设置首选的包管理器:

```console
# 使用命令行参数指定
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

#### 项目级选择

每个项目都可以使用不同的包管理器。该选择在创建项目时决定,并会影响:

- **依赖文件格式**:每种管理器创建对应的文件
- **虚拟环境管理**:激活方式各不相同
- **依赖安装**:命令视管理器而异

### 包管理器特性

#### UV(默认)
- **快速**:基于 Rust,依赖解析速度极快
- **兼容**:可作为 pip 与 pip-tools 的替代品
- **现代**:支持 PEP 621 项目元数据

<div class="termy">

```console
$ fastkit init --package-manager uv
# 生成带 UV 配置的 pyproject.toml
```

</div>

#### PDM
- **现代**:支持 PEP 582 与 PEP 621
- **进阶**:更复杂的依赖解析
- **灵活**:支持多种项目布局

<div class="termy">

```console
$ fastkit init --package-manager pdm
# 生成带 PDM 配置的 pyproject.toml
```

</div>

#### Poetry
- **成熟**:广为使用
- **一体化**:支持构建与发布
- **锁文件**:poetry.lock 保证可复现构建

<div class="termy">

```console
$ fastkit init --package-manager poetry
# 生成带 Poetry 配置的 pyproject.toml
```

</div>

#### PIP
- **标准**:Python 内置
- **兼容**:到哪都能用
- **简单**:工作流朴素直接

<div class="termy">

```console
$ fastkit init --package-manager pip
# 生成 requirements.txt
```

</div>

### 创建后的使用方式

使用对应包管理器创建项目后:

#### UV 项目
```console
cd my-project
uv sync          # 安装依赖
uv add requests  # 添加新依赖
uv run pytest    # 在项目环境中运行命令
```

#### PDM 项目
```console
cd my-project
pdm install      # 安装依赖
pdm add requests # 添加新依赖
pdm run pytest   # 在项目环境中运行命令
```

#### Poetry 项目
```console
cd my-project
poetry install      # 安装依赖
poetry add requests # 添加新依赖
poetry run pytest   # 在项目环境中运行命令
```

#### PIP 项目
```console
cd my-project
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install requests
pytest
```

## 下一步

现在您已经了解 CLI:

1. **[快速上手](quick-start.md)**:动手体验各命令
2. **[您的第一个项目](../tutorial/first-project.md)**:构建一个完整的应用
3. **[参与贡献](../contributing/development-setup.md)**:为 FastAPI-fastkit 贡献代码

!!! tip "CLI 小贴士"
    - 任何命令搭配 `--help` 都可以查看详细帮助
    - 配置默认设置可以加快项目创建
    - 借助模板搭建复杂项目
    - 把命令组合起来,可以构建强大的工作流

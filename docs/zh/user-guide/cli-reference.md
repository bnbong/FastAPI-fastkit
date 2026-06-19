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
| `--package-manager` | 要使用的包管理器(pip、uv、pdm、poetry) | uv |
| `--help` | 显示命令帮助 | - |

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

### `startdemo`

基于预构建的模板创建 FastAPI 项目。

#### 语法

```console
$ fastkit startdemo [OPTIONS]
```

#### 选项

| 选项 | 描述 | 默认值 |
|--------|-------------|---------|
| `--package-manager` | 要使用的包管理器(pip、uv、pdm、poetry) | uv |
| `--help` | 显示命令帮助 | - |

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
| `fastapi-async-crud` | 异步 item 管理 API | async/await、性能优化 |
| `fastapi-custom-response` | 自定义响应系统 | 自定义响应、分页 |
| `fastapi-dockerized` | 已 Docker 化的 FastAPI | Docker、适合生产部署 |
| `fastapi-psql-orm` | 基于 PostgreSQL 的 FastAPI | PostgreSQL、SQLAlchemy、Alembic |
| `fastapi-empty` | 最小化的 FastAPI 项目 | 极简骨架 |

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
- 项目必须含有 `src/main.py`,并定义了 FastAPI 应用
- 建议提前激活虚拟环境

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

## 环境变量

FastAPI-fastkit 会读取以下环境变量:

| 变量 | 描述 | 默认值 |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | 配置目录 | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | 自定义模板目录 | 内置模板 |
| `FASTKIT_LOG_LEVEL` | 日志级别 | `INFO` |

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

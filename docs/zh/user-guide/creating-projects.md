# 创建项目

详细介绍如何使用 FastAPI-fastkit 创建各种类型的 FastAPI 项目。

## 基本的项目创建

### 1. 交互模式下的项目创建

最基础的创建方式如下：

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Awesome FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-api          │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ Awesome FastAPI project │
└──────────────┴─────────────────────────┘
```

</div>

### 2. 选择技术栈

选择您希望项目包含的依赖栈：

#### MINIMAL 栈(默认)

最基础的 FastAPI 项目:

- `fastapi` —— FastAPI 框架
- `uvicorn` —— ASGI 服务器
- `pydantic` —— 数据校验
- `pydantic-settings` —— 设置管理

**适合:**

- 学习 FastAPI
- 简单的 API
- 原型
- 微服务

#### STANDARD 栈

包含数据库支持与测试:

- 所有 MINIMAL 依赖
- `sqlalchemy` —— 数据库操作的 ORM
- `alembic` —— 数据库迁移
- `pytest` —— 测试框架

**适合:**

- 大多数 Web 应用
- 带数据库存储的 API
- 准备走向生产的应用
- 团队项目

#### FULL 栈

完整的开发环境:

- 所有 STANDARD 依赖
- `redis` —— 缓存与会话存储
- `celery` —— 后台任务处理

**适合:**

- 大型应用
- 对性能有较高要求
- 复杂的业务逻辑
- 企业应用

## 高级项目选项

### 自定义项目配置

您可以在创建项目时进行定制:

<div class="termy">

```console
$ fastkit init
Enter the project name: advanced-api
Enter the author name: Development Team
Enter the author email: dev@company.com
Enter the project description: Advanced FastAPI application with custom features

# 选择 STANDARD 栈以获得数据库支持
Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 项目结构说明

创建项目时,FastAPI-fastkit 会生成如下结构：

```
my-awesome-api/
├── .venv/                      # 虚拟环境
├── src/                        # 源代码
│   ├── __init__.py
│   ├── main.py                # 应用入口
│   ├── core/                  # 核心配置
│   │   ├── __init__.py
│   │   └── config.py         # 设置与配置
│   ├── api/                   # API 层
│   │   ├── __init__.py
│   │   ├── api.py            # 主 API 路由
│   │   └── routes/           # 各个路由模块
│   │       ├── __init__.py
│   │       └── items.py      # items 示例端点
│   ├── crud/                  # 数据库操作
│   │   ├── __init__.py
│   │   └── items.py          # items 相关的 CRUD 操作
│   ├── schemas/               # Pydantic 模型
│   │   ├── __init__.py
│   │   └── items.py          # 数据校验模式
│   └── mocks/                 # 测试数据
│       ├── __init__.py
│       └── mock_items.json   # 开发用示例数据
├── tests/                     # 测试套件
│   ├── __init__.py
│   ├── conftest.py           # 测试配置
│   └── test_items.py         # 示例测试
├── scripts/                   # 辅助脚本
│   ├── test.sh               # 运行测试
│   ├── coverage.sh           # 测试覆盖率
│   └── lint.sh               # 代码检查
├── requirements.txt           # Python 依赖
├── setup.py                  # 包配置
└── README.md                 # 项目文档
```

### 3. 选择包管理器

FastAPI-fastkit 支持多种 Python 包管理器,请选择最适合您工作流程的那一种：

#### 可用的包管理器

<div class="termy">

```console
Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

每种包管理器都有各自的优势：

#### UV(默认 —— 推荐)

**基于 Rust 的高速包管理器**

- ⚡ **超快**:比 pip 快 10–100 倍
- 🔧 **上手直接**:兼容 pip 工作流
- 📦 **现代**:完整支持 PEP 621
- 🛠️ **可靠**:确定性的依赖解析

**生成的文件：**

- `pyproject.toml`(PEP 621 格式)
- `uv.lock`(锁文件)

**创建项目后常用的命令：**
```console
cd my-project
uv sync              # 安装依赖
uv add requests      # 添加新依赖
uv run pytest        # 运行测试
```

#### PDM

**现代化的 Python 依赖管理**

- 🚀 **现代**:支持 PEP 582 与 PEP 621
- 🧠 **智能**:更强的依赖解析
- 💼 **专业**:支持工作区与多项目
- 📊 **分析能力**:依赖分析工具

**生成的文件：**

- `pyproject.toml`(PEP 621 格式)
- `pdm.lock`(锁文件)

**创建项目后常用的命令：**
```console
cd my-project
pdm install          # 安装依赖
pdm add requests     # 添加新依赖
pdm run pytest       # 运行测试
```

#### Poetry

**成熟的依赖管理与打包工具**

- ✅ **成熟**:广泛使用
- 📦 **一体化**:支持构建与发布
- 🔒 **可复现**:poetry.lock 锁定精确版本
- 🏗️ **完整**:覆盖项目完整生命周期

**生成的文件：**

- `pyproject.toml`(Poetry 格式)
- `poetry.lock`(锁文件)

**创建项目后常用的命令：**
```console
cd my-project
poetry install       # 安装依赖
poetry add requests  # 添加新依赖
poetry run pytest    # 运行测试
```

#### PIP

**标准的 Python 包管理器**

- 🏠 **内置**:Python 自带
- 🌍 **通用**:到哪都能用
- 📚 **熟悉**:大多数开发者都很熟悉
- 🔧 **简单**:工作流朴素直接

**生成的文件：**

- `requirements.txt`

**创建项目后常用的命令：**
```console
cd my-project
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install requests
pytest
```

#### 指定包管理器

您也可以直接指定偏好的包管理器：

**交互式选择（默认）：**
```console
$ fastkit init
# ... 接下来会提示选择包管理器
```

**命令行参数：**
```console
$ fastkit init --package-manager poetry
$ fastkit init --package-manager pdm
$ fastkit init --package-manager uv
$ fastkit init --package-manager pip
```

### 各目录用途解析

#### `src/` 目录

这里包含项目的全部应用源代码,采用 **src 布局** —— 这是 Python 打包中的常见最佳实践。

#### `core/` 模块

- **config.py**：应用设置、环境变量与配置
- 集中管理所有配置
- 支持 `.env` 文件以满足按环境配置的需求

#### `api/` 模块

- **api.py**：主 API 路由,统一汇总所有子路由
- **routes/**：针对不同资源拆分出的独立路由模块
- 不同 API 端点之间职责清晰

#### `crud/` 模块

- 数据库操作与业务逻辑
- **C**reate / **R**ead / **U**pdate / **D**elete 操作
- API 路由与数据存储之间的抽象层

#### `schemas/` 模块

- 用于数据校验的 Pydantic 模型
- 请求 / 响应模式
- 类型定义与数据模型

#### `tests/` 目录

- 应用完整的测试套件
- 包含单元测试与集成测试
- 已预配置 pytest

## 各栈对比

| 功能 | MINIMAL | STANDARD | FULL |
|---------|---------|----------|------|
| FastAPI 与 Uvicorn | ✅ | ✅ | ✅ |
| 数据校验 | ✅ | ✅ | ✅ |
| 数据库支持 | ❌ | ✅ | ✅ |
| 数据迁移 | ❌ | ✅ | ✅ |
| 测试框架 | ❌ | ✅ | ✅ |
| 缓存(Redis) | ❌ | ❌ | ✅ |
| 后台任务 | ❌ | ❌ | ✅ |
| **适合** | 学习、简单 API | 大多数应用 | 企业、复杂应用 |

## 项目创建示例

### 示例 1:学习项目

<div class="termy">

```console
$ fastkit init
Enter the project name: fastapi-learning
Enter the author name: Student
Enter the author email: student@example.com
Enter the project description: Learning FastAPI basics

Select stack (minimal, standard, full): minimal
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 示例 2:电商 API

<div class="termy">

```console
$ fastkit init
Enter the project name: ecommerce-api
Enter the author name: E-commerce Team
Enter the author email: team@ecommerce.com
Enter the project description: E-commerce platform API

Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### 示例 3:高性能应用

<div class="termy">

```console
$ fastkit init
Enter the project name: enterprise-api
Enter the author name: Enterprise Team
Enter the author email: enterprise@company.com
Enter the project description: High-performance enterprise API

Select stack (minimal, standard, full): full
Do you want to proceed with project creation? [y/N]: y
```

</div>

## 创建项目之后

### 1. 激活虚拟环境

<div class="termy">

```console
$ cd my-awesome-api
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

### 2. 校验安装

<div class="termy">

```console
$ pip list
Package         Version
fastapi         0.104.1
uvicorn         0.24.0
pydantic        2.5.0
...
```

</div>

### 3. 开始开发

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

## 配置管理

### 环境变量

项目支持通过 `.env` 文件按环境进行配置：

在项目根目录创建 `.env` 文件：

```env
# .env
APP_NAME=My Awesome API
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### 在代码中的配置

生成的 `src/core/config.py` 会自动加载这些变量：

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key"

    class Config:
        env_file = ".env"

settings = Settings()
```

## 定制选项

### 添加自定义依赖

项目创建后,还可以继续添加更多依赖：

<div class="termy">

```console
$ pip install requests httpx python-jose
$ pip freeze > requirements.txt
```

</div>

### 修改项目结构

生成的结构遵循最佳实践,但您完全可以按需调整：

- 在 `src/` 下添加新模块
- 在 `api/routes/` 下新增路由文件
- 在 `crud/` 中扩展 CRUD 操作
- 在 `schemas/` 中添加更多模式

## 最佳实践

### 1. 虚拟环境

请始终使用虚拟环境隔离项目依赖：

```bash
# 创建项目（会自动生成 .venv）
$ fastkit init  # Automatically creates .venv/

# 开始开发前激活环境
$ source .venv/bin/activate
```

### 2. 版本控制

项目创建后建议初始化 git 仓库:

<div class="termy">

```console
$ cd my-awesome-api
$ git init
$ git add .
$ git commit -m "Initial commit - FastAPI project setup"
```

</div>

### 3. 环境配置

- 使用 `.env` 文件做本地开发配置
- 在生产环境使用环境变量
- 切勿将敏感信息提交到版本控制

### 4. 测试

充分使用内置的测试框架:

<div class="termy">

```console
$ python -m pytest
$ bash scripts/test.sh
```

</div>

## 下一步

创建项目之后:

1. **[添加路由](adding-routes.md)**:学习如何添加新的 API 端点
2. **[CLI 参考](cli-reference.md)**:掌握所有可用命令
3. **[您的第一个项目教程](../tutorial/first-project.md)**:构建一个完整的应用

!!! tip "项目创建小贴士"
    - 选择与项目需求相匹配的技术栈
    - 学习时从 MINIMAL 开始,大多数项目用 STANDARD 即可
    - 项目结构兼顾扩展性与可维护性
    - 所有生成的代码都遵循 FastAPI 的最佳实践

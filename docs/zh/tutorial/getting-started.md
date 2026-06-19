# 入门指南

这是一份完整的 FastAPI-fastkit 上手教程,会带您一步步从安装走到运行第一个 API,大约 15 分钟即可完成。

## 前置条件

开始之前,请确认您已具备:

- 已在系统上安装 **Python 3.12 及以上**
- 具备 **Python 基础知识**(变量、函数、类)
- 可以访问 **终端 / 命令行**
- 一个 **文本编辑器或 IDE**(VS Code、PyCharm 等)

## 第 1 步:安装

首先安装 FastAPI-fastkit。建议使用虚拟环境以保持项目隔离。

### 方案 A:使用 pip(传统)

<div class="termy">

```console
$ pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### 方案 B:使用 UV(推荐 —— 更快)

UV 是一款高速的 Python 包管理器。若您尚未安装 UV:

<div class="termy">

```console
# Install UV first
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# Then install FastAPI-fastkit
$ uv pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### 方案 C:使用虚拟环境

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # On Windows: fastapi-env\Scripts\activate
$ pip install fastapi-fastkit
```

</div>

### 验证安装

确认 FastAPI-fastkit 已正确安装:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

## 第 2 步:创建您的第一个项目

接下来用交互式的 `init` 命令创建第一个 FastAPI 项目:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-api
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-first-api            │
│ Author       │ Your Name               │
│ Author Email │ your.email@example.com  │
│ Description  │ My first FastAPI project│
└──────────────┴─────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

Creating virtual environment...
Installing dependencies...
✨ FastAPI project 'my-first-api' has been created successfully!
```

</div>

!!! note "技术栈选择"
    本教程为简化起见选择了 **MINIMAL**。在真实项目中,可以考虑 **STANDARD**(包含数据库支持)或 **FULL**(包含后台任务)。

## 第 3 步:进入项目目录

进入刚创建好的项目目录:

<div class="termy">

```console
$ cd my-first-api
$ ls -la
total 32
drwxr-xr-x  8 user user  256 Dec  7 10:30 .
drwxr-xr-x  3 user user   96 Dec  7 10:30 ..
drwxr-xr-x  5 user user  160 Dec  7 10:30 .venv
-rw-r--r--  1 user user  156 Dec  7 10:30 README.md
-rw-r--r--  1 user user  243 Dec  7 10:30 requirements.txt
drwxr-xr-x  3 user user   96 Dec  7 10:30 scripts
-rw-r--r--  1 user user 1245 Dec  7 10:30 setup.py
drwxr-xr-x  8 user user  256 Dec  7 10:30 src
drwxr-xr-x  3 user user   96 Dec  7 10:30 tests
```

</div>

## 第 4 步:激活虚拟环境

您的项目已预先配置好虚拟环境,激活它:

<div class="termy">

```console
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
(my-first-api) $
```

</div>

注意您的终端提示符现在会显示 `(my-first-api)`,表示虚拟环境已激活。

## 第 5 步:启动开发服务器

接下来是激动人心的部分 —— 启动 FastAPI 服务器:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720] using StatReload
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

🎉 **恭喜!** 您的 FastAPI 服务器已经运行起来了。

## 第 6 步:测试 API

下面用几种方式测试您的 API:

### 方式 1:浏览器

打开浏览器,访问:

- **API 主端点**:[http://127.0.0.1:8000](http://127.0.0.1:8000)

您会看到:
```json
{"message": "Hello World"}
```

### 方式 2:交互式 API 文档

访问 FastAPI 自动生成的 API 文档:

- **Swagger UI**:[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**:[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Swagger UI 尤为实用,您可以:

- 查看所有可用端点
- 直接在浏览器中测试端点
- 查看请求 / 响应的模式
- 下载 OpenAPI 规范

### 方式 3:命令行

另开一个终端(保持服务器运行),用 curl 测试:

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Hello World"}

$ curl http://127.0.0.1:8000/api/v1/items/
[]

$ curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Item", "description": "This is a test item"}'
{
  "id": 1,
  "title": "My First Item",
  "description": "This is a test item"
}
```

</div>

## 第 7 步:了解您的项目结构

来看看 FastAPI-fastkit 为您生成了哪些内容：

<div class="termy">

```console
$ tree src
src/
├── __init__.py
├── main.py                 # FastAPI 应用入口
├── core/
│   ├── __init__.py
│   └── config.py          # 应用配置
├── api/
│   ├── __init__.py
│   ├── api.py             # 主 API 路由
│   └── routes/
│       ├── __init__.py
│       └── items.py       # items API 端点
├── crud/
│   ├── __init__.py
│   └── items.py           # items 相关业务逻辑
├── schemas/
│   ├── __init__.py
│   └── items.py           # 数据校验模式
└── mocks/
    ├── __init__.py
    └── mock_items.json    # 示例数据
```

</div>

### 关键文件说明

**`src/main.py`** —— 应用的核心:
```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**`src/core/config.py`** —— 应用设置:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "my-first-api"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

**`src/api/routes/items.py`** —— API 端点:
```python
from typing import List
from fastapi import APIRouter, HTTPException
from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import items_crud

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items():
    """Get all items"""
    return items_crud.get_all()

@router.post("/", response_model=Item)
def create_item(item: ItemCreate):
    """Create a new item"""
    return items_crud.create(item)
```

## 第 8 步:添加您的第一个自定义路由

接下来添加一个新的 API 路由,练习刚学到的内容:

<div class="termy">

```console
$ fastkit addroute users my-first-api
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-api                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-first-api'
```

</div>

服务器会自动重启,您将拥有以下新端点:

- `GET /api/v1/users/` —— 获取所有用户
- `POST /api/v1/users/` —— 创建新用户
- `GET /api/v1/users/{user_id}` —— 获取指定用户
- 等等……

### 测试新路由

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}

$ curl http://127.0.0.1:8000/api/v1/users/
[
  {
    "id": 1,
    "title": "John Doe",
    "description": "Software Developer"
  }
]
```

</div>

## 第 9 步:探索并修改代码

我们做一个小修改,看看代码是如何运作的。

### 修改欢迎信息

在编辑器中打开 `src/main.py`,修改根端点:

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!"}
```

保存文件。由于启用了自动重载,服务器会自动重启。

### 测试改动

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Welcome to my first FastAPI application!"}
```

</div>

### 添加一个新端点

在 `src/main.py` 中加入一个简单的端点:

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### 测试新端点

<div class="termy">

```console
$ curl http://127.0.0.1:8000/hello/World
{"message":"Hello, World!"}

$ curl http://127.0.0.1:8000/hello/FastAPI
{"message":"Hello, FastAPI!"}
```

</div>

## 第 10 步:运行测试

您的项目已预置好测试,运行它们:

<div class="termy">

```console
$ python -m pytest
======================== test session starts ========================
collected 5 items

tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED

======================== 5 passed in 0.45s ========================
```

</div>

## 理解核心概念

### 1. FastAPI 应用结构

FastAPI-fastkit 采用 **模块化架构**:

- **`main.py`**:应用入口与全局端点
- **`api/`**:API 路由组织
- **`core/`**:应用配置与设置
- **`crud/`**:业务逻辑与数据操作
- **`schemas/`**:数据校验与序列化
- **`tests/`**:自动化测试

### 2. 依赖管理

您的项目采用现代 Python 依赖管理:

- **虚拟环境**:隔离的 Python 环境
- **requirements.txt**:列出所有依赖
- **自动安装**:在创建项目时自动安装依赖

### 3. 开发服务器

FastAPI-fastkit 使用 **Uvicorn** 作为 ASGI 服务器:

- **自动重载**:代码变更时自动重启
- **快速启动**:开发迭代迅速
- **可用于生产**:开发与生产使用同一款服务器

### 4. API 文档

FastAPI 会自动生成:

- **OpenAPI 规范**:业界标准的 API 文档
- **Swagger UI**:交互式测试界面
- **ReDoc**:另一种文档视图

## 下一步

恭喜!您已成功完成:

✅ 安装 FastAPI-fastkit
✅ 创建第一个项目
✅ 启动开发服务器
✅ 测试 API 端点
✅ 添加新路由
✅ 修改现有代码
✅ 运行测试

### 继续学习

1. **[您的第一个项目](first-project.md)**:构建一个带有进阶特性的完整博客 API
2. **[添加路由](../user-guide/adding-routes.md)**:学习创建复杂的 API 端点
3. **[使用模板](../user-guide/using-templates.md)**:探索预构建的项目模板

### 多多动手

尝试以下挑战:

1. **添加校验**:修改 schema,加入数据校验规则
2. **自定义响应**:更改路由的响应格式
3. **环境变量**:使用 `.env` 文件做配置
4. **添加中间件**:实现 CORS 或认证
5. **数据库集成**:升级到 STANDARD 栈以获得数据库支持

### 常见问题与解决方案

**服务器无法启动:**

- 检查是否处于项目目录中
- 确认虚拟环境已激活
- 确认代码没有语法错误

**导入错误:**

- 确认所有 `__init__.py` 文件存在
- 检查导入路径是否正确
- 确认正在使用虚拟环境

**端口已被占用:**
```console
$ fastkit runserver --port 8080
```

## 您已掌握的最佳实践

1. **虚拟环境**:始终使用隔离的环境
2. **项目结构**:遵循组织良好的模块化架构
3. **自动重载**:利用开发服务器实现快速迭代
4. **API 文档**:善用自动文档生成能力
5. **测试**:在开发过程中定期运行测试

!!! tip "开发小贴士"
    - 编码时让开发服务器一直运行
    - 使用交互式文档(`/docs`)测试您的 API
    - 关注终端中的报错信息
    - 经常把代码提交到版本控制

您已经准备好用 FastAPI-fastkit 构建出色的 API 了!🚀

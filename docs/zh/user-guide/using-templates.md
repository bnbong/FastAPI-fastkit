# 使用模板

FastAPI-fastkit 提供了一组预构建项目模板,帮助您按不同技术栈快速起步。

## 可用的模板

使用 `list-templates` 命令查看可用模板:

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

## 模板说明

### 1. `fastapi-default`

**简单的 FastAPI 项目**

- 包含必要功能的基础 FastAPI 配置
- 基于 mock 数据的 item 管理
- 适合学习与简单 API
- 内置基本的 CRUD 操作

**适合:**

- FastAPI 新手
- 简单的 Web API
- 学习与原型开发

### 2. `fastapi-async-crud`

**异步 Item 管理 API 服务**

- 完全异步的 FastAPI 应用
- 基于 async/await 的进阶 CRUD 操作
- I/O 操作性能更好
- 基于 mock 数据的异步模式

**适合:**

- 高性能应用
- I/O 密集型操作
- 现代异步 Python 开发

### 3. `fastapi-custom-response`

**带自定义响应系统的异步 Item 管理 API**

- 自定义响应模型与格式化
- 进阶的错误处理
- 支持分页
- 自定义 HTTP 状态码与响应

**适合:**

- 需要特定响应格式的 API
- 复杂的错误处理需求
- 在响应中加入自定义业务逻辑

### 4. `fastapi-dockerized`

**已容器化的 FastAPI Item 管理 API**

- 完整的 Docker 容器化
- 面向生产的部署配置
- 多阶段 Docker 构建
- 基于环境变量的配置

**适合:**

- 生产部署
- 容器化环境
- DevOps 与 CI/CD 管道

### 5. `fastapi-psql-orm`

**集成 PostgreSQL 的已容器化 FastAPI Item 管理 API**

- 集成 PostgreSQL 数据库
- 使用 SQLAlchemy ORM 与 Alembic 迁移
- 通过 Docker Compose 支持本地开发
- 完整的基于数据库的 CRUD 操作

**适合:**

- 数据驱动的应用
- 生产级数据存储
- 复杂的数据关系

### 6. `fastapi-empty`

**极简 FastAPI 项目**

- 极简的 FastAPI 配置
- 不预置任何功能
- 适合从零开始定制开发

**适合:**

- 从零开始
- 依赖最少
- 自定义架构需求

## 基于模板创建项目

使用 `startdemo` 命令基于模板创建项目:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Blog API with PostgreSQL

Available Templates:
           fastapi-default
┌─────────────┬──────────────────────┐
│ Description │ Simple FastAPI       │
│             │ Project              │
│ Stack       │ FastAPI, Uvicorn     │
│ Database    │ Mock Data            │
│ Features    │ Basic CRUD           │
└─────────────┴──────────────────────┘

           fastapi-psql-orm
┌─────────────┬──────────────────────┐
│ Description │ Dockerized FastAPI   │
│             │ Item Management API  │
│             │ with PostgreSQL      │
│ Stack       │ FastAPI, PostgreSQL, │
│             │ SQLAlchemy, Docker   │
│ Database    │ PostgreSQL           │
│ Features    │ Full ORM, Migrations │
└─────────────┴──────────────────────┘

Select template (fastapi-default, fastapi-async-crud, fastapi-custom-response, fastapi-dockerized, fastapi-psql-orm, fastapi-empty): fastapi-psql-orm

           Project Information
┌──────────────┬─────────────────────┐
│ Project Name │ my-blog-api         │
│ Author       │ John Doe            │
│ Author Email │ john@example.com    │
│ Description  │ Blog API with       │
│              │ PostgreSQL          │
└──────────────┴─────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ psycopg2-binary   │
│ Dependency 6 │ python-dotenv     │
│ Dependency 7 │ pytest            │
└──────────────┴───────────────────┘

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

✨ FastAPI project 'my-blog-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## 模板功能对比

| 功能 | 默认模板 | 异步 CRUD | 自定义响应 | Docker 化 | PostgreSQL ORM | 空模板 |
|---------|---------|------------|-----------------|------------|----------------|-------|
| **基础 FastAPI** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Mock 数据** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **异步支持** | 基础 | ✅ | ✅ | ✅ | ✅ | ❌ |
| **自定义响应** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **数据库** | Mock | Mock | Mock | Mock | PostgreSQL | 无 |
| **ORM** | ❌ | ❌ | ❌ | ❌ | SQLAlchemy | ❌ |
| **数据迁移** | ❌ | ❌ | ❌ | ❌ | Alembic | ❌ |
| **测试** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **适合** | 学习 | 性能 | 自定义 API | 生产 | 数据应用 | 自定义 |

## 各模板的专属设置

### 使用 `fastapi-psql-orm`

该模板包含完整的 PostgreSQL 配置。创建完成后：

1. **使用 Docker 启动 PostgreSQL：**

<div class="termy">

```console
$ cd my-blog-api
$ docker-compose up -d postgres
Starting my-blog-api_postgres_1 ... done
```

</div>

2. **运行数据库迁移：**

<div class="termy">

```console
$ source .venv/bin/activate
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> bedcdc35b64a, first alembic
```

</div>

3. **启动 API 服务器：**

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 使用 `fastapi-dockerized`

该模板提供完整的 Docker 支持：

1. **构建 Docker 镜像：**

<div class="termy">

```console
$ cd my-dockerized-api
$ docker build -t my-dockerized-api .
Successfully built abc123def456
Successfully tagged my-dockerized-api:latest
```

</div>

2. **运行容器：**

<div class="termy">

```console
$ docker run -p 8000:8000 my-dockerized-api
INFO:     Uvicorn running on http://0.0.0.0:8000
```

</div>

### 使用 `fastapi-custom-response`

该模板包含进阶的响应处理:

1. **自定义响应模型:**

```python
from src.helper.pagination import PaginatedResponse
from src.schemas.base import StandardResponse

@router.get("/", response_model=PaginatedResponse[Item])
def read_items(skip: int = 0, limit: int = 10):
    items = items_crud.get_multi(skip=skip, limit=limit)
    total = items_crud.count()

    return PaginatedResponse(
        data=items,
        total=total,
        page=skip // limit + 1,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=StandardResponse[Item])
def create_item(item: ItemCreate):
    new_item = items_crud.create(item)
    return StandardResponse(
        data=new_item,
        message="Item created successfully",
        status_code=201
    )
```

2. **增强的错误处理：**

```python
from src.helper.exceptions import ItemNotFoundError, ValidationError

@router.get("/{item_id}", response_model=StandardResponse[Item])
def read_item(item_id: int):
    try:
        item = items_crud.get(item_id)
        return StandardResponse(data=item)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )
```

## 各模板的项目结构

每个模板都遵循统一但又针对自身做了定制的结构:

### `fastapi-default` 结构
```
my-project/
├── src/
│   ├── main.py
│   ├── core/config.py
│   ├── api/
│   │   ├── api.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   └── mocks/mock_items.json
├── tests/
├── scripts/
└── requirements.txt
```

### `fastapi-psql-orm` 结构
```
my-project/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── db.py
│   ├── api/
│   │   ├── api.py
│   │   ├── deps.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   └── utils/
├── tests/
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── requirements.txt
```

## 定制模板

基于模板创建项目后,您可以进行定制:

### 1. 添加新路由

<div class="termy">

```console
$ fastkit addroute posts my-blog-api
$ fastkit addroute users my-blog-api
$ fastkit addroute comments my-blog-api
```

</div>

### 2. 修改配置

按需修改 `src/core/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # 数据库设置（适用于 PostgreSQL 模板）
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # 安全设置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. 添加环境变量

在项目根目录创建 `.env`:

```env
# .env
PROJECT_NAME=My Blog API
VERSION=1.0.0
DEBUG=True

# 数据库设置（适用于 PostgreSQL 模板）
DATABASE_URL=postgresql://user:password@localhost:5432/myblogdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=myblogdb

# 安全设置
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 测试模板

每个模板都附带预配置的测试:

<div class="termy">

```console
$ cd my-blog-api
$ source .venv/bin/activate
$ python -m pytest

======================== test session starts ========================
tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED
======================== 5 passed in 0.23s ========================
```

</div>

## 基于模板的开发流程

### 1. 选择合适的模板

- **学习 / 简单 API**:`fastapi-default`
- **高性能**:`fastapi-async-crud`
- **自定义响应格式**:`fastapi-custom-response`
- **生产部署**:`fastapi-dockerized`
- **数据库应用**:`fastapi-psql-orm`
- **自定义架构**:`fastapi-empty`

### 2. 创建并配置

<div class="termy">

```console
$ fastkit startdemo
# 按提示完成选择
$ cd your-project
$ source .venv/bin/activate
```

</div>

### 3. 开发

<div class="termy">

```console
# 启动开发服务器
$ fastkit runserver

# 运行测试
$ python -m pytest

# 添加新功能
$ fastkit addroute new-resource your-project
```

</div>

### 4. 部署

对于面向生产的模板(`fastapi-dockerized`、`fastapi-psql-orm`):

<div class="termy">

```console
# 构建生产镜像
$ docker build -t your-app .

# 使用 Docker Compose 部署
$ docker-compose up -d
```

</div>

## 最佳实践

### 1. 谨慎选择模板

- 学习时从更简单的模板开始
- 数据驱动应用使用数据库模板
- 生产部署使用 Docker 模板

### 2. 环境管理

- 始终使用 `.env` 文件管理配置
- 切勿将敏感信息提交到版本控制
- 开发与生产使用不同的环境

### 3. 定制策略

- 使用 `fastkit addroute` 添加新路由
- 根据您的业务逻辑改造现有代码
- 保持项目结构清晰

### 4. 测试

- 开发过程中持续运行测试
- 为新实现的功能补充测试
- 把内置的测试结构当作参考模板

## 故障排查

### 数据库连接问题(PostgreSQL 模板)

若无法连接 PostgreSQL:

1. **检查 Docker 是否在运行:**

   <div class="termy">
   ```console
   $ docker ps
   ```
   </div>

2. **检查 PostgreSQL 容器:**

   <div class="termy">
   ```console
   $ docker-compose logs postgres
   ```
   </div>

3. **检查环境变量:**

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Docker 构建失败

若 Docker 构建失败:

1. **检查 Dockerfile 语法**
2. **确认所有文件都存在**
3. **确认 Docker 守护进程已启动**

### 依赖缺失

若出现 import 错误:

1. **激活虚拟环境:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

2. **安装依赖:**
   <div class="termy">
   ```console
   $ pip install -r requirements.txt
   ```
   </div>

## 下一步

现在您已了解模板:

1. **[您的第一个项目](../tutorial/first-project.md)**:构建一个完整的应用
2. **[添加路由](adding-routes.md)**:扩展基于模板创建的项目
3. **[CLI 参考](cli-reference.md)**:掌握所有可用命令

!!! tip "模板小贴士"
    - 模板是优秀的起点,而非最终方案
    - 根据具体需求自定义模板
    - 阅读模板代码,学习 FastAPI 最佳实践
    - 使用版本控制记录您的修改

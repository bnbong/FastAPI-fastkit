# 常见问题

围绕 FastAPI-fastkit 的常见问答。

## 安装与配置

### 问:支持哪些 Python 版本?

**答:** FastAPI-fastkit 需要 **Python 3.12 及以上**。我们建议使用最新的稳定版 Python,以获得最佳体验。

<div class="termy">

```console
$ python --version
Python 3.12.1

$ pip install fastapi-fastkit
```

</div>

### 问:如何安装 FastAPI-fastkit?

**答:** 使用 pip 即可安装:

<div class="termy">

```console
# Latest stable version
$ pip install fastapi-fastkit

# Development version from GitHub
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git

# Specific version
$ pip install fastapi-fastkit==1.0.0
```

</div>

### 问:安装时出现权限错误失败

**答:** 请尝试在虚拟环境中安装,或以当前用户身份安装:

<div class="termy">

```console
# Create virtual environment
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # On Windows: fastapi-env\Scripts\activate

# Install in virtual environment
$ pip install fastapi-fastkit

# Or install for current user only
$ pip install --user fastapi-fastkit
```

</div>

### 问:安装后找不到 `fastkit` 命令

**答:** 这通常意味着安装目录不在您的 PATH 中:

<div class="termy">

```console
# Check if installed
$ pip show fastapi-fastkit

# Find installation location
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__file__)"

# Try running directly
$ python -m fastapi_fastkit --version

# Or add to PATH (Linux/macOS)
$ export PATH="$HOME/.local/bin:$PATH"
```

</div>

## 创建项目

### 问:可选哪些依赖栈?

**答:** FastAPI-fastkit 提供三种依赖栈:

- **MINIMAL**:FastAPI、Uvicorn、Pydantic、Pydantic-Settings(基础 Web API)
- **STANDARD**:再加上 SQLAlchemy、Alembic、pytest(数据库支持)
- **FULL**:再加上 Redis、Celery(后台任务)

!!! tip "默认包管理器"
    默认包管理器是 `uv`,依赖安装更快。您也可以选择 `pip`、`pdm` 或 `poetry`。

<div class="termy">

```console
$ fastkit init
# Select your preferred stack during project creation
```

</div>

### 问:可以自定义项目模板吗?

**答:** 可以!您可以:

1. **使用现有模板**(`fastkit startdemo`)
2. **创建自定义模板** —— 在现有模板基础上复制并修改
3. **逐步添加路由**(`fastkit addroute`)

<div class="termy">

```console
# Use pre-built templates
$ fastkit list-templates
$ fastkit startdemo

# Add routes to existing project
$ fastkit addroute users .          # Add 'users' route to current directory
$ fastkit addroute users my-project # Add 'users' route to 'my-project'
```

</div>

### 问:项目名称有什么格式要求?

**答:** 项目名称必须是合法的 Python 标识符:

- ✅ `my-api`、`blog_system`、`UserService`
- ❌ `my api`、`123project`、`project-name!`

<div class="termy">

```console
$ fastkit init
Enter the project name: my_awesome_api  # Valid
Enter the project name: my-awesome-api  # Valid (hyphens converted to underscores)
```

</div>

### 问:创建项目失败,提示「directory already exists」

**答:** 项目目录已经存在。处理方式:

1. **换一个名字**
2. **删除已有目录**(确认安全后)
3. **使用其他输出位置**

<div class="termy">

```console
# Check if directory exists
$ ls my-project

# Remove if safe (CAUTION!)
$ rm -rf my-project

# Or create in different location
$ mkdir projects
$ cd projects
$ fastkit init
```

</div>

### 问:如何用交互模式创建项目?

**答:** 使用 `fastkit init --interactive` 进入引导式逐步项目创建,并自动智能选择功能:

<div class="termy">

```console
$ fastkit init --interactive
```

</div>

交互模式会依次带您完成以下步骤:

1. **项目信息** —— 名称、作者、邮箱、描述。
2. **架构预设** —— 选定项目布局。推荐默认是 `domain-starter`;直接回车即可接受。每种预设的具体布局,以及哪些功能组合需要手动接入,详见 [架构预设矩阵](preset-feature-matrix.md)。
3. **功能选择** —— 数据库、认证、后台任务、缓存、监控、测试、工具、部署。
4. **包管理器与自定义包** —— pip / uv / pdm / poetry,以及您想固定下来的额外依赖。
5. **确认** —— 在项目创建之前展示一张总结表,列出全部选择(包含架构预设)。

交互模式提供丰富的功能目录可选:

| 类别 | 可选项 |
|----------|-------------------|
| **架构** | minimal、single-module、classic-layered、**domain-starter**(推荐默认) |
| **数据库** | PostgreSQL、MySQL、MongoDB、Redis、SQLite |
| **认证** | JWT、OAuth2、FastAPI-Users、基于会话 |
| **后台任务** | Celery、Dramatiq |
| **测试** | Basic(pytest)、Coverage、Advanced(附带 faker、factory-boy) |
| **缓存** | 基于 fastapi-cache2 的 Redis |
| **监控** | Loguru、OpenTelemetry、Prometheus |
| **工具** | CORS、限流、分页、WebSocket |
| **部署** | Docker、docker-compose,自动生成配置 |

交互模式会自动生成:

- 一个集成所选功能的 `main.py`
- 当所选选项支持代码生成时,会生成数据库与认证的配置文件(例如数据库选 PostgreSQL/MySQL/SQLite/MongoDB,认证选 JWT/FastAPI-Users);其他选项仅安装必要的包
- 与所选部署选项匹配的部署文件(选了 `Docker` 会生成 `Dockerfile`,选了 `docker-compose` 会生成 `docker-compose.yml`)
- 基于所选测试选项的测试配置(只有选择 `Coverage` 或 `Advanced` 时才会包含覆盖率设置)

### 问:如何查看交互模式可用的功能?

**答:** 使用 `list-features` 命令,可以展示所有可用功能及其包:

<div class="termy">

```console
$ fastkit list-features
# Shows all available features organized by category
# with their associated packages
```

</div>

这可以帮助您理解每个功能选择会安装哪些包。

## 路由开发

### 问:如何为路由加上认证?

**答:** 创建一个用于认证的依赖:

```python
# src/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # Verify token and return user
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return get_user_from_token(token)

# src/api/routes/users.py
@router.get("/me")
def get_current_user_profile(user = Depends(get_current_user)):
    return user
```

### 问:如何为项目添加数据库模型?

**答:** 在 STANDARD 或 FULL 栈中,创建 SQLAlchemy 模型:

```python
# src/models/users.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### 问:如何为请求数据加校验?

**答:** 在 schema 中使用 Pydantic 模型:

```python
# src/schemas/users.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### 问:如何处理文件上传?

**答:** 使用 FastAPI 的 `UploadFile`:

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    # Save file
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

## 模板

### 问:有哪些可用模板?

**答:** FastAPI-fastkit 自带多个预制模板:

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-default         │ Simple FastAPI Project            │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-custom-response │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI API            │
│ fastapi-empty           │ Minimal FastAPI Project           │
│ fastapi-mcp             │ MCP (Model Context Protocol) API  │
│ fastapi-psql-orm        │ PostgreSQL FastAPI API            │
│ fastapi-single-module   │ Single-file FastAPI Project       │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

### 问:如何使用指定模板?

**答:** 使用 `startdemo` 命令:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Select template: fastapi-psql-orm
```

</div>

### 问:可以创建自定义模板吗?

**答:** 可以!创建目录结构并使用模板变量:

```
my-template/
├── src/
│   └── main.py-tpl
├── requirements.txt-tpl
└── template.yaml
```

```python
# main.py-tpl
from fastapi import FastAPI

app = FastAPI(title="{{PROJECT_NAME}}")

@app.get("/")
def read_root():
    return {"message": "Hello from {{PROJECT_NAME}}!"}
```

### 问:如何修改已有模板?

**答:** 模板位于 `fastapi_project_template` 目录,您可以:

1. **fork 仓库** 并修改模板
2. **基于现有模板创建自定义模板**
3. **在创建项目后覆盖特定文件**

## 开发服务器

### 问:如何启动开发服务器?

**答:** 在项目目录中使用 `runserver` 命令:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate  # Activate virtual environment
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 问:服务器无法启动 —— 「Address already in use」

**答:** 8000 端口被占用。换一个端口,或结束已有进程:

<div class="termy">

```console
# Use different port
$ fastkit runserver --port 8080

# Or find and kill existing process
$ lsof -ti:8000 | xargs kill -9

# On Windows
$ netstat -ano | findstr :8000
$ taskkill /PID <PID> /F
```

</div>

### 问:自动重载不生效

**答:** 确认您处在项目目录中,并已激活虚拟环境:

<div class="termy">

```console
# Check current directory
$ pwd
/path/to/my-project

# Check virtual environment
$ which python
/path/to/my-project/.venv/bin/python

# Start with explicit reload
$ fastkit runserver --reload
```

</div>

### 问:生产环境下如何配置服务器?

**答:** **不要**在生产环境使用开发服务器,而应:

```python
# Use gunicorn or similar WSGI server
$ pip install gunicorn
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Docker with the fastapi-dockerized template
$ fastkit startdemo  # Select fastapi-dockerized
$ docker build -t my-app .
$ docker run -p 8000:8000 my-app
```

## 性能与优化

### 问:如何提升 API 性能?

**答:** 多种优化策略:

1. 对 I/O 操作使用 **async/await**
2. 为开销大的操作**加缓存**
3. **优化数据库查询**
4. 用**后台任务**处理重活

```python
# Async endpoint
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await users_service.get_user_async(user_id)
    return user

# Background task
from fastapi import BackgroundTasks

@router.post("/send-email")
def send_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(send_notification_email, email)
    return {"message": "Email will be sent in background"}
```

### 问:如何加入缓存?

**答:** 使用 Redis 做缓存:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)
async def get_expensive_data():
    # Expensive operation
    return complex_calculation()
```

### 问:如何处理大量并发请求?

**答:** 使用合适的服务器配置:

<div class="termy">

```console
# Development
$ fastkit runserver --workers 1  # Single worker for development

# Production
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
$ uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

</div>

## 测试

### 问:如何运行测试?

**答:** 在项目目录中使用 pytest:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate
$ python -m pytest

# With coverage
$ python -m pytest --cov=src

# Specific test file
$ python -m pytest tests/test_users.py

# With verbose output
$ python -m pytest -v
```

</div>

### 问:如何编写 API 测试?

**答:** 使用 FastAPI 的 test client:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user():
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
```

### 问:如何对外部依赖进行 mock?

**答:** 使用 pytest fixture 与 mock:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    with patch('src.database.get_db') as mock_db:
        mock_db.return_value = Mock()
        yield mock_db

def test_user_creation_with_mock_db(mock_database):
    # Test with mocked database
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
```

## 参与贡献

### 问:如何为 FastAPI-fastkit 做贡献?

**答:** 按以下步骤即可:

1. 在 GitHub 上 **fork 仓库**
2. **配置开发环境**
3. **创建特性分支**
4. **进行改动**并附上测试
5. **提交 Pull Request**

<div class="termy">

```console
$ git clone https://github.com/yourusername/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make dev-setup  # Set up development environment
$ git checkout -b feature/my-feature
# Make changes...
$ make dev-check  # Format, lint, and test
$ git commit -m "feat: add new feature"
$ git push origin feature/my-feature
```

</div>

### 问:Pull Request 应当包含什么?

**答:** 每个 Pull Request 都应包含:

- [ ] **对改动的清晰描述**
- [ ] 新功能对应的**测试**
- [ ] 必要时更新**文档**
- [ ] **遵循代码规范**
- [ ] **所有检查通过**

### 问:如何报告 bug?

**答:** 在 GitHub 上创建 issue,包含:

1. **bug 描述**与预期行为
2. **复现步骤**
3. **环境信息**(操作系统、Python 版本等)
4. **错误信息**或日志
5. **最小可复现示例**(如可能)

### 问:如何提交新特性请求?

**答:** 打开一个特性请求 issue,包含:

1. 对特性的**清晰描述**
2. **使用场景**与动机
3. **建议的实现方式**(可选)
4. **类似特性的例子**

## 故障排查

### 问:出现 import 错误

**答:** 检查您的 Python path 与虚拟环境:

<div class="termy">

```console
# Check virtual environment is activated
$ which python
/path/to/project/.venv/bin/python

# Check Python path
$ python -c "import sys; print(sys.path)"

# Reinstall in editable mode (for development)
$ pip install -e .
```

</div>

### 问:数据库连接问题

**答:** 对于带数据库的模板,请确认数据库已运行:

<div class="termy">

```console
# PostgreSQL template
$ docker-compose up -d postgres  # Start database
$ alembic upgrade head            # Run migrations

# Check connection
$ docker-compose logs postgres
```

</div>

### 问:找不到模板文件

**答:** 这通常意味着模板路径有问题:

<div class="termy">

```console
# Check available templates
$ fastkit list-templates

# Check template directory
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__path__)"

# Reinstall if templates missing
$ pip uninstall fastapi-fastkit
$ pip install fastapi-fastkit
```

</div>

### 问:pre-commit 钩子失败

**答:** 安装并运行钩子:

<div class="termy">

```console
$ pip install pre-commit
$ pre-commit install
$ pre-commit run --all-files

# Fix formatting issues
$ black src/ tests/
$ isort src/ tests/
```

</div>

### 问:CI 测试失败,但本地通过

**答:** 常见原因与解决办法:

1. **环境差异**:核对 Python 版本是否一致
2. **缺少依赖**:确认测试依赖已安装
3. **路径问题**:使用绝对 import
4. **时序问题**:在异步测试中加入合理的等待

<div class="termy">

```console
# Test with same Python version as CI
$ python3.12 -m pytest

# Check for missing dependencies
$ pip install -r requirements-dev.txt

# Run tests in isolated environment
$ tox
```

</div>

## 获取帮助

### 问:在哪里获取帮助?

**答:** 多种渠道:

- **GitHub Issues**:报告 bug 与请求特性
- **GitHub Discussions**:提问与社区交流
- **文档**:用户指南与教程
- **代码示例**:查看已有模板与测试

### 问:如何掌握最新动态?

**答:** 关注项目更新:

- 在 GitHub 上 **watch 仓库**
- 通过 **releases** 了解新特性
- 阅读 **changelog**,关注破坏性变更
- 在文档中**遵循最佳实践**

!!! tip "进阶小贴士"
    - 始终在 Python 项目中使用虚拟环境
    - 保持 FastAPI-fastkit 安装为最新
    - 用 `fastkit --help` 查看可用命令
    - 卡住时回到文档查阅
    - 不要犹豫,在 GitHub Discussions 上多多提问

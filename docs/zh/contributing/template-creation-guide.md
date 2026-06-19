# FastAPI 模板创建指南

为 FastAPI-fastkit 添加新 FastAPI 项目模板的完整指南。

## 🎯 总览

添加新模板分为 5 个步骤:

1. **📋 规划与设计** —— 明确模板用途与结构
2. **🏗️ 模板实现** —— 创建必需的结构与文件
3. **🔍 本地校验** —— 用 inspector 校验模板
4. **📚 文档** —— 编写 README 与使用指南
5. **🚀 提交与评审** —— 创建 PR 并由社区评审

## 📋 第 1 步:规划与设计

### 明确模板用途

在创建新模板之前,请回答以下问题:

- **该模板的独特价值是什么?**
- **它与现有模板的差异在哪里?**
- **目标用户群体是谁?**
- **会包含怎样的技术栈?**

### 模板命名规范

```
fastapi-{purpose}-{stack}
```

示例:

- `fastapi-microservice`(微服务模板)
- `fastapi-graphql`(GraphQL 集成模板)
- `fastapi-auth-jwt`(JWT 认证模板)

### 技术栈规划

事先定义好要包含的主要技术:

```yaml
# Example: fastapi-microservice template
core_dependencies:
  - fastapi
  - uvicorn
  - pydantic
  - pydantic-settings

additional_features:
  - sqlalchemy (ORM)
  - alembic (migrations)
  - redis (caching)
  - celery (background tasks)
  - pytest (testing)

development_tools:
  - black (code formatting)
  - isort (import sorting)
  - mypy (type checking)
  - pre-commit (Git hooks)
```

## 🏗️ 第 2 步:模板实现

### 必需的目录结构

```
fastapi-{template-name}/
├── src/                          # Application source code
│   ├── main.py-tpl              # ✅ FastAPI app entry point (required)
│   ├── __init__.py-tpl
│   ├── api/                     # API routers
│   │   ├── __init__.py-tpl
│   │   ├── api.py-tpl           # Main API router
│   │   └── routes/              # Individual routes
│   │       ├── __init__.py-tpl
│   │       └── items.py-tpl     # Example route
│   ├── core/                    # Core configuration
│   │   ├── __init__.py-tpl
│   │   └── config.py-tpl        # Settings management
│   ├── crud/                    # CRUD logic
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   ├── schemas/                 # Pydantic models
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   └── utils/                   # Utility functions
│       ├── __init__.py-tpl
│       └── helpers.py-tpl
├── tests/                       # ✅ Tests (required)
│   ├── __init__.py-tpl
│   ├── conftest.py-tpl         # pytest configuration
│   └── test_items.py-tpl       # Example tests
├── scripts/                     # Scripts
│   ├── format.sh-tpl           # Code formatting
│   ├── lint.sh-tpl             # Linting
│   ├── run-server.sh-tpl       # Server execution
│   └── test.sh-tpl             # Test execution
├── pyproject.toml-tpl           # ✅ Primary metadata (PEP 621, preferred)
├── setup.py-tpl                # 🟡 Legacy metadata (accepted for back-compat)
├── requirements.txt-tpl         # 🟡 Optional when pyproject declares deps
├── setup.cfg-tpl               # Development tools configuration
├── README.md-tpl               # ✅ Project documentation (required)
├── .env-tpl                    # Environment variables template
└── .gitignore-tpl              # Git ignore file
```

**最少必备文件。** 一个模板至少要提供:

- `tests/` 目录
- `README.md-tpl`
- 至少一份元数据文件:`pyproject.toml-tpl`(推荐,PEP 621)或 `setup.py-tpl`(遗留,仍可接受)
- 在以下至少一个位置声明 `fastapi` 依赖:`pyproject.toml-tpl` 的 `[project].dependencies`、`requirements.txt-tpl`,或 `setup.py-tpl` 的 `install_requires`

当 `pyproject.toml-tpl` 已声明 `[project].dependencies` 时,`requirements.txt-tpl` 不再是严格必需的。新模板**建议**采用 `pyproject.toml-tpl` 作为主要元数据文件。

### 文件编写指南

#### 1. 编写 main.py-tpl

```python
"""
FastAPI application entry point

This file is the main application for the <project_name> project created with FastAPI-fastkit.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api import api_router
from core.config import settings

# Create FastAPI app (required for inspector validation)
app = FastAPI(
    title="<project_name>",
    description="Project created with FastAPI-fastkit",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello from <project_name>!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. 编写 pyproject.toml-tpl(推荐)

新模板应使用 PEP 621 的 `pyproject.toml-tpl` 来声明元数据与依赖。该文件至少要有一个 `[project]` 段,内含 `name`、`version`、`description`,以及包含 `fastapi` 的 `dependencies` 列表。模板还必须携带两个 FastAPI-fastkit 身份标识,这样 `is_fastkit_project()` 才能在用户工作区中把生成的项目与无关的 FastAPI 项目区分开:

- 在 `description` 中带 `[FastAPI-fastkit templated]` 前缀
- 专门提供 `[tool.fastapi-fastkit]` 表,并设置 `managed = true`

识别时只需任一标识匹配即可(不区分大小写)。若模板遗漏了它们,元数据注入会在项目生成时自动补上,但作者**应当显式包含**它们。

```toml
[project]
name = "<project_name>"
version = "0.1.0"
description = "[FastAPI-fastkit templated] <description>"
authors = [
    {name = "<author>", email = "<author_email>"},
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.28.0",
]

[tool.fastapi-fastkit]
managed = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 3. 编写 requirements.txt-tpl(可选)

当 `pyproject.toml-tpl` 已经声明 `[project].dependencies` 时为可选。对于偏好纯 `pip` 工作流的模板,仍然有用。

```txt
# FastAPI core dependencies (required)
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Data validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Environment variable management
python-dotenv==1.0.0

# Database (if needed)
sqlalchemy==2.0.23
alembic==1.13.0

# Development tools
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Code quality
black==23.11.0
isort==5.12.0
mypy==1.7.1
```

#### 4. 编写 setup.py-tpl(遗留 —— 在已有 pyproject 时为可选)

保留它是为了兼容遗留模板。如果新模板已附带 `pyproject.toml-tpl`,则无需此文件。

```python
"""
<project_name> package setup

Project created with FastAPI-fastkit.
"""
from setuptools import find_packages, setup

# Dependencies list (type annotation required)
install_requires: list[str] = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

setup(
    name="<project_name>",
    version="1.0.0",
    description="[FastAPI-fastkit templated] <description>",  # Identity marker used by is_fastkit_project()
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="<author>",
    author_email="<author_email>",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
```

#### 5. 编写测试文件

```python
# tests/test_items.py-tpl
"""
Items API test module
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_item():
    """Test item creation"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]

def test_read_items():
    """Test reading items list"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 🔍 第 3 步:本地校验

### 运行自动校验脚本

新模板准备好后,用以下命令进行校验:

```bash
# Validate all templates
make inspect-templates

# Validate specific template only
make inspect-template TEMPLATES="fastapi-your-template"

# Validate with verbose output
python scripts/inspect-templates.py --templates "fastapi-your-template" --verbose
```

!!! note

    您提交 PR 后,**Template PR Inspection** 工作流会自动运行并校验您的模板改动,反馈会直接出现在 PR 上。

### 校验清单

inspector 会自动校验以下项目:

#### ✅ 文件结构校验

- [ ] 存在 `tests/` 目录
- [ ] 存在 `README.md-tpl` 文件
- [ ] 至少存在 `pyproject.toml-tpl`(推荐)或 `setup.py-tpl`(遗留)之一

#### ✅ 文件扩展名校验

- [ ] 所有 Python 文件使用 `.py-tpl` 扩展名
- [ ] 不存在 `.py` 扩展名的文件

#### ✅ 依赖校验

- [ ] `fastapi` 至少声明于以下其一:
    - [ ] `pyproject.toml-tpl` 的 `[project].dependencies`(推荐)
    - [ ] `requirements.txt-tpl`
    - [ ] `setup.py-tpl` 的 `install_requires`

#### ✅ FastAPI 实现校验

- [ ] `main.py-tpl` 中存在 `FastAPI` 的 import
- [ ] `main.py-tpl` 中存在形如 `app = FastAPI()` 的应用创建

#### ✅ 测试执行校验

- [ ] 成功创建虚拟环境
- [ ] 成功安装依赖
- [ ] 所有 pytest 测试通过

#### ✅ 自动化模板测试

FastAPI-fastkit 自带**自动化模板测试**,会对所有模板执行完整测试:

**测试覆盖范围:**

- ✅ 模板创建过程
- ✅ 项目元数据注入
- ✅ 虚拟环境搭建
- ✅ 依赖安装(覆盖所有包管理器)
- ✅ 基本项目结构校验
- ✅ FastAPI 项目识别

**测试执行:**
```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Test specific template
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v
```

**模板测试自动发现:**
新模板会被**自动发现**并测试,无需手动配置:

1. ✅ **零配置**:加入模板即可自动测试
2. ✅ **一致的测试**:对所有模板使用相同的质量标准
3. ✅ **多种包管理器**:覆盖 UV、PDM、Poetry 与 PIP
4. ✅ **全面校验**:结构、元数据与功能性都会检查

**这对您意味着什么:**

- 🚀 **`FastAPI-fastkit` 主源码中无需新增测试**:您的模板会被自动测试
- ⚡ **开发更快**:专注模板内容,而不是测试配置
- 🛡️ **质量保证**:所有模板拥有一致的测试体验
- 🔄 **CI/CD 集成**:Pull Request 中自动测试

**仍需手动测试的内容:**

- 🧪 **模板特有的功能**:业务逻辑与定制特性
- 🔧 **集成测试**:外部服务与复杂工作流
- 📱 **端到端场景**:完整的用户流程

**测试最佳实践:**
```console
# 1. Test your template locally
$ fastkit startdemo your-template-name

# 2. Run automated tests
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v

# 3. Test with different package managers
$ fastkit startdemo your-template-name --package-manager poetry
$ fastkit startdemo your-template-name --package-manager pdm
$ fastkit startdemo your-template-name --package-manager uv
```

### 手动校验清单

在自动校验之外,还要手动检查以下项:

#### 🔧 代码质量

- [ ] 代码遵循 PEP 8 风格指南
- [ ] 合理使用类型注解
- [ ] 变量与函数命名有意义
- [ ] 注释与 docstring 得当

#### 🏗️ 架构

- [ ] 关注点分离(API、业务逻辑、数据访问相互独立)
- [ ] 组件设计可复用
- [ ] 结构便于扩展
- [ ] 落实安全最佳实践

#### 📚 文档

- [ ] README.md-tpl 遵循 PROJECT_README_TEMPLATE.md 的格式
- [ ] 明确说明安装与运行方式
- [ ] 提供 API 文档(OpenAPI / Swagger)
- [ ] 解释环境变量

## 📚 第 4 步:文档

### 编写 README.md-tpl

参照 [PROJECT_README_TEMPLATE.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/PROJECT_README_TEMPLATE.md) 指南编写。

### 编写模板说明文档

在 `src/fastapi_fastkit/fastapi_project_template/README.md` 中加入对新模板的说明:

```markdown
## fastapi-your-template

Write a brief description and use cases for your new template here.

### Features:
- Feature 1
- Feature 2
- Feature 3

### Use Cases:
- Use case 1
- Use case 2
```

## 🚀 第 5 步:提交与评审

### 创建 PR 前的清单

- [ ] 全部自动校验通过(`make inspect-templates`)
- [ ] 完成代码格式化(`make format`)
- [ ] 静态检查通过(`make lint`)
- [ ] 所有测试通过(`make test`)
- [ ] 文档已完成
- [ ] 遵循 CONTRIBUTING.md 的规范

### PR 标题与描述

```
[TEMPLATE] Add fastapi-{template-name} template

## Overview
Adds a new {purpose} template.

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Validation Results
- [ ] Inspector validation passed
- [ ] All tests passed
- [ ] Documentation completed

## Usage Example
\```bash
fastkit startdemo
# Select template: fastapi-{template-name}
\```

## Related Issues
Closes #issue-number
```

### 评审流程

1. **自动校验**:GitHub Actions 自动校验模板
    - **Template PR Inspection**:对修改模板的 PR 运行 `inspect-changed-templates.py`
    - **Weekly Inspection**:每周三对所有模板进行完整校验
2. **代码评审**:维护者与社区评审代码
3. **测试**:在不同环境中测试模板
4. **文档评审**:核对文档的准确性与完整性
5. **批准与合并**:所有要求满足后合并到 main 分支

!!! note

    您会自动收到带有校验结果的 PR 评论。在请求评审前先确认这些结果!

## 🎯 最佳实践

### 安全考量

- 用环境变量管理敏感信息
- 合理配置 CORS
- 校验输入数据
- 预防 SQL 注入

### 性能优化

- 善用异步处理
- 优化数据库查询
- 合理的缓存策略
- 配置响应压缩

### 可维护性

- 代码结构清晰
- 测试覆盖全面
- 文档详尽
- 配置日志与监控

## 🆘 需要帮助?

- 📖 [开发环境配置指南](development-setup.md)
- 📋 [代码规范](code-guidelines.md)
- 💬 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- 📧 [联系维护者](mailto:bbbong9@gmail.com)

为 FastAPI-fastkit 社区添加新模板是非常宝贵的贡献。
您的创意与付出会对其他开发者大有帮助!🚀

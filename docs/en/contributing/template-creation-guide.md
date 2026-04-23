# FastAPI Template Creation Guide

A comprehensive guide for adding new FastAPI project templates to FastAPI-fastkit.

## 🎯 Overview

Adding a new template follows a 5-step process:

1. **📋 Planning & Design** - Define template purpose and structure
2. **🏗️ Template Implementation** - Create required structure and files
3. **🔍 Local Validation** - Validate template using inspector
4. **📚 Documentation** - Write README and usage guide
5. **🚀 Submission & Review** - Create PR and community review

## 📋 Step 1: Planning & Design

### Define Template Purpose

Before creating a new template, answer these questions:

- **What is the unique value of this template?**
- **How does it differentiate from existing templates?**
- **Which user group is the target audience?**
- **What technology stack will it include?**

### Template Naming Convention

```
fastapi-{purpose}-{stack}
```

Examples:
- `fastapi-microservice` (Microservice template)
- `fastapi-graphql` (GraphQL integration template)
- `fastapi-auth-jwt` (JWT authentication template)

### Technology Stack Planning

Pre-define the main technologies to include:

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

## 🏗️ Step 2: Template Implementation

### Required Directory Structure

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

**Minimum required files.** A template must provide:

- `tests/` directory
- `README.md-tpl`
- At least one metadata file: `pyproject.toml-tpl` (preferred, PEP 621) or
  `setup.py-tpl` (legacy, still accepted)
- A declaration of `fastapi` as a dependency in at least one of:
  `pyproject.toml-tpl` `[project].dependencies`, `requirements.txt-tpl`, or
  `setup.py-tpl` `install_requires`

`requirements.txt-tpl` is no longer strictly required when `pyproject.toml-tpl`
declares `[project].dependencies`. Modern templates SHOULD adopt
`pyproject.toml-tpl` as their primary metadata file.

### File Writing Guide

#### 1. Writing main.py-tpl

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

#### 2. Writing pyproject.toml-tpl (preferred)

Modern templates should declare metadata and dependencies with a PEP 621
`pyproject.toml-tpl`. At minimum the file must expose a `[project]` section with
`name`, `version`, a `description`, and a `dependencies` list that includes
`fastapi`. Templates must also carry two FastAPI-fastkit identity markers so
`is_fastkit_project()` can tell generated projects apart from unrelated FastAPI
projects in the user's workspace:

- `[FastAPI-fastkit templated]` prefix in `description`
- A dedicated `[tool.fastapi-fastkit]` table with `managed = true`

Detection accepts either marker (matching is case-insensitive). Metadata
injection will add both at project generation time if a template omits them,
but authors should include them explicitly.

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

#### 3. Writing requirements.txt-tpl (optional)

Optional when `pyproject.toml-tpl` declares `[project].dependencies`. Still
useful for templates that prefer `pip`-only workflows.

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

#### 4. Writing setup.py-tpl (legacy — optional when pyproject is present)

Retained for legacy templates. New templates do not need this file if they
ship `pyproject.toml-tpl`.

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

#### 5. Writing Test Files

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

## 🔍 Step 3: Local Validation

### Running Automated Validation Scripts

Once your new template is ready, validate it with these commands:

```bash
# Validate all templates
make inspect-templates

# Validate specific template only
make inspect-template TEMPLATES="fastapi-your-template"

# Validate with verbose output
python scripts/inspect-templates.py --templates "fastapi-your-template" --verbose
```

!!! note

    When you submit a PR, the **Template PR Inspection** workflow will automatically run and validate your template changes. You'll receive feedback directly on your PR.

### Validation Checklist

The inspector automatically validates the following items:

#### ✅ File Structure Validation

- [ ] `tests/` directory exists
- [ ] `README.md-tpl` file exists
- [ ] At least one of `pyproject.toml-tpl` (preferred) or `setup.py-tpl`
      (legacy) exists

#### ✅ File Extension Validation

- [ ] All Python files use `.py-tpl` extension
- [ ] No `.py` extension files exist

#### ✅ Dependencies Validation

- [ ] `fastapi` is declared in at least one of:
  - [ ] `pyproject.toml-tpl` under `[project].dependencies` (preferred)
  - [ ] `requirements.txt-tpl`
  - [ ] `setup.py-tpl` under `install_requires`

#### ✅ FastAPI Implementation Validation

- [ ] `FastAPI` import exists in `main.py-tpl`
- [ ] App creation like `app = FastAPI()` exists in `main.py-tpl`

#### ✅ Test Execution Validation

- [ ] Virtual environment creation successful
- [ ] Dependencies installation successful
- [ ] All pytest tests pass

#### ✅ Automated Template Testing

FastAPI-fastkit includes **automated template testing** that runs comprehensive tests for all templates:

**Test Coverage:**
- ✅ Template creation process
- ✅ Project metadata injection
- ✅ Virtual environment setup
- ✅ Dependency installation (all package managers)
- ✅ Basic project structure validation
- ✅ FastAPI project identification

**Test Execution:**
```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Test specific template
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v
```

**Template Test Discovery:**
New templates are **automatically discovered** and tested without manual configuration:

1. ✅ **Zero Configuration**: Add template → automatic testing
2. ✅ **Consistent Testing**: Same quality standards for all templates
3. ✅ **Multiple Package Managers**: Tests with UV, PDM, Poetry, and PIP
4. ✅ **Comprehensive Validation**: Structure, metadata, and functionality checks

**What This Means for You:**
- 🚀 **No Additional Test Files at `FastAPI-fastkit`'s main source testcases**: Your template is tested automatically
- ⚡ **Faster Development**: Focus on template content, not test setup
- 🛡️ **Quality Assurance**: Consistent testing across all templates
- 🔄 **CI/CD Integration**: Automatic testing in pull requests

**Manual Testing Still Required:**
- 🧪 **Template-specific functionality**: Business logic and custom features
- 🔧 **Integration testing**: External services and complex workflows
- 📱 **End-to-end scenarios**: Complete user workflows

**Testing Best Practices:**
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

### Manual Validation Checklist

In addition to automated validation, manually check the following items:

#### 🔧 Code Quality

- [ ] Code follows PEP 8 style guide
- [ ] Appropriate type hints usage
- [ ] Meaningful variable and function names
- [ ] Proper comments and docstrings

#### 🏗️ Architecture

- [ ] Separation of concerns (API, business logic, data access separation)
- [ ] Reusable component design
- [ ] Scalable structure
- [ ] Security best practices applied

#### 📚 Documentation

- [ ] README.md-tpl follows PROJECT_README_TEMPLATE.md format
- [ ] Installation and execution methods specified
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Environment variables explanation

## 📚 Step 4: Documentation

### Writing README.md-tpl

Write based on [PROJECT_README_TEMPLATE.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/PROJECT_README_TEMPLATE.md) guide.

### Writing Template Description Documentation

Add a description of your new template to `src/fastapi_fastkit/fastapi_project_template/README.md`:

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

## 🚀 Step 5: Submission & Review

### Pre-PR Creation Checklist

- [ ] All automated validation passed (`make inspect-templates`)
- [ ] Code formatting completed (`make format`)
- [ ] Linting checks passed (`make lint`)
- [ ] All tests passed (`make test`)
- [ ] Documentation completed
- [ ] CONTRIBUTING.md guidelines followed

### PR Title and Description

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

### Review Process

1. **Automated Validation**: GitHub Actions automatically validates the template
   - **Template PR Inspection**: Runs `inspect-changed-templates.py` on PRs modifying templates
   - **Weekly Inspection**: Full template validation every Wednesday
2. **Code Review**: Maintainers and community review the code
3. **Testing**: Template is tested in various environments
4. **Documentation Review**: Review documentation accuracy and completeness
5. **Approval & Merge**: Merge to main branch when all requirements are satisfied

!!! note

    You'll receive automatic PR comments with validation results. Check these before requesting a review!

## 🎯 Best Practices

### Security Considerations

- Manage sensitive information with environment variables
- Proper CORS configuration
- Input data validation
- SQL injection prevention

### Performance Optimization

- Utilize asynchronous processing
- Optimize database queries
- Appropriate caching strategies
- Response compression settings

### Maintainability

- Clear code structure
- Comprehensive test coverage
- Detailed documentation
- Logging and monitoring setup

## 🆘 Need Help?

- 📖 [Development Setup Guide](development-setup.md)
- 📋 [Code Guidelines](code-guidelines.md)
- 💬 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- 📧 [Contact Maintainer](mailto:bbbong9@gmail.com)

Adding a new template is a great contribution to the FastAPI-fastkit community.
Your ideas and efforts will be a great help to other developers! 🚀

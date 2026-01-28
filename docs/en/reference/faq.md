# Frequently Asked Questions

Common questions and answers about FastAPI-fastkit.

## Installation & Setup

### Q: What Python versions are supported?

**A:** FastAPI-fastkit requires **Python 3.12 or higher**. We recommend using the latest stable Python version for the best experience.

<div class="termy">

```console
$ python --version
Python 3.12.1

$ pip install fastapi-fastkit
```

</div>

### Q: How do I install FastAPI-fastkit?

**A:** You can install FastAPI-fastkit using pip:

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

### Q: Installation fails with permission errors

**A:** Try installing in a virtual environment or with user permissions:

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

### Q: Command `fastkit` not found after installation

**A:** This usually means the installation directory is not in your PATH:

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

## Project Creation

### Q: What dependency stacks are available?

**A:** FastAPI-fastkit offers three dependency stacks:

- **MINIMAL**: FastAPI, Uvicorn, Pydantic, Pydantic-Settings (basic web API)
- **STANDARD**: Adds SQLAlchemy, Alembic, pytest (database support)
- **FULL**: Adds Redis, Celery (background tasks)

!!! tip "Default Package Manager"
    The default package manager is `uv` for faster dependency installation. You can also choose `pip`, `pdm`, or `poetry`.

<div class="termy">

```console
$ fastkit init
# Select your preferred stack during project creation
```

</div>

### Q: Can I customize the project template?

**A:** Yes! You can either:

1. **Use existing templates** with `fastkit startdemo`
2. **Create custom templates** by copying and modifying existing ones
3. **Add routes incrementally** with `fastkit addroute`

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

### Q: How do I create a project with a specific name format?

**A:** Project names must be valid Python identifiers:

- ✅ `my-api`, `blog_system`, `UserService`
- ❌ `my api`, `123project`, `project-name!`

<div class="termy">

```console
$ fastkit init
Enter the project name: my_awesome_api  # Valid
Enter the project name: my-awesome-api  # Valid (hyphens converted to underscores)
```

</div>

### Q: Project creation fails with "directory already exists"

**A:** The project directory already exists. Either:

1. **Choose a different name**
2. **Remove the existing directory** (if safe to do so)
3. **Use a different output location**

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

### Q: How do I use interactive mode for project setup?

**A:** Use `fastkit init --interactive` for guided step-by-step project setup with intelligent feature selection:

<div class="termy">

```console
$ fastkit init --interactive
```

</div>

Interactive mode allows you to select from a comprehensive feature catalog:

| Category | Available Options |
|----------|-------------------|
| **Database** | PostgreSQL, MySQL, MongoDB, Redis, SQLite |
| **Authentication** | JWT, OAuth2, FastAPI-Users, Session-based |
| **Background Tasks** | Celery, Dramatiq |
| **Testing** | Basic (pytest), Coverage, Advanced (with faker, factory-boy) |
| **Caching** | Redis with fastapi-cache2 |
| **Monitoring** | Loguru, OpenTelemetry, Prometheus |
| **Utilities** | CORS, Rate-Limiting, Pagination, WebSocket |
| **Deployment** | Docker, docker-compose with auto-generated configs |

The interactive mode automatically generates:

- `main.py` with selected features integrated
- Database and authentication configuration files
- Docker deployment files (Dockerfile, docker-compose.yml)
- Test configuration (pytest with coverage)

### Q: How do I see available features for interactive mode?

**A:** Use the `list-features` command to display all available features and their packages:

<div class="termy">

```console
$ fastkit list-features
# Shows all available features organized by category
# with their associated packages
```

</div>

This helps you understand what packages will be installed for each feature selection.

## Route Development

### Q: How do I add authentication to my routes?

**A:** Create a dependency for authentication:

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

### Q: How do I add database models to my project?

**A:** For STANDARD or FULL stacks, create SQLAlchemy models:

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

### Q: How do I add validation to request data?

**A:** Use Pydantic models in your schemas:

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

### Q: How do I handle file uploads?

**A:** Use FastAPI's `UploadFile`:

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

## Templates

### Q: What templates are available?

**A:** FastAPI-fastkit includes several pre-built templates:

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

### Q: How do I use a specific template?

**A:** Use the `startdemo` command:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Select template: fastapi-psql-orm
```

</div>

### Q: Can I create my own templates?

**A:** Yes! Create a directory structure and use template variables:

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

### Q: How do I modify an existing template?

**A:** Templates are in the `fastapi_project_template` directory. You can:

1. **Fork the repository** and modify templates
2. **Create a custom template** based on existing ones
3. **Override specific files** after project creation

## Development Server

### Q: How do I start the development server?

**A:** Use the `runserver` command from your project directory:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate  # Activate virtual environment
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Q: Server won't start - "Address already in use"

**A:** Port 8000 is busy. Use a different port or kill the existing process:

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

### Q: Auto-reload not working

**A:** Make sure you're in the project directory and have the virtual environment activated:

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

### Q: How do I configure the server for production?

**A:** Don't use the development server in production. Instead:

```python
# Use gunicorn or similar WSGI server
$ pip install gunicorn
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Docker with the fastapi-dockerized template
$ fastkit startdemo  # Select fastapi-dockerized
$ docker build -t my-app .
$ docker run -p 8000:8000 my-app
```

## Performance & Optimization

### Q: How do I improve API performance?

**A:** Several optimization strategies:

1. **Use async/await** for I/O operations
2. **Add caching** for expensive operations
3. **Optimize database queries**
4. **Use background tasks** for heavy processing

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

### Q: How do I add caching?

**A:** Use Redis for caching:

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

### Q: How do I handle many concurrent requests?

**A:** Use appropriate server configuration:

<div class="termy">

```console
# Development
$ fastkit runserver --workers 1  # Single worker for development

# Production
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
$ uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

</div>

## Testing

### Q: How do I run tests?

**A:** Use pytest from your project directory:

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

### Q: How do I write API tests?

**A:** Use FastAPI's test client:

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

### Q: How do I mock external dependencies?

**A:** Use pytest fixtures and mocking:

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

## Contributing

### Q: How do I contribute to FastAPI-fastkit?

**A:** Follow these steps:

1. **Fork the repository** on GitHub
2. **Set up development environment**
3. **Create a feature branch**
4. **Make your changes** with tests
5. **Submit a pull request**

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

### Q: What should I include in a pull request?

**A:** Every pull request should include:

- [ ] **Clear description** of changes
- [ ] **Tests** for new functionality
- [ ] **Documentation** updates if needed
- [ ] **Following code guidelines**
- [ ] **All checks passing**

### Q: How do I report a bug?

**A:** Create an issue on GitHub with:

1. **Bug description** and expected behavior
2. **Steps to reproduce**
3. **Environment information** (OS, Python version, etc.)
4. **Error messages** or logs
5. **Minimal example** if possible

### Q: How do I request a new feature?

**A:** Open a feature request issue with:

1. **Clear description** of the feature
2. **Use case** and motivation
3. **Proposed implementation** (optional)
4. **Examples** of similar features

## Troubleshooting

### Q: I'm getting import errors

**A:** Check your Python path and virtual environment:

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

### Q: Database connection issues

**A:** For database templates, ensure database is running:

<div class="termy">

```console
# PostgreSQL template
$ docker-compose up -d postgres  # Start database
$ alembic upgrade head            # Run migrations

# Check connection
$ docker-compose logs postgres
```

</div>

### Q: Template files not found

**A:** This usually indicates a template path issue:

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

### Q: Pre-commit hooks failing

**A:** Install and run the hooks:

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

### Q: Tests failing on CI but passing locally

**A:** Common causes and solutions:

1. **Environment differences**: Check Python versions match
2. **Missing dependencies**: Ensure test requirements are installed
3. **Path issues**: Use absolute imports
4. **Timing issues**: Add appropriate waits in async tests

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

## Getting Help

### Q: Where can I get help?

**A:** Several options for getting help:

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and community support
- **Documentation**: User guides and tutorials
- **Code Examples**: Check existing templates and tests

### Q: How do I stay updated?

**A:** Follow project updates:

- **Watch the repository** on GitHub
- **Check releases** for new features
- **Read the changelog** for breaking changes
- **Follow best practices** in documentation

!!! tip "Pro Tips"
    - Always use virtual environments for Python projects
    - Keep your FastAPI-fastkit installation up to date
    - Use `fastkit --help` to see available commands
    - Check the documentation when stuck
    - Don't hesitate to ask questions in GitHub Discussions

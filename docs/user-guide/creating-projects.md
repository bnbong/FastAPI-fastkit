# Creating Projects

A detailed guide on how to create various types of FastAPI projects with FastAPI-fastkit.

## Basic Project Creation

### 1. Interactive Mode Project Creation

The most basic way to create a project interactively:

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

### 2. Stack Selection

Choose the dependency stack to include in your project:

#### MINIMAL Stack (Default)

The most basic FastAPI project:

- `fastapi` - FastAPI framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pydantic-settings` - Settings management

**Best for:**

- Learning FastAPI
- Simple APIs
- Prototypes
- Microservices

#### STANDARD Stack

Includes database support and testing:

- All MINIMAL dependencies
- `sqlalchemy` - ORM for database operations
- `alembic` - Database migrations
- `pytest` - Testing framework

**Best for:**

- Most web applications
- APIs with database storage
- Production-ready applications
- Team projects

#### FULL Stack

Complete development environment:

- All STANDARD dependencies
- `redis` - Caching and session storage
- `celery` - Background task processing

**Best for:**

- Large applications
- High-performance requirements
- Complex business logic
- Enterprise applications

## Advanced Project Options

### Custom Project Configuration

You can customize your project during creation:

<div class="termy">

```console
$ fastkit init
Enter the project name: advanced-api
Enter the author name: Development Team
Enter the author email: dev@company.com
Enter the project description: Advanced FastAPI application with custom features

# Choose STANDARD stack for database support
Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Project Structure Explanation

When you create a project, FastAPI-fastkit generates this structure:

```
my-awesome-api/
├── .venv/                      # Virtual environment
├── src/                        # Source code
│   ├── __init__.py
│   ├── main.py                # Application entry point
│   ├── core/                  # Core configuration
│   │   ├── __init__.py
│   │   └── config.py         # Settings and configuration
│   ├── api/                   # API layer
│   │   ├── __init__.py
│   │   ├── api.py            # Main API router
│   │   └── routes/           # Individual route modules
│   │       ├── __init__.py
│   │       └── items.py      # Example items endpoints
│   ├── crud/                  # Database operations
│   │   ├── __init__.py
│   │   └── items.py          # CRUD operations for items
│   ├── schemas/               # Pydantic models
│   │   ├── __init__.py
│   │   └── items.py          # Data validation schemas
│   └── mocks/                 # Test data
│       ├── __init__.py
│       └── mock_items.json   # Sample data for development
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Test configuration
│   └── test_items.py         # Example tests
├── scripts/                   # Utility scripts
│   ├── test.sh               # Run tests
│   ├── coverage.sh           # Test coverage
│   └── lint.sh               # Code linting
├── requirements.txt           # Python dependencies
├── setup.py                  # Package configuration
└── README.md                 # Project documentation
```

### Understanding Each Directory

#### `src/` Directory

Contains all your application source code following the **src layout** pattern, which is a Python packaging best practice.

#### `core/` Module

- **config.py**: Application settings, environment variables, and configuration
- Centralizes all configuration management
- Supports `.env` file for environment-specific settings

#### `api/` Module

- **api.py**: Main API router that includes all sub-routers
- **routes/**: Individual route modules for different resources
- Clean separation of concerns for different API endpoints

#### `crud/` Module

- Database operations and business logic
- **C**reate, **R**ead, **U**pdate, **D**elete operations
- Abstraction layer between API routes and data storage

#### `schemas/` Module

- Pydantic models for data validation
- Request/response schemas
- Type definitions and data models

#### `tests/` Directory

- Complete test suite for your application
- Includes unit tests and integration tests
- Pre-configured with pytest

## Stack Comparison

| Feature | MINIMAL | STANDARD | FULL |
|---------|---------|----------|------|
| FastAPI & Uvicorn | ✅ | ✅ | ✅ |
| Data Validation | ✅ | ✅ | ✅ |
| Database Support | ❌ | ✅ | ✅ |
| Migrations | ❌ | ✅ | ✅ |
| Testing Framework | ❌ | ✅ | ✅ |
| Caching (Redis) | ❌ | ❌ | ✅ |
| Background Tasks | ❌ | ❌ | ✅ |
| **Best For** | Learning, Simple APIs | Most Applications | Enterprise, Complex Apps |

## Project Creation Examples

### Example 1: Learning Project

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

### Example 2: E-commerce API

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

### Example 3: High-Performance Application

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

## After Project Creation

### 1. Activate Virtual Environment

<div class="termy">

```console
$ cd my-awesome-api
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

### 2. Verify Installation

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

### 3. Start Development

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

## Configuration Management

### Environment Variables

Your project supports environment-based configuration through `.env` files:

Create a `.env` file in your project root:

```env
# .env
APP_NAME=My Awesome API
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### Configuration in Code

The generated `src/core/config.py` automatically loads these variables:

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

## Customization Options

### Adding Custom Dependencies

After project creation, you can add more dependencies:

<div class="termy">

```console
$ pip install requests httpx python-jose
$ pip freeze > requirements.txt
```

</div>

### Modifying Project Structure

While the generated structure follows best practices, you can modify it:

- Add new modules in `src/`
- Create additional route files in `api/routes/`
- Extend CRUD operations in `crud/`
- Add more schemas in `schemas/`

## Best Practices

### 1. Virtual Environment

Always use virtual environments to isolate project dependencies:

```bash
# Create project with virtual environment
$ fastkit init  # Automatically creates .venv/

# Activate when working
$ source .venv/bin/activate
```

### 2. Version Control

Initialize git repository after project creation:

<div class="termy">

```console
$ cd my-awesome-api
$ git init
$ git add .
$ git commit -m "Initial commit - FastAPI project setup"
```

</div>

### 3. Environment Configuration

- Use `.env` files for local development
- Use environment variables for production
- Never commit sensitive data to version control

### 4. Testing

Leverage the included test framework:

<div class="termy">

```console
$ python -m pytest
$ bash scripts/test.sh
```

</div>

## Next Steps

After creating your project:

1. **[Adding Routes](adding-routes.md)**: Learn to add new API endpoints
2. **[CLI Reference](cli-reference.md)**: Master all available commands
3. **[Your First Project Tutorial](../tutorial/first-project.md)**: Build a complete application

!!! tip "Project Creation Tips"
    - Choose the stack that matches your project requirements
    - Start with MINIMAL for learning, use STANDARD for most projects
    - The project structure is designed for scalability and maintainability
    - All generated code follows FastAPI best practices

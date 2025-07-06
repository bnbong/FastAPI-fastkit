# Getting Started

A comprehensive, step-by-step tutorial for getting started with FastAPI-fastkit. This guide will take you from installation to running your first API in about 15 minutes.

## Prerequisites

Before we begin, make sure you have:

- **Python 3.12 or higher** installed on your system
- **Basic knowledge of Python** (variables, functions, classes)
- **Terminal/Command line** access
- **Text editor or IDE** (VS Code, PyCharm, etc.)

## Step 1: Installation

First, let's install FastAPI-fastkit. We recommend using a virtual environment to keep your projects isolated.

### Option A: Using pip (Recommended)

<div class="termy">

```console
$ pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### Option B: Using a Virtual Environment

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # On Windows: fastapi-env\Scripts\activate
$ pip install fastapi-fastkit
```

</div>

### Verify Installation

Check that FastAPI-fastkit is installed correctly:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

## Step 2: Create Your First Project

Now let's create your first FastAPI project using the interactive `init` command:

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
Do you want to proceed with project creation? [y/N]: y

Creating virtual environment...
Installing dependencies...
✨ FastAPI project 'my-first-api' has been created successfully!
```

</div>

!!! note "Stack Selection"
    We chose **MINIMAL** for this tutorial to keep things simple. For real projects, consider **STANDARD** (includes database support) or **FULL** (includes background tasks).

## Step 3: Navigate to Your Project

Move into your newly created project directory:

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

## Step 4: Activate Virtual Environment

Your project comes with a pre-configured virtual environment. Let's activate it:

<div class="termy">

```console
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
(my-first-api) $
```

</div>

Notice how your terminal prompt now shows `(my-first-api)` indicating the virtual environment is active.

## Step 5: Start the Development Server

Now comes the exciting part - let's start your FastAPI server:

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

🎉 **Congratulations!** Your FastAPI server is now running.

## Step 6: Test Your API

Let's test your API in several ways:

### Method 1: Browser

Open your web browser and visit:

- **Main API endpoint**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

You should see:
```json
{"message": "Hello World"}
```

### Method 2: Interactive API Documentation

Visit the automatically generated API documentation:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

The Swagger UI is particularly useful - you can:
- See all available endpoints
- Test endpoints directly in your browser
- View request/response schemas
- Download OpenAPI specifications

### Method 3: Command Line

Open a new terminal (keep the server running) and test with curl:

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

## Step 7: Understand Your Project Structure

Let's explore what FastAPI-fastkit generated for you:

<div class="termy">

```console
$ tree src
src/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── core/
│   ├── __init__.py
│   └── config.py          # Application configuration
├── api/
│   ├── __init__.py
│   ├── api.py             # Main API router
│   └── routes/
│       ├── __init__.py
│       └── items.py       # Items API endpoints
├── crud/
│   ├── __init__.py
│   └── items.py           # Business logic for items
├── schemas/
│   ├── __init__.py
│   └── items.py           # Data validation schemas
└── mocks/
    ├── __init__.py
    └── mock_items.json    # Sample data
```

</div>

### Key Files Explained

**`src/main.py`** - The heart of your application:
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

**`src/core/config.py`** - Application settings:
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

**`src/api/routes/items.py`** - API endpoints:
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

## Step 8: Add Your First Custom Route

Let's add a new API route to practice what you've learned:

<div class="termy">

```console
$ fastkit addroute my-first-api users
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

The server will automatically restart and now you have new endpoints:
- `GET /api/v1/users/` - Get all users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get a specific user
- And more...

### Test Your New Route

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

## Step 9: Explore and Modify the Code

Now let's make a small modification to understand how the code works.

### Modify the Welcome Message

Open `src/main.py` in your text editor and change the root endpoint:

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!"}
```

Save the file. Thanks to auto-reload, your server automatically restarts.

### Test the Change

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Welcome to my first FastAPI application!"}
```

</div>

### Add a New Endpoint

Let's add a simple endpoint to `src/main.py`:

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### Test the New Endpoint

<div class="termy">

```console
$ curl http://127.0.0.1:8000/hello/World
{"message":"Hello, World!"}

$ curl http://127.0.0.1:8000/hello/FastAPI
{"message":"Hello, FastAPI!"}
```

</div>

## Step 10: Run Tests

Your project comes with pre-configured tests. Let's run them:

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

## Understanding Core Concepts

### 1. FastAPI Application Structure

FastAPI-fastkit follows a **modular architecture**:

- **`main.py`**: Application entry point and global endpoints
- **`api/`**: API route organization
- **`core/`**: Application configuration and settings
- **`crud/`**: Business logic and data operations
- **`schemas/`**: Data validation and serialization
- **`tests/`**: Automated testing

### 2. Dependency Management

Your project uses modern Python dependency management:

- **Virtual environment**: Isolated Python environment
- **requirements.txt**: Lists all dependencies
- **Automatic installation**: Dependencies installed during project creation

### 3. Development Server

FastAPI-fastkit uses **Uvicorn** as the ASGI server:

- **Auto-reload**: Automatically restarts when code changes
- **Fast startup**: Quick development iteration
- **Production-ready**: Same server used in production

### 4. API Documentation

FastAPI automatically generates:

- **OpenAPI specification**: Industry-standard API documentation
- **Swagger UI**: Interactive testing interface
- **ReDoc**: Alternative documentation view

## Next Steps

Congratulations! You've successfully:

✅ Installed FastAPI-fastkit
✅ Created your first project
✅ Started the development server
✅ Tested your API endpoints
✅ Added a new route
✅ Modified existing code
✅ Run tests

### Continue Learning

1. **[Your First Project](first-project.md)**: Build a complete blog API with advanced features
2. **[Adding Routes](../user-guide/adding-routes.md)**: Learn to create complex API endpoints
3. **[Using Templates](../user-guide/using-templates.md)**: Explore pre-built project templates

### Experiment More

Try these challenges:

1. **Add validation**: Modify schemas to add data validation rules
2. **Custom responses**: Change response formats in routes
3. **Environment variables**: Use `.env` files for configuration
4. **Add middleware**: Implement CORS or authentication
5. **Database integration**: Upgrade to STANDARD stack for database support

### Common Issues and Solutions

**Server won't start:**
- Check you're in the project directory
- Ensure virtual environment is activated
- Verify no syntax errors in your code

**Import errors:**
- Make sure all `__init__.py` files exist
- Check your import paths are correct
- Verify you're using the virtual environment

**Port already in use:**
```console
$ fastkit runserver --port 8080
```

## Best Practices You've Learned

1. **Virtual Environments**: Always use isolated environments
2. **Project Structure**: Follow organized, modular architecture
3. **Auto-reload**: Use development server for fast iteration
4. **API Documentation**: Leverage automatic documentation generation
5. **Testing**: Run tests regularly during development

!!! tip "Development Tips"
    - Keep the development server running while coding
    - Use the interactive docs (`/docs`) to test your APIs
    - Check the terminal for helpful error messages
    - Commit your code to version control regularly

You're now ready to build amazing APIs with FastAPI-fastkit! 🚀

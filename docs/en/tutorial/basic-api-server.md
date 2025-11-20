# Building a Basic API Server

Learn how to quickly build a simple REST API server using FastAPI-fastkit. This tutorial is suitable for FastAPI beginners and covers creating basic CRUD APIs.

## What You'll Learn in This Tutorial

- Creating a basic API server with the `fastkit startdemo` command
- Understanding FastAPI project structure
- Using basic CRUD endpoints
- API testing and documentation
- Project expansion methods

## Prerequisites

- Python 3.12 or higher installed
- FastAPI-fastkit installed (`pip install fastapi-fastkit`)
- Basic Python knowledge

## Step 1: Creating a Basic API Project

Let's create a basic API server using the `fastapi-default` template.

<div class="termy">

```console
$ fastkit startdemo fastapi-default
Enter the project name: my-first-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: My first FastAPI server
Deploying FastAPI project using 'fastapi-default' template

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-first-api               │
│ Author       │ Developer Kim              │
│ Author Email │ developer@example.com      │
│ Description  │ My first FastAPI server    │
└──────────────┴────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-api' from 'fastapi-default' has been created successfully!
```

</div>

## Step 2: Understanding the Generated Project Structure

Let's examine the generated project structure:

```
my-first-api/
├── README.md                 # Project documentation
├── requirements.txt          # Dependency package list
├── setup.py                  # Package configuration
├── scripts/
│   └── run-server.sh        # Server execution script
├── src/                     # Main source code
│   ├── main.py              # FastAPI application entry point
│   ├── core/
│   │   └── config.py        # Configuration management
│   ├── api/
│   │   ├── api.py           # API router collection
│   │   └── routes/
│   │       └── items.py     # Item-related endpoints
│   ├── schemas/
│   │   └── items.py         # Data model definitions
│   ├── crud/
│   │   └── items.py         # Data processing logic
│   └── mocks/
│       └── mock_items.json  # Test data
└── tests/                   # Test code
    ├── __init__.py
    ├── conftest.py
    └── test_items.py
```

### Key File Descriptions

- **`src/main.py`**: FastAPI application entry point
- **`src/api/routes/items.py`**: Item-related API endpoint definitions
- **`src/schemas/items.py`**: Request/response data structure definitions
- **`src/crud/items.py`**: Database operation logic
- **`src/mocks/mock_items.json`**: Sample data for development

## Step 3: Running the Server

Let's navigate to the generated project directory and run the server.

<div class="termy">

```console
$ cd my-first-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Will watch for changes in these directories: ['/path/to/my-first-api']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

Once the server is successfully running, you can access the following URLs in your browser:

- **API Server**: http://127.0.0.1:8000
- **Swagger UI Documentation**: http://127.0.0.1:8000/docs
- **ReDoc Documentation**: http://127.0.0.1:8000/redoc

## Step 4: Exploring API Endpoints

The generated API provides the following endpoints by default:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/items/` | Retrieve all items |
| GET | `/items/{item_id}` | Retrieve specific item |
| POST | `/items/` | Create new item |
| PUT | `/items/{item_id}` | Update item |
| DELETE | `/items/{item_id}` | Delete item |

### Testing the API

**1. Retrieving All Items**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/"
[
  {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  },
  {
    "id": 2,
    "name": "Mouse",
    "description": "Wireless mouse",
    "price": 29.99,
    "tax": 2.99
  }
]
```

</div>

**2. Creating a New Item**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Keyboard",
       "description": "Mechanical keyboard",
       "price": 150.00,
       "tax": 15.00
     }'

{
  "id": 3,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.0,
  "tax": 15.0
}
```

</div>

**3. Retrieving a Specific Item**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/1"
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "tax": 99.99
}
```

</div>

## Step 5: Testing API with Swagger UI

Navigate to http://127.0.0.1:8000/docs in your browser to view the automatically generated API documentation.

What you can do with Swagger UI:

1. **View API Endpoints**: Visually see all available endpoints
2. **Check Request/Response Schemas**: View input/output formats for each endpoint
3. **Test APIs Directly**: Make actual API calls with the "Try it out" button
4. **View Example Data**: See example request/response data for each endpoint

### How to Use Swagger UI

1. Click on the `/items/` GET endpoint
2. Click the "Try it out" button
3. Click the "Execute" button
4. View the server response

## Step 6: Understanding Code Structure

### Main Application (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### Item Schema (`src/schemas/items.py`)

```python
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
```

### CRUD Logic (`src/crud/items.py`)

```python
from typing import List, Optional
from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self):
        self.items: List[Item] = []
        self.next_id = 1

    def create_item(self, item: ItemCreate) -> Item:
        new_item = Item(id=self.next_id, **item.dict())
        self.items.append(new_item)
        self.next_id += 1
        return new_item

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)
```

## Step 7: Expanding the Project

### Adding New Routes

You can add new endpoints using the `fastkit addroute` command:

<div class="termy">

```console
$ fastkit addroute user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ user                                     │
│ Target Directory │ /path/to/my-first-api                   │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to the current project? [Y/n]: y

✨ Successfully added new route 'user' to the current project!
```

</div>

This command creates the following files:

- `src/api/routes/user.py` - User-related endpoints
- `src/schemas/user.py` - User data models
- `src/crud/user.py` - User data processing logic

### Customizing Environment Configuration

You can modify the `src/core/config.py` file to change project settings:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My First API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "My first FastAPI server"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Step 8: Running Tests

The project includes basic tests:

<div class="termy">

```console
$ pytest tests/ -v
======================== test session starts ========================
collected 4 items

tests/test_items.py::test_create_item PASSED                   [ 25%]
tests/test_items.py::test_read_items PASSED                    [ 50%]
tests/test_items.py::test_read_item PASSED                     [ 75%]
tests/test_items.py::test_update_item PASSED                   [100%]

======================== 4 passed in 0.15s ========================
```

</div>

## Next Steps

You've completed building a basic API server! Next things to try:

1. **[Building Asynchronous CRUD APIs](async-crud-api.md)** - Learn more complex asynchronous processing
2. **[Database Integration](database-integration.md)** - Using PostgreSQL and SQLAlchemy
3. **[Docker Containerization](docker-deployment.md)** - Preparing for production deployment
4. **[Custom Response Handling](custom-response-handling.md)** - Advanced response format configuration

## Troubleshooting

### Common Issues

**Q: The server won't start**
A: Check that your virtual environment is activated and dependencies are properly installed.

**Q: Cannot access API endpoints**
A: Verify that the server is running normally and the port number (default: 8000) is correct.

**Q: APIs don't appear in Swagger UI**
A: Check that the router is properly included in `src/main.py`.

## Summary

In this tutorial, we used FastAPI-fastkit to:

- ✅ Create a basic FastAPI project
- ✅ Understand project structure
- ✅ Use CRUD API endpoints
- ✅ API documentation and testing
- ✅ Project expansion methods

Now that you've learned the basics of FastAPI, try taking on more complex projects!

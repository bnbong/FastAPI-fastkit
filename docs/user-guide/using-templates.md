# Using Templates

FastAPI-fastkit provides pre-built project templates to help you get started quickly with different technology stacks.

## Available Templates

Check the available templates with the `list-templates` command:

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

## Template Descriptions

### 1. `fastapi-default`

**Simple FastAPI Project**

- Basic FastAPI setup with essential features
- Item management with mock data
- Perfect for learning and simple APIs
- Includes basic CRUD operations

**Best for:**

- FastAPI beginners
- Simple web APIs
- Learning and prototyping

### 2. `fastapi-async-crud`

**Async Item Management API Server**

- Fully asynchronous FastAPI application
- Advanced CRUD operations with async/await
- Better performance for I/O operations
- Mock data storage with async patterns

**Best for:**

- High-performance applications
- I/O intensive operations
- Modern async Python development

### 3. `fastapi-custom-response`

**Async Item Management API with Custom Response System**

- Custom response models and formatting
- Advanced error handling
- Pagination support
- Custom HTTP status codes and responses

**Best for:**

- APIs requiring specific response formats
- Advanced error handling needs
- Custom business logic in responses

### 4. `fastapi-dockerized`

**Dockerized FastAPI Item Management API**

- Full Docker containerization
- Production-ready deployment setup
- Multi-stage Docker builds
- Environment-based configuration

**Best for:**

- Production deployments
- Containerized environments
- DevOps and CI/CD pipelines

### 5. `fastapi-psql-orm`

**Dockerized FastAPI Item Management API with PostgreSQL**

- PostgreSQL database integration
- SQLAlchemy ORM with Alembic migrations
- Docker Compose for local development
- Full database CRUD operations

**Best for:**

- Database-driven applications
- Production-grade data storage
- Complex data relationships

### 6. `fastapi-empty`

**Minimal FastAPI Project**

- Bare minimum FastAPI setup
- No pre-built features
- Clean slate for custom development

**Best for:**

- Starting from scratch
- Minimal dependencies
- Custom architecture requirements

## Creating a Project from Template

Use the `startdemo` command to create a project from a template:

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

Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## Template Features Comparison

| Feature | Default | Async CRUD | Custom Response | Dockerized | PostgreSQL ORM | Empty |
|---------|---------|------------|-----------------|------------|----------------|-------|
| **Basic FastAPI** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Mock Data** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Async Support** | Basic | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Custom Responses** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Database** | Mock | Mock | Mock | Mock | PostgreSQL | None |
| **ORM** | ❌ | ❌ | ❌ | ❌ | SQLAlchemy | ❌ |
| **Migrations** | ❌ | ❌ | ❌ | ❌ | Alembic | ❌ |
| **Testing** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Best For** | Learning | Performance | Custom APIs | Production | Database Apps | Custom |

## Template-Specific Setup

### Using `fastapi-psql-orm`

This template includes full PostgreSQL setup. After creation:

1. **Start PostgreSQL with Docker:**

<div class="termy">

```console
$ cd my-blog-api
$ docker-compose up -d postgres
Starting my-blog-api_postgres_1 ... done
```

</div>

2. **Run database migrations:**

<div class="termy">

```console
$ source .venv/bin/activate
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> bedcdc35b64a, first alembic
```

</div>

3. **Start the API server:**

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Using `fastapi-dockerized`

This template provides full Docker support:

1. **Build the Docker image:**

<div class="termy">

```console
$ cd my-dockerized-api
$ docker build -t my-dockerized-api .
Successfully built abc123def456
Successfully tagged my-dockerized-api:latest
```

</div>

2. **Run the container:**

<div class="termy">

```console
$ docker run -p 8000:8000 my-dockerized-api
INFO:     Uvicorn running on http://0.0.0.0:8000
```

</div>

### Using `fastapi-custom-response`

This template includes advanced response handling:

1. **Custom response models:**

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

2. **Enhanced error handling:**

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

## Template Project Structure

Each template follows a consistent but customized structure:

### `fastapi-default` Structure
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

### `fastapi-psql-orm` Structure
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

## Customizing Templates

After creating a project from a template, you can customize it:

### 1. Add New Routes

<div class="termy">

```console
$ fastkit addroute my-blog-api posts
$ fastkit addroute my-blog-api users
$ fastkit addroute my-blog-api comments
```

</div>

### 2. Modify Configuration

Edit `src/core/config.py` to match your needs:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings (for PostgreSQL templates)
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Add Environment Variables

Create a `.env` file in your project root:

```env
# .env
PROJECT_NAME=My Blog API
VERSION=1.0.0
DEBUG=True

# Database (for PostgreSQL templates)
DATABASE_URL=postgresql://user:password@localhost:5432/myblogdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=myblogdb

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Template Testing

Each template comes with pre-configured tests:

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

## Template Development Workflow

### 1. Choose the Right Template

- **Learning/Simple APIs**: `fastapi-default`
- **High Performance**: `fastapi-async-crud`
- **Custom Response Formats**: `fastapi-custom-response`
- **Production Deployment**: `fastapi-dockerized`
- **Database Applications**: `fastapi-psql-orm`
- **Custom Architecture**: `fastapi-empty`

### 2. Create and Setup

<div class="termy">

```console
$ fastkit startdemo
# Follow the prompts
$ cd your-project
$ source .venv/bin/activate
```

</div>

### 3. Development

<div class="termy">

```console
# Start development server
$ fastkit runserver

# Run tests
$ python -m pytest

# Add new features
$ fastkit addroute your-project new-resource
```

</div>

### 4. Deployment

For production templates (`fastapi-dockerized`, `fastapi-psql-orm`):

<div class="termy">

```console
# Build for production
$ docker build -t your-app .

# Deploy with Docker Compose
$ docker-compose up -d
```

</div>

## Best Practices

### 1. Choose Templates Wisely

- Start with simpler templates for learning
- Use database templates for data-driven apps
- Use Docker templates for production deployments

### 2. Environment Management

- Always use `.env` files for configuration
- Never commit sensitive data to version control
- Use different environments for development/production

### 3. Customization Strategy

- Add new routes using `fastkit addroute`
- Modify existing code to fit your business logic
- Keep the project structure organized

### 4. Testing

- Run tests regularly during development
- Add tests for new features you implement
- Use the provided test structure as a guide

## Troubleshooting

### Database Connection Issues (PostgreSQL templates)

If you can't connect to PostgreSQL:

1. **Check Docker is running:**

   <div class="termy">
   ```console
   $ docker ps
   ```
   </div>

2. **Verify PostgreSQL container:**

   <div class="termy">
   ```console
   $ docker-compose logs postgres
   ```
   </div>

3. **Check environment variables:**

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Docker Build Failures

If Docker build fails:

1. **Check Dockerfile syntax**
2. **Verify all files are present**
3. **Check Docker daemon is running**

### Missing Dependencies

If you get import errors:

1. **Activate virtual environment:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

2. **Install dependencies:**
   <div class="termy">
   ```console
   $ pip install -r requirements.txt
   ```
   </div>

## Next Steps

Now that you understand templates:

1. **[Your First Project](../tutorial/first-project.md)**: Build a complete application
2. **[Adding Routes](adding-routes.md)**: Expand your template-based project
3. **[CLI Reference](cli-reference.md)**: Master all available commands

!!! tip "Template Tips"
    - Templates provide excellent starting points, not final solutions
    - Customize templates to match your specific requirements
    - Study template code to learn FastAPI best practices
    - Use version control to track your customizations

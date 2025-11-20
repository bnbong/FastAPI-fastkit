# Quick Start

Create your first FastAPI project with FastAPI-fastkit in under 5 minutes!

## 1. Create Project

Use FastAPI-fastkit's `init` command to create a new project:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-app
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI application

           Project Information
┌──────────────┬─────────────────────────────┐
│ Project Name │ my-first-app                │
│ Author       │ Your Name                   │
│ Author Email │ your.email@example.com      │
│ Description  │ My first FastAPI application│
└──────────────┴─────────────────────────────┘

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

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
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

✨ FastAPI project 'my-first-app' has been created successfully!
```

</div>

## 2. Activate Virtual Environment

Navigate to your project and activate the virtual environment:

<div class="termy">

```console
$ cd my-first-app
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

## 3. Start Development Server

Start the FastAPI development server:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

!!! success "Congratulations!"
    Your FastAPI server is now running! Open your browser to check it out.

## 4. Test Your API

Open your browser and visit these URLs:

### Main Endpoint

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

You'll see:

```json
{"message": "Hello World"}
```

### Interactive API Documentation

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

This is the automatically generated **Swagger UI** documentation where you can:
- See all your API endpoints
- Test endpoints directly in the browser
- View request/response schemas

### Alternative Documentation

Visit [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

This is the **ReDoc** documentation interface with a different, clean design.

## 5. Add Your First Route

Let's add a new API route to your project:

<div class="termy">

```console
$ fastkit addroute my-first-app users
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-app                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-app                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-app'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-first-app`                                        │
╰───────────────────────────────────────────────────────╯
```

</div>

The server will automatically reload, and now you have new endpoints:

- `GET /api/v1/users/` - Get all users
- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/{user_id}` - Get a specific user
- `PUT /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

## 6. Test the New API

### Using curl

**Get all users:**

<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/
[]
```

</div>

**Create a new user:**

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
```

</div>

### Using the Interactive Docs

1. Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Expand the **"users"** section
3. Click on **"POST /api/v1/users/"**
4. Click **"Try it out"**
5. Fill in the request body:
   ```json
   {
     "title": "Jane Smith",
     "description": "Product Manager"
   }
   ```
6. Click **"Execute"**

## 7. Explore Your Project Structure

Your generated project has a clean, organized structure:

```
my-first-app/
├── .venv/                    # Virtual environment
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # App configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API router collection
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── items.py     # Default items route
│   │       └── users.py     # Your new users route
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── items.py         # CRUD operations for items
│   │   └── users.py         # CRUD operations for users
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── items.py         # Pydantic schemas for items
│   │   └── users.py         # Pydantic schemas for users
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Test data
├── tests/                   # Test files
├── scripts/                 # Utility scripts
├── requirements.txt         # Python dependencies
├── setup.py                # Package configuration
└── README.md               # Project documentation
```

## 8. Package Manager Options

FastAPI-fastkit supports multiple Python package managers to suit your preferences:

### Available Package Managers

| Manager | Description | Best For |
|---------|-------------|----------|
| **UV** | Fast Python package manager (default) | Speed and performance |
| **PDM** | Modern Python dependency management | Advanced dependency resolution |
| **Poetry** | Python dependency management and packaging | Poetry-based workflows |
| **PIP** | Standard Python package manager | Traditional Python development |

### Specifying Package Manager

You can specify your preferred package manager in several ways:

#### 1. Interactive Selection (Default)

When you run `fastkit init` or `fastkit startdemo`, you'll be prompted to choose:

<div class="termy">

```console
$ fastkit init
# ... after project details and stack selection ...

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

#### 2. Command Line Option

Skip the interactive prompt by specifying the package manager directly:

<div class="termy">

```console
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

</div>

### Dependency Files Generated

Each package manager creates its appropriate dependency files:

- **UV/PDM**: `pyproject.toml` (PEP 621 format)
- **Poetry**: `pyproject.toml` (Poetry format)
- **PIP**: `requirements.txt`

## 9. What's Next?

Congratulations! You've successfully:

✅ Created your first FastAPI project
✅ Started the development server
✅ Added a new API route
✅ Tested your APIs

### Continue Learning

1. **[Your First Project](../tutorial/first-project.md)**: Build a more complex blog API
2. **[Creating Projects](creating-projects.md)**: Learn about different stacks and options
3. **[Adding Routes](adding-routes.md)**: Master the art of API development
4. **[Using Templates](using-templates.md)**: Explore pre-built project templates

### Experiment More

Try these commands to explore more features:

<div class="termy">

```console
# List available templates
$ fastkit list-templates

# Create a project from a template
$ fastkit startdemo

# Add more routes
$ fastkit addroute my-first-app products
$ fastkit addroute my-first-app orders
```

</div>

!!! tip "Development Tips"
    - The server automatically reloads when you change files
    - Always check the interactive docs at `/docs` when adding new features
    - Use the virtual environment to keep dependencies isolated
    - Explore the generated code to understand the project structure

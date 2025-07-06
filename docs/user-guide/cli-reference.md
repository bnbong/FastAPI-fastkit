# CLI Reference

Complete reference for all FastAPI-fastkit command-line interface commands.

## Global Options

All commands support these global options:

```console
$ fastkit [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

| Option | Description |
|--------|-------------|
| `--version` | Show FastAPI-fastkit version |
| `--help` | Show help message |

### Examples

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0

$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## Commands

### `init`

Create a new FastAPI project with interactive setup.

#### Syntax

```console
$ fastkit init [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--help` | Show command help | - |

#### Interactive Prompts

The `init` command will prompt you for:

1. **Project name**: Directory name and package name
2. **Author name**: Package author information
3. **Author email**: Contact email for package
4. **Project description**: Brief description of the project
5. **Stack selection**: Choose from minimal, standard, or full

#### Stack Options

**MINIMAL Stack:**

- `fastapi` - FastAPI framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `pydantic-settings` - Configuration management

**STANDARD Stack:**

- All MINIMAL stack packages
- `sqlalchemy` - SQL toolkit and ORM
- `alembic` - Database migration tool
- `pytest` - Testing framework

**FULL Stack:**

- All STANDARD stack packages
- `redis` - In-memory data store
- `celery` - Distributed task queue

#### Examples

<div class="termy">

```console
$ fastkit init
Enter the project name: my-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome API

Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-api' has been created successfully!
```

</div>

#### Generated Structure

Creates a project with this structure:

```
my-api/
├── .venv/                    # Virtual environment
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # API router collection
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── items.py     # Example route
│   ├── crud/
│   │   ├── __init__.py
│   │   └── items.py         # CRUD operations
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── items.py         # Pydantic schemas
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Test data
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

### `addroute`

Add a new API route to an existing FastAPI project.

#### Syntax

```console
$ fastkit addroute PROJECT_NAME ROUTE_NAME [OPTIONS]
```

#### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `PROJECT_NAME` | Name of the existing project | Yes |
| `ROUTE_NAME` | Name of the new route (plural recommended) | Yes |

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--help` | Show command help | - |

#### Examples

<div class="termy">

```console
$ fastkit addroute my-api users
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-api                                   │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-api                                 │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-api'
```

</div>

#### Generated Files

Creates these files in the project:

- `src/api/routes/users.py` - Route handlers
- `src/crud/users.py` - CRUD operations
- `src/schemas/users.py` - Pydantic schemas

Also updates `src/api/api.py` to include the new router.

#### Generated Endpoints

Creates full CRUD endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | Get all users |
| `POST` | `/api/v1/users/` | Create new user |
| `GET` | `/api/v1/users/{user_id}` | Get specific user |
| `PUT` | `/api/v1/users/{user_id}` | Update user |
| `DELETE` | `/api/v1/users/{user_id}` | Delete user |

### `startdemo`

Create a FastAPI project from a pre-built template.

#### Syntax

```console
$ fastkit startdemo [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--help` | Show command help | - |

#### Interactive Prompts

The `startdemo` command will prompt you for:

1. **Project name**: Directory name for the new project
2. **Author name**: Package author information
3. **Author email**: Contact email
4. **Project description**: Brief description
5. **Template selection**: Choose from available templates

#### Available Templates

| Template | Description | Features |
|----------|-------------|----------|
| `fastapi-default` | Simple FastAPI Project | Basic CRUD, Mock data |
| `fastapi-async-crud` | Async Item Management API | Async/await, Performance |
| `fastapi-custom-response` | Custom Response System | Custom responses, Pagination |
| `fastapi-dockerized` | Dockerized FastAPI API | Docker, Production ready |
| `fastapi-psql-orm` | PostgreSQL FastAPI API | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-empty` | Minimal FastAPI Project | Bare minimum setup |

#### Examples

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Enter the author name: Jane Smith
Enter the author email: jane@example.com
Enter the project description: Blog API with PostgreSQL

Select template: fastapi-psql-orm
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog' from 'fastapi-psql-orm' has been created!
```

</div>

### `runserver`

Start the FastAPI development server.

#### Syntax

```console
$ fastkit runserver [OPTIONS]
```

#### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--host` | `-h` | Host to bind to | `127.0.0.1` |
| `--port` | `-p` | Port to bind to | `8000` |
| `--reload` | `-r` | Enable auto-reload | `True` |
| `--workers` | `-w` | Number of workers | `1` |
| `--help` | | Show command help | - |

#### Examples

<div class="termy">

```console
# Basic usage (default settings)
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000

# Custom host and port
$ fastkit runserver --host 0.0.0.0 --port 8080
INFO:     Uvicorn running on http://0.0.0.0:8080

# Disable auto-reload
$ fastkit runserver --no-reload
INFO:     Uvicorn running on http://127.0.0.1:8000

# Multiple workers (production)
$ fastkit runserver --workers 4
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

#### Requirements

- Must be run from a FastAPI project directory
- Project must have `src/main.py` with FastAPI app
- Virtual environment should be activated

### `list-templates`

List all available FastAPI project templates.

#### Syntax

```console
$ fastkit list-templates [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--help` | Show command help | - |

#### Examples

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

## Environment Variables

FastAPI-fastkit respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | Configuration directory | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Custom templates directory | Built-in templates |
| `FASTKIT_LOG_LEVEL` | Logging level | `INFO` |

### Examples

<div class="termy">

```console
# Custom configuration directory
$ export FASTKIT_CONFIG_DIR=~/my-fastkit-config
$ fastkit init

# Custom templates directory
$ export FASTKIT_TEMPLATES_DIR=~/my-templates
$ fastkit list-templates

# Debug logging
$ export FASTKIT_LOG_LEVEL=DEBUG
$ fastkit init
```

</div>

## Configuration Files

FastAPI-fastkit can use configuration files for default settings.

### Configuration File Location

1. `$FASTKIT_CONFIG_DIR/config.yaml` (if `FASTKIT_CONFIG_DIR` is set)
2. `~/.fastkit/config.yaml` (default)
3. `./fastkit.yaml` (project-specific)

### Configuration Format

```yaml
# ~/.fastkit/config.yaml
default:
  author:
    name: "Your Name"
    email: "your.email@example.com"

  project:
    stack: "standard"
    create_venv: true
    install_deps: true

  server:
    host: "127.0.0.1"
    port: 8000
    reload: true

templates:
  custom_dir: "~/my-templates"

logging:
  level: "INFO"
  file: "~/.fastkit/logs/fastkit.log"
```

## Common Workflows

### 1. Create New Project

<div class="termy">

```console
# Create a new project
$ fastkit init
# Follow prompts...

# Navigate to project
$ cd my-awesome-api

# Activate virtual environment
$ source .venv/bin/activate

# Start development server
$ fastkit runserver
```

</div>

### 2. Add Features to Existing Project

<div class="termy">

```console
# Add multiple routes
$ fastkit addroute my-api users
$ fastkit addroute my-api products
$ fastkit addroute my-api orders

# Test the API
$ fastkit runserver
# Visit http://127.0.0.1:8000/docs
```

</div>

### 3. Use Templates for Complex Projects

<div class="termy">

```console
# List available templates
$ fastkit list-templates

# Create from template
$ fastkit startdemo
# Select fastapi-psql-orm for database project

# Setup database (for PostgreSQL template)
$ cd my-project
$ docker-compose up -d postgres
$ source .venv/bin/activate
$ alembic upgrade head
$ fastkit runserver
```

</div>

## Troubleshooting

### Command Not Found

If `fastkit` command is not found:

1. **Check installation:**
   <div class="termy">
   ```console
   $ pip show fastapi-fastkit
   ```
   </div>

2. **Reinstall if needed:**
   <div class="termy">
   ```console
   $ pip uninstall fastapi-fastkit
   $ pip install fastapi-fastkit
   ```
   </div>

3. **Check PATH:**
   <div class="termy">
   ```console
   $ which fastkit
   ```
   </div>

### Virtual Environment Issues

If virtual environment creation fails:

1. **Check Python version:**
   <div class="termy">
   ```console
   $ python --version  # Should be 3.12+
   ```
   </div>

2. **Check venv module:**
   <div class="termy">
   ```console
   $ python -m venv --help
   ```
   </div>

3. **Manual virtual environment:**
   <div class="termy">
   ```console
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ```
   </div>

### Server Won't Start

If `fastkit runserver` fails:

1. **Check you're in project directory**
2. **Verify `src/main.py` exists**
3. **Activate virtual environment:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

4. **Check for syntax errors:**
   <div class="termy">
   ```console
   $ python -c "from src.main import app"
   ```
   </div>

### Port Already in Use

If port 8000 is busy:

<div class="termy">

```console
# Use different port
$ fastkit runserver --port 8080

# Or kill existing process
$ lsof -ti:8000 | xargs kill -9
```

</div>

## Advanced Usage

### Custom Templates

You can create custom templates by:

1. **Creating template directory:**
   ```
   my-template/
   ├── src/
   │   └── main.py-tpl
   ├── requirements.txt-tpl
   └── setup.py-tpl
   ```

2. **Setting environment variable:**
   <div class="termy">
   ```console
   $ export FASTKIT_TEMPLATES_DIR=~/my-templates
   ```
   </div>

3. **Using custom template:**
   <div class="termy">
   ```console
   $ fastkit startdemo
   # Your custom templates will appear in the list
   ```
   </div>

### Scripting with FastAPI-fastkit

You can use FastAPI-fastkit in scripts:

```bash
#!/bin/bash
# create-microservices.sh

for service in users products orders; do
    echo "Creating $service service..."
    fastkit init <<EOF
$service-service
Company Team
team@company.com
$service microservice
minimal
y
EOF

    cd "$service-service"
    fastkit addroute "$service-service" "$service"
    cd ..
done
```

### Integration with CI/CD

Example GitHub Actions workflow:

```yaml
name: Test FastAPI-fastkit Project

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install FastAPI-fastkit
      run: pip install fastapi-fastkit

    - name: Create test project
      run: |
        fastkit init <<EOF
        test-project
        CI
        ci@example.com
        Test project
        standard
        y
        EOF

    - name: Test project
      run: |
        cd test-project
        source .venv/bin/activate
        python -m pytest
```

## Next Steps

Now that you understand the CLI:

1. **[Quick Start](quick-start.md)**: Try the commands hands-on
2. **[Your First Project](../tutorial/first-project.md)**: Build a complete application
3. **[Contributing](../contributing/development-setup.md)**: Contribute to FastAPI-fastkit

!!! tip "CLI Tips"
    - Use `--help` with any command for detailed help
    - Configure default settings to speed up project creation
    - Use templates for complex project setups
    - Combine commands to create powerful workflows

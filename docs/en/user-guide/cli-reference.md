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
| `--interactive` | Guided setup: architecture preset, then feature selection | off |
| `--config <path>` | Create the project from a saved configuration file, with no prompts | - |
| `--save-config <path>` | With `--interactive`, write the answered configuration to this path | - |
| `--project-name` | Project name (prompted when omitted) | - |
| `--author` | Author name (prompted when omitted) | - |
| `--author-email` | Author email (prompted when omitted) | - |
| `--description` | Project description (prompted when omitted) | - |
| `--package-manager` | Package manager to use (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Show the files and packages that would be created, without writing anything | off |
| `--no-venv` | Skip virtual environment creation (implies `--no-install`) | off |
| `--no-install` | Skip dependency installation | off |
| `--yes` / `-y` | Do not ask for confirmation before overwriting existing files when deploying the project in place | off |
| `--help` | Show command help | - |

#### Configuration files (`--config` / `--save-config`)

An interactive session's answers are a plain mapping, and that mapping can
travel through a file. This turns project creation into something you can
commit, review and replay.

```console
# record an interactive session
$ fastkit init --interactive --save-config fastkit.config.json

# replay it later, with no prompts at all
$ fastkit init --config fastkit.config.json
```

If you don't pass `--save-config`, an interactive run that reaches the end
asks whether to save the selections and where to put them. That prompt only
appears when a human is at the terminal — piped or CI runs stay silent and
opt in with the flag instead.

**Supported formats** are chosen from the file extension:

| Extension | Availability |
|---|---|
| `.json` | Always (standard library) |
| `.toml` | Always (standard library) |
| `.yaml` / `.yml` | Only when PyYAML is installed — fastkit does not add it as a runtime dependency |

A loaded file must contain a mapping at its top level with at least
`project_name`, `author` and `author_email`. It is then validated with the
same rules the interactive prompts use (project name shape, email format,
`all_dependencies` must be a list), and every problem is reported before
anything is written. A file that lists only feature selections — no
`all_dependencies` — is expanded through the interactive builder, so a
hand-written config and a wizard session resolve the same package set.

A minimal example:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv"
}
```

#### Configuration file schema

Every config file — hand-written or produced by `--save-config` — is passed
through the same normalizer before it reaches the generator
(`normalize_project_config` in
`backend/project_builder/config_schema.py`). An unknown key, an unknown
choice for a known axis, or a value of the wrong type is rejected with the
offending name and the list of values that are actually allowed, instead of
being silently ignored.

| Key | Shape | Notes |
|---|---|---|
| `project_name`, `author`, `author_email` | string | Required |
| `description` | string | Required |
| `architecture_preset` (alias `preset`) | `"minimal"` \| `"single-module"` \| `"classic-layered"` \| `"domain-starter"` | The two spellings must agree if both are present |
| `package_manager` | `"pip"` \| `"uv"` \| `"pdm"` \| `"poetry"` | |
| `database` | string, or `{"type": <choice>}` | `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `SQLite`, `None` |
| `authentication`, `async_tasks`, `testing`, `caching`, `monitoring`, `migrations`, `logging` | string, or `{"type": <choice>}` | Single-select axes — see the [feature catalog](#interactive-builder-feature-catalog-interactive) above for each axis's choices |
| `utilities`, `tooling` | list of strings | Multi-select axes — same catalog for choices |
| `deployment` | list of strings | Subset of `Docker`, `docker-compose`; picking `docker-compose` pulls in `Docker` automatically |
| `custom_packages` | list of strings | Extra packages to install verbatim |

Every axis accepts either its bare choice (`"authentication": "JWT"`) or the
`{"type": ...}` mapping shape that `database` and a project's own
`[tool.fastapi-fastkit]` metadata use (`"authentication": {"type": "JWT"}`) —
both normalize to the same canonical form, and `--save-config` always writes
the canonical, bare-string form back out.

A config exercising most of the axes:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv",
  "database": "PostgreSQL",
  "authentication": "JWT",
  "async_tasks": "Celery",
  "caching": "Redis",
  "migrations": "Alembic",
  "tooling": ["ruff", "makefile"],
  "deployment": ["Docker"]
}
```

The same configuration as TOML:

```toml
project_name = "orders-api"
author = "Developer Kim"
author_email = "developer@example.com"
description = "Domain-oriented orders service"
architecture_preset = "domain-starter"
package_manager = "uv"
database = "PostgreSQL"
authentication = "JWT"
async_tasks = "Celery"
caching = "Redis"
migrations = "Alembic"
tooling = ["ruff", "makefile"]
deployment = ["Docker"]
```

#### Previewing and skipping steps

`--dry-run` prints the tree that would be created and the packages that
would be installed — with the package manager that would install them —
and then exits without touching the disk:

```console
$ fastkit init --config fastkit.config.json --dry-run
```

`--no-install` stops after the virtual environment is created;
`--no-venv` skips the environment as well (and therefore the install).
Both are useful in containers, in CI, and anywhere the environment is
managed outside fastkit.

#### In-place deployment and overwrite confirmation (`--yes` / `-y`)

When a project is deployed in place — into the current workspace rather
than a new project folder — fastkit asks "Overwrite these files?" before
replacing any file that already exists. `--yes` (or its short form `-y`)
skips that confirmation and proceeds with the overwrite. It does not affect
the separate "Do you want to proceed with project creation?" prompt, which
is still shown. In a non-interactive environment (stdin is not a TTY, as in
CI or a piped run), the overwrite confirmation is skipped automatically
even without `--yes`.

#### Interactive Prompts

The `init` command will prompt you for:

1. **Project name**: Directory name and package name
2. **Author name**: Package author information
3. **Author email**: Contact email for package
4. **Project description**: Brief description of the project
5. **Stack selection**: Choose from minimal, standard, or full
6. **Package manager selection**: Choose from pip, uv, pdm, or poetry (unless specified with `--package-manager`)

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

#### Interactive builder feature catalog (`--interactive`)

`fastkit init --interactive` walks a different, axis-based catalog instead
of the minimal/standard/full stack above (source of truth:
`FastkitConfig.PACKAGE_CATALOG` in `core/settings.py`, and
`DynamicConfigGenerator.build_artifacts()` for what each choice generates).
Every axis defaults to `None` (skip); `utilities` and `tooling` are
multi-select.

Every selection now generates real code, not just installed packages — see
the [architecture preset / feature matrix](../reference/preset-feature-matrix.md)
for how `minimal` / `single-module` (regenerated `main.py`) and
`classic-layered` / `domain-starter` (preserved `main.py`, manual-wiring
warnings) differ.

| Axis | Choices | Installed packages | Generated files |
|---|---|---|---|
| `database` | PostgreSQL, MySQL, MongoDB, Redis, SQLite, None | PostgreSQL: `asyncpg`, `sqlalchemy` · MySQL: `aiomysql`, `sqlalchemy` · MongoDB: `motor` · Redis: `redis[hiredis]` · SQLite: `sqlalchemy`, `aiosqlite` | A database config module at the preset's path (e.g. `src/config/database.py`) |
| `authentication` | JWT, OAuth2, FastAPI-Users, Session-based, None | JWT: `pyjwt[crypto]`, `pwdlib[argon2]` · OAuth2: `authlib`, `itsdangerous`, `httpx` · FastAPI-Users: `fastapi-users[sqlalchemy]`, `pyjwt[crypto]`, `pwdlib[argon2]` · Session-based: `itsdangerous` | An auth config module at the preset's path; OAuth2 and Session-based also add `main.py` middleware setup |
| `async_tasks` | Celery, Dramatiq, None | Celery: `celery[redis]`, `redis[hiredis]` · Dramatiq: `dramatiq[redis]`, `redis[hiredis]` | `<pkg>/worker.py` (background worker) + `<pkg>/features/tasks.py` (task routes) |
| `testing` | Basic, Coverage, Advanced, None | Basic: `pytest`, `pytest-asyncio`, `httpx` · Coverage: + `pytest-cov` · Advanced: + `faker`, `factory-boy` | `pytest.ini`; Advanced also adds `tests/factories.py` and `tests/test_factories.py` |
| `caching` | Redis, None | Redis: `redis[hiredis]`, `fastapi-cache2`, `jinja2` | `<pkg>/features/cache.py` (cached endpoints) |
| `monitoring` | Loguru, OpenTelemetry, Prometheus, None | Loguru: `loguru` · OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp-proto-http` · Prometheus: `prometheus-client`, `prometheus-fastapi-instrumentator` | No standalone file — wired directly into `main.py` (import / lifespan / setup) |
| `utilities` (multi-select) | CORS, Rate-Limiting, Pagination, WebSocket, None | CORS: none (built into FastAPI) · Rate-Limiting: `slowapi` · Pagination: `fastapi-pagination` · WebSocket: `websockets` | CORS and Rate-Limiting wire into `main.py` directly; Pagination adds `<pkg>/features/pagination.py`, WebSocket adds `<pkg>/features/websocket.py` |
| `migrations` | Alembic, None | Alembic: `alembic` | `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, a baseline `alembic/versions/<id>_initial.py`, `scripts/migrate.sh` — only when the database axis is a SQL database |
| `tooling` (multi-select) | ruff, pre-commit, github-actions, devcontainer, makefile, None | ruff: `ruff` · pre-commit: `pre-commit` · github-actions / devcontainer / makefile: none | ruff merges a `[tool.ruff]` block into `pyproject.toml` (or writes `ruff.toml` for `pip` projects); pre-commit writes `.pre-commit-config.yaml`; github-actions writes `.github/workflows/test.yml`; devcontainer writes `.devcontainer/devcontainer.json`; makefile writes `Makefile` |
| `logging` | structured, None | None (stdlib `logging` + `json` only) | `<pkg>/logging_config.py` (structured JSON logging + request-id middleware), wired into `main.py` |

Regardless of selection, every generated project gets `/health` and
`/ready` endpoints in `main.py`, and `--dry-run` prints this exact file set
before anything is written.

#### Examples

<div class="termy">

```console
$ fastkit init
Enter the project name: my-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome API

Select stack (minimal, standard, full): standard
Select package manager (pip, uv, pdm, poetry) [uv]: uv
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
$ fastkit addroute ROUTE_NAME [PROJECT_DIR] [OPTIONS]
```

#### Arguments

| Argument | Description | Required |
|----------|-------------|----------|
| `ROUTE_NAME` | Name of the new route (plural recommended) | Yes |
| `PROJECT_DIR` | Project directory under your workspace (defaults to `.`, the current directory) | No |

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--help` | Show command help | - |

#### Examples

<div class="termy">

```console
$ cd my-api
$ fastkit addroute users
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

You can also target a project under your workspace by name without `cd`-ing into it:

<div class="termy">

```console
$ fastkit addroute users my-api
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

#### Where the code is inserted

`addroute` needs two things from the project: where to put the new imports,
and where to register the router. Templates and generated entrypoints mark
both with anchor comments:

```python
# src/app/api/router.py
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

Keep those comments in place when you edit the file — `addroute` inserts
directly above `# fastkit:imports` and `# fastkit:routes`. A project that
lost them (or was generated before the anchors existed) still works: fastkit
falls back to an AST-based insertion that finds the import block and the
router registrations itself. The anchors simply make the result predictable.

`addroute` also reads the project's `[tool.fastapi-fastkit]` block to locate
the entrypoint, so it works on layouts the on-disk scan alone would rank
wrongly.

### `startdemo`

Create a FastAPI project from a pre-built template.

#### Syntax

```console
$ fastkit startdemo [OPTIONS]
```

#### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-name` | Project name (prompted when omitted) | - |
| `--author` | Author name (prompted when omitted) | - |
| `--author-email` | Author email (prompted when omitted) | - |
| `--description` | Project description (prompted when omitted) | - |
| `--package-manager` | Package manager to use (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Show the files and packages that would be created, without writing anything | off |
| `--no-venv` | Skip virtual environment creation (implies `--no-install`) | off |
| `--no-install` | Skip dependency installation | off |
| `--yes` / `-y` | Do not ask for confirmation before overwriting existing files when deploying the project in place | off |
| `--help` | Show command help | - |

Like `init`, `startdemo` refuses to run when the target project directory
already exists (`Error: Project '{name}' already exists.`). `--dry-run` is
the exception: since it never writes to disk, it is still allowed to target
a name that already has a directory. See
[In-place deployment and overwrite confirmation](#in-place-deployment-and-overwrite-confirmation-yes-y)
above for what `--yes` does when deploying into the current workspace.

#### Interactive Prompts

The `startdemo` command will prompt you for:

1. **Project name**: Directory name for the new project
2. **Author name**: Package author information
3. **Author email**: Contact email
4. **Project description**: Brief description
5. **Package manager selection**: Choose from pip, uv, pdm, or poetry (unless specified with `--package-manager`)

#### Available Templates

| Template | Description | Features |
|----------|-------------|----------|
| `fastapi-default` | Simple FastAPI Project | Basic CRUD, Mock data |
| `fastapi-domain-starter` | Domain-oriented starter | One folder per business concept, `/health` |
| `fastapi-auth-jwt` | JWT authentication | Access/refresh rotation, argon2id, roles and scopes, Alembic |
| `fastapi-sqlmodel` | Async SQLModel persistence | SQLModel + async SQLAlchemy, Alembic, generic CRUD, pagination |
| `fastapi-llm-agent` | Streaming Claude agent | SSE streaming, tool-call loop, conversation memory |
| `fastapi-custom-response` | Custom Response System | Custom responses, Pagination |
| `fastapi-psql-orm` | PostgreSQL FastAPI API | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-mcp` | Model Context Protocol server | MCP integration |
| `fastapi-single-module` | Single-file sandbox | One module, no package boundaries |
| `fastapi-empty` | Minimal FastAPI Project | Bare minimum setup |
| `fastapi-async-crud` | *(deprecated)* Async Item Management API | Superseded by `fastapi-sqlmodel` |
| `fastapi-dockerized` | *(deprecated)* Dockerized FastAPI API | Docker tooling now ships with the newer templates |

The deprecated templates still generate working projects; they are simply no
longer recommended starting points. See
[Which starter should I choose?](choosing-a-starter.md).

#### Examples

<div class="termy">

```console
$ fastkit startdemo fastapi-psql-orm
Enter the project name: my-blog
Enter the author name: Jane Smith
Enter the author email: jane@example.com
Enter the project description: Blog API with PostgreSQL

Select package manager (pip, uv, pdm, poetry) [uv]: poetry
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
- The project must expose a FastAPI app — resolved from
  `[tool.fastapi-fastkit].app_module` when present, otherwise discovered by
  scanning for `main.py`
- Virtual environment should be activated

If neither the recorded entrypoint nor the scan finds a module, `runserver`
reports that it could not find `main.py` and stops.

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

## Project metadata (`[tool.fastapi-fastkit]`)

Every project fastkit generates records how it was produced, in its own
`pyproject.toml`:

```toml
[tool.fastapi-fastkit]
managed = true
version = "1.4.0"
template = "fastapi-domain-starter"
preset = "domain-starter"
package_manager = "uv"
app_module = "src.app.main:app"
features = ["database:PostgreSQL", "authentication:JWT"]
```

| Key | Meaning |
|---|---|
| `managed` | Always `true`; marks the project as fastkit-managed |
| `version` | The fastkit version that generated the project |
| `template` | The `startdemo` template, or the preset's base template |
| `preset` | The `init --interactive` architecture preset (omitted otherwise) |
| `package_manager` | The manager used to build the environment |
| `app_module` | The uvicorn `module:attr` entrypoint |
| `features` | Flat `"<category>:<choice>"` list of interactive selections |

This block is the single source of truth for the project's entrypoint:
`fastkit runserver` reads `app_module` from it before falling back to
scanning the tree, `fastkit addroute` uses it to locate the application, and
generated Dockerfiles use the same value in their `CMD`.

The block is written at the very end of generation — package managers rewrite
`pyproject.toml` while resolving dependencies, so it has to be stamped after
that — and a later regeneration replaces it rather than appending a second
copy. Editing `app_module` by hand is the supported way to tell fastkit about
a layout you reorganized yourself.

## Environment Variables

FastAPI-fastkit respects these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | Configuration directory | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Custom templates directory | Built-in templates |
| `FASTKIT_LOG_LEVEL` | Logging level | `INFO` |
| `FASTKIT_SUBPROCESS_TIMEOUT` | Overrides every package-manager subprocess timeout, in seconds | per-operation (30 / 120 / 900) |

Package manager calls are individually bounded so a hung child process can
never block the CLI: 30 seconds for an availability check, 120 for creating
a virtual environment, 900 for installing dependencies.
`FASTKIT_SUBPROCESS_TIMEOUT` replaces all three with one value — useful on a
slow network, or to fail fast in CI. A value that isn't a positive integer is
ignored.

```console
$ export FASTKIT_SUBPROCESS_TIMEOUT=1800
$ fastkit startdemo fastapi-sqlmodel
```

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
# Add multiple routes (project name as second positional arg = workspace project)
$ fastkit addroute users my-api
$ fastkit addroute products my-api
$ fastkit addroute orders my-api

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
    fastkit addroute "$service"
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

## Package Manager Support

FastAPI-fastkit supports multiple Python package managers, allowing you to choose the one that best fits your workflow.

### Supported Package Managers

| Manager | Description | Dependency File | Best For |
|---------|-------------|----------------|----------|
| **UV** (default) | Fast Python package manager | `pyproject.toml` | Speed and performance |
| **PDM** | Modern Python dependency management | `pyproject.toml` | Advanced dependency resolution |
| **Poetry** | Python dependency management and packaging | `pyproject.toml` | Poetry-based workflows |
| **PIP** | Standard Python package manager | `requirements.txt` | Traditional Python development |

### Specifying Package Manager

#### Global Configuration

You can set your preferred package manager for all projects:

```console
# Using command line options
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

#### Project-specific Selection

Each project can use a different package manager. The choice is made during project creation and affects:

- **Dependency file format**: Each manager creates its appropriate files
- **Virtual environment management**: Different activation methods
- **Dependency installation**: Manager-specific commands

### Package Manager Features

#### UV (Default)
- **Fast**: Rust-based, extremely fast dependency resolution
- **Compatible**: Drop-in replacement for pip and pip-tools
- **Modern**: Support for PEP 621 project metadata

<div class="termy">

```console
$ fastkit init --package-manager uv
# Creates pyproject.toml with UV configuration
```

</div>

#### PDM
- **Modern**: PEP 582 and PEP 621 support
- **Advanced**: Sophisticated dependency resolution
- **Flexible**: Multiple project layouts

<div class="termy">

```console
$ fastkit init --package-manager pdm
# Creates pyproject.toml with PDM configuration
```

</div>

#### Poetry
- **Established**: Mature and widely adopted
- **Integrated**: Build and publish support
- **Lockfile**: poetry.lock for reproducible builds

<div class="termy">

```console
$ fastkit init --package-manager poetry
# Creates pyproject.toml with Poetry configuration
```

</div>

#### PIP
- **Standard**: Built into Python
- **Compatible**: Works everywhere
- **Simple**: Straightforward dependency management

<div class="termy">

```console
$ fastkit init --package-manager pip
# Creates requirements.txt
```

</div>

### Working with Projects

After creating a project with a specific package manager:

#### UV Projects
```console
cd my-project
uv sync          # Install dependencies
uv add requests  # Add new dependency
uv run pytest   # Run commands in environment
```

#### PDM Projects
```console
cd my-project
pdm install      # Install dependencies
pdm add requests # Add new dependency
pdm run pytest  # Run commands in environment
```

#### Poetry Projects
```console
cd my-project
poetry install      # Install dependencies
poetry add requests # Add new dependency
poetry run pytest  # Run commands in environment
```

#### PIP Projects
```console
cd my-project
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install requests
pytest
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

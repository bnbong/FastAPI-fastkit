<p align="center">
    <img align="top" width="70%" src=".github/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>: Fast, easy-to-use starter kit for new users of Python and FastAPI</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-fastkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-fastkit" alt="PyPI - Version">
</a>
<a href="https://github.com/bnbong/FastAPI-fastkit/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/bnbong/FastAPI-fastkit" alt="GitHub Release">
</a>
<a href="https://pepy.tech/project/fastapi-fastkit">
    <img src="https://static.pepy.tech/personalized-badge/fastapi-fastkit?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
</a>
</p>

---

This project was created to speed up the configuration of the development environment needed to develop Python-based web apps for new users of Python and [FastAPI](https://github.com/fastapi/fastapi).

This project was inspired by the `SpringBoot initializer` & Python Django's `django-admin` CLI operation.

!!! info "Translation status"
    English is the source of truth for these docs. Other languages in
    the language switcher may be partial or fall back to English page by
    page. See [Translation Status](reference/translation-status.md) for
    each locale's actual completeness.

## Key Features

- **⚡ Immediate FastAPI project creation** : Super-fast FastAPI workspace & project creation via CLI, inspired by `django-admin` feature of [Python Django](https://github.com/django/django)
- **✨ Interactive project builder**: Guided step-by-step feature selection for databases, authentication, caching, monitoring, and more with auto-generated code
- **🎨 Prettier CLI outputs** : Beautiful CLI experience powered by [rich library](https://github.com/Textualize/rich)
- **📋 Standards-based FastAPI project templates** : All FastAPI-fastkit templates are based on Python standards and FastAPI's common use patterns
- **🔍 Automated template quality assurance** : Weekly automated testing ensures all templates remain functional and up-to-date
- **🚀 Multiple project templates** : Choose from various pre-configured templates for different use cases (async CRUD, Docker, PostgreSQL, etc.)
- **📦 Multiple package manager support** : Choose your preferred Python package manager (pip, uv, pdm, poetry) for dependency management
- **🧾 Reproducible project configs** : Save an interactive session with `--save-config` and replay it later with `fastkit init --config` — no prompts, same project
- **🏷️ Self-describing projects** : Every generated project records its template, preset, package manager, entrypoint and selected features in a `[tool.fastapi-fastkit]` block that `runserver` and `addroute` read back

## Installation

Install `FastAPI-fastkit` at your Python environment.

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## Usage

### Create a new FastAPI project workspace environment immediately

You can now start new FastAPI project really fast with FastAPI-fastkit!

Create a new FastAPI project workspace immediately with:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI project

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-awesome-project         │
│ Author       │ John Doe                   │
│ Author Email │ john@example.com           │
│ Description  │ My awesome FastAPI project │
└──────────────┴────────────────────────────┘

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
FastAPI project will deploy at '~your-project-path~'

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into pyproject.toml              │
╰──────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into config file                 │
╰──────────────────────────────────────────────────────╯

        Creating Project:
       my-awesome-project
┌───────────────────┬───────────┐
│ Component         │ Collected │
│ fastapi           │ ✓         │
│ uvicorn           │ ✓         │
│ pydantic          │ ✓         │
│ pydantic-settings │ ✓         │
└───────────────────┴───────────┘

Creating virtual environment...

╭──────────────────────── Info ────────────────────────╮
│ ℹ venv created at                                    │
│ ~your-project-path~/my-awesome-project/.venv         │
│ To activate the virtual environment, run:            │
│                                                      │
│     source                                           │
│ ~your-project-path~/my-awesome-project/.venv/bin/act │
│ ivate                                                │
╰──────────────────────────────────────────────────────╯

Installing dependencies...
⠙ Setting up project environment...Collecting <packages~>

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-project' has been      │
│ created successfully and saved to                     │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ To start your project, run 'fastkit runserver' at  │
│ newly created FastAPI project directory              │
╰──────────────────────────────────────────────────────╯
```

</div>

This command will create a new FastAPI project workspace environment with Python virtual environment.

- Key options:
  - `--project-name`, `--author`, `--author-email`, `--description`
  - `--package-manager` [pip|uv|pdm|poetry]
  - `--config <path>`: create the project from a saved config file (`.json` / `.toml`, and `.yaml` when PyYAML is installed) with no prompts
  - `--save-config <path>`: with `--interactive`, record the answers for later reuse
  - `--dry-run`: print the files and packages that would be created, write nothing
  - `--no-venv`: skip virtual environment creation (implies `--no-install`)
  - `--no-install`: skip dependency installation
  - `--yes` / `-y`: skip the "Overwrite these files?" confirmation when deploying in place

### Create a project with interactive mode ✨ NEW!

For more complex projects, use the **interactive mode** to build your FastAPI application step-by-step with intelligent feature selection:

<div class="termy">

```console
$ fastkit init --interactive

⚡ FastAPI-fastkit Interactive Project Setup ⚡

📋 Basic Project Information
Enter the project name: my-fullstack-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Full-stack FastAPI project with PostgreSQL and JWT

🧱 Architecture Preset
Pick a project layout. Press Enter to accept the recommended default.
  1. minimal           - Smallest viable FastAPI app
  2. single-module     - Everything in one module (prototypes / scripts)
  3. classic-layered   - api/routes + crud + schemas + core (à la fastapi-default)
  4. domain-starter    - Domain-oriented src/app/domains/<concept>/ (recommended)

Select architecture preset: [4]

🗄️ Database Selection
Select database (PostgreSQL, MySQL, MongoDB, Redis, SQLite, None):
  1. PostgreSQL - PostgreSQL database with SQLAlchemy
  2. MySQL - MySQL database with SQLAlchemy
  3. MongoDB - MongoDB with motor async driver
  4. Redis - Redis for caching and session storage
  5. SQLite - SQLite database for development
  6. None - No database

Select database: 1

🔐 Authentication Selection
Select authentication (JWT, OAuth2, FastAPI-Users, Session-based, None):
  1. JWT - JSON Web Token authentication
  2. OAuth2 - OAuth2 with password flow
  3. FastAPI-Users - Full featured user management
  4. Session-based - Cookie-based sessions
  5. None - No authentication

Select authentication: 1

⚙️ Background Tasks Selection
Select background tasks (Celery, Dramatiq, None):
  1. Celery - Distributed task queue
  2. Dramatiq - Fast and reliable task processing
  3. None - No background tasks

Select background tasks: 1

💾 Caching Selection
Select caching (Redis, fastapi-cache2, None):
  1. Redis - Redis caching
  2. fastapi-cache2 - Simple caching for FastAPI
  3. None - No caching

Select caching: 1

📊 Monitoring Selection
Select monitoring (Loguru, OpenTelemetry, Prometheus, None):
  1. Loguru - Simple and powerful logging
  2. OpenTelemetry - Observability framework
  3. Prometheus - Metrics and monitoring
  4. None - No monitoring

Select monitoring: 3

🧪 Testing Framework Selection
Select testing framework (Basic, Coverage, Advanced, None):
  1. Basic - pytest + httpx for API testing
  2. Coverage - Basic + code coverage
  3. Advanced - Coverage + faker + factory-boy for fixtures
  4. None - No testing framework

Select testing framework: 2

🛠️ Additional Utilities
Select utilities (comma-separated numbers, e.g., 1,3,4):
  1. CORS - Cross-Origin Resource Sharing
  2. Rate-Limiting - Request rate limiting
  3. Pagination - Pagination support
  4. WebSocket - WebSocket support

Select utilities: 1

🪵 Logging Format
Select logging format:
  1. structured - JSON logs + X-Request-ID correlation middleware (stdlib only)
  2. None - Uvicorn's default plain-text logging

Select logging format [2]: 1

🧬 Database Migrations
Select migration tool:
  1. Alembic - alembic.ini + async alembic/env.py + scripts/migrate.sh (recommended for SQL databases)
  2. None - No migration tooling

Select migration tool [1]: 1

🧰 Developer Tooling
Select tooling to generate (comma-separated numbers, e.g., 1,3)
  1. ruff ruff + ruff-format config in pyproject.toml (replaces black/isort)
  2. pre-commit .pre-commit-config.yaml
  3. github-actions .github/workflows/test.yml (Python 3.12)
  4. devcontainer .devcontainer/devcontainer.json
  5. makefile Makefile with install/test/lint/format/run

Your choice (or press Enter to skip): 1,2

🚀 Deployment Configuration
Select deployment option:
  1. Docker - Generate Dockerfile
  2. docker-compose - Generate docker-compose.yml (includes Docker)
  3. None - No deployment configuration

Select deployment option: 2

📦 Package Manager Selection
Select package manager (pip, uv, pdm, poetry): uv

📝 Custom Packages (optional)
Enter custom package names (comma-separated, press Enter to skip):

📋 Project Configuration Summary
┌─────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Setting             │ Value                                                                     │
├─────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ Project Name        │ my-fullstack-project                                                      │
│ Author              │ John Doe                                                                  │
│ Email               │ john@example.com                                                          │
│ Description         │ Full-stack FastAPI project with PostgreSQL and JWT                        │
│ Architecture Preset │ domain-starter — Domain-oriented: src/app/domains/<concept>/ (recommended)│
│ Database            │ PostgreSQL                                                                │
│ Authentication      │ JWT                                                                       │
│ Async Tasks         │ Celery                                                                    │
│ Caching             │ Redis                                                                     │
│ Monitoring          │ Prometheus                                                                │
│ Testing             │ Coverage                                                                  │
│ Utilities           │ CORS                                                                      │
│ Logging             │ structured                                                                │
│ Migrations          │ Alembic                                                                   │
│ Tooling             │ ruff, pre-commit                                                          │
│ Package Manager     │ uv                                                                        │
└─────────────────────┴───────────────────────────────────────────────────────────────────────────┘

Total dependencies to install: 18

Proceed with project creation? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into pyproject.toml              │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated dependency file with 18 packages         │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Preserving template-shipped main.py for preset     │
│ 'domain-starter'.                                    │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated Docker deployment files                  │
╰───────────────────────────────────────────────────────╯
╭────────────────────── Warning ────────────────────────╮
│ ⚠ Preset compatibility                               │
│ fastapi-domain-starter's shipped src/app/main.py is  │
│ preserved. The selections below need manual wiring   │
│ there (CORS is already wired — set                   │
│ BACKEND_CORS_ORIGINS in .env to activate it).        │
│ Affected selections (packages installed, but no      │
│ dynamic main.py edits applied for the                │
│ 'domain-starter' preset): Prometheus                 │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated configuration files for selected stack   │
╰───────────────────────────────────────────────────────╯

Creating virtual environment...
Installing dependencies...

----> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-fullstack-project' from        │
│ 'fastapi-domain-starter' has been created!            │
╰───────────────────────────────────────────────────────╯
```

</div>

The interactive mode provides:

- **Architecture preset selection** (`minimal` / `single-module` / `classic-layered` / `domain-starter`) that picks the right base template and project layout
- **Guided selection** for databases, authentication, background tasks, caching, monitoring, and more
- **Auto-generated code** for selected features — varies by preset (regenerated `main.py` for `minimal` / `single-module`; preserve template-shipped `main.py` and overlay config modules for `classic-layered` / `domain-starter`)
- **Preset-aware Docker generation** — the generated `Dockerfile` `CMD` targets the preset's actual entrypoint (`src.main:app` or `src.app.main:app`)
- **Smart dependency management** with automatic pip compatibility
- **Feature validation** with manual-wiring warnings for selections the preset cannot auto-wire
- **Identity markers** in the generated `pyproject.toml` (description marker + `[tool.fastapi-fastkit]` table) so `is_fastkit_project()` can recognize generated projects later
- **Project metadata** recorded in `[tool.fastapi-fastkit]` — template, preset, package manager, `app_module` and the selected `features` — which `fastkit runserver` and `fastkit addroute` read back
- **Reproducible runs**: `--save-config <path>` records the answers, `--config <path>` replays them without a single prompt, and `--dry-run` previews the result without writing anything

Every catalog selection now generates real, working code rather than just
installing a package — background tasks (Celery/Dramatiq), Redis caching,
WebSocket, Pagination, OpenTelemetry tracing, and OAuth2 / session-based
auth all ship with a matching module and `main.py` wiring. Three new axes
round out the catalog:

- **Logging**: `structured` adds stdlib `logging` + `json` structured output with a request-id middleware — no new dependency
- **Migrations**: `Alembic` generates a full async migration environment (`alembic.ini`, `alembic/env.py`, a baseline revision, `scripts/migrate.sh`) for any SQL database selection
- **Tooling** (multi-select): `ruff`, `pre-commit`, `github-actions`, `devcontainer`, `makefile` — each generates its own config file; `ruff` also merges a `[tool.ruff]` block into `pyproject.toml`

Every generated project also gets `/health` and `/ready` endpoints, and
`--dry-run` lists the exact same file set a real run would write, including
these new artifacts. `classic-layered` and `domain-starter` preserve their
shipped `main.py`, so feature validation warns when a selection under any
of these axes needs manual wiring — see the
[preset / feature matrix](reference/preset-feature-matrix.md) for details.

### Add a new route to the FastAPI project

`FastAPI-fastkit` makes it easy to expand your FastAPI project.

Add a new route endpoint to your FastAPI project with:

<div class="termy">

```console
$ fastkit addroute user my-awesome-project
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-awesome-project                       │
│ Route Name       │ user                                     │
│ Target Directory │ ~your-project-path~                      │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to project 'my-awesome-project'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'user' to project     │
│ `my-awesome-project`                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

### Place a structured FastAPI demo project immediately

You can also start with a structured FastAPI demo project.

Demo projects are consist of various tech stacks with simple item CRUD endpoints implemented.

Place a structured FastAPI demo project immediately with:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-awesome-demo
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI demo
Deploying FastAPI project using 'fastapi-default' template
Template path:
/~fastapi_fastkit-package-path~/fastapi_project_template/fastapi-default

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-demo         │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ My awesome FastAPI demo │
└──────────────┴─────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

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
FastAPI template project will deploy at '~your-project-path~'

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-demo' from             │
│ 'fastapi-default' has been created and saved to       │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

- Key options:
  - `--project-name`, `--author`, `--author-email`, `--description`
  - `--package-manager` [pip|uv|pdm|poetry]
  - `--dry-run`, `--no-venv`, `--no-install`, `--yes`/`-y` — same meaning as on `init`
  - Refuses to run if the target project directory already exists (`--dry-run` excepted)

To view the list of available FastAPI demos, check with:

<div class="termy">

```console
$ fastkit list-templates
                              Available Templates
┌────────────────────────┬───────────────────────────────────────────────────────┐
│ fastapi-custom-response│ Async Item Management API with Custom Response System │
│ fastapi-mcp            │ FastAPI MCP Project                                   │
│ fastapi-domain-starter │ FastAPI Domain Starter                                │
│ fastapi-dockerized     │ Dockerized FastAPI Item Management API                │
│ fastapi-empty          │ Minimal FastAPI Template                              │
│ fastapi-async-crud     │ Async Item Management API Server                      │
│ fastapi-psql-orm       │ Dockerized FastAPI Item Management API with           │
│                        │ PostgreSQL                                            │
│ fastapi-default        │ Simple FastAPI Project                                │
│ fastapi-single-module  │ FastAPI Single Module Template                        │
│ fastapi-auth-jwt       │ FastAPI JWT Authentication                            │
│ fastapi-sqlmodel       │ FastAPI SQLModel                                      │
│ fastapi-llm-agent      │ FastAPI LLM Agent                                     │
└────────────────────────┴───────────────────────────────────────────────────────┘
```

</div>

Available templates:

| Template | Description | Notes |
|---|---|---|
| [`fastapi-default`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-default/README.md-tpl) | Simple FastAPI project with a classic layered layout | Good first choice |
| [`fastapi-empty`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-empty/README.md-tpl) | Minimal FastAPI template | Base for `minimal` preset |
| [`fastapi-single-module`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-single-module/README.md-tpl) | Single-file FastAPI app | Base for `single-module` preset |
| [`fastapi-domain-starter`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-domain-starter/README.md-tpl) | Domain-oriented, pyproject-first starter for medium-sized APIs | Base for `domain-starter` preset |
| [`fastapi-auth-jwt`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-auth-jwt/README.md-tpl) | JWT authentication with refresh-token rotation, argon2 hashing and scopes | New in v1.4.0 |
| [`fastapi-sqlmodel`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-sqlmodel/README.md-tpl) | Async SQLModel + Alembic migrations + generic CRUD with pagination | New in v1.4.0 |
| [`fastapi-llm-agent`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-llm-agent/README.md-tpl) | Streaming Claude chat agent (SSE) with a tool-call loop | New in v1.4.0 |
| [`fastapi-mcp`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-mcp/README.md-tpl) | FastAPI app exposed as an MCP server | |
| [`fastapi-psql-orm`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-psql-orm/README.md-tpl) | Item management API with PostgreSQL, SQLModel, Alembic and docker-compose | Requires Docker |
| [`fastapi-custom-response`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response/README.md-tpl) | Item management API with a custom response envelope, error handling and pagination | |
| [`fastapi-async-crud`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud/README.md-tpl) | Async item management API | **Deprecated** — use `fastapi-sqlmodel` |
| [`fastapi-dockerized`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-dockerized/README.md-tpl) | Dockerized item management API | **Deprecated** — use `fastapi-default` with the Docker option in `init --interactive` |

Deprecated templates still work but are no longer recommended starting points. See [Which starter should I choose?](user-guide/choosing-a-starter.md) for a decision guide.

## Documentation

For comprehensive guides and detailed usage instructions, explore our documentation:

- 🧭 **[Which starter should I choose?](user-guide/choosing-a-starter.md)** - Beginner decision guide for `startdemo` templates and interactive presets
- 📚 **[User Guide](user-guide/quick-start.md)** - Detailed installation and usage guides
- 🎯 **[Tutorial](tutorial/getting-started.md)** - Step-by-step tutorials for beginners
- 📖 **[CLI Reference](user-guide/cli-reference.md)** - Complete command reference
- 🧱 **[Architecture Preset Matrix](reference/preset-feature-matrix.md)** - Per-preset / per-feature contract for interactive generation
- 🔍 **[Template Quality Assurance](reference/template-quality-assurance.md)** - Automated testing and quality standards

## 🚀 Template-based Tutorials

Learn FastAPI development through practical use cases with our pre-built templates:

### 📖 Core Tutorials

- **[Building a Basic API Server](tutorial/basic-api-server.md)** - Create your first FastAPI server using the `fastapi-default` template
- **[Building an Asynchronous CRUD API](tutorial/async-crud-api.md)** - Develop a high-performance async API with the `fastapi-async-crud` template
- **[Domain-oriented Project (Domain Starter)](tutorial/domain-starter.md)** - Build a medium-sized API with the `fastapi-domain-starter` template, the recommended modern default
- **[JWT Authentication](tutorial/auth-jwt.md)** - Add real accounts with the `fastapi-auth-jwt` template: rotating refresh tokens, argon2id hashing, role and scope guards

### 🗄️ Database & Infrastructure

- **[Integrating with a Database](tutorial/database-integration.md)** - Utilize PostgreSQL + SQLAlchemy with the `fastapi-psql-orm` template
- **[Async Persistence with SQLModel](tutorial/sqlmodel.md)** - Async SQLModel, Alembic migrations, a generic CRUD base and paginated lists with the `fastapi-sqlmodel` template
- **[Dockerizing and Deploying](tutorial/docker-deployment.md)** - Set up a production deployment environment using the `fastapi-dockerized` template *(deprecated template — kept for existing users)*

### ⚡ Advanced Features

- **[Custom Response Handling & Advanced API Design](tutorial/custom-response-handling.md)** - Build enterprise-grade APIs with the `fastapi-custom-response` template
- **[Integrating with MCP](tutorial/mcp-integration.md)** - Create an API server integrated with AI models using the `fastapi-mcp` template
- **[Streaming LLM Agent](tutorial/llm-agent.md)** - Build a streaming Claude chat backend with a real tool-call loop using the `fastapi-llm-agent` template

Each tutorial provides:

- ✅ **Practical Examples** - Code you can use directly in real projects
- ✅ **Step-by-Step Guides** - Detailed explanations for beginners to follow easily
- ✅ **Best Practices** - Industry-standard patterns and security considerations
- ✅ **Extension Methods** - Guidance for taking your project to the next level

## Contributing

We welcome contributions from the community! FastAPI-fastkit is designed to help newcomers to Python and FastAPI, and your contributions can make a significant impact.

### What You Can Contribute

- 🚀 **New FastAPI templates** - Add templates for different use cases
- 🐛 **Bug fixes** - Help us improve stability and reliability
- 📚 **Documentation** - Improve guides, examples, and translations
- 🧪 **Tests** - Increase test coverage and add integration tests
- 💡 **Features** - Suggest and implement new CLI features

### Getting Started with Contributing

To get started with contributing to FastAPI-fastkit, please refer to our comprehensive guides:

- **[Development Setup](contributing/development-setup.md)** - Complete guide for setting up your development environment
- **[Code Guidelines](contributing/code-guidelines.md)** - Coding standards and best practices
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** - Comprehensive contribution guide
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** - Project principles and community standards
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** - Security guidelines and reporting

## Significance of FastAPI-fastkit

FastAPI-fastkit aims to provide a fast and easy-to-use starter kit for new users of Python and FastAPI.

This idea was initiated with the aim of helping FastAPI newcomers learn from the beginning, which aligns with the production significance of the FastAPI-cli package added with the [FastAPI 0.111.0 version update](https://github.com/fastapi/fastapi/releases/tag/0.111.0).

As someone who has been using and loving FastAPI for a long time, I wanted to develop a project that could help fulfill [the wonderful motivation](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) that FastAPI developer [tiangolo](https://github.com/tiangolo) has expressed.

FastAPI-fastkit bridges the gap between getting started and building production-ready applications by providing:

- **Immediate productivity** for newcomers who might be overwhelmed by setup complexity
- **Best practices** built into every template, helping users learn proper FastAPI patterns
- **Scalable foundations** that grow with users as they advance from beginners to experts
- **Community-driven templates** that reflect real-world FastAPI usage patterns

## Next Steps

Ready to get started with FastAPI-fastkit? Follow these next steps:

### 🚀 Quick Start

1. **[Installation](user-guide/installation.md)**: Install FastAPI-fastkit
2. **[Quick Start](user-guide/quick-start.md)**: Create your first project in 5 minutes
3. **[Getting Started Tutorial](tutorial/getting-started.md)**: Step-by-step detailed tutorial

### 📚 Advanced Learning

- **[Creating Projects](user-guide/creating-projects.md)**: Create projects with different stacks
- **[Adding Routes](user-guide/adding-routes.md)**: Add API endpoints to your project
- **[Using Templates](user-guide/using-templates.md)**: Use pre-built project templates

### 🛠️ Contributing

Want to contribute to FastAPI-fastkit?

- **[Development Setup](contributing/development-setup.md)**: Set up your development environment
- **[Code Guidelines](contributing/code-guidelines.md)**: Follow our coding standards and best practices
- **[Contributing Guidelines](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)**: Comprehensive contribution guide

### 🔍 Reference

- **[CLI Reference](user-guide/cli-reference.md)**: Complete CLI command reference
- **[Template Quality Assurance](reference/template-quality-assurance.md)**: Automated testing and quality standards
- **[FAQ](reference/faq.md)**: Frequently asked questions
- **[GitHub Repository](https://github.com/bnbong/FastAPI-fastkit)**: Source code and issue tracking

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) file for details.

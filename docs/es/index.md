<p align="center">
    <img align="top" width="70%" src="img/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>: kit de inicio rápido y fácil de usar para nuevos usuarios de Python y FastAPI</em>
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

Este proyecto se creó para acelerar la configuración del entorno de desarrollo que necesitan las personas que se inician con Python y [FastAPI](https://github.com/fastapi/fastapi) para desarrollar aplicaciones web basadas en Python.

Está inspirado en el `SpringBoot initializer` y en el CLI `django-admin` de Python Django.

!!! info "Estado de las traducciones"
    El inglés es la referencia principal de esta documentación. Los demás idiomas del selector pueden estar traducidos solo en parte o mostrar la versión en inglés página por página. Consulta el [Estado de las traducciones](reference/translation-status.md) para ver el grado real de traducción de cada idioma.

## Características principales

- **⚡ Creación inmediata de proyectos FastAPI**: crea espacios de trabajo y proyectos FastAPI en segundos desde la CLI, inspirándose en la experiencia de `django-admin` de [Python Django](https://github.com/django/django)
- **✨ Asistente interactivo de proyectos**: elige paso a paso bases de datos, autenticación, caché, monitorización y más, con generación automática de código
- **🎨 Salida CLI más bonita**: experiencia CLI cuidada gracias a la [librería rich](https://github.com/Textualize/rich)
- **📋 Plantillas de proyecto FastAPI basadas en estándares**: todas las plantillas de FastAPI-fastkit se basan en estándares Python y patrones de uso habituales de FastAPI
- **🔍 Aseguramiento de calidad automatizado de las plantillas**: pruebas automáticas semanales garantizan que todas las plantillas siguen funcionando y al día
- **🚀 Múltiples plantillas de proyecto**: elige entre varias plantillas preconfiguradas para distintos casos de uso (async CRUD, Docker, PostgreSQL, etc.)
- **📦 Soporte de varios gestores de paquetes**: elige tu gestor de paquetes Python preferido (pip, uv, pdm, poetry) para gestionar dependencias
- **🧾 Configuraciones de proyecto reproducibles**: guarda una sesión interactiva con `--save-config` y reprodúcela más tarde con `fastkit init --config` — sin prompts, el mismo proyecto
- **🏷️ Proyectos autodescriptivos**: cada proyecto generado registra su plantilla, preset, gestor de paquetes, entrypoint y funcionalidades seleccionadas en un bloque `[tool.fastapi-fastkit]` que `runserver` y `addroute` vuelven a leer

## Instalación

Instala `FastAPI-fastkit` en tu entorno Python.

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## Uso

### Crear al instante el espacio de trabajo de un nuevo proyecto FastAPI

¡Ahora puedes empezar un nuevo proyecto FastAPI muy rápidamente con FastAPI-fastkit!

Crea al instante un nuevo espacio de trabajo para tu proyecto FastAPI con:

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

Este comando crea un nuevo espacio de trabajo para tu proyecto FastAPI e incluye también un entorno virtual de Python.

- Opciones principales:
  - `--project-name`, `--author`, `--author-email`, `--description`
  - `--package-manager` [pip|uv|pdm|poetry]
  - `--config <path>`: crea el proyecto a partir de un archivo de configuración guardado (`.json` / `.toml`, y `.yaml` cuando PyYAML está instalado), sin prompts
  - `--save-config <path>`: con `--interactive`, registra las respuestas para reutilizarlas después
  - `--dry-run`: muestra los archivos y paquetes que se crearían, sin escribir nada
  - `--no-venv`: omite la creación del entorno virtual (implica `--no-install`)
  - `--no-install`: omite la instalación de dependencias
  - `--yes` / `-y`: omite la confirmación "Overwrite these files?" al desplegar in situ

### Crear un proyecto en modo interactivo ✨ ¡NUEVO!

Para proyectos más complejos, usa el **modo interactivo** para construir tu aplicación FastAPI paso a paso con selección inteligente de funcionalidades:

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

El modo interactivo ofrece:

- **Selección del preset de arquitectura** (`minimal` / `single-module` / `classic-layered` / `domain-starter`) que escoge la plantilla base y el layout adecuados
- **Selección guiada** de bases de datos, autenticación, tareas en segundo plano, caché, monitorización y más
- **Código autogenerado** para las funcionalidades seleccionadas — varía según el preset (`main.py` regenerado para `minimal` / `single-module`; `main.py` que viene en la plantilla preservado y módulos de configuración superpuestos para `classic-layered` / `domain-starter`)
- **Generación de Docker consciente del preset** — el `CMD` del `Dockerfile` generado apunta al punto de entrada real del preset (`src.main:app` o `src.app.main:app`)
- **Gestión inteligente de dependencias** con compatibilidad automática con pip
- **Validación de funcionalidades** con avisos de cableado manual para las selecciones que el preset no puede conectar automáticamente
- **Marcadores de identidad** en el `pyproject.toml` generado (marcador en `description` + tabla `[tool.fastapi-fastkit]`) para que `is_fastkit_project()` reconozca después los proyectos generados
- **Metadatos del proyecto** registrados en `[tool.fastapi-fastkit]` — plantilla, preset, gestor de paquetes, `app_module` y las `features` seleccionadas — que `fastkit runserver` y `fastkit addroute` vuelven a leer
- **Ejecuciones reproducibles**: `--save-config <path>` registra las respuestas, `--config <path>` las reproduce sin un solo prompt y `--dry-run` previsualiza el resultado sin escribir nada

Ahora cada selección del catálogo genera código real y funcional, en lugar de
limitarse a instalar un paquete — las tareas en segundo plano
(Celery/Dramatiq), la caché con Redis, WebSocket, Pagination, el tracing con
OpenTelemetry y la autenticación OAuth2 / basada en sesiones incluyen un
módulo correspondiente y su cableado en `main.py`. Tres ejes nuevos completan
el catálogo:

- **Logging**: `structured` añade salida estructurada con `logging` + `json` de la stdlib y un middleware de request-id — sin dependencias nuevas
- **Migraciones**: `Alembic` genera un entorno de migraciones asíncrono completo (`alembic.ini`, `alembic/env.py`, una revisión base, `scripts/migrate.sh`) para cualquier base de datos SQL seleccionada
- **Herramientas** (selección múltiple): `ruff`, `pre-commit`, `github-actions`, `devcontainer`, `makefile` — cada una genera su propio archivo de configuración; `ruff` además fusiona un bloque `[tool.ruff]` en `pyproject.toml`

Cada proyecto generado obtiene también los endpoints `/health` y `/ready`, y
`--dry-run` lista exactamente el mismo conjunto de archivos que escribiría una
ejecución real, incluidos estos nuevos artefactos. `classic-layered` y
`domain-starter` conservan el `main.py` que trae la plantilla, así que la
validación de funcionalidades avisa cuando una selección de cualquiera de
estos ejes necesita cableado manual — consulta la
[matriz de presets / funcionalidades](reference/preset-feature-matrix.md) para
más detalles.

### Añadir una ruta nueva al proyecto FastAPI

`FastAPI-fastkit` facilita extender tu proyecto FastAPI.

Añade un nuevo endpoint de ruta a tu proyecto FastAPI con:

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

### Desplegar de inmediato un proyecto de demo FastAPI estructurado

También puedes empezar con un proyecto de demo FastAPI estructurado.

Los proyectos demo se componen de varias pilas tecnológicas con endpoints CRUD simples sobre items.

Despliega de inmediato un proyecto de demo FastAPI estructurado con:

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

- Opciones principales:
  - `--project-name`, `--author`, `--author-email`, `--description`
  - `--package-manager` [pip|uv|pdm|poetry]
  - `--dry-run`, `--no-venv`, `--no-install`, `--yes`/`-y` — mismo significado que en `init`
  - Se niega a ejecutarse si el directorio del proyecto de destino ya existe (salvo con `--dry-run`)

Para ver la lista de demos FastAPI disponibles, ejecuta:

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

Plantillas disponibles:

| Plantilla | Descripción | Notas |
|---|---|---|
| [`fastapi-default`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-default/README.md-tpl) | Proyecto FastAPI simple con una estructura clásica por capas | Buena primera opción |
| [`fastapi-empty`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-empty/README.md-tpl) | Plantilla FastAPI mínima | Base del preset `minimal` |
| [`fastapi-single-module`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-single-module/README.md-tpl) | App FastAPI de un solo archivo | Base del preset `single-module` |
| [`fastapi-domain-starter`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-domain-starter/README.md-tpl) | Starter orientado a dominios, centrado en pyproject, para APIs de tamaño medio | Base del preset `domain-starter` |
| [`fastapi-auth-jwt`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-auth-jwt/README.md-tpl) | Autenticación JWT con rotación de refresh tokens, hash argon2 y scopes | Nueva en v1.4.0 |
| [`fastapi-sqlmodel`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-sqlmodel/README.md-tpl) | SQLModel asíncrono + migraciones con Alembic + CRUD genérico con paginación | Nueva en v1.4.0 |
| [`fastapi-llm-agent`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-llm-agent/README.md-tpl) | Agente de chat Claude con streaming (SSE) y bucle de llamadas a herramientas | Nueva en v1.4.0 |
| [`fastapi-mcp`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-mcp/README.md-tpl) | App FastAPI expuesta como servidor MCP | |
| [`fastapi-psql-orm`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-psql-orm/README.md-tpl) | API de gestión de items con PostgreSQL, SQLModel, Alembic y docker-compose | Requiere Docker |
| [`fastapi-custom-response`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response/README.md-tpl) | API de gestión de items con un envoltorio de respuesta personalizado, manejo de errores y paginación | |
| [`fastapi-async-crud`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud/README.md-tpl) | API asíncrona de gestión de items | **Obsoleta** — usa `fastapi-sqlmodel` |
| [`fastapi-dockerized`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/fastapi-dockerized/README.md-tpl) | API de gestión de items dockerizada | **Obsoleta** — usa `fastapi-default` con la opción Docker de `init --interactive` |

Las plantillas obsoletas siguen funcionando, pero ya no son puntos de partida recomendados. Consulta [¿Qué starter elegir?](user-guide/choosing-a-starter.md) para una guía de decisión.

## Documentación

Para guías completas e instrucciones detalladas, explora nuestra documentación:

- 🧭 **[¿Qué starter elegir?](user-guide/choosing-a-starter.md)** - Guía de decisión para principiantes sobre las plantillas de `startdemo` y los presets interactivos
- 📚 **[Guía de usuario](user-guide/quick-start.md)** - Guías detalladas de instalación y uso
- 🎯 **[Tutorial](tutorial/getting-started.md)** - Tutoriales paso a paso para principiantes
- 📖 **[Referencia de la CLI](user-guide/cli-reference.md)** - Referencia completa de comandos
- 🧱 **[Matriz de presets de arquitectura](reference/preset-feature-matrix.md)** - Contrato por preset y por funcionalidad de la generación interactiva
- 🔍 **[Aseguramiento de calidad de plantillas](reference/template-quality-assurance.md)** - Pruebas automatizadas y estándares de calidad

## 🚀 Tutoriales basados en plantillas

Aprende FastAPI con casos prácticos usando nuestras plantillas ya preparadas:

### 📖 Tutoriales centrales

- **[Construir un servidor API básico](tutorial/basic-api-server.md)** - Crea tu primer servidor FastAPI con la plantilla `fastapi-default`
- **[Construir una API CRUD asíncrona](tutorial/async-crud-api.md)** - Desarrolla una API async de alto rendimiento con la plantilla `fastapi-async-crud`
- **[Proyecto orientado a dominios (Domain Starter)](tutorial/domain-starter.md)** - Construye una API mediana con la plantilla `fastapi-domain-starter`, la opción moderna recomendada
- **[Autenticación JWT](tutorial/auth-jwt.md)** - Añade cuentas reales con la plantilla `fastapi-auth-jwt`: refresh tokens rotatorios, hash argon2id y guards de roles y scopes

### 🗄️ Base de datos e infraestructura

- **[Integrar con una base de datos](tutorial/database-integration.md)** - Usa PostgreSQL + SQLAlchemy con la plantilla `fastapi-psql-orm`
- **[Persistencia asíncrona con SQLModel](tutorial/sqlmodel.md)** - SQLModel asíncrono, migraciones con Alembic, una base CRUD genérica y listas paginadas con la plantilla `fastapi-sqlmodel`
- **[Dockerizar y desplegar](tutorial/docker-deployment.md)** - Configura un entorno de despliegue de producción con la plantilla `fastapi-dockerized` *(plantilla obsoleta — se mantiene para los usuarios existentes)*

### ⚡ Funcionalidades avanzadas

- **[Manejo personalizado de respuestas y diseño avanzado de API](tutorial/custom-response-handling.md)** - Construye APIs de nivel empresarial con la plantilla `fastapi-custom-response`
- **[Integrar con MCP](tutorial/mcp-integration.md)** - Crea un servidor API integrado con modelos de IA con la plantilla `fastapi-mcp`
- **[Agente LLM con streaming](tutorial/llm-agent.md)** - Construye un backend de chat Claude con streaming y un bucle real de llamadas a herramientas con la plantilla `fastapi-llm-agent`

Cada tutorial ofrece:

- ✅ **Ejemplos prácticos** - Código que puedes usar directamente en proyectos reales
- ✅ **Guías paso a paso** - Explicaciones detalladas, fáciles de seguir para principiantes
- ✅ **Buenas prácticas** - Patrones estándar de la industria y consideraciones de seguridad
- ✅ **Métodos de extensión** - Orientación para llevar tu proyecto al siguiente nivel

## Cómo colaborar

¡Las contribuciones de la comunidad son bienvenidas! FastAPI-fastkit se diseñó para ayudar a quienes empiezan con Python y FastAPI, y tu contribución puede tener un impacto importante.

### Qué puedes aportar

- 🚀 **Nuevas plantillas FastAPI** - Añade plantillas para distintos casos de uso
- 🐛 **Correcciones de bugs** - Ayúdanos a mejorar la estabilidad y la fiabilidad
- 📚 **Documentación** - Mejora guías, ejemplos y traducciones
- 🧪 **Tests** - Aumenta la cobertura de pruebas y añade tests de integración
- 💡 **Funcionalidades** - Propón e implementa nuevas funcionalidades de la CLI

### Empezar a colaborar

Para empezar a contribuir a FastAPI-fastkit, consulta nuestras guías completas:

- **[Configuración de desarrollo](contributing/development-setup.md)** - Guía completa para configurar tu entorno de desarrollo
- **[Guía de código](contributing/code-guidelines.md)** - Estándares y buenas prácticas de codificación
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** - Guía de contribución completa
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** - Principios del proyecto y estándares de la comunidad
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** - Pautas de seguridad y reportes

## Por qué FastAPI-fastkit

FastAPI-fastkit pretende ofrecer un kit de inicio rápido y fácil de usar a las personas que empiezan con Python y FastAPI.

Esta idea surgió con el objetivo de ayudar a los recién llegados a FastAPI a aprender desde el principio, en línea con el sentido productivo del paquete FastAPI-cli añadido en la [actualización a la versión 0.111.0 de FastAPI](https://github.com/fastapi/fastapi/releases/tag/0.111.0).

Como alguien que lleva mucho tiempo usando y disfrutando FastAPI, quería desarrollar un proyecto que pudiera contribuir a la [maravillosa motivación](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) que ha expresado [tiangolo](https://github.com/tiangolo), creador de FastAPI.

FastAPI-fastkit cubre el hueco entre empezar y construir aplicaciones listas para producción aportando:

- **Productividad inmediata** para los recién llegados a quienes la complejidad inicial puede abrumarles
- **Buenas prácticas** integradas en cada plantilla, ayudando a aprender los patrones correctos de FastAPI
- **Bases escalables** que crecen con el usuario, de principiante a experto
- **Plantillas impulsadas por la comunidad** que reflejan patrones de uso reales de FastAPI

## Próximos pasos

¿Listo para empezar con FastAPI-fastkit? Sigue estos pasos:

### 🚀 Inicio rápido

1. **[Instalación](user-guide/installation.md)**: Instala FastAPI-fastkit
2. **[Inicio rápido](user-guide/quick-start.md)**: Crea tu primer proyecto en 5 minutos
3. **[Tutorial inicial](tutorial/getting-started.md)**: Tutorial detallado paso a paso

### 📚 Aprendizaje avanzado

- **[Crear proyectos](user-guide/creating-projects.md)**: Crea proyectos con distintos stacks
- **[Añadir rutas](user-guide/adding-routes.md)**: Añade endpoints de API a tu proyecto
- **[Usar plantillas](user-guide/using-templates.md)**: Usa plantillas de proyecto ya preparadas

### 🛠️ Contribuir

¿Quieres contribuir a FastAPI-fastkit?

- **[Configuración de desarrollo](contributing/development-setup.md)**: Configura tu entorno de desarrollo
- **[Guía de código](contributing/code-guidelines.md)**: Sigue nuestros estándares y buenas prácticas
- **[Guía de contribución](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)**: Guía completa de contribución

### 🔍 Referencia

- **[Referencia de la CLI](user-guide/cli-reference.md)**: Referencia completa de comandos
- **[Aseguramiento de calidad de plantillas](reference/template-quality-assurance.md)**: Pruebas automatizadas y estándares de calidad
- **[FAQ](reference/faq.md)**: Preguntas frecuentes
- **[Repositorio GitHub](https://github.com/bnbong/FastAPI-fastkit)**: Código fuente y seguimiento de issues

## Licencia

Este proyecto se distribuye bajo la licencia MIT — consulta el archivo [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) para más detalles.

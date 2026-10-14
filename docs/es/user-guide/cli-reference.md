# Referencia de la CLI

Referencia completa de todos los comandos de la CLI de FastAPI-fastkit.

## Opciones globales

Todos los comandos admiten estas opciones globales:

```console
$ fastkit [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Opciones globales

| Opción | Descripción |
|---|---|
| `--version` | Muestra la versión de FastAPI-fastkit |
| `--help` | Muestra el mensaje de ayuda |

### Ejemplos

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

## Comandos

### `init`

Crea un nuevo proyecto FastAPI con configuración interactiva.

#### Sintaxis

```console
$ fastkit init [OPTIONS]
```

#### Opciones

| Opción | Descripción | Por defecto |
|---|---|---|
| `--interactive` | Configuración guiada: preset de arquitectura y después selección de funcionalidades | off |
| `--config <path>` | Crea el proyecto a partir de un archivo de configuración guardado, sin prompts | - |
| `--save-config <path>` | Con `--interactive`, escribe la configuración respondida en esta ruta | - |
| `--project-name` | Nombre del proyecto (se pide si se omite) | - |
| `--author` | Nombre del autor (se pide si se omite) | - |
| `--author-email` | Email del autor (se pide si se omite) | - |
| `--description` | Descripción del proyecto (se pide si se omite) | - |
| `--package-manager` | Gestor de paquetes a usar (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Muestra los archivos y paquetes que se crearían, sin escribir nada | off |
| `--no-venv` | Omite la creación del entorno virtual (implica `--no-install`) | off |
| `--no-install` | Omite la instalación de dependencias | off |
| `--yes` / `-y` | No pide confirmación antes de sobrescribir archivos existentes al desplegar el proyecto in situ | off |
| `--help` | Muestra la ayuda del comando | - |

#### Archivos de configuración (`--config` / `--save-config`)

Las respuestas de una sesión interactiva son un simple mapeo, y ese mapeo
puede viajar en un archivo. Así la creación de un proyecto se convierte en
algo que puedes hacer commit, revisar y reproducir.

```console
# grabar una sesión interactiva
$ fastkit init --interactive --save-config fastkit.config.json

# reproducirla más tarde, sin ningún prompt
$ fastkit init --config fastkit.config.json
```

Si no pasas `--save-config`, una ejecución interactiva que llega al final
pregunta si quieres guardar las selecciones y dónde. Ese prompt solo aparece
cuando hay una persona delante del terminal — las ejecuciones con pipe o en
CI no preguntan nada y activan el guardado con el flag.

**Los formatos soportados** se eligen según la extensión del archivo:

| Extensión | Disponibilidad |
|---|---|
| `.json` | Siempre (biblioteca estándar) |
| `.toml` | Siempre (biblioteca estándar) |
| `.yaml` / `.yml` | Solo cuando PyYAML está instalado — fastkit no lo añade como dependencia de ejecución |

Un archivo cargado debe contener un mapeo en su nivel superior con al menos
`project_name`, `author` y `author_email`. Después se valida con las mismas
reglas que usan los prompts interactivos (forma del nombre del proyecto,
formato del email, `all_dependencies` debe ser una lista), y se informa de
todos los problemas antes de escribir nada. Un archivo que solo enumera
selecciones de funcionalidades — sin `all_dependencies` — se expande a través
del builder interactivo, de modo que una configuración escrita a mano y una
sesión del asistente resuelven el mismo conjunto de paquetes.

Un ejemplo mínimo:

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

#### Esquema del archivo de configuración

Todo archivo de configuración — escrito a mano o producido por
`--save-config` — pasa por el mismo normalizador antes de llegar al generador
(`normalize_project_config` en
`backend/project_builder/config_schema.py`). Una clave desconocida, una
opción desconocida para un eje conocido o un valor de tipo incorrecto se
rechaza indicando el nombre problemático y la lista de valores realmente
permitidos, en lugar de ignorarse en silencio.

| Clave | Forma | Notas |
|---|---|---|
| `project_name`, `author`, `author_email` | string | Obligatorias |
| `description` | string | Obligatoria |
| `architecture_preset` (alias `preset`) | `"minimal"` \| `"single-module"` \| `"classic-layered"` \| `"domain-starter"` | Si aparecen ambas formas, deben coincidir |
| `package_manager` | `"pip"` \| `"uv"` \| `"pdm"` \| `"poetry"` | |
| `database` | string, o `{"type": <choice>}` | `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `SQLite`, `None` |
| `authentication`, `async_tasks`, `testing`, `caching`, `monitoring`, `migrations`, `logging` | string, o `{"type": <choice>}` | Ejes de selección única — consulta el [catálogo de funcionalidades](#catalogo-de-funcionalidades-del-builder-interactivo-interactive) más arriba para ver las opciones de cada eje |
| `utilities`, `tooling` | lista de strings | Ejes de selección múltiple — mismo catálogo para las opciones |
| `deployment` | lista de strings | Subconjunto de `Docker`, `docker-compose`; elegir `docker-compose` añade `Docker` automáticamente |
| `custom_packages` | lista de strings | Paquetes adicionales que se instalan tal cual |

Cada eje acepta su opción sin más (`"authentication": "JWT"`) o la forma de
mapeo `{"type": ...}` que usan `database` y los propios metadatos
`[tool.fastapi-fastkit]` de un proyecto (`"authentication": {"type": "JWT"}`)
— ambas se normalizan a la misma forma canónica, y `--save-config` siempre
escribe de vuelta la forma canónica de string simple.

Una configuración que usa la mayoría de los ejes:

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

La misma configuración en TOML:

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

#### Previsualizar y omitir pasos

`--dry-run` muestra el árbol que se crearía y los paquetes que se instalarían
— con el gestor de paquetes que los instalaría — y después termina sin tocar
el disco:

```console
$ fastkit init --config fastkit.config.json --dry-run
```

`--no-install` se detiene después de crear el entorno virtual;
`--no-venv` omite también el entorno (y, por tanto, la instalación).
Ambos son útiles en contenedores, en CI y en cualquier lugar donde el
entorno se gestione fuera de fastkit.

#### Despliegue in situ y confirmación de sobrescritura (`--yes` / `-y`)

Cuando un proyecto se despliega in situ — en el workspace actual en lugar de
en una carpeta de proyecto nueva — fastkit pregunta "Overwrite these files?"
antes de sustituir cualquier archivo que ya exista. `--yes` (o su forma corta
`-y`) omite esa confirmación y procede con la sobrescritura. No afecta al
prompt independiente "Do you want to proceed with project creation?", que se
sigue mostrando. En un entorno no interactivo (stdin no es un TTY, como en CI
o en una ejecución con pipe), la confirmación de sobrescritura se omite
automáticamente incluso sin `--yes`.

#### Prompts interactivos

El comando `init` te pedirá:

1. **Nombre del proyecto**: nombre del directorio y del paquete
2. **Nombre del autor**: información del autor del paquete
3. **Email del autor**: email de contacto del paquete
4. **Descripción del proyecto**: descripción breve del proyecto
5. **Selección del stack**: elige entre minimal, standard o full
6. **Selección del gestor de paquetes**: elige entre pip, uv, pdm o poetry (a menos que lo especifiques con `--package-manager`)

#### Opciones de stack

**Stack MINIMAL:**

- `fastapi` - Framework FastAPI
- `uvicorn` - Servidor ASGI
- `pydantic` - Validación de datos
- `pydantic-settings` - Gestión de configuración

**Stack STANDARD:**

- Todos los paquetes del stack MINIMAL
- `sqlalchemy` - Toolkit SQL y ORM
- `alembic` - Herramienta de migraciones de base de datos
- `pytest` - Framework de pruebas

**Stack FULL:**

- Todos los paquetes del stack STANDARD
- `redis` - Almacén de datos en memoria
- `celery` - Cola distribuida de tareas

#### Catálogo de funcionalidades del builder interactivo (`--interactive`)

`fastkit init --interactive` recorre un catálogo distinto, basado en ejes, en
lugar del stack minimal/standard/full anterior (fuente de verdad:
`FastkitConfig.PACKAGE_CATALOG` en `core/settings.py`, y
`DynamicConfigGenerator.build_artifacts()` para lo que genera cada opción).
Cada eje tiene `None` (omitir) como valor por defecto; `utilities` y
`tooling` son de selección múltiple.

Ahora cada selección genera código real, no solo paquetes instalados —
consulta la [matriz de presets de arquitectura / funcionalidades](../reference/preset-feature-matrix.md)
para ver en qué se diferencian `minimal` / `single-module` (`main.py`
regenerado) y `classic-layered` / `domain-starter` (`main.py` conservado,
avisos de cableado manual).

| Eje | Opciones | Paquetes instalados | Archivos generados |
|---|---|---|---|
| `database` | PostgreSQL, MySQL, MongoDB, Redis, SQLite, None | PostgreSQL: `asyncpg`, `sqlalchemy` · MySQL: `aiomysql`, `sqlalchemy` · MongoDB: `motor` · Redis: `redis[hiredis]` · SQLite: `sqlalchemy`, `aiosqlite` | Un módulo de configuración de base de datos en la ruta del preset (p. ej. `src/config/database.py`) |
| `authentication` | JWT, OAuth2, FastAPI-Users, Session-based, None | JWT: `pyjwt[crypto]`, `pwdlib[argon2]` · OAuth2: `authlib`, `itsdangerous`, `httpx` · FastAPI-Users: `fastapi-users[sqlalchemy]`, `pyjwt[crypto]`, `pwdlib[argon2]` · Session-based: `itsdangerous` | Un módulo de configuración de auth en la ruta del preset; OAuth2 y Session-based añaden además la configuración de middleware en `main.py` |
| `async_tasks` | Celery, Dramatiq, None | Celery: `celery[redis]`, `redis[hiredis]` · Dramatiq: `dramatiq[redis]`, `redis[hiredis]` | `<pkg>/worker.py` (worker en segundo plano) + `<pkg>/features/tasks.py` (rutas de tareas) |
| `testing` | Basic, Coverage, Advanced, None | Basic: `pytest`, `pytest-asyncio`, `httpx` · Coverage: + `pytest-cov` · Advanced: + `faker`, `factory-boy` | `pytest.ini`; Advanced añade además `tests/factories.py` y `tests/test_factories.py` |
| `caching` | Redis, None | Redis: `redis[hiredis]`, `fastapi-cache2`, `jinja2` | `<pkg>/features/cache.py` (endpoints con caché) |
| `monitoring` | Loguru, OpenTelemetry, Prometheus, None | Loguru: `loguru` · OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp-proto-http` · Prometheus: `prometheus-client`, `prometheus-fastapi-instrumentator` | Sin archivo independiente — se cablea directamente en `main.py` (import / lifespan / setup) |
| `utilities` (selección múltiple) | CORS, Rate-Limiting, Pagination, WebSocket, None | CORS: ninguno (integrado en FastAPI) · Rate-Limiting: `slowapi` · Pagination: `fastapi-pagination` · WebSocket: `websockets` | CORS y Rate-Limiting se cablean directamente en `main.py`; Pagination añade `<pkg>/features/pagination.py` y WebSocket añade `<pkg>/features/websocket.py` |
| `migrations` | Alembic, None | Alembic: `alembic` | `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, una revisión base `alembic/versions/<id>_initial.py`, `scripts/migrate.sh` — solo cuando el eje de base de datos es una base de datos SQL |
| `tooling` (selección múltiple) | ruff, pre-commit, github-actions, devcontainer, makefile, None | ruff: `ruff` · pre-commit: `pre-commit` · github-actions / devcontainer / makefile: ninguno | ruff fusiona un bloque `[tool.ruff]` en `pyproject.toml` (o escribe `ruff.toml` en proyectos `pip`); pre-commit escribe `.pre-commit-config.yaml`; github-actions escribe `.github/workflows/test.yml`; devcontainer escribe `.devcontainer/devcontainer.json`; makefile escribe `Makefile` |
| `logging` | structured, None | Ninguno (solo `logging` + `json` de la stdlib) | `<pkg>/logging_config.py` (logging JSON estructurado + middleware de request-id), cableado en `main.py` |

Sea cual sea la selección, cada proyecto generado obtiene los endpoints
`/health` y `/ready` en `main.py`, y `--dry-run` muestra exactamente este
conjunto de archivos antes de escribir nada.

#### Ejemplos

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

#### Estructura generada

Crea un proyecto con esta estructura:

```
my-api/
├── .venv/                    # Entorno virtual
├── src/
│   ├── __init__.py
│   ├── main.py              # Aplicación FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuración
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # Conjunto de routers de la API
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── items.py     # Ruta de ejemplo
│   ├── crud/
│   │   ├── __init__.py
│   │   └── items.py         # Operaciones CRUD
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── items.py         # Esquemas Pydantic
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Datos de prueba
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

### `addroute`

Añade una nueva ruta de API a un proyecto FastAPI existente.

#### Sintaxis

```console
$ fastkit addroute ROUTE_NAME [PROJECT_DIR] [OPTIONS]
```

#### Argumentos

| Argumento | Descripción | Obligatorio |
|---|---|---|
| `ROUTE_NAME` | Nombre de la nueva ruta (se recomienda en plural) | Sí |
| `PROJECT_DIR` | Directorio del proyecto bajo tu espacio de trabajo (por defecto `.`, el directorio actual) | No |

#### Opciones

| Opción | Descripción | Por defecto |
|---|---|---|
| `--help` | Muestra la ayuda del comando | - |

#### Ejemplos

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

También puedes apuntar a un proyecto bajo tu espacio de trabajo por nombre sin tener que hacer `cd`:

<div class="termy">

```console
$ fastkit addroute users my-api
```

</div>

#### Archivos generados

Crea estos archivos en el proyecto:

- `src/api/routes/users.py` - Handlers de ruta
- `src/crud/users.py` - Operaciones CRUD
- `src/schemas/users.py` - Esquemas Pydantic

También actualiza `src/api/api.py` para incluir el nuevo router.

#### Endpoints generados

Crea endpoints CRUD completos:

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/users/` | Obtener todos los usuarios |
| `POST` | `/api/v1/users/` | Crear un usuario nuevo |
| `GET` | `/api/v1/users/{user_id}` | Obtener un usuario concreto |
| `PUT` | `/api/v1/users/{user_id}` | Actualizar un usuario |
| `DELETE` | `/api/v1/users/{user_id}` | Eliminar un usuario |

#### Dónde se inserta el código

`addroute` necesita dos cosas del proyecto: dónde poner los nuevos imports y
dónde registrar el router. Las plantillas y los entrypoints generados marcan
ambos lugares con comentarios ancla:

```python
# src/app/api/router.py
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

Mantén esos comentarios en su sitio cuando edites el archivo — `addroute`
inserta justo encima de `# fastkit:imports` y `# fastkit:routes`. Un
proyecto que los haya perdido (o que se generó antes de que existieran las
anclas) sigue funcionando: fastkit recurre a una inserción basada en AST que
encuentra por sí misma el bloque de imports y los registros de routers. Las
anclas simplemente hacen que el resultado sea predecible.

`addroute` también lee el bloque `[tool.fastapi-fastkit]` del proyecto para
localizar el entrypoint, así que funciona en estructuras que el escaneo del
disco por sí solo clasificaría mal.

### `startdemo`

Crea un proyecto FastAPI a partir de una plantilla ya preparada.

#### Sintaxis

```console
$ fastkit startdemo [OPTIONS]
```

#### Opciones

| Opción | Descripción | Por defecto |
|---|---|---|
| `--project-name` | Nombre del proyecto (se pide si se omite) | - |
| `--author` | Nombre del autor (se pide si se omite) | - |
| `--author-email` | Email del autor (se pide si se omite) | - |
| `--description` | Descripción del proyecto (se pide si se omite) | - |
| `--package-manager` | Gestor de paquetes a usar (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Muestra los archivos y paquetes que se crearían, sin escribir nada | off |
| `--no-venv` | Omite la creación del entorno virtual (implica `--no-install`) | off |
| `--no-install` | Omite la instalación de dependencias | off |
| `--yes` / `-y` | No pide confirmación antes de sobrescribir archivos existentes al desplegar el proyecto in situ | off |
| `--help` | Muestra la ayuda del comando | - |

Igual que `init`, `startdemo` se niega a ejecutarse cuando el directorio del
proyecto de destino ya existe (`Error: Project '{name}' already exists.`).
`--dry-run` es la excepción: como nunca escribe en disco, sí puede apuntar a
un nombre que ya tiene directorio. Consulta
[Despliegue in situ y confirmación de sobrescritura](#despliegue-in-situ-y-confirmacion-de-sobrescritura-yes-y)
más arriba para ver qué hace `--yes` al desplegar en el workspace actual.

#### Prompts interactivos

El comando `startdemo` te pedirá:

1. **Nombre del proyecto**: nombre del directorio del nuevo proyecto
2. **Nombre del autor**: información del autor del paquete
3. **Email del autor**: email de contacto
4. **Descripción del proyecto**: descripción breve
5. **Selección del gestor de paquetes**: elige entre pip, uv, pdm o poetry (a menos que lo especifiques con `--package-manager`)

#### Plantillas disponibles

| Plantilla | Descripción | Funcionalidades |
|---|---|---|
| `fastapi-default` | Proyecto FastAPI simple | CRUD básico, datos mock |
| `fastapi-domain-starter` | Starter orientado a dominios | Una carpeta por concepto de negocio, `/health` |
| `fastapi-auth-jwt` | Autenticación JWT | Rotación de access/refresh, argon2id, roles y scopes, Alembic |
| `fastapi-sqlmodel` | Persistencia asíncrona con SQLModel | SQLModel + SQLAlchemy asíncrono, Alembic, CRUD genérico, paginación |
| `fastapi-llm-agent` | Agente Claude con streaming | Streaming SSE, bucle de llamadas a herramientas, memoria de conversación |
| `fastapi-custom-response` | Sistema de respuesta personalizada | Respuestas a medida, paginación |
| `fastapi-psql-orm` | API FastAPI con PostgreSQL | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-mcp` | Servidor Model Context Protocol | Integración con MCP |
| `fastapi-single-module` | Sandbox de un solo archivo | Un módulo, sin fronteras de paquete |
| `fastapi-empty` | Proyecto FastAPI mínimo | Configuración mínima |
| `fastapi-async-crud` | *(obsoleta)* API de gestión de items async | Sustituida por `fastapi-sqlmodel` |
| `fastapi-dockerized` | *(obsoleta)* API FastAPI dockerizada | Las herramientas de Docker vienen ahora con las plantillas más nuevas |

Las plantillas obsoletas siguen generando proyectos que funcionan;
simplemente ya no son puntos de partida recomendados. Consulta
[¿Qué starter elegir?](choosing-a-starter.md).

#### Ejemplos

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

Arranca el servidor de desarrollo de FastAPI.

#### Sintaxis

```console
$ fastkit runserver [OPTIONS]
```

#### Opciones

| Opción | Corto | Descripción | Por defecto |
|---|---|---|---|
| `--host` | `-h` | Host al que enlazar | `127.0.0.1` |
| `--port` | `-p` | Puerto al que enlazar | `8000` |
| `--reload` | `-r` | Activar recarga automática | `True` |
| `--workers` | `-w` | Número de workers | `1` |
| `--help` | | Muestra la ayuda del comando | - |

#### Ejemplos

<div class="termy">

```console
# Uso básico (configuración por defecto)
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000

# Host y puerto personalizados
$ fastkit runserver --host 0.0.0.0 --port 8080
INFO:     Uvicorn running on http://0.0.0.0:8080

# Desactivar recarga automática
$ fastkit runserver --no-reload
INFO:     Uvicorn running on http://127.0.0.1:8000

# Varios workers (producción)
$ fastkit runserver --workers 4
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

#### Requisitos

- Debe ejecutarse desde el directorio de un proyecto FastAPI
- El proyecto debe exponer una app FastAPI — se resuelve desde
  `[tool.fastapi-fastkit].app_module` cuando existe y, si no, se descubre
  buscando `main.py`
- El entorno virtual debe estar activado

Si ni el entrypoint registrado ni el escaneo encuentran un módulo,
`runserver` informa de que no ha podido encontrar `main.py` y se detiene.

### `list-templates`

Lista todas las plantillas de proyecto FastAPI disponibles.

#### Sintaxis

```console
$ fastkit list-templates [OPTIONS]
```

#### Opciones

| Opción | Descripción | Por defecto |
|---|---|---|
| `--help` | Muestra la ayuda del comando | - |

#### Ejemplos

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

## Metadatos del proyecto (`[tool.fastapi-fastkit]`)

Cada proyecto que genera fastkit registra cómo se produjo, en su propio
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

| Clave | Significado |
|---|---|
| `managed` | Siempre `true`; marca el proyecto como gestionado por fastkit |
| `version` | La versión de fastkit que generó el proyecto |
| `template` | La plantilla de `startdemo`, o la plantilla base del preset |
| `preset` | El preset de arquitectura de `init --interactive` (se omite en otro caso) |
| `package_manager` | El gestor usado para construir el entorno |
| `app_module` | El entrypoint `module:attr` de uvicorn |
| `features` | Lista plana `"<category>:<choice>"` de las selecciones interactivas |

Este bloque es la única fuente de verdad del entrypoint del proyecto:
`fastkit runserver` lee `app_module` de aquí antes de recurrir al escaneo del
árbol, `fastkit addroute` lo usa para localizar la aplicación y los
Dockerfiles generados usan el mismo valor en su `CMD`.

El bloque se escribe al final de la generación — los gestores de paquetes
reescriben `pyproject.toml` mientras resuelven dependencias, así que hay que
estamparlo después — y una regeneración posterior lo sustituye en lugar de
añadir una segunda copia. Editar `app_module` a mano es la forma soportada de
indicar a fastkit una estructura que has reorganizado tú mismo.

## Variables de entorno

FastAPI-fastkit respeta estas variables de entorno:

| Variable | Descripción | Por defecto |
|---|---|---|
| `FASTKIT_CONFIG_DIR` | Directorio de configuración | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Directorio de plantillas personalizadas | Plantillas integradas |
| `FASTKIT_LOG_LEVEL` | Nivel de log | `INFO` |
| `FASTKIT_SUBPROCESS_TIMEOUT` | Sustituye todos los timeouts de los subprocesos del gestor de paquetes, en segundos | por operación (30 / 120 / 900) |

Cada llamada al gestor de paquetes tiene su propio límite, para que un
proceso hijo colgado nunca pueda bloquear la CLI: 30 segundos para una
comprobación de disponibilidad, 120 para crear un entorno virtual y 900 para
instalar dependencias. `FASTKIT_SUBPROCESS_TIMEOUT` sustituye los tres por un
único valor — útil en una red lenta o para fallar rápido en CI. Un valor que
no sea un entero positivo se ignora.

```console
$ export FASTKIT_SUBPROCESS_TIMEOUT=1800
$ fastkit startdemo fastapi-sqlmodel
```

### Ejemplos

<div class="termy">

```console
# Directorio de configuración personalizado
$ export FASTKIT_CONFIG_DIR=~/my-fastkit-config
$ fastkit init

# Directorio de plantillas personalizadas
$ export FASTKIT_TEMPLATES_DIR=~/my-templates
$ fastkit list-templates

# Logs de depuración
$ export FASTKIT_LOG_LEVEL=DEBUG
$ fastkit init
```

</div>

## Archivos de configuración

FastAPI-fastkit puede usar archivos de configuración para los valores por defecto.

### Ubicación del archivo de configuración

1. `$FASTKIT_CONFIG_DIR/config.yaml` (si `FASTKIT_CONFIG_DIR` está definido)
2. `~/.fastkit/config.yaml` (por defecto)
3. `./fastkit.yaml` (específico del proyecto)

### Formato del archivo de configuración

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

## Flujos de trabajo habituales

### 1. Crear un proyecto nuevo

<div class="termy">

```console
# Crear un proyecto nuevo
$ fastkit init
# Sigue los prompts...

# Entrar en el proyecto
$ cd my-awesome-api

# Activar el entorno virtual
$ source .venv/bin/activate

# Arrancar el servidor de desarrollo
$ fastkit runserver
```

</div>

### 2. Añadir funcionalidades a un proyecto existente

<div class="termy">

```console
# Añadir varias rutas (segundo argumento posicional = proyecto del workspace)
$ fastkit addroute users my-api
$ fastkit addroute products my-api
$ fastkit addroute orders my-api

# Probar la API
$ fastkit runserver
# Visita http://127.0.0.1:8000/docs
```

</div>

### 3. Usar plantillas para proyectos complejos

<div class="termy">

```console
# Listar las plantillas disponibles
$ fastkit list-templates

# Crear desde plantilla
$ fastkit startdemo
# Selecciona fastapi-psql-orm para un proyecto con base de datos

# Configurar la base de datos (para la plantilla PostgreSQL)
$ cd my-project
$ docker-compose up -d postgres
$ source .venv/bin/activate
$ alembic upgrade head
$ fastkit runserver
```

</div>

## Solución de problemas

### Comando no encontrado

Si el comando `fastkit` no aparece:

1. **Comprueba la instalación:**
   <div class="termy">
   ```console
   $ pip show fastapi-fastkit
   ```
   </div>

2. **Reinstala si hace falta:**
   <div class="termy">
   ```console
   $ pip uninstall fastapi-fastkit
   $ pip install fastapi-fastkit
   ```
   </div>

3. **Comprueba el PATH:**
   <div class="termy">
   ```console
   $ which fastkit
   ```
   </div>

### Problemas con el entorno virtual

Si la creación del entorno virtual falla:

1. **Comprueba la versión de Python:**
   <div class="termy">
   ```console
   $ python --version  # Debería ser 3.12+
   ```
   </div>

2. **Comprueba el módulo venv:**
   <div class="termy">
   ```console
   $ python -m venv --help
   ```
   </div>

3. **Entorno virtual manual:**
   <div class="termy">
   ```console
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ```
   </div>

### El servidor no arranca

Si `fastkit runserver` falla:

1. **Comprueba que estás en el directorio del proyecto**
2. **Verifica que existe `src/main.py`**
3. **Activa el entorno virtual:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

4. **Comprueba errores de sintaxis:**
   <div class="termy">
   ```console
   $ python -c "from src.main import app"
   ```
   </div>

### Puerto ya en uso

Si el puerto 8000 está ocupado:

<div class="termy">

```console
# Usa otro puerto
$ fastkit runserver --port 8080

# O mata el proceso existente
$ lsof -ti:8000 | xargs kill -9
```

</div>

## Uso avanzado

### Plantillas personalizadas

Puedes crear plantillas personalizadas siguiendo estos pasos:

1. **Crear el directorio de la plantilla:**
   ```
   my-template/
   ├── src/
   │   └── main.py-tpl
   ├── requirements.txt-tpl
   └── setup.py-tpl
   ```

2. **Definir la variable de entorno:**
   <div class="termy">
   ```console
   $ export FASTKIT_TEMPLATES_DIR=~/my-templates
   ```
   </div>

3. **Usar la plantilla personalizada:**
   <div class="termy">
   ```console
   $ fastkit startdemo
   # Tus plantillas personalizadas aparecerán en la lista
   ```
   </div>

### FastAPI-fastkit desde scripts

Puedes usar FastAPI-fastkit en scripts:

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

### Integración con CI/CD

Ejemplo de flujo de trabajo con GitHub Actions:

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

## Soporte de gestores de paquetes

FastAPI-fastkit soporta varios gestores de paquetes Python para que elijas el que mejor encaje con tu flujo de trabajo.

### Gestores soportados

| Gestor | Descripción | Archivo de dependencias | Ideal para |
|---|---|---|---|
| **UV** (por defecto) | Gestor de paquetes Python rápido | `pyproject.toml` | Velocidad y rendimiento |
| **PDM** | Gestión moderna de dependencias Python | `pyproject.toml` | Resolución avanzada de dependencias |
| **Poetry** | Gestión de dependencias y empaquetado Python | `pyproject.toml` | Flujos basados en Poetry |
| **PIP** | Gestor estándar de paquetes Python | `requirements.txt` | Desarrollo tradicional en Python |

### Especificar el gestor de paquetes

#### Configuración global

Puedes definir tu gestor preferido para todos los proyectos:

```console
# Con opciones de línea de comandos
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

#### Selección por proyecto

Cada proyecto puede usar un gestor distinto. La elección se hace en el momento de la creación y afecta a:

- **Formato del archivo de dependencias**: cada gestor crea los archivos apropiados
- **Gestión del entorno virtual**: distintos métodos de activación
- **Instalación de dependencias**: comandos específicos por gestor

### Características de los gestores

#### UV (por defecto)
- **Rápido**: basado en Rust, resolución de dependencias extremadamente rápida
- **Compatible**: sustituye directamente a pip y pip-tools
- **Moderno**: soporta los metadatos de proyecto PEP 621

<div class="termy">

```console
$ fastkit init --package-manager uv
# Crea un pyproject.toml con configuración para UV
```

</div>

#### PDM
- **Moderno**: soporta PEP 582 y PEP 621
- **Avanzado**: resolución de dependencias sofisticada
- **Flexible**: varias estructuras de proyecto

<div class="termy">

```console
$ fastkit init --package-manager pdm
# Crea un pyproject.toml con configuración para PDM
```

</div>

#### Poetry
- **Consolidado**: maduro y muy adoptado
- **Integrado**: soporte de build y publicación
- **Lockfile**: poetry.lock para builds reproducibles

<div class="termy">

```console
$ fastkit init --package-manager poetry
# Crea un pyproject.toml con configuración para Poetry
```

</div>

#### PIP
- **Estándar**: viene con Python
- **Compatible**: funciona en todas partes
- **Simple**: gestión de dependencias directa

<div class="termy">

```console
$ fastkit init --package-manager pip
# Crea requirements.txt
```

</div>

### Trabajar con los proyectos

Tras crear un proyecto con un gestor concreto:

#### Proyectos UV
```console
cd my-project
uv sync          # Instalar dependencias
uv add requests  # Añadir nueva dependencia
uv run pytest   # Ejecutar comandos dentro del entorno
```

#### Proyectos PDM
```console
cd my-project
pdm install      # Instalar dependencias
pdm add requests # Añadir nueva dependencia
pdm run pytest  # Ejecutar comandos dentro del entorno
```

#### Proyectos Poetry
```console
cd my-project
poetry install      # Instalar dependencias
poetry add requests # Añadir nueva dependencia
poetry run pytest  # Ejecutar comandos dentro del entorno
```

#### Proyectos PIP
```console
cd my-project
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install requests
pytest
```

## Próximos pasos

Ahora que conoces la CLI:

1. **[Inicio rápido](quick-start.md)**: Prueba los comandos en la práctica
2. **[Tu primer proyecto](../tutorial/first-project.md)**: Construye una aplicación completa
3. **[Contribuir](../contributing/development-setup.md)**: Contribuye a FastAPI-fastkit

!!! tip "Consejos de la CLI"
    - Usa `--help` con cualquier comando para ver la ayuda detallada
    - Configura los valores por defecto para acelerar la creación de proyectos
    - Usa plantillas para setups de proyecto complejos
    - Combina comandos para crear flujos de trabajo potentes

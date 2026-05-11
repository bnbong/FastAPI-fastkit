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
| `--package-manager` | Gestor de paquetes a usar (pip, uv, pdm, poetry) | uv |
| `--help` | Muestra la ayuda del comando | - |

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

### `startdemo`

Crea un proyecto FastAPI a partir de una plantilla ya preparada.

#### Sintaxis

```console
$ fastkit startdemo [OPTIONS]
```

#### Opciones

| Opción | Descripción | Por defecto |
|---|---|---|
| `--package-manager` | Gestor de paquetes a usar (pip, uv, pdm, poetry) | uv |
| `--help` | Muestra la ayuda del comando | - |

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
| `fastapi-async-crud` | API de gestión de items async | async/await, rendimiento |
| `fastapi-custom-response` | Sistema de respuesta personalizada | Respuestas a medida, paginación |
| `fastapi-dockerized` | API FastAPI dockerizada | Docker, listo para producción |
| `fastapi-psql-orm` | API FastAPI con PostgreSQL | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-empty` | Proyecto FastAPI mínimo | Configuración mínima |

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
- El proyecto debe tener `src/main.py` con la app FastAPI
- El entorno virtual debe estar activado

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

## Variables de entorno

FastAPI-fastkit respeta estas variables de entorno:

| Variable | Descripción | Por defecto |
|---|---|---|
| `FASTKIT_CONFIG_DIR` | Directorio de configuración | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Directorio de plantillas personalizadas | Plantillas integradas |
| `FASTKIT_LOG_LEVEL` | Nivel de log | `INFO` |

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

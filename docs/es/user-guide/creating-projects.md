# Crear proyectos

Guía detallada para crear distintos tipos de proyectos FastAPI con FastAPI-fastkit.

## Creación básica de proyectos

### 1. Crear un proyecto en modo interactivo

La forma más básica de crear un proyecto de manera interactiva:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Awesome FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-api          │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ Awesome FastAPI project │
└──────────────┴─────────────────────────┘
```

</div>

### 2. Selección del stack

Elige el stack de dependencias que quieres incluir en tu proyecto:

#### Stack MINIMAL (por defecto)

El proyecto FastAPI más básico:

- `fastapi` - Framework FastAPI
- `uvicorn` - Servidor ASGI
- `pydantic` - Validación de datos
- `pydantic-settings` - Gestión de configuración

**Ideal para:**

- Aprender FastAPI
- APIs simples
- Prototipos
- Microservicios

#### Stack STANDARD

Incluye soporte para base de datos y pruebas:

- Todas las dependencias de MINIMAL
- `sqlalchemy` - ORM para operaciones de base de datos
- `alembic` - Migraciones de base de datos
- `pytest` - Framework de pruebas

**Ideal para:**

- La mayoría de aplicaciones web
- APIs con almacenamiento en base de datos
- Aplicaciones listas para producción
- Proyectos en equipo

#### Stack FULL

Entorno de desarrollo completo:

- Todas las dependencias de STANDARD
- `redis` - Caché y almacenamiento de sesiones
- `celery` - Procesamiento de tareas en segundo plano

**Ideal para:**

- Aplicaciones grandes
- Requisitos de alto rendimiento
- Lógica de negocio compleja
- Aplicaciones empresariales

## Opciones avanzadas del proyecto

### Configuración personalizada del proyecto

Puedes personalizar tu proyecto durante la creación:

<div class="termy">

```console
$ fastkit init
Enter the project name: advanced-api
Enter the author name: Development Team
Enter the author email: dev@company.com
Enter the project description: Advanced FastAPI application with custom features

# Elige el stack STANDARD para soporte de base de datos
Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Explicación de la estructura del proyecto

Cuando creas un proyecto, FastAPI-fastkit genera esta estructura:

```
my-awesome-api/
├── .venv/                      # Entorno virtual
├── src/                        # Código fuente
│   ├── __init__.py
│   ├── main.py                # Punto de entrada de la app
│   ├── core/                  # Configuración central
│   │   ├── __init__.py
│   │   └── config.py         # Ajustes y configuración
│   ├── api/                   # Capa de API
│   │   ├── __init__.py
│   │   ├── api.py            # Router principal de la API
│   │   └── routes/           # Módulos individuales de rutas
│   │       ├── __init__.py
│   │       └── items.py      # Endpoints de ejemplo de items
│   ├── crud/                  # Operaciones de base de datos
│   │   ├── __init__.py
│   │   └── items.py          # Operaciones CRUD para items
│   ├── schemas/               # Modelos Pydantic
│   │   ├── __init__.py
│   │   └── items.py          # Esquemas de validación de datos
│   └── mocks/                 # Datos de prueba
│       ├── __init__.py
│       └── mock_items.json   # Datos de ejemplo para desarrollo
├── tests/                     # Suite de pruebas
│   ├── __init__.py
│   ├── conftest.py           # Configuración de pruebas
│   └── test_items.py         # Pruebas de ejemplo
├── scripts/                   # Scripts de utilidades
│   ├── test.sh               # Ejecutar pruebas
│   ├── coverage.sh           # Cobertura de pruebas
│   └── lint.sh               # Linting de código
├── requirements.txt           # Dependencias Python
├── setup.py                  # Configuración del paquete
└── README.md                 # Documentación del proyecto
```

### 3. Selección del gestor de paquetes

FastAPI-fastkit soporta varios gestores de paquetes Python. Elige el que mejor encaje con tu flujo de desarrollo:

#### Gestores disponibles

<div class="termy">

```console
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

Cada gestor tiene sus ventajas:

#### UV (Por defecto — recomendado)

**Gestor de paquetes rápido basado en Rust**

- ⚡ **Ultra rápido**: 10-100x más rápido que pip
- 🔧 **Sin complicaciones**: Compatible con los flujos habituales de pip
- 📦 **Moderno**: Soporte completo de PEP 621
- 🛠️ **Fiable**: Resolución determinista

**Archivos generados:**

- `pyproject.toml` (formato PEP 621)
- `uv.lock` (archivo de lock)

**Uso tras la creación:**
```console
cd my-project
uv sync              # Instalar dependencias
uv add requests      # Añadir nueva dependencia
uv run pytest       # Ejecutar pruebas
```

#### PDM

**Gestión moderna de dependencias Python**

- 🚀 **Moderno**: Soporte para PEP 582 y PEP 621
- 🧠 **Inteligente**: Resolución avanzada de dependencias
- 💼 **Profesional**: Workspaces y soporte multi-proyecto
- 📊 **Analíticas**: Herramientas de análisis de dependencias

**Archivos generados:**

- `pyproject.toml` (formato PEP 621)
- `pdm.lock` (archivo de lock)

**Uso tras la creación:**
```console
cd my-project
pdm install          # Instalar dependencias
pdm add requests     # Añadir nueva dependencia
pdm run pytest      # Ejecutar pruebas
```

#### Poetry

**Gestión de dependencias y empaquetado maduros**

- ✅ **Consolidado**: Maduro y muy adoptado
- 📦 **Integrado**: Soporte de build y publicación
- 🔒 **Reproducible**: poetry.lock para versiones exactas
- 🏗️ **Completo**: Ciclo de vida del proyecto completo

**Archivos generados:**

- `pyproject.toml` (formato Poetry)
- `poetry.lock` (archivo de lock)

**Uso tras la creación:**
```console
cd my-project
poetry install       # Instalar dependencias
poetry add requests  # Añadir nueva dependencia
poetry run pytest   # Ejecutar pruebas
```

#### PIP

**Gestor estándar de paquetes Python**

- 🏠 **Incluido**: Viene con Python
- 🌍 **Universal**: Funciona en todas partes
- 📚 **Familiar**: La mayoría de desarrolladores lo conoce
- 🔧 **Simple**: Flujo de trabajo directo

**Archivos generados:**

- `requirements.txt`

**Uso tras la creación:**
```console
cd my-project
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install requests
pytest
```

#### Especificar el gestor de paquetes

Puedes especificar tu gestor preferido:

**Selección interactiva (por defecto):**
```console
$ fastkit init
# ... pide la selección de gestor de paquetes
```

**Opción de línea de comandos:**
```console
$ fastkit init --package-manager poetry
$ fastkit init --package-manager pdm
$ fastkit init --package-manager uv
$ fastkit init --package-manager pip
```

### Entender cada directorio

#### Directorio `src/`

Contiene todo el código fuente de tu aplicación siguiendo el patrón **src layout**, buena práctica de empaquetado en Python.

#### Módulo `core/`

- **config.py**: Ajustes de la app, variables de entorno y configuración
- Centraliza toda la gestión de configuración
- Soporta archivos `.env` para ajustes por entorno

#### Módulo `api/`

- **api.py**: Router principal que incluye todos los sub-routers
- **routes/**: Módulos individuales de rutas para distintos recursos
- Separación clara de responsabilidades para distintos endpoints

#### Módulo `crud/`

- Operaciones de base de datos y lógica de negocio
- Operaciones **C**reate, **R**ead, **U**pdate, **D**elete
- Capa de abstracción entre las rutas de la API y el almacenamiento

#### Módulo `schemas/`

- Modelos Pydantic para validación de datos
- Esquemas de petición / respuesta
- Definiciones de tipos y modelos de datos

#### Directorio `tests/`

- Suite completa de pruebas para tu aplicación
- Incluye pruebas unitarias y de integración
- Preconfigurado con pytest

## Comparación de stacks

| Característica | MINIMAL | STANDARD | FULL |
|---|---|---|---|
| FastAPI y Uvicorn | ✅ | ✅ | ✅ |
| Validación de datos | ✅ | ✅ | ✅ |
| Soporte de base de datos | ❌ | ✅ | ✅ |
| Migraciones | ❌ | ✅ | ✅ |
| Framework de pruebas | ❌ | ✅ | ✅ |
| Caché (Redis) | ❌ | ❌ | ✅ |
| Tareas en segundo plano | ❌ | ❌ | ✅ |
| **Ideal para** | Aprendizaje, APIs simples | La mayoría de aplicaciones | Empresarial, apps complejas |

## Ejemplos de creación de proyectos

### Ejemplo 1: Proyecto de aprendizaje

<div class="termy">

```console
$ fastkit init
Enter the project name: fastapi-learning
Enter the author name: Student
Enter the author email: student@example.com
Enter the project description: Learning FastAPI basics

Select stack (minimal, standard, full): minimal
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Ejemplo 2: API de e-commerce

<div class="termy">

```console
$ fastkit init
Enter the project name: ecommerce-api
Enter the author name: E-commerce Team
Enter the author email: team@ecommerce.com
Enter the project description: E-commerce platform API

Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Ejemplo 3: Aplicación de alto rendimiento

<div class="termy">

```console
$ fastkit init
Enter the project name: enterprise-api
Enter the author name: Enterprise Team
Enter the author email: enterprise@company.com
Enter the project description: High-performance enterprise API

Select stack (minimal, standard, full): full
Do you want to proceed with project creation? [y/N]: y
```

</div>

## Después de crear el proyecto

### 1. Activar el entorno virtual

<div class="termy">

```console
$ cd my-awesome-api
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

### 2. Verificar la instalación

<div class="termy">

```console
$ pip list
Package         Version
fastapi         0.104.1
uvicorn         0.24.0
pydantic        2.5.0
...
```

</div>

### 3. Empezar a desarrollar

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

## Gestión de configuración

### Variables de entorno

Tu proyecto soporta configuración por entorno mediante archivos `.env`:

Crea un archivo `.env` en la raíz del proyecto:

```env
# .env
APP_NAME=My Awesome API
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### Configuración desde el código

El archivo generado `src/core/config.py` carga estas variables automáticamente:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Opciones de personalización

### Añadir dependencias personalizadas

Tras crear el proyecto, puedes añadir más dependencias:

<div class="termy">

```console
$ pip install requests httpx pyjwt
$ pip freeze > requirements.txt
```

</div>

### Modificar la estructura del proyecto

Aunque la estructura generada sigue buenas prácticas, puedes modificarla:

- Añade módulos nuevos en `src/`
- Crea archivos de rutas adicionales en `api/routes/`
- Amplía las operaciones CRUD en `crud/`
- Añade más esquemas en `schemas/`

## Buenas prácticas

### 1. Entorno virtual

Usa siempre entornos virtuales para aislar las dependencias del proyecto:

```bash
# Crear proyecto con entorno virtual
$ fastkit init  # Crea automáticamente .venv/

# Activarlo al trabajar
$ source .venv/bin/activate
```

### 2. Control de versiones

Inicializa el repositorio git tras crear el proyecto:

<div class="termy">

```console
$ cd my-awesome-api
$ git init
$ git add .
$ git commit -m "Initial commit - FastAPI project setup"
```

</div>

### 3. Configuración por entorno

- Usa archivos `.env` para desarrollo local
- Usa variables de entorno para producción
- No comitees nunca datos sensibles al control de versiones

### 4. Pruebas

Aprovecha el framework de pruebas incluido:

<div class="termy">

```console
$ python -m pytest
$ bash scripts/test.sh
```

</div>

## Próximos pasos

Tras crear tu proyecto:

1. **[Añadir rutas](adding-routes.md)**: Aprende a añadir nuevos endpoints de API
2. **[Referencia de la CLI](cli-reference.md)**: Domina todos los comandos disponibles
3. **[Tutorial de tu primer proyecto](../tutorial/first-project.md)**: Construye una aplicación completa

!!! tip "Consejos para crear proyectos"
    - Elige el stack que se ajusta a los requisitos de tu proyecto
    - Empieza con MINIMAL para aprender, usa STANDARD para la mayoría de proyectos
    - La estructura del proyecto está pensada para escalar y mantenerse
    - Todo el código generado sigue las buenas prácticas de FastAPI

# Usar plantillas

FastAPI-fastkit ofrece plantillas de proyecto ya preparadas para que puedas empezar rápido con distintas pilas tecnológicas.

## Plantillas disponibles

Consulta las plantillas disponibles con el comando `list-templates`:

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

## Descripción de las plantillas

### 1. `fastapi-default`

**Proyecto FastAPI simple**

- Configuración básica de FastAPI con lo esencial
- Gestión de items con datos mock
- Perfecto para aprender y APIs simples
- Incluye operaciones CRUD básicas

**Ideal para:**

- Principiantes en FastAPI
- APIs web simples
- Aprendizaje y prototipado

### 2. `fastapi-async-crud`

**Servidor API de gestión de items async**

- Aplicación FastAPI totalmente asíncrona
- Operaciones CRUD avanzadas con async/await
- Mejor rendimiento para operaciones de I/O
- Almacenamiento de datos mock con patrones async

**Ideal para:**

- Aplicaciones de alto rendimiento
- Operaciones intensivas de I/O
- Desarrollo Python async moderno

### 3. `fastapi-custom-response`

**API de gestión de items async con sistema de respuesta personalizada**

- Modelos y formato de respuesta personalizados
- Manejo avanzado de errores
- Soporte de paginación
- Códigos de estado HTTP y respuestas personalizadas

**Ideal para:**

- APIs que requieren formatos de respuesta específicos
- Necesidades avanzadas de manejo de errores
- Lógica de negocio personalizada en las respuestas

### 4. `fastapi-dockerized`

**API de gestión de items FastAPI dockerizada**

- Contenedorización Docker completa
- Configuración de despliegue lista para producción
- Builds Docker multi-stage
- Configuración basada en entorno

**Ideal para:**

- Despliegues a producción
- Entornos contenedorizados
- DevOps y pipelines de CI/CD

### 5. `fastapi-psql-orm`

**API de gestión de items FastAPI dockerizada con PostgreSQL**

- Integración con base de datos PostgreSQL
- ORM SQLAlchemy con migraciones Alembic
- Docker Compose para desarrollo local
- Operaciones CRUD completas sobre la base de datos

**Ideal para:**

- Aplicaciones basadas en base de datos
- Almacenamiento de datos a nivel producción
- Relaciones de datos complejas

### 6. `fastapi-empty`

**Proyecto FastAPI mínimo**

- Configuración mínima de FastAPI
- Sin funciones añadidas de antemano
- Lienzo en blanco para desarrollo personalizado

**Ideal para:**

- Empezar desde cero
- Dependencias mínimas
- Requisitos de arquitectura personalizada

## Crear un proyecto desde una plantilla

Usa el comando `startdemo` para crear un proyecto a partir de una plantilla:

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

✨ FastAPI project 'my-blog-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## Comparación de funcionalidades de las plantillas

| Funcionalidad | Default | Async CRUD | Custom Response | Dockerized | PostgreSQL ORM | Empty |
|---|---|---|---|---|---|---|
| **FastAPI básico** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Datos mock** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Soporte async** | Básico | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Respuestas personalizadas** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Base de datos** | Mock | Mock | Mock | Mock | PostgreSQL | Ninguna |
| **ORM** | ❌ | ❌ | ❌ | ❌ | SQLAlchemy | ❌ |
| **Migraciones** | ❌ | ❌ | ❌ | ❌ | Alembic | ❌ |
| **Pruebas** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Ideal para** | Aprendizaje | Rendimiento | APIs personalizadas | Producción | Apps con BD | Personalizado |

## Configuración específica por plantilla

### Usar `fastapi-psql-orm`

Esta plantilla incluye una configuración completa de PostgreSQL. Tras crearla:

1. **Arrancar PostgreSQL con Docker:**

<div class="termy">

```console
$ cd my-blog-api
$ docker-compose up -d postgres
Starting my-blog-api_postgres_1 ... done
```

</div>

2. **Ejecutar las migraciones:**

<div class="termy">

```console
$ source .venv/bin/activate
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> bedcdc35b64a, first alembic
```

</div>

3. **Arrancar el servidor de la API:**

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Usar `fastapi-dockerized`

Esta plantilla ofrece soporte completo de Docker:

1. **Construir la imagen de Docker:**

<div class="termy">

```console
$ cd my-dockerized-api
$ docker build -t my-dockerized-api .
Successfully built abc123def456
Successfully tagged my-dockerized-api:latest
```

</div>

2. **Ejecutar el contenedor:**

<div class="termy">

```console
$ docker run -p 8000:8000 my-dockerized-api
INFO:     Uvicorn running on http://0.0.0.0:8000
```

</div>

### Usar `fastapi-custom-response`

Esta plantilla incluye un manejo avanzado de respuestas:

1. **Modelos de respuesta personalizados:**

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

2. **Manejo mejorado de errores:**

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

## Estructura de proyecto de las plantillas

Cada plantilla sigue una estructura consistente pero personalizada:

### Estructura de `fastapi-default`
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

### Estructura de `fastapi-psql-orm`
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

## Personalizar las plantillas

Tras crear un proyecto desde una plantilla, puedes personalizarlo:

### 1. Añadir rutas nuevas

<div class="termy">

```console
$ fastkit addroute posts my-blog-api
$ fastkit addroute users my-blog-api
$ fastkit addroute comments my-blog-api
```

</div>

### 2. Modificar la configuración

Edita `src/core/config.py` según tus necesidades:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Configuración de base de datos (para plantillas PostgreSQL)
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # Configuración de seguridad
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Añadir variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# .env
PROJECT_NAME=My Blog API
VERSION=1.0.0
DEBUG=True

# Base de datos (para plantillas PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/myblogdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=myblogdb

# Seguridad
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Probar las plantillas

Cada plantilla viene con pruebas preconfiguradas:

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

## Flujo de trabajo con plantillas

### 1. Elegir la plantilla adecuada

- **Aprendizaje / APIs simples**: `fastapi-default`
- **Alto rendimiento**: `fastapi-async-crud`
- **Formatos de respuesta personalizados**: `fastapi-custom-response`
- **Despliegue a producción**: `fastapi-dockerized`
- **Aplicaciones con base de datos**: `fastapi-psql-orm`
- **Arquitectura personalizada**: `fastapi-empty`

### 2. Crear y preparar

<div class="termy">

```console
$ fastkit startdemo
# Sigue los prompts
$ cd your-project
$ source .venv/bin/activate
```

</div>

### 3. Desarrollo

<div class="termy">

```console
# Arrancar el servidor de desarrollo
$ fastkit runserver

# Ejecutar pruebas
$ python -m pytest

# Añadir nuevas funcionalidades
$ fastkit addroute new-resource your-project
```

</div>

### 4. Despliegue

Para plantillas de producción (`fastapi-dockerized`, `fastapi-psql-orm`):

<div class="termy">

```console
# Build para producción
$ docker build -t your-app .

# Desplegar con Docker Compose
$ docker-compose up -d
```

</div>

## Buenas prácticas

### 1. Elegir plantillas con cabeza

- Empieza con plantillas más simples para aprender
- Usa plantillas con base de datos para apps basadas en datos
- Usa plantillas con Docker para despliegues a producción

### 2. Gestión del entorno

- Usa siempre archivos `.env` para la configuración
- Nunca comitees datos sensibles al control de versiones
- Usa entornos distintos para desarrollo / producción

### 3. Estrategia de personalización

- Añade rutas nuevas con `fastkit addroute`
- Modifica el código existente para adaptarlo a tu lógica de negocio
- Mantén la estructura del proyecto ordenada

### 4. Pruebas

- Ejecuta las pruebas regularmente durante el desarrollo
- Añade pruebas para cada funcionalidad nueva
- Usa la estructura de pruebas incluida como guía

## Solución de problemas

### Problemas de conexión a base de datos (plantillas PostgreSQL)

Si no puedes conectarte a PostgreSQL:

1. **Comprueba que Docker está corriendo:**

   <div class="termy">
   ```console
   $ docker ps
   ```
   </div>

2. **Verifica el contenedor PostgreSQL:**

   <div class="termy">
   ```console
   $ docker-compose logs postgres
   ```
   </div>

3. **Revisa las variables de entorno:**

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Fallos al construir la imagen Docker

Si falla el build de Docker:

1. **Comprueba la sintaxis del Dockerfile**
2. **Verifica que todos los archivos están presentes**
3. **Comprueba que el daemon de Docker está corriendo**

### Dependencias faltantes

Si recibes errores de import:

1. **Activa el entorno virtual:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

2. **Instala las dependencias:**
   <div class="termy">
   ```console
   $ pip install -r requirements.txt
   ```
   </div>

## Próximos pasos

Ahora que entiendes las plantillas:

1. **[Tu primer proyecto](../tutorial/first-project.md)**: Construye una aplicación completa
2. **[Añadir rutas](adding-routes.md)**: Amplía tu proyecto basado en plantilla
3. **[Referencia de la CLI](cli-reference.md)**: Domina todos los comandos disponibles

!!! tip "Consejos sobre plantillas"
    - Las plantillas son excelentes puntos de partida, no soluciones finales
    - Personaliza las plantillas según tus requisitos específicos
    - Lee el código de las plantillas para aprender buenas prácticas de FastAPI
    - Usa el control de versiones para rastrear tus personalizaciones

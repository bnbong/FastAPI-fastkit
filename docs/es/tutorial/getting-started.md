# Primeros pasos

Tutorial completo paso a paso para empezar con FastAPI-fastkit. Esta guía te lleva desde la instalación hasta tener tu primera API en marcha en unos 15 minutos.

## Requisitos previos

Antes de empezar, asegúrate de tener:

- **Python 3.12 o superior** instalado en el sistema
- **Conocimientos básicos de Python** (variables, funciones, clases)
- Acceso a una **terminal / línea de comandos**
- **Editor de texto o IDE** (VS Code, PyCharm, etc.)

## Paso 1: Instalación

Primero instalemos FastAPI-fastkit. Recomendamos usar un entorno virtual para aislar tus proyectos.

### Opción A: Con pip (tradicional)

<div class="termy">

```console
$ pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### Opción B: Con UV (recomendado - más rápido)

UV es un gestor de paquetes Python rápido. Si todavía no tienes UV instalado:

<div class="termy">

```console
# Primero instala UV
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# Luego instala FastAPI-fastkit
$ uv pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### Opción C: Con un entorno virtual

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # En Windows: fastapi-env\Scripts\activate
$ pip install fastapi-fastkit
```

</div>

### Verificar la instalación

Comprueba que FastAPI-fastkit se ha instalado correctamente:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

## Paso 2: Crear tu primer proyecto

Ahora vamos a crear tu primer proyecto FastAPI con el comando interactivo `init`:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-api
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-first-api            │
│ Author       │ Your Name               │
│ Author Email │ your.email@example.com  │
│ Description  │ My first FastAPI project│
└──────────────┴─────────────────────────┘

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

Creating virtual environment...
Installing dependencies...
✨ FastAPI project 'my-first-api' has been created successfully!
```

</div>

!!! note "Selección del stack"
    Hemos elegido **MINIMAL** para este tutorial por simplicidad. Para proyectos reales, considera **STANDARD** (incluye soporte de base de datos) o **FULL** (incluye tareas en segundo plano).

## Paso 3: Entrar en tu proyecto

Entra en el directorio del proyecto recién creado:

<div class="termy">

```console
$ cd my-first-api
$ ls -la
total 32
drwxr-xr-x  8 user user  256 Dec  7 10:30 .
drwxr-xr-x  3 user user   96 Dec  7 10:30 ..
drwxr-xr-x  5 user user  160 Dec  7 10:30 .venv
-rw-r--r--  1 user user  156 Dec  7 10:30 README.md
-rw-r--r--  1 user user  243 Dec  7 10:30 requirements.txt
drwxr-xr-x  3 user user   96 Dec  7 10:30 scripts
-rw-r--r--  1 user user 1245 Dec  7 10:30 setup.py
drwxr-xr-x  8 user user  256 Dec  7 10:30 src
drwxr-xr-x  3 user user   96 Dec  7 10:30 tests
```

</div>

## Paso 4: Activar el entorno virtual

El proyecto incluye un entorno virtual preconfigurado. Vamos a activarlo:

<div class="termy">

```console
$ source .venv/bin/activate  # En Windows: .venv\Scripts\activate
(my-first-api) $
```

</div>

Fíjate en cómo el prompt del terminal ahora muestra `(my-first-api)`, indicando que el entorno virtual está activo.

## Paso 5: Iniciar el servidor de desarrollo

Llega la parte emocionante — vamos a arrancar tu servidor FastAPI:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720] using StatReload
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

🎉 **¡Enhorabuena!** Tu servidor FastAPI ya está en marcha.

## Paso 6: Probar tu API

Vamos a probar tu API de varias formas:

### Método 1: Navegador

Abre tu navegador web y visita:

- **Endpoint principal de la API**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Deberías ver:
```json
{"message": "Hello World"}
```

### Método 2: Documentación interactiva de la API

Entra en la documentación generada automáticamente:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Swagger UI es especialmente útil — te permite:

- Ver todos los endpoints disponibles
- Probar endpoints directamente desde el navegador
- Consultar esquemas de petición / respuesta
- Descargar la especificación OpenAPI

### Método 3: Línea de comandos

Abre una terminal nueva (deja el servidor en marcha) y prueba con curl:

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Hello World"}

$ curl http://127.0.0.1:8000/api/v1/items/
[]

$ curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Item", "description": "This is a test item"}'
{
  "id": 1,
  "title": "My First Item",
  "description": "This is a test item"
}
```

</div>

## Paso 7: Entender la estructura del proyecto

Vamos a explorar lo que FastAPI-fastkit ha generado para ti:

<div class="termy">

```console
$ tree src
src/
├── __init__.py
├── main.py                 # Punto de entrada de la app FastAPI
├── core/
│   ├── __init__.py
│   └── config.py          # Configuración de la aplicación
├── api/
│   ├── __init__.py
│   ├── api.py             # Router principal de la API
│   └── routes/
│       ├── __init__.py
│       └── items.py       # Endpoints de la API de items
├── crud/
│   ├── __init__.py
│   └── items.py           # Lógica de negocio para items
├── schemas/
│   ├── __init__.py
│   └── items.py           # Esquemas de validación de datos
└── mocks/
    ├── __init__.py
    └── mock_items.json    # Datos de ejemplo
```

</div>

### Archivos clave

**`src/main.py`** — El corazón de tu aplicación:
```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**`src/core/config.py`** — Ajustes de la aplicación:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "my-first-api"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

**`src/api/routes/items.py`** — Endpoints de la API:
```python
from typing import List
from fastapi import APIRouter, HTTPException
from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import items_crud

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items():
    """Get all items"""
    return items_crud.get_all()

@router.post("/", response_model=Item)
def create_item(item: ItemCreate):
    """Create a new item"""
    return items_crud.create(item)
```

## Paso 8: Añadir tu primera ruta personalizada

Añadamos una nueva ruta de API para practicar lo que has aprendido:

<div class="termy">

```console
$ fastkit addroute users my-first-api
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-api                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-first-api'
```

</div>

El servidor se reinicia automáticamente y ahora tienes nuevos endpoints:

- `GET /api/v1/users/` - Obtener todos los usuarios
- `POST /api/v1/users/` - Crear un usuario nuevo
- `GET /api/v1/users/{user_id}` - Obtener un usuario concreto
- Y más...

### Probar la nueva ruta

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

$ curl http://127.0.0.1:8000/api/v1/users/
[
  {
    "id": 1,
    "title": "John Doe",
    "description": "Software Developer"
  }
]
```

</div>

## Paso 9: Explorar y modificar el código

Ahora hagamos una pequeña modificación para entender cómo funciona el código.

### Cambiar el mensaje de bienvenida

Abre `src/main.py` en tu editor y cambia el endpoint raíz:

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!"}
```

Guarda el archivo. Gracias a la recarga automática, tu servidor se reinicia solo.

### Probar el cambio

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Welcome to my first FastAPI application!"}
```

</div>

### Añadir un endpoint nuevo

Añadamos un endpoint simple en `src/main.py`:

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### Probar el nuevo endpoint

<div class="termy">

```console
$ curl http://127.0.0.1:8000/hello/World
{"message":"Hello, World!"}

$ curl http://127.0.0.1:8000/hello/FastAPI
{"message":"Hello, FastAPI!"}
```

</div>

## Paso 10: Ejecutar las pruebas

El proyecto trae pruebas preconfiguradas. Vamos a ejecutarlas:

<div class="termy">

```console
$ python -m pytest
======================== test session starts ========================
collected 5 items

tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED

======================== 5 passed in 0.45s ========================
```

</div>

## Conceptos centrales

### 1. Estructura de la aplicación FastAPI

FastAPI-fastkit sigue una **arquitectura modular**:

- **`main.py`**: Punto de entrada de la aplicación y endpoints globales
- **`api/`**: Organización de rutas de la API
- **`core/`**: Configuración y ajustes de la aplicación
- **`crud/`**: Lógica de negocio y operaciones sobre datos
- **`schemas/`**: Validación y serialización de datos
- **`tests/`**: Pruebas automatizadas

### 2. Gestión de dependencias

Tu proyecto usa gestión moderna de dependencias Python:

- **Entorno virtual**: entorno Python aislado
- **requirements.txt**: lista todas las dependencias
- **Instalación automática**: las dependencias se instalan al crear el proyecto

### 3. Servidor de desarrollo

FastAPI-fastkit usa **Uvicorn** como servidor ASGI:

- **Recarga automática**: se reinicia solo cuando el código cambia
- **Arranque rápido**: iteración de desarrollo ágil
- **Listo para producción**: el mismo servidor se usa en producción

### 4. Documentación de la API

FastAPI genera automáticamente:

- **Especificación OpenAPI**: documentación de API estándar de la industria
- **Swagger UI**: interfaz interactiva para pruebas
- **ReDoc**: visualización alternativa de la documentación

## Próximos pasos

¡Enhorabuena! Has conseguido:

✅ Instalar FastAPI-fastkit
✅ Crear tu primer proyecto
✅ Arrancar el servidor de desarrollo
✅ Probar tus endpoints de API
✅ Añadir una ruta nueva
✅ Modificar código existente
✅ Ejecutar pruebas

### Seguir aprendiendo

1. **[Tu primer proyecto](first-project.md)**: Construye una API de blog completa con funcionalidades avanzadas
2. **[Añadir rutas](../user-guide/adding-routes.md)**: Aprende a crear endpoints más complejos
3. **[Usar plantillas](../user-guide/using-templates.md)**: Explora plantillas de proyecto ya preparadas

### Experimenta más

Prueba estos retos:

1. **Añadir validación**: Modifica los esquemas para añadir reglas de validación de datos
2. **Respuestas personalizadas**: Cambia los formatos de respuesta en las rutas
3. **Variables de entorno**: Usa archivos `.env` para la configuración
4. **Añadir middleware**: Implementa CORS o autenticación
5. **Integración con base de datos**: Actualiza al stack STANDARD para soporte de base de datos

### Problemas comunes y soluciones

**El servidor no arranca:**

- Comprueba que estás en el directorio del proyecto
- Asegúrate de que el entorno virtual está activado
- Verifica que no hay errores de sintaxis en tu código

**Errores de import:**

- Asegúrate de que existen todos los archivos `__init__.py`
- Comprueba que tus rutas de import son correctas
- Verifica que estás usando el entorno virtual

**Puerto ya en uso:**
```console
$ fastkit runserver --port 8080
```

## Buenas prácticas que has aprendido

1. **Entornos virtuales**: Usa siempre entornos aislados
2. **Estructura del proyecto**: Sigue una arquitectura modular y organizada
3. **Recarga automática**: Usa el servidor de desarrollo para iterar rápido
4. **Documentación de API**: Aprovecha la generación automática de documentación
5. **Pruebas**: Ejecuta las pruebas regularmente durante el desarrollo

!!! tip "Consejos de desarrollo"
    - Mantén el servidor de desarrollo en marcha mientras programas
    - Usa la documentación interactiva (`/docs`) para probar tus APIs
    - Revisa el terminal en busca de mensajes de error útiles
    - Haz commits frecuentes al control de versiones

¡Ya estás listo para construir APIs increíbles con FastAPI-fastkit! 🚀

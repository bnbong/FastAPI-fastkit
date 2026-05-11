# Preguntas frecuentes

Preguntas y respuestas habituales sobre FastAPI-fastkit.

## Instalación y configuración

### P: ¿Qué versiones de Python están soportadas?

**R:** FastAPI-fastkit requiere **Python 3.12 o superior**. Recomendamos usar la última versión estable de Python para tener la mejor experiencia.

<div class="termy">

```console
$ python --version
Python 3.12.1

$ pip install fastapi-fastkit
```

</div>

### P: ¿Cómo instalo FastAPI-fastkit?

**R:** Puedes instalar FastAPI-fastkit con pip:

<div class="termy">

```console
# Última versión estable
$ pip install fastapi-fastkit

# Versión de desarrollo desde GitHub
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git

# Una versión concreta
$ pip install fastapi-fastkit==1.0.0
```

</div>

### P: La instalación falla con errores de permisos

**R:** Prueba a instalar en un entorno virtual o con permisos de usuario:

<div class="termy">

```console
# Crear el entorno virtual
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # En Windows: fastapi-env\Scripts\activate

# Instalar dentro del entorno virtual
$ pip install fastapi-fastkit

# O instalar solo para el usuario actual
$ pip install --user fastapi-fastkit
```

</div>

### P: El comando `fastkit` no aparece tras la instalación

**R:** Suele significar que el directorio de instalación no está en tu PATH:

<div class="termy">

```console
# Comprobar que está instalado
$ pip show fastapi-fastkit

# Buscar la ruta de instalación
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__file__)"

# Probar a ejecutarlo directamente
$ python -m fastapi_fastkit --version

# O añadirlo al PATH (Linux/macOS)
$ export PATH="$HOME/.local/bin:$PATH"
```

</div>

## Creación de proyectos

### P: ¿Qué stacks de dependencias están disponibles?

**R:** FastAPI-fastkit ofrece tres stacks:

- **MINIMAL**: FastAPI, Uvicorn, Pydantic, Pydantic-Settings (API web básica)
- **STANDARD**: añade SQLAlchemy, Alembic, pytest (soporte de base de datos)
- **FULL**: añade Redis, Celery (tareas en segundo plano)

!!! tip "Gestor de paquetes por defecto"
    El gestor de paquetes por defecto es `uv` para instalar dependencias más rápido. También puedes elegir `pip`, `pdm` o `poetry`.

<div class="termy">

```console
$ fastkit init
# Elige tu stack preferido durante la creación del proyecto
```

</div>

### P: ¿Puedo personalizar la plantilla del proyecto?

**R:** ¡Sí! Tienes varias opciones:

1. **Usar las plantillas existentes** con `fastkit startdemo`
2. **Crear plantillas personalizadas** copiando y modificando las existentes
3. **Añadir rutas de forma incremental** con `fastkit addroute`

<div class="termy">

```console
# Usar plantillas ya preparadas
$ fastkit list-templates
$ fastkit startdemo

# Añadir rutas a un proyecto existente
$ fastkit addroute users .          # Añade la ruta 'users' al directorio actual
$ fastkit addroute users my-project # Añade la ruta 'users' a 'my-project'
```

</div>

### P: ¿Cómo creo un proyecto con un formato concreto de nombre?

**R:** El nombre del proyecto debe ser un identificador Python válido:

- ✅ `my-api`, `blog_system`, `UserService`
- ❌ `my api`, `123project`, `project-name!`

<div class="termy">

```console
$ fastkit init
Enter the project name: my_awesome_api  # Válido
Enter the project name: my-awesome-api  # Válido (los guiones se convierten en guiones bajos)
```

</div>

### P: La creación del proyecto falla con "directory already exists"

**R:** El directorio del proyecto ya existe. Tienes varias opciones:

1. **Elige otro nombre**
2. **Elimina el directorio existente** (si es seguro hacerlo)
3. **Crea el proyecto en otra ubicación**

<div class="termy">

```console
# Comprobar si el directorio existe
$ ls my-project

# Eliminar si es seguro (¡PRECAUCIÓN!)
$ rm -rf my-project

# O crear en otra ubicación
$ mkdir projects
$ cd projects
$ fastkit init
```

</div>

### P: ¿Cómo uso el modo interactivo para configurar el proyecto?

**R:** Usa `fastkit init --interactive` para una configuración paso a paso guiada con selección inteligente de funcionalidades:

<div class="termy">

```console
$ fastkit init --interactive
```

</div>

El modo interactivo te lleva por estos pasos en orden:

1. **Información del proyecto** — nombre, autor, email, descripción.
2. **Preset de arquitectura** — elige la estructura del proyecto. La opción recomendada es `domain-starter`; pulsa Enter para aceptarla. Consulta la [matriz de presets / funcionalidades](preset-feature-matrix.md) para ver la estructura exacta que produce cada preset y qué combinaciones requieren cableado manual.
3. **Selección de funcionalidades** — base de datos, autenticación, tareas en segundo plano, caché, monitorización, pruebas, utilidades, despliegue.
4. **Gestor de paquetes y paquetes personalizados** — pip / uv / pdm / poetry, además de cualquier extra que quieras fijar.
5. **Confirmación** — una tabla resumen muestra todas las elecciones (incluido el preset de arquitectura) antes de crear el proyecto.

El modo interactivo te permite seleccionar de un catálogo de funcionalidades completo:

| Categoría | Opciones disponibles |
|---|---|
| **Arquitectura** | minimal, single-module, classic-layered, **domain-starter** (opción recomendada por defecto) |
| **Base de datos** | PostgreSQL, MySQL, MongoDB, Redis, SQLite |
| **Autenticación** | JWT, OAuth2, FastAPI-Users, Basada en sesiones |
| **Tareas en segundo plano** | Celery, Dramatiq |
| **Pruebas** | Basic (pytest), Coverage, Advanced (con faker, factory-boy) |
| **Caché** | Redis con fastapi-cache2 |
| **Monitorización** | Loguru, OpenTelemetry, Prometheus |
| **Utilidades** | CORS, Rate-Limiting, Paginación, WebSocket |
| **Despliegue** | Docker, docker-compose con configs autogeneradas |

El modo interactivo genera automáticamente:

- `main.py` con las funcionalidades seleccionadas integradas
- Archivos de configuración de base de datos y autenticación cuando las opciones seleccionadas soportan generación de código (p. ej. PostgreSQL/MySQL/SQLite/MongoDB para base de datos, JWT/FastAPI-Users para autenticación); otras opciones solo instalan los paquetes necesarios
- Archivos de despliegue acordes con la opción de despliegue elegida (`Dockerfile` si seleccionas `Docker`, `docker-compose.yml` si seleccionas `docker-compose`)
- Configuración de pruebas según la opción de testing elegida (la configuración de coverage solo se incluye cuando seleccionas `Coverage` o `Advanced`)

### P: ¿Cómo veo las funcionalidades disponibles del modo interactivo?

**R:** Usa el comando `list-features` para mostrar todas las funcionalidades disponibles y sus paquetes:

<div class="termy">

```console
$ fastkit list-features
# Muestra todas las funcionalidades disponibles organizadas por categoría
# con sus paquetes asociados
```

</div>

Esto te ayuda a entender qué paquetes se instalarán para cada selección.

## Desarrollo de rutas

### P: ¿Cómo añado autenticación a mis rutas?

**R:** Crea una dependencia para la autenticación:

```python
# src/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # Verificar el token y devolver el usuario
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return get_user_from_token(token)

# src/api/routes/users.py
@router.get("/me")
def get_current_user_profile(user = Depends(get_current_user)):
    return user
```

### P: ¿Cómo añado modelos de base de datos a mi proyecto?

**R:** Para stacks STANDARD o FULL, crea modelos SQLAlchemy:

```python
# src/models/users.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### P: ¿Cómo añado validación a los datos de petición?

**R:** Usa modelos Pydantic en tus esquemas:

```python
# src/schemas/users.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### P: ¿Cómo manejo la subida de archivos?

**R:** Usa `UploadFile` de FastAPI:

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    # Guardar el archivo
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

## Plantillas

### P: ¿Qué plantillas hay disponibles?

**R:** FastAPI-fastkit incluye varias plantillas ya preparadas:

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-default         │ Simple FastAPI Project            │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-custom-response │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI API            │
│ fastapi-empty           │ Minimal FastAPI Project           │
│ fastapi-mcp             │ MCP (Model Context Protocol) API  │
│ fastapi-psql-orm        │ PostgreSQL FastAPI API            │
│ fastapi-single-module   │ Single-file FastAPI Project       │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

### P: ¿Cómo uso una plantilla concreta?

**R:** Usa el comando `startdemo`:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Select template: fastapi-psql-orm
```

</div>

### P: ¿Puedo crear mis propias plantillas?

**R:** ¡Sí! Crea una estructura de directorios y usa variables de plantilla:

```
my-template/
├── src/
│   └── main.py-tpl
├── requirements.txt-tpl
└── template.yaml
```

```python
# main.py-tpl
from fastapi import FastAPI

app = FastAPI(title="{{PROJECT_NAME}}")

@app.get("/")
def read_root():
    return {"message": "Hello from {{PROJECT_NAME}}!"}
```

### P: ¿Cómo modifico una plantilla existente?

**R:** Las plantillas están en el directorio `fastapi_project_template`. Puedes:

1. **Hacer fork del repositorio** y modificar las plantillas
2. **Crear una plantilla personalizada** basada en las existentes
3. **Sobrescribir archivos concretos** después de crear el proyecto

## Servidor de desarrollo

### P: ¿Cómo arranco el servidor de desarrollo?

**R:** Usa el comando `runserver` desde el directorio del proyecto:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate  # Activar el entorno virtual
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### P: El servidor no arranca — "Address already in use"

**R:** El puerto 8000 está ocupado. Usa otro puerto o mata el proceso existente:

<div class="termy">

```console
# Usar otro puerto
$ fastkit runserver --port 8080

# O buscar y matar el proceso existente
$ lsof -ti:8000 | xargs kill -9

# En Windows
$ netstat -ano | findstr :8000
$ taskkill /PID <PID> /F
```

</div>

### P: El auto-reload no funciona

**R:** Asegúrate de estar en el directorio del proyecto y de tener el entorno virtual activado:

<div class="termy">

```console
# Comprobar el directorio actual
$ pwd
/path/to/my-project

# Comprobar el entorno virtual
$ which python
/path/to/my-project/.venv/bin/python

# Arrancar con reload explícito
$ fastkit runserver --reload
```

</div>

### P: ¿Cómo configuro el servidor para producción?

**R:** No uses el servidor de desarrollo en producción. En su lugar:

```python
# Usar gunicorn u otro servidor WSGI
$ pip install gunicorn
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# O usar Docker con la plantilla fastapi-dockerized
$ fastkit startdemo  # Selecciona fastapi-dockerized
$ docker build -t my-app .
$ docker run -p 8000:8000 my-app
```

## Rendimiento y optimización

### P: ¿Cómo mejoro el rendimiento de la API?

**R:** Varias estrategias de optimización:

1. **Usa async/await** para operaciones de I/O
2. **Añade caché** para operaciones costosas
3. **Optimiza las consultas a la base de datos**
4. **Usa tareas en segundo plano** para procesamientos pesados

```python
# Endpoint asíncrono
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await users_service.get_user_async(user_id)
    return user

# Tarea en segundo plano
from fastapi import BackgroundTasks

@router.post("/send-email")
def send_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(send_notification_email, email)
    return {"message": "Email will be sent in background"}
```

### P: ¿Cómo añado caché?

**R:** Usa Redis para la caché:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Intentar obtener desde la caché
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Ejecutar la función y cachear el resultado
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)
async def get_expensive_data():
    # Operación costosa
    return complex_calculation()
```

### P: ¿Cómo manejo muchas peticiones concurrentes?

**R:** Usa una configuración de servidor adecuada:

<div class="termy">

```console
# Desarrollo
$ fastkit runserver --workers 1  # Un solo worker para desarrollo

# Producción
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
$ uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

</div>

## Pruebas

### P: ¿Cómo ejecuto las pruebas?

**R:** Usa pytest desde el directorio del proyecto:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate
$ python -m pytest

# Con cobertura
$ python -m pytest --cov=src

# Un archivo de pruebas concreto
$ python -m pytest tests/test_users.py

# Con salida detallada
$ python -m pytest -v
```

</div>

### P: ¿Cómo escribo pruebas de API?

**R:** Usa el cliente de pruebas de FastAPI:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user():
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
```

### P: ¿Cómo hago mock de dependencias externas?

**R:** Usa fixtures de pytest y mocks:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    with patch('src.database.get_db') as mock_db:
        mock_db.return_value = Mock()
        yield mock_db

def test_user_creation_with_mock_db(mock_database):
    # Probar con la base de datos mockeada
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
```

## Cómo contribuir

### P: ¿Cómo contribuyo a FastAPI-fastkit?

**R:** Sigue estos pasos:

1. **Haz fork del repositorio** en GitHub
2. **Configura el entorno de desarrollo**
3. **Crea una rama de funcionalidad**
4. **Haz tus cambios** con pruebas
5. **Envía un pull request**

<div class="termy">

```console
$ git clone https://github.com/yourusername/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make dev-setup  # Configurar el entorno de desarrollo
$ git checkout -b feature/my-feature
# Hacer cambios...
$ make dev-check  # Formatear, lintear y probar
$ git commit -m "feat: add new feature"
$ git push origin feature/my-feature
```

</div>

### P: ¿Qué debe incluir un pull request?

**R:** Todo pull request debe incluir:

- [ ] **Descripción clara** de los cambios
- [ ] **Pruebas** para las nuevas funcionalidades
- [ ] **Actualizaciones de documentación** si hace falta
- [ ] **Cumplir la guía de código**
- [ ] **Todas las verificaciones en verde**

### P: ¿Cómo reporto un bug?

**R:** Crea un issue en GitHub con:

1. **Descripción del bug** y comportamiento esperado
2. **Pasos para reproducirlo**
3. **Información del entorno** (SO, versión de Python, etc.)
4. **Mensajes de error** o logs
5. **Ejemplo mínimo** si es posible

### P: ¿Cómo solicito una nueva funcionalidad?

**R:** Abre un issue de petición de funcionalidad con:

1. **Descripción clara** de la funcionalidad
2. **Caso de uso** y motivación
3. **Implementación propuesta** (opcional)
4. **Ejemplos** de funcionalidades similares

## Solución de problemas

### P: Estoy recibiendo errores de import

**R:** Revisa tu Python path y tu entorno virtual:

<div class="termy">

```console
# Comprobar que el entorno virtual está activo
$ which python
/path/to/project/.venv/bin/python

# Comprobar el Python path
$ python -c "import sys; print(sys.path)"

# Reinstalar en modo editable (para desarrollo)
$ pip install -e .
```

</div>

### P: Problemas de conexión a la base de datos

**R:** En las plantillas con base de datos, asegúrate de que la base de datos está corriendo:

<div class="termy">

```console
# Plantilla PostgreSQL
$ docker-compose up -d postgres  # Arrancar la base de datos
$ alembic upgrade head            # Ejecutar las migraciones

# Comprobar la conexión
$ docker-compose logs postgres
```

</div>

### P: No se encuentran los archivos de plantilla

**R:** Suele indicar un problema con la ruta de las plantillas:

<div class="termy">

```console
# Comprobar las plantillas disponibles
$ fastkit list-templates

# Comprobar el directorio de las plantillas
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__path__)"

# Reinstalar si faltan plantillas
$ pip uninstall fastapi-fastkit
$ pip install fastapi-fastkit
```

</div>

### P: Los hooks de pre-commit fallan

**R:** Instala y ejecuta los hooks:

<div class="termy">

```console
$ pip install pre-commit
$ pre-commit install
$ pre-commit run --all-files

# Arreglar problemas de formato
$ black src/ tests/
$ isort src/ tests/
```

</div>

### P: Las pruebas fallan en CI pero pasan en local

**R:** Causas y soluciones habituales:

1. **Diferencias de entorno**: comprueba que las versiones de Python coinciden
2. **Dependencias faltantes**: asegúrate de instalar las dependencias de testing
3. **Problemas de rutas**: usa imports absolutos
4. **Problemas de timing**: añade esperas adecuadas en pruebas asíncronas

<div class="termy">

```console
# Probar con la misma versión de Python que CI
$ python3.12 -m pytest

# Comprobar si faltan dependencias
$ pip install -r requirements-dev.txt

# Ejecutar las pruebas en un entorno aislado
$ tox
```

</div>

## Pedir ayuda

### P: ¿Dónde puedo conseguir ayuda?

**R:** Varias opciones para conseguir ayuda:

- **GitHub Issues**: para bugs y peticiones de funcionalidad
- **GitHub Discussions**: para preguntas y soporte de la comunidad
- **Documentación**: guías y tutoriales
- **Ejemplos de código**: revisa las plantillas y las pruebas existentes

### P: ¿Cómo me mantengo al día?

**R:** Sigue las novedades del proyecto:

- Haz **Watch del repositorio** en GitHub
- Revisa los **releases** para ver las nuevas funcionalidades
- Lee el **changelog** para ver los cambios incompatibles
- Sigue las **buenas prácticas** de la documentación

!!! tip "Consejos pro"
    - Usa siempre entornos virtuales para tus proyectos Python
    - Mantén tu instalación de FastAPI-fastkit actualizada
    - Usa `fastkit --help` para ver los comandos disponibles
    - Consulta la documentación cuando te bloquees
    - No dudes en preguntar en GitHub Discussions

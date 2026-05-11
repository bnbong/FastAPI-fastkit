# Construir un servidor API básico

Aprende a crear rápidamente una API REST sencilla con FastAPI-fastkit. Este tutorial está pensado para quienes empiezan con FastAPI y cubre la creación de APIs CRUD básicas.

## Lo que aprenderás en este tutorial

- Crear un servidor API básico con el comando `fastkit startdemo`
- Entender la estructura de un proyecto FastAPI
- Usar endpoints CRUD básicos
- Probar y documentar la API
- Métodos para ampliar el proyecto

## Requisitos previos

- Python 3.12 o superior instalado
- FastAPI-fastkit instalado (`pip install fastapi-fastkit`)
- Conocimientos básicos de Python

## Paso 1: Crear un proyecto API básico

Vamos a crear una API básica usando la plantilla `fastapi-default`.

<div class="termy">

```console
$ fastkit startdemo fastapi-default
Enter the project name: my-first-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: My first FastAPI server
Deploying FastAPI project using 'fastapi-default' template

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-first-api               │
│ Author       │ Developer Kim              │
│ Author Email │ developer@example.com      │
│ Description  │ My first FastAPI server    │
└──────────────┴────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-first-api' from 'fastapi-default' has been created successfully!
```

</div>

## Paso 2: Entender la estructura del proyecto generado

Examinemos la estructura del proyecto generado:

```
my-first-api/
├── README.md                 # Documentación del proyecto
├── requirements.txt          # Lista de paquetes de dependencias
├── setup.py                  # Configuración del paquete
├── scripts/
│   └── run-server.sh        # Script de ejecución del servidor
├── src/                     # Código fuente principal
│   ├── main.py              # Punto de entrada de la app FastAPI
│   ├── core/
│   │   └── config.py        # Gestión de configuración
│   ├── api/
│   │   ├── api.py           # Conjunto de routers de la API
│   │   └── routes/
│   │       └── items.py     # Endpoints relacionados con items
│   ├── schemas/
│   │   └── items.py         # Definiciones de modelos de datos
│   ├── crud/
│   │   └── items.py         # Lógica de procesamiento de datos
│   └── mocks/
│       └── mock_items.json  # Datos de prueba
└── tests/                   # Código de pruebas
    ├── __init__.py
    ├── conftest.py
    └── test_items.py
```

### Descripción de los archivos clave

- **`src/main.py`**: Punto de entrada de la app FastAPI
- **`src/api/routes/items.py`**: Definiciones de endpoints relacionados con items
- **`src/schemas/items.py`**: Definiciones de estructuras de datos de petición / respuesta
- **`src/crud/items.py`**: Lógica de operaciones de base de datos
- **`src/mocks/mock_items.json`**: Datos de ejemplo para desarrollo

## Paso 3: Ejecutar el servidor

Entra en el directorio del proyecto generado y ejecuta el servidor.

<div class="termy">

```console
$ cd my-first-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

INFO:     Will watch for changes in these directories: ['/path/to/my-first-api']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

Una vez que el servidor esté en marcha, puedes acceder a estas URLs en tu navegador:

- **Servidor API**: http://127.0.0.1:8000
- **Documentación Swagger UI**: http://127.0.0.1:8000/docs
- **Documentación ReDoc**: http://127.0.0.1:8000/redoc

## Paso 4: Explorar los endpoints de la API

La API generada ofrece por defecto estos endpoints:

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/items/` | Obtener todos los items |
| GET | `/items/{item_id}` | Obtener un item concreto |
| POST | `/items/` | Crear un item nuevo |
| PUT | `/items/{item_id}` | Actualizar un item |
| DELETE | `/items/{item_id}` | Eliminar un item |

### Probar la API

**1. Obtener todos los items**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/"
[
  {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  },
  {
    "id": 2,
    "name": "Mouse",
    "description": "Wireless mouse",
    "price": 29.99,
    "tax": 2.99
  }
]
```

</div>

**2. Crear un item nuevo**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/items/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Keyboard",
       "description": "Mechanical keyboard",
       "price": 150.00,
       "tax": 15.00
     }'

{
  "id": 3,
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.0,
  "tax": 15.0
}
```

</div>

**3. Obtener un item concreto**

<div class="termy">

```console
$ curl -X GET "http://127.0.0.1:8000/items/1"
{
  "id": 1,
  "name": "Laptop",
  "description": "High-performance laptop",
  "price": 999.99,
  "tax": 99.99
}
```

</div>

## Paso 5: Probar la API con Swagger UI

Entra en http://127.0.0.1:8000/docs en tu navegador para ver la documentación de la API generada automáticamente.

Lo que puedes hacer con Swagger UI:

1. **Ver los endpoints de la API**: visualmente, todos los endpoints disponibles
2. **Consultar los esquemas de petición / respuesta**: formatos de entrada / salida de cada endpoint
3. **Probar APIs directamente**: hacer llamadas reales con el botón "Try it out"
4. **Ver datos de ejemplo**: ejemplos de petición / respuesta de cada endpoint

### Cómo usar Swagger UI

1. Pulsa en el endpoint GET `/items/`
2. Pulsa el botón "Try it out"
3. Pulsa el botón "Execute"
4. Mira la respuesta del servidor

## Paso 6: Entender la estructura del código

### Aplicación principal (`src/main.py`)

```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

### Esquema de Item (`src/schemas/items.py`)

```python
from pydantic import BaseModel
from typing import Optional

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    name: Optional[str] = None
    price: Optional[float] = None

class Item(ItemBase):
    id: int

    class Config:
        from_attributes = True
```

### Lógica CRUD (`src/crud/items.py`)

```python
from typing import List, Optional
from src.schemas.items import Item, ItemCreate, ItemUpdate

class ItemCRUD:
    def __init__(self):
        self.items: List[Item] = []
        self.next_id = 1

    def create_item(self, item: ItemCreate) -> Item:
        new_item = Item(id=self.next_id, **item.dict())
        self.items.append(new_item)
        self.next_id += 1
        return new_item

    def get_items(self) -> List[Item]:
        return self.items

    def get_item(self, item_id: int) -> Optional[Item]:
        return next((item for item in self.items if item.id == item_id), None)
```

## Paso 7: Ampliar el proyecto

### Añadir rutas nuevas

Puedes añadir nuevos endpoints con el comando `fastkit addroute`:

<div class="termy">

```console
$ fastkit addroute user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ user                                     │
│ Target Directory │ /path/to/my-first-api                   │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to the current project? [Y/n]: y

✨ Successfully added new route 'user' to the current project!
```

</div>

Este comando crea los archivos:

- `src/api/routes/user.py` - endpoints relacionados con user
- `src/schemas/user.py` - modelos de datos para user
- `src/crud/user.py` - lógica de procesamiento de datos para user

### Personalizar la configuración del entorno

Puedes modificar `src/core/config.py` para cambiar los ajustes del proyecto:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My First API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "My first FastAPI server"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Paso 8: Ejecutar las pruebas

El proyecto incluye pruebas básicas:

<div class="termy">

```console
$ pytest tests/ -v
======================== test session starts ========================
collected 4 items

tests/test_items.py::test_create_item PASSED                   [ 25%]
tests/test_items.py::test_read_items PASSED                    [ 50%]
tests/test_items.py::test_read_item PASSED                     [ 75%]
tests/test_items.py::test_update_item PASSED                   [100%]

======================== 4 passed in 0.15s ========================
```

</div>

## Próximos pasos

¡Has terminado de construir un servidor API básico! Próximos pasos:

1. **[Construir APIs CRUD asíncronas](async-crud-api.md)** - Aprende procesamiento asíncrono más complejo
2. **[Integración con base de datos](database-integration.md)** - Usar PostgreSQL y SQLAlchemy
3. **[Contenedorización con Docker](docker-deployment.md)** - Preparar el despliegue a producción
4. **[Manejo personalizado de respuestas](custom-response-handling.md)** - Configurar formatos de respuesta avanzados

## Solución de problemas

### Problemas comunes

**P: El servidor no arranca**
R: Comprueba que el entorno virtual está activado y que las dependencias se han instalado correctamente.

**P: No se puede acceder a los endpoints de la API**
R: Verifica que el servidor está corriendo correctamente y que el número de puerto (por defecto: 8000) es el correcto.

**P: Las APIs no aparecen en Swagger UI**
R: Comprueba que el router está correctamente incluido en `src/main.py`.

## Resumen

En este tutorial hemos usado FastAPI-fastkit para:

- ✅ Crear un proyecto FastAPI básico
- ✅ Entender la estructura del proyecto
- ✅ Usar endpoints CRUD
- ✅ Documentar y probar la API
- ✅ Aprender métodos para ampliar el proyecto

Ahora que conoces lo básico de FastAPI, ¡prueba proyectos más complejos!

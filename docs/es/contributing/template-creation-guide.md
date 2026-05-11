# Guía para crear plantillas de FastAPI

Guía completa para añadir nuevas plantillas de proyecto FastAPI a FastAPI-fastkit.

## 🎯 Visión general

Añadir una plantilla nueva sigue un proceso de 5 pasos:

1. **📋 Planificación y diseño** — definir el propósito y la estructura de la plantilla
2. **🏗️ Implementación de la plantilla** — crear la estructura y los archivos requeridos
3. **🔍 Validación local** — validar la plantilla con el inspector
4. **📚 Documentación** — escribir el README y la guía de uso
5. **🚀 Envío y revisión** — crear el PR y obtener la revisión de la comunidad

## 📋 Paso 1: Planificación y diseño

### Definir el propósito de la plantilla

Antes de crear una plantilla nueva, responde a estas preguntas:

- **¿Cuál es el valor único de esta plantilla?**
- **¿En qué se diferencia de las plantillas existentes?**
- **¿Qué grupo de usuarios es el público objetivo?**
- **¿Qué stack tecnológico va a incluir?**

### Convención de nombres de plantillas

```
fastapi-{purpose}-{stack}
```

Ejemplos:

- `fastapi-microservice` (plantilla de microservicio)
- `fastapi-graphql` (plantilla de integración GraphQL)
- `fastapi-auth-jwt` (plantilla de autenticación JWT)

### Planificación del stack tecnológico

Define de antemano las tecnologías principales que vas a incluir:

```yaml
# Ejemplo: plantilla fastapi-microservice
core_dependencies:
  - fastapi
  - uvicorn
  - pydantic
  - pydantic-settings

additional_features:
  - sqlalchemy (ORM)
  - alembic (migraciones)
  - redis (caché)
  - celery (tareas en segundo plano)
  - pytest (pruebas)

development_tools:
  - black (formateo de código)
  - isort (ordenación de imports)
  - mypy (chequeo de tipos)
  - pre-commit (hooks de Git)
```

## 🏗️ Paso 2: Implementación de la plantilla

### Estructura de directorios requerida

```
fastapi-{template-name}/
├── src/                          # Código fuente de la aplicación
│   ├── main.py-tpl              # ✅ Punto de entrada de la app FastAPI (requerido)
│   ├── __init__.py-tpl
│   ├── api/                     # Routers de la API
│   │   ├── __init__.py-tpl
│   │   ├── api.py-tpl           # Router principal de la API
│   │   └── routes/              # Rutas individuales
│   │       ├── __init__.py-tpl
│   │       └── items.py-tpl     # Ruta de ejemplo
│   ├── core/                    # Configuración central
│   │   ├── __init__.py-tpl
│   │   └── config.py-tpl        # Gestión de ajustes
│   ├── crud/                    # Lógica CRUD
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   ├── schemas/                 # Modelos Pydantic
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   └── utils/                   # Funciones utilitarias
│       ├── __init__.py-tpl
│       └── helpers.py-tpl
├── tests/                       # ✅ Pruebas (requeridas)
│   ├── __init__.py-tpl
│   ├── conftest.py-tpl         # Configuración de pytest
│   └── test_items.py-tpl       # Pruebas de ejemplo
├── scripts/                     # Scripts
│   ├── format.sh-tpl           # Formateo de código
│   ├── lint.sh-tpl             # Linting
│   ├── run-server.sh-tpl       # Ejecución del servidor
│   └── test.sh-tpl             # Ejecución de pruebas
├── pyproject.toml-tpl           # ✅ Metadatos primarios (PEP 621, preferido)
├── setup.py-tpl                # 🟡 Metadatos legacy (aceptados por compatibilidad)
├── requirements.txt-tpl         # 🟡 Opcional si pyproject declara dependencias
├── setup.cfg-tpl               # Configuración de herramientas de desarrollo
├── README.md-tpl               # ✅ Documentación del proyecto (requerida)
├── .env-tpl                    # Plantilla de variables de entorno
└── .gitignore-tpl              # Archivo Git ignore
```

**Archivos mínimos requeridos.** Una plantilla debe proporcionar:

- Un directorio `tests/`
- `README.md-tpl`
- Al menos un archivo de metadatos: `pyproject.toml-tpl` (preferido, PEP 621) o `setup.py-tpl` (legacy, todavía aceptado)
- Una declaración de `fastapi` como dependencia en al menos uno de: `pyproject.toml-tpl` `[project].dependencies`, `requirements.txt-tpl`, o `setup.py-tpl` `install_requires`

`requirements.txt-tpl` ya no es estrictamente necesario cuando `pyproject.toml-tpl` declara `[project].dependencies`. Las plantillas modernas DEBERÍAN adoptar `pyproject.toml-tpl` como su archivo de metadatos principal.

### Guía de escritura de archivos

#### 1. Escribir main.py-tpl

```python
"""
Punto de entrada de la aplicación FastAPI

Este archivo es la aplicación principal del proyecto <project_name>
creado con FastAPI-fastkit.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api import api_router
from core.config import settings

# Crear la app FastAPI (requerido por la validación del inspector)
app = FastAPI(
    title="<project_name>",
    description="Project created with FastAPI-fastkit",
    version="1.0.0",
)

# Configuración del middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar el router de la API
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {"message": "Hello from <project_name>!"}

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. Escribir pyproject.toml-tpl (preferido)

Las plantillas modernas deberían declarar metadatos y dependencias con un `pyproject.toml-tpl` PEP 621. Como mínimo el archivo debe exponer una sección `[project]` con `name`, `version`, `description` y una lista `dependencies` que incluya `fastapi`. Las plantillas también deben llevar dos marcadores de identidad de FastAPI-fastkit para que `is_fastkit_project()` pueda distinguir los proyectos generados de otros proyectos FastAPI no relacionados dentro del espacio de trabajo del usuario:

- Prefijo `[FastAPI-fastkit templated]` en `description`
- Una tabla específica `[tool.fastapi-fastkit]` con `managed = true`

La detección acepta cualquiera de los dos marcadores (la comparación no distingue entre mayúsculas y minúsculas). La inyección de metadatos añadirá ambos al generar el proyecto si la plantilla los omite, pero los autores deberían incluirlos explícitamente.

```toml
[project]
name = "<project_name>"
version = "0.1.0"
description = "[FastAPI-fastkit templated] <description>"
authors = [
    {name = "<author>", email = "<author_email>"},
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.28.0",
]

[tool.fastapi-fastkit]
managed = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 3. Escribir requirements.txt-tpl (opcional)

Opcional cuando `pyproject.toml-tpl` declara `[project].dependencies`. Sigue siendo útil para plantillas que prefieran flujos exclusivamente con `pip`.

```txt
# Dependencias FastAPI core (requeridas)
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Validación de datos
pydantic==2.5.0
pydantic-settings==2.1.0

# Gestión de variables de entorno
python-dotenv==1.0.0

# Base de datos (si hace falta)
sqlalchemy==2.0.23
alembic==1.13.0

# Herramientas de desarrollo
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Calidad de código
black==23.11.0
isort==5.12.0
mypy==1.7.1
```

#### 4. Escribir setup.py-tpl (legacy — opcional si existe pyproject)

Se conserva para plantillas legacy. Las plantillas nuevas no necesitan este archivo si traen `pyproject.toml-tpl`.

```python
"""
Setup del paquete <project_name>

Proyecto creado con FastAPI-fastkit.
"""
from setuptools import find_packages, setup

# Lista de dependencias (anotación de tipo requerida)
install_requires: list[str] = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

setup(
    name="<project_name>",
    version="1.0.0",
    description="[FastAPI-fastkit templated] <description>",  # Marcador de identidad usado por is_fastkit_project()
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="<author>",
    author_email="<author_email>",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
```

#### 5. Escribir los archivos de pruebas

```python
# tests/test_items.py-tpl
"""
Módulo de pruebas de la API de items
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test del health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_item():
    """Test de creación de item"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]

def test_read_items():
    """Test de listado de items"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 🔍 Paso 3: Validación local

### Ejecutar los scripts de validación automatizada

Cuando tu plantilla nueva esté lista, valídala con estos comandos:

```bash
# Validar todas las plantillas
make inspect-templates

# Validar solo una plantilla concreta
make inspect-template TEMPLATES="fastapi-your-template"

# Validar con salida detallada
python scripts/inspect-templates.py --templates "fastapi-your-template" --verbose
```

!!! note

    Cuando envíes un PR, el flujo de trabajo **Template PR Inspection** se ejecutará automáticamente y validará tus cambios en la plantilla. Recibirás comentarios directamente en tu PR.

### Checklist de validación

El inspector valida automáticamente lo siguiente:

#### ✅ Validación de la estructura de archivos

- [ ] Existe el directorio `tests/`
- [ ] Existe el archivo `README.md-tpl`
- [ ] Existe al menos uno de `pyproject.toml-tpl` (preferido) o `setup.py-tpl` (legacy)

#### ✅ Validación de extensiones

- [ ] Todos los archivos Python usan la extensión `.py-tpl`
- [ ] No hay archivos con extensión `.py`

#### ✅ Validación de dependencias

- [ ] `fastapi` está declarado en al menos uno de:
    - [ ] `pyproject.toml-tpl` bajo `[project].dependencies` (preferido)
    - [ ] `requirements.txt-tpl`
    - [ ] `setup.py-tpl` bajo `install_requires`

#### ✅ Validación de la implementación de FastAPI

- [ ] Existe el import de `FastAPI` en `main.py-tpl`
- [ ] Existe la creación de la app del estilo `app = FastAPI()` en `main.py-tpl`

#### ✅ Validación de ejecución de pruebas

- [ ] La creación del entorno virtual es correcta
- [ ] La instalación de dependencias es correcta
- [ ] Todas las pruebas de pytest pasan

#### ✅ Pruebas automatizadas de plantillas

FastAPI-fastkit incluye **pruebas automatizadas de plantillas** que ejecutan pruebas integrales sobre todas las plantillas:

**Cobertura de pruebas:**

- ✅ Proceso de creación de la plantilla
- ✅ Inyección de metadatos del proyecto
- ✅ Configuración del entorno virtual
- ✅ Instalación de dependencias (todos los gestores)
- ✅ Validación básica de la estructura del proyecto
- ✅ Identificación del proyecto como FastAPI

**Ejecución de las pruebas:**
```console
# Probar todas las plantillas automáticamente
$ pytest tests/test_templates/test_all_templates.py -v

# Probar una plantilla concreta
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v
```

**Descubrimiento automático de pruebas:**
Las plantillas nuevas se **descubren automáticamente** y se prueban sin configuración manual:

1. ✅ **Cero configuración**: añade plantilla → pruebas automáticas
2. ✅ **Pruebas consistentes**: mismos estándares de calidad para todas las plantillas
3. ✅ **Varios gestores de paquetes**: se prueba con UV, PDM, Poetry y PIP
4. ✅ **Validación completa**: estructura, metadatos y funcionalidad

**Qué significa esto para ti:**

- 🚀 **No hace falta añadir archivos de prueba en el código principal de `FastAPI-fastkit`**: tu plantilla se prueba automáticamente
- ⚡ **Desarrollo más rápido**: te concentras en el contenido de la plantilla, no en la configuración de las pruebas
- 🛡️ **Aseguramiento de calidad**: pruebas consistentes para todas las plantillas
- 🔄 **Integración CI/CD**: pruebas automáticas en los pull requests

**Pruebas manuales que aún son necesarias:**

- 🧪 **Funcionalidad específica de la plantilla**: lógica de negocio y features personalizadas
- 🔧 **Pruebas de integración**: servicios externos y flujos complejos
- 📱 **Escenarios de extremo a extremo**: flujos de usuario completos

**Buenas prácticas de prueba:**
```console
# 1. Probar tu plantilla localmente
$ fastkit startdemo your-template-name

# 2. Ejecutar las pruebas automatizadas
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v

# 3. Probar con distintos gestores de paquetes
$ fastkit startdemo your-template-name --package-manager poetry
$ fastkit startdemo your-template-name --package-manager pdm
$ fastkit startdemo your-template-name --package-manager uv
```

### Checklist de validación manual

Además de la validación automatizada, comprueba a mano lo siguiente:

#### 🔧 Calidad del código

- [ ] El código sigue la guía de estilo PEP 8
- [ ] Uso adecuado de type hints
- [ ] Nombres significativos para variables y funciones
- [ ] Comentarios y docstrings adecuados

#### 🏗️ Arquitectura

- [ ] Separación de responsabilidades (API, lógica de negocio, acceso a datos)
- [ ] Diseño de componentes reutilizable
- [ ] Estructura escalable
- [ ] Buenas prácticas de seguridad aplicadas

#### 📚 Documentación

- [ ] `README.md-tpl` sigue el formato de PROJECT_README_TEMPLATE.md
- [ ] Métodos de instalación y ejecución indicados
- [ ] Documentación de la API (OpenAPI/Swagger)
- [ ] Explicación de las variables de entorno

## 📚 Paso 4: Documentación

### Escribir el README.md-tpl

Escribe basándote en la guía de [PROJECT_README_TEMPLATE.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/PROJECT_README_TEMPLATE.md).

### Escribir la documentación de descripción de la plantilla

Añade una descripción de tu plantilla nueva en `src/fastapi_fastkit/fastapi_project_template/README.md`:

```markdown
## fastapi-your-template

Escribe aquí una descripción breve y los casos de uso de tu plantilla nueva.

### Funcionalidades:
- Funcionalidad 1
- Funcionalidad 2
- Funcionalidad 3

### Casos de uso:
- Caso de uso 1
- Caso de uso 2
```

## 🚀 Paso 5: Envío y revisión

### Checklist previo a la creación del PR

- [ ] Toda la validación automatizada pasada (`make inspect-templates`)
- [ ] Formato de código completado (`make format`)
- [ ] Comprobaciones de linting pasadas (`make lint`)
- [ ] Todas las pruebas pasadas (`make test`)
- [ ] Documentación completada
- [ ] Guía CONTRIBUTING.md seguida

### Título y descripción del PR

```
[TEMPLATE] Add fastapi-{template-name} template

## Overview
Adds a new {purpose} template.

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Validation Results
- [ ] Inspector validation passed
- [ ] All tests passed
- [ ] Documentation completed

## Usage Example
\```bash
fastkit startdemo
# Select template: fastapi-{template-name}
\```

## Related Issues
Closes #issue-number
```

### Proceso de revisión

1. **Validación automatizada**: GitHub Actions valida la plantilla automáticamente
    - **Template PR Inspection**: ejecuta `inspect-changed-templates.py` en los PRs que modifican plantillas
    - **Inspección semanal**: validación completa de plantillas cada miércoles
2. **Revisión de código**: mantenedores y comunidad revisan el código
3. **Pruebas**: la plantilla se prueba en distintos entornos
4. **Revisión de la documentación**: se revisa la precisión y el grado de completitud de la documentación
5. **Aprobación y merge**: se fusiona en `main` cuando se cumplen todos los requisitos

!!! note

    Recibirás comentarios automáticos en tu PR con los resultados de la validación. ¡Revísalos antes de pedir revisión!

## 🎯 Buenas prácticas

### Consideraciones de seguridad

- Gestiona la información sensible con variables de entorno
- Configuración CORS adecuada
- Validación de los datos de entrada
- Prevención de inyección SQL

### Optimización del rendimiento

- Aprovechar el procesamiento asíncrono
- Optimizar las consultas a la base de datos
- Estrategias de caché adecuadas
- Configuración de compresión de respuestas

### Mantenibilidad

- Estructura clara del código
- Cobertura de pruebas amplia
- Documentación detallada
- Configuración de logging y monitorización

## 🆘 ¿Necesitas ayuda?

- 📖 [Guía de configuración de desarrollo](development-setup.md)
- 📋 [Guía de código](code-guidelines.md)
- 💬 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- 📧 [Contactar al mantenedor](mailto:bbbong9@gmail.com)

Añadir una plantilla nueva es una gran contribución a la comunidad de FastAPI-fastkit.
¡Tus ideas y tu esfuerzo serán de gran ayuda para otros desarrolladores! 🚀

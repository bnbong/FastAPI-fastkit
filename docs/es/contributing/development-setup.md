# Configuración del entorno de desarrollo

Guía completa para configurar un entorno de desarrollo y contribuir a FastAPI-fastkit.

## Requisitos previos

Antes de empezar, asegúrate de tener:

- **Python 3.12 o superior** instalado
- **Git** instalado y configurado
- **Conocimientos básicos** de Python y FastAPI
- **Editor de texto o IDE** (VS Code, PyCharm, etc.)

## Configuración rápida con el Makefile

FastAPI-fastkit incluye un Makefile para una configuración de desarrollo fácil:

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make install-dev
Setting up development environment...
Creating virtual environment...
Installing dependencies...
Installing pre-commit hooks...
✅ Development environment ready!
```

</div>

Este único comando:

- Instala el paquete en modo editable con las dependencias de desarrollo
- Configura los pre-commit hooks
- Ajusta las herramientas de desarrollo

!!! note

    Deberías crear y activar un entorno virtual antes de ejecutar este comando.

## Configuración manual

Si prefieres configurarlo manualmente o el Makefile no funciona en tu sistema:

### 1. Clonar el repositorio

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
```

</div>

### 2. Crear un entorno virtual

<div class="termy">

```console
$ python -m venv .venv
$ source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

</div>

### 3. Instalar las dependencias

<div class="termy">

```console
# Instalar el paquete en modo editable con dependencias de desarrollo
$ pip install -e ".[dev]"

# O instalar desde los archivos de requirements
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

</div>

### 4. Configurar los pre-commit hooks

<div class="termy">

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

</div>

### 5. Verificar la instalación

<div class="termy">

```console
$ fastkit --version
fastapi-fastkit, version 1.2.1

$ python -m pytest tests/
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
tests/test_templates.py::test_template_listing PASSED
...
======================== 45 passed in 2.34s ========================
```

</div>

## Herramientas de desarrollo

El entorno de desarrollo incluye varias herramientas para mantener la calidad del código:

### Comandos directos

Con el Makefile:

```console
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!
```

Con los scripts incluidos:

```console
$ ./scripts/format.sh
$ ./scripts/lint.sh
```

### Formato del código

**Black** — formateador de código:

<div class="termy">

```console
$ black src/ tests/
reformatted src/main.py
reformatted tests/test_cli.py
All done! ✨ 🍰 ✨
```

</div>

**isort** — ordenador de imports:

<div class="termy">

```console
$ isort src/ tests/
Fixing import order in src/main.py
```

</div>

### Linting de código

**mypy** — chequeo de tipos:

<div class="termy">

```console
$ mypy src/
Success: no issues found in 12 source files
```

</div>

## Comandos Make disponibles

El Makefile del proyecto incluye comandos útiles para las tareas de desarrollo más comunes:

### Comandos de configuración

| Comando | Descripción |
|---|---|
| `make install` | Instala el paquete en modo producción |
| `make install-dev` | Instala el paquete con dependencias de desarrollo |
| `make install-test` | Instala el paquete para pruebas (desinstala + reinstala) |
| `make uninstall` | Desinstala el paquete |
| `make clean` | Limpia artefactos de build y archivos de caché |

### Comandos de calidad de código

| Comando | Descripción |
|---|---|
| `make format` | Formatea el código con black e isort |
| `make format-check` | Comprueba el formato sin hacer cambios |
| `make lint` | Ejecuta todas las comprobaciones de linting (isort, black, mypy) |

### Comandos de pruebas

| Comando | Descripción |
|---|---|
| `make test` | Ejecuta todas las pruebas |
| `make test-verbose` | Ejecuta las pruebas con salida detallada |
| `make test-coverage` | Ejecuta las pruebas con informe de cobertura |
| `make coverage-report` | Genera un informe de cobertura detallado (FORMAT=html/xml/json/all) |

### Comandos de inspección de plantillas

| Comando | Descripción |
|---|---|
| `make inspect-templates` | Inspecciona todas las plantillas |
| `make inspect-templates-verbose` | Inspecciona con salida detallada |
| `make inspect-template` | Inspecciona plantillas concretas (parámetro TEMPLATES) |

### Comandos de documentación

| Comando | Descripción |
|---|---|
| `make serve-docs` | Sirve la documentación localmente |
| `make build-docs` | Construye la documentación |

### Comandos de traducción

| Comando | Descripción |
|---|---|
| `make translate` | Traduce la documentación (parámetros LANG, PROVIDER, MODEL) |

### Ejemplos

<div class="termy">

```console
# Formatear el código y ejecutar todas las comprobaciones
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!

# Ejecutar pruebas con cobertura
$ make test-coverage
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
...
======================== 45 passed in 2.34s ========================

---------- coverage: platform darwin, python 3.12.1-final-0 ----------
Name                     Stmts   Miss  Cover
--------------------------------------------
src/main.py                 45      2    96%
src/cli.py                  89      5    94%
src/templates.py            67      3    96%
--------------------------------------------
TOTAL                      201     10    95%

# Generar informe HTML de cobertura
$ make coverage-report FORMAT=html
🌐 Opening HTML coverage report in browser...

# Traducir la documentación al coreano
$ make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
Starting translation...
Running: python scripts/translate.py --target-lang ko --api-provider github --model gpt-4o-mini
```

</div>

## Estructura del proyecto

Entender la estructura del proyecto es clave para el desarrollo:

```bash
FastAPI-fastkit/
├── src/
│   ├── fastapi_fastkit/
│   │   ├── __main__.py                      # Punto de entrada de la aplicación
│   │   ├── backend/
│   │   │   ├── inspector.py                 # Inspector de plantillas
│   │   │   ├── interactive/
│   │   │   │   ├── config_builder.py        # Constructor de configuración para el modo interactivo
│   │   │   │   ├── prompts.py               # Prompts del modo interactivo
│   │   │   │   ├── selectors.py             # Lógica de selectores del modo interactivo
│   │   │   │   └── validators.py            # Validadores de entrada del modo interactivo
│   │   │   ├── main.py                      # Punto de entrada de la lógica del backend
│   │   │   ├── package_managers/
│   │   │   │   ├── base.py                  # Clase base de los gestores de paquetes
│   │   │   │   ├── factory.py               # Factory de gestores de paquetes
│   │   │   │   ├── pdm_manager.py           # Gestor PDM
│   │   │   │   ├── pip_manager.py           # Gestor pip
│   │   │   │   ├── poetry_manager.py        # Gestor Poetry
│   │   │   │   └── uv_manager.py            # Gestor uv
│   │   │   ├── project_builder/
│   │   │   │   ├── config_generator.py      # Generador de configuración para el project builder
│   │   │   │   └── dependency_collector.py  # Colector de dependencias para el project builder
│   │   │   └── transducer.py                # Transducer del project builder
│   │   ├── cli.py                           # Punto de entrada principal de la CLI
│   │   ├── core/
│   │   │   ├── exceptions.py                # Manejo de excepciones
│   │   │   └── settings.py                  # Configuración
│   │   ├── fastapi_project_template/
│   │   │   ├── PROJECT_README_TEMPLATE.md   # README base de las plantillas fastkit
│   │   │   ├── README.md                    # README de las plantillas fastkit
│   │   │   ├── fastapi-async-crud/
│   │   │   ├── fastapi-custom-response/
│   │   │   ├── fastapi-default/
│   │   │   ├── fastapi-dockerized/
│   │   │   ├── fastapi-empty/
│   │   │   ├── fastapi-mcp/
│   │   │   ├── fastapi-psql-orm/
│   │   │   ├── fastapi-single-module/
│   │   │   └── modules/
│   │   │       ├── api/
│   │   │       │   └── routes/
│   │   │       ├── crud/
│   │   │       └── schemas/
│   │   ├── py.typed
│   │   └── utils/
│   │       ├── logging.py                   # Configuración de logging
│   │       └── main.py                      # Punto de entrada principal de FastAPI-fastkit
│   └── logs
├── tests
│   ├── conftest.py                          # Configuración de pytest
│   ├── test_backends/
│   ├── test_cli_operations/
│   ├── test_core.py
│   ├── test_rich/
│   ├── test_templates/
│   └── test_utils.py
├── uv.lock
├── docs/                                    # Documentación
├── scripts/                                 # Scripts de desarrollo
├── mkdocs.yml
├── overrides/                               # overrides de mkdocs
├── pdm.lock
├── pyproject.toml
├── requirements-docs.txt                    # requirements para la documentación
├── requirements.txt                         # requirements para desarrollo
├── CHANGELOG.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── SECURITY.md
└── env.example                              # ejemplo de variables de entorno (configura las del modelo IA de traducción)
```

### Directorios clave

- **`src/fastapi_fastkit/`** — código fuente del paquete principal
    - **`cli.py`** — punto de entrada principal de la CLI
    - **`backend/`** — lógica central del backend
        - **`inspector.py`** — inspector de plantillas
        - **`interactive/`** — componentes del modo interactivo (prompts, selectores, validadores)
        - **`package_managers/`** — implementaciones de los gestores de paquetes (pip, uv, pdm, poetry)
        - **`project_builder/`** — utilidades de construcción de proyectos
        - **`transducer.py`** — transducer de plantillas
    - **`core/`** — configuración central y excepciones
    - **`fastapi_project_template/`** — plantillas de proyecto (fastapi-default, fastapi-async-crud, etc.)
    - **`utils/`** — funciones de utilidad compartidas
- **`tests/`** — suite de pruebas
    - **`test_backends/`** — pruebas específicas del backend
    - **`test_cli_operations/`** — pruebas de operaciones de la CLI
    - **`test_templates/`** — pruebas del sistema de plantillas
- **`docs/`** — documentación (MkDocs)
    - Guías de usuario, tutoriales y referencia de la API

## Flujo de desarrollo

### 1. Crear una rama de feature

<div class="termy">

```console
$ git checkout -b feature/add-new-template
Switched to a new branch 'feature/add-new-template'
```

</div>

### 2. Hacer los cambios

Edita el código, añade funcionalidades, arregla bugs...

### 3. Ejecutar pruebas y comprobaciones

<div class="termy">

```console
$ make dev-check
Running all quality checks...
Running all tests...
✅ All tests passed!
```

</div>

### 4. Hacer commit de los cambios

Los pre-commit hooks se ejecutan automáticamente:

<div class="termy">

```console
$ git add .
$ git commit -m "Add new FastAPI template with authentication"
format...................................................................Passed
isort-check..............................................................Passed
black-fix................................................................Passed
mypy.....................................................................Passed
[feature/add-new-template abc1234] Add new FastAPI template with authentication
```

</div>

### 5. Push y crear el Pull Request

<div class="termy">

```console
$ git push origin feature/add-new-template
$ gh pr create --title "Add new FastAPI template with authentication"
```

</div>

## Pruebas

### Ejecutar las pruebas

**Todas las pruebas:**

<div class="termy">

```console
$ make test
# o
$ python -m pytest
```

</div>

**Un archivo de pruebas concreto:**

<div class="termy">

```console
$ python -m pytest tests/test_cli.py -v
```

</div>

**Con cobertura:**

<div class="termy">

```console
$ make test-coverage
# o
$ python -m pytest --cov=src --cov-report=html
```

</div>

### Escribir pruebas

Cuando añadas nuevas funcionalidades, incluye siempre pruebas:

```python
# tests/test_commands/test_new_feature.py
import pytest
from fastapi_fastkit.commands.new_feature import NewFeatureCommand

class TestNewFeatureCommand:
    def test_command_success(self):
        """Test successful command execution"""
        command = NewFeatureCommand()
        result = command.execute(valid_args)
        assert result.success is True
        assert result.message == "Feature executed successfully"

    def test_command_validation_error(self):
        """Test command with invalid arguments"""
        command = NewFeatureCommand()
        with pytest.raises(ValueError, match="Invalid argument"):
            command.execute(invalid_args)

    def test_command_edge_case(self):
        """Test edge case handling"""
        command = NewFeatureCommand()
        result = command.execute(edge_case_args)
        assert result.success is True
        assert "warning" in result.message.lower()
```

### Categorías de pruebas

**Pruebas unitarias** — prueban funciones y clases individuales:

```python
def test_validate_project_name():
    assert validate_project_name("valid-name") is True
    assert validate_project_name("invalid name!") is False
```

**Pruebas de integración** — prueban interacciones entre comandos:

```python
def test_init_command_creates_project(tmp_path):
    result = runner.invoke(cli, ['init'], input='test-project\n...')
    assert result.exit_code == 0
    assert (tmp_path / "test-project").exists()
```

**Pruebas de extremo a extremo** — cubren flujos completos:

```python
def test_full_project_creation_workflow(tmp_path):
    # Crear el proyecto
    result = runner.invoke(cli, ['init'], input='...')
    assert result.exit_code == 0

    # Añadir una ruta
    result = runner.invoke(cli, ['addroute', 'test-project', 'users'])
    assert result.exit_code == 0

    # Verificar que existen los archivos
    assert (tmp_path / "test-project" / "src" / "api" / "routes" / "users.py").exists()
```

## Documentación

### Servir la documentación localmente

<div class="termy">

```console
$ make serve-docs
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.43 seconds
INFO     -  [14:30:00] Serving on http://127.0.0.1:8000/
```

</div>

### Construir la documentación

<div class="termy">

```console
$ make build-docs
INFO     -  Building documentation...
INFO     -  Documentation built in 0.43 seconds
```

</div>

### Escribir documentación

La documentación se escribe en Markdown y se construye con MkDocs. Aquí tienes un ejemplo de estructura:

**Plantilla de guía de funcionalidad:**

````markdown
# New Feature Guide

This guide explains how to use the new feature.

## Prerequisites

- FastAPI-fastkit installed
- Basic Python knowledge

## Usage

<div class="termy">

```console
$ fastkit new-feature --option value
✅ Feature executed successfully!
```

</div>

!!! tip "Pro Tip"
    Use `--help` to see all available options.
````

Para una referencia detallada sobre cómo usar `mkdocs-material`, consulta la [documentación de mkdocs-material](https://squidfunk.github.io/mkdocs-material/reference/admonitions/).

## Guía de estilo de código

### Estilo de código Python

Sigue [PEP 8](https://www.python.org/dev/peps/pep-0008/) con estas reglas específicas:

- **Longitud de línea**: 88 caracteres (por defecto en Black)
- **Imports**: organizados con isort
- **Type hints**: requeridos en todas las funciones públicas
- **Docstrings**: estilo Google para todas las APIs públicas

### Ejemplo

```python
from typing import List, Optional
from pathlib import Path

def create_project_structure(
    project_name: str,
    template_path: Path,
    output_dir: Optional[Path] = None,
) -> List[Path]:
    """Create project structure from template.

    Args:
        project_name: Name of the project to create
        template_path: Path to the template directory
        output_dir: Output directory, defaults to current directory

    Returns:
        List of created file paths

    Raises:
        ValueError: If project_name is invalid
        FileNotFoundError: If template_path doesn't exist
    """
    if not project_name.isidentifier():
        raise ValueError(f"Invalid project name: {project_name}")

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Implementación aquí...
    return created_files
```

## Variables de entorno

Para desarrollo, puedes definir estas variables de entorno:

| Variable | Descripción | Por defecto |
|---|---|---|
| `FASTKIT_DEBUG` | Activa el logging de depuración | `False` |
| `FASTKIT_DEV_MODE` | Activa funcionalidades de desarrollo | `False` |
| `FASTKIT_TEMPLATE_DIR` | Directorio de plantillas personalizadas | Plantillas integradas |
| `FASTKIT_CONFIG_DIR` | Directorio de configuración | `~/.fastkit` |
| `TRANSLATION_API_KEY` | Clave de API de traducción (usa un PAT de GitHub al usar el [proveedor de modelos IA de GitHub](https://github.com/marketplace/models/azure-openai)) | `None` |

<div class="termy">

```console
$ export FASTKIT_DEBUG=true
$ export FASTKIT_DEV_MODE=true
$ fastkit init
DEBUG: Loading configuration from /home/user/.fastkit/
DEBUG: Available templates: ['fastapi-default', ...]
```

</div>

Para otras variables de entorno, consulta el módulo [@settings.py](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/core/settings.py).

## Solución de problemas

### Problemas habituales

**1. Los pre-commit hooks fallan:**

<div class="termy">

```console
$ git commit -m "Fix bug"
black....................................................................Failed
hookid: black

Files were modified by this hook. Additional output:

would reformat src/cli.py
```

</div>

**Solución:** ejecuta los formateadores y vuelve a hacer commit:

<div class="termy">

```console
$ make format
$ git add .
$ git commit -m "Fix bug"
```

</div>

**2. Las pruebas fallan en versiones distintas de Python:**

**Solución:** usa tox para probar con varias versiones:

<div class="termy">

```console
$ pip install tox
$ tox
py38: commands succeeded
py39: commands succeeded
py310: commands succeeded
py311: commands succeeded
py312: commands succeeded
```

</div>

**3. Errores de import en desarrollo:**

**Solución:** instala el paquete en modo editable:
<div class="termy">

```console
$ pip install -e .
```

</div>

### Cómo conseguir ayuda

- **[GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)**: reportar bugs y solicitar funcionalidades
- **[GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)**: preguntas e ideas
- **Documentación**: revisa la [Guía de usuario](../user-guide/installation.md)

## Pautas para contribuir

### Antes de enviar un PR

1. **Ejecuta todas las comprobaciones:** `make dev-check`
2. **Actualiza la documentación** si hace falta
3. **Añade pruebas** para las funcionalidades nuevas
4. **Sigue las convenciones de mensaje de commit**

### Formato del mensaje de commit

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**Tipos:**

- `feat`: nueva funcionalidad
- `fix`: corrección de bug
- `docs`: cambios de documentación
- `style`: cambios de estilo de código
- `refactor`: refactorización
- `test`: añadir o cambiar pruebas
- `chore`: tareas de mantenimiento

**Ejemplos:**

```
feat(cli): add new template command

Add support for creating projects from custom templates.
The command accepts a template path and creates a new
project with the specified configuration.

Fixes #45

fix(templates): handle missing template files gracefully

When a template file is missing, show a clear error message
instead of crashing with a stack trace.

Fixes #67
```

## Proceso de release

Para mantenedores, el proceso de release es:

1. **Actualizar la versión** en `setup.py` y `__init__.py`
2. **Actualizar CHANGELOG.md**
3. **Crear un PR de release**
4. **Etiquetar la release** tras el merge
5. **GitHub Actions** se encarga de la build y publicación

<div class="termy">

```console
$ git tag v1.2.0
$ git push origin v1.2.0
```

</div>

## Próximos pasos

Ahora que tu entorno de desarrollo está listo:

1. **[Explora el código](https://github.com/bnbong/FastAPI-fastkit/tree/main/src/fastapi_fastkit)** para entender la arquitectura
2. **Ejecuta la suite de pruebas** para asegurarte de que todo funciona
3. **Elige un [issue](https://github.com/bnbong/FastAPI-fastkit/issues)** de GitHub para trabajar
4. **Únete a las [discusiones](https://github.com/bnbong/FastAPI-fastkit/discussions)** para conectar con otros colaboradores

¡Feliz programación! 🚀

!!! tip "Consejos de desarrollo"
    - Usa `make dev-check` antes de hacer commit
    - Escribe primero las pruebas (enfoque TDD)
    - Mantén los commits pequeños y enfocados
    - Actualiza la documentación junto con las nuevas funcionalidades

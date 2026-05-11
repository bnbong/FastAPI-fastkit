# Guía de código

Guía completa de estándares y buenas prácticas de codificación para contribuir a FastAPI-fastkit.

## Visión general

Esta guía garantiza la calidad, consistencia y mantenibilidad del código en todo el proyecto FastAPI-fastkit. Seguir estos estándares ayuda a construir un código base fácil de leer, mantener y ampliar.

## Estilo de código Python

### Conformidad con PEP 8

Sigue [PEP 8](https://www.python.org/dev/peps/pep-0008/) con estas configuraciones específicas:

- **Longitud de línea**: 88 caracteres (por defecto en Black)
- **Indentación**: 4 espacios (sin tabs)
- **Comas finales**: requeridas en estructuras multilínea
- **Comillas de strings**: se prefieren comillas dobles

### Formato de código

Usamos **Black** para formateo automático:

```python
# Bien ✅
def create_project(
    name: str,
    template: str,
    options: Dict[str, Any],
) -> ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name, template=template)

# Mal ❌
def create_project(name: str, template: str, options: Dict[str,Any])->ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name,template=template)
```

### Organización de imports

Usa **isort** para organizar imports:

```python
# Imports de la librería estándar
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# Imports de terceros
import click
import pydantic
from fastapi import FastAPI

# Imports locales
from fastapi_fastkit.commands import BaseCommand
from fastapi_fastkit.utils import validation
from fastapi_fastkit.templates.manager import TemplateManager
```

## Type hints

### Type hints obligatorios

Todas las funciones y métodos públicos deben incluir type hints:

```python
# Bien ✅
def validate_project_name(name: str) -> bool:
    """Validate project name format."""
    return name.isidentifier() and not name.startswith('_')

def create_files(
    files: List[Path],
    template_data: Dict[str, Any]
) -> List[Path]:
    """Create files from template data."""
    created_files = []
    for file_path in files:
        # Implementación...
        created_files.append(file_path)
    return created_files

# Mal ❌
def validate_project_name(name):
    return name.isidentifier() and not name.startswith('_')
```

### Anotaciones de tipos complejos

Usa anotaciones de tipo adecuadas para estructuras complejas:

```python
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

# Alias de tipos complejos
ProjectConfig = Dict[str, Union[str, bool, List[str]]]
FileMapping = Dict[Path, str]
ValidationResult = Tuple[bool, Optional[str]]

def process_template(
    template_path: Path,
    config: ProjectConfig,
    output_dir: Optional[Path] = None,
) -> ValidationResult:
    """Process template with configuration."""
    # Implementación...
    return True, None
```

## Convenciones de nombres

### Variables y funciones

- **snake_case** para variables y funciones
- **Nombres descriptivos** que expliquen su propósito
- **Evita abreviaturas** salvo las muy reconocidas

```python
# Bien ✅
project_name = "my-api"
template_directory = Path("templates")
user_input_data = get_user_input()

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    return "@" in email and "." in email

# Mal ❌
proj_nm = "my-api"
temp_dir = Path("templates")
usr_data = get_input()

def validate_email(e):
    return "@" in e and "." in e
```

### Clases

- **PascalCase** para nombres de clase
- **Descriptivos y específicos**

```python
# Bien ✅
class SomeClass:
    """Represents example class of FastAPI-fastkit."""
    pass

class SomeClassValidationError(Exception):
    """Raised when example class validation fails."""
    pass

class UserInputHandler:
    """Handles user input validation and processing."""
    pass

# Mal ❌
class Class:
    pass

class Error(Exception):
    pass

class Handler:
    pass
```

### Constantes

- **MAYÚSCULAS** con guiones bajos
- Solo **a nivel de módulo**

```python
# Bien ✅
DEFAULT_TEMPLATE_NAME = "fastapi-default"
MAX_PROJECT_NAME_LENGTH = 50
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# Mal ❌
default_template = "fastapi-default"
maxLength = 50
versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

## Estándares de documentación

### Docstrings

Usa **docstrings estilo Google** para todas las APIs públicas:

```python
def create_project_structure(
    project_name: str,
    template_path: Path,
    output_directory: Optional[Path] = None,
    overwrite: bool = False,
) -> List[Path]:
    """Create project structure from template.

    Creates a new FastAPI project structure by copying and processing
    template files. Supports variable substitution and file customization.

    Args:
        project_name: Name of the project to create. Must be a valid
            Python identifier.
        template_path: Path to the template directory containing
            source files and configuration.
        output_directory: Directory where project will be created.
            Defaults to current working directory.
        overwrite: Whether to overwrite existing files. If False,
            raises error when files exist.

    Returns:
        List of created file paths in order of creation.

    Raises:
        ValueError: If project_name is invalid or empty.
        FileExistsError: If output directory exists and overwrite is False.
        TemplateNotFoundError: If template_path doesn't exist.
        PermissionError: If insufficient permissions to create files.

    Example:
        ```python
        template_path = Path("templates/fastapi-default")
        created_files = create_project_structure(
            project_name="my-api",
            template_path=template_path,
            output_directory=Path("./projects"),
            overwrite=False
        )
        print(f"Created {len(created_files)} files")
        ```
    """
    # Implementación aquí...
    pass
```

### Comentarios

- **Explica el PORQUÉ, no el QUÉ**
- **Úsalos con moderación** — el código debería autoexplicarse
- **Actualiza los comentarios** cuando cambia el código

```python
# Bien ✅
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # Saltar la validación en modo desarrollo para permitir paquetes experimentales
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # Comprobar cada requirement contra vulnerabilidades de seguridad conocidas
    for requirement in requirements:
        if is_vulnerable_package(requirement):
            return False

    return True

# Mal ❌
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # Comprobar si es modo dev
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # Bucle por los requirements
    for requirement in requirements:
        # Comprobar si es vulnerable
        if is_vulnerable_package(requirement):
            return False

    # Devolver true
    return True
```

## Manejo de errores

### Manejo de excepciones

- **Captura excepciones concretas** siempre que sea posible
- **Proporciona mensajes de error útiles**
- **Loguea los errores correctamente**

```python
# Bien ✅
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise TemplateNotFoundError(
            f"Template configuration not found: {config_file}"
        )
    except yaml.YAMLError as e:
        raise TemplateConfigError(
            f"Invalid YAML syntax in {config_file}: {e}"
        )
    except PermissionError:
        raise TemplateAccessError(
            f"Permission denied reading {config_file}"
        )

# Mal ❌
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config: {e}")
```

### Excepciones personalizadas

Define excepciones específicas para distintas condiciones de error:

```python
class FastKitError(Exception):
    """Base exception for FastAPI-fastkit errors."""
    pass

class ProjectCreationError(FastKitError):
    """Raised when project creation fails."""
    pass

class TemplateNotFoundError(FastKitError):
    """Raised when template is not found."""
    pass

class ValidationError(FastKitError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field
```

## Estándares de pruebas

### Estructura de las pruebas

Organiza las pruebas con una estructura y nombres claros:

```python
class TestProjectCreation:
    """Test project creation functionality."""

    def test_create_project_with_valid_name(self, tmp_path):
        """Test project creation with valid project name."""
        project_name = "test-project"
        result = create_project(project_name, template="minimal", output=tmp_path)

        assert result.success is True
        assert (tmp_path / project_name).exists()
        assert (tmp_path / project_name / "src" / "main.py").exists()

    def test_create_project_with_invalid_name(self):
        """Test project creation fails with invalid name."""
        with pytest.raises(ValueError, match="Invalid project name"):
            create_project("invalid-project-name!", template="minimal")

    def test_create_project_overwrites_existing(self, tmp_path):
        """Test project creation overwrites existing directory when forced."""
        project_name = "existing-project"
        project_dir = tmp_path / project_name
        project_dir.mkdir()

        result = create_project(
            project_name,
            template="minimal",
            output=tmp_path,
            overwrite=True
        )

        assert result.success is True
        assert project_dir.exists()
```

### Cobertura de pruebas

- **Apunta al 90% o más** de cobertura en código nuevo
- **Cubre casos límite** y condiciones de error
- **Mockea las dependencias externas**

```python
def test_template_download_with_network_error(mock_requests):
    """Test template download handles network errors gracefully."""
    mock_requests.get.side_effect = requests.ConnectionError("Network unreachable")

    with pytest.raises(TemplateDownloadError, match="Network error"):
        download_template("https://example.com/template.zip")

def test_file_creation_with_permission_error(mock_open):
    """Test file creation handles permission errors."""
    mock_open.side_effect = PermissionError("Permission denied")

    with pytest.raises(FileCreationError, match="Permission denied"):
        create_file(Path("/restricted/file.py"), content="test")
```

## Guía de imports

### Organización de imports

!!! note

    El formateador `isort` organiza los imports automáticamente, así que puedes ordenarlos fácilmente ejecutando `bash scripts/format.sh`.

1. Primero la **librería estándar**
2. Después los imports de **terceros**
3. Por último los imports de la **aplicación local**
4. **Línea en blanco** entre cada grupo

```python
# Librería estándar
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Terceros
import click
import pydantic
import yaml
from fastapi import FastAPI

# Aplicación local
from fastapi_fastkit.commands.base import BaseCommand
from fastapi_fastkit.utils.validation import validate_project_name
from fastapi_fastkit.templates import TemplateManager
```

### Buenas prácticas de imports

- **Evita imports comodín** (`from module import *`)
- **Usa imports absolutos** para mayor claridad
- **Importa módulos, no elementos concretos** cuando importes muchos elementos

```python
# Bien ✅
from fastapi_fastkit.utils import validation, files, formatting

# Bien ✅ (cuando importas pocos elementos)
from fastapi_fastkit.utils.validation import validate_email, validate_project_name

# Mal ❌
from fastapi_fastkit.utils.validation import *

# Mal ❌ (cuando importas muchos elementos)
from fastapi_fastkit.utils.validation import (
    validate_email, validate_project_name, validate_template_name,
    validate_dependencies, validate_python_version, validate_directory
)
```

## Guía de seguridad

### Validación de entrada

Valida y sanitiza siempre la entrada del usuario:

```python
def validate_project_name(name: str) -> str:
    """Validate and sanitize project name."""
    if not name:
        raise ValueError("Project name cannot be empty")

    if not name.isidentifier():
        raise ValueError("Project name must be a valid Python identifier")

    if name.startswith('_'):
        raise ValueError("Project name cannot start with underscore")

    if len(name) > 50:
        raise ValueError("Project name too long (max 50 characters)")

    # Sanitizar eliminando caracteres peligrosos
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)

    return sanitized
```

### Operaciones con archivos

Ten cuidado con rutas y operaciones de archivos:

```python
def create_file_safely(file_path: Path, content: str, base_dir: Path) -> None:
    """Create file safely within base directory."""
    # Resolver para evitar ataques de directory traversal
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    # Asegurar que el archivo está dentro del directorio base
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise SecurityError(f"File path outside base directory: {file_path}")

    # Crear los directorios padres de forma segura
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    # Escribir el archivo con permisos adecuados
    resolved_path.write_text(content, encoding='utf-8')
    resolved_path.chmod(0o644)  # Lectura/escritura para el dueño, lectura para el resto
```

## Guía de rendimiento

### Prácticas de código eficiente

- **Usa generadores** para datasets grandes
- **Evita optimizaciones prematuras**
- **Perfila antes de optimizar**

```python
# Bien ✅ - generador para eficiencia de memoria
def process_large_template(template_files: List[Path]) -> Iterator[ProcessedFile]:
    """Process template files efficiently."""
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        yield ProcessedFile(path=file_path, content=processed_content)

# Mal ❌ - carga todo en memoria
def process_large_template(template_files: List[Path]) -> List[ProcessedFile]:
    """Process template files."""
    results = []
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        results.append(ProcessedFile(path=file_path, content=processed_content))
    return results
```

### Caché

Usa caché para operaciones costosas:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_template_metadata(template_path: Path) -> TemplateMetadata:
    """Get template metadata with caching."""
    config_file = template_path / "template.yaml"

    if not config_file.exists():
        return TemplateMetadata(name=template_path.name)

    config = yaml.safe_load(config_file.read_text())
    return TemplateMetadata.from_config(config)
```

## Guía de commits de Git

### Formato del mensaje de commit

Usa el formato Conventional Commits:

```
type(scope): description

[optional body]

[optional footer]
```

### Tipos de commit

- **feat**: nueva funcionalidad
- **fix**: corrección de bug
- **docs**: cambios de documentación
- **style**: cambios de estilo de código (formateo, etc.)
- **refactor**: refactorización
- **test**: añadir o actualizar pruebas
- **chore**: tareas de mantenimiento

### Ejemplos

```bash
# Bien ✅
feat(cli): add template validation command

Add new command to validate template structure and configuration.
The command checks for required files, validates YAML syntax,
and ensures template follows conventions.

Closes #123

# Bien ✅
fix(templates): handle missing dependency files gracefully

When a template references a requirements file that doesn't exist,
show a clear error message instead of crashing.

# Mal ❌
update stuff

# Mal ❌
Fixed bug
```

## Guía de revisión de código

### Para autores

Antes de enviar código para revisión:

1. **Ejecuta todas las pruebas** y comprueba que pasan
2. **Comprueba que mantienes la cobertura**
3. **Actualiza la documentación** si hace falta
4. **Sigue las convenciones de mensaje de commit**
5. **Mantén los pull requests** enfocados y pequeños

### Para revisores

Al revisar código:

1. **Comprueba la funcionalidad**: ¿hace lo que debe?
2. **Revisa las pruebas**: ¿cubren los casos límite?
3. **Verifica la documentación**: ¿es clara y está al día?
4. **Comprueba el estilo de código**: ¿sigue las convenciones?
5. **Considera la seguridad**: ¿hay vulnerabilidades potenciales?

### Checklist de revisión

- [ ] El código sigue la guía de estilo
- [ ] Las pruebas son completas y pasan
- [ ] La documentación está actualizada
- [ ] No hay vulnerabilidades de seguridad
- [ ] Se han considerado los aspectos de rendimiento
- [ ] El manejo de errores es adecuado
- [ ] Los mensajes de commit siguen las convenciones

## Herramientas y automatización

### Hooks de pre-commit

Usamos pre-commit hooks para aplicar los estándares:

```yaml
# .pre-commit-config.yaml
repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-toml

-   repo: local
    hooks:
    -   id: format
        name: format
        entry: black --config pyproject.toml --check .
        language: python
        types: [python]
        additional_dependencies: ['black>=24.10.0']
        pass_filenames: false

    -   id: isort-check
        name: isort check
        entry: isort --sp pyproject.toml --check-only --diff .
        language: python
        types: [python]
        additional_dependencies: ['isort>=5.13.2']
        pass_filenames: false

    -   id: isort-fix
        name: isort fix
        entry: isort --sp pyproject.toml .
        language: python
        types: [python]
        additional_dependencies: ['isort>=5.13.2']
        pass_filenames: false

    -   id: black-fix
        name: black fix
        entry: black --config pyproject.toml .
        language: python
        types: [python]
        additional_dependencies: ['black>=24.10.0']
        pass_filenames: false

    -   id: mypy
        name: mypy
        entry: mypy --config-file pyproject.toml src
        language: python
        types: [python]
        additional_dependencies:
          - mypy>=1.12.0
          - rich>=13.9.2
          - click>=8.1.7
          - pyyaml>=6.0.0
          - types-PyYAML>=6.0.12
        pass_filenames: false

ci:
    autofix_commit_msg: 🎨 [pre-commit.ci] Auto format from pre-commit.com hooks
    autoupdate_commit_msg: ⬆ [pre-commit.ci] pre-commit autoupdate
```

!!! note

    Los hooks de pre-commit usan entornos Python aislados (`language: python`).

### Configuración del IDE

Configuración recomendada para VS Code:

```json
{
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.path": "isort",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

## Próximos pasos

Tras revisar esta guía:

1. **Configura el entorno de desarrollo** siguiendo [Configuración de desarrollo](development-setup.md)
2. **Practica con contribuciones pequeñas** para familiarizarte
3. **Pregunta** en GitHub Discussions si algo no está claro
4. **Revisa el código existente** para ver estas convenciones en acción

!!! tip "Referencia rápida"
    - Usa `make check-all` para comprobar que tu código cumple todas las convenciones
    - Configura los pre-commit hooks para detectar problemas pronto
    - Si tienes dudas, mira el código existente como ejemplo
    - No dudes en pedir ayuda en las revisiones de código

¡Seguir esta guía ayuda a mantener la alta calidad del código de FastAPI-fastkit y facilita la colaboración para todos! 🚀

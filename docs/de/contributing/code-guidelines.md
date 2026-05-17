# Code-Richtlinien

Umfassende Coding-Standards und Best Practices für Beiträge zu FastAPI-fastkit.

## Überblick

Diese Richtlinien sorgen für Code-Qualität, Konsistenz und Wartbarkeit im gesamten FastAPI-fastkit-Projekt. Wenn Sie ihnen folgen, entsteht eine Codebasis, die leicht zu lesen, zu pflegen und zu erweitern ist.

## Python-Codestil

### PEP-8-Konformität

Folgen Sie [PEP 8](https://www.python.org/dev/peps/pep-0008/) mit diesen spezifischen Einstellungen:

- **Zeilenlänge**: 88 Zeichen (Black-Standard)
- **Einrückung**: 4 Leerzeichen (keine Tabs)
- **Nachgestellte Kommas**: in mehrzeiligen Strukturen erforderlich
- **Anführungszeichen**: doppelte Anführungszeichen bevorzugt

### Code-Formatierung

Wir verwenden **Black** für automatische Code-Formatierung:

```python
# Gut ✅
def create_project(
    name: str,
    template: str,
    options: Dict[str, Any],
) -> ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name, template=template)

# Nicht gut ❌
def create_project(name: str, template: str, options: Dict[str,Any])->ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name,template=template)
```

### Import-Organisation

Verwenden Sie **isort**, um Imports zu organisieren:

```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

# Third-party imports
import click
import pydantic
from fastapi import FastAPI

# Local imports
from fastapi_fastkit.commands import BaseCommand
from fastapi_fastkit.utils import validation
from fastapi_fastkit.templates.manager import TemplateManager
```

## Type Hints

### Erforderliche Type Hints

Alle öffentlichen Funktionen und Methoden müssen Type Hints enthalten:

```python
# Gut ✅
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
        # Implementation...
        created_files.append(file_path)
    return created_files

# Nicht gut ❌
def validate_project_name(name):
    return name.isidentifier() and not name.startswith('_')
```

### Komplexe Type-Annotationen

Verwenden Sie passende Annotationen für komplexe Strukturen:

```python
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path

# Type aliases for complex types
ProjectConfig = Dict[str, Union[str, bool, List[str]]]
FileMapping = Dict[Path, str]
ValidationResult = Tuple[bool, Optional[str]]

def process_template(
    template_path: Path,
    config: ProjectConfig,
    output_dir: Optional[Path] = None,
) -> ValidationResult:
    """Process template with configuration."""
    # Implementation...
    return True, None
```

## Namenskonventionen

### Variablen und Funktionen

- **snake_case** für Variablen und Funktionen
- **Aussagekräftige Namen**, die den Zweck erklären
- **Abkürzungen vermeiden**, sofern nicht gängig

```python
# Gut ✅
project_name = "my-api"
template_directory = Path("templates")
user_input_data = get_user_input()

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    return "@" in email and "." in email

# Nicht gut ❌
proj_nm = "my-api"
temp_dir = Path("templates")
usr_data = get_input()

def validate_email(e):
    return "@" in e and "." in e
```

### Klassen

- **PascalCase** für Klassennamen
- **Beschreibende und spezifische** Namen

```python
# Gut ✅
class SomeClass:
    """Represents example class of FastAPI-fastkit."""
    pass

class SomeClassValidationError(Exception):
    """Raised when example class validation fails."""
    pass

class UserInputHandler:
    """Handles user input validation and processing."""
    pass

# Nicht gut ❌
class Class:
    pass

class Error(Exception):
    pass

class Handler:
    pass
```

### Konstanten

- **UPPER_CASE** mit Unterstrichen
- Konstanten **nur auf Modul-Ebene**

```python
# Gut ✅
DEFAULT_TEMPLATE_NAME = "fastapi-default"
MAX_PROJECT_NAME_LENGTH = 50
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# Nicht gut ❌
default_template = "fastapi-default"
maxLength = 50
versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

## Dokumentations-Standards

### Docstrings

Verwenden Sie **Google-Style-Docstrings** für alle öffentlichen APIs:

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
    # Implementation here...
    pass
```

### Kommentare

- **WARUM erklären, nicht WAS**
- **Sparsam einsetzen** — Code sollte selbsterklärend sein
- **Kommentare aktualisieren**, wenn sich Code ändert

```python
# Gut ✅
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # Skip validation in development mode to allow experimental packages
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # Check each requirement against known security vulnerabilities
    for requirement in requirements:
        if is_vulnerable_package(requirement):
            return False

    return True

# Nicht gut ❌
def validate_dependencies(requirements: List[str]) -> bool:
    """Validate project dependencies."""
    # Check if dev mode
    if os.getenv("FASTKIT_DEV_MODE"):
        return True

    # Loop through requirements
    for requirement in requirements:
        # Check if vulnerable
        if is_vulnerable_package(requirement):
            return False

    # Return true
    return True
```

## Fehlerbehandlung

### Behandlung von Exceptions

- **Spezifische Exceptions** soweit möglich abfangen
- **Aussagekräftige Fehlermeldungen** liefern
- **Fehler angemessen loggen**

```python
# Gut ✅
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

# Nicht gut ❌
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config: {e}")
```

### Benutzerdefinierte Exceptions

Definieren Sie spezifische Exceptions für unterschiedliche Fehlerbedingungen:

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

## Test-Standards

### Teststruktur

Organisieren Sie Tests mit klarer Struktur und klarer Benennung:

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

### Testabdeckung

- **Streben Sie 90 %+ Abdeckung** bei neuem Code an
- **Grenzfälle und Fehlerbedingungen** testen
- **Externe Abhängigkeiten mocken**

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

## Import-Richtlinien

### Import-Organisation

!!! note

    `isort` ordnet Imports automatisch — Sie können Imports einfach mit `bash scripts/format.sh` ordnen.

1. **Standardbibliothek** zuerst
2. **Drittanbieter** als Zweites
3. **Lokale Anwendung** zuletzt
4. **Leerzeile** zwischen jeder Gruppe

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Third-party
import click
import pydantic
import yaml
from fastapi import FastAPI

# Local application
from fastapi_fastkit.commands.base import BaseCommand
from fastapi_fastkit.utils.validation import validate_project_name
from fastapi_fastkit.templates import TemplateManager
```

### Best Practices für Imports

- **Wildcard-Imports vermeiden** (`from module import *`)
- **Absolute Imports** für Klarheit verwenden
- **Module importieren, nicht einzelne Symbole**, wenn Sie viele Symbole brauchen

```python
# Gut ✅
from fastapi_fastkit.utils import validation, files, formatting

# Gut ✅ (wenn nur wenige Elemente importiert werden)
from fastapi_fastkit.utils.validation import validate_email, validate_project_name

# Nicht gut ❌
from fastapi_fastkit.utils.validation import *

# Nicht gut ❌ (wenn viele Elemente importiert werden)
from fastapi_fastkit.utils.validation import (
    validate_email, validate_project_name, validate_template_name,
    validate_dependencies, validate_python_version, validate_directory
)
```

## Sicherheitsrichtlinien

### Eingabevalidierung

Nutzereingaben immer validieren und säubern:

```python
def validate_project_name(name: str) -> str:
    """Projektname validieren und bereinigen."""
    if not name:
        raise ValueError("Project name cannot be empty")

    if not name.isidentifier():
        raise ValueError("Project name must be a valid Python identifier")

    if name.startswith('_'):
        raise ValueError("Project name cannot start with underscore")

    if len(name) > 50:
        raise ValueError("Project name too long (max 50 characters)")

    # Potenziell problematische Zeichen entfernen
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)

    return sanitized
```

### Dateioperationen

Seien Sie vorsichtig mit Dateipfaden und -operationen:

```python
def create_file_safely(file_path: Path, content: str, base_dir: Path) -> None:
    """Datei sicher innerhalb des Basisverzeichnisses anlegen."""
    # Pfad auflösen, um Directory-Traversal-Angriffe zu verhindern
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    # Sicherstellen, dass die Datei innerhalb des Basisverzeichnisses liegt
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise SecurityError(f"File path outside base directory: {file_path}")

    # Übergeordnete Verzeichnisse sicher anlegen
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    # Datei mit passenden Berechtigungen schreiben
    resolved_path.write_text(content, encoding='utf-8')
    resolved_path.chmod(0o644)  # Besitzer: lesen/schreiben, andere: nur lesen
```

## Performance-Richtlinien

### Effiziente Code-Praktiken

- **Generatoren** für große Datenmengen verwenden
- **Vorzeitige Optimierung vermeiden**
- **Vor dem Optimieren profilen**

```python
# Gut ✅ - Generator spart Arbeitsspeicher
def process_large_template(template_files: List[Path]) -> Iterator[ProcessedFile]:
    """Vorlagendateien effizient verarbeiten."""
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        yield ProcessedFile(path=file_path, content=processed_content)

# Nicht gut ❌ - lädt alles in den Arbeitsspeicher
def process_large_template(template_files: List[Path]) -> List[ProcessedFile]:
    """Vorlagendateien verarbeiten."""
    results = []
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        results.append(ProcessedFile(path=file_path, content=processed_content))
    return results
```

### Caching

Cache für teure Operationen nutzen:

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

## Git-Commit-Richtlinien

### Format der Commit-Nachricht

Verwenden Sie das Conventional-Commit-Format:

```
type(scope): description

[optional body]

[optional footer]
```

### Commit-Typen

- **feat**: neue Funktion
- **fix**: Fehlerbehebung
- **docs**: Dokumentationsänderungen
- **style**: Code-Stil-Änderungen (Formatierung usw.)
- **refactor**: Refactoring
- **test**: Tests hinzufügen oder aktualisieren
- **chore**: Wartungsarbeiten

### Beispiele

```bash
# Gut ✅
feat(cli): add template validation command

Add new command to validate template structure and configuration.
The command checks for required files, validates YAML syntax,
and ensures template follows conventions.

Closes #123

# Gut ✅
fix(templates): handle missing dependency files gracefully

When a template references a requirements file that doesn't exist,
show a clear error message instead of crashing.

# Nicht gut ❌
update stuff

# Nicht gut ❌
Fixed bug
```

## Code-Review-Richtlinien

### Für Autoren

Vor dem Einreichen zur Review:

1. **Alle Tests ausführen** und sicherstellen, dass sie bestehen
2. **Code-Abdeckung prüfen**, damit sie erhalten bleibt
3. **Dokumentation aktualisieren**, falls nötig
4. **Commit-Konventionen befolgen**
5. **Pull-Requests** fokussiert und klein halten

### Für Reviewer

Beim Review:

1. **Funktionsfähigkeit prüfen** — funktioniert es wie beabsichtigt?
2. **Tests überprüfen** — sind Grenzfälle abgedeckt?
3. **Dokumentation verifizieren** — klar und aktuell?
4. **Codestil prüfen** — folgt er den Projekt-Konventionen?
5. **Sicherheit beachten** — potenzielle Schwachstellen?

### Review-Checkliste

- [ ] Code folgt den Style-Richtlinien
- [ ] Tests sind umfassend und bestehen
- [ ] Dokumentation ist aktuell
- [ ] Keine Sicherheitslücken
- [ ] Performance-Überlegungen berücksichtigt
- [ ] Fehlerbehandlung ist angemessen
- [ ] Commit-Nachrichten folgen den Konventionen

## Werkzeuge und Automatisierung

### Pre-Commit-Hooks

Wir nutzen Pre-Commit-Hooks zur Durchsetzung der Standards:

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

    Pre-Commit-Hooks verwenden isolierte Python-Umgebungen (`language: python`).

### IDE-Konfiguration

Empfohlene VS-Code-Einstellungen:

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

## Nächste Schritte

Nachdem Sie diese Richtlinien gelesen haben:

1. **Entwicklungsumgebung einrichten** gemäß [Entwicklungsumgebung einrichten](development-setup.md)
2. **Mit kleinen Beiträgen üben**, um sich vertraut zu machen
3. **Fragen stellen** in GitHub Discussions, falls etwas unklar ist
4. **Vorhandenen Code lesen**, um diese Richtlinien in der Praxis zu sehen

!!! tip "Schnelle Referenz"
    - Verwenden Sie `make check-all`, um zu prüfen, ob Ihr Code allen Richtlinien folgt
    - Richten Sie Pre-Commit-Hooks ein, um Probleme früh zu erkennen
    - Im Zweifel: Beispiele im bestehenden Code anschauen
    - Zögern Sie nicht, in Code-Reviews um Hilfe zu bitten

Diese Richtlinien zu befolgen hilft, die hohe Code-Qualität von FastAPI-fastkit zu erhalten und macht die Zusammenarbeit für alle einfacher! 🚀

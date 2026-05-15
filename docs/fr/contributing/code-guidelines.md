# Directives de code

Standards de codage et bonnes pratiques complets pour contribuer à FastAPI-fastkit.

## Vue d'ensemble

Ces directives garantissent la qualité, la cohérence et la maintenabilité du code dans l'ensemble du projet FastAPI-fastkit. Suivre ces standards aide à créer une base de code facile à lire, à maintenir et à étendre.

## Style de code Python

### Conformité PEP 8

Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/) avec ces configurations spécifiques :

- **Longueur de ligne** : 88 caractères (par défaut de Black)
- **Indentation** : 4 espaces (pas de tabulations)
- **Virgules finales** : requises dans les structures multi-lignes
- **Guillemets** : guillemets doubles préférés

### Mise en forme du code

Nous utilisons **Black** pour la mise en forme automatique du code :

```python
# Bon ✅
def create_project(
    name: str,
    template: str,
    options: Dict[str, Any],
) -> ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name, template=template)

# À éviter ❌
def create_project(name: str, template: str, options: Dict[str,Any])->ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name,template=template)
```

### Organisation des imports

Utilisez **isort** pour organiser les imports :

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

## Annotations de type

### Annotations de type requises

Toutes les fonctions et méthodes publiques doivent inclure des annotations de type :

```python
# Bon ✅
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

# À éviter ❌
def validate_project_name(name):
    return name.isidentifier() and not name.startswith('_')
```

### Annotations de type complexes

Utilisez les annotations de type appropriées pour les structures complexes :

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

## Conventions de nommage

### Variables et fonctions

- **snake_case** pour les variables et les fonctions
- **Noms explicites** qui décrivent l'usage
- **Évitez les abréviations** sauf si elles sont largement comprises

```python
# Bon ✅
project_name = "my-api"
template_directory = Path("templates")
user_input_data = get_user_input()

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    return "@" in email and "." in email

# À éviter ❌
proj_nm = "my-api"
temp_dir = Path("templates")
usr_data = get_input()

def validate_email(e):
    return "@" in e and "." in e
```

### Classes

- **PascalCase** pour les noms de classes
- Noms **explicites et précis**

```python
# Bon ✅
class SomeClass:
    """Represents example class of FastAPI-fastkit."""
    pass

class SomeClassValidationError(Exception):
    """Raised when example class validation fails."""
    pass

class UserInputHandler:
    """Handles user input validation and processing."""
    pass

# À éviter ❌
class Class:
    pass

class Error(Exception):
    pass

class Handler:
    pass
```

### Constantes

- **UPPER_CASE** avec des underscores
- Constantes **au niveau du module** uniquement

```python
# Bon ✅
DEFAULT_TEMPLATE_NAME = "fastapi-default"
MAX_PROJECT_NAME_LENGTH = 50
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# À éviter ❌
default_template = "fastapi-default"
maxLength = 50
versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

## Standards de documentation

### Docstrings

Utilisez les **docstrings de style Google** pour toutes les API publiques :

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

### Commentaires

- **Expliquez le POURQUOI, pas le QUOI**
- **Utilisez-les avec parcimonie** — le code doit s'auto-documenter
- **Mettez à jour les commentaires** quand le code change

```python
# Bon ✅
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

# À éviter ❌
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

## Gestion des erreurs

### Gestion des exceptions

- **Attrapez des exceptions précises** autant que possible
- **Fournissez des messages d'erreur explicites**
- **Journalisez les erreurs de manière appropriée**

```python
# Bon ✅
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

# À éviter ❌
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config: {e}")
```

### Exceptions personnalisées

Définissez des exceptions précises pour différentes conditions d'erreur :

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

## Standards de tests

### Structure des tests

Organisez les tests avec une structure et un nommage clairs :

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

### Couverture des tests

- **Visez 90 %+ de couverture** sur le code nouveau
- **Testez les cas limites** et les conditions d'erreur
- **Simulez les dépendances externes**

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

## Directives sur les imports

### Organisation des imports

!!! note

    Le formateur `isort` organise automatiquement les imports : vous pouvez donc les organiser facilement en lançant `bash scripts/format.sh`.

1. Imports de la **bibliothèque standard** en premier
2. Imports **tiers** en deuxième
3. Imports de l'**application du projet** en dernier
4. **Ligne vide** entre chaque groupe

```python
# Bibliothèque standard
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Bibliothèques tierces
import click
import pydantic
import yaml
from fastapi import FastAPI

# Application du projet
from fastapi_fastkit.commands.base import BaseCommand
from fastapi_fastkit.utils.validation import validate_project_name
from fastapi_fastkit.templates import TemplateManager
```

### Bonnes pratiques d'imports

- **Évitez les imports avec joker** (`from module import *`)
- **Utilisez les imports absolus** pour plus de clarté
- **Importez les modules, pas des éléments précis** quand vous importez beaucoup d'éléments

```python
# Bon ✅
from fastapi_fastkit.utils import validation, files, formatting

# Bon ✅ (quand vous importez peu d'éléments)
from fastapi_fastkit.utils.validation import validate_email, validate_project_name

# À éviter ❌
from fastapi_fastkit.utils.validation import *

# À éviter ❌ (quand vous importez beaucoup d'éléments)
from fastapi_fastkit.utils.validation import (
    validate_email, validate_project_name, validate_template_name,
    validate_dependencies, validate_python_version, validate_directory
)
```

## Directives de sécurité

### Validation des entrées

Validez et assainissez toujours les entrées utilisateur :

```python
def validate_project_name(name: str) -> str:
    """Valider et assainir le nom du projet."""
    if not name:
        raise ValueError("Project name cannot be empty")

    if not name.isidentifier():
        raise ValueError("Project name must be a valid Python identifier")

    if name.startswith('_'):
        raise ValueError("Project name cannot start with underscore")

    if len(name) > 50:
        raise ValueError("Project name too long (max 50 characters)")

    # Assainir en supprimant les caractères dangereux
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)

    return sanitized
```

### Opérations sur les fichiers

Soyez prudent avec les chemins et les opérations sur les fichiers :

```python
def create_file_safely(file_path: Path, content: str, base_dir: Path) -> None:
    """Créer un fichier de manière sûre dans le répertoire de base."""
    # Résoudre le chemin pour éviter les attaques de traversée de répertoires
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    # Vérifier que le fichier reste dans le répertoire de base
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise SecurityError(f"File path outside base directory: {file_path}")

    # Créer les répertoires parents en toute sécurité
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    # Écrire le fichier avec des permissions appropriées
    resolved_path.write_text(content, encoding='utf-8')
    resolved_path.chmod(0o644)  # Lecture/écriture pour le propriétaire, lecture pour les autres
```

## Directives de performance

### Pratiques de code efficaces

- **Utilisez des générateurs** pour les grands jeux de données
- **Évitez l'optimisation prématurée**
- **Profilez avant d'optimiser**

```python
# Bon ✅ - Générateur plus économe en mémoire
def process_large_template(template_files: List[Path]) -> Iterator[ProcessedFile]:
    """Process template files efficiently."""
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        yield ProcessedFile(path=file_path, content=processed_content)

# À éviter ❌ - Charge tout en mémoire
def process_large_template(template_files: List[Path]) -> List[ProcessedFile]:
    """Process template files."""
    results = []
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        results.append(ProcessedFile(path=file_path, content=processed_content))
    return results
```

### Mise en cache

Utilisez la mise en cache pour les opérations coûteuses :

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

## Directives sur les commits Git

### Format de message de commit

Utilisez le format de commit conventionnel :

```
type(scope): description

[optional body]

[optional footer]
```

### Types de commits

- **feat** : nouvelle fonctionnalité
- **fix** : correction de bogue
- **docs** : changements de documentation
- **style** : changements de style de code (mise en forme, etc.)
- **refactor** : refactoring de code
- **test** : ajout ou mise à jour de tests
- **chore** : tâches de maintenance

### Exemples

```bash
# Bon ✅
feat(cli): add template validation command

Add new command to validate template structure and configuration.
The command checks for required files, validates YAML syntax,
and ensures template follows conventions.

Closes #123

# Bon ✅
fix(templates): handle missing dependency files gracefully

When a template references a requirements file that doesn't exist,
show a clear error message instead of crashing.

# À éviter ❌
update stuff

# À éviter ❌
Fixed bug
```

## Directives de relecture de code

### Pour les auteurs

Avant de soumettre du code à la relecture :

1. **Lancez tous les tests** et assurez-vous qu'ils passent
2. **Vérifiez que la couverture de code** est maintenue
3. **Mettez à jour la documentation** si nécessaire
4. **Suivez les conventions** de messages de commit
5. **Gardez les pull requests** ciblées et petites

### Pour les relecteurs

Lorsque vous relisez du code :

1. **Vérifiez le fonctionnement** — est-ce que ça marche comme prévu ?
2. **Relisez les tests** — les cas limites sont-ils couverts ?
3. **Vérifiez la documentation** — est-elle claire et à jour ?
4. **Vérifiez le style de code** — respecte-t-il les conventions du projet ?
5. **Pensez à la sécurité** — vulnérabilités potentielles ?

### Liste de vérification de relecture

- [ ] Le code respecte les directives de style
- [ ] Les tests sont complets et passent
- [ ] La documentation est à jour
- [ ] Aucune vulnérabilité de sécurité
- [ ] Les considérations de performance sont prises en compte
- [ ] La gestion des erreurs est appropriée
- [ ] Les messages de commit respectent les conventions

## Outils et automatisation

### Hooks pre-commit

Nous utilisons les hooks pre-commit pour faire respecter les standards :

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

    Les hooks pre-commit utilisent des environnements Python isolés (`language: python`).

### Configuration de l'IDE

Paramètres VS Code recommandés :

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

## Étapes suivantes

Après avoir parcouru ces directives :

1. **Mettez en place l'environnement de développement** en suivant [Configuration du développement](development-setup.md)
2. **Pratiquez avec de petites contributions** pour vous familiariser
3. **Posez des questions** dans GitHub Discussions si quelque chose n'est pas clair
4. **Relisez le code existant** pour voir ces directives en pratique

!!! tip "Référence rapide"
    - Utilisez `make check-all` pour vérifier que votre code respecte toutes les directives
    - Configurez les hooks pre-commit pour détecter les problèmes tôt
    - En cas de doute, regardez le code existant pour des exemples
    - N'hésitez pas à demander de l'aide lors des relectures de code

Suivre ces directives aide à maintenir la haute qualité de code de FastAPI-fastkit et facilite la collaboration pour tous ! 🚀

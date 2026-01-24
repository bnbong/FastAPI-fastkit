# Code Guidelines

Comprehensive coding standards and best practices for contributing to FastAPI-fastkit.

## Overview

These guidelines ensure code quality, consistency, and maintainability across the FastAPI-fastkit project. Following these standards helps create a codebase that is easy to read, maintain, and extend.

## Python Code Style

### PEP 8 Compliance

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specific configurations:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)
- **Trailing commas**: Required in multi-line structures
- **String quotes**: Double quotes preferred

### Code Formatting

We use **Black** for automatic code formatting:

```python
# Good ✅
def create_project(
    name: str,
    template: str,
    options: Dict[str, Any],
) -> ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name, template=template)

# Bad ❌
def create_project(name: str, template: str, options: Dict[str,Any])->ProjectResult:
    """Create a new FastAPI project."""
    return ProjectResult(name=name,template=template)
```

### Import Organization

Use **isort** to organize imports:

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

## Type Hinting

### Required Type Hints

All public functions and methods must include type hints:

```python
# Good ✅
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

# Bad ❌
def validate_project_name(name):
    return name.isidentifier() and not name.startswith('_')
```

### Complex Type Annotations

Use proper type annotations for complex structures:

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

## Naming Conventions

### Variables and Functions

- **snake_case** for variables and functions
- **Descriptive names** that explain purpose
- **Avoid abbreviations** unless commonly understood

```python
# Good ✅
project_name = "my-api"
template_directory = Path("templates")
user_input_data = get_user_input()

def validate_email_address(email: str) -> bool:
    """Validate email address format."""
    return "@" in email and "." in email

# Bad ❌
proj_nm = "my-api"
temp_dir = Path("templates")
usr_data = get_input()

def validate_email(e):
    return "@" in e and "." in e
```

### Classes

- **PascalCase** for class names
- **Descriptive and specific** names

```python
# Good ✅
class ProjectTemplate:
    """Represents a FastAPI project template."""
    pass

class TemplateValidationError(Exception):
    """Raised when template validation fails."""
    pass

class UserInputHandler:
    """Handles user input validation and processing."""
    pass

# Bad ❌
class Template:
    pass

class Error(Exception):
    pass

class Handler:
    pass
```

### Constants

- **UPPER_CASE** with underscores
- **Module-level** constants only

```python
# Good ✅
DEFAULT_TEMPLATE_NAME = "fastapi-default"
MAX_PROJECT_NAME_LENGTH = 50
SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12"]

# Bad ❌
default_template = "fastapi-default"
maxLength = 50
versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

## Documentation Standards

### Docstrings

Use **Google-style docstrings** for all public APIs:

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

### Comments

- **Explain WHY, not WHAT**
- **Use sparingly** - code should be self-documenting
- **Update comments** when code changes

```python
# Good ✅
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

# Bad ❌
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

## Error Handling

### Exception Handling

- **Catch specific exceptions** whenever possible
- **Provide meaningful error messages**
- **Log errors appropriately**

```python
# Good ✅
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

# Bad ❌
def load_template_config(template_path: Path) -> Dict[str, Any]:
    """Load template configuration from file."""
    config_file = template_path / "template.yaml"

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"Error loading config: {e}")
```

### Custom Exceptions

Define specific exceptions for different error conditions:

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

## Testing Standards

### Test Structure

Organize tests with clear structure and naming:

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

### Test Coverage

- **Aim for 90%+ coverage** on new code
- **Test edge cases** and error conditions
- **Mock external dependencies**

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

## Import Guidelines

### Import Organization

1. **Standard library** imports first
2. **Third-party** imports second
3. **Local application** imports last
4. **Blank line** between each group

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

### Import Best Practices

- **Avoid wildcard imports** (`from module import *`)
- **Use absolute imports** for clarity
- **Import modules, not specific items** when importing many items

```python
# Good ✅
from fastapi_fastkit.utils import validation, files, formatting

# Good ✅ (when importing few items)
from fastapi_fastkit.utils.validation import validate_email, validate_project_name

# Bad ❌
from fastapi_fastkit.utils.validation import *

# Bad ❌ (when importing many items)
from fastapi_fastkit.utils.validation import (
    validate_email, validate_project_name, validate_template_name,
    validate_dependencies, validate_python_version, validate_directory
)
```

## Security Guidelines

### Input Validation

Always validate and sanitize user input:

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

    # Sanitize by removing dangerous characters
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', name)

    return sanitized
```

### File Operations

Be careful with file paths and operations:

```python
def create_file_safely(file_path: Path, content: str, base_dir: Path) -> None:
    """Create file safely within base directory."""
    # Resolve to prevent directory traversal attacks
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    # Ensure file is within base directory
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise SecurityError(f"File path outside base directory: {file_path}")

    # Create parent directories safely
    resolved_path.parent.mkdir(parents=True, exist_ok=True)

    # Write file with appropriate permissions
    resolved_path.write_text(content, encoding='utf-8')
    resolved_path.chmod(0o644)  # Read/write for owner, read for others
```

## Performance Guidelines

### Efficient Code Practices

- **Use generators** for large datasets
- **Avoid premature optimization**
- **Profile before optimizing**

```python
# Good ✅ - Generator for memory efficiency
def process_large_template(template_files: List[Path]) -> Iterator[ProcessedFile]:
    """Process template files efficiently."""
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        yield ProcessedFile(path=file_path, content=processed_content)

# Bad ❌ - Loads everything into memory
def process_large_template(template_files: List[Path]) -> List[ProcessedFile]:
    """Process template files."""
    results = []
    for file_path in template_files:
        content = file_path.read_text()
        processed_content = process_template_content(content)
        results.append(ProcessedFile(path=file_path, content=processed_content))
    return results
```

### Caching

Use caching for expensive operations:

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

## Git Commit Guidelines

### Commit Message Format

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

### Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
# Good ✅
feat(cli): add template validation command

Add new command to validate template structure and configuration.
The command checks for required files, validates YAML syntax,
and ensures template follows conventions.

Closes #123

# Good ✅
fix(templates): handle missing dependency files gracefully

When a template references a requirements file that doesn't exist,
show a clear error message instead of crashing.

# Bad ❌
update stuff

# Bad ❌
Fixed bug
```

## Code Review Guidelines

### For Authors

Before submitting code for review:

1. **Run all tests** and ensure they pass
2. **Check code coverage** is maintained
3. **Update documentation** if needed
4. **Follow commit message** conventions
5. **Keep pull requests** focused and small

### For Reviewers

When reviewing code:

1. **Check functionality** - does it work as intended?
2. **Review tests** - are edge cases covered?
3. **Verify documentation** - is it clear and up-to-date?
4. **Check code style** - follows project conventions?
5. **Consider security** - any potential vulnerabilities?

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance considerations addressed
- [ ] Error handling is appropriate
- [ ] Commit messages follow conventions

## Tools and Automation

### Pre-commit Hooks

We use pre-commit hooks to enforce standards:

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

> **Note:** Pre-commit hooks use isolated Python environments (`language: python`).

### IDE Configuration

Recommended VS Code settings:

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

## Next Steps

After reviewing these guidelines:

1. **Set up development environment** following [Development Setup](development-setup.md)
2. **Practice with small contributions** to familiarize yourself
3. **Ask questions** in GitHub Discussions if anything is unclear
4. **Review existing code** to see these guidelines in practice

!!! tip "Quick Reference"
    - Use `make check-all` to verify your code follows all guidelines
    - Set up pre-commit hooks to catch issues early
    - When in doubt, look at existing code for examples
    - Don't hesitate to ask for help in code reviews

Following these guidelines helps maintain FastAPI-fastkit's high code quality and makes collaboration easier for everyone! 🚀

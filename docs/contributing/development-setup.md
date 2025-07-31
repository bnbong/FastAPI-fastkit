# Development Setup

A comprehensive guide for setting up a development environment to contribute to FastAPI-fastkit.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.12 or higher** installed
- **Git** installed and configured
- **Basic knowledge** of Python and FastAPI
- **Text editor or IDE** (VS Code, PyCharm, etc.)

## Quick Setup with Makefile

FastAPI-fastkit provides a Makefile for easy development setup:

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

This single command:
- Creates a virtual environment
- Installs all dependencies
- Sets up pre-commit hooks
- Configures development tools

## Manual Setup

If you prefer manual setup or the Makefile doesn't work on your system:

### 1. Clone the Repository

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
```

</div>

### 2. Create Virtual Environment

<div class="termy">

```console
$ python -m venv .venv
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

</div>

### 3. Install Dependencies

<div class="termy">

```console
# Install package in editable mode with development dependencies
$ pip install -e ".[dev]"

# Or install from requirements files
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

</div>

### 4. Set Up Pre-commit Hooks

<div class="termy">

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

</div>

### 5. Verify Installation

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0-dev

$ python -m pytest tests/
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
tests/test_templates.py::test_template_listing PASSED
...
======================== 45 passed in 2.34s ========================
```

</div>

## Development Tools

The development environment includes several tools to maintain code quality:

### Code Formatting

**Black** - Code formatter:

<div class="termy">

```console
$ black src/ tests/
reformatted src/main.py
reformatted tests/test_cli.py
All done! ✨ 🍰 ✨
```

</div>

**isort** - Import sorter:

<div class="termy">

```console
$ isort src/ tests/
Fixing import order in src/main.py
```

</div>

### Code Linting

**flake8** - Style guide enforcement:

<div class="termy">

```console
$ flake8 src/ tests/
src/main.py:45:80: E501 line too long (82 > 79 characters)
```

</div>

**mypy** - Type checking:

<div class="termy">

```console
$ mypy src/
Success: no issues found in 12 source files
```

</div>

## Available Make Commands

The project Makefile provides convenient commands for common development tasks:

### Setup Commands

| Command | Description |
|---------|-------------|
| `make install` | Install package in production mode |
| `make install-dev` | Install package with development dependencies |
| `make clean` | Clean build artifacts and cache files |

### Code Quality Commands

| Command | Description |
|---------|-------------|
| `make format` | Format code with black and isort |
| `make lint` | Run flake8 linting |
| `make type-check` | Run mypy type checking |
| `make security` | Run bandit security checks |
| `make check-all` | Run all quality checks |

### Testing Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-unit` | Run unit tests only |
| `make test-integration` | Run integration tests only |
| `make test-coverage` | Run tests with coverage report |
| `make test-watch` | Run tests in watch mode |

### Documentation Commands

| Command | Description |
|---------|-------------|
| `make docs-serve` | Serve documentation locally |
| `make docs-build` | Build documentation |
| `make docs-deploy` | Deploy documentation to GitHub Pages |

### Examples

<div class="termy">

```console
# Format code and run all checks
$ make format lint type-check security
Running black...
Running isort...
Running flake8...
Running mypy...
Running bandit...
✅ All checks passed!

# Run tests with coverage
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
```

</div>

## Project Structure

Understanding the project structure is crucial for development:

```
FastAPI-fastkit/
├── src/
│   └── fastapi_fastkit/
│       ├── __init__.py
│       ├── cli.py                  # CLI command implementations
│       │   ├── __init__.py
│       │   ├── init.py            # Project initialization
│       │   ├── addroute.py        # Route addition
│       │   ├── startdemo.py       # Template demos
│       │   └── runserver.py       # Development server
│       ├── templates/             # Project templates
│       │   ├── __init__.py
│       │   └── manager.py         # Template management
│       ├── utils/                 # Utility functions
│       │   ├── __init__.py
│       │   ├── files.py           # File operations
│       │   ├── validation.py      # Input validation
│       │   └── formatting.py      # Output formatting
│       └── fastapi_project_template/  # Default template
│           ├── src/
│           ├── tests/
│           └── requirements.txt
├── tests/
│   ├── __init__.py
│   ├── test_cli.py               # CLI testing
│   ├── test_commands/            # Command-specific tests
│   ├── test_templates/           # Template testing
│   ├── test_utils/               # Utility testing
│   └── conftest.py               # Test configuration
├── docs/                         # Documentation
├── scripts/                      # Development scripts
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package configuration
├── Makefile                      # Development commands
├── .pre-commit-config.yaml       # Pre-commit configuration
├── pyproject.toml               # Project metadata
└── README.md
```

### Key Directories

**`src/fastapi_fastkit/`** - Main package source code
- **`cli.py`** - Main CLI entry point
- **`commands/`** - Individual command implementations
- **`templates/`** - Template management system
- **`utils/`** - Shared utility functions

**`tests/`** - Test suite
- **`test_cli.py`** - CLI integration tests
- **`test_commands/`** - Command-specific unit tests
- **`test_templates/`** - Template system tests

**`docs/`** - Documentation (MkDocs)
- User guides, tutorials, and API reference

## Development Workflow

### 1. Create a Feature Branch

<div class="termy">

```console
$ git checkout -b feature/add-new-template
Switched to a new branch 'feature/add-new-template'
```

</div>

### 2. Make Changes

Edit code, add features, fix bugs...

### 3. Run Tests and Checks

<div class="termy">

```console
$ make check-all test
Running all quality checks...
Running all tests...
✅ All checks and tests passed!
```

</div>

### 4. Commit Changes

Pre-commit hooks will automatically run:

<div class="termy">

```console
$ git add .
$ git commit -m "Add new FastAPI template with authentication"
black....................................................................Passed
isort....................................................................Passed
flake8...................................................................Passed
mypy.....................................................................Passed
bandit...................................................................Passed
[feature/add-new-template abc1234] Add new FastAPI template with authentication
```

</div>

### 5. Push and Create Pull Request

<div class="termy">

```console
$ git push origin feature/add-new-template
$ gh pr create --title "Add new FastAPI template with authentication"
```

</div>

## Testing

### Running Tests

**All tests:**

<div class="termy">

```console
$ make test
# or
$ python -m pytest
```

</div>

**Specific test file:**

<div class="termy">

```console
$ python -m pytest tests/test_cli.py -v
```

</div>

**With coverage:**

<div class="termy">

```console
$ make test-coverage
# or
$ python -m pytest --cov=src --cov-report=html
```

</div>

**Watch mode for development:**

<div class="termy">

```console
$ make test-watch
# or
$ ptw tests/
```

</div>

### Writing Tests

When adding new features, always include tests:

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

### Test Categories

**Unit Tests** - Test individual functions and classes:

```python
def test_validate_project_name():
    assert validate_project_name("valid-name") is True
    assert validate_project_name("invalid name!") is False
```

**Integration Tests** - Test command interactions:

```python
def test_init_command_creates_project(tmp_path):
    result = runner.invoke(cli, ['init'], input='test-project\n...')
    assert result.exit_code == 0
    assert (tmp_path / "test-project").exists()
```

**End-to-End Tests** - Test complete workflows:

```python
def test_full_project_creation_workflow(tmp_path):
    # Create project
    result = runner.invoke(cli, ['init'], input='...')
    assert result.exit_code == 0

    # Add route
    result = runner.invoke(cli, ['addroute', 'test-project', 'users'])
    assert result.exit_code == 0

    # Verify files exist
    assert (tmp_path / "test-project" / "src" / "api" / "routes" / "users.py").exists()
```

## Documentation

### Serving Documentation Locally

<div class="termy">

```console
$ make docs-serve
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.43 seconds
INFO     -  [14:30:00] Serving on http://127.0.0.1:8000/
```

</div>

### Building Documentation

<div class="termy">

```console
$ make docs-build
INFO     -  Building documentation...
INFO     -  Documentation built in 0.43 seconds
```

</div>

### Writing Documentation

Documentation is written in Markdown and built with MkDocs. Here's an example structure:

**Feature Guide Template:**

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

## Code Style Guidelines

### Python Code Style

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these specific rules:

- **Line length**: 88 characters (Black default)
- **Imports**: Organized with isort
- **Type hints**: Required for all public functions
- **Docstrings**: Google style for all public APIs

### Example

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

    # Implementation here...
    return created_files
```

## Environment Variables

For development, you can set these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `FASTKIT_DEBUG` | Enable debug logging | `False` |
| `FASTKIT_DEV_MODE` | Enable development features | `False` |
| `FASTKIT_TEMPLATE_DIR` | Custom template directory | Built-in templates |
| `FASTKIT_CONFIG_DIR` | Configuration directory | `~/.fastkit` |

<div class="termy">

```console
$ export FASTKIT_DEBUG=true
$ export FASTKIT_DEV_MODE=true
$ fastkit init
DEBUG: Loading configuration from /home/user/.fastkit/
DEBUG: Available templates: ['fastapi-default', ...]
```

</div>

## Troubleshooting

### Common Issues

**1. Pre-commit hooks fail:**

<div class="termy">

```console
$ git commit -m "Fix bug"
black....................................................................Failed
hookid: black

Files were modified by this hook. Additional output:

would reformat src/cli.py
```

</div>

**Solution:** Run formatters and commit again:

<div class="termy">

```console
$ make format
$ git add .
$ git commit -m "Fix bug"
```

</div>

**2. Tests fail on different Python versions:**

**Solution:** Use tox to test multiple Python versions:

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

**3. Import errors in development:**

**Solution:** Install package in editable mode:
<div class="termy">

```console
$ pip install -e .
```

</div>

### Getting Help

- **GitHub Issues**: Report bugs and request features
- **GitHub Discussions**: Ask questions and share ideas
- **Documentation**: Check the [User Guide](../user-guide/installation.md)

## Contributing Guidelines

### Before Submitting a PR

1. **Run all checks:** `make check-all test`
2. **Update documentation** if needed
3. **Add tests** for new features
4. **Update CHANGELOG.md**
5. **Follow commit message conventions**

### Commit Message Format

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Maintenance tasks

**Examples:**

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

## Release Process

For maintainers, the release process is:

1. **Update version** in `setup.py` and `__init__.py`
2. **Update CHANGELOG.md**
3. **Create release PR**
4. **Tag release** after merge
5. **GitHub Actions** automatically builds and publishes

<div class="termy">

```console
$ git tag v1.2.0
$ git push origin v1.2.0
```

</div>

## Next Steps

Now that your development environment is set up:

1. **Explore the codebase** to understand the architecture
2. **Run the test suite** to ensure everything works
3. **Pick an issue** from GitHub to work on
4. **Join discussions** to connect with other contributors

Happy coding! 🚀

!!! tip "Development Tips"
    - Use `make check-all` before committing
    - Write tests first (TDD approach)
    - Keep commits small and focused
    - Update documentation with new features

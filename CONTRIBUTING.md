# CONTRIBUTING of FastAPI-fastkit

It is highly desirable to improve the project to provide better access for users who are new to Python and FastAPI.

Highly appreciate it for your interesting in this project and for your contribution by investing your precious time.

Before contributing to this open source, I strongly recommend that you read the
[SECURITY.md](SECURITY.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) files to understand
the direction of this project and the precautions for cooperation.

### Milestone of FastAPI-fastkit

Before get started, you'd better take a look at [MILESTONE](https://github.com/bnbong/FastAPI-fastkit/discussions/2) of this project.

To provide good productivity and quality service, I opened the source code for this project, but the direction of the project must be properly and firmly to provide a good user experience, leaving a milestone for the project officially.

This document will also be a good indicator for you to gain insight into the direction of this project's contribution.

## Setting up development environment

FastAPI-fastkit uses following stacks:

- Python 3.12+
- click 8.1.7+
- rich 13.9.2+
- pre-commit
- pytest for testing
- black for code formatting
- isort for import sorting
- mypy for static type checking

### Quick Setup with Makefile

The easiest way to set up your development environment is using our Makefile:

1. Clone repository:

```bash
git clone https://github.com/bnbong/FastAPI-fastkit.git
cd FastAPI-fastkit
```

2. Set up complete development environment:

```bash
make dev-setup
```

This single command will:
- Upgrade pip to the latest version
- Install the package in development mode with all dev dependencies
- Install documentation dependencies
- Set up pre-commit hooks
- Create a ready-to-use development environment

### Manual Setup (Alternative)

If you prefer manual setup or need more control:

1. Create and activate virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate # for Windows, use: .venv\Scripts\activate
```

2. Install development dependencies:

```bash
make install-dev
```

### Available Development Commands

Use `make help` to see all available development commands:

```bash
make help
```

Key commands for contributors:

#### Development Workflow
- `make dev-setup` - Complete development environment setup
- `make dev-check` - Run all development checks (format, lint, test)
- `make dev-fix` - Fix formatting and run tests
- `make quick-test` - Quick test after code changes

#### Code Quality
- `make format` - Format code using black and isort
- `make format-check` - Check code formatting without making changes
- `make lint` - Run all linting checks (isort, black, mypy)

#### Testing
- `make test` - Run all tests
- `make test-verbose` - Run tests with verbose output
- `make test-coverage` - Run tests with coverage report

#### Installation and Building
- `make install-test` - Install package for testing (uninstall + reinstall)
- `make clean` - Clean build artifacts and cache files
- `make build` - Build the package

#### Documentation
- `make build-docs` - Build documentation
- `make serve-docs` - Serve documentation locally

### Development Workflow

1. **Before making changes:**
   ```bash
   make dev-setup  # First time only
   make dev-check  # Ensure everything is working
   ```

2. **During development:**
   ```bash
   make quick-test  # After making changes
   ```

3. **Before committing:**
   ```bash
   make dev-check  # Final verification
   ```

### Linting & Formatting

Code quality is maintained using these tools:

1. **Black**: Code formatting
   ```bash
   make format
   ```

2. **isort**: Import sorting (integrated with black profile)
   ```bash
   # Included in make format
   ```

3. **mypy**: Static type checking
   ```bash
   make lint
   ```

4. **All checks together**:
   ```bash
   make dev-check
   ```

### Testing

Run tests using these commands:

1. **Basic test run:**
   ```bash
   make test
   ```

2. **Verbose output:**
   ```bash
   make test-verbose
   ```

3. **Coverage report:**
   ```bash
   make test-coverage
   ```

### Making PRs

Use these tags in PR title:

- [FEAT]: New feature
- [FIX]: Bug fix
- [DOCS]: Documentation changes
- [STYLE]: Code formatting
- [TEST]: Test code
- [REFACTOR]: Code refactoring
- [CHORE]: Build, config changes

Example:

```bash
# PR title example 1
'[FEAT] Add new FastAPI template for microservices'

# PR title example 2
'[FIX] Fix virtual environment activation in Windows'
```

#### Pre-commit

Pre-commit hooks are automatically installed with `make dev-setup`. The hooks will run automatically when you commit and include:

- Code formatting (black, isort)
- Linting checks
- Type checking (mypy)

If pre-commit finds issues, fix them and commit again:

```bash
make dev-fix  # Fix common issues
git add .
git commit -m "Your commit message"
```

## Documentation

Follow these documentation guidelines:

1. Docstring for all functions/classes (not necessary, but recommended)
2. Except for translations and typographical corrections, modifications to the core [README.md](README.md), [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) files of the FastAPI-fastkit project itself are prohibited.

## Adding new FastAPI-based template project

When adding a new FastAPI template project, follow these guidelines:

### Template Structure Requirements

1. Directory Structure:

```
template-name/
├── src/
│ ├── main.py-tpl
│ ├── config/
│ ├── models/
│ ├── routes/
│ └── utils/
├── tests/
├── scripts/
├── requirements.txt-tpl
├── setup.py-tpl
└── README.md-tpl
```

2. File Extensions:
   - All Python source files must use `.py-tpl` extension
   - Template files must include proper configuration files (.env-tpl, etc.)

3. Dependencies:
   - Include `fastapi-fastkit` in setup.py
   - Specify version numbers in requirements.txt
   - Use latest stable versions of dependencies

### Security Requirements

1. Implementation Requirements:
   - Environment variables management (.env)
   - Basic authentication system
   - CORS configuration
   - Exception handling and logging

2. Security Checks:
   - All template code must pass `inspector.py` validation
   - Include security middleware configurations
   - Follow security guidelines in SECURITY.md

### Documentation

1. README.md Requirements:
   - Use PROJECT_README_TEMPLATE.md format
   - Include comprehensive setup instructions
   - Document all environment variables
   - List all major dependencies
   - Provide API documentation

2. Code Documentation:
   - Include docstrings for all functions/classes
   - Document API endpoints
   - Include example usage (not necessary, but recommended)
   - Provide configuration explanations

### Testing

1. Required Tests:
   - Basic CRUD operations
   - Authentication/Authorization
   - Error handling
   - API endpoints
   - Configuration validation

2. Test Coverage:
   - Minimum 80% code coverage
   - Include integration tests
   - API testing examples

### Submission Process

1. **Initial Setup:**
   ```bash
   git clone https://github.com/bnbong/FastAPI-fastkit.git
   cd FastAPI-fastkit
   make dev-setup
   ```

2. **Development:**
   ```bash
   # Create new branch
   git checkout -b feature/new-template-name

   # Implement your template
   # ...

   # Run development checks
   make dev-check
   ```

3. **Pre-submission Checklist:**
   ```bash
   make dev-check  # Must pass all checks
   ```
   - [ ] All files use .py-tpl extension
   - [ ] FastAPI-fastkit dependency included
   - [ ] Security requirements met
   - [ ] Tests implemented and passing
   - [ ] Documentation complete
   - [ ] inspector.py validation passes
   - [ ] All make dev-check tests pass

4. **Pull Request:**
   - Provide detailed description
   - Include test results from `make test-coverage`
   - Document any special requirements
   - Reference related issues

<br>

For more detailed information about security requirements and project guidelines, please refer to:
- [SECURITY.md](SECURITY.md) for security guidelines
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for project principles

## Additional note

If you look at source codes, you will see a commentary at the top of the module that describes about the module.

In that section, I have my information as the manager of this project as author, but that doesn't mean I'm the only one who can modify the module.

I emphasize that the reason I left my information in the comment section is to specify the information about the project's final director and not to increase the barriers to entry into the open source contribution of other contributors.

**However**, I would like to inform you that I have only the right to modify the document file content itself of FastAPI-fastkit project's core documents (README.md, SECURITY.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md) file.

If the contribution to the project includes the document contribution except translation and typographical corrections, there is a possibility that PR will be rejected.

---
@author bnbong bbbong9@gmail.com

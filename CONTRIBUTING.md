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

- Python 3.12.4
- click 8.1.7
- rich 13.9.2
- pre-commit

### Local dev configuration

1. Clone repository:

```bash
git clone https://github.com/bnbong/FastAPI-fastkit.git
```

2. Set up virtual environment & Install dependencies:

```bash
cd FastAPI-fastkit

python -m venv .venv
source .venv/bin/activate # for Windows, use: .venv\Scripts\activate

pip install -r requirements.txt
```

### Linting & Formatting

Use these tools for code quality:

1. Black: Code formatting

```bash
bash scripts/format.sh
```

2. isort: Import sorting

```bash
bash scripts/sort.sh
```

3. mypy: Static type checking

```bash
bash scripts/lint.sh
```


### Making commits

Use these tags in commit messages:

- [FEAT]: New feature
- [FIX]: Bug fix
- [DOCS]: Documentation changes
- [STYLE]: Code formatting
- [TEST]: Test code
- [REFACTOR]: Code refactoring
- [CHORE]: Build, config changes

Example:

```bash
git commit -m '[FEAT] Add new FastAPI template for microservices'
git commit -m '[FIX] Fix virtual environment activation in Windows'
```

#### Pre-commit

You can use pre-commit to automatically run linting, formatting, and type checking before committing.

```bash
# Install pre-commit hooks
pre-commit install
```

After installing pre-commit hooks, the pre-commit hooks will be run automatically when you commit.

Check the pre-commit's output when you making new commit, and fix the code if there are any errors.

## Documentation

Follow these documentation guidelines:

1. Docstring for all functions/classes (not necessary, but recommended)
2. Except for translations and typographical corrections, modifications to the core [README.md](README.md), [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) files of the FastAPI-fastkit project itself are prohibited.

## Testing

After writing new tests or modifying existing tests, run these commands to ensure the tests pass:

1. Run tests:

```bash
pytest tests/
```

2. Check coverage:

```bash
pytest --cov=src tests/
```

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

1. Initial Setup:
   - Clone or Fork the repository
   - Create a new branch for your template
   - Follow the template structure

2. Development:
   - Implement required features
   - Add comprehensive tests
   - Document all components
   - Run inspector.py validation

3. Pre-submission Checklist:
   - [ ] All files use .py-tpl extension
   - [ ] FastAPI-fastkit dependency included
   - [ ] README.md follows template
   - [ ] Security requirements met
   - [ ] Tests implemented and passing
   - [ ] Documentation complete
   - [ ] inspector.py validation passes

4. Pull Request:
   - Provide detailed description
   - Include test results
   - Document any special requirements
   - Reference related issues

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

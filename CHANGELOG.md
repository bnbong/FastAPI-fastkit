# Changelog

## v1.1.3 (2025-09-13)

### Templates

- add `fastapi-single-module` template
- update `fastapi-psql-orm` template : fix dockerfile & docker-compose.yml scripts errors

## v1.1.2 (2025-09-05)

### Improvements

- add a feature of `fastkit init`, `fastkit startdemo` command to define to make a new project folder at current working directory
- add `setuptools` package at `fastapi-empty` template's dependency list.
- add a feature of `fastkit addroute`command to recognize current working project (with cmd option `.`).

## v1.1.1 (2025-08-15)

### Improvements

- fix template inspection workflow & script
  - fixing uv supportation compatibility
  - for now, template inspection is running with `uv` package manager

## v1.1.0 (2025-08-08)

### Features

- **Package Manager Support**: Add comprehensive support for multiple Python package managers
  - Support for UV (default), PDM, Poetry, and PIP package managers
  - Interactive package manager selection in `fastkit init` and `fastkit startdemo` commands
  - `--package-manager` CLI option for non-interactive usage
  - Automatic generation of appropriate dependency files (`pyproject.toml` for UV/PDM/Poetry, `requirements.txt` for PIP)
  - PEP 621 compliant project metadata for modern package managers

- **Automated Template Testing System**: Revolutionary zero-configuration template testing
  - Dynamic template discovery - new templates are automatically tested
  - Comprehensive end-to-end testing with actual project creation
  - Multi-package manager compatibility testing
  - Virtual environment creation and dependency installation validation
  - Project structure and FastAPI integration verification
  - Parameterized testing with pytest for scalable test execution

### Improvements

- **Enhanced CLI Experience**: Package manager selection with interactive prompts and helpful descriptions
- **Better Template Quality Assurance**: Multi-layer quality assurance with static inspection and dynamic testing
- **Improved Developer Experience**: Zero boilerplate test configuration for template contributors
- **Cross-Platform Compatibility**: Enhanced support for different package manager workflows

### Documentation

- Updated all user guides with package manager selection examples
- Enhanced CLI reference with comprehensive package manager documentation
- Updated contributing guidelines with new automated testing system
- Improved template creation guide with zero-configuration testing instructions
- Enhanced template quality assurance documentation

### Technical

- Implemented BasePackageManager abstract class with concrete implementations
- Added PackageManagerFactory for dynamic package manager instantiation
- Enhanced project metadata injection for all package managers
- Improved test infrastructure with dynamic template discovery
- Updated CI/CD pipelines for multi-package manager testing

### Breaking Changes

- **Default Package Manager**: Changed from PIP to UV for better performance
- **CLI Prompts**: Added package manager selection step in interactive commands

## v1.0.2 (2025-07-02)

### Features

- add logging feature at `--debug` mode option : debugging log will be stored at package directory

### Maintenances

- add coverage test report and apply it at pre-commit hook

## v1.0.1 (2025-06-27)

### Fixes

- bump `h11` version from 0.14.0 to 0.16.0

### Documentations

- add github.io site for FastAPI-fastkit (with termynal & mkdocs-material)

### Maintenances

- add a test case : test_cli_extended.py

## v1.0.0 (2025-03-01)

official release version

### Features

- rename some `fastkit` commands:
  - `fastkit startup` -> `fastkit startdemo`
  - `fastkit startproject` -> `fastkit init`
- add `fastkit addroute` command : for adding a route to project
- add `fastkit runserver` command : for running FastAPI server

### Documentations

- complete contribution guides

## v0.1.1 (2025-02-21)

pre-release version

### Fixes

- modified template metadata injection modules

## v0.1.0 (2025-02-13)

initial release : pre-release version

### Templates

- add `fastapi-default` template
- add `fastapi-asnyc-crud` template
- add `fastapi-customized-response` template
- add `fastapi-dockerized` template
- add `fastapi-psql-orm` template

### Features

- add `fastkit` command line base structure : `fastkit <command>`
  - add `fastkit --help` command : for more information about fastkit command
  - add `fastkit --version` command : for version information
  - add `fastkit --debug` command : for debugging information
  - add `fastkit echo` command : for echo test
  - add `fastkit list-templates` command : for listing available templates
  - add `fastkit startup` command : for starting project with template
  - add `fastkit startproject`command : for starting empty FastAPI project
  - add `fastkit deleteproject` command : for deleting project

### Maintenances

- add test cases including template test cases

### Chores

- add version tag system
- add pr-branching methods

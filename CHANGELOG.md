# Changelog

## v1.3.0 (Unreleased)

### Maintenances

- **Modernize template contract to be pyproject-first** (#42)
  - Template inspection now accepts `pyproject.toml-tpl` (PEP 621) as the primary metadata file. A template passes structural validation as long as `tests/`, `README.md-tpl`, and **at least one** of `pyproject.toml-tpl` / `setup.py-tpl` are present. `requirements.txt-tpl` is no longer strictly required when `pyproject.toml-tpl` declares `[project].dependencies`.
  - `_check_dependencies` consults every available source (`requirements.txt-tpl`, `pyproject.toml-tpl` `[project].dependencies`, `setup.py-tpl` `install_requires`) independently and passes if **any** one declares `fastapi`. A template with a stale `requirements.txt-tpl` is no longer rejected when its `pyproject.toml-tpl` is authoritative.
  - `read_template_stack` gained a pyproject fallback between the existing `requirements.txt-tpl` and `setup.py-tpl` paths; legacy templates resolve dependencies exactly as before.
  - Template authoring docs (`src/fastapi_fastkit/fastapi_project_template/README.md`, `docs/en/contributing/template-creation-guide.md`, `docs/en/reference/template-quality-assurance.md`) now describe required vs optional files under the pyproject-first contract.
  - Added focused tests for the new rules (pyproject-only structural and dependency validation, setup.py-only legacy validation, pyproject fallback in `read_template_stack`, and `requirements.txt-tpl`-over-pyproject precedence).
- **Pyproject-aware project identity detection** (follow-up to #42)
  - `is_fastkit_project()` now recognises FastAPI-fastkit-managed projects from `pyproject.toml` in addition to legacy `setup.py`. Detection precedence: `[tool.fastapi-fastkit].managed = true` → `[project].description` contains the `[FastAPI-fastkit templated]` marker (case-insensitive) → `setup.py` contains `fastapi-fastkit` (case-insensitive). Keeps the pre-existing setup.py path working; the new pyproject paths prevent pyproject-only templates from being mistaken for unrelated FastAPI projects in the user's workspace.
  - Canonical marker strings (`[FastAPI-fastkit templated]` and the `[tool.fastapi-fastkit]` table key `fastapi-fastkit`) are exported from `fastapi_fastkit.utils.main` as `FASTKIT_DESCRIPTION_MARKER` / `FASTKIT_TOOL_SECTION` so templates, metadata injection, and detection all reference the same strings.
  - `_process_pyproject_file` idempotently ensures the description marker and `[tool.fastapi-fastkit]\nmanaged = true` section are present after placeholder replacement, providing a safety net when a template author forgets to include them.
  - All 8 shipped `pyproject.toml-tpl` templates updated to carry `description = "[FastAPI-fastkit templated] <description>"` and a `[tool.fastapi-fastkit]` table with `managed = true`.

## v1.2.1 (2026-04-17)

### Fixes

- **`fastkit init` failure no longer wipes the user workspace**
  - Introduced `_cleanup_failed_project` helper; the previous `shutil.rmtree(project_dir)` on error could delete the entire workspace when `create_project_folder=False` (in-place deploy). Cleanup now refuses to remove the workspace and only deletes freshly created project folders.
- **Single-module template (`fastapi-single-module`) now renders the project name**
  - `inject_project_metadata()` was not substituting `<project_name>` placeholders that live directly in `main.py`. Added `_process_main_file` so single-module templates come out with the correct title/name.
- **Generated test configuration written to `pytest.ini`, not `tests/conftest.py`**
  - Interactive init used to dump INI-format content into a Python module, breaking the generated project's test suite immediately. Test config now lands in `pytest.ini` at the project root.
- **Poetry dependency generation now handles the full PEP 508 spec**
  - `PoetryManager.generate_dependency_file` previously only split on `==`. Any other specifier (`>=`, `~=`, `<=`, `!=`, `===`), environment marker (e.g. `; sys_platform != 'win32'`), or `extras + version` combination was emitted as part of the TOML key, producing an invalid `pyproject.toml` that `poetry install` could not parse. Added `_parse_pip_requirement` to split name, extras, version specifier, and marker, emitting inline tables when needed.
- **SQLite stack now installs `aiosqlite`**
  - `core/settings.py` catalog previously omitted the async driver, so SQLite projects failed at runtime when the generated code used async sessions.
- **Dockerfile `CMD` uses exec form with double-quoted JSON array**
  - The previous single-quoted form was interpreted as shell form by some Docker versions and bypassed signal handling (no graceful shutdown on `SIGTERM`).

### Security

Addressed open Dependabot advisories by bumping minimum versions:

- `pytest >= 9.0.3` — tmpdir handling advisory (GHSA)
- `black >= 26.3.1` — arbitrary file writes via cache file name
- `pygments >= 2.20.0` — ReDoS in GUID regex (transitive via `rich`)
- `requests >= 2.33.0` — insecure temp file reuse in `extract_zipped_paths`
- `pymdown-extensions >= 10.17.2` — required to run on `pygments` 2.20+ (prevents `html.escape(None)` crash during docs build)

### Documentation

- **FAQ (`docs/en/reference/faq.md`)**: the "interactive mode automatically generates" bullets now accurately describe what is generated conditionally — database/auth files only when the selected option supports code generation, Docker files only for the selected deployment option, and coverage config only when `Coverage` or `Advanced` testing is selected.
- Contributing and development-setup guides updated; `fastkit --version` example refreshed to 1.2.1.

### Maintenances

- Added regression tests for every fix above, plus targeted tests to close Codecov patch-coverage gaps (`_process_main_file` error handling, `_cleanup_failed_project` edge cases, interactive init failure branch).
- Cleaned up Ruff warnings in `src/fastapi_fastkit/cli.py` (E402 import ordering for `__version__`, four stray F541 `f""` prefixes).
- Refreshed `requirements.txt`, `requirements-docs.txt`, `pdm.lock`, and `uv.lock` to the new security floors.

## v1.2.0 (2025-11-27)

### Features

- **(Breaking Change) Add `fastkit init --interactive` feature**: Revolutionary feature-by-feature project builder
  - `fastkit init --interactive` now provides guided project setup with intelligent feature selection
  - Always uses Empty project (fastapi-empty template) as base template to prevent conflicts with DynamicConfigGenerator
  - Interactive project configuration with validation and compatibility warnings
  - Real-time dependency collection based on selected features
  - Confirmation summary before project creation

- **Dynamic Code Generation**: Intelligent code generation based on feature selections
  - Integrated DynamicConfigGenerator for automatic code scaffolding
  - Generates `main.py` with selected features (auth, database, monitoring, etc.)
  - Creates database configuration files for PostgreSQL, MySQL, MongoDB, SQLite
  - Generates authentication setup for JWT, OAuth2, FastAPI-Users
  - Auto-generates test configuration (pytest with optional coverage)
  - Docker deployment files (Dockerfile, docker-compose.yml) generation

- **Enhanced Dependency Management**: Multi-format dependency file generation
  - Automatically generates both package-manager-specific files AND requirements.txt
  - Ensures pip compatibility regardless of selected package manager
  - Dependencies correctly reflect all selected stack features
  - Smart dependency deduplication and version management

### Improvements

- **Interactive CLI Experience**:
  - Step-by-step feature selection with descriptions. Each selection step proceeds in the following order below:
    - Database selection (PostgreSQL, MySQL, MongoDB, Redis, SQLite)
    - Authentication options (JWT, OAuth2, FastAPI-Users, Session-based)
    - Background tasks (Celery, Dramatiq)
    - Caching layer (Redis, fastapi-cache2)
    - Monitoring integration (Loguru, OpenTelemetry, Prometheus)
    - Testing framework (Basic, Coverage, Advanced)
    - Utilities (CORS, Rate-Limiting, Pagination, WebSocket)
    - Deployment configuration (Docker, docker-compose)
    - Package manager selection (pip, uv, pdm, poetry)
    - Custom package addition support

### Technical

- **Interactive Backend Architecture**:
  - `InteractiveConfigBuilder`: Orchestrates full interactive flow
  - `DynamicConfigGenerator`: Generates feature-specific code
  - `DependencyCollector`: Intelligently collects stack dependencies
  - Input validators with comprehensive error handling
  - Multi-select prompts for utilities and deployment options
  - Feature compatibility validation system

### Documentation

- Add AI translation support of user guides(docs/ folder sources that mkdocs renders)

## v1.1.5 (2025-09-14)

### Improvements

- **Adaptive Console Sizing**: Enhanced terminal output display
  - Console width is 80% of terminal width, capped at 120 characters
  - Console height is terminal height minus buffer (5 lines)
  - Automatic terminal size detection with fallback to default sizes (80x24)
  - Dynamic sizing based on actual terminal dimensions

### Fixes

- **Text Truncation Prevention**: Completely eliminated text truncation in CLI output
  - Template names and descriptions are now fully displayed without "..." truncation
  - Table columns automatically adjust to content length to prevent text cutting
  - Added `overflow="fold"` and `no_wrap=False` settings to Rich tables
  - Template listing now shows complete template names (e.g., `fastapi-custom-response` instead of `fastapi-custom-respo...`)
- **Fixing the object `console` not found error**
  - this critical error was occurred every version before this version.
  - this error was occurred because of the mismatched logic between distribute github actions workflow and the top `__init__.py` file of fastkit project package.
  - This issue was discovered during the development of version 1.1.2, and I spent a lot of time troubleshooting it. I believe this was due to my lack of development experience. I sincerely apologize.

## v1.1.4 (deprecated)

this version was hotfix build, but it is deprecated.

The issues that were being addressed during the development of this version remained unresolved and were fixed in version v1.1.5.

For more details, please refer to the CHANGELOG.md file for v1.1.5.

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

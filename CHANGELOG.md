# Changelog

## v1.5.1 (2026-10-27)

### Security

- Templates: `black` pinned to 26.10.1 in 11 templates and the `black>=26.10.1` floor applied to every `pyproject.toml-tpl` and the `fastapi-mcp` `setup.cfg-tpl` (GHSA-cg8m-r9f2-5wm2); `certifi` 2026.10.23 in 9 templates (GHSA-6q48-6c7w-9gw2, critical); `fastapi-dockerized` pins `setuptools==84.2.1` (GHSA-xmj3-9gf7-h52w); `fastapi-mcp` pins `mcp==1.30.0` with constraint `mcp>=1.30.0,<2.0.0` (GHSA-84m7-p3x7-pcfv). `pip-audit` reports no known vulnerabilities for all 12 template `requirements.txt-tpl` files (#86, #88, #90).
- Workspace: 40 open Dependabot alerts resolved (#90). Docs group floor `certifi>=2026.10.19` (GHSA-6q48-6c7w-9gw2, critical, transitive via `requests`); dev extra floors `black>=26.10.1`, `virtualenv>=21.14.9` (GHSA-8rjx-v5ww-45pp, GHSA-c947-3pg5-gm8q, GHSA-5vjq-rrrf-7h2q, GHSA-vxj4-q4g9-crj7 and 12 related advisories, transitive via `pre-commit`) and new `filelock>=4.2.1` (GHSA-v4x8-3wr5-3wq8 plus two related advisories, transitive via `virtualenv`). `uv.lock`, `pdm.lock`, `requirements.txt`, and `requirements-docs.txt` relocked on certifi 2026.10.23, black 26.10.1, virtualenv 21.14.13, filelock 4.2.4; `distlib`, `packaging`, and `python-discovery` moved as `virtualenv` requirements.

### Maintenance

- `scripts/update_nav_translations.py` moved its AI fallback from `gpt-4` (retired by OpenAI on 2026-10-23) to `gpt-5.6-sol`, using `max_completion_tokens=1000` and dropping `temperature`, which reasoning models reject (contributed by @brunobuddy, #89).

### Notes

- `mcp` 1.30.0 changes some defaults in generated `fastapi-mcp` projects: HTTP clients follow redirects only within the same origin, idle Streamable HTTP sessions close after 30 minutes (`FastMCP(session_idle_timeout=None, max_sessions=None)` disables this), and the OAuth client validates the authorization server's `issuer`. The template's own tests pass unchanged.

## v1.5.0 (2026-10-14)

### Features

- `fastkit addroute --layout classic-layer|domain` (contributed by @vastimofeev, #83). Without the option, the layout is resolved from `[tool.fastapi-fastkit]`: `preset = "domain-starter"` selects `domain`, other presets keep `classic-layer`; when no preset is recorded (`startdemo`, older `init` projects), a `template = "fastapi-domain-starter"` entry selects `domain`. The resolved layout is shown in the confirmation table.
- `domain` layout generates `domains/<route>/` with `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`, and a re-exporting `__init__.py`; class names are derived from the route (`health_checks` → `HealthChecksService`). The example is a typed CRUD API backed by a thread-safe in-memory repository (process-local, lost on restart) with a `reset_store()` hook, and is registered in the shared API router with `prefix="/<route>"` and `tags=["<route>"]`.
- Re-running `addroute` is idempotent for both layouts: existing files are kept, existing `include_router` registrations (positional or `router=` keyword form) are not duplicated, and custom prefix/options on an existing registration are preserved with an info message. An unparsable router module falls back to text insertion, and import aliases (`<route>_router`, `<route>_2`, …) let same-named modules from different layouts coexist.

### Templates

- `fastapi-domain-starter`: the shipped `items` domain now follows the same convention (`APIRouter()` in the domain, `prefix="/items", tags=["items"]` on `include_router`; endpoints unchanged), and `tests/conftest.py` resets the in-memory store of every domain that exposes `service.reset_store()` before and after each test, so generated domains stay isolated (#83).

### Security

- `PyJWT` floor raised to 2.15.1 in `fastapi-auth-jwt` and `fastapi-mcp` (PYSEC-2026-4140 ~ 4152); `fastapi-mcp` pins `urllib3==2.8.0` (PYSEC-2026-4175 ~ 4177).
- Workspace security floors `urllib3>=2.8.0` (GHSA-gh4c-6fx4-qh6g) and `anyio>=4.14.2` (GHSA-82r6-8w77-94w6, GHSA-5p39-cfhj-2xmp) added to `pyproject.toml`; `uv.lock` (anyio 4.14.2, urllib3 2.8.0), `pdm.lock` (anyio 4.15.1, urllib3 2.8.0), and `requirements-docs.txt` (urllib3 2.8.0) relocked (#80, #82).
- Dev extra floor `virtualenv>=21.7.13` (transitive via `pre-commit`) closes GHSA-p58f-9548-mpm2 (bash/fish activation scripts execute commands embedded in paths), GHSA-x78j-v8h9-3j2q (command injection via `--prompt` in `activate.bat`), GHSA-94p9-xgh2-xp45 (seed wheels not integrity-checked) and GHSA-9h9j-4vrj-gf7g (`pyvenv.cfg` prompt injection); `requirements.txt` pinned to 21.7.16 and `uv.lock` / `pdm.lock` relocked (virtualenv 21.7.9 → 21.7.16, no other packages moved).

### Documentation

- Docs landing pages (root and every locale) now load the logo from `img/fastkit_general_logo.png` instead of the repo-only `.github/` path (#81).
- English: `adding-routes`, `cli-reference`, and the domain-starter tutorial document `--layout` and the domain layout (#83); the MCP tutorial's `dependencies.py` snippet gains the missing `import jwt`; `development-setup` says "see above" instead of "see below".
- All six translated locales (ko/ja/zh/es/fr/de) brought to parity with English: the `auth-jwt`, `sqlmodel`, and `llm-agent` tutorials translated, drifted pages (`index`, `development-setup`, `template-creation-guide`, `preset-feature-matrix`, `template-quality-assurance`, `cli-reference`, `creating-projects`, `choosing-a-starter`, `mcp-integration`) re-synced, and the translation-status page updated (#84). The three pages changed by #83 (domain-starter tutorial, `adding-routes`, `cli-reference`) are re-synced in every locale in this release.

### Maintenance

- `addroute` generation moved into `backend/route_generators.py` (`ClassicLayeredRouteGenerator`, `DomainRouteGenerator`, `resolve_route_layout`) and `backend/route_wiring.py` (`register_router`, `router_alias`); `add_new_route()` gained an optional `layout` argument. Suite size: **1047 tests passing**.

### Breaking Changes

- `addroute` in a `domain-starter` project (or a project generated from `fastapi-domain-starter` without a recorded preset) now generates the domain layout instead of `api/routes` / `crud` / `schemas` modules; pass `--layout classic-layer` to keep the old output.

## v1.4.1 (2026-09-10)

### Security

- `python-jose` → `PyJWT[crypto]` in the JWT / FastAPI-Users catalog entries and the `fastapi-mcp` template (drops the unpatched `ecdsa` CVE-2024-23342); docs dependency floors raised for Dependabot advisories (mkdocs-material ≥ 9.7.7, pymdown-extensions ≥ 11.0.1, idna ≥ 3.15; urllib3 / virtualenv / filelock refreshed in lock files).
- `passlib[bcrypt]` → `pwdlib[argon2]` in the JWT / FastAPI-Users catalog entries and the `fastapi-mcp` template (passlib is unmaintained and pinned bcrypt to 4.0.1; generated projects now hash with argon2id like `fastapi-auth-jwt`).

### Fixes

- Template inspector's compile check no longer writes bytecode and runs before the Docker test step (fixes the weekly `fastapi-psql-orm` PermissionError); Docker strategy reclaims bind-mount ownership after container runs; CI pins PDM's interpreter to 3.12; security-scan workflow now builds a valid JSON report and counts vulnerabilities correctly.
- Template inspector parses every `docker-compose ps --format json` shape (single JSON array on Compose < 2.21, NDJSON on newer releases) and falls back to the `docker compose` plugin when the standalone binary is missing.
- Docker-backed templates are smoke-tested against the container's published port instead of requiring a host virtualenv (the weekly `fastapi-psql-orm` run now reaches and passes the smoke step).
- `startdemo` / `init` normalize copied text files to LF and keep executable bits, and a new `.gitattributes` pins template line endings, so shell scripts generated on Windows or with `core.autocrlf=true` no longer fail with `bash\r: No such file or directory`. `fastapi-psql-orm` `.env` now sets `ENVIRONMENT=development`.

## v1.4.0 (2026-09-04)

### Features

- `fastkit init --config <file>` (JSON/TOML/YAML) for prompt-free, reproducible generation, plus `--save-config` to capture an interactive session. Configs are normalized and schema-validated.
- `--dry-run`, `--no-venv`, `--no-install`, and `--yes` for `init` and `startdemo`.
- Generated projects record a `[tool.fastapi-fastkit]` metadata block (`template`, `preset`, `package_manager`, `app_module`, `features`); `runserver` and `addroute` use it instead of guessing the layout.
- Interactive builder now generates working code for every catalog choice (Celery/Dramatiq, Redis cache, WebSocket, Pagination, OpenTelemetry, OAuth2, Session auth) and adds three axes: `migrations` (Alembic), `tooling` (ruff, pre-commit, GitHub Actions, devcontainer, Makefile), `logging` (structured JSON). `/health` and `/ready` are always generated.
- `# fastkit:imports` / `# fastkit:routes` anchors in templates; `addroute` falls back to AST-based insertion.
- Package-manager subprocesses are bounded by timeouts (`FASTKIT_SUBPROCESS_TIMEOUT`); auto-detection prefers `uv`.

### Templates

- New: `fastapi-auth-jwt` (refresh-token rotation, argon2, scopes), `fastapi-sqlmodel` (async SQLModel + Alembic + generic CRUD), `fastapi-llm-agent` (Claude SSE streaming with tool loop).
- Deprecated: `fastapi-dockerized`, `fastapi-async-crud` (still shipped).
- All templates aligned on Python 3.12, `setup.py-tpl` removed, self-dependency on `FastAPI-fastkit` removed, dependency pins refreshed, `fastapi-mcp` package renamed to `mcp_server` to stop shadowing the `mcp` library.

### Fixes

- Rollback on a failed run no longer deletes a project directory that existed before the run; `startdemo` refuses an existing target.
- In-place deployment only substitutes placeholders in files it copied and asks before overwriting.
- Quotes and backslashes in project name/author/description no longer break `pyproject.toml` or generated Python.
- Rewriting the `[tool.fastapi-fastkit]` block no longer corrupts arrays in it.

### Maintenance

- Interactive code generation moved from string concatenation to Jinja2 fragments (`src/fastapi_fastkit/fragments/`); generated apps use `lifespan` and `python:3.12-slim`. `jinja2` is the only new runtime dependency.
- Template inspector split into `fastapi_fastkit.backend.inspection` with real smoke tests (boots uvicorn, probes `/docs` and `/health`), config-consistency, dependency-drift, and placeholder-residue checks. `scripts/inspect-templates.py` gained `--offline`, `--no-smoke`, `--mypy`.
- `cli.init` orchestration extracted into `backend/scaffolder.py`; package managers share one checked-run helper.
- Docs: tutorials for the three new templates, CLI reference and starter guide updated (EN/KO). Suite size: **781 tests passing**.

### Breaking Changes

- `setup.py-tpl` removed from bundled templates (pyproject-first).
- Generated projects no longer list `FastAPI-fastkit` as a runtime dependency.
- `pip` is no longer auto-upgraded during environment setup.
- Auto-detection prefers `uv` over `pip`; pass `--package-manager pip` to keep the old behaviour.
- `TemplateInspector` / `inspect_fastapi_template` take an `InspectionOptions` argument; check functions moved to `fastapi_fastkit.backend.inspection`.

## v1.3.0 (2026-05-06)

### Features

- **Architecture preset selection in interactive init**
  - `fastkit init --interactive` now includes an `Architecture Preset` step with `minimal`, `single-module`, `classic-layered`, and `domain-starter`.
  - The selected preset is saved in the interactive config and shown in the final summary.
  - CLI help and interactive docs were updated to match the new flow.
- **Preset-aware project generation**
  - Interactive generation now selects a different base template for each preset.
  - `minimal` and `single-module` continue to use generated `main.py`, while `classic-layered` and `domain-starter` preserve the template-shipped entrypoint.
  - Database/auth config output paths, compatibility warnings, and app module resolution are now preset-aware.
  - `fastkit runserver` and generated Dockerfiles now resolve the correct app module for non-default layouts such as `src/app/main.py`.

### Templates

- **Add `fastapi-domain-starter` template**
  - New pyproject-first, domain-oriented starter for medium-sized FastAPI APIs.
  - Includes a built-in `/api/v1/health` endpoint and an example `items` domain.
  - Ships with FastAPI-fastkit identity markers in `pyproject.toml`.
- Improve template metadata/path handling for the domain-oriented layout.
- Update template README titles so `fastkit list-templates` shows readable descriptions.

### Documentation

- Add `Choosing a Starter` guide for template and preset selection.
- Add `Preset Feature Matrix` reference docs for preset-specific generation behavior.
- Add `fastapi-domain-starter` tutorial and generated project walkthrough.
- Add translation status and source-of-truth policy docs, plus translation status notices on the English and Korean landing pages.
- Refresh CLI examples and fix the Korean `init --interactive` walkthrough so docs match the current flow.

### Tests

- Add end-to-end coverage for architecture presets and `fastapi-domain-starter`.
- Add regression tests for preset layout decisions, app module derivation, and interactive summary rendering.
- Add package-manager compatibility coverage for `fastapi-domain-starter`, including the `pip` path.
- Suite size: **612 tests passing** at the close of v1.3.0.

### Maintenances

- **Modernize template contract to be pyproject-first**
  - Template inspection now accepts `pyproject.toml-tpl` as a primary metadata source.
  - Dependency inspection and `read_template_stack` now support `pyproject.toml-tpl` alongside existing files.
  - Template authoring and QA docs were updated for the new contract.
- **Add pyproject-aware project identity detection**
  - `is_fastkit_project()` now detects FastAPI-fastkit-managed projects from `pyproject.toml` as well as legacy `setup.py`.
  - Standardize the FastAPI-fastkit description marker and `[tool.fastapi-fastkit] managed = true` metadata across shipped pyproject templates.
- Add `requirements.txt-tpl` to `fastapi-domain-starter` for full package-manager compatibility, including `pip`.

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

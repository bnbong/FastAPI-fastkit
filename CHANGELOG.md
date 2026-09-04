# Changelog

## v1.4.0 (2026-09-04)

### Features

- **Reproducible project configuration files**
  - `fastkit init --config <path>` creates a project without a single prompt, replaying a saved configuration. `.json` and `.toml` are always available; `.yaml` / `.yml` work when PyYAML happens to be installed (fastkit does not add it as a runtime dependency).
  - `fastkit init --interactive --save-config <path>` writes the answered configuration to disk. Without the flag, an interactive session that reached the end offers to save the answers — but only when a human is at the terminal, so scripted runs stay silent.
  - Loaded configs are validated with the same rules the interactive prompts use (project name, author email, `all_dependencies` shape) and every problem is reported before anything is written.
  - A hand-written config that lists only feature selections is expanded through the interactive builder, so a file and a wizard session resolve dependencies identically.
  - Every config, hand-written or `--save-config`-produced, is normalized and schema-validated (`normalize_project_config`) before it reaches the generator: unknown keys, unknown axis choices and wrong-typed values are rejected with the offending name and the allowed values.
- **`--dry-run` preview for `init` and `startdemo`**
  - Prints the file tree that would be created and the packages that would be installed (with the package manager that would install them), then exits without touching the disk.
- **`--no-venv` and `--no-install` for `init` and `startdemo`**
  - `--no-install` skips dependency installation; `--no-venv` skips virtual environment creation and implies `--no-install`. Useful in containers, CI, and on machines where the environment is managed elsewhere.
- **`[tool.fastapi-fastkit]` project metadata block**
  - Every generated project now records how it was produced in its `pyproject.toml`: `managed`, `version`, `template`, `preset` (interactive runs only), `package_manager`, `app_module` and `features` (a flat `"<category>:<choice>"` list).
  - `fastkit runserver` reads `app_module` from that block first and only falls back to scanning the tree, so non-standard layouts start correctly. Generated Dockerfiles use the same entrypoint.
  - The block is rewritten (never duplicated) when generation runs again, and it is stamped after the package manager has finished rewriting `pyproject.toml`.
- **Explicit route anchors for `addroute`**
  - Templates and generated entrypoints carry `# fastkit:imports` and `# fastkit:routes` comments marking where `fastkit addroute` inserts imports and router registrations. Projects without the anchors still work through the AST-based fallback.
- **Configurable subprocess timeouts**
  - Every package manager invocation is bounded (availability check, virtualenv creation, dependency install). `FASTKIT_SUBPROCESS_TIMEOUT` overrides all of them with a single value in seconds; an unparsable or non-positive value is ignored.
- **`--yes` / `-y` skips the overwrite confirmation for in-place deployment**
  - Added to both `fastkit init` and `fastkit startdemo`. When a project is deployed in place (no new project folder), fastkit no longer asks "Overwrite these files?" before replacing existing files. It has no effect on the separate "Do you want to proceed with project creation?" prompt. Non-interactive runs (stdin not a TTY, e.g. CI) already skipped the overwrite confirmation automatically and continue to do so without the flag.

- **Interactive builder now generates real code for every catalog selection**
  - Previously, choosing Celery/Dramatiq, Redis caching, WebSocket, Pagination, OpenTelemetry, OAuth2 or Session-based auth only installed packages and left the wiring to the user. Every one of those selections now generates working code: a `worker.py` + `features/tasks.py` router for background tasks, `features/cache.py` for Redis caching, `features/websocket.py` and `features/pagination.py` for the matching utilities, `main.py` OpenTelemetry tracing setup, and OAuth2 / session-based auth modules with the matching `main.py` middleware.
- **Three new interactive builder axes**
  - `logging`: a `structured` choice adds stdlib `logging` + `json` structured output with a request-id middleware (`logging_config.py`), no new dependency.
  - `migrations`: an `Alembic` choice generates a full async migration environment (`alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, a baseline revision, `scripts/migrate.sh`) for any SQL database selection.
  - `tooling` (multi-select): `ruff`, `pre-commit`, `github-actions`, `devcontainer` and `makefile` choices generate the matching config file(s); `ruff` also merges a `[tool.ruff]` block into `pyproject.toml` (or writes a standalone `ruff.toml` for `pip` projects).
- **`/health` and `/ready` endpoints generated for every project**
  - Every `main.py` overlay now always includes a liveness (`/health`) and readiness (`/ready`) probe, regardless of feature selection.
- **`--dry-run` lists every file a run would create**
  - The preview now enumerates the exact same file set `generate_all_files()` would write, including the new logging/migrations/tooling artifacts.
- **Preset compatibility warnings cover the new axes**
  - `classic-layered` and `domain-starter` preserve their template-shipped `main.py`, so feature validation now warns when a selection under the new axes (or the existing ones) needs manual wiring into that preserved entrypoint.

### Templates

- **Add `fastapi-auth-jwt` template** — production-shaped JWT authentication: access/refresh token pairs with rotation (each refresh token tracked by `jti`, so a replay is rejected), argon2id hashing via `pwdlib`, single-session and all-session logout, `require_scopes(...)` and superuser dependencies, SQLModel users with Alembic migrations, SQLite by default and PostgreSQL via `DATABASE_URL`.
- **Add `fastapi-sqlmodel` template** — persistence-first starter: SQLModel over an async SQLAlchemy 2.0 engine, async Alembic migrations, a generic `CRUDBase`, and paginated list endpoints behind a `Page[T]` envelope. Runs on SQLite out of the box, switches to PostgreSQL by changing `DATABASE_URL`.
- **Add `fastapi-llm-agent` template** — streaming Claude chat agent: SSE token delivery, a real tool-call loop with an iteration cap, conversation history behind a `ConversationStore` interface, bundled `calculator` / `current_time` tools, and a test suite that runs offline against a scripted fake client.
- **Deprecate `fastapi-dockerized` and `fastapi-async-crud`** — both remain shipped and generate working projects, but they are no longer recommended starting points. Docker tooling is now part of the newer templates and of interactive deployment selection, and async CRUD is better served by `fastapi-sqlmodel`.
- **Template hygiene pass across every shipped template**
  - Aligned on Python 3.12 (`requires-python`, black `target-version`, mypy `python_version`, `python:3.12-slim` base images).
  - Removed `setup.py-tpl` in favour of a pyproject-first contract.
  - Refreshed dependency pins to current stable releases (in progress at the time of the release).

### Documentation

- Add tutorials for the three new templates: JWT authentication, SQLModel persistence, and the LLM agent.
- Rewrite `Choosing a Starter` around the expanded template set, with deprecation notes for `fastapi-dockerized` and `fastapi-async-crud`.
- Document `--config`, `--save-config`, `--dry-run`, `--no-venv`, `--no-install`, the `[tool.fastapi-fastkit]` metadata contract, the route anchors, and `FASTKIT_SUBPROCESS_TIMEOUT` in the CLI reference.
- Expand the Template Quality Assurance reference with the smoke test, configuration-consistency, dependency-drift and placeholder-residue checks, plus the `--offline` / `--no-smoke` / `--mypy` inspection flags.
- Link the fragment authoring procedure (`src/fastapi_fastkit/fragments/README.md`) from the contributor guides.
- Sync the Korean landing page, CLI reference and starter guide; refresh translation status counts for every locale.

### Tests

- Coverage for config-file round-trips (JSON / TOML / YAML), validation failures, and the `--config` / `--save-config` paths.
- Coverage for `--dry-run`, `--no-venv` and `--no-install` across `init` and `startdemo`.
- Coverage for metadata block rendering, idempotent rewrites, and `runserver` app-module resolution from recorded metadata.
- Rendered-fragment tests asserting every generated Python file parses, across the feature combination matrix.
- End-to-end coverage for the three new templates, including their own test suites.

### Maintenances

- **Interactive code generation moved to Jinja2 fragments** — the generated `main.py`, database/auth modules, Docker files and pytest configuration are now rendered from templates under `src/fastapi_fastkit/fragments/` instead of being assembled from strings. Generated apps use the `lifespan` context manager (not the deprecated `@app.on_event`) and `python:3.12-slim` images. `jinja2` is the one new runtime dependency.
- **Package manager auto-detection prefers `uv`** — detection order is now `uv` → `pdm` → `poetry` → `pip`, with `pip` as the last resort. An explicitly requested manager still wins.
- **Removed the automatic `pip` self-upgrade** during environment setup — fastkit no longer mutates the freshly created virtual environment's `pip`.
- **Template inspector restructured** into `fastapi_fastkit.backend.inspection` (context / checks / consistency / freshness / smoke / lint / report modules) driven by an `InspectionOptions` dataclass. `fastapi_fastkit.backend.inspector` remains as a facade for the historical import path.
- `scripts/inspect-templates.py` gained `--offline`, `--no-smoke` and `--mypy`.

### Fixes

- **`fastkit startdemo` now refuses to target an existing project directory**
  - Like `init`, `startdemo` stops with `Error: Project '{name}' already exists.` when the target project directory is already there. `--dry-run` is unaffected, since it never writes to disk. Rollback on a failed run only removes a project folder that this run created — a directory that already existed beforehand is never deleted.
- **Project name, author and description are escaped correctly for every generated file type**
  - Values containing quotes (`"`, `'`) or backslashes no longer produce a broken `pyproject.toml` or invalid Python source; each generated file escapes the value according to its own syntax (TOML string escaping, Python string escaping). `startdemo` and non-interactive `init` now also validate the project name before generating anything.
- **Template smoke tests capture full server output and retry on port conflicts**
  - The internal template inspector's smoke test now captures the `uvicorn` subprocess output to a file and includes the tail of that log when a smoke test fails, and retries with a different port (up to 3 attempts) if the chosen port is already in use.

### Breaking Changes

- **`setup.py-tpl` removed from shipped templates.** Template metadata is pyproject-first. Inspection still accepts `setup.py-tpl` for third-party templates, but no bundled template ships one and new templates should not add one.
- **Generated projects no longer depend on `FastAPI-fastkit` at runtime.** The CLI is a development tool; a generated project's dependency list now contains only what the application itself imports. Projects generated by earlier versions can drop the dependency safely.
- **The automatic `pip` upgrade during environment setup is gone.** Environments that relied on fastkit refreshing `pip` need to run `pip install --upgrade pip` themselves.
- **Package manager auto-detection now prefers `uv` over `pip`.** A machine with `uv` installed that previously fell through to `pip` will now get a `pyproject.toml`-based project. Pass `--package-manager pip` to keep the old outcome.
- **Template inspector API changed.** `TemplateInspector` and `inspect_fastapi_template` now take an `InspectionOptions` argument and the individual checks live in `fastapi_fastkit.backend.inspection`. Code importing check functions directly from `fastapi_fastkit.backend.inspector` must be updated.

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

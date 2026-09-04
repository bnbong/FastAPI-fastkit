# Template Quality Assurance

FastAPI-fastkit provides comprehensive automated template validation to ensure all templates maintain high quality and remain functional across different environments and package managers.

## Multi-Layer Quality Assurance

FastAPI-fastkit employs **two complementary quality assurance systems**:

### 1. Static Template Inspection
**Weekly automated validation of template structure and syntax**

### 2. Dynamic Template Testing
**Comprehensive end-to-end testing with actual project creation**

## Automated Weekly Inspection

Every Wednesday at midnight (UTC), our GitHub Actions workflow automatically inspects all FastAPI templates to ensure they meet quality standards:

- ✅ **File Structure Validation** - Ensures all required files and directories are present
- ✅ **File Extension Verification** - Validates that template files use correct `.py-tpl` extensions
- ✅ **Dependency Checking** - Confirms FastAPI and required dependencies are properly defined
- ✅ **FastAPI Implementation** - Verifies that templates contain proper FastAPI app initialization
- ✅ **Test Execution** - Runs template tests to ensure functionality
- ✅ **Smoke Test** - Boots the generated project with uvicorn and probes its HTTP surface
- ✅ **Configuration Consistency** - Python version pins, dependency drift, self-dependency
- ✅ **Placeholder Residue** - No `<placeholder>` survives project generation
- ✅ **Dependency Freshness** - Warns about pins lagging behind their latest PyPI release

## What each check does

Inspection generates a **real project** from the template — copy, `-tpl`
conversion, metadata injection — and then runs every check against that
generated project, not against the template source. A check that only reads
the template can't catch a placeholder that generation failed to substitute.

### Smoke test

The generated project is started with uvicorn on a free port, and the
inspector polls until the server answers or the timeout expires. Once it is
up, `/docs` and `/health` are requested and their status codes checked. The
server process is then terminated, escalating to `SIGKILL` if it does not
stop.

The uvicorn target is resolved in order: `[tool.fastapi-fastkit].app_module`
in the generated `pyproject.toml`, then `app_module` in the template's
`template-config.yml`, then the conventional `main.py` locations. That is
the same contract `fastkit runserver` uses, so a template whose smoke test
boots is a template whose generated project runs.

This is the check that catches what static analysis cannot: an import that
resolves only at runtime, a `lifespan` that raises, a config field with no
default.

### Configuration consistency

Three things are validated against the template's `pyproject.toml-tpl`:

- **Python version pins agree and target 3.12** —
  `requires-python`, black's `target-version` and mypy's `python_version`.
  A template that formats as `py311` while declaring `>=3.12` is a bug
  waiting to reach a contributor.
- **No dependency drift** — packages declared in `requirements.txt-tpl` and
  in `[project].dependencies` must not disagree. Templates ship both files
  for package-manager compatibility, and two lists always diverge unless
  something checks them.
- **No self-dependency** — a generated project must not declare
  `FastAPI-fastkit` as a runtime dependency. The CLI is a development tool;
  shipping it into every generated app pulls the entire fastkit dependency
  tree into unrelated projects.

### Placeholder residue

Every `<project_name>`, `<description>` and friend must be substituted
during generation. Any `<placeholder>` still present in the generated
project is an error — it means metadata injection does not know about that
file, and the user would receive it verbatim.

### Dependency freshness

Pinned versions are compared against the latest release on PyPI and
reported as warnings, never errors — a template lagging one minor version
is information, not a failure. This is the only check that touches the
network, and `--offline` skips it.

## Automated Template Testing System

FastAPI-fastkit includes a **revolutionary automated testing system** that provides comprehensive validation of every template:

### Dynamic Template Discovery

The testing system **automatically discovers all templates** without manual configuration:

```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Results show all discovered templates
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-async-crud]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-dockerized]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-psql-orm]
```

### Comprehensive Test Coverage

Each template undergoes **comprehensive end-to-end testing**:

#### ✅ Project Creation Process
- Template copying and file transformation
- Project metadata injection (name, author, description)
- File structure validation

#### ✅ Package Manager Compatibility
- **UV** (default): Fast Rust-based package manager
- **PDM**: Modern Python dependency management
- **Poetry**: Established dependency management
- **PIP**: Traditional Python package manager

#### ✅ Virtual Environment Management
- Environment creation for each package manager
- Dependency installation verification
- Package manager-specific workflows

#### ✅ Dependency Resolution
- `pyproject.toml` generation (UV, PDM, Poetry)
- `requirements.txt` generation (PIP)
- Metadata compliance (PEP 621)
- Build system configuration

#### ✅ Project Structure Validation
- FastAPI project identification
- Required file existence
- Directory structure verification

### Test Execution Examples

**Run all template tests:**
```console
$ pytest tests/test_templates/test_all_templates.py -v
```

**Test specific template:**
```console
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default] -v
```

**Test with PDM environment:**
```console
$ pdm run pytest tests/test_templates/test_all_templates.py -v
```

### Continuous Integration

The automated testing system runs in **CI/CD pipelines**:

- ✅ **Pull Request Validation**: Every PR tests affected templates
- ✅ **Nightly Testing**: Complete template suite validation
- ✅ **Package Manager Testing**: Cross-validation with all managers
- ✅ **Environment Testing**: Multiple Python versions and platforms

### Benefits for Contributors

**Zero Configuration Testing:**

- 🚀 Add new template → automatic testing
- ⚡ No manual test file creation required
- 🛡️ Consistent quality standards

**Comprehensive Coverage:**

- 🔍 End-to-end project creation testing
- 📦 Multi package manager validation
- 🏗️ Complete dependency resolution testing
- ✅ Real-world usage simulation

**Developer Experience:**

- 🎯 **Focus on Template Content**: Testing is automatic
- 🔄 **Immediate Feedback**: Fast test execution
- 📊 **Clear Results**: Detailed test reporting
- 🚫 **No Boilerplate**: Zero test configuration needed

## Manual Template Inspection

For development and debugging purposes, you can manually inspect templates using our local inspection script or Makefile commands:

### Using the Inspection Script Directly

```console
# Inspect all templates
$ python scripts/inspect-templates.py

# Inspect specific templates
$ python scripts/inspect-templates.py --templates fastapi-default,fastapi-async-crud

# Verbose output with detailed information
$ python scripts/inspect-templates.py --verbose

# Save results to custom file
$ python scripts/inspect-templates.py --output my_results.json
```

#### Inspection flags

| Flag | Effect | Use it when |
|---|---|---|
| `--offline` | Skips every network lookup (dependency freshness reporting) | No network, or you want a fast, hermetic run |
| `--no-smoke` | Skips booting the generated project with uvicorn | Iterating on structure only; the smoke test is the slowest step |
| `--mypy` | Type-checks the generated project with mypy | Before submitting a template — it is opt-in because it is slow |
| `--templates` | Comma-separated list of templates to inspect | Working on one template |
| `--verbose` | Detailed output | Debugging a failure |
| `--output` | Path for the JSON result file | Keeping several runs side by side |

A quick local loop on a single template:

```console
$ python scripts/inspect-templates.py \
    --templates fastapi-sqlmodel --offline --no-smoke --verbose
```

...and the full check before opening a PR:

```console
$ python scripts/inspect-templates.py --templates fastapi-sqlmodel --mypy
```

### Using Makefile Commands

```console
# Inspect all templates
$ make inspect-templates

# Inspect with verbose output
$ make inspect-templates-verbose

# Inspect specific templates
$ make inspect-template TEMPLATES="fastapi-default,fastapi-async-crud"
```

## Inspection Results

- **Successful inspections** are logged in workflow outputs and artifacts
- **Failed inspections** automatically create GitHub issues with detailed error reports
- **Inspection history** is preserved for 30 days in GitHub Actions artifacts

## Understanding Inspection Output

When running template inspection, you'll see output like this:

```console
📋 Found 6 templates to inspect: fastapi-async-crud, fastapi-custom-response, fastapi-default, fastapi-dockerized, fastapi-empty, fastapi-psql-orm
============================================================
🔍 Inspecting template: fastapi-async-crud
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud
✅ fastapi-async-crud: PASSED
----------------------------------------
🔍 Inspecting template: fastapi-custom-response
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response
✅ fastapi-custom-response: PASSED
----------------------------------------
...
============================================================
📊 INSPECTION SUMMARY
   Total templates: 6
   ✅ Passed: 6
   ❌ Failed: 0
🎉 All templates passed inspection!
📄 Results saved to: template_inspection_results.json
```

## Template Requirements

For a template to pass inspection, it must meet these requirements:

### File Structure
- Must contain a `src/` directory with Python source files
- Python files must use `.py-tpl` extension
- Must include a `tests/` directory and a `README.md-tpl` file
- Must include `pyproject.toml-tpl` (PEP 621). Bundled templates are
  pyproject-first and no longer ship `setup.py-tpl`; inspection still accepts
  it so third-party templates keep working, but new templates must not add
  one.
- `requirements.txt-tpl` is optional when `pyproject.toml-tpl` declares
  `[project].dependencies` — but when both are present, they must agree
  (see *Configuration consistency*)
- Must target Python 3.12 consistently: `requires-python = ">=3.12"`, black
  `target-version = ["py312"]`, mypy `python_version = "3.12"`, and
  `python:3.12-slim` for any Docker base image
- Must not declare `FastAPI-fastkit` as a runtime dependency
- Must not leave any `<placeholder>` unsubstituted after generation

### FastAPI Requirements
- Must contain FastAPI app initialization
- Must declare `fastapi` as a dependency in at least one of
  `pyproject.toml-tpl` `[project].dependencies`, `requirements.txt-tpl`, or
  `setup.py-tpl` `install_requires`
- Must have valid Python syntax in all template files

### Identity Markers
Templates should carry FastAPI-fastkit identity markers so generated projects
are distinguishable from unrelated FastAPI projects in the user's workspace:

- `pyproject.toml-tpl` — both a `[FastAPI-fastkit templated]` prefix in
  `description` and a `[tool.fastapi-fastkit]` table with `managed = true`.
- `setup.py-tpl` — `[FastAPI-fastkit templated]` prefix in the `description`
  argument to `setup()`.

`is_fastkit_project()` accepts any one of these (pyproject takes precedence,
setup.py is the legacy fallback; matching is case-insensitive). Metadata
injection ensures the markers end up in generated projects even if a template
forgets them.

### Quality Standards
- All template files must be syntactically correct
- Dependencies must be properly specified
- Template structure must follow FastAPI-fastkit conventions

This automated quality assurance ensures that all templates remain reliable and ready for production use.

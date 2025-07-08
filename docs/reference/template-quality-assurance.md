# Template Quality Assurance

FastAPI-fastkit provides automated template validation to ensure all templates maintain high quality and remain functional.

## Automated Weekly Inspection

Every Wednesday at midnight (UTC), our GitHub Actions workflow automatically inspects all FastAPI templates to ensure they meet quality standards:

- ✅ **File Structure Validation** - Ensures all required files and directories are present
- ✅ **File Extension Verification** - Validates that template files use correct `.py-tpl` extensions
- ✅ **Dependency Checking** - Confirms FastAPI and required dependencies are properly defined
- ✅ **FastAPI Implementation** - Verifies that templates contain proper FastAPI app initialization
- ✅ **Test Execution** - Runs template tests to ensure functionality

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
- Must include a `requirements.txt-tpl` file
- Must include a `setup.py-tpl` file

### FastAPI Requirements
- Must contain FastAPI app initialization
- Must include proper dependency declarations
- Must have valid Python syntax in all template files

### Quality Standards
- All template files must be syntactically correct
- Dependencies must be properly specified
- Template structure must follow FastAPI-fastkit conventions

This automated quality assurance ensures that all templates remain reliable and ready for production use.

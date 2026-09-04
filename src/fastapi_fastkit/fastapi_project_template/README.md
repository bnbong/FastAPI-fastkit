# About fastapi project templates

Each fastapi demo project in this folder is pasted to the user's local folder with the FastAPI-fastkit replication as the source code is.

For those with experience in developing Django, it is easy to understand that it performs a similar operation to the `$ django-admin startproject <project-name>` cli-operation.

All source codes in demo projects must consist of **`.py-tpl`**, _not_ .py.

## Base structure of FastAPI template project

### Required Structure

```
template-name/
├── src/
│ ├── main.py-tpl
│ ├── config/
│ ├── models/
│ ├── routes/
│ └── utils/
├── tests/                    # required
├── scripts/
├── pyproject.toml-tpl        # required primary metadata file (PEP 621)
├── requirements.txt-tpl      # optional when pyproject.toml-tpl declares deps
└── README.md-tpl             # required
```

The minimum required files for a modern template are `tests/`, `README.md-tpl`,
and `pyproject.toml-tpl`. `requirements.txt-tpl` is optional when the
template's dependencies are declared under `[project].dependencies` in
`pyproject.toml-tpl`.

Templates are **pyproject-first**: as of v1.4.0 no bundled template ships a
`setup.py-tpl`, and new templates must not add one. Inspection still accepts
`setup.py-tpl` so third-party templates keep working, but it is a legacy
path.

Generated projects must **not** declare `FastAPI-fastkit` as a runtime
dependency — the CLI is a development tool, and a template's dependency list
should contain only what the generated application itself imports. Template
inspection fails a template that declares it.

Every template targets **Python 3.12**: `requires-python = ">=3.12"`, black
`target-version = ["py312"]`, mypy `python_version = "3.12"`, and
`python:3.12-slim` as the Docker base image.

### Key Requirements:

1. All source files must use `.py-tpl` extension
2. The template must declare `fastapi` as a dependency in at least one of:
   - `pyproject.toml-tpl` under `[project].dependencies` (preferred)
   - `requirements.txt-tpl`
   - `setup.py-tpl` under `install_requires`
3. `pyproject.toml-tpl` (preferred) should use PEP 621 metadata and carry the
   FastAPI-fastkit identity markers so that `is_fastkit_project()` can tell
   generated projects apart from unrelated FastAPI projects in the user's
   workspace:
   ```
   [project]
   name = "<project_name>"
   version = "0.1.0"
   description = "[FastAPI-fastkit templated] <description>"
   dependencies = [
       "fastapi>=0.115.0",
       ...
   ]

   [tool.fastapi-fastkit]
   managed = true
   ```
   The `[FastAPI-fastkit templated]` marker in `description` and the
   `[tool.fastapi-fastkit]` table are both recognized by detection (any one
   suffices; matching is case-insensitive). Metadata injection will also add
   these markers at project-generation time if a template forgets them, but
   authors should include them explicitly.
4. Legacy templates using `setup.py-tpl` should:
   - declare dependencies via a type-annotated `install_requires` list, e.g.
     ```
     install_requires: list[str] = [
        ...
     ]
     ```
   - include the `[FastAPI-fastkit templated]` marker in the project
     description. Detection falls back to a case-insensitive scan for
     `fastapi-fastkit` in `setup.py`, so this marker keeps legacy projects
     identifiable:
     ```
     setup(
        ...
        description = "[FastAPI-fastkit templated] <description>",
        ...
     )
     ```
5. Basic CRUD operations example
6. Unit tests implementation
7. API documentation (OpenAPI/Swagger)

## Available templates

| Template | When to choose |
|---|---|
| `fastapi-default` | Quick CRUD demo with the classic layered layout (`api/routes`, `crud`, `schemas`). Good first stop. |
| `fastapi-empty` | Minimal scaffold for users who want to add their own structure on top. |
| `fastapi-single-module` | Single-file sandbox for tiny prototypes / scripts. |
| `fastapi-custom-response` | Demonstrates custom response formatting / envelope patterns. |
| `fastapi-psql-orm` | PostgreSQL + SQLAlchemy + Alembic (synchronous); pick this for a Compose stack around a real database. |
| `fastapi-mcp` | Model Context Protocol integration. |
| `fastapi-domain-starter` | **Recommended modern default for medium-sized APIs.** Pyproject-first, domain-oriented layout (`src/app/domains/<concept>/`) with a clean transport / service / repository split, plus a built-in `/health` probe. |
| `fastapi-auth-jwt` | JWT authentication: access/refresh rotation tracked by `jti`, argon2id hashing, role and scope guards, SQLModel users, Alembic migrations. |
| `fastapi-sqlmodel` | Persistence-first: SQLModel over an async SQLAlchemy engine, async Alembic, a generic `CRUDBase`, paginated list endpoints. |
| `fastapi-llm-agent` | Streaming Claude chat agent: SSE token delivery, a tool-call loop with an iteration cap, conversation memory, offline tests. |
| `fastapi-async-crud` | ⚠️ **Deprecated.** Async-flavoured equivalent of `fastapi-default`; use `fastapi-sqlmodel` instead. |
| `fastapi-dockerized` | ⚠️ **Deprecated.** Added a production-ready Dockerfile to the default layout; every current template now ships one. |

Deprecated templates are still shipped and still generate working projects.
They are kept for existing users and are not recommended for new projects.

## Base structure of modules template

This template is used to create a new FastAPI project with a specific module structure.

This template strategy is used at `fastkit addroute` operation.

The module structure is as follows (version 1.0.X based):

```
modules/
├── api/
├── crud/
└── schemas/
```

In further versions, I don't have any plan to add other modules to this template, for example, `auth`, `db`, etc.

So, if you have any suggestions, please let me know or contribute to this operation.


## Adding new FastAPI-based template project

Before adding new FastAPI-based template project here, I strongly recommend that you read the
[SECURITY.md](../SECURITY.md) and [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) files to understand
the direction of this project and the precautions for cooperation.

Follow these steps when adding a new template:

1. Follow template structure
2. Pass inspector.py tests
3. Meet security requirements
4. Pre-PR checklist:
   - [ ] All files use .py-tpl extension
   - [ ] FastAPI-fastkit dependency included
   - [ ] Security requirements met
   - [ ] Tests implemented and passing
   - [ ] Documentation complete
   - [ ] inspector.py validation passes

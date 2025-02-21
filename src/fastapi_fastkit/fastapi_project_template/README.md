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
├── tests/
├── scripts/
├── requirements.txt-tpl
├── setup.py-tpl
└── README.md-tpl
```

### Key Requirements:

1. All source files must use `.py-tpl` extension
2. `setup.py` must include `fastapi-fastkit` string in project description
   for example:
   ```
   ...
   setup(
      ...
      description = "[fastapi-fastkit templated] <description>",
      ...
   )
   ```
3. `setup.py` must include `install_requires` section, it must include essential dependencies for the template project. Also, note that install_requires list must be type annotated.
   for example:
   ```
   ...
   install_requires: list[str] = [
      ...
   ],
   ```
4. Basic CRUD operations example
5. Unit tests implementation
6. API documentation (OpenAPI/Swagger)

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
   - [ ] README.md follows template
   - [ ] Security requirements met
   - [ ] Tests implemented and passing
   - [ ] Documentation complete
   - [ ] inspector.py validation passes

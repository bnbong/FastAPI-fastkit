<p align="center">
    <img align="top" width="70%" src="https://bnbong.github.io/projects/img/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>: Fast, easy-to-use starter kit for new users of Python and FastAPI</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-fastkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-fastkit" alt="PyPI - Version">
</a>
<a href="https://github.com/bnbong/FastAPI-fastkit/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/bnbong/FastAPI-fastkit" alt="GitHub Release">
</a>
</p>

---

This project was created to speed up the configuration of the development environment needed to develop Python-based web apps for new users of Python and [FastAPI](https://github.com/fastapi/fastapi).

This project was inspired by the `SpringBoot initializer` & Python Django's `django-admin` cli operation.

## Key Features

- **⚡ Immediate FastAPI project creation** : Super-fast FastAPI workspace & project creation via CLI, inspired by `django-admin` feature of [Python Django](https://github.com/django/django)
- **🎨 Prettier CLI outputs** : Beautiful CLI experience powered by [rich library](https://github.com/Textualize/rich)
- **📋 Standards-based FastAPI project templates** : All FastAPI-fastkit templates are based on Python standards and FastAPI's common use patterns
- **🔍 Automated template quality assurance** : Weekly automated testing ensures all templates remain functional and up-to-date
- **🚀 Multiple project templates** : Choose from various pre-configured templates for different use cases (async CRUD, Docker, PostgreSQL, etc.)

## Installation

Install `FastAPI-fastkit` at your Python environment.

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## Usage

### Create a new FastAPI project workspace environment immediately

You can now start new FastAPI project really fast with FastAPI-fastkit!

Create a new FastAPI project workspace immediately with:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI project

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-awesome-project         │
│ Author       │ John Doe                   │
│ Author Email │ john@example.com           │
│ Description  │ My awesome FastAPI project │
└──────────────┴────────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal
Do you want to proceed with project creation? [y/N]: y
FastAPI project will deploy at '~your-project-path~'

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into setup.py                    │
╰──────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into config file                 │
╰──────────────────────────────────────────────────────╯

        Creating Project:
       my-awesome-project
┌───────────────────┬───────────┐
│ Component         │ Collected │
│ fastapi           │ ✓         │
│ uvicorn           │ ✓         │
│ pydantic          │ ✓         │
│ pydantic-settings │ ✓         │
└───────────────────┴───────────┘

Creating virtual environment...

╭──────────────────────── Info ────────────────────────╮
│ ℹ venv created at                                    │
│ ~your-project-path~/my-awesome-project/.venv         │
│ To activate the virtual environment, run:            │
│                                                      │
│     source                                           │
│ ~your-project-path~/my-awesome-project/.venv/bin/act │
│ ivate                                                │
╰──────────────────────────────────────────────────────╯

Installing dependencies...
⠙ Setting up project environment...Collecting <packages~>

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-project' has been      │
│ created successfully and saved to                     │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ To start your project, run 'fastkit runserver' at  │
│ newly created FastAPI project directory              │
╰──────────────────────────────────────────────────────╯
```

</div>

This command will create a new FastAPI project workspace environment with Python virtual environment.

### Add a new route to the FastAPI project

`FastAPI-fastkit` makes it easy to expand your FastAPI project.

Add a new route endpoint to your FastAPI project with:

<div class="termy">

```console
$ fastkit addroute my-awesome-project user
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-awesome-project                       │
│ Route Name       │ user                                     │
│ Target Directory │ ~your-project-path~                      │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to project 'my-awesome-project'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'user' to project     │
│ `my-awesome-project`                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

### Place a structured FastAPI demo project immediately

You can also start with a structured FastAPI demo project.

Demo projects are consist of various tech stacks with simple item CRUD endpoints implemented.

Place a structured FastAPI demo project immediately with:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-awesome-demo
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI demo
Deploying FastAPI project using 'fastapi-default' template
Template path:
/~fastapi_fastkit-package-path~/fastapi_project_template/fastapi-default

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-demo         │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ My awesome FastAPI demo │
└──────────────┴─────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Do you want to proceed with project creation? [y/N]: y
FastAPI template project will deploy at '~your-project-path~'

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-demo' from             │
│ 'fastapi-default' has been created and saved to       │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

To view the list of available FastAPI demos, check with:

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-custom-response │ Async Item Management API with    │
│                         │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI Item           │
│                         │ Management API                    │
│ fastapi-empty           │ No description                    │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-psql-orm        │ Dockerized FastAPI Item           │
│                         │ Management API with PostgreSQL    │
│ fastapi-default         │ Simple FastAPI Project            │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

## Documentation

For comprehensive guides and detailed usage instructions, explore our documentation:

- 📚 **[User Guide](user-guide/quick-start.md)** - Detailed installation and usage guides
- 🎯 **[Tutorial](tutorial/getting-started.md)** - Step-by-step tutorials for beginners
- 📖 **[CLI Reference](user-guide/cli-reference.md)** - Complete command reference
- 🔍 **[Template Quality Assurance](reference/template-quality-assurance.md)** - Automated testing and quality standards

## Contributing

We welcome contributions from the community! FastAPI-fastkit is designed to help newcomers to Python and FastAPI, and your contributions can make a significant impact.

### What You Can Contribute

- 🚀 **New FastAPI templates** - Add templates for different use cases
- 🐛 **Bug fixes** - Help us improve stability and reliability
- 📚 **Documentation** - Improve guides, examples, and translations
- 🧪 **Tests** - Increase test coverage and add integration tests
- 💡 **Features** - Suggest and implement new CLI features

### Getting Started with Contributing

To get started with contributing to FastAPI-fastkit, please refer to our comprehensive guides:

- **[Development Setup](contributing/development-setup.md)** - Complete guide for setting up your development environment
- **[Code Guidelines](contributing/code-guidelines.md)** - Coding standards and best practices
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** - Comprehensive contribution guide
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** - Project principles and community standards
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** - Security guidelines and reporting

## Significance of FastAPI-fastkit

FastAPI-fastkit aims to provide a fast and easy-to-use starter kit for new users of Python and FastAPI.

This idea was initiated with the aim of helping FastAPI newcomers learn from the beginning, which aligns with the production significance of the FastAPI-cli package added with the [FastAPI 0.111.0 version update](https://github.com/fastapi/fastapi/releases/tag/0.111.0).

As someone who has been using and loving FastAPI for a long time, I wanted to develop a project that could help fulfill [the wonderful motivation](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) that FastAPI developer [tiangolo](https://github.com/tiangolo) has expressed.

FastAPI-fastkit bridges the gap between getting started and building production-ready applications by providing:

- **Immediate productivity** for newcomers who might be overwhelmed by setup complexity
- **Best practices** built into every template, helping users learn proper FastAPI patterns
- **Scalable foundations** that grow with users as they advance from beginners to experts
- **Community-driven templates** that reflect real-world FastAPI usage patterns

## Next Steps

Ready to get started with FastAPI-fastkit? Follow these next steps:

### 🚀 Quick Start

1. **[Installation](user-guide/installation.md)**: Install FastAPI-fastkit
2. **[Quick Start](user-guide/quick-start.md)**: Create your first project in 5 minutes
3. **[Getting Started Tutorial](tutorial/getting-started.md)**: Step-by-step detailed tutorial

### 📚 Advanced Learning

- **[Creating Projects](user-guide/creating-projects.md)**: Create projects with different stacks
- **[Adding Routes](user-guide/adding-routes.md)**: Add API endpoints to your project
- **[Using Templates](user-guide/using-templates.md)**: Use pre-built project templates

### 🛠️ Contributing

Want to contribute to FastAPI-fastkit?

- **[Development Setup](contributing/development-setup.md)**: Set up your development environment
- **[Code Guidelines](contributing/code-guidelines.md)**: Follow our coding standards and best practices
- **[Contributing Guidelines](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)**: Comprehensive contribution guide

### 🔍 Reference

- **[CLI Reference](user-guide/cli-reference.md)**: Complete CLI command reference
- **[Template Quality Assurance](reference/template-quality-assurance.md)**: Automated testing and quality standards
- **[FAQ](reference/faq.md)**: Frequently asked questions
- **[GitHub Repository](https://github.com/bnbong/FastAPI-fastkit)**: Source code and issue tracking

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) file for details.

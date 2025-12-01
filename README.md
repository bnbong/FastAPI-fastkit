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
<a href="https://codecov.io/gh/bnbong/FastAPI-fastkit" >
    <img src="https://codecov.io/gh/bnbong/FastAPI-fastkit/graph/badge.svg?token=WS0B6WWD8K"/>
</a>
<a href="https://pepy.tech/project/fastapi-fastkit">
    <img src="https://static.pepy.tech/personalized-badge/fastapi-fastkit?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
</a>
</p>

---

This project was created to speed up the configuration of the development environment needed to develop Python-based web apps for new users of Python and [FastAPI](https://github.com/fastapi/fastapi).

This project was inspired by the `SpringBoot initializer` & Python Django's `django-admin` CLI operation.

## Key Features

- **⚡ Immediate FastAPI project creation** : Super-fast FastAPI workspace & project creation via CLI, inspired by `django-admin` feature of [Python Django](https://github.com/django/django)
- **✨ Interactive project builder**: Guided step-by-step feature selection for databases, authentication, caching, monitoring, and more with auto-generated code
- **🎨 Prettier CLI output** : Beautiful CLI experience powered by [rich library](https://github.com/Textualize/rich)
- **📋 Standards-based FastAPI project templates** : Templates follow Python standards and common FastAPI patterns.
- **🔍 Automated template quality assurance** : Weekly automated testing ensures all templates remain functional and up-to-date
- **🚀 Multiple project templates** : Choose from various pre-configured templates for different use cases (async CRUD, Docker, PostgreSQL, etc.)
- **📦 Multiple package manager support** : Choose your preferred Python package manager (pip, uv, pdm, poetry) for dependency management

## Installation

Install `FastAPI-fastkit` in your Python environment.

```console
$ pip install FastAPI-fastkit
```


## Usage

- Global options
  - `--help`: Show help
  - `--version`: Show version
  - `--debug/--no-debug`: Toggle debug mode

### Create a new FastAPI project
```console
fastkit init [OPTIONS]
```
- What it does: Scaffolds an empty FastAPI project, creates a virtual environment, installs dependencies
- Key options:
  - `--project-name`, `--author`, `--author-email`, `--description`
  - `--package-manager` [pip|uv|pdm|poetry]
  - Stack selection: `minimal` | `standard` | `full` (interactive)

### Create a project with interactive mode
```console
fastkit init --interactive
```
- What it does: Guided step-by-step project setup with intelligent feature selection
- Features:
  - **Database selection**: PostgreSQL, MySQL, MongoDB, Redis, SQLite
  - **Authentication**: JWT, OAuth2, FastAPI-Users, Session-based
  - **Background tasks**: Celery, Dramatiq
  - **Caching**: Redis, fastapi-cache2
  - **Monitoring**: Loguru, OpenTelemetry, Prometheus
  - **Testing**: Basic (pytest), Coverage, Advanced (with faker, factory-boy)
  - **Utilities**: CORS, Rate-Limiting, Pagination, WebSocket
  - **Deployment**: Docker, docker-compose with auto-generated configs
  - **Package manager**: pip, uv, pdm, poetry
  - **Custom packages**: Add your own dependencies
- Auto-generates:
  - `main.py` with selected features integrated
  - Database and authentication configuration files
  - Docker deployment files (Dockerfile, docker-compose.yml)
  - Test configuration (pytest with coverage)

### Create a project from a template
```console
fastkit startdemo [TEMPLATE] [OPTIONS]
```
- What it does: Creates a project from a template (e.g., `fastapi-default`) and installs dependencies
- Key options:
  - `--project-name`, `--author`, `--author-email`, `--description`
  - `--package-manager` [pip|uv|pdm|poetry]
- Tip: List available templates with `fastkit list-templates`

### Add a new route
```console
fastkit addroute <project_name> <route_name>
```
- What it does: Adds a new API route to the specified project

### Run the development server
```console
fastkit runserver [OPTIONS]
```
- What it does: Starts the uvicorn development server
- Key options:
  - `--host`, `--port`, `--reload/--no-reload`, `--workers`

### List templates
```console
fastkit list-templates
```

### Delete a project
```console
fastkit deleteproject <project_name>
```

## Documentation

For comprehensive guides and detailed usage instructions, visit our documentation:

- 📚 **[User Guide](https://bnbong.github.io/FastAPI-fastkit/user-guide/quick-start/)** - Detailed installation and usage guides
- 🎯 **[Tutorial](https://bnbong.github.io/FastAPI-fastkit/tutorial/getting-started/)** - Step-by-step tutorials for beginners
- 📖 **[CLI Reference](https://bnbong.github.io/FastAPI-fastkit/user-guide/cli-reference/)** - Complete command reference
- 🔍 **[Template Quality Assurance](https://bnbong.github.io/FastAPI-fastkit/reference/template-quality-assurance/)** - Automated testing and quality standards

## Contributing

We welcome contributions from the community! FastAPI-fastkit is designed to help newcomers to Python and FastAPI, and your contributions can make a significant impact.

<details>
<summary><b>Contributing Guide</b></summary>

### Quick Start for Contributors

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/bnbong/FastAPI-fastkit.git
   cd FastAPI-fastkit
   ```

2. **Set up development environment:**
   ```bash
   make dev-setup  # Sets up everything you need
   ```

3. **Run development checks:**
   ```bash
   make dev-check  # Format, lint, and test
   ```

### What You Can Contribute

- 🚀 **New FastAPI templates** - Add templates for different use cases
- 🐛 **Bug fixes** - Help us improve stability and reliability
- 📚 **Documentation** - Improve guides, examples, and translations
- 🧪 **Tests** - Increase test coverage and add integration tests
- 💡 **Features** - Suggest and implement new CLI features

### Contribution Guidelines

For detailed contribution guidelines, development setup, and project standards, please refer to:

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Comprehensive contribution guide
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Project principles and community standards
- **[SECURITY.md](SECURITY.md)** - Security guidelines and reporting

</details>

## Significance of FastAPI-fastkit

FastAPI-fastkit aims to provide a fast and easy-to-use starter kit for new users of Python and FastAPI.

This idea was initiated with the aim of helping FastAPI newcomers learn from the beginning, which aligns with the production significance of the FastAPI CLI package added with the [FastAPI 0.111.0 version update](https://github.com/fastapi/fastapi/releases/tag/0.111.0).

As someone who has been using and loving FastAPI for a long time, I wanted to develop a project that could help fulfill [the wonderful motivation](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) that FastAPI developer [tiangolo](https://github.com/tiangolo) has expressed.

FastAPI-fastkit bridges the gap between getting started and building production-ready applications by providing:

- **Immediate productivity** for newcomers who might be overwhelmed by setup complexity
- **Best practices** built into every template, helping users learn proper FastAPI patterns
- **Scalable foundations** that grow with users as they advance from beginners to experts
- **Community-driven templates** that reflect real-world FastAPI usage patterns

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) file for details.

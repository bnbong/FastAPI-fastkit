<p align="center">
    <img align="top" width="70%" src="https://bnbong.github.io/projects/img/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>：面向 Python 与 FastAPI 新手的快速、易用启动套件</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-fastkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-fastkit" alt="PyPI - Version">
</a>
<a href="https://github.com/bnbong/FastAPI-fastkit/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/bnbong/FastAPI-fastkit" alt="GitHub Release">
</a>
<a href="https://pepy.tech/project/fastapi-fastkit">
    <img src="https://static.pepy.tech/personalized-badge/fastapi-fastkit?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
</a>
</p>

---

本项目旨在帮助 Python 与 [FastAPI](https://github.com/fastapi/fastapi) 新手更快完成基于 Python 的 Web 应用开发环境配置。

本项目的灵感来自 `Spring Boot Initializr` 以及 Django 的 `django-admin` CLI 工具。

!!! info "翻译状态"
    英文是本文档的权威来源。语言切换器中的其他语言可能尚未完整翻译,缺失页面会按页回退到英文。请参阅 [翻译状态](reference/translation-status.md) 了解各语言版本的实际覆盖情况。

## 主要特性

- **⚡ 即时创建 FastAPI 项目**：通过 CLI 快速创建 FastAPI 工作区与项目,灵感来自 [Django](https://github.com/django/django) 的 `django-admin`
- **✨ 交互式项目构建器**：对数据库、认证、缓存、监控等进行分步引导式选择,并自动生成代码
- **🎨 更美观的 CLI 输出**：基于 [rich](https://github.com/Textualize/rich) 提供更好的 CLI 体验
- **📋 基于标准的 FastAPI 项目模板**：所有 FastAPI-fastkit 模板都遵循 Python 标准与 FastAPI 常见实践
- **🔍 自动化的模板质量保障**：通过每周自动化测试,确保所有模板始终可用并保持更新
- **🚀 多种项目模板**：提供多种预配置模板,覆盖 async CRUD、Docker、PostgreSQL 等不同使用场景
- **📦 支持多种包管理器**：可选用您偏好的 Python 包管理器(pip、uv、pdm、poetry)管理依赖

## 安装

请在您的 Python 环境中安装 `FastAPI-fastkit`。

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## 使用方法

### 立即创建新的 FastAPI 项目工作区

现在您可以使用 FastAPI-fastkit 快速启动一个新的 FastAPI 项目。

使用下面的命令即可创建新的 FastAPI 项目工作区：

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

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
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

该命令将创建一个包含 Python 虚拟环境的新 FastAPI 项目工作区。

### 使用交互模式创建项目 ✨ 新功能

如果项目需求更复杂,可以使用 **交互模式** 通过功能选择一步步搭建 FastAPI 应用：

<div class="termy">

```console
$ fastkit init --interactive

⚡ FastAPI-fastkit Interactive Project Setup ⚡

📋 Basic Project Information
Enter the project name: my-fullstack-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Full-stack FastAPI project with PostgreSQL and JWT

🧱 Architecture Preset
Pick a project layout. Press Enter to accept the recommended default.
  1. minimal           - Smallest viable FastAPI app
  2. single-module     - Everything in one module (prototypes / scripts)
  3. classic-layered   - api/routes + crud + schemas + core (à la fastapi-default)
  4. domain-starter    - Domain-oriented src/app/domains/<concept>/ (recommended)

Select architecture preset: [4]

🗄️ Database Selection
Select database (PostgreSQL, MySQL, MongoDB, Redis, SQLite, None):
  1. PostgreSQL - PostgreSQL database with SQLAlchemy
  2. MySQL - MySQL database with SQLAlchemy
  3. MongoDB - MongoDB with motor async driver
  4. Redis - Redis for caching and session storage
  5. SQLite - SQLite database for development
  6. None - No database

Select database: 1

🔐 Authentication Selection
Select authentication (JWT, OAuth2, FastAPI-Users, Session-based, None):
  1. JWT - JSON Web Token authentication
  2. OAuth2 - OAuth2 with password flow
  3. FastAPI-Users - Full featured user management
  4. Session-based - Cookie-based sessions
  5. None - No authentication

Select authentication: 1

⚙️ Background Tasks Selection
Select background tasks (Celery, Dramatiq, None):
  1. Celery - Distributed task queue
  2. Dramatiq - Fast and reliable task processing
  3. None - No background tasks

Select background tasks: 1

💾 Caching Selection
Select caching (Redis, fastapi-cache2, None):
  1. Redis - Redis caching
  2. fastapi-cache2 - Simple caching for FastAPI
  3. None - No caching

Select caching: 1

📊 Monitoring Selection
Select monitoring (Loguru, OpenTelemetry, Prometheus, None):
  1. Loguru - Simple and powerful logging
  2. OpenTelemetry - Observability framework
  3. Prometheus - Metrics and monitoring
  4. None - No monitoring

Select monitoring: 3

🧪 Testing Framework Selection
Select testing framework (Basic, Coverage, Advanced, None):
  1. Basic - pytest + httpx for API testing
  2. Coverage - Basic + code coverage
  3. Advanced - Coverage + faker + factory-boy for fixtures
  4. None - No testing framework

Select testing framework: 2

🛠️ Additional Utilities
Select utilities (comma-separated numbers, e.g., 1,3,4):
  1. CORS - Cross-Origin Resource Sharing
  2. Rate-Limiting - Request rate limiting
  3. Pagination - Pagination support
  4. WebSocket - WebSocket support

Select utilities: 1

🚀 Deployment Configuration
Select deployment option:
  1. Docker - Generate Dockerfile
  2. docker-compose - Generate docker-compose.yml (includes Docker)
  3. None - No deployment configuration

Select deployment option: 2

📦 Package Manager Selection
Select package manager (pip, uv, pdm, poetry): uv

📝 Custom Packages (optional)
Enter custom package names (comma-separated, press Enter to skip):

📋 Project Configuration Summary
┌─────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Setting             │ Value                                                                     │
├─────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ Project Name        │ my-fullstack-project                                                      │
│ Author              │ John Doe                                                                  │
│ Email               │ john@example.com                                                          │
│ Description         │ Full-stack FastAPI project with PostgreSQL and JWT                        │
│ Architecture Preset │ domain-starter — Domain-oriented: src/app/domains/<concept>/ (recommended)│
│ Database            │ PostgreSQL                                                                │
│ Authentication      │ JWT                                                                       │
│ Async Tasks         │ Celery                                                                    │
│ Caching             │ Redis                                                                     │
│ Monitoring          │ Prometheus                                                                │
│ Testing             │ Coverage                                                                  │
│ Utilities           │ CORS                                                                      │
│ Package Manager     │ uv                                                                        │
└─────────────────────┴───────────────────────────────────────────────────────────────────────────┘

Total dependencies to install: 18

Proceed with project creation? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into pyproject.toml              │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated dependency file with 18 packages         │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Preserving template-shipped main.py for preset     │
│ 'domain-starter'.                                    │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated Docker deployment files                  │
╰───────────────────────────────────────────────────────╯
╭────────────────────── Warning ────────────────────────╮
│ ⚠ Preset compatibility                               │
│ fastapi-domain-starter's shipped src/app/main.py is  │
│ preserved. The selections below need manual wiring   │
│ there (CORS is already wired — set                   │
│ BACKEND_CORS_ORIGINS in .env to activate it).        │
│ Affected selections (packages installed, but no      │
│ dynamic main.py edits applied for the                │
│ 'domain-starter' preset): Prometheus                 │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated configuration files for selected stack   │
╰───────────────────────────────────────────────────────╯

Creating virtual environment...
Installing dependencies...

----> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-fullstack-project' from        │
│ 'fastapi-domain-starter' has been created!            │
╰───────────────────────────────────────────────────────╯
```

</div>

交互模式提供：

- **架构预设选择**(`minimal` / `single-module` / `classic-layered` / `domain-starter`),用于决定基础模板与项目布局
- **引导式功能选择**,覆盖数据库、认证、后台任务、缓存、监控等配置
- **自动生成代码** —— 会根据预设行为有所不同(`minimal` / `single-module` 会重新生成 `main.py`;`classic-layered` / `domain-starter` 会保留模板自带的 `main.py` 并补充配置模块)
- **感知预设的 Docker 生成** —— 生成的 `Dockerfile` 中 `CMD` 会指向当前预设真正的入口点(`src.main:app` 或 `src.app.main:app`)
- **智能依赖管理**,自动兼容 pip
- **功能校验**,当预设无法自动完成接入时会给出手动处理提示
- **项目身份标识** 会写入生成的 `pyproject.toml`(description 标识 + `[tool.fastapi-fastkit]` 节),便于后续由 `is_fastkit_project()` 识别生成的项目

### 向 FastAPI 项目添加新路由

`FastAPI-fastkit` 让扩展 FastAPI 项目变得更简单。

使用以下命令向您的 FastAPI 项目添加一个新的路由端点:

<div class="termy">

```console
$ fastkit addroute user my-awesome-project
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

### 立即部署一个结构化的 FastAPI 示例项目

您也可以从一个结构完整的 FastAPI 示例项目开始。

这些示例项目覆盖不同技术栈,并内置了简单的 item CRUD 端点实现。

使用下面的命令即可创建一个结构完整的 FastAPI 示例项目：

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

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
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

如需查看可用的 FastAPI 示例列表,请运行:

<div class="termy">

```console
$ fastkit list-templates
                              Available Templates
┌────────────────────────┬───────────────────────────────────────────────────────┐
│ fastapi-custom-response│ Async Item Management API with Custom Response System │
│ fastapi-mcp            │ FastAPI MCP Project                                   │
│ fastapi-domain-starter │ FastAPI Domain Starter                                │
│ fastapi-dockerized     │ Dockerized FastAPI Item Management API                │
│ fastapi-empty          │ Minimal FastAPI Template                              │
│ fastapi-async-crud     │ Async Item Management API Server                      │
│ fastapi-psql-orm       │ Dockerized FastAPI Item Management API with           │
│                        │ PostgreSQL                                            │
│ fastapi-default        │ Simple FastAPI Project                                │
│ fastapi-single-module  │ FastAPI Single Module Template                        │
└────────────────────────┴───────────────────────────────────────────────────────┘
```

</div>

## 文档

如需更完整的指南与详细使用说明,请查阅我们的文档:

- 📚 **[用户指南](user-guide/quick-start.md)** —— 详细的安装与使用指南
- 🎯 **[教程](tutorial/getting-started.md)** —— 面向新手的分步教程
- 📖 **[CLI 参考](user-guide/cli-reference.md)** —— 完整的命令参考
- 🔍 **[模板质量保障](reference/template-quality-assurance.md)** —— 自动化测试与质量标准

## 🚀 基于模板的教程

通过我们的预构建模板,在实际用例中学习 FastAPI 开发:

### 📖 核心教程

- **[构建基础 API 服务器](tutorial/basic-api-server.md)** —— 使用 `fastapi-default` 模板创建您的第一个 FastAPI 服务器
- **[构建异步 CRUD API](tutorial/async-crud-api.md)** —— 使用 `fastapi-async-crud` 模板开发高性能异步 API
- **[领域驱动项目(Domain Starter)](tutorial/domain-starter.md)** —— 使用 `fastapi-domain-starter` 模板构建中型规模的 API,这是推荐的现代默认选项

### 🗄️ 数据库与基础设施

- **[集成数据库](tutorial/database-integration.md)** —— 借助 `fastapi-psql-orm` 模板使用 PostgreSQL + SQLAlchemy
- **[Docker 化与部署](tutorial/docker-deployment.md)** —— 借助 `fastapi-dockerized` 模板搭建生产部署环境

### ⚡ 高级功能

- **[自定义响应处理与高级 API 设计](tutorial/custom-response-handling.md)** —— 借助 `fastapi-custom-response` 模板构建企业级 API
- **[集成 MCP](tutorial/mcp-integration.md)** —— 借助 `fastapi-mcp` 模板创建与 AI 模型集成的 API 服务器

每个教程包含:

- ✅ **实用示例** —— 可直接用于真实项目的代码
- ✅ **分步指南** —— 详细的说明,易于新手跟随
- ✅ **最佳实践** —— 行业标准模式与安全考量
- ✅ **拓展方法** —— 帮助您将项目推向新阶段

## 贡献

我们欢迎社区的贡献!FastAPI-fastkit 旨在帮助 Python 与 FastAPI 的新手,而您的贡献能带来巨大的影响。

### 您可以贡献什么

- 🚀 **新的 FastAPI 模板** —— 为不同的场景添加模板
- 🐛 **修复缺陷** —— 帮助我们提升稳定性与可靠性
- 📚 **文档** —— 改进指南、示例与翻译
- 🧪 **测试** —— 提高测试覆盖率,补充集成测试
- 💡 **功能** —— 提议并实现新的 CLI 功能

### 如何开始贡献

要开始为 FastAPI-fastkit 贡献,请参考我们的完整指南:

- **[开发环境设置](contributing/development-setup.md)** —— 配置开发环境的完整指南
- **[代码规范](contributing/code-guidelines.md)** —— 编码标准与最佳实践
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** —— 完整的贡献指南
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** —— 项目原则与社区准则
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** —— 安全指引与上报方式

## FastAPI-fastkit 的意义

FastAPI-fastkit 的目标是为 Python 与 FastAPI 的新手提供一个快速、易用的启动套件。

这个想法的初衷,是帮助 FastAPI 新手从一开始就轻松上手 —— 这与 [FastAPI 0.111.0 版本更新](https://github.com/fastapi/fastapi/releases/tag/0.111.0) 中加入的 FastAPI-cli 包对生产环境的意义不谋而合。

作为一名长期使用并热爱 FastAPI 的开发者,我希望开发一个项目,可以帮助实现 FastAPI 开发者 [tiangolo](https://github.com/tiangolo) 所表达的 [那份美好初衷](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417)。

FastAPI-fastkit 通过以下几点,在「快速上手」与「构建生产级应用」之间架起桥梁:

- **新手即可立刻获得生产力**,不再被复杂的配置流程吓退
- **每个模板内置最佳实践**,帮助使用者学习正确的 FastAPI 模式
- **可扩展的基础**,陪伴使用者从新手成长为专家
- **社区驱动的模板**,反映真实世界的 FastAPI 使用模式

## 下一步

准备好开始使用 FastAPI-fastkit 了吗?请按以下步骤继续:

### 🚀 快速开始

1. **[安装](user-guide/installation.md)**:安装 FastAPI-fastkit
2. **[快速上手](user-guide/quick-start.md)**:5 分钟内创建您的第一个项目
3. **[入门教程](tutorial/getting-started.md)**:分步详细教程

### 📚 进阶学习

- **[创建项目](user-guide/creating-projects.md)**:使用不同的技术栈创建项目
- **[添加路由](user-guide/adding-routes.md)**:为您的项目添加 API 端点
- **[使用模板](user-guide/using-templates.md)**:使用预构建的项目模板

### 🛠️ 参与贡献

想要为 FastAPI-fastkit 做贡献?

- **[开发环境设置](contributing/development-setup.md)**:配置您的开发环境
- **[代码规范](contributing/code-guidelines.md)**:遵循我们的编码标准与最佳实践
- **[贡献指南](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)**:完整的贡献指南

### 🔍 参考

- **[CLI 参考](user-guide/cli-reference.md)**:完整的 CLI 命令参考
- **[模板质量保障](reference/template-quality-assurance.md)**:自动化测试与质量标准
- **[FAQ](reference/faq.md)**:常见问题解答
- **[GitHub 仓库](https://github.com/bnbong/FastAPI-fastkit)**:源代码与问题跟踪

## 许可证

本项目采用 MIT 许可证 —— 详细信息见 [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) 文件。

<p align="center">
    <img align="top" width="70%" src=".github/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b>: schnelles, einfach zu nutzendes Starter-Kit für Neulinge in Python und FastAPI</em>
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

Dieses Projekt wurde entwickelt, um die Konfiguration der Entwicklungsumgebung zu beschleunigen, die für die Entwicklung von Python-basierten Web-Apps für Neulinge in Python und [FastAPI](https://github.com/fastapi/fastapi) nötig ist.

Inspiriert wurde dieses Projekt vom `SpringBoot initializer` und vom CLI-Werkzeug `django-admin` von Python Django.

!!! info "Übersetzungsstatus"
    Englisch ist die maßgebliche Quelle dieser Dokumentation. Andere Sprachen im Sprachumschalter können unvollständig sein oder seitenweise auf die englische Version zurückfallen. Siehe [Übersetzungsstatus](reference/translation-status.md) für die tatsächliche Abdeckung jeder Locale.

## Hauptmerkmale

- **⚡ Sofortige Erstellung von FastAPI-Projekten**: blitzschnelles Anlegen von FastAPI-Workspaces und -Projekten über CLI, inspiriert vom `django-admin`-Werkzeug von [Python Django](https://github.com/django/django)
- **✨ Interaktiver Projekt-Builder**: geführte schrittweise Auswahl von Funktionen für Datenbanken, Authentifizierung, Caching, Monitoring und mehr, mit automatisch generiertem Code
- **🎨 Schönere CLI-Ausgaben**: ansprechende CLI-Erfahrung dank der [rich-Bibliothek](https://github.com/Textualize/rich)
- **📋 Auf Standards basierende FastAPI-Projektvorlagen**: alle Vorlagen von FastAPI-fastkit folgen Python-Standards und den verbreiteten FastAPI-Nutzungsmustern
- **🔍 Automatisierte Qualitätssicherung der Vorlagen**: wöchentliche automatisierte Tests stellen sicher, dass alle Vorlagen funktionsfähig und aktuell bleiben
- **🚀 Mehrere Projektvorlagen**: Auswahl aus verschiedenen vorkonfigurierten Vorlagen für unterschiedliche Anwendungsfälle (async CRUD, Docker, PostgreSQL usw.)
- **📦 Unterstützung mehrerer Paketmanager**: wählen Sie Ihren bevorzugten Python-Paketmanager (pip, uv, pdm, poetry) für die Verwaltung der Abhängigkeiten

## Installation

Installieren Sie `FastAPI-fastkit` in Ihrer Python-Umgebung.

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## Nutzung

### Sofort eine neue FastAPI-Projekt-Workspace-Umgebung erstellen

Sie können jetzt sehr schnell ein neues FastAPI-Projekt mit FastAPI-fastkit starten!

Erstellen Sie sofort einen neuen FastAPI-Projekt-Workspace mit:

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

Dieser Befehl erstellt eine neue FastAPI-Projekt-Workspace-Umgebung mit einer virtuellen Python-Umgebung.

### Ein Projekt im interaktiven Modus erstellen ✨ NEU!

Für komplexere Projekte nutzen Sie den **interaktiven Modus**, um Ihre FastAPI-Anwendung Schritt für Schritt mit intelligenter Funktionsauswahl aufzubauen:

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

Der interaktive Modus bietet:

- **Auswahl eines Architektur-Presets** (`minimal` / `single-module` / `classic-layered` / `domain-starter`), das die passende Basisvorlage und das Projekt-Layout auswählt
- **Geführte Auswahl** für Datenbanken, Authentifizierung, Hintergrundaufgaben, Caching, Monitoring und mehr
- **Automatisch generierter Code** für die ausgewählten Funktionen — je nach Preset unterschiedlich (regenerierte `main.py` für `minimal` / `single-module`; bei `classic-layered` / `domain-starter` bleibt die mitgelieferte `main.py` erhalten und passende Konfigurationsmodule werden ergänzt)
- **Docker-Generierung passend zum gewählten Preset** — das `CMD` des generierten `Dockerfile` verweist auf den tatsächlichen Einstiegspunkt des Presets (`src.main:app` oder `src.app.main:app`)
- **Intelligente Verwaltung der Abhängigkeiten** mit automatischer pip-Kompatibilität
- **Funktionsvalidierung** mit Hinweisen auf manuelle Verkabelung für Auswahlmöglichkeiten, die das Preset nicht automatisch verdrahten kann
- **Identitätsmarker** in der generierten `pyproject.toml` (Beschreibungs-Marker + `[tool.fastapi-fastkit]`-Tabelle), damit `is_fastkit_project()` generierte Projekte später wiedererkennt

### Eine neue Route zum FastAPI-Projekt hinzufügen

`FastAPI-fastkit` macht es einfach, Ihr FastAPI-Projekt zu erweitern.

Fügen Sie einen neuen Routen-Endpunkt zu Ihrem FastAPI-Projekt hinzu mit:

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

### Sofort ein strukturiertes FastAPI-Demoprojekt anlegen

Sie können auch mit einem strukturierten FastAPI-Demoprojekt starten.

Demoprojekte bestehen aus verschiedenen Tech-Stacks mit implementierten einfachen Item-CRUD-Endpunkten.

Legen Sie sofort ein strukturiertes FastAPI-Demoprojekt an mit:

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

Um die Liste der verfügbaren FastAPI-Demos anzuzeigen, prüfen Sie mit:

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

## Dokumentation

Für umfassende Anleitungen und detaillierte Nutzungshinweise erkunden Sie unsere Dokumentation:

- 📚 **[Benutzerhandbuch](user-guide/quick-start.md)** — ausführliche Installations- und Nutzungsanleitungen
- 🎯 **[Tutorial](tutorial/getting-started.md)** — Schritt-für-Schritt-Tutorials für Einsteiger
- 📖 **[CLI-Referenz](user-guide/cli-reference.md)** — vollständige Befehlsreferenz
- 🔍 **[Qualitätssicherung der Vorlagen](reference/template-quality-assurance.md)** — automatisierte Tests und Qualitätsstandards

## 🚀 Vorlagenbasierte Tutorials

Lernen Sie die FastAPI-Entwicklung anhand praktischer Anwendungsfälle mit unseren gebrauchsfertigen Vorlagen:

### 📖 Kerntutorials

- **[Einen einfachen API-Server bauen](tutorial/basic-api-server.md)** — erstellen Sie Ihren ersten FastAPI-Server mit der Vorlage `fastapi-default`
- **[Eine asynchrone CRUD-API bauen](tutorial/async-crud-api.md)** — entwickeln Sie eine leistungsstarke asynchrone API mit der Vorlage `fastapi-async-crud`
- **[Domänenorientiertes Projekt (Domain Starter)](tutorial/domain-starter.md)** — bauen Sie eine mittelgroße API mit der Vorlage `fastapi-domain-starter`, dem empfohlenen modernen Standard

### 🗄️ Datenbank und Infrastruktur

- **[Integration einer Datenbank](tutorial/database-integration.md)** — nutzen Sie PostgreSQL + SQLAlchemy mit der Vorlage `fastapi-psql-orm`
- **[Docker-Containerisierung und Deployment](tutorial/docker-deployment.md)** — richten Sie eine produktionsreife Deployment-Umgebung mit der Vorlage `fastapi-dockerized` ein

### ⚡ Erweiterte Funktionen

- **[Benutzerdefinierte Antwortbehandlung und fortgeschrittenes API-Design](tutorial/custom-response-handling.md)** — bauen Sie Enterprise-APIs mit der Vorlage `fastapi-custom-response`
- **[Integration mit MCP](tutorial/mcp-integration.md)** — erstellen Sie einen API-Server, der mit KI-Modellen integriert ist, mit der Vorlage `fastapi-mcp`

Jedes Tutorial bietet:

- ✅ **Praktische Beispiele** — Code, den Sie direkt in echten Projekten verwenden können
- ✅ **Schritt-für-Schritt-Anleitungen** — detaillierte Erklärungen, denen Einsteiger leicht folgen können
- ✅ **Best Practices** — branchenübliche Muster und Sicherheitserwägungen
- ✅ **Erweiterungsmethoden** — Hinweise, wie Sie Ihr Projekt auf die nächste Stufe heben

## Mitwirken

Wir freuen uns über Beiträge aus der Community! FastAPI-fastkit soll Einsteigern in Python und FastAPI helfen, und Ihre Beiträge können einen großen Unterschied machen.

### Was Sie beitragen können

- 🚀 **Neue FastAPI-Vorlagen** — fügen Sie Vorlagen für verschiedene Anwendungsfälle hinzu
- 🐛 **Bugfixes** — helfen Sie uns, Stabilität und Zuverlässigkeit zu verbessern
- 📚 **Dokumentation** — verbessern Sie Anleitungen, Beispiele und Übersetzungen
- 🧪 **Tests** — erhöhen Sie die Testabdeckung und ergänzen Sie Integrationstests
- 💡 **Funktionen** — schlagen Sie neue CLI-Funktionen vor und implementieren Sie diese

### Erste Schritte zum Mitwirken

Um mit der Mitarbeit an FastAPI-fastkit zu beginnen, sehen Sie sich unsere umfassenden Leitfäden an:

- **[Entwicklungsumgebung einrichten](contributing/development-setup.md)** — vollständige Anleitung zum Einrichten Ihrer Entwicklungsumgebung
- **[Code-Richtlinien](contributing/code-guidelines.md)** — Programmierstandards und Best Practices
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** — umfassender Beitragsleitfaden
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** — Projektprinzipien und Community-Standards
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** — Sicherheitsrichtlinien und Meldungen

## Bedeutung von FastAPI-fastkit

FastAPI-fastkit zielt darauf ab, ein schnelles und einfach zu nutzendes Starter-Kit für Neulinge in Python und FastAPI bereitzustellen.

Diese Idee entstand mit dem Ziel, FastAPI-Einsteigern beim Lernen von Anfang an zu helfen — im Einklang mit der produktiven Bedeutung des FastAPI-cli-Pakets, das mit dem [FastAPI-0.111.0-Update](https://github.com/fastapi/fastapi/releases/tag/0.111.0) eingeführt wurde.

Als jemand, der FastAPI seit langem nutzt und liebt, wollte ich ein Projekt entwickeln, das dazu beiträgt, [die wunderbare Motivation](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) zu erfüllen, die der FastAPI-Entwickler [tiangolo](https://github.com/tiangolo) zum Ausdruck gebracht hat.

FastAPI-fastkit schlägt eine Brücke zwischen dem Einstieg und dem Bau produktionsreifer Anwendungen, indem es Folgendes bietet:

- **Sofortige Produktivität** für Neueinsteiger, die von der Einrichtung überfordert sein könnten
- **Best Practices** in jeder Vorlage, die Anwendern beim Erlernen korrekter FastAPI-Muster helfen
- **Skalierbare Grundlagen**, die mit den Anwendern wachsen, vom Anfänger zum Experten
- **Community-getriebene Vorlagen**, die reale FastAPI-Nutzungsmuster widerspiegeln

## Nächste Schritte

Bereit, mit FastAPI-fastkit zu starten? Folgen Sie diesen nächsten Schritten:

### 🚀 Schnellstart

1. **[Installation](user-guide/installation.md)**: FastAPI-fastkit installieren
2. **[Schnellstart](user-guide/quick-start.md)**: erstellen Sie Ihr erstes Projekt in 5 Minuten
3. **[Tutorial – Erste Schritte](tutorial/getting-started.md)**: detailliertes Schritt-für-Schritt-Tutorial

### 📚 Vertiefung

- **[Projekte erstellen](user-guide/creating-projects.md)**: Projekte mit verschiedenen Stacks erstellen
- **[Routen hinzufügen](user-guide/adding-routes.md)**: fügen Sie API-Endpunkte zu Ihrem Projekt hinzu
- **[Vorlagen verwenden](user-guide/using-templates.md)**: nutzen Sie vorgefertigte Projektvorlagen

### 🛠️ Mitwirken

Möchten Sie zu FastAPI-fastkit beitragen?

- **[Entwicklungsumgebung einrichten](contributing/development-setup.md)**: richten Sie Ihre Entwicklungsumgebung ein
- **[Code-Richtlinien](contributing/code-guidelines.md)**: folgen Sie unseren Programmierstandards und Best Practices
- **[Contributing-Richtlinien](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)**: umfassender Beitragsleitfaden

### 🔍 Referenz

- **[CLI-Referenz](user-guide/cli-reference.md)**: vollständige Referenz der CLI-Befehle
- **[Qualitätssicherung der Vorlagen](reference/template-quality-assurance.md)**: automatisierte Tests und Qualitätsstandards
- **[FAQ](reference/faq.md)**: häufig gestellte Fragen
- **[GitHub-Repository](https://github.com/bnbong/FastAPI-fastkit)**: Quellcode und Issue-Tracking

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz — Details siehe die Datei [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE).

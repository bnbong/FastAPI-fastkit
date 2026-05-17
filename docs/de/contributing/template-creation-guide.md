# Leitfaden zur Erstellung von FastAPI-Vorlagen

Ein umfassender Leitfaden zum Hinzufügen neuer FastAPI-Projektvorlagen zu FastAPI-fastkit.

## 🎯 Überblick

Das Hinzufügen einer neuen Vorlage erfolgt in einem Prozess aus 5 Schritten:

1. **📋 Planung und Entwurf** — Zweck und Struktur der Vorlage definieren
2. **🏗️ Implementierung der Vorlage** — die erforderliche Struktur und Dateien erstellen
3. **🔍 Lokale Validierung** — die Vorlage mit dem Inspektor prüfen
4. **📚 Dokumentation** — README und Nutzungsleitfaden verfassen
5. **🚀 Einreichung und Review** — PR erstellen und Community-Review

## 📋 Schritt 1: Planung und Entwurf

### Zweck der Vorlage definieren

Bevor Sie eine neue Vorlage erstellen, beantworten Sie folgende Fragen:

- **Welchen einzigartigen Wert bietet diese Vorlage?**
- **Wie unterscheidet sie sich von bestehenden Vorlagen?**
- **Welche Nutzergruppe ist die Zielgruppe?**
- **Welche Tech-Stack-Komponenten wird sie enthalten?**

### Namenskonvention für Vorlagen

```
fastapi-{purpose}-{stack}
```

Beispiele:

- `fastapi-microservice` (Microservice-Vorlage)
- `fastapi-graphql` (GraphQL-Integrationsvorlage)
- `fastapi-auth-jwt` (JWT-Authentifizierungsvorlage)

### Planung des Tech-Stacks

Definieren Sie die wichtigsten Technologien vorab:

```yaml
# Example: fastapi-microservice template
core_dependencies:
  - fastapi
  - uvicorn
  - pydantic
  - pydantic-settings

additional_features:
  - sqlalchemy (ORM)
  - alembic (migrations)
  - redis (caching)
  - celery (background tasks)
  - pytest (testing)

development_tools:
  - black (code formatting)
  - isort (import sorting)
  - mypy (type checking)
  - pre-commit (Git hooks)
```

## 🏗️ Schritt 2: Implementierung der Vorlage

### Erforderliche Verzeichnisstruktur

```
fastapi-{template-name}/
├── src/                          # Application source code
│   ├── main.py-tpl              # ✅ FastAPI app entry point (required)
│   ├── __init__.py-tpl
│   ├── api/                     # API routers
│   │   ├── __init__.py-tpl
│   │   ├── api.py-tpl           # Main API router
│   │   └── routes/              # Individual routes
│   │       ├── __init__.py-tpl
│   │       └── items.py-tpl     # Example route
│   ├── core/                    # Core configuration
│   │   ├── __init__.py-tpl
│   │   └── config.py-tpl        # Settings management
│   ├── crud/                    # CRUD logic
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   ├── schemas/                 # Pydantic models
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   └── utils/                   # Utility functions
│       ├── __init__.py-tpl
│       └── helpers.py-tpl
├── tests/                       # ✅ Tests (required)
│   ├── __init__.py-tpl
│   ├── conftest.py-tpl         # pytest configuration
│   └── test_items.py-tpl       # Example tests
├── scripts/                     # Scripts
│   ├── format.sh-tpl           # Code formatting
│   ├── lint.sh-tpl             # Linting
│   ├── run-server.sh-tpl       # Server execution
│   └── test.sh-tpl             # Test execution
├── pyproject.toml-tpl           # ✅ Primary metadata (PEP 621, preferred)
├── setup.py-tpl                # 🟡 Legacy metadata (accepted for back-compat)
├── requirements.txt-tpl         # 🟡 Optional when pyproject declares deps
├── setup.cfg-tpl               # Development tools configuration
├── README.md-tpl               # ✅ Project documentation (required)
├── .env-tpl                    # Environment variables template
└── .gitignore-tpl              # Git ignore file
```

**Minimal erforderliche Dateien.** Eine Vorlage muss bereitstellen:

- ein `tests/`-Verzeichnis
- eine `README.md-tpl`-Datei
- mindestens eine Metadaten-Datei: `pyproject.toml-tpl` (bevorzugt, PEP 621) oder `setup.py-tpl` (legacy, weiterhin akzeptiert)
- eine Deklaration von `fastapi` als Abhängigkeit in mindestens einem von: `pyproject.toml-tpl` `[project].dependencies`, `requirements.txt-tpl` oder `setup.py-tpl` `install_requires`

`requirements.txt-tpl` ist nicht mehr zwingend erforderlich, wenn `pyproject.toml-tpl` `[project].dependencies` deklariert. Moderne Vorlagen SOLLTEN `pyproject.toml-tpl` als primäre Metadaten-Datei adoptieren.

### Anleitung zum Schreiben der Dateien

#### 1. main.py-tpl schreiben

```python
"""
FastAPI application entry point

This file is the main application for the <project_name> project created with FastAPI-fastkit.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api import api_router
from core.config import settings

# Create FastAPI app (required for inspector validation)
app = FastAPI(
    title="<project_name>",
    description="Project created with FastAPI-fastkit",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello from <project_name>!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. pyproject.toml-tpl schreiben (bevorzugt)

Moderne Vorlagen sollten Metadaten und Abhängigkeiten in einem PEP-621-`pyproject.toml-tpl` deklarieren. Mindestens muss die Datei einen `[project]`-Abschnitt mit `name`, `version`, einer `description` und einer `dependencies`-Liste, die `fastapi` enthält, bereitstellen. Vorlagen müssen außerdem zwei FastAPI-fastkit-Identitätsmarker tragen, damit `is_fastkit_project()` generierte Projekte von unverwandten FastAPI-Projekten im Workspace des Nutzers unterscheiden kann:

- `[FastAPI-fastkit templated]`-Präfix in `description`
- eine eigene Tabelle `[tool.fastapi-fastkit]` mit `managed = true`

Die Erkennung akzeptiert jeden der beiden Marker (Vergleich ist case-insensitive). Die Metadaten-Injektion fügt beide bei der Projektgenerierung hinzu, falls die Vorlage sie weglässt — Autoren sollten sie aber explizit angeben.

```toml
[project]
name = "<project_name>"
version = "0.1.0"
description = "[FastAPI-fastkit templated] <description>"
authors = [
    {name = "<author>", email = "<author_email>"},
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.28.0",
]

[tool.fastapi-fastkit]
managed = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 3. requirements.txt-tpl schreiben (optional)

Optional, wenn `pyproject.toml-tpl` `[project].dependencies` deklariert. Weiterhin nützlich für Vorlagen, die reine `pip`-Workflows bevorzugen.

```txt
# FastAPI core dependencies (required)
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Data validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Environment variable management
python-dotenv==1.0.0

# Database (if needed)
sqlalchemy==2.0.23
alembic==1.13.0

# Development tools
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Code quality
black==23.11.0
isort==5.12.0
mypy==1.7.1
```

#### 4. setup.py-tpl schreiben (legacy — optional, falls pyproject vorhanden)

Erhalten für Legacy-Vorlagen. Neue Vorlagen benötigen diese Datei nicht, wenn sie `pyproject.toml-tpl` mitliefern.

```python
"""
<project_name> package setup

Project created with FastAPI-fastkit.
"""
from setuptools import find_packages, setup

# Dependencies list (type annotation required)
install_requires: list[str] = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "python-dotenv>=1.0.0",
]

setup(
    name="<project_name>",
    version="1.0.0",
    description="[FastAPI-fastkit templated] <description>",  # Identity marker used by is_fastkit_project()
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="<author>",
    author_email="<author_email>",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
```

#### 5. Test-Dateien schreiben

```python
# tests/test_items.py-tpl
"""
Items API test module
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_item():
    """Test item creation"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]

def test_read_items():
    """Test reading items list"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 🔍 Schritt 3: Lokale Validierung

### Automatisierte Validierungsskripte ausführen

Sobald Ihre neue Vorlage fertig ist, prüfen Sie sie mit folgenden Befehlen:

```bash
# Validate all templates
make inspect-templates

# Validate specific template only
make inspect-template TEMPLATES="fastapi-your-template"

# Validate with verbose output
python scripts/inspect-templates.py --templates "fastapi-your-template" --verbose
```

!!! note

    Wenn Sie eine PR einreichen, läuft der **Template PR Inspection**-Workflow automatisch und validiert Ihre Vorlagenänderungen. Sie erhalten das Feedback direkt in Ihrer PR.

### Validierungs-Checkliste

Der Inspektor validiert automatisch die folgenden Punkte:

#### ✅ Validierung der Dateistruktur

- [ ] `tests/`-Verzeichnis existiert
- [ ] `README.md-tpl`-Datei existiert
- [ ] Mindestens eine von `pyproject.toml-tpl` (bevorzugt) oder `setup.py-tpl` (legacy) existiert

#### ✅ Validierung der Dateiendungen

- [ ] Alle Python-Dateien verwenden die Endung `.py-tpl`
- [ ] Keine `.py`-Dateien existieren

#### ✅ Validierung der Abhängigkeiten

- [ ] `fastapi` ist in mindestens einem von Folgendem deklariert:
    - [ ] `pyproject.toml-tpl` unter `[project].dependencies` (bevorzugt)
    - [ ] `requirements.txt-tpl`
    - [ ] `setup.py-tpl` unter `install_requires`

#### ✅ Validierung der FastAPI-Implementierung

- [ ] `FastAPI`-Import existiert in `main.py-tpl`
- [ ] App-Erstellung wie `app = FastAPI()` existiert in `main.py-tpl`

#### ✅ Validierung der Testausführung

- [ ] Erstellung der virtuellen Umgebung erfolgreich
- [ ] Installation der Abhängigkeiten erfolgreich
- [ ] Alle pytest-Tests bestehen

#### ✅ Automatisiertes Vorlagen-Testen

FastAPI-fastkit enthält **automatisierte Vorlagen-Tests**, die umfassende Tests für alle Vorlagen ausführen:

**Testabdeckung:**

- ✅ Prozess der Projektanlegung
- ✅ Injektion der Projekt-Metadaten
- ✅ Einrichtung der virtuellen Umgebung
- ✅ Installation der Abhängigkeiten (alle Paketmanager)
- ✅ Validierung der grundlegenden Projektstruktur
- ✅ Identifikation als FastAPI-Projekt

**Testausführung:**
```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Test specific template
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v
```

**Erkennung der Vorlagen-Tests:**
Neue Vorlagen werden **automatisch erkannt** und ohne manuelle Konfiguration getestet:

1. ✅ **Null Konfiguration**: Vorlage hinzufügen → automatische Tests
2. ✅ **Einheitliche Tests**: gleiche Qualitätsstandards für alle Vorlagen
3. ✅ **Mehrere Paketmanager**: Tests mit UV, PDM, Poetry und PIP
4. ✅ **Umfassende Validierung**: Struktur, Metadaten und Funktionsprüfungen

**Was das für Sie bedeutet:**

- 🚀 **Keine zusätzlichen Test-Dateien in der Hauptquelle von `FastAPI-fastkit`**: Ihre Vorlage wird automatisch getestet
- ⚡ **Schnellere Entwicklung**: Fokus auf Vorlageninhalt, nicht auf Test-Setup
- 🛡️ **Qualitätssicherung**: einheitliche Tests über alle Vorlagen hinweg
- 🔄 **CI/CD-Integration**: automatische Tests in Pull-Requests

**Manuelle Tests bleiben weiterhin nötig:**

- 🧪 **Vorlagenspezifische Funktionen**: Geschäftslogik und individuelle Features
- 🔧 **Integrationstests**: externe Dienste und komplexe Workflows
- 📱 **End-to-End-Szenarien**: vollständige Nutzerflüsse

**Best Practices für Tests:**
```console
# 1. Test your template locally
$ fastkit startdemo your-template-name

# 2. Run automated tests
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v

# 3. Test with different package managers
$ fastkit startdemo your-template-name --package-manager poetry
$ fastkit startdemo your-template-name --package-manager pdm
$ fastkit startdemo your-template-name --package-manager uv
```

### Manuelle Validierungs-Checkliste

Zusätzlich zur automatisierten Validierung manuell überprüfen:

#### 🔧 Code-Qualität

- [ ] Code folgt dem PEP-8-Styleguide
- [ ] Angemessene Verwendung von Type Hints
- [ ] Sinnvolle Variablen- und Funktionsnamen
- [ ] Angemessene Kommentare und Docstrings

#### 🏗️ Architektur

- [ ] Trennung der Belange (API, Geschäftslogik, Datenzugriff getrennt)
- [ ] Wiederverwendbare Komponenten
- [ ] Skalierbare Struktur
- [ ] Best Practices für Sicherheit angewendet

#### 📚 Dokumentation

- [ ] README.md-tpl folgt dem Format von PROJECT_README_TEMPLATE.md
- [ ] Installations- und Ausführungsmethoden beschrieben
- [ ] API-Dokumentation (OpenAPI/Swagger)
- [ ] Erläuterung der Umgebungsvariablen

## 📚 Schritt 4: Dokumentation

### README.md-tpl verfassen

Schreiben Sie auf Basis des Leitfadens [PROJECT_README_TEMPLATE.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/PROJECT_README_TEMPLATE.md).

### Beschreibung der Vorlage schreiben

Fügen Sie eine Beschreibung Ihrer neuen Vorlage zu `src/fastapi_fastkit/fastapi_project_template/README.md` hinzu:

```markdown
## fastapi-your-template

Write a brief description and use cases for your new template here.

### Features:
- Feature 1
- Feature 2
- Feature 3

### Use Cases:
- Use case 1
- Use case 2
```

## 🚀 Schritt 5: Einreichung und Review

### Checkliste vor der PR

- [ ] Alle automatisierten Validierungen bestanden (`make inspect-templates`)
- [ ] Code-Formatierung abgeschlossen (`make format`)
- [ ] Linting-Prüfungen bestanden (`make lint`)
- [ ] Alle Tests bestanden (`make test`)
- [ ] Dokumentation abgeschlossen
- [ ] Richtlinien aus CONTRIBUTING.md befolgt

### PR-Titel und -Beschreibung

```
[TEMPLATE] Add fastapi-{template-name} template

## Overview
Adds a new {purpose} template.

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Validation Results
- [ ] Inspector validation passed
- [ ] All tests passed
- [ ] Documentation completed

## Usage Example
\```bash
fastkit startdemo
# Select template: fastapi-{template-name}
\```

## Related Issues
Closes #issue-number
```

### Review-Prozess

1. **Automatisierte Validierung**: GitHub Actions validiert die Vorlage automatisch
    - **Template PR Inspection**: führt `inspect-changed-templates.py` bei PRs aus, die Vorlagen ändern
    - **Wöchentliche Inspektion**: vollständige Validierung der Vorlagen jeden Mittwoch
2. **Code-Review**: Maintainer und Community prüfen den Code
3. **Tests**: Die Vorlage wird in verschiedenen Umgebungen getestet
4. **Dokumentations-Review**: Genauigkeit und Vollständigkeit der Dokumentation prüfen
5. **Freigabe und Merge**: Merge in den Main-Branch, sobald alle Anforderungen erfüllt sind

!!! note

    Sie erhalten automatische PR-Kommentare mit den Validierungsergebnissen. Prüfen Sie diese, bevor Sie ein Review anfordern!

## 🎯 Best Practices

### Sicherheitsüberlegungen

- Sensible Informationen über Umgebungsvariablen verwalten
- Korrekte CORS-Konfiguration
- Eingabedaten validieren
- SQL-Injection verhindern

### Performance-Optimierung

- Asynchrone Verarbeitung nutzen
- Datenbankabfragen optimieren
- Passende Caching-Strategien
- Antwortkompression konfigurieren

### Wartbarkeit

- Klare Codestruktur
- Umfassende Testabdeckung
- Detaillierte Dokumentation
- Logging und Monitoring einrichten

## 🆘 Brauchen Sie Hilfe?

- 📖 [Anleitung zur Entwicklungsumgebung](development-setup.md)
- 📋 [Code-Richtlinien](code-guidelines.md)
- 💬 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- 📧 [Maintainer kontaktieren](mailto:bbbong9@gmail.com)

Eine neue Vorlage hinzuzufügen ist ein wertvoller Beitrag zur FastAPI-fastkit-Community. Ihre Ideen und Ihr Einsatz werden anderen Entwicklern enorm helfen! 🚀

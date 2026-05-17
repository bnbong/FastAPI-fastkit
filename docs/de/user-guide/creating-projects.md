# Projekte erstellen

Eine ausführliche Anleitung zum Erstellen verschiedener Arten von FastAPI-Projekten mit FastAPI-fastkit.

## Grundlegende Projekterstellung

### 1. Projekterstellung im interaktiven Modus

Die einfachste Möglichkeit, ein Projekt interaktiv zu erstellen:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Awesome FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-api          │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ Awesome FastAPI project │
└──────────────┴─────────────────────────┘
```

</div>

### 2. Stack-Auswahl

Wählen Sie den Abhängigkeits-Stack, den Sie in Ihr Projekt aufnehmen möchten:

#### MINIMAL-Stack (Standard)

Das schlichteste FastAPI-Projekt:

- `fastapi` — FastAPI-Framework
- `uvicorn` — ASGI-Server
- `pydantic` — Datenvalidierung
- `pydantic-settings` — Einstellungsverwaltung

**Am besten für:**

- FastAPI lernen
- Einfache APIs
- Prototypen
- Microservices

#### STANDARD-Stack

Enthält Datenbankunterstützung und Tests:

- Alle MINIMAL-Abhängigkeiten
- `sqlalchemy` — ORM für Datenbankoperationen
- `alembic` — Datenbankmigrationen
- `pytest` — Test-Framework

**Am besten für:**

- Die meisten Webanwendungen
- APIs mit Datenbankspeicherung
- Produktionsreife Anwendungen
- Teamprojekte

#### FULL-Stack

Vollständige Entwicklungsumgebung:

- Alle STANDARD-Abhängigkeiten
- `redis` — Caching und Session-Speicher
- `celery` — Verarbeitung von Hintergrundaufgaben

**Am besten für:**

- Große Anwendungen
- Hohe Leistungsanforderungen
- Komplexe Geschäftslogik
- Unternehmensanwendungen

## Erweiterte Projektoptionen

### Benutzerdefinierte Projektkonfiguration

Sie können Ihr Projekt während der Erstellung anpassen:

<div class="termy">

```console
$ fastkit init
Enter the project name: advanced-api
Enter the author name: Development Team
Enter the author email: dev@company.com
Enter the project description: Advanced FastAPI application with custom features

# Choose STANDARD stack for database support
Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Erklärung der Projektstruktur

Wenn Sie ein Projekt erstellen, generiert FastAPI-fastkit folgende Struktur:

```
my-awesome-api/
├── .venv/                      # Virtuelle Umgebung
├── src/                        # Quellcode
│   ├── __init__.py
│   ├── main.py                # Einstiegspunkt der Anwendung
│   ├── core/                  # Zentrale Konfiguration
│   │   ├── __init__.py
│   │   └── config.py         # Einstellungen und Konfiguration
│   ├── api/                   # API-Schicht
│   │   ├── __init__.py
│   │   ├── api.py            # Haupt-Router der API
│   │   └── routes/           # Einzelne Routenmodule
│   │       ├── __init__.py
│   │       └── items.py      # Beispiel-Endpunkte für Items
│   ├── crud/                  # Datenbankoperationen
│   │   ├── __init__.py
│   │   └── items.py          # CRUD-Operationen für Items
│   ├── schemas/               # Pydantic-Modelle
│   │   ├── __init__.py
│   │   └── items.py          # Schemas zur Datenvalidierung
│   └── mocks/                 # Testdaten
│       ├── __init__.py
│       └── mock_items.json   # Beispieldaten für die Entwicklung
├── tests/                     # Testsuite
│   ├── __init__.py
│   ├── conftest.py           # Testkonfiguration
│   └── test_items.py         # Beispieltests
├── scripts/                   # Hilfsskripte
│   ├── test.sh               # Tests ausführen
│   ├── coverage.sh           # Testabdeckung
│   └── lint.sh               # Code-Linting
├── requirements.txt           # Python-Abhängigkeiten
├── setup.py                  # Paketkonfiguration
└── README.md                 # Projektdokumentation
```

### 3. Paketmanager-Auswahl

FastAPI-fastkit unterstützt mehrere Python-Paketmanager. Wählen Sie den, der am besten zu Ihrem Workflow passt:

#### Verfügbare Paketmanager

<div class="termy">

```console
Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

Jeder Paketmanager hat seine Stärken:

#### UV (Standard — empfohlen)

**Schneller Paketmanager auf Rust-Basis**

- ⚡ **Ultraschnell**: 10–100× schneller als pip
- 🔧 **Direkter Ersatz**: kompatibel mit pip-Workflows
- 📦 **Modern**: vollständige PEP-621-Unterstützung
- 🛠️ **Zuverlässig**: deterministische Auflösung

**Generierte Dateien:**

- `pyproject.toml` (PEP-621-Format)
- `uv.lock` (Lockfile)

**Nutzung nach der Erstellung:**
```console
cd my-project
uv sync              # Abhängigkeiten installieren
uv add requests      # Neue Abhängigkeit hinzufügen
uv run pytest        # Tests ausführen
```

#### PDM

**Moderne Python-Abhängigkeitsverwaltung**

- 🚀 **Modern**: Unterstützung von PEP 582 und PEP 621
- 🧠 **Intelligent**: fortgeschrittene Abhängigkeitsauflösung
- 💼 **Professionell**: Unterstützung für Workspaces und Multi-Projekt-Setups
- 📊 **Analytisch**: Werkzeuge zur Analyse der Abhängigkeiten

**Generierte Dateien:**

- `pyproject.toml` (PEP-621-Format)
- `pdm.lock` (Lockfile)

**Nutzung nach der Erstellung:**
```console
cd my-project
pdm install          # Abhängigkeiten installieren
pdm add requests     # Neue Abhängigkeit hinzufügen
pdm run pytest       # Tests ausführen
```

#### Poetry

**Ausgereifte Abhängigkeitsverwaltung und Packaging**

- ✅ **Etabliert**: ausgereift und weit verbreitet
- 📦 **Integriert**: Unterstützung für Build und Veröffentlichung
- 🔒 **Reproduzierbar**: poetry.lock für exakte Versionen
- 🏗️ **Komplett**: vollständige Verwaltung des Projektlebenszyklus

**Generierte Dateien:**

- `pyproject.toml` (Poetry-Format)
- `poetry.lock` (Lockfile)

**Nutzung nach der Erstellung:**
```console
cd my-project
poetry install       # Abhängigkeiten installieren
poetry add requests  # Neue Abhängigkeit hinzufügen
poetry run pytest    # Tests ausführen
```

#### PIP

**Standard-Python-Paketmanager**

- 🏠 **Eingebaut**: in Python enthalten
- 🌍 **Universell**: funktioniert überall
- 📚 **Vertraut**: die meisten Entwickler kennen ihn
- 🔧 **Einfach**: geradliniger Workflow

**Generierte Dateien:**

- `requirements.txt`

**Nutzung nach der Erstellung:**
```console
cd my-project
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
pip install -r requirements.txt
pip install requests
pytest
```

#### Paketmanager angeben

Sie können Ihren bevorzugten Paketmanager angeben:

**Interaktive Auswahl (Standard):**
```console
$ fastkit init
# ... prompts for package manager selection
```

**Kommandozeilenoption:**
```console
$ fastkit init --package-manager poetry
$ fastkit init --package-manager pdm
$ fastkit init --package-manager uv
$ fastkit init --package-manager pip
```

### Die einzelnen Verzeichnisse verstehen

#### `src/`-Verzeichnis

Enthält den gesamten Quellcode Ihrer Anwendung nach dem **src-Layout**-Muster, einer Best Practice für Python-Packaging.

#### `core/`-Modul

- **config.py**: Anwendungseinstellungen, Umgebungsvariablen und Konfiguration
- Zentralisiert die gesamte Konfigurationsverwaltung
- Unterstützt eine `.env`-Datei für umgebungsspezifische Einstellungen

#### `api/`-Modul

- **api.py**: Haupt-API-Router, der alle Unter-Router einbindet
- **routes/**: einzelne Routenmodule für verschiedene Ressourcen
- Saubere Trennung der Zuständigkeiten für verschiedene API-Endpunkte

#### `crud/`-Modul

- Datenbankoperationen und Geschäftslogik
- **C**reate, **R**ead, **U**pdate, **D**elete
- Abstraktionsschicht zwischen API-Routen und Datenspeicher

#### `schemas/`-Modul

- Pydantic-Modelle zur Datenvalidierung
- Anfrage-/Antwortschemata
- Typdefinitionen und Datenmodelle

#### `tests/`-Verzeichnis

- Vollständige Test-Suite für Ihre Anwendung
- Enthält Unit-Tests und Integrationstests
- Vorkonfiguriert mit pytest

## Stack-Vergleich

| Funktion | MINIMAL | STANDARD | FULL |
|---------|---------|----------|------|
| FastAPI & Uvicorn | ✅ | ✅ | ✅ |
| Datenvalidierung | ✅ | ✅ | ✅ |
| Datenbankunterstützung | ❌ | ✅ | ✅ |
| Migrationen | ❌ | ✅ | ✅ |
| Test-Framework | ❌ | ✅ | ✅ |
| Caching (Redis) | ❌ | ❌ | ✅ |
| Hintergrundaufgaben | ❌ | ❌ | ✅ |
| **Am besten für** | Lernen, einfache APIs | Die meisten Anwendungen | Enterprise, komplexe Apps |

## Beispiele zur Projekterstellung

### Beispiel 1: Lernprojekt

<div class="termy">

```console
$ fastkit init
Enter the project name: fastapi-learning
Enter the author name: Student
Enter the author email: student@example.com
Enter the project description: Learning FastAPI basics

Select stack (minimal, standard, full): minimal
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Beispiel 2: E-Commerce-API

<div class="termy">

```console
$ fastkit init
Enter the project name: ecommerce-api
Enter the author name: E-commerce Team
Enter the author email: team@ecommerce.com
Enter the project description: E-commerce platform API

Select stack (minimal, standard, full): standard
Do you want to proceed with project creation? [y/N]: y
```

</div>

### Beispiel 3: Hochleistungsanwendung

<div class="termy">

```console
$ fastkit init
Enter the project name: enterprise-api
Enter the author name: Enterprise Team
Enter the author email: enterprise@company.com
Enter the project description: High-performance enterprise API

Select stack (minimal, standard, full): full
Do you want to proceed with project creation? [y/N]: y
```

</div>

## Nach der Projekterstellung

### 1. Virtuelle Umgebung aktivieren

<div class="termy">

```console
$ cd my-awesome-api
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

### 2. Installation überprüfen

<div class="termy">

```console
$ pip list
Package         Version
fastapi         0.104.1
uvicorn         0.24.0
pydantic        2.5.0
...
```

</div>

### 3. Mit der Entwicklung beginnen

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

## Konfigurationsverwaltung

### Umgebungsvariablen

Ihr Projekt unterstützt umgebungsbasierte Konfiguration über `.env`-Dateien:

Erstellen Sie eine `.env`-Datei im Projekt-Stammverzeichnis:

```env
# .env
APP_NAME=My Awesome API
APP_VERSION=1.0.0
DEBUG=True
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key-here
```

### Konfiguration im Code

Die generierte `src/core/config.py` lädt diese Variablen automatisch:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Application"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key"

    class Config:
        env_file = ".env"

settings = Settings()
```

## Anpassungsmöglichkeiten

### Benutzerdefinierte Abhängigkeiten hinzufügen

Nach der Projekterstellung können Sie weitere Abhängigkeiten hinzufügen:

<div class="termy">

```console
$ pip install requests httpx python-jose
$ pip freeze > requirements.txt
```

</div>

### Projektstruktur anpassen

Die generierte Struktur folgt Best Practices, lässt sich aber anpassen:

- Neue Module in `src/` hinzufügen
- Weitere Routendateien in `api/routes/` anlegen
- CRUD-Operationen in `crud/` erweitern
- Weitere Schemata in `schemas/` hinzufügen

## Best Practices

### 1. Virtuelle Umgebung

Verwenden Sie immer virtuelle Umgebungen, um Projektabhängigkeiten zu isolieren:

```bash
# Create project with virtual environment
$ fastkit init  # Automatically creates .venv/

# Activate when working
$ source .venv/bin/activate
```

### 2. Versionsverwaltung

Initialisieren Sie ein Git-Repository nach der Projekterstellung:

<div class="termy">

```console
$ cd my-awesome-api
$ git init
$ git add .
$ git commit -m "Initial commit - FastAPI project setup"
```

</div>

### 3. Umgebungskonfiguration

- Verwenden Sie `.env`-Dateien für die lokale Entwicklung
- Verwenden Sie Umgebungsvariablen für die Produktion
- Committen Sie niemals sensible Daten in die Versionsverwaltung

### 4. Testen

Nutzen Sie das mitgelieferte Test-Framework:

<div class="termy">

```console
$ python -m pytest
$ bash scripts/test.sh
```

</div>

## Nächste Schritte

Nachdem Sie Ihr Projekt erstellt haben:

1. **[Routen hinzufügen](adding-routes.md)**: lernen Sie, wie Sie neue API-Endpunkte hinzufügen
2. **[CLI-Referenz](cli-reference.md)**: meistern Sie alle verfügbaren Befehle
3. **[Tutorial – Ihr erstes Projekt](../tutorial/first-project.md)**: bauen Sie eine vollständige Anwendung

!!! tip "Tipps zur Projekterstellung"
    - Wählen Sie den Stack, der zu Ihren Projektanforderungen passt
    - Beginnen Sie mit MINIMAL zum Lernen, nutzen Sie STANDARD für die meisten Projekte
    - Die Projektstruktur ist auf Skalierbarkeit und Wartbarkeit ausgelegt
    - Der gesamte generierte Code folgt FastAPI-Best-Practices

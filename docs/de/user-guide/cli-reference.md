# CLI-Referenz

Vollständige Referenz aller Befehle der FastAPI-fastkit-Kommandozeilenschnittstelle.

## Globale Optionen

Alle Befehle unterstützen diese globalen Optionen:

```console
$ fastkit [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Globale Optionen

| Option | Beschreibung |
|--------|-------------|
| `--version` | Die Version von FastAPI-fastkit anzeigen |
| `--help` | Die Hilfenachricht anzeigen |

### Beispiele

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0

$ fastkit --help
Usage: fastkit [OPTIONS] COMMAND [ARGS]...

  FastAPI-fastkit CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  addroute       Add a new route to FastAPI project
  init           Create a new FastAPI project
  list-templates List available FastAPI templates
  runserver      Start FastAPI development server
  startdemo      Create FastAPI project from template
```

</div>

## Befehle

### `init`

Ein neues FastAPI-Projekt mit interaktiver Einrichtung erstellen.

#### Syntax

```console
$ fastkit init [OPTIONS]
```

#### Optionen

| Option | Beschreibung | Standard |
|--------|-------------|---------|
| `--package-manager` | Zu verwendender Paketmanager (pip, uv, pdm, poetry) | uv |
| `--help` | Hilfe zum Befehl anzeigen | - |

#### Interaktive Eingabeaufforderungen

Der Befehl `init` fragt Sie ab:

1. **Projektname**: Verzeichnis- und Paketname
2. **Name des Autors**: Information zum Autor des Pakets
3. **E-Mail des Autors**: Kontakt-E-Mail des Pakets
4. **Projektbeschreibung**: kurze Beschreibung des Projekts
5. **Stack-Auswahl**: Wahl zwischen minimal, standard oder full
6. **Paketmanager-Auswahl**: Wahl zwischen pip, uv, pdm oder poetry (außer wenn mit `--package-manager` angegeben)

#### Stack-Optionen

**MINIMAL-Stack:**

- `fastapi` — FastAPI-Framework
- `uvicorn` — ASGI-Server
- `pydantic` — Datenvalidierung
- `pydantic-settings` — Konfigurationsverwaltung

**STANDARD-Stack:**

- Alle Pakete des MINIMAL-Stacks
- `sqlalchemy` — SQL-Toolkit und ORM
- `alembic` — Werkzeug für Datenbankmigrationen
- `pytest` — Test-Framework

**FULL-Stack:**

- Alle Pakete des STANDARD-Stacks
- `redis` — In-Memory-Datenspeicher
- `celery` — verteilte Aufgabenwarteschlange

#### Beispiele

<div class="termy">

```console
$ fastkit init
Enter the project name: my-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome API

Select stack (minimal, standard, full): standard
Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-api' has been created successfully!
```

</div>

#### Generierte Struktur

Erstellt ein Projekt mit folgender Struktur:

```
my-api/
├── .venv/                    # Virtuelle Umgebung
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI-Anwendung
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Konfiguration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # Sammlung der API-Router
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── items.py     # Beispielroute
│   ├── crud/
│   │   ├── __init__.py
│   │   └── items.py         # CRUD-Operationen
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── items.py         # Pydantic-Schemas
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Testdaten
├── tests/
├── scripts/
├── requirements.txt
├── setup.py
└── README.md
```

### `addroute`

Eine neue API-Route zu einem bestehenden FastAPI-Projekt hinzufügen.

#### Syntax

```console
$ fastkit addroute ROUTE_NAME [PROJECT_DIR] [OPTIONS]
```

#### Argumente

| Argument | Beschreibung | Erforderlich |
|----------|-------------|----------|
| `ROUTE_NAME` | Name der neuen Route (Plural empfohlen) | Ja |
| `PROJECT_DIR` | Projektverzeichnis unterhalb Ihres Workspaces (Standard `.`, das aktuelle Verzeichnis) | Nein |

#### Optionen

| Option | Beschreibung | Standard |
|--------|-------------|---------|
| `--help` | Hilfe zum Befehl anzeigen | - |

#### Beispiele

<div class="termy">

```console
$ cd my-api
$ fastkit addroute users
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-api                                   │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-api                                 │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-api'
```

</div>

Sie können auch ein Projekt unter Ihrem Workspace per Namen ansteuern, ohne mit `cd` hineinzuwechseln:

<div class="termy">

```console
$ fastkit addroute users my-api
```

</div>

#### Generierte Dateien

Erstellt diese Dateien im Projekt:

- `src/api/routes/users.py` — Routen-Handler
- `src/crud/users.py` — CRUD-Operationen
- `src/schemas/users.py` — Pydantic-Schemas

Aktualisiert außerdem `src/api/api.py`, um den neuen Router einzubinden.

#### Generierte Endpunkte

Erstellt vollständige CRUD-Endpunkte:

| Methode | Endpunkt | Beschreibung |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | Alle Nutzer abrufen |
| `POST` | `/api/v1/users/` | Neuen Nutzer anlegen |
| `GET` | `/api/v1/users/{user_id}` | Bestimmten Nutzer abrufen |
| `PUT` | `/api/v1/users/{user_id}` | Nutzer aktualisieren |
| `DELETE` | `/api/v1/users/{user_id}` | Nutzer löschen |

### `startdemo`

Ein FastAPI-Projekt aus einer vorgefertigten Vorlage erstellen.

#### Syntax

```console
$ fastkit startdemo [OPTIONS]
```

#### Optionen

| Option | Beschreibung | Standard |
|--------|-------------|---------|
| `--package-manager` | Zu verwendender Paketmanager (pip, uv, pdm, poetry) | uv |
| `--help` | Hilfe zum Befehl anzeigen | - |

#### Interaktive Eingabeaufforderungen

Der Befehl `startdemo` fragt Sie ab:

1. **Projektname**: Verzeichnisname für das neue Projekt
2. **Name des Autors**: Information zum Autor des Pakets
3. **E-Mail des Autors**: Kontakt-E-Mail
4. **Projektbeschreibung**: kurze Beschreibung
5. **Paketmanager-Auswahl**: Wahl zwischen pip, uv, pdm oder poetry (außer wenn mit `--package-manager` angegeben)

#### Verfügbare Vorlagen

| Vorlage | Beschreibung | Funktionen |
|----------|-------------|----------|
| `fastapi-default` | Einfaches FastAPI-Projekt | Basis-CRUD, Mock-Daten |
| `fastapi-async-crud` | Asynchrone Item-Management-API | Async/await, Performance |
| `fastapi-custom-response` | Benutzerdefiniertes Antwortsystem | Benutzerdefinierte Antworten, Paginierung |
| `fastapi-dockerized` | Dockerisierte FastAPI-API | Docker, produktionsreif |
| `fastapi-psql-orm` | PostgreSQL-FastAPI-API | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-empty` | Minimales FastAPI-Projekt | Absolutes Minimum |

#### Beispiele

<div class="termy">

```console
$ fastkit startdemo fastapi-psql-orm
Enter the project name: my-blog
Enter the author name: Jane Smith
Enter the author email: jane@example.com
Enter the project description: Blog API with PostgreSQL

Select package manager (pip, uv, pdm, poetry) [uv]: poetry
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'my-blog' from 'fastapi-psql-orm' has been created!
```

</div>

### `runserver`

Den FastAPI-Entwicklungsserver starten.

#### Syntax

```console
$ fastkit runserver [OPTIONS]
```

#### Optionen

| Option | Kurz | Beschreibung | Standard |
|--------|-------|-------------|---------|
| `--host` | `-h` | Host, an den gebunden werden soll | `127.0.0.1` |
| `--port` | `-p` | Port, an den gebunden werden soll | `8000` |
| `--reload` | `-r` | Automatisches Neuladen aktivieren | `True` |
| `--workers` | `-w` | Anzahl der Worker | `1` |
| `--help` | | Hilfe zum Befehl anzeigen | - |

#### Beispiele

<div class="termy">

```console
# Grundlegende Verwendung (Standardeinstellungen)
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000

# Eigener Host und Port
$ fastkit runserver --host 0.0.0.0 --port 8080
INFO:     Uvicorn running on http://0.0.0.0:8080

# Automatisches Neuladen deaktivieren
$ fastkit runserver --no-reload
INFO:     Uvicorn running on http://127.0.0.1:8000

# Mehrere Worker (Produktion)
$ fastkit runserver --workers 4
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

#### Voraussetzungen

- Muss aus dem Verzeichnis eines FastAPI-Projekts ausgeführt werden
- Das Projekt muss `src/main.py` mit einer FastAPI-App enthalten
- Die virtuelle Umgebung sollte aktiviert sein

### `list-templates`

Alle verfügbaren FastAPI-Projektvorlagen auflisten.

#### Syntax

```console
$ fastkit list-templates [OPTIONS]
```

#### Optionen

| Option | Beschreibung | Standard |
|--------|-------------|---------|
| `--help` | Hilfe zum Befehl anzeigen | - |

#### Beispiele

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

## Umgebungsvariablen

FastAPI-fastkit berücksichtigt folgende Umgebungsvariablen:

| Variable | Beschreibung | Standard |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | Konfigurationsverzeichnis | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Verzeichnis für benutzerdefinierte Vorlagen | Integrierte Vorlagen |
| `FASTKIT_LOG_LEVEL` | Log-Level | `INFO` |

### Beispiele

<div class="termy">

```console
# Eigenes Konfigurationsverzeichnis
$ export FASTKIT_CONFIG_DIR=~/my-fastkit-config
$ fastkit init

# Eigenes Vorlagenverzeichnis
$ export FASTKIT_TEMPLATES_DIR=~/my-templates
$ fastkit list-templates

# Debug-Logging
$ export FASTKIT_LOG_LEVEL=DEBUG
$ fastkit init
```

</div>

## Konfigurationsdateien

FastAPI-fastkit kann Konfigurationsdateien für Standardwerte verwenden.

### Ort der Konfigurationsdatei

1. `$FASTKIT_CONFIG_DIR/config.yaml` (falls `FASTKIT_CONFIG_DIR` gesetzt ist)
2. `~/.fastkit/config.yaml` (Standard)
3. `./fastkit.yaml` (projektspezifisch)

### Konfigurationsformat

```yaml
# ~/.fastkit/config.yaml
default:
  author:
    name: "Your Name"
    email: "your.email@example.com"

  project:
    stack: "standard"
    create_venv: true
    install_deps: true

  server:
    host: "127.0.0.1"
    port: 8000
    reload: true

templates:
  custom_dir: "~/my-templates"

logging:
  level: "INFO"
  file: "~/.fastkit/logs/fastkit.log"
```

## Häufige Workflows

### 1. Neues Projekt erstellen

<div class="termy">

```console
# Create a new project
$ fastkit init
# Follow prompts...

# Navigate to project
$ cd my-awesome-api

# Activate virtual environment
$ source .venv/bin/activate

# Start development server
$ fastkit runserver
```

</div>

### 2. Funktionen zu einem bestehenden Projekt hinzufügen

<div class="termy">

```console
# Mehrere Routen hinzufügen (Projektname als zweites Positionsargument = Projekt im Workspace)
$ fastkit addroute users my-api
$ fastkit addroute products my-api
$ fastkit addroute orders my-api

# API testen
$ fastkit runserver
# Öffnen Sie danach http://127.0.0.1:8000/docs
```

</div>

### 3. Vorlagen für komplexe Projekte nutzen

<div class="termy">

```console
# Verfügbare Vorlagen auflisten
$ fastkit list-templates

# Projekt aus Vorlage erzeugen
$ fastkit startdemo
# Für ein Datenbankprojekt fastapi-psql-orm auswählen

# Datenbank einrichten (für die PostgreSQL-Vorlage)
$ cd my-project
$ docker-compose up -d postgres
$ source .venv/bin/activate
$ alembic upgrade head
$ fastkit runserver
```

</div>

## Fehlerbehebung

### Befehl nicht gefunden

Falls der Befehl `fastkit` nicht gefunden wird:

1. **Installation prüfen:**
   <div class="termy">
   ```console
   $ pip show fastapi-fastkit
   ```
   </div>

2. **Falls nötig neu installieren:**
   <div class="termy">
   ```console
   $ pip uninstall fastapi-fastkit
   $ pip install fastapi-fastkit
   ```
   </div>

3. **PATH prüfen:**
   <div class="termy">
   ```console
   $ which fastkit
   ```
   </div>

### Probleme mit der virtuellen Umgebung

Falls die Erstellung der virtuellen Umgebung fehlschlägt:

1. **Python-Version prüfen:**
   <div class="termy">
   ```console
   $ python --version  # Should be 3.12+
   ```
   </div>

2. **venv-Modul prüfen:**
   <div class="termy">
   ```console
   $ python -m venv --help
   ```
   </div>

3. **Manuelle virtuelle Umgebung:**
   <div class="termy">
   ```console
   $ python -m venv .venv
   $ source .venv/bin/activate
   $ pip install -r requirements.txt
   ```
   </div>

### Server startet nicht

Falls `fastkit runserver` fehlschlägt:

1. **Prüfen Sie, dass Sie im Projektverzeichnis sind**
2. **Sicherstellen, dass `src/main.py` existiert**
3. **Virtuelle Umgebung aktivieren:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

4. **Auf Syntaxfehler prüfen:**
   <div class="termy">
   ```console
   $ python -c "from src.main import app"
   ```
   </div>

### Port bereits in Verwendung

Falls Port 8000 belegt ist:

<div class="termy">

```console
# Use different port
$ fastkit runserver --port 8080

# Or kill existing process
$ lsof -ti:8000 | xargs kill -9
```

</div>

## Fortgeschrittene Nutzung

### Benutzerdefinierte Vorlagen

Sie können benutzerdefinierte Vorlagen erstellen, indem Sie:

1. **Ein Vorlagenverzeichnis anlegen:**
   ```
   my-template/
   ├── src/
   │   └── main.py-tpl
   ├── requirements.txt-tpl
   └── setup.py-tpl
   ```

2. **Eine Umgebungsvariable setzen:**
   <div class="termy">
   ```console
   $ export FASTKIT_TEMPLATES_DIR=~/my-templates
   ```
   </div>

3. **Die benutzerdefinierte Vorlage verwenden:**
   <div class="termy">
   ```console
   $ fastkit startdemo
   # Your custom templates will appear in the list
   ```
   </div>

### Skripten mit FastAPI-fastkit

Sie können FastAPI-fastkit in Skripten verwenden:

```bash
#!/bin/bash
# create-microservices.sh

for service in users products orders; do
    echo "Creating $service service..."
    fastkit init <<EOF
$service-service
Company Team
team@company.com
$service microservice
minimal
y
EOF

    cd "$service-service"
    fastkit addroute "$service"
    cd ..
done
```

### Integration mit CI/CD

Beispiel für einen GitHub-Actions-Workflow:

```yaml
name: Test FastAPI-fastkit Project

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install FastAPI-fastkit
      run: pip install fastapi-fastkit

    - name: Create test project
      run: |
        fastkit init <<EOF
        test-project
        CI
        ci@example.com
        Test project
        standard
        y
        EOF

    - name: Test project
      run: |
        cd test-project
        source .venv/bin/activate
        python -m pytest
```

## Unterstützung von Paketmanagern

FastAPI-fastkit unterstützt mehrere Python-Paketmanager, sodass Sie den auswählen können, der am besten zu Ihrem Workflow passt.

### Unterstützte Paketmanager

| Manager | Beschreibung | Abhängigkeitsdatei | Am besten für |
|---------|-------------|----------------|----------|
| **UV** (Standard) | Schneller Python-Paketmanager | `pyproject.toml` | Geschwindigkeit und Leistung |
| **PDM** | Moderne Python-Abhängigkeitsverwaltung | `pyproject.toml` | Fortgeschrittene Abhängigkeitsauflösung |
| **Poetry** | Python-Abhängigkeitsverwaltung und Packaging | `pyproject.toml` | Poetry-basierte Workflows |
| **PIP** | Standard-Python-Paketmanager | `requirements.txt` | Klassische Python-Entwicklung |

### Paketmanager angeben

#### Globale Konfiguration

Sie können Ihren bevorzugten Paketmanager für alle Projekte festlegen:

```console
# Using command line options
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

#### Projektspezifische Auswahl

Jedes Projekt kann einen anderen Paketmanager verwenden. Die Auswahl erfolgt während der Projekterstellung und beeinflusst:

- **Format der Abhängigkeitsdatei**: jeder Manager erstellt die passenden Dateien
- **Verwaltung der virtuellen Umgebung**: unterschiedliche Aktivierungsmethoden
- **Installation der Abhängigkeiten**: managerspezifische Befehle

### Funktionen der Paketmanager

#### UV (Standard)
- **Schnell**: Rust-basiert, extrem schnelle Abhängigkeitsauflösung
- **Kompatibel**: Drop-in-Ersatz für pip und pip-tools
- **Modern**: Unterstützung für PEP-621-Projektmetadaten

<div class="termy">

```console
$ fastkit init --package-manager uv
# Creates pyproject.toml with UV configuration
```

</div>

#### PDM
- **Modern**: PEP-582- und PEP-621-Unterstützung
- **Fortgeschritten**: ausgefeilte Abhängigkeitsauflösung
- **Flexibel**: mehrere Projekt-Layouts

<div class="termy">

```console
$ fastkit init --package-manager pdm
# Creates pyproject.toml with PDM configuration
```

</div>

#### Poetry
- **Etabliert**: ausgereift und weit verbreitet
- **Integriert**: Build- und Veröffentlichungs-Unterstützung
- **Lockfile**: poetry.lock für reproduzierbare Builds

<div class="termy">

```console
$ fastkit init --package-manager poetry
# Creates pyproject.toml with Poetry configuration
```

</div>

#### PIP
- **Standard**: in Python enthalten
- **Kompatibel**: funktioniert überall
- **Einfach**: geradlinige Abhängigkeitsverwaltung

<div class="termy">

```console
$ fastkit init --package-manager pip
# Creates requirements.txt
```

</div>

### Arbeiten mit Projekten

Nach dem Erstellen eines Projekts mit einem bestimmten Paketmanager:

#### UV-Projekte
```console
cd my-project
uv sync          # Abhängigkeiten installieren
uv add requests  # Neue Abhängigkeit hinzufügen
uv run pytest    # Befehle in der Umgebung ausführen
```

#### PDM-Projekte
```console
cd my-project
pdm install      # Abhängigkeiten installieren
pdm add requests # Neue Abhängigkeit hinzufügen
pdm run pytest   # Befehle in der Umgebung ausführen
```

#### Poetry-Projekte
```console
cd my-project
poetry install      # Abhängigkeiten installieren
poetry add requests # Neue Abhängigkeit hinzufügen
poetry run pytest   # Befehle in der Umgebung ausführen
```

#### PIP-Projekte
```console
cd my-project
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
pip install requests
pytest
```

## Nächste Schritte

Jetzt, da Sie die CLI verstehen:

1. **[Schnellstart](quick-start.md)**: probieren Sie die Befehle praktisch aus
2. **[Ihr erstes Projekt](../tutorial/first-project.md)**: bauen Sie eine vollständige Anwendung
3. **[Mitwirken](../contributing/development-setup.md)**: tragen Sie zu FastAPI-fastkit bei

!!! tip "CLI-Tipps"
    - Verwenden Sie `--help` mit jedem Befehl für detaillierte Hilfe
    - Konfigurieren Sie Standardwerte, um die Projekterstellung zu beschleunigen
    - Verwenden Sie Vorlagen für komplexe Projekt-Setups
    - Kombinieren Sie Befehle für leistungsstarke Workflows

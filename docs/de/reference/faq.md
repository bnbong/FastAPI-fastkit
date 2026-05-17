# Häufig gestellte Fragen

Allgemeine Fragen und Antworten zu FastAPI-fastkit.

## Installation und Setup

### F. Welche Python-Versionen werden unterstützt?

**A.** FastAPI-fastkit erfordert **Python 3.12 oder höher**. Wir empfehlen, die neueste stabile Python-Version für die beste Erfahrung zu verwenden.

<div class="termy">

```console
$ python --version
Python 3.12.1

$ pip install fastapi-fastkit
```

</div>

### F. Wie installiere ich FastAPI-fastkit?

**A.** Sie können FastAPI-fastkit mit pip installieren:

<div class="termy">

```console
# Latest stable version
$ pip install fastapi-fastkit

# Development version from GitHub
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git

# Specific version
$ pip install fastapi-fastkit==1.0.0
```

</div>

### F. Die Installation schlägt mit Berechtigungsfehlern fehl

**A.** Versuchen Sie es in einer virtuellen Umgebung oder mit Nutzerberechtigungen:

<div class="termy">

```console
# Create virtual environment
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # On Windows: fastapi-env\Scripts\activate

# Install in virtual environment
$ pip install fastapi-fastkit

# Or install for current user only
$ pip install --user fastapi-fastkit
```

</div>

### F. Der Befehl `fastkit` wird nach der Installation nicht gefunden

**A.** Das bedeutet meist, dass das Installationsverzeichnis nicht im PATH liegt:

<div class="termy">

```console
# Check if installed
$ pip show fastapi-fastkit

# Find installation location
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__file__)"

# Try running directly
$ python -m fastapi_fastkit --version

# Or add to PATH (Linux/macOS)
$ export PATH="$HOME/.local/bin:$PATH"
```

</div>

## Projekterstellung

### F. Welche Abhängigkeits-Stacks gibt es?

**A.** FastAPI-fastkit bietet drei Abhängigkeits-Stacks:

- **MINIMAL**: FastAPI, Uvicorn, Pydantic, Pydantic-Settings (einfache Web-API)
- **STANDARD**: ergänzt SQLAlchemy, Alembic, pytest (Datenbankunterstützung)
- **FULL**: ergänzt Redis, Celery (Hintergrundaufgaben)

!!! tip "Standard-Paketmanager"
    Der Standard-Paketmanager ist `uv` für schnellere Installation. Sie können auch `pip`, `pdm` oder `poetry` wählen.

<div class="termy">

```console
$ fastkit init
# Select your preferred stack during project creation
```

</div>

### F. Kann ich die Projektvorlage anpassen?

**A.** Ja! Sie können:

1. **Vorhandene Vorlagen nutzen** mit `fastkit startdemo`
2. **Eigene Vorlagen** durch Kopieren und Anpassen bestehender Vorlagen erstellen
3. **Routen schrittweise hinzufügen** mit `fastkit addroute`

<div class="termy">

```console
# Use pre-built templates
$ fastkit list-templates
$ fastkit startdemo

# Add routes to existing project
$ fastkit addroute users .          # Add 'users' route to current directory
$ fastkit addroute users my-project # Add 'users' route to 'my-project'
```

</div>

### F. Wie erstelle ich ein Projekt mit einem bestimmten Namensformat?

**A.** Projektnamen müssen gültige Python-Identifier sein:

- ✅ `my-api`, `blog_system`, `UserService`
- ❌ `my api`, `123project`, `project-name!`

<div class="termy">

```console
$ fastkit init
Enter the project name: my_awesome_api  # Valid
Enter the project name: my-awesome-api  # Valid (hyphens converted to underscores)
```

</div>

### F. Projekterstellung schlägt mit „directory already exists" fehl

**A.** Das Projektverzeichnis existiert bereits. Wählen Sie:

1. **Einen anderen Namen**
2. **Das vorhandene Verzeichnis entfernen** (sofern unbedenklich)
3. **Einen anderen Ablageort verwenden**

<div class="termy">

```console
# Check if directory exists
$ ls my-project

# Remove if safe (CAUTION!)
$ rm -rf my-project

# Or create in different location
$ mkdir projects
$ cd projects
$ fastkit init
```

</div>

### F. Wie nutze ich den interaktiven Modus zur Projekteinrichtung?

**A.** Verwenden Sie `fastkit init --interactive` für eine geführte, schrittweise Einrichtung mit intelligenter Funktionsauswahl:

<div class="termy">

```console
$ fastkit init --interactive
```

</div>

Der interaktive Modus führt Sie der Reihe nach durch diese Schritte:

1. **Projektinformationen** — Name, Autor, E-Mail, Beschreibung.
2. **Architektur-Preset** — wählt das Projekt-Layout. Die empfohlene Standardlösung ist `domain-starter`; drücken Sie Enter, um ihn zu übernehmen. In der [Preset-/Funktionsmatrix](preset-feature-matrix.md) sehen Sie, welches Layout jedes Preset erzeugt und welche Funktionskombinationen noch manuell eingebunden werden müssen.
3. **Funktionsauswahl** — Datenbank, Authentifizierung, Hintergrundaufgaben, Caching, Monitoring, Tests, Utilities, Deployment.
4. **Paketmanager und eigene Pakete** — pip / uv / pdm / poetry, plus zusätzliche Pakete, die Sie fixieren möchten.
5. **Bestätigung** — eine Übersichtstabelle zeigt jede Auswahl (einschließlich Architektur-Preset), bevor das Projekt erstellt wird.

Der interaktive Modus erlaubt Ihnen, aus einem umfassenden Funktionskatalog zu wählen:

| Kategorie | Verfügbare Optionen |
|----------|-------------------|
| **Architektur** | minimal, single-module, classic-layered, **domain-starter** (empfohlene Standardlösung) |
| **Datenbank** | PostgreSQL, MySQL, MongoDB, Redis, SQLite |
| **Authentifizierung** | JWT, OAuth2, FastAPI-Users, sessionbasiert |
| **Hintergrundaufgaben** | Celery, Dramatiq |
| **Tests** | Basic (pytest), Coverage, Advanced (mit faker, factory-boy) |
| **Caching** | Redis mit fastapi-cache2 |
| **Monitoring** | Loguru, OpenTelemetry, Prometheus |
| **Utilities** | CORS, Rate-Limiting, Pagination, WebSocket |
| **Deployment** | Docker, docker-compose mit automatisch generierten Konfigurationen |

Der interaktive Modus erzeugt automatisch:

- `main.py` mit den ausgewählten Funktionen integriert
- Datenbank- und Authentifizierungs-Konfigurationsdateien, sofern die ausgewählten Optionen Code-Generierung unterstützen (z. B. PostgreSQL/MySQL/SQLite/MongoDB für Datenbanken, JWT/FastAPI-Users für Authentifizierung); andere Optionen installieren nur die nötigen Pakete
- Deployment-Dateien passend zur gewählten Deployment-Option (`Dockerfile`, wenn `Docker` gewählt ist, `docker-compose.yml`, wenn `docker-compose` gewählt ist)
- Testkonfiguration basierend auf der gewählten Testoption (Coverage-Einstellungen werden nur eingefügt, wenn `Coverage` oder `Advanced` gewählt ist)

### F. Wie sehe ich die verfügbaren Funktionen für den interaktiven Modus?

**A.** Verwenden Sie den Befehl `list-features`, um alle verfügbaren Funktionen und ihre Pakete anzuzeigen:

<div class="termy">

```console
$ fastkit list-features
# Shows all available features organized by category
# with their associated packages
```

</div>

So sehen Sie, welche Pakete für jede Auswahl installiert würden.

## Routenentwicklung

### F. Wie füge ich Authentifizierung zu meinen Routen hinzu?

**A.** Erstellen Sie eine Dependency für die Authentifizierung:

```python
# src/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # Verify token and return user
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return get_user_from_token(token)

# src/api/routes/users.py
@router.get("/me")
def get_current_user_profile(user = Depends(get_current_user)):
    return user
```

### F. Wie füge ich Datenbank-Modelle zu meinem Projekt hinzu?

**A.** Für die Stacks STANDARD oder FULL erstellen Sie SQLAlchemy-Modelle:

```python
# src/models/users.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### F. Wie validiere ich Anfragedaten?

**A.** Verwenden Sie Pydantic-Modelle in Ihren Schemas:

```python
# src/schemas/users.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### F. Wie verarbeite ich Datei-Uploads?

**A.** Verwenden Sie das `UploadFile` von FastAPI:

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    # Save file
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

## Vorlagen

### F. Welche Vorlagen sind verfügbar?

**A.** FastAPI-fastkit liefert mehrere einsatzbereite Vorlagen:

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-default         │ Simple FastAPI Project            │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-custom-response │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI API            │
│ fastapi-empty           │ Minimal FastAPI Project           │
│ fastapi-mcp             │ MCP (Model Context Protocol) API  │
│ fastapi-psql-orm        │ PostgreSQL FastAPI API            │
│ fastapi-single-module   │ Single-file FastAPI Project       │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

### F. Wie nutze ich eine bestimmte Vorlage?

**A.** Verwenden Sie den Befehl `startdemo`:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Select template: fastapi-psql-orm
```

</div>

### F. Kann ich eigene Vorlagen erstellen?

**A.** Ja! Legen Sie eine Verzeichnisstruktur an und nutzen Sie Vorlagenvariablen:

```
my-template/
├── src/
│   └── main.py-tpl
├── requirements.txt-tpl
└── template.yaml
```

```python
# main.py-tpl
from fastapi import FastAPI

app = FastAPI(title="{{PROJECT_NAME}}")

@app.get("/")
def read_root():
    return {"message": "Hello from {{PROJECT_NAME}}!"}
```

### F. Wie passe ich eine bestehende Vorlage an?

**A.** Vorlagen liegen im Verzeichnis `fastapi_project_template`. Sie können:

1. **Das Repository forken** und Vorlagen anpassen
2. **Eine eigene Vorlage** basierend auf vorhandenen erstellen
3. **Einzelne Dateien überschreiben**, nachdem das Projekt erstellt wurde

## Entwicklungsserver

### F. Wie starte ich den Entwicklungsserver?

**A.** Verwenden Sie den Befehl `runserver` aus dem Projektverzeichnis:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate  # Activate virtual environment
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### F. Der Server startet nicht — „Address already in use"

**A.** Port 8000 ist belegt. Wählen Sie einen anderen Port oder beenden Sie den bestehenden Prozess:

<div class="termy">

```console
# Use different port
$ fastkit runserver --port 8080

# Or find and kill existing process
$ lsof -ti:8000 | xargs kill -9

# On Windows
$ netstat -ano | findstr :8000
$ taskkill /PID <PID> /F
```

</div>

### F. Automatisches Neuladen funktioniert nicht

**A.** Stellen Sie sicher, dass Sie im Projektverzeichnis sind und die virtuelle Umgebung aktiv ist:

<div class="termy">

```console
# Check current directory
$ pwd
/path/to/my-project

# Check virtual environment
$ which python
/path/to/my-project/.venv/bin/python

# Start with explicit reload
$ fastkit runserver --reload
```

</div>

### F. Wie konfiguriere ich den Server für die Produktion?

**A.** Verwenden Sie den Entwicklungsserver nicht in der Produktion. Stattdessen:

```python
# Use gunicorn or similar WSGI server
$ pip install gunicorn
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Docker with the fastapi-dockerized template
$ fastkit startdemo  # Select fastapi-dockerized
$ docker build -t my-app .
$ docker run -p 8000:8000 my-app
```

## Performance und Optimierung

### F. Wie verbessere ich die API-Leistung?

**A.** Mehrere Optimierungsstrategien:

1. **async/await für I/O** nutzen
2. **Caching für teure Operationen** einsetzen
3. **Datenbankabfragen optimieren**
4. **Hintergrundaufgaben für intensive Verarbeitung** nutzen

```python
# Async endpoint
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await users_service.get_user_async(user_id)
    return user

# Background task
from fastapi import BackgroundTasks

@router.post("/send-email")
def send_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(send_notification_email, email)
    return {"message": "Email will be sent in background"}
```

### F. Wie füge ich Caching hinzu?

**A.** Verwenden Sie Redis als Cache:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)
async def get_expensive_data():
    # Expensive operation
    return complex_calculation()
```

### F. Wie verarbeite ich viele parallele Anfragen?

**A.** Verwenden Sie eine passende Server-Konfiguration:

<div class="termy">

```console
# Development
$ fastkit runserver --workers 1  # Single worker for development

# Production
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
$ uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

</div>

## Testen

### F. Wie führe ich Tests aus?

**A.** Verwenden Sie pytest aus dem Projektverzeichnis:

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate
$ python -m pytest

# With coverage
$ python -m pytest --cov=src

# Specific test file
$ python -m pytest tests/test_users.py

# With verbose output
$ python -m pytest -v
```

</div>

### F. Wie schreibe ich API-Tests?

**A.** Verwenden Sie den Test-Client von FastAPI:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user():
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
```

### F. Wie mocke ich externe Abhängigkeiten?

**A.** Verwenden Sie pytest-Fixtures und Mocking:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    with patch('src.database.get_db') as mock_db:
        mock_db.return_value = Mock()
        yield mock_db

def test_user_creation_with_mock_db(mock_database):
    # Test with mocked database
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
```

## Mitwirken

### F. Wie kann ich zu FastAPI-fastkit beitragen?

**A.** Folgen Sie diesen Schritten:

1. **Fork** des Repositorys auf GitHub
2. **Entwicklungsumgebung einrichten**
3. **Feature-Branch erstellen**
4. **Änderungen mit Tests** vornehmen
5. **Pull-Request einreichen**

<div class="termy">

```console
$ git clone https://github.com/yourusername/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make dev-setup  # Set up development environment
$ git checkout -b feature/my-feature
# Make changes...
$ make dev-check  # Format, lint, and test
$ git commit -m "feat: add new feature"
$ git push origin feature/my-feature
```

</div>

### F. Was sollte eine Pull-Request enthalten?

**A.** Jede Pull-Request sollte enthalten:

- [ ] **Klare Beschreibung** der Änderungen
- [ ] **Tests** für neue Funktionen
- [ ] **Dokumentations-Updates**, falls nötig
- [ ] **Code-Richtlinien** befolgen
- [ ] **Alle Prüfungen grün**

### F. Wie melde ich einen Bug?

**A.** Erstellen Sie ein Issue auf GitHub mit:

1. **Fehlerbeschreibung** und erwartetem Verhalten
2. **Schritten zur Reproduktion**
3. **Umgebungsinformationen** (OS, Python-Version usw.)
4. **Fehlermeldungen** oder Logs
5. **Minimalbeispiel**, falls möglich

### F. Wie schlage ich eine neue Funktion vor?

**A.** Öffnen Sie ein Feature-Request-Issue mit:

1. **Klarer Beschreibung** der Funktion
2. **Anwendungsfall** und Motivation
3. **Implementierungsvorschlag** (optional)
4. **Beispielen** ähnlicher Funktionen

## Fehlerbehebung

### F. Ich bekomme Import-Fehler

**A.** Prüfen Sie Ihren Python-Pfad und die virtuelle Umgebung:

<div class="termy">

```console
# Check virtual environment is activated
$ which python
/path/to/project/.venv/bin/python

# Check Python path
$ python -c "import sys; print(sys.path)"

# Reinstall in editable mode (for development)
$ pip install -e .
```

</div>

### F. Probleme mit der Datenbankverbindung

**A.** Bei Datenbankvorlagen sicherstellen, dass die Datenbank läuft:

<div class="termy">

```console
# PostgreSQL template
$ docker-compose up -d postgres  # Start database
$ alembic upgrade head            # Run migrations

# Check connection
$ docker-compose logs postgres
```

</div>

### F. Vorlagendateien werden nicht gefunden

**A.** Das deutet meist auf ein Problem mit dem Vorlagenpfad hin:

<div class="termy">

```console
# Check available templates
$ fastkit list-templates

# Check template directory
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__path__)"

# Reinstall if templates missing
$ pip uninstall fastapi-fastkit
$ pip install fastapi-fastkit
```

</div>

### F. Pre-Commit-Hooks schlagen fehl

**A.** Installieren und ausführen:

<div class="termy">

```console
$ pip install pre-commit
$ pre-commit install
$ pre-commit run --all-files

# Fix formatting issues
$ black src/ tests/
$ isort src/ tests/
```

</div>

### F. Tests scheitern in CI, laufen aber lokal durch

**A.** Häufige Ursachen und Lösungen:

1. **Umgebungsunterschiede**: prüfen, ob die Python-Versionen übereinstimmen
2. **Fehlende Abhängigkeiten**: sicherstellen, dass Test-Abhängigkeiten installiert sind
3. **Pfad-Probleme**: absolute Imports verwenden
4. **Timing-Probleme**: in asynchronen Tests passende Wartezeiten einbauen

<div class="termy">

```console
# Test with same Python version as CI
$ python3.12 -m pytest

# Check for missing dependencies
$ pip install -r requirements-dev.txt

# Run tests in isolated environment
$ tox
```

</div>

## Hilfe finden

### F. Wo bekomme ich Hilfe?

**A.** Mehrere Möglichkeiten, Hilfe zu erhalten:

- **GitHub Issues**: für Bugs und Feature-Requests
- **GitHub Discussions**: für Fragen und Community-Support
- **Dokumentation**: Nutzerhandbücher und Tutorials
- **Code-Beispiele**: vorhandene Vorlagen und Tests prüfen

### F. Wie bleibe ich auf dem Laufenden?

**A.** Verfolgen Sie die Projekt-Updates:

- **Repository „Watchen"** auf GitHub
- **Releases prüfen** für neue Funktionen
- **Changelog lesen** für Breaking Changes
- **Best Practices** in der Dokumentation befolgen

!!! tip "Profi-Tipps"
    - Verwenden Sie immer virtuelle Umgebungen für Python-Projekte
    - Halten Sie Ihre FastAPI-fastkit-Installation aktuell
    - Verwenden Sie `fastkit --help`, um verfügbare Befehle zu sehen
    - Schauen Sie in die Dokumentation, wenn Sie nicht weiterkommen
    - Zögern Sie nicht, Fragen in GitHub Discussions zu stellen

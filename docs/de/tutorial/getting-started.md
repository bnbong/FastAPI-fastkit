# Erste Schritte

Ein umfassendes Schritt-für-Schritt-Tutorial zum Einstieg in FastAPI-fastkit. Dieser Leitfaden führt Sie in etwa 15 Minuten von der Installation bis zum Ausführen Ihrer ersten API.

## Voraussetzungen

Bevor Sie starten, stellen Sie sicher, dass Sie haben:

- **Python 3.12 oder höher** auf Ihrem System installiert
- **Grundkenntnisse in Python** (Variablen, Funktionen, Klassen)
- Zugang zum **Terminal / zur Kommandozeile**
- **Einen Texteditor oder eine IDE** (VS Code, PyCharm usw.)

## Schritt 1: Installation

Zuerst installieren wir FastAPI-fastkit. Wir empfehlen die Nutzung einer virtuellen Umgebung, um Ihre Projekte zu isolieren.

### Option A: mit pip (klassisch)

<div class="termy">

```console
$ pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### Option B: mit UV (empfohlen — schneller)

UV ist ein schneller Python-Paketmanager. Falls Sie UV nicht installiert haben:

<div class="termy">

```console
# Install UV first
$ curl -LsSf https://astral.sh/uv/install.sh | sh

# Then install FastAPI-fastkit
$ uv pip install fastapi-fastkit
---> 100%
Successfully installed fastapi-fastkit
```

</div>

### Option C: mit virtueller Umgebung

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # On Windows: fastapi-env\Scripts\activate
$ pip install fastapi-fastkit
```

</div>

### Installation überprüfen

Überprüfen Sie, dass FastAPI-fastkit korrekt installiert ist:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

## Schritt 2: Ihr erstes Projekt erstellen

Erstellen wir nun Ihr erstes FastAPI-Projekt mit dem interaktiven Befehl `init`:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-api
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI project

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-first-api            │
│ Author       │ Your Name               │
│ Author Email │ your.email@example.com  │
│ Description  │ My first FastAPI project│
└──────────────┴─────────────────────────┘

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

Creating virtual environment...
Installing dependencies...
✨ FastAPI project 'my-first-api' has been created successfully!
```

</div>

!!! note "Stack-Auswahl"
    Wir haben für dieses Tutorial **MINIMAL** gewählt, um es einfach zu halten. Für echte Projekte ziehen Sie **STANDARD** (mit Datenbankunterstützung) oder **FULL** (mit Hintergrundaufgaben) in Betracht.

## Schritt 3: In Ihr Projekt wechseln

Wechseln Sie in das neu erstellte Projektverzeichnis:

<div class="termy">

```console
$ cd my-first-api
$ ls -la
total 32
drwxr-xr-x  8 user user  256 Dec  7 10:30 .
drwxr-xr-x  3 user user   96 Dec  7 10:30 ..
drwxr-xr-x  5 user user  160 Dec  7 10:30 .venv
-rw-r--r--  1 user user  156 Dec  7 10:30 README.md
-rw-r--r--  1 user user  243 Dec  7 10:30 requirements.txt
drwxr-xr-x  3 user user   96 Dec  7 10:30 scripts
-rw-r--r--  1 user user 1245 Dec  7 10:30 setup.py
drwxr-xr-x  8 user user  256 Dec  7 10:30 src
drwxr-xr-x  3 user user   96 Dec  7 10:30 tests
```

</div>

## Schritt 4: Virtuelle Umgebung aktivieren

Ihr Projekt enthält eine vorkonfigurierte virtuelle Umgebung. Aktivieren Sie sie:

<div class="termy">

```console
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
(my-first-api) $
```

</div>

Beachten Sie, dass Ihre Terminal-Eingabeaufforderung jetzt `(my-first-api)` anzeigt, was darauf hinweist, dass die virtuelle Umgebung aktiv ist.

## Schritt 5: Entwicklungsserver starten

Nun kommt der spannende Teil — starten wir Ihren FastAPI-Server:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720] using StatReload
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

🎉 **Glückwunsch!** Ihr FastAPI-Server läuft jetzt.

## Schritt 6: Ihre API testen

Lassen Sie uns Ihre API auf mehrere Arten testen:

### Methode 1: Browser

Öffnen Sie Ihren Browser und besuchen Sie:

- **Haupt-API-Endpunkt**: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Sie sollten sehen:
```json
{"message": "Hello World"}
```

### Methode 2: Interaktive API-Dokumentation

Besuchen Sie die automatisch generierte API-Dokumentation:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Die Swagger UI ist besonders nützlich — Sie können:

- alle verfügbaren Endpunkte sehen
- Endpunkte direkt im Browser testen
- Anfrage-/Antwortschemas einsehen
- OpenAPI-Spezifikationen herunterladen

### Methode 3: Kommandozeile

Öffnen Sie ein neues Terminal (lassen Sie den Server weiterlaufen) und testen Sie mit curl:

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Hello World"}

$ curl http://127.0.0.1:8000/api/v1/items/
[]

$ curl -X POST "http://127.0.0.1:8000/api/v1/items/" \
     -H "Content-Type: application/json" \
     -d '{"title": "My First Item", "description": "This is a test item"}'
{
  "id": 1,
  "title": "My First Item",
  "description": "This is a test item"
}
```

</div>

## Schritt 7: Ihre Projektstruktur verstehen

Erkunden wir, was FastAPI-fastkit für Sie generiert hat:

<div class="termy">

```console
$ tree src
src/
├── __init__.py
├── main.py                 # Einstiegspunkt der FastAPI-Anwendung
├── core/
│   ├── __init__.py
│   └── config.py          # Anwendungskonfiguration
├── api/
│   ├── __init__.py
│   ├── api.py             # Haupt-Router der API
│   └── routes/
│       ├── __init__.py
│       └── items.py       # API-Endpunkte für Items
├── crud/
│   ├── __init__.py
│   └── items.py           # Geschäftslogik für Items
├── schemas/
│   ├── __init__.py
│   └── items.py           # Schemas zur Datenvalidierung
└── mocks/
    ├── __init__.py
    └── mock_items.json    # Beispieldaten
```

</div>

### Wichtige Dateien erklärt

**`src/main.py`** — das Herz Ihrer Anwendung:
```python
from fastapi import FastAPI
from src.api.api import api_router
from src.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Hello World"}
```

**`src/core/config.py`** — Anwendungseinstellungen:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "my-first-api"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()
```

**`src/api/routes/items.py`** — API-Endpunkte:
```python
from typing import List
from fastapi import APIRouter, HTTPException
from src.schemas.items import Item, ItemCreate, ItemUpdate
from src.crud.items import items_crud

router = APIRouter()

@router.get("/", response_model=List[Item])
def read_items():
    """Get all items"""
    return items_crud.get_all()

@router.post("/", response_model=Item)
def create_item(item: ItemCreate):
    """Create a new item"""
    return items_crud.create(item)
```

## Schritt 8: Ihre erste benutzerdefinierte Route hinzufügen

Fügen wir eine neue API-Route hinzu, um das Gelernte zu üben:

<div class="termy">

```console
$ fastkit addroute users my-first-api
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-api                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-api                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-api'? [Y/n]: y

✨ Successfully added new route 'users' to project 'my-first-api'
```

</div>

Der Server startet automatisch neu und Sie verfügen nun über neue Endpunkte:

- `GET /api/v1/users/` — alle Nutzer abrufen
- `POST /api/v1/users/` — einen neuen Nutzer anlegen
- `GET /api/v1/users/{user_id}` — einen bestimmten Nutzer abrufen
- und mehr…

### Ihre neue Route testen

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}

$ curl http://127.0.0.1:8000/api/v1/users/
[
  {
    "id": 1,
    "title": "John Doe",
    "description": "Software Developer"
  }
]
```

</div>

## Schritt 9: Den Code erkunden und anpassen

Nehmen wir eine kleine Anpassung vor, um zu verstehen, wie der Code funktioniert.

### Die Willkommensnachricht anpassen

Öffnen Sie `src/main.py` in Ihrem Texteditor und ändern Sie den Root-Endpunkt:

```python
@app.get("/")
def read_root():
    return {"message": "Welcome to my first FastAPI application!"}
```

Speichern Sie die Datei. Dank automatischem Neuladen startet Ihr Server automatisch neu.

### Die Änderung testen

<div class="termy">

```console
$ curl http://127.0.0.1:8000
{"message":"Welcome to my first FastAPI application!"}
```

</div>

### Einen neuen Endpunkt hinzufügen

Fügen wir einen einfachen Endpunkt in `src/main.py` hinzu:

```python
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}!"}
```

### Den neuen Endpunkt testen

<div class="termy">

```console
$ curl http://127.0.0.1:8000/hello/World
{"message":"Hello, World!"}

$ curl http://127.0.0.1:8000/hello/FastAPI
{"message":"Hello, FastAPI!"}
```

</div>

## Schritt 10: Tests ausführen

Ihr Projekt enthält vorkonfigurierte Tests. Lassen Sie sie laufen:

<div class="termy">

```console
$ python -m pytest
======================== test session starts ========================
collected 5 items

tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED

======================== 5 passed in 0.45s ========================
```

</div>

## Kernkonzepte verstehen

### 1. Struktur einer FastAPI-Anwendung

FastAPI-fastkit folgt einer **modularen Architektur**:

- **`main.py`**: Einstiegspunkt der Anwendung und globale Endpunkte
- **`api/`**: Organisation der API-Routen
- **`core/`**: Konfiguration und Einstellungen der Anwendung
- **`crud/`**: Geschäftslogik und Datenoperationen
- **`schemas/`**: Datenvalidierung und Serialisierung
- **`tests/`**: Automatisierte Tests

### 2. Abhängigkeitsverwaltung

Ihr Projekt nutzt moderne Python-Abhängigkeitsverwaltung:

- **Virtuelle Umgebung**: isolierte Python-Umgebung
- **requirements.txt**: listet alle Abhängigkeiten
- **Automatische Installation**: Abhängigkeiten werden bei der Projekterstellung installiert

### 3. Entwicklungsserver

FastAPI-fastkit verwendet **Uvicorn** als ASGI-Server:

- **Automatisches Neuladen**: startet automatisch neu, wenn sich Code ändert
- **Schneller Start**: schnelle Entwicklungsiteration
- **Produktionsreif**: derselbe Server wird in der Produktion verwendet

### 4. API-Dokumentation

FastAPI generiert automatisch:

- **OpenAPI-Spezifikation**: branchenstandardisierte API-Dokumentation
- **Swagger UI**: interaktive Testoberfläche
- **ReDoc**: alternative Dokumentationsansicht

## Nächste Schritte

Glückwunsch! Sie haben erfolgreich:

✅ FastAPI-fastkit installiert
✅ Ihr erstes Projekt erstellt
✅ den Entwicklungsserver gestartet
✅ Ihre API-Endpunkte getestet
✅ eine neue Route hinzugefügt
✅ vorhandenen Code angepasst
✅ Tests ausgeführt

### Weiter lernen

1. **[Ihr erstes Projekt](first-project.md)**: bauen Sie eine vollständige Blog-API mit fortgeschrittenen Funktionen
2. **[Routen hinzufügen](../user-guide/adding-routes.md)**: lernen Sie, komplexe API-Endpunkte zu erstellen
3. **[Vorlagen verwenden](../user-guide/using-templates.md)**: erkunden Sie vorgefertigte Projektvorlagen

### Mehr experimentieren

Probieren Sie diese Herausforderungen aus:

1. **Validierung hinzufügen**: erweitern Sie Schemata um Validierungsregeln
2. **Benutzerdefinierte Antworten**: ändern Sie Antwortformate in Routen
3. **Umgebungsvariablen**: nutzen Sie `.env`-Dateien für Konfiguration
4. **Middleware hinzufügen**: implementieren Sie CORS oder Authentifizierung
5. **Datenbankintegration**: wechseln Sie auf den STANDARD-Stack für Datenbankunterstützung

### Häufige Probleme und Lösungen

**Server startet nicht:**

- Prüfen Sie, dass Sie im Projektverzeichnis sind
- Stellen Sie sicher, dass die virtuelle Umgebung aktiviert ist
- Überprüfen Sie, dass keine Syntaxfehler im Code vorliegen

**Import-Fehler:**

- Stellen Sie sicher, dass alle `__init__.py`-Dateien existieren
- Prüfen Sie, dass Ihre Importpfade korrekt sind
- Vergewissern Sie sich, dass Sie die virtuelle Umgebung nutzen

**Port bereits in Verwendung:**
```console
$ fastkit runserver --port 8080
```

## Best Practices, die Sie gelernt haben

1. **Virtuelle Umgebungen**: immer isolierte Umgebungen verwenden
2. **Projektstruktur**: organisierter, modularer Architektur folgen
3. **Automatisches Neuladen**: Entwicklungsserver für schnelle Iteration nutzen
4. **API-Dokumentation**: automatische Dokumentationsgenerierung ausnutzen
5. **Testen**: Tests während der Entwicklung regelmäßig ausführen

!!! tip "Entwicklungstipps"
    - Halten Sie den Entwicklungsserver während des Codens am Laufen
    - Nutzen Sie die interaktive Doku (`/docs`), um Ihre APIs zu testen
    - Beobachten Sie das Terminal auf hilfreiche Fehlermeldungen
    - Committen Sie Ihren Code regelmäßig in die Versionsverwaltung

Sie sind nun bereit, beeindruckende APIs mit FastAPI-fastkit zu bauen! 🚀

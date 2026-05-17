# Vorlagen verwenden

FastAPI-fastkit bietet vorgefertigte Projektvorlagen, mit denen Sie schnell mit verschiedenen Tech-Stacks starten können.

## Verfügbare Vorlagen

Prüfen Sie die verfügbaren Vorlagen mit dem Befehl `list-templates`:

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

## Beschreibungen der Vorlagen

### 1. `fastapi-default`

**Einfaches FastAPI-Projekt**

- Grundlegende FastAPI-Einrichtung mit essenziellen Funktionen
- Itemverwaltung mit Mock-Daten
- Ideal zum Lernen und für einfache APIs
- Enthält grundlegende CRUD-Operationen

**Am besten für:**

- FastAPI-Einsteiger
- Einfache Web-APIs
- Lernen und Prototyping

### 2. `fastapi-async-crud`

**Asynchrone Item-Management-API**

- Vollständig asynchrone FastAPI-Anwendung
- Erweiterte CRUD-Operationen mit async/await
- Bessere Leistung bei I/O-Operationen
- Mock-Datenspeicher mit asynchronen Mustern

**Am besten für:**

- Hochleistungsanwendungen
- I/O-intensive Operationen
- Moderne asynchrone Python-Entwicklung

### 3. `fastapi-custom-response`

**Asynchrone Item-Management-API mit benutzerdefiniertem Antwortsystem**

- Benutzerdefinierte Antwortmodelle und Formatierung
- Erweiterte Fehlerbehandlung
- Unterstützung für Paginierung
- Benutzerdefinierte HTTP-Statuscodes und Antworten

**Am besten für:**

- APIs, die bestimmte Antwortformate benötigen
- Erweiterte Anforderungen an die Fehlerbehandlung
- Benutzerdefinierte Geschäftslogik in Antworten

### 4. `fastapi-dockerized`

**Dockerisierte FastAPI-Item-Management-API**

- Vollständige Docker-Containerisierung
- Produktionsreife Deployment-Konfiguration
- Mehrstufige Docker-Builds
- Umgebungsbasierte Konfiguration

**Am besten für:**

- Produktionsdeployments
- Containerisierte Umgebungen
- DevOps- und CI/CD-Pipelines

### 5. `fastapi-psql-orm`

**Dockerisierte FastAPI-Item-Management-API mit PostgreSQL**

- PostgreSQL-Datenbankintegration
- SQLAlchemy-ORM mit Alembic-Migrationen
- Docker Compose für die lokale Entwicklung
- Vollständige CRUD-Operationen auf der Datenbank

**Am besten für:**

- Datenbankgetriebene Anwendungen
- Produktionsreife Datenspeicherung
- Komplexe Datenbeziehungen

### 6. `fastapi-empty`

**Minimales FastAPI-Projekt**

- Absolute Minimal-Einrichtung von FastAPI
- Keine vorgefertigten Funktionen
- Leere Leinwand für individuelle Entwicklung

**Am besten für:**

- Bei Null beginnen
- Minimale Abhängigkeiten
- Spezielle Architekturanforderungen

## Ein Projekt aus einer Vorlage erstellen

Verwenden Sie den Befehl `startdemo`, um ein Projekt aus einer Vorlage zu erstellen:

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog-api
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Blog API with PostgreSQL

Available Templates:
           fastapi-default
┌─────────────┬──────────────────────┐
│ Description │ Simple FastAPI       │
│             │ Project              │
│ Stack       │ FastAPI, Uvicorn     │
│ Database    │ Mock Data            │
│ Features    │ Basic CRUD           │
└─────────────┴──────────────────────┘

           fastapi-psql-orm
┌─────────────┬──────────────────────┐
│ Description │ Dockerized FastAPI   │
│             │ Item Management API  │
│             │ with PostgreSQL      │
│ Stack       │ FastAPI, PostgreSQL, │
│             │ SQLAlchemy, Docker   │
│ Database    │ PostgreSQL           │
│ Features    │ Full ORM, Migrations │
└─────────────┴──────────────────────┘

Select template (fastapi-default, fastapi-async-crud, fastapi-custom-response, fastapi-dockerized, fastapi-psql-orm, fastapi-empty): fastapi-psql-orm

           Project Information
┌──────────────┬─────────────────────┐
│ Project Name │ my-blog-api         │
│ Author       │ John Doe            │
│ Author Email │ john@example.com    │
│ Description  │ Blog API with       │
│              │ PostgreSQL          │
└──────────────┴─────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ psycopg2-binary   │
│ Dependency 6 │ python-dotenv     │
│ Dependency 7 │ pytest            │
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

✨ FastAPI project 'my-blog-api' from 'fastapi-psql-orm' has been created successfully!
```

</div>

## Funktionsvergleich der Vorlagen

| Funktion | Default | Async CRUD | Custom Response | Dockerized | PostgreSQL ORM | Empty |
|---------|---------|------------|-----------------|------------|----------------|-------|
| **FastAPI-Basis** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Mock-Daten** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Async-Unterstützung** | Basis | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Benutzerdefinierte Antworten** | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Docker** | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Datenbank** | Mock | Mock | Mock | Mock | PostgreSQL | Keine |
| **ORM** | ❌ | ❌ | ❌ | ❌ | SQLAlchemy | ❌ |
| **Migrationen** | ❌ | ❌ | ❌ | ❌ | Alembic | ❌ |
| **Testen** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Am besten für** | Lernen | Leistung | Benutzerdefinierte APIs | Produktion | Datenbank-Apps | Individuelles |

## Vorlagenspezifische Einrichtung

### `fastapi-psql-orm` verwenden

Diese Vorlage enthält eine vollständige PostgreSQL-Einrichtung. Nach der Erstellung:

1. **PostgreSQL mit Docker starten:**

<div class="termy">

```console
$ cd my-blog-api
$ docker-compose up -d postgres
Starting my-blog-api_postgres_1 ... done
```

</div>

2. **Datenbankmigrationen ausführen:**

<div class="termy">

```console
$ source .venv/bin/activate
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade -> bedcdc35b64a, first alembic
```

</div>

3. **API-Server starten:**

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### `fastapi-dockerized` verwenden

Diese Vorlage bietet vollständige Docker-Unterstützung:

1. **Docker-Image bauen:**

<div class="termy">

```console
$ cd my-dockerized-api
$ docker build -t my-dockerized-api .
Successfully built abc123def456
Successfully tagged my-dockerized-api:latest
```

</div>

2. **Container ausführen:**

<div class="termy">

```console
$ docker run -p 8000:8000 my-dockerized-api
INFO:     Uvicorn running on http://0.0.0.0:8000
```

</div>

### `fastapi-custom-response` verwenden

Diese Vorlage enthält fortgeschrittene Antwortbehandlung:

1. **Benutzerdefinierte Antwortmodelle:**

```python
from src.helper.pagination import PaginatedResponse
from src.schemas.base import StandardResponse

@router.get("/", response_model=PaginatedResponse[Item])
def read_items(skip: int = 0, limit: int = 10):
    items = items_crud.get_multi(skip=skip, limit=limit)
    total = items_crud.count()

    return PaginatedResponse(
        data=items,
        total=total,
        page=skip // limit + 1,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=StandardResponse[Item])
def create_item(item: ItemCreate):
    new_item = items_crud.create(item)
    return StandardResponse(
        data=new_item,
        message="Item created successfully",
        status_code=201
    )
```

2. **Erweiterte Fehlerbehandlung:**

```python
from src.helper.exceptions import ItemNotFoundError, ValidationError

@router.get("/{item_id}", response_model=StandardResponse[Item])
def read_item(item_id: int):
    try:
        item = items_crud.get(item_id)
        return StandardResponse(data=item)
    except ItemNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Item with id {item_id} not found"
        )
```

## Projektstruktur der Vorlagen

Jede Vorlage folgt einer konsistenten, aber angepassten Struktur:

### Struktur von `fastapi-default`
```
my-project/
├── src/
│   ├── main.py
│   ├── core/config.py
│   ├── api/
│   │   ├── api.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   └── mocks/mock_items.json
├── tests/
├── scripts/
└── requirements.txt
```

### Struktur von `fastapi-psql-orm`
```
my-project/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── db.py
│   ├── api/
│   │   ├── api.py
│   │   ├── deps.py
│   │   └── routes/items.py
│   ├── crud/items.py
│   ├── schemas/items.py
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   └── utils/
├── tests/
├── scripts/
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── requirements.txt
```

## Vorlagen anpassen

Nachdem Sie ein Projekt aus einer Vorlage erstellt haben, können Sie es anpassen:

### 1. Neue Routen hinzufügen

<div class="termy">

```console
$ fastkit addroute posts my-blog-api
$ fastkit addroute users my-blog-api
$ fastkit addroute comments my-blog-api
```

</div>

### 2. Konfiguration anpassen

Bearbeiten Sie `src/core/config.py` nach Ihren Bedürfnissen:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "My Blog API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database settings (for PostgreSQL templates)
    DATABASE_URL: str = "postgresql://user:password@localhost/dbname"

    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

### 3. Umgebungsvariablen hinzufügen

Erstellen Sie eine `.env`-Datei im Projekt-Stammverzeichnis:

```env
# .env
PROJECT_NAME=My Blog API
VERSION=1.0.0
DEBUG=True

# Database (for PostgreSQL templates)
DATABASE_URL=postgresql://user:password@localhost:5432/myblogdb
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=myblogdb

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Vorlagen testen

Jede Vorlage wird mit vorkonfigurierten Tests ausgeliefert:

<div class="termy">

```console
$ cd my-blog-api
$ source .venv/bin/activate
$ python -m pytest

======================== test session starts ========================
tests/test_items.py::test_create_item PASSED
tests/test_items.py::test_read_items PASSED
tests/test_items.py::test_read_item PASSED
tests/test_items.py::test_update_item PASSED
tests/test_items.py::test_delete_item PASSED
======================== 5 passed in 0.23s ========================
```

</div>

## Entwicklungs-Workflow mit Vorlagen

### 1. Die passende Vorlage wählen

- **Lernen / einfache APIs**: `fastapi-default`
- **Hohe Leistung**: `fastapi-async-crud`
- **Benutzerdefinierte Antwortformate**: `fastapi-custom-response`
- **Produktions-Deployment**: `fastapi-dockerized`
- **Datenbankanwendungen**: `fastapi-psql-orm`
- **Eigene Architektur**: `fastapi-empty`

### 2. Erstellen und Einrichten

<div class="termy">

```console
$ fastkit startdemo
# Follow the prompts
$ cd your-project
$ source .venv/bin/activate
```

</div>

### 3. Entwicklung

<div class="termy">

```console
# Start development server
$ fastkit runserver

# Tests ausführen
$ python -m pytest

# Neue Funktionen hinzufügen
$ fastkit addroute new-resource your-project
```

</div>

### 4. Deployment

Für die Produktionsvorlagen (`fastapi-dockerized`, `fastapi-psql-orm`):

<div class="termy">

```console
# Build for production
$ docker build -t your-app .

# Deploy with Docker Compose
$ docker-compose up -d
```

</div>

## Best Practices

### 1. Vorlagen mit Bedacht wählen

- Beginnen Sie mit einfacheren Vorlagen zum Lernen
- Nutzen Sie Datenbankvorlagen für datengetriebene Apps
- Verwenden Sie Docker-Vorlagen für Produktionsdeployments

### 2. Umgebungsverwaltung

- Verwenden Sie immer `.env`-Dateien für die Konfiguration
- Committen Sie niemals sensible Daten in die Versionsverwaltung
- Nutzen Sie unterschiedliche Umgebungen für Entwicklung/Produktion

### 3. Anpassungsstrategie

- Fügen Sie neue Routen mit `fastkit addroute` hinzu
- Passen Sie vorhandenen Code an Ihre Geschäftslogik an
- Halten Sie die Projektstruktur übersichtlich

### 4. Testen

- Führen Sie Tests während der Entwicklung regelmäßig aus
- Ergänzen Sie Tests für neu implementierte Funktionen
- Nutzen Sie die mitgelieferte Teststruktur als Leitfaden

## Fehlerbehebung

### Probleme mit der Datenbankverbindung (PostgreSQL-Vorlagen)

Wenn Sie keine Verbindung zu PostgreSQL herstellen können:

1. **Prüfen Sie, ob Docker läuft:**

   <div class="termy">
   ```console
   $ docker ps
   ```
   </div>

2. **PostgreSQL-Container überprüfen:**

   <div class="termy">
   ```console
   $ docker-compose logs postgres
   ```
   </div>

3. **Umgebungsvariablen prüfen:**

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   ```

### Fehlgeschlagene Docker-Builds

Wenn der Docker-Build fehlschlägt:

1. **Syntax des Dockerfile prüfen**
2. **Sicherstellen, dass alle Dateien vorhanden sind**
3. **Prüfen, ob der Docker-Daemon läuft**

### Fehlende Abhängigkeiten

Wenn Sie Import-Fehler erhalten:

1. **Aktivieren Sie die virtuelle Umgebung:**
   <div class="termy">
   ```console
   $ source .venv/bin/activate
   ```
   </div>

2. **Abhängigkeiten installieren:**
   <div class="termy">
   ```console
   $ pip install -r requirements.txt
   ```
   </div>

## Nächste Schritte

Jetzt, da Sie die Vorlagen verstehen:

1. **[Ihr erstes Projekt](../tutorial/first-project.md)**: bauen Sie eine vollständige Anwendung
2. **[Routen hinzufügen](adding-routes.md)**: erweitern Sie Ihr vorlagenbasiertes Projekt
3. **[CLI-Referenz](cli-reference.md)**: meistern Sie alle verfügbaren Befehle

!!! tip "Tipps zu Vorlagen"
    - Vorlagen sind hervorragende Ausgangspunkte, keine fertigen Lösungen
    - Passen Sie Vorlagen an Ihre spezifischen Anforderungen an
    - Studieren Sie den Code der Vorlagen, um FastAPI-Best-Practices zu lernen
    - Nutzen Sie Versionsverwaltung, um Ihre Anpassungen nachzuhalten

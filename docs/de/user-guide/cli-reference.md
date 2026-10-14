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
| `--interactive` | Geführte Einrichtung: zuerst Architektur-Preset, dann Funktionsauswahl | aus |
| `--config <path>` | Das Projekt ohne Eingabeaufforderungen aus einer gespeicherten Konfigurationsdatei erstellen | - |
| `--save-config <path>` | Zusammen mit `--interactive` die beantwortete Konfiguration unter diesem Pfad speichern | - |
| `--project-name` | Projektname (wird abgefragt, falls weggelassen) | - |
| `--author` | Name des Autors (wird abgefragt, falls weggelassen) | - |
| `--author-email` | E-Mail des Autors (wird abgefragt, falls weggelassen) | - |
| `--description` | Projektbeschreibung (wird abgefragt, falls weggelassen) | - |
| `--package-manager` | Zu verwendender Paketmanager (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Zeigt die Dateien und Pakete an, die erstellt würden, ohne etwas zu schreiben | aus |
| `--no-venv` | Erstellung der virtuellen Umgebung überspringen (impliziert `--no-install`) | aus |
| `--no-install` | Installation der Abhängigkeiten überspringen | aus |
| `--yes` / `-y` | Beim Bereitstellen des Projekts im aktuellen Verzeichnis nicht nachfragen, bevor vorhandene Dateien überschrieben werden | aus |
| `--help` | Hilfe zum Befehl anzeigen | - |

#### Konfigurationsdateien (`--config` / `--save-config`)

Die Antworten einer interaktiven Sitzung sind ein einfaches Mapping, und dieses Mapping lässt sich über eine Datei weitergeben. So wird die Projekterstellung zu etwas, das Sie committen, prüfen und erneut abspielen können.

```console
# eine interaktive Sitzung aufzeichnen
$ fastkit init --interactive --save-config fastkit.config.json

# später ganz ohne Eingabeaufforderungen erneut abspielen
$ fastkit init --config fastkit.config.json
```

Wenn Sie `--save-config` nicht übergeben, fragt ein interaktiver Lauf, der bis zum Ende kommt, ob die Auswahl gespeichert werden soll und wohin. Diese Abfrage erscheint nur, wenn ein Mensch am Terminal sitzt — Läufe über Pipes oder in CI bleiben still und aktivieren das Speichern stattdessen über das Flag.

**Unterstützte Formate** werden anhand der Dateiendung gewählt:

| Endung | Verfügbarkeit |
|---|---|
| `.json` | Immer (Standardbibliothek) |
| `.toml` | Immer (Standardbibliothek) |
| `.yaml` / `.yml` | Nur wenn PyYAML installiert ist — fastkit fügt es nicht als Laufzeitabhängigkeit hinzu |

Eine geladene Datei muss auf oberster Ebene ein Mapping mit mindestens `project_name`, `author` und `author_email` enthalten. Sie wird anschließend mit denselben Regeln validiert, die auch die interaktiven Abfragen verwenden (Form des Projektnamens, E-Mail-Format, `all_dependencies` muss eine Liste sein), und jedes Problem wird gemeldet, bevor irgendetwas geschrieben wird. Eine Datei, die nur Funktionsauswahlen auflistet — ohne `all_dependencies` —, wird über den interaktiven Builder erweitert, sodass eine handgeschriebene Konfiguration und eine Assistentensitzung zur selben Paketmenge führen.

Ein minimales Beispiel:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv"
}
```

#### Schema der Konfigurationsdatei

Jede Konfigurationsdatei — handgeschrieben oder von `--save-config` erzeugt — durchläuft denselben Normalisierer, bevor sie den Generator erreicht (`normalize_project_config` in `backend/project_builder/config_schema.py`). Ein unbekannter Schlüssel, eine unbekannte Auswahl für eine bekannte Achse oder ein Wert mit falschem Typ wird mit dem betroffenen Namen und der Liste der tatsächlich erlaubten Werte abgelehnt, statt stillschweigend ignoriert zu werden.

| Schlüssel | Form | Hinweise |
|---|---|---|
| `project_name`, `author`, `author_email` | String | Erforderlich |
| `description` | String | Erforderlich |
| `architecture_preset` (Alias `preset`) | `"minimal"` \| `"single-module"` \| `"classic-layered"` \| `"domain-starter"` | Sind beide Schreibweisen vorhanden, müssen sie übereinstimmen |
| `package_manager` | `"pip"` \| `"uv"` \| `"pdm"` \| `"poetry"` | |
| `database` | String oder `{"type": <choice>}` | `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `SQLite`, `None` |
| `authentication`, `async_tasks`, `testing`, `caching`, `monitoring`, `migrations`, `logging` | String oder `{"type": <choice>}` | Achsen mit Einfachauswahl — die Auswahlmöglichkeiten jeder Achse finden Sie oben im [Funktionskatalog](#interactive-builder-feature-catalog-interactive) |
| `utilities`, `tooling` | Liste von Strings | Achsen mit Mehrfachauswahl — Auswahlmöglichkeiten im selben Katalog |
| `deployment` | Liste von Strings | Teilmenge von `Docker`, `docker-compose`; die Wahl von `docker-compose` zieht `Docker` automatisch nach |
| `custom_packages` | Liste von Strings | Zusätzliche Pakete, die unverändert installiert werden |

Jede Achse akzeptiert entweder die reine Auswahl (`"authentication": "JWT"`) oder die Mapping-Form `{"type": ...}`, die `database` und die projekteigenen `[tool.fastapi-fastkit]`-Metadaten verwenden (`"authentication": {"type": "JWT"}`) — beide werden in dieselbe kanonische Form normalisiert, und `--save-config` schreibt immer die kanonische Form als reinen String zurück.

Eine Konfiguration, die die meisten Achsen nutzt:

```json
{
  "project_name": "orders-api",
  "author": "Developer Kim",
  "author_email": "developer@example.com",
  "description": "Domain-oriented orders service",
  "architecture_preset": "domain-starter",
  "package_manager": "uv",
  "database": "PostgreSQL",
  "authentication": "JWT",
  "async_tasks": "Celery",
  "caching": "Redis",
  "migrations": "Alembic",
  "tooling": ["ruff", "makefile"],
  "deployment": ["Docker"]
}
```

Dieselbe Konfiguration als TOML:

```toml
project_name = "orders-api"
author = "Developer Kim"
author_email = "developer@example.com"
description = "Domain-oriented orders service"
architecture_preset = "domain-starter"
package_manager = "uv"
database = "PostgreSQL"
authentication = "JWT"
async_tasks = "Celery"
caching = "Redis"
migrations = "Alembic"
tooling = ["ruff", "makefile"]
deployment = ["Docker"]
```

#### Vorschau und Überspringen von Schritten

`--dry-run` gibt den Baum aus, der erstellt würde, sowie die Pakete, die installiert würden — zusammen mit dem Paketmanager, der sie installieren würde —, und beendet sich dann, ohne die Festplatte zu berühren:

```console
$ fastkit init --config fastkit.config.json --dry-run
```

`--no-install` stoppt, nachdem die virtuelle Umgebung erstellt wurde; `--no-venv` überspringt auch die Umgebung (und damit die Installation). Beides ist nützlich in Containern, in CI und überall dort, wo die Umgebung außerhalb von fastkit verwaltet wird.

#### Bereitstellung im aktuellen Verzeichnis und Bestätigung des Überschreibens (`--yes` / `-y`) { #in-place-deployment-and-overwrite-confirmation-yes-y }

Wenn ein Projekt an Ort und Stelle bereitgestellt wird — in den aktuellen Workspace statt in einen neuen Projektordner —, fragt fastkit „Overwrite these files?“, bevor eine bereits vorhandene Datei ersetzt wird. `--yes` (oder die Kurzform `-y`) überspringt diese Bestätigung und überschreibt direkt. Die separate Abfrage „Do you want to proceed with project creation?“ ist davon nicht betroffen und wird weiterhin angezeigt. In einer nicht-interaktiven Umgebung (stdin ist kein TTY, etwa in CI oder bei einem Lauf über eine Pipe) wird die Bestätigung des Überschreibens auch ohne `--yes` automatisch übersprungen.

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

#### Funktionskatalog des interaktiven Builders (`--interactive`) { #interactive-builder-feature-catalog-interactive }

`fastkit init --interactive` durchläuft statt des obigen Stacks minimal/standard/full einen anderen, achsenbasierten Katalog (maßgebliche Quelle: `FastkitConfig.PACKAGE_CATALOG` in `core/settings.py` und `DynamicConfigGenerator.build_artifacts()` für das, was jede Auswahl erzeugt). Jede Achse hat den Standardwert `None` (überspringen); `utilities` und `tooling` erlauben eine Mehrfachauswahl.

Jede Auswahl erzeugt inzwischen echten Code, nicht nur installierte Pakete — wie sich `minimal` / `single-module` (regenerierte `main.py`) und `classic-layered` / `domain-starter` (erhaltene `main.py`, Warnungen zur manuellen Verdrahtung) unterscheiden, zeigt die [Architektur-Preset- / Funktionsmatrix](../reference/preset-feature-matrix.md).

| Achse | Auswahlmöglichkeiten | Installierte Pakete | Generierte Dateien |
|---|---|---|---|
| `database` | PostgreSQL, MySQL, MongoDB, Redis, SQLite, None | PostgreSQL: `asyncpg`, `sqlalchemy` · MySQL: `aiomysql`, `sqlalchemy` · MongoDB: `motor` · Redis: `redis[hiredis]` · SQLite: `sqlalchemy`, `aiosqlite` | Ein Datenbank-Konfigurationsmodul am Pfad des Presets (z. B. `src/config/database.py`) |
| `authentication` | JWT, OAuth2, FastAPI-Users, Session-based, None | JWT: `pyjwt[crypto]`, `pwdlib[argon2]` · OAuth2: `authlib`, `itsdangerous`, `httpx` · FastAPI-Users: `fastapi-users[sqlalchemy]`, `pyjwt[crypto]`, `pwdlib[argon2]` · Session-based: `itsdangerous` | Ein Auth-Konfigurationsmodul am Pfad des Presets; OAuth2 und Session-based ergänzen zusätzlich das Middleware-Setup in `main.py` |
| `async_tasks` | Celery, Dramatiq, None | Celery: `celery[redis]`, `redis[hiredis]` · Dramatiq: `dramatiq[redis]`, `redis[hiredis]` | `<pkg>/worker.py` (Hintergrund-Worker) + `<pkg>/features/tasks.py` (Task-Routen) |
| `testing` | Basic, Coverage, Advanced, None | Basic: `pytest`, `pytest-asyncio`, `httpx` · Coverage: + `pytest-cov` · Advanced: + `faker`, `factory-boy` | `pytest.ini`; Advanced fügt zusätzlich `tests/factories.py` und `tests/test_factories.py` hinzu |
| `caching` | Redis, None | Redis: `redis[hiredis]`, `fastapi-cache2`, `jinja2` | `<pkg>/features/cache.py` (gecachte Endpunkte) |
| `monitoring` | Loguru, OpenTelemetry, Prometheus, None | Loguru: `loguru` · OpenTelemetry: `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp-proto-http` · Prometheus: `prometheus-client`, `prometheus-fastapi-instrumentator` | Keine eigene Datei — direkt in `main.py` verdrahtet (Import / Lifespan / Setup) |
| `utilities` (Mehrfachauswahl) | CORS, Rate-Limiting, Pagination, WebSocket, None | CORS: keine (in FastAPI integriert) · Rate-Limiting: `slowapi` · Pagination: `fastapi-pagination` · WebSocket: `websockets` | CORS und Rate-Limiting werden direkt in `main.py` verdrahtet; Pagination fügt `<pkg>/features/pagination.py` hinzu, WebSocket fügt `<pkg>/features/websocket.py` hinzu |
| `migrations` | Alembic, None | Alembic: `alembic` | `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, eine Basis-Revision `alembic/versions/<id>_initial.py`, `scripts/migrate.sh` — nur wenn die Datenbankachse eine SQL-Datenbank ist |
| `tooling` (Mehrfachauswahl) | ruff, pre-commit, github-actions, devcontainer, makefile, None | ruff: `ruff` · pre-commit: `pre-commit` · github-actions / devcontainer / makefile: keine | ruff fügt einen `[tool.ruff]`-Block in `pyproject.toml` ein (oder schreibt `ruff.toml` bei `pip`-Projekten); pre-commit schreibt `.pre-commit-config.yaml`; github-actions schreibt `.github/workflows/test.yml`; devcontainer schreibt `.devcontainer/devcontainer.json`; makefile schreibt `Makefile` |
| `logging` | structured, None | Keine (nur stdlib `logging` + `json`) | `<pkg>/logging_config.py` (strukturiertes JSON-Logging + Request-ID-Middleware), in `main.py` verdrahtet |

Unabhängig von der Auswahl erhält jedes generierte Projekt die Endpunkte `/health` und `/ready` in `main.py`, und `--dry-run` gibt genau diese Dateimenge aus, bevor irgendetwas geschrieben wird.

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

#### Wo der Code eingefügt wird

`addroute` braucht zwei Dinge vom Projekt: wohin die neuen Imports kommen und wo der Router registriert wird. Vorlagen und generierte Einstiegspunkte markieren beides mit Anker-Kommentaren:

```python
# src/app/api/router.py
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

Lassen Sie diese Kommentare beim Bearbeiten der Datei an ihrem Platz — `addroute` fügt direkt oberhalb von `# fastkit:imports` und `# fastkit:routes` ein. Ein Projekt, dem sie fehlen (oder das erzeugt wurde, bevor es die Anker gab), funktioniert trotzdem: fastkit greift auf ein AST-basiertes Einfügen zurück, das den Importblock und die Router-Registrierungen selbst findet. Die Anker machen das Ergebnis lediglich vorhersehbar.

`addroute` liest außerdem den `[tool.fastapi-fastkit]`-Block des Projekts, um den Einstiegspunkt zu finden, und funktioniert daher auch bei Layouts, die ein reiner Scan des Dateisystems falsch einordnen würde.

### `startdemo`

Ein FastAPI-Projekt aus einer vorgefertigten Vorlage erstellen.

#### Syntax

```console
$ fastkit startdemo [OPTIONS]
```

#### Optionen

| Option | Beschreibung | Standard |
|--------|-------------|---------|
| `--project-name` | Projektname (wird abgefragt, falls weggelassen) | - |
| `--author` | Name des Autors (wird abgefragt, falls weggelassen) | - |
| `--author-email` | E-Mail des Autors (wird abgefragt, falls weggelassen) | - |
| `--description` | Projektbeschreibung (wird abgefragt, falls weggelassen) | - |
| `--package-manager` | Zu verwendender Paketmanager (pip, uv, pdm, poetry) | uv |
| `--dry-run` | Zeigt die Dateien und Pakete an, die erstellt würden, ohne etwas zu schreiben | aus |
| `--no-venv` | Erstellung der virtuellen Umgebung überspringen (impliziert `--no-install`) | aus |
| `--no-install` | Installation der Abhängigkeiten überspringen | aus |
| `--yes` / `-y` | Beim Bereitstellen des Projekts im aktuellen Verzeichnis nicht nachfragen, bevor vorhandene Dateien überschrieben werden | aus |
| `--help` | Hilfe zum Befehl anzeigen | - |

Wie `init` verweigert auch `startdemo` die Ausführung, wenn das Zielprojektverzeichnis bereits existiert (`Error: Project '{name}' already exists.`). `--dry-run` ist die Ausnahme: Da es nie auf die Festplatte schreibt, darf es auch einen Namen verwenden, für den bereits ein Verzeichnis existiert. Was `--yes` beim Bereitstellen in den aktuellen Workspace bewirkt, erfahren Sie oben unter [Bereitstellung im aktuellen Verzeichnis und Bestätigung des Überschreibens](#in-place-deployment-and-overwrite-confirmation-yes-y).

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
| `fastapi-domain-starter` | Domänenorientierter Starter | Ein Ordner pro Geschäftskonzept, `/health` |
| `fastapi-auth-jwt` | JWT-Authentifizierung | Access-/Refresh-Rotation, argon2id, Rollen und Scopes, Alembic |
| `fastapi-sqlmodel` | Asynchrone SQLModel-Persistenz | SQLModel + asynchrones SQLAlchemy, Alembic, generisches CRUD, Paginierung |
| `fastapi-llm-agent` | Streaming-Claude-Agent | SSE-Streaming, Tool-Call-Schleife, Konversationsspeicher |
| `fastapi-custom-response` | Benutzerdefiniertes Antwortsystem | Benutzerdefinierte Antworten, Paginierung |
| `fastapi-psql-orm` | PostgreSQL-FastAPI-API | PostgreSQL, SQLAlchemy, Alembic |
| `fastapi-mcp` | Model-Context-Protocol-Server | MCP-Integration |
| `fastapi-single-module` | Sandbox in einer Datei | Ein Modul, keine Paketgrenzen |
| `fastapi-empty` | Minimales FastAPI-Projekt | Absolutes Minimum |
| `fastapi-async-crud` | *(veraltet)* Asynchrone Item-Management-API | Abgelöst durch `fastapi-sqlmodel` |
| `fastapi-dockerized` | *(veraltet)* Dockerisierte FastAPI-API | Docker-Tooling ist jetzt in den neueren Vorlagen enthalten |

Die veralteten Vorlagen erzeugen weiterhin funktionierende Projekte; sie werden lediglich nicht mehr als Ausgangspunkt empfohlen. Siehe [Welchen Starter soll ich wählen?](choosing-a-starter.md).

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
- Das Projekt muss eine FastAPI-App bereitstellen — ermittelt aus `[tool.fastapi-fastkit].app_module`, falls vorhanden, andernfalls durch Suche nach `main.py`
- Die virtuelle Umgebung sollte aktiviert sein

Findet weder der gespeicherte Einstiegspunkt noch die Suche ein Modul, meldet `runserver`, dass es `main.py` nicht finden konnte, und bricht ab.

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

## Projektmetadaten (`[tool.fastapi-fastkit]`)

Jedes von fastkit generierte Projekt hält in seiner eigenen `pyproject.toml` fest, wie es erzeugt wurde:

```toml
[tool.fastapi-fastkit]
managed = true
version = "1.4.0"
template = "fastapi-domain-starter"
preset = "domain-starter"
package_manager = "uv"
app_module = "src.app.main:app"
features = ["database:PostgreSQL", "authentication:JWT"]
```

| Schlüssel | Bedeutung |
|---|---|
| `managed` | Immer `true`; kennzeichnet das Projekt als von fastkit verwaltet |
| `version` | Die fastkit-Version, die das Projekt generiert hat |
| `template` | Die `startdemo`-Vorlage oder die Basisvorlage des Presets |
| `preset` | Das Architektur-Preset von `init --interactive` (sonst weggelassen) |
| `package_manager` | Der Paketmanager, mit dem die Umgebung aufgebaut wurde |
| `app_module` | Der uvicorn-Einstiegspunkt im Format `module:attr` |
| `features` | Flache Liste `"<category>:<choice>"` der interaktiven Auswahlen |

Dieser Block ist die einzige maßgebliche Quelle für den Einstiegspunkt des Projekts: `fastkit runserver` liest daraus `app_module`, bevor es auf das Durchsuchen des Baums zurückgreift, `fastkit addroute` nutzt ihn, um die Anwendung zu finden, und generierte Dockerfiles verwenden denselben Wert in ihrem `CMD`.

Der Block wird ganz am Ende der Generierung geschrieben — Paketmanager schreiben `pyproject.toml` beim Auflösen der Abhängigkeiten neu, daher muss er danach eingetragen werden —, und eine spätere Regenerierung ersetzt ihn, statt eine zweite Kopie anzuhängen. `app_module` von Hand zu bearbeiten, ist der unterstützte Weg, fastkit über ein Layout zu informieren, das Sie selbst umorganisiert haben.

## Umgebungsvariablen

FastAPI-fastkit berücksichtigt folgende Umgebungsvariablen:

| Variable | Beschreibung | Standard |
|----------|-------------|---------|
| `FASTKIT_CONFIG_DIR` | Konfigurationsverzeichnis | `~/.fastkit` |
| `FASTKIT_TEMPLATES_DIR` | Verzeichnis für benutzerdefinierte Vorlagen | Integrierte Vorlagen |
| `FASTKIT_LOG_LEVEL` | Log-Level | `INFO` |
| `FASTKIT_SUBPROCESS_TIMEOUT` | Überschreibt jedes Timeout für Paketmanager-Subprozesse, in Sekunden | je Vorgang (30 / 120 / 900) |

Aufrufe von Paketmanagern sind einzeln begrenzt, sodass ein hängender Kindprozess das CLI niemals blockieren kann: 30 Sekunden für eine Verfügbarkeitsprüfung, 120 für das Erstellen einer virtuellen Umgebung, 900 für die Installation der Abhängigkeiten. `FASTKIT_SUBPROCESS_TIMEOUT` ersetzt alle drei durch einen einzigen Wert — nützlich in einem langsamen Netzwerk oder um in CI schnell fehlzuschlagen. Ein Wert, der keine positive ganze Zahl ist, wird ignoriert.

```console
$ export FASTKIT_SUBPROCESS_TIMEOUT=1800
$ fastkit startdemo fastapi-sqlmodel
```

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

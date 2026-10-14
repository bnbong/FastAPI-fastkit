# Architektur-Preset- / Funktionsmatrix

Das interaktive `fastkit init --interactive` fragt nach einem **Architektur-Preset** ([Issue #44](https://github.com/bnbong/FastAPI-fastkit/issues/44)), bevor es die Funktionsauswahl erhebt. Das Preset prägt das Layout des generierten Projekts — jedes Preset bringt eine andere Basisvorlage mit und legt generierte Konfigurationsdateien an unterschiedlichen Orten ab, damit sie neben der vorhandenen Struktur sitzen und nicht in einer parallelen `src/config/`-Hierarchie.

Diese Seite ist die maßgebliche Referenz dafür, was jedes Preset tut, wo Dateien landen und welche Funktionskombinationen manuell eingebunden werden müssen.

## Preset → Basisvorlage

| Preset | Basisvorlage | Beschreibung |
|---|---|---|
| `minimal` | `fastapi-empty` | Die kleinstmögliche lauffähige FastAPI-App — Platzhalter-`main.py` wird aus Ihren Funktionsauswahlen regeneriert. |
| `single-module` | `fastapi-single-module` | FastAPI-App in einer Datei — `main.py` wird regeneriert. |
| `classic-layered` | `fastapi-default` | Geschichtete Aufteilung (`api/routes`, `crud`, `schemas`, `core`). Die mitgelieferte `main.py` bleibt erhalten. |
| `domain-starter` | `fastapi-domain-starter` | Domänenorientiert (`src/app/domains/<concept>/`). Die mitgelieferte `main.py` bleibt erhalten. **Empfohlene Standardlösung.** |

## Speicherorte der generierten Dateien

| Preset | `main.py`-Overlay | Zielpfad für DB-Konfig | Zielpfad für Auth-Konfig |
|---|---|---|---|
| `minimal` | regeneriert unter `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `single-module` | regeneriert unter `src/main.py` | `src/config/database.py` | `src/config/auth.py` |
| `classic-layered` | erhalten (vorlagenseitig) | `src/core/database.py` | `src/core/auth.py` |
| `domain-starter` | erhalten (vorlagenseitig) | `src/app/core/database.py` | `src/app/core/auth.py` |

## Unterstützung der Datenbank- / Auth-Funktionen je Preset

Diese Funktionen werden in **jedem** Preset unterstützt — die Paketinstallation gelingt immer; der Unterschied ist, ob das dynamische `main.py`-Overlay sie auch automatisch verdrahtet.

| Funktion | `minimal` / `single-module` | `classic-layered` / `domain-starter` |
|---|---|---|
| **Datenbank** (PostgreSQL, MySQL, SQLite, MongoDB) | Erzeugt das Konfigurationsmodul **und** legt `await init_db()`-Aufrufe in der regenerierten `main.py` an. | Erzeugt das Konfigurationsmodul am Pfad des Presets. Die mitgelieferte `main.py` bleibt **erhalten**, daher `get_db()` manuell in Router einbinden. |
| **Authentifizierung** (JWT, FastAPI-Users, OAuth2, sessionbasiert) | Erzeugt das Auth-Konfigurationsmodul; JWT importiert `HTTPBearer`, OAuth2 und sessionbasiert ergänzen zusätzlich ihr Middleware-Setup in der `main.py`. | Erzeugt das Auth-Konfigurationsmodul am Pfad des Presets. Keine Imports werden zu `main.py` hinzugefügt — Abhängigkeiten manuell verdrahten. |
| **Hintergrundaufgaben** (Celery, Dramatiq) | Erzeugt `worker.py` und `features/tasks.py` und bindet den Task-Router in der regenerierten `main.py` ein. | Erzeugt `worker.py` und `features/tasks.py`, aber die mitgelieferte `main.py` bleibt **erhalten** — binden Sie den Router manuell ein. |
| **Caching** (Redis) | Erzeugt `features/cache.py` und bindet es in der regenerierten `main.py` ein bzw. initialisiert es dort. | Erzeugt `features/cache.py`; binden Sie es manuell ein. |
| **Utilities: Pagination / WebSocket** | Erzeugt `features/pagination.py` / `features/websocket.py` und bindet den Router in der regenerierten `main.py` ein. | Erzeugt dasselbe Modul; binden Sie es manuell ein. |
| **Monitoring: OpenTelemetry** | Keine eigene Datei — das Tracing-Setup wird direkt in die regenerierte `main.py` eingefügt. | Keine eigene Datei. Die mitgelieferte `main.py` bleibt erhalten, daher ist das Tracing **nicht verdrahtet** — ergänzen Sie das Setup manuell. |
| **Migrationen** (Alembic) | Erzeugt `alembic.ini`, `alembic/env.py`, eine Basis-Revision und `scripts/migrate.sh` für jede SQL-Datenbankauswahl — unabhängig vom `main.py`-Overlay. | Wie nebenan — die Alembic-Generierung hängt nicht davon ab, ob `main.py` erhalten bleibt. |
| **Tooling** (ruff, pre-commit, github-actions, devcontainer, makefile) | Erzeugt die passende(n) Konfigurationsdatei(en), unabhängig vom `main.py`-Overlay. | Wie nebenan. |
| **Logging** (strukturiert) | Erzeugt `logging_config.py` und verdrahtet die Request-ID-Middleware in der regenerierten `main.py`. | Erzeugt `logging_config.py`; die mitgelieferte `main.py` bleibt erhalten, daher die Middleware manuell verdrahten. |
| **CORS** (Utility) | `CORSMiddleware` mit `allow_origins=['*']` wird in die regenerierte `main.py` eingefügt. | **Bereits verdrahtet** in der mitgelieferten `main.py` (bedingt durch `settings.all_cors_origins`). Aktivieren Sie es, indem Sie `BACKEND_CORS_ORIGINS` in `.env` setzen — keine Code-Änderungen nötig. |
| **Testen** (Basic / Coverage / Advanced) | `pytest.ini` wird im Projekt-Root erzeugt; Advanced fügt zusätzlich `tests/factories.py` und `tests/test_factories.py` hinzu. | Wie nebenan. |
| **Deployment** (Docker, docker-compose) | `Dockerfile` und/oder `docker-compose.yml` werden im Projekt-Root abgelegt. | Wie nebenan. |
| **`/health` / `/ready`** | Immer in der regenerierten `main.py` vorhanden. | Bereits in der erhaltenen, vorlagenseitig mitgelieferten `main.py` vorhanden. |

## Wann eine Warnung zur Preset-Kompatibilität erscheint

Bei Presets, die die **mitgelieferte `main.py` erhalten** (`classic-layered`, `domain-starter`), werden manche Funktionsauswahlen nicht automatisch in die App verdrahtet. Das CLI gibt am Ende der Generierung eine einmalige Warnung aus, die auflistet, welche Auswahlen manuelle Verdrahtung benötigen:

| Ausgewählte Funktion | Löst Warnung unter `classic-layered` / `domain-starter` aus? |
|---|---|
| `CORS` (Utility) | ❌ — bereits in der mitgelieferten `main.py` verdrahtet. Setzen Sie nur `BACKEND_CORS_ORIGINS` in `.env`. |
| `Rate-Limiting` (Utility) | ✅ — Setup des `slowapi`-Limiters wird nicht ergänzt |
| `Pagination` / `WebSocket` (Utility) | ✅ — der generierte Router (`features/pagination.py` / `features/websocket.py`) wird nicht eingebunden |
| `Celery` / `Dramatiq` (async_tasks) | ✅ — der generierte `worker.py`- / `features/tasks.py`-Router wird nicht eingebunden |
| `Redis` (Caching) | ✅ — das generierte `features/cache.py` wird weder eingebunden noch initialisiert |
| `Prometheus` / `OpenTelemetry` (Monitoring) | ✅ — das Instrumentierungs-Setup wird nicht zu `main.py` hinzugefügt |
| `structured` (Logging) | ✅ — `logging_config.py` wird erzeugt, aber die Request-ID-Middleware wird nicht zu `main.py` hinzugefügt |
| `Alembic` (Migrationen), `tooling`-Auswahlen | ❌ — diese Dateien werden unabhängig vom Preset erzeugt und sind nutzbar; nichts hängt von `main.py` ab |
| Jegliche Datenbank- / Auth-Auswahl | ⚠️ — Konfigurationsdateien werden erzeugt, aber Sie müssen sie per `Depends()` in Ihre Router einbinden |

Für die Presets `minimal` und `single-module` übernimmt das dynamische `main.py`-Overlay alle oben genannten Achsen automatisch; es werden keine Warnungen ausgelöst.

## Nicht unterstützte Kombinationen (auf Nummer sicher gehen)

Die Strategie versucht **bewusst nicht**, generierten Code in eine vorlagenseitig mitgelieferte `main.py` einzufügen. Das würde riskieren, kaputte Imports oder doppelte Router zu erzeugen. Der Vertrag lautet:

- Ausgewählte Pakete werden immer installiert (damit `pip freeze` der Nutzerabsicht entspricht).
- Generierte Konfigurationsmodule landen immer am preset-passenden Pfad.
- Bei Presets, die `main.py` erhalten, wird dem Nutzer gesagt, welche Auswahlen noch manuelle Verdrahtung brauchen, statt stillschweigend kaputten Code zu liefern.

Wenn Sie die vollautomatische Verdrahtung aller Funktionen benötigen, wählen Sie `minimal` oder `single-module` — diese regenerieren `main.py` aus den Funktions-Flags.

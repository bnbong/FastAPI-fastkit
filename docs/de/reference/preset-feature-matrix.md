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
| **Authentifizierung** (JWT, FastAPI-Users, OAuth2, sessionbasiert) | Erzeugt das Auth-Konfigurationsmodul. JWT importiert zusätzlich `HTTPBearer` in der regenerierten `main.py`. | Erzeugt das Auth-Konfigurationsmodul am Pfad des Presets. Keine Imports werden zu `main.py` hinzugefügt — Abhängigkeiten manuell verdrahten. |
| **Hintergrundaufgaben** (Celery, Dramatiq) | Pakete installiert; aktuell kein main.py-Overlay. | Wie nebenan. |
| **Caching** (Redis) | Pakete installiert; aktuell kein main.py-Overlay. | Wie nebenan. |
| **CORS** (Utility) | `CORSMiddleware` mit `allow_origins=['*']` wird in die regenerierte `main.py` eingefügt. | **Bereits verdrahtet** in der mitgelieferten `main.py` (bedingt durch `settings.all_cors_origins`). Aktivieren Sie es, indem Sie `BACKEND_CORS_ORIGINS` in `.env` setzen — keine Code-Änderungen nötig. |
| **Testen** (Basic / Coverage / Advanced) | `pytest.ini` wird im Projekt-Root erzeugt. | Wie nebenan. |
| **Deployment** (Docker, docker-compose) | `Dockerfile` und/oder `docker-compose.yml` werden im Projekt-Root abgelegt. | Wie nebenan. |

## Wann eine Warnung zur Preset-Kompatibilität erscheint

Bei Presets, die die **mitgelieferte `main.py` erhalten** (`classic-layered`, `domain-starter`), werden manche Funktionsauswahlen nicht automatisch in die App verdrahtet. Das CLI gibt am Ende der Generierung eine einmalige Warnung aus, die auflistet, welche Auswahlen manuelle Verdrahtung benötigen:

| Ausgewählte Funktion | Löst Warnung unter `classic-layered` / `domain-starter` aus? |
|---|---|
| `CORS` (Utility) | ❌ — bereits in der mitgelieferten `main.py` verdrahtet. Setzen Sie nur `BACKEND_CORS_ORIGINS` in `.env`. |
| `Rate-Limiting` (Utility) | ✅ — Setup des `slowapi`-Limiters wird nicht ergänzt |
| `Prometheus` (Monitoring) | ✅ — `Instrumentator().instrument(app)` wird nicht aufgerufen |
| Jegliche Datenbank- / Auth-Auswahl | ⚠️ — Konfigurationsdateien werden erzeugt, aber Sie müssen sie per `Depends()` in Ihre Router einbinden |

Für die Presets `minimal` und `single-module` übernimmt das dynamische `main.py`-Overlay CORS, Rate-Limiting und Prometheus-Instrumentierung automatisch; es werden keine Warnungen ausgelöst.

## Nicht unterstützte Kombinationen (auf Nummer sicher gehen)

Die Strategie versucht **bewusst nicht**, generierten Code in eine vorlagenseitig mitgelieferte `main.py` einzufügen. Das würde riskieren, kaputte Imports oder doppelte Router zu erzeugen. Der Vertrag lautet:

- Ausgewählte Pakete werden immer installiert (damit `pip freeze` der Nutzerabsicht entspricht).
- Generierte Konfigurationsmodule landen immer am preset-passenden Pfad.
- Bei Presets, die `main.py` erhalten, wird dem Nutzer gesagt, welche Auswahlen noch manuelle Verdrahtung brauchen, statt stillschweigend kaputten Code zu liefern.

Wenn Sie die vollautomatische Verdrahtung aller Funktionen benötigen, wählen Sie `minimal` oder `single-module` — diese regenerieren `main.py` aus den Funktions-Flags.

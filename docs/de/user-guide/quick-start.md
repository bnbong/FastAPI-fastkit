# Schnellstart

Erstellen Sie Ihr erstes FastAPI-Projekt mit FastAPI-fastkit in weniger als 5 Minuten!

!!! tip "Unsicher, welchen Starter Sie wählen sollen?"
    Siehe [**Welchen Starter soll ich wählen?**](choosing-a-starter.md) für einen einsteigerfreundlichen Vergleich der `startdemo`-Vorlagen und der interaktiven Architektur-Presets (`minimal` / `single-module` / `classic-layered` / `domain-starter`). Kurz gesagt: **`fastkit init --interactive` mit dem Preset `domain-starter` ist die empfohlene Standardlösung für moderne APIs.**

## 1. Projekt erstellen

Verwenden Sie den Befehl `init` von FastAPI-fastkit, um ein neues Projekt zu erstellen:

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-app
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI application

           Project Information
┌──────────────┬─────────────────────────────┐
│ Project Name │ my-first-app                │
│ Author       │ Your Name                   │
│ Author Email │ your.email@example.com      │
│ Description  │ My first FastAPI application│
└──────────────┴─────────────────────────────┘

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

✨ FastAPI project 'my-first-app' has been created successfully!
```

</div>

## 2. Virtuelle Umgebung aktivieren

Wechseln Sie in Ihr Projekt und aktivieren Sie die virtuelle Umgebung:

<div class="termy">

```console
$ cd my-first-app
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

## 3. Entwicklungsserver starten

Starten Sie den FastAPI-Entwicklungsserver:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

!!! success "Glückwunsch!"
    Ihr FastAPI-Server läuft jetzt! Öffnen Sie Ihren Browser, um ihn zu erkunden.

## 4. Ihre API testen

Öffnen Sie Ihren Browser und rufen Sie diese URLs auf:

### Hauptendpunkt

Besuchen Sie [http://127.0.0.1:8000](http://127.0.0.1:8000)

Sie sehen:

```json
{"message": "Hello World"}
```

### Interaktive API-Dokumentation

Besuchen Sie [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Dies ist die automatisch generierte **Swagger-UI**-Dokumentation, mit der Sie können:

- alle Ihre API-Endpunkte sehen
- Endpunkte direkt im Browser testen
- Anfrage- und Antwortschemas einsehen

### Alternative Dokumentation

Besuchen Sie [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Dies ist die **ReDoc**-Dokumentationsoberfläche mit einem anderen, schlichten Design.

## 5. Ihre erste Route hinzufügen

Lassen Sie uns eine neue API-Route zu Ihrem Projekt hinzufügen:

<div class="termy">

```console
$ fastkit addroute users my-first-app
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-app                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-app                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-app'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-first-app`                                        │
╰───────────────────────────────────────────────────────╯
```

</div>

Der Server lädt automatisch neu, und Sie haben nun neue Endpunkte:

- `GET /api/v1/users/` — alle Nutzer abrufen
- `POST /api/v1/users/` — einen neuen Nutzer anlegen
- `GET /api/v1/users/{user_id}` — einen bestimmten Nutzer abrufen
- `PUT /api/v1/users/{user_id}` — einen Nutzer aktualisieren
- `DELETE /api/v1/users/{user_id}` — einen Nutzer löschen

## 6. Die neue API testen

### Mit curl

**Alle Nutzer abrufen:**

<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/
[]
```

</div>

**Einen neuen Nutzer anlegen:**

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
```

</div>

### Über die interaktive Dokumentation

1. Besuchen Sie [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Klappen Sie den Abschnitt **„users"** auf
3. Klicken Sie auf **„POST /api/v1/users/"**
4. Klicken Sie auf **„Try it out"**
5. Füllen Sie den Request-Body aus:
   ```json
   {
     "title": "Jane Smith",
     "description": "Product Manager"
   }
   ```
6. Klicken Sie auf **„Execute"**

## 7. Ihre Projektstruktur erkunden

Ihr generiertes Projekt hat eine klare, organisierte Struktur:

```
my-first-app/
├── .venv/                    # Virtuelle Umgebung
├── src/
│   ├── __init__.py
│   ├── main.py              # Einstiegspunkt der FastAPI-App
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # App-Konfiguration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # Sammlung der API-Router
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── items.py     # Standardroute für Items
│   │       └── users.py     # Ihre neue Users-Route
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── items.py         # CRUD-Operationen für Items
│   │   └── users.py         # CRUD-Operationen für Users
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── items.py         # Pydantic-Schemas für Items
│   │   └── users.py         # Pydantic-Schemas für Users
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Testdaten
├── tests/                   # Testdateien
├── scripts/                 # Hilfsskripte
├── requirements.txt         # Python-Abhängigkeiten
├── setup.py                # Paketkonfiguration
└── README.md               # Projektdokumentation
```

## 8. Paketmanager-Optionen

FastAPI-fastkit unterstützt mehrere Python-Paketmanager, passend zu Ihren Vorlieben:

### Verfügbare Paketmanager

| Manager | Beschreibung | Am besten für |
|---------|-------------|----------|
| **UV** | Schneller Python-Paketmanager (Standard) | Geschwindigkeit und Leistung |
| **PDM** | Moderne Python-Abhängigkeitsverwaltung | Fortgeschrittene Abhängigkeitsauflösung |
| **Poetry** | Python-Abhängigkeitsverwaltung und Packaging | Poetry-basierte Workflows |
| **PIP** | Standard-Python-Paketmanager | Klassische Python-Entwicklung |

### Paketmanager angeben

Sie können Ihren bevorzugten Paketmanager auf mehrere Arten angeben:

#### 1. Interaktive Auswahl (Standard)

Wenn Sie `fastkit init` oder `fastkit startdemo` ausführen, werden Sie zur Auswahl aufgefordert:

<div class="termy">

```console
$ fastkit init
# ... after project details and stack selection ...

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

#### 2. Kommandozeilenoption

Überspringen Sie die interaktive Eingabeaufforderung, indem Sie den Paketmanager direkt angeben:

<div class="termy">

```console
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

</div>

### Generierte Abhängigkeitsdateien

Jeder Paketmanager erzeugt die jeweils passenden Abhängigkeitsdateien:

- **UV/PDM**: `pyproject.toml` (PEP-621-Format)
- **Poetry**: `pyproject.toml` (Poetry-Format)
- **PIP**: `requirements.txt`

## 9. Wie geht es weiter?

Glückwunsch! Sie haben erfolgreich:

✅ Ihr erstes FastAPI-Projekt erstellt
✅ den Entwicklungsserver gestartet
✅ eine neue API-Route hinzugefügt
✅ Ihre APIs getestet

### Weiter lernen

1. **[Ihr erstes Projekt](../tutorial/first-project.md)**: bauen Sie eine umfassendere Blog-API
2. **[Projekte erstellen](creating-projects.md)**: lernen Sie verschiedene Stacks und Optionen kennen
3. **[Routen hinzufügen](adding-routes.md)**: meistern Sie die API-Entwicklung
4. **[Vorlagen verwenden](using-templates.md)**: erkunden Sie vorgefertigte Projektvorlagen

### Mehr experimentieren

Probieren Sie diese Befehle aus, um weitere Funktionen zu erkunden:

<div class="termy">

```console
# List available templates
$ fastkit list-templates

# Create a project from a template
$ fastkit startdemo

# Add more routes (route name first, project dir second)
$ fastkit addroute products my-first-app
$ fastkit addroute orders my-first-app
```

</div>

!!! tip "Entwicklungstipps"
    - Der Server lädt automatisch neu, wenn Sie Dateien ändern
    - Prüfen Sie immer die interaktive Doku unter `/docs`, wenn Sie neue Funktionen hinzufügen
    - Verwenden Sie die virtuelle Umgebung, um Abhängigkeiten zu isolieren
    - Erkunden Sie den generierten Code, um die Projektstruktur zu verstehen

# Entwicklungsumgebung einrichten

Ein umfassender Leitfaden zum Einrichten einer Entwicklungsumgebung für Beiträge zu FastAPI-fastkit.

## Voraussetzungen

Bevor Sie starten, stellen Sie sicher, dass Sie haben:

- **Python 3.12 oder höher** installiert
- **Git** installiert und konfiguriert
- **Grundkenntnisse** in Python und FastAPI
- **Einen Texteditor oder eine IDE** (VS Code, PyCharm usw.)

## Schnelles Setup mit Makefile

FastAPI-fastkit bietet ein Makefile für einfaches Entwicklungs-Setup:

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make install-dev
Setting up development environment...
Creating virtual environment...
Installing dependencies...
Installing pre-commit hooks...
✅ Development environment ready!
```

</div>

Dieser einzelne Befehl:

- Installiert das Paket im Editable-Modus mit Dev-Abhängigkeiten
- Richtet Pre-Commit-Hooks ein
- Konfiguriert Entwicklungstools

!!! note

    Sie sollten eine virtuelle Umgebung erstellen und aktivieren, bevor Sie diesen Befehl ausführen.

## Manuelles Setup

Wenn Sie ein manuelles Setup bevorzugen oder das Makefile auf Ihrem System nicht funktioniert:

### 1. Repository klonen

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
```

</div>

### 2. Virtuelle Umgebung erstellen

<div class="termy">

```console
$ python -m venv .venv
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

</div>

### 3. Abhängigkeiten installieren

<div class="termy">

```console
# Install package in editable mode with development dependencies
$ pip install -e ".[dev]"

# Or install from requirements files
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

</div>

### 4. Pre-Commit-Hooks einrichten

<div class="termy">

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

</div>

### 5. Installation überprüfen

<div class="termy">

```console
$ fastkit --version
fastapi-fastkit, version 1.2.1

$ python -m pytest tests/
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
tests/test_templates.py::test_template_listing PASSED
...
======================== 45 passed in 2.34s ========================
```

</div>

## Entwicklungstools

Die Entwicklungsumgebung enthält mehrere Tools zur Code-Qualität:

### Einzeilen-Befehle

mit Makefile:

```console
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!
```

mit den mitgelieferten Skripten:

```console
$ ./scripts/format.sh
$ ./scripts/lint.sh
```

### Code-Formatierung

**Black** — Code-Formatter:

<div class="termy">

```console
$ black src/ tests/
reformatted src/main.py
reformatted tests/test_cli.py
All done! ✨ 🍰 ✨
```

</div>

**isort** — Import-Sortierer:

<div class="termy">

```console
$ isort src/ tests/
Fixing import order in src/main.py
```

</div>

### Code-Linting

**mypy** — Typprüfung:

<div class="termy">

```console
$ mypy src/
Success: no issues found in 12 source files
```

</div>

## Verfügbare Make-Befehle

Das Projekt-Makefile bietet praktische Befehle für gängige Entwicklungsaufgaben:

### Setup-Befehle

| Befehl | Beschreibung |
|---------|-------------|
| `make install` | Paket im Produktionsmodus installieren |
| `make install-dev` | Paket mit Dev-Abhängigkeiten installieren |
| `make install-test` | Paket für Tests installieren (deinstallieren + neu installieren) |
| `make uninstall` | Paket deinstallieren |
| `make clean` | Build-Artefakte und Cache-Dateien löschen |

### Befehle zur Code-Qualität

| Befehl | Beschreibung |
|---------|-------------|
| `make format` | Code mit black und isort formatieren |
| `make format-check` | Formatierung prüfen, ohne Änderungen vorzunehmen |
| `make lint` | Alle Linting-Prüfungen ausführen (isort, black, mypy) |

### Test-Befehle

| Befehl | Beschreibung |
|---------|-------------|
| `make test` | Alle Tests ausführen |
| `make test-verbose` | Tests mit ausführlicher Ausgabe ausführen |
| `make test-coverage` | Tests mit Coverage-Bericht ausführen |
| `make coverage-report` | Detaillierten Coverage-Bericht erzeugen (FORMAT=html/xml/json/all) |

### Befehle zur Vorlagen-Inspektion

| Befehl | Beschreibung |
|---------|-------------|
| `make inspect-templates` | Alle Vorlagen inspizieren |
| `make inspect-templates-verbose` | Mit ausführlicher Ausgabe inspizieren |
| `make inspect-template` | Eine oder mehrere Vorlagen inspizieren (Parameter TEMPLATES) |

Das zugrunde liegende Skript kennt drei Flags, die beim Iterieren nützlich sind: `--offline` (überspringt die PyPI-Aktualitätsabfragen), `--no-smoke` (überspringt das Starten des generierten Projekts mit uvicorn — der langsamste Schritt) und `--mypy` (Typprüfung des generierten Projekts; optional, weil sie langsam ist). Was jede Prüfung genau tut, beschreibt [Qualitätssicherung der Vorlagen](../reference/template-quality-assurance.md).

```console
$ python scripts/inspect-templates.py --templates fastapi-sqlmodel --offline --no-smoke
```

### Generierter Code liegt in Jinja2-Fragmenten

Alles, was `fastkit init --interactive` in ein Projekt schreibt — `main.py`, Datenbank- und Auth-Module, Docker-Dateien, die pytest-Konfiguration — wird aus Vorlagen unter `src/fastapi_fastkit/fragments/` gerendert und nicht in Python aus Strings zusammengesetzt. `main.py.j2` codiert keine Funktion fest: Es iteriert über die Listen `import_fragments`, `lifespan_fragments` und `setup_fragments`, die `DynamicConfigGenerator` liefert, und bindet jedes Fragment ein, sodass sich Funktionen frei kombinieren lassen.

Eine Funktion hinzuzufügen, sieht ungefähr so aus:

1. Legen Sie die Bausteine in `main/imports/`, `main/lifespan/` und/oder `main/setup/` ab (Lifespan-Fragmente sind um vier Leerzeichen eingerückt, die anderen beiden nicht).
2. Registrieren Sie sie in `DynamicConfigGenerator._main_fragments()`, abgesichert durch die passende Konfigurationsabfrage.
3. Für ein eigenständiges Modul fügen Sie `<area>/<feature>.py.j2` hinzu und rendern es mit `self._render(...)`.
4. Erweitern Sie die Kombinationsmatrix in `tests/test_backends/test_project_builder_config_generator.py` — sie prüft, dass sich jede gerenderte Python-Datei mit `ast.parse` parsen lässt.

Zwei Einschränkungen, über die man leicht stolpert: Jedes Fragment muss mit einem abschließenden Zeilenumbruch enden (die Umgebung wird mit `keep_trailing_newline=True` erstellt), und `main.py.j2` muss seine Anker `# fastkit:imports` / `# fastkit:routes` behalten — `fastkit addroute` fügt an ihnen ein.

Das maßgebliche Vorgehen ist direkt neben den Fragmenten dokumentiert, in [`src/fastapi_fastkit/fragments/README.md`](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fragments/README.md).

### Dokumentations-Befehle

| Befehl | Beschreibung |
|---------|-------------|
| `make serve-docs` | Dokumentation lokal bereitstellen |
| `make build-docs` | Dokumentation bauen |

### Übersetzungs-Befehle

| Befehl | Beschreibung |
|---------|-----------|
| `make translate` | Dokumentation übersetzen (Parameter LANG, PROVIDER, MODEL) |

### Beispiele

<div class="termy">

```console
# Format code and run all checks
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!

# Run tests with coverage
$ make test-coverage
======================== test session starts ========================
collected 45 items
tests/test_cli.py::test_init_command PASSED
...
======================== 45 passed in 2.34s ========================

---------- coverage: platform darwin, python 3.12.1-final-0 ----------
Name                     Stmts   Miss  Cover
--------------------------------------------
src/main.py                 45      2    96%
src/cli.py                  89      5    94%
src/templates.py            67      3    96%
--------------------------------------------
TOTAL                      201     10    95%

# Generate HTML coverage report
$ make coverage-report FORMAT=html
🌐 Opening HTML coverage report in browser...

# Translate documentation to Korean
$ make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
Starting translation...
Running: python scripts/translate.py --target-lang ko --api-provider github --model gpt-4o-mini
```

</div>

## Projektstruktur

Die Projektstruktur zu verstehen, ist für die Entwicklung entscheidend:

```bash
FastAPI-fastkit/
├── src/
│   ├── fastapi_fastkit/
│   │   ├── __main__.py                      # Entry point of the application
│   │   ├── backend/
│   │   │   ├── inspector.py                 # FastAPI-fastkit template inspector
│   │   │   ├── interactive/
│   │   │   │   ├── config_builder.py        # Configuration builder for interactive mode
│   │   │   │   ├── prompts.py               # Prompts for interactive mode
│   │   │   │   ├── selectors.py             # Selectors logic for interactive mode
│   │   │   │   └── validators.py            # User input validators for interactive mode
│   │   │   ├── main.py                      # Backend's logic entry point
│   │   │   ├── package_managers/
│   │   │   │   ├── base.py                  # Base class for package managers
│   │   │   │   ├── factory.py               # Factory for package managers
│   │   │   │   ├── pdm_manager.py           # PDM package manager
│   │   │   │   ├── pip_manager.py           # pip package manager
│   │   │   │   ├── poetry_manager.py        # Poetry package manager
│   │   │   │   └── uv_manager.py            # uv package manager
│   │   │   ├── project_builder/
│   │   │   │   ├── config_generator.py      # Configuration generator for project builder
│   │   │   │   └── dependency_collector.py  # Dependency collector for project builder
│   │   │   └── transducer.py                # Transducer for project builder
│   │   ├── cli.py                           # FastAPI-fastkit main CLI entry point
│   │   ├── core/
│   │   │   ├── exceptions.py                # Exception handling
│   │   │   └── settings.py                  # Settings configuration
│   │   ├── fastapi_project_template/
│   │   │   ├── PROJECT_README_TEMPLATE.md   # fastkit template project base README file
│   │   │   ├── README.md                    # fastkit template README
│   │   │   ├── fastapi-async-crud/
│   │   │   ├── fastapi-custom-response/
│   │   │   ├── fastapi-default/
│   │   │   ├── fastapi-dockerized/
│   │   │   ├── fastapi-empty/
│   │   │   ├── fastapi-mcp/
│   │   │   ├── fastapi-psql-orm/
│   │   │   ├── fastapi-single-module/
│   │   │   └── modules/
│   │   │       ├── api/
│   │   │       │   └── routes/
│   │   │       ├── crud/
│   │   │       └── schemas/
│   │   ├── py.typed
│   │   └── utils/
│   │       ├── logging.py                   # Logging configuration
│   │       └── main.py                      # FastAPI-fastkit main entry point
│   └── logs
├── tests
│   ├── conftest.py                          # pytest configuration
│   ├── test_backends/
│   ├── test_cli_operations/
│   ├── test_core.py
│   ├── test_rich/
│   ├── test_templates/
│   └── test_utils.py
├── uv.lock
├── docs/                                    # Documentation
├── scripts/                                 # Development scripts
├── mkdocs.yml
├── overrides/                               # mkdocs overrides
├── pdm.lock
├── pyproject.toml
├── requirements-docs.txt                    # requirements for documentation
├── requirements.txt                         # requirements for development
├── CHANGELOG.md
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── SECURITY.md
└── env.example                              # environment example(configures translation AI model env vars)
```

### Wichtige Verzeichnisse

- **`src/fastapi_fastkit/`** — Hauptquellcode des Pakets
    - **`cli.py`** — Haupteinstiegspunkt des CLI
    - **`backend/`** — zentrale Backend-Logik
        - **`inspection/`** — Pipeline zur Vorlagen-Inspektion (context, checks, consistency, freshness, smoke, lint, report)
        - **`inspector.py`** — Fassade über `inspection/`, beibehalten für den historischen Importpfad
        - **`interactive/`** — Komponenten des interaktiven Modus (Prompts, Selectors, Validators)
        - **`package_managers/`** — Implementierungen der Paketmanager (pip, uv, pdm, poetry)
        - **`project_builder/`** — Hilfsfunktionen zum Projektbau, einschließlich des fragmentbasierten Konfigurationsgenerators
        - **`scaffolder.py`** — die Generierungspipeline, die `init` und `startdemo` gemeinsam nutzen
        - **`transducer.py`** — Vorlagen-Transducer
    - **`core/`** — zentrale Konfiguration und Exceptions
    - **`fragments/`** — Jinja2-Fragmente, die in generierte Projekte gerendert werden (siehe oben)
    - **`fastapi_project_template/`** — Projektvorlagen (fastapi-default, fastapi-domain-starter usw.)
    - **`utils/`** — gemeinsame Hilfsfunktionen
- **`tests/`** — Test-Suite
    - **`test_backends/`** — Backend-spezifische Tests
    - **`test_cli_operations/`** — Tests der CLI-Operationen
    - **`test_templates/`** — Tests des Vorlagensystems
- **`docs/`** — Dokumentation (MkDocs)
    - Nutzerhandbücher, Tutorials und API-Referenz

## Entwicklungs-Workflow

### 1. Feature-Branch erstellen

<div class="termy">

```console
$ git checkout -b feature/add-new-template
Switched to a new branch 'feature/add-new-template'
```

</div>

### 2. Änderungen vornehmen

Code bearbeiten, Funktionen ergänzen, Bugs beheben…

### 3. Tests und Prüfungen ausführen

<div class="termy">

```console
$ make dev-check
Running all quality checks...
Running all tests...
✅ All tests passed!
```

</div>

### 4. Änderungen committen

Pre-Commit-Hooks laufen automatisch:

<div class="termy">

```console
$ git add .
$ git commit -m "Add new FastAPI template with authentication"
format...................................................................Passed
isort-check..............................................................Passed
black-fix................................................................Passed
mypy.....................................................................Passed
[feature/add-new-template abc1234] Add new FastAPI template with authentication
```

</div>

### 5. Pushen und Pull-Request erstellen

<div class="termy">

```console
$ git push origin feature/add-new-template
$ gh pr create --title "Add new FastAPI template with authentication"
```

</div>

## Testen

### Tests ausführen

**Alle Tests:**

<div class="termy">

```console
$ make test
# or
$ python -m pytest
```

</div>

**Bestimmte Testdatei:**

<div class="termy">

```console
$ python -m pytest tests/test_cli.py -v
```

</div>

**Mit Coverage:**

<div class="termy">

```console
$ make test-coverage
# or
$ python -m pytest --cov=src --cov-report=html
```

</div>

### Tests schreiben

Bei neuen Funktionen immer Tests beifügen:

```python
# tests/test_commands/test_new_feature.py
import pytest
from fastapi_fastkit.commands.new_feature import NewFeatureCommand

class TestNewFeatureCommand:
    def test_command_success(self):
        """Test successful command execution"""
        command = NewFeatureCommand()
        result = command.execute(valid_args)
        assert result.success is True
        assert result.message == "Feature executed successfully"

    def test_command_validation_error(self):
        """Test command with invalid arguments"""
        command = NewFeatureCommand()
        with pytest.raises(ValueError, match="Invalid argument"):
            command.execute(invalid_args)

    def test_command_edge_case(self):
        """Test edge case handling"""
        command = NewFeatureCommand()
        result = command.execute(edge_case_args)
        assert result.success is True
        assert "warning" in result.message.lower()
```

### Test-Kategorien

**Unit-Tests** — einzelne Funktionen und Klassen testen:

```python
def test_validate_project_name():
    assert validate_project_name("valid-name") is True
    assert validate_project_name("invalid name!") is False
```

**Integrationstests** — Interaktionen zwischen Befehlen testen:

```python
def test_init_command_creates_project(tmp_path):
    result = runner.invoke(cli, ['init'], input='test-project\n...')
    assert result.exit_code == 0
    assert (tmp_path / "test-project").exists()
```

**End-to-End-Tests** — komplette Flüsse testen:

```python
def test_full_project_creation_workflow(tmp_path):
    # Create project
    result = runner.invoke(cli, ['init'], input='...')
    assert result.exit_code == 0

    # Add route
    result = runner.invoke(cli, ['addroute', 'test-project', 'users'])
    assert result.exit_code == 0

    # Verify files exist
    assert (tmp_path / "test-project" / "src" / "api" / "routes" / "users.py").exists()
```

## Dokumentation

### Dokumentation lokal bereitstellen

<div class="termy">

```console
$ make serve-docs
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.43 seconds
INFO     -  [14:30:00] Serving on http://127.0.0.1:8000/
```

</div>

### Dokumentation bauen

<div class="termy">

```console
$ make build-docs
INFO     -  Building documentation...
INFO     -  Documentation built in 0.43 seconds
```

</div>

### Dokumentation schreiben

Die Dokumentation wird in Markdown verfasst und mit MkDocs gebaut. Beispielstruktur:

**Vorlage für einen Funktions-Leitfaden:**

````markdown
# New Feature Guide

This guide explains how to use the new feature.

## Prerequisites

- FastAPI-fastkit installed
- Basic Python knowledge

## Usage

<div class="termy">

```console
$ fastkit new-feature --option value
✅ Feature executed successfully!
```

</div>

!!! tip "Pro Tip"
    Use `--help` to see all available options.
````

Für eine ausführliche Referenz zu `mkdocs-material` siehe [mkdocs-material-Dokumentation](https://squidfunk.github.io/mkdocs-material/reference/admonitions/).

## Code-Stil-Richtlinien

### Python-Codestil

Folgen Sie [PEP 8](https://www.python.org/dev/peps/pep-0008/) mit folgenden Regeln:

- **Zeilenlänge**: 88 Zeichen (Black-Standard)
- **Imports**: mit isort organisiert
- **Type Hints**: für alle öffentlichen Funktionen erforderlich
- **Docstrings**: Google-Style für alle öffentlichen APIs

### Beispiel

```python
from typing import List, Optional
from pathlib import Path

def create_project_structure(
    project_name: str,
    template_path: Path,
    output_dir: Optional[Path] = None,
) -> List[Path]:
    """Create project structure from template.

    Args:
        project_name: Name of the project to create
        template_path: Path to the template directory
        output_dir: Output directory, defaults to current directory

    Returns:
        List of created file paths

    Raises:
        ValueError: If project_name is invalid
        FileNotFoundError: If template_path doesn't exist
    """
    if not project_name.isidentifier():
        raise ValueError(f"Invalid project name: {project_name}")

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    # Implementation here...
    return created_files
```

## Umgebungsvariablen

Für die Entwicklung können Sie folgende Umgebungsvariablen setzen:

| Variable | Beschreibung | Standard |
|----------|-------------|---------|
| `FASTKIT_DEBUG` | Debug-Logging aktivieren | `False` |
| `FASTKIT_DEV_MODE` | Entwicklungs-Funktionen aktivieren | `False` |
| `FASTKIT_TEMPLATE_DIR` | Verzeichnis für eigene Vorlagen | Eingebaute Vorlagen |
| `FASTKIT_CONFIG_DIR` | Konfigurationsverzeichnis | `~/.fastkit` |
| `TRANSLATION_API_KEY` | API-Schlüssel für Übersetzungen (verwenden Sie ein GitHub-PAT, wenn Sie den [GitHub-KI-Modell-Anbieter](https://github.com/marketplace/models/azure-openai) nutzen) | `None` |

<div class="termy">

```console
$ export FASTKIT_DEBUG=true
$ export FASTKIT_DEV_MODE=true
$ fastkit init
DEBUG: Loading configuration from /home/user/.fastkit/
DEBUG: Available templates: ['fastapi-default', ...]
```

</div>

Für weitere Einstellungen zu Umgebungsvariablen siehe das Modul [@settings.py](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/core/settings.py).

## Fehlerbehebung

### Häufige Probleme

**1. Pre-Commit-Hooks schlagen fehl:**

<div class="termy">

```console
$ git commit -m "Fix bug"
black....................................................................Failed
hookid: black

Files were modified by this hook. Additional output:

would reformat src/cli.py
```

</div>

**Lösung:** Formatter ausführen und erneut committen:

<div class="termy">

```console
$ make format
$ git add .
$ git commit -m "Fix bug"
```

</div>

**2. Tests schlagen bei unterschiedlichen Python-Versionen fehl:**

**Lösung:** tox verwenden, um mehrere Python-Versionen zu testen:

<div class="termy">

```console
$ pip install tox
$ tox
py38: commands succeeded
py39: commands succeeded
py310: commands succeeded
py311: commands succeeded
py312: commands succeeded
```

</div>

**3. Import-Fehler in der Entwicklung:**

**Lösung:** Paket im Editable-Modus installieren:
<div class="termy">

```console
$ pip install -e .
```

</div>

### Hilfe bekommen

- **[GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)**: Bugs und Feature-Requests melden
- **[GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)**: Fragen stellen und Ideen teilen
- **Dokumentation**: siehe [Benutzerhandbuch](../user-guide/installation.md)

## Beitrags-Richtlinien

### Vor dem Einreichen einer PR

1. **Alle Prüfungen ausführen:** `make dev-check`
2. **Dokumentation aktualisieren**, falls nötig
3. **Tests** für neue Funktionen hinzufügen
4. **Commit-Konventionen** befolgen

### Format der Commit-Nachricht

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**Typen:**

- `feat`: neue Funktion
- `fix`: Bugfix
- `docs`: Dokumentationsänderungen
- `style`: Code-Stil-Änderungen
- `refactor`: Refactoring
- `test`: Tests hinzufügen/ändern
- `chore`: Wartungsaufgaben

**Beispiele:**

```
feat(cli): add new template command

Add support for creating projects from custom templates.
The command accepts a template path and creates a new
project with the specified configuration.

Fixes #45

fix(templates): handle missing template files gracefully

When a template file is missing, show a clear error message
instead of crashing with a stack trace.

Fixes #67
```

## Release-Prozess

Für Maintainer sieht der Release-Prozess so aus:

1. **Version aktualisieren** in `setup.py` und `__init__.py`
2. **CHANGELOG.md aktualisieren**
3. **Release-PR erstellen**
4. **Release nach dem Merge taggen**
5. **GitHub Actions** baut und veröffentlicht automatisch

<div class="termy">

```console
$ git tag v1.2.0
$ git push origin v1.2.0
```

</div>

## Nächste Schritte

Nachdem Ihre Entwicklungsumgebung eingerichtet ist:

1. **[Code erkunden](https://github.com/bnbong/FastAPI-fastkit/tree/main/src/fastapi_fastkit)**, um die Architektur zu verstehen
2. **Test-Suite ausführen**, um sicherzustellen, dass alles funktioniert
3. **Ein [Issue](https://github.com/bnbong/FastAPI-fastkit/issues)** auf GitHub auswählen
4. **Sich an [Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)** beteiligen, um sich mit anderen Mitwirkenden zu vernetzen

Viel Spaß beim Programmieren! 🚀

!!! tip "Entwicklungs-Tipps"
    - Vor dem Committen `make dev-check` ausführen
    - Tests zuerst schreiben (TDD-Ansatz)
    - Commits klein und fokussiert halten
    - Dokumentation mit neuen Funktionen aktualisieren

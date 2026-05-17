# Installation

Diese Anleitung erklärt, wie FastAPI-fastkit installiert wird.

## Voraussetzungen

Um FastAPI-fastkit zu verwenden, müssen die folgenden Voraussetzungen erfüllt sein:

- **Python**: 3.12 oder höher
- **Betriebssystem**: Windows, macOS, Linux unterstützt

## Installationsmethoden

### Installation mit pip (empfohlen)

Die einfachste Installationsmethode:

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

### Eine bestimmte Version installieren

Um eine bestimmte Version zu installieren:

<div class="termy">

```console
$ pip install FastAPI-fastkit==1.0.0
---> 100%
Successfully installed FastAPI-fastkit-1.0.0
```

</div>

### Entwicklungsversion installieren

Um die neueste Entwicklungsversion direkt von GitHub zu installieren:

<div class="termy">

```console
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git
---> 100%
Successfully installed FastAPI-fastkit
```

</div>

!!! warning "Hinweis zur Entwicklungsversion"
    Entwicklungsversionen können instabil sein und werden für Produktionsumgebungen nicht empfohlen.

## Einrichtung einer virtuellen Umgebung (empfohlen)

Es wird dringend empfohlen, eine virtuelle Umgebung zu verwenden, um Abhängigkeitskonflikte zu vermeiden:

### Mit venv

<div class="termy">

```console
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # Linux/macOS
$ fastapi-env\Scripts\activate     # Windows
$ pip install FastAPI-fastkit
```

</div>

### Mit conda

<div class="termy">

```console
$ conda create -n fastapi-env python=3.12
$ conda activate fastapi-env
$ pip install FastAPI-fastkit
```

</div>

## Installation überprüfen

Überprüfen Sie nach der Installation, dass FastAPI-fastkit korrekt installiert ist:

<div class="termy">

```console
$ fastkit --version
FastAPI-fastkit version 1.0.0
```

</div>

<div class="termy">

```console
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

## Fehlerbehebung

### Befehl nicht gefunden

Wenn Sie den Fehler „command not found" erhalten:

1. **Prüfen Sie, ob FastAPI-fastkit installiert ist**:

   <div class="termy">
   ```console
   $ pip show FastAPI-fastkit
   ```
   </div>

2. **Prüfen Sie Ihre virtuelle Umgebung**:

   <div class="termy">
   ```console
   $ which python
   $ which pip
   ```
   </div>

3. **Installieren Sie FastAPI-fastkit erneut**:

   <div class="termy">
   ```console
   $ pip uninstall FastAPI-fastkit
   $ pip install FastAPI-fastkit
   ```
   </div>

### Berechtigungsfehler

Wenn Sie bei der Installation auf Berechtigungsfehler stoßen:

**Unter Linux/macOS:**

<div class="termy">

```console
$ pip install --user FastAPI-fastkit
```

</div>

**Unter Windows (als Administrator ausführen):**

<div class="termy">

```console
$ pip install FastAPI-fastkit
```

</div>

### Python-Versionskompatibilität

FastAPI-fastkit erfordert Python 3.12+. Überprüfen Sie Ihre Python-Version:

<div class="termy">

```console
$ python --version
Python 3.12.0
```

</div>

Falls Sie eine ältere Version haben, aktualisieren Sie Python:

- **Offizielles Python**: [python.org/downloads](https://www.python.org/downloads/)
- **Mit pyenv**: `pyenv install 3.12.0`
- **Mit conda**: `conda install python=3.12`

## Nächste Schritte

Sobald die Installation abgeschlossen ist:

1. **[Schnellstart](quick-start.md)**: erstellen Sie Ihr erstes Projekt in 5 Minuten
2. **[Tutorial – Erste Schritte](../tutorial/getting-started.md)**: detailliertes Schritt-für-Schritt-Tutorial
3. **[CLI-Referenz](cli-reference.md)**: vollständige Befehlsreferenz

!!! tip "Installationstipps"
    - Verwenden Sie immer virtuelle Umgebungen, um Projekte zu isolieren
    - Halten Sie FastAPI-fastkit auf der neuesten Version
    - Im [GitHub-Repository](https://github.com/bnbong/FastAPI-fastkit) finden Sie Updates und Issues

# Qualitätssicherung der Vorlagen

FastAPI-fastkit bietet eine umfassende automatisierte Validierung aller Vorlagen, um sicherzustellen, dass sie hohe Qualität halten und in verschiedenen Umgebungen und mit unterschiedlichen Paketmanagern funktionsfähig bleiben.

## Mehrstufige Qualitätssicherung

FastAPI-fastkit setzt **zwei sich ergänzende Qualitätssicherungssysteme** ein:

### 1. Statische Vorlagen-Inspektion
**Wöchentliche automatisierte Validierung von Vorlagenstruktur und -syntax**

### 2. Dynamische Vorlagen-Tests
**Umfassende End-to-End-Tests durch tatsächliches Anlegen von Projekten**

## Automatisierte wöchentliche Inspektion

Jeden Mittwoch um Mitternacht (UTC) inspiziert unser GitHub-Actions-Workflow automatisch alle FastAPI-Vorlagen, um sicherzustellen, dass sie die Qualitätsstandards erfüllen:

- ✅ **Validierung der Dateistruktur** — stellt sicher, dass alle erforderlichen Dateien und Verzeichnisse vorhanden sind
- ✅ **Überprüfung der Dateiendungen** — validiert, dass Vorlagendateien die korrekten `.py-tpl`-Endungen verwenden
- ✅ **Abhängigkeitsprüfung** — bestätigt, dass FastAPI und benötigte Abhängigkeiten ordnungsgemäß deklariert sind
- ✅ **FastAPI-Implementierung** — prüft, dass Vorlagen eine korrekte FastAPI-App-Initialisierung enthalten
- ✅ **Testausführung** — führt die Tests der Vorlage aus, um die Funktionsfähigkeit zu bestätigen
- ✅ **Smoke-Test** — startet das generierte Projekt mit uvicorn und prüft seine HTTP-Oberfläche
- ✅ **Konsistenz der Konfiguration** — Festlegung der Python-Version, Abhängigkeitsabweichungen, Selbstabhängigkeit
- ✅ **Platzhalter-Rückstände** — kein `<placeholder>` übersteht die Projektgenerierung
- ✅ **Aktualität der Abhängigkeiten** — warnt vor festgelegten Versionen, die hinter ihrem neuesten PyPI-Release zurückliegen

## Was jede Prüfung tut

Die Inspektion generiert aus der Vorlage ein **echtes Projekt** — Kopieren, `-tpl`-Konvertierung, Einfügen der Metadaten — und führt dann jede Prüfung gegen dieses generierte Projekt aus, nicht gegen den Quellcode der Vorlage. Eine Prüfung, die nur die Vorlage liest, kann keinen Platzhalter erkennen, den die Generierung nicht ersetzt hat.

### Smoke-Test

Das generierte Projekt wird mit uvicorn auf einem freien Port gestartet, und der Inspektor fragt so lange ab, bis der Server antwortet oder das Timeout abläuft. Sobald er läuft, werden `/docs` und `/health` angefragt und ihre Statuscodes geprüft. Anschließend wird der Serverprozess beendet, notfalls mit `SIGKILL`, wenn er nicht stoppt.

Das uvicorn-Ziel wird in dieser Reihenfolge ermittelt: `[tool.fastapi-fastkit].app_module` in der generierten `pyproject.toml`, dann `app_module` in der `template-config.yml` der Vorlage, dann die üblichen `main.py`-Speicherorte. Das ist derselbe Vertrag, den `fastkit runserver` verwendet: Eine Vorlage, deren Smoke-Test startet, ist eine Vorlage, deren generiertes Projekt läuft.

Diese Prüfung findet, was statische Analyse nicht finden kann: einen Import, der sich erst zur Laufzeit auflöst, einen `lifespan`, der eine Ausnahme auslöst, ein Konfigurationsfeld ohne Standardwert.

### Konsistenz der Konfiguration

Drei Dinge werden gegen die `pyproject.toml-tpl` der Vorlage geprüft:

- **Die Festlegungen der Python-Version stimmen überein und zielen auf 3.12** — `requires-python`, `target-version` von black und `python_version` von mypy. Eine Vorlage, die als `py311` formatiert, aber `>=3.12` deklariert, ist ein Fehler, der nur darauf wartet, einen Mitwirkenden zu treffen.
- **Keine Abhängigkeitsabweichung** — die in `requirements.txt-tpl` und in `[project].dependencies` deklarierten Pakete dürfen sich nicht widersprechen. Vorlagen liefern beide Dateien aus Gründen der Paketmanager-Kompatibilität mit, und zwei Listen laufen immer auseinander, solange nichts sie prüft.
- **Keine Selbstabhängigkeit** — ein generiertes Projekt darf `FastAPI-fastkit` nicht als Laufzeitabhängigkeit deklarieren. Das CLI ist ein Entwicklungswerkzeug; es in jede generierte App mitzuliefern, zieht den gesamten Abhängigkeitsbaum von fastkit in fremde Projekte.

### Platzhalter-Rückstände

Jedes `<project_name>`, `<description>` und Verwandte müssen während der Generierung ersetzt werden. Jeder `<placeholder>`, der im generierten Projekt noch vorhanden ist, ist ein Fehler — er bedeutet, dass das Einfügen der Metadaten diese Datei nicht kennt und der Nutzer sie unverändert erhalten würde.

### Aktualität der Abhängigkeiten

Festgelegte Versionen werden mit dem neuesten Release auf PyPI verglichen und als Warnungen gemeldet, nie als Fehler — eine Vorlage, die eine Minor-Version zurückliegt, ist eine Information, kein Fehlschlag. Dies ist die einzige Prüfung, die auf das Netzwerk zugreift, und `--offline` überspringt sie.

## Automatisiertes Vorlagen-Testsystem

FastAPI-fastkit enthält ein **revolutionäres automatisiertes Testsystem**, das eine umfassende Validierung jeder Vorlage durchführt:

### Dynamische Vorlagenerkennung

Das Testsystem **erkennt alle Vorlagen automatisch**, ohne manuelle Konfiguration:

```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Results show all discovered templates
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-async-crud]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-dockerized]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-psql-orm]
```

### Umfassende Testabdeckung

Jede Vorlage durchläuft **umfassende End-to-End-Tests**:

#### ✅ Projektanlegung
- Kopieren der Vorlage und Transformation der Dateien
- Injektion der Projekt-Metadaten (Name, Autor, Beschreibung)
- Validierung der Dateistruktur

#### ✅ Kompatibilität mit Paketmanagern
- **UV** (Standard): schneller Rust-basierter Paketmanager
- **PDM**: moderne Python-Abhängigkeitsverwaltung
- **Poetry**: etablierte Abhängigkeitsverwaltung
- **PIP**: traditioneller Python-Paketmanager

#### ✅ Verwaltung der virtuellen Umgebung
- Erstellen der Umgebung je Paketmanager
- Verifikation der Abhängigkeitsinstallation
- Workflows je Paketmanager

#### ✅ Auflösung der Abhängigkeiten
- Erzeugung von `pyproject.toml` (UV, PDM, Poetry)
- Erzeugung von `requirements.txt` (PIP)
- Metadaten-Konformität (PEP 621)
- Konfiguration des Build-Systems

#### ✅ Validierung der Projektstruktur
- Identifikation als FastAPI-Projekt
- Existenz der erforderlichen Dateien
- Verifikation der Verzeichnisstruktur

### Beispiele für die Testausführung

**Alle Vorlagen-Tests ausführen:**
```console
$ pytest tests/test_templates/test_all_templates.py -v
```

**Eine bestimmte Vorlage testen:**
```console
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default] -v
```

**Mit PDM-Umgebung testen:**
```console
$ pdm run pytest tests/test_templates/test_all_templates.py -v
```

### Continuous Integration

Das automatisierte Testsystem läuft in **CI/CD-Pipelines**:

- ✅ **PR-Validierung**: jede PR testet die betroffenen Vorlagen
- ✅ **Nightly-Tests**: vollständige Validierung der Vorlagen-Suite
- ✅ **Paketmanager-Tests**: Kreuzvalidierung mit allen Managern
- ✅ **Umgebungstests**: mehrere Python-Versionen und Plattformen

### Vorteile für Mitwirkende

**Tests ohne Konfiguration:**

- 🚀 neue Vorlage hinzufügen → automatische Tests
- ⚡ keine manuelle Erstellung von Testdateien nötig
- 🛡️ konsistente Qualitätsstandards

**Umfassende Abdeckung:**

- 🔍 End-to-End-Tests der Projektanlegung
- 📦 Validierung mit mehreren Paketmanagern
- 🏗️ vollständige Tests der Abhängigkeitsauflösung
- ✅ Simulation realer Nutzung

**Entwicklererfahrung:**

- 🎯 **Konzentration auf den Vorlageninhalt**: Tests laufen automatisch
- 🔄 **Sofortiges Feedback**: schnelle Testausführung
- 📊 **Klare Ergebnisse**: detaillierte Testberichte
- 🚫 **Kein Boilerplate**: null Testkonfiguration nötig

## Manuelle Vorlagen-Inspektion

Für Entwicklung und Debugging können Sie Vorlagen manuell mit unserem lokalen Inspektionsskript oder den Makefile-Befehlen prüfen:

### Das Inspektionsskript direkt verwenden

```console
# Inspect all templates
$ python scripts/inspect-templates.py

# Inspect specific templates
$ python scripts/inspect-templates.py --templates fastapi-default,fastapi-async-crud

# Verbose output with detailed information
$ python scripts/inspect-templates.py --verbose

# Save results to custom file
$ python scripts/inspect-templates.py --output my_results.json
```

#### Inspektions-Flags

| Flag | Wirkung | Verwenden Sie es, wenn |
|---|---|---|
| `--offline` | Überspringt jede Netzwerkabfrage (Bericht zur Aktualität der Abhängigkeiten) | kein Netzwerk verfügbar ist oder Sie einen schnellen, abgeschotteten Lauf möchten |
| `--no-smoke` | Überspringt das Starten des generierten Projekts mit uvicorn | Sie nur an der Struktur iterieren; der Smoke-Test ist der langsamste Schritt |
| `--mypy` | Führt eine Typprüfung des generierten Projekts mit mypy durch | Sie eine Vorlage einreichen — optional, weil es langsam ist |
| `--templates` | Kommagetrennte Liste der zu inspizierenden Vorlagen | Sie an einer einzelnen Vorlage arbeiten |
| `--verbose` | Ausführliche Ausgabe | Sie einen Fehlschlag debuggen |
| `--output` | Pfad für die JSON-Ergebnisdatei | Sie mehrere Läufe nebeneinander aufbewahren möchten |

Eine schnelle lokale Schleife für eine einzelne Vorlage:

```console
$ python scripts/inspect-templates.py \
    --templates fastapi-sqlmodel --offline --no-smoke --verbose
```

…und die vollständige Prüfung vor dem Öffnen einer PR:

```console
$ python scripts/inspect-templates.py --templates fastapi-sqlmodel --mypy
```

### Makefile-Befehle verwenden

```console
# Inspect all templates
$ make inspect-templates

# Inspect with verbose output
$ make inspect-templates-verbose

# Inspect specific templates
$ make inspect-template TEMPLATES="fastapi-default,fastapi-async-crud"
```

## Ergebnisse der Inspektion

- **Erfolgreiche Inspektionen** werden in Workflow-Ausgaben und -Artefakten protokolliert
- **Fehlgeschlagene Inspektionen** erstellen automatisch GitHub-Issues mit detaillierten Fehlerberichten
- Die **Inspektionshistorie** wird 30 Tage lang in GitHub-Actions-Artefakten aufbewahrt

## Die Inspektionsausgabe verstehen

Beim Ausführen der Vorlagen-Inspektion sehen Sie eine Ausgabe wie diese:

```console
📋 Found 6 templates to inspect: fastapi-async-crud, fastapi-custom-response, fastapi-default, fastapi-dockerized, fastapi-empty, fastapi-psql-orm
============================================================
🔍 Inspecting template: fastapi-async-crud
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-async-crud
✅ fastapi-async-crud: PASSED
----------------------------------------
🔍 Inspecting template: fastapi-custom-response
   Path: /path/to/src/fastapi_fastkit/fastapi_project_template/fastapi-custom-response
✅ fastapi-custom-response: PASSED
----------------------------------------
...
============================================================
📊 INSPECTION SUMMARY
   Total templates: 6
   ✅ Passed: 6
   ❌ Failed: 0
🎉 All templates passed inspection!
📄 Results saved to: template_inspection_results.json
```

## Anforderungen an Vorlagen

Damit eine Vorlage die Inspektion besteht, muss sie diese Anforderungen erfüllen:

### Dateistruktur
- Muss ein `src/`-Verzeichnis mit Python-Quellcodedateien enthalten
- Python-Dateien müssen die Endung `.py-tpl` verwenden
- Muss ein `tests/`-Verzeichnis und eine `README.md-tpl`-Datei enthalten
- Muss `pyproject.toml-tpl` (PEP 621) enthalten. Mitgelieferte Vorlagen sind pyproject-first und liefern keine `setup.py-tpl` mehr mit; die Inspektion akzeptiert sie weiterhin, damit Vorlagen von Drittanbietern funktionsfähig bleiben, aber neue Vorlagen dürfen keine hinzufügen.
- `requirements.txt-tpl` ist optional, wenn `pyproject.toml-tpl` `[project].dependencies` deklariert — sind jedoch beide vorhanden, müssen sie übereinstimmen (siehe *Konsistenz der Konfiguration*)
- Muss durchgängig auf Python 3.12 zielen: `requires-python = ">=3.12"`, black `target-version = ["py312"]`, mypy `python_version = "3.12"` und `python:3.12-slim` für jedes Docker-Basis-Image
- Darf `FastAPI-fastkit` nicht als Laufzeitabhängigkeit deklarieren
- Darf nach der Generierung keinen `<placeholder>` unersetzt lassen

### FastAPI-Anforderungen
- Muss die FastAPI-App-Initialisierung enthalten
- Muss `fastapi` als Abhängigkeit in mindestens einem von `pyproject.toml-tpl` `[project].dependencies`, `requirements.txt-tpl` oder `setup.py-tpl` `install_requires` deklarieren
- Muss in allen Vorlagendateien gültige Python-Syntax aufweisen

### Identitätsmarker
Vorlagen sollten FastAPI-fastkit-Identitätsmarker tragen, damit generierte Projekte von unverwandten FastAPI-Projekten im Workspace des Nutzers unterscheidbar sind:

- `pyproject.toml-tpl` — sowohl ein `[FastAPI-fastkit templated]`-Präfix in `description` als auch eine `[tool.fastapi-fastkit]`-Tabelle mit `managed = true`.
- `setup.py-tpl` — `[FastAPI-fastkit templated]`-Präfix im `description`-Argument von `setup()`.

`is_fastkit_project()` akzeptiert jeden dieser Marker (pyproject hat Vorrang, setup.py ist der Legacy-Fallback; die Übereinstimmungsprüfung ist case-insensitive). Die Metadaten-Injektion sorgt dafür, dass die Marker in generierten Projekten landen, auch wenn eine Vorlage sie vergisst.

### Qualitätsstandards
- Alle Vorlagendateien müssen syntaktisch korrekt sein
- Abhängigkeiten müssen korrekt spezifiziert sein
- Die Vorlagenstruktur muss den FastAPI-fastkit-Konventionen folgen

Diese automatisierte Qualitätssicherung garantiert, dass alle Vorlagen zuverlässig und produktionsreif bleiben.

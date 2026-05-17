# Welchen Starter soll ich wählen?

FastAPI-fastkit bietet mehrere Wege, ein Projekt zu starten. Diese Seite ist eine **Entscheidungshilfe** für Einsteiger: Wählen Sie hier einen Pfad und springen Sie dann zum [Schnellstart](quick-start.md), um das Projekt tatsächlich zu erstellen.

Wenn Sie unsicher sind, lautet die kurze Antwort:

> **Beginnen Sie mit `fastkit init --interactive` und wählen Sie das Preset `domain-starter`.** Es ist der empfohlene Standard für moderne API-Projekte.

Der Rest dieser Seite erklärt, warum das so ist und wann eine andere Wahl sinnvoller sein kann.

## TL;DR — Wahl nach Benutzertyp

| Sie sind … | Beginnen Sie mit |
|---|---|
| Neu bei FastAPI und möchten eine geführte Tour | `fastkit init --interactive` (Preset: **`domain-starter`**) |
| Möchten eine funktionierende CRUD-Demo zum Lesen und Anpassen | `fastkit startdemo fastapi-default` |
| Möchten das kleinstmögliche Gerüst | `fastkit init --interactive` (Preset: **`minimal`**) |
| Schreiben einen schnellen Prototyp / ein Single-File-Skript | `fastkit init --interactive` (Preset: **`single-module`**) |
| Brauchen eine echte Datenbank (PostgreSQL + SQLAlchemy + Alembic) | `fastkit startdemo fastapi-psql-orm` |
| Möchten ein produktionsnahes domänenorientiertes Layout für eine mittelgroße API | `fastkit init --interactive` (Preset: **`domain-starter`**) |

## `startdemo` vs. `init --interactive` — wo ist der Unterschied?

Dies sind die beiden Haupteinstiegspunkte. Sie decken unterschiedliche Bedürfnisse ab.

### `fastkit startdemo <template>`

Legt ein **vollständiges, funktionierendes Beispielprojekt** auf der Festplatte ab, basierend auf einer der mitgelieferten Vorlagen (`fastapi-default`, `fastapi-async-crud`, `fastapi-psql-orm`, `fastapi-domain-starter`, …). Der Quellcode der Vorlage wird unverändert übernommen, wobei Platzhalter für Metadaten (`<project_name>` usw.) gefüllt werden.

- ✅ Der schnellste Weg zu einer lauffähigen Demo.
- ✅ Aller Code ist real und lesbar — ideal zum Lernen anhand von Beispielen.
- ❌ Stack und Struktur der Vorlage stehen fest; Sie können also nicht nebenbei CORS auswählen und gleichzeitig die Authentifizierung weglassen.

```console
$ fastkit list-templates              # show what's available
$ fastkit startdemo fastapi-default   # generate a project from one
```

### `fastkit init --interactive`

Führt Sie durch einen **geführten Assistenten**: Projektmetadaten → Architektur-Preset → Funktionsauswahl (Datenbank, Authentifizierung, Tests, Deployment, …) → Paketmanager → Bestätigung. Der Generator wählt pro Preset eine geeignete Basisvorlage und überlagert die ausgewählten Funktionen.

- ✅ Sie stellen den Stack zusammen, den Sie wirklich wollen.
- ✅ Das Architektur-Preset formt das Projekt-Layout (Single-File, geschichtet, domänenorientiert, …).
- ❌ Die umfangreicheren Presets, bei denen die mitgelieferte `main.py` erhalten bleibt (`classic-layered`, `domain-starter`), erzeugen zwar Konfigurationsmodule, erwarten aber, dass Sie diese selbst in die vorhandenen Router einbinden. Die genaue Vereinbarung pro Preset und pro Funktion finden Sie in der [Architektur-Preset-Matrix](../reference/preset-feature-matrix.md).

```console
$ fastkit init --interactive
```

## Die vier Architektur-Presets

Diese erscheinen in `fastkit init --interactive` nach den Projektinformations-Eingaben. Nutzen Sie diesen Abschnitt, um Ihre Wahl zu treffen.

### `minimal` — möglichst einfach starten, später wachsen

Die kleinstmögliche lauffähige FastAPI-App. Leeres Gerüst + eine einzige `src/main.py`, die aus Ihren Funktions-Flags regeneriert wird. CORS, Rate-Limiting und Prometheus-Instrumentierung werden automatisch in `main.py` eingebaut, sofern ausgewählt.

- 👤 **Wer**: Personen, die Struktur selbst hinzufügen möchten, wenn das Projekt wächst, oder die FastAPI ohne vorgefertigte Layout-Meinungen erkunden.
- 📦 **Basisvorlage**: `fastapi-empty`.
- 🧠 **Mentales Modell**: „Gib mir eine Datei mit importiertem FastAPI, den Rest ergänze ich selbst.“

### `single-module` — Prototyp im Skriptstil

Alles lebt in einem einzigen Modul. Dieselbe `main.py`-Regenerierung wie bei `minimal`.

- 👤 **Wer**: Sie schreiben ein Klebescript, einen kleinen Webhook oder einen Eintages-Prototyp, der keine Paketgrenzen braucht.
- 📦 **Basisvorlage**: `fastapi-single-module`.
- 🧠 **Mentales Modell**: „ich will eine Python-Datei, die ich am Stück ausführen und lesen kann."

### `classic-layered` — geschichtetes Layout (api / crud / schemas / core)

Das „Django-artige“ Layout: Der Code wird horizontal nach Verantwortungsbereichen getrennt, also Router in `api/`, CRUD-Logik in `crud/`, Pydantic-Schemas in `schemas/` und die Konfiguration in `core/`. Die mitgelieferte `main.py` bleibt **erhalten** (CORS ist dort bereits eingebunden); generierte Datenbank-/Auth-Konfigurationen landen unter `src/core/`.

- 👤 **Wer**: Teams, die mit Django-/Rails-Layouts vertraut sind, Projekte mit vielen kleinen Endpunkten, die sich gemeinsame CRUD-Infrastruktur teilen.
- 📦 **Basisvorlage**: `fastapi-default`.
- 🧠 **Mentales Modell**: „Code danach teilen, was er _ist_."

### `domain-starter` — domänenorientiert (empfohlener Standard)

Code wird vertikal nach **Geschäftskonzept** geteilt: Jede Domäne besitzt ihren eigenen Router, Service, Repository und ihre Schemas unter `src/app/domains/<concept>/`. Wird mit einem `/health`-Endpunkt und einer Beispieldomäne `items` geliefert, die Sie für jedes neue Konzept kopieren und umbenennen. Die mitgelieferte `main.py` (unter `src/app/`) bleibt erhalten; generierte Konfigurationen landen unter `src/app/core/`.

- 👤 **Wer**: mittelgroße APIs, die mehrere unterschiedliche Konzepte aufnehmen werden (users, orders, billing, …). Die empfohlene Standardlösung für moderne APIs.
- 📦 **Basisvorlage**: `fastapi-domain-starter`.
- 🧠 **Mentales Modell**: „Code danach teilen, was er _für das Geschäft tut_."

## Vergleichsmatrix

Eine Übersicht auf einen Blick.

| | `minimal` | `single-module` | `classic-layered` | `domain-starter` |
|---|---|---|---|---|
| Basisvorlage | `fastapi-empty` | `fastapi-single-module` | `fastapi-default` | `fastapi-domain-starter` |
| Projekteinstieg | `src/main.py` | `src/main.py` | `src/main.py` | `src/app/main.py` |
| Speicherort der Router | (Sie fügen sie hinzu) | (innerhalb von `main.py`) | `src/api/routes/` | `src/app/domains/<concept>/router.py` |
| Ordner pro Domäne | ❌ | ❌ | ❌ | ✅ |
| Eingebauter `/health`-Endpunkt | ✅ | ✅ | ❌ | ✅ |
| `main.py` aus Funktionen regeneriert | ✅ | ✅ | ❌ | ❌ |
| CORS in `main.py` vorverdrahtet | wird bei Auswahl ergänzt | wird bei Auswahl ergänzt | ja (env-gesteuert) | ja (env-gesteuert) |
| pyproject-first | optional | optional | optional | ✅ |
| Am besten für | „ich baue meine Struktur selbst auf" | „Single-File-Prototyp" | „nach Anliegen teilen" | „nach Geschäftskonzept teilen" |

Für den vollständigen Vertrag pro Funktion (Zielpfade von Datenbank-/Auth-Konfigurationen, welche Auswahlen manuelle Verdrahtung statt automatischer benötigen, wann Warnungen ausgelöst werden) siehe die [Architektur-Preset-Matrix](../reference/preset-feature-matrix.md).

## Eine `startdemo`-Vorlage wählen

`fastkit startdemo <template>` ist am besten geeignet, wenn Sie ein **vollständiges, lauffähiges Beispiel** statt einer geführten Zusammenstellung wollen. Die meisten Vorlagen entsprechen grob einem der vier Presets oben, bringen aber zusätzlichen Beispielcode mit (CRUD-Endpunkte über einem Mock-Speicher, benutzerdefinierte Antwortbehandlung, Docker-Werkzeuge usw.).

| Vorlage | Nächstes Preset | Wann auswählen |
|---|---|---|
| `fastapi-default` | `classic-layered` | Funktionierende CRUD-Demo mit dem geschichteten Layout. Gute Anlaufstelle. |
| `fastapi-empty` | `minimal` | Nacktes Gerüst; gleiche Form, die `minimal` produziert. |
| `fastapi-single-module` | `single-module` | Single-File-Demo. |
| `fastapi-domain-starter` | `domain-starter` | Empfohlener moderner Standard; bringt ein items-Domänenbeispiel mit. |
| `fastapi-async-crud` | `classic-layered` | Asynchrone Variante von `fastapi-default`. |
| `fastapi-custom-response` | `classic-layered` | Demonstriert benutzerdefinierte Response-Hüllen / Formatierung. |
| `fastapi-dockerized` | `classic-layered` | Fügt dem Standard-Layout ein produktionstaugliches Dockerfile hinzu. |
| `fastapi-psql-orm` | (kein direktes Preset) | PostgreSQL + SQLAlchemy + Alembic. Wählen Sie dies, wenn Sie eine echte Datenbank brauchen. |
| `fastapi-mcp` | (kein direktes Preset) | Integration des Model Context Protocol. |

`fastkit list-templates` zeigt die aktuelle Liste mit einzeiligen Beschreibungen.

## Häufige Fragen

**F. Muss ich mich gleich am Anfang auf ein Preset / eine Vorlage festlegen?**
Nein — Sie können den generierten Code später jederzeit von Hand reorganisieren. Die Presets sind Ausgangspunkte, keine Verträge. Überdenken Sie die Wahl nicht zu lange.

**F. Was ist die „moderne" Wahl?**
`domain-starter`. Dieses Preset ist pyproject-first, bringt einen `/health`-Endpunkt mit und nutzt ein Layout, auf das viele gut gepflegte mittelgroße FastAPI-Projekte früher oder später hinauslaufen.

**F. Kann ich später von `classic-layered` zu `domain-starter` wechseln?**
Ja, aber das ist ein manuelles Refactoring — es gibt keinen Migrationsbefehl. Wenn Sie meinen, Ihr Projekt wird groß genug, um Domänenordner zu brauchen, starten Sie gleich dort.

**F. Was, wenn ich einfach nur FastAPI lernen will?**
Beginnen Sie mit `fastkit startdemo fastapi-default` — lesen Sie den Code, lassen Sie die Tests laufen, ändern Sie ein paar Endpunkte. Sobald Sie sich wohlfühlen, ist `fastkit init --interactive` mit dem Preset `domain-starter` der natürliche nächste Schritt.

**F. Wo sehe ich die genauen Dateien, die jedes Preset generiert?**
Die [Architektur-Preset-Matrix](../reference/preset-feature-matrix.md) ist die Referenzseite dafür.

## Nächste Schritte

- [Schnellstart](quick-start.md) — erstellen Sie tatsächlich Ihr erstes Projekt.
- [Projekte erstellen](creating-projects.md) — ausführlichere Vorstellung der CLI-Optionen.
- [Tutorial Domänenorientiertes Projekt](../tutorial/domain-starter.md) — wenn Sie `domain-starter` gewählt haben, führt Sie dieses Tutorial Schritt für Schritt durch den generierten Projektbaum, das mitgelieferte `items`-Beispiel und das Hinzufügen Ihrer nächsten Domäne.
- [Architektur-Preset-Matrix](../reference/preset-feature-matrix.md) — der vollständige Vertrag pro Preset / pro Funktion.

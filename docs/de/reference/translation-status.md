# Übersetzungsstatus

FastAPI-fastkit stellt die Dokumentation in mehreren Sprachen bereit, diese Übersetzungen sind aber **nicht vollständig gleichauf**. Diese Seite ist die maßgebliche Übersicht dafür, was tatsächlich wo übersetzt ist, was angezeigt wird, wenn eine Seite noch nicht übersetzt wurde, und wie Sie helfen können.

## Maßgebliche Referenz

> **Englisch (`en`) ist die maßgebliche Referenz.** Alle in der Dokumentation beschriebenen Verhaltensweisen von Produkt, CLI und API werden zuerst in den englischen Dateien festgehalten. Andere Sprachen sind Übersetzungen dieser englischen Quellen und können einem Release hinterherhinken.
>
> Wenn eine übersetzte Seite der englischen Seite widerspricht, **vertrauen Sie der englischen Seite**, bis die Übersetzung nachgezogen wird.

Die englischen Dateien liegen unter [`docs/en/`](https://github.com/bnbong/FastAPI-fastkit/tree/main/docs/en). Jede andere Sprache (`docs/ko/`, `docs/ja/`, …) ist ein Übersetzungsziel.

Die `CHANGELOG.md` im Stammverzeichnis des Repositorys gehört ebenfalls zu dieser englischen Referenz. Sprachspezifische `changelog.md`-Seiten können als Einstiegspunkt dienen, verwenden aber bewusst die kanonische englische Releasehistorie statt eigener übersetzter Kopien.

## Vollständigkeit pro Sprache

Die unten stehenden Zahlen zählen die Markdown-Seiten im Verzeichnisbaum jeder Sprache relativ zur englischen Quelle. Sie spiegeln wider, was tatsächlich im Repository vorhanden ist — nicht das, was im Sprachumschalter angezeigt wird (siehe nächster Abschnitt).

| Sprache | Status | Markdown-Seiten | Anmerkungen |
|---|---|---:|---|
| 🇬🇧 Englisch (`en`) | ✅ Maßgebliche Referenz | 26 / 26 | Maßgeblich. |
| 🇰🇷 Koreanisch (`ko`) | ✅ Vollständig | 26 / 26 | Alle Seiten dieser Sprachversion sind vorhanden. Phase 1: oberste Ebene + Kern des Benutzerhandbuchs; Phase 2: restliches Benutzerhandbuch + alle Tutorials; Phase 3: Beiträge + Referenzseiten. `docs/ko/changelog.md` verweist bewusst auf das kanonische englische `CHANGELOG.md`. |
| 🇯🇵 Japanisch (`ja`) | ✅ Vollständig | 26 / 26 | Alle Seiten dieser Sprachversion sind vorhanden. Phase 1: oberste Ebene + Kern des Benutzerhandbuchs; Phase 2: restliches Benutzerhandbuch + alle Tutorials; Phase 3: Beiträge + Referenzseiten. `docs/ja/changelog.md` verweist bewusst auf das kanonische englische `CHANGELOG.md`. |
| 🇨🇳 Chinesisch (`zh`) | 🔴 Skelett | 0 / 26 | Nur als Sprach-Build-Ziel vorhanden. Jede Seite fällt auf Englisch zurück. |
| 🇪🇸 Spanisch (`es`) | ✅ Vollständig | 26 / 26 | Alle Seiten dieser Sprachversion sind vorhanden. Phase 1: oberste Ebene + Kern des Benutzerhandbuchs; Phase 2: restliches Benutzerhandbuch + alle Tutorials; Phase 3: Beiträge + Referenzseiten. `docs/es/changelog.md` verweist bewusst auf das kanonische englische `CHANGELOG.md`. |
| 🇫🇷 Französisch (`fr`) | ✅ Vollständig | 26 / 26 | Alle Seiten dieser Sprachversion sind vorhanden. Phase 1: oberste Ebene + Kern des Benutzerhandbuchs; Phase 2: restliches Benutzerhandbuch + alle Tutorials; Phase 3: Beiträge + Referenzseiten. `docs/fr/changelog.md` verweist bewusst auf das kanonische englische `CHANGELOG.md`. |
| 🇩🇪 Deutsch (`de`) | ✅ Vollständig | 26 / 26 | Alle Seiten dieser Sprachversion sind vorhanden. Phase 1: oberste Ebene + Kern des Benutzerhandbuchs; Phase 2: restliches Benutzerhandbuch + alle Tutorials; Phase 3: Beiträge + Referenzseiten. `docs/de/changelog.md` verweist bewusst auf das kanonische englische `CHANGELOG.md`. |

*Stand verifiziert am 2026-05-17; die Zeile `de` wurde für den aktuellen Branch nach dem Abschluss von Phase 3 (Beiträge + Referenzseiten) neu gezählt. Deutsch umfasst nun alle Seiten dieser Sprachversion, und `docs/de/changelog.md` verweist auf den kanonischen englischen Changelog.* Diese Zahlen werden manuell gepflegt; um den aktuellen Stand vom Repo-Root neu zu zählen, führen Sie aus:

```console
$ for loc in en ko ja zh es fr de; do
    echo "$loc: $(find docs/$loc -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
  done
```

Wenn die Neuzählung nicht mit der Tabelle übereinstimmt, ist die Tabelle veraltet — bitte aktualisieren Sie sie (oder öffnen Sie eine PR / ein Issue, das die Abweichung meldet).

Legende:

- ✅ **Maßgebliche Referenz** — die Sprache, in der zuerst geschrieben wird.
- 🟡 **Teilweise** — einige Seiten sind übersetzt; fehlende Seiten fallen auf Englisch zurück.
- 🔴 **Skelett** — der Eintrag im Sprachumschalter existiert, es sind aber noch keine übersetzten Seiten eingecheckt. Die Seite rendert englische Inhalte unter den übersetzten Navigationsbeschriftungen.

## Wie der Fallback funktioniert

Die Dokumentations-Site verwendet [`mkdocs-static-i18n`](https://github.com/ultrabug/mkdocs-static-i18n) mit `fallback_to_default: true`. Das bedeutet:

- Für jede übersetzte Sprache schreibt MkDocs nur die Seiten, die im Verzeichnis dieser Sprache existieren.
- Für jede Seite, die **nicht** in einer Sprache vorhanden ist, fällt der Build auf die englische Version dieser Seite zurück.
- Der seitenweite Sprachumschalter listet immer alle konfigurierten Sprachen auf, unabhängig davon, wie viele Seiten jede enthält, weil der Build für jeden Fall eine erreichbare URL erzeugt (Seite → ggf. Fallback auf Englisch).

Ein 🔴 Skelett-Eintrag im Sprachumschalter ist also **kein** Versprechen, dass die Dokumentation übersetzt ist — er bedeutet nur, dass das Build-Ziel für diese Sprachversion konfiguriert ist. Das Verhalten ist beabsichtigt (externe Mitwirkende können Seite für Seite übersetzen, ohne die Linkstruktur zu zerstören), lässt den Sprachumschalter aber vollständiger wirken, als der zugrunde liegende Inhalt tatsächlich ist.

## So lesen Sie die Dokumentationsseite

- **Standardmäßig Englisch verwenden**, wenn Sie die genaueste, aktuellste Information möchten.
- **Eine übersetzte Sprache** nur verwenden, nachdem Sie auf dieser Seite den Status der Sprache geprüft haben. Ist er 🟡 oder 🔴 und stoßen Sie auf ein noch nicht übersetztes Thema, lesen Sie tatsächlich einen englischen Fallback unter einer übersetzten Navigationsbeschriftung.

## Wie Sie helfen können

Der aktuelle Rollout läuft nach dem Prinzip **ein Tracking-Issue pro Sprache**, mit der Arbeit aufgeteilt in **Phasen** — `ko` etwa wird in Phase 1 (oberste Ebene + Kern des Benutzerhandbuchs), Phase 2 (restliches Benutzerhandbuch + alle Tutorials) und Phase 3 (Beiträge + Referenzseiten) ausgeliefert. Jede Phase wird als eigene PR geliefert, sodass Reviewer einen zusammenhängenden Ausschnitt absegnen können, ohne auf die Fertigstellung der gesamten Sprachversion zu warten.

Wenn Sie beitragen möchten:

1. Lesen Sie den [Übersetzungsleitfaden](../contributing/translation-guide.md) für Workflow, Werkzeuge und Stilkonventionen.
2. **Prüfen oder eröffnen Sie zuerst das Tracking-Issue der Sprachversion.** Hat eine Sprachversion bereits ein offenes Tracking-Issue, reservieren Sie dort eine Phase (oder eine bestimmte Seite innerhalb einer Phase), damit die Arbeit nicht doppelt erfolgt. Existiert noch kein Tracking-Issue für die gewünschte Sprachversion, öffnen Sie eines, das die zugehörigen Seiten je Phase auflistet, und starten Sie mit Phase 1.
3. **Eine PR pro Phase ist die bevorzugte Form.** Kleinere PRs zum Korrigieren einzelner Seiten sind weiterhin willkommen — besonders, wenn eine Übersetzung veraltet ist — aber bei neuer Lokalisierungsarbeit hält das Bündeln pro Phase Glossar-Entscheidungen und Formulierungen für Querverweise über den gesamten Ausschnitt hinweg konsistent.
4. Öffnen Sie die PR und legen Sie Dateien unter `docs/<locale>/<gleicher Pfad>` ab. Halten Sie die Dateinamen identisch zur englischen Quelle, damit MkDocs sie automatisch erfasst.
5. Behandeln Sie lokalisierte Changelog-Seiten als Einstiegsseite oder Verweis auf das kanonische englische `CHANGELOG.md`, sofern die Projektrichtlinie das nicht ausdrücklich ändert.
6. Aktualisieren Sie die Tabelle auf dieser Seite, um die neue Vollständigkeit widerzuspiegeln (verwenden Sie das Neuzählungs-Snippet am Anfang der Seite), und aktualisieren Sie das „Stand verifiziert"-Datum, damit Reviewer sehen, wann zuletzt abgeglichen wurde. Geben Sie in der Spalte „Anmerkungen" an, welche Phase abgeschlossen ist, falls die Sprache noch teilweise ist.

Bug-Reports zu übersetzten Seiten, die mit dem englischen Original auseinanderlaufen, sind willkommen — bitte verlinken Sie die englische und die übersetzte Seite, damit wir triagieren können.

## Warum wir 🔴 Skelett-Sprachen überhaupt ausliefern

Zwei Gründe:

1. **Vorhersehbare URL-Struktur.** Jede Sprache hat bereits ihren `/<locale>/`-Unterbaum erreichbar, sodass der Link einer übersetzten Seite ab dem ersten Tag stabil ist — einschließlich der in diesem Leitfaden veröffentlichten Links.
2. **Geringere Hürde für Mitwirkende.** Wer eine einzelne Seite übersetzt, muss nicht zusätzlich ein neues Sprach-Build-Ziel in der MkDocs-Konfiguration einrichten — es reicht, die Datei an der richtigen Stelle abzulegen.

Bleibt eine Sprache über einen längeren Zeitraum auf 🔴 Skelett ohne Beitragsaktivität, prüfen wir gegebenenfalls, ob das Build-Ziel weiter aktiv bleibt. Diese Entscheidung wird separat verfolgt und **wird** durch diese Statusseite nicht stillschweigend geändert.

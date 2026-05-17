# Übersetzungsleitfaden

Dieser Leitfaden erklärt, wie Sie Übersetzungen zur Dokumentation von FastAPI-fastkit beitragen.

## Maßgebliche Referenz und Übersetzungsrichtlinie

> **Englisch (`en`) ist die maßgebliche Referenz** für die FastAPI-fastkit-Dokumentation. Jede andere Sprache ist ein Übersetzungsziel, das dem Englischen um ein Release oder einzelne Seiten hinterherhängen kann.
>
> Wenn eine übersetzte Seite der englischen Seite widerspricht, **vertrauen Sie der englischen Seite**, bis die Übersetzung nachzieht. Übersetzungen werden in dem Vollständigkeitsgrad ausgeliefert, den die Mitwirkenden erreicht haben — eine teilweise Abdeckung ist normal und zu erwarten.

Das nutzerseitige Pendant zu dieser Politik ist die Seite [Übersetzungsstatus](../reference/translation-status.md), die die tatsächliche Vollständigkeit jeder Sprache auflistet und erklärt, wie MkDocs noch nicht übersetzte Seiten rendert (kurz: sie fallen auf Englisch zurück).

Die `CHANGELOG.md` im Stammverzeichnis des Repositorys bleibt ebenfalls als kanonische Releasehistorie auf Englisch. Falls eine Sprache eine `changelog.md`-Seite anbietet, sollte diese auf den kanonischen englischen Changelog verlinken oder ihn einbinden, statt einen separaten übersetzten Changelog zu pflegen — sofern die Projektrichtlinie das später nicht ändert.

Wenn Sie eine Übersetzung beitragen, aktualisieren Sie auch die Tabelle der Statusseite, damit Nutzer den Stand sehen können, ohne ihn aus dem Sprachumschalter erraten zu müssen.

## Übersicht

FastAPI-fastkit nutzt ein automatisiertes Übersetzungssystem auf KI-Basis, um die Dokumentation in mehrere Sprachen zu übersetzen. Das System:

- Liest die Quelldokumentation auf Englisch
- Übersetzt Inhalte über KI-APIs (OpenAI oder Anthropic)
- Speichert Übersetzungen in sprachspezifischen Verzeichnissen
- Erstellt GitHub-Pull-Requests zur Überprüfung

Die Automatisierung liefert einen Ausgangspunkt; eine menschliche Überprüfung ist vor dem Merge weiterhin erforderlich. KI-generierte Übersetzungen sollten in ihren PRs als „draft" markiert und von einem fließenden Sprecher überprüft werden, bevor sie gemergt werden.

## Unterstützte Sprachen

Dies sind die Sprachen, für die die Dokumentations-Site derzeit einen Build erzeugt. Die bloße Konfiguration eines Sprach-Build-Ziels **bedeutet nicht**, dass die Seiten dieser Sprache bereits übersetzt sind — den tatsächlichen Stand sehen Sie im [Übersetzungsstatus](../reference/translation-status.md).

- 🇰🇷 Koreanisch (ko)
- 🇯🇵 Japanisch (ja)
- 🇨🇳 Chinesisch (zh)
- 🇪🇸 Spanisch (es)
- 🇫🇷 Französisch (fr)
- 🇩🇪 Deutsch (de)

## Voraussetzungen

### 1. Abhängigkeiten für Übersetzungen installieren

```bash
# Mit pip installieren
pip install openai anthropic

# Oder mit pdm
pdm install -G translation
```

### 2. API-Schlüssel einrichten

Sie benötigen einen API-Schlüssel von OpenAI oder Anthropic:

```bash
# Für OpenAI
export TRANSLATION_API_KEY="sk-..."

# Oder für Anthropic
export TRANSLATION_API_KEY="sk-ant-..."
```

### 3. GitHub CLI installieren (optional)

Für die automatische PR-Erstellung:

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Anmelden
gh auth login
```

## Nutzung

### Mit Make-Befehlen (empfohlen)

Der einfachste Weg, Übersetzungen auszuführen:

```bash
# Alle Dokumente in alle Sprachen übersetzen
make translate

# In eine bestimmte Sprache übersetzen
make translate LANG=ko

# API-Anbieter und Modell festlegen
make translate LANG=ko PROVIDER=openai MODEL=gpt-4
make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
```

### Mit dem Skript direkt

#### Die gesamte Dokumentation übersetzen

Die gesamte Dokumentation in alle unterstützten Sprachen übersetzen:

```bash
python scripts/translate.py --api-provider openai
```

### In eine bestimmte Sprache übersetzen

Nur ins Koreanische übersetzen:

```bash
python scripts/translate.py --target-lang ko --api-provider openai
```

### Bestimmte Dateien übersetzen

Nur bestimmte Dokumentationsdateien übersetzen:

```bash
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/installation.md user-guide/quick-start.md \
  --api-provider openai
```

### PR-Erstellung überspringen

Übersetzen, ohne eine GitHub-PR zu erstellen:

```bash
python scripts/translate.py --target-lang ko --no-pr --api-provider openai
```

### Anthropic Claude verwenden

Anthropic Claude statt OpenAI verwenden:

```bash
python scripts/translate.py \
  --target-lang ko \
  --api-provider anthropic \
  --api-key "sk-ant-..."
```

## Verzeichnisstruktur

Nach der Übersetzung sieht die Dokumentationsstruktur so aus:

```
docs/
├── en/                    # Englisch (Original)
│   ├── index.md
│   ├── user-guide/
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── ...
│   ├── tutorial/
│   └── ...
├── ko/                    # Koreanisch
│   ├── index.md
│   ├── user-guide/
│   └── ...
├── ja/                    # Japanisch
├── zh/                    # Chinesisch
├── es/                    # Spanisch
├── fr/                    # Französisch
├── de/                    # Deutsch
├── css/                   # Gemeinsame Assets
├── js/                    # Gemeinsame Assets
└── img/                   # Gemeinsame Assets
```

## Übersetzungs-Workflow

### 1. Dokumentation auf Englisch schreiben

Alle Dokumentation sollte zuerst auf Englisch im Verzeichnis `docs/` geschrieben werden:

```bash
# Neue Dokumentationsseite anlegen
vim docs/user-guide/new-feature.md
```

### 2. Übersetzung starten

Sobald die englische Dokumentation fertig ist, führen Sie das Übersetzungsskript aus:

```bash
python scripts/translate.py --target-lang ko
```

### 3. Pull-Request prüfen

Das Skript erstellt eine Pull-Request mit den Übersetzungen. Prüfen Sie die PR:

1. Markdown-Formatierung wurde erhalten
2. Technische Begriffe sind korrekt behandelt
3. Code-Beispiele bleiben unverändert
4. Sprachspezifische Eigenheiten beachten

### Changelog-Politik

- Halten Sie die `CHANGELOG.md` im Stammverzeichnis auf Englisch.
- Eröffnen Sie keine Übersetzungs-PRs, deren Ziel es ist, die Releasehistorie im Stamm-Changelog in einer anderen Sprache neu zu schreiben.
- Falls eine Sprache eine Changelog-Seite benötigt, behandeln Sie `docs/<locale>/changelog.md` als Einstiegsseite oder Verweis auf den kanonischen englischen Changelog.

### 4. Freigeben und mergen (für Maintainer)

Sobald die Übersetzung verifiziert ist:

```bash
gh pr review <pr-number> --approve
gh pr merge <pr-number>
```

### 5. Dokumentation veröffentlichen

Die Dokumentations-Site wird automatisch mit den neuen Übersetzungen neu gebaut.

## Übersetzungs-Konfiguration

Bearbeiten Sie `scripts/translation_config.json`, um anzupassen:

```json
{
  "source_language": "en",
  "target_languages": [
    {
      "code": "ko",
      "name": "Korean",
      "native_name": "한국어",
      "enabled": true
    }
  ],
  "translation_settings": {
    "default_api_provider": "openai",
    "batch_size": 5,
    "preserve_formatting": true
  },
  "github_settings": {
    "create_pr_by_default": true,
    "branch_prefix": "translation"
  }
}
```

## Best Practices

### Für die Quelldokumentation

1. **Klare Sprache verwenden**: schreiben Sie klares, einfaches Englisch, das sich gut übersetzen lässt
2. **Einheitliche Terminologie**: verwenden Sie einheitliche Fachbegriffe
3. **Saubere Code-Blöcke**: geben Sie immer die Sprache im Code-Block an
4. **Linkprüfung**: stellen Sie sicher, dass alle internen Links relative Pfade nutzen

### Für die Überprüfung von Übersetzungen

1. **Fachbegriffe**: prüfen Sie, dass Fachbegriffe für die Zielsprache angemessen sind
2. **Kultureller Kontext**: prüfen Sie, ob Beispiele lokalisiert werden müssen
3. **Formatierung**: stellen Sie sicher, dass die gesamte Markdown-Formatierung erhalten bleibt
4. **Code-Integrität**: prüfen Sie, dass Code-Blöcke unverändert sind

## Fehlerbehebung

### API-Ratenbeschränkungen

Bei API-Ratenlimits in kleineren Chargen übersetzen:

```bash
# Translate only user guide
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/*.md
```

### Probleme mit der Übersetzungsqualität

Wenn die Übersetzungen schlecht sind:

1. Prüfen Sie, dass Ihr API-Schlüssel gültig ist
2. Versuchen Sie einen anderen KI-Anbieter
3. Zerlegen Sie komplexe Dokumente in kleinere Abschnitte
4. Manuell überprüfen und nachbearbeiten

### GitHub-PR schlägt fehl

Wenn die PR-Erstellung fehlschlägt:

```bash
# Translate without PR
python scripts/translate.py --target-lang ko --no-pr

# Manually create PR
git checkout -b translation/ko
git add docs/ko/
git commit -m "Add Korean translations"
git push -u origin translation/ko
gh pr create --title "Add Korean translations"
```

## Manuelle Übersetzung

Sie können auch manuell übersetzen:

1. Englische Datei in das Zielsprachenverzeichnis kopieren:
```bash
mkdir -p docs/ko/user-guide
cp docs/en/user-guide/installation.md docs/ko/user-guide/installation.md
```

2. Die Datei in Ihrem bevorzugten Editor bearbeiten
3. Committen und eine PR erstellen

## Sprachumschalter

Die Dokumentations-Site bietet einen Sprachumschalter in der oberen Navigation. Nutzer können:

1. Auf den Sprachumschalter klicken
2. Ihre bevorzugte Sprache wählen
3. Durch die übersetzte Dokumentation navigieren

## Neue Sprachen beitragen

Um eine neue Sprache hinzuzufügen:

1. `scripts/translation_config.json` bearbeiten:
```json
{
  "code": "pt",
  "name": "Portuguese",
  "native_name": "Português",
  "enabled": true
}
```

2. `mkdocs.yml` aktualisieren:
```yaml
- locale: pt
  name: Português
  build: true
```

3. Übersetzung starten:
```bash
python scripts/translate.py --target-lang pt
```

## Brauchen Sie Hilfe?

- **Issues**: Übersetzungsprobleme auf [GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues) melden
- **Discussions**: Fragen in [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions) stellen
- **Mitwirken**: siehe [CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)

## Qualitätsstandards für Übersetzungen

Alle Übersetzungen müssen diese Standards erfüllen:

- ✅ Die gesamte Markdown-Formatierung erhalten
- ✅ Code-Blöcke unverändert lassen
- ✅ Fachterminologie angemessen beibehalten
- ✅ Korrekte Grammatik und Rechtschreibung verwenden
- ✅ Sprachspezifische Konventionen befolgen
- ✅ Alle Links auf Funktionsfähigkeit testen

Vielen Dank, dass Sie zu den FastAPI-fastkit-Übersetzungen beitragen! 🌍

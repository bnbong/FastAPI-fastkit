# Guide de traduction

Ce guide explique comment contribuer aux traductions de la documentation de FastAPI-fastkit.

## Source de vérité et politique de traduction

> **L'anglais (`en`) est la référence canonique** pour la documentation de FastAPI-fastkit. Toutes les autres locales sont des cibles de traduction qui peuvent avoir un décalage d'une version complète ou de quelques pages par rapport à l'anglais.
>
> Si une page traduite contredit la page anglaise, **faites confiance à la page anglaise** jusqu'à ce que la traduction rattrape son retard. Les traductions sont livrées dans l'état d'avancement atteint par les contributeurs — une couverture partielle est normale et attendue.

Le pendant côté utilisateur de cette politique est la page [État des traductions](../reference/translation-status.md), qui liste la complétude réelle de chaque locale et la manière dont MkDocs rend les pages qui n'ont pas encore été traduites (en résumé : elles retombent sur l'anglais).

Le `CHANGELOG.md` à la racine du dépôt reste également en anglais comme historique de versions canonique. Si une locale expose une page `changelog.md`, cette page doit pointer vers le changelog canonique en anglais ou l'inclure, plutôt que de maintenir une copie traduite séparée, à moins que la politique du projet ne change plus tard.

Lorsque vous contribuez à une traduction, mettez aussi à jour le tableau de la page d'état pour que les utilisateurs sachent ce qui est disponible sans avoir à deviner depuis le sélecteur de langue.

## Vue d'ensemble

FastAPI-fastkit utilise un système de traduction automatisé propulsé par l'IA pour traduire la documentation dans plusieurs langues. Le système :

- Lit la documentation source en anglais
- Traduit le contenu via des API IA (OpenAI ou Anthropic)
- Enregistre les traductions dans des répertoires propres à chaque langue
- Crée des pull requests GitHub pour relecture

L'automatisation produit un point de départ ; une relecture humaine reste requise avant la fusion. Les traductions générées par IA doivent être marquées comme « brouillon » dans leurs PR et relues par un locuteur courant avant d'atterrir.

## Langues prises en charge

Voici les locales que le site de documentation **compile** actuellement. La configuration de cible de build seule **ne signifie pas** que les pages d'une locale sont traduites — consultez [État des traductions](../reference/translation-status.md) pour la complétude réelle par locale.

- 🇰🇷 Coréen (ko)
- 🇯🇵 Japonais (ja)
- 🇨🇳 Chinois (zh)
- 🇪🇸 Espagnol (es)
- 🇫🇷 Français (fr)
- 🇩🇪 Allemand (de)

## Prérequis

### 1. Installer les dépendances de traduction

```bash
# Install using pip
pip install openai anthropic

# Or using pdm
pdm install -G translation
```

### 2. Configurer les clés d'API

Vous avez besoin d'une clé d'API d'OpenAI ou d'Anthropic :

```bash
# For OpenAI
export TRANSLATION_API_KEY="sk-..."

# Or for Anthropic
export TRANSLATION_API_KEY="sk-ant-..."
```

### 3. Installer GitHub CLI (optionnel)

Pour la création automatique de PR :

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Authenticate
gh auth login
```

## Utilisation

### Avec les commandes Make (recommandé)

La façon la plus simple d'exécuter les traductions :

```bash
# Translate all docs to all languages
make translate

# Translate to specific language
make translate LANG=ko

# Specify API provider and model
make translate LANG=ko PROVIDER=openai MODEL=gpt-4
make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
```

### Avec le script directement

#### Traduire toute la documentation

Traduire toute la documentation dans toutes les langues prises en charge :

```bash
python scripts/translate.py --api-provider openai
```

### Traduire vers une langue spécifique

Traduire uniquement vers le coréen :

```bash
python scripts/translate.py --target-lang ko --api-provider openai
```

### Traduire des fichiers spécifiques

Traduire uniquement certains fichiers de documentation :

```bash
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/installation.md user-guide/quick-start.md \
  --api-provider openai
```

### Sauter la création de PR

Traduire sans créer de PR GitHub :

```bash
python scripts/translate.py --target-lang ko --no-pr --api-provider openai
```

### Utiliser Anthropic Claude

Utiliser Claude d'Anthropic au lieu d'OpenAI :

```bash
python scripts/translate.py \
  --target-lang ko \
  --api-provider anthropic \
  --api-key "sk-ant-..."
```

## Structure des répertoires

Après la traduction, la structure de la documentation ressemblera à ceci :

```
docs/
├── en/                    # English (original)
│   ├── index.md
│   ├── user-guide/
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── ...
│   ├── tutorial/
│   └── ...
├── ko/                    # Korean
│   ├── index.md
│   ├── user-guide/
│   └── ...
├── ja/                    # Japanese
├── zh/                    # Chinese
├── es/                    # Spanish
├── fr/                    # French
├── de/                    # German
├── css/                   # Shared assets
├── js/                    # Shared assets
└── img/                   # Shared assets
```

## Flux de travail de traduction

### 1. Rédiger la documentation en anglais

Toute la documentation doit d'abord être rédigée en anglais dans le répertoire `docs/` :

```bash
# Create new documentation
vim docs/user-guide/new-feature.md
```

### 2. Lancer la traduction

Une fois la documentation anglaise terminée, lancez le script de traduction :

```bash
python scripts/translate.py --target-lang ko
```

### 3. Relire la pull request

Le script créera une pull request avec les traductions. Relisez la PR :

1. Vérifiez que la mise en forme markdown est préservée
2. Vérifiez que les termes techniques sont correctement traités
3. Assurez-vous que les exemples de code restent inchangés
4. Vérifiez les particularités propres à la langue

### Politique sur le changelog

- Conservez le `CHANGELOG.md` à la racine du dépôt en anglais.
- N'ouvrez pas de PR de traduction dont l'objectif est de réécrire l'historique de versions dans une autre langue au sein du changelog racine.
- Si une locale a besoin d'une page de changelog, traitez `docs/<locale>/changelog.md` comme une enveloppe ou un point d'entrée vers le changelog canonique en anglais.

### 4. Approuver et fusionner (pour les mainteneurs)

Une fois la traduction vérifiée :

```bash
gh pr review <pr-number> --approve
gh pr merge <pr-number>
```

### 5. Déployer la documentation

Le site de documentation sera automatiquement reconstruit avec les nouvelles traductions.

## Configuration de la traduction

Modifiez `scripts/translation_config.json` pour personnaliser :

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

## Bonnes pratiques

### Pour la documentation source

1. **Utilisez un langage clair** : rédigez un anglais clair et simple qui se traduit bien
2. **Terminologie cohérente** : utilisez des termes techniques cohérents
3. **Blocs de code propres** : précisez toujours la langue des blocs de code
4. **Vérification des liens** : assurez-vous que tous les liens internes utilisent des chemins relatifs

### Pour la relecture des traductions

1. **Termes techniques** : vérifiez que les termes techniques sont appropriés à la langue cible
2. **Contexte culturel** : vérifiez si les exemples nécessitent une localisation
3. **Mise en forme** : assurez-vous que toute la mise en forme markdown est préservée
4. **Intégrité du code** : vérifiez que les blocs de code sont inchangés

## Dépannage

### Limites de débit de l'API

Si vous atteignez les limites de débit de l'API, traduisez par lots plus petits :

```bash
# Translate only user guide
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/*.md
```

### Problèmes de qualité de traduction

Si les traductions sont de mauvaise qualité :

1. Vérifiez que votre clé d'API est valide
2. Essayez un autre fournisseur d'IA
3. Découpez les documents complexes en sections plus petites
4. Relisez et éditez manuellement la traduction

### Échec de la PR GitHub

Si la création de PR échoue :

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

## Traduction manuelle

Vous pouvez aussi traduire manuellement :

1. Copiez le fichier anglais dans le répertoire de la langue cible :
```bash
mkdir -p docs/ko/user-guide
cp docs/en/user-guide/installation.md docs/ko/user-guide/installation.md
```

2. Éditez le fichier dans votre éditeur favori
3. Committez et créez une PR

## Changement de langue

Le site de documentation inclut un sélecteur de langue dans la navigation supérieure. Les utilisateurs peuvent :

1. Cliquer sur le sélecteur de langue
2. Choisir leur langue préférée
3. Naviguer dans la documentation traduite

## Contribuer de nouvelles langues

Pour ajouter une nouvelle langue :

1. Modifiez `scripts/translation_config.json` :
```json
{
  "code": "pt",
  "name": "Portuguese",
  "native_name": "Português",
  "enabled": true
}
```

2. Mettez à jour `mkdocs.yml` :
```yaml
- locale: pt
  name: Português
  build: true
```

3. Lancez la traduction :
```bash
python scripts/translate.py --target-lang pt
```

## Besoin d'aide ?

- **Issues** : signalez les problèmes de traduction sur [GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)
- **Discussions** : posez vos questions dans [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- **Contribution** : consultez [CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)

## Standards de qualité des traductions

Toutes les traductions doivent respecter ces standards :

- ✅ Préserver toute la mise en forme markdown
- ✅ Laisser les blocs de code inchangés
- ✅ Maintenir une terminologie technique appropriée
- ✅ Utiliser une grammaire et une orthographe correctes
- ✅ Suivre les conventions propres à la langue
- ✅ Vérifier que tous les liens fonctionnent

Merci de contribuer aux traductions de FastAPI-fastkit ! 🌍

# Configuration du développement

Un guide complet pour mettre en place un environnement de développement afin de contribuer à FastAPI-fastkit.

## Prérequis

Avant de commencer, assurez-vous d'avoir :

- **Python 3.12 ou supérieur** installé
- **Git** installé et configuré
- **Connaissances de base** de Python et de FastAPI
- **Un éditeur de texte ou IDE** (VS Code, PyCharm, etc.)

## Configuration rapide avec le Makefile

FastAPI-fastkit fournit un Makefile pour une configuration facile du développement :

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

Cette commande unique :

- Installe le paquet en mode éditable avec les dépendances de développement
- Met en place les hooks pre-commit
- Configure les outils de développement

!!! note

    Vous devez créer et activer un environnement virtuel avant de lancer cette commande.

## Configuration manuelle

Si vous préférez la configuration manuelle ou si le Makefile ne fonctionne pas sur votre système :

### 1. Cloner le dépôt

<div class="termy">

```console
$ git clone https://github.com/bnbong/FastAPI-fastkit.git
$ cd FastAPI-fastkit
```

</div>

### 2. Créer l'environnement virtuel

<div class="termy">

```console
$ python -m venv .venv
$ source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

</div>

### 3. Installer les dépendances

<div class="termy">

```console
# Installer le paquet en mode éditable avec les dépendances de développement
$ pip install -e ".[dev]"

# Ou installer depuis les fichiers requirements
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt
```

</div>

### 4. Configurer les hooks pre-commit

<div class="termy">

```console
$ pre-commit install
pre-commit installed at .git/hooks/pre-commit
```

</div>

### 5. Vérifier l'installation

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

## Outils de développement

L'environnement de développement inclut plusieurs outils pour maintenir la qualité du code :

### Commandes en une ligne

avec le Makefile :

```console
$ make format lint
Running isort...
Running black...
Running mypy...
✅ All checks passed!
```

avec les scripts fournis :

```console
$ ./scripts/format.sh
$ ./scripts/lint.sh
```

### Mise en forme du code

**Black** — formateur de code :

<div class="termy">

```console
$ black src/ tests/
reformatted src/main.py
reformatted tests/test_cli.py
All done! ✨ 🍰 ✨
```

</div>

**isort** — tri des imports :

<div class="termy">

```console
$ isort src/ tests/
Fixing import order in src/main.py
```

</div>

### Linting du code

**mypy** — vérification de types :

<div class="termy">

```console
$ mypy src/
Success: no issues found in 12 source files
```

</div>

## Commandes Make disponibles

Le Makefile du projet fournit des commandes pratiques pour les tâches courantes de développement :

### Commandes de configuration

| Commande | Description |
|---------|-------------|
| `make install` | Installer le paquet en mode production |
| `make install-dev` | Installer le paquet avec les dépendances de développement |
| `make install-test` | Installer le paquet pour les tests (désinstaller + réinstaller) |
| `make uninstall` | Désinstaller le paquet |
| `make clean` | Nettoyer les artefacts de build et les fichiers de cache |

### Commandes de qualité de code

| Commande | Description |
|---------|-------------|
| `make format` | Mettre en forme le code avec black et isort |
| `make format-check` | Vérifier la mise en forme sans modifier |
| `make lint` | Lancer toutes les vérifications de linting (isort, black, mypy) |

### Commandes de tests

| Commande | Description |
|---------|-------------|
| `make test` | Lancer tous les tests |
| `make test-verbose` | Lancer les tests avec une sortie détaillée |
| `make test-coverage` | Lancer les tests avec un rapport de couverture |
| `make coverage-report` | Générer un rapport de couverture détaillé (FORMAT=html/xml/json/all) |

### Commandes d'inspection des modèles

| Commande | Description |
|---------|-------------|
| `make inspect-templates` | Lancer l'inspection sur tous les modèles |
| `make inspect-templates-verbose` | Lancer l'inspection avec une sortie détaillée |
| `make inspect-template` | Inspecter un ou plusieurs modèles précis (paramètre TEMPLATES) |

### Commandes de documentation

| Commande | Description |
|---------|-------------|
| `make serve-docs` | Servir la documentation en local |
| `make build-docs` | Construire la documentation |

### Commandes de traduction

| Commande | Description |
|---------|-----------|
| `make translate` | Traduire la documentation (paramètres LANG, PROVIDER, MODEL) |

### Exemples

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

## Structure du projet

Comprendre la structure du projet est crucial pour le développement :

```bash
FastAPI-fastkit/
├── src/
│   ├── fastapi_fastkit/
│   │   ├── __main__.py                      # Point d'entrée de l'application
│   │   ├── backend/
│   │   │   ├── inspector.py                 # FastAPI-fastkit template inspector
│   │   │   ├── interactive/
│   │   │   │   ├── config_builder.py        # Construction de la configuration pour le mode interactif
│   │   │   │   ├── prompts.py               # Invites du mode interactif
│   │   │   │   ├── selectors.py             # Logique de sélection pour le mode interactif
│   │   │   │   └── validators.py            # Validation des saisies utilisateur en mode interactif
│   │   │   ├── main.py                      # Point d'entrée de la logique backend
│   │   │   ├── package_managers/
│   │   │   │   ├── base.py                  # Classe de base des gestionnaires de paquets
│   │   │   │   ├── factory.py               # Fabrique des gestionnaires de paquets
│   │   │   │   ├── pdm_manager.py           # Gestionnaire de paquets PDM
│   │   │   │   ├── pip_manager.py           # Gestionnaire de paquets pip
│   │   │   │   ├── poetry_manager.py        # Gestionnaire de paquets Poetry
│   │   │   │   └── uv_manager.py            # Gestionnaire de paquets uv
│   │   │   ├── project_builder/
│   │   │   │   ├── config_generator.py      # Générateur de configuration pour le project builder
│   │   │   │   └── dependency_collector.py  # Collecteur de dépendances pour le project builder
│   │   │   └── transducer.py                # Transducteur pour le project builder
│   │   ├── cli.py                           # Point d'entrée principal du CLI FastAPI-fastkit
│   │   ├── core/
│   │   │   ├── exceptions.py                # Exception handling
│   │   │   └── settings.py                  # Settings configuration
│   │   ├── fastapi_project_template/
│   │   │   ├── PROJECT_README_TEMPLATE.md   # README de base des projets de template fastkit
│   │   │   ├── README.md                    # README des templates fastkit
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
│   │       ├── logging.py                   # Configuration du logging
│   │       └── main.py                      # Point d'entrée principal de FastAPI-fastkit
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

### Répertoires clés

- **`src/fastapi_fastkit/`** — code source du paquet principal
    - **`cli.py`** — point d'entrée principal du CLI
    - **`backend/`** — logique backend centrale
        - **`inspector.py`** — inspecteur de modèles
        - **`interactive/`** — composants du mode interactif (invites, sélecteurs, validateurs)
        - **`package_managers/`** — implémentations des gestionnaires de paquets (pip, uv, pdm, poetry)
        - **`project_builder/`** — utilitaires de construction de projet
        - **`transducer.py`** — transducer de modèle
    - **`core/`** — configuration centrale et exceptions
    - **`fastapi_project_template/`** — modèles de projet (fastapi-default, fastapi-async-crud, etc.)
    - **`utils/`** — fonctions utilitaires partagées
- **`tests/`** — suite de tests
    - **`test_backends/`** — tests propres au backend
    - **`test_cli_operations/`** — tests d'opérations CLI
    - **`test_templates/`** — tests du système de modèles
- **`docs/`** — documentation (MkDocs)
    - guides utilisateur, tutoriels et référence d'API

## Flux de travail de développement

### 1. Créer une branche de fonctionnalité

<div class="termy">

```console
$ git checkout -b feature/add-new-template
Switched to a new branch 'feature/add-new-template'
```

</div>

### 2. Apporter des changements

Modifiez du code, ajoutez des fonctionnalités, corrigez des bogues…

### 3. Lancer les tests et les vérifications

<div class="termy">

```console
$ make dev-check
Running all quality checks...
Running all tests...
✅ All tests passed!
```

</div>

### 4. Committer les changements

Les hooks pre-commit s'exécuteront automatiquement :

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

### 5. Pousser et créer une pull request

<div class="termy">

```console
$ git push origin feature/add-new-template
$ gh pr create --title "Add new FastAPI template with authentication"
```

</div>

## Tests

### Lancer les tests

**Tous les tests :**

<div class="termy">

```console
$ make test
# or
$ python -m pytest
```

</div>

**Fichier de test précis :**

<div class="termy">

```console
$ python -m pytest tests/test_cli.py -v
```

</div>

**Avec couverture :**

<div class="termy">

```console
$ make test-coverage
# or
$ python -m pytest --cov=src --cov-report=html
```

</div>

### Écrire des tests

Lorsque vous ajoutez de nouvelles fonctionnalités, incluez toujours des tests :

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

### Catégories de tests

**Tests unitaires** — tester des fonctions et des classes individuelles :

```python
def test_validate_project_name():
    assert validate_project_name("valid-name") is True
    assert validate_project_name("invalid name!") is False
```

**Tests d'intégration** — tester les interactions entre commandes :

```python
def test_init_command_creates_project(tmp_path):
    result = runner.invoke(cli, ['init'], input='test-project\n...')
    assert result.exit_code == 0
    assert (tmp_path / "test-project").exists()
```

**Tests de bout en bout** — tester des flux complets :

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

## Documentation

### Servir la documentation en local

<div class="termy">

```console
$ make serve-docs
INFO     -  Building documentation...
INFO     -  Cleaning site directory
INFO     -  Documentation built in 0.43 seconds
INFO     -  [14:30:00] Serving on http://127.0.0.1:8000/
```

</div>

### Construire la documentation

<div class="termy">

```console
$ make build-docs
INFO     -  Building documentation...
INFO     -  Documentation built in 0.43 seconds
```

</div>

### Rédiger la documentation

La documentation est rédigée en Markdown et construite avec MkDocs. Voici un exemple de structure :

**Modèle de guide de fonctionnalité :**

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

Pour une référence détaillée sur l'utilisation de `mkdocs-material`, consultez la [documentation mkdocs-material](https://squidfunk.github.io/mkdocs-material/reference/admonitions/).

## Directives de style de code

### Style de code Python

Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/) avec ces règles spécifiques :

- **Longueur de ligne** : 88 caractères (par défaut de Black)
- **Imports** : organisés avec isort
- **Annotations de type** : requises pour toutes les fonctions publiques
- **Docstrings** : style Google pour toutes les API publiques

### Exemple

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

## Variables d'environnement

Pour le développement, vous pouvez définir ces variables d'environnement :

| Variable | Description | Défaut |
|----------|-------------|---------|
| `FASTKIT_DEBUG` | Activer la journalisation de débogage | `False` |
| `FASTKIT_DEV_MODE` | Activer les fonctionnalités de développement | `False` |
| `FASTKIT_TEMPLATE_DIR` | Répertoire de modèles personnalisés | Modèles intégrés |
| `FASTKIT_CONFIG_DIR` | Répertoire de configuration | `~/.fastkit` |
| `TRANSLATION_API_KEY` | Clé d'API de traduction (mettez un PAT GitHub si vous utilisez le [fournisseur de modèles IA Github](https://github.com/marketplace/models/azure-openai)) | `None` |

<div class="termy">

```console
$ export FASTKIT_DEBUG=true
$ export FASTKIT_DEV_MODE=true
$ fastkit init
DEBUG: Loading configuration from /home/user/.fastkit/
DEBUG: Available templates: ['fastapi-default', ...]
```

</div>

Pour les autres paramètres de variables d'environnement, référez-vous au module [@settings.py](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/core/settings.py).

## Dépannage

### Problèmes courants

**1. Les hooks pre-commit échouent :**

<div class="termy">

```console
$ git commit -m "Fix bug"
black....................................................................Failed
hookid: black

Files were modified by this hook. Additional output:

would reformat src/cli.py
```

</div>

**Solution :** lancez les formateurs et committez à nouveau :

<div class="termy">

```console
$ make format
$ git add .
$ git commit -m "Fix bug"
```

</div>

**2. Les tests échouent sur différentes versions de Python :**

**Solution :** utilisez tox pour tester plusieurs versions de Python :

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

**3. Erreurs d'import en développement :**

**Solution :** installez le paquet en mode éditable :
<div class="termy">

```console
$ pip install -e .
```

</div>

### Obtenir de l'aide

- **[GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)** : signaler des bogues et demander des fonctionnalités
- **[GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)** : poser des questions et partager des idées
- **Documentation** : consultez le [Guide de l'utilisateur](../user-guide/installation.md)

## Directives de contribution

### Avant de soumettre une PR

1. **Lancez toutes les vérifications :** `make dev-check`
2. **Mettez à jour la documentation** si nécessaire
3. **Ajoutez des tests** pour les nouvelles fonctionnalités
4. **Suivez les conventions de messages de commit**

### Format de message de commit

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**Types :**

- `feat` : nouvelle fonctionnalité
- `fix` : correction de bogue
- `docs` : changements de documentation
- `style` : changements de style de code
- `refactor` : refactoring de code
- `test` : ajout / modification de tests
- `chore` : tâches de maintenance

**Exemples :**

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

## Processus de release

Pour les mainteneurs, le processus de release est :

1. **Mettre à jour la version** dans `setup.py` et `__init__.py`
2. **Mettre à jour CHANGELOG.md**
3. **Créer une PR de release**
4. **Tagger la release** après la fusion
5. **GitHub Actions** construit et publie automatiquement

<div class="termy">

```console
$ git tag v1.2.0
$ git push origin v1.2.0
```

</div>

## Étapes suivantes

Maintenant que votre environnement de développement est en place :

1. **[Explorez le code](https://github.com/bnbong/FastAPI-fastkit/tree/main/src/fastapi_fastkit)** pour comprendre l'architecture
2. **Lancez la suite de tests** pour vérifier que tout fonctionne
3. **Choisissez une [issue](https://github.com/bnbong/FastAPI-fastkit/issues)** sur GitHub à traiter
4. **Rejoignez les [discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)** pour échanger avec les autres contributeurs

Bon développement ! 🚀

!!! tip "Astuces de développement"
    - Utilisez `make dev-check` avant de committer
    - Écrivez les tests d'abord (approche TDD)
    - Gardez les commits petits et ciblés
    - Mettez à jour la documentation avec les nouvelles fonctionnalités

# Guide de création de modèles FastAPI

Un guide complet pour ajouter de nouveaux modèles de projet FastAPI à FastAPI-fastkit.

## 🎯 Vue d'ensemble

L'ajout d'un nouveau modèle suit un processus en 5 étapes :

1. **📋 Planification et conception** — définir l'objectif et la structure du modèle
2. **🏗️ Implémentation du modèle** — créer la structure et les fichiers requis
3. **🔍 Validation locale** — valider le modèle avec l'inspecteur
4. **📚 Documentation** — rédiger le README et le guide d'utilisation
5. **🚀 Soumission et relecture** — créer la PR et relecture par la communauté

## 📋 Étape 1 : Planification et conception

### Définir l'objectif du modèle

Avant de créer un nouveau modèle, répondez à ces questions :

- **Quelle est la valeur unique de ce modèle ?**
- **En quoi se distingue-t-il des modèles existants ?**
- **Quel groupe d'utilisateurs est visé ?**
- **Quelle pile technique sera incluse ?**

### Convention de nommage des modèles

```
fastapi-{purpose}-{stack}
```

Exemples :

- `fastapi-microservice` (modèle microservice)
- `fastapi-graphql` (modèle d'intégration GraphQL)
- `fastapi-auth-jwt` (modèle d'authentification JWT)

### Planification de la pile technique

Définissez à l'avance les principales technologies à inclure :

```yaml
# Example: fastapi-microservice template
core_dependencies:
  - fastapi
  - uvicorn
  - pydantic
  - pydantic-settings

additional_features:
  - sqlalchemy (ORM)
  - alembic (migrations)
  - redis (caching)
  - celery (background tasks)
  - pytest (testing)

development_tools:
  - black (code formatting)
  - isort (import sorting)
  - mypy (vérification des types)
  - pre-commit (hooks Git)
```

## 🏗️ Étape 2 : Implémentation du modèle

### Structure de répertoires requise

```
fastapi-{template-name}/
├── src/                          # Code source de l'application
│   ├── main.py-tpl              # ✅ Point d'entrée FastAPI (obligatoire)
│   ├── __init__.py-tpl
│   ├── api/                     # Routeurs API
│   │   ├── __init__.py-tpl
│   │   ├── api.py-tpl           # Routeur API principal
│   │   └── routes/              # Routes individuelles
│   │       ├── __init__.py-tpl
│   │       └── items.py-tpl     # Exemple de route
│   ├── core/                    # Configuration centrale
│   │   ├── __init__.py-tpl
│   │   └── config.py-tpl        # Gestion des paramètres
│   ├── crud/                    # Logique CRUD
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   ├── schemas/                 # Modèles Pydantic
│   │   ├── __init__.py-tpl
│   │   └── items.py-tpl
│   └── utils/                   # Fonctions utilitaires
│       ├── __init__.py-tpl
│       └── helpers.py-tpl
├── tests/                       # ✅ Tests (obligatoires)
│   ├── __init__.py-tpl
│   ├── conftest.py-tpl         # Configuration pytest
│   └── test_items.py-tpl       # Exemples de tests
├── scripts/                     # Scripts
│   ├── format.sh-tpl           # Formatage du code
│   ├── lint.sh-tpl             # Vérifications de style
│   ├── run-server.sh-tpl       # Lancement du serveur
│   └── test.sh-tpl             # Exécution des tests
├── pyproject.toml-tpl           # ✅ Métadonnées principales (PEP 621, requis)
├── requirements.txt-tpl         # 🟡 Optionnel si pyproject déclare déjà les dépendances
├── setup.cfg-tpl               # Configuration des outils de développement
├── README.md-tpl               # ✅ Documentation du projet (obligatoire)
├── .env-tpl                    # Modèle de variables d'environnement
└── .gitignore-tpl              # Fichier d'exclusion Git
```

**Fichiers minimaux requis.** Un modèle doit fournir :

- un répertoire `tests/`
- un fichier `README.md-tpl`
- `pyproject.toml-tpl` (PEP 621)
- une déclaration de `fastapi` comme dépendance dans `pyproject.toml-tpl` `[project].dependencies` ou dans `requirements.txt-tpl`

`requirements.txt-tpl` n'est pas requis quand `pyproject.toml-tpl` déclare `[project].dependencies` — mais lorsqu'un modèle fournit les deux, ils doivent concorder : l'inspection échoue en cas de divergence des dépendances entre eux.

**Les nouveaux modèles sont pyproject-first et ne doivent pas fournir de `setup.py-tpl`.** Aucun modèle livré n'en contient depuis v1.4.0. L'inspection accepte toujours ce fichier pour que les modèles hors dépôt continuent de fonctionner, mais il s'agit d'un chemin legacy.

**Ciblez Python 3.12 de manière cohérente** : `requires-python = ">=3.12"`, black `target-version = ["py312"]`, mypy `python_version = "3.12"`, et `python:3.12-slim` pour toute image Docker de base. L'inspection vérifie que ces trois épinglages concordent.

**Ne déclarez jamais `FastAPI-fastkit` comme dépendance d'exécution** d'un projet généré. Le CLI est un outil de développement ; la liste des dépendances d'un modèle ne doit contenir que ce que l'application générée importe elle-même.

### Guide d'écriture des fichiers

#### 1. Écrire main.py-tpl

```python
"""
Point d'entrée de l'application FastAPI

Ce fichier correspond à l'application principale du projet <project_name> créé avec FastAPI-fastkit.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.api import api_router
from core.config import settings

# Create FastAPI app (required for inspector validation)
app = FastAPI(
    title="<project_name>",
    description="Project created with FastAPI-fastkit",
    version="1.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Hello from <project_name>!"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 2. Écrire pyproject.toml-tpl (préféré)

Les modèles modernes doivent déclarer leurs métadonnées et leurs dépendances avec un `pyproject.toml-tpl` PEP 621. Au minimum, le fichier doit exposer une section `[project]` avec `name`, `version`, une `description` et une liste `dependencies` qui inclut `fastapi`. Les modèles doivent aussi porter deux marqueurs d'identité FastAPI-fastkit afin que `is_fastkit_project()` puisse distinguer les projets générés des projets FastAPI non liés dans l'espace de travail de l'utilisateur :

- préfixe `[FastAPI-fastkit templated]` dans `description`
- une table dédiée `[tool.fastapi-fastkit]` avec `managed = true`

La détection accepte n'importe lequel des deux marqueurs (la comparaison est insensible à la casse). L'injection de métadonnées ajoutera les deux au moment de la génération du projet si un modèle les omet, mais les auteurs devraient les inclure explicitement.

```toml
[project]
name = "<project_name>"
version = "0.1.0"
description = "[FastAPI-fastkit templated] <description>"
authors = [
    {name = "<author>", email = "<author_email>"},
]
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.7.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "httpx>=0.28.0",
]

[tool.fastapi-fastkit]
managed = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

#### 3. Écrire requirements.txt-tpl (optionnel)

Optionnel quand `pyproject.toml-tpl` déclare `[project].dependencies`. Reste utile pour les modèles qui préfèrent des flux de travail uniquement `pip`.

```txt
# FastAPI core dependencies (required)
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Data validation
pydantic==2.5.0
pydantic-settings==2.1.0

# Environment variable management
python-dotenv==1.0.0

# Database (if needed)
sqlalchemy==2.0.23
alembic==1.13.0

# Development tools
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Code quality
black==23.11.0
isort==5.12.0
mypy==1.7.1
```

#### 4. Ancres de routes

Les modèles qui fournissent un `main.py-tpl` ou un module d'agrégation d'API doivent marquer l'endroit où `fastkit addroute` insère du code :

```python
from src.app.api import health

# fastkit:imports

api_router = APIRouter()
api_router.include_router(health.router)

# fastkit:routes
```

Sans ces ancres, `addroute` se rabat sur une insertion fondée sur l'AST qui repère elle-même le bloc d'imports et les enregistrements de routeurs — un modèle qui en est dépourvu fonctionne donc toujours, mais le résultat est moins prévisible. Conservez ces commentaires lorsque vous modifiez ces fichiers.

#### 5. Écrire les fichiers de test

```python
# tests/test_items.py-tpl
"""
Items API test module
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    """Tester le point de contrôle de santé"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_item():
    """Test item creation"""
    item_data = {
        "name": "Test Item",
        "description": "Test Description"
    }
    response = client.post("/api/v1/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == item_data["name"]
    assert data["description"] == item_data["description"]

def test_read_items():
    """Test reading items list"""
    response = client.get("/api/v1/items/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 🔍 Étape 3 : Validation locale

### Exécuter les scripts de validation automatisés

Une fois votre nouveau modèle prêt, validez-le avec ces commandes :

```bash
# Validate all templates
make inspect-templates

# Validate specific template only
make inspect-template TEMPLATES="fastapi-your-template"

# Validate with verbose output
python scripts/inspect-templates.py --templates "fastapi-your-template" --verbose

# Fast local loop: no network, no server boot
python scripts/inspect-templates.py --templates "fastapi-your-template" \
    --offline --no-smoke

# Full check before opening a PR (adds mypy over the generated project)
python scripts/inspect-templates.py --templates "fastapi-your-template" --mypy
```

`--offline` ignore les vérifications de fraîcheur des dépendances sur PyPI, `--no-smoke` ignore le démarrage du projet généré (l'étape la plus lente) et `--mypy` vérifie les types du projet généré. Consultez [Assurance qualité des modèles](../reference/template-quality-assurance.md) pour savoir ce que fait chaque vérification.

!!! note

    Lorsque vous soumettez une PR, le workflow **Template PR Inspection** se déclenche automatiquement et valide vos changements de modèle. Vous recevrez le retour directement sur votre PR.

### Liste de vérification

L'inspecteur valide automatiquement les éléments suivants :

#### ✅ Validation de la structure des fichiers

- [ ] Le répertoire `tests/` existe
- [ ] Le fichier `README.md-tpl` existe
- [ ] `pyproject.toml-tpl` existe (pas de `setup.py-tpl` dans les nouveaux modèles)

#### ✅ Validation des extensions de fichiers

- [ ] Tous les fichiers Python utilisent l'extension `.py-tpl`
- [ ] Aucun fichier en `.py` n'existe

#### ✅ Validation des dépendances

- [ ] `fastapi` est déclaré dans au moins l'un de :
    - [ ] `pyproject.toml-tpl` sous `[project].dependencies` (préféré)
    - [ ] `requirements.txt-tpl`
- [ ] `requirements.txt-tpl` et `[project].dependencies` ne divergent pas
- [ ] `FastAPI-fastkit` n'est **pas** une dépendance d'exécution

#### ✅ Validation de l'implémentation FastAPI

- [ ] L'import `FastAPI` existe dans `main.py-tpl`
- [ ] La création d'application du type `app = FastAPI()` existe dans `main.py-tpl`

#### ✅ Validation de l'exécution des tests

- [ ] La création de l'environnement virtuel réussit
- [ ] L'installation des dépendances réussit
- [ ] Tous les tests pytest passent

#### ✅ Test smoke

- [ ] Le projet généré démarre sous uvicorn
- [ ] `/docs` répond
- [ ] `/health` répond

La cible uvicorn est résolue à partir de `[tool.fastapi-fastkit].app_module` dans le `pyproject.toml` généré, puis de `app_module` dans `template-config.yml`, puis des emplacements conventionnels de `main.py`.

#### ✅ Cohérence de la configuration

- [ ] `requires-python`, black `target-version` et mypy `python_version` indiquent tous Python 3.12
- [ ] Aucune divergence de dépendances entre `requirements.txt-tpl` et `[project].dependencies`
- [ ] Aucune auto-dépendance à `FastAPI-fastkit`

#### ✅ Résidus d'emplacements

- [ ] Aucun `<placeholder>` ne subsiste après la génération du projet

#### ✅ Tests automatisés des modèles

FastAPI-fastkit inclut des **tests automatisés des modèles** qui exécutent des tests complets pour tous les modèles :

**Couverture des tests :**

- ✅ Processus de création de modèle
- ✅ Injection des métadonnées de projet
- ✅ Mise en place de l'environnement virtuel
- ✅ Installation des dépendances (tous les gestionnaires de paquets)
- ✅ Validation de la structure basique du projet
- ✅ Identification du projet FastAPI

**Exécution des tests :**
```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Test specific template
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v
```

**Découverte des tests de modèle :**
Les nouveaux modèles sont **automatiquement découverts** et testés sans configuration manuelle :

1. ✅ **Zéro configuration** : ajoutez un modèle → tests automatiques
2. ✅ **Tests cohérents** : mêmes standards de qualité pour tous les modèles
3. ✅ **Gestionnaires de paquets multiples** : tests avec UV, PDM, Poetry et PIP
4. ✅ **Validation complète** : vérifications de structure, métadonnées et fonctionnalités

**Ce que cela signifie pour vous :**

- 🚀 **Aucun fichier de test supplémentaire dans la source principale de `FastAPI-fastkit`** : votre modèle est testé automatiquement
- ⚡ **Développement plus rapide** : concentrez-vous sur le contenu du modèle, pas sur la configuration des tests
- 🛡️ **Assurance qualité** : tests cohérents pour tous les modèles
- 🔄 **Intégration CI/CD** : tests automatiques dans les pull requests

**Tests manuels toujours requis :**

- 🧪 **Fonctionnalités propres au modèle** : logique métier et fonctionnalités personnalisées
- 🔧 **Tests d'intégration** : services externes et flux de travail complexes
- 📱 **Scénarios de bout en bout** : flux utilisateurs complets

**Bonnes pratiques de test :**
```console
# 1. Test your template locally
$ fastkit startdemo your-template-name

# 2. Run automated tests
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[your-template-name] -v

# 3. Test with different package managers
$ fastkit startdemo your-template-name --package-manager poetry
$ fastkit startdemo your-template-name --package-manager pdm
$ fastkit startdemo your-template-name --package-manager uv
```

### Liste de vérification manuelle

En complément de la validation automatisée, vérifiez manuellement les éléments suivants :

#### 🔧 Qualité du code

- [ ] Le code respecte le guide de style PEP 8
- [ ] Utilisation appropriée des annotations de type
- [ ] Noms de variables et de fonctions explicites
- [ ] Commentaires et docstrings appropriés

#### 🏗️ Architecture

- [ ] Séparation des préoccupations (séparation API, logique métier, accès aux données)
- [ ] Conception de composants réutilisables
- [ ] Structure évolutive
- [ ] Bonnes pratiques de sécurité appliquées

#### 📚 Documentation

- [ ] README.md-tpl respecte le format de PROJECT_README_TEMPLATE.md
- [ ] Méthodes d'installation et d'exécution précisées
- [ ] Documentation de l'API (OpenAPI/Swagger)
- [ ] Explication des variables d'environnement

## 📚 Étape 4 : Documentation

### Rédiger README.md-tpl

Rédigez en suivant le guide [PROJECT_README_TEMPLATE.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/src/fastapi_fastkit/fastapi_project_template/PROJECT_README_TEMPLATE.md).

### Rédiger la documentation de description du modèle

Ajoutez une description de votre nouveau modèle à `src/fastapi_fastkit/fastapi_project_template/README.md` :

```markdown
## fastapi-your-template

Write a brief description and use cases for your new template here.

### Features:
- Feature 1
- Feature 2
- Feature 3

### Use Cases:
- Use case 1
- Use case 2
```

## 🚀 Étape 5 : Soumission et relecture

### Liste de vérification avant création de la PR

- [ ] Toute la validation automatisée est passée (`make inspect-templates`)
- [ ] La mise en forme du code est terminée (`make format`)
- [ ] Les contrôles de linting sont passés (`make lint`)
- [ ] Tous les tests sont passés (`make test`)
- [ ] La documentation est complète
- [ ] Les directives de CONTRIBUTING.md sont respectées

### Titre et description de la PR

```
[TEMPLATE] Add fastapi-{template-name} template

## Overview
Adds a new {purpose} template.

## Key Features
- Feature 1
- Feature 2
- Feature 3

## Validation Results
- [ ] Inspector validation passed
- [ ] All tests passed
- [ ] Documentation completed

## Usage Example
\```bash
fastkit startdemo
# Select template: fastapi-{template-name}
\```

## Related Issues
Closes #issue-number
```

### Processus de relecture

1. **Validation automatisée** : GitHub Actions valide automatiquement le modèle
    - **Template PR Inspection** : exécute `inspect-changed-templates.py` sur les PR qui modifient des modèles
    - **Inspection hebdomadaire** : validation complète des modèles chaque mercredi
2. **Relecture de code** : les mainteneurs et la communauté relisent le code
3. **Tests** : le modèle est testé dans divers environnements
4. **Relecture de la documentation** : vérification de l'exactitude et de la complétude de la documentation
5. **Approbation et fusion** : fusion dans la branche main lorsque toutes les exigences sont satisfaites

!!! note

    Vous recevrez des commentaires automatiques de PR avec les résultats de validation. Vérifiez-les avant de demander une relecture !

## 🎯 Bonnes pratiques

### Considérations de sécurité

- Gérez les informations sensibles avec des variables d'environnement
- Configuration CORS correcte
- Validation des données d'entrée
- Prévention des injections SQL

### Optimisation des performances

- Tirer parti du traitement asynchrone
- Optimiser les requêtes de base de données
- Stratégies de mise en cache appropriées
- Paramètres de compression des réponses

### Maintenabilité

- Structure de code claire
- Couverture de tests complète
- Documentation détaillée
- Mise en place de journalisation et de supervision

## 🆘 Besoin d'aide ?

- 📖 [Guide de configuration du développement](development-setup.md)
- 📋 [Directives de code](code-guidelines.md)
- 💬 [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- 📧 [Contacter le mainteneur](mailto:bbbong9@gmail.com)

Ajouter un nouveau modèle est une superbe contribution à la communauté FastAPI-fastkit. Vos idées et vos efforts seront d'une grande aide pour d'autres développeurs ! 🚀

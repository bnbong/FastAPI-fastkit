# Assurance qualité des modèles

FastAPI-fastkit fournit une validation automatisée et complète des modèles pour s'assurer qu'ils maintiennent une qualité élevée et restent fonctionnels dans différents environnements et avec différents gestionnaires de paquets.

## Assurance qualité multi-couches

FastAPI-fastkit s'appuie sur **deux systèmes d'assurance qualité complémentaires** :

### 1. Inspection statique des modèles
**Validation automatisée hebdomadaire de la structure et de la syntaxe des modèles**

### 2. Tests dynamiques des modèles
**Tests complets de bout en bout avec création de projets réels**

## Inspection hebdomadaire automatisée

Chaque mercredi à minuit (UTC), notre workflow GitHub Actions inspecte automatiquement tous les modèles FastAPI pour s'assurer qu'ils respectent les standards de qualité :

- ✅ **Validation de la structure des fichiers** — vérifie que tous les fichiers et répertoires requis sont présents
- ✅ **Vérification des extensions de fichiers** — valide que les fichiers de modèle utilisent les bonnes extensions `.py-tpl`
- ✅ **Vérification des dépendances** — confirme que FastAPI et les dépendances requises sont correctement définies
- ✅ **Implémentation FastAPI** — vérifie que les modèles contiennent une initialisation correcte de l'application FastAPI
- ✅ **Exécution des tests** — exécute les tests du modèle pour s'assurer du bon fonctionnement
- ✅ **Test smoke** — démarre le projet généré avec uvicorn et sonde sa surface HTTP
- ✅ **Cohérence de la configuration** — épinglages de version Python, divergence des dépendances, auto-dépendance
- ✅ **Résidus d'emplacements** — aucun `<placeholder>` ne subsiste après la génération du projet
- ✅ **Fraîcheur des dépendances** — signale les épinglages en retard sur leur dernière version publiée sur PyPI

## Ce que fait chaque vérification

L'inspection génère un **véritable projet** à partir du modèle — copie, conversion des fichiers `-tpl`, injection des métadonnées — puis exécute chaque vérification sur ce projet généré, et non sur la source du modèle. Une vérification qui ne lit que le modèle ne peut pas détecter un emplacement que la génération n'a pas réussi à substituer.

### Test smoke

Le projet généré est démarré avec uvicorn sur un port libre, et l'inspecteur interroge le serveur jusqu'à ce qu'il réponde ou que le délai expire. Une fois le serveur opérationnel, `/docs` et `/health` sont appelés et leurs codes de statut vérifiés. Le processus serveur est ensuite arrêté, avec escalade vers `SIGKILL` s'il ne s'arrête pas.

La cible uvicorn est résolue dans l'ordre suivant : `[tool.fastapi-fastkit].app_module` dans le `pyproject.toml` généré, puis `app_module` dans le `template-config.yml` du modèle, puis les emplacements conventionnels de `main.py`. C'est le même contrat que celui utilisé par `fastkit runserver` : un modèle dont le test smoke démarre est donc un modèle dont le projet généré s'exécute.

C'est la vérification qui détecte ce que l'analyse statique ne peut pas voir : un import qui ne se résout qu'à l'exécution, un `lifespan` qui lève une exception, un champ de configuration sans valeur par défaut.

### Cohérence de la configuration

Trois points sont validés par rapport au `pyproject.toml-tpl` du modèle :

- **Les épinglages de version Python concordent et ciblent 3.12** — `requires-python`, le `target-version` de black et le `python_version` de mypy. Un modèle qui formate en `py311` tout en déclarant `>=3.12` est un bug qui attend de tomber sur un contributeur.
- **Aucune divergence des dépendances** — les paquets déclarés dans `requirements.txt-tpl` et dans `[project].dependencies` ne doivent pas se contredire. Les modèles fournissent les deux fichiers pour la compatibilité avec les gestionnaires de paquets, et deux listes finissent toujours par diverger si rien ne les vérifie.
- **Aucune auto-dépendance** — un projet généré ne doit pas déclarer `FastAPI-fastkit` comme dépendance d'exécution. Le CLI est un outil de développement ; l'embarquer dans chaque application générée ferait entrer tout l'arbre de dépendances de fastkit dans des projets sans rapport.

### Résidus d'emplacements

Chaque `<project_name>`, `<description>` et consorts doit être substitué pendant la génération. Tout `<placeholder>` encore présent dans le projet généré est une erreur — cela signifie que l'injection des métadonnées ne connaît pas ce fichier, et que l'utilisateur le recevrait tel quel.

### Fraîcheur des dépendances

Les versions épinglées sont comparées à la dernière version publiée sur PyPI et signalées comme avertissements, jamais comme erreurs — un modèle en retard d'une version mineure est une information, pas un échec. C'est la seule vérification qui accède au réseau, et `--offline` l'ignore.

## Système de tests automatisés des modèles

FastAPI-fastkit inclut un **système de tests automatisés révolutionnaire** qui fournit une validation complète de chaque modèle :

### Découverte dynamique des modèles

Le système de tests **découvre automatiquement tous les modèles** sans configuration manuelle :

```console
# Test all templates automatically
$ pytest tests/test_templates/test_all_templates.py -v

# Results show all discovered templates
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-async-crud]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-dockerized]
PASSED tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-psql-orm]
```

### Couverture de tests complète

Chaque modèle subit des **tests complets de bout en bout** :

#### ✅ Processus de création de projet
- Copie du modèle et transformation des fichiers
- Injection des métadonnées du projet (nom, auteur, description)
- Validation de la structure des fichiers

#### ✅ Compatibilité avec les gestionnaires de paquets
- **UV** (par défaut) : gestionnaire de paquets rapide basé sur Rust
- **PDM** : gestion moderne des dépendances Python
- **Poetry** : gestion des dépendances établie
- **PIP** : gestionnaire de paquets Python traditionnel

#### ✅ Gestion de l'environnement virtuel
- Création de l'environnement pour chaque gestionnaire de paquets
- Vérification de l'installation des dépendances
- Flux de travail propres à chaque gestionnaire de paquets

#### ✅ Résolution des dépendances
- Génération de `pyproject.toml` (UV, PDM, Poetry)
- Génération de `requirements.txt` (PIP)
- Conformité aux métadonnées (PEP 621)
- Configuration du système de build

#### ✅ Validation de la structure du projet
- Identification du projet FastAPI
- Existence des fichiers requis
- Vérification de la structure des répertoires

### Exemples d'exécution des tests

**Lancer tous les tests des modèles :**
```console
$ pytest tests/test_templates/test_all_templates.py -v
```

**Tester un modèle précis :**
```console
$ pytest tests/test_templates/test_all_templates.py::TestAllTemplates::test_template_creation[fastapi-default] -v
```

**Tester avec un environnement PDM :**
```console
$ pdm run pytest tests/test_templates/test_all_templates.py -v
```

### Intégration continue

Le système de tests automatisés s'exécute dans les **pipelines CI/CD** :

- ✅ **Validation des pull requests** : chaque PR teste les modèles concernés
- ✅ **Tests nocturnes** : validation complète de la suite de modèles
- ✅ **Tests des gestionnaires de paquets** : validation croisée avec tous les gestionnaires
- ✅ **Tests d'environnement** : plusieurs versions de Python et plateformes

### Avantages pour les contributeurs

**Tests sans configuration :**

- 🚀 Ajout d'un nouveau modèle → tests automatiques
- ⚡ Aucune création manuelle de fichier de test requise
- 🛡️ Standards de qualité cohérents

**Couverture complète :**

- 🔍 Tests de bout en bout de la création de projet
- 📦 Validation multi-gestionnaire de paquets
- 🏗️ Tests complets de résolution des dépendances
- ✅ Simulation d'usage réel

**Expérience développeur :**

- 🎯 **Concentrez-vous sur le contenu du modèle** : les tests sont automatiques
- 🔄 **Retour immédiat** : exécution rapide des tests
- 📊 **Résultats clairs** : rapport de tests détaillé
- 🚫 **Pas de plomberie** : zéro configuration de test nécessaire

## Inspection manuelle des modèles

Pour le développement et le débogage, vous pouvez inspecter manuellement les modèles avec notre script d'inspection local ou les commandes Makefile :

### Utiliser le script d'inspection directement

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

#### Options d'inspection

| Option | Effet | Quand l'utiliser |
|---|---|---|
| `--offline` | Ignore toutes les requêtes réseau (rapport de fraîcheur des dépendances) | Pas de réseau, ou vous voulez une exécution rapide et hermétique |
| `--no-smoke` | Ignore le démarrage du projet généré avec uvicorn | Vous itérez uniquement sur la structure ; le test smoke est l'étape la plus lente |
| `--mypy` | Vérifie les types du projet généré avec mypy | Avant de soumettre un modèle — option à activer explicitement car elle est lente |
| `--templates` | Liste de modèles à inspecter, séparés par des virgules | Vous travaillez sur un seul modèle |
| `--verbose` | Sortie détaillée | Vous déboguez un échec |
| `--output` | Chemin du fichier de résultats JSON | Vous conservez plusieurs exécutions côte à côte |

Une boucle locale rapide sur un seul modèle :

```console
$ python scripts/inspect-templates.py \
    --templates fastapi-sqlmodel --offline --no-smoke --verbose
```

...et la vérification complète avant d'ouvrir une PR :

```console
$ python scripts/inspect-templates.py --templates fastapi-sqlmodel --mypy
```

### Utiliser les commandes Makefile

```console
# Inspect all templates
$ make inspect-templates

# Inspect with verbose output
$ make inspect-templates-verbose

# Inspect specific templates
$ make inspect-template TEMPLATES="fastapi-default,fastapi-async-crud"
```

## Résultats de l'inspection

- Les **inspections réussies** sont consignées dans les sorties et artefacts du workflow
- Les **inspections échouées** créent automatiquement des issues GitHub avec des rapports d'erreur détaillés
- L'**historique d'inspection** est conservé pendant 30 jours dans les artefacts GitHub Actions

## Comprendre la sortie d'inspection

Quand vous exécutez l'inspection de modèles, vous verrez une sortie comme celle-ci :

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

## Exigences des modèles

Pour qu'un modèle passe l'inspection, il doit remplir ces exigences :

### Structure des fichiers
- Doit contenir un répertoire `src/` avec des fichiers source Python
- Les fichiers Python doivent utiliser l'extension `.py-tpl`
- Doit inclure un répertoire `tests/` et un fichier `README.md-tpl`
- Doit inclure `pyproject.toml-tpl` (PEP 621). Les modèles livrés sont pyproject-first et ne fournissent plus de `setup.py-tpl` ; l'inspection l'accepte toujours pour que les modèles tiers continuent de fonctionner, mais les nouveaux modèles ne doivent pas en ajouter.
- `requirements.txt-tpl` est optionnel quand `pyproject.toml-tpl` déclare `[project].dependencies` — mais lorsque les deux sont présents, ils doivent concorder (voir *Cohérence de la configuration*)
- Doit cibler Python 3.12 de manière cohérente : `requires-python = ">=3.12"`, black `target-version = ["py312"]`, mypy `python_version = "3.12"`, et `python:3.12-slim` pour toute image Docker de base
- Ne doit pas déclarer `FastAPI-fastkit` comme dépendance d'exécution
- Ne doit laisser aucun `<placeholder>` non substitué après la génération

### Exigences FastAPI
- Doit contenir l'initialisation de l'application FastAPI
- Doit déclarer `fastapi` comme dépendance dans au moins l'un de : `pyproject.toml-tpl` `[project].dependencies`, `requirements.txt-tpl`, ou `setup.py-tpl` `install_requires`
- Doit avoir une syntaxe Python valide dans tous les fichiers de modèle

### Marqueurs d'identité
Les modèles doivent porter des marqueurs d'identité FastAPI-fastkit afin que les projets générés se distinguent de projets FastAPI non liés dans l'espace de travail de l'utilisateur :

- `pyproject.toml-tpl` — à la fois un préfixe `[FastAPI-fastkit templated]` dans `description` et une table `[tool.fastapi-fastkit]` avec `managed = true`.
- `setup.py-tpl` — préfixe `[FastAPI-fastkit templated]` dans l'argument `description` passé à `setup()`.

`is_fastkit_project()` accepte n'importe lequel des deux (pyproject prend la priorité, setup.py est le repli legacy ; la comparaison est insensible à la casse). L'injection de métadonnées garantit que les marqueurs finissent dans les projets générés même si un modèle les oublie.

### Standards de qualité
- Tous les fichiers de modèle doivent être syntaxiquement corrects
- Les dépendances doivent être correctement spécifiées
- La structure du modèle doit suivre les conventions FastAPI-fastkit

Cette assurance qualité automatisée garantit que tous les modèles restent fiables et prêts pour un usage en production.

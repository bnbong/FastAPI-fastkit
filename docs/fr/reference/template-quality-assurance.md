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
- Doit inclure **au moins un** fichier de métadonnées :
    - `pyproject.toml-tpl` (préféré, PEP 621), ou
    - `setup.py-tpl` (legacy, toujours accepté)
- `requirements.txt-tpl` est optionnel quand `pyproject.toml-tpl` déclare `[project].dependencies`

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

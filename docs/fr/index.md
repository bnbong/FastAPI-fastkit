<p align="center">
    <img align="top" width="70%" src=".github/fastkit_general_logo.png" alt="FastAPI-fastkit"/>
</p>
<p align="center">
<em><b>FastAPI-fastkit</b> : kit de démarrage rapide et facile à utiliser pour les nouveaux utilisateurs de Python et FastAPI</em>
</p>
<p align="center">
<a href="https://pypi.org/project/fastapi-fastkit" target="_blank">
    <img src="https://img.shields.io/pypi/v/fastapi-fastkit" alt="PyPI - Version">
</a>
<a href="https://github.com/bnbong/FastAPI-fastkit/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/bnbong/FastAPI-fastkit" alt="GitHub Release">
</a>
<a href="https://pepy.tech/project/fastapi-fastkit">
    <img src="https://static.pepy.tech/personalized-badge/fastapi-fastkit?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
</a>
</p>

---

Ce projet a été créé pour accélérer la configuration de l'environnement de développement nécessaire au développement d'applications web basées sur Python pour les nouveaux utilisateurs de Python et de [FastAPI](https://github.com/fastapi/fastapi).

Ce projet s'inspire de l'`initializer` de SpringBoot et de l'opération CLI `django-admin` de Python Django.

!!! info "État des traductions"
    L'anglais sert de référence principale pour cette documentation. Les autres langues du sélecteur peuvent être incomplètes ou afficher, page par page, la version anglaise. Consultez [État des traductions](reference/translation-status.md) pour connaître le niveau réel de traduction de chaque locale.

## Fonctionnalités clés

- **⚡ Création immédiate de projets FastAPI** : création en quelques secondes d'espaces de travail et de projets FastAPI depuis la CLI, inspirée de l'expérience `django-admin` de [Python Django](https://github.com/django/django)
- **✨ Assistant interactif de création** : choix pas à pas des bases de données, de l'authentification, du cache, de la supervision et d'autres fonctionnalités, avec génération automatique du code correspondant
- **🎨 Sorties CLI plus élégantes** : expérience CLI soignée grâce à la [bibliothèque rich](https://github.com/Textualize/rich)
- **📋 Modèles de projet FastAPI fondés sur les standards** : tous les modèles de FastAPI-fastkit s'appuient sur les standards Python et les usages courants de FastAPI
- **🔍 Assurance qualité automatisée des modèles** : des tests automatisés hebdomadaires garantissent que tous les modèles restent fonctionnels et à jour
- **🚀 Plusieurs modèles de projet** : choisissez parmi divers modèles préconfigurés pour différents cas d'usage (async CRUD, Docker, PostgreSQL, etc.)
- **📦 Prise en charge de plusieurs gestionnaires de paquets** : choisissez votre gestionnaire de paquets Python préféré (pip, uv, pdm, poetry) pour la gestion des dépendances

## Installation

Installez `FastAPI-fastkit` dans votre environnement Python.

<div class="termy">

```console
$ pip install FastAPI-fastkit
---> 100%
```

</div>


## Utilisation

### Créer immédiatement un nouvel espace de travail FastAPI

Vous pouvez désormais démarrer un nouveau projet FastAPI très rapidement avec FastAPI-fastkit !

Créez immédiatement un nouvel espace de travail pour votre projet FastAPI avec :

<div class="termy">

```console
$ fastkit init
Enter the project name: my-awesome-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI project

           Project Information
┌──────────────┬────────────────────────────┐
│ Project Name │ my-awesome-project         │
│ Author       │ John Doe                   │
│ Author Email │ john@example.com           │
│ Description  │ My awesome FastAPI project │
└──────────────┴────────────────────────────┘

Available Stacks and Dependencies:
           MINIMAL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
└──────────────┴───────────────────┘

           STANDARD Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ pydantic          │
│ Dependency 7 │ pydantic-settings │
└──────────────┴───────────────────┘

             FULL Stack
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ sqlalchemy        │
│ Dependency 4 │ alembic           │
│ Dependency 5 │ pytest            │
│ Dependency 6 │ redis             │
│ Dependency 7 │ celery            │
│ Dependency 8 │ pydantic          │
│ Dependency 9 │ pydantic-settings │
└──────────────┴───────────────────┘

Select stack (minimal, standard, full): minimal

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
FastAPI project will deploy at '~your-project-path~'

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into setup.py                    │
╰──────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into config file                 │
╰──────────────────────────────────────────────────────╯

        Creating Project:
       my-awesome-project
┌───────────────────┬───────────┐
│ Component         │ Collected │
│ fastapi           │ ✓         │
│ uvicorn           │ ✓         │
│ pydantic          │ ✓         │
│ pydantic-settings │ ✓         │
└───────────────────┴───────────┘

Creating virtual environment...

╭──────────────────────── Info ────────────────────────╮
│ ℹ venv created at                                    │
│ ~your-project-path~/my-awesome-project/.venv         │
│ To activate the virtual environment, run:            │
│                                                      │
│     source                                           │
│ ~your-project-path~/my-awesome-project/.venv/bin/act │
│ ivate                                                │
╰──────────────────────────────────────────────────────╯

Installing dependencies...
⠙ Setting up project environment...Collecting <packages~>

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-project' has been      │
│ created successfully and saved to                     │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ To start your project, run 'fastkit runserver' at  │
│ newly created FastAPI project directory              │
╰──────────────────────────────────────────────────────╯
```

</div>

Cette commande crée un nouvel espace de travail FastAPI avec son environnement virtuel Python.

### Créer un projet en mode interactif ✨ NOUVEAU !

Pour les projets plus complexes, utilisez le **mode interactif** afin de construire votre application FastAPI étape par étape, avec une sélection intelligente des fonctionnalités :

<div class="termy">

```console
$ fastkit init --interactive

⚡ FastAPI-fastkit Interactive Project Setup ⚡

📋 Basic Project Information
Enter the project name: my-fullstack-project
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: Full-stack FastAPI project with PostgreSQL and JWT

🧱 Architecture Preset
Pick a project layout. Press Enter to accept the recommended default.
  1. minimal           - Smallest viable FastAPI app
  2. single-module     - Everything in one module (prototypes / scripts)
  3. classic-layered   - api/routes + crud + schemas + core (à la fastapi-default)
  4. domain-starter    - Domain-oriented src/app/domains/<concept>/ (recommended)

Select architecture preset: [4]

🗄️ Database Selection
Select database (PostgreSQL, MySQL, MongoDB, Redis, SQLite, None):
  1. PostgreSQL - PostgreSQL database with SQLAlchemy
  2. MySQL - MySQL database with SQLAlchemy
  3. MongoDB - MongoDB with motor async driver
  4. Redis - Redis for caching and session storage
  5. SQLite - SQLite database for development
  6. None - No database

Select database: 1

🔐 Authentication Selection
Select authentication (JWT, OAuth2, FastAPI-Users, Session-based, None):
  1. JWT - JSON Web Token authentication
  2. OAuth2 - OAuth2 with password flow
  3. FastAPI-Users - Full featured user management
  4. Session-based - Cookie-based sessions
  5. None - No authentication

Select authentication: 1

⚙️ Background Tasks Selection
Select background tasks (Celery, Dramatiq, None):
  1. Celery - Distributed task queue
  2. Dramatiq - Fast and reliable task processing
  3. None - No background tasks

Select background tasks: 1

💾 Caching Selection
Select caching (Redis, fastapi-cache2, None):
  1. Redis - Redis caching
  2. fastapi-cache2 - Simple caching for FastAPI
  3. None - No caching

Select caching: 1

📊 Monitoring Selection
Select monitoring (Loguru, OpenTelemetry, Prometheus, None):
  1. Loguru - Simple and powerful logging
  2. OpenTelemetry - Observability framework
  3. Prometheus - Metrics and monitoring
  4. None - No monitoring

Select monitoring: 3

🧪 Testing Framework Selection
Select testing framework (Basic, Coverage, Advanced, None):
  1. Basic - pytest + httpx for API testing
  2. Coverage - Basic + code coverage
  3. Advanced - Coverage + faker + factory-boy for fixtures
  4. None - No testing framework

Select testing framework: 2

🛠️ Additional Utilities
Select utilities (comma-separated numbers, e.g., 1,3,4):
  1. CORS - Cross-Origin Resource Sharing
  2. Rate-Limiting - Request rate limiting
  3. Pagination - Pagination support
  4. WebSocket - WebSocket support

Select utilities: 1

🚀 Deployment Configuration
Select deployment option:
  1. Docker - Generate Dockerfile
  2. docker-compose - Generate docker-compose.yml (includes Docker)
  3. None - No deployment configuration

Select deployment option: 2

📦 Package Manager Selection
Select package manager (pip, uv, pdm, poetry): uv

📝 Custom Packages (optional)
Enter custom package names (comma-separated, press Enter to skip):

📋 Project Configuration Summary
┌─────────────────────┬───────────────────────────────────────────────────────────────────────────┐
│ Setting             │ Value                                                                     │
├─────────────────────┼───────────────────────────────────────────────────────────────────────────┤
│ Project Name        │ my-fullstack-project                                                      │
│ Author              │ John Doe                                                                  │
│ Email               │ john@example.com                                                          │
│ Description         │ Full-stack FastAPI project with PostgreSQL and JWT                        │
│ Architecture Preset │ domain-starter — Domain-oriented: src/app/domains/<concept>/ (recommended)│
│ Database            │ PostgreSQL                                                                │
│ Authentication      │ JWT                                                                       │
│ Async Tasks         │ Celery                                                                    │
│ Caching             │ Redis                                                                     │
│ Monitoring          │ Prometheus                                                                │
│ Testing             │ Coverage                                                                  │
│ Utilities           │ CORS                                                                      │
│ Package Manager     │ uv                                                                        │
└─────────────────────┴───────────────────────────────────────────────────────────────────────────┘

Total dependencies to install: 18

Proceed with project creation? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Injected metadata into pyproject.toml              │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated dependency file with 18 packages         │
╰───────────────────────────────────────────────────────╯
╭──────────────────────── Info ────────────────────────╮
│ ℹ Preserving template-shipped main.py for preset     │
│ 'domain-starter'.                                    │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated Docker deployment files                  │
╰───────────────────────────────────────────────────────╯
╭────────────────────── Warning ────────────────────────╮
│ ⚠ Preset compatibility                               │
│ fastapi-domain-starter's shipped src/app/main.py is  │
│ preserved. The selections below need manual wiring   │
│ there (CORS is already wired — set                   │
│ BACKEND_CORS_ORIGINS in .env to activate it).        │
│ Affected selections (packages installed, but no      │
│ dynamic main.py edits applied for the                │
│ 'domain-starter' preset): Prometheus                 │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Generated configuration files for selected stack   │
╰───────────────────────────────────────────────────────╯

Creating virtual environment...
Installing dependencies...

----> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-fullstack-project' from        │
│ 'fastapi-domain-starter' has been created!            │
╰───────────────────────────────────────────────────────╯
```

</div>

Le mode interactif offre :

- **Sélection d'un préréglage d'architecture** (`minimal` / `single-module` / `classic-layered` / `domain-starter`) qui choisit le modèle de base et la disposition de projet adaptés
- **Sélection guidée** des bases de données, de l'authentification, des tâches en arrière-plan, de la mise en cache, de la supervision et plus encore
- **Génération automatique de code** pour les fonctionnalités sélectionnées — varie selon le préréglage (régénération de `main.py` pour `minimal` / `single-module` ; préservation du `main.py` fourni par le modèle et superposition de modules de configuration pour `classic-layered` / `domain-starter`)
- **Génération Docker adaptée au préréglage** — le `CMD` du `Dockerfile` généré pointe vers le véritable point d'entrée du préréglage (`src.main:app` ou `src.app.main:app`)
- **Gestion intelligente des dépendances** avec compatibilité automatique pour pip
- **Validation des fonctionnalités** avec des avertissements de câblage manuel pour les sélections que le préréglage ne peut pas câbler automatiquement
- **Marqueurs d'identité** dans le `pyproject.toml` généré (marqueur de description + table `[tool.fastapi-fastkit]`) afin que `is_fastkit_project()` puisse reconnaître les projets générés par la suite

### Ajouter une nouvelle route au projet FastAPI

`FastAPI-fastkit` facilite l'extension de votre projet FastAPI.

Ajoutez un nouveau point d'extrémité de route à votre projet FastAPI avec :

<div class="termy">

```console
$ fastkit addroute user my-awesome-project
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-awesome-project                       │
│ Route Name       │ user                                     │
│ Target Directory │ ~your-project-path~                      │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'user' to project 'my-awesome-project'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'user' to project     │
│ `my-awesome-project`                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

### Déployer immédiatement un projet de démonstration FastAPI structuré

Vous pouvez aussi démarrer avec un projet de démonstration FastAPI structuré.

Les projets de démonstration sont composés de diverses piles techniques avec des points d'extrémité CRUD d'items simples implémentés.

Déployez immédiatement un projet de démonstration FastAPI structuré avec :

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-awesome-demo
Enter the author name: John Doe
Enter the author email: john@example.com
Enter the project description: My awesome FastAPI demo
Deploying FastAPI project using 'fastapi-default' template
Template path:
/~fastapi_fastkit-package-path~/fastapi_project_template/fastapi-default

           Project Information
┌──────────────┬─────────────────────────┐
│ Project Name │ my-awesome-demo         │
│ Author       │ John Doe                │
│ Author Email │ john@example.com        │
│ Description  │ My awesome FastAPI demo │
└──────────────┴─────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ python-dotenv     │
└──────────────┴───────────────────┘

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y
FastAPI template project will deploy at '~your-project-path~'

---> 100%

╭─────────────────────── Success ───────────────────────╮
│ ✨ Dependencies installed successfully                │
╰───────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ FastAPI project 'my-awesome-demo' from             │
│ 'fastapi-default' has been created and saved to       │
│ ~your-project-path~!                                  │
╰───────────────────────────────────────────────────────╯
```

</div>

Pour consulter la liste des démos FastAPI disponibles, vérifiez avec :

<div class="termy">

```console
$ fastkit list-templates
                              Available Templates
┌────────────────────────┬───────────────────────────────────────────────────────┐
│ fastapi-custom-response│ Async Item Management API with Custom Response System │
│ fastapi-mcp            │ FastAPI MCP Project                                   │
│ fastapi-domain-starter │ FastAPI Domain Starter                                │
│ fastapi-dockerized     │ Dockerized FastAPI Item Management API                │
│ fastapi-empty          │ Minimal FastAPI Template                              │
│ fastapi-async-crud     │ Async Item Management API Server                      │
│ fastapi-psql-orm       │ Dockerized FastAPI Item Management API with           │
│                        │ PostgreSQL                                            │
│ fastapi-default        │ Simple FastAPI Project                                │
│ fastapi-single-module  │ FastAPI Single Module Template                        │
└────────────────────────┴───────────────────────────────────────────────────────┘
```

</div>

## Documentation

Pour des guides complets et des instructions d'utilisation détaillées, explorez notre documentation :

- 📚 **[Guide de l'utilisateur](user-guide/quick-start.md)** — guides détaillés d'installation et d'utilisation
- 🎯 **[Tutoriel](tutorial/getting-started.md)** — tutoriels pas à pas pour les débutants
- 📖 **[Référence CLI](user-guide/cli-reference.md)** — référence complète des commandes
- 🔍 **[Assurance qualité des modèles](reference/template-quality-assurance.md)** — tests automatisés et standards de qualité

## 🚀 Tutoriels basés sur les modèles

Apprenez FastAPI à travers des cas pratiques grâce à nos modèles déjà prêts à l'emploi :

### 📖 Tutoriels principaux

- **[Construire un serveur d'API basique](tutorial/basic-api-server.md)** — créez votre premier serveur FastAPI à l'aide du modèle `fastapi-default`
- **[Construire une API CRUD asynchrone](tutorial/async-crud-api.md)** — développez une API asynchrone haute performance avec le modèle `fastapi-async-crud`
- **[Projet orienté domaine (Domain Starter)](tutorial/domain-starter.md)** — construisez une API de taille moyenne avec le modèle `fastapi-domain-starter`, l'option moderne recommandée

### 🗄️ Base de données et infrastructure

- **[Intégration avec une base de données](tutorial/database-integration.md)** — exploitez PostgreSQL + SQLAlchemy avec le modèle `fastapi-psql-orm`
- **[Conteneurisation Docker et déploiement](tutorial/docker-deployment.md)** — configurez un environnement de déploiement en production avec le modèle `fastapi-dockerized`

### ⚡ Fonctionnalités avancées

- **[Gestion des réponses personnalisées et conception d'API avancée](tutorial/custom-response-handling.md)** — construisez des API d'entreprise avec le modèle `fastapi-custom-response`
- **[Intégration avec MCP](tutorial/mcp-integration.md)** — créez un serveur d'API intégré à des modèles d'IA avec le modèle `fastapi-mcp`

Chaque tutoriel propose :

- ✅ **Exemples pratiques** — du code directement utilisable dans des projets réels
- ✅ **Guides pas à pas** — explications détaillées faciles à suivre pour les débutants
- ✅ **Bonnes pratiques** — motifs standards de l'industrie et considérations de sécurité
- ✅ **Méthodes d'extension** — conseils pour faire passer votre projet au niveau supérieur

## Contribution

Nous accueillons avec plaisir les contributions de la communauté ! FastAPI-fastkit est conçu pour aider les nouveaux venus à Python et à FastAPI, et vos contributions peuvent avoir un impact significatif.

### Ce que vous pouvez apporter

- 🚀 **Nouveaux modèles FastAPI** — ajoutez des modèles pour différents cas d'usage
- 🐛 **Corrections de bogues** — aidez-nous à améliorer la stabilité et la fiabilité
- 📚 **Documentation** — améliorez les guides, les exemples et les traductions
- 🧪 **Tests** — augmentez la couverture des tests et ajoutez des tests d'intégration
- 💡 **Fonctionnalités** — proposez et implémentez de nouvelles fonctionnalités CLI

### Premiers pas pour contribuer

Pour commencer à contribuer à FastAPI-fastkit, consultez nos guides complets :

- **[Configuration de l'environnement de développement](contributing/development-setup.md)** — guide complet pour configurer votre environnement de développement
- **[Directives de code](contributing/code-guidelines.md)** — standards de codage et bonnes pratiques
- **[CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** — guide de contribution complet
- **[CODE_OF_CONDUCT.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CODE_OF_CONDUCT.md)** — principes du projet et standards de la communauté
- **[SECURITY.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/SECURITY.md)** — directives de sécurité et signalement

## Pourquoi FastAPI-fastkit

FastAPI-fastkit vise à fournir un kit de démarrage rapide et facile à utiliser pour les nouveaux utilisateurs de Python et de FastAPI.

Cette idée est née avec l'objectif d'aider les nouveaux venus à FastAPI à apprendre dès le départ, dans la lignée de l'importance pour la production du paquet FastAPI-cli ajouté lors de la [mise à jour FastAPI 0.111.0](https://github.com/fastapi/fastapi/releases/tag/0.111.0).

En tant qu'utilisateur passionné de FastAPI depuis longtemps, je voulais développer un projet capable de répondre à [la magnifique motivation](https://github.com/fastapi/fastapi/pull/11522#issuecomment-2264639417) exprimée par le développeur de FastAPI [tiangolo](https://github.com/tiangolo).

FastAPI-fastkit comble l'écart entre la prise en main et la création d'applications prêtes pour la production en proposant :

- **Productivité immédiate** pour les nouveaux venus qui pourraient être submergés par la complexité de la configuration
- **Bonnes pratiques** intégrées à chaque modèle, aidant les utilisateurs à apprendre les motifs FastAPI corrects
- **Fondations évolutives** qui accompagnent les utilisateurs depuis leurs débuts jusqu'à l'expertise
- **Modèles portés par la communauté** qui reflètent les usages réels de FastAPI

## Étapes suivantes

Prêt à commencer avec FastAPI-fastkit ? Suivez ces étapes :

### 🚀 Démarrage rapide

1. **[Installation](user-guide/installation.md)** : installer FastAPI-fastkit
2. **[Démarrage rapide](user-guide/quick-start.md)** : créer votre premier projet en 5 minutes
3. **[Tutoriel de prise en main](tutorial/getting-started.md)** : tutoriel détaillé pas à pas

### 📚 Apprentissage avancé

- **[Créer des projets](user-guide/creating-projects.md)** : créer des projets avec différentes piles
- **[Ajouter des routes](user-guide/adding-routes.md)** : ajouter des points d'extrémité d'API à votre projet
- **[Utiliser les modèles](user-guide/using-templates.md)** : utiliser des modèles de projet déjà prêts à l'emploi

### 🛠️ Contribution

Envie de contribuer à FastAPI-fastkit ?

- **[Configuration du développement](contributing/development-setup.md)** : configurer votre environnement de développement
- **[Directives de code](contributing/code-guidelines.md)** : suivre nos standards de codage et bonnes pratiques
- **[Directives de contribution](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)** : guide de contribution complet

### 🔍 Référence

- **[Référence CLI](user-guide/cli-reference.md)** : référence complète des commandes CLI
- **[Assurance qualité des modèles](reference/template-quality-assurance.md)** : tests automatisés et standards de qualité
- **[FAQ](reference/faq.md)** : foire aux questions
- **[Dépôt GitHub](https://github.com/bnbong/FastAPI-fastkit)** : code source et suivi des tickets

## Licence

Ce projet est sous licence MIT — consultez le fichier [LICENSE](https://github.com/bnbong/FastAPI-fastkit/blob/main/LICENSE) pour plus de détails.

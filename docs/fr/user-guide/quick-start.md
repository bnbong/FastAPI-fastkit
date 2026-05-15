# Démarrage rapide

Créez votre premier projet FastAPI avec FastAPI-fastkit en moins de 5 minutes !

!!! tip "Vous ne savez pas quel starter choisir ?"
    Consultez [**Quel starter choisir ?**](choosing-a-starter.md) pour voir une comparaison pensée pour les débutants entre les modèles `startdemo` et les préréglages d'architecture interactifs (`minimal` / `single-module` / `classic-layered` / `domain-starter`). En bref : **`fastkit init --interactive` avec le préréglage `domain-starter` est l'option moderne recommandée.**

## 1. Créer le projet

Utilisez la commande `init` de FastAPI-fastkit pour créer un nouveau projet :

<div class="termy">

```console
$ fastkit init
Enter the project name: my-first-app
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: My first FastAPI application

           Project Information
┌──────────────┬─────────────────────────────┐
│ Project Name │ my-first-app                │
│ Author       │ Your Name                   │
│ Author Email │ your.email@example.com      │
│ Description  │ My first FastAPI application│
└──────────────┴─────────────────────────────┘

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

✨ FastAPI project 'my-first-app' has been created successfully!
```

</div>

## 2. Activer l'environnement virtuel

Allez dans votre projet et activez l'environnement virtuel :

<div class="termy">

```console
$ cd my-first-app
$ source .venv/bin/activate  # Linux/macOS
$ .venv\Scripts\activate     # Windows
```

</div>

## 3. Démarrer le serveur de développement

Démarrez le serveur de développement FastAPI :

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [28720]
INFO:     Started server process [28722]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

</div>

!!! success "Félicitations !"
    Votre serveur FastAPI tourne maintenant ! Ouvrez votre navigateur pour le découvrir.

## 4. Tester votre API

Ouvrez votre navigateur et rendez-vous à ces URL :

### Point d'extrémité principal

Visitez [http://127.0.0.1:8000](http://127.0.0.1:8000)

Vous verrez :

```json
{"message": "Hello World"}
```

### Documentation interactive de l'API

Visitez [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Il s'agit de la documentation **Swagger UI** générée automatiquement, où vous pouvez :

- Voir tous vos points d'extrémité d'API
- Tester les points d'extrémité directement dans le navigateur
- Consulter les schémas de requête et de réponse

### Documentation alternative

Visitez [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Il s'agit de l'interface de documentation **ReDoc**, au design différent et épuré.

## 5. Ajouter votre première route

Ajoutons une nouvelle route d'API à votre projet :

<div class="termy">

```console
$ fastkit addroute users my-first-app
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-first-app                             │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-first-app                           │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-first-app'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-first-app`                                        │
╰───────────────────────────────────────────────────────╯
```

</div>

Le serveur va se recharger automatiquement, et vous disposez désormais de nouveaux points d'extrémité :

- `GET /api/v1/users/` — récupérer tous les utilisateurs
- `POST /api/v1/users/` — créer un nouvel utilisateur
- `GET /api/v1/users/{user_id}` — récupérer un utilisateur précis
- `PUT /api/v1/users/{user_id}` — mettre à jour un utilisateur
- `DELETE /api/v1/users/{user_id}` — supprimer un utilisateur

## 6. Tester la nouvelle API

### Avec curl

**Récupérer tous les utilisateurs :**

<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/
[]
```

</div>

**Créer un nouvel utilisateur :**

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{"title": "John Doe", "description": "Software Developer"}'
{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}
```

</div>

### Avec la documentation interactive

1. Rendez-vous sur [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
2. Dépliez la section **« users »**
3. Cliquez sur **« POST /api/v1/users/ »**
4. Cliquez sur **« Try it out »**
5. Remplissez le corps de la requête :
   ```json
   {
     "title": "Jane Smith",
     "description": "Product Manager"
   }
   ```
6. Cliquez sur **« Execute »**

## 7. Explorer la structure de votre projet

Votre projet généré a une structure claire et organisée :

```
my-first-app/
├── .venv/                    # Environnement virtuel
├── src/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée de l'application FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # Configuration de l'application
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py          # Ensemble des routeurs de l'API
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── items.py     # Route items par défaut
│   │       └── users.py     # Votre nouvelle route users
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── items.py         # Opérations CRUD pour items
│   │   └── users.py         # Opérations CRUD pour users
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── items.py         # Schémas Pydantic pour items
│   │   └── users.py         # Schémas Pydantic pour users
│   └── mocks/
│       ├── __init__.py
│       └── mock_items.json  # Données de test
├── tests/                   # Fichiers de test
├── scripts/                 # Scripts utilitaires
├── requirements.txt         # Dépendances Python
├── setup.py                # Configuration du paquet
└── README.md               # Documentation du projet
```

## 8. Options de gestionnaire de paquets

FastAPI-fastkit prend en charge plusieurs gestionnaires de paquets Python adaptés à vos préférences :

### Gestionnaires de paquets disponibles

| Gestionnaire | Description | Idéal pour |
|---------|-------------|----------|
| **UV** | Gestionnaire de paquets Python rapide (par défaut) | La vitesse et la performance |
| **PDM** | Gestion moderne des dépendances Python | La résolution avancée des dépendances |
| **Poetry** | Gestion des dépendances et packaging Python | Les flux de travail basés sur Poetry |
| **PIP** | Gestionnaire de paquets Python standard | Le développement Python traditionnel |

### Spécifier le gestionnaire de paquets

Vous pouvez indiquer votre gestionnaire de paquets préféré de plusieurs manières :

#### 1. Sélection interactive (par défaut)

Lorsque vous lancez `fastkit init` ou `fastkit startdemo`, vous serez invité à faire un choix :

<div class="termy">

```console
$ fastkit init
# ... after project details and stack selection ...

Available Package Managers:
                   Package Managers
┌────────┬────────────────────────────────────────────┐
│ PIP    │ Standard Python package manager            │
│ UV     │ Fast Python package manager                │
│ PDM    │ Modern Python dependency management        │
│ POETRY │ Python dependency management and packaging │
└────────┴────────────────────────────────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
```

</div>

#### 2. Option en ligne de commande

Évitez l'invite interactive en spécifiant directement le gestionnaire de paquets :

<div class="termy">

```console
$ fastkit init --package-manager poetry
$ fastkit startdemo --package-manager pdm
```

</div>

### Fichiers de dépendances générés

Chaque gestionnaire de paquets crée les fichiers de dépendances appropriés :

- **UV/PDM** : `pyproject.toml` (format PEP 621)
- **Poetry** : `pyproject.toml` (format Poetry)
- **PIP** : `requirements.txt`

## 9. Et ensuite ?

Félicitations ! Vous avez :

✅ Créé votre premier projet FastAPI
✅ Démarré le serveur de développement
✅ Ajouté une nouvelle route d'API
✅ Testé vos API

### Continuer à apprendre

1. **[Votre premier projet](../tutorial/first-project.md)** : construire une API de blog plus complexe
2. **[Créer des projets](creating-projects.md)** : découvrir les différentes piles et options
3. **[Ajouter des routes](adding-routes.md)** : maîtriser l'art du développement d'API
4. **[Utiliser les modèles](using-templates.md)** : explorer les modèles de projet déjà prêts à l'emploi

### Expérimenter davantage

Essayez ces commandes pour explorer d'autres fonctionnalités :

<div class="termy">

```console
# List available templates
$ fastkit list-templates

# Create a project from a template
$ fastkit startdemo

# Add more routes (route name first, project dir second)
$ fastkit addroute products my-first-app
$ fastkit addroute orders my-first-app
```

</div>

!!! tip "Astuces de développement"
    - Le serveur se recharge automatiquement quand vous modifiez des fichiers
    - Consultez toujours la documentation interactive à `/docs` lors de l'ajout de nouvelles fonctionnalités
    - Utilisez l'environnement virtuel pour isoler vos dépendances
    - Explorez le code généré pour comprendre la structure du projet

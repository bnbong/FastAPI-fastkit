# Foire aux questions

Questions et réponses fréquentes sur FastAPI-fastkit.

## Installation et configuration

### Q. Quelles versions de Python sont prises en charge ?

**R.** FastAPI-fastkit requiert **Python 3.12 ou supérieur**. Nous recommandons d'utiliser la dernière version stable de Python pour la meilleure expérience.

<div class="termy">

```console
$ python --version
Python 3.12.1

$ pip install fastapi-fastkit
```

</div>

### Q. Comment installer FastAPI-fastkit ?

**R.** Vous pouvez installer FastAPI-fastkit avec pip :

<div class="termy">

```console
# Latest stable version
$ pip install fastapi-fastkit

# Development version from GitHub
$ pip install git+https://github.com/bnbong/FastAPI-fastkit.git

# Specific version
$ pip install fastapi-fastkit==1.0.0
```

</div>

### Q. L'installation échoue avec des erreurs de permission

**R.** Essayez d'installer dans un environnement virtuel ou avec les permissions utilisateur :

<div class="termy">

```console
# Create virtual environment
$ python -m venv fastapi-env
$ source fastapi-env/bin/activate  # On Windows: fastapi-env\Scripts\activate

# Install in virtual environment
$ pip install fastapi-fastkit

# Or install for current user only
$ pip install --user fastapi-fastkit
```

</div>

### Q. La commande `fastkit` est introuvable après l'installation

**R.** Cela signifie généralement que le répertoire d'installation n'est pas dans votre PATH :

<div class="termy">

```console
# Check if installed
$ pip show fastapi-fastkit

# Find installation location
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__file__)"

# Try running directly
$ python -m fastapi_fastkit --version

# Or add to PATH (Linux/macOS)
$ export PATH="$HOME/.local/bin:$PATH"
```

</div>

## Création de projet

### Q. Quelles piles de dépendances sont disponibles ?

**R.** FastAPI-fastkit propose trois piles de dépendances :

- **MINIMAL** : FastAPI, Uvicorn, Pydantic, Pydantic-Settings (API web basique)
- **STANDARD** : ajoute SQLAlchemy, Alembic, pytest (prise en charge des bases de données)
- **FULL** : ajoute Redis, Celery (tâches en arrière-plan)

!!! tip "Gestionnaire de paquets par défaut"
    Le gestionnaire de paquets par défaut est `uv` pour une installation plus rapide des dépendances. Vous pouvez aussi choisir `pip`, `pdm` ou `poetry`.

<div class="termy">

```console
$ fastkit init
# Select your preferred stack during project creation
```

</div>

### Q. Puis-je personnaliser le modèle de projet ?

**R.** Oui ! Vous pouvez :

1. **Utiliser des modèles existants** avec `fastkit startdemo`
2. **Créer des modèles personnalisés** en copiant et modifiant des modèles existants
3. **Ajouter des routes au fur et à mesure** avec `fastkit addroute`

<div class="termy">

```console
# Use pre-built templates
$ fastkit list-templates
$ fastkit startdemo

# Add routes to existing project
$ fastkit addroute users .          # Add 'users' route to current directory
$ fastkit addroute users my-project # Add 'users' route to 'my-project'
```

</div>

### Q. Comment créer un projet avec un format de nom particulier ?

**R.** Les noms de projet doivent être des identifiants Python valides :

- ✅ `my-api`, `blog_system`, `UserService`
- ❌ `my api`, `123project`, `project-name!`

<div class="termy">

```console
$ fastkit init
Enter the project name: my_awesome_api  # Valid
Enter the project name: my-awesome-api  # Valid (hyphens converted to underscores)
```

</div>

### Q. La création de projet échoue avec « directory already exists »

**R.** Le répertoire du projet existe déjà. Vous pouvez :

1. **Choisir un autre nom**
2. **Supprimer le répertoire existant** (si c'est sans danger)
3. **Utiliser un autre emplacement de sortie**

<div class="termy">

```console
# Check if directory exists
$ ls my-project

# Remove if safe (CAUTION!)
$ rm -rf my-project

# Or create in different location
$ mkdir projects
$ cd projects
$ fastkit init
```

</div>

### Q. Comment utiliser le mode interactif pour configurer un projet ?

**R.** Utilisez `fastkit init --interactive` pour une configuration pas à pas guidée du projet avec une sélection intelligente de fonctionnalités :

<div class="termy">

```console
$ fastkit init --interactive
```

</div>

Le mode interactif vous guide à travers ces étapes dans l'ordre :

1. **Informations du projet** — nom, auteur, e-mail, description.
2. **Préréglage d'architecture** — choisit la disposition du projet. L'option recommandée par défaut est `domain-starter` ; appuyez sur Entrée pour l'accepter. Consultez la [matrice des préréglages et fonctionnalités](preset-feature-matrix.md) pour voir la disposition exacte produite par chaque préréglage et les combinaisons de fonctionnalités qui demandent un câblage manuel.
3. **Sélections de fonctionnalités** — base de données, authentification, tâches en arrière-plan, mise en cache, supervision, tests, utilitaires, déploiement.
4. **Gestionnaire de paquets et paquets personnalisés** — pip / uv / pdm / poetry, ainsi que les extras que vous souhaitez épingler.
5. **Confirmation** — un tableau récapitulatif affiche chaque choix (y compris le préréglage d'architecture) avant la création du projet.

Le mode interactif vous permet de choisir dans un catalogue complet de fonctionnalités :

| Catégorie | Options disponibles |
|----------|-------------------|
| **Architecture** | minimal, single-module, classic-layered, **domain-starter** (option recommandée par défaut) |
| **Base de données** | PostgreSQL, MySQL, MongoDB, Redis, SQLite |
| **Authentification** | JWT, OAuth2, FastAPI-Users, basée sur session |
| **Tâches en arrière-plan** | Celery, Dramatiq |
| **Tests** | Basic (pytest), Coverage, Advanced (avec faker, factory-boy) |
| **Mise en cache** | Redis avec fastapi-cache2 |
| **Supervision** | Loguru, OpenTelemetry, Prometheus |
| **Utilitaires** | CORS, Rate-Limiting, Pagination, WebSocket |
| **Déploiement** | Docker, docker-compose avec configurations auto-générées |

Le mode interactif génère automatiquement :

- `main.py` avec les fonctionnalités sélectionnées intégrées
- Des fichiers de configuration base de données et authentification lorsque les options sélectionnées prennent en charge la génération de code (par ex. PostgreSQL/MySQL/SQLite/MongoDB pour les bases de données, JWT/FastAPI-Users pour l'authentification) ; les autres options installent uniquement les paquets nécessaires
- Des fichiers de déploiement correspondant à l'option choisie (`Dockerfile` quand `Docker` est sélectionné, `docker-compose.yml` quand `docker-compose` est sélectionné)
- Une configuration de tests basée sur l'option de tests sélectionnée (les paramètres de couverture ne sont inclus que lorsque `Coverage` ou `Advanced` est sélectionné)

### Q. Comment voir les fonctionnalités disponibles pour le mode interactif ?

**R.** Utilisez la commande `list-features` pour afficher toutes les fonctionnalités disponibles et leurs paquets :

<div class="termy">

```console
$ fastkit list-features
# Shows all available features organized by category
# with their associated packages
```

</div>

Cela vous aide à comprendre quels paquets seront installés pour chaque sélection de fonctionnalité.

## Développement de routes

### Q. Comment ajouter l'authentification à mes routes ?

**R.** Créez une dépendance pour l'authentification :

```python
# src/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(token: str = Depends(security)):
    # Verify token and return user
    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return get_user_from_token(token)

# src/api/routes/users.py
@router.get("/me")
def get_current_user_profile(user = Depends(get_current_user)):
    return user
```

### Q. Comment ajouter des modèles de base de données à mon projet ?

**R.** Pour les piles STANDARD ou FULL, créez des modèles SQLAlchemy :

```python
# src/models/users.py
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
```

### Q. Comment ajouter la validation aux données de requête ?

**R.** Utilisez les modèles Pydantic dans vos schémas :

```python
# src/schemas/users.py
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### Q. Comment gérer les téléversements de fichiers ?

**R.** Utilisez `UploadFile` de FastAPI :

```python
from fastapi import UploadFile, File

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    # Save file
    with open(f"uploads/{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

## Modèles

### Q. Quels modèles sont disponibles ?

**R.** FastAPI-fastkit inclut plusieurs modèles prêts à l'emploi :

<div class="termy">

```console
$ fastkit list-templates
                      Available Templates
┌─────────────────────────┬───────────────────────────────────┐
│ fastapi-default         │ Simple FastAPI Project            │
│ fastapi-async-crud      │ Async Item Management API Server  │
│ fastapi-custom-response │ Custom Response System            │
│ fastapi-dockerized      │ Dockerized FastAPI API            │
│ fastapi-empty           │ Minimal FastAPI Project           │
│ fastapi-mcp             │ MCP (Model Context Protocol) API  │
│ fastapi-psql-orm        │ PostgreSQL FastAPI API            │
│ fastapi-single-module   │ Single-file FastAPI Project       │
└─────────────────────────┴───────────────────────────────────┘
```

</div>

### Q. Comment utiliser un modèle spécifique ?

**R.** Utilisez la commande `startdemo` :

<div class="termy">

```console
$ fastkit startdemo
Enter the project name: my-blog
Select template: fastapi-psql-orm
```

</div>

### Q. Puis-je créer mes propres modèles ?

**R.** Oui ! Créez une structure de répertoires et utilisez les variables de modèle :

```
my-template/
├── src/
│   └── main.py-tpl
├── requirements.txt-tpl
└── template.yaml
```

```python
# main.py-tpl
from fastapi import FastAPI

app = FastAPI(title="{{PROJECT_NAME}}")

@app.get("/")
def read_root():
    return {"message": "Hello from {{PROJECT_NAME}}!"}
```

### Q. Comment modifier un modèle existant ?

**R.** Les modèles se trouvent dans le répertoire `fastapi_project_template`. Vous pouvez :

1. **Forker le dépôt** et modifier les modèles
2. **Créer un modèle personnalisé** basé sur les existants
3. **Remplacer des fichiers précis** après la création du projet

## Serveur de développement

### Q. Comment démarrer le serveur de développement ?

**R.** Utilisez la commande `runserver` depuis le répertoire de votre projet :

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate  # Activate virtual environment
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Q. Le serveur ne démarre pas — « Address already in use »

**R.** Le port 8000 est occupé. Utilisez un autre port ou tuez le processus existant :

<div class="termy">

```console
# Use different port
$ fastkit runserver --port 8080

# Or find and kill existing process
$ lsof -ti:8000 | xargs kill -9

# On Windows
$ netstat -ano | findstr :8000
$ taskkill /PID <PID> /F
```

</div>

### Q. Le rechargement automatique ne fonctionne pas

**R.** Assurez-vous d'être dans le répertoire du projet et que l'environnement virtuel est activé :

<div class="termy">

```console
# Check current directory
$ pwd
/path/to/my-project

# Check virtual environment
$ which python
/path/to/my-project/.venv/bin/python

# Start with explicit reload
$ fastkit runserver --reload
```

</div>

### Q. Comment configurer le serveur pour la production ?

**R.** N'utilisez pas le serveur de développement en production. À la place :

```python
# Use gunicorn or similar WSGI server
$ pip install gunicorn
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Or use Docker with the fastapi-dockerized template
$ fastkit startdemo  # Select fastapi-dockerized
$ docker build -t my-app .
$ docker run -p 8000:8000 my-app
```

## Performance et optimisation

### Q. Comment améliorer les performances de l'API ?

**R.** Plusieurs stratégies d'optimisation :

1. **Utilisez async/await** pour les opérations d'E/S
2. **Ajoutez du cache** pour les opérations coûteuses
3. **Optimisez les requêtes de base de données**
4. **Utilisez des tâches en arrière-plan** pour les traitements lourds

```python
# Async endpoint
@router.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await users_service.get_user_async(user_id)
    return user

# Background task
from fastapi import BackgroundTasks

@router.post("/send-email")
def send_email(background_tasks: BackgroundTasks, email: str):
    background_tasks.add_task(send_notification_email, email)
    return {"message": "Email will be sent in background"}
```

### Q. Comment ajouter du cache ?

**R.** Utilisez Redis pour la mise en cache :

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiration: int = 300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function and cache result
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)
async def get_expensive_data():
    # Expensive operation
    return complex_calculation()
```

### Q. Comment gérer beaucoup de requêtes concurrentes ?

**R.** Utilisez une configuration de serveur appropriée :

<div class="termy">

```console
# Development
$ fastkit runserver --workers 1  # Single worker for development

# Production
$ gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
$ uvicorn src.main:app --workers 4 --host 0.0.0.0 --port 8000
```

</div>

## Tests

### Q. Comment lancer les tests ?

**R.** Utilisez pytest depuis le répertoire de votre projet :

<div class="termy">

```console
$ cd my-project
$ source .venv/bin/activate
$ python -m pytest

# With coverage
$ python -m pytest --cov=src

# Specific test file
$ python -m pytest tests/test_users.py

# With verbose output
$ python -m pytest -v
```

</div>

### Q. Comment écrire des tests d'API ?

**R.** Utilisez le client de test de FastAPI :

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "username": "testuser"}
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_get_user():
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
```

### Q. Comment simuler les dépendances externes ?

**R.** Utilisez les fixtures pytest et la simulation :

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_database():
    with patch('src.database.get_db') as mock_db:
        mock_db.return_value = Mock()
        yield mock_db

def test_user_creation_with_mock_db(mock_database):
    # Test with mocked database
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
```

## Contribution

### Q. Comment contribuer à FastAPI-fastkit ?

**R.** Suivez ces étapes :

1. **Forkez le dépôt** sur GitHub
2. **Mettez en place l'environnement de développement**
3. **Créez une branche de fonctionnalité**
4. **Apportez vos changements** avec des tests
5. **Soumettez une pull request**

<div class="termy">

```console
$ git clone https://github.com/yourusername/FastAPI-fastkit.git
$ cd FastAPI-fastkit
$ make dev-setup  # Set up development environment
$ git checkout -b feature/my-feature
# Make changes...
$ make dev-check  # Format, lint, and test
$ git commit -m "feat: add new feature"
$ git push origin feature/my-feature
```

</div>

### Q. Que dois-je inclure dans une pull request ?

**R.** Chaque pull request doit inclure :

- [ ] **Description claire** des changements
- [ ] **Tests** pour les nouvelles fonctionnalités
- [ ] **Mise à jour de la documentation** si nécessaire
- [ ] **Respect des directives de code**
- [ ] **Toutes les vérifications passent**

### Q. Comment signaler un bogue ?

**R.** Créez une issue sur GitHub avec :

1. **Description du bogue** et comportement attendu
2. **Étapes pour reproduire**
3. **Informations sur l'environnement** (OS, version de Python, etc.)
4. **Messages d'erreur** ou journaux
5. **Exemple minimal** si possible

### Q. Comment proposer une nouvelle fonctionnalité ?

**R.** Ouvrez une issue de demande de fonctionnalité avec :

1. **Description claire** de la fonctionnalité
2. **Cas d'usage** et motivation
3. **Implémentation proposée** (optionnelle)
4. **Exemples** de fonctionnalités similaires

## Dépannage

### Q. Je rencontre des erreurs d'import

**R.** Vérifiez votre chemin Python et votre environnement virtuel :

<div class="termy">

```console
# Check virtual environment is activated
$ which python
/path/to/project/.venv/bin/python

# Check Python path
$ python -c "import sys; print(sys.path)"

# Reinstall in editable mode (for development)
$ pip install -e .
```

</div>

### Q. Problèmes de connexion à la base de données

**R.** Pour les modèles avec base de données, assurez-vous que la base de données est en cours d'exécution :

<div class="termy">

```console
# PostgreSQL template
$ docker-compose up -d postgres  # Start database
$ alembic upgrade head            # Run migrations

# Check connection
$ docker-compose logs postgres
```

</div>

### Q. Fichiers de modèle introuvables

**R.** Cela indique généralement un problème de chemin de modèle :

<div class="termy">

```console
# Check available templates
$ fastkit list-templates

# Check template directory
$ python -c "import fastapi_fastkit; print(fastapi_fastkit.__path__)"

# Reinstall if templates missing
$ pip uninstall fastapi-fastkit
$ pip install fastapi-fastkit
```

</div>

### Q. Les hooks pre-commit échouent

**R.** Installez et lancez les hooks :

<div class="termy">

```console
$ pip install pre-commit
$ pre-commit install
$ pre-commit run --all-files

# Fix formatting issues
$ black src/ tests/
$ isort src/ tests/
```

</div>

### Q. Les tests échouent en CI mais passent localement

**R.** Causes courantes et solutions :

1. **Différences d'environnement** : vérifiez que les versions de Python correspondent
2. **Dépendances manquantes** : assurez-vous que les dépendances de test sont installées
3. **Problèmes de chemin** : utilisez des imports absolus
4. **Problèmes de timing** : ajoutez des attentes appropriées dans les tests asynchrones

<div class="termy">

```console
# Test with same Python version as CI
$ python3.12 -m pytest

# Check for missing dependencies
$ pip install -r requirements-dev.txt

# Run tests in isolated environment
$ tox
```

</div>

## Obtenir de l'aide

### Q. Où puis-je obtenir de l'aide ?

**R.** Plusieurs options pour obtenir de l'aide :

- **GitHub Issues** : pour les bogues et les demandes de fonctionnalités
- **GitHub Discussions** : pour les questions et le soutien communautaire
- **Documentation** : guides utilisateur et tutoriels
- **Exemples de code** : consultez les modèles et tests existants

### Q. Comment me tenir à jour ?

**R.** Suivez les mises à jour du projet :

- **Surveillez le dépôt** sur GitHub
- **Consultez les releases** pour les nouvelles fonctionnalités
- **Lisez le changelog** pour les changements cassants
- **Suivez les bonnes pratiques** dans la documentation

!!! tip "Astuces de pro"
    - Utilisez toujours des environnements virtuels pour les projets Python
    - Maintenez votre installation de FastAPI-fastkit à jour
    - Utilisez `fastkit --help` pour voir les commandes disponibles
    - Consultez la documentation quand vous êtes bloqué
    - N'hésitez pas à poser des questions dans GitHub Discussions

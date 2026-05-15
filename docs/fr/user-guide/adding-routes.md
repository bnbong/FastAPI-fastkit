# Ajouter des routes

Apprenez à ajouter de nouvelles routes d'API à votre projet FastAPI existant.

## Ajout de route basique

### Utiliser la commande `addroute`

La commande `addroute` de FastAPI-fastkit facilite l'ajout de nouvelles routes :

<div class="termy">

```console
$ fastkit addroute users my-awesome-api
                       Adding New Route
┌──────────────────┬──────────────────────────────────────────┐
│ Project          │ my-awesome-api                           │
│ Route Name       │ users                                    │
│ Target Directory │ ~/my-awesome-api                         │
└──────────────────┴──────────────────────────────────────────┘

Do you want to add route 'users' to project 'my-awesome-api'? [Y/n]: y

╭──────────────────────── Info ────────────────────────╮
│ ℹ Updated main.py to include the API router          │
╰──────────────────────────────────────────────────────╯
╭─────────────────────── Success ───────────────────────╮
│ ✨ Successfully added new route 'users' to project    │
│ `my-awesome-api`                                      │
╰───────────────────────────────────────────────────────╯
```

</div>

## Ce qui est créé

Lorsque vous ajoutez une route, FastAPI-fastkit crée automatiquement :

### 1. Fichier de route : `src/api/routes/users.py`

```python
from typing import List
from fastapi import APIRouter, HTTPException, status
from src.schemas.users import User, UserCreate, UserUpdate
from src.crud.users import users_crud

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users():
    """Get all users"""
    return users_crud.get_all()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Create a new user"""
    return users_crud.create(user)

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    """Get a specific user"""
    user = users_crud.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate):
    """Update a user"""
    updated_user = users_crud.update(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """Delete a user"""
    success = users_crud.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
```

### 2. Opérations CRUD : `src/crud/users.py`

```python
from typing import List, Optional
from src.schemas.users import User, UserCreate, UserUpdate

class UsersCRUD:
    def __init__(self):
        self._users: List[User] = []
        self._next_id = 1

    def get_all(self) -> List[User]:
        """Get all users"""
        return self._users

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return next((user for user in self._users if user.id == user_id), None)

    def create(self, user: UserCreate) -> User:
        """Create a new user"""
        new_user = User(
            id=self._next_id,
            title=user.title,
            description=user.description
        )
        self._next_id += 1
        self._users.append(new_user)
        return new_user

    def update(self, user_id: int, user: UserUpdate) -> Optional[User]:
        """Update an existing user"""
        existing_user = self.get_by_id(user_id)
        if existing_user:
            update_data = user.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_user, field, value)
            return existing_user
        return None

    def delete(self, user_id: int) -> bool:
        """Delete a user"""
        user = self.get_by_id(user_id)
        if user:
            self._users.remove(user)
            return True
        return False

users_crud = UsersCRUD()
```

### 3. Schémas Pydantic : `src/schemas/users.py`

```python
from typing import Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    title: str
    description: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True
```

### 4. Enregistrement du routeur

La commande met automatiquement à jour `src/api/api.py` pour inclure le nouveau routeur :

```python
from fastapi import APIRouter
from src.api.routes import items, users

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

## Points d'extrémité d'API générés

Après avoir ajouté la route `users`, vous disposerez de ces points d'extrémité :

| Méthode | Point d'extrémité | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | Récupérer tous les utilisateurs |
| `POST` | `/api/v1/users/` | Créer un nouvel utilisateur |
| `GET` | `/api/v1/users/{user_id}` | Récupérer un utilisateur précis |
| `PUT` | `/api/v1/users/{user_id}` | Mettre à jour un utilisateur |
| `DELETE` | `/api/v1/users/{user_id}` | Supprimer un utilisateur |

## Tester vos nouvelles routes

### 1. Démarrer le serveur

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 2. Consulter la documentation de l'API

Rendez-vous sur [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) pour voir vos nouveaux points d'extrémité dans la documentation interactive.

### 3. Tester avec curl

**Créer un utilisateur :**
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

**Récupérer tous les utilisateurs :**
<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/

[
  {
    "id": 1,
    "title": "John Doe",
    "description": "Software Developer"
  }
]
```

</div>

**Récupérer un utilisateur précis :**
<div class="termy">

```console
$ curl http://127.0.0.1:8000/api/v1/users/1

{
  "id": 1,
  "title": "John Doe",
  "description": "Software Developer"
}
```

</div>

## Personnaliser le code généré

Le code généré est entièrement personnalisable. Voici des modifications courantes :

### 1. Schéma utilisateur enrichi

Modifiez `src/schemas/users.py` pour des données utilisateur plus réalistes :

```python
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str
```

### 2. CRUD enrichi avec validation

Mettez à jour `src/crud/users.py` avec une meilleure validation :

```python
from typing import List, Optional
from datetime import datetime
import hashlib
from src.schemas.users import UserCreate, UserUpdate, UserInDB

class UsersCRUD:
    def __init__(self):
        self._users: List[UserInDB] = []
        self._next_id = 1

    def _hash_password(self, password: str) -> str:
        """Simple password hashing (use bcrypt in production)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        return next((user for user in self._users if user.email == email), None)

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        return next((user for user in self._users if user.username == username), None)

    def create(self, user: UserCreate) -> UserInDB:
        """Create a new user with validation"""
        # Vérifier les doublons
        if self.get_by_email(user.email):
            raise ValueError("Email already registered")
        if self.get_by_username(user.username):
            raise ValueError("Username already taken")

        new_user = UserInDB(
            id=self._next_id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=datetime.now(),
            hashed_password=self._hash_password(user.password)
        )
        self._next_id += 1
        self._users.append(new_user)
        return new_user

users_crud = UsersCRUD()
```

### 3. Route enrichie avec gestion d'erreurs

Mettez à jour `src/api/routes/users.py` avec une meilleure gestion des erreurs :

```python
from typing import List
from fastapi import APIRouter, HTTPException, status
from src.schemas.users import User, UserCreate, UserUpdate
from src.crud.users import users_crud

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Create a new user"""
    try:
        new_user = users_crud.create(user)
        # Retourner l'utilisateur sans son hash de mot de passe
        return User(**new_user.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    """Get a specific user"""
    user = users_crud.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return User(**user.dict())
```

## Ajouter plusieurs routes

Vous pouvez ajouter plusieurs routes pour construire une API complète :

<div class="termy">

```console
# Ajouter d'autres routes de ressources (nom de route d'abord, répertoire du projet ensuite)
$ fastkit addroute products my-awesome-api
$ fastkit addroute orders my-awesome-api
$ fastkit addroute categories my-awesome-api

# Chaque commande crée une structure CRUD complète
```

</div>

Cela crée une API complète avec :

- `/api/v1/users/` — gestion des utilisateurs
- `/api/v1/products/` — catalogue de produits
- `/api/v1/orders/` — traitement des commandes
- `/api/v1/categories/` — gestion des catégories

## Organisation des routes

### Regrouper des points d'extrémité liés

Vous pouvez organiser les routes par domaine :

```python
# src/api/api.py
from fastapi import APIRouter
from src.api.routes import users, products, orders, categories

api_router = APIRouter()

# Gestion des utilisateurs
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["User Management"]
)

# E-commerce
api_router.include_router(
    products.router,
    prefix="/products",
    tags=["E-commerce"]
)
api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["E-commerce"]
)
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["E-commerce"]
)
```

### Ajouter des dépendances de route

Ajoutez l'authentification ou d'autres dépendances :

```python
from fastapi import APIRouter, Depends
from src.core.auth import get_current_user

router = APIRouter()

@router.get("/profile", response_model=User)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return current_user

@router.post("/", response_model=User)
def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return users_crud.create(user)
```

## Bonnes pratiques

### 1. Nommage cohérent

Suivez des conventions de nommage cohérentes :

- **Noms de routes** : utilisez des noms au pluriel (`users`, `products`, `orders`)
- **Noms de schémas** : utilisez le singulier (`User`, `Product`, `Order`)
- **Classes CRUD** : terminez par `CRUD` (`UsersCRUD`, `ProductsCRUD`)

### 2. Gestion des erreurs

Gérez toujours les erreurs proprement :

```python
@router.post("/", response_model=User)
def create_user(user: UserCreate):
    try:
        return users_crud.create(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 3. Documentation

Ajoutez des docstrings complètes :

```python
@router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    """
    Get a specific user by ID.

    Args:
        user_id: The unique identifier for the user

    Returns:
        User: The user object with all details

    Raises:
        HTTPException: 404 if user not found
    """
    user = users_crud.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 4. Tests

Testez toujours vos nouvelles routes :

```python
# tests/test_users.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_create_user():
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "securepassword123"
    }
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]

def test_get_user():
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
```

## Dépannage

### La route n'apparaît pas

Si votre route n'apparaît pas dans la documentation de l'API :

1. **Vérifiez l'enregistrement du routeur** dans `src/api/api.py`
2. **Redémarrez le serveur** après avoir ajouté des routes
3. **Recherchez d'éventuelles erreurs d'import** dans le fichier de route

### Erreurs d'import

Si vous obtenez des erreurs d'import :

1. **Vérifiez que la structure des fichiers** correspond à la disposition attendue
2. **Vérifiez les imports des schémas** dans les fichiers de route et de CRUD
3. **Assurez-vous que tous les fichiers `__init__.py` existent**

### Le serveur ne démarre pas

Si le serveur ne démarre pas après l'ajout de routes :

1. **Recherchez les erreurs de syntaxe** dans les fichiers générés
2. **Vérifiez la compatibilité des schémas** entre les fichiers
3. **Consultez les journaux** pour des messages d'erreur précis

## Étapes suivantes

Maintenant que vous savez ajouter des routes :

1. **[Votre premier projet](../tutorial/first-project.md)** : construire une API de blog complète
2. **[Référence CLI](cli-reference.md)** : découvrir toutes les commandes disponibles
3. **[Utiliser les modèles](using-templates.md)** : explorer les modèles de projet prêts à l'emploi

!!! tip "Astuces de développement de routes"
    - Testez toujours les nouvelles routes dans la documentation interactive (`/docs`)
    - Utilisez des codes d'état HTTP pertinents
    - Implémentez une gestion d'erreurs correcte pour tous les points d'extrémité
    - Gardez les gestionnaires de route simples et déléguez la logique métier aux classes CRUD

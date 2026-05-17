# Routen hinzufügen

Lernen Sie, wie Sie neue API-Routen zu Ihrem bestehenden FastAPI-Projekt hinzufügen.

## Grundlegendes Hinzufügen einer Route

### Den Befehl `addroute` verwenden

Der Befehl `addroute` von FastAPI-fastkit erleichtert das Hinzufügen neuer Routen:

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

## Was wird erstellt

Wenn Sie eine Route hinzufügen, erzeugt FastAPI-fastkit automatisch:

### 1. Routen-Datei: `src/api/routes/users.py`

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

### 2. CRUD-Operationen: `src/crud/users.py`

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

### 3. Pydantic-Schemas: `src/schemas/users.py`

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

### 4. Router-Registrierung

Der Befehl aktualisiert `src/api/api.py` automatisch, um den neuen Router einzubinden:

```python
from fastapi import APIRouter
from src.api.routes import items, users

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

## Generierte API-Endpunkte

Nach dem Hinzufügen der Route `users` stehen Ihnen folgende Endpunkte zur Verfügung:

| Methode | Endpunkt | Beschreibung |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | Alle Nutzer abrufen |
| `POST` | `/api/v1/users/` | Einen neuen Nutzer anlegen |
| `GET` | `/api/v1/users/{user_id}` | Einen bestimmten Nutzer abrufen |
| `PUT` | `/api/v1/users/{user_id}` | Einen Nutzer aktualisieren |
| `DELETE` | `/api/v1/users/{user_id}` | Einen Nutzer löschen |

## Ihre neuen Routen testen

### 1. Server starten

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 2. API-Dokumentation prüfen

Besuchen Sie [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs), um Ihre neuen Endpunkte in der interaktiven Dokumentation zu sehen.

### 3. Mit curl testen

**Einen Nutzer anlegen:**
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

**Alle Nutzer abrufen:**
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

**Einen bestimmten Nutzer abrufen:**
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

## Generierten Code anpassen

Der generierte Code ist vollständig anpassbar. Hier sind häufige Anpassungen:

### 1. Erweitertes Nutzer-Schema

Bearbeiten Sie `src/schemas/users.py` für realistischere Nutzerdaten:

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

### 2. CRUD mit Validierung erweitern

Aktualisieren Sie `src/crud/users.py` um bessere Validierung:

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
        # Check for duplicates
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

### 3. Route mit Fehlerbehandlung erweitern

Aktualisieren Sie `src/api/routes/users.py` um eine bessere Fehlerbehandlung:

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
        # Return user without password hash
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

## Mehrere Routen hinzufügen

Sie können mehrere Routen hinzufügen, um eine vollständige API aufzubauen:

<div class="termy">

```console
# Weitere Ressourcenrouten hinzufügen (zuerst der Routenname, dann das Projektverzeichnis)
$ fastkit addroute products my-awesome-api
$ fastkit addroute orders my-awesome-api
$ fastkit addroute categories my-awesome-api

# Jede davon erzeugt die vollständige CRUD-Struktur
```

</div>

Dies erzeugt eine umfassende API mit:

- `/api/v1/users/` — Nutzerverwaltung
- `/api/v1/products/` — Produktkatalog
- `/api/v1/orders/` — Bestellabwicklung
- `/api/v1/categories/` — Kategorienverwaltung

## Routenorganisation

### Verwandte Endpunkte gruppieren

Sie können Routen nach Domäne organisieren:

```python
# src/api/api.py
from fastapi import APIRouter
from src.api.routes import users, products, orders, categories

api_router = APIRouter()

# User management
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

### Routen-Abhängigkeiten hinzufügen

Fügen Sie Authentifizierung oder andere Abhängigkeiten hinzu:

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

## Best Practices

### 1. Einheitliche Benennung

Halten Sie sich an einheitliche Benennungskonventionen:

- **Routennamen**: Substantive im Plural verwenden (`users`, `products`, `orders`)
- **Schema-Namen**: Singular verwenden (`User`, `Product`, `Order`)
- **CRUD-Klassen**: mit `CRUD` enden (`UsersCRUD`, `ProductsCRUD`)

### 2. Fehlerbehandlung

Behandeln Sie Fehler immer sauber:

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

### 3. Dokumentation

Schreiben Sie ausführliche Docstrings:

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

### 4. Testen

Testen Sie Ihre neuen Routen immer:

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

## Fehlerbehebung

### Route erscheint nicht

Wenn Ihre Route nicht in der API-Dokumentation auftaucht:

1. **Router-Registrierung prüfen** in `src/api/api.py`
2. **Server neu starten** nach dem Hinzufügen von Routen
3. **Auf Import-Fehler** in der Routen-Datei prüfen

### Import-Fehler

Wenn Sie Import-Fehler erhalten:

1. **Dateistruktur prüfen** — sie sollte dem erwarteten Layout entsprechen
2. **Schema-Imports** in Routen- und CRUD-Dateien überprüfen
3. **Sicherstellen, dass alle `__init__.py`-Dateien existieren**

### Server startet nicht

Wenn der Server nach dem Hinzufügen von Routen nicht startet:

1. **Auf Syntaxfehler** in den generierten Dateien prüfen
2. **Schema-Kompatibilität** zwischen Dateien überprüfen
3. **Logs prüfen** auf konkrete Fehlermeldungen

## Nächste Schritte

Jetzt, da Sie Routen hinzufügen können:

1. **[Ihr erstes Projekt](../tutorial/first-project.md)**: bauen Sie eine vollständige Blog-API
2. **[CLI-Referenz](cli-reference.md)**: lernen Sie alle verfügbaren Befehle
3. **[Vorlagen verwenden](using-templates.md)**: erkunden Sie vorgefertigte Projektvorlagen

!!! tip "Tipps zur Routenentwicklung"
    - Testen Sie neue Routen immer in der interaktiven Doku (`/docs`)
    - Verwenden Sie aussagekräftige HTTP-Statuscodes
    - Implementieren Sie eine ordentliche Fehlerbehandlung für alle Endpunkte
    - Halten Sie Routen-Handler schlank und delegieren Sie Geschäftslogik an CRUD-Klassen

# Añadir rutas

Aprende a añadir nuevas rutas de API a un proyecto FastAPI existente.

## Añadir una ruta básica

### Usar el comando `addroute`

El comando `addroute` de FastAPI-fastkit facilita añadir nuevas rutas:

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

## Qué se crea

Cuando añades una ruta, FastAPI-fastkit crea automáticamente:

### 1. Archivo de ruta: `src/api/routes/users.py`

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

### 2. Operaciones CRUD: `src/crud/users.py`

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

### 3. Esquemas Pydantic: `src/schemas/users.py`

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

### 4. Registro del router

El comando actualiza automáticamente `src/api/api.py` para incluir el nuevo router:

```python
from fastapi import APIRouter
from src.api.routes import items, users

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

## Endpoints de API generados

Tras añadir la ruta `users`, tendrás estos endpoints:

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/users/` | Obtener todos los usuarios |
| `POST` | `/api/v1/users/` | Crear un usuario nuevo |
| `GET` | `/api/v1/users/{user_id}` | Obtener un usuario concreto |
| `PUT` | `/api/v1/users/{user_id}` | Actualizar un usuario |
| `DELETE` | `/api/v1/users/{user_id}` | Eliminar un usuario |

## Probar las nuevas rutas

### 1. Iniciar el servidor

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 2. Comprobar la documentación de la API

Entra en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para ver tus nuevos endpoints en la documentación interactiva.

### 3. Probar con curl

**Crear un usuario:**
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

**Obtener todos los usuarios:**
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

**Obtener un usuario concreto:**
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

## Personalizar el código generado

El código generado se puede personalizar por completo. Algunas modificaciones habituales:

### 1. Esquema de usuario ampliado

Modifica `src/schemas/users.py` para datos de usuario más realistas:

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

### 2. CRUD con validación

Actualiza `src/crud/users.py` con una validación más cuidada:

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
        # Comprobar duplicados
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

### 3. Ruta con manejo de errores

Actualiza `src/api/routes/users.py` con un mejor manejo de errores:

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
        # Devolver el usuario sin el hash de la contraseña
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

## Añadir varias rutas

Puedes añadir varias rutas para construir una API completa:

<div class="termy">

```console
# Añadir más rutas de recursos (nombre de ruta primero, directorio del proyecto después)
$ fastkit addroute products my-awesome-api
$ fastkit addroute orders my-awesome-api
$ fastkit addroute categories my-awesome-api

# Cada una crea la estructura CRUD completa
```

</div>

Esto crea una API completa con:

- `/api/v1/users/` - Gestión de usuarios
- `/api/v1/products/` - Catálogo de productos
- `/api/v1/orders/` - Procesamiento de pedidos
- `/api/v1/categories/` - Gestión de categorías

## Organización de las rutas

### Agrupar endpoints relacionados

Puedes organizar las rutas por dominio:

```python
# src/api/api.py
from fastapi import APIRouter
from src.api.routes import users, products, orders, categories

api_router = APIRouter()

# Gestión de usuarios
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

### Añadir dependencias a las rutas

Añade autenticación u otras dependencias:

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

## Buenas prácticas

### 1. Nombres consistentes

Sigue convenciones de nombres consistentes:

- **Nombres de ruta**: usa sustantivos en plural (`users`, `products`, `orders`)
- **Nombres de esquema**: usa singular (`User`, `Product`, `Order`)
- **Clases CRUD**: termina con `CRUD` (`UsersCRUD`, `ProductsCRUD`)

### 2. Manejo de errores

Maneja los errores siempre con cuidado:

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

### 3. Documentación

Añade docstrings completos:

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

### 4. Pruebas

Prueba siempre tus nuevas rutas:

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

## Solución de problemas

### La ruta no aparece

Si tu ruta no aparece en la documentación de la API:

1. **Comprueba el registro del router** en `src/api/api.py`
2. **Reinicia el servidor** tras añadir rutas
3. **Comprueba si hay errores de import** en el archivo de la ruta

### Errores de import

Si recibes errores de import:

1. **Comprueba que la estructura de archivos** coincide con la esperada
2. **Verifica los imports de esquemas** en los archivos de ruta y CRUD
3. **Asegúrate de que existen todos los `__init__.py`**

### El servidor no arranca

Si el servidor no arranca tras añadir rutas:

1. **Comprueba errores de sintaxis** en los archivos generados
2. **Verifica la compatibilidad de esquemas** entre archivos
3. **Revisa los logs** buscando mensajes de error concretos

## Próximos pasos

Ahora que sabes añadir rutas:

1. **[Tu primer proyecto](../tutorial/first-project.md)**: Construye una API de blog completa
2. **[Referencia de la CLI](cli-reference.md)**: Aprende todos los comandos disponibles
3. **[Usar plantillas](using-templates.md)**: Explora plantillas de proyecto ya preparadas

!!! tip "Consejos para desarrollar rutas"
    - Prueba siempre las rutas nuevas en la documentación interactiva (`/docs`)
    - Usa códigos de estado HTTP con significado
    - Implementa manejo de errores adecuado en todos los endpoints
    - Mantén los handlers simples y delega la lógica de negocio a las clases CRUD

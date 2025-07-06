# Adding Routes

Learn how to add new API routes to your existing FastAPI project.

## Basic Route Addition

### Using the `addroute` Command

FastAPI-fastkit's `addroute` command makes it easy to add new routes:

<div class="termy">

```console
$ fastkit addroute my-awesome-api users
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

## What Gets Created

When you add a route, FastAPI-fastkit automatically creates:

### 1. Route File: `src/api/routes/users.py`

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

### 2. CRUD Operations: `src/crud/users.py`

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

### 3. Pydantic Schemas: `src/schemas/users.py`

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

### 4. Router Registration

The command automatically updates `src/api/api.py` to include the new router:

```python
from fastapi import APIRouter
from src.api.routes import items, users

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

## Generated API Endpoints

After adding the `users` route, you'll have these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | Get all users |
| `POST` | `/api/v1/users/` | Create a new user |
| `GET` | `/api/v1/users/{user_id}` | Get a specific user |
| `PUT` | `/api/v1/users/{user_id}` | Update a user |
| `DELETE` | `/api/v1/users/{user_id}` | Delete a user |

## Testing Your New Routes

### 1. Start the Server

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 2. Check API Documentation

Visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to see your new endpoints in the interactive documentation.

### 3. Test with curl

**Create a user:**
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

**Get all users:**
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

**Get a specific user:**
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

## Customizing Generated Code

The generated code is fully customizable. Here are common modifications:

### 1. Enhanced User Schema

Modify `src/schemas/users.py` for more realistic user data:

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

### 2. Enhanced CRUD with Validation

Update `src/crud/users.py` with better validation:

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

### 3. Enhanced Route with Error Handling

Update `src/api/routes/users.py` with better error handling:

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

## Adding Multiple Routes

You can add multiple routes to build a complete API:

<div class="termy">

```console
# Add more resource routes
$ fastkit addroute my-awesome-api products
$ fastkit addroute my-awesome-api orders
$ fastkit addroute my-awesome-api categories

# Each creates the full CRUD structure
```

</div>

This creates a comprehensive API with:
- `/api/v1/users/` - User management
- `/api/v1/products/` - Product catalog
- `/api/v1/orders/` - Order processing
- `/api/v1/categories/` - Category management

## Route Organization

### Grouping Related Endpoints

You can organize routes by domain:

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

### Adding Route Dependencies

Add authentication or other dependencies:

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

### 1. Consistent Naming

Follow consistent naming conventions:
- **Route names**: Use plural nouns (`users`, `products`, `orders`)
- **Schema names**: Use singular (`User`, `Product`, `Order`)
- **CRUD classes**: End with `CRUD` (`UsersCRUD`, `ProductsCRUD`)

### 2. Error Handling

Always handle errors gracefully:

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

Add comprehensive docstrings:

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

### 4. Testing

Always test your new routes:

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

## Troubleshooting

### Route Not Appearing

If your route doesn't appear in the API documentation:

1. **Check router registration** in `src/api/api.py`
2. **Restart the server** after adding routes
3. **Check for import errors** in the route file

### Import Errors

If you get import errors:

1. **Check file structure** matches the expected layout
2. **Verify schema imports** in route and CRUD files
3. **Ensure all `__init__.py` files exist**

### Server Won't Start

If the server fails to start after adding routes:

1. **Check syntax errors** in generated files
2. **Verify schema compatibility** between files
3. **Check logs** for specific error messages

## Next Steps

Now that you know how to add routes:

1. **[Your First Project](../tutorial/first-project.md)**: Build a complete blog API
2. **[CLI Reference](cli-reference.md)**: Learn all available commands
3. **[Using Templates](using-templates.md)**: Explore pre-built project templates

!!! tip "Route Development Tips"
    - Always test new routes in the interactive docs (`/docs`)
    - Use meaningful HTTP status codes
    - Implement proper error handling for all endpoints
    - Keep route handlers simple and delegate business logic to CRUD classes

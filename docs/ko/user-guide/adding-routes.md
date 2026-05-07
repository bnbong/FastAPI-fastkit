# 라우트 추가

기존 FastAPI 프로젝트에 새 API 라우트를 추가하는 방법을 안내합니다.

## 기본 라우트 추가

### `addroute` 명령 사용

FastAPI-fastkit의 `addroute` 명령을 쓰면 새 라우트를 간편하게 추가할 수 있습니다:

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

## 무엇이 만들어지나

라우트를 추가하면 FastAPI-fastkit이 다음 항목을 자동으로 만들어 줍니다:

### 1. 라우트 파일: `src/api/routes/users.py`

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

### 2. CRUD 작업: `src/crud/users.py`

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

### 3. Pydantic 스키마: `src/schemas/users.py`

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

### 4. 라우터 등록

명령은 `src/api/api.py` 도 자동으로 갱신해 새 라우터를 포함시킵니다:

```python
from fastapi import APIRouter
from src.api.routes import items, users

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

## 생성되는 API 엔드포인트

`users` 라우트를 추가하면 다음 엔드포인트들이 만들어집니다:

| 메서드 | 엔드포인트 | 설명 |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | 모든 사용자 조회 |
| `POST` | `/api/v1/users/` | 새 사용자 생성 |
| `GET` | `/api/v1/users/{user_id}` | 특정 사용자 조회 |
| `PUT` | `/api/v1/users/{user_id}` | 사용자 갱신 |
| `DELETE` | `/api/v1/users/{user_id}` | 사용자 삭제 |

## 새 라우트 테스트하기

### 1. 서버 시작

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 2. API 문서 확인

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) 에 접속해 인터랙티브 문서에서 새 엔드포인트들을 확인하세요.

### 3. curl 로 테스트

**사용자 생성:**
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

**모든 사용자 조회:**
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

**특정 사용자 조회:**
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

## 생성된 코드 커스터마이즈하기

생성된 코드는 자유롭게 수정할 수 있습니다. 자주 하는 변경들을 소개합니다:

### 1. 향상된 User 스키마

좀 더 현실적인 사용자 데이터를 위해 `src/schemas/users.py` 를 수정하세요:

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

### 2. 검증을 강화한 CRUD

검증 로직을 더 갖춘 `src/crud/users.py` 로 갱신하세요:

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

### 3. 에러 처리를 개선한 라우트

에러 처리를 더 갖춘 `src/api/routes/users.py` 로 갱신하세요:

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

## 여러 라우트 추가하기

여러 라우트를 추가해 구조가 갖춰진 API를 만들 수 있습니다:

<div class="termy">

```console
# 추가 리소스 라우트 생성
$ fastkit addroute my-awesome-api products
$ fastkit addroute my-awesome-api orders
$ fastkit addroute my-awesome-api categories

# 각각이 전체 CRUD 구조를 만들어 줍니다
```

</div>

이렇게 하면 다음과 같은 종합적인 API 구성이 완성됩니다:

- `/api/v1/users/` - 사용자 관리
- `/api/v1/products/` - 상품 카탈로그
- `/api/v1/orders/` - 주문 처리
- `/api/v1/categories/` - 카테고리 관리

## 라우트 구성

### 관련 엔드포인트 묶기

라우트를 도메인 단위로 정리할 수 있습니다:

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

### 라우트 의존성 추가

인증 등 의존성을 추가할 수 있습니다:

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

## 모범 사례

### 1. 일관된 명명

명명 규칙을 일관되게 유지하세요:

- **라우트 이름**: 복수 명사 사용 (`users`, `products`, `orders`)
- **스키마 이름**: 단수 사용 (`User`, `Product`, `Order`)
- **CRUD 클래스**: 끝에 `CRUD` 붙이기 (`UsersCRUD`, `ProductsCRUD`)

### 2. 에러 처리

항상 에러를 우아하게 처리하세요:

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

### 3. 문서화

자세한 docstring 을 추가하세요:

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

### 4. 테스트

새로 추가한 라우트는 항상 테스트하세요:

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

## 문제 해결

### 라우트가 보이지 않을 때

API 문서에 라우트가 나타나지 않는다면:

1. `src/api/api.py` 에서 **라우터 등록을 확인**하세요
2. 라우트 추가 후 **서버를 재시작**하세요
3. 라우트 파일에 **import 오류가 없는지 확인**하세요

### Import 오류

import 오류가 발생한다면:

1. **파일 구조**가 기대 레이아웃과 일치하는지 확인하세요
2. 라우트와 CRUD 파일의 **스키마 import 를 검증**하세요
3. **모든 `__init__.py` 파일이 존재**하는지 확인하세요

### 서버가 시작되지 않을 때

라우트 추가 후 서버가 시작되지 않는다면:

1. 생성된 파일에 **문법 오류가 없는지 확인**하세요
2. 파일 간 **스키마 호환성을 검증**하세요
3. 구체적인 에러 메시지를 보려면 **로그를 확인**하세요

## 다음 단계

이제 라우트 추가 방법을 알았으니:

1. **[첫 프로젝트 만들기](../tutorial/first-project.md)**: 완전한 블로그 API 구축
2. **[CLI 레퍼런스](cli-reference.md)**: 사용 가능한 모든 명령어 학습
3. **[템플릿 사용하기](using-templates.md)**: 사전 구축 프로젝트 템플릿 살펴보기

!!! tip "라우트 개발 팁"
    - 새 라우트는 항상 인터랙티브 문서 (`/docs`) 에서 테스트하세요
    - 의미 있는 HTTP 상태 코드를 사용하세요
    - 모든 엔드포인트에 적절한 에러 처리를 구현하세요
    - 라우트 핸들러는 단순하게 유지하고 비즈니스 로직은 CRUD 클래스에 위임하세요

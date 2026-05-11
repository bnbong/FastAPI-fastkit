# ルートの追加

既存の FastAPI プロジェクトに新しい API ルートを追加する方法を学びます。

## 基本的なルート追加

### `addroute` コマンドを使う

FastAPI-fastkit の `addroute` コマンドは、新しいルートの追加を簡単にします:

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

## 何が作成されるか

ルートを追加すると、FastAPI-fastkit は次のファイルや設定を自動で生成します:

### 1. ルートファイル: `src/api/routes/users.py`

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

### 2. CRUD 操作: `src/crud/users.py`

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

### 3. Pydantic スキーマ: `src/schemas/users.py`

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

### 4. ルーターの登録

このコマンドは `src/api/api.py` を自動で更新し、新しいルーターを取り込みます:

```python
from fastapi import APIRouter
from src.api.routes import items, users

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

## 生成される API エンドポイント

`users` ルートを追加すると、次のエンドポイントが使えるようになります:

| メソッド | エンドポイント | 説明 |
|---|---|---|
| `GET` | `/api/v1/users/` | すべてのユーザーを取得 |
| `POST` | `/api/v1/users/` | 新しいユーザーを作成 |
| `GET` | `/api/v1/users/{user_id}` | 特定のユーザーを取得 |
| `PUT` | `/api/v1/users/{user_id}` | ユーザーを更新 |
| `DELETE` | `/api/v1/users/{user_id}` | ユーザーを削除 |

## 新しいルートのテスト

### 1. サーバーの起動

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 2. API ドキュメントの確認

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) にアクセスして、対話型ドキュメントで新しいエンドポイントを確認しましょう。

### 3. curl でのテスト

**ユーザーを作成:**
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

**すべてのユーザーを取得:**
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

**特定のユーザーを取得:**
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

## 生成コードのカスタマイズ

生成されたコードは完全にカスタマイズ可能です。よく行う変更例を示します:

### 1. ユーザースキーマの拡張

`src/schemas/users.py` をより実用的なユーザーデータ向けに変更します:

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

### 2. 検証つきの CRUD 拡張

`src/crud/users.py` を、より洗練された検証で更新します:

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

### 3. エラーハンドリングを強化したルート

`src/api/routes/users.py` を、より丁寧なエラーハンドリングで更新します:

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

## 複数のルートを追加する

複数のルートを追加して、本格的な API に育てていくこともできます:

<div class="termy">

```console
# リソースルートを追加 (ルート名が先、プロジェクトディレクトリが後)
$ fastkit addroute products my-awesome-api
$ fastkit addroute orders my-awesome-api
$ fastkit addroute categories my-awesome-api

# それぞれが完全な CRUD 構造を生成します
```

</div>

これで次のような包括的な API が生成されます:

- `/api/v1/users/` - ユーザー管理
- `/api/v1/products/` - 商品カタログ
- `/api/v1/orders/` - 注文処理
- `/api/v1/categories/` - カテゴリ管理

## ルートの整理

### 関連エンドポイントのグループ化

ドメインごとにルートを整理できます:

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

### ルートに依存性を追加

認証などの依存性を追加します:

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

## ベストプラクティス

### 1. 一貫した命名

一貫した命名規則に従いましょう:

- **ルート名**: 複数形の名詞を使用 (`users`、`products`、`orders`)
- **スキーマ名**: 単数形を使用 (`User`、`Product`、`Order`)
- **CRUD クラス**: 末尾を `CRUD` に統一 (`UsersCRUD`、`ProductsCRUD`)

### 2. エラーハンドリング

常にエラーを丁寧に扱いましょう:

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

### 3. ドキュメント

充実した docstring を書きましょう:

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

### 4. テスト

新しいルートには必ずテストを書きましょう:

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

## トラブルシューティング

### ルートが表示されない

API ドキュメントにルートが表示されない場合:

1. `src/api/api.py` の **ルーター登録を確認**
2. ルート追加後に **サーバーを再起動**
3. ルートファイルに **インポートエラーがないか確認**

### インポートエラー

インポートエラーが発生する場合:

1. **ファイル構造** が想定どおりか確認
2. ルートと CRUD ファイルの **スキーマインポート** を確認
3. **すべての `__init__.py` ファイルが存在するか確認**

### サーバーが起動しない

ルート追加後にサーバーが起動しない場合:

1. 生成ファイルに **構文エラーがないか確認**
2. ファイル間の **スキーマ互換性** を確認
3. 具体的なエラーメッセージについて **ログを確認**

## 次のステップ

ルートの追加方法を理解できたら:

1. **[最初のプロジェクト](../tutorial/first-project.md)**: 完全なブログ API を構築
2. **[CLI リファレンス](cli-reference.md)**: 利用可能なすべてのコマンドを学ぶ
3. **[テンプレートの利用](using-templates.md)**: 事前構築済みのプロジェクトテンプレートを試す

!!! tip "ルート開発のヒント"
    - 新しいルートは常に対話型ドキュメント (`/docs`) でテストしましょう
    - 意味のある HTTP ステータスコードを使いましょう
    - すべてのエンドポイントに適切なエラーハンドリングを実装しましょう
    - ルートハンドラはシンプルに保ち、ビジネスロジックは CRUD クラスへ委譲しましょう

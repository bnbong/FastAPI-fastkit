# 添加路由

学习如何向已有的 FastAPI 项目添加新的 API 路由。

## 基本的路由添加

### 使用 `addroute` 命令

FastAPI-fastkit 的 `addroute` 命令让添加新路由变得很简单：

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

## 会生成什么

当您添加一个路由时,FastAPI-fastkit 会自动创建：

### 1. 路由文件:`src/api/routes/users.py`

```python
from typing import List
from fastapi import APIRouter, HTTPException, status
from src.schemas.users import User, UserCreate, UserUpdate
from src.crud.users import users_crud

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users():
    """获取所有用户"""
    return users_crud.get_all()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """创建新用户"""
    return users_crud.create(user)

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    """获取指定用户"""
    user = users_crud.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user: UserUpdate):
    """更新用户"""
    updated_user = users_crud.update(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    """删除用户"""
    success = users_crud.delete(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
```

### 2. CRUD 操作:`src/crud/users.py`

```python
from typing import List, Optional
from src.schemas.users import User, UserCreate, UserUpdate

class UsersCRUD:
    def __init__(self):
        self._users: List[User] = []
        self._next_id = 1

    def get_all(self) -> List[User]:
        """获取所有用户"""
        return self._users

    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据 ID 获取用户"""
        return next((user for user in self._users if user.id == user_id), None)

    def create(self, user: UserCreate) -> User:
        """创建新用户"""
        new_user = User(
            id=self._next_id,
            title=user.title,
            description=user.description
        )
        self._next_id += 1
        self._users.append(new_user)
        return new_user

    def update(self, user_id: int, user: UserUpdate) -> Optional[User]:
        """更新已有用户"""
        existing_user = self.get_by_id(user_id)
        if existing_user:
            update_data = user.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_user, field, value)
            return existing_user
        return None

    def delete(self, user_id: int) -> bool:
        """删除用户"""
        user = self.get_by_id(user_id)
        if user:
            self._users.remove(user)
            return True
        return False

users_crud = UsersCRUD()
```

### 3. Pydantic 模式:`src/schemas/users.py`

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

### 4. 注册路由

该命令会自动更新 `src/api/api.py`,把新路由器纳入其中:

```python
from fastapi import APIRouter
from src.api.routes import items, users

api_router = APIRouter()

api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
```

## 生成的 API 端点

添加 `users` 路由后,您将拥有以下端点:

| 方法 | 端点 | 描述 |
|--------|----------|-------------|
| `GET` | `/api/v1/users/` | 获取所有用户 |
| `POST` | `/api/v1/users/` | 创建新用户 |
| `GET` | `/api/v1/users/{user_id}` | 获取指定用户 |
| `PUT` | `/api/v1/users/{user_id}` | 更新用户 |
| `DELETE` | `/api/v1/users/{user_id}` | 删除用户 |

## 测试新路由

### 1. 启动服务器

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 2. 查看 API 文档

访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs),在交互式文档中查看新端点。

### 3. 使用 curl 测试

**创建用户:**
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

**获取所有用户:**
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

**获取指定用户:**
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

## 定制生成的代码

生成出来的代码可以完全按需定制。下面是一些常见的扩展方式：

### 1. 扩展的用户模式

修改 `src/schemas/users.py`,加入更贴近真实场景的字段：

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

### 2. 增强 CRUD,加入校验

更新 `src/crud/users.py`,加入更完善的校验：

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
        """简单的密码哈希示例（生产环境请使用 bcrypt）"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        """根据邮箱获取用户"""
        return next((user for user in self._users if user.email == email), None)

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        """根据用户名获取用户"""
        return next((user for user in self._users if user.username == username), None)

    def create(self, user: UserCreate) -> UserInDB:
        """带校验地创建新用户"""
        # 检查是否存在重复用户
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

### 3. 加入错误处理的路由

更新 `src/api/routes/users.py`,加入更完善的错误处理：

```python
from typing import List
from fastapi import APIRouter, HTTPException, status
from src.schemas.users import User, UserCreate, UserUpdate
from src.crud.users import users_crud

router = APIRouter()

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """创建新用户"""
    try:
        new_user = users_crud.create(user)
        # 返回时去掉密码哈希
        return User(**new_user.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    """获取指定用户"""
    user = users_crud.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return User(**user.dict())
```

## 同时添加多个路由

您可以连续添加多个路由,构建一个完整的 API:

<div class="termy">

```console
# 添加更多资源路由（先写路由名,再写项目目录）
$ fastkit addroute products my-awesome-api
$ fastkit addroute orders my-awesome-api
$ fastkit addroute categories my-awesome-api

# 每条命令都会生成一整套 CRUD 结构
```

</div>

由此可获得一个更完整的 API:

- `/api/v1/users/` —— 用户管理
- `/api/v1/products/` —— 商品目录
- `/api/v1/orders/` —— 订单处理
- `/api/v1/categories/` —— 类目管理

## 路由组织

### 按相关性分组端点

可按领域组织路由:

```python
# src/api/api.py
from fastapi import APIRouter
from src.api.routes import users, products, orders, categories

api_router = APIRouter()

# 用户管理
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["User Management"]
)

# 电商相关
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

### 为路由添加依赖

为路由添加认证或其他依赖：

```python
from fastapi import APIRouter, Depends
from src.core.auth import get_current_user

router = APIRouter()

@router.get("/profile", response_model=User)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户的个人资料"""
    return current_user

@router.post("/", response_model=User)
def create_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user)
):
    """创建新用户（仅限管理员）"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return users_crud.create(user)
```

## 最佳实践

### 1. 命名一致

遵循一致的命名约定:

- **路由名称**:使用复数名词(`users`、`products`、`orders`)
- **模式名称**:使用单数(`User`、`Product`、`Order`)
- **CRUD 类**:以 `CRUD` 结尾(`UsersCRUD`、`ProductsCRUD`)

### 2. 错误处理

始终优雅地处理错误:

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

### 3. 文档

建议为接口补充清晰的 docstring：

```python
@router.get("/{user_id}", response_model=User)
def read_user(user_id: int):
    """
    根据 ID 获取指定用户。

    Args:
        user_id：用户的唯一标识

    Returns:
        User：包含完整信息的用户对象

    Raises:
        HTTPException：当用户不存在时返回 404
    """
    user = users_crud.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 4. 测试

始终为新路由编写测试:

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

## 故障排查

### 路由未出现

如果您的路由没有出现在 API 文档中:

1. **检查路由器是否在 `src/api/api.py` 中注册**
2. **添加路由后重启服务器**
3. **检查路由文件中的导入错误**

### 导入错误

如果出现导入错误:

1. **核对文件结构是否符合预期布局**
2. **检查路由文件与 CRUD 文件中的模式导入**
3. **确保所有 `__init__.py` 文件都存在**

### 服务器无法启动

如果添加路由后服务器无法启动:

1. **检查生成文件是否存在语法错误**
2. **检查文件之间的模式是否兼容**
3. **查看日志获取具体的错误信息**

## 下一步

学会添加路由后:

1. **[您的第一个项目](../tutorial/first-project.md)**:构建完整的博客 API
2. **[CLI 参考](cli-reference.md)**:学习所有可用命令
3. **[使用模板](using-templates.md)**:探索预构建的项目模板

!!! tip "路由开发小贴士"
    - 始终在交互式文档(`/docs`)中测试新路由
    - 使用合适的 HTTP 状态码
    - 为所有端点实现完善的错误处理
    - 让路由处理器保持简单,把业务逻辑委托给 CRUD 类

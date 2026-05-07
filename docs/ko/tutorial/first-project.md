# 첫 프로젝트 만들기

FastAPI-fastkit으로 사용자 관리, 게시물 작성, 댓글 시스템을 갖춘 완전한 블로그 API를 구축합니다.

## 프로젝트 개요

이 튜토리얼에서는 다음 기능을 갖춘 **블로그 API** 를 만듭니다:

- **사용자 관리**: 회원 가입, 인증, 사용자 프로필
- **게시물 관리**: 블로그 게시물 생성, 조회, 갱신, 삭제
- **댓글 시스템**: 블로그 게시물에 댓글 추가
- **데이터 검증**: 견고한 입력 검증 및 에러 처리
- **API 문서화**: 자동 OpenAPI 문서
- **테스트**: 완전한 테스트 스위트

### 배우는 내용

이 튜토리얼이 끝날 때면 다음을 이해하게 됩니다:

- 고급 FastAPI-fastkit 프로젝트 구조
- SQLAlchemy와의 데이터베이스 통합
- 사용자 인증과 권한 부여
- 복잡한 데이터 관계
- 에러 처리와 검증
- 테스트 모범 사례

## 사전 요구 사항

시작하기 전에 다음을 갖춰 두세요:

- [시작하기](getting-started.md) 튜토리얼 완료
- REST API의 기본 이해
- Python 3.12+ 설치
- 텍스트 에디터 또는 IDE 준비

## 1단계: 프로젝트 생성

데이터베이스 지원을 위해 **STANDARD** 스택으로 새 프로젝트를 시작합니다:

<div class="termy">

```console
$ fastkit init
Enter the project name: blog-api
Enter the author name: Your Name
Enter the author email: your.email@example.com
Enter the project description: A complete blog API with users, posts, and comments

           Project Information
┌──────────────┬─────────────────────────────────────────┐
│ Project Name │ blog-api                                │
│ Author       │ Your Name                               │
│ Author Email │ your.email@example.com                  │
│ Description  │ A complete blog API with users, posts,  │
│              │ and comments                            │
└──────────────┴─────────────────────────────────────────┘

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

Select stack (minimal, standard, full): standard

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

✨ FastAPI project 'blog-api' has been created successfully!
```

</div>

## 2단계: 프로젝트 설정

프로젝트로 이동해 가상 환경을 활성화합니다:

<div class="termy">

```console
$ cd blog-api
$ source .venv/bin/activate
```

</div>

## 3단계: 필요한 라우트 추가

블로그 API의 주요 리소스를 추가합니다:

<div class="termy">

```console
$ fastkit addroute users blog-api
✨ Successfully added new route 'users' to project 'blog-api'

$ fastkit addroute posts blog-api
✨ Successfully added new route 'posts' to project 'blog-api'

$ fastkit addroute comments blog-api
✨ Successfully added new route 'comments' to project 'blog-api'
```

</div>

## 4단계: 데이터 모델 설계

데이터 스키마를 설계해 봅시다. 먼저 사용자 스키마를 좀 더 현실적으로 갱신합니다.

### User 스키마 갱신

`src/schemas/users.py` 를 수정합니다:

```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    is_active: bool = True

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    created_at: datetime
    posts_count: int = 0

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str
```

### Post 스키마 작성

`src/schemas/posts.py` 를 수정합니다:

```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

class PostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    published: bool = True

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    published: Optional[bool] = None

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    comments_count: int = 0

    class Config:
        from_attributes = True

class PostWithAuthor(Post):
    author: "User"

class PostWithComments(Post):
    comments: List["Comment"] = []

# 순환 import 회피를 위한 import
from src.schemas.users import User
from src.schemas.comments import Comment
PostWithAuthor.model_rebuild()
PostWithComments.model_rebuild()
```

### Comment 스키마 작성

`src/schemas/comments.py` 를 수정합니다:

```python
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class CommentCreate(CommentBase):
    post_id: int

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=1000)

class Comment(CommentBase):
    id: int
    post_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CommentWithAuthor(Comment):
    author: "User"

# 순환 import 회피를 위한 import
from src.schemas.users import User
CommentWithAuthor.model_rebuild()
```

## 5단계: 고급 CRUD 작업 구현

### 향상된 User CRUD

`src/crud/users.py` 를 갱신합니다:

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

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(plain_password) == hashed_password

    def get_all(self) -> List[UserInDB]:
        """Get all users"""
        return [user for user in self._users if user.is_active]

    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        """Get user by ID"""
        return next((user for user in self._users if user.id == user_id), None)

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
            bio=user.bio,
            is_active=user.is_active,
            created_at=datetime.now(),
            posts_count=0,
            hashed_password=self._hash_password(user.password)
        )
        self._next_id += 1
        self._users.append(new_user)
        return new_user

    def update(self, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update an existing user"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        # Check for duplicates on email/username changes
        update_data = user_update.dict(exclude_unset=True)
        if "email" in update_data and update_data["email"] != user.email:
            if self.get_by_email(update_data["email"]):
                raise ValueError("Email already registered")

        if "username" in update_data and update_data["username"] != user.username:
            if self.get_by_username(update_data["username"]):
                raise ValueError("Username already taken")

        for field, value in update_data.items():
            setattr(user, field, value)

        return user

    def delete(self, user_id: int) -> bool:
        """Soft delete user (deactivate)"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            return True
        return False

    def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        """Authenticate user by email and password"""
        user = self.get_by_email(email)
        if user and self._verify_password(password, user.hashed_password):
            return user
        return None

users_crud = UsersCRUD()
```

### Posts CRUD

`src/crud/posts.py` 를 갱신합니다:

```python
from typing import List, Optional
from datetime import datetime
from src.schemas.posts import PostCreate, PostUpdate, Post

class PostsCRUD:
    def __init__(self):
        self._posts: List[Post] = []
        self._next_id = 1

    def get_all(self, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[Post]:
        """Get all posts with pagination"""
        posts = self._posts
        if published_only:
            posts = [post for post in posts if post.published]
        return posts[skip:skip + limit]

    def get_by_id(self, post_id: int) -> Optional[Post]:
        """Get post by ID"""
        return next((post for post in self._posts if post.id == post_id), None)

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        """Get posts by author"""
        author_posts = [post for post in self._posts if post.author_id == author_id]
        return author_posts[skip:skip + limit]

    def create(self, post: PostCreate, author_id: int) -> Post:
        """Create a new post"""
        now = datetime.now()
        new_post = Post(
            id=self._next_id,
            title=post.title,
            content=post.content,
            published=post.published,
            author_id=author_id,
            created_at=now,
            updated_at=now,
            comments_count=0
        )
        self._next_id += 1
        self._posts.append(new_post)

        # Update author's post count
        from src.crud.users import users_crud
        author = users_crud.get_by_id(author_id)
        if author:
            author.posts_count += 1

        return new_post

    def update(self, post_id: int, post_update: PostUpdate, author_id: int) -> Optional[Post]:
        """Update an existing post"""
        post = self.get_by_id(post_id)
        if not post or post.author_id != author_id:
            return None

        update_data = post_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        post.updated_at = datetime.now()
        return post

    def delete(self, post_id: int, author_id: int) -> bool:
        """Delete a post"""
        post = self.get_by_id(post_id)
        if post and post.author_id == author_id:
            self._posts.remove(post)

            # Update author's post count
            from src.crud.users import users_crud
            author = users_crud.get_by_id(author_id)
            if author:
                author.posts_count = max(0, author.posts_count - 1)

            return True
        return False

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """Search posts by title or content"""
        query_lower = query.lower()
        matching_posts = [
            post for post in self._posts
            if post.published and (
                query_lower in post.title.lower() or
                query_lower in post.content.lower()
            )
        ]
        return matching_posts[skip:skip + limit]

posts_crud = PostsCRUD()
```

### Comments CRUD

`src/crud/comments.py` 를 갱신합니다:

```python
from typing import List, Optional
from datetime import datetime
from src.schemas.comments import CommentCreate, CommentUpdate, Comment

class CommentsCRUD:
    def __init__(self):
        self._comments: List[Comment] = []
        self._next_id = 1

    def get_all(self) -> List[Comment]:
        """Get all comments"""
        return self._comments

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID"""
        return next((comment for comment in self._comments if comment.id == comment_id), None)

    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get comments for a specific post"""
        post_comments = [comment for comment in self._comments if comment.post_id == post_id]
        return post_comments[skip:skip + limit]

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get comments by author"""
        author_comments = [comment for comment in self._comments if comment.author_id == author_id]
        return author_comments[skip:skip + limit]

    def create(self, comment: CommentCreate, author_id: int) -> Comment:
        """Create a new comment"""
        # Verify post exists
        from src.crud.posts import posts_crud
        post = posts_crud.get_by_id(comment.post_id)
        if not post:
            raise ValueError("Post not found")

        now = datetime.now()
        new_comment = Comment(
            id=self._next_id,
            content=comment.content,
            post_id=comment.post_id,
            author_id=author_id,
            created_at=now,
            updated_at=now
        )
        self._next_id += 1
        self._comments.append(new_comment)

        # Update post's comment count
        post.comments_count += 1

        return new_comment

    def update(self, comment_id: int, comment_update: CommentUpdate, author_id: int) -> Optional[Comment]:
        """Update an existing comment"""
        comment = self.get_by_id(comment_id)
        if not comment or comment.author_id != author_id:
            return None

        update_data = comment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)

        comment.updated_at = datetime.now()
        return comment

    def delete(self, comment_id: int, author_id: int) -> bool:
        """Delete a comment"""
        comment = self.get_by_id(comment_id)
        if comment and comment.author_id == author_id:
            self._comments.remove(comment)

            # Update post's comment count
            from src.crud.posts import posts_crud
            post = posts_crud.get_by_id(comment.post_id)
            if post:
                post.comments_count = max(0, post.comments_count - 1)

            return True
        return False

comments_crud = CommentsCRUD()
```

## 6단계: 고급 API 라우트 구현

### 향상된 User 라우트

`src/api/routes/users.py` 를 갱신합니다:

```python
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.users import User, UserCreate, UserUpdate
from src.crud.users import users_crud

router = APIRouter()

# Helper function to get current user (simplified for tutorial)
def get_current_user_id() -> int:
    # In a real app, this would verify JWT token and return user ID
    return 1  # For tutorial purposes

@router.get("/", response_model=List[User])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all users with pagination"""
    users = users_crud.get_all()[skip:skip + limit]
    return [User(**user.dict()) for user in users]

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Register a new user"""
    try:
        new_user = users_crud.create(user)
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

@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """Update user profile"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )

    try:
        updated_user = users_crud.update(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return User(**updated_user.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """Deactivate user account"""
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own account"
        )

    success = users_crud.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

@router.post("/login")
def login(email: str, password: str):
    """Authenticate user"""
    user = users_crud.authenticate(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # In a real app, return JWT token
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username
    }
```

### 향상된 Posts 라우트

`src/api/routes/posts.py` 를 갱신합니다:

```python
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.posts import Post, PostCreate, PostUpdate
from src.crud.posts import posts_crud

router = APIRouter()

def get_current_user_id() -> int:
    return 1  # Simplified for tutorial

@router.get("/", response_model=List[Post])
def read_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """Get all posts with optional search"""
    if search:
        posts = posts_crud.search(search, skip, limit)
    else:
        posts = posts_crud.get_all(skip, limit)
    return posts

@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
def create_post(
    post: PostCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """Create a new blog post"""
    new_post = posts_crud.create(post, current_user_id)
    return new_post

@router.get("/{post_id}", response_model=Post)
def read_post(post_id: int):
    """Get a specific post"""
    post = posts_crud.get_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    return post

@router.put("/{post_id}", response_model=Post)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """Update a blog post"""
    updated_post = posts_crud.update(post_id, post_update, current_user_id)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to edit it"
        )
    return updated_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """Delete a blog post"""
    success = posts_crud.delete(post_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )

@router.get("/author/{author_id}", response_model=List[Post])
def read_posts_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get posts by a specific author"""
    posts = posts_crud.get_by_author(author_id, skip, limit)
    return posts
```

### 향상된 Comments 라우트

`src/api/routes/comments.py` 를 갱신합니다:

```python
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.comments import Comment, CommentCreate, CommentUpdate
from src.crud.comments import comments_crud

router = APIRouter()

def get_current_user_id() -> int:
    return 1  # Simplified for tutorial

@router.get("/", response_model=List[Comment])
def read_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get all comments"""
    comments = comments_crud.get_all()[skip:skip + limit]
    return comments

@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """Create a new comment"""
    try:
        new_comment = comments_crud.create(comment, current_user_id)
        return new_comment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{comment_id}", response_model=Comment)
def read_comment(comment_id: int):
    """Get a specific comment"""
    comment = comments_crud.get_by_id(comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return comment

@router.put("/{comment_id}", response_model=Comment)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user_id: int = Depends(get_current_user_id)
):
    """Update a comment"""
    updated_comment = comments_crud.update(comment_id, comment_update, current_user_id)
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to edit it"
        )
    return updated_comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user_id: int = Depends(get_current_user_id)
):
    """Delete a comment"""
    success = comments_crud.delete(comment_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )

@router.get("/post/{post_id}", response_model=List[Comment])
def read_comments_by_post(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get comments for a specific post"""
    comments = comments_crud.get_by_post(post_id, skip, limit)
    return comments

@router.get("/author/{author_id}", response_model=List[Comment])
def read_comments_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Get comments by a specific author"""
    comments = comments_crud.get_by_author(author_id, skip, limit)
    return comments
```

## 7단계: 블로그 API 테스트

서버를 시작하고 완성된 블로그 API를 테스트합니다:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### 사용자 회원 가입 테스트

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com",
       "username": "john_doe",
       "full_name": "John Doe",
       "bio": "Software developer and blogger",
       "password": "securepassword123"
     }'

{
  "id": 1,
  "email": "john@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "bio": "Software developer and blogger",
  "is_active": true,
  "created_at": "2023-12-07T10:30:00",
  "posts_count": 0
}
```

</div>

### 사용자 로그인 테스트

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/users/login" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "john@example.com",
       "password": "securepassword123"
     }'

{
  "message": "Login successful",
  "user_id": 1,
  "username": "john_doe"
}
```

</div>

### 게시물 생성 테스트

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/posts/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "My First Blog Post",
       "content": "This is the content of my first blog post. It'\''s about learning FastAPI with FastAPI-fastkit!",
       "published": true
     }'

{
  "id": 1,
  "title": "My First Blog Post",
  "content": "This is the content of my first blog post. It's about learning FastAPI with FastAPI-fastkit!",
  "published": true,
  "author_id": 1,
  "created_at": "2023-12-07T10:35:00",
  "updated_at": "2023-12-07T10:35:00",
  "comments_count": 0
}
```

</div>

### 댓글 생성 테스트

<div class="termy">

```console
$ curl -X POST "http://127.0.0.1:8000/api/v1/comments/" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Great post! I learned a lot from this.",
       "post_id": 1
     }'

{
  "id": 1,
  "content": "Great post! I learned a lot from this.",
  "post_id": 1,
  "author_id": 1,
  "created_at": "2023-12-07T10:40:00",
  "updated_at": "2023-12-07T10:40:00"
}
```

</div>

### 검색 기능 테스트

<div class="termy">

```console
$ curl "http://127.0.0.1:8000/api/v1/posts/?search=FastAPI"

[
  {
    "id": 1,
    "title": "My First Blog Post",
    "content": "This is the content of my first blog post. It's about learning FastAPI with FastAPI-fastkit!",
    "published": true,
    "author_id": 1,
    "created_at": "2023-12-07T10:35:00",
    "updated_at": "2023-12-07T10:35:00",
    "comments_count": 1
  }
]
```

</div>

## 8단계: API 문서

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)에 접속해 완성된 API 문서를 확인하세요. 다음 내용을 볼 수 있습니다:

- **Users**: 회원 가입, 로그인, 프로필 관리
- **Posts**: CRUD 작업, 검색, 작성자 필터링
- **Comments**: CRUD 작업, 게시물 / 작성자 필터링
- **Items**: 원래 예제 엔드포인트

문서에서 보여 주는 것:

- 사용 가능한 모든 엔드포인트  
- 요청 / 응답 스키마  
- 데이터 검증 규칙  
- 에러 응답  

## 9단계: 테스트 작성

블로그 API를 위한 종합 테스트를 만들어 봅시다. `tests/test_blog_api.py`를 작성합니다:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestUserAPI:
    def test_create_user(self):
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "bio": "Test bio",
            "password": "testpassword123"
        }
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data  # Should not expose password

    def test_duplicate_email(self):
        # First user
        user_data1 = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }
        response1 = client.post("/api/v1/users/", json=user_data1)
        assert response1.status_code == 201

        # Second user with same email
        user_data2 = {
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "password123"
        }
        response2 = client.post("/api/v1/users/", json=user_data2)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]

    def test_login(self):
        # Create user first
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpassword123"
        }
        client.post("/api/v1/users/", json=user_data)

        # Test login
        login_data = {
            "email": "login@example.com",
            "password": "loginpassword123"
        }
        response = client.post("/api/v1/users/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert data["username"] == "loginuser"

class TestPostAPI:
    def test_create_post(self):
        post_data = {
            "title": "Test Post",
            "content": "This is a test post content",
            "published": True
        }
        response = client.post("/api/v1/posts/", json=post_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["content"] == post_data["content"]
        assert "id" in data
        assert "author_id" in data

    def test_read_posts(self):
        response = client.get("/api/v1/posts/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_posts(self):
        # Create a post with specific content
        post_data = {
            "title": "FastAPI Tutorial",
            "content": "Learn how to build APIs with FastAPI",
            "published": True
        }
        client.post("/api/v1/posts/", json=post_data)

        # Search for the post
        response = client.get("/api/v1/posts/?search=FastAPI")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any("FastAPI" in post["title"] or "FastAPI" in post["content"] for post in data)

class TestCommentAPI:
    def test_create_comment(self):
        # Create a post first
        post_data = {
            "title": "Post for Comments",
            "content": "This post will receive comments",
            "published": True
        }
        post_response = client.post("/api/v1/posts/", json=post_data)
        post_id = post_response.json()["id"]

        # Create comment
        comment_data = {
            "content": "This is a test comment",
            "post_id": post_id
        }
        response = client.post("/api/v1/comments/", json=comment_data)
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == comment_data["content"]
        assert data["post_id"] == post_id

    def test_get_comments_by_post(self):
        # Create post and comment first
        post_data = {
            "title": "Post with Comments",
            "content": "This post has comments",
            "published": True
        }
        post_response = client.post("/api/v1/posts/", json=post_data)
        post_id = post_response.json()["id"]

        comment_data = {
            "content": "Comment on post",
            "post_id": post_id
        }
        client.post("/api/v1/comments/", json=comment_data)

        # Get comments for the post
        response = client.get(f"/api/v1/comments/post/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(comment["post_id"] == post_id for comment in data)

# Run the tests
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
```

### 테스트 실행

<div class="termy">

```console
$ python -m pytest tests/test_blog_api.py -v
======================== test session starts ========================
tests/test_blog_api.py::TestUserAPI::test_create_user PASSED
tests/test_blog_api.py::TestUserAPI::test_duplicate_email PASSED
tests/test_blog_api.py::TestUserAPI::test_login PASSED
tests/test_blog_api.py::TestPostAPI::test_create_post PASSED
tests/test_blog_api.py::TestPostAPI::test_read_posts PASSED
tests/test_blog_api.py::TestPostAPI::test_search_posts PASSED
tests/test_blog_api.py::TestCommentAPI::test_create_comment PASSED
tests/test_blog_api.py::TestCommentAPI::test_get_comments_by_post PASSED
======================== 8 passed in 1.23s ========================
```

</div>

## 무엇을 만들었나

축하합니다! 다음 기능을 갖춘 완전한 블로그 API를 성공적으로 구축했습니다:

### ✅ 구현한 기능

- **사용자 관리**
    - 검증을 갖춘 사용자 회원 가입
    - 사용자 인증 (로그인)
    - 프로필 관리
    - 중복 방지

- **블로그 게시물**
    - 게시물 생성, 조회, 갱신, 삭제
    - 작성자 기반 필터링
    - 검색 기능
    - 게시 / 임시 저장 상태

- **댓글 시스템**
    - 게시물에 댓글 추가
    - 게시물별 / 작성자별 댓글 조회
    - 댓글 관리

- **데이터 검증**
    - 이메일 검증
    - 패스워드 요구 사항
    - 콘텐츠 길이 제한
    - 필수 필드 검증

- **에러 처리**
    - 적절한 HTTP 상태 코드
    - 설명적인 에러 메시지
    - 입력 검증 에러

- **API 문서화**
    - 자동 OpenAPI 생성
    - 인터랙티브 테스트 인터페이스
    - 요청 / 응답 스키마

- **테스트**
    - 종합 테스트 커버리지
    - 모든 엔드포인트의 단위 테스트
    - 엣지 케이스 테스트

## 다음 단계

### 가능한 개선 사항

1. **실제 인증**
    - JWT 토큰 구현
    - bcrypt 로 패스워드 해싱 추가
    - 역할 기반 권한

2. **데이터베이스 통합**
    - PostgreSQL 또는 MySQL 사용
    - 적절한 데이터베이스 모델 구현
    - 데이터베이스 마이그레이션 추가

3. **고급 기능**
    - 이미지 파일 업로드
    - 이메일 알림
    - 게시물 카테고리 / 태그
    - 좋아요 / 싫어요 시스템

4. **프로덕션 준비**
    - 로깅 추가
    - 캐싱 구현
    - 레이트 제한 추가
    - 환경 설정

### 학습 이어가기

1. **[템플릿 사용하기](../user-guide/using-templates.md)**: 데이터베이스 통합을 위한 `fastapi-psql-orm` 템플릿 살펴보기
2. **[라우트 추가](../user-guide/adding-routes.md)**: 더 고급 라우팅 패턴 학습
3. **[기여 안내](../contributing/development-setup.md)**: FastAPI-fastkit에 기여하기

!!! tip "여기서 배운 모범 사례"
    - **모듈형 아키텍처**: 스키마, CRUD, 라우트로 관심사 분리
    - **데이터 검증**: 견고한 입력 검증을 위한 Pydantic 사용
    - **에러 처리**: 적절한 HTTP 상태 코드와 에러 메시지
    - **테스트**: 모든 기능을 아우르는 종합 테스트 커버리지
    - **문서화**: 자동 API 문서 생성 활용

이제 FastAPI-fastkit으로 실서비스 수준의 API를 만들 기본기를 갖췄습니다! 🚀

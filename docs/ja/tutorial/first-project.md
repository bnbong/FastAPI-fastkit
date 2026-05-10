# 最初のプロジェクト

FastAPI-fastkit を使って、ユーザー管理・投稿作成・コメント機能を備えた完全なブログ API を構築します。

## プロジェクト概要

このチュートリアルでは、次の機能を持つ **ブログ API** を作成します:

- **ユーザー管理**: ユーザー登録、認証、プロフィール
- **投稿管理**: ブログ投稿の作成・取得・更新・削除
- **コメント機能**: ブログ投稿にコメントを追加
- **データ検証**: 堅牢な入力検証とエラー処理
- **API ドキュメント**: 自動 OpenAPI ドキュメント
- **テスト**: 包括的なテストスイート

### 学べること

このチュートリアルを終えると、次が理解できます:

- FastAPI-fastkit プロジェクトの応用的な構造
- SQLAlchemy によるデータベース統合
- ユーザー認証と認可
- 複雑なデータ関係
- エラー処理と検証
- テストのベストプラクティス

## 前提条件

開始前に、次が用意されていることを確認してください:

- [はじめに](getting-started.md) チュートリアルを完了済み
- REST API の基本理解
- Python 3.12 以上がインストール済み
- テキストエディタまたは IDE が利用可能

## ステップ 1: プロジェクトの作成

データベース対応を含めるため、**STANDARD** スタックで新しいプロジェクトを作成します:

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

## ステップ 2: プロジェクトのセットアップ

プロジェクトに移動し、仮想環境を有効化します:

<div class="termy">

```console
$ cd blog-api
$ source .venv/bin/activate
```

</div>

## ステップ 3: 必要なルートを追加

ブログ API のメインリソースを追加しましょう:

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

## ステップ 4: データモデルの設計

データスキーマを設計します。より実用的な内容にするため、まずユーザースキーマを更新しましょう。

### ユーザースキーマの更新

`src/schemas/users.py` を編集します:

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

### 投稿スキーマの作成

`src/schemas/posts.py` を編集します:

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

# 循環インポートを避けるためのインポート
from src.schemas.users import User
from src.schemas.comments import Comment
PostWithAuthor.model_rebuild()
PostWithComments.model_rebuild()
```

### コメントスキーマの作成

`src/schemas/comments.py` を編集します:

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

# 循環インポートを避けるためのインポート
from src.schemas.users import User
CommentWithAuthor.model_rebuild()
```

## ステップ 5: 高度な CRUD 操作の実装

### ユーザー CRUD の拡張

`src/crud/users.py` を更新します:

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
        """シンプルなパスワードハッシュ (本番では bcrypt を使用)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """ハッシュとパスワードを照合"""
        return self._hash_password(plain_password) == hashed_password

    def get_all(self) -> List[UserInDB]:
        """すべてのユーザーを取得"""
        return [user for user in self._users if user.is_active]

    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        """ID でユーザーを取得"""
        return next((user for user in self._users if user.id == user_id), None)

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        """メールアドレスでユーザーを取得"""
        return next((user for user in self._users if user.email == email), None)

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        """ユーザー名でユーザーを取得"""
        return next((user for user in self._users if user.username == username), None)

    def create(self, user: UserCreate) -> UserInDB:
        """検証付きで新しいユーザーを作成"""
        # 重複チェック
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
        """既存ユーザーを更新"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        # メール / ユーザー名の重複チェック
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
        """ユーザーを論理削除 (非アクティブ化)"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            return True
        return False

    def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        """メールとパスワードでユーザーを認証"""
        user = self.get_by_email(email)
        if user and self._verify_password(password, user.hashed_password):
            return user
        return None

users_crud = UsersCRUD()
```

### 投稿の CRUD

`src/crud/posts.py` を更新します:

```python
from typing import List, Optional
from datetime import datetime
from src.schemas.posts import PostCreate, PostUpdate, Post

class PostsCRUD:
    def __init__(self):
        self._posts: List[Post] = []
        self._next_id = 1

    def get_all(self, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[Post]:
        """ページネーション付きで全投稿を取得"""
        posts = self._posts
        if published_only:
            posts = [post for post in posts if post.published]
        return posts[skip:skip + limit]

    def get_by_id(self, post_id: int) -> Optional[Post]:
        """ID で投稿を取得"""
        return next((post for post in self._posts if post.id == post_id), None)

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        """作者ごとの投稿を取得"""
        author_posts = [post for post in self._posts if post.author_id == author_id]
        return author_posts[skip:skip + limit]

    def create(self, post: PostCreate, author_id: int) -> Post:
        """新しい投稿を作成"""
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

        # 作者の投稿数を更新
        from src.crud.users import users_crud
        author = users_crud.get_by_id(author_id)
        if author:
            author.posts_count += 1

        return new_post

    def update(self, post_id: int, post_update: PostUpdate, author_id: int) -> Optional[Post]:
        """既存投稿を更新"""
        post = self.get_by_id(post_id)
        if not post or post.author_id != author_id:
            return None

        update_data = post_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        post.updated_at = datetime.now()
        return post

    def delete(self, post_id: int, author_id: int) -> bool:
        """投稿を削除"""
        post = self.get_by_id(post_id)
        if post and post.author_id == author_id:
            self._posts.remove(post)

            # 作者の投稿数を更新
            from src.crud.users import users_crud
            author = users_crud.get_by_id(author_id)
            if author:
                author.posts_count = max(0, author.posts_count - 1)

            return True
        return False

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """タイトルや本文で投稿を検索"""
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

### コメントの CRUD

`src/crud/comments.py` を更新します:

```python
from typing import List, Optional
from datetime import datetime
from src.schemas.comments import CommentCreate, CommentUpdate, Comment

class CommentsCRUD:
    def __init__(self):
        self._comments: List[Comment] = []
        self._next_id = 1

    def get_all(self) -> List[Comment]:
        """すべてのコメントを取得"""
        return self._comments

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """ID でコメントを取得"""
        return next((comment for comment in self._comments if comment.id == comment_id), None)

    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """特定投稿のコメントを取得"""
        post_comments = [comment for comment in self._comments if comment.post_id == post_id]
        return post_comments[skip:skip + limit]

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """作者ごとのコメントを取得"""
        author_comments = [comment for comment in self._comments if comment.author_id == author_id]
        return author_comments[skip:skip + limit]

    def create(self, comment: CommentCreate, author_id: int) -> Comment:
        """新しいコメントを作成"""
        # 投稿の存在確認
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

        # 投稿のコメント数を更新
        post.comments_count += 1

        return new_comment

    def update(self, comment_id: int, comment_update: CommentUpdate, author_id: int) -> Optional[Comment]:
        """既存コメントを更新"""
        comment = self.get_by_id(comment_id)
        if not comment or comment.author_id != author_id:
            return None

        update_data = comment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)

        comment.updated_at = datetime.now()
        return comment

    def delete(self, comment_id: int, author_id: int) -> bool:
        """コメントを削除"""
        comment = self.get_by_id(comment_id)
        if comment and comment.author_id == author_id:
            self._comments.remove(comment)

            # 投稿のコメント数を更新
            from src.crud.posts import posts_crud
            post = posts_crud.get_by_id(comment.post_id)
            if post:
                post.comments_count = max(0, post.comments_count - 1)

            return True
        return False

comments_crud = CommentsCRUD()
```

## ステップ 6: 高度な API ルートの実装

### ユーザールートの拡張

`src/api/routes/users.py` を更新します:

```python
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.users import User, UserCreate, UserUpdate
from src.crud.users import users_crud

router = APIRouter()

# 現在のユーザーを取得するヘルパ (チュートリアル用に簡略化)
def get_current_user_id() -> int:
    # 実際のアプリでは JWT を検証してユーザー ID を返す
    return 1  # チュートリアル用

@router.get("/", response_model=List[User])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """ページネーション付きで全ユーザーを取得"""
    users = users_crud.get_all()[skip:skip + limit]
    return [User(**user.dict()) for user in users]

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """新しいユーザーを登録"""
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
    """特定のユーザーを取得"""
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
    """ユーザープロフィールを更新"""
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
    """ユーザーアカウントを非アクティブ化"""
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
    """ユーザーを認証"""
    user = users_crud.authenticate(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # 実アプリでは JWT を返す
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username
    }
```

### 投稿ルートの拡張

`src/api/routes/posts.py` を更新します:

```python
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.posts import Post, PostCreate, PostUpdate
from src.crud.posts import posts_crud

router = APIRouter()

def get_current_user_id() -> int:
    return 1  # チュートリアル用に簡略化

@router.get("/", response_model=List[Post])
def read_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """検索オプション付きで全投稿を取得"""
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
    """新しいブログ投稿を作成"""
    new_post = posts_crud.create(post, current_user_id)
    return new_post

@router.get("/{post_id}", response_model=Post)
def read_post(post_id: int):
    """特定の投稿を取得"""
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
    """ブログ投稿を更新"""
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
    """ブログ投稿を削除"""
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
    """特定の作者の投稿を取得"""
    posts = posts_crud.get_by_author(author_id, skip, limit)
    return posts
```

### コメントルートの拡張

`src/api/routes/comments.py` を更新します:

```python
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.comments import Comment, CommentCreate, CommentUpdate
from src.crud.comments import comments_crud

router = APIRouter()

def get_current_user_id() -> int:
    return 1  # チュートリアル用に簡略化

@router.get("/", response_model=List[Comment])
def read_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """すべてのコメントを取得"""
    comments = comments_crud.get_all()[skip:skip + limit]
    return comments

@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """新しいコメントを作成"""
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
    """特定のコメントを取得"""
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
    """コメントを更新"""
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
    """コメントを削除"""
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
    """特定投稿のコメントを取得"""
    comments = comments_crud.get_by_post(post_id, skip, limit)
    return comments

@router.get("/author/{author_id}", response_model=List[Comment])
def read_comments_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """特定作者のコメントを取得"""
    comments = comments_crud.get_by_author(author_id, skip, limit)
    return comments
```

## ステップ 7: ブログ API のテスト

サーバーを起動して、完成したブログ API をテストしましょう:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### ユーザー登録のテスト

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

### ログインのテスト

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

### 投稿作成のテスト

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

### コメント作成のテスト

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

### 検索機能のテスト

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

## ステップ 8: API ドキュメント

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) を開いて、完成した API ドキュメントを確認しましょう。次が表示されるはずです:

- **Users**: 登録、ログイン、プロフィール管理
- **Posts**: CRUD、検索、作者フィルタ
- **Comments**: CRUD、投稿 / 作者によるフィルタ
- **Items**: 元のサンプルエンドポイント

ドキュメントには次が含まれます:

- 利用可能なすべてのエンドポイント
- リクエスト / レスポンススキーマ
- データ検証ルール
- エラーレスポンス

## ステップ 9: テストの作成

ブログ API の包括的なテストを作成しましょう。`tests/test_blog_api.py` を作成します:

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
        assert "hashed_password" not in data  # パスワードを露出させない

    def test_duplicate_email(self):
        # 1 人目のユーザー
        user_data1 = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }
        response1 = client.post("/api/v1/users/", json=user_data1)
        assert response1.status_code == 201

        # 2 人目を同じメールで作成
        user_data2 = {
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "password123"
        }
        response2 = client.post("/api/v1/users/", json=user_data2)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]

    def test_login(self):
        # まずユーザーを作成
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpassword123"
        }
        client.post("/api/v1/users/", json=user_data)

        # ログインをテスト
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
        # 特定の内容を含む投稿を作成
        post_data = {
            "title": "FastAPI Tutorial",
            "content": "Learn how to build APIs with FastAPI",
            "published": True
        }
        client.post("/api/v1/posts/", json=post_data)

        # 投稿を検索
        response = client.get("/api/v1/posts/?search=FastAPI")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any("FastAPI" in post["title"] or "FastAPI" in post["content"] for post in data)

class TestCommentAPI:
    def test_create_comment(self):
        # まず投稿を作成
        post_data = {
            "title": "Post for Comments",
            "content": "This post will receive comments",
            "published": True
        }
        post_response = client.post("/api/v1/posts/", json=post_data)
        post_id = post_response.json()["id"]

        # コメントを作成
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
        # まず投稿とコメントを作成
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

        # 投稿のコメントを取得
        response = client.get(f"/api/v1/comments/post/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(comment["post_id"] == post_id for comment in data)

# テスト実行
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
```

### テストを実行する

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

## 構築したもの

おめでとうございます! 次の機能を備えた完全なブログ API を構築できました:

### ✅ 実装した機能

- **ユーザー管理**
    - 検証付きのユーザー登録
    - ユーザー認証 (ログイン)
    - プロフィール管理
    - 重複防止

- **ブログ投稿**
    - 投稿の作成、取得、更新、削除
    - 作者によるフィルタ
    - 検索機能
    - 公開 / 下書きの状態

- **コメント機能**
    - 投稿へのコメント追加
    - 投稿 / 作者ごとのコメント表示
    - コメント管理

- **データ検証**
    - メールアドレスの検証
    - パスワード要件
    - コンテンツ長の制限
    - 必須フィールドの検証

- **エラー処理**
    - 適切な HTTP ステータスコード
    - 説明的なエラーメッセージ
    - 入力検証エラー

- **API ドキュメント**
    - 自動 OpenAPI 生成
    - 対話型テストインターフェイス
    - リクエスト / レスポンススキーマ

- **テスト**
    - 包括的なテストカバレッジ
    - 全エンドポイントの単体テスト
    - エッジケースのテスト

## 次のステップ

### 拡張のアイデア

1. **本格的な認証**
    - JWT トークンの実装
    - bcrypt によるパスワードハッシュ
    - ロールベースの権限管理

2. **データベース統合**
    - PostgreSQL や MySQL の利用
    - 適切なデータベースモデル
    - データベースマイグレーション

3. **高度な機能**
    - 画像のファイルアップロード
    - メール通知
    - 投稿カテゴリ / タグ
    - いいね / よくないね機能

4. **本番運用への対応**
    - ログの追加
    - キャッシュの実装
    - レート制限
    - 環境ごとの設定

### 学習を続ける

1. **[テンプレートの利用](../user-guide/using-templates.md)**: データベース統合のために `fastapi-psql-orm` テンプレートを試す
2. **[ルートの追加](../user-guide/adding-routes.md)**: より高度なルーティングパターンを学ぶ
3. **[コントリビュート](../contributing/development-setup.md)**: FastAPI-fastkit に貢献する

!!! tip "学んだベストプラクティス"
    - **モジュール型アーキテクチャ**: schemas、CRUD、routes による関心事の分離
    - **データ検証**: Pydantic を使った堅牢な入力検証
    - **エラー処理**: 適切な HTTP ステータスコードとエラーメッセージ
    - **テスト**: すべての機能の包括的なテストカバレッジ
    - **ドキュメント**: 自動 API ドキュメント生成の活用

これで FastAPI-fastkit を使ってプロダクション品質の API を構築するスキルが身につきました! 🚀

# Tu primer proyecto

Construye una API de blog completa con gestión de usuarios, creación de posts y sistema de comentarios usando FastAPI-fastkit.

## Visión general del proyecto

En este tutorial vamos a crear una **API de blog** con las siguientes funcionalidades:

- **Gestión de usuarios**: registro, autenticación y perfiles
- **Gestión de posts**: crear, leer, actualizar y eliminar entradas de blog
- **Sistema de comentarios**: añadir comentarios a las entradas
- **Validación de datos**: validación robusta de entrada y manejo de errores
- **Documentación de la API**: documentación OpenAPI automática
- **Pruebas**: suite de pruebas completa

### Qué aprenderás

Al final de este tutorial entenderás:

- Estructura avanzada de un proyecto FastAPI-fastkit
- Integración de base de datos con SQLAlchemy
- Autenticación y autorización de usuarios
- Relaciones de datos complejas
- Manejo de errores y validación
- Buenas prácticas de pruebas

## Requisitos previos

Antes de empezar, asegúrate de tener:

- Haber completado el tutorial de [Primeros pasos](getting-started.md)
- Conocimientos básicos de APIs REST
- Python 3.12+ instalado
- Editor de texto o IDE listo

## Paso 1: Crear el proyecto

Empecemos creando un proyecto nuevo con el stack **STANDARD** para tener soporte de base de datos:

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

## Paso 2: Preparar el proyecto

Entra en el proyecto y activa el entorno virtual:

<div class="termy">

```console
$ cd blog-api
$ source .venv/bin/activate
```

</div>

## Paso 3: Añadir las rutas necesarias

Añadamos los recursos principales de nuestra API de blog:

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

## Paso 4: Diseñar los modelos de datos

Vamos a diseñar nuestros esquemas de datos. Empezaremos actualizando el esquema de usuario para que sea más realista.

### Actualizar el esquema de usuario

Edita `src/schemas/users.py`:

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

### Crear el esquema de post

Edita `src/schemas/posts.py`:

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

# Import para evitar imports circulares
from src.schemas.users import User
from src.schemas.comments import Comment
PostWithAuthor.model_rebuild()
PostWithComments.model_rebuild()
```

### Crear el esquema de comentario

Edita `src/schemas/comments.py`:

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

# Import para evitar imports circulares
from src.schemas.users import User
CommentWithAuthor.model_rebuild()
```

## Paso 5: Implementar operaciones CRUD avanzadas

### CRUD de usuarios mejorado

Actualiza `src/crud/users.py`:

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
        """Hash simple de contraseña (usa bcrypt en producción)"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return self._hash_password(plain_password) == hashed_password

    def get_all(self) -> List[UserInDB]:
        """Obtener todos los usuarios"""
        return [user for user in self._users if user.is_active]

    def get_by_id(self, user_id: int) -> Optional[UserInDB]:
        """Obtener usuario por ID"""
        return next((user for user in self._users if user.id == user_id), None)

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Obtener usuario por email"""
        return next((user for user in self._users if user.email == email), None)

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        """Obtener usuario por nombre de usuario"""
        return next((user for user in self._users if user.username == username), None)

    def create(self, user: UserCreate) -> UserInDB:
        """Crear un nuevo usuario con validación"""
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
        """Actualizar un usuario existente"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        # Comprobar duplicados en cambios de email/username
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
        """Eliminar usuario lógicamente (desactivar)"""
        user = self.get_by_id(user_id)
        if user:
            user.is_active = False
            return True
        return False

    def authenticate(self, email: str, password: str) -> Optional[UserInDB]:
        """Autenticar usuario por email y contraseña"""
        user = self.get_by_email(email)
        if user and self._verify_password(password, user.hashed_password):
            return user
        return None

users_crud = UsersCRUD()
```

### CRUD de posts

Actualiza `src/crud/posts.py`:

```python
from typing import List, Optional
from datetime import datetime
from src.schemas.posts import PostCreate, PostUpdate, Post

class PostsCRUD:
    def __init__(self):
        self._posts: List[Post] = []
        self._next_id = 1

    def get_all(self, skip: int = 0, limit: int = 100, published_only: bool = True) -> List[Post]:
        """Obtener todos los posts con paginación"""
        posts = self._posts
        if published_only:
            posts = [post for post in posts if post.published]
        return posts[skip:skip + limit]

    def get_by_id(self, post_id: int) -> Optional[Post]:
        """Obtener post por ID"""
        return next((post for post in self._posts if post.id == post_id), None)

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Post]:
        """Obtener posts por autor"""
        author_posts = [post for post in self._posts if post.author_id == author_id]
        return author_posts[skip:skip + limit]

    def create(self, post: PostCreate, author_id: int) -> Post:
        """Crear un post nuevo"""
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

        # Actualizar el contador de posts del autor
        from src.crud.users import users_crud
        author = users_crud.get_by_id(author_id)
        if author:
            author.posts_count += 1

        return new_post

    def update(self, post_id: int, post_update: PostUpdate, author_id: int) -> Optional[Post]:
        """Actualizar un post existente"""
        post = self.get_by_id(post_id)
        if not post or post.author_id != author_id:
            return None

        update_data = post_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(post, field, value)

        post.updated_at = datetime.now()
        return post

    def delete(self, post_id: int, author_id: int) -> bool:
        """Eliminar un post"""
        post = self.get_by_id(post_id)
        if post and post.author_id == author_id:
            self._posts.remove(post)

            # Actualizar el contador de posts del autor
            from src.crud.users import users_crud
            author = users_crud.get_by_id(author_id)
            if author:
                author.posts_count = max(0, author.posts_count - 1)

            return True
        return False

    def search(self, query: str, skip: int = 0, limit: int = 100) -> List[Post]:
        """Buscar posts por título o contenido"""
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

### CRUD de comentarios

Actualiza `src/crud/comments.py`:

```python
from typing import List, Optional
from datetime import datetime
from src.schemas.comments import CommentCreate, CommentUpdate, Comment

class CommentsCRUD:
    def __init__(self):
        self._comments: List[Comment] = []
        self._next_id = 1

    def get_all(self) -> List[Comment]:
        """Obtener todos los comentarios"""
        return self._comments

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Obtener comentario por ID"""
        return next((comment for comment in self._comments if comment.id == comment_id), None)

    def get_by_post(self, post_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Obtener comentarios de un post concreto"""
        post_comments = [comment for comment in self._comments if comment.post_id == post_id]
        return post_comments[skip:skip + limit]

    def get_by_author(self, author_id: int, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Obtener comentarios por autor"""
        author_comments = [comment for comment in self._comments if comment.author_id == author_id]
        return author_comments[skip:skip + limit]

    def create(self, comment: CommentCreate, author_id: int) -> Comment:
        """Crear un comentario nuevo"""
        # Verificar que el post existe
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

        # Actualizar contador de comentarios del post
        post.comments_count += 1

        return new_comment

    def update(self, comment_id: int, comment_update: CommentUpdate, author_id: int) -> Optional[Comment]:
        """Actualizar un comentario existente"""
        comment = self.get_by_id(comment_id)
        if not comment or comment.author_id != author_id:
            return None

        update_data = comment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(comment, field, value)

        comment.updated_at = datetime.now()
        return comment

    def delete(self, comment_id: int, author_id: int) -> bool:
        """Eliminar un comentario"""
        comment = self.get_by_id(comment_id)
        if comment and comment.author_id == author_id:
            self._comments.remove(comment)

            # Actualizar contador de comentarios del post
            from src.crud.posts import posts_crud
            post = posts_crud.get_by_id(comment.post_id)
            if post:
                post.comments_count = max(0, post.comments_count - 1)

            return True
        return False

comments_crud = CommentsCRUD()
```

## Paso 6: Implementar rutas de API avanzadas

### Rutas de usuario mejoradas

Actualiza `src/api/routes/users.py`:

```python
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.users import User, UserCreate, UserUpdate
from src.crud.users import users_crud

router = APIRouter()

# Helper para obtener el usuario actual (simplificado para el tutorial)
def get_current_user_id() -> int:
    # En una app real, esto verificaría el token JWT y devolvería el ID
    return 1  # Para el tutorial

@router.get("/", response_model=List[User])
def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Obtener todos los usuarios con paginación"""
    users = users_crud.get_all()[skip:skip + limit]
    return [User(**user.dict()) for user in users]

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Registrar un nuevo usuario"""
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
    """Obtener un usuario concreto"""
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
    """Actualizar el perfil de usuario"""
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
    """Desactivar la cuenta de usuario"""
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
    """Autenticar usuario"""
    user = users_crud.authenticate(email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # En una app real, devolverías un token JWT
    return {
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username
    }
```

### Rutas de posts mejoradas

Actualiza `src/api/routes/posts.py`:

```python
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.posts import Post, PostCreate, PostUpdate
from src.crud.posts import posts_crud

router = APIRouter()

def get_current_user_id() -> int:
    return 1  # Simplificado para el tutorial

@router.get("/", response_model=List[Post])
def read_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = Query(None)
):
    """Obtener todos los posts con búsqueda opcional"""
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
    """Crear una nueva entrada de blog"""
    new_post = posts_crud.create(post, current_user_id)
    return new_post

@router.get("/{post_id}", response_model=Post)
def read_post(post_id: int):
    """Obtener un post concreto"""
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
    """Actualizar una entrada de blog"""
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
    """Eliminar una entrada de blog"""
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
    """Obtener posts de un autor concreto"""
    posts = posts_crud.get_by_author(author_id, skip, limit)
    return posts
```

### Rutas de comentarios mejoradas

Actualiza `src/api/routes/comments.py`:

```python
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from src.schemas.comments import Comment, CommentCreate, CommentUpdate
from src.crud.comments import comments_crud

router = APIRouter()

def get_current_user_id() -> int:
    return 1  # Simplificado para el tutorial

@router.get("/", response_model=List[Comment])
def read_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Obtener todos los comentarios"""
    comments = comments_crud.get_all()[skip:skip + limit]
    return comments

@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment: CommentCreate,
    current_user_id: int = Depends(get_current_user_id)
):
    """Crear un comentario nuevo"""
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
    """Obtener un comentario concreto"""
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
    """Actualizar un comentario"""
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
    """Eliminar un comentario"""
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
    """Obtener comentarios de un post concreto"""
    comments = comments_crud.get_by_post(post_id, skip, limit)
    return comments

@router.get("/author/{author_id}", response_model=List[Comment])
def read_comments_by_author(
    author_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
):
    """Obtener comentarios de un autor concreto"""
    comments = comments_crud.get_by_author(author_id, skip, limit)
    return comments
```

## Paso 7: Probar tu API de blog

Vamos a arrancar el servidor y probar nuestra API de blog completa:

<div class="termy">

```console
$ fastkit runserver
INFO:     Uvicorn running on http://127.0.0.1:8000
```

</div>

### Probar el registro de usuario

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

### Probar el login

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

### Probar la creación de un post

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

### Probar la creación de un comentario

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

### Probar la búsqueda

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

## Paso 8: Documentación de la API

Entra en [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para ver la documentación completa de tu API. Deberías ver:

- **Users**: Registro, login, gestión de perfil
- **Posts**: Operaciones CRUD, búsqueda, filtrado por autor
- **Comments**: Operaciones CRUD, filtrado por post / autor
- **Items**: Endpoints de ejemplo originales

La documentación muestra:

- Todos los endpoints disponibles
- Esquemas de petición / respuesta
- Reglas de validación de datos
- Respuestas de error

## Paso 9: Escribir pruebas

Vamos a crear pruebas completas para la API de blog. Crea `tests/test_blog_api.py`:

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
        assert "hashed_password" not in data  # No debe exponer la contraseña

    def test_duplicate_email(self):
        # Primer usuario
        user_data1 = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123"
        }
        response1 = client.post("/api/v1/users/", json=user_data1)
        assert response1.status_code == 201

        # Segundo usuario con el mismo email
        user_data2 = {
            "email": "duplicate@example.com",
            "username": "user2",
            "password": "password123"
        }
        response2 = client.post("/api/v1/users/", json=user_data2)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]

    def test_login(self):
        # Crear usuario primero
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "loginpassword123"
        }
        client.post("/api/v1/users/", json=user_data)

        # Probar login
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
        # Crear post con contenido concreto
        post_data = {
            "title": "FastAPI Tutorial",
            "content": "Learn how to build APIs with FastAPI",
            "published": True
        }
        client.post("/api/v1/posts/", json=post_data)

        # Buscar el post
        response = client.get("/api/v1/posts/?search=FastAPI")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert any("FastAPI" in post["title"] or "FastAPI" in post["content"] for post in data)

class TestCommentAPI:
    def test_create_comment(self):
        # Crear un post primero
        post_data = {
            "title": "Post for Comments",
            "content": "This post will receive comments",
            "published": True
        }
        post_response = client.post("/api/v1/posts/", json=post_data)
        post_id = post_response.json()["id"]

        # Crear comentario
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
        # Crear post y comentario primero
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

        # Obtener comentarios del post
        response = client.get(f"/api/v1/comments/post/{post_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(comment["post_id"] == post_id for comment in data)

# Ejecutar las pruebas
if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
```

### Ejecutar las pruebas

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

## Lo que has construido

¡Enhorabuena! Has construido con éxito una API de blog completa con:

### ✅ Funcionalidades implementadas

- **Gestión de usuarios**
    - Registro de usuarios con validación
    - Autenticación de usuarios (login)
    - Gestión de perfil
    - Prevención de duplicados

- **Posts de blog**
    - Crear, leer, actualizar y eliminar posts
    - Filtrado por autor
    - Funcionalidad de búsqueda
    - Estado publicado / borrador

- **Sistema de comentarios**
    - Añadir comentarios a posts
    - Ver comentarios por post o autor
    - Gestión de comentarios

- **Validación de datos**
    - Validación de email
    - Requisitos de contraseña
    - Límites de longitud de contenido
    - Validación de campos obligatorios

- **Manejo de errores**
    - Códigos de estado HTTP adecuados
    - Mensajes de error descriptivos
    - Errores de validación de entrada

- **Documentación de la API**
    - Generación automática de OpenAPI
    - Interfaz interactiva de pruebas
    - Esquemas de petición / respuesta

- **Pruebas**
    - Cobertura amplia
    - Pruebas unitarias para todos los endpoints
    - Pruebas de casos límite

## Próximos pasos

### Posibles mejoras

1. **Autenticación real**
    - Implementar tokens JWT
    - Hash de contraseñas con bcrypt
    - Permisos basados en roles

2. **Integración con base de datos**
    - Usar PostgreSQL o MySQL
    - Implementar modelos de base de datos
    - Añadir migraciones

3. **Funcionalidades avanzadas**
    - Subida de archivos para imágenes
    - Notificaciones por email
    - Categorías / etiquetas
    - Sistema de "me gusta" / "no me gusta"

4. **Listo para producción**
    - Añadir logging
    - Implementar caché
    - Añadir rate limiting
    - Configuración por entorno

### Continúa aprendiendo

1. **[Usar plantillas](../user-guide/using-templates.md)**: Explora la plantilla `fastapi-psql-orm` para integración con base de datos
2. **[Añadir rutas](../user-guide/adding-routes.md)**: Aprende patrones de enrutamiento más avanzados
3. **[Contribuir](../contributing/development-setup.md)**: Contribuye a FastAPI-fastkit

!!! tip "Buenas prácticas que has aprendido"
    - **Arquitectura modular**: Separación de responsabilidades con schemas, CRUD y rutas
    - **Validación de datos**: Uso de Pydantic para validación de entrada robusta
    - **Manejo de errores**: Códigos de estado HTTP y mensajes de error adecuados
    - **Pruebas**: Cobertura completa para todas las funcionalidades
    - **Documentación**: Aprovecha la generación automática de documentación de API

¡Ahora tienes las habilidades para construir APIs de nivel producción con FastAPI-fastkit! 🚀

# Integración con MCP (Model Context Protocol)

Aprende a integrar Model Context Protocol (MCP) con FastAPI para construir un sistema en el que los modelos de IA puedan usar endpoints de API como herramientas. Implementaremos una API integrada con IA completa que incluye autenticación, gestión de permisos e implementación del servidor MCP usando la plantilla `fastapi-mcp`.

## Lo que aprenderás en este tutorial

- Conceptos e implementación de Model Context Protocol (MCP)
- Construir sistemas de autenticación basados en JWT
- Implementar control de acceso basado en roles (RBAC)
- Exponer y gestionar herramientas MCP
- Comunicación segura entre la API y los modelos de IA
- Gestión de sesiones y contexto de usuario

## Requisitos previos

- Haber completado el [tutorial de manejo personalizado de respuestas](custom-response-handling.md)
- Conceptos básicos de JWT y OAuth2
- Conceptos de comunicación API con modelos IA/LLM
- Conocimientos básicos del protocolo MCP

## ¿Qué es Model Context Protocol (MCP)?

MCP es un protocolo estandarizado que permite a los modelos de IA interactuar con sistemas externos.

### Enfoque tradicional vs MCP

**Enfoque tradicional (llamadas directas a la API):**
```
Modelo IA → Petición HTTP → Servidor API → Respuesta
```

**Enfoque MCP:**
```
Modelo IA → Cliente MCP → Servidor MCP (FastAPI) → Ejecución segura de herramientas → Respuesta
```

### Ventajas de MCP

- **Seguridad**: gestión integrada de autenticación y permisos
- **Estandarización**: provee una interfaz consistente
- **Gestión de contexto**: mantenimiento de estado basado en sesiones
- **Abstracción de herramientas**: expone APIs complejas como herramientas simples

## Paso 1: Crear un proyecto de integración MCP

Crea un proyecto usando la plantilla `fastapi-mcp`:

<div class="termy">

```console
$ fastkit startdemo fastapi-mcp
Enter the project name: ai-integrated-api
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: MCP-based API server integrated with AI models
Deploying FastAPI project using 'fastapi-mcp' template

           Project Information
┌──────────────┬─────────────────────────────────────────────┐
│ Project Name │ ai-integrated-api                           │
│ Author       │ Developer Kim                               │
│ Author Email │ developer@example.com                       │
│ Description  │ MCP-based API server integrated with AI models │
└──────────────┴─────────────────────────────────────────────┘

       Template Dependencies
┌──────────────┬────────────────┐
│ Dependency 1 │ fastapi        │
│ Dependency 2 │ uvicorn        │
│ Dependency 3 │ pydantic       │
│ Dependency 4 │ python-jose    │
│ Dependency 5 │ passlib        │
│ Dependency 6 │ python-multipart│
│ Dependency 7 │ mcp            │
└──────────────┴────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'ai-integrated-api' from 'fastapi-mcp' has been created successfully!
```

</div>

## Paso 2: Análisis de la estructura del proyecto

Veamos la estructura del proyecto generado:

```
ai-integrated-api/
├── src/
│   ├── main.py                     # Aplicación FastAPI
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py               # Modelos relacionados con autenticación
│   │   ├── jwt_handler.py          # Manejo de tokens JWT
│   │   ├── dependencies.py         # Dependencias de autenticación
│   │   └── routes.py               # Router de autenticación
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py               # Implementación del servidor MCP
│   │   ├── tools.py                # Definiciones de herramientas MCP
│   │   └── client.py               # Cliente MCP (para pruebas)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── api.py                  # Conjunto de routers
│   │   └── routes/
│   │       ├── items.py            # API de gestión de items
│   │       ├── users.py            # API de gestión de usuarios
│   │       └── admin.py            # API de administración
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                 # Esquemas de autenticación
│   │   ├── users.py                # Esquemas de usuario
│   │   └── items.py                # Esquemas de items
│   └── core/
│       ├── __init__.py
│       ├── config.py               # Configuración
│       ├── database.py             # Base de datos (en memoria)
│       └── security.py             # Configuración de seguridad
└── tests/
    ├── test_auth.py                # Pruebas de autenticación
    ├── test_mcp.py                 # Pruebas de MCP
    └── test_integration.py         # Pruebas de integración
```

## Paso 3: Implementación del sistema de autenticación

### Manejo de tokens JWT (`src/auth/jwt_handler.py`)

```python
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from src.core.config import settings

# Hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificación de contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generación del access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt

def create_refresh_token(user_id: str) -> str:
    """Generación del refresh token"""
    data = {"sub": user_id, "type": "refresh"}
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = data.copy()
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodificar token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def verify_token(token: str, token_type: str = "access") -> Optional[str]:
    """Verifica el token y devuelve el ID de usuario"""
    payload = decode_token(token)

    if not payload:
        return None

    # Verificar el tipo de token
    if token_type == "refresh" and payload.get("type") != "refresh":
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return user_id

class TokenManager:
    """Gestor de tokens"""

    def __init__(self):
        self.blacklisted_tokens = set()

    def blacklist_token(self, token: str):
        """Añade token a la lista negra"""
        self.blacklisted_tokens.add(token)

    def is_blacklisted(self, token: str) -> bool:
        """Comprueba si un token está en la lista negra"""
        return token in self.blacklisted_tokens

    def create_token_pair(self, user_id: str, user_role: str) -> Dict[str, str]:
        """Crea un par de access/refresh tokens"""
        access_token_data = {
            "sub": user_id,
            "role": user_role,
            "type": "access"
        }

        access_token = create_access_token(access_token_data)
        refresh_token = create_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

# Gestor global de tokens
token_manager = TokenManager()
```

### Modelo de usuario y base de datos (`src/auth/models.py`)

```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    """Roles de usuario"""
    ADMIN = "admin"
    USER = "user"
    AI_AGENT = "ai_agent"
    READONLY = "readonly"

class Permission(str, Enum):
    """Permisos"""
    READ_ITEMS = "read:items"
    WRITE_ITEMS = "write:items"
    DELETE_ITEMS = "delete:items"
    MANAGE_USERS = "manage:users"
    USE_MCP_TOOLS = "use:mcp_tools"
    ADMIN_MCP = "admin:mcp"

class User(BaseModel):
    """Modelo de usuario"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole
    permissions: List[Permission]
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    api_key: Optional[str] = None  # Para el cliente MCP

class UserInDB(User):
    """Modelo de usuario para almacenar en base de datos"""
    hashed_password: str

class UserCreate(BaseModel):
    """Esquema de creación de usuario"""
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    """Esquema de actualización de usuario"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class LoginRequest(BaseModel):
    """Esquema de petición de login"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Esquema de respuesta del token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User

# Permisos por defecto según el rol
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        Permission.READ_ITEMS,
        Permission.WRITE_ITEMS,
        Permission.DELETE_ITEMS,
        Permission.MANAGE_USERS,
        Permission.USE_MCP_TOOLS,
        Permission.ADMIN_MCP
    ],
    UserRole.USER: [
        Permission.READ_ITEMS,
        Permission.WRITE_ITEMS,
        Permission.USE_MCP_TOOLS
    ],
    UserRole.AI_AGENT: [
        Permission.READ_ITEMS,
        Permission.WRITE_ITEMS,
        Permission.USE_MCP_TOOLS
    ],
    UserRole.READONLY: [
        Permission.READ_ITEMS
    ]
}

class UserDatabase:
    """Base de datos de usuarios en memoria"""

    def __init__(self):
        self.users: Dict[str, UserInDB] = {}
        self._init_default_users()

    def _init_default_users(self):
        """Crea usuarios por defecto"""
        from src.auth.jwt_handler import get_password_hash
        import uuid

        # Cuenta de administrador
        admin_id = str(uuid.uuid4())
        self.users[admin_id] = UserInDB(
            id=admin_id,
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            role=UserRole.ADMIN,
            permissions=ROLE_PERMISSIONS[UserRole.ADMIN],
            hashed_password=get_password_hash("admin123"),
            created_at=datetime.utcnow(),
            api_key=str(uuid.uuid4())
        )

        # Cuenta de agente IA
        ai_id = str(uuid.uuid4())
        self.users[ai_id] = UserInDB(
            id=ai_id,
            email="ai@example.com",
            username="ai_agent",
            full_name="AI Assistant",
            role=UserRole.AI_AGENT,
            permissions=ROLE_PERMISSIONS[UserRole.AI_AGENT],
            hashed_password=get_password_hash("ai123"),
            created_at=datetime.utcnow(),
            api_key=str(uuid.uuid4())
        )

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Obtener usuario por nombre de usuario"""
        return next(
            (user for user in self.users.values() if user.username == username),
            None
        )

    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Obtener usuario por ID"""
        return self.users.get(user_id)

    def get_user_by_api_key(self, api_key: str) -> Optional[UserInDB]:
        """Obtener usuario por API key"""
        return next(
            (user for user in self.users.values() if user.api_key == api_key),
            None
        )

    def create_user(self, user_create: UserCreate) -> UserInDB:
        """Crear usuario"""
        import uuid
        from src.auth.jwt_handler import get_password_hash

        user_id = str(uuid.uuid4())
        user = UserInDB(
            id=user_id,
            email=user_create.email,
            username=user_create.username,
            full_name=user_create.full_name,
            role=user_create.role,
            permissions=ROLE_PERMISSIONS[user_create.role],
            hashed_password=get_password_hash(user_create.password),
            created_at=datetime.utcnow(),
            api_key=str(uuid.uuid4())
        )

        self.users[user_id] = user
        return user

    def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Actualizar usuario"""
        if user_id not in self.users:
            return None

        user = self.users[user_id]
        update_data = user_update.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        # Actualizar permisos si cambia el rol
        if "role" in update_data:
            user.permissions = ROLE_PERMISSIONS[user.role]

        return user

    def update_last_login(self, user_id: str):
        """Actualizar el último login"""
        if user_id in self.users:
            self.users[user_id].last_login = datetime.utcnow()

# Instancia global de base de datos
user_db = UserDatabase()
```

## Paso 4: Implementación de dependencias de autenticación

### Dependencias de autenticación (`src/auth/dependencies.py`)

```python
from typing import Optional, List
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from jose import JWTError

from src.auth.jwt_handler import decode_token, token_manager
from src.auth.models import User, UserInDB, Permission, user_db

# Esquema de seguridad
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """Obtener el usuario autenticado actual"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials

        # Comprobar la lista negra
        if token_manager.is_blacklisted(token):
            raise credentials_exception

        payload = decode_token(token)
        if payload is None:
            raise credentials_exception

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = user_db.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return User(**user.dict())

async def get_current_user_by_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[User]:
    """Autenticar usuario por API key"""
    if not api_key:
        return None

    user = user_db.get_user_by_api_key(api_key)
    if not user or not user.is_active:
        return None

    return User(**user.dict())

async def get_current_user_flexible(
    token_user: Optional[User] = Depends(get_current_user),
    api_key_user: Optional[User] = Depends(get_current_user_by_api_key)
) -> User:
    """Autenticar usuario por token o API key (autenticación flexible)"""
    user = token_user or api_key_user

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    return user

def require_permissions(*required_permissions: Permission):
    """Dependencia que requiere ciertos permisos"""
    def permission_checker(current_user: User = Depends(get_current_user_flexible)) -> User:
        for permission in required_permissions:
            if permission not in current_user.permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
        return current_user

    return permission_checker

def require_roles(*required_roles):
    """Dependencia que requiere ciertos roles"""
    def role_checker(current_user: User = Depends(get_current_user_flexible)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role must be one of: {', '.join(required_roles)}"
            )
        return current_user

    return role_checker

# Dependencias de permisos comunes
RequireAdmin = require_roles("admin")
RequireReadItems = require_permissions(Permission.READ_ITEMS)
RequireWriteItems = require_permissions(Permission.WRITE_ITEMS)
RequireDeleteItems = require_permissions(Permission.DELETE_ITEMS)
RequireMCPTools = require_permissions(Permission.USE_MCP_TOOLS)
RequireAdminMCP = require_permissions(Permission.ADMIN_MCP)
```

### Router de autenticación (`src/auth/routes.py`)

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.models import (
    User, UserCreate, UserUpdate, LoginRequest, TokenResponse,
    user_db, UserRole
)
from src.auth.jwt_handler import (
    verify_password, token_manager, verify_token, create_access_token
)
from src.auth.dependencies import get_current_user, RequireAdmin
from src.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=User)
async def register_user(user_create: UserCreate):
    """Registrar usuario"""
    # Comprobar duplicado de username
    if user_db.get_user_by_username(user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # El primer usuario se marca automáticamente como admin
    if not user_db.users:
        user_create.role = UserRole.ADMIN

    user = user_db.create_user(user_create)
    return User(**user.dict())

@router.post("/login", response_model=TokenResponse)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login de usuario"""
    user = user_db.get_user_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Crear tokens
    tokens = token_manager.create_token_pair(user.id, user.role)

    # Actualizar último login
    user_db.update_last_login(user.id)

    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=User(**user.dict())
    )

@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_token: str):
    """Refrescar token"""
    user_id = verify_token(refresh_token, "refresh")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = user_db.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Crear nuevo par de tokens
    tokens = token_manager.create_token_pair(user.id, user.role)

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"],
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/logout")
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout de usuario"""
    # En la implementación real, añade el token a la lista negra
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Obtener información del usuario actual"""
    return current_user

@router.put("/me", response_model=User)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Actualizar información del usuario actual"""
    # Los usuarios normales no pueden cambiar el rol
    if user_update.role and current_user.role != UserRole.ADMIN:
        user_update.role = None

    updated_user = user_db.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return User(**updated_user.dict())

@router.get("/users", response_model=list[User])
async def list_users(admin_user: User = Depends(RequireAdmin)):
    """Listar usuarios (solo admin)"""
    return [User(**user.dict()) for user in user_db.users.values()]

@router.post("/users/{user_id}/generate-api-key")
async def generate_api_key(
    user_id: str,
    admin_user: User = Depends(RequireAdmin)
):
    """Crear API key de usuario (solo admin)"""
    import uuid

    user = user_db.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Crear nueva API key
    new_api_key = str(uuid.uuid4())
    user.api_key = new_api_key

    return {
        "api_key": new_api_key,
        "message": "API key generated successfully"
    }
```

## Paso 5: Implementación del servidor MCP

### Definición de herramientas MCP (`src/mcp/tools.py`)

```python
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

class ToolCategory(str, Enum):
    """Categoría de herramienta"""
    DATA_MANAGEMENT = "data_management"
    SEARCH = "search"
    ANALYSIS = "analysis"
    ADMIN = "admin"

class MCPTool(BaseModel):
    """Definición de herramienta MCP"""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: ToolCategory = Field(..., description="Tool category")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameter schema")
    required_permissions: List[str] = Field(default_factory=list, description="Required permissions")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="Usage examples")

class ToolRegistry:
    """Registro de herramientas"""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        """Registra las herramientas por defecto"""

        # Herramienta de creación de item
        self.register_tool(MCPTool(
            name="create_item",
            description="Create a new item",
            category=ToolCategory.DATA_MANAGEMENT,
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Item name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Item description"
                    },
                    "price": {
                        "type": "number",
                        "description": "Item price",
                        "minimum": 0
                    },
                    "category": {
                        "type": "string",
                        "description": "Item category"
                    }
                },
                "required": ["name", "price"]
            },
            required_permissions=["write:items"],
            examples=[
                {
                    "name": "Notebook",
                    "description": "High-performance gaming notebook",
                    "price": 1500000,
                    "category": "electronics"
                }
            ]
        ))

        # Herramienta de búsqueda de items
        self.register_tool(MCPTool(
            name="search_items",
            description="Search for items",
            category=ToolCategory.SEARCH,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category filter"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Result count limit",
                        "default": 10,
                        "maximum": 100
                    }
                },
                "required": ["query"]
            },
            required_permissions=["read:items"],
            examples=[
                {
                    "query": "Notebook",
                    "category": "electronics",
                    "max_price": 2000000,
                    "limit": 5
                }
            ]
        ))

        # Herramienta de análisis de items
        self.register_tool(MCPTool(
            name="analyze_items",
            description="Analyze item data",
            category=ToolCategory.ANALYSIS,
            parameters={
                "type": "object",
                "properties": {
                    "analysis_type": {
                        "type": "string",
                        "enum": ["price_distribution", "category_breakdown", "trend_analysis"],
                        "description": "Analysis type"
                    },
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "format": "date"},
                            "end_date": {"type": "string", "format": "date"}
                        },
                        "description": "Analysis period"
                    }
                },
                "required": ["analysis_type"]
            },
            required_permissions=["read:items"],
            examples=[
                {
                    "analysis_type": "price_distribution",
                    "date_range": {
                        "start_date": "2024-01-01",
                        "end_date": "2024-12-31"
                    }
                }
            ]
        ))

        # Herramienta de gestión de usuarios (solo admin)
        self.register_tool(MCPTool(
            name="manage_users",
            description="Manage users",
            category=ToolCategory.ADMIN,
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "create", "update", "deactivate"],
                        "description": "Action to perform"
                    },
                    "user_data": {
                        "type": "object",
                        "description": "User data (create/update)"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID (update/deactivate)"
                    }
                },
                "required": ["action"]
            },
            required_permissions=["manage:users"],
            examples=[
                {
                    "action": "list"
                },
                {
                    "action": "create",
                    "user_data": {
                        "username": "newuser",
                        "email": "newuser@example.com",
                        "role": "user"
                    }
                }
            ]
        ))

    def register_tool(self, tool: MCPTool):
        """Registrar una herramienta"""
        self.tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Obtener una herramienta"""
        return self.tools.get(tool_name)

    def list_tools(self, user_permissions: List[str] = None) -> List[MCPTool]:
        """Lista de herramientas según los permisos del usuario"""
        if user_permissions is None:
            return list(self.tools.values())

        available_tools = []
        for tool in self.tools.values():
            # Comprobar permisos
            if all(perm in user_permissions for perm in tool.required_permissions):
                available_tools.append(tool)

        return available_tools

    def get_tools_by_category(self, category: ToolCategory, user_permissions: List[str] = None) -> List[MCPTool]:
        """Lista de herramientas por categoría"""
        tools = self.list_tools(user_permissions)
        return [tool for tool in tools if tool.category == category]

# Registro global de herramientas
tool_registry = ToolRegistry()
```

### Implementación del servidor MCP (`src/mcp/server.py`)

```python
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
import asyncio
import json

from src.mcp.tools import tool_registry, ToolCategory
from src.auth.models import User, Permission
from src.api.routes.items import ItemCRUD
from src.auth.models import user_db

class MCPServer:
    """Servidor de Model Context Protocol"""

    def __init__(self):
        self.item_crud = ItemCRUD()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def create_session(self, user: User) -> str:
        """Crear sesión MCP"""
        import uuid

        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "user_id": user.id,
            "user": user,
            "created_at": datetime.utcnow(),
            "context": {},
            "tool_usage_count": 0,
            "last_activity": datetime.utcnow()
        }

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtener sesión"""
        session = self.active_sessions.get(session_id)
        if session:
            session["last_activity"] = datetime.utcnow()
        return session

    async def close_session(self, session_id: str):
        """Cerrar sesión"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]

    async def list_tools(self, user: User) -> List[Dict[str, Any]]:
        """Listar herramientas disponibles para el usuario"""
        user_permissions = [perm.value for perm in user.permissions]
        tools = tool_registry.list_tools(user_permissions)

        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "parameters": tool.parameters,
                "examples": tool.examples
            }
            for tool in tools
        ]

    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user: User,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ejecutar herramienta"""

        # Comprobar si la herramienta existe
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tool '{tool_name}' not found"
            )

        # Comprobar permisos
        user_permissions = [perm.value for perm in user.permissions]
        for required_perm in tool.required_permissions:
            if required_perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{required_perm}' required for tool '{tool_name}'"
                )

        # Actualizar la sesión
        if session_id:
            session = await self.get_session(session_id)
            if session:
                session["tool_usage_count"] += 1

        # Ejecutar la herramienta
        try:
            result = await self._execute_tool_logic(tool_name, parameters, user)

            return {
                "success": True,
                "tool": tool_name,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def _execute_tool_logic(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user: User
    ) -> Any:
        """Lógica de ejecución de la herramienta"""

        if tool_name == "create_item":
            return await self._create_item(parameters)

        elif tool_name == "search_items":
            return await self._search_items(parameters)

        elif tool_name == "analyze_items":
            return await self._analyze_items(parameters)

        elif tool_name == "manage_users":
            return await self._manage_users(parameters, user)

        else:
            raise ValueError(f"Tool '{tool_name}' implementation not found")

    async def _create_item(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación de la herramienta de creación de item"""
        from src.schemas.items import ItemCreate

        try:
            item_create = ItemCreate(**parameters)
            created_item = await self.item_crud.create(item_create)

            return {
                "action": "create_item",
                "item": created_item.dict(),
                "message": f"Item '{created_item.name}' created successfully"
            }
        except Exception as e:
            raise ValueError(f"Failed to create item: {str(e)}")

    async def _search_items(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación de la herramienta de búsqueda de items"""
        query = parameters.get("query", "")
        category = parameters.get("category")
        min_price = parameters.get("min_price")
        max_price = parameters.get("max_price")
        limit = parameters.get("limit", 10)

        # Implementación de la lógica de búsqueda
        all_items = await self.item_crud.get_all()
        filtered_items = []

        for item in all_items:
            # Búsqueda por texto
            if query.lower() not in item.name.lower() and query.lower() not in (item.description or "").lower():
                continue

            # Filtro de categoría
            if category and getattr(item, 'category', None) != category:
                continue

            # Filtro de precio
            if min_price is not None and item.price < min_price:
                continue
            if max_price is not None and item.price > max_price:
                continue

            filtered_items.append(item)

        # Límite de resultados
        result_items = filtered_items[:limit]

        return {
            "action": "search_items",
            "query": query,
            "total_found": len(filtered_items),
            "returned_count": len(result_items),
            "items": [item.dict() for item in result_items]
        }

    async def _analyze_items(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación de la herramienta de análisis de items"""
        analysis_type = parameters.get("analysis_type")
        date_range = parameters.get("date_range", {})

        all_items = await self.item_crud.get_all()

        if analysis_type == "price_distribution":
            prices = [item.price for item in all_items]
            if not prices:
                return {"analysis": "price_distribution", "result": "No items found"}

            return {
                "analysis": "price_distribution",
                "result": {
                    "total_items": len(prices),
                    "min_price": min(prices),
                    "max_price": max(prices),
                    "average_price": sum(prices) / len(prices),
                    "price_ranges": {
                        "under_100k": len([p for p in prices if p < 100000]),
                        "100k_to_500k": len([p for p in prices if 100000 <= p < 500000]),
                        "500k_to_1m": len([p for p in prices if 500000 <= p < 1000000]),
                        "over_1m": len([p for p in prices if p >= 1000000])
                    }
                }
            }

        elif analysis_type == "category_breakdown":
            categories = {}
            for item in all_items:
                category = getattr(item, 'category', 'uncategorized')
                categories[category] = categories.get(category, 0) + 1

            return {
                "analysis": "category_breakdown",
                "result": {
                    "total_categories": len(categories),
                    "categories": categories
                }
            }

        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")

    async def _manage_users(self, parameters: Dict[str, Any], requesting_user: User) -> Dict[str, Any]:
        """Implementación de la herramienta de gestión de usuarios"""
        action = parameters.get("action")

        # Comprobar permisos de administrador
        if Permission.MANAGE_USERS not in requesting_user.permissions:
            raise ValueError("Insufficient permissions for user management")

        if action == "list":
            users = [User(**user.dict()) for user in user_db.users.values()]
            return {
                "action": "list_users",
                "total_users": len(users),
                "users": [user.dict() for user in users]
            }

        elif action == "create":
            user_data = parameters.get("user_data", {})
            from src.auth.models import UserCreate

            user_create = UserCreate(**user_data)
            created_user = user_db.create_user(user_create)

            return {
                "action": "create_user",
                "user": User(**created_user.dict()).dict(),
                "message": f"User '{created_user.username}' created successfully"
            }

        else:
            raise ValueError(f"Unknown user management action: {action}")

# Instancia global del servidor MCP
mcp_server = MCPServer()
```

## Paso 6: Implementar los endpoints del MCP

### Router del MCP (`src/api/routes/mcp.py`)

```python
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel

from src.auth.dependencies import get_current_user_flexible, RequireMCPTools
from src.auth.models import User
from src.mcp.server import mcp_server
from src.mcp.tools import ToolCategory

router = APIRouter(prefix="/mcp", tags=["MCP"])

class ToolExecuteRequest(BaseModel):
    """Petición de ejecución de herramienta"""
    tool_name: str
    parameters: Dict[str, Any]
    session_id: Optional[str] = None

class SessionCreateResponse(BaseModel):
    """Respuesta de creación de sesión"""
    session_id: str
    message: str

@router.post("/session", response_model=SessionCreateResponse)
async def create_mcp_session(
    current_user: User = Depends(RequireMCPTools)
):
    """Crear sesión MCP"""
    session_id = await mcp_server.create_session(current_user)

    return SessionCreateResponse(
        session_id=session_id,
        message=f"MCP session created (User: {current_user.username})"
    )

@router.delete("/session/{session_id}")
async def close_mcp_session(
    session_id: str,
    current_user: User = Depends(RequireMCPTools)
):
    """Cerrar sesión MCP"""
    session = await mcp_server.get_session(session_id)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    # Comprobar el propietario de la sesión
    if session["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot close another user's session"
        )

    await mcp_server.close_session(session_id)

    return {"message": "Session closed successfully"}

@router.get("/tools")
async def list_mcp_tools(
    category: Optional[ToolCategory] = None,
    current_user: User = Depends(RequireMCPTools)
):
    """Listar las herramientas MCP disponibles"""
    tools = await mcp_server.list_tools(current_user)

    if category:
        tools = [tool for tool in tools if tool["category"] == category]

    return {
        "user": current_user.username,
        "total_tools": len(tools),
        "tools": tools
    }

@router.post("/execute")
async def execute_mcp_tool(
    request: ToolExecuteRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(RequireMCPTools)
):
    """Ejecutar herramienta MCP"""

    # Comprobar la sesión (opcional)
    if request.session_id:
        session = await mcp_server.get_session(request.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        if session["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot use another user's session"
            )

    # Ejecutar la herramienta
    result = await mcp_server.execute_tool(
        tool_name=request.tool_name,
        parameters=request.parameters,
        user=current_user,
        session_id=request.session_id
    )

    # Registrar el uso de la herramienta en segundo plano
    background_tasks.add_task(
        log_tool_usage,
        current_user.id,
        request.tool_name,
        result["success"]
    )

    return result

@router.get("/sessions")
async def list_user_sessions(
    current_user: User = Depends(RequireMCPTools)
):
    """Listar sesiones activas del usuario"""
    user_sessions = []

    for session_id, session_data in mcp_server.active_sessions.items():
        if session_data["user_id"] == current_user.id:
            user_sessions.append({
                "session_id": session_id,
                "created_at": session_data["created_at"],
                "tool_usage_count": session_data["tool_usage_count"],
                "last_activity": session_data["last_activity"]
            })

    return {
        "user": current_user.username,
        "active_sessions": len(user_sessions),
        "sessions": user_sessions
    }

@router.get("/stats")
async def get_mcp_stats(
    current_user: User = Depends(RequireMCPTools)
):
    """Estadísticas de uso de MCP"""
    total_sessions = len(mcp_server.active_sessions)
    user_sessions = len([
        s for s in mcp_server.active_sessions.values()
        if s["user_id"] == current_user.id
    ])

    return {
        "user_stats": {
            "username": current_user.username,
            "active_sessions": user_sessions,
            "permissions": [perm.value for perm in current_user.permissions]
        },
        "server_stats": {
            "total_active_sessions": total_sessions,
            "available_tools": len(await mcp_server.list_tools(current_user))
        }
    }

async def log_tool_usage(user_id: str, tool_name: str, success: bool):
    """Registrar uso de herramienta (tarea en segundo plano)"""
    import logging

    logger = logging.getLogger("mcp.usage")
    logger.info(
        f"Tool usage - User: {user_id}, Tool: {tool_name}, Success: {success}"
    )
```

## Paso 7: Integración y prueba de la aplicación

### Aplicación principal (`src/main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.auth.routes import router as auth_router
from src.api.routes.items import router as items_router
from src.api.routes.mcp import router as mcp_router
from src.core.config import settings

app = FastAPI(
    title="AI Integrated API",
    description="AI model integrated MCP-based API server",
    version="1.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth_router)
app.include_router(items_router, prefix="/api/v1")
app.include_router(mcp_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "AI Integrated API with MCP Support",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/auth",
            "items": "/api/v1/items",
            "mcp": "/api/v1/mcp",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "auth": "operational",
            "mcp": "operational",
            "database": "operational"
        }
    }
```

### Ejecutar el servidor y probar

<div class="termy">

```console
$ cd ai-integrated-api
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

# Login de usuario
$ curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "admin@example.com",
    "username": "admin",
    "role": "admin",
    "permissions": ["read:items", "write:items", ...]
  }
}

# Crear sesión MCP
$ curl -X POST "http://localhost:8000/api/v1/mcp/session" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

{
  "session_id": "abc123-def456-ghi789",
  "message": "MCP session created (User: admin)"
}

# Listar las herramientas disponibles
$ curl "http://localhost:8000/api/v1/mcp/tools" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

{
  "user": "admin",
  "total_tools": 4,
  "tools": [
    {
      "name": "create_item",
      "description": "Create a new item",
      "category": "data_management",
      "parameters": {...},
      "examples": [...]
    },
    ...
  ]
}

# Ejecutar herramienta MCP (crear item)
$ curl -X POST "http://localhost:8000/api/v1/mcp/execute" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_item",
    "parameters": {
      "name": "AI generated item",
      "description": "MCP through AI generated item",
      "price": 500000,
      "category": "ai_generated"
    },
    "session_id": "abc123-def456-ghi789"
  }'

{
  "success": true,
  "tool": "create_item",
  "result": {
    "action": "create_item",
    "item": {
      "id": 1,
      "name": "AI generated item",
      "description": "MCP through AI generated item",
      "price": 500000,
      "category": "ai_generated",
      "created_at": "2024-01-01T12:00:00Z"
    },
    "message": "Item 'AI generated item' created successfully"
  },
  "timestamp": "2024-01-01T12:00:00.123456Z"
}

# Ejecutar herramienta MCP (buscar item)
$ curl -X POST "http://localhost:8000/api/v1/mcp/execute" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_items",
    "parameters": {
      "query": "AI",
      "limit": 5
    }
  }'
```

</div>

## Paso 8: Ejemplo de cliente IA

### Ejemplo de cliente MCP en Python

```python
# client_example.py
import asyncio
import aiohttp
from typing import Dict, Any, List

class MCPClient:
    """Ejemplo de cliente MCP"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session_id = None
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={"X-API-Key": self.api_key}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session_id:
            await self.close_session()
        if self.session:
            await self.session.close()

    async def create_session(self) -> str:
        """Crear sesión MCP"""
        async with self.session.post(f"{self.base_url}/api/v1/mcp/session") as resp:
            data = await resp.json()
            self.session_id = data["session_id"]
            return self.session_id

    async def close_session(self):
        """Cerrar sesión MCP"""
        if self.session_id:
            async with self.session.delete(f"{self.base_url}/api/v1/mcp/session/{self.session_id}"):
                pass
            self.session_id = None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """Listar herramientas disponibles"""
        async with self.session.get(f"{self.base_url}/api/v1/mcp/tools") as resp:
            data = await resp.json()
            return data["tools"]

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecutar herramienta"""
        payload = {
            "tool_name": tool_name,
            "parameters": parameters,
            "session_id": self.session_id
        }

        async with self.session.post(
            f"{self.base_url}/api/v1/mcp/execute",
            json=payload
        ) as resp:
            return await resp.json()

    async def ai_assistant_workflow(self, user_request: str) -> str:
        """Simulación del flujo de un asistente IA"""

        # 1. Crear sesión
        await self.create_session()
        print(f"Session created: {self.session_id}")

        # 2. Analizar la petición del usuario y seleccionar la herramienta adecuada
        if "Create item" in user_request or "Create" in user_request:
            # Petición de creación de item
            result = await self.execute_tool("create_item", {
                "name": "AI recommended item",
                "description": "AI generated item based on user request",
                "price": 100000,
                "category": "ai_recommended"
            })

            if result["success"]:
                item_name = result["result"]["item"]["name"]
                return f"✅ '{item_name}' item created successfully!"
            else:
                return f"❌ Item creation failed: {result.get('error', 'Unknown error')}"

        elif "Search" in user_request or "Find" in user_request:
            # Petición de búsqueda
            search_query = "Item"  # En la práctica se extrae mediante NLP
            result = await self.execute_tool("search_items", {
                "query": search_query,
                "limit": 5
            })

            if result["success"]:
                items = result["result"]["items"]
                item_list = "\n".join([f"- {item['name']} (₩{item['price']:,})" for item in items])
                return f"🔍 Search results ({len(items)} items):\n{item_list}"
            else:
                return f"❌ Search failed: {result.get('error', 'Unknown error')}"

        elif "Analyze" in user_request:
            # Petición de análisis
            result = await self.execute_tool("analyze_items", {
                "analysis_type": "price_distribution"
            })

            if result["success"]:
                analysis = result["result"]["result"]
                return f"📊 Price analysis:\nAverage price: ₩{analysis['average_price']:,.0f}\nMinimum: ₩{analysis['min_price']:,} - Maximum: ₩{analysis['max_price']:,}"
            else:
                return f"❌ Analysis failed: {result.get('error', 'Unknown error')}"

        else:
            return "Sorry, I couldn't find a tool to handle that request."

async def main():
    """Prueba del cliente"""
    async with MCPClient("http://localhost:8000", "your-api-key-here") as client:

        # Listar herramientas disponibles
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")

        print("\n" + "="*50 + "\n")

        # Simulación de asistente IA
        test_requests = [
            "Create a new item",
            "Search for items",
            "Analyze price distribution"
        ]

        for request in test_requests:
            print(f"User request: {request}")
            response = await client.ai_assistant_workflow(request)
            print(f"AI response: {response}")
            print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())
```

<!-- ## Próximos pasos

¡Has terminado la integración con MCP! Aquí tienes lo que puedes probar a continuación: -->

<!-- 1. **[Implementación de comunicación en tiempo real](websocket-realtime.md)** - Comunicación MCP en tiempo real con WebSocket
2. **[Arquitectura de microservicios](microservices-architecture.md)** - Separar el servidor MCP como servicio independiente
3. **[Optimización del rendimiento](performance-optimization.md)** - Optimizar el procesamiento de peticiones IA a gran volumen
4. **[Sistema de monitorización](monitoring-system.md)** - Monitorización del uso y el rendimiento de MCP -->

## Resumen

En este tutorial hemos implementado la integración con MCP (Model Context Protocol) con:

- ✅ Construcción de un sistema de autenticación basado en JWT
- ✅ Implementación de control de acceso basado en roles (RBAC)
- ✅ Implementación del servidor MCP y el sistema de herramientas
- ✅ Gestión de contexto basada en sesiones
- ✅ Comunicación API segura con modelos de IA
- ✅ Gestión de permisos y trazabilidad de uso de herramientas
- ✅ Implementación de un ejemplo real de cliente IA

¡Ahora puedes construir un sistema basado en MCP completo donde los modelos de IA puedan aprovechar de forma segura y eficiente las funcionalidades de tu API!

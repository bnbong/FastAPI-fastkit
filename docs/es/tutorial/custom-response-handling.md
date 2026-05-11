# Manejo personalizado de respuestas y diseño avanzado de APIs

Aprende a implementar formatos de respuesta consistentes, manejo de errores, paginación y documentación OpenAPI personalizada con las funcionalidades avanzadas de FastAPI. Implementaremos patrones de diseño de API a nivel empresa usando la plantilla `fastapi-custom-response`.

## Lo que aprenderás en este tutorial

- Diseñar formatos de respuesta estandarizados
- Manejo global de excepciones y respuestas de error personalizadas
- Implementar sistemas de paginación
- Filtrado y ordenación
- Personalizar la documentación OpenAPI
- Versionado de la API
- Caché y optimización de respuestas

## Requisitos previos

- Haber completado el [tutorial de contenedorización con Docker](docker-deployment.md)
- Conocer los principios de diseño REST
- Conocer los códigos de estado HTTP
- Conceptos básicos de OpenAPI / Swagger

## Importancia de respuestas de API estandarizadas

### Respuestas inconsistentes vs estandarizadas

**Formato de respuesta problemático:**
```json
// Éxito
{"id": 1, "name": "item"}

// Error
{"detail": "Not found"}

// Listado
[{"id": 1}, {"id": 2}]
```

**Formato de respuesta estandarizado:**
```json
// Éxito
{
  "success": true,
  "data": {"id": 1, "name": "item"},
  "message": "Item retrieved successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}

// Error
{
  "success": false,
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "Item not found",
    "details": {"item_id": 123}
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

## Paso 1: Crear un proyecto de respuestas personalizadas

Crea un proyecto con la plantilla `fastapi-custom-response`:

<div class="termy">

```console
$ fastkit startdemo fastapi-custom-response
Enter the project name: advanced-api-server
Enter the author name: Developer Kim
Enter the author email: developer@example.com
Enter the project description: API server with advanced response handling
Deploying FastAPI project using 'fastapi-custom-response' template

           Project Information
┌──────────────┬─────────────────────────────────────────────┐
│ Project Name │ advanced-api-server                         │
│ Author       │ Developer Kim                               │
│ Author Email │ developer@example.com                       │
│ Description  │ API server with advanced response handling  │
└──────────────┴─────────────────────────────────────────────┘

       Template Dependencies
┌──────────────┬───────────────────┐
│ Dependency 1 │ fastapi           │
│ Dependency 2 │ uvicorn           │
│ Dependency 3 │ pydantic          │
│ Dependency 4 │ pydantic-settings │
│ Dependency 5 │ aiofiles          │
│ Dependency 6 │ python-multipart  │
└──────────────┴───────────────────┘

Select package manager (pip, uv, pdm, poetry) [uv]: uv
Do you want to proceed with project creation? [y/N]: y

✨ FastAPI project 'advanced-api-server' from 'fastapi-custom-response' has been created successfully!
```

</div>

## Paso 2: Analizar la estructura del proyecto

Examinemos las funcionalidades avanzadas del proyecto generado:

```
advanced-api-server/
├── src/
│   ├── main.py                     # Aplicación FastAPI
│   ├── schemas/
│   │   ├── base.py                 # Esquemas base de respuesta
│   │   ├── items.py                # Esquemas de items
│   │   └── responses.py            # Definiciones de formato de respuesta
│   ├── helper/
│   │   ├── exceptions.py           # Clases de excepciones personalizadas
│   │   └── pagination.py           # Helpers de paginación
│   ├── utils/
│   │   ├── responses.py            # Utilidades de respuesta
│   │   └── documents.py            # Personalización de OpenAPI
│   ├── api/
│   │   └── routes/
│   │       └── items.py            # Endpoints avanzados
│   ├── crud/
│   │   └── items.py                # Lógica CRUD
│   └── core/
│       └── config.py               # Configuración
└── tests/
    └── test_responses.py           # Pruebas de formato de respuesta
```

## Paso 3: Implementar esquemas de respuesta estandarizados

### Esquema base de respuesta (`src/schemas/base.py`)

```python
from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """Estado de la respuesta"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ErrorDetail(BaseModel):
    """Información detallada del error"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field where error occurred")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error information")

class BaseResponse(BaseModel, Generic[T]):
    """Formato base de respuesta"""
    success: bool = Field(..., description="Request success status")
    status: ResponseStatus = Field(..., description="Response status")
    data: Optional[T] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

class ErrorResponse(BaseModel):
    """Formato de respuesta de error"""
    success: bool = Field(False, description="Request success status")
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="Response status")
    error: ErrorDetail = Field(..., description="Error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

class PaginationMeta(BaseModel):
    """Metadatos de paginación"""
    page: int = Field(..., ge=1, description="Current page")
    size: int = Field(..., ge=1, le=100, description="Page size")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether next page exists")
    has_prev: bool = Field(..., description="Whether previous page exists")

class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada"""
    success: bool = Field(True, description="Request success status")
    status: ResponseStatus = Field(ResponseStatus.SUCCESS, description="Response status")
    data: List[T] = Field(..., description="Data list")
    meta: PaginationMeta = Field(..., description="Pagination information")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response time")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

class ValidationErrorDetail(BaseModel):
    """Detalle de error de validación"""
    field: str = Field(..., description="Validation failed field")
    message: str = Field(..., description="Error message")
    invalid_value: Any = Field(..., description="Invalid value")

class ValidationErrorResponse(BaseModel):
    """Respuesta de error de validación"""
    success: bool = Field(False, description="Request success status")
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="Response status")
    error: ErrorDetail = Field(..., description="Error information")
    validation_errors: List[ValidationErrorDetail] = Field(..., description="Validation error list")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response time")
    request_id: Optional[str] = Field(None, description="Request tracking ID")
```

### Funciones utilitarias de respuesta (`src/utils/responses.py`)

```python
from typing import Any, Optional, List, TypeVar
from fastapi import Request
from fastapi.responses import JSONResponse
import uuid

from src.schemas.base import (
    BaseResponse, ErrorResponse, PaginatedResponse,
    ResponseStatus, ErrorDetail, PaginationMeta
)

T = TypeVar('T')

def generate_request_id() -> str:
    """Generar un ID de seguimiento de la petición"""
    return str(uuid.uuid4())

def success_response(
    data: Any = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """Generar respuesta de éxito"""
    response_data = BaseResponse[Any](
        success=True,
        status=ResponseStatus.SUCCESS,
        data=data,
        message=message or "Request processed successfully",
        request_id=request_id or generate_request_id()
    )

    return JSONResponse(
        status_code=status_code,
        content=response_data.dict(exclude_none=True)
    )

def error_response(
    error_code: str,
    error_message: str,
    details: Optional[dict] = None,
    status_code: int = 400,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Generar respuesta de error"""
    error_detail = ErrorDetail(
        code=error_code,
        message=error_message,
        details=details
    )

    response_data = ErrorResponse(
        error=error_detail,
        request_id=request_id or generate_request_id()
    )

    return JSONResponse(
        status_code=status_code,
        content=response_data.dict(exclude_none=True)
    )

def paginated_response(
    data: List[T],
    page: int,
    size: int,
    total: int,
    message: Optional[str] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Generar respuesta paginada"""
    pages = (total + size - 1) // size  # redondeo hacia arriba
    has_next = page < pages
    has_prev = page > 1

    meta = PaginationMeta(
        page=page,
        size=size,
        total=total,
        pages=pages,
        has_next=has_next,
        has_prev=has_prev
    )

    response_data = PaginatedResponse[T](
        data=data,
        meta=meta,
        message=message or f"Page {page}/{pages} data retrieved",
        request_id=request_id or generate_request_id()
    )

    return JSONResponse(
        status_code=200,
        content=response_data.dict(exclude_none=True)
    )

class ResponseHelper:
    """Helper de respuestas"""

    @staticmethod
    def created(data: Any, message: str = "Resource created successfully") -> JSONResponse:
        return success_response(data=data, message=message, status_code=201)

    @staticmethod
    def updated(data: Any, message: str = "Resource updated successfully") -> JSONResponse:
        return success_response(data=data, message=message, status_code=200)

    @staticmethod
    def deleted(message: str = "Resource deleted successfully") -> JSONResponse:
        return success_response(data=None, message=message, status_code=204)

    @staticmethod
    def not_found(resource: str = "Resource") -> JSONResponse:
        return error_response(
            error_code="RESOURCE_NOT_FOUND",
            error_message=f"{resource} not found",
            status_code=404
        )

    @staticmethod
    def bad_request(message: str = "Bad request") -> JSONResponse:
        return error_response(
            error_code="BAD_REQUEST",
            error_message=message,
            status_code=400
        )

    @staticmethod
    def unauthorized(message: str = "Authentication required") -> JSONResponse:
        return error_response(
            error_code="UNAUTHORIZED",
            error_message=message,
            status_code=401
        )

    @staticmethod
    def forbidden(message: str = "Permission denied") -> JSONResponse:
        return error_response(
            error_code="FORBIDDEN",
            error_message=message,
            status_code=403
        )

    @staticmethod
    def server_error(message: str = "Server internal error occurred") -> JSONResponse:
        return error_response(
            error_code="INTERNAL_SERVER_ERROR",
            error_message=message,
            status_code=500
        )
```

## Paso 4: Sistema personalizado de manejo de excepciones

### Clase de excepción personalizada (`src/helper/exceptions.py`)

```python
from typing import Optional, Dict, Any
from fastapi import HTTPException

class BaseAPIException(HTTPException):
    """Clase base de excepción de la API"""

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)

class ValidationException(BaseAPIException):
    """Excepción de validación"""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details or {"field": field} if field else None
        )

class ResourceNotFoundException(BaseAPIException):
    """Excepción de recurso no encontrado"""

    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource}(ID: {resource_id}) not found",
            status_code=404,
            details={"resource": resource, "id": resource_id}
        )

class DuplicateResourceException(BaseAPIException):
    """Excepción de recurso duplicado"""

    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            error_code="DUPLICATE_RESOURCE",
            message=f"{resource} {field} '{value}' already exists",
            status_code=409,
            details={"resource": resource, "field": field, "value": value}
        )

class BusinessLogicException(BaseAPIException):
    """Excepción de lógica de negocio"""

    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=422
        )

class RateLimitException(BaseAPIException):
    """Excepción de límite de peticiones"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            error_code="RATE_LIMIT_EXCEEDED",
            message="Request limit exceeded. Please try again later",
            status_code=429,
            details={"retry_after": retry_after}
        )

class AuthenticationException(BaseAPIException):
    """Excepción de autenticación"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            error_code="AUTHENTICATION_REQUIRED",
            message=message,
            status_code=401
        )

class AuthorizationException(BaseAPIException):
    """Excepción de autorización"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            error_code="INSUFFICIENT_PERMISSIONS",
            message=message,
            status_code=403
        )
```

### Manejador global de excepciones (`src/main.py`)

```python
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging
import traceback

from src.helper.exceptions import BaseAPIException
from src.utils.responses import error_response, generate_request_id
from src.schemas.base import ValidationErrorDetail, ValidationErrorResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced API Server",
    description="API server with advanced response handling",
    version="1.0.0"
)

@app.exception_handler(BaseAPIException)
async def custom_api_exception_handler(request: Request, exc: BaseAPIException):
    """Manejador personalizado de excepciones de la API"""
    request_id = generate_request_id()

    logger.error(
        f"API Exception: {exc.error_code} - {exc.message}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )

    return error_response(
        error_code=exc.error_code,
        error_message=exc.message,
        details=exc.details,
        status_code=exc.status_code,
        request_id=request_id
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Manejador de excepciones de validación de Pydantic"""
    request_id = generate_request_id()

    validation_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append(
            ValidationErrorDetail(
                field=field,
                message=error["msg"],
                invalid_value=error.get("input", "")
            )
        )

    error_response_data = ValidationErrorResponse(
        error={
            "code": "VALIDATION_ERROR",
            "message": "Input data validation failed",
            "details": {"error_count": len(validation_errors)}
        },
        validation_errors=validation_errors,
        request_id=request_id
    )

    logger.warning(
        f"Validation Error: {len(validation_errors)} validation errors",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "errors": [err.dict() for err in validation_errors]
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response_data.dict(exclude_none=True)
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Manejador de excepciones HTTP"""
    request_id = generate_request_id()

    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        500: "INTERNAL_SERVER_ERROR"
    }

    error_code = error_code_map.get(exc.status_code, "HTTP_ERROR")

    return error_response(
        error_code=error_code,
        error_message=exc.detail,
        status_code=exc.status_code,
        request_id=request_id
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Manejador general de excepciones"""
    request_id = generate_request_id()

    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )

    return error_response(
        error_code="INTERNAL_SERVER_ERROR",
        error_message="Unexpected error occurred",
        status_code=500,
        request_id=request_id
    )
```

## Paso 5: Sistema avanzado de paginación

### Helper de paginación (`src/helper/pagination.py`)

```python
from typing import List, Optional, Any, Dict, Callable
from pydantic import BaseModel, Field
from fastapi import Query
from enum import Enum

class SortOrder(str, Enum):
    """Orden de la ordenación"""
    ASC = "asc"
    DESC = "desc"

class PaginationParams(BaseModel):
    """Parámetros de paginación"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order")

class FilterParams(BaseModel):
    """Parámetros de filtrado"""
    search: Optional[str] = Field(None, description="Search term")
    category: Optional[str] = Field(None, description="Category")
    status: Optional[str] = Field(None, description="Status")
    date_from: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")

def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: SortOrder = Query(SortOrder.ASC, description="Sort order")
) -> PaginationParams:
    """Dependencia de parámetros de paginación"""
    return PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

def filter_params(
    search: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Category"),
    status: Optional[str] = Query(None, description="Status"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
) -> FilterParams:
    """Dependencia de parámetros de filtrado"""
    return FilterParams(
        search=search,
        category=category,
        status=status,
        date_from=date_from,
        date_to=date_to
    )

class AdvancedPaginator:
    """Clase de paginación avanzada"""

    def __init__(self, data: List[Any], pagination: PaginationParams, filters: FilterParams):
        self.data = data
        self.pagination = pagination
        self.filters = filters
        self.filtered_data = self._apply_filters()
        self.sorted_data = self._apply_sorting()

    def _apply_filters(self) -> List[Any]:
        """Aplicar filtros"""
        filtered = self.data

        if self.filters.search:
            # Filtrar por término de búsqueda (ejemplo: campos name o description)
            search_term = self.filters.search.lower()
            filtered = [
                item for item in filtered
                if (hasattr(item, 'name') and search_term in item.name.lower()) or
                   (hasattr(item, 'description') and item.description and search_term in item.description.lower())
            ]

        if self.filters.category:
            filtered = [item for item in filtered if hasattr(item, 'category') and item.category == self.filters.category]

        if self.filters.status:
            filtered = [item for item in filtered if hasattr(item, 'status') and item.status == self.filters.status]

        # Filtro por fecha (si existe el campo de fecha)
        if self.filters.date_from or self.filters.date_to:
            from datetime import datetime
            filtered = self._apply_date_filter(filtered)

        return filtered

    def _apply_date_filter(self, data: List[Any]) -> List[Any]:
        """Aplicar filtro por fecha"""
        from datetime import datetime

        if not self.filters.date_from and not self.filters.date_to:
            return data

        filtered = []
        for item in data:
            if not hasattr(item, 'created_at'):
                continue

            item_date = item.created_at.date() if hasattr(item.created_at, 'date') else item.created_at

            if self.filters.date_from:
                start_date = datetime.strptime(self.filters.date_from, "%Y-%m-%d").date()
                if item_date < start_date:
                    continue

            if self.filters.date_to:
                end_date = datetime.strptime(self.filters.date_to, "%Y-%m-%d").date()
                if item_date > end_date:
                    continue

            filtered.append(item)

        return filtered

    def _apply_sorting(self) -> List[Any]:
        """Aplicar ordenación"""
        if not self.pagination.sort_by:
            return self.filtered_data

        reverse = self.pagination.sort_order == SortOrder.DESC

        try:
            return sorted(
                self.filtered_data,
                key=lambda x: getattr(x, self.pagination.sort_by, 0),
                reverse=reverse
            )
        except (AttributeError, TypeError):
            # Devolver los datos originales si el campo no existe o no se puede ordenar
            return self.filtered_data

    def get_page(self) -> tuple[List[Any], int]:
        """Devolver los datos de la página actual y el total"""
        total = len(self.sorted_data)
        start = (self.pagination.page - 1) * self.pagination.size
        end = start + self.pagination.size

        page_data = self.sorted_data[start:end]
        return page_data, total

    def get_metadata(self) -> Dict[str, Any]:
        """Devolver los metadatos de paginación"""
        total = len(self.sorted_data)
        pages = (total + self.pagination.size - 1) // self.pagination.size

        return {
            "page": self.pagination.page,
            "size": self.pagination.size,
            "total": total,
            "pages": pages,
            "has_next": self.pagination.page < pages,
            "has_prev": self.pagination.page > 1,
            "filters_applied": {
                "search": self.filters.search,
                "category": self.filters.category,
                "status": self.filters.status,
                "date_range": f"{self.filters.date_from} ~ {self.filters.date_to}" if self.filters.date_from or self.filters.date_to else None
            },
            "sorting": {
                "field": self.pagination.sort_by,
                "order": self.pagination.sort_order
            } if self.pagination.sort_by else None
        }
```

## Paso 6: Implementar endpoints avanzados

### Router de items (`src/api/routes/items.py`)

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from fastapi.responses import JSONResponse

from src.schemas.items import Item, ItemCreate, ItemUpdate, ItemResponse
from src.helper.pagination import pagination_params, filter_params, PaginationParams, FilterParams, AdvancedPaginator
from src.helper.exceptions import ResourceNotFoundException, DuplicateResourceException, ValidationException
from src.utils.responses import success_response, paginated_response, ResponseHelper
from src.crud.items import ItemCRUD

router = APIRouter(prefix="/items", tags=["items"])
crud = ItemCRUD()

@router.post("/", response_model=dict, status_code=201)
async def create_item(
    item_create: ItemCreate,
    background_tasks: BackgroundTasks
) -> JSONResponse:
    """
    Crear un item nuevo

    - **name**: Nombre del item (obligatorio)
    - **description**: Descripción del item (opcional)
    - **price**: Precio (obligatorio, 0 o mayor)
    - **category**: Categoría (opcional)
    """
    # Comprobar duplicados
    existing_item = await crud.get_by_name(item_create.name)
    if existing_item:
        raise DuplicateResourceException("Item", "name", item_create.name)

    # Validación de lógica de negocio
    if item_create.price < 0:
        raise ValidationException("Price must be 0 or greater", "price")

    # Crear item
    created_item = await crud.create(item_create)

    # Tarea en segundo plano (p. ej. enviar notificación, log, etc.)
    background_tasks.add_task(send_creation_notification, created_item.id)

    return ResponseHelper.created(
        data=created_item.dict(),
        message=f"Item '{created_item.name}' created successfully"
    )

@router.get("/", response_model=dict)
async def list_items(
    pagination: PaginationParams = Depends(pagination_params),
    filters: FilterParams = Depends(filter_params)
) -> JSONResponse:
    """
    Obtener la lista de items (con paginación, filtrado y ordenación)

    **Paginación:**
    - page: número de página (por defecto: 1)
    - size: tamaño de página (por defecto: 20, máximo: 100)

    **Ordenación:**
    - sort_by: campo de ordenación (name, price, created_at, etc.)
    - sort_order: orden (asc, desc)

    **Filtrado:**
    - search: término de búsqueda (busca en name o description)
    - category: filtro de categoría
    - status: filtro de estado
    - date_from: fecha inicial (YYYY-MM-DD)
    - date_to: fecha final (YYYY-MM-DD)
    """
    # Obtener todos los items
    all_items = await crud.get_all()

    # Aplicar la paginación avanzada
    paginator = AdvancedPaginator(all_items, pagination, filters)
    page_data, total = paginator.get_page()

    # Añadir metadatos extra a la respuesta
    metadata = paginator.get_metadata()

    # Construir mensaje personalizado
    message = f"Total {total} items, {len(page_data)} items retrieved"
    if filters.search:
        message += f" (Search term: '{filters.search}')"

    return paginated_response(
        data=[item.dict() for item in page_data],
        page=pagination.page,
        size=pagination.size,
        total=total,
        message=message
    )

@router.get("/search/advanced", response_model=dict)
async def advanced_search(
    q: str = Query(..., min_length=1, description="Search term"),
    fields: List[str] = Query(["name", "description"], description="Search fields"),
    exact_match: bool = Query(False, description="Exact match"),
    case_sensitive: bool = Query(False, description="Case sensitive"),
    pagination: PaginationParams = Depends(pagination_params)
) -> JSONResponse:
    """
    Funcionalidad de búsqueda avanzada

    - **q**: término de búsqueda (obligatorio)
    - **fields**: lista de campos donde buscar
    - **exact_match**: coincidencia exacta
    - **case_sensitive**: sensible a mayúsculas
    """
    results = await crud.advanced_search(
        query=q,
        fields=fields,
        exact_match=exact_match,
        case_sensitive=case_sensitive
    )

    # Aplicar paginación
    total = len(results)
    start = (pagination.page - 1) * pagination.size
    end = start + pagination.size
    page_data = results[start:end]

    return paginated_response(
        data=[item.dict() for item in page_data],
        page=pagination.page,
        size=pagination.size,
        total=total,
        message=f"'{q}' search results: {total} items"
    )

@router.get("/{item_id}", response_model=dict)
async def get_item(
    item_id: int = Path(..., gt=0, description="Item ID")
) -> JSONResponse:
    """Obtener un item concreto"""
    item = await crud.get_by_id(item_id)
    if not item:
        raise ResourceNotFoundException("Item", item_id)

    return success_response(
        data=item.dict(),
        message=f"Item '{item.name}' retrieved successfully"
    )

@router.put("/{item_id}", response_model=dict)
async def update_item(
    item_id: int = Path(..., gt=0, description="Item ID"),
    item_update: ItemUpdate
) -> JSONResponse:
    """Actualizar un item"""
    existing_item = await crud.get_by_id(item_id)
    if not existing_item:
        raise ResourceNotFoundException("Item", item_id)

    # Comprobar duplicados de nombre (frente a otros items)
    if item_update.name and item_update.name != existing_item.name:
        duplicate = await crud.get_by_name(item_update.name)
        if duplicate:
            raise DuplicateResourceException("Item", "name", item_update.name)

    updated_item = await crud.update(item_id, item_update)

    return ResponseHelper.updated(
        data=updated_item.dict(),
        message=f"Item '{updated_item.name}' updated successfully"
    )

@router.delete("/{item_id}", response_model=dict, status_code=204)
async def delete_item(
    item_id: int = Path(..., gt=0, description="Item ID"),
    force: bool = Query(False, description="Force delete")
) -> JSONResponse:
    """Eliminar un item"""
    item = await crud.get_by_id(item_id)
    if not item:
        raise ResourceNotFoundException("Item", item_id)

    # Validación previa al borrado (p. ej. existencia de pedidos relacionados)
    if not force and await crud.has_related_orders(item_id):
        raise ValidationException(
            "Related orders exist, cannot be deleted. Use force=true to force delete"
        )

    await crud.delete(item_id)

    return ResponseHelper.deleted(
        message=f"Item '{item.name}' deleted successfully"
    )

@router.post("/bulk", response_model=dict)
async def bulk_create_items(
    items: List[ItemCreate],
    skip_duplicates: bool = Query(False, description="Skip duplicates")
) -> JSONResponse:
    """Crear varios items en lote"""
    if len(items) > 100:
        raise ValidationException("Maximum 100 items can be created at once")

    created_items = []
    skipped_items = []
    errors = []

    for i, item_create in enumerate(items):
        try:
            # Comprobar duplicados
            existing = await crud.get_by_name(item_create.name)
            if existing:
                if skip_duplicates:
                    skipped_items.append({"index": i, "name": item_create.name, "reason": "Duplicate name"})
                    continue
                else:
                    errors.append({"index": i, "name": item_create.name, "error": "Duplicate name"})
                    continue

            created_item = await crud.create(item_create)
            created_items.append(created_item)

        except Exception as e:
            errors.append({"index": i, "name": item_create.name, "error": str(e)})

    result = {
        "created_count": len(created_items),
        "skipped_count": len(skipped_items),
        "error_count": len(errors),
        "created_items": [item.dict() for item in created_items],
        "skipped_items": skipped_items,
        "errors": errors
    }

    message = f"{len(created_items)} items created"
    if skipped_items:
        message += f", {len(skipped_items)} skipped"
    if errors:
        message += f", {len(errors)} errors"

    return success_response(data=result, message=message)

async def send_creation_notification(item_id: int):
    """Notificación de creación de item (tarea en segundo plano)"""
    # En la implementación real, envía notificación por email, Slack, etc.
    import asyncio
    await asyncio.sleep(1)  # Simulación
    print(f"Item {item_id} creation notification sent")
```

## Paso 7: Personalización de la documentación OpenAPI

### Personalización de OpenAPI (`src/utils/documents.py`)

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Crear el esquema OpenAPI personalizado"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Añadir información personalizada
    openapi_schema["info"].update({
        "contact": {
            "name": "API Support",
            "url": "https://example.com/support",
            "email": "support@example.com"
        },
        "license": {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        },
        "termsOfService": "https://example.com/terms"
    })

    # Añadir información de servidores
    openapi_schema["servers"] = [
        {
            "url": "https://api.example.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.example.com",
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]

    # Añadir esquemas comunes de respuesta
    openapi_schema["components"]["schemas"].update({
        "SuccessResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": True},
                "status": {"type": "string", "example": "success"},
                "data": {"type": "object"},
                "message": {"type": "string", "example": "Request processed successfully"},
                "timestamp": {"type": "string", "format": "date-time"},
                "request_id": {"type": "string", "example": "123e4567-e89b-12d3-a456-426614174000"}
            }
        },
        "ErrorResponse": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "example": False},
                "status": {"type": "string", "example": "error"},
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "example": "RESOURCE_NOT_FOUND"},
                        "message": {"type": "string", "example": "Resource not found"},
                        "details": {"type": "object"}
                    }
                },
                "timestamp": {"type": "string", "format": "date-time"},
                "request_id": {"type": "string", "example": "123e4567-e89b-12d3-a456-426614174000"}
            }
        }
    })

    # Añadir agrupación y descripción de tags
    openapi_schema["tags"] = [
        {
            "name": "items",
            "description": "Item management API",
            "externalDocs": {
                "description": "More information",
                "url": "https://example.com/docs/items"
            }
        },
        {
            "name": "health",
            "description": "System status check API"
        }
    ]

    # Añadir esquema de seguridad
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

def setup_docs(app: FastAPI):
    """Configurar la documentación"""
    app.openapi = lambda: custom_openapi(app)

    # Configuración de Swagger UI
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"

    # Endpoint adicional de documentación
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_endpoint():
        return custom_openapi(app)
```

### Aplicar a la app principal (`src/main.py` adicional)

```python
from src.utils.documents import setup_docs
from src.api.routes import items

# Incluir router
app.include_router(items.router, prefix="/api/v1")

# Aplicar configuración de la documentación
setup_docs(app)

# Añadir middleware de request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = generate_request_id()
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response
```

## Paso 8: Implementar sistema de caché

### Caché de respuestas (`src/utils/cache.py`)

```python
from typing import Optional, Any, Dict
from functools import wraps
import asyncio
import json
import hashlib
from datetime import datetime, timedelta

class MemoryCache:
    """Caché en memoria"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Obtener un valor de la caché"""
        if key not in self._cache:
            return None

        item = self._cache[key]
        if datetime.utcnow() > item["expires_at"]:
            del self._cache[key]
            return None

        return item["value"]

    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Guardar un valor en la caché"""
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds),
            "created_at": datetime.utcnow()
        }

    async def delete(self, key: str):
        """Eliminar un valor de la caché"""
        self._cache.pop(key, None)

    async def clear(self):
        """Eliminar toda la caché"""
        self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Estadísticas de la caché"""
        now = datetime.utcnow()
        valid_items = [
            item for item in self._cache.values()
            if now <= item["expires_at"]
        ]

        return {
            "total_items": len(self._cache),
            "valid_items": len(valid_items),
            "expired_items": len(self._cache) - len(valid_items),
            "memory_usage_mb": len(str(self._cache)) / 1024 / 1024
        }

# instancia global de la caché
cache = MemoryCache()

def cache_response(ttl_seconds: int = 300, key_prefix: str = ""):
    """Decorador de caché de respuestas"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar la clave de caché
            cache_key = generate_cache_key(func.__name__, args, kwargs, key_prefix)

            # Obtener desde caché
            cached_response = await cache.get(cache_key)
            if cached_response:
                return cached_response

            # Ejecutar la función
            response = await func(*args, **kwargs)

            # Cachear la respuesta
            await cache.set(cache_key, response, ttl_seconds)

            return response
        return wrapper
    return decorator

def generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generar la clave de caché"""
    # Generar clave única basada en el nombre de la función y los argumentos
    key_data = {
        "function": func_name,
        "args": str(args),
        "kwargs": sorted(kwargs.items())
    }

    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{prefix}:{func_name}:{key_hash}" if prefix else f"{func_name}:{key_hash}"

# Endpoint de gestión de caché
@app.get("/admin/cache/stats")
async def get_cache_stats():
    """Estadísticas de la caché"""
    stats = cache.get_stats()
    return success_response(data=stats, message="Cache statistics retrieved")

@app.delete("/admin/cache/clear")
async def clear_cache():
    """Limpiar toda la caché"""
    await cache.clear()
    return success_response(message="Cache deleted successfully")
```

### Ejemplo de uso de caché

```python
# Aplicar caché en src/api/routes/items.py

from src.utils.cache import cache_response

@router.get("/", response_model=dict)
@cache_response(ttl_seconds=60, key_prefix="items_list")  # caché de 1 minuto
async def list_items(
    pagination: PaginationParams = Depends(pagination_params),
    filters: FilterParams = Depends(filter_params)
) -> JSONResponse:
    # ... código existente ...

@router.get("/{item_id}", response_model=dict)
@cache_response(ttl_seconds=300, key_prefix="item_detail")  # caché de 5 minutos
async def get_item(item_id: int = Path(..., gt=0)) -> JSONResponse:
    # ... código existente ...
```

## Paso 9: Probar la API

### Ejecutar el servidor y prueba básica

<div class="termy">

```console
$ cd advanced-api-server
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

# Probar el formato de respuesta personalizado
$ curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Advanced notebook",
    "description": "Notebook with latest technology",
    "price": 2500000,
    "category": "electronics"
  }'

{
  "success": true,
  "status": "success",
  "data": {
    "id": 1,
    "name": "Advanced notebook",
    "description": "Notebook with latest technology",
    "price": 2500000,
    "category": "electronics",
    "created_at": "2024-01-01T12:00:00Z"
  },
  "message": "Item 'Advanced notebook' created successfully",
  "timestamp": "2024-01-01T12:00:00.123456Z",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}

# Probar paginación y filtrado
$ curl "http://localhost:8000/api/v1/items/?page=1&size=10&search=notebook&sort_by=price&sort_order=desc"

# Probar la búsqueda avanzada
$ curl "http://localhost:8000/api/v1/items/search/advanced?q=notebook&fields=name&fields=description&exact_match=false"

# Probar la respuesta de error
$ curl "http://localhost:8000/api/v1/items/999"

{
  "success": false,
  "status": "error",
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Item (ID: 999) not found",
    "details": {
      "resource": "Item",
      "id": 999
    }
  },
  "timestamp": "2024-01-01T12:00:00.123456Z",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

</div>

### Revisar la documentación OpenAPI

Entra en http://localhost:8000/docs en tu navegador para ver la documentación personalizada de la API.

## Próximos pasos

¡Has terminado el sistema de manejo personalizado de respuestas! Próximos pasos:

1. **[Integración con MCP](mcp-integration.md)** - Implementar el Model Context Protocol
<!-- 2. **[Building Authentication Systems](authentication-system.md)** - JWT-based authentication/authorization -->
<!-- 3. **[Building Real-time APIs](realtime-api.md)** - WebSocket and Server-Sent Events -->
<!-- 4. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->

## Resumen

En este tutorial hemos implementado un sistema avanzado de manejo de respuestas:

- ✅ Diseñar formatos de respuesta estandarizados
- ✅ Manejo global de excepciones y respuestas de error personalizadas
- ✅ Sistemas avanzados de paginación y filtrado
- ✅ Personalización de la documentación OpenAPI
- ✅ Caché de respuestas y optimización del rendimiento
- ✅ Sistema de seguimiento de peticiones (request ID)
- ✅ Procesamiento en segundo plano
- ✅ APIs de operaciones en lote

¡Ahora puedes implementar todas las funcionalidades clave de un servidor API de nivel empresa!

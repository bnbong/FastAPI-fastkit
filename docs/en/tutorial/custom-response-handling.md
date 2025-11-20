# Custom Response Handling and Advanced API Design

Learn how to implement consistent response formats, error handling, pagination, and custom OpenAPI documentation using FastAPI's advanced features. We'll implement enterprise-grade API design patterns using the `fastapi-custom-response` template.

## What You'll Learn in This Tutorial

- Designing standardized API response formats
- Global exception handling and custom error responses
- Implementing pagination systems
- Filtering and sorting functionality
- Customizing OpenAPI documentation
- API version management
- Response caching and optimization

## Prerequisites

- Completed the [Docker Containerization Tutorial](docker-deployment.md)
- Understanding of REST API design principles
- Knowledge of HTTP status codes
- Basic concepts of OpenAPI/Swagger

## The Importance of Standardized API Responses

### Inconsistent vs Standardized Responses

**Problematic response format:**
```json
// Success
{"id": 1, "name": "item"}

// Error
{"detail": "Not found"}

// List retrieval
[{"id": 1}, {"id": 2}]
```

**Standardized response format:**
```json
// Success
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

## Step 1: Creating a Custom Response Project

Create a project using the `fastapi-custom-response` template:

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

## Step 2: Analyzing Project Structure

Let's examine the advanced features of the generated project:

```
advanced-api-server/
├── src/
│   ├── main.py                     # FastAPI application
│   ├── schemas/
│   │   ├── base.py                 # Base response schemas
│   │   ├── items.py                # Item schemas
│   │   └── responses.py            # Response format definitions
│   ├── helper/
│   │   ├── exceptions.py           # Custom exception classes
│   │   └── pagination.py           # Pagination helpers
│   ├── utils/
│   │   ├── responses.py            # Response utilities
│   │   └── documents.py            # OpenAPI documentation customization
│   ├── api/
│   │   └── routes/
│   │       └── items.py            # Advanced API endpoints
│   ├── crud/
│   │   └── items.py                # CRUD logic
│   └── core/
│       └── config.py               # Configuration
└── tests/
    └── test_responses.py           # Response format tests
```

## Step 3: Implementing Standardized Response Schemas

### Base Response Schema (`src/schemas/base.py`)

```python
from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """Response status"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ErrorDetail(BaseModel):
    """Error detail information"""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field where error occurred")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error information")

class BaseResponse(BaseModel, Generic[T]):
    """Base response format"""
    success: bool = Field(..., description="Request success status")
    status: ResponseStatus = Field(..., description="Response status")
    data: Optional[T] = Field(None, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

class ErrorResponse(BaseModel):
    """Error response format"""
    success: bool = Field(False, description="Request success status")
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="Response status")
    error: ErrorDetail = Field(..., description="Error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., ge=1, description="Current page")
    size: int = Field(..., ge=1, le=100, description="Page size")
    total: int = Field(..., ge=0, description="Total number of items")
    pages: int = Field(..., ge=0, description="Total number of pages")
    has_next: bool = Field(..., description="Whether next page exists")
    has_prev: bool = Field(..., description="Whether previous page exists")

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response"""
    success: bool = Field(True, description="Request success status")
    status: ResponseStatus = Field(ResponseStatus.SUCCESS, description="Response status")
    data: List[T] = Field(..., description="Data list")
    meta: PaginationMeta = Field(..., description="Pagination information")
    message: Optional[str] = Field(None, description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response time")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str = Field(..., description="Validation failed field")
    message: str = Field(..., description="Error message")
    invalid_value: Any = Field(..., description="Invalid value")

class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = Field(False, description="Request success status")
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="Response status")
    error: ErrorDetail = Field(..., description="Error information")
    validation_errors: List[ValidationErrorDetail] = Field(..., description="Validation error list")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response time")
    request_id: Optional[str] = Field(None, description="Request tracking ID")
```

### Response utility functions (`src/utils/responses.py`)

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
    """Generate request tracking ID"""
    return str(uuid.uuid4())

def success_response(
    data: Any = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """Generate success response"""
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
    """Generate error response"""
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
    """Generate paginated response"""
    pages = (total + size - 1) // size  # round up calculation
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
    """Response helper class"""

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

## Step 4: Custom exception handling system

### Custom exception class (`src/helper/exceptions.py`)

```python
from typing import Optional, Dict, Any
from fastapi import HTTPException

class BaseAPIException(HTTPException):
    """Base API exception class"""

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
    """Validation exception"""

    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=422,
            details=details or {"field": field} if field else None
        )

class ResourceNotFoundException(BaseAPIException):
    """Resource not found exception"""

    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource}(ID: {resource_id}) not found",
            status_code=404,
            details={"resource": resource, "id": resource_id}
        )

class DuplicateResourceException(BaseAPIException):
    """Duplicate resource exception"""

    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            error_code="DUPLICATE_RESOURCE",
            message=f"{resource} {field} '{value}' already exists",
            status_code=409,
            details={"resource": resource, "field": field, "value": value}
        )

class BusinessLogicException(BaseAPIException):
    """Business logic exception"""

    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(
            error_code=error_code,
            message=message,
            status_code=422
        )

class RateLimitException(BaseAPIException):
    """Request limit exception"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            error_code="RATE_LIMIT_EXCEEDED",
            message="Request limit exceeded. Please try again later",
            status_code=429,
            details={"retry_after": retry_after}
        )

class AuthenticationException(BaseAPIException):
    """Authentication exception"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            error_code="AUTHENTICATION_REQUIRED",
            message=message,
            status_code=401
        )

class AuthorizationException(BaseAPIException):
    """Authorization exception"""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            error_code="INSUFFICIENT_PERMISSIONS",
            message=message,
            status_code=403
        )
```

### Global exception handler (`src/main.py`)

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
    """Custom API exception handler"""
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
    """Pydantic validation exception handler"""
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
    """HTTP exception handler"""
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
    """General exception handler"""
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

## Step 5: Advanced pagination system

### Pagination helper (`src/helper/pagination.py`)

```python
from typing import List, Optional, Any, Dict, Callable
from pydantic import BaseModel, Field
from fastapi import Query
from enum import Enum

class SortOrder(str, Enum):
    """Sort order"""
    ASC = "asc"
    DESC = "desc"

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: SortOrder = Field(SortOrder.ASC, description="Sort order")

class FilterParams(BaseModel):
    """Filtering parameters"""
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
    """Pagination parameters dependency"""
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
    """Filtering parameters dependency"""
    return FilterParams(
        search=search,
        category=category,
        status=status,
        date_from=date_from,
        date_to=date_to
    )

class AdvancedPaginator:
    """Advanced pagination class"""

    def __init__(self, data: List[Any], pagination: PaginationParams, filters: FilterParams):
        self.data = data
        self.pagination = pagination
        self.filters = filters
        self.filtered_data = self._apply_filters()
        self.sorted_data = self._apply_sorting()

    def _apply_filters(self) -> List[Any]:
        """Apply filters"""
        filtered = self.data

        if self.filters.search:
            # Filter by search term (example: search in name or description fields)
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

        # Implement date filtering (if date field exists)
        if self.filters.date_from or self.filters.date_to:
            from datetime import datetime
            filtered = self._apply_date_filter(filtered)

        return filtered

    def _apply_date_filter(self, data: List[Any]) -> List[Any]:
        """Apply date filter"""
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
        """Apply sorting"""
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
            # Return original data if sort field is not found or cannot be sorted
            return self.filtered_data

    def get_page(self) -> tuple[List[Any], int]:
        """Return current page data and total count"""
        total = len(self.sorted_data)
        start = (self.pagination.page - 1) * self.pagination.size
        end = start + self.pagination.size

        page_data = self.sorted_data[start:end]
        return page_data, total

    def get_metadata(self) -> Dict[str, Any]:
        """Return pagination metadata"""
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

## Step 6: Implementing advanced API endpoints

### Item API router (`src/api/routes/items.py`)

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
    Create a new item

    - **name**: Item name (required)
    - **description**: Item description (optional)
    - **price**: Price (required, 0 or greater)
    - **category**: Category (optional)
    """
    # Check for duplicates
    existing_item = await crud.get_by_name(item_create.name)
    if existing_item:
        raise DuplicateResourceException("Item", "name", item_create.name)

    # Business logic validation
    if item_create.price < 0:
        raise ValidationException("Price must be 0 or greater", "price")

    # Create item
    created_item = await crud.create(item_create)

    # Background tasks (e.g. sending notifications, logging, etc.)
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
    Get item list (pagination, filtering, sorting supported)

    **Pagination:**
    - page: Page number (default: 1)
    - size: Page size (default: 20, maximum: 100)

    **Sorting:**
    - sort_by: Sort field (name, price, created_at, etc.)
    - sort_order: Sort order (asc, desc)

    **Filtering:**
    - search: Search term (search in name or description fields)
    - category: Category filter
    - status: Status filter
    - date_from: Start date (YYYY-MM-DD)
    - date_to: End date (YYYY-MM-DD)
    """
    # Get all items
    all_items = await crud.get_all()

    # Apply advanced pagination
    paginator = AdvancedPaginator(all_items, pagination, filters)
    page_data, total = paginator.get_page()

    # Include additional metadata in response
    metadata = paginator.get_metadata()

    # Create custom message
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
    Advanced search functionality

    - **q**: Search term (required)
    - **fields**: Search fields list
    - **exact_match**: Exact match
    - **case_sensitive**: Case sensitive
    """
    results = await crud.advanced_search(
        query=q,
        fields=fields,
        exact_match=exact_match,
        case_sensitive=case_sensitive
    )

    # Apply pagination
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
    """Get specific item"""
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
    """Update item"""
    existing_item = await crud.get_by_id(item_id)
    if not existing_item:
        raise ResourceNotFoundException("Item", item_id)

    # Check for duplicate name (with other items)
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
    """Delete item"""
    item = await crud.get_by_id(item_id)
    if not item:
        raise ResourceNotFoundException("Item", item_id)

    # Validation before deletion (e.g. related orders)
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
    """Bulk create items"""
    if len(items) > 100:
        raise ValidationException("Maximum 100 items can be created at once")

    created_items = []
    skipped_items = []
    errors = []

    for i, item_create in enumerate(items):
        try:
            # Check for duplicates
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
    """Item creation notification (background task)"""
    # In actual implementation, send notification via email, Slack, etc.
    import asyncio
    await asyncio.sleep(1)  # Simulation
    print(f"Item {item_id} creation notification sent")
```

## Step 7: OpenAPI documentation customization

### OpenAPI documentation customization (`src/utils/documents.py`)

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """Create custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add custom information
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

    # Add server information
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

    # Add common response schema
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

    # Add tag grouping and description
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

    # Add security schema
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
    """Setup documentation"""
    app.openapi = lambda: custom_openapi(app)

    # Swagger UI setup
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"

    # Additional document endpoint
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_endpoint():
        return custom_openapi(app)
```

### Apply to main application (`src/main.py` addition)

```python
from src.utils.documents import setup_docs
from src.api.routes import items

# Include router
app.include_router(items.router, prefix="/api/v1")

# Apply documentation setup
setup_docs(app)

# Add request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = generate_request_id()
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response
```

## Step 8: Implementing caching system

### Response caching (`src/utils/cache.py`)

```python
from typing import Optional, Any, Dict
from functools import wraps
import asyncio
import json
import hashlib
from datetime import datetime, timedelta

class MemoryCache:
    """Memory-based cache"""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None

        item = self._cache[key]
        if datetime.utcnow() > item["expires_at"]:
            del self._cache[key]
            return None

        return item["value"]

    async def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Save value to cache"""
        self._cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds),
            "created_at": datetime.utcnow()
        }

    async def delete(self, key: str):
        """Delete value from cache"""
        self._cache.pop(key, None)

    async def clear(self):
        """Delete all cache"""
        self._cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Cache statistics"""
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

# Global cache instance
cache = MemoryCache()

def cache_response(ttl_seconds: int = 300, key_prefix: str = ""):
    """Response caching decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(func.__name__, args, kwargs, key_prefix)

            # Get from cache
            cached_response = await cache.get(cache_key)
            if cached_response:
                return cached_response

            # Execute function
            response = await func(*args, **kwargs)

            # Cache response
            await cache.set(cache_key, response, ttl_seconds)

            return response
        return wrapper
    return decorator

def generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generate cache key"""
    # Generate unique key based on function name and arguments
    key_data = {
        "function": func_name,
        "args": str(args),
        "kwargs": sorted(kwargs.items())
    }

    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{prefix}:{func_name}:{key_hash}" if prefix else f"{func_name}:{key_hash}"

# Cache management endpoint
@app.get("/admin/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    stats = cache.get_stats()
    return success_response(data=stats, message="Cache statistics retrieved")

@app.delete("/admin/cache/clear")
async def clear_cache():
    """Delete all cache"""
    await cache.clear()
    return success_response(message="Cache deleted successfully")
```

### Caching example

```python
# Apply caching to src/api/routes/items.py

from src.utils.cache import cache_response

@router.get("/", response_model=dict)
@cache_response(ttl_seconds=60, key_prefix="items_list")  # 1 minute caching
async def list_items(
    pagination: PaginationParams = Depends(pagination_params),
    filters: FilterParams = Depends(filter_params)
) -> JSONResponse:
    # ... existing code ...

@router.get("/{item_id}", response_model=dict)
@cache_response(ttl_seconds=300, key_prefix="item_detail")  # 5 minute caching
async def get_item(item_id: int = Path(..., gt=0)) -> JSONResponse:
    # ... existing code ...
```

## Step 9: API test

### Run server and basic test

<div class="termy">

```console
$ cd advanced-api-server
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

# Custom response format test
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

# Pagination and filtering test
$ curl "http://localhost:8000/api/v1/items/?page=1&size=10&search=notebook&sort_by=price&sort_order=desc"

# Advanced search test
$ curl "http://localhost:8000/api/v1/items/search/advanced?q=notebook&fields=name&fields=description&exact_match=false"

# Error response test
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

### OpenAPI document check

Browse to http://localhost:8000/docs to view the customized API document.

## Next Steps

You've completed the custom response handling system! Next things to try:

1. **[MCP Integration](mcp-integration.md)** - Implementing Model Context Protocol
<!-- 2. **[Building Authentication Systems](authentication-system.md)** - JWT-based authentication/authorization -->
<!-- 3. **[Building Real-time APIs](realtime-api.md)** - WebSocket and Server-Sent Events -->
<!-- 4. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->

## Summary

In this tutorial, we implemented an advanced response handling system:

- ✅ Designed standardized API response formats
- ✅ Global exception handling and custom error responses
- ✅ Advanced pagination and filtering systems
- ✅ OpenAPI documentation customization
- ✅ Response caching and performance optimization
- ✅ Request tracking system
- ✅ Background task processing
- ✅ Batch operation APIs

Now you can implement all the core features of enterprise-grade API servers!

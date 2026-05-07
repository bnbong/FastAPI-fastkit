# 커스텀 응답 처리와 고급 API 설계

FastAPI의 고급 기능을 활용해 일관된 응답 형식, 에러 처리, 페이지네이션, 그리고 OpenAPI 문서 맞춤 구성을 구현하는 방법을 배웁니다. `fastapi-custom-response` 템플릿으로 엔터프라이즈급 API 설계 패턴을 구현합니다.

## 이 튜토리얼에서 배우는 내용

- 표준화된 API 응답 형식 설계
- 전역 예외 처리와 커스텀 에러 응답
- 페이지네이션 시스템 구현
- 필터링과 정렬 기능
- OpenAPI 문서 커스터마이즈
- API 버전 관리
- 응답 캐싱과 최적화

## 사전 요구 사항

- [Docker 컨테이너화 튜토리얼](docker-deployment.md) 완료
- REST API 설계 원칙에 대한 이해
- HTTP 상태 코드 지식
- OpenAPI / Swagger의 기본 개념

## 표준화된 API 응답이 중요한 이유

### 일관성 없는 응답 vs 표준화된 응답

**문제가 있는 응답 형식:**
```json
// 성공
{"id": 1, "name": "item"}

// 에러
{"detail": "Not found"}

// 목록 조회
[{"id": 1}, {"id": 2}]
```

**표준화된 응답 형식:**
```json
// 성공
{
  "success": true,
  "data": {"id": 1, "name": "item"},
  "message": "Item retrieved successfully",
  "timestamp": "2024-01-01T12:00:00Z"
}

// 에러
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

## 1단계: 커스텀 응답 프로젝트 생성

`fastapi-custom-response` 템플릿으로 프로젝트를 만듭니다:

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

## 2단계: 프로젝트 구조 분석

생성된 프로젝트의 고급 기능을 살펴봅시다:

```
advanced-api-server/
├── src/
│   ├── main.py                     # FastAPI 애플리케이션
│   ├── schemas/
│   │   ├── base.py                 # 기본 응답 스키마
│   │   ├── items.py                # Item 스키마
│   │   └── responses.py            # 응답 형식 정의
│   ├── helper/
│   │   ├── exceptions.py           # 커스텀 예외 클래스
│   │   └── pagination.py           # 페이지네이션 헬퍼
│   ├── utils/
│   │   ├── responses.py            # 응답 유틸리티
│   │   └── documents.py            # OpenAPI 문서 커스터마이즈
│   ├── api/
│   │   └── routes/
│   │       └── items.py            # 고급 API 엔드포인트
│   ├── crud/
│   │   └── items.py                # CRUD 로직
│   └── core/
│       └── config.py               # 설정
└── tests/
    └── test_responses.py           # 응답 형식 테스트
```

## 3단계: 표준화된 응답 스키마 구현

### 기본 응답 스키마 (`src/schemas/base.py`)

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

### 응답 유틸리티 함수 (`src/utils/responses.py`)

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
    pages = (total + size - 1) // size  # 올림 계산
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

## 4단계: 커스텀 예외 처리 시스템

### 커스텀 예외 클래스 (`src/helper/exceptions.py`)

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

### 전역 예외 핸들러 (`src/main.py`)

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

## 5단계: 고급 페이지네이션 시스템

### 페이지네이션 헬퍼 (`src/helper/pagination.py`)

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
            # 검색어 필터 (예: name 또는 description 필드 검색)
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

        # 날짜 필터링 구현 (날짜 필드가 있을 때)
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
            # 정렬 필드를 찾지 못하거나 정렬할 수 없으면 원본 반환
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

## 6단계: 고급 API 엔드포인트 구현

### Item API 라우터 (`src/api/routes/items.py`)

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
    새 item 생성

    - **name**: item 이름 (필수)
    - **description**: item 설명 (선택)
    - **price**: 가격 (필수, 0 이상)
    - **category**: 카테고리 (선택)
    """
    # 중복 확인
    existing_item = await crud.get_by_name(item_create.name)
    if existing_item:
        raise DuplicateResourceException("Item", "name", item_create.name)

    # 비즈니스 로직 검증
    if item_create.price < 0:
        raise ValidationException("Price must be 0 or greater", "price")

    # item 생성
    created_item = await crud.create(item_create)

    # 백그라운드 작업 (예: 알림 발송, 로깅 등)
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
    item 목록 조회 (페이지네이션, 필터링, 정렬 지원)

    **페이지네이션:**
    - page: 페이지 번호 (기본값: 1)
    - size: 페이지 크기 (기본값: 20, 최대: 100)

    **정렬:**
    - sort_by: 정렬 필드 (name, price, created_at 등)
    - sort_order: 정렬 순서 (asc, desc)

    **필터링:**
    - search: 검색어 (name 또는 description 필드 검색)
    - category: 카테고리 필터
    - status: 상태 필터
    - date_from: 시작 날짜 (YYYY-MM-DD)
    - date_to: 종료 날짜 (YYYY-MM-DD)
    """
    # 모든 item 조회
    all_items = await crud.get_all()

    # 고급 페이지네이션 적용
    paginator = AdvancedPaginator(all_items, pagination, filters)
    page_data, total = paginator.get_page()

    # 응답에 추가 메타데이터 포함
    metadata = paginator.get_metadata()

    # 커스텀 메시지 작성
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
    고급 검색 기능

    - **q**: 검색어 (필수)
    - **fields**: 검색 대상 필드 목록
    - **exact_match**: 정확 일치
    - **case_sensitive**: 대소문자 구분
    """
    results = await crud.advanced_search(
        query=q,
        fields=fields,
        exact_match=exact_match,
        case_sensitive=case_sensitive
    )

    # 페이지네이션 적용
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

    # 다른 item 들과 이름 중복 확인
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

    # 삭제 전 검증 (예: 관련 주문 존재 여부)
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
            # 중복 확인
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
    # 실제 구현에서는 이메일, Slack 등으로 알림 발송
    import asyncio
    await asyncio.sleep(1)  # 시뮬레이션
    print(f"Item {item_id} creation notification sent")
```

## 7단계: OpenAPI 문서 커스터마이즈

### OpenAPI 문서 커스터마이즈 (`src/utils/documents.py`)

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

    # 커스텀 정보 추가
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

    # 서버 정보 추가
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

    # 공통 응답 스키마 추가
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

    # 태그 그룹과 설명 추가
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

    # 보안 스키마 추가
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

    # Swagger UI 설정
    app.docs_url = "/docs"
    app.redoc_url = "/redoc"

    # 추가 문서 엔드포인트
    @app.get("/openapi.json", include_in_schema=False)
    async def get_openapi_endpoint():
        return custom_openapi(app)
```

### 메인 애플리케이션에 적용 (`src/main.py` 추가)

```python
from src.utils.documents import setup_docs
from src.api.routes import items

# 라우터 포함
app.include_router(items.router, prefix="/api/v1")

# 문서화 설정 적용
setup_docs(app)

# 요청 ID 미들웨어 추가
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = generate_request_id()
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    return response
```

## 8단계: 캐싱 시스템 구현

### 응답 캐싱 (`src/utils/cache.py`)

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

# 전역 캐시 인스턴스
cache = MemoryCache()

def cache_response(ttl_seconds: int = 300, key_prefix: str = ""):
    """Response caching decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = generate_cache_key(func.__name__, args, kwargs, key_prefix)

            # 캐시에서 가져오기
            cached_response = await cache.get(cache_key)
            if cached_response:
                return cached_response

            # 함수 실행
            response = await func(*args, **kwargs)

            # 응답 캐시
            await cache.set(cache_key, response, ttl_seconds)

            return response
        return wrapper
    return decorator

def generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str = "") -> str:
    """Generate cache key"""
    # 함수 이름과 인자를 기반으로 고유 키 생성
    key_data = {
        "function": func_name,
        "args": str(args),
        "kwargs": sorted(kwargs.items())
    }

    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()

    return f"{prefix}:{func_name}:{key_hash}" if prefix else f"{func_name}:{key_hash}"

# 캐시 관리 엔드포인트
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

### 캐싱 예시

```python
# src/api/routes/items.py 에 캐싱 적용

from src.utils.cache import cache_response

@router.get("/", response_model=dict)
@cache_response(ttl_seconds=60, key_prefix="items_list")  # 1분 캐싱
async def list_items(
    pagination: PaginationParams = Depends(pagination_params),
    filters: FilterParams = Depends(filter_params)
) -> JSONResponse:
    # ... 기존 코드 ...

@router.get("/{item_id}", response_model=dict)
@cache_response(ttl_seconds=300, key_prefix="item_detail")  # 5분 캐싱
async def get_item(item_id: int = Path(..., gt=0)) -> JSONResponse:
    # ... 기존 코드 ...
```

## 9단계: API 테스트

### 서버 실행과 기본 테스트

<div class="termy">

```console
$ cd advanced-api-server
$ fastkit runserver
Starting FastAPI server at 127.0.0.1:8000...

# 커스텀 응답 형식 테스트
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

# 페이지네이션과 필터링 테스트
$ curl "http://localhost:8000/api/v1/items/?page=1&size=10&search=notebook&sort_by=price&sort_order=desc"

# 고급 검색 테스트
$ curl "http://localhost:8000/api/v1/items/search/advanced?q=notebook&fields=name&fields=description&exact_match=false"

# 에러 응답 테스트
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

### OpenAPI 문서 확인

브라우저에서 http://localhost:8000/docs 로 이동해 맞춤 구성된 API 문서를 확인하세요.

## 다음 단계

커스텀 응답 처리 시스템을 마쳤습니다! 다음으로 시도해 볼 만한 것들:

1. **[MCP 통합](mcp-integration.md)** — Model Context Protocol 구현
<!-- 2. **[Building Authentication Systems](authentication-system.md)** - JWT-based authentication/authorization -->
<!-- 3. **[Building Real-time APIs](realtime-api.md)** - WebSocket and Server-Sent Events -->
<!-- 4. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->

## 요약

이 튜토리얼에서는 고급 응답 처리 시스템을 다음과 같이 구현했습니다:

- ✅ 표준화된 API 응답 형식 설계
- ✅ 전역 예외 처리와 커스텀 에러 응답
- ✅ 고급 페이지네이션과 필터링 시스템
- ✅ OpenAPI 문서 커스터마이즈
- ✅ 응답 캐싱과 성능 최적화
- ✅ 요청 추적 시스템
- ✅ 백그라운드 작업 처리
- ✅ 배치 작업 API

이제 엔터프라이즈급 API 서버의 핵심 기능을 스스로 구현할 수 있습니다!

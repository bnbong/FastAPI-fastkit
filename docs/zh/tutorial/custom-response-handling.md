# 自定义响应处理与进阶 API 设计

学习如何利用 FastAPI 的进阶特性,实现一致的响应格式、错误处理、分页与自定义 OpenAPI 文档。本节我们将通过 `fastapi-custom-response` 模板实现企业级 API 设计模式。

## 您将学到的内容

- 设计标准化的 API 响应格式
- 全局异常处理与自定义错误响应
- 实现分页系统
- 过滤与排序功能
- 自定义 OpenAPI 文档
- API 版本管理
- 响应缓存与优化

## 前置条件

- 完成 [Docker 容器化教程](docker-deployment.md)
- 理解 REST API 设计原则
- 熟悉 HTTP 状态码
- 对 OpenAPI / Swagger 有基础认识

## 标准化 API 响应的重要性

### 不一致 vs 标准化的响应

**有问题的响应格式:**
```json
// Success
{"id": 1, "name": "item"}

// Error
{"detail": "Not found"}

// List retrieval
[{"id": 1}, {"id": 2}]
```

**标准化的响应格式:**
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

## 第 1 步:创建自定义响应项目

使用 `fastapi-custom-response` 模板创建项目:

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

## 第 2 步:分析项目结构

让我们看看生成项目中的进阶特性:

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
│   │   ├── responses.py            # 响应工具
│   │   └── documents.py            # OpenAPI 文档定制
│   ├── api/
│   │   └── routes/
│   │       └── items.py            # 进阶 API 端点
│   ├── crud/
│   │   └── items.py                # CRUD 逻辑
│   └── core/
│       └── config.py               # 配置
└── tests/
    └── test_responses.py           # 响应格式测试
```

## 第 3 步:实现标准化的响应模式

### 基础响应模式(`src/schemas/base.py`)

```python
from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class ResponseStatus(str, Enum):
    """响应状态"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"

class ErrorDetail(BaseModel):
    """错误详情信息"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误信息")
    field: Optional[str] = Field(None, description="发生错误的字段")
    details: Optional[Dict[str, Any]] = Field(None, description="附加错误信息")

class BaseResponse(BaseModel, Generic[T]):
    """基础响应格式"""
    success: bool = Field(..., description="请求是否成功")
    status: ResponseStatus = Field(..., description="响应状态")
    data: Optional[T] = Field(None, description="响应数据")
    message: Optional[str] = Field(None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求追踪 ID")

class ErrorResponse(BaseModel):
    """错误响应格式"""
    success: bool = Field(False, description="请求是否成功")
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="响应状态")
    error: ErrorDetail = Field(..., description="错误信息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求追踪 ID")

class PaginationMeta(BaseModel):
    """分页元数据"""
    page: int = Field(..., ge=1, description="当前页码")
    size: int = Field(..., ge=1, le=100, description="每页条数")
    total: int = Field(..., ge=0, description="总条目数")
    pages: int = Field(..., ge=0, description="总页数")
    has_next: bool = Field(..., description="是否存在下一页")
    has_prev: bool = Field(..., description="是否存在上一页")

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    success: bool = Field(True, description="请求是否成功")
    status: ResponseStatus = Field(ResponseStatus.SUCCESS, description="响应状态")
    data: List[T] = Field(..., description="数据列表")
    meta: PaginationMeta = Field(..., description="分页信息")
    message: Optional[str] = Field(None, description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    request_id: Optional[str] = Field(None, description="请求追踪 ID")

class ValidationErrorDetail(BaseModel):
    """校验错误详情"""
    field: str = Field(..., description="校验失败的字段")
    message: str = Field(..., description="错误信息")
    invalid_value: Any = Field(..., description="无效值")

class ValidationErrorResponse(BaseModel):
    """校验错误响应格式"""
    success: bool = Field(False, description="请求是否成功")
    status: ResponseStatus = Field(ResponseStatus.ERROR, description="响应状态")
    error: ErrorDetail = Field(..., description="错误信息")
    validation_errors: List[ValidationErrorDetail] = Field(..., description="校验错误列表")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    request_id: Optional[str] = Field(None, description="请求追踪 ID")
```

### 响应工具函数(`src/utils/responses.py`)

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
    """生成请求追踪 ID"""
    return str(uuid.uuid4())

def success_response(
    data: Any = None,
    message: Optional[str] = None,
    request_id: Optional[str] = None,
    status_code: int = 200
) -> JSONResponse:
    """生成成功响应"""
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
    """生成错误响应"""
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

## 第 4 步:自定义异常处理体系

### 自定义异常类(`src/helper/exceptions.py`)

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

### 全局异常处理器(`src/main.py`)

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
    """Pydantic 校验异常处理器"""
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

## 第 5 步:进阶分页系统

### 分页助手(`src/helper/pagination.py`)

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

## 第 6 步:实现进阶 API 端点

### Item API 路由(`src/api/routes/items.py`)

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
    创建新条目

    - **name**：条目名称（必填）
    - **description**：条目描述（可选）
    - **price**：价格（必填，且不小于 0）
    - **category**：分类（可选）
    """
    # 检查是否存在重复条目
    existing_item = await crud.get_by_name(item_create.name)
    if existing_item:
        raise DuplicateResourceException("Item", "name", item_create.name)

    # 业务逻辑校验
    if item_create.price < 0:
        raise ValidationException("Price must be 0 or greater", "price")

    # 创建条目
    created_item = await crud.create(item_create)

    # 后台任务（如发送通知、记录日志等）
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
    获取条目列表（支持分页、筛选与排序）

    **分页：**
    - page：页码（默认：1）
    - size：每页数量（默认：20，最大：100）

    **排序：**
    - sort_by：排序字段（name、price、created_at 等）
    - sort_order：排序顺序（asc、desc）

    **筛选：**
    - search：搜索关键词（在名称或描述字段中搜索）
    - category：分类筛选
    - status：状态筛选
    - date_from：开始日期（YYYY-MM-DD）
    - date_to：结束日期（YYYY-MM-DD）
    """
    # 获取全部条目
    all_items = await crud.get_all()

    # 应用高级分页
    paginator = AdvancedPaginator(all_items, pagination, filters)
    page_data, total = paginator.get_page()

    # 在响应中加入额外元数据
    metadata = paginator.get_metadata()

    # 生成自定义提示信息
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
    q: str = Query(..., min_length=1, description="搜索关键词"),
    fields: List[str] = Query(["name", "description"], description="搜索字段"),
    exact_match: bool = Query(False, description="是否精确匹配"),
    case_sensitive: bool = Query(False, description="是否区分大小写"),
    pagination: PaginationParams = Depends(pagination_params)
) -> JSONResponse:
    """
    高级搜索功能

    - **q**：搜索关键词（必填）
    - **fields**：搜索字段列表
    - **exact_match**：是否精确匹配
    - **case_sensitive**：是否区分大小写
    """
    results = await crud.advanced_search(
        query=q,
        fields=fields,
        exact_match=exact_match,
        case_sensitive=case_sensitive
    )

    # 应用分页
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
    item_id: int = Path(..., gt=0, description="条目 ID")
) -> JSONResponse:
    """获取指定条目"""
    item = await crud.get_by_id(item_id)
    if not item:
        raise ResourceNotFoundException("Item", item_id)

    return success_response(
        data=item.dict(),
        message=f"Item '{item.name}' retrieved successfully"
    )

@router.put("/{item_id}", response_model=dict)
async def update_item(
    item_id: int = Path(..., gt=0, description="条目 ID"),
    item_update: ItemUpdate
) -> JSONResponse:
    """更新条目"""
    existing_item = await crud.get_by_id(item_id)
    if not existing_item:
        raise ResourceNotFoundException("Item", item_id)

    # 检查名称是否与其他条目重复
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
    item_id: int = Path(..., gt=0, description="条目 ID"),
    force: bool = Query(False, description="是否强制删除")
) -> JSONResponse:
    """删除条目"""
    item = await crud.get_by_id(item_id)
    if not item:
        raise ResourceNotFoundException("Item", item_id)

    # 删除前校验（例如是否存在关联订单）
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
    skip_duplicates: bool = Query(False, description="跳过重复项")
) -> JSONResponse:
    """批量创建条目"""
    if len(items) > 100:
        raise ValidationException("Maximum 100 items can be created at once")

    created_items = []
    skipped_items = []
    errors = []

    for i, item_create in enumerate(items):
        try:
            # 检查是否存在重复项
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
    """条目创建通知（后台任务）"""
    # 在实际实现中，可以通过邮件、Slack 等方式发送通知
    import asyncio
    await asyncio.sleep(1)  # 模拟耗时处理
    print(f"Item {item_id} creation notification sent")
```

## 第 7 步:自定义 OpenAPI 文档

### 自定义 OpenAPI 文档(`src/utils/documents.py`)

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from typing import Dict, Any

def custom_openapi(app: FastAPI) -> Dict[str, Any]:
    """创建自定义 OpenAPI Schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # 添加自定义信息
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

### 应用到主程序(`src/main.py` 中追加)

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

## 第 8 步:实现缓存系统

### 响应缓存(`src/utils/cache.py`)

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

# 全局缓存实例
cache = MemoryCache()

def cache_response(ttl_seconds: int = 300, key_prefix: str = ""):
    """响应缓存装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = generate_cache_key(func.__name__, args, kwargs, key_prefix)

            # 从缓存中读取
            cached_response = await cache.get(cache_key)
            if cached_response:
                return cached_response

            # 执行原始函数
            response = await func(*args, **kwargs)

            # 写入缓存
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

### 缓存使用示例

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

## 第 9 步:API 测试

### 启动服务器并做基础测试

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

### 查看 OpenAPI 文档

在浏览器中访问 http://localhost:8000/docs,查看已自定义过的 API 文档。

## 下一步

恭喜您完成了自定义响应处理系统!接下来可以尝试:

1. **[MCP 集成](mcp-integration.md)** —— 实现 Model Context Protocol
<!-- 2. **[Building Authentication Systems](authentication-system.md)** - JWT-based authentication/authorization -->
<!-- 3. **[Building Real-time APIs](realtime-api.md)** - WebSocket and Server-Sent Events -->
<!-- 4. **[Microservices Architecture](microservices-architecture.md)** - Service separation and scaling -->

## 小结

在本教程中,我们实现了一套进阶的响应处理系统:

- ✅ 设计标准化的 API 响应格式
- ✅ 全局异常处理与自定义错误响应
- ✅ 进阶的分页与过滤系统
- ✅ 自定义 OpenAPI 文档
- ✅ 响应缓存与性能优化
- ✅ 请求追踪系统
- ✅ 后台任务处理
- ✅ 批量操作 API

现在您已经能实现企业级 API 服务器的全部核心功能!

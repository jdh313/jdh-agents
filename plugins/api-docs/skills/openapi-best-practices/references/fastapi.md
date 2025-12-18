# FastAPI OpenAPI Implementation

FastAPI auto-generates OpenAPI specs from type hints and Pydantic models. This reference covers FastAPI-specific patterns for implementing OpenAPI best practices.

## Schema Definitions

### Basic Schema Pattern

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime

class UserBase(BaseModel):
    """Shared fields - never expose directly in API."""
    email: EmailStr = Field(..., description="User's primary email address")
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's display name"
    )

class UserCreate(UserBase):
    """Request body for creating a user."""
    password: str = Field(
        ...,
        min_length=8,
        description="Password (min 8 characters)"
    )

class UserUpdate(BaseModel):
    """Request body for updating a user. All fields optional."""
    email: EmailStr | None = Field(None, description="New email address")
    name: str | None = Field(None, description="New display name")

class UserRead(UserBase):
    """Response model for user data."""
    id: int = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
```

### Adding Examples

```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "jane@example.com",
                "name": "Jane Doe",
                "password": "securepassword123"
            }
        }
    )
```

### Generic Response Wrapper

```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class DataResponse(BaseModel, Generic[T]):
    """Standard response wrapper."""
    data: T

class ListResponse(BaseModel, Generic[T]):
    """Paginated list response."""
    data: list[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
```

## Endpoint Documentation

### Complete Endpoint Example

```python
from fastapi import FastAPI, HTTPException, Query, Path
from typing import Annotated

app = FastAPI(
    title="User API",
    description="API for managing users",
    version="1.0.0"
)

@app.get(
    "/users/{user_id}",
    response_model=UserRead,
    operation_id="get_user",
    tags=["users"],
    summary="Get a user by ID",
    responses={
        404: {"model": ProblemDetail, "description": "User not found"},
        403: {"model": ProblemDetail, "description": "Permission denied"},
    }
)
async def get_user(
    user_id: Annotated[int, Path(..., description="User ID", ge=1)]
) -> UserRead:
    """
    Retrieve a user by their unique identifier.

    Returns the user's profile information including email and name.
    """
    user = await user_service.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Pagination Parameters

```python
from fastapi import Query
from typing import Annotated

PaginationPage = Annotated[
    int,
    Query(ge=1, description="Page number (1-indexed)")
]
PaginationPerPage = Annotated[
    int,
    Query(ge=1, le=100, description="Items per page (max 100)")
]

@app.get("/users", response_model=ListResponse[UserRead], operation_id="list_users")
async def list_users(
    page: PaginationPage = 1,
    per_page: PaginationPerPage = 20
) -> ListResponse[UserRead]:
    """List all users with pagination."""
    ...
```

### Query Parameters with Dependencies

```python
from fastapi import Depends

class PaginationParams:
    def __init__(
        self,
        page: PaginationPage = 1,
        per_page: PaginationPerPage = 20
    ):
        self.page = page
        self.per_page = per_page
        self.offset = (page - 1) * per_page

@app.get("/users", response_model=ListResponse[UserRead])
async def list_users(
    pagination: Annotated[PaginationParams, Depends()]
) -> ListResponse[UserRead]:
    ...
```

## Error Handling

### RFC 7807 Problem Detail Schema

```python
from pydantic import BaseModel, Field
from typing import Any

class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details for HTTP APIs."""
    type: str = Field(
        ...,
        description="URI identifying the problem type"
    )
    title: str = Field(
        ...,
        description="Human-readable problem summary"
    )
    status: int = Field(
        ...,
        description="HTTP status code"
    )
    detail: str = Field(
        ...,
        description="Human-readable explanation specific to this occurrence"
    )
    instance: str | None = Field(
        None,
        description="URI reference identifying the specific occurrence"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "https://api.example.com/errors/not-found",
                "title": "Not Found",
                "status": 404,
                "detail": "User with ID 123 was not found",
                "instance": "/users/123"
            }
        }
    )
```

### Custom Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        error_type: str,
        title: str,
        detail: str,
        instance: str | None = None
    ):
        self.status_code = status_code
        self.error_type = error_type
        self.title = title
        self.detail = detail
        self.instance = instance

@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": f"https://api.example.com/errors/{exc.error_type}",
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": exc.instance or str(request.url.path),
        }
    )

# Usage
raise APIError(
    status_code=404,
    error_type="not-found",
    title="Not Found",
    detail=f"User with ID {user_id} was not found"
)
```

### Reusable Response Definitions

```python
# Define once in a constants module
COMMON_RESPONSES = {
    401: {"model": ProblemDetail, "description": "Authentication required"},
    403: {"model": ProblemDetail, "description": "Permission denied"},
}

NOT_FOUND_RESPONSE = {
    404: {"model": ProblemDetail, "description": "Resource not found"}
}

VALIDATION_RESPONSE = {
    422: {"model": ProblemDetail, "description": "Validation error"}
}

# Use in endpoints
@app.get(
    "/users/{user_id}",
    responses={**COMMON_RESPONSES, **NOT_FOUND_RESPONSE}
)
async def get_user(user_id: int): ...

@app.post(
    "/users",
    responses={**COMMON_RESPONSES, **VALIDATION_RESPONSE}
)
async def create_user(user: UserCreate): ...
```

## Tags and Grouping

### Router-Level Tags

```python
from fastapi import APIRouter

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={**COMMON_RESPONSES}  # Applied to all routes
)

@users_router.get("/", response_model=ListResponse[UserRead])
async def list_users(): ...

@users_router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int): ...

app.include_router(users_router)
```

### Tag Metadata

```python
tags_metadata = [
    {
        "name": "users",
        "description": "User management operations",
    },
    {
        "name": "orders",
        "description": "Order processing and tracking",
    },
]

app = FastAPI(openapi_tags=tags_metadata)
```

## OpenAPI Customization

### Custom Schema Names

```python
class UserRead(UserBase):
    id: int

    model_config = ConfigDict(
        # Override default schema name
        json_schema_extra={"title": "User"}
    )
```

### Hiding Endpoints from OpenAPI

```python
@app.get("/internal/health", include_in_schema=False)
async def health_check():
    return {"status": "ok"}
```

### Custom OpenAPI Schema

```python
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="API description with **markdown** support",
        routes=app.routes,
    )

    # Add custom fields
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## Common Patterns

### CRUD Router Factory

```python
from typing import Type, TypeVar
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateType = TypeVar("CreateType", bound=BaseModel)
UpdateType = TypeVar("UpdateType", bound=BaseModel)
ReadType = TypeVar("ReadType", bound=BaseModel)

def create_crud_router(
    model_name: str,
    create_schema: Type[CreateType],
    update_schema: Type[UpdateType],
    read_schema: Type[ReadType],
) -> APIRouter:
    router = APIRouter(prefix=f"/{model_name}s", tags=[f"{model_name}s"])

    @router.get("/", response_model=ListResponse[read_schema], operation_id=f"list_{model_name}s")
    async def list_items(): ...

    @router.get("/{item_id}", response_model=read_schema, operation_id=f"get_{model_name}")
    async def get_item(item_id: int): ...

    @router.post("/", response_model=read_schema, operation_id=f"create_{model_name}")
    async def create_item(item: create_schema): ...

    @router.patch("/{item_id}", response_model=read_schema, operation_id=f"update_{model_name}")
    async def update_item(item_id: int, item: update_schema): ...

    @router.delete("/{item_id}", operation_id=f"delete_{model_name}")
    async def delete_item(item_id: int): ...

    return router
```

### Dependency Injection for Common Parameters

```python
from fastapi import Depends, Header
from typing import Annotated

async def get_current_user(
    authorization: Annotated[str, Header(description="Bearer token")]
) -> User:
    # Validate token, return user
    ...

CurrentUser = Annotated[User, Depends(get_current_user)]

@app.get("/me", response_model=UserRead)
async def get_current_user_profile(user: CurrentUser) -> UserRead:
    return user
```

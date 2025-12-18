# Django Ninja OpenAPI Implementation

Django Ninja provides automatic OpenAPI generation with Pydantic schemas. This reference covers Django Ninja-specific patterns for implementing OpenAPI best practices.

## Schema Definitions

### Basic Schema Pattern

```python
from ninja import Schema, Field
from datetime import datetime
from pydantic import EmailStr

class UserBase(Schema):
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

class UserUpdate(Schema):
    """Request body for updating a user. All fields optional."""
    email: EmailStr | None = Field(None, description="New email address")
    name: str | None = Field(None, description="New display name")

class UserRead(UserBase):
    """Response model for user data."""
    id: int = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
```

### Adding Examples

```python
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "jane@example.com",
                "name": "Jane Doe",
                "password": "securepassword123"
            }
        }
```

### Generic Response Wrapper

```python
from typing import Generic, TypeVar, List
from ninja import Schema

T = TypeVar("T")

class DataResponse(Schema, Generic[T]):
    """Standard response wrapper."""
    data: T

class ListResponse(Schema, Generic[T]):
    """Paginated list response."""
    data: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
```

## API Configuration

### Basic API Setup

```python
from ninja import NinjaAPI

api = NinjaAPI(
    title="User API",
    description="API for managing users",
    version="1.0.0",
)
```

### With Authentication

```python
from ninja.security import HttpBearer

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        # Validate token
        if valid_token(token):
            return token
        return None

api = NinjaAPI(
    title="User API",
    version="1.0.0",
    auth=AuthBearer(),
)
```

## Endpoint Documentation

### Complete Endpoint Example

```python
from ninja import Router, Path, Query
from django.shortcuts import get_object_or_404
from typing import Annotated

router = Router(tags=["users"])

@router.get(
    "/{user_id}",
    response=UserRead,
    operation_id="get_user",
    summary="Get a user by ID",
    description="Retrieve a user by their unique identifier.",
)
def get_user(
    request,
    user_id: Annotated[int, Path(..., description="User ID", ge=1)]
) -> UserRead:
    user = get_object_or_404(User, id=user_id)
    return user
```

### Multiple Response Types

```python
from ninja import Router
from ninja.responses import codes_4xx

@router.get(
    "/{user_id}",
    response={
        200: UserRead,
        404: ProblemDetail,
        403: ProblemDetail,
    },
    operation_id="get_user",
)
def get_user(request, user_id: int):
    try:
        user = User.objects.get(id=user_id)
        return 200, user
    except User.DoesNotExist:
        return 404, ProblemDetail(
            type="https://api.example.com/errors/not-found",
            title="Not Found",
            status=404,
            detail=f"User with ID {user_id} was not found"
        )
```

### Pagination Parameters

```python
from ninja import Query, Schema
from typing import Annotated

class PaginationParams(Schema):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")

@router.get("/", response=ListResponse[UserRead], operation_id="list_users")
def list_users(
    request,
    pagination: Annotated[PaginationParams, Query(...)]
):
    offset = (pagination.page - 1) * pagination.per_page
    users = User.objects.all()[offset:offset + pagination.per_page]
    total = User.objects.count()
    return ListResponse(
        data=list(users),
        total=total,
        page=pagination.page,
        per_page=pagination.per_page,
        pages=(total + pagination.per_page - 1) // pagination.per_page
    )
```

## Error Handling

### RFC 7807 Problem Detail Schema

```python
from ninja import Schema, Field

class ProblemDetail(Schema):
    """RFC 7807 Problem Details for HTTP APIs."""
    type: str = Field(..., description="URI identifying the problem type")
    title: str = Field(..., description="Human-readable problem summary")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable explanation")
    instance: str | None = Field(None, description="URI of specific occurrence")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "https://api.example.com/errors/not-found",
                "title": "Not Found",
                "status": 404,
                "detail": "User with ID 123 was not found",
                "instance": "/api/users/123"
            }
        }
```

### Custom Exception Handler

```python
from ninja import NinjaAPI
from ninja.errors import HttpError

class APIError(Exception):
    def __init__(self, status_code: int, error_type: str, title: str, detail: str):
        self.status_code = status_code
        self.error_type = error_type
        self.title = title
        self.detail = detail

api = NinjaAPI()

@api.exception_handler(APIError)
def api_error_handler(request, exc: APIError):
    return api.create_response(
        request,
        {
            "type": f"https://api.example.com/errors/{exc.error_type}",
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.path,
        },
        status=exc.status_code,
    )

# Usage
raise APIError(
    status_code=404,
    error_type="not-found",
    title="Not Found",
    detail=f"User with ID {user_id} was not found"
)
```

### Validation Error Customization

```python
from ninja.errors import ValidationError

@api.exception_handler(ValidationError)
def validation_error_handler(request, exc: ValidationError):
    return api.create_response(
        request,
        {
            "type": "https://api.example.com/errors/validation-error",
            "title": "Validation Error",
            "status": 422,
            "detail": str(exc.errors),
            "instance": request.path,
        },
        status=422,
    )
```

## Routers and Organization

### Router Setup

```python
from ninja import Router

users_router = Router(tags=["users"])
orders_router = Router(tags=["orders"])

@users_router.get("/", response=ListResponse[UserRead])
def list_users(request): ...

@users_router.get("/{user_id}", response=UserRead)
def get_user(request, user_id: int): ...

# Register with main API
api.add_router("/users", users_router)
api.add_router("/orders", orders_router)
```

### Nested Routers

```python
# users/orders endpoints
user_orders_router = Router()

@user_orders_router.get("/", response=ListResponse[OrderRead])
def list_user_orders(request, user_id: int): ...

users_router.add_router("/{user_id}/orders", user_orders_router)
```

## Tags and Grouping

### Tag Definitions

```python
api = NinjaAPI(
    title="My API",
    version="1.0.0",
    openapi_extra={
        "tags": [
            {"name": "users", "description": "User management operations"},
            {"name": "orders", "description": "Order processing and tracking"},
        ]
    }
)
```

### Multiple Tags per Endpoint

```python
@router.get(
    "/{user_id}/orders",
    response=ListResponse[OrderRead],
    tags=["users", "orders"],  # Appears in both sections
)
def list_user_orders(request, user_id: int): ...
```

## Model Integration

### From Django Model

```python
from ninja import ModelSchema
from myapp.models import User

class UserRead(ModelSchema):
    class Meta:
        model = User
        fields = ["id", "email", "name", "created_at", "updated_at"]
```

### Partial Updates with ModelSchema

```python
class UserUpdate(ModelSchema):
    class Meta:
        model = User
        fields = ["email", "name"]
        fields_optional = "__all__"  # All fields optional for PATCH
```

### Excluding Fields

```python
class UserRead(ModelSchema):
    class Meta:
        model = User
        exclude = ["password", "is_superuser", "is_staff"]
```

## OpenAPI Customization

### Custom Operation IDs

```python
@router.get(
    "/{user_id}",
    response=UserRead,
    operation_id="get_user_by_id",  # Custom operation ID
)
def get_user(request, user_id: int): ...
```

### Deprecating Endpoints

```python
@router.get(
    "/legacy/{user_id}",
    response=UserRead,
    deprecated=True,
    summary="Get user (deprecated)",
    description="Use /users/{user_id} instead.",
)
def get_user_legacy(request, user_id: int): ...
```

### Hiding from OpenAPI

```python
@router.get("/internal/health", include_in_schema=False)
def health_check(request):
    return {"status": "ok"}
```

## Common Patterns

### CRUD Mixin

```python
from typing import Type, TypeVar
from ninja import Router, Schema

def create_crud_router(
    model,
    create_schema: Type[Schema],
    update_schema: Type[Schema],
    read_schema: Type[Schema],
    prefix: str,
    tags: list[str],
) -> Router:
    router = Router(tags=tags)

    @router.get("/", response=ListResponse[read_schema], operation_id=f"list_{prefix}")
    def list_items(request):
        return ListResponse(data=list(model.objects.all()), ...)

    @router.get("/{item_id}", response=read_schema, operation_id=f"get_{prefix[:-1]}")
    def get_item(request, item_id: int):
        return get_object_or_404(model, id=item_id)

    @router.post("/", response=read_schema, operation_id=f"create_{prefix[:-1]}")
    def create_item(request, payload: create_schema):
        return model.objects.create(**payload.dict())

    @router.patch("/{item_id}", response=read_schema, operation_id=f"update_{prefix[:-1]}")
    def update_item(request, item_id: int, payload: update_schema):
        item = get_object_or_404(model, id=item_id)
        for attr, value in payload.dict(exclude_unset=True).items():
            setattr(item, attr, value)
        item.save()
        return item

    @router.delete("/{item_id}", operation_id=f"delete_{prefix[:-1]}")
    def delete_item(request, item_id: int):
        item = get_object_or_404(model, id=item_id)
        item.delete()
        return {"success": True}

    return router
```

### Authentication Dependency

```python
from ninja.security import HttpBearer
from typing import Annotated

class BearerAuth(HttpBearer):
    def authenticate(self, request, token):
        user = validate_token(token)
        if user:
            return user
        return None

# Apply to specific endpoints
@router.get("/me", response=UserRead, auth=BearerAuth())
def get_current_user(request):
    return request.auth  # The authenticated user

# Or apply to entire router
protected_router = Router(auth=BearerAuth())
```

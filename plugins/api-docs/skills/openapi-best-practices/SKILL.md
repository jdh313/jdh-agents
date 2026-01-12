---
name: OpenAPI Best Practices
description: Use Skill(api-docs:openapi-best-practices) when the user asks to "write an API endpoint", "create a FastAPI route", "add a Django Ninja endpoint", "document an API", "write OpenAPI spec", "fix API documentation", "review API code", or when writing code that involves FastAPI, Django Ninja, or OpenAPI specifications. Provides naming conventions, schema reuse patterns, and error standardization guidance.
version: 0.1.0
---

# OpenAPI Best Practices

Guidance for writing consistent, well-documented APIs using FastAPI, Django Ninja, or manual OpenAPI specifications.

## Core Principles

### 1. Single Source of Truth

Define each piece of information once. Duplication leads to inconsistency.

- Define error messages in error classes, not repeated in endpoint descriptions
- Define field descriptions in schema models, not in endpoint parameters
- Use schema references (`$ref`) instead of inline definitions

### 2. Consistent Naming

Follow the `{Model}{Operation}` pattern for all schemas:

| Pattern | Purpose | Example |
|---------|---------|---------|
| `{Model}Create` | Request body for POST | `UserCreate` |
| `{Model}Update` | Request body for PATCH/PUT | `UserUpdate` |
| `{Model}Read` | Response model | `UserRead` |
| `{Model}List` | Paginated list response | `UserList` |
| `{Model}Base` | Shared fields (internal only) | `UserBase` |

**Rules:**
- Use PascalCase for schema names
- Use snake_case for field names
- Never expose `Base` schemas in API responses
- Keep names short but descriptive

### 3. Standardized Error Responses

Follow RFC 7807 "Problem Details for HTTP APIs":

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Field 'email' must be a valid email address",
  "instance": "/users"
}
```

**Required fields:**
- `type`: URI identifying the error type
- `title`: Human-readable error category
- `status`: HTTP status code
- `detail`: Specific error message

**Optional fields:**
- `instance`: URI of the request that caused the error
- Custom fields for additional context

See `references/error-responses.md` for complete implementation patterns.

## Schema Design

### Field Documentation

Document fields in the schema, not the endpoint:

```python
# CORRECT - description lives with the field
class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's primary email address")
    name: str = Field(..., min_length=1, max_length=100, description="Display name")

# INCORRECT - duplicating description in endpoint
@app.post("/users", description="Create user with email and name...")
def create_user(user: UserCreate): ...
```

### Reusable Components

Extract common patterns into reusable schemas:

**Pagination:**
```python
class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int
```

**Common fields:**
```python
class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime

class UserRead(UserBase, TimestampMixin):
    id: int
```

### Inheritance Hierarchy

Structure schema inheritance to avoid duplication:

```
UserBase (shared fields: email, name)
├── UserCreate (inherits Base, adds password)
├── UserUpdate (all fields optional)
└── UserRead (inherits Base, adds id, timestamps)
```

## Endpoint Documentation

### Operation IDs

Provide explicit, consistent operation IDs:

```python
@app.get("/users/{user_id}", operation_id="get_user")
@app.get("/users", operation_id="list_users")
@app.post("/users", operation_id="create_user")
@app.patch("/users/{user_id}", operation_id="update_user")
@app.delete("/users/{user_id}", operation_id="delete_user")
```

**Pattern:** `{verb}_{resource}` in snake_case

### Tags

Group related endpoints with consistent tags:

```python
@app.get("/users", tags=["users"])
@app.get("/users/{id}/orders", tags=["users", "orders"])
```

### Response Documentation

Document all possible responses:

```python
@app.get(
    "/users/{user_id}",
    response_model=UserRead,
    responses={
        404: {"model": ProblemDetail, "description": "User not found"},
        403: {"model": ProblemDetail, "description": "Permission denied"},
    }
)
```

## DRY Patterns

### Error Response Reuse

Define error responses once, reference everywhere:

```python
# Define once
NOT_FOUND_RESPONSE = {
    404: {"model": ProblemDetail, "description": "Resource not found"}
}
FORBIDDEN_RESPONSE = {
    403: {"model": ProblemDetail, "description": "Permission denied"}
}

# Reuse
@app.get("/users/{id}", responses={**NOT_FOUND_RESPONSE, **FORBIDDEN_RESPONSE})
@app.get("/orders/{id}", responses={**NOT_FOUND_RESPONSE, **FORBIDDEN_RESPONSE})
```

### Description Templates

For repetitive descriptions, use constants:

```python
PAGINATION_DESCRIPTION = "Page number (1-indexed)"
PER_PAGE_DESCRIPTION = "Items per page (max 100)"

class PaginationParams(BaseModel):
    page: int = Field(1, description=PAGINATION_DESCRIPTION)
    per_page: int = Field(20, description=PER_PAGE_DESCRIPTION)
```

### Shared Examples

Define examples in schemas, not endpoints:

```python
class UserCreate(BaseModel):
    email: EmailStr
    name: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "Jane Doe"
            }
        }
    )
```

## Review Checklist

When reviewing API code, verify:

**Naming:**
- [ ] Schema names follow `{Model}{Operation}` pattern
- [ ] Field names use snake_case
- [ ] Operation IDs are consistent (`{verb}_{resource}`)
- [ ] No `Base` schemas exposed in responses

**Documentation:**
- [ ] Field descriptions in schemas, not endpoints
- [ ] All error responses documented
- [ ] Examples provided in schemas
- [ ] Tags group related endpoints

**DRY:**
- [ ] No duplicated error messages
- [ ] Common responses extracted to constants
- [ ] Pagination/filtering patterns reused
- [ ] No inline schema definitions (use `$ref`)

**Errors:**
- [ ] Single error response schema used everywhere
- [ ] RFC 7807 structure followed
- [ ] Error types are URIs
- [ ] Detail messages are specific

## Framework References

For framework-specific implementation details:

- **FastAPI**: See `references/fastapi.md`
- **Django Ninja**: See `references/django-ninja.md`
- **Manual OpenAPI**: See `references/manual-spec.md`
- **Error Responses**: See `references/error-responses.md`

## Aggression Levels

When reviewing code, apply these standards based on level:

**Strict:** Flag all deviations from best practices
- Missing descriptions on any field
- Any naming inconsistency
- Missing response documentation
- Inline schema definitions

**Normal (default):** Flag clear violations, suggest improvements
- Duplicated descriptions/schemas
- Inconsistent naming patterns
- Missing error responses
- Exposed internal schemas

**Minimal:** Only flag serious issues
- Completely missing documentation
- Duplicate schemas with different names
- No error handling documented

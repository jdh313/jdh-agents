# Error Response Standardization

This reference covers implementing RFC 7807 "Problem Details for HTTP APIs" and creating consistent error responses across your API.

## RFC 7807 Overview

RFC 7807 defines a standard format for HTTP API error responses. Using this format ensures:

- Consistent error structure across all endpoints
- Machine-readable error types via URIs
- Human-readable details for debugging
- Extensibility for domain-specific error information

## Problem Detail Structure

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | URI | Identifies the problem type. Should be a URL that provides documentation. |
| `title` | string | Human-readable summary of the problem type (same for all occurrences) |
| `status` | integer | HTTP status code |
| `detail` | string | Human-readable explanation specific to this occurrence |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `instance` | URI | URI reference identifying the specific occurrence |
| (custom) | any | Additional fields for domain-specific information |

### Example

```json
{
  "type": "https://api.example.com/errors/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "Field 'email' must be a valid email address",
  "instance": "/users",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "value": "not-an-email"
    }
  ]
}
```

## Error Type URIs

### Designing Error Type URIs

Error type URIs should:

1. Be stable and permanent
2. Point to human-readable documentation
3. Follow a consistent naming pattern
4. Be specific enough to be actionable

### Recommended Structure

```
https://api.example.com/errors/{category}/{specific-error}
```

### Standard Error Types

```yaml
# Authentication errors
https://api.example.com/errors/auth/unauthorized
https://api.example.com/errors/auth/invalid-token
https://api.example.com/errors/auth/token-expired

# Authorization errors
https://api.example.com/errors/auth/forbidden
https://api.example.com/errors/auth/insufficient-scope

# Resource errors
https://api.example.com/errors/resource/not-found
https://api.example.com/errors/resource/already-exists
https://api.example.com/errors/resource/conflict

# Validation errors
https://api.example.com/errors/validation/invalid-input
https://api.example.com/errors/validation/missing-field
https://api.example.com/errors/validation/invalid-format

# Rate limiting
https://api.example.com/errors/rate-limit/exceeded

# Server errors
https://api.example.com/errors/server/internal-error
https://api.example.com/errors/server/service-unavailable
```

## Common Error Responses

### 400 Bad Request

```json
{
  "type": "https://api.example.com/errors/validation/invalid-input",
  "title": "Bad Request",
  "status": 400,
  "detail": "The request body could not be parsed as valid JSON"
}
```

### 401 Unauthorized

```json
{
  "type": "https://api.example.com/errors/auth/unauthorized",
  "title": "Unauthorized",
  "status": 401,
  "detail": "Authentication credentials were not provided or are invalid"
}
```

### 403 Forbidden

```json
{
  "type": "https://api.example.com/errors/auth/forbidden",
  "title": "Forbidden",
  "status": 403,
  "detail": "You do not have permission to access this resource"
}
```

### 404 Not Found

```json
{
  "type": "https://api.example.com/errors/resource/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User with ID 123 was not found",
  "instance": "/users/123"
}
```

### 409 Conflict

```json
{
  "type": "https://api.example.com/errors/resource/conflict",
  "title": "Conflict",
  "status": 409,
  "detail": "A user with email 'jane@example.com' already exists"
}
```

### 422 Unprocessable Entity

```json
{
  "type": "https://api.example.com/errors/validation/invalid-input",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request contains invalid data",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "code": "invalid_format"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters",
      "code": "min_length"
    }
  ]
}
```

### 429 Too Many Requests

```json
{
  "type": "https://api.example.com/errors/rate-limit/exceeded",
  "title": "Too Many Requests",
  "status": 429,
  "detail": "Rate limit exceeded. Try again in 60 seconds",
  "retry_after": 60
}
```

### 500 Internal Server Error

```json
{
  "type": "https://api.example.com/errors/server/internal-error",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred. Please try again later",
  "trace_id": "abc123xyz"
}
```

## Implementation Patterns

### Error Constants

Define error types as constants to ensure consistency:

```python
# errors.py
from dataclasses import dataclass
from typing import ClassVar

@dataclass
class ErrorType:
    type_suffix: str
    title: str
    status: int

    @property
    def type_uri(self) -> str:
        return f"https://api.example.com/errors/{self.type_suffix}"

class Errors:
    UNAUTHORIZED = ErrorType("auth/unauthorized", "Unauthorized", 401)
    FORBIDDEN = ErrorType("auth/forbidden", "Forbidden", 403)
    NOT_FOUND = ErrorType("resource/not-found", "Not Found", 404)
    CONFLICT = ErrorType("resource/conflict", "Conflict", 409)
    VALIDATION = ErrorType("validation/invalid-input", "Validation Error", 422)
    RATE_LIMITED = ErrorType("rate-limit/exceeded", "Too Many Requests", 429)
    INTERNAL = ErrorType("server/internal-error", "Internal Server Error", 500)
```

### Error Factory

```python
from typing import Any

def create_problem_detail(
    error_type: ErrorType,
    detail: str,
    instance: str | None = None,
    **extra: Any
) -> dict:
    response = {
        "type": error_type.type_uri,
        "title": error_type.title,
        "status": error_type.status,
        "detail": detail,
    }
    if instance:
        response["instance"] = instance
    response.update(extra)
    return response

# Usage
error = create_problem_detail(
    Errors.NOT_FOUND,
    detail=f"User with ID {user_id} was not found",
    instance=f"/users/{user_id}"
)
```

### Validation Error Helper

```python
def create_validation_error(errors: list[dict]) -> dict:
    return create_problem_detail(
        Errors.VALIDATION,
        detail="The request contains invalid data",
        errors=errors
    )

# Usage
error = create_validation_error([
    {"field": "email", "message": "Invalid format", "code": "invalid_format"},
    {"field": "name", "message": "Required field", "code": "required"},
])
```

## Avoiding Common Mistakes

### Mistake 1: Inconsistent Error Formats

```json
// WRONG - Different formats for different endpoints
// Endpoint A:
{"error": "User not found"}

// Endpoint B:
{"message": "Not found", "code": 404}

// Endpoint C:
{"errors": [{"msg": "Invalid input"}]}
```

```json
// CORRECT - Same format everywhere
{
  "type": "https://api.example.com/errors/resource/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User not found"
}
```

### Mistake 2: Duplicating Error Messages

```python
# WRONG - Message defined in multiple places
@app.get("/users/{id}")
def get_user(id: int):
    raise HTTPException(404, "User not found")  # Duplicated

@app.delete("/users/{id}")
def delete_user(id: int):
    raise HTTPException(404, "User not found")  # Duplicated
```

```python
# CORRECT - Single source of truth
class UserNotFoundError(APIError):
    def __init__(self, user_id: int):
        super().__init__(
            error_type=Errors.NOT_FOUND,
            detail=f"User with ID {user_id} was not found"
        )

@app.get("/users/{id}")
def get_user(id: int):
    raise UserNotFoundError(id)

@app.delete("/users/{id}")
def delete_user(id: int):
    raise UserNotFoundError(id)
```

### Mistake 3: Exposing Internal Details

```json
// WRONG - Exposes stack trace and internal info
{
  "error": "NullPointerException at UserService.java:123",
  "stack": "..."
}
```

```json
// CORRECT - Generic message, internal tracking
{
  "type": "https://api.example.com/errors/server/internal-error",
  "title": "Internal Server Error",
  "status": 500,
  "detail": "An unexpected error occurred",
  "trace_id": "abc123"  // For internal debugging
}
```

### Mistake 4: Wrong Status Codes

| Situation | Wrong | Correct |
|-----------|-------|---------|
| Resource doesn't exist | 400 | 404 |
| Invalid input format | 400 | 422 |
| Not authenticated | 403 | 401 |
| Not authorized | 401 | 403 |
| Duplicate resource | 400 | 409 |

## Simplified Alternative

For simpler APIs, a reduced format is acceptable:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User with ID 123 was not found"
  }
}
```

**When to use simplified format:**
- Internal APIs with limited consumers
- APIs where full RFC 7807 is overkill
- Consistency is still maintained across all endpoints

**Key requirement:** Whatever format is chosen, use it consistently everywhere.

## Schema Definition

### Full RFC 7807 Schema

```yaml
components:
  schemas:
    ProblemDetail:
      type: object
      required:
        - type
        - title
        - status
        - detail
      properties:
        type:
          type: string
          format: uri
          description: URI identifying the problem type
          example: https://api.example.com/errors/not-found
        title:
          type: string
          description: Human-readable problem summary
          example: Not Found
        status:
          type: integer
          description: HTTP status code
          example: 404
        detail:
          type: string
          description: Human-readable explanation
          example: User with ID 123 was not found
        instance:
          type: string
          format: uri
          description: URI of specific occurrence
          example: /users/123

    ValidationError:
      allOf:
        - $ref: '#/components/schemas/ProblemDetail'
        - type: object
          properties:
            errors:
              type: array
              items:
                type: object
                properties:
                  field:
                    type: string
                  message:
                    type: string
                  code:
                    type: string
```

### Simplified Schema

```yaml
components:
  schemas:
    Error:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: Error code
              example: NOT_FOUND
            message:
              type: string
              description: Error message
              example: User with ID 123 was not found
```

## Testing Error Responses

Verify error responses in tests:

```python
def test_user_not_found_returns_problem_detail():
    response = client.get("/users/999")

    assert response.status_code == 404
    data = response.json()

    # Verify RFC 7807 structure
    assert data["type"] == "https://api.example.com/errors/resource/not-found"
    assert data["title"] == "Not Found"
    assert data["status"] == 404
    assert "999" in data["detail"]
    assert data["instance"] == "/users/999"

def test_validation_error_includes_field_details():
    response = client.post("/users", json={"email": "invalid"})

    assert response.status_code == 422
    data = response.json()

    assert data["type"] == "https://api.example.com/errors/validation/invalid-input"
    assert "errors" in data
    assert any(e["field"] == "email" for e in data["errors"])
```

# Manual OpenAPI Specification

This reference covers writing OpenAPI specifications directly in YAML or JSON, following OpenAPI 3.1 best practices.

## Document Structure

### Minimal Valid Spec

```yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0
paths: {}
```

### Complete Structure

```yaml
openapi: 3.1.0
info:
  title: User API
  description: API for managing users
  version: 1.0.0
  contact:
    name: API Support
    email: support@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: https://api.example.com/v1
    description: Production
  - url: https://staging-api.example.com/v1
    description: Staging

tags:
  - name: users
    description: User management operations
  - name: orders
    description: Order processing

paths:
  /users:
    # ... endpoints

components:
  schemas:
    # ... schema definitions
  responses:
    # ... reusable responses
  parameters:
    # ... reusable parameters
  securitySchemes:
    # ... auth definitions
```

## Schema Definitions

### Basic Schema with Naming Convention

```yaml
components:
  schemas:
    # Base schema (internal reference only)
    UserBase:
      type: object
      properties:
        email:
          type: string
          format: email
          description: User's primary email address
        name:
          type: string
          minLength: 1
          maxLength: 100
          description: User's display name
      required:
        - email
        - name

    # Create request schema
    UserCreate:
      allOf:
        - $ref: '#/components/schemas/UserBase'
        - type: object
          properties:
            password:
              type: string
              minLength: 8
              description: Password (min 8 characters)
          required:
            - password

    # Update request schema (all optional)
    UserUpdate:
      type: object
      properties:
        email:
          type: string
          format: email
          description: New email address
        name:
          type: string
          description: New display name

    # Response schema
    UserRead:
      allOf:
        - $ref: '#/components/schemas/UserBase'
        - type: object
          properties:
            id:
              type: integer
              description: Unique user identifier
            created_at:
              type: string
              format: date-time
              description: Account creation timestamp
            updated_at:
              type: string
              format: date-time
              description: Last update timestamp
          required:
            - id
            - created_at
            - updated_at
```

### Adding Examples

```yaml
components:
  schemas:
    UserCreate:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        password:
          type: string
      required:
        - email
        - name
        - password
      example:
        email: jane@example.com
        name: Jane Doe
        password: securepassword123
```

### Generic List Response

```yaml
components:
  schemas:
    UserList:
      type: object
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/UserRead'
        total:
          type: integer
          description: Total number of items
        page:
          type: integer
          description: Current page number
        per_page:
          type: integer
          description: Items per page
        pages:
          type: integer
          description: Total number of pages
      required:
        - data
        - total
        - page
        - per_page
        - pages
```

## Path Definitions

### Complete CRUD Example

```yaml
paths:
  /users:
    get:
      operationId: list_users
      summary: List all users
      description: Retrieve a paginated list of users
      tags:
        - users
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PerPageParam'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
        '401':
          $ref: '#/components/responses/Unauthorized'

    post:
      operationId: create_user
      summary: Create a new user
      tags:
        - users
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserRead'
        '422':
          $ref: '#/components/responses/ValidationError'

  /users/{user_id}:
    get:
      operationId: get_user
      summary: Get a user by ID
      tags:
        - users
      parameters:
        - $ref: '#/components/parameters/UserIdParam'
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserRead'
        '404':
          $ref: '#/components/responses/NotFound'

    patch:
      operationId: update_user
      summary: Update a user
      tags:
        - users
      parameters:
        - $ref: '#/components/parameters/UserIdParam'
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserUpdate'
      responses:
        '200':
          description: User updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserRead'
        '404':
          $ref: '#/components/responses/NotFound'
        '422':
          $ref: '#/components/responses/ValidationError'

    delete:
      operationId: delete_user
      summary: Delete a user
      tags:
        - users
      parameters:
        - $ref: '#/components/parameters/UserIdParam'
      responses:
        '204':
          description: User deleted
        '404':
          $ref: '#/components/responses/NotFound'
```

## Reusable Components

### Parameters

```yaml
components:
  parameters:
    UserIdParam:
      name: user_id
      in: path
      required: true
      description: User ID
      schema:
        type: integer
        minimum: 1

    PageParam:
      name: page
      in: query
      description: Page number (1-indexed)
      schema:
        type: integer
        minimum: 1
        default: 1

    PerPageParam:
      name: per_page
      in: query
      description: Items per page (max 100)
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
```

### Responses

```yaml
components:
  responses:
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
          example:
            type: https://api.example.com/errors/not-found
            title: Not Found
            status: 404
            detail: The requested resource was not found

    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
          example:
            type: https://api.example.com/errors/unauthorized
            title: Unauthorized
            status: 401
            detail: Authentication credentials were not provided

    Forbidden:
      description: Permission denied
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'

    ValidationError:
      description: Validation error
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetail'
```

## Error Schema (RFC 7807)

```yaml
components:
  schemas:
    ProblemDetail:
      type: object
      description: RFC 7807 Problem Details
      properties:
        type:
          type: string
          format: uri
          description: URI identifying the problem type
        title:
          type: string
          description: Human-readable problem summary
        status:
          type: integer
          description: HTTP status code
        detail:
          type: string
          description: Human-readable explanation
        instance:
          type: string
          format: uri
          description: URI of specific occurrence
      required:
        - type
        - title
        - status
        - detail
      example:
        type: https://api.example.com/errors/not-found
        title: Not Found
        status: 404
        detail: User with ID 123 was not found
        instance: /users/123
```

## Security Schemes

### Bearer Token

```yaml
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: JWT Bearer token authentication

# Apply globally
security:
  - BearerAuth: []

# Or per-endpoint
paths:
  /users:
    get:
      security:
        - BearerAuth: []
```

### API Key

```yaml
components:
  securitySchemes:
    ApiKeyAuth:
      type: apiKey
      in: header
      name: X-API-Key
```

### OAuth2

```yaml
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/oauth/authorize
          tokenUrl: https://auth.example.com/oauth/token
          scopes:
            read:users: Read user data
            write:users: Modify user data
```

## Best Practices

### Use $ref for Everything Reusable

```yaml
# CORRECT - using references
paths:
  /users/{user_id}:
    get:
      parameters:
        - $ref: '#/components/parameters/UserIdParam'
      responses:
        '404':
          $ref: '#/components/responses/NotFound'

# INCORRECT - inline definitions
paths:
  /users/{user_id}:
    get:
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '404':
          description: Not found
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
```

### Consistent Operation IDs

```yaml
# Pattern: {verb}_{resource}
paths:
  /users:
    get:
      operationId: list_users
    post:
      operationId: create_user
  /users/{user_id}:
    get:
      operationId: get_user
    patch:
      operationId: update_user
    delete:
      operationId: delete_user
```

### Tag Organization

```yaml
tags:
  - name: users
    description: User management operations
    externalDocs:
      description: User management guide
      url: https://docs.example.com/users

paths:
  /users:
    get:
      tags: [users]
  /users/{user_id}:
    get:
      tags: [users]
  /users/{user_id}/orders:
    get:
      tags: [users, orders]  # Multiple tags for cross-cutting endpoints
```

### Descriptions at the Right Level

```yaml
# CORRECT - descriptions in schema
components:
  schemas:
    UserCreate:
      type: object
      properties:
        email:
          type: string
          format: email
          description: User's primary email address  # Description here

# INCORRECT - repeating in endpoint
paths:
  /users:
    post:
      description: Create user with email address...  # Don't repeat
```

## File Organization

For large APIs, split into multiple files:

```
api/
├── openapi.yaml        # Main file with $ref to others
├── paths/
│   ├── users.yaml
│   └── orders.yaml
├── schemas/
│   ├── user.yaml
│   └── order.yaml
└── responses/
    └── errors.yaml
```

### Main File

```yaml
# openapi.yaml
openapi: 3.1.0
info:
  title: My API
  version: 1.0.0

paths:
  /users:
    $ref: './paths/users.yaml#/users'
  /users/{user_id}:
    $ref: './paths/users.yaml#/users~1{user_id}'

components:
  schemas:
    UserCreate:
      $ref: './schemas/user.yaml#/UserCreate'
    UserRead:
      $ref: './schemas/user.yaml#/UserRead'
  responses:
    NotFound:
      $ref: './responses/errors.yaml#/NotFound'
```

## Validation Tools

Validate specs with:

```bash
# Using swagger-cli
npx @apidevtools/swagger-cli validate openapi.yaml

# Using redocly
npx @redocly/cli lint openapi.yaml

# Using spectral
npx @stoplight/spectral-cli lint openapi.yaml
```

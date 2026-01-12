---
name: fastapi-expert
description: Use Skill(fastapi-expert:fastapi-expert) when working with FastAPI code or REST API development in Python. Use for building, refactoring, or troubleshooting FastAPI REST APIs. Trigger phrases include "FastAPI", "REST API in Python", "API endpoint", "add authentication", "database integration", "async SQLAlchemy", "Alembic migrations", "API testing", "rate limiting", or any production-grade FastAPI development. Provides comprehensive patterns covering project setup, JWT/OAuth2 auth, async database access, error handling, testing strategies, and performance optimization.
allowed-tools:
  - Read
  - Grep
  - Glob
  - WebSearch
  - WebFetch
---

# FastAPI Expert

## Overview

Provide expert guidance for building production-grade FastAPI REST APIs following modern best practices. This skill provides access to a comprehensive reference guide covering 14 major categories of FastAPI development, from project structure and database integration to security, testing, and monitoring.

## When to Use This Skill

Invoke this skill for:

- **Project Setup**: Initializing new FastAPI projects with proper structure
- **Authentication/Security**: Implementing JWT, OAuth2, RBAC, CORS, rate limiting
- **Database Integration**: Setting up async SQLAlchemy, Alembic migrations, connection pooling
- **API Design**: RESTful conventions, status codes, pagination, filtering
- **Error Handling**: Custom exceptions, global handlers, structured logging
- **Testing**: Pytest with async support, fixtures, unit/integration/e2e patterns
- **Performance**: Caching strategies, rate limiting, query optimization
- **Background Tasks**: Choosing between BackgroundTasks and Celery
- **Configuration**: Pydantic Settings, environment variables
- **API Versioning**: Sub-applications vs router prefixes
- **Monitoring**: OpenTelemetry, Prometheus metrics, health checks
- **Code Quality**: Ruff/MyPy setup, pre-commit hooks, CI/CD
- **Troubleshooting**: Debugging async issues, N+1 queries, connection pool problems

## When NOT to Use This Skill

Skip this skill for:
- Simple read-only endpoints with no authentication requirements
- Quick prototypes or proof-of-concept code without production requirements
- Non-FastAPI Python web frameworks (Flask, Django, Tornado)
- Static file serving or simple redirect endpoints

## Using the Reference Guide

Access the comprehensive reference guide in `references/fastapi-reference.md` for detailed patterns and examples. The reference is organized into 14 sections with a table of contents for quick navigation.

**To use the reference effectively:**

1. Read the reference file when starting a new FastAPI task
2. Navigate directly to relevant sections using the table of contents
3. Copy and adapt code examples for the specific use case
4. Follow the established patterns for consistency

**Key sections include:**

- **Section 1**: Project structure and layered architecture patterns
- **Section 2**: Database setup with async SQLAlchemy and Alembic
- **Section 3**: RESTful API design conventions and status codes
- **Section 4**: Authentication (JWT/OAuth2) and authorization (RBAC)
- **Section 5**: Error handling with custom exceptions and global handlers
- **Section 6**: Testing strategies with pytest and async support
- **Section 7**: Performance optimization (async, caching, rate limiting)
- **Section 8**: Background tasks (BackgroundTasks vs Celery)
- **Section 9**: Configuration management with Pydantic Settings
- **Section 10**: API versioning strategies
- **Section 11**: Monitoring with OpenTelemetry and Prometheus
- **Section 12**: OpenAPI documentation customization
- **Section 13**: Code quality tools (Ruff, MyPy, pre-commit)
- **Section 14**: Additional topics (WebSockets, file uploads, middleware)

## Quick Start Examples

### Creating a New FastAPI Project

```python
# Project structure following layered architecture
project/
├── app/
│   ├── main.py
│   ├── config/settings.py
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── repositories/     # Data access
│   ├── services/         # Business logic
│   ├── routers/          # API endpoints
│   ├── dependencies.py
│   └── exceptions.py
├── tests/
├── migrations/
└── pyproject.toml
```

Refer to Section 1 in the reference guide for complete setup details.

### Implementing JWT Authentication

```python
# Snippet - see references/fastapi-reference.md Section 4 for complete implementation
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    # ... (complete implementation in reference guide)
    pass
```

### Setting Up Database with Alembic

```bash
# See Section 2 for complete database setup
alembic init -t async migrations
alembic revision --autogenerate -m "initial migration"
alembic upgrade head
```

### Adding Rate Limiting

```python
# Snippet - see references/fastapi-reference.md Section 7 for complete implementation
from slowapi import Limiter

@router.post("/api/resource")
@limiter.limit("5/minute")
async def create_resource(request: Request):
    # ... (complete implementation in reference guide)
    pass
```

## Development Workflow

**For new features:**

1. Read relevant section in the reference guide
2. Implement following the established patterns
3. Add tests (unit, integration, e2e as appropriate)
4. Run linting and type checking
5. Verify test coverage meets project standards (typically 80%+ overall, 95%+ for critical paths)

**For troubleshooting:**

1. Identify the problem category (async, database, auth, etc.)
2. Consult the relevant reference section
3. Check for common anti-patterns documented in the guide
4. Apply the recommended solution pattern

**Best practices to follow:**

- Use `uv` for all Python package management
- Async SQLAlchemy with proper connection pooling
- Separate schemas for create/update/response operations
- Dependency injection with `Annotated` types
- Structured error responses with request IDs
- Comprehensive test coverage with pytest

## Resources

### references/

**fastapi-reference.md** - Comprehensive 14-section reference guide with:
- Complete code examples for all major patterns
- Best practices for production deployments
- Common pitfalls and anti-patterns to avoid
- Quick reference commands
- Links to official documentation

Access this file when implementing any FastAPI feature to ensure following established best practices and patterns.

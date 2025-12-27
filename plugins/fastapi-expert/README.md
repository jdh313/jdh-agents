# fastapi-expert

Expert guidance for building production-grade FastAPI REST APIs with modern best practices.

## What It Does

This plugin provides comprehensive patterns and expert guidance for FastAPI development, covering:

- Project structure and layered architecture
- Async SQLAlchemy database integration with Alembic migrations
- RESTful API design and conventions
- Authentication (JWT/OAuth2) and authorization (RBAC)
- Error handling and structured logging
- Testing strategies (unit, integration, e2e) with pytest
- Performance optimization (caching, rate limiting, async patterns)
- Background tasks and async queue patterns
- Configuration management with Pydantic Settings
- API versioning strategies
- OpenTelemetry monitoring and Prometheus metrics
- Code quality tools (Ruff, MyPy, pre-commit hooks)

## When to Use

Invoke this plugin when:

- Building or refactoring FastAPI REST APIs
- Implementing authentication and authorization
- Setting up database connections and migrations
- Testing async code
- Optimizing API performance
- Troubleshooting async issues, N+1 queries, or connection pool problems
- Establishing best practices for production deployments

Key triggers include: "FastAPI", "REST API in Python", "API endpoint", "add authentication", "database integration", "async SQLAlchemy", "Alembic migrations", "API testing", "rate limiting", or any production-grade FastAPI development.

## Reference Materials

### `skills/fastapi-expert.md`

Main skill documentation with when/why to use guidance and quick start examples.

### `references/fastapi-reference.md`

Comprehensive 14-section reference guide with:

- Complete, copy-paste-ready code examples for all major patterns
- Best practices for production deployments
- Common pitfalls and anti-patterns to avoid
- Quick reference commands
- Links to official documentation

**Key Sections:**

1. Project structure and layered architecture
2. Database setup (async SQLAlchemy, Alembic, connection pooling)
3. RESTful conventions (status codes, pagination, filtering)
4. Authentication (JWT/OAuth2, RBAC)
5. Error handling (custom exceptions, global handlers)
6. Testing (pytest, async fixtures, patterns)
7. Performance (caching, rate limiting, optimization)
8. Background tasks (BackgroundTasks vs Celery)
9. Configuration (Pydantic Settings, environment variables)
10. API versioning (sub-applications vs router prefixes)
11. Monitoring (OpenTelemetry, Prometheus, health checks)
12. OpenAPI documentation customization
13. Code quality (Ruff, MyPy, pre-commit)
14. Advanced topics (WebSockets, file uploads, middleware)

## Installation

Add to your project's `.claude/rules/plugins.json`:

```json
{
  "plugins": [
    {
      "name": "fastapi-expert",
      "enabled": true,
      "triggers": ["fastapi", "rest api", "async"]
    }
  ]
}
```

Or enable globally in `.claude/settings.json`:

```json
{
  "enabledPlugins": ["fastapi-expert"]
}
```

## Quick Start

When working on a FastAPI project:

1. Reference the **When to Use** section above to confirm this plugin applies
2. Consult `skills/fastapi-expert.md` for trigger-based guidance
3. Navigate to the relevant section in `references/fastapi-reference.md` using the table of contents
4. Copy and adapt code examples for your specific use case
5. Follow the established patterns for consistency across your codebase

## Maintainer

Jacob Waites

## Version

1.0.0

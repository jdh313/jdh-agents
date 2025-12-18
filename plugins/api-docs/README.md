# api-docs

OpenAPI documentation best practices for FastAPI, Django Ninja, and manual specs.

## Features

- **Skill**: Comprehensive OpenAPI best practices (naming conventions, schema reuse, error standardization)
- **Agent**: Proactive API code reviewer - activates when writing endpoints
- **Command**: `/api-docs:openapi-review` - explicit validation on demand

## Components

### Skill: openapi-best-practices

Core knowledge for writing high-quality OpenAPI documentation:

- Schema naming conventions (`{Model}{Operation}` pattern)
- Error response standardization (RFC 7807)
- DRY principles for API documentation
- Framework-specific guidance (FastAPI, Django Ninja, manual specs)

### Agent: openapi-reviewer

Proactively reviews API code as you write it:

- Detects naming inconsistencies
- Flags duplicated descriptions/schemas
- Suggests best practice improvements
- Configurable aggression levels: `strict`, `normal`, `minimal`

### Command: /api-docs:openapi-review

On-demand review of existing API code:

```
/api-docs:openapi-review [file|directory|project] [--level strict|normal|minimal]
```

## Best Practices Covered

### Schema Naming

| Pattern | Use Case | Example |
|---------|----------|---------|
| `{Model}Create` | Request body for creation | `UserCreate` |
| `{Model}Update` | Request body for updates | `UserUpdate` |
| `{Model}Read` | Response model | `UserRead` |
| `{Model}List` | Paginated list response | `UserList` |

### Error Responses

Follows RFC 7807 "Problem Details for HTTP APIs":

```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Not Found",
  "status": 404,
  "detail": "User with ID 123 was not found"
}
```

## Installation

Add via marketplace or install directly:

```bash
claude /plugin install api-docs
```

## License

MIT

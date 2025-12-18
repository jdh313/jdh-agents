---
description: Review API code for OpenAPI documentation best practices
argument-hint: "[file|directory] [--level strict|normal|minimal]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Task
---

# OpenAPI Review Command

Review API code for OpenAPI documentation best practices, checking naming conventions, error handling, and documentation completeness.

## Arguments

Parse the user's input for:

1. **Target** (optional): File path, directory, or "project" for entire codebase
   - Default: Current directory
   - Examples: `src/api/`, `routes.py`, `project`

2. **Level** (optional): Review strictness
   - `--level strict` - Flag all deviations
   - `--level normal` - Flag clear violations (default)
   - `--level minimal` - Only critical issues

## Execution Process

1. **Determine scope**:
   - If file specified: Review that file only
   - If directory specified: Find all Python files with API patterns
   - If "project" or no target: Search entire codebase for API files

2. **Detect framework**:
   - Look for `from fastapi import` → FastAPI
   - Look for `from ninja import` → Django Ninja
   - Look for `.yaml`/`.yml` with `openapi:` → Manual spec

3. **Find API files** using these patterns:
   ```
   # FastAPI
   @app.get, @app.post, @router.get, @router.post
   from fastapi import FastAPI, APIRouter

   # Django Ninja
   @api.get, @api.post, @router.get
   from ninja import NinjaAPI, Router

   # Manual specs
   openapi: 3.x, paths:, components:
   ```

4. **Load the openapi-best-practices skill** for review criteria

5. **Analyze each file** for:
   - Schema naming (`{Model}{Operation}` pattern)
   - Error response consistency (RFC 7807)
   - Documentation completeness
   - Duplicated descriptions/schemas
   - Missing response types

6. **Apply aggression level**:
   - **strict**: Report everything including style suggestions
   - **normal**: Report violations and important improvements
   - **minimal**: Only critical issues (missing docs, duplicates)

## Output Format

Present results as:

```markdown
## OpenAPI Review: [target]

**Framework:** FastAPI | Django Ninja | Manual | Mixed
**Level:** strict | normal | minimal
**Files Reviewed:** X

### Critical Issues (must fix)

#### [filename:line]
**Issue:** [Description]
**Current:**
```python
[problematic code]
```
**Suggested:**
```python
[fixed code]
```

### Improvements (recommended)

- **[filename:line]**: [Suggestion]

### Good Practices Found

- [Positive observation]

### Summary

[Brief assessment and priority recommendations]
```

## Examples

**Review single file:**
```
/api-docs:openapi-review src/api/users.py
```

**Review directory with strict checking:**
```
/api-docs:openapi-review src/api/ --level strict
```

**Review entire project:**
```
/api-docs:openapi-review project --level minimal
```

## Tips

- Start with `--level minimal` on legacy codebases
- Use `--level strict` for new code or before releases
- Review incrementally: fix critical issues first, then improvements
- The agent version (`openapi-reviewer`) runs proactively while coding

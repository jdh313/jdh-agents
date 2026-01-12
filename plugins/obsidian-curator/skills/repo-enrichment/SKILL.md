---
name: repo-enrichment
description: >
  Use Skill(obsidian-curator:repo-enrichment) when working on a known repository
  to suggest updates to its repo note. At session end or after significant work,
  checks if new patterns, gotchas, or learnings should be added to the repo's
  documentation in the vault.
allowed-tools:
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_append_content
  - mcp__CodeMCP__Obsidian__obsidian_patch_content
---

# Repo Enrichment

You help keep repository notes up-to-date by suggesting additions
based on work done during coding sessions.

## When to Activate

Suggest repo note updates when:

1. **Working on a known repo** — Identify if a repo note exists
2. **Discovering a pattern or gotcha** — Worth documenting
3. **Making architectural decisions** — Should be recorded
4. **Session ending** — Review what was learned

## Repo Note Detection

### Find Repo Note for Current Work

```python
# Search for repo note by name
obsidian_simple_search(query="Gateway Config API", context_length=100)

# Or check known location
obsidian_get_file_contents("80 Waites/Repos/Gateway Config API.md")
```

### Common Repo Note Locations

```
80 Waites/Repos/[Repo Name].md
80 Waites/Repos/[repo-name].md
80 Waites/Projects and Tasks/[Project Name].md
```

## What to Capture

### 1. Patterns & Best Practices

Code patterns that should be followed consistently:

```markdown
## Patterns & Gotchas

### Repository Pattern
- Use `ConfigRepository` for all database access
- Return domain objects, not ORM models
- Keep queries in repository, not in route handlers
```

### 2. Gotchas & Pitfalls

Things that bit you and might bite again:

```markdown
### Rate Limiting Gotcha
The API returns 429 with exponential backoff headers.
**Don't** use fixed retry intervals — parse `Retry-After` header.
```

### 3. Key Files & Entry Points

Important files discovered during work:

```markdown
## Key Files

| File | Purpose |
|------|---------|
| `src/api/routes/config.py` | Main config endpoints |
| `src/repositories/config.py` | Database access layer |
| `src/models/config.py` | Pydantic models |
```

### 4. Dependencies & Integrations

External services and how they're used:

```markdown
## Dependencies

- **PostgreSQL** — Main data store
- **Redis** — Caching layer for config lookups
- **SQS** — Event queue for config changes
```

### 5. Development Notes

Setup, testing, or deployment insights:

```markdown
## Development Notes

### Running Tests
```bash
PYTHONPATH=. pytest tests/ -v
```

### Environment Variables
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection (optional)
```

## How to Suggest

### Inline During Work

When you discover something notable:

```markdown
---
> 💡 **Repo note suggestion**
> Add to Gateway Config API.md → Patterns & Gotchas:
>
> "Rate limiting uses exponential backoff with Retry-After header"
>
> Add this? [Yes / Later / Skip]
---
```

### Batch at Session End

Collect discoveries and present together:

```markdown
## Repo Note Updates

During this session on **Gateway Config API**, I noticed:

| Section | Addition |
|---------|----------|
| Patterns | Repository pattern for config access |
| Gotchas | Rate limiting exponential backoff |
| Key Files | Added `src/repositories/config.py` |

Update the repo note with these? [All / Select / Skip]
```

## Update Format

### Appending to Existing Section

```python
obsidian_patch_content(
  filepath="80 Waites/Repos/Gateway Config API.md",
  operation="append",
  target_type="heading",
  target="Patterns & Gotchas",
  content="\n### Rate Limiting\nUse exponential backoff with Retry-After header.\n"
)
```

### Adding New Section

```python
obsidian_append_content(
  filepath="80 Waites/Repos/Gateway Config API.md",
  content="\n## Development Notes\n\n### Running Tests\n```bash\nPYTHONPATH=. pytest tests/\n```\n"
)
```

## Session End Integration

At session end, if working on a known repo:

```markdown
## Session Summary

Worked on: **Gateway Config API**

### Potential Repo Note Updates

1. **New pattern discovered:**
   Repository pattern with domain objects (src/repositories/)

2. **Gotcha found:**
   Rate limiting needs Retry-After header parsing

3. **Key file identified:**
   `src/api/middleware/rate_limit.py` — custom rate limiter

Add any of these to the repo note? (1-3, all, or skip)
```

## Repo Note Template

If no repo note exists, suggest creating one:

```markdown
---
date created: {{date}}
date_modified: {{date}}
github-url: https://github.com/waites/gateway-config-api
status: active
aliases: [gateway-api, config-api]
---

# Gateway Config API

## Overview
[Brief description of the repo's purpose]

## Key Files

| File | Purpose |
|------|---------|

## Patterns & Gotchas

### [Pattern Name]
[Description]

## Dependencies

## Development Notes

### Running Locally
```bash
# Setup commands
```

## Related
- [[Other Repo]]
- [[Project Note]]
```

## Remember

- **Be selective** — Only suggest genuinely useful additions
- **Match existing style** — Follow the repo note's current format
- **Avoid duplication** — Check if info already exists before suggesting
- **Batch suggestions** — Don't interrupt flow with every discovery
- **Ask permission** — Never modify repo notes without consent
- **Link appropriately** — Add [[wikilinks]] to related notes

## Common Patterns to Capture

| Type | Example | Section |
|------|---------|---------|
| Code pattern | "Use dataclasses for configs" | Patterns |
| Gotcha | "JSON dates need ISO format" | Gotchas |
| Debugging tip | "Enable debug logging with X" | Development Notes |
| Architecture | "Events flow through SQS" | Overview or Dependencies |
| Test strategy | "Mock external APIs with X" | Development Notes |
| Deployment | "Requires VPN for staging" | Development Notes |

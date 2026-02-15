# Freeform Commits Reference

This reference documents freeform commit message style — clear, descriptive messages without a rigid type-prefix structure.

## Format Structure

```
<summary>

[optional body]
```

**Key rules:**
- Summary is required, clear, and specific
- Imperative mood ("Add feature" not "Added feature")
- Capitalize the first word of the summary
- No trailing period on the summary line
- Body is optional, separated by blank line, maximum 5 lines

## Writing Good Summaries

The summary should immediately convey what the commit does. Be specific enough that someone scanning `git log --oneline` can understand the change without reading the diff.

**Good examples:**
```
Add user authentication endpoint
Fix memory leak in stats processor
Extract connection pool logic into separate module
Update dependencies to latest versions
Remove unused middleware from request pipeline
Simplify error handling in payment flow
```

**Bad examples:**
```
Update stuff                    # Too vague
fix                             # No context
Changes to auth                 # What changes?
WIP                             # Not a finished commit
Misc updates and fixes          # Multiple concerns, vague
```

## Summary Guidelines

### Imperative Mood

Write as if you're giving the codebase an instruction:
- "Add login endpoint" (not "Added" or "Adds" or "Adding")
- "Fix null pointer in parser" (not "Fixed" or "Fixes")
- "Remove deprecated API calls" (not "Removed" or "Removing")

### Be Specific

The summary should answer: "If I apply this commit, it will..."
- "Fix race condition in message processing" (not "Fix bug")
- "Add rate limiting to API endpoints" (not "Add feature")
- "Update Python to 3.13" (not "Update dependencies")

### Capitalization

Capitalize the first word of the summary. This is the primary visual difference from conventional commits:
- "Add user authentication" (freeform)
- "feat: add user authentication" (conventional)

## Commit Body Guidelines

Use the optional body when:
- The change requires additional context or explanation
- The motivation isn't obvious from the summary alone
- There are important technical details or side effects
- The change affects multiple areas

**Body formatting:**
- Separate from summary with one blank line
- Use imperative mood like the summary
- Keep to maximum 5 lines
- Focus on WHY, not WHAT (the diff shows what changed)

**Example with body:**
```
Fix race condition in message processing

Add mutex locking around message ID insertion to prevent
duplicate processing when multiple Lambda instances handle
messages with the same UUID concurrently. This resolves
intermittent duplicate stat entries in the database.
```

**Example without body (self-explanatory change):**
```
Remove unused imports from auth module
```

## Common Patterns

| Change Type | Example Summary |
|-------------|-----------------|
| New feature | `Add password reset flow` |
| Bug fix | `Fix timezone handling in date parser` |
| Refactor | `Extract database connection logic` |
| Performance | `Optimize query for large datasets` |
| Documentation | `Update API usage examples in README` |
| Tests | `Add unit tests for protobuf processor` |
| Dependencies | `Update React to v19` |
| Configuration | `Configure ESLint rules for new modules` |
| Cleanup | `Remove deprecated helper functions` |

## Anti-Patterns to Avoid

**Don't:**
- End summary with a period: `Add login.`
- Use past tense: `Fixed the bug`
- Write vague summaries: `Updates` or `Fix stuff`
- Start with lowercase (that's conventional style): `add login`
- Include issue numbers in summary: `#123 resolve bug`
- Exceed 5 lines in body
- Repeat WHAT in the body (the diff shows what)

**Do:**
- Keep summary concise and descriptive
- Use imperative mood consistently
- Be specific about what changed
- Use body for context when needed

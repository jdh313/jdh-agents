# Conventional Commits Reference

This reference documents the Angular/Conventional Commits format for writing clear, structured commit messages.

## Format Structure

```
<type>: <summary>

[optional body]
```

**Key rules:**
- Type is required, lowercase, no scope
- Summary is required, lowercase, no period at end
- Body is optional, maximum 5 lines, separated by blank line from summary
- Summary should be imperative mood ("add feature" not "added feature")

## Standard Types

### feat
New features or functionality added to the codebase.

**Examples:**
```
feat: add user authentication
feat: implement password reset flow
```

### fix
Bug fixes or corrections to existing functionality.

**Examples:**
```
fix: resolve memory leak in stats processor
fix: correct timezone handling in date parser
fix: prevent duplicate message processing
```

### chore
Maintenance tasks, dependency updates, configuration changes.

**Examples:**
```
chore: update dependencies to latest versions
chore: configure eslint rules
chore: add .gitignore entries
```

### docs
Documentation changes only (README, comments, guides).

**Examples:**
```
docs: add API usage examples to README
docs: update installation instructions
docs: clarify environment variable descriptions
```

### style
Code style changes that don't affect functionality (formatting, whitespace, semicolons).

**Examples:**
```
style: format code with prettier
style: fix indentation in handler functions
```

### refactor
Code restructuring without changing external behavior.

**Examples:**
```
refactor: extract database connection logic
refactor: simplify error handling flow
refactor: rename variables for clarity
```

### perf
Performance improvements.

**Examples:**
```
perf: optimize database query for large datasets
perf: add caching layer for frequent requests
```

### test
Adding or updating tests.

**Examples:**
```
test: add unit tests for protobuf processor
test: update integration tests for new endpoint
```

### build
Changes to build system, dependencies, or tooling.

**Examples:**
```
build: configure webpack for production builds
build: add SAM build configuration
```

### ci
Changes to CI/CD configuration and scripts.

**Examples:**
```
ci: add automated testing workflow
ci: configure deployment pipeline
```

### revert
Reverting a previous commit.

**Examples:**
```
revert: revert "feat: add experimental feature"
```

## Commit Body Guidelines

Use the optional body when:
- The change requires additional context or explanation
- The summary alone doesn't fully capture the motivation
- There are important technical details or side effects
- The change affects multiple areas

**Body formatting:**
- Separate from summary with one blank line
- Use imperative mood like the summary
- Keep to maximum 5 lines
- Focus on WHY, not WHAT (the diff shows what changed)

**Example with body:**
```
fix: prevent race condition in message processing

Add mutex locking around message ID insertion to prevent
duplicate processing when multiple Lambda instances handle
messages with the same UUID concurrently. This resolves
intermittent duplicate stat entries in the database.
```

## Type Selection Guide

When choosing a type:
1. **feat** - Does it add new capability for users?
2. **fix** - Does it correct incorrect behavior?
3. **refactor** - Does it restructure without changing behavior?
4. **perf** - Does it specifically improve performance?
5. **docs** - Is it only documentation?
6. **test** - Is it only test code?
7. **chore** - Everything else (configs, dependencies, tooling)

**Common patterns:**
- Adding new API endpoint -> `feat`
- Fixing broken endpoint -> `fix`
- Reorganizing endpoint code -> `refactor`
- Updating README -> `docs`
- Updating dependencies -> `chore`
- Adding endpoint tests -> `test`

## House Style

- **`Co-Authored-By:` footers follow the detected policy** (see `detection.md`). Default: strip — the commit describes the change, the VCS records authorship. Keep when CLAUDE.md mandates it or repo history consistently carries it.
- No trailing period on the summary line.
- **Issue refs follow the detected placement** (see `detection.md`). Default: out of the summary, in the PR description. Keep `(TEAM-123)`/`#123` in the summary when CLAUDE.md declares `Issue refs: summary` or history consistently uses it (e.g. a Linear/Jira integration keys off the subject).

## Anti-Patterns to Avoid

**Don't:**
- End summary with period: `feat: add login.`
- Use past tense: `fix: fixed the bug`
- Use capital letters: `Feat: Add Login`
- Include issue numbers in summary: `fix: #123 resolve bug` — *unless the repo convention is `summary` (see House Style)*
- Write vague summaries: `fix: bug fix` or `chore: updates`
- Exceed 5 lines in body
- Append `Co-Authored-By:` footers — *unless the policy is `keep` (see House Style)*

**Do:**
- Keep summary concise and descriptive: `feat: add login`
- Use imperative mood: `fix: resolve memory leak`
- Be specific: `fix: prevent null pointer in stats processor`
- Use body for context when needed

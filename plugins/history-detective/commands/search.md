---
description: Search commit messages and code changes with filters for author, date, and path
argument-hint: <pattern> [--author=<name>] [--since=<date>] [--path=<path>]
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash([[:*)
  - Bash(if:*)
  - Read
---

# Search Commit History

Search and filter commit history by message, code changes, author, date, and file path.

## VCS Detection

Automatically detect the version control system:

```bash
VCS=$([[ -d .jj ]] && echo "jj" || echo "git")
echo "Using: $VCS"
```

## Search Commit Messages

### Git

Search commit messages for a keyword or pattern:

```bash
git log --grep="<pattern>"
```

Example: Find all commits with "bug" in the message:

```bash
git log --grep="bug"
```

### Jj

Search commit descriptions:

```bash
jj log -r 'description(keyword)'
```

Example:

```bash
jj log -r 'description(bug)'
```

## Search Code Changes (Pickaxe)

Find commits that added or removed specific code.

### Git: Literal String Search

Search for commits where a specific string was added or removed:

```bash
git log -S "<code>"
```

Example: Find when `TODO: refactor` was added/removed:

```bash
git log -S "TODO: refactor"
```

### Git: Regex Pattern Search

Search using regular expressions:

```bash
git log -G "<regex>"
```

Example: Find commits changing any occurrence of `const\s+\w+`:

```bash
git log -G "const\s+\w+"
```

### Jj

Jj does not have direct pickaxe equivalents. Use `jj diff` with revsets to inspect changes:

```bash
jj diff -r '<revset>'
```

## Filter by Author

### Git

Find commits by a specific author:

```bash
git log --author="<name>"
```

Example:

```bash
git log --author="Jane Doe"
```

### Jj

Filter by author using revsets:

```bash
jj log -r 'author(name)'
```

Example:

```bash
jj log -r 'author("Jane Doe")'
```

## Filter by Date Range

### Git

Filter commits within a date range:

```bash
git log --since="2024-01-01" --until="2024-12-31"
```

Relative dates are also supported:

```bash
git log --since="1 month ago" --until="1 week ago"
```

### Jj

Filter using revsets with date conditions:

```bash
jj log -r 'committer_date(after:"2024-01-01") & committer_date(before:"2024-12-31")'
```

Example with relative dates (using ISO 8601):

```bash
jj log -r 'committer_date(after:"2024-01-01")'
```

## Filter by File Path

### Git

Show commits affecting a specific file or directory:

```bash
git log -- <path>
```

Example: Commits affecting `src/auth.js`:

```bash
git log -- src/auth.js
```

Example: Commits affecting the `src/` directory:

```bash
git log -- src/
```

### Jj

Show commits affecting a path:

```bash
jj log <path>
```

Example:

```bash
jj log src/auth.js
```

## Combined Filters

Apply multiple filters together.

### Git

Combine author, date, message, and path filters:

```bash
git log --author="Jane" --since="1 month ago" --grep="fix" -- src/
```

This finds commits:
- By author Jane
- In the last month
- With "fix" in the message
- Affecting files in `src/`

Other combinations:

```bash
# Commits by a user with code changes in a file
git log --author="Bob" -S "error handling" -- src/errors.js

# Commits matching a pattern, excluding certain paths
git log --grep="feature" -- src/ ':!src/tests/'
```

### Jj

Combine filters using revset operators: `&` (and), `|` (or):

```bash
jj log -r 'author("Jane") & description(fix) & committer_date(after:"2024-01-01")'
```

Example with path:

```bash
jj log -r 'author("Jane") & description(fix)' src/
```

## Output Formatting

### Git

Format output for readability:

```bash
# Oneline format
git log --oneline --grep="bug"

# Custom format
git log --format="%h %an %ad %s" --date=short --grep="feature"

# With diff summary
git log --author="Jane" --stat
```

### Jj

Format output using templates:

```bash
# Default format
jj log -r 'author("Jane")'

# Custom template
jj log -r 'author("Jane")' -T 'change_id.short() ++ " - " ++ description.first_line()'

# With commit info
jj log -r 'description(fix)' -T 'commit_id.short() ++ " " ++ author ++ " - " ++ description.first_line()'
```

## Examples

### Example 1: Find All Bug Fixes in the Last Month

Git:
```bash
git log --since="1 month ago" --grep="fix"
```

Jj:
```bash
jj log -r 'description(fix) & committer_date(after:"1 month ago")'
```

### Example 2: Search Code Changes by Multiple Authors

Git:
```bash
git log -S "api_key" --author="Alice\|Bob"
```

Jj:
```bash
jj log -r 'author("Alice") | author("Bob")' -T 'change_id.short() ++ " " ++ author ++ " - " ++ description.first_line()'
```

### Example 3: Commits Affecting a Feature in a Date Range

Git:
```bash
git log --since="2024-06-01" --until="2024-06-30" --grep="auth" -- src/auth/
```

Jj:
```bash
jj log -r 'committer_date(after:"2024-06-01") & committer_date(before:"2024-06-30")' src/auth/
```

### Example 4: Find Who Last Modified a File

Git:
```bash
git log -1 --format="%an %ae" -- src/config.js
```

Jj:
```bash
jj log --limit 1 -T 'author.name() ++ " - " ++ description.first_line()' src/config.js
```

## Tips

- **Case-insensitive search:** Use `-i` flag with git grep commands
- **Extended regex:** Use `-E` with git for extended regex patterns
- **All branches:** Add `--all` to search across all branches
- **Exclude merges:** Use `--no-merges` to skip merge commits
- **Limit results:** Use `-n <number>` to limit output (e.g., `git log -10`)

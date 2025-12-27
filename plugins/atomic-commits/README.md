# Atomic Commits Plugin

Create atomic commits with conventional commit messages. Supports both git and jj (Jujutsu).

## Features

- **Atomic commit guidance**: Split changes into logical, reversible units
- **Conventional commits**: Angular-style commit messages (feat, fix, chore, etc.)
- **Dual VCS support**: Works with both git and jj
- **Immediate VCS detection**: Commands use `!` backticks for guaranteed detection
- **Auto-invocation**: Skill triggers on any commit-related request

## Installation

```bash
claude plugin install /path/to/atomic-commits
# or from marketplace
claude plugin install atomic-commits
```

## Usage

### Explicit Commands

Use slash commands for deterministic behavior with immediate VCS detection:

```
/atomic-commits:commit    # Create a single atomic commit
/atomic-commits:split     # Split changes into multiple atomic commits
/atomic-commits:review    # Review/improve a commit message
```

### Auto-Invocation

The skill automatically triggers on commit-related requests:

- "commit these changes"
- "write a commit message"
- "split this into atomic commits"
- "review my commit message"
- "help me commit"

## Commands

### `/atomic-commits:commit`

Create a single atomic commit for current changes.

**Behavior:**
1. Immediately detects VCS (git or jj)
2. Shows current status and diff
3. Analyzes if changes are atomic
4. Composes conventional commit message
5. Executes the commit
6. Verifies result

### `/atomic-commits:split`

Split changes into multiple atomic commits.

**Behavior:**
1. Detects VCS and shows all changes
2. Analyzes and identifies atomic units
3. Presents recommended split with reasoning
4. Creates commits one by one
5. Verifies clean state

### `/atomic-commits:review [message]`

Review and improve a commit message.

**Example:**
```
/atomic-commits:review "fixed the bug in login"
```

**Behavior:**
1. Analyzes message against conventional commits standards
2. Checks format, type appropriateness, imperative mood
3. Provides improved version with explanations
4. Optionally commits with improved message

## Commit Message Format

```
<type>: <summary>

[optional body - max 5 lines]
```

**Types:** feat, fix, chore, docs, style, refactor, perf, test, build, ci, revert

**Examples:**
```
feat: add user authentication endpoint
fix: prevent race condition in message processing
refactor: extract database connection logic
```

## VCS Support

### Git
- Uses `git add` for staging
- Uses `git commit` for committing
- Uses `git add -p` for partial staging

### Jujutsu (jj)
- Uses `jj describe` to set commit message
- Uses `jj split` to separate changes
- Uses `jj new` to start fresh working copy

## References

The plugin includes reference documentation:

- `references/conventional-commits.md` - Message format specification
- `references/git-workflow.md` - Git-specific commands
- `references/jj-workflow.md` - Jujutsu-specific commands

## License

MIT

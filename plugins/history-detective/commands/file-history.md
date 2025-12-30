---
description: Trace file evolution and line-by-line blame for understanding code history
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# File History Command

Trace file evolution and perform line-by-line blame analysis to understand when and why code changed. Supports both Git and Jujutsu (jj) version control systems.

## Quick Start

```bash
# Detect VCS
VCS=$([[ -d .jj ]] && echo "jj" || echo "git")
echo "Using VCS: $VCS"

# Get file history
# For Git: git log --follow -- <file>
# For Jj: jj log <file>

# Get blame information
# For Git: git blame <file>
# For Jj: jj file annotate <file>
```

## File History

View the complete history of changes to a file, including commit messages and authors.

### Git

```bash
# Full history with follow (tracks file renames)
git log --follow -- src/auth.py

# With patch output (shows what changed)
git log --follow -p -- src/auth.py

# With abbreviated output
git log --follow --oneline -- src/auth.py

# Show only specific number of commits
git log --follow -n 10 -- src/auth.py

# With formatted output (author, date, message)
git log --follow --format="%h %an %ad %s" --date=short -- src/auth.py
```

### Jujutsu

```bash
# File evolution log
jj log src/auth.py

# With verbose template showing change IDs and descriptions
jj log -T 'change_id.short() ++ " - " ++ description.first_line()' src/auth.py

# Show which commits affected a file
jj log --grep='src/auth.py' -T 'change_id.short() ++ " - " ++ description.first_line()'
```

## Blame / Annotate

View line-by-line blame information to see who changed each line and when.

### Git

```bash
# Full blame output
git blame src/auth.py

# Blame for specific line range
git blame -L 42,65 src/auth.py

# Ignore whitespace-only changes
git blame -w src/auth.py

# Show commit hash, author, and date only
git blame --line-porcelain src/auth.py

# Blame with original file (before merge)
git blame -C src/auth.py

# View blame with shortened output
git blame -L 1,20 --abbrev=8 src/auth.py
```

### Jujutsu

```bash
# Annotate with change information
jj file annotate src/auth.py

# Annotate specific file at current revision
jj file annotate --at-op src/auth.py

# View annotation with template (change ID and description)
jj file annotate -T 'change_id.short() ++ " | " ++ author.name()' src/auth.py
```

## View File at Specific Point

Retrieve the content of a file at a specific commit or revision.

### Git

```bash
# View file at specific commit
git show abc1234:src/auth.py

# View file from N commits ago (relative reference)
git show HEAD~3:src/auth.py

# View file at tag
git show v1.2.0:src/auth.py

# Compare file across commits
git show abc1234:src/auth.py > /tmp/old.py
git show def5678:src/auth.py > /tmp/new.py
diff /tmp/old.py /tmp/new.py
```

### Jujutsu

```bash
# View file at specific revision
jj cat -r <change-id> src/auth.py

# View file at parent revision
jj cat -r '@-' src/auth.py

# View file at specific operation
jj cat -r 'heads() & stable' src/auth.py

# Compare file content across revisions
jj cat -r abc123 src/auth.py > /tmp/old.py
jj cat -r def456 src/auth.py > /tmp/new.py
diff /tmp/old.py /tmp/new.py
```

## Evolution Log (Jujutsu Only)

Track the complete evolution of a specific change, including all rewrites and amendments.

```bash
# View all versions of a change
jj evolog <change-id>

# With detailed template
jj evolog -T 'self.change_id().short() ++ " at " ++ self.commit_id().short()' <change-id>

# Show evolution of current change
jj evolog @
```

## Common Workflows

### Find When a Line Was Added

**Git:**
```bash
# Get blame for the file
git blame src/auth.py | grep "the line content"

# Then view that commit
git show <commit-hash>
```

**Jujutsu:**
```bash
# Annotate to find the change
jj file annotate src/auth.py | grep "the line content"

# View the change
jj show <change-id>
```

### Track a Function Through History

**Git:**
```bash
# Blame specific function lines
git blame -L /^def authenticate/,/^def [^_]/ src/auth.py

# View history of function (with context)
git log --follow -p -S "def authenticate" -- src/auth.py
```

**Jujutsu:**
```bash
# Search for function in history
jj log -S "def authenticate" src/auth.py

# View the evolution of that function
jj log -T 'change_id.short() ++ " - " ++ description.first_line()' -S "def authenticate"
```

### Compare Versions Before/After Refactor

**Git:**
```bash
# Get commit hashes for before and after
git log --oneline --follow -- src/auth.py | head -20

# View diff between two commits
git diff abc1234 def5678 -- src/auth.py

# View file at each point
git show abc1234:src/auth.py
git show def5678:src/auth.py
```

**Jujutsu:**
```bash
# View change evolution
jj evolog <change-id>

# Compare revisions
jj diff -r <revision1> <revision2> src/auth.py

# View file at specific point
jj cat -r <change-id> src/auth.py
```

## Advanced Options

### Git Advanced

```bash
# Show statistics for file changes
git log --stat -- src/auth.py

# Show file changes by author
git log --format="%an" --follow -- src/auth.py | sort | uniq -c | sort -rn

# Blame only commits after specific date
git blame --since="2024-01-01" src/auth.py

# Show blame with copy detection
git blame -C -C src/auth.py

# Interactive blame (requires git 2.40+)
git blame -L 1,50 --porcelain src/auth.py
```

### Jujutsu Advanced

```bash
# Search file history with grep
jj log src/auth.py | jj log --grep="pattern"

# View file at specific operation ID
jj cat -r <op-id>@<index> src/auth.py

# Compare file across branches
jj cat -r main: src/auth.py > /tmp/main.py
jj cat -r feature: src/auth.py > /tmp/feature.py
diff /tmp/main.py /tmp/feature.py

# Show all changes that touched specific lines
jj log -p src/auth.py | grep -A5 -B5 "line pattern"
```

## Tips & Tricks

1. **Use `--follow` in Git** to track file renames when viewing history
2. **Combine blame with grep** to find patterns and their authors
3. **Use `git show` / `jj cat`** to view the exact content at any point
4. **For Jjustsu, use change IDs** instead of commit hashes—they persist through rewrites
5. **Blame is most useful with `-L`** to focus on specific line ranges
6. **Use `jj file annotate`** in Jujutsu for the equivalent of `git blame`
7. **Check `jj evolog`** to see the full edit history of a change in Jujutsu

## See Also

- `git log` — Full documentation
- `git blame` — Detailed blame options
- `jj log` — Jujutsu logging
- `jj file annotate` — Jujutsu blame equivalent
- `jj cat` — View file content at revisions
- `jj evolog` — Track change evolution

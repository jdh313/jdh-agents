---
description: Identify frequently changed files, code churn, and contributor patterns
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Code Evolution Hotspots & Analysis

Detect frequently changed files, code churn patterns, and contributor activity to identify areas of instability, active development, or maintenance burden.

## Quick Reference

| Task | Git | Jj |
|------|-----|-----|
| Find most-changed files | `git log --name-only --pretty=format: \| sort \| uniq -c \| sort -rn \| head -20` | `jj log --name-status -T ''` |
| Code churn in path | `git log --numstat --pretty=format: -- <path>` | `jj log --stat -- <path>` |
| Contributors to file | `git shortlog -sn -- <path>` | `jj log -T 'author.name()' -- <path>` |
| Commit frequency | `git log --format='%ad' --date=format:'%Y-%W'` | `jj log -T 'commit_time.utc().strftime("%Y-%W")'` |
| Evolution chain | `git log --oneline <path>` | `jj evolog <change-id>` |

## Recipes

### 1. Detect Hot Spots (Most Frequently Changed Files)

#### Git Version

```bash
# List files by change frequency (top 20)
git log --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20
```

**Output:**
```
    145 src/api/handlers.py
    132 tests/integration/test_api.py
    118 docs/api-guide.md
     95 src/core/auth.py
     ...
```

**Interpretation:**
- High frequency = active development, active bugs, or refactoring
- Correlate with commit messages to understand if churn is feature work or stabilization
- Files appearing together often suggest coupling

**Extended analysis:**
```bash
# Top 30 with full paths
git log --name-only --pretty=format: | sort | uniq -c | sort -rn | head -30

# Group by directory (first-level)
git log --name-only --pretty=format: | sed 's|/.*||' | sort | uniq -c | sort -rn | head -20

# Exclude tests and docs
git log --name-only --pretty=format: | grep -v '^test' | grep -v '^docs' | sort | uniq -c | sort -rn | head -20
```

#### Jj Version

```bash
# List files by change frequency (requires parsing commit log)
jj log --name-status -T 'change_id.short() ++ ": " ++ description.first_line()' | \
  awk '{for(i=2;i<=NF;i++) print $i}' | sort | uniq -c | sort -rn | head -20
```

**Note:** Jj's name-status output format differs from git. For detailed file analysis, combine with file pattern filtering.

### 2. Analyze Code Churn (Added vs. Deleted Lines)

#### Git Version

```bash
# Overall churn across entire repository
git log --numstat --pretty=format: | awk 'NF==3 {add+=$1; del+=$2} END {print "Added:", add, "Deleted:", del, "Net:", add-del}'
```

**Output:**
```
Added: 15432 Deleted: 8921 Net: 6511
```

**Churn in specific path:**
```bash
# Replace <path> with file or directory (e.g., "src/api")
git log --numstat --pretty=format: -- <path> | awk 'NF==3 {add+=$1; del+=$2} END {print "Path:", "<path>", "Added:", add, "Deleted:", del, "Net:", add-del}'
```

**Churn by file type:**
```bash
# All .py files
git log --numstat --pretty=format: -- '*.py' | awk 'NF==3 {add+=$1; del+=$2} END {print "Python files - Added:", add, "Deleted:", del}'

# All test files
git log --numstat --pretty=format: -- 'test*.py' | awk 'NF==3 {add+=$1; del+=$2} END {print "Tests - Added:", add, "Deleted:", del}'
```

**High churn files (potential refactoring candidates):**
```bash
# Files with most churn (deletions + additions, not net)
git log --numstat --pretty=format: | awk 'NF==3 {total=$1+$2; print total, $3}' | sort -rn | head -20
```

#### Jj Version

```bash
# Code churn in specific path
jj log --stat -- <path> | grep -E '^\s+[0-9]+ files? changed'
```

**Alternative (extract added/deleted):**
```bash
# Detailed stat summary (requires parsing)
jj log --stat -- <path>
```

**Note:** Jj's `--stat` format matches git's numstat. For per-file analysis, filter output accordingly.

### 3. Contributor Analysis (Who Changes What)

#### Git Version

```bash
# Top contributors to specific file/path
git shortlog -sn -- <path>
```

**Output:**
```
   45  Alice Smith
   32  Bob Johnson
   18  Carol Davis
```

**Example: Contributors to auth module**
```bash
git shortlog -sn -- src/core/auth.py
```

**Contributors with email:**
```bash
git shortlog -sen -- <path>
```

**Contributors over time (by date):**
```bash
git log --format='%an | %ad' --date=short -- <path> | sort | uniq -c | sort -rn | head -20
```

**Who modified specific lines:**
```bash
# Show blame for file (line-by-line attribution)
git blame <path> | head -20
```

**Most active contributor in last 3 months:**
```bash
git log --since="3 months ago" --format='%an' -- <path> | sort | uniq -c | sort -rn | head -10
```

#### Jj Version

```bash
# Contributors to path (requires log parsing)
jj log -T 'author.name() ++ "\n"' -- <path> | sort | uniq -c | sort -rn

# With email
jj log -T 'author.email() ++ " - " ++ author.name() ++ "\n"' -- <path> | sort | uniq -c | sort -rn
```

**Interpretation:**
- Uneven distribution = knowledge silos (risk if contributor leaves)
- Single contributor = bus factor of 1 (critical path dependency)
- Multiple contributors = healthier code ownership, distributed knowledge

### 4. Commit Frequency & Cadence

#### Git Version

```bash
# Commits per week (last 52 weeks)
git log --format='%ad' --date=format:'%Y-%W' | sort | uniq -c
```

**Output:**
```
  12 2025-50
  15 2025-49
   8 2025-48
   ...
```

**Total commits by date range:**
```bash
# Last 30 days
git log --since="30 days ago" --format='%ad' --date=format:'%Y-%m-%d' | sort | uniq -c | sort -rn

# By month (full year)
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
```

**Peak activity (day of week):**
```bash
# Commits by day of week (0=Sunday, 6=Saturday)
git log --format='%ad' --date=format:'%w' | sort | uniq -c
# Requires manual interpretation: 0=Sun, 1=Mon, ..., 6=Sat
```

**Activity heatmap (hour of day):**
```bash
git log --format='%ad' --date=format:'%H' | sort | uniq -c | sort -n
```

#### Jj Version

```bash
# Commits per week
jj log --no-graph -T 'committer.timestamp().format("%Y-%W") ++ "\n"' | sort | uniq -c

# By month
jj log --no-graph -T 'committer.timestamp().format("%Y-%m") ++ "\n"' | sort | uniq -c
```

**Interpretation:**
- Declining frequency = maintenance mode or project stalled
- Spiky frequency = burst-driven development (sprints, deadlines)
- Steady frequency = healthy continuous development

### 5. Evolution Chains & History Inspection

#### Git Version

```bash
# Linear history of single file
git log --oneline <path> | head -20

# Full diff history for file
git log -p <path> | head -100

# When was this line added/changed?
git blame -L <start>,<end> <path>

# When did function/feature get introduced?
git log -S 'function_name' --oneline -- <path>

# Show commits touching multiple files together
git log --name-only --format='%h %ad %s' --date=short -- <path1> <path2>
```

**Example: Trace evolution of API endpoint**
```bash
# Show all commits touching handlers.py
git log --oneline -- src/api/handlers.py | head -20

# Show detailed changes
git log -p --follow -- src/api/handlers.py | head -200
```

#### Jj Version

```bash
# Evolution of change (requires change ID)
jj evolog <change-id>

# Linear history of file
jj log --oneline -- <path>

# Full commit log with template
jj log -T 'change_id.short() ++ " - " ++ description.first_line() ++ "\n"' -- <path>

# Find commit introducing specific code
jj log -S 'search_term' -- <path>

# Show relations between changes
jj log --graph -T 'change_id.short()' -- <path>
```

**Example: Inspect evolution of specific change**
```bash
# Get the change ID first
jj log -T 'change_id.short() ++ " - " ++ description.first_line()' | head -1
# Output: abc1234def - Fix auth flow

# Then inspect its evolution
jj evolog abc1234def
```

**Correct Jj Template Syntax (CRITICAL):**
- Use `author.name()` NOT `author` (requires function call)
- Use `change_id.short()` NOT `change_id` (requires function call)
- Use `.strftime()` for date formatting NOT string interpolation
- Example: `jj log -T 'author.name() ++ " - " ++ change_id.short()'`

### 6. Stability & Risk Assessment

#### Identify High-Risk Files

```bash
# Combine frequency + churn for risk score
# High frequency + high churn = unstable (actively refactored or buggy)
git log --numstat --pretty=format: | \
  awk 'NF==3 {churn=$1+$2; files[$3]+=churn; count[$3]++} \
  END {for (f in files) print count[f], files[f], f}' | \
  sort -rn | head -20
```

**Output interpretation:**
```
 145 2843 src/api/handlers.py          <- 145 commits, 2843 total churn
 132 1956 tests/integration/test_api.py
  95 1543 src/core/auth.py
```

**Action items:**
- High frequency + high churn = candidate for refactoring or testing investment
- High frequency + low churn = stable, frequently used (good pattern)
- Low frequency + high churn = recently rewritten (monitor for stability)

#### Test Coverage & Stability Correlation

```bash
# Find test-to-source ratio
echo "Source files:"; git log --name-only --pretty=format: -- 'src/**/*.py' | sort -u | wc -l
echo "Test files:"; git log --name-only --pretty=format: -- 'test*.py' | sort -u | wc -l

# Files with low test coverage (changed rarely in tests, frequently in source)
git log --name-only --pretty=format: -- 'src/**/*.py' | sort | uniq -c > /tmp/src_changes.txt
git log --name-only --pretty=format: -- 'test*.py' | sort | uniq -c > /tmp/test_changes.txt
```

### 7. Coupling & Dependency Analysis

```bash
# Files often changed together (strong coupling indicator)
git log --name-only --pretty=format:%H | \
  awk '{if (NF>1) for(i=1;i<=NF;i++) for(j=i+1;j<=NF;j++) print $i, $j}' | \
  sort | uniq -c | sort -rn | head -20
```

**Example output:**
```
  23 src/api/handlers.py src/core/auth.py
  18 src/api/handlers.py tests/integration/test_api.py
  15 src/db/models.py src/db/migrations.py
```

**Interpretation:**
- Files changed together frequently = high coupling
- May indicate shared responsibility or architectural smell
- Consider refactoring or improving separation of concerns

## Workflow Examples

### Find Files Causing Most Merge Conflicts

```bash
# Proxy: files changed in many commits close together
git log --all --pretty=format: --name-only | sort | uniq -c | sort -rn | head -10
```

### Monitor Team Activity (Last Week)

```bash
# Commits by author (last 7 days)
git log --since="7 days ago" --format='%an' | sort | uniq -c | sort -rn

# Files touched (last 7 days)
git log --since="7 days ago" --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20
```

### Pre-Deployment Risk Check

```bash
# Changes in current branch compared to main
git log main..HEAD --name-only --pretty=format: | sort | uniq -c | sort -rn

# Churn analysis for branch changes
git log main..HEAD --numstat --pretty=format: | awk 'NF==3 {add+=$1; del+=$2} END {print "Branch churn - Added:", add, "Deleted:", del}'
```

### Identify Dead Code & Obsolete Files

```bash
# Files not changed in 2 years
cutoff_date=$(date -d "2 years ago" +%Y-%m-%d)
git log --before="$cutoff_date" --name-only --pretty=format: | sort -u > /tmp/old_files.txt
git log --name-only --pretty=format: | sort -u > /tmp/all_files.txt
comm -23 /tmp/old_files.txt /tmp/all_files.txt
```

## Notes

- **VCS Detection:** Use `[[ -d .jj ]] && echo "jj" || echo "git"` to determine repo type
- **Jj Template Syntax:** Always use function call syntax (e.g., `author.name()`, not `author`)
- **Large Repositories:** Use `--since` to limit history (e.g., `--since="1 year ago"`)
- **Performance:** Avoid piping git log output multiple times; combine with awk when possible
- **Interpretation:** High churn doesn't always mean problems—active development is healthy; correlate with test coverage and commit messages

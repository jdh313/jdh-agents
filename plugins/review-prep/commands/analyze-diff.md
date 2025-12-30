---
description: Comprehensive diff analysis with risk detection and impact metrics for code review
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash([[:*)
  - Bash(if:*)
  - Read
---

# Analyze Diff

Generate a comprehensive diff analysis report showing all changes, risk indicators, and impact metrics for code review preparation.

## Immediate Execution

**VCS Detection:**
!`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS, this command will analyze all changes and generate a structured report with risk detection and impact metrics.

### Step 1: Detect Base Branch (Git Only)

**For git:**

Determine the base branch for comparison:

```bash
# Try to detect main branch
if git show-ref --verify --quiet refs/heads/main; then
  echo "main"
elif git show-ref --verify --quiet refs/heads/master; then
  echo "master"
elif git show-ref --verify --quiet refs/heads/develop; then
  echo "develop"
else
  echo "HEAD~1"
fi
```

Store the detected base branch for use in subsequent commands. If none of the common branches exist, fall back to comparing against the previous commit.

**For jj:**

jj compares against the parent change automatically, so no base detection is needed.

### Step 2: Collect File Change Summary

**For git:**

Get comprehensive file status including renames:

```bash
# Get all changes from base branch to current HEAD
git diff --name-status --find-renames <base-branch>..HEAD

# Also check for unstaged changes in working directory
git diff --name-status

# And staged changes
git diff --name-status --staged
```

The output uses status codes:
- `A` = Added (new file)
- `M` = Modified
- `D` = Deleted
- `R###` = Renamed (### shows similarity percentage)
- `C###` = Copied

**For jj:**

Get summary of all changes in current change:

```bash
# Get file change summary with status
jj diff --summary

# Get just file names for processing
jj diff --name-only
```

### Step 3: Calculate Impact Metrics

**For git:**

Calculate comprehensive statistics:

```bash
# Overall statistics (files changed, insertions, deletions)
git diff --shortstat <base-branch>..HEAD

# Include working directory changes
git diff --shortstat

# Include staged changes
git diff --shortstat --staged

# Detailed per-file statistics
git diff --stat <base-branch>..HEAD
```

The `--stat` output shows:
```
path/to/file.py | 150 ++++++++++++++++++++++++++---
```
Where `150` is the total lines changed.

**For jj:**

Calculate statistics for current change:

```bash
# Get detailed statistics
jj diff --stat

# Get change summary
jj diff --summary
```

### Step 4: Risk Detection

Analyze changed files for risk indicators. Process the file list from Step 2 and categorize files:

**Risk Categories:**

1. **Configuration Files** (High Risk):
   - Pattern: `*.json`, `*.yaml`, `*.yml`, `*.toml`, `*.env*`, `*.config.*`, `*.ini`, `.properties`
   - Examples: `settings.yaml`, `.env.production`, `app.config.js`

2. **Dependency Files** (High Risk):
   - Exact matches: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - Exact matches: `requirements.txt`, `Pipfile`, `Pipfile.lock`, `pyproject.toml`, `poetry.lock`
   - Exact matches: `Cargo.toml`, `Cargo.lock`, `go.mod`, `go.sum`
   - Exact matches: `Gemfile`, `Gemfile.lock`, `build.gradle`, `pom.xml`

3. **Security-Sensitive Files** (Critical Risk):
   - Pattern: Files containing `secret`, `password`, `key`, `token`, `auth`, `credential`, `cert`, `private`
   - Examples: `auth-config.js`, `api-keys.yaml`, `secrets.json`

4. **Database Migrations** (High Risk):
   - Pattern: `**/migrations/**`, `**/migrate/**`, `**/alembic/**`, `**/db/migrate/**`
   - Examples: `db/migrations/001_create_users.sql`, `alembic/versions/abc123_add_column.py`

5. **CI/CD Configuration** (Medium Risk):
   - Pattern: `.github/**`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/**`, `.travis.yml`
   - Examples: `.github/workflows/deploy.yml`, `Jenkinsfile`

6. **Infrastructure as Code** (High Risk):
   - Pattern: `*.tf`, `*.tfvars`, `**/terraform/**`, `**/ansible/**`, `docker-compose*.yml`, `Dockerfile*`
   - Examples: `main.tf`, `docker-compose.production.yml`

7. **Large Files** (Medium Risk):
   - Criteria: Files with >500 lines changed (insertions + deletions)
   - Requires parsing `git diff --stat` or `jj diff --stat` output

**Detection Method:**

**For git:**

```bash
# Get list of changed files
git diff --name-only <base-branch>..HEAD

# Check each file against risk patterns using grep
# Example for config files:
git diff --name-only <base-branch>..HEAD | grep -E '\.(json|yaml|yml|toml|env|ini|config\.)' || echo "No config files"

# Example for dependency files:
git diff --name-only <base-branch>..HEAD | grep -E '^(package\.json|requirements\.txt|Cargo\.toml|go\.mod|Gemfile|pom\.xml)$' || echo "No dependency files"

# Example for security-sensitive:
git diff --name-only <base-branch>..HEAD | grep -iE '(secret|password|key|token|auth|credential|cert|private)' || echo "No security-sensitive files"
```

**For jj:**

```bash
# Get list of changed files
jj diff --name-only

# Apply same grep patterns as git examples above
jj diff --name-only | grep -E '\.(json|yaml|yml|toml|env|ini|config\.)' || echo "No config files"
```

**Large File Detection:**

Parse the stat output to find files with >500 total changes:

```bash
# Git example - extract line counts
git diff --stat <base-branch>..HEAD | awk '{
  # Match lines like: "path/to/file.py | 150 +++++++++++---"
  if (NF >= 3 && $2 == "|") {
    file = $1
    changes = $3
    # Remove + and - characters to get numeric count
    gsub(/[^0-9]/, "", changes)
    if (changes > 500) {
      print file " (" changes " lines changed)"
    }
  }
}'
```

### Step 5: Group Files by Directory

Organize changed files by directory for easier navigation:

**Processing:**

1. Extract directory path from each file (everything before last `/`)
2. Group files under their parent directory
3. Sort directories alphabetically
4. Within each directory, sort files alphabetically

**Example grouping logic:**

```bash
# Git example
git diff --name-status --find-renames <base-branch>..HEAD | awk '{
  status = $1
  file = $2
  # For renames, use the new filename (third column)
  if (status ~ /^R/) {
    file = $3
  }
  # Extract directory
  split(file, parts, "/")
  if (length(parts) > 1) {
    dir = parts[1]
    for (i = 2; i < length(parts); i++) {
      dir = dir "/" parts[i]
    }
  } else {
    dir = "."
  }
  print dir "/" file " [" status "]"
}' | sort
```

### Step 6: Generate Structured Report

Combine all collected information into a comprehensive markdown report:

```markdown
# Diff Analysis Report

## Summary

**Impact Metrics:**
- Files changed: <count>
- Lines added: <insertions>
- Lines removed: <deletions>
- Net change: +/- <net> lines
- Total churn: <insertions + deletions> lines

**Change Breakdown:**
- New files: <count>
- Modified files: <count>
- Deleted files: <count>
- Renamed/moved files: <count>

---

## ⚠️  Risk Assessment

### Critical Risks
<List files in Critical risk category, if any>

### High Risks
<List files in High risk category, if any>

### Medium Risks
<List files in Medium risk category, if any>

---

## Changes by Directory

### src/
- [M] auth/login.py (+50, -20)
- [A] auth/oauth.py (+120, -0)
- [M] auth/middleware.py (+15, -8)

### tests/
- [M] test_auth.py (+80, -10)
- [A] test_oauth.py (+95, -0)

### config/
- [M] settings.yaml (+5, -2) ⚠️  **Config file**

### .github/workflows/
- [M] ci.yml (+10, -5) ⚠️  **CI/CD**

---

## File Details

<For each file, optionally show detailed diff on request>

---

## Review Checklist

Based on detected changes, recommended review focus areas:

- [ ] Configuration changes reviewed and validated
- [ ] Dependency updates reviewed for breaking changes
- [ ] Security-sensitive changes reviewed
- [ ] Database migration tested
- [ ] CI/CD changes validated
- [ ] Large file changes reviewed for complexity
- [ ] Test coverage updated
```

**Report Generation Steps:**

1. **Summary Section:** Calculate and format all metrics
2. **Risk Assessment:** List files grouped by risk level (Critical → High → Medium)
3. **Changes by Directory:** Group files as described in Step 5, annotate risky files with ⚠️
4. **Review Checklist:** Generate based on detected risk categories

### Step 7: Offer Detailed Diff Review

After displaying the report, ask the user if they want to see detailed diffs:

```
Would you like to see detailed diffs? Choose an option:

1. View all file diffs
2. View only risky file diffs
3. View specific file diff (you'll be prompted for filename)
4. Skip detailed review

Enter choice (1-4):
```

**For option 1 (all diffs):**

**Git:**
```bash
git diff <base-branch>..HEAD
git diff           # unstaged
git diff --staged  # staged
```

**jj:**
```bash
jj diff
```

**For option 2 (risky files only):**

Show diffs only for files identified as risky in Step 4:

**Git:**
```bash
# For each risky file
git diff <base-branch>..HEAD -- <risky-file-path>
```

**jj:**
```bash
# For each risky file
jj diff <risky-file-path>
```

**For option 3 (specific file):**

Prompt for filename and show its diff:

```
Enter filename to review: <user-input>
```

Then show:

**Git:**
```bash
git diff <base-branch>..HEAD -- <user-specified-file>
```

**jj:**
```bash
jj diff <user-specified-file>
```

**For option 4:**

Skip detailed diff display and end with final summary.

### Step 8: Final Summary

Display completion summary:

```
✓ Diff analysis complete

**Report Summary:**
- Total files analyzed: <count>
- Risks detected: <count>
- Recommended reviews: <count from checklist>

**Next Steps:**
- Review flagged files before submitting for code review
- Ensure tests cover changed functionality
- Update documentation if needed
- Run linters and formatters

Use this analysis to prepare your code review submission.
```

## Performance Optimizations

To meet NFR-2.1 (<10s for 50+ commits) and NFR-2.4 (1000+ files):

1. **Limit stat output:** Use `--shortstat` instead of `--stat` for summary metrics
2. **Stream processing:** Process file lists line-by-line instead of loading all into memory
3. **Parallel detection:** Run risk pattern greps independently (they're read operations)
4. **Limit diff context:** When showing detailed diffs, use `--unified=3` (default) or less
5. **Cache base branch:** Detect once and reuse throughout
6. **Skip binary files:** Don't show diffs for binary files

**Example optimization for risk detection:**

```bash
# Run all grep patterns in parallel (git example)
FILES=$(git diff --name-only <base-branch>..HEAD)

# Parallel execution
echo "$FILES" | grep -E '\.(json|yaml|yml|toml)' > /tmp/risk_config.txt &
echo "$FILES" | grep -E '^(package\.json|requirements\.txt)' > /tmp/risk_deps.txt &
echo "$FILES" | grep -iE '(secret|password|key)' > /tmp/risk_security.txt &
wait

# Combine results
cat /tmp/risk_*.txt | sort -u
rm /tmp/risk_*.txt
```

## Error Handling

**Common error scenarios:**

1. **Not in a git/jj repository:**
   - Message: "Error: Not in a git or jj repository. Run this command from a repository root."

2. **No base branch found (git):**
   - Fallback: Compare against `HEAD~1` or `HEAD^`
   - Message: "Warning: No main/master/develop branch found. Comparing against previous commit."

3. **No changes detected:**
   - Message: "No changes detected. Working directory is clean."
   - Exit gracefully

4. **Binary file diffs:**
   - Message: "Skipping binary file: <filename>"
   - Use `git diff --binary` flag to detect

5. **Very large diffs (>10,000 lines):**
   - Warning: "Large diff detected (>10,000 lines). Consider reviewing in smaller chunks."
   - Offer to show summary only

**Example error detection:**

```bash
# Check if in repo
if [[ -d .git ]] || [[ -d .jj ]]; then
  # Proceed
else
  echo "Error: Not in a git or jj repository."
  exit 1
fi

# Check for changes
if [[ $(git diff --name-only <base>..HEAD | wc -l) -eq 0 ]]; then
  echo "No changes detected between <base> and HEAD."
  # Check working directory
  if [[ $(git diff --name-only | wc -l) -eq 0 ]]; then
    echo "Working directory is also clean. Nothing to analyze."
    exit 0
  fi
fi
```

## Safety Considerations

1. **Read-only operations:** All commands are read-only. No modifications to repository state.
2. **No destructive actions:** Analysis only. No commits, resets, or deletions.
3. **Large repository handling:** Stream processing and limited output to prevent memory issues.
4. **Binary file safety:** Skip binary file diffs to avoid terminal corruption.
5. **Sensitive data warning:** Warn if files containing "secret", "password", etc. are detected.

## Example Output

```markdown
# Diff Analysis Report

## Summary

**Impact Metrics:**
- Files changed: 12
- Lines added: 487
- Lines removed: 156
- Net change: +331 lines
- Total churn: 643 lines

**Change Breakdown:**
- New files: 3
- Modified files: 8
- Deleted files: 1
- Renamed/moved files: 0

---

## ⚠️  Risk Assessment

### High Risks
- config/settings.yaml (Configuration file modified)
- package.json (Dependencies updated)
- db/migrations/003_add_oauth.sql (Database migration)

### Medium Risks
- .github/workflows/ci.yml (CI/CD configuration)
- src/api/handler.py (Large change: 520 lines)

---

## Changes by Directory

### src/api/
- [M] handler.py (+450, -70) ⚠️  **Large file**
- [A] oauth.py (+120, -0)
- [M] middleware.py (+25, -10)

### src/auth/
- [M] login.py (+50, -20)
- [A] session.py (+80, -0)

### tests/
- [M] test_api.py (+90, -15)
- [A] test_oauth.py (+75, -0)
- [D] test_deprecated.py (-50)

### config/
- [M] settings.yaml (+5, -2) ⚠️  **Config file**

### db/migrations/
- [A] 003_add_oauth.sql (+45, -0) ⚠️  **Migration**

### .github/workflows/
- [M] ci.yml (+10, -5) ⚠️  **CI/CD**

### Root files:
- [M] package.json (+8, -4) ⚠️  **Dependencies**
- [M] README.md (+15, -5)

---

## Review Checklist

Based on detected changes, recommended review focus areas:

- [ ] Configuration changes in settings.yaml reviewed and validated
- [ ] Dependency updates in package.json reviewed for breaking changes
- [ ] Database migration 003_add_oauth.sql tested and reversible
- [ ] CI/CD changes in ci.yml validated in test environment
- [ ] Large changes in handler.py reviewed for complexity and maintainability
- [ ] Test coverage updated for new OAuth functionality
- [ ] Documentation updated in README.md

---

Would you like to see detailed diffs? Choose an option:

1. View all file diffs
2. View only risky file diffs (5 files)
3. View specific file diff
4. Skip detailed review

Enter choice (1-4):
```

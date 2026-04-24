---
name: note-health
description: Run a health check on your Obsidian vault to find issues
disable-model-invocation: true
allowed-tools:
  - Bash(obsidian orphans *)
  - Bash(obsidian deadends *)
  - Bash(obsidian unresolved *)
  - Bash(obsidian read *)
  - Bash(obsidian search *)
  - Bash(obsidian files *)
  - Bash(obsidian properties *)
  - Bash(obsidian wordcount *)
  - Bash(obsidian backlinks *)
  - Bash(obsidian outline *)
  - Bash(obsidian history *)
  - Read
---

# Vault Health Check

Run a comprehensive health check on your Obsidian vault.

## Usage

```
/note-health
/note-health --focus=orphans
/note-health --focus=stale
/note-health --folder="50 Developer Notes"
```

## What This Checks

| Category | Description | Detection Method |
|----------|-------------|------------------|
| Orphaned notes | Notes with no incoming links | `obsidian orphans` |
| Dead-end notes | Notes with no outgoing links | `obsidian deadends` |
| Broken links | Links pointing to non-existent notes | `obsidian unresolved` |
| Missing frontmatter | Notes without required metadata | `obsidian properties path="X"` |
| Stale notes | Notes not updated in 6+ months | `obsidian history path="X"` |
| Oversized notes | Notes that may need splitting | `obsidian wordcount path="X"` |
| Convention violations | Wrong folders, naming issues | Compare to CLAUDE.md rules |

## Arguments

- `--focus=TYPE` — Check only one category:
  - `orphans` — Orphaned notes only
  - `deadends` — Dead-end notes only
  - `broken` — Broken links only
  - `frontmatter` — Missing frontmatter only
  - `stale` — Stale notes only
  - `oversized` — Oversized notes only
  - `conventions` — Convention violations only

- `--folder=PATH` — Limit check to specific folder:
  - `--folder="Reference/Developer"`
  - `--folder="Waites"`

## Output Format

Returns a scannable health report:

```markdown
## Vault Health Report

### Summary
| Category | Issues | Status |
|----------|--------|--------|
| Orphaned notes | 7 | Needs attention |
| Broken links | 2 | Needs attention |
| Missing frontmatter | 12 | Needs attention |
| Stale notes | 4 | Review recommended |
| Convention violations | 3 | Minor |

**Overall Health:** 72/100

### Top Issues by Category

#### Orphaned Notes (7)
1. `Python Decorators.md` — No incoming links
2. `Old Meeting.md` — No incoming links
3. `Random Note.md` — No incoming links
... (showing top 5)

#### Broken Links (2)
1. `[[Missing Note]]` in `Developer Notes.md:42`
2. `[[Old Project]]` in `Projects.md:18`

#### Missing Frontmatter (12)
1. `Quick Note.md` — Missing: date created, date_modified
2. `Meeting 2025-01.md` — Missing: projects
... (showing top 5)

### Recommendations

1. **High priority:** Fix 2 broken links (blocks navigation)
2. **Medium priority:** Add frontmatter to 12 notes (improves search)
3. **Low priority:** Review 4 stale notes (may be outdated)

Run `/note-cleanup` to start fixing these issues.
```

## Health Score Calculation

The health score (0-100) is calculated as:

| Factor | Weight | Deduction per Issue |
|--------|--------|---------------------|
| Broken links | 25% | -5 per link |
| Orphaned notes | 20% | -2 per note |
| Dead-end notes | 10% | -1 per note |
| Missing frontmatter | 15% | -1 per note |
| Oversized notes | 10% | -2 per note |
| Convention violations | 10% | -2 per violation |
| Stale notes | 10% | -1 per note |

## Quick vs Full Check

**Quick check** (default): Samples 20% of vault, estimates totals
**Full check** (`--full`): Checks every note (slower but accurate)

```
/note-health --full
```

## Implementation

```bash
# 1. Read vault conventions
Read /Users/jacob/Loose Ends/.claude/CLAUDE.md

# 2. Run health checks using dedicated CLI commands:
obsidian orphans total          # Notes with no incoming links
obsidian deadends total         # Notes with no outgoing links
obsidian unresolved total       # Broken/unresolved links

# 3. For folder-scoped checks:
obsidian files folder="path"    # List notes in folder

# 4. Per-note checks (sample or full):
obsidian properties path="X"    # Check frontmatter
obsidian wordcount path="X"     # Check size
obsidian history path="X"       # Check staleness
obsidian outline path="X"       # Check structure

# 5. Calculate health score from results
# 6. Generate report
```

## Follow-up Actions

After viewing the health report:

- **Fix issues:** Run `/note-cleanup` to start interactive cleanup
- **Focus on category:** `/note-cleanup --type=orphans`
- **Re-check:** Run `/note-health` again to see improvement

## Example Session

```
User: /note-health

Claude: Running vault health check...

## Vault Health Report

### Summary
| Category | Issues | Status |
|----------|--------|--------|
| Orphaned notes | 7 | Needs attention |
| Broken links | 0 | Healthy |
| Missing frontmatter | 3 | Minor |
| Stale notes | 2 | Review recommended |
| Convention violations | 1 | Minor |

**Overall Health:** 85/100

Your vault is in good shape! The main issues are:
- 7 orphaned notes that could use links
- 3 notes missing frontmatter

Want to run `/note-cleanup` to fix these?
```

## Related Skills

- `/note-cleanup` — Start interactive cleanup session
- `/note-capture` — Quick capture to daily note

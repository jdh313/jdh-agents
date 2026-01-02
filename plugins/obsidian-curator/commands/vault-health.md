---
description: Run a health check on your Obsidian vault to find issues
---

# Vault Health Check

Run a comprehensive health check on your Obsidian vault.

## Usage

```
/obsidian-curator:vault-health
/obsidian-curator:vault-health --focus=orphans
/obsidian-curator:vault-health --focus=stale
/obsidian-curator:vault-health --folder="50 Developer Notes"
```

## What This Checks

| Category | Description | Detection Method |
|----------|-------------|------------------|
| Orphaned notes | Notes with no incoming links | Search for `[[Note Name]]` |
| Broken links | Links pointing to non-existent notes | Parse links, check targets |
| Missing frontmatter | Notes without required metadata | Check for `date created` |
| Stale notes | Notes not updated in 6+ months | Check `date_modified` |
| Convention violations | Wrong folders, naming issues | Compare to CLAUDE.md rules |

## Arguments

- `--focus=TYPE` — Check only one category:
  - `orphans` — Orphaned notes only
  - `broken` — Broken links only
  - `frontmatter` — Missing frontmatter only
  - `stale` — Stale notes only
  - `conventions` — Convention violations only

- `--folder=PATH` — Limit check to specific folder:
  - `--folder="50 Developer Notes"`
  - `--folder="80 Waites"`

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

Run `/obsidian-curator:cleanup` to start fixing these issues.
```

## Health Score Calculation

The health score (0-100) is calculated as:

| Factor | Weight | Deduction per Issue |
|--------|--------|---------------------|
| Broken links | 30% | -5 per link |
| Orphaned notes | 25% | -2 per note |
| Missing frontmatter | 20% | -1 per note |
| Convention violations | 15% | -2 per violation |
| Stale notes | 10% | -1 per note |

## Quick vs Full Check

**Quick check** (default): Samples 20% of vault, estimates totals
**Full check** (`--full`): Checks every note (slower but accurate)

```
/obsidian-curator:vault-health --full
```

## Implementation

```python
# 1. Read vault conventions
vault_rules = Read("/Users/jacob/Loose Ends/.claude/CLAUDE.md")

# 2. List all notes (or filtered subset)
if folder:
    notes = obsidian_list_files_in_dir(folder)
else:
    notes = obsidian_list_files_in_vault()

# 3. Check each category
orphans = find_orphaned_notes(notes)
broken = find_broken_links(notes)
missing_fm = find_missing_frontmatter(notes)
stale = find_stale_notes(notes)
violations = find_convention_violations(notes, vault_rules)

# 4. Calculate health score
score = calculate_health_score(orphans, broken, missing_fm, stale, violations)

# 5. Generate report
report = generate_health_report(score, orphans, broken, missing_fm, stale, violations)
```

## Follow-up Actions

After viewing the health report:

- **Fix issues:** Run `/obsidian-curator:cleanup` to start interactive cleanup
- **Focus on category:** `/obsidian-curator:cleanup --type=orphans`
- **Re-check:** Run `/obsidian-curator:vault-health` again to see improvement

## Example Session

```
User: /obsidian-curator:vault-health

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

Want to run `/obsidian-curator:cleanup` to fix these?
```

## Related Commands

- `/obsidian-curator:cleanup` — Start interactive cleanup session
- `/obsidian-curator:capture` — Quick capture to daily note

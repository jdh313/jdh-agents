---
description: View and search doing entries
context: fork
allowed-tools:
  - Bash(doing:*)
---

# View Entries

View, search, and filter time tracking entries.

## Usage

**Quick views:**
```bash
doing last                      # Most recent
doing today                     # Today's entries
doing yesterday                 # Yesterday's entries
doing recent                    # Last few entries
```

**Filtered views:**
```bash
doing show --tag=<tag>          # By tag
doing show --from "<date>"      # Date range
doing show --search "<text>"    # Text search
```

**With totals:**
```bash
doing show --totals             # Include time totals
doing today --totals            # Today with totals
```

## Common Filters

| Filter | Example |
|--------|---------|
| Tag | `--tag=client`, `--tag=meetings,billable` |
| Date range | `--from "monday"`, `--from "last week"` |
| Before/after | `--after "9am"`, `--before "yesterday"` |
| Search | `--search "API"`, `--search "bug"` |
| Only timed | `--only_timed` |

## Execution

1. Determine what view the user wants:
   - Time-based: today, yesterday, this week, specific date
   - Tag-based: entries with specific tags
   - Search: entries matching text
   - Recent: last N entries

2. Construct command:
   ```bash
   doing <view> [--tag=<tags>] [--from "<range>"] [--search "<text>"] [--totals]
   ```

3. Present results clearly, noting:
   - Number of entries found
   - Time range covered
   - Total time if `--totals` used

## Examples

| User says | Command |
|-----------|---------|
| "what did I do today" | `doing today` |
| "show yesterday's work" | `doing yesterday` |
| "time on client project" | `doing show --tag=client --totals` |
| "this week's meetings" | `doing show --tag=meetings --from "monday" --totals` |
| "find API related tasks" | `doing show --search "API"` |
| "last entry" | `doing last` |
| "recent entries" | `doing recent` |

## Output Formats

For reports, add `-o <format>`:
```bash
doing show --from "monday" -o markdown    # Markdown report
doing show --tag=client -o csv            # CSV export
doing today -o json                       # JSON data
```

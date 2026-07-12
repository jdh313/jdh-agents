---
name: note-cleanup
description: Explicit invocation only. Start an interactive vault cleanup session. Never invoke implicitly.
context: fork
agent: vault-curator
---

Apply the runtime mappings in [`../../RUNTIME.md`](../../RUNTIME.md).

# Vault Cleanup Session

Start an interactive session to clean up and maintain your vault.

## Usage

```
/note-cleanup
/note-cleanup --type=orphans
/note-cleanup --type=duplicates
/note-cleanup --type=stale
/note-cleanup --type=frontmatter
/note-cleanup --type=conventions
```

## What This Does

Launches the `vault-curator` agent for an interactive cleanup session.
The agent guides you through finding and fixing vault issues one category at a time.

## Why a persistent agent (not a cold fork per category)

Cleanup is iterative and stateful: inspect → clean → re-inspect, often
across several categories in one sitting, with skip decisions that must
not be re-litigated. `vault-curator` is therefore a **persistent**
session, not a one-shot worker:

- The skill forks `@vault-curator` **once**. Every follow-up turn
  (next category, re-inspect after fixes, a second `/note-cleanup` later
  in the same session) **re-engages the same instance** via `SendMessage`
  to its agent ID — it keeps the running Found/Fixed/Skipped tally,
  the conventions it loaded, and what you already chose to skip.
- After applying fixes, the curator **re-inspects surgically** — re-runs
  only the detection for the categories it touched to confirm counts
  dropped, not the whole sweep.
- Cold-forking per category would discard your accumulated skip
  decisions and force a full re-detect every turn. That's why this loop
  is persistent.

Contrast `/vault-inspect`, which is a genuine **one-shot** diagnostic
(single read-only pass, no state to carry) and stays on its cold fork.
The re-engagement contract lives in `agents/vault-curator.md`
(`## Persistent cleanup session`).

## Cleanup Types

| Type | What It Fixes | Typical Actions |
|------|---------------|-----------------|
| `orphans` | Notes with no incoming links | Link, add to MOC, or delete |
| `duplicates` | Overlapping notes on same topic | Merge or differentiate |
| `stale` | Notes not updated in 6+ months | Update, archive, or mark reviewed |
| `frontmatter` | Notes missing required metadata | Add date created, tags, etc. |
| `conventions` | Notes in wrong folders, bad naming | Move, rename, restructure |

## Session Flow

```
1. Choose focus area (or auto-detect highest priority)
   |
2. Scan vault for issues in that category
   |
3. Present findings in scannable list
   |
4. Process issues one by one:
   - Show issue details
   - Present options (Fix / Skip / Batch)
   - Execute chosen action
   - Show progress
   |
5. Category complete -> offer to continue or end
   |
6. Session summary with actions taken
```

## ADHD-Friendly Features

| Feature | How It Helps |
|---------|--------------|
| One question at a time | No decision overload |
| Progress indicators | "Fixed 3/7 issues" keeps momentum |
| Batch operations | "Fix all 5 similar issues at once?" |
| Clear recommendations | Always suggests best action |
| Easy exit | Can stop anytime, progress is saved |
| Celebration | "Great work! Fixed 12 issues!" |

## Example Session

```
User: /note-cleanup

Claude: Starting vault cleanup session...

## Vault Cleanup

What would you like to focus on?

| # | Category | Issues Found | Priority |
|---|----------|--------------|----------|
| 1 | Orphaned notes | 7 | High |
| 2 | Missing frontmatter | 12 | Medium |
| 3 | Stale notes | 4 | Low |
| 4 | Convention violations | 3 | Low |

Choose a category (1-4) or type "auto" for highest priority:

User: 1

Claude: ## Orphaned Notes (7 found)

### 1 of 7: Python Decorators.md

**Location:** `50 Developer Notes/Python Decorators.md`
**Created:** 2025-06-15
**Size:** 1.2KB
**Content preview:**
> Python decorators are functions that modify other functions...

**No incoming links found.**

**Options:**
1. Link from `[[Python]]` (recommended)
2. Add to `50 Developer Notes/00 Dashboard.md`
3. Delete note
4. Skip for now

Choose (1-4):

User: 1

Claude: Added link from Python.md

## Progress: 1/7 fixed

### 2 of 7: Old Meeting Notes.md
...
```

## Batch Operations

When multiple issues are similar, batch fixing is offered:

```
Claude: ## Missing Frontmatter (5 similar issues)

These 5 notes are all missing `date created` and `date_modified`:

1. Quick Note.md
2. Random Thought.md
3. Untitled.md
4. New Idea.md
5. Draft.md

**Options:**
1. Add standard frontmatter to ALL 5 (recommended)
2. Review each one individually
3. Skip all

Choose (1-3):
```

## Session Summary

At the end of a cleanup session:

```markdown
## Cleanup Session Complete

### Actions Taken
| Category | Fixed | Skipped |
|----------|-------|---------|
| Orphaned notes | 5 | 2 |
| Missing frontmatter | 12 | 0 |
| **Total** | **17** | **2** |

### Details
- Linked 5 orphaned notes to MOCs
- Added frontmatter to 12 notes
- Skipped 2 notes (user preference)

### Vault Health Improvement
Before: 72/100 -> After: 89/100 (+17 points)

Great work! Your vault is much healthier now.

---
Run `/vault-inspect` to see the full report.
```

## Continuing Later

If you stop mid-session:
- Progress is shown in the summary
- Run `/note-cleanup` again to continue
- Or run `/note-cleanup --type=X` to focus on remaining issues

## Arguments

- `--type=TYPE` — Start with specific category (see table above)
- `--folder=PATH` — Limit cleanup to specific folder
- `--auto` — Automatically start with highest-priority category

## Related Skills

- `/vault-inspect` — Quick audit without interactive session
- `/note-capture` — Quick capture to daily note

---
name: doing-assistant
description: >
  INVOKE for time tracking requests. Triggers: "track time", "log work", "start task",
  "finish task", "what did I do", "backdate", "add past task". Handles starting/stopping
  time entries, backdating entries, and querying work history using the doing CLI.
allowed-tools:
  - Bash(doing:*)
  - Read
  - Glob
---

# Doing Time Tracking Assistant

## Overview

Track what you're working on using Brett Terpstra's `doing` CLI. Supports real-time tracking, backdating past work, and querying history.

**Commands available:**
- `/doing:now` - Start tracking a task
- `/doing:done` - Complete a task (current or backdated)
- `/doing:show` - View and search entries

## Core Workflows

### 1. Start Tracking (Real-time)

```bash
doing now <description>
doing now <description> @tag1 @tag2
```

**Examples:**
```bash
doing now debugging authentication issue
doing now code review for PR #123 @reviews
doing now working on API endpoint @client-project
```

### 2. Complete Current Task

```bash
doing finish                    # Mark current task @done
doing done                      # Alias for finish
```

### 3. Add Past Work (Backdating)

For work you forgot to track or need to log after the fact:

```bash
# Completed task with known duration
doing done --back <start> --took <duration> <description>

# Completed task with known start and end
doing done --back <start> --at <end> <description>

# Completed task ending now, duration known
doing done --took <duration> <description>
```

**Examples:**
```bash
# Meeting from 9am, lasted 1 hour
doing done --back 9am --took 1h standup meeting @meetings

# Worked on feature from 2pm to 4:30pm
doing done --back 2pm --at 4:30pm implemented user auth @feature

# Just finished something that took 45 minutes
doing done --took 45m fixed pagination bug @bugs

# Yesterday's work
doing done --back "yesterday 10am" --took 3h client workshop @client
```

### 4. Modify Recent Entry

Add notes to the last entry:
```bash
doing note "additional context here"
doing note "PR #456, blocked by API issue"
```

Add tags to the last entry:
```bash
doing tag @newtag
doing tag @client @billable
```

Reset start time of last entry:
```bash
doing reset --to 2pm            # Change when task started
```

### 5. View Entries

```bash
doing last                      # Most recent entry
doing today                     # Today's entries
doing yesterday                 # Yesterday's entries
doing recent                    # Last few entries
doing show                      # All entries
doing show --tag=<tag>          # Filter by tag
doing show --from "monday"      # Date range
```

## Time Pattern Reference

See `references/time-patterns.md` for comprehensive date/time formats.

**Quick reference:**
| Pattern | Example | Meaning |
|---------|---------|---------|
| Relative | `30m`, `2h`, `1h30m` | Duration ago |
| Clock | `2pm`, `14:30`, `9:00am` | Time today |
| Named | `noon`, `midnight` | Common times |
| Yesterday | `yesterday 3pm` | Previous day |
| Day name | `monday 9am` | Recent day |
| Range | `"9am to 5pm"` | Start to end |

## Workflow Recommendations

### Real-time Tracking
```bash
doing now starting feature X    # Begin
# ... work ...
doing finish                    # Complete
doing now moving to code review # Next task
```

### End-of-Day Logging
```bash
doing done --back 9am --took 30m standup @meetings
doing done --back 9:30am --took 2h feature development @project-x
doing done --back 11:30am --took 1h code review @reviews
doing done --back 1pm --took 3h bug fixes @bugs
```

### Session Integration

When starting a coding session:
- Check `doing last` to see what was in progress
- Use `doing again` to resume a previous task

When ending a session:
- Use `doing finish` to mark current work done
- Or leave running if continuing later

## Error Handling

**"No entries found"**: No matching entries for the query. Try broader filters.

**"Invalid date"**: Check date format. Use quotes for multi-word dates: `--back "yesterday 2pm"`

**"doing: command not found"**: Install with `brew install brew-gem/gems/gem-doing`

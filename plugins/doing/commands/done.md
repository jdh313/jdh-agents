---
description: Complete a task or log past work with doing
allowed-tools:
  - Bash(doing:*)
---

# Complete/Log Task

Mark current task done, or log completed work (including backdated entries).

## Usage

**Finish current task:**
```bash
doing finish
doing done
```

**Log completed task (ending now):**
```bash
doing done <description>
doing done --took <duration> <description>
```

**Backdate completed task:**
```bash
doing done --back <start> --took <duration> <description>
doing done --back <start> --at <end> <description>
```

## Time Flags

| Flag | Purpose | Example |
|------|---------|---------|
| `--back` | Set start time | `--back 2pm`, `--back "yesterday 9am"` |
| `--took` | Set duration | `--took 1h`, `--took 45m`, `--took 2h30m` |
| `--at` | Set end time | `--at 5pm`, `--at "today noon"` |

## Execution

1. Determine what the user wants:
   - **Finish current**: No description, just mark done
   - **Log new completed**: Has description, may have timing
   - **Backdate**: Mentions past time or duration

2. Parse timing information:
   - Start time ("started at", "from", "at X")
   - End time ("until", "to", "ended at")
   - Duration ("took", "for", "lasted")

3. Construct command:
   ```bash
   doing done [--back <start>] [--took <duration>] [--at <end>] [<description>] [@tags]
   ```

4. Confirm to user:
   - What was logged
   - Time range (start to end)
   - Duration calculated

## Examples

| User says | Command |
|-----------|---------|
| "done" or "finish" | `doing finish` |
| "done with the bug fix" | `doing done bug fix` |
| "took 2 hours on code review" | `doing done --took 2h code review` |
| "had a meeting from 9 to 10am" | `doing done --back 9am --took 1h meeting` |
| "worked on API from 2pm to 4:30pm" | `doing done --back 2pm --at 4:30pm API work` |
| "yesterday did 3 hours of testing" | `doing done --back "yesterday" --took 3h testing` |
| "log standup at 9am, 15 minutes" | `doing done --back 9am --took 15m standup @meetings` |

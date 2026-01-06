---
description: Start tracking a task with doing
allowed-tools:
  - Bash(doing:*)
---

# Start Tracking

Start tracking what you're working on now.

## Usage

**Basic:**
```bash
doing now <description>
```

**With tags:**
```bash
doing now <description> @tag1 @tag2
```

**Backdated start:**
```bash
doing now --back <time> <description>
```

## Execution

1. Parse the user's request for:
   - Task description
   - Any tags (words starting with @)
   - Backdate time (if mentioned: "started at 2pm", "been working since 10am")

2. Construct and run the command:
   ```bash
   doing now [--back <time>] <description> [@tags]
   ```

3. Confirm to user:
   - What task was started
   - What time it was logged at
   - Any tags applied

## Examples

| User says | Command |
|-----------|---------|
| "start tracking API work" | `doing now API work` |
| "tracking bug fix for auth" | `doing now bug fix for auth` |
| "started working on tests at 2pm" | `doing now --back 2pm working on tests` |
| "log client meeting, tag it billable" | `doing now client meeting @billable` |

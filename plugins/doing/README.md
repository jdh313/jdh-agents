# doing

Time tracking plugin for Claude Code using Brett Terpstra's [doing](https://brettterpstra.com/projects/doing/) CLI.

## Features

- **Real-time tracking**: Start/stop tasks as you work
- **Backdating**: Log past work with flexible time formats
- **History queries**: View entries by date, tag, or search

## Prerequisites

Install doing via Homebrew:

```bash
brew install brew-gem/gems/gem-doing
```

## Commands

| Command | Description |
|---------|-------------|
| `/doing:now` | Start tracking a task |
| `/doing:done` | Complete task or log past work |
| `/doing:show` | View and search entries |

## Quick Examples

**Start tracking:**
```
/doing:now debugging auth issue
```

**Finish current task:**
```
/doing:done
```

**Log past work:**
```
/doing:done had a meeting from 9am for 1 hour
```

**View today's work:**
```
/doing:show today
```

## Backdating

Log work you forgot to track:

```bash
# Meeting from 9-10am
doing done --back 9am --took 1h standup @meetings

# Afternoon work block
doing done --back 2pm --at 4:30pm feature work

# Yesterday's entry
doing done --back "yesterday 10am" --took 2h client call
```

## Time Patterns

- **Durations**: `30m`, `1h`, `2h30m`
- **Times**: `9am`, `14:30`, `noon`
- **Relative**: `yesterday`, `monday`, `last week`
- **Ranges**: `"monday to friday"`, `"9am to 5pm"`

See `skills/doing-assistant/references/time-patterns.md` for full reference.

## Tags

Add tags inline with `@`:

```bash
doing now working on API @client @billable
doing done --took 1h code review @reviews
doing show --tag=client --totals
```

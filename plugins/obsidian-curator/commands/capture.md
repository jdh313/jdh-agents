---
description: Quickly capture a thought or note to today's daily note
---

# Quick Capture

Append a quick capture to today's daily note.

## Usage

```
/obsidian-curator:capture This is my quick thought
/obsidian-curator:capture Debugging approach: restart the service first
/obsidian-curator:capture Pattern: use dataclasses for config objects
```

## What This Does

1. Gets today's daily note using `obsidian_get_periodic_note`
2. Checks if "## Captured" section exists
3. Appends your capture with a timestamp
4. Confirms the capture was added

## Capture Format

Captures are added under the "## Captured" section in this format:

```markdown
## Captured

%%CLAUDE WRITTEN START%%
- **10:30** — This is my quick thought
%%CLAUDE WRITTEN END%%
%%CLAUDE WRITTEN START%%
- **14:15** — Debugging approach: restart the service first
%%CLAUDE WRITTEN END%%
%%CLAUDE WRITTEN START%%
- **16:45** — Pattern: use dataclasses for config objects
%%CLAUDE WRITTEN END%%
```

Note: Each capture is wrapped individually with AI content markers (hidden in reading view).

## No Arguments?

If you run `/obsidian-curator:capture` without any text, I'll prompt you for what to capture.

## Implementation

```python
# Get current time for timestamp
from datetime import datetime
now = datetime.now()
timestamp = now.strftime("%H:%M")

# Get today's daily note
daily_note = obsidian_get_periodic_note(period="daily", type="content")

# Parse the note to find or create "## Captured" section
# Append with AI content markers:
# \n%%CLAUDE WRITTEN START%%\n- **{timestamp}** — {capture_text}\n%%CLAUDE WRITTEN END%%\n

# Write back using obsidian_put_content or obsidian_patch_content
```

## When to Use This vs. Regular Notes

**Use /capture for:**
- Quick thoughts (1-3 sentences)
- Reminders
- Ideas to flesh out later
- Session discoveries that aren't yet substantial

**Use a proper note for:**
- Detailed explanations
- Code examples
- Multi-paragraph content
- Anything with structure (headers, lists, etc.)

## Arguments

- `$ARGUMENTS` — The text to capture (everything after the command)

## Example Session

```
User: /obsidian-curator:capture Lambda cold starts fixed with provisioned concurrency

Claude: ✓ Captured to today's daily note (01 Daily Notes/2025-01-02.md):

## Captured
%%CLAUDE WRITTEN START%%
- **14:23** — Lambda cold starts fixed with provisioned concurrency
%%CLAUDE WRITTEN END%%
```

## Related Commands

- Use `vault-knowledge` skill for creating proper notes
- Use `contextual-search` skill to find existing notes before capturing

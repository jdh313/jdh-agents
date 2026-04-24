---
name: note-capture
description: Quickly capture a thought or note to today's daily note
disable-model-invocation: true
allowed-tools:
  - Bash(obsidian daily:read *)
  - Bash(obsidian daily:append *)
  - Bash(obsidian read *)
  - Bash(obsidian append *)
  - Edit
---

# Quick Capture

Append a quick capture to today's daily note.

## Usage

```
/note-capture This is my quick thought
/note-capture Debugging approach: restart the service first
/note-capture Pattern: use dataclasses for config objects
```

## What This Does

1. Finds today's daily note in `Daily Notes/YYYY-MM-DD.md`
2. Checks if "## Captured" section exists
3. Appends your capture with a timestamp
4. Confirms the capture was added

## Capture Format

Captures are added under the "## Captured" section in this format:

```markdown
## Captured

- **10:30** — This is my quick thought
- **14:15** — Debugging approach: restart the service first
- **16:45** — Pattern: use dataclasses for config objects
```

## No Arguments?

If you run `/note-capture` without any text, I'll prompt you for what to capture.

## Implementation

```bash
# 1. Read today's daily note
obsidian daily:read

# 2. If "## Captured" section exists, append to it:
obsidian daily:append content="$(cat <<'EOF'
- **{timestamp}** — {capture_text}
EOF
)"

# 3. If "## Captured" section doesn't exist, use Edit tool to add it:
# Edit tool on /Users/jacob/Loose Ends/Daily Notes/{date}.md
# to insert the section at the appropriate location

# 4. If daily note doesn't exist yet, it will be created by daily:append
```

## When to Use This vs. Regular Notes

**Use /note-capture for:**
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
User: /note-capture Lambda cold starts fixed with provisioned concurrency

Claude: Captured to today's daily note (Daily Notes/2025-01-02.md):

## Captured
- **14:23** — Lambda cold starts fixed with provisioned concurrency
```

## Related Skills

- Use `vault-knowledge` skill for creating proper notes
- Use `contextual-search` skill to find existing notes before capturing

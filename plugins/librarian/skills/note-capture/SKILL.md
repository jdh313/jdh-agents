---
name: note-capture
description: Quickly capture a thought or note to today's daily note
disable-model-invocation: true
context: fork
agent: note-editor
---

# Quick Capture

Append a quick capture to today's daily note under the `## Captured`
section. The slash command forks to `@note-editor`, which executes the
write.

## Usage

```
/note-capture This is my quick thought
/note-capture Debugging approach: restart the service first
/note-capture Pattern: use dataclasses for config objects
```

If invoked with no arguments, prompt the user for what to capture.

## Operation

For the forked `@note-editor`:

1. **Locate today's daily note** at `Daily Notes/YYYY-MM-DD.md` (the
   vault's daily-note convention). If the file doesn't exist yet,
   `obsidian-cli daily:append` creates it.

2. **Capture format** — one bullet under `## Captured` with a timestamp:

   ```markdown
   ## Captured

   - **HH:MM** — <capture text>
   ```

   Use 24-hour time. If `## Captured` already exists, append to it. If
   not, add the section in the appropriate position (typically near the
   top of the daily note's content).

3. **Confirm** to the user: file path + the line that was added.

## When to use this vs. regular notes

**Use `/note-capture` for:**
- Quick thoughts (1-3 sentences)
- Reminders
- Ideas to flesh out later
- Session discoveries that aren't yet substantial

**Use a proper note (`wiki-create` etc.) for:**
- Detailed explanations
- Code examples
- Multi-paragraph content
- Anything with structure (headers, lists, etc.)

## Arguments

`$ARGUMENTS` — the text to capture (everything after the slash command).

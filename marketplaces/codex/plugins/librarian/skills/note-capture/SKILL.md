---
name: note-capture
description: Quickly capture a thought or note to today's daily note
---

# Quick Capture

## Codex registered dispatch

On Codex, this skill's `note-editor` route follows
the active installed Librarian `RUNTIME.md` (derived from the active
`SKILL.md` path; `## Codex optional registered vault roles` and
`## Installed resources and vault destination`). Immediately before each exact
dispatch, run the selected-scope check. Only a current result permits
`agent_type: "librarian:note-editor"` with the required `## Runtime context`;
do not set a dispatch model or effort. A failed or stale check blocks native
dispatch. The user may separately choose the installed Markdown/procedure
fallback with no `agent_type`; that route does not register a role. The
existing Claude `agent: note-editor` flow remains unchanged.

On Codex, every vault path below is rooted at the verified `vault_root` and
each CLI or connector operation binds the verified `vault_name`. Literal
`~/Loose Ends` and unqualified integration examples remain Claude-only,
including before dispatch.

Append a quick capture to today's daily note under the `## Captured`
section. The slash command forks to `@note-editor`, which executes the
write.

**One-shot by design.** This is a single mechanical append with no
carried state, so it stays on a cold `context: fork` dispatch — there's
nothing to re-engage. Persistent re-engagement is reserved for stateful
multi-turn sessions (`note-cleanup`'s curator loop, multi-step reader
sessions); a single capture doesn't qualify.

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

Use the user's invocation input as the text to capture (everything after the slash command).

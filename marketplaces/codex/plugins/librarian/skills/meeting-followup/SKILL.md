---
name: meeting-followup
description: >
  Use Skill(meeting-followup) when working on a project to surface relevant
  unchecked action items from recent meeting notes in the active work context.
  Presents contextually without interrupting flow.
---

# Meeting Follow-up

## Codex registered dispatch

On Codex, this skill's `@vault-reader` and `@note-editor` routes follow
the active installed Librarian `RUNTIME.md` (derived from the active
`SKILL.md` path; `## Codex optional registered vault roles` and
`## Installed resources and vault destination`). Immediately before each exact
dispatch, run the selected-scope check. Only a current result permits the
matching `agent_type` (`librarian:vault-reader` or `librarian:note-editor`)
with the required `## Runtime context`; do not set a dispatch model or effort.
A failed or stale check blocks native dispatch. The user may separately choose
the installed Markdown/procedure fallback with no `agent_type`; that route does
not register a role. The existing Claude routes remain unchanged.

On Codex, every vault path below is rooted at the verified `vault_root` and
each CLI or connector operation binds the verified `vault_name`. Literal
`~/Loose Ends` and unqualified integration examples remain Claude-only,
including before dispatch.

Surface relevant unchecked action items from meeting notes when they
match the current work context. Read and mark-complete operations both
dispatch to agents; this skill gathers intent and presents results.

## Configuration

This skill operates on `${active_work_context}/Meetings/`. On Claude, before
any agent dispatch, read `~/Loose Ends/.claude/librarian.local.md` and extract
`active_work_context` from its frontmatter. On Codex, first validate the
Runtime context destination, then read
`<vault_root>/.claude/librarian.local.md` and extract the same value. Substitute
that value for `${active_work_context}` everywhere below. Default to `Work` if
the config file or key is missing. See
`${CLAUDE_PLUGIN_ROOT}/references/work-context-config.md` for full
substitution rules. On Codex, resolve that file beneath the active installed
`plugin_root` and pass its canonical absolute path in `## Runtime context`;
never use a source checkout or current working directory.

## When to activate

1. **Starting work on a project** — Check for related tasks
2. **Discussing a topic covered in recent meetings** — Surface relevant notes
3. **User mentions a meeting or action item** — Find the source
4. **Working on code in the active work context** — Check for project tasks

## Workflow

### 1. Identify the current work context

What project, repo, person, or topic is the user actively engaged with?
Capture as a short context string (one or two terms).

### 2. Dispatch the search to vault-reader

Invoke `@vault-reader` with:

```markdown
## Intent
find unchecked action items relevant to <context-string>

## Constraints
- Search path: `${active_work_context}/Meetings/`
- Match: project, topic, person, or repo in `<context-string>`
- Window: last 14 days
- Filter: unchecked checkboxes only (`- [ ]`)

## Input
context: <context-string>

## Output shape
Table of items with columns: Meeting path, Date, Item text, Owner.
Include `## Notes` if anything is ambiguous.
```

### 3. Present to user (non-interrupting style)

If results are non-empty, surface inline or as a batch summary depending
on count:

**Inline (1-2 items):**
```markdown
> **Related action item** from `<meeting>` on `<date>`:
> - [ ] <item text>
>
> Address now or skip?
```

**Batch (3+ items):**
```markdown
## Relevant Meeting Actions
| Meeting | Date | Item | Owner |
|---|---|---|---|
| ... |

Address any of these? (1-N, all, skip)
```

If results are empty: do not surface anything. Do not nag.

### 4. If the user wants to mark an item complete

Dispatch the write to `@note-editor`:

```markdown
## Intent
mark action item complete in `<meeting-path>`

## Constraints
Item text (verbatim): `- [ ] <text>`

## Input
Replace `- [ ]` with `- [x]` on the line matching the verbatim text.
Preserve all other content in the file.

## Output shape
Confirm file modified, return modified line for sanity-check.
```

## Presentation style

- **Non-interrupting** — surface at natural breakpoints, not mid-flow
- **Actionable** — show the checkbox text exactly; include meeting date
- **ADHD-friendly** — one item inline OR batch at breakpoint; clear
  skip; no repeat nagging for skipped items

## Remember

- Be helpful, not annoying — only surface truly relevant items
- Empty results mean stay quiet
- Skip is always a valid response

---
name: base-add
description: Create a new entry for a specific Obsidian Base with correct frontmatter
disable-model-invocation: true
context: fork
agent: note-editor
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
---

# Add to Base

Create a note with the correct properties and location to appear in a
specified Obsidian Base. The slash command forks to `@note-editor`, which
loads `${CLAUDE_PLUGIN_ROOT}/references/bases.md` for base schemas and
filter conventions and executes the write.

## Usage

```
/base-add ideas My new project idea
/base-add software Ruff - Fast Python linter
/base-add adr Use PostgreSQL for primary datastore
```

## Operation

For the forked `@note-editor`:

1. **Identify the target base** from the first argument (`$1`).
2. **Query the base** to see structure and required properties:

   ```bash
   obsidian-cli base:query path="Bases/<BaseName>.base" format=json
   ```

3. **Determine the target folder** from the base's filter
   (e.g., `file.inFolder("Inbox")` → `Inbox/`).
4. **Read the template** for the note type if one exists:

   ```bash
   obsidian-cli template:read name="<TemplateName>" resolve title="<Title>"
   ```

5. **Prompt the user** for any required properties not derivable from
   context. Required properties are typically those in the base's `order`
   array.
6. **Show a preview** of the proposed frontmatter + body for approval.
7. **Create the note** at the resolved folder + filename:

   ```bash
   obsidian-cli create path="<folder>/<title>.md" content="..."
   ```

8. **Confirm** to the user with the full path.

## Available bases

| Shortcut | Base | Location | Key properties |
|----------|------|----------|----------------|
| `ideas` | Ideas | `Inbox/` | status |
| `software` | Software | `Reference/Tools/Software Catalog/` | category, solves, status, url |
| `prompts` | Prompts | `Reference/Tools/Prompts/` | description |
| `adr` | ADRs | (legacy: `Waites/Decisions/`) | decision_date, status, area, context |
| `repo` | Repos | (legacy: `Waites/Repos/`) | github-url, status |
| `hobby` | Hobbies | `Hobbies/` | status, time_commitment |

> The `adr` and `repo` rows point at archived Waites paths. The Bases
> registry needs the same update; flagged for vault maintenance.

## Required properties by base

### Ideas

```yaml
status: proposed | in-progress | done | archived
```

### Software

```yaml
category: developer-tools | infrastructure | productivity | ...
solves: What problem this software solves
status: considering | trialing | using | dropped
url: Official URL
alternatives: [] # Optional
integrations: [] # Optional
```

### ADRs

```yaml
decision_date: YYYY-MM-DD
status: proposed | accepted | deprecated | superseded
area: backend | frontend | infrastructure | ...
context: Why this decision was needed
jira_tickets: [] # Optional
decision_makers: [] # Optional
```

### Repos

```yaml
github-url: https://github.com/<org>/<repo>
status: active | archived | deprecated
used-in: [] # Optional
uses: [] # Optional
```

### Hobbies

```yaml
status: active | paused | considering | dropped
time_commitment: X hours/week
financial_commitment: $/month # Optional
```

### Prompts

```yaml
description: What this prompt does
```

## Arguments

- First word: base shortcut (`ideas`, `software`, `adr`, `repo`, `hobby`, `prompts`)
- Remaining: title or initial content for the entry

## No arguments?

If run without arguments, the agent prompts for:

1. Which base to add to
2. Title of the entry
3. Required properties for that base

## When to use this vs. quick capture

**Use `/base-add` for:**
- Structured entries that should appear in a base
- Content with specific properties (status, category, etc.)
- Anything you want to track and query later

**Use `/note-capture` for:**
- Quick thoughts without structure
- Temporary notes
- Content to sort later

## Related

- `${CLAUDE_PLUGIN_ROOT}/references/bases.md` — base schemas and filter conventions (the agent loads this)
- `/note-capture` — quick unstructured captures

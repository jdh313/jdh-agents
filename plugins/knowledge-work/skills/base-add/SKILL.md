---
name: base-add
description: Create a new entry for a specific Obsidian Base with correct frontmatter
disable-model-invocation: true
allowed-tools:
  - Bash(obsidian *)
  - Read
  - Glob
---

# Add to Base

Create a note with the correct properties and location to appear in a specified Base.

## Usage

```
/base-add ideas My new project idea
/base-add software Ruff - Fast Python linter
/base-add adr Use PostgreSQL for primary datastore
```

## What This Does

1. Identifies the target base from the first argument
2. Reads the base file to understand required properties
3. Determines the correct folder location (from base filter)
4. Prompts for any required properties
5. Shows proposed note with frontmatter for approval
6. Creates the note in the correct location

## Available Bases

| Shortcut | Base | Location | Key Properties |
|----------|------|----------|----------------|
| `ideas` | Ideas | `Inbox/` | status |
| `software` | Software | `Reference/Tools/Software Catalog/` | category, solves, status, url |
| `prompts` | Prompts | `Reference/Tools/Prompts/` | description |
| `adr` | ADRs | `Waites/Decisions/` | decision_date, status, area, context |
| `repo` | Waites Repos | `Waites/Repos/` | github-url, status |
| `hobby` | Hobbies | `Hobbies/` | status, time_commitment |

## Example Session

```
User: /base-add software Ruff - Fast Python linter

Claude: Creating entry for **Software** base...

What does Ruff solve? (e.g., "Python linting and formatting")
User: Python linting and formatting, replaces flake8 + black

Claude: Proposed note for Software base:

---
date created: 2025-01-03 10:30
date_modified: 2025-01-03 10:30
category: developer-tools
solves: Python linting and formatting, replaces flake8 + black
status: using
url: https://docs.astral.sh/ruff/
alternatives: [flake8, pylint, black]
---


# Ruff

Fast Python linter and formatter. Replaces flake8 + black in one tool.

## Overview
...

Location: `Reference/Tools/Software Catalog/Ruff.md`

Create this note? [Yes / Edit / Cancel]
```

## Required Properties by Base

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
alternatives: [] # Optional list of alternatives
integrations: [] # Optional list of integrations
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

### Waites Repos
```yaml
github-url: https://github.com/waites/repo-name
status: active | archived | deprecated
used-in: [] # Optional - what uses this
uses: [] # Optional - what this uses
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

- First word: Base shortcut (ideas, software, adr, repo, hobby, prompts)
- Remaining: Title or initial content for the entry

## No Arguments?

If run without arguments, prompts for:
1. Which base to add to
2. Title of the entry
3. Required properties for that base

## Implementation Flow

```bash
# 1. Parse base shortcut and title from arguments

# 2. Query the base to see existing entries and structure:
obsidian base:query path="Bases/{base_name}.base" format=json

# 3. Read the template for this note type (if available):
obsidian template:read name="{template_name}" resolve title="{title}"

# 4. Determine target folder from base filter
# e.g., file.inFolder("Inbox") -> folder = "Inbox/"

# 5. Get required properties from base views
# Properties in "order" array are typically required

# 6. Prompt user for missing required properties

# 7. Generate frontmatter + content

# 8. Show preview for approval

# 9. Create note:
obsidian create path="{folder}/{title}.md" content="$(cat <<'EOF'
...content with frontmatter and body...
EOF
)"
```

## When to Use This vs. Quick Capture

**Use /base-add for:**
- Structured entries that should appear in a base
- Content with specific properties (status, category, etc.)
- Anything you want to track and query later

**Use /note-capture for:**
- Quick thoughts without structure
- Temporary notes
- Content to sort later

## Related Skills

- `bases-knowledge` skill — Understands base structure
- `vault-knowledge` skill — General vault conventions
- `/note-capture` — Quick unstructured captures

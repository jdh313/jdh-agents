---
description: Create a new entry for a specific Obsidian Base with correct frontmatter
---

# Add to Base

Create a note with the correct properties and location to appear in a specified Base.

## Usage

```
/obsidian-curator:add-to-base ideas My new project idea
/obsidian-curator:add-to-base software Ruff - Fast Python linter
/obsidian-curator:add-to-base adr Use PostgreSQL for primary datastore
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
| `ideas` | Ideas | `Ideas/` | status |
| `software` | Software | `30 Productivity and Tools/Software Catalog/` | category, solves, status, url |
| `prompts` | Prompts | `Prompts/` | description |
| `adr` | ADRs | `80 Waites/ADRs/` | decision_date, status, area, context |
| `repo` | Waites Repos | `80 Waites/Repos/` | github-url, status |
| `hobby` | Hobbies | `20 Hobbies/Hobby Catalog/` | status, time_commitment |

## Example Session

```
User: /obsidian-curator:add-to-base software Ruff - Fast Python linter

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

Location: `30 Productivity and Tools/Software Catalog/Ruff.md`

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

```python
# 1. Parse base shortcut
base_name = args.split()[0].lower()
title = ' '.join(args.split()[1:])

# 2. Read base file to get filter/properties
base_file = Read(f"/Users/jacob/Loose Ends/Bases/{base_mapping[base_name]}.base")

# 3. Determine target folder from filter
# e.g., file.inFolder("Ideas") -> folder = "Ideas/"

# 4. Get required properties from base views
# Properties in "order" array are typically required

# 5. Prompt user for missing required properties

# 6. Generate frontmatter + content
# 7. Show preview for approval
# 8. Create note with obsidian_put_content
```

## When to Use This vs. Quick Capture

**Use /add-to-base for:**
- Structured entries that should appear in a base
- Content with specific properties (status, category, etc.)
- Anything you want to track and query later

**Use /capture for:**
- Quick thoughts without structure
- Temporary notes
- Content to sort later

## Related

- `bases-knowledge` skill — Understands base structure
- `vault-knowledge` skill — General vault conventions
- `/capture` command — Quick unstructured captures

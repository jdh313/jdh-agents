# Bases

Reference for agents and skills that work with the user's Obsidian Bases —
`.base` files that present saved views over notes filtered by folder, tag,
or property. Was the `bases-knowledge` skill; demoted to reference per the
rewrite design.

The vault's `~/Loose Ends/.claude/CLAUDE.md` `## Bases` section is the
canonical registry. Read it for the up-to-date list of bases, their
filters, and required properties; the table below is a quick map.

## First Step: Load Bases Registry

When invoked, read the bases registry from the vault's CLAUDE.md:

```
Read /Users/jacob/Loose Ends/.claude/CLAUDE.md
```

Look for the `## Bases` section which documents all bases, their purposes,
filters, and required properties.

## Base File Format

Bases are stored as `.base` files (YAML) in `Bases/` folder:

```yaml
filters:
  and:
    - file.inFolder("Waites/Repos")
formulas:
  Days Worked: note["working-days"].length
views:
  - type: table
    name: Backend
    order:
      - file.name
      - github-url
      - status
    groupBy:
      property: status
```

### Key Components

- **filters** — Determine which notes appear in the base
  - `file.inFolder("path")` — Notes in specific folder
  - `file.hasTag("tag")` — Notes with specific tag
  - `type == "value"` — Property equals value
  - `and: [...]` / `or: [...]` — Combine conditions

- **views** — Display configurations (table, cards, list)
  - `order` — Properties shown as columns
  - `groupBy` — Grouping property
  - `sort` — Sort order

- **formulas** — Calculated fields

## Context-to-Base Mapping

Map current work context to relevant bases:

| Context | Relevant Bases | Why |
|---------|----------------|-----|
| Working on a repo | Waites Repos | Find repo notes, patterns |
| Making architecture decision | ADRs | Check prior decisions |
| Debugging/fixing | Jira Tickets | Related tasks, history |
| Meeting notes | Meetings | Find related meetings |
| New tool/library | Software | Check if already tracked |
| New technique/pattern | Ideas | Capture for later |
| Created useful prompt | Prompts | Add to prompt library |
| Hobby project | Hobbies, Hobby Reviews | Track hobby work |

## Determining Required Properties

To create an entry that appears in a base correctly:

1. **Read the base file** to understand its filters
2. **Check existing entries** to see property patterns
3. **Ensure new note meets filter criteria**:
   - Correct folder location
   - Required tags
   - Required property values

### Example: Creating an ADR Entry

The ADRs base has filters:
```yaml
filters:
  or:
    - file.folder == "Waites/Decisions"
    - contains(tags, "type/adr")
```

Required properties (from views):
- `decision_date` — Date of decision
- `status` — proposed/accepted/deprecated/superseded
- `area` — Domain area
- `context` — Why this decision was needed
- `jira_tickets` — Related tickets
- `decision_makers` — Who decided

## Operations

### Find Relevant Base for Context

```bash
# User is working on Gateway Config API
# Query the Waites Repos base directly:
obsidian base:query path="Bases/Waites Repos.base" format=json
# Or search within the base's folder:
obsidian search query="Gateway" path="Waites/Repos" format=json
```

### Check if Entry Exists

Before suggesting a new base entry:
1. Identify the target base
2. Search notes matching that base's filter
3. Check if similar entry already exists

### Suggest Base Entry

When user discovers something worth capturing:

```markdown
> **Base suggestion**
> This rate limiting pattern could be an entry in your **Ideas** base.
>
> Required properties:
> - `status`: proposed
>
> Create this entry? [Yes / No]
```

## User's Bases Reference

### Work Bases

**Waites Repos** (`Bases/Waites Repos.base`)
- Filter: `file.inFolder("Waites/Repos")`
- Properties: github-url, used-in, uses, status
- Use: Repository documentation

**ADRs** (`Bases/ADRs.base`)
- Filter: `file.folder == "Waites/Decisions"` OR `tags contains "type/adr"`
- Properties: decision_date, status, area, context, jira_tickets, decision_makers
- Use: Architecture Decision Records

**Jira Tickets** (`Bases/Jira Tickets.base`)
- Filter: Complex (type == "task" with epic, or in Jira Tickets folder)
- Properties: title, estimated-days, status, epic, epic-order, type, working-days
- Use: Task tracking

**Meetings** (`Bases/Meetings.base`)
- Filter: Meeting notes folder
- Use: Meeting documentation

### Knowledge Bases

**Ideas** (`Bases/Ideas.base`)
- Filter: `file.inFolder("Inbox")`
- Properties: status
- Use: Capture ideas for later

**Prompts** (`Bases/Prompts.base`)
- Filter: `file.inFolder("Reference/Tools/Prompts")`
- Properties: description
- Use: Useful prompts library

**Software** (`Bases/Software.base`)
- Filter: Software Catalog folder OR AWS service notes
- Properties: category, solves, status, alternatives, url, integrations
- Use: Software/tool catalog

### Personal Bases

**Hobbies** (`Bases/Hobbies.base`)
- Filter: `file.inFolder("Hobbies")`
- Properties: status, time_commitment, financial_commitment
- Use: Hobby inventory

## Remember

- **Bases are views, not storage** — Notes live in folders, bases display them
- **Filters determine membership** — Note must match filter to appear in base
- **Properties shown in order** — The `order` array lists expected properties
- **Check before suggesting** — Search base for existing entries first
- **Prefer existing bases** — Suggest entries in user's established bases

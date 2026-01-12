---
name: vault-knowledge
description: >
  Use Skill(obsidian-curator:vault-knowledge) when working with Obsidian vault,
  taking notes, or when user mentions notes, documentation, capturing, or organizing.
  Reads vault conventions from ~/Loose Ends/.claude/CLAUDE.md for folder structure,
  templates, and patterns. NOT for simple note creation—use MCP tools directly.
allowed-tools:
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_complex_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_batch_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_list_files_in_dir
  - mcp__CodeMCP__Obsidian__obsidian_get_periodic_note
  - mcp__CodeMCP__Obsidian__obsidian_get_recent_periodic_notes
  - mcp__CodeMCP__Obsidian__obsidian_put_content
  - mcp__CodeMCP__Obsidian__obsidian_append_content
  - mcp__CodeMCP__Obsidian__obsidian_patch_content
  - Read
---

# Vault Knowledge

You are working with the user's Obsidian vault "Loose Ends".

## First Step: Load Vault Conventions

When invoked, immediately read the vault's CLAUDE.md for conventions:

```
Read /Users/jacob/Loose Ends/.claude/CLAUDE.md
```

This file contains:
- Folder structure and location decision tree
- Note types and templates for each type
- Frontmatter conventions
- Naming patterns
- Tag conventions
- Link patterns
- Dataview query examples
- Quick capture locations

## Core Principles

1. **Search first** — Always check if a related note already exists before suggesting a new one
2. **Edit over create** — Prefer appending to existing notes when content fits
3. **Link generously** — Add `[[wikilinks]]` to connect new content to existing notes
4. **Match templates** — Use the appropriate template structure for the note type
5. **Ask before writing** — Never create, edit, or delete notes without explicit user consent
6. **Never delete silently** — Deletion always requires explicit confirmation

## Working with the Vault

### Before Creating a Note

1. **Search for existing content**
   - Use `obsidian_simple_search` for keyword search
   - Use `obsidian_complex_search` with JsonLogic for folder/tag filtering
   - Check if the topic already has a note

2. **If existing note found**
   - Suggest appending/editing instead of creating new
   - Show where the addition would go
   - Explain why editing is better than creating

3. **If new note is needed**
   - Determine correct location using the decision tree from CLAUDE.md
   - Select appropriate template for the note type
   - Propose frontmatter fields
   - Suggest related notes to link to
   - Present full proposed content for approval

### Quick vs. Substantial Captures

- **Quick capture (1-3 sentences)** → Append to today's daily note under "## Captured"
- **Substantial topic (explanations, examples, context)** → Create proper note with full template

Use `obsidian_get_periodic_note(period="daily")` to get today's daily note.

### Location Determination

Follow the decision tree in the vault's CLAUDE.md:
- Waites work → `80 Waites/` (with appropriate subfolder)
- Technical patterns/reference → `50 Developer Notes/`
- Quick thoughts → Today's daily note
- Hobby-related → `20 Hobbies/`
- Career/professional → `70 Career/`

### Template Application

Match the template structure from CLAUDE.md based on note type:
- Daily notes — Include RAM, Captured, Session Summaries sections
- Reference notes — Include Overview, Key Points, Code Examples, Related sections
- Meeting notes — Include Attendees, Agenda, Notes, Action Items sections
- Repo notes — Include Overview, Key Files, Patterns & Gotchas, Dependencies sections
- MOC/Dashboard notes — Include dataview queries for folder listings

### Linking Strategy

When creating or editing notes:
1. Identify concepts mentioned that have their own notes
2. Search for those notes using `obsidian_simple_search`
3. Add `[[wikilinks]]` for first mention of each concept
4. Use `up` frontmatter field to link to parent MOC if hierarchical
5. Suggest adding new note to relevant MOCs/Dashboards

### MOC Maintenance

When creating notes in folders that have MOCs or Dashboards, ensure the new note is properly integrated.

**Detection:**
```python
# Check if folder has a dashboard/MOC
obsidian_list_files_in_dir("50 Developer Notes")
# Look for: "00 Dashboard.md", "[Folder Name] MOC.md", or similar
```

**Common MOC patterns:**
- `00 Dashboard.md` — Usually has dataview queries that auto-list notes
- `[Topic] MOC.md` — Map of Content with manually curated links
- Folder notes (same name as folder) — Index for the folder

**After creating a note:**

1. **Check for dataview queries:**
   - Read the folder's dashboard/MOC
   - Check if it uses dataview to auto-list notes
   - If yes, verify new note will be caught by the query (correct folder, tags, etc.)

2. **Check for manual links:**
   - If MOC has manually curated links (not dataview)
   - Suggest adding the new note to the appropriate section
   - Provide the exact link to add: `- [[New Note Name]]`

3. **Suggest MOC update if needed:**
   ```markdown
   The new note won't automatically appear in the folder's MOC.

   Add to `50 Developer Notes/00 Dashboard.md`?

   Under "## Patterns" section, add:
   - [[New Pattern Name]]

   [Add link / Skip]
   ```

**Example MOC check:**
```python
# After creating "Repository Pattern.md" in "50 Developer Notes/Patterns/"
# 1. Check parent folder for MOC
moc = obsidian_get_file_contents("50 Developer Notes/00 Dashboard.md")

# 2. Check if dataview will catch it
# If MOC has: ```dataview LIST FROM "50 Developer Notes" ```
# Then new note WILL appear automatically

# 3. If MOC has manual links under "## Patterns":
# Suggest adding: - [[Repository Pattern]]
```

**MOC types and behavior:**

| MOC Type | Auto-includes new notes? | Action needed |
|----------|--------------------------|---------------|
| Dataview query | Yes (if matches query) | Verify tags/folder match |
| Manual links | No | Suggest adding link |
| Hybrid (both) | Partial | Check both parts |

## Common Operations

### Get Today's Daily Note
```
obsidian_get_periodic_note(period="daily", type="content")
```

### Search for Related Notes
```
obsidian_simple_search(
  query="topic keywords",
  context_length=200
)
```

### Search Specific Folder
```json
obsidian_complex_search({
  "and": [
    {"glob": ["**/50 Developer Notes/**/*.md", {"var": "path"}]},
    {"regexp": ["pattern", {"var": "content"}]}
  ]
})
```

### Append to Daily Note
```
obsidian_append_content(
  filepath="01 Daily Notes/2025-01-02.md",
  content="\n- **10:30** — Captured thought\n"
)
```

### Create New Note
```
obsidian_put_content(
  filepath="50 Developer Notes/New Pattern.md",
  content="<full markdown content with frontmatter>"
)
```

## Remember

- **Always read CLAUDE.md first** when invoked to get current vault conventions
- **Search before suggesting** to avoid duplicate notes
- **Respect user's organization** — follow their folder structure and templates
- **Get permission** before any write operation
- **Present clearly** — show location, template, and content for approval

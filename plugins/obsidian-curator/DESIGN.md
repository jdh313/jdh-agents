# Obsidian Curator Plugin Design

> A Claude Code plugin that makes Claude a note-aware collaborator for your Obsidian vault.

## Overview

**Obsidian Curator** transforms Claude from a tool executor into a vault-aware collaborator that:
- Automatically searches your notes when relevant
- Suggests captures for reusable knowledge
- Helps edit, maintain, and organize your vault
- Respects your organization system and ADHD needs

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Reads are automatic** | Claude searches vault during exploration, stuck moments, decisions |
| **Writes need consent** | Never modify vault without explicit approval |
| **Edit over create** | Check for existing notes before suggesting new ones |
| **Link everything** | Propose `[[wikilinks]]` to connect new content |
| **Match your system** | Follow your folder structure, templates, naming conventions |
| **ADHD-friendly** | Batched suggestions, scannable output, one question at a time |
| **Never delete silently** | Deletion always requires explicit confirmation |

---

## Plugin Structure

```
obsidian-curator/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── vault-knowledge/
│   │   └── SKILL.md              # Points to vault's CLAUDE.md
│   ├── note-suggester/
│   │   └── SKILL.md              # Capture suggestion logic
│   └── contextual-search/
│       └── SKILL.md              # Auto-search triggers
├── agents/
│   ├── vault-curator.md          # Dedicated cleanup sessions
│   └── note-editor.md            # Complex editing tasks
├── commands/
│   ├── vault-health.md           # Run vault audit
│   ├── capture.md                # Quick capture to daily note
│   └── cleanup.md                # Start cleanup session
├── hooks/
│   └── hooks.json                # Session end automation
└── README.md

# Vault knowledge lives separately:
~/Loose Ends/.claude/CLAUDE.md    # Folder structure, templates, conventions
```

---

## Component Details

### Skills (Auto-Triggered)

Skills teach Claude specialized knowledge that triggers automatically based on context.

---

#### 1. `vault-knowledge` — Core Vault Awareness

**Purpose:** Points Claude to vault conventions stored in `~/Loose Ends/.claude/CLAUDE.md`.

**Triggers:** Always active when Obsidian tools are available.

**Key Design:** Vault knowledge lives in the vault itself, not in the plugin. This keeps
the plugin portable and makes vault conventions easy to update alongside the vault.

**SKILL.md Content:**
```yaml
---
name: vault-knowledge
description: >
  INVOKE when working with Obsidian vault, taking notes, or when user mentions
  notes, documentation, capturing, or organizing. Reads vault conventions from
  ~/Loose Ends/.claude/CLAUDE.md for folder structure, templates, and patterns.
allowed-tools:
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_complex_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_list_files_in_dir
  - mcp__CodeMCP__Obsidian__obsidian_get_periodic_note
  - Read
---

# Vault Knowledge

You are working with the user's Obsidian vault "Loose Ends".

## First Step

Read the vault's CLAUDE.md for conventions:
```
Read ~/Loose Ends/.claude/CLAUDE.md
```

This file contains:
- Folder structure and location decision tree
- Note types and templates
- Frontmatter conventions
- Naming patterns
- Tag conventions
- Link patterns

## Core Principles

1. **Search first** — Check if a related note already exists
2. **Edit over create** — Append to existing notes when possible
3. **Link generously** — Add `[[wikilinks]]` to connect content
4. **Match templates** — Use the appropriate structure for the note type
5. **Ask before writing** — Never modify without consent
```

**No supporting files needed** — all vault knowledge lives in `~/Loose Ends/.claude/CLAUDE.md`.

---

#### Legacy Reference (for context)

The original design included bundled `folder-structure.md`, `templates.md`, and
`frontmatter.md` files. These have been consolidated into the vault's CLAUDE.md.

Example of what was in `folder-structure.md`:
```markdown
# Folder Structure

## Numbered Areas (Primary Organization)

| Folder | Purpose | Example Content |
|--------|---------|-----------------|
| `01 Daily Notes` | Daily capture + git summaries | `2025-10-23.md` |
| `10 Personal and Admin` | Personal life management | Appointments, Health |
| `20 Hobbies` | Hobby documentation | 3D Printing, Homelab |
| `30 Productivity and Tools` | Software catalog | Tool notes |
| `50 Developer Notes` | Technical reference | Patterns, Python attrs |
| `70 Career` | Career history | 2022-Synthetik, 2025-Waites |
| `80 Waites` | Current work | ADRs, Meetings, Projects, Repos |

## Location Decision Tree

When suggesting where to put content:

1. **Is it about current work at Waites?** → `80 Waites/`
   - ADR → `80 Waites/ADRs/`
   - Meeting notes → `80 Waites/Meetings/`
   - Project docs → `80 Waites/Projects and Tasks/`
   - Repo notes → `80 Waites/Repos/`

2. **Is it a reusable technical pattern?** → `50 Developer Notes/`
   - Design pattern → `50 Developer Notes/Patterns/`
   - Language/library reference → `50 Developer Notes/`

3. **Is it a quick thought or capture?** → Today's daily note
   - Use `obsidian_get_periodic_note(period="daily")`
   - Append under "## Captured" or "## RAM"

4. **Is it hobby-related?** → `20 Hobbies/[Hobby Name]/`

5. **Is it career/professional development?** → `70 Career/`

## Folder Notes (MOCs/Dashboards)

Most folders have an index note:
- `00 Dashboard.md` — Uses dataview for dynamic listing
- `[Topic] MOC.md` — Map of Content with curated links

When creating notes in a folder, verify they'll be caught by the dataview query
or suggest adding to the MOC.
```

`templates.md`:
```markdown
# Note Templates

## Daily Note
```markdown
---
date created: {{date}} {{time}}
date_modified: {{date}} {{time}}
---

# {{date:YYYY-MM-DD}}

## RAM
- Quick thoughts go here

## Captured
- Session captures appended here

## Git Activity
<!-- Auto-generated -->
```

## Reference Note (Developer Notes)
```markdown
---
date created: {{date}} {{time}}
date_modified: {{date}} {{time}}
tags: []
aliases: []
up: "[[Parent MOC]]"
---

# Title

## Overview
Brief description of the concept.

## Key Points
- Point 1
- Point 2

## Code Examples
\`\`\`python
# Example code
\`\`\`

## Related
- [[Related Note 1]]
- [[Related Note 2]]
```

## Meeting Note
```markdown
---
date created: {{date}} {{time}}
date_modified: {{date}} {{time}}
projects: []
---

# {{date:YYYY-MM-DD}} Meeting Topic

## Attendees
-

## Agenda
- [ ] Item 1
- [ ] Item 2

## Notes

## Action Items
- [ ] Action 1
- [ ] Action 2
```

## Project/Repo Note
```markdown
---
date created: {{date}} {{time}}
date_modified: {{date}} {{time}}
github-url:
status: active
aliases: []
---

# Project Name

## Overview

## Key Files

## Patterns & Gotchas

## Dependencies

## Related
- [[Related Project]]
```
```

`frontmatter.md`:
```markdown
# Frontmatter Conventions

## Universal Fields (All Notes)
```yaml
date created: 2025-01-02 10:30
date_modified: 2025-01-02 10:30
```

## By Note Type

### Daily Notes
```yaml
git_commits: 6
git_last_updated: 2025-01-02T10:30:00
git_repos: [repo1, repo2]
```

### Reference Notes
```yaml
tags: [python, patterns]
aliases: [Alternative Name]
up: "[[Parent MOC]]"
```

### Meeting Notes
```yaml
projects: [["Project Name"]]
```

### Repo Notes
```yaml
github-url: https://github.com/org/repo
status: active  # or: archived, deprecated
aliases: [short-name]
```

### Folder Notes
```yaml
type: folder-note
BC-folder-note-field: true
```

## Tag Conventions
- Hierarchical with `/`: `#topic/dev/patterns`
- Kebab-case: `#3d-printing`, not `#3D_Printing`
- Common prefixes: `#type/`, `#topic/`, domain tags
```

---

#### 2. `note-suggester` — Capture Recognition

**Purpose:** Recognizes when something is worth capturing and suggests it.

**Triggers:** During coding sessions when reusable knowledge emerges.

**SKILL.md Content:**
```yaml
---
name: note-suggester
description: >
  INVOKE during coding sessions to recognize reusable knowledge worth capturing.
  Suggests note captures inline when: debugging approaches work, patterns emerge,
  decisions are made with rationale, or techniques could apply elsewhere.
  Suggests inline (not interrupting) and batches for end-of-session summary.
---

# Note Suggester

You help the user build their knowledge base by recognizing when something
is worth capturing in Obsidian.

## What's Worth Capturing?

Suggest a note when you encounter:

1. **Decisions with rationale** — "We chose X because Y"
2. **Debugging approaches that worked** — Steps that solved a tricky problem
3. **Patterns or techniques** — Reusable code patterns, architectural approaches
4. **Gotchas or surprises** — Things that weren't obvious, edge cases
5. **Cross-project knowledge** — Something useful beyond this specific task

## What's NOT Worth Capturing?

Skip suggesting for:
- Routine refactors following existing patterns
- Typo fixes
- Single-use solutions
- Things already documented elsewhere

## How to Suggest

### Inline (During Work)
Keep it brief and non-interrupting:
```
💡 This debugging approach might be worth capturing in `50 Developer Notes/`.
```

### Batch Tracking
Keep a mental list of potential captures. At session end, present them together:
```
## Session Captures

During this session, these items seemed worth noting:

1. **Lambda cold start mitigation** — The caching approach we used
   → Suggested location: `50 Developer Notes/Patterns/`

2. **Gateway API rate limiting gotcha** — The 429 retry behavior
   → Suggested location: `80 Waites/Repos/Gateway Config API.md` (append)

Want me to draft any of these?
```

## Size Guidance

- **Quick capture** (1-3 sentences) → Append to daily note
- **Substantial topic** (explanation, examples, context) → Proper note with template

## Always Remember

- **Ask before writing** — Never create/edit without consent
- **Check existing notes first** — Maybe this extends an existing note
- **Suggest location + template** — Make it easy to approve
```

---

#### 3. `contextual-search` — Auto-Search Triggers

**Purpose:** Automatically searches vault during exploration, stuck moments, and decisions.

**Triggers:** When Claude detects relevant context.

**SKILL.md Content:**
```yaml
---
name: contextual-search
description: >
  INVOKE automatically during: (1) topic exploration - search for existing notes
  on the topic, (2) debugging/stuck - search for similar past problems or solutions,
  (3) decision points - search for prior art, past decisions, or related context.
  Weave findings into responses naturally without asking permission to search.
allowed-tools:
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_complex_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
---

# Contextual Search

You automatically search the user's Obsidian vault when context is relevant.
Do NOT ask permission to search — reads are automatic.

## When to Search

### 1. Topic Exploration
User is researching or exploring a topic.
```
Triggers: "How does X work?", "What's the best way to...", "I'm looking into..."
Action: Search for existing notes on the topic
```

### 2. Stuck/Debugging
User is blocked on a problem.
```
Triggers: "This isn't working", "I'm getting an error", "Why is this failing?"
Action: Search for similar problems, debugging approaches, past incidents
```

### 3. Decision Points
User needs to make a choice.
```
Triggers: "Should we use X or Y?", "What's the best approach?", "How did we handle this before?"
Action: Search for prior decisions, ADRs, related context
```

## Search Strategy

1. **Start broad** — `obsidian_simple_search` with key terms
2. **Narrow if needed** — `obsidian_complex_search` with JsonLogic for specific folders/tags
3. **Read relevant hits** — `obsidian_get_file_contents` for promising results
4. **Weave into response** — Reference findings naturally:
   ```
   Based on your notes about the SQS incident from October, you previously
   solved similar Lambda timeout issues by...
   ```

## Search Patterns

### By Topic Area
```python
# Work-related (Gateway, Waites)
obsidian_complex_search({"glob": ["**/80 Waites/**/*.md", {"var": "path"}]})

# Technical patterns
obsidian_complex_search({"glob": ["**/50 Developer Notes/**/*.md", {"var": "path"}]})

# Recent daily notes
obsidian_get_recent_periodic_notes(period="daily", limit=7, include_content=True)
```

### By Content
```python
# Find notes mentioning specific tech
obsidian_simple_search(query="Lambda cold start", context_length=200)

# Find meeting notes with action items
obsidian_complex_search({
  "and": [
    {"glob": ["**/Meetings/**/*.md", {"var": "path"}]},
    {"regexp": ["- \\[ \\]", {"var": "content"}]}
  ]
})
```

## What to Do With Results

- **Relevant hit:** Quote or summarize, link to note path
- **No hits:** Proceed without mentioning the search
- **Partial match:** Mention it might be worth updating that note
```

---

### Agents (Subagents for Complex Tasks)

Agents are specialized subagents with their own context for complex operations.

---

#### 1. `vault-curator` — Dedicated Cleanup Sessions

**Purpose:** Runs comprehensive vault audits and maintenance.

**Invocation:** Via `/cleanup` command or "let's do vault maintenance"

**vault-curator.md:**
```markdown
---
name: vault-curator
description: >
  Specialized agent for vault maintenance and cleanup. Invoke for dedicated
  cleanup sessions, finding orphaned notes, identifying duplicates, proposing
  merges/splits, and updating notes to follow conventions.
tools:
  - mcp__CodeMCP__Obsidian__obsidian_list_files_in_vault
  - mcp__CodeMCP__Obsidian__obsidian_list_files_in_dir
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_complex_search
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_batch_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_get_recent_changes
---

# Vault Curator

You are a vault maintenance specialist. Your job is to help the user keep their
Obsidian vault healthy, organized, and useful.

## Maintenance Categories

### 1. Orphaned Notes
Notes with no incoming links and not in any MOC/Dashboard.

**Detection:**
- List all notes in a folder
- Check each for backlinks (search for `[[Note Name]]`)
- Flag those with zero incoming links

**Resolution options:**
- Link from related notes
- Add to parent MOC/Dashboard
- Suggest deletion (with confirmation)

### 2. Duplicate/Overlapping Notes
Notes covering the same topic.

**Detection:**
- Search for similar titles
- Look for notes with overlapping content
- Check for multiple notes on same concept

**Resolution:**
- Propose merge (keep one, incorporate content from other)
- Never delete without explicit permission

### 3. Notes Needing Splits
Single notes covering too many topics.

**Detection:**
- Notes over 500 lines
- Multiple H1 headers
- Distinct topic sections

**Resolution:**
- Propose split into focused notes
- Suggest linking structure

### 4. Convention Violations
Notes not following vault patterns.

**Detection:**
- Missing required frontmatter
- Wrong folder location
- Inconsistent naming
- Missing `up` field for hierarchy

**Resolution:**
- Propose corrections one at a time

### 5. Stale Notes
Notes that may need updating.

**Detection:**
- `date_modified` older than 6 months
- References to deprecated tools/patterns
- Incomplete sections

**Resolution:**
- Surface for review
- Suggest updates

## Interaction Style

### ADHD-Friendly Approach
1. **One category at a time** — Don't overwhelm with all issues
2. **Show progress** — "Found 3/7 orphaned notes, fixed 2"
3. **Batch actions** — "Here are 5 notes that need frontmatter. Fix all?"
4. **Clear choices** — Present options, recommend one

### Session Flow
```
1. Ask which maintenance type to focus on
2. Run detection for that category
3. Present findings in scannable list
4. Process issues one by one (or batch if similar)
5. Summarize what was done
6. Ask if user wants to continue with another category
```

### Output Format
```markdown
## Orphaned Notes (3 found)

1. **Python Decorators.md** (50 Developer Notes/)
   - No incoming links
   - Recommendation: Link from [[Python attrs Library]]
   - [Link it] [Delete] [Skip]

2. **Old Meeting Notes.md** (80 Waites/Meetings/)
   - No incoming links, last modified 8 months ago
   - Recommendation: Archive or delete
   - [Archive] [Delete] [Skip]

Progress: 1/3 processed
```
```

---

#### 2. `note-editor` — Complex Editing Tasks

**Purpose:** Handles complex note editing, merging, and restructuring.

**Invocation:** When editing requires significant restructuring.

**note-editor.md:**
```markdown
---
name: note-editor
description: >
  Specialized agent for complex note editing operations: merging multiple notes,
  restructuring content, adding comprehensive links, updating to new templates,
  and enriching sparse notes with detail.
tools:
  - mcp__CodeMCP__Obsidian__obsidian_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_batch_get_file_contents
  - mcp__CodeMCP__Obsidian__obsidian_simple_search
  - mcp__CodeMCP__Obsidian__obsidian_put_content
  - mcp__CodeMCP__Obsidian__obsidian_patch_content
  - mcp__CodeMCP__Obsidian__obsidian_append_content
---

# Note Editor

You are a note editing specialist. You handle complex operations that require
careful restructuring while preserving the user's voice and content.

## Operations

### Merge Notes
Combine multiple notes on the same topic.

**Process:**
1. Read all source notes
2. Identify unique content from each
3. Propose merged structure
4. Show preview before writing
5. After merge, suggest what to do with source notes (archive/delete)

### Restructure Note
Reorganize a note's structure.

**Process:**
1. Read current note
2. Analyze sections and flow
3. Propose new structure
4. Show before/after comparison
5. Apply only with approval

### Template Migration
Update notes to follow new/updated templates.

**Process:**
1. Read note and target template
2. Map existing content to template sections
3. Add missing frontmatter fields
4. Preserve all existing content
5. Show changes before applying

### Link Enrichment
Add links to related notes throughout a note.

**Process:**
1. Read target note
2. Search for related notes by topic
3. Identify opportunities for `[[wikilinks]]`
4. Propose additions (show in context)
5. Apply approved links

### Content Enrichment
Expand sparse notes with more detail.

**Process:**
1. Read sparse note
2. Search vault for related content
3. Search Graphiti for relevant learnings
4. Propose additions that maintain user's voice
5. Apply only with approval

## Rules

1. **Never lose content** — Merges and restructures preserve everything
2. **Show before applying** — Always preview changes
3. **Maintain voice** — Don't rewrite user's words, reorganize them
4. **One operation at a time** — Don't combine merge + restructure
5. **Explicit consent** — Every write requires approval
```

---

### Commands (Explicit User Invocation)

Commands are slash commands the user explicitly runs.

---

#### 1. `/vault-health` — Run Vault Audit

**vault-health.md:**
```markdown
---
description: Run a health check on your Obsidian vault to find issues
---

# Vault Health Check

Run a comprehensive health check on your Obsidian vault.

## What This Checks

1. **Orphaned notes** — Notes with no incoming links
2. **Broken links** — `[[Links]]` pointing to non-existent notes
3. **Missing frontmatter** — Notes without required metadata
4. **Stale notes** — Notes not updated in 6+ months
5. **Convention violations** — Wrong folders, naming issues

## Usage

```
/obsidian-curator:vault-health
/obsidian-curator:vault-health --focus=orphans
/obsidian-curator:vault-health --folder="50 Developer Notes"
```

## Output

Returns a scannable report with:
- Issue counts by category
- Top 5 issues in each category
- Recommended actions

Use `/obsidian-curator:cleanup` to start fixing issues.
```

---

#### 2. `/capture` — Quick Capture to Daily Note

**capture.md:**
```markdown
---
description: Quickly capture a thought or note to today's daily note
---

# Quick Capture

Append a quick capture to today's daily note.

## Usage

```
/obsidian-curator:capture This is my quick thought
/obsidian-curator:capture Debugging approach: restart the service first
```

## Behavior

1. Gets today's daily note via `obsidian_get_periodic_note`
2. Appends under "## Captured" section (or creates it)
3. Adds timestamp prefix
4. Confirms capture was added

## Format

```markdown
## Captured

- **10:30** — This is my quick thought
- **10:45** — Debugging approach: restart the service first
```

## Arguments

- `$ARGUMENTS` — The text to capture

If no arguments provided, prompts for what to capture.
```

---

#### 3. `/cleanup` — Start Cleanup Session

**cleanup.md:**
```markdown
---
description: Start an interactive vault cleanup session
---

# Vault Cleanup Session

Start an interactive session to clean up and maintain your vault.

## Usage

```
/obsidian-curator:cleanup
/obsidian-curator:cleanup --type=orphans
/obsidian-curator:cleanup --type=duplicates
```

## Session Flow

1. **Choose focus area** (or specify with `--type`):
   - Orphaned notes
   - Duplicates
   - Stale notes
   - Convention violations
   - MOC maintenance

2. **Review findings** one category at a time

3. **Process issues** with clear choices:
   - Fix / Skip / Batch fix all similar

4. **Progress tracking** throughout

5. **Summary** at end of session

## ADHD-Friendly Features

- One question at a time
- Clear progress indicators
- Batch operations for similar issues
- Can stop anytime without losing progress
```

---

### Hooks (Event-Driven Automation)

Hooks trigger automatically on specific events.

---

**hooks.json:**
```json
{
  "hooks": [
    {
      "event": "Stop",
      "type": "prompt",
      "prompt": "Before ending this session, check if there are note suggestions to present:\n\n1. Were there any debugging approaches, patterns, or decisions worth capturing?\n2. If yes, present them in a batched summary.\n3. Ask if user wants any captured to daily note or proper notes.\n4. If working on a specific repo, ask if the repo note should be updated.\n\nKeep it brief - if nothing worth capturing, just end normally."
    },
    {
      "event": "Stop",
      "type": "prompt",
      "prompt": "Append a brief session summary to today's daily note:\n\n1. Get today's daily note\n2. Append under '## Session Summaries' (create if missing)\n3. Include: repos touched, key decisions, captures made\n4. Keep it to 3-5 bullet points max\n\nAsk permission before appending."
    }
  ]
}
```

---

## Proactive Features Implementation

### 1. Session Summaries (via Stop hook)
- Triggered at session end
- Appends to daily note under "## Session Summaries"
- Includes: repos touched, decisions made, captures
- Asks permission before writing

### 2. Meeting Follow-up (via contextual-search skill)
- When working on a project, search recent meeting notes
- Surface unchecked action items that seem relevant
- Present contextually, not as interruption

### 3. MOC Maintenance (via vault-knowledge skill)
- When creating notes in a folder with `00 Dashboard.md`
- Check if note will be caught by dataview query
- Suggest adding to MOC if needed

### 4. Repo Note Enrichment (via note-suggester skill)
- When working on a known repo (e.g., Gateway Config API)
- At session end, check if new learnings should go to repo note
- Propose specific additions

---

## ADHD Accommodations

Built into all components:

| Accommodation | Implementation |
|---------------|----------------|
| **One question at a time** | Never present multiple decisions simultaneously |
| **Batching** | Collect suggestions, present together at natural breakpoints |
| **Progress visibility** | "Fixed 3/7 issues" style feedback |
| **Scannable output** | Lists, tables, headers — no walls of text |
| **Clear defaults** | Recommend one option, easy to accept |
| **Forgiving** | Ignored suggestions don't pile up or nag |
| **Low activation energy** | One command starts a guided session |

---

## Integration Points

### With Existing MCP Tools
Uses your current Obsidian Local REST API tools:
- `obsidian_simple_search` — Text search
- `obsidian_complex_search` — JsonLogic queries
- `obsidian_get_file_contents` — Read notes
- `obsidian_batch_get_file_contents` — Read multiple
- `obsidian_put_content` — Create/overwrite
- `obsidian_append_content` — Add to notes
- `obsidian_patch_content` — Insert at heading/block
- `obsidian_get_periodic_note` — Daily/weekly notes
- `obsidian_get_recent_changes` — Recently modified

### With Graphiti Memory
- Vault captures = for human (Obsidian)
- Agent learnings = for Claude (Graphiti)
- No duplication needed — different audiences

### With Existing Skills
- Works alongside `context-gatherer` at session start
- Complements `learnings-recorder` at session end
- Doesn't conflict with existing `obsidian-assistant`

---

## Implementation Priority

### Phase 1: Core (MVP)
1. `vault-knowledge` skill with your folder/template docs
2. `contextual-search` skill for auto-search
3. `/capture` command for quick notes

### Phase 2: Suggestions
4. `note-suggester` skill
5. Stop hooks for session summary + capture batching

### Phase 3: Maintenance
6. `vault-curator` agent
7. `/vault-health` command
8. `/cleanup` command

### Phase 4: Advanced
9. `note-editor` agent
10. Meeting follow-up integration
11. Repo note enrichment

---

## Design Decisions

| Question | Decision |
|----------|----------|
| **Vault knowledge location** | File in vault: `~/Loose Ends/.claude/CLAUDE.md` |
| **Session summary frequency** | Significant sessions only |
| **Existing obsidian-assistant** | Replace (single source of truth) |

---

## Next Steps

1. Review this design
2. Adjust based on feedback
3. Implement Phase 1 components
4. Test with real vault operations
5. Iterate based on usage

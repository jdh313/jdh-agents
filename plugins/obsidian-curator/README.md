# Obsidian Curator

A Claude Code plugin that makes Claude a note-aware collaborator for your Obsidian vault.

## What It Does

Obsidian Curator transforms Claude from a tool executor into a vault-aware collaborator that:
- **Automatically searches** your notes when relevant (no permission needed)
- **Suggests captures** for reusable knowledge (with your approval)
- **Helps edit and maintain** your vault (following your conventions)
- **Respects your organization** (folders, templates, ADHD needs)

## Features

### Automatic (No Action Needed)

These features work in the background without any commands.

#### 🔍 Contextual Search

Claude automatically searches your vault when relevant:
- **Topic exploration** — "How does X work?" → checks your notes first
- **Debugging** — "This is failing" → looks for similar past problems
- **Decision points** — "Should we use X or Y?" → finds prior decisions, ADRs

Findings are woven naturally into responses:
```
You: "How did we handle authentication in the Gateway API?"
Claude: "According to your Gateway API repo note, authentication uses JWT tokens..."
```

#### 📝 Vault Awareness

Claude understands your vault's organization:
- Folder structure (PARA-inspired numbered areas)
- Note types and templates
- Naming conventions and frontmatter
- Tag patterns and link conventions

Conventions are stored in `~/Loose Ends/.claude/CLAUDE.md` (easy to update).

#### 📋 Meeting Follow-up

Surfaces relevant action items when working on related code:

```markdown
> 📋 Found a related action item from your 1-on-1 on 2025-01-02:
> - [ ] Update Gateway API rate limiting documentation
>
> Since we're touching this code, want to update the docs too?
```

#### 🔄 Repo Note Suggestions

When working on a known repo, Claude notices patterns and gotchas worth documenting:

```markdown
> 💡 This rate limiting pattern might be worth adding to the Gateway Config API repo note.
```

---

### On Request (Commands & Requests)

Explicit actions you can trigger.

#### ⚡ Quick Capture

`/obsidian-curator:capture` — Append quick thoughts to today's daily note:

```
/obsidian-curator:capture Lambda cold starts fixed with provisioned concurrency
```

Result in daily note:
```markdown
## Captured
- **14:23** — Lambda cold starts fixed with provisioned concurrency
```

#### 🏥 Vault Health Check

`/obsidian-curator:vault-health` — Audit your vault's health:

```
/obsidian-curator:vault-health
/obsidian-curator:vault-health --focus=orphans
/obsidian-curator:vault-health --folder="50 Developer Notes"
```

Returns a scannable report:
```markdown
## Vault Health Report

| Category | Issues | Status |
|----------|--------|--------|
| Orphaned notes | 7 | Needs attention |
| Broken links | 0 | Healthy |
| Missing frontmatter | 3 | Minor |

**Overall Health:** 85/100
```

#### 🧹 Interactive Cleanup

`/obsidian-curator:cleanup` — Start a guided cleanup session:

```
/obsidian-curator:cleanup
/obsidian-curator:cleanup --type=orphans
/obsidian-curator:cleanup --type=duplicates
```

Guides you through fixing:
- **Orphaned notes** — Link, add to MOC, or archive
- **Duplicates** — Merge or differentiate
- **Stale notes** — Update, archive, or mark reviewed
- **Convention violations** — Fix frontmatter, move to correct folders

ADHD-friendly: one question at a time, progress tracking, batch operations.

#### ✏️ Complex Editing

Ask Claude to perform advanced note operations:

| Request | What Happens |
|---------|--------------|
| "Merge these Python notes" | Combines content, preserves everything |
| "Restructure this note" | Reorganizes sections with preview |
| "Update this to the new template" | Migrates to current template format |
| "Add links to this note" | Finds and adds relevant `[[wikilinks]]` |
| "Flesh out this stub" | Enriches from vault and memory |

All operations show previews before applying changes.

---

### At Session End (Automatic Prompts)

These trigger when you finish a session.

#### 💡 Capture Suggestions

Reviews the session for knowledge worth saving:

```markdown
## Session Captures

During this session, these items seemed worth noting:

| # | Topic | Type | Location |
|---|-------|------|----------|
| 1 | Lambda cold start fix | Pattern | `50 Developer Notes/Patterns/` |
| 2 | Gateway 429 behavior | Gotcha | `80 Waites/Repos/Gateway Config API.md` |

Draft any of these? (1, 2, both, or skip)
```

Only appears if there's something worth capturing.

#### 📓 Session Summary

For significant work sessions, offers to log a summary:

```markdown
Want me to add a summary to today's daily note?

### 14:30 — Gateway API Rate Limiting
- Implemented exponential backoff for 429 responses
- Updated repo note with new pattern
- Tests passing

Add to daily note? [Yes / Edit / Skip]
```

Skips silently for quick questions or minor sessions.

## Prerequisites

1. **Obsidian** with **Local REST API plugin** installed and running
2. **Claude Code** with MCP Obsidian tools configured
3. **Vault CLAUDE.md** — Create `~/Loose Ends/.claude/CLAUDE.md` (see setup below)

## Installation

```bash
# From your Claude Code plugins directory
cd ~/.claude/plugins/marketplaces/your-marketplace/plugins

# Clone or copy the plugin
cp -r /path/to/cc-marketplace/plugins/obsidian-curator .

# Install the plugin
claude plugin install obsidian-curator

# Restart Claude Code to load the plugin
```

## Setup

### Step 1: Create Vault CLAUDE.md

The plugin reads vault conventions from `~/Loose Ends/.claude/CLAUDE.md`.

**Option A:** This file was created during plugin setup. Verify it exists:
```bash
ls -la ~/Loose\ Ends/.claude/CLAUDE.md
```

**Option B:** If missing, create it manually or use the template in `DESIGN.md`.

### Step 2: Verify Obsidian MCP Tools

Ensure these MCP tools are available:
- `mcp__CodeMCP__Obsidian__obsidian_simple_search`
- `mcp__CodeMCP__Obsidian__obsidian_complex_search`
- `mcp__CodeMCP__Obsidian__obsidian_get_file_contents`
- `mcp__CodeMCP__Obsidian__obsidian_get_periodic_note`
- `mcp__CodeMCP__Obsidian__obsidian_put_content`
- `mcp__CodeMCP__Obsidian__obsidian_append_content`

Test by running:
```
/tools | grep obsidian
```

### Step 3: Test the Plugin

1. **Test contextual search:**
   ```
   Ask Claude: "How does Python's attrs library work?"
   ```
   Claude should search your vault and reference any existing notes.

2. **Test quick capture:**
   ```
   /obsidian-curator:capture Test capture from new plugin
   ```
   Check `01 Daily Notes/YYYY-MM-DD.md` for the capture.

3. **Test vault knowledge:**
   ```
   Ask Claude: "Where should I put a note about a new debugging pattern?"
   ```
   Claude should reference your folder structure and suggest `50 Developer Notes/Patterns/`.

## Usage

### Automatic Search

Just ask questions. Claude will search your vault when relevant:

```
You: "How did we handle authentication in the Gateway API?"
Claude: [Searches vault, finds Gateway Config API repo note]
"According to your Gateway API repo note, authentication uses JWT tokens..."
```

### Quick Captures

Capture quick thoughts to today's daily note:

```
/obsidian-curator:capture Learned that FastAPI auto-validates with Pydantic
```

### Creating Proper Notes

Ask Claude to create a note. It will:
1. Search for existing related notes
2. Suggest the right location and template
3. Show you the full content for approval
4. Create it only after you confirm

```
You: "Create a note about the Repository Pattern"
Claude: [Searches, finds no existing note]
"I'll create a reference note in 50 Developer Notes/Patterns/Repository Pattern.md

Here's the proposed content:
[Shows full markdown with template]

Create this note?"

You: "Yes"
Claude: [Creates note]
```

## How It Works

### Skills (Auto-Triggered)

| Skill | Triggers When | What It Does |
|-------|---------------|--------------|
| `vault-knowledge` | Working with Obsidian | Reads `~/Loose Ends/.claude/CLAUDE.md` for conventions |
| `contextual-search` | Exploring, stuck, or deciding | Searches vault, weaves findings into responses |
| `note-suggester` | During coding sessions | Recognizes capture-worthy moments, suggests notes |
| `meeting-followup` | Working on projects | Surfaces relevant unchecked action items |
| `repo-enrichment` | Working on known repos | Suggests updates to repo notes |

### Hooks (Automatic)

| Hook | Event | What It Does |
|------|-------|--------------|
| Capture suggestions | Stop | Reviews session, presents batched capture suggestions |
| Session summary | Stop | Offers to append work summary to daily note |

### Agents (Subagents)

| Agent | Purpose | Invocation |
|-------|---------|------------|
| `vault-curator` | Interactive cleanup sessions | Via `/cleanup` command |
| `note-editor` | Complex note editing (merge, restructure) | Via direct request |

### Commands (Explicit)

| Command | Purpose |
|---------|---------|
| `/obsidian-curator:capture` | Quick capture to daily note |
| `/obsidian-curator:vault-health` | Run vault health audit |
| `/obsidian-curator:cleanup` | Start interactive cleanup session |

## Principles

1. **Reads are automatic** — Claude searches without asking
2. **Writes need consent** — Never modifies vault without approval
3. **Edit over create** — Prefers appending to existing notes
4. **Link everything** — Proposes `[[wikilinks]]` to connect content
5. **Match your system** — Follows your folders, templates, conventions
6. **ADHD-friendly** — Scannable output, batched suggestions, one question at a time

## Configuration

### Vault Path

Default: `~/Loose Ends`

To use a different vault, edit your vault's CLAUDE.md path in:
- `skills/vault-knowledge/SKILL.md` (line ~90)
- `skills/contextual-search/SKILL.md` (if it references the path)

### Template Customization

Update `~/Loose Ends/.claude/CLAUDE.md` with your:
- Folder structure changes
- New note templates
- Modified frontmatter fields
- Different naming conventions

The plugin reads from there, so changes apply immediately.

## Troubleshooting

### "No vault conventions found"
- Verify `~/Loose Ends/.claude/CLAUDE.md` exists
- Check the path in `skills/vault-knowledge/SKILL.md`

### "Obsidian MCP tools not available"
- Ensure Obsidian is running
- Verify Local REST API plugin is enabled
- Check MCP server configuration in Claude Code

### Quick capture not working
- Verify today's daily note exists: `01 Daily Notes/YYYY-MM-DD.md`
- Check daily note has proper frontmatter
- Ensure Obsidian API is responding

### Search finds nothing
- Check spelling and keywords
- Try broader search terms
- Verify notes exist in the expected location
- Use `/tools mcp__CodeMCP__Obsidian__obsidian_simple_search` to test directly

## Contributing

See `DESIGN.md` for the full plugin architecture and design decisions.

## License

MIT

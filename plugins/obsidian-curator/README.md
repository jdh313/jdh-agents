# Obsidian Curator

A Claude Code plugin that makes Claude a note-aware collaborator for your Obsidian vault.

## What It Does

Obsidian Curator transforms Claude from a tool executor into a vault-aware collaborator that:
- **Automatically searches** your notes when relevant (no permission needed)
- **Suggests captures** for reusable knowledge (with your approval)
- **Helps edit and maintain** your vault (following your conventions)
- **Respects your organization** (folders, templates, ADHD needs)

## Features

### Phase 1: Core

#### 🔍 Contextual Search
Claude automatically searches your vault during:
- **Topic exploration** — "How does X work?" → checks your notes first
- **Debugging** — "This is failing" → looks for similar past problems
- **Decision points** — "Should we use X or Y?" → finds prior decisions, ADRs

No permission needed for searches. Findings are woven naturally into responses.

#### 📝 Vault Knowledge
Claude understands your vault's:
- Folder structure (PARA-inspired numbered areas)
- Note types and templates
- Naming conventions and frontmatter
- Tag patterns and link conventions

Vault conventions are stored in `~/Loose Ends/.claude/CLAUDE.md` (easy to update).

#### ⚡ Quick Capture
`/obsidian-curator:capture` — Append quick thoughts to today's daily note with timestamps.

```
/obsidian-curator:capture Lambda cold starts fixed with provisioned concurrency
```

Result:
```markdown
## Captured
- **14:23** — Lambda cold starts fixed with provisioned concurrency
```

### Phase 2: Suggestions

#### 💡 Note Suggester

Claude recognizes capture-worthy moments during your session:
- **Debugging wins** — Steps that solved a tricky problem
- **Patterns discovered** — Reusable code patterns, architectural approaches
- **Decisions made** — Choices with clear rationale (ADR candidates)
- **Gotchas found** — Things that weren't obvious, edge cases

Suggestions are non-interrupting:
- **Inline hints** — Brief suggestion at end of response when relevant
- **Batched summary** — All captures presented together at session end

#### 🔔 Session End Hooks

At session end, Claude automatically:
1. Reviews the session for capture-worthy items
2. Presents a batched summary if anything is worth noting
3. Asks which items to draft (if any)

Example session-end summary:
```markdown
## Session Captures

| # | Topic | Type | Location |
|---|-------|------|----------|
| 1 | Lambda cold start fix | Pattern | `50 Developer Notes/Patterns/` |
| 2 | Gateway 429 behavior | Gotcha | `80 Waites/Repos/Gateway Config API.md` |

Draft any of these? (1, 2, both, or skip)
```

### Phase 3: Maintenance

#### 🏥 Vault Health Check

`/obsidian-curator:vault-health` — Quick audit of your vault's health:

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

The vault-curator agent guides you through:
- **Orphaned notes** — Link, add to MOC, or archive
- **Duplicates** — Merge or differentiate
- **Stale notes** — Update, archive, or mark reviewed
- **Convention violations** — Fix frontmatter, move to correct folders

ADHD-friendly features:
- One question at a time
- Progress tracking ("Fixed 3/7 issues")
- Batch operations ("Fix all 5 similar issues?")
- Clear recommendations with easy choices

### Phase 4: Advanced

#### ✏️ Note Editor Agent

Complex editing operations handled by a specialized agent:

| Operation | What It Does |
|-----------|--------------|
| **Merge notes** | Combine duplicates, preserve all content |
| **Restructure** | Reorganize sections, fix header hierarchy |
| **Template migration** | Update notes to follow new templates |
| **Link enrichment** | Add `[[wikilinks]]` to related notes |
| **Content enrichment** | Expand sparse notes with vault/memory content |

All operations show previews before applying changes.

#### 📋 Meeting Follow-up

Surfaces relevant action items from meeting notes:

```markdown
> 📋 Found a related action item from your 1-on-1 on 2025-01-02:
> - [ ] Update Gateway API rate limiting documentation
>
> Since we're touching this code, want to update the docs too?
```

- Searches `80 Waites/Meetings/` for unchecked items
- Presents contextually when relevant to current work
- Offers to mark items complete when work is done

#### 🔄 Repo Note Enrichment

Suggests updates to repo notes based on session work:

```markdown
## Repo Note Updates

During this session on **Gateway Config API**, I noticed:

| Section | Addition |
|---------|----------|
| Patterns | Repository pattern for config access |
| Gotchas | Rate limiting exponential backoff |

Update the repo note? [All / Select / Skip]
```

- Detects when working on known repos
- Captures patterns, gotchas, key files
- Batches suggestions at session end

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
| Session end | Stop | Reviews session, presents batched capture suggestions |

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

## Roadmap

### ✅ Phase 1: Core (Complete)
- `vault-knowledge` skill — Vault conventions awareness
- `contextual-search` skill — Auto-search during exploration/debugging
- `/capture` command — Quick capture to daily note

### ✅ Phase 2: Suggestions (Complete)
- `note-suggester` skill — Recognizes capture-worthy moments
- Session end hooks — Batch suggestions at session end

### ✅ Phase 3: Maintenance (Complete)
- `vault-curator` agent — Dedicated cleanup sessions
- `/vault-health` command — Run vault audit
- `/cleanup` command — Interactive cleanup

### ✅ Phase 4: Advanced (Complete)
- `note-editor` agent — Complex merging, restructuring
- `meeting-followup` skill — Surface unchecked action items
- `repo-enrichment` skill — Auto-suggest repo note updates

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

# Obsidian CLI Gotchas (Wiki Operations)

Shared reference for `wiki-create`, `wiki-query`, `wiki-refresh`, and `vault-inspect` skills when operating on the Knowledge Wiki.

## Frontmatter-only changes → use property:set OR Edit, not file rewrite

When the change is purely a frontmatter field, prefer `obsidian property:set` for single-value updates and the Edit tool for multi-value list updates.

### Single-value or single-item-list updates → property:set

```bash
obsidian property:set name="up" value="[[Parent Page]]" type="list" path="Reference/Developer/Page.md"
obsidian property:set name="date_updated" value="2026-04-06" path="Reference/Developer/Page.md"
obsidian property:set name="owner" value="ai" path="Reference/Developer/Page.md"
```

This works cleanly for: setting a single string value, setting a single list item, replacing one value entirely.

### Multi-item list updates (multiple sources, multiple tags) → Edit tool

`obsidian property:set` does NOT have a clean syntax for setting a list to multiple items in one call. For these cases, use Read + Edit:

```
1. Read the first ~15 lines of the file to capture exact frontmatter text
2. Use Edit tool with old_string = the existing block, new_string = the corrected block
```

Example: updating a `sources:` list from 1 entry to 3 entries, or fixing a `tags:` list to add `topic/` prefix to multiple tags.

Save full file rewrites for cases where the body is genuinely changing.

## Long content → temp file pattern

For wiki pages and source notes (anything more than ~10 lines), do NOT try to inline-escape content with `\n`. Instead:

1. Write content to a temp file with the Write tool (`/tmp/wiki-foo.md`)
2. Pass to obsidian-cli via command substitution:
   ```bash
   obsidian create path="Reference/Developer/Foo.md" content="$(cat /tmp/wiki-foo.md)" silent
   ```
3. Clean up temp files at the end

## Short content → inline is fine

For log entries and small appends, inline `\n` escapes work well:
```bash
obsidian append path="Reference/log.md" content="\n## [date] entry\n- bullet"
```

## Help syntax

Use `obsidian help <command>`, NOT `obsidian <command> --help`. The latter creates an "Untitled" note in the vault root because `--help` is parsed as a flag rather than a help request.

## Required flags

- **`silent`** — prevents files from opening in Obsidian on creation
- **`overwrite`** — required when replacing an existing file (e.g., updating index.md)
- **`path=`** — exact path from vault root, REQUIRED to land files in the correct folder. Without `path=`, files land in vault root.

## Vault targeting

The CLI defaults to the most recently focused vault. If working from another project session, prefix with `vault="Loose Ends"` to be explicit:

```bash
obsidian vault="Loose Ends" create path="Sources/2026-04-09 Title.md" content="..." silent
```

## Useful commands for wiki operations

```bash
# Create source file
obsidian create path="Sources/2026-04-09 Title.md" content="..." silent

# Create wiki page in appropriate folder
obsidian create path="Reference/Developer/Page.md" content="..." silent

# Replace existing file
obsidian create path="Reference/index.md" content="..." overwrite silent

# Append to log
obsidian append path="Reference/log.md" content="\n## [date] ..."

# Read file
obsidian read path="Reference/Developer/Page.md"

# Search wiki content
obsidian search query="rotation distance" limit=10

# Get backlinks (orphan detection)
obsidian backlinks path="Reference/Developer/Page.md"

# Find all wiki pages by type
obsidian search query="type: wiki" limit=200

# Set frontmatter property
obsidian property:set name="date_updated" value="2026-04-06" path="Reference/Developer/Page.md"
```

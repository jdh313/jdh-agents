---
name: wiki-query
description: Answer questions using the Knowledge Wiki as context. Use when user asks questions about topics that may be covered in the wiki, says "check the wiki", "what do I know about", or "search the knowledge base".
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(obsidian-cli *)
disallowed-tools:
  - Write
  - Edit
---

Apply the runtime mappings in [`../../RUNTIME.md`](../../RUNTIME.md).

# Wiki Query

Answer questions by searching the Knowledge Wiki. Wiki pages are
distributed across the vault and identified by `owner: ai` + `type: wiki`
frontmatter. The search and synthesis run inside the `@vault-reader`
agent; this skill gathers intent, dispatches, and presents the result.

## Wiki-first principle

The wiki is the first stop for any topic lookup. Check it before going
to external sources. The wiki captures *our* context — how we use
things, decisions made, gotchas hit — which generic docs won't have.
Only go external when the wiki has gaps, and suggest ingesting the new
information back.

## Vault tool usage

Start with `obsidian-cli search:context query='...'` and `obsidian-cli backlinks file='...'` for read-side retrieval. For multi-note synthesis use `mcp__obsidian-mcp__read_multiple_notes` (up to 10 paths) or delegate to vault-reader agent. Use `mcp__obsidian-mcp__search_notes` with `searchFrontmatter: true` for ad-hoc frontmatter-value lookups when no pre-built Base exists.

## Workflow

### 1. Clarify the question

If the user's question is ambiguous (broad topic, no concrete angle),
ask one focused follow-up. Otherwise proceed.

### 2. Dispatch to vault-reader

Invoke `@vault-reader` with this payload:

```markdown
## Intent
wiki query: <one-line question>

## Constraints
- Restrict to `owner: ai` + `type: wiki` pages
- Follow `up:`, `expands:`, and `[[wikilink]]` references to gather depth
- Cap reads at ~10 pages

## Input
<the user's question, verbatim>

## Output shape
Synthesis (2-4 sentence direct answer) + "Going deeper" pointer list +
cited sources + any gaps noticed.
```

### 3. Present the result

Surface the agent's `## Result` block to the user. If the agent flagged
gaps in `## Notes`, mention them.

**Multi-question sessions — re-engage, don't re-dispatch.** If the user
asks a follow-up wiki question in the same session, re-engage the *same*
`@vault-reader` instance (via `SendMessage` to its agent ID) with the new
question rather than cold-spawning a fresh reader. The reader keeps the
conventions it loaded and the pages it already read, so a related
follow-up ("and how does that compare to X?") is cheap and stays
coherent across the thread. A single one-off question needs no
re-engagement — take the one `## Result` and stop.

This skill is **read-only** — it never writes (note `disallowed-tools:
Write, Edit` in the frontmatter). Any persistence of a synthesis routes
through a writing skill (`wiki-create` / `wiki-refresh`), which owns
`@note-editor`.

### 4. Suggest next steps (when applicable)

- If the answer represents a useful synthesis worth keeping: offer to
  save it via `wiki-create` (stub mode, `page_type: concept`).
- If external sources would fill flagged gaps: offer to ingest them via
  `wiki-create` (ingest mode).
- If wiki pages appear contradictory or stale: flag for `wiki-refresh`.

## Quality rules

- Only use information from the agent's `## Result`. Do not supplement
  with training knowledge unless the user explicitly asks.
- When the agent reports insufficient coverage, say so clearly rather
  than filling gaps with general knowledge.
- Distinguish between "the wiki says X" and "generally, X is true".

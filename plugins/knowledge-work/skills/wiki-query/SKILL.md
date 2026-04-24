---
name: wiki-query
description: Answer questions using the Knowledge Wiki as context. Use when user asks questions about topics that may be covered in the wiki, says "check the wiki", "what do I know about", or "search the knowledge base".
---

# Wiki Query

Answer questions by searching the Knowledge Wiki. Wiki pages are distributed
across the vault, identified by `owner: ai` + `type: wiki` frontmatter.

## Required skills
- **Skill(obsidian:obsidian-cli)** — for searching notes by content, tags, or properties
- **Skill(obsidian:obsidian-markdown)** — when filing answers back as new wiki pages

## Wiki-first principle

The wiki is the first stop for any topic lookup. Check it before going to
external sources. The wiki captures our context — how we use things, decisions
made, gotchas hit — which generic docs won't have. Only go external when the
wiki has gaps, and suggest ingesting the new information back.

## Workflow

### 1. Search the wiki

- Read `Reference/index.md` to identify relevant pages
- For deeper search, use `Skill(obsidian:obsidian-cli)` to query by content, tags, or properties
- Read the most relevant wiki pages (limit to 5-10 to manage context)

### 2. Synthesize answer

- Answer the question using wiki content
- Cite which wiki pages (and underlying sources) support each point
- Note gaps — what the wiki doesn't cover that would help answer the question
- Flag any contradictions between wiki pages

### 3. Optionally file the answer

If the answer represents a useful synthesis (comparison, analysis, connection between topics), ask the user:

"This answer connects several topics. Want me to save it as a wiki page?"

If yes, use `wiki-stub` to create the page so it emits the canonical skeleton
for the appropriate `page_type` — almost always `concept` for synthesized
answers. Fill the skeleton with:
- A neutral 1-2 sentence definition at the top
- The synthesized content distributed across the H2 sections
- `owner: ai`, `type: wiki`, `page_type: concept` in frontmatter
- `sources:` listing all wiki pages that contributed (and any external sources consulted)
- Update `Reference/index.md` and `Reference/log.md`

### 4. Suggest next steps

- Sources that would fill gaps in coverage — offer to ingest them via `wiki-ingest`
- Related questions worth exploring
- Wiki pages that might need updating based on the question
- If external sources were consulted to answer the question, suggest ingesting
  the key findings back into the wiki so the answer is available next time

## Implementation Notes

See `${CLAUDE_PLUGIN_ROOT}/references/obsidian-cli-gotchas.md` for obsidian-cli patterns and command examples (search, read, backlinks).

## Quality Rules

- Only use information present in wiki pages — don't supplement with training knowledge unless explicitly asked
- When wiki content is insufficient, say so clearly rather than filling gaps with general knowledge
- Distinguish between "the wiki says X" and "generally, X is true"

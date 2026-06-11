# Resources.md Format

`Resources.md` is a vault note at the workspace-folder root: a curated index of trusted sources for this topic. Knowledge for explainers should be drawn from here, not from parametric guesses. Wisdom comes from the communities listed here.

## Vault integration

- **Ingest, don't inline.** Material worth keeping (articles, videos, transcripts) is saved to the vault's global `Sources/` namespace via the `wiki-create` skill (ingest mode), which writes a `type: source` note. `Resources.md` then links to it by `[[wikilink]]` rather than duplicating the content.
- **External-only links** (a community, a site you won't ingest) can be listed inline as plain markdown links.
- Minimal frontmatter: `owner: ai`, `up: "[[Mission]]"`, `tags: [learning, topic/{x}]`.

## Structure

```md
# {Topic} Resources

## Knowledge

- [[Sources/2026-06-12 The Science and Practice of Strength Training — Zatsiorsky & Kraemer|Zatsiorsky & Kraemer — Strength Training]]
  Foundational text on programming and adaptation. Use for: anything to do with periodisation, recovery, intensity zones. _(ingested)_
- [Article: "How Much Should I Train?" — Greg Nuckols (Stronger By Science)](https://example.com)
  Evidence-based review of volume landmarks. Use for: weekly set targets per muscle group.

## Wisdom (Communities)

- [r/weightroom](https://reddit.com/r/weightroom)
  High-signal subreddit, moderated against bro-science. Use for: programme critique, plateau troubleshooting.
- Local: Tuesday strength class at {gym name}
  Use for: real-time coaching feedback on lifts.
```

## Rules

- **High-trust only.** Prefer primary sources, recognised experts, peer-reviewed work, and communities with strong moderation. If a resource is marketing dressed as education, leave it out.
- **Annotate every entry.** A bare link is useless in three months. Add one line: what it covers and when to reach for it.
- **Group by Knowledge / Wisdom.** Mirrors the philosophy in [SKILL.md](./SKILL.md). It is fine for a resource to appear in only one group.
- **Surface gaps explicitly.** If no good resource exists for an area the mission needs, write a `## Gaps` section listing what is missing. This drives future search.
- **Prune ruthlessly.** A resource that turned out to be wrong, shallow, or off-mission should be removed, not buried. Better five sharp sources than thirty mediocre ones.
- **Record community preferences.** If the user has opted out of joining communities, note it here so future sessions don't keep proposing them.

# Work context configuration

Some skills in this plugin (`meeting-notes`, `meeting-followup`, `meeting-restructure`) operate on meeting notes filed under a top-level work-context folder in the Obsidian vault. The folder name changes when the user's primary work context changes (job rotation, contract end, etc.), so it is configured outside the plugin rather than hardcoded.

## Location

`~/Loose Ends/.claude/knowledge-work.local.md`

Lives with the vault, not the plugin install. A vault clone or sync carries the config across machines; a plugin reinstall does not touch it.

Use `~/Loose Ends/` consistently in skill bodies — the user has multiple machines with different home directories (`/Users/jacob` and `/Users/carta`), and `~` resolves correctly on each.

## Format

YAML frontmatter in a markdown file:

```yaml
---
active_work_context: Carta
---
```

A human-readable body explaining the keys is encouraged but not required.

## Substitution

Skills that depend on work-context paths must, before producing output:

1. Read `~/Loose Ends/.claude/knowledge-work.local.md`.
2. Extract `active_work_context` from the frontmatter.
3. Substitute that value for every occurrence of `${active_work_context}` in the skill body, any examples, and any output the skill generates.

Paths in skill bodies are written in variable form (e.g. `${active_work_context}/Meetings/`, `[[${active_work_context}/Meetings/...]]`) so updates take effect by editing the config alone — no skill edits required.

## Fallback

If the config file does not exist, or if `active_work_context` is missing from its frontmatter, default to `Carta`.

## When to change

Edit the one line in the config file. Affected skills resolve the new value on their next invocation. No plugin reinstall, no skill edits.

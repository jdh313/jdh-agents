# Understanding.md Format

`Understanding.md` lives at the grok workspace-folder root, as a vault note. It is the codebase-comprehension equivalent of `teach`'s `Mission.md`: it captures **why you are building understanding of this repo** and **what you understand so far**. Every grok decision — what to explain next, which subsystem to walk, how deep to go — should trace back to it.

## One workspace per repo

Unlike a `teach` mission (one mission per workspace), a repo is a long-lived thing you return to. So:

- **One workspace per repo**, not per goal. Records accumulate across focus shifts — understanding of the auth layer stays valid when you move on to billing.
- `Understanding.md` holds a **current focus** (the subsystem/goal driving _this stretch_ of sessions) plus a running **map of what's understood**. The focus is expected to move over time; the map only grows.

## Frontmatter

```yaml
---
owner: ai
type: understanding-goal
status: active            # active | dormant | achieved
repo: {Repo Name}
repo_path: {absolute or ~-relative path to the working tree}
started: YYYY-MM-DD
up: "[[{Context parent MOC}]]"
related: ["[[Learning Style]]"]
tags: [understanding, repo/{x}, context/{y}]
---
```

`date created` / `date_modified` are managed by the Linter plugin — do not set them.

## Body template

```md
# Understanding: {Repo Name}

## Why
{1-3 sentences. The concrete reason you're building understanding here. Ship feature X? Own subsystem Y? Debug a recurring class of bug? Avoid abstract "to understand the codebase" framings — name the real outcome. For a cold/new repo this may start broad ("get oriented enough to make changes safely") and sharpen as a real task lands.}

## Current focus
- {The subsystem or question driving this stretch of sessions. This moves over time — update it; don't accumulate stale focuses.}

## Map — what's understood so far
- **{Subsystem}** — {one line on the model you hold} → [[Records/NNNN-slug]]
- **{Subsystem}** — {…}
{A scannable index of the territory covered, each line pointing at the record(s) that hold the detail. This is the zone-of-proximal-development input: it's how the next session knows the floor.}

## Open questions
- {Things you know you don't understand yet — the candidate next-focus list.}

## Grounding sources
- CONTEXT.md: {present / absent}
- NDR atoms: {areas with relevant heads, or "none found"}
- {READMEs, design docs, owner pages, or people who know this code}

## Preferences
- {How the user wants this repo explained — depth, pace, diagram appetite, things to skip. Surfaces over sessions.}
```

## Rules

- **One workspace per repo.** Two repos = two workspaces. A monorepo with bounded contexts may earn one workspace per context — propose and confirm.
- **Concrete over abstract.** "Understand the booking state machine well enough to add partial cancellation" beats "understand bookings."
- **Push back on vagueness.** If the user can't say why they're building this understanding, interview them before writing anything — a session with no goal produces explanations that feel abstract and untethered.
- **The map grows; the focus moves.** Keep the map current as records land. Update the focus when the user's attention shifts — don't leave a stale focus steering the zone of proximal development.
- **Keep it short.** If `Understanding.md` runs past a screen, the detail has leaked in from the records — push it back out. This note is a compass and an index, not the knowledge itself.

## Where the workspace lives

Mirror `teach`'s context-first placement. A codebase workspace is a technical/dev topic, so it defaults to:

```
Reference/Developer/{Repo Name}/
  Understanding.md
  Records/0001-*.md
  maps/0001-*.html        # optional set-piece walkthroughs
```

Confirm the path with the user before creating anything (use the vault's Location Decision Tree). Work repos may belong under a `Carta/` context instead — and for proprietary repos, **do not** route durable shared facts into the personal vault; graduate those to the repo's own `CONTEXT.md` / an internal authority, exactly as `grill-with-docs` does.

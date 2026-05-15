# Workflow

How `/capture-decision` and `/decisions` interact, end-to-end.

## Capture flow

`/capture-decision` is invokable from any chat where decisions landed. The flow:

1. **Scan.** Skill scans current conversation context for atomic decisions. Atomic = one chosen path with one set of consequences. Bundled candidates (e.g. "use FastAPI + Postgres") get split.
2. **Confirm.** Each candidate is presented as a one-line summary. User confirms, edits, or removes. Result: a final list of N atoms.
3. **Draft each atom.** Frontmatter + body drafted from conversation context. Missing required fields are surfaced as prompts.
4. **Review-then-persist.** Drafts live in-memory until the user accepts. No `draft` status; drafts never touch disk. Lineage and identity stay reviewed longest.
5. **Taxonomy enforcement.** `area:` and `topic:` validated against `taxonomy/*.yaml`. Unknown value triggers a "use existing or add new?" prompt; "add new" writes the taxonomy file.
6. **Supersession protection.** If the skill detects this is a *revising* decision (intent words like "revises", "supersedes", "instead of", or an `informed_by:` pointing at a `current` decision the new one disagrees with), it refuses to write while `supersedes:` is empty.
7. **Two-write supersession (three-write with alias handover).** When `supersedes: [X]` is non-empty:
   - Write the successor first.
   - Patch the predecessor: set `status: superseded`, append the successor to `superseded_by: []`.
   - **If the predecessor carries `aliases:`**, the patch also moves each slug: append to the successor's `aliases:`, then clear the predecessor's `aliases:` to `[]`. The slug handover is part of the same patch operation, not a separate user step.
   - On patch failure (including alias handover), report the half-state — which slugs were moved, which weren't — and exit non-zero. No silent partial write.
   - Refuse to patch if the predecessor is already `superseded` by a *different* successor — manual resolution needed.
8. **ID assignment.** Auto-assigned as next zero-padded 4-digit (`max(existing) + 1` across both `<id>-*.md` files and `<id>-*/` directories).
9. **Storage.** Writes to `~/Loose Ends/Decisions/<id>-<kebab-title>.md`. Always single-file — hybrid altitude callouts handle length-management without splitting.

## Read flow

`/decisions <ref-or-topic>` is the supersession-aware reader. It parses three reference grains plus a free-text fallback (see [Reference convention](#reference-convention)) and then runs two-stage retrieval:

### Stage 1 — frontmatter probe

```
mcp__obsidian-mcp__search_notes
  query: "<user-supplied topic terms>"
  searchFrontmatter: true
  searchContent: false
  limit: 10
```

Returns hit titles + match counts. Cheap and precise.

### Stage 2 — load matches

Agent picks the top 1–3 hits, calls `mcp__obsidian-mcp__read_multiple_notes`. Total cost lands at 500–1500 tokens.

### Stage 3 — walk supersession

For each loaded decision: if `superseded_by:` is non-empty, follow the chain to the head. Read the *current* version, not the seed. **This is what makes reading drift-safe.**

### Stage 4 — synthesize

Output: one short brief — "Current state on \<topic\>: \<head-decision title\> — \<one paragraph\>. Lineage: A → … → head."

If the head's body has a `## Assumptions` section with `Revisit if:` conditions plausibly tripped by the current context, surface them as caveats. (Assumptions live in the body as `> [!warning]- <slug>` callouts — description paragraph + `**Current state:**` / `**Revisit if:**` bullets.)

### Fallbacks

- If Stage 1 returns zero hits, retry once with `searchContent: true`.
- If still zero, return "no decisions matched \<topic\>". Don't fabricate.
- If no topic argument is given, the skill prompts for one.

## Reference convention

External code, READMEs, design docs, and vault notes that need to point at NDRs use the `ndr:` prefix with three resolvable grains:

| Form | Example | Resolves to | Use when |
| --- | --- | --- | --- |
| **atom-id** | `ndr:0011` | the exact atom, frozen | documenting why something was built (historical anchor) |
| **slug** | `ndr:#monorepo-shape` | the atom currently aliased to this slug; follows supersession via `aliases:` field | current governance matters; you want the live atom, not the one that was current at write-time |
| **topic** | `ndr:architecture/repo-shape` | all `status: current` atoms with that `area`/`topic` | the whole area governs the call site |

The `/decisions` skill parses all three forms (plus a free-text fallback). Slugs are minted **lazily** — per atom, only when external reference is needed. Most atoms never carry one.

### Inside the vault

Vault wikilinks can use slugs directly: `[[ndr-monorepo-shape]]` resolves through Obsidian's native alias mechanism to whichever atom currently holds the alias. Supersession moves the alias atomically (see Capture flow step 7), so the wikilink target updates without the link itself changing.

### Why three grains

References are bi-temporal: a writer may mean "the atom that justified this code" (historical) or "the decision that currently governs this code" (live). Forcing one reference form to do both jobs is what makes `ADR-NNNN` style refs go stale on supersession. The three grains let the writer name intent at write-time, and `/decisions` resolves the appropriate atom(s) at read-time.

## Auto-loaded rule

`rules/ndr-decisions.md` is symlinked into `~/.claude/rules/` and tells the agent to:

- Run `/decisions <inferred topic>` early in sessions on tracked projects.
- Treat unread decisions as ground truth — don't re-derive current state from older artifacts.

Tracked projects are opted in via a project-level `.claude/CLAUDE.md` marker (deferred to post-scaffold; first tracked project will likely be a Carta repo).

## Why this shape

- **Atomic decisions** (one per artifact) make supersession work cleanly per-part. Bundling defeats the supersession primitive.
- **Frontmatter-first search** is cheaper and more precise than full-text. The schema is small enough to keep top-of-mind.
- **Walk to head** is the load-bearing piece — the whole MVP is "not just yet another markdown notes folder" because of Stage 3.
- **Refuse-to-write supersession protection** keeps the primitive from depending on discipline. Refusal is structural, not advisory.

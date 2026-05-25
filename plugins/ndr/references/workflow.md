# Workflow

How `/capture-decision` and `/decisions` interact, end-to-end.

## Capture flow

`/capture-decision` is invokable from any chat where decisions landed. The skill itself is a thin orchestrator; the work happens in a pipeline of focused subagents plus a deterministic persistence helper:

```
in-skill scan ──► user confirms candidates ──► ndr-drafter ──► ndr-reviewer ──► persist.py ──► summary
```

1. **Scan.** Skill scans the current conversation for atomic decisions. Atomic = one chosen path with one set of consequences. Bundled candidates (e.g. "use FastAPI + Postgres") get split. **For long sources** (pasted transcript, file, PR thread), the skill invokes the `ndr-extractor` subagent instead of scanning inline; the extractor returns structured candidates with supporting quotes.
2. **Detect supersession intent.** The skill watches for revising signals — intent words ("revises", "supersedes", "instead of"), or a candidate that contradicts a decision named in chat / `informed_by:` context. Candidates with revising signal are tagged so Step 3 can ask the user what's being superseded.
3. **Confirm candidates.** Each candidate is presented as a one-line summary. User confirms titles, drops candidates, names predecessors for revising signals, and (rarely) opts in to slug minting. Refusal-to-proceed is structural: if revising intent is present and the user neither names a predecessor nor confirms "this is fresh", the skill stops.
4. **Taxonomy preflight.** Skill suggests `area:` / `topic:` per candidate from the on-disk taxonomy (`~/Loose Ends/Decisions/.taxonomy/{areas,topics}.yaml`). Unknown values trigger a "use existing or add new?" prompt; "add new" appends to the YAML file before drafting. `persist.py` re-validates — this preflight is friendly UX, not the structural gate.
5. **Delegate composition.** Skill invokes the `ndr-drafter` subagent with confirmed candidates. The drafter returns `{frontmatter, body, missing_fields}` per atom. **The drafter never touches disk and never assigns IDs** — `id:` stays as `"PLACEHOLDER"`. If `missing_fields` is non-empty, the skill prompts the user, fills the gap, and re-invokes the drafter. Drafts live in memory.
6. **Review.** Skill invokes `ndr-reviewer` with `{mode: "pre-persist", drafts: [...]}`. The reviewer's load-bearing checks are atomicity (one chosen path, one set of consequences) and body altitude (heading + one-line gist + collapsed callouts, not free prose). It also runs soft mechanical checks (frontmatter completeness, taxonomy, status, alias namespace). Verdict is `pass` or `fail` with structured issues. Mechanical issues may be auto-fixed and re-reviewed; load-bearing failures route back to the drafter or to user edits.
7. **Persist.** Skill pipes drafts to `${CLAUDE_PLUGIN_ROOT}/scripts/persist.py` as JSON on stdin. The persistence helper:
   - Validates `area:` / `topic:` against the on-disk taxonomy (hard gate).
   - Assigns the next ID as `max(existing) + 1` across both `<id>-*.md` files and `<id>-*/` directories.
   - Writes `~/Loose Ends/Decisions/<id>-<kebab-title>.md`. Always single-file — hybrid altitude callouts handle length-management inside the file.
   - On non-empty `supersedes:`, performs three-write supersession (see below).
   - Returns a JSON summary on stdout. Exit codes: `0` success, `1` validation, `2` supersession conflict, `3` mid-transaction half-state.
8. **Three-write supersession (with alias handover).** When `supersedes: [X]` is non-empty, `persist.py`:
   - Writes the successor first.
   - Patches each predecessor: `status: superseded`, appends the successor wikilink to `superseded_by: []`.
   - **If the predecessor carries `aliases:`**, the patch also moves each slug: appends to the successor's `aliases:` (re-writing the successor file with merged aliases), then clears the predecessor's `aliases:` to `[]`. The slug handover is part of the same operation, not a separate user step.
   - Refuses if the predecessor is already `superseded` by a *different* successor — exits `2` with a conflict report; manual resolution needed.
   - On patch failure mid-transaction, reports the half-state (which slugs moved, which writes succeeded) and exits `3`. No silent partial writes.
9. **Summarize.** Skill prints a compact summary to the main context: IDs written, IDs patched (with status flips), and any alias handovers. One line per file.

### Why this shape

The pipeline split is deliberate:

- **Skill = scope detection + user interaction.** The skill owns "what is this conversation about?" because the conversation context is already loaded; sending it to a subagent costs tokens and adds latency.
- **Subagents = focused composition.** Each subagent has one job (extract, draft, review) and isolated context. The reviewer cannot accidentally rewrite the draft; the drafter cannot accidentally write to disk.
- **`persist.py` = determinism.** ID assignment, taxonomy enforcement, and the supersession transaction must not depend on LLM judgment. The persistence helper is the only path that touches disk, and it's plain Python — easy to test (`scripts/test_persist.py`) and easy to reason about under failure.

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

For each loaded decision: if `superseded_by:` is non-empty, follow the chain to the head. Read the *current* version via `obsidian-cli read file=<path>`, not the seed. **This is what makes reading drift-safe.**

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

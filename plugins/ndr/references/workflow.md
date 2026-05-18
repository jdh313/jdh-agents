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

The read side has two entry points and one worker:

| Entry point | Driven by | Use when |
| --- | --- | --- |
| `/decisions <ref-or-topic>` | user-supplied topic or `ndr:` ref | The user (or another agent) already knows the topic — "what did we decide about X?", "resolve `ndr:0011`" |
| `/ground [scope]` | active code work — cwd, file path, area phrase | Before substantive edits or before delegating to a coding subagent (junior-dev / senior-dev / tech-lead) — "ground me in the NDRs for this area" |
| `@ndr-reader` | both skills, and any agent with Agent-tool access | The single worker: parses the inbound payload, does the obsidian-cli work, walks supersession to head, returns a structured brief. Read-only |

Both skills are thin: they handle argument parsing or scope detection plus presentation, and dispatch to `@ndr-reader` for the work. That keeps the supersession walk (Stage 3 below) in one place — see [Why this shape](#why-this-shape).

`@ndr-reader` runs two-stage retrieval (skipped when the caller already passes a specific `ref:`):

### Stage 1 — frontmatter probe

```
obsidian-cli search query="<user-supplied topic terms>" path="Decisions" limit=10 format=json
```

`obsidian-cli search` matches against file content (which includes YAML frontmatter); focused query terms — area, topic, title fragments — push frontmatter matches to the top. The skill post-filters hits by reading frontmatter fields (`obsidian-cli property:read name="area" path="..."`, etc.) and reranks frontmatter matches ahead of pure body-text matches. Cheap and precise.

### Stage 2 — load matches

Skill picks the top 1–3 hits and calls `obsidian-cli read path="<path>"` once per pick (the CLI has no batch read; loop the calls). Total cost lands at 500–1500 tokens.

### Stage 3 — walk supersession

For each loaded decision: if `superseded_by:` is non-empty, follow the chain to the head. Read the *current* version, not the seed. **This is what makes reading drift-safe.**

### Stage 4 — synthesize

Output: one short brief — "Current state on \<topic\>: \<head-decision title\> — \<one paragraph\>. Lineage: A → … → head."

If the head's body has a `## Assumptions` section with `Revisit if:` conditions plausibly tripped by the current context, surface them as caveats. (Assumptions live in the body as `> [!warning]- <slug>` callouts — description paragraph + `**Current state:**` / `**Revisit if:**` bullets.)

### Fallbacks

- If Stage 1 returns zero hits, retry once with `obsidian-cli search:context query="..." path="Decisions" limit=10 format=json` (broader content match with surrounding lines).
- If still zero, return "no decisions matched \<topic\>". Don't fabricate.
- If no topic argument is given, the skill prompts for one.

## Grounding flow

`/ground [scope]` is the active-work entry point. Where `/decisions` waits for a user-supplied topic or `ndr:` reference, `/ground` detects scope from whatever the orchestrator already knows about the current task and pulls relevant heads proactively — typically just before substantive code edits or before delegating to a coding subagent.

```
scope detection (skill) ──► @ndr-reader ──► brief surfaced to orchestrator ──► (optional) folded into delegation prompt
```

### Why this is separate from `/decisions`

The two skills share `@ndr-reader` but differ in who supplies the scope and what shape the answer takes:

| Aspect | `/decisions` | `/ground` |
| --- | --- | --- |
| Scope source | user argument (`$ARGUMENTS`) | cwd, recently edited files, area phrase, conversation context |
| Activation | user types it, or user asks a topic-shaped question | orchestrator about to do or delegate substantive code work in a tracked project |
| Output emphasis | one brief — answer the question | one or more briefs + `ndr:` reference strings ready to paste into a delegation prompt |
| Quiet on empty | optional "no matches" line | mandatory — one line, no nag |

### Skill responsibilities

1. **Detect scope.** Build a lightweight payload from `pwd` / `git rev-parse --show-toplevel`, `$ARGUMENTS`, and recently-edited files in conversation context. Do NOT load atoms — that is the agent's job.
2. **Dispatch.** Hand `@ndr-reader` the canonical Intent / Constraints / Input / Output shape payload. `Output shape: brief` is the default.
3. **Present.** Inline (1–2 heads) or batched table (3+). Surface assumption-warning callouts verbatim — those are the load-bearing signal that prior reasoning may be tripping.
4. **(Optional) Hand off.** If the orchestrator is about to dispatch `junior-dev` / `senior-dev` / `tech-lead`, append the `ndr:` reference strings from the brief to the delegation prompt so the subagent has stable identifiers without needing to query the vault itself.

### Why skill + agent split (not just an agent)

Subagents don't see the skills list. The orchestrator does — its always-visible reminder block carries each skill's frontmatter description. That's the primary "Claude knows when to invoke this" mechanism. An agent alone, with no skill, would have a much weaker activation path: agent descriptions are only visible to agents that have Agent-tool access *and* are actively scanning. The skill provides the trigger surface; the agent provides the isolated context for the work. This is the same shape `librarian:meeting-followup` + `librarian:vault-reader` use.

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

## Opting a repo into the grounding rule

NDR coverage is per-repo and opt-in. The opt-in artifact is a snippet in the repo's `.claude/CLAUDE.md` that names this repo as NDR-tracked and tells the orchestrator to run `/ground` before substantive code work.

The bootstrap installs a canonical copy of the snippet to `~/Loose Ends/Decisions/.templates/project-claude-md.md`. To opt a repo in:

```
cat ~/Loose\ Ends/Decisions/.templates/project-claude-md.md >> <repo>/.claude/CLAUDE.md
```

The snippet covers:

- That decisions for this repo live as atoms with `project: [[<this-repo>]]`.
- When to invoke `/ground` (substantive edits, before delegating to a coding subagent) and when to skip (typo fixes, comment-only).
- Treating returned decision heads as ground truth — no re-deriving from READMEs / ADRs / code comments.
- The `ndr:` reference convention for pointing at decisions from code.
- When to invoke `/capture-decision` at end of chat.

Why opt-in: not every repo has NDR coverage, and pulling vault context for repos that don't would be noise. Editing CLAUDE.md is also intentional — opting in records a per-repo commitment to consult the decision corpus.

## Why this shape

- **Atomic decisions** (one per artifact) make supersession work cleanly per-part. Bundling defeats the supersession primitive.
- **Frontmatter-first search** is cheaper and more precise than full-text. The schema is small enough to keep top-of-mind.
- **Walk to head** is the load-bearing piece — the whole MVP is "not just yet another markdown notes folder" because of Stage 3.
- **Refuse-to-write supersession protection** keeps the primitive from depending on discipline. Refusal is structural, not advisory.

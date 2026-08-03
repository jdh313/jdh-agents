# Understanding Record Format

Understanding records are vault notes living in `./Records/` inside the repo's grok workspace, with sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the directory lazily — only when the first record is written.

They are the codebase-comprehension equivalent of ADRs (they read natively next to the vault's `Decisions/` and the repo's NDR atoms): they capture **what you now genuinely understand about this codebase** — a subsystem's contract, a non-obvious invariant, a gotcha, or a corrected mental model. They are used to calculate the zone of proximal development for the next session, so future `/grok` sessions don't re-explain ground already covered.

A record is personal knowledge. It is **not** a shared fact yet — shared facts graduate out of records into the repo's own durable layer (see "Graduation" below).

## Frontmatter

```yaml
---
owner: ai
type: understanding-record
repo: {Repo Name}
subsystem: {area or module the record is about}
insight: "{one-line gist of what is now understood}"
status: current           # current | revised | superseded
up: "[[Understanding]]"
tags: [understanding-record, repo/{x}]
---
```

Optional: `derived_from: "[[0003-some-record]]"` (which session or record produced it), `superseded_by: "[[0007-some-record]]"` (set when superseded), `commit: {sha}` (the code state the understanding was formed against — useful because code drifts and a record can go stale).

## Body template

```md
# {Short title of what is now understood}

{1-3 sentences: the mental model, contract, or invariant — and why it matters for navigating or changing this code. Use the project's CONTEXT.md vocabulary and the module/seam/depth language from the codebase-design skill (`craft:codebase-design`).}
```

That is the whole format. A record can be a single paragraph. The value is recording _that_ this is now understood and _why_ it changes what to explain next — not in filling out sections.

## Optional body sections

Only include these when they add genuine value. Most records won't need them.

- **Evidence** — how the understanding was demonstrated (a flow traced end-to-end, a behavior predicted correctly, a change made successfully). Useful when the claim might be revisited.
- **Anchors** — `file_path:line` pointers to the load-bearing code, so a future session can re-verify against the source instead of trusting the record blind.
- **Implications** — what this unlocks or rules out for future sessions. Worth recording when non-obvious.

## Numbering

Scan `./Records/` for the highest existing number and increment by one.

## When to write an understanding record

Write one when any of these is true:

1. **You built a durable mental model of something non-trivial** — a data flow, a control path, why a seam exists where it does, an invariant the code relies on. Not just "read the file" — a model you could use to predict behavior or make a change.
2. **You corrected a wrong model** — the code did not work the way it looked like it worked. These are the highest-value records: they predict where the next reader (you, later) will stumble.
3. **You confirmed prior knowledge the user disclosed** — "I already understand the auth layer." Record it (and the depth claimed) so future sessions don't re-explain it.
4. **The understanding goal shifted in response to what you learned** — the user discovered the real work was elsewhere. Cross-link to [[Understanding]] and update it.

### What does _not_ qualify

- Code that was merely read or skimmed. Coverage is not understanding. Wait for a model you can use.
- A term definition that belongs in the repo's `CONTEXT.md`. Put it there (via `grill-with-docs`), don't duplicate it as a record.
- A decision with rationale and genuine trade-offs. That is an NDR atom (via `/capture-decision`), not an understanding record.
- Session-by-session activity logs. Records are decision-grade insights about the code, not a journal of what you looked at.

## Supersession

When a later record contradicts an earlier one (your model deepened, or the code itself changed under you), set the old record's `status: superseded` and `superseded_by: "[[NNNN-slug]]"` rather than deleting it. Use `status: revised` for a softer update that refines rather than overturns. The history of how understanding evolved is itself signal — and mirrors both the vault's decision-supersession pattern and the NDR ledger's.

## Graduation

A record is personal and provisional. When a fact inside it turns out to be **shared, stable truth about the repo**, graduate it out — don't let the record become the canonical home:

- **A name for a thing** → the repo's `CONTEXT.md` glossary, via the `grill-with-docs` skill.
- **A decision with rationale and real trade-offs** → an NDR atom, via `/capture-decision`.

After graduating, the record can point at the graduated artifact (`_See_: ndr:area/topic/NNNN-slug` or `_See_: [[CONTEXT term]]`) and stay as the personal-understanding trace of how you got there.

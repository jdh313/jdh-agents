# Learning Record Format

Learning records are vault notes living in `./Records/` inside the workspace folder, with sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the directory lazily — only when the first record is written.

They are the teaching equivalent of ADRs (they read natively next to the vault's `Decisions/`): they capture non-obvious lessons, key insights, and stated prior knowledge that will steer future sessions. They are used to calculate the zone of proximal development.

## Frontmatter

```yaml
---
owner: ai
type: learning-record
topic: {Topic}
lesson: "{one-line insight}"
status: current           # current | revised | superseded
up: "[[Mission]]"
tags: [learning-record, topic/{x}]
---
```

Optional: `derived_from: "[[0003-some-lesson]]"` (which lesson or session produced it), `superseded_by: "[[0007-some-record]]"` (set when superseded).

## Body template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it matters for future sessions.}
```

That is the whole format. A learning record can be a single paragraph. The value is recording _that_ this is now known and _why_ it changes what to teach next — not in filling out sections.

## Optional body sections

Only include these when they add genuine value. Most records won't need them.

- **Evidence** — how the user demonstrated the understanding (a question answered, an exercise completed, prior experience cited). Useful when the claim might be revisited.
- **Implications** — what this unlocks or rules out for future sessions. Worth recording when non-obvious.

## Numbering

Scan `./Records/` for the highest existing number and increment by one.

## When to write a learning record

Write one when any of these is true:

1. **The user demonstrated genuine understanding of something non-trivial** — not just exposure, but evidence they can use the concept correctly. This sets a new floor for what to teach next.
2. **The user disclosed prior knowledge** — "I already know X." Record it so future sessions don't re-teach it. Also record the _depth_ claimed.
3. **A misconception was corrected** — the user previously believed something wrong and now sees why. These are high-value: they predict future stumbling blocks for related topics.
4. **The mission shifted in response to learning** — the user discovered they cared about something different than they thought. Cross-link to [[Mission]] and update it.

### What does _not_ qualify

- Material that was merely covered. Coverage is not learning. Wait for evidence.
- Anything already captured tersely in [[Glossary]] as a term definition. Don't duplicate.
- Session-by-session activity logs. Learning records are not a journal — they are decision-grade insights.

## Supersession

When a later record contradicts an earlier one (the user's understanding deepened or corrected), set the old record's `status: superseded` and `superseded_by: "[[NNNN-slug]]"` rather than deleting it. (Use `status: revised` for a softer update that refines rather than overturns.) The history of how understanding evolved is itself useful signal — and mirrors the vault's own decision-supersession pattern.

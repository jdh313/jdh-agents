# ADR Schema

Modeled on the voyager project's `docs/arch/` practice. The `Constraints` section as a separate first-class field and the `Review Notes` scratchpad are the load-bearing additions over the canonical Nygard schema.

## Filename convention

```
notes/adr/NNNN-slug.md
```

- `NNNN` — sequential number, zero-padded to four digits
- `slug` — short kebab-case description (e.g. `0003-schema-lite-projection`)
- ADR directory is project-configurable; `notes/adr/` is the default this plugin assumes when nothing else is found

## Status lifecycle

```
Proposed ──► Accepted ──► Superseded by ADR-NNNN
   │
   └──────► Rejected
```

- **Proposed** — drafted, not yet ratified by the human. Default for any newly created ADR.
- **Accepted** — ratified. Treated as binding for drift-check.
- **Rejected** — considered and explicitly turned down. Kept in the record for posterity; not binding.
- **Superseded by ADR-NNNN** — replaced by a later ADR. Original kept; status updated with forward link.

**The agent never unilaterally accepts.** Acceptance is a deliberate human ritual: read Context / Constraints / Decision / Consequences, walk Review Notes, trim resolved items, flip status.

## Body schema

```markdown
# ADR-NNNN: <Short Title>

## Status

- Proposed | Accepted | Rejected | Superseded by ADR-NNNN

---

## Context

- What problem are we trying to solve?
- Why is this decision needed now?
- What's the technical or organizational background?

---

## Constraints

- List any constraints that shape the decision (technical, regulatory, operational, business).
- Constraints document what *forced* the decision — the WHY future readers can't reconstruct from code.

---

## Decision

- State the choice as a clear, affirmative sentence.
- Example: "We will use Kafka as the message bus for asynchronous events."

---

## Consequences

- What happens because of this decision?
- Both positive (benefits, simplifications) and negative (trade-offs, risks, costs).
- Operational and maintenance implications.

---

## Alternatives Considered

- Option A: short description + why not chosen
- Option B: short description + why not chosen
- Add more as needed

---

## Review Notes (to be trimmed before acceptance)

- Open questions raised during drafting.
- Uncertainty flags from the agent for the human to resolve.
- Items to validate against running code.
- This section gets trimmed (not deleted) when the human flips status to Accepted — surviving items become amendments to Context / Decision / Consequences.
```

## Section-by-section guidance

### Title

Short, descriptive name of the decision. Reads as a noun phrase, not a verb phrase. Good: *"Schema-lite projection over ops-sheet facts"*. Bad: *"Project the ops sheet"*.

### Status

One of the four lifecycle states. Always starts at `Proposed`.

### Context

Background that produced the decision. Answer: why now? What changed? What problem are we addressing?

Avoid restating the decision here. Context is the *setup*; Decision is the *answer*.

### Constraints

The forces that bound the decision space. Technical (must run on Python 3.14), regulatory (must keep PHI out), operational (no team to self-host), business (Chris's two optimization axes), or stylistic (must compose with existing CLAUDE.md gotchas).

Constraints are the most-load-bearing recovery surface for future readers. Code rarely encodes the constraints that produced it; ADRs should.

### Decision

A clear, affirmative sentence. *"We will X."* Not *"We're considering X"* or *"X seems good"*.

### Consequences

Both positive and negative. Skipping the negative side is the most common ADR antipattern — every real decision has trade-offs.

### Alternatives Considered

Each alternative gets a short description plus the reason it was rejected. Future readers revisiting the same problem benefit from knowing what was already ruled out.

Optional: skip if there were no real alternatives. But "no alternatives considered" is itself a signal — if you can't name one, the decision may not be worth an ADR.

### Review Notes (to be trimmed before acceptance)

This section is novel relative to canonical ADR templates and is the primary integration point with AI-assisted drafting:

- During drafting, the agent parks open questions, uncertainty flags, and items requiring human validation here.
- During ratification, the human walks the section and resolves each item: fold relevant content back into Context / Decision / Consequences, drop irrelevant items, surface external follow-ups elsewhere.
- The section is **trimmed before flipping to Accepted**, not deleted — it can stay (often with the items folded out) as historical evidence of what was debated.

If Review Notes still has unresolved items, the ADR is not ready to flip to `Accepted`.

## Template file

A copy-paste template with this structure should live alongside the ADRs in the project — typically `notes/adr/0000-template.md`. The plugin scaffolds new ADRs from a copy of that template rather than embedding the schema in skill prompts.

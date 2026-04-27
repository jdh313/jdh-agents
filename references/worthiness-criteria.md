# ADR Worthiness Criteria

The ADR layer's value depends on it not being polluted with marginal entries. Pushback is a feature: many things look ADR-shaped without being worth one.

This file codifies the gate. The `adr-evaluate` skill (when added) walks through these criteria; until then, use this as a checklist when deciding by hand.

## The bar

Modeled on the voyager project's ADR-001 commitment: *"ADRs are intended for big decisions — those that significantly affect system architecture, core technology choices, or long-term direction. Smaller implementation details do not need ADRs."*

A candidate decision earns an ADR when **most** of these are true:

1. **It binds future code.** Changing the decision later would require a non-trivial refactor across multiple files or a behavior change visible to users / consumers.
2. **The WHY is non-obvious.** A future reader (or agent) of the code cannot reconstruct the reasoning from the code itself. Constraint encoded but motivation invisible.
3. **The constraint is expected to hold for >3 months.** Decisions that are explicitly time-boxed (try X for two weeks, then revisit) probably don't need ADRs — they belong in session notes or experiment artifacts.
4. **A future developer or agent might confidently undo it without context.** ADRs are most valuable when their absence would let someone "fix" a deliberate constraint they didn't recognize as deliberate.
5. **It reflects a choice between real alternatives.** If you can name two or more options that were genuinely on the table, the trade-off is worth recording.

The gate is **soft, not hard** — if 3 of the 5 are clearly true, write the ADR. If only 1 or 2, route the content elsewhere (see below). If you're at 4 or 5 and hesitating, the hesitation is probably about format, not worthiness.

## Anti-criteria — things that look ADR-shaped but usually aren't

- **Library or framework version pins.** Belong in `pyproject.toml` / lockfile. The ADR layer doesn't track versions.
- **Code style preferences.** Belong in CLAUDE.md or a style guide. ADRs don't enforce indentation or naming conventions.
- **In-flight experiments.** Belong in session notes or a Track-2-style scratch file. ADRs are for decisions you've already made; experiments are decisions deferred until evidence arrives.
- **Implementation detail that the next refactor will touch anyway.** If the decision will naturally evolve as the code matures, an ADR locks in something that won't survive — and locks the reader's expectation that it should.
- **One-off bug-fix rationale.** Belongs in the commit message and (if subtle) a code comment. ADRs aren't for "we did X because Y was broken" unless Y is itself a structural property.
- **Decisions that bind only one function.** ADRs operate at the architecture / module / cross-cutting level. If the blast radius is one function, comment it.

## Where else the content might go

When a candidate fails the worthiness gate, it usually belongs somewhere — just not in the ADR layer:

| Where | When |
|---|---|
| **CLAUDE.md gotcha** | Recurring trap that affects how the agent should write code in this repo. *"Always route VARCHAR numeric columns through `_clean_numeric` before cast."* |
| **Inline code comment** | Truly subtle constraint local to the code. Reserve for behavior that would surprise a careful reader of just the surrounding code. |
| **Session note Reflection** | Something locked in today but probably worth revisiting once more evidence arrives. |
| **Experiment / scratch artifact** | Observation about how an AI workflow performed. Track 2-style learning, not an architectural commitment. |
| **No record needed** | The code expresses the decision adequately on its own; nothing would be served by prose. The honest default for a lot of small choices. |

## Friction-of-creation note

The worthiness gate exists *to keep ADR friction high enough that ADRs stay meaningful*. If creating an ADR feels too easy, you are probably writing them for things that don't deserve the durable layer.

This is the inverse of most documentation tooling. Most tools optimize for capture; this one optimizes for *deliberate* capture.

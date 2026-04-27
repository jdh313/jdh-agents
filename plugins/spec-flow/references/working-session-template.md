---
type: reference
tags:
  - type/working-session
sources: []
date_created: {{TODAY}}
date_updated: {{TODAY}}
---

Planning note for {{PROJECT}} on {{TODAY}}. {{ONE_LINE_FRAMING}}

## Goal

{{One paragraph: what today is *for*. Reference the previous session's reflection if relevant. State whether the day's work is single-thread or parallel-thread.}}

## Tiers

- **Floor (target).** {{Minimum acceptable end-state. If you only ship one thing, it's this.}}
- **Moderate.** {{Floor plus the next-most-likely additions. Includes any ADR or design artifact the work justifies.}}
- **Ambitious (stretch).** {{Moderate plus speculative reach. Explicitly stretch — drop first if the budget tightens.}}

## Mapping to project goals

{{How today's work feeds the project's broader deliverables. Reference the project hub note or roadmap. Skip the heading entirely if not applicable.}}

## Components

1. **{{Component one}}.** {{What it is, why it's first, expected output.}}
2. **{{Component two}}.** {{Same shape.}}

## Non-goals

- {{Things deliberately not in scope today. The list is load-bearing — non-goals are how you protect the time budget when scope creep tempts.}}

## Dependencies

- {{Anything blocking — credentials, upstream data, an unanswered question. If empty, write `(none)`.}}

## Risks

- **{{Risk name}}.** {{What could go wrong, mitigation strategy. Tier-drop strategy if the risk fires: which tier gets dropped first.}}

## End-of-day artifacts

- [ ] {{Concrete artifact — file, commit, ADR, test passing, screenshot. Each item is independently verifiable.}}
- [ ] {{...}}

## Reflection (end of day)

*To be filled: what shipped, what didn't, what changed about the plan.*

**Decisions to promote to ADRs:**

*(List anything decided today that should outlive this session. Empty is the common case — only fill when a constraint binding future code got locked in. Items here are the input to the next ADR-evaluation pass.)*

## See also

- {{Project hub note}}
- {{Previous session note, if relevant}}
- {{Related design / domain notes}}

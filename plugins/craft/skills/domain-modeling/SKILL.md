---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, capture an architectural decision that surfaces while modelling, or when another craft skill needs to maintain the domain model. Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
upstream:
  repo: mattpocock/skills
  path: skills/engineering/domain-modeling
  reviewed_sha: 697d4ce9742d
  reviewed: 2026-07-27
  status: reviewed
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Skill
---

Apply the skill-composition mapping in [`../../RUNTIME.md`](../../RUNTIME.md).

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary down the moment it crystallises. (Merely *reading* `CONTEXT.md` for vocabulary is not this skill — that's a one-line habit any skill can do. This skill is for when you're changing the model, not just consuming it.)

The glossary lives in `CONTEXT.md`. Decision rationale lives in the NDR ledger (in-repo, like the code), but this skill never writes it **directly** — qualifying decisions route through `/capture-decision`, which owns id assignment, validation, and supersession. See "Route capture-worthy decisions" below.

## File structure

Most repos have a single context. The glossary is a single `CONTEXT.md` at the **repo root**:

```
/
├── CONTEXT.md
└── src/
```

Create `CONTEXT.md` lazily — only when the first term is resolved in conversation. Don't pre-create empty files. A repo earns a `CONTEXT.md` when it has internal vocabulary not covered by external sources (vault wiki pages for personal repos; internal docs for work repos). One-off scratch repos and pure-config repos often don't earn one.

**No `docs/adr/`.** The source skill wrote its own in-repo ADR files; this ecosystem keeps decisions in the NDR ledger instead (also in-repo, via `/capture-decision`). The difference is authority and format, not location — this skill never writes decision records directly; the `/capture-decision` flow does.

**Multi-context (work repos only, future).** If a proprietary monorepo grows multiple bounded contexts (Ordering, Billing, Fulfillment, …), a `CONTEXT-MAP.md` at the repo root catalogs them and points to per-context glossaries. Personal repos don't earn this — they use vault wiki pages as the cross-cutting authority. Format details in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `CONTEXT.md`, call it out immediately. "`CONTEXT.md` defines `cancellation` as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When either side uses vague or overloaded terms, propose a precise canonical term. "You said `account` — do you mean the Customer or the User? Those are different things." Either side may propose the canonical name first; the agent often spots drift the human has stopped noticing, the human often has the lived-experience name. Record the agreed term either way.

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts. Keep the scenarios pointed at terminology and concept boundaries — where one concept ends and another begins — not at general plan correctness.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code calls this `cancelOrder`, but you just said partial cancellation is possible — does `CONTEXT.md` need a different term, or does the code need a rename?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` right there. Don't batch these up — capture them as they happen. Use the format in [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).

`CONTEXT.md` should be totally devoid of implementation details and rationale. Do not treat it as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else — it answers "what do we call this thing?" and stops there. Rationale becomes an NDR atom (below); what-we-did lives in the code.

### Route capture-worthy decisions

The source skill offered to write in-repo ADR files. This ecosystem's durable decision layer is the NDR ledger — same decision gate, different destination and write-authority. Rationale is captured via `/capture-decision`; this skill never writes decision records directly.

Only offer to capture a decision when **all three** hold:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will look at the code and wonder "why on earth did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and one was picked for specific reasons

If any of the three is missing, skip it. If a decision is easy to reverse, you'll just reverse it. If it's not surprising, nobody will wonder why. If there was no real alternative, there's nothing to record beyond "we did the obvious thing."

When all three hold, route through `/capture-decision` (ndr plugin) — don't write atom files directly. What typically qualifies:

- **Architectural shape.** "The write model is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider — the ones that would take a quarter to swap out, not every library.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; other contexts reference it by ID only." The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual SQL instead of an ORM because X." Anything where a reasonable reader would assume the opposite — it stops the next engineer from "fixing" something deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of compliance requirements." "Response times must be under 200ms because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** If you considered GraphQL and picked REST for subtle reasons, capture it — otherwise someone will suggest GraphQL again in six months.

## Composition with other plugins

- **`/capture-decision`** (ndr plugin) is the canonical route for turning a resolved-but-rationale-bearing decision into a durable NDR atom. Don't write atom files directly.
- **`craft:grill-with-docs`** runs the same CONTEXT.md maintenance + NDR-capture discipline inside an interview loop against a plan. This skill is the standalone modelling discipline; `grill-with-docs` is the plan-grilling application of it. Both work standalone.
- **`/drift-check`** (ndr plugin) can flag drift between CONTEXT.md term definitions and code naming. Out of scope here — flag candidates for follow-up rather than fixing inline.

## Explicit non-goals

- **No example dialogue.** Definitions only — no demonstrative "dev meets domain expert" conversation. Write-once-never-maintained content. Skip.
- **No rationale in CONTEXT.md.** Why a term was chosen, what alternatives were weighed — that's NDR territory, captured via `/capture-decision`.
- **No `CONTEXT-MAP.md` for personal repos.** Multi-context maps are for proprietary monorepos with bounded contexts; personal repos use vault wiki pages as the cross-cutting authority.

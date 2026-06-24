# Worked run — software-catalog template redesign

The validated session this skill was distilled from. The artifact was an Obsidian wiki "software catalog entry" template; the method produced the V2 schema. Read it as a concrete trace of the eight phases, not as catalog-specific guidance.

## Phase 1 — Frame and ground

Read the current template and stated its shape: frontmatter (`kind` / `lifecycle` / `solves` / relations) all on a "gist hub" page, a separate "Decision" child page carrying the reasoning, body of neutral-definition → `## Advantages` → Breadcrumbs trees. Anchored on the motivation: the existing shape felt wrong but it wasn't clear why. Did not edit anything yet.

## Phase 2 — Cast the actors

Listed the users of a catalog entry, **including non-human actors**:

1. **Writer** — capturing a verdict right after evaluating a tool
2. **Reader** — months later: "what did I decide about X, and why?"
3. **The AI** — creating/updating entries, and reading them during retrieval/grounding
4. **The `.base`** — projects frontmatter into table columns
5. **Breadcrumbs** — renders the hierarchy

Then **challenged the cast** — and that's where the load-bearing actor appeared: **decide-right-now** — actively choosing adopt/trial/drop at a commitment gate, *distinct from* the reader who retrieves an already-settled verdict. This single added actor reframed the whole design.

## Phase 3 — Stories, hardest first

Wrote the **decide-right-now** story first because it was the contentious one:

> As the deciding actor, I want to open an entry and immediately see where it stands, what it's weighed against, and what would tip the call — so I can decide or defer without re-deriving.

## Phase 4 — Sharpen, one fork at a time

The dominating fork: **does this actor READ a materialized verdict, or THINK IN a worksheet they actively fill?** That one fork decided whether the template needed decision-*scaffolding* fields (trial triggers, open unknowns) or just decision-*display* fields.

Resolved: the thinking happens in conversation (debate / first-principles / mulling); the entry *displays* the materialized result.

> **Resolved story:** the deciding actor *reads* a live decision surface — verdict + why, what it was weighed against, what would tip it.

## Phase 5 — Derive the shape

Read fields off the stories: a `summary` (the reader/`.base` both need a one-glance "what is it"), routing data for "when to reach for it", relations for "what it's weighed against", revisit-triggers for "what would tip it". Each traced to a story; fields serving no story became cut candidates.

## Phase 6 — Ground in a real instance

Pulled a **real catalog page** (`Prefect.md`) that predated the template. It exposed two flaws the abstract shape hid:

- The real page was a **single self-contained page**, not the hub+child split the template forced — and the deciding actor (who *reads*) is better served by one stop.
- It still carried a `## Revisit Triggers` section the template had dropped — exactly the "what would tip it" the decide-right-now story needs.

**The axis-conflation tell fired:** it felt *impossible to say* the tool was "adopt" or "drop" — because it was simultaneously adopted in one project and rejected in another. That impossibility meant one field was conflating two independent axes:

1. **Toolbox membership** — do I reach for this *at all*? (a property of the tool)
2. **Per-project selection** — did I pick it *here*, over the alternatives? (a property of a decision, not the tool)

Splitting them dissolved the contradiction: the entry carries only membership; per-project selection moved to the project layer. (This is precisely the kind of finding `interrogate-model` audits for — the derived shape could be handed to it for a full representability pass.)

## Phase 7 — Lock / park ledger (maintained throughout)

- `Locked:` top-level page name → "Entry"; alternatives are auto-derived, not hand-listed.
- `Provisionally locked:` Entry carries membership only; selection lives on the project layer.
- `Parked:` solution-space page as a new type vs. a section on the concept page — didn't block the entry design, so parked and kept moving; revisited once the comparison surface's contents were known.

## Phase 8 — Emit and hand off

Wrote the V2 Entry as a real Obsidian note for review, then drafted a second entry (Dagster) via a background agent for comparison. The load-bearing calls (membership-vs-selection split, single-page entry, `stance` enum) became durable decisions; the build became follow-up work.

---

**What made it work:** the added actor in Phase 2, the read-vs-think fork in Phase 4, and the real instance in Phase 6 that turned an abstract "this feels off" into a concrete two-axis split. None of those surface from tweaking the template directly.

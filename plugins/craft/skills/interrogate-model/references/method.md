# Method — per-phase heuristics

The how behind each phase of `interrogate-model`. Terms are defined in [`../../../CONTEXT.md`](../../../CONTEXT.md).

## Reconstructing the model as axes (Phase 1)

An **axis** is a dimension whose value *should* be settable without constraining the others. To find the axes, look for the independent questions the model answers about a principal or entity: *what can they do?* (action tier), *over what?* (scope/tenancy), *in what status?* (state). Each independent question is a candidate axis; its answers are the axis's values.

- Read the enforcement site, not just the schema. A capability matrix, a policy function, a status enum, a `require_*` guard — that is where axes actually live. Quote the code site for each axis.
- Build the table: **axis | values | code site | independently variable?** The last column is a *claim* to test in Phase 4, not a fact.

**Spotting a candidate latent axis:** a concern that is enforced but is not a value on any declared axis, and that *rides inside* one value of an existing axis. Tell: "to get X you must also be Y," where X and Y are conceptually independent (grant-management requires the top role; all-scope requires the top role). Each "must also be" is a candidate latent axis — a dimension that was fused instead of declared.

## Enumerating scenarios (Phase 2)

The cross-product of axis values is the candidate scenario space, but most gaps are scenarios *outside* what the code anticipated. Two sources:

1. **Mechanical:** walk the axis cross-product and keep the combinations a real subject would need.
2. **Human (the load-bearing source):** ask the user for the personas/states they expect served. Use `AskUserQuestion`. A missing capability is invisible until its scenario is named — a scoped-owner persona, say, often surfaces only once someone says it aloud.

For access models, force every scenario into **subject–action–object–scope** so the required axis-values are explicit. For state machines / data models, a scenario is a required state-combination or configuration.

Keep scenarios at the **archetype** granularity — distinct iff they need a different position in axis-space. "CS rep for Acme" and "CS rep for Globex" are one scenario (scoped owner), not two.

## Building the matrix (Phase 3)

For each scenario, decide reachability:

- **representable** — a grant/state exists that yields exactly this, nothing more.
- **only-via-overreach** — reachable only by over-committing another axis (you can get delete-on-one *only* by also granting all-scope). This is the subtle, dangerous verdict — the capability "works" but drags unwanted authority. Always name the over-grant.
- **unrepresentable** — no combination yields it at all.

For every non-representable scenario, name the **specific axis or coupling** that blocks it. A gap with no named cause is not yet analyzed.

## Detecting conflations and re-auditing the seam (Phase 4)

A **conflation** is forced co-variation: setting one axis's value silently changes another's. Test each axis pair: *hold axis A fixed and vary axis B — does the enforcement actually honor B, or does some value of A override it?* An override that ignores B's recorded value is a conflation.

The **seam** is where an axis added later meets assumptions baked into an axis designed earlier. This is the highest-yield place to look, because each decision was correct alone:

- Date the axes (git blame / atom dates). The *older* axis carries assumptions ("the top role is all-powerful") formed before the newer axis existed.
- At the seam, look for the *shim* that made the old axis keep working when the new one arrived — that shim is usually the conflation.
- Ask the counterfactual the original work never did: *should this coupling exist, or was it just convenient?*

## Distinguishing a silently waived departure from drift (Phase 5)

Both are **departures** (behavior diverges from a stated principle). The split is **intent**:

- **Drift** — accidental divergence; the code drifted from the atom. Resolution: reconcile → `drift-check` owns this. Note it and move on.
- **Silently waived departure** — the departure is *deliberate* (a feature, often documented in a comment/docstring) but no decision owns it. Tells: a docstring/comment that *justifies* the divergence ("regardless of what the data source records"), a deliberate short-circuit, a `# intentional` aside. Resolution: capture the waiver as a decision that names what it forecloses.

Cross-check every candidate against current heads with `ndr search '<terms>'` / `ndr current --area <area>` — never `Read` a seed atom directly (the CLI owns the supersession walk). If a head already records the waiver, it is owned — not a finding.

## Routing (Phase 8)

| Finding | Route |
|---------|-------|
| Silently waived departure | `/capture-decision` — record the waiver, name what it forecloses, add a revisit trigger |
| Unrepresentable / overreach scenario | follow-up change (Linear / spec-flow) **or** `/capture-decision` to accept the limitation explicitly |
| Conflation | follow-up change to decouple, **or** captured decision if the coupling is deliberate |
| Latent axis | follow-up change to lift it to its own axis |
| Accidental departure (drift) | hand to `drift-check` |

The governing principle: a foreclosure must be *owned forward* — captured as a commitment that names its cost — never left as an inline convenience.

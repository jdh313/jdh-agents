# Gap-report scaffold

The Phase 6 report, written to `<repo>/.docs/model-review-<timestamp>.md` (gitignored scratch). Group by finding type, lead with the headline gap, trace every gap to a cause. Quote code sites as `path:line`.

```markdown
# Model review — <model name>

_<repo> · <timestamp> · interrogate-model_

## The model

| Axis | Values | Defined at | Intended orthogonal? |
|------|--------|-----------|---------------------|
| <axis> | <values> | `path:line` | yes / claimed |

Governing decisions: <ndr:refs surfaced by /ground>.

## Headline

<One sentence: the most consequential thing this model cannot express, and why.>

## Unrepresentable / only-via-overreach scenarios

| Scenario | Verdict | Blocked by |
|----------|---------|-----------|
| <subject–action–object–scope> | unrepresentable / only-via-overreach | `path:line` — <the axis or coupling> |

For each overreach scenario, name the unwanted authority it drags in.

## Conflations (forced cross-axis co-variation)

- **<axis A> × <axis B>** — <how a value of A overrides B>. `path:line`. Contradicts `<ndr:ref>` if a principle is stated.

## Latent axes (concerns fused into an existing axis)

- **<concern>** — currently rides inside <axis>/<value>. Should be its own axis because <the two are independently needed>. `path:line`.

## Silently waived departures

- **<principle>** waived at `path:line` — <the deliberate departure, quote the docstring/comment>. No owning decision (`ndr current` confirms). Forecloses: <scenarios>.

## Seam analysis

<Which axis came first, which arrived later, and the shim at the seam that fused them. The counterfactual the original work never posed.>

## Recommended routing

| Finding | Resolution | Handoff |
|---------|-----------|---------|
| <finding> | capture waiver / decouple / lift axis / accept-and-own | `/capture-decision` · Linear · spec-flow · drift-check |
```

## Shape guidance

- **Lead with the headline gap**, not the axes table — the reader wants the load-bearing limitation first.
- **Every gap names its cause.** A gap row with an empty "blocked by" is unfinished analysis.
- **Distinguish overreach from unrepresentable.** "Works but over-grants" is a different (often more dangerous) finding than "impossible" — it passes tests while leaking authority.
- **Keep findings to what the matrix and audit produced.** This is a representability report, not a structural one — send module-depth/coupling observations to `improve-codebase-architecture` rather than folding them in.

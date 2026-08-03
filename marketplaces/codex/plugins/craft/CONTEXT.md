# craft

Craftsmanship and design-quality skills: diagnosis, TDD, prototyping, architecture deepening, and model representability review. Adapted in part from mattpocock/skills (MIT).

## Language

These terms are the operating vocabulary of `interrogate-model` (representability review). Other craft skills add their terms here as they crystallise.

**Model (under review)**
The system's domain model in the DDD sense: the holistic abstraction of what the design represents — its schemes, axes, roles, and state spaces, and how they compose. The object of a **representability** review (which legitimate states/scenarios it can and cannot express — Minsky's "make illegal states unrepresentable," read forward), distinct from a **structural** review of module depth/coupling.
_Avoid_: the model (LLM sense), `models.py` / ORM entity, schema, design (too broad)
_See_: `interrogate-model` skill, `improve-codebase-architecture` skill (the structural counterpart)

**Axis**
An independently-variable dimension of the model, along which a principal's authority is set without constraining the others. The defining test: *can this dimension's value vary independently for a legitimate scenario?* Forced co-variation between two axes is a **conflation**. A concern that should be its own axis but was absorbed into another is a **latent axis** (a missing dimension). Example: an authz model with a *role/action* axis (viewer/editor/admin) and a *tenant-scope* axis (specific tenants / all); "system administration" fused into the admin role is a latent axis.
_Avoid_: dimension (ok as a gloss), field, attribute, role (a role is one *value* on the role axis, not an axis)

**Scenario**
The unit `interrogate-model` enumerates and tests: a legitimate thing the model must be able to express — a capability, a state combination, a configuration. A model is **representability-complete** iff every legitimate scenario is **representable**. The three verdicts per scenario: *representable*, *unrepresentable*, or *only-via-overreach* (expressible only by over-committing another axis — e.g. "delete within one tenant" reachable only by granting global superuser). Domain-agnostic: applies to access models, state machines, data models, pricing models.
_Avoid_: use case (ok as a gloss; carries UML actor-flavor), test case, requirement, story

**Subject** *(access-model scenarios only)*
The *who* of a scenario when the model is an access/authorization model: the noun behind the verb in a *subject–action–object–scope* capability statement (CS owner, global viewer, service account). A domain-specific decomposition of a scenario, not a top-level term — state-machine and data-model scenarios have no subject.
_Avoid_: persona, actor (too close to *role*), user, principal (reserve for authenticated-identity sense)

**Departure**
An observable divergence between the model's behavior and one of its own stated principles (an NDR atom, a CONTEXT.md invariant, an explicit commitment). Intent-neutral: a departure is either *accidental* (drift → `drift-check`) or **waived**.
_Avoid_: exception (code collision), override (OOP collision), violation, drift (drift is the *accidental* species specifically)

**Waive** *(v.)*
To deliberately set aside a stated principle to allow a departure. The `interrogate-model` finding is a **silently waived departure**: one waived in inline code / comment / docstring instead of by a named decision that records what it forecloses. Example: an all-scope short-circuit in a policy function that silently waives a stated axis-orthogonality principle, documented only in a comment. Division of labor: `drift-check` catches accidental departures; `interrogate-model` catches silently waived ones.
_Avoid_: waiver/carve-out (ok as glosses; prefer the verb *waive* and the noun *departure*)

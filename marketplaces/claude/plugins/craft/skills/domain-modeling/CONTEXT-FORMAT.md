# CONTEXT.md Format

The per-repo glossary this skill maintains. Lives at the repo root. AI-maintained, definitions only, no prose, no rationale.

## Structure

```markdown
# {Repo Name}

{One or two sentence description of what this repo is and what it's for.}

## Language

**Term**
One- or two-sentence definition. Define what it IS, not what it does.
_Avoid_: alias1, alias2, alias3
_See_: [[Vault Wiki Page]] OR ndr:area/topic/NNNN-slug

**Another Term**
...
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others as `_Avoid_:` aliases. Indecisive glossaries are useless glossaries.
- **Keep definitions tight.** One or two sentences max. Define what the thing IS. If you need a paragraph, the content belongs elsewhere (code docstring, NDR atom, vault wiki page).
- **Only project-specific terms.** General programming concepts (timeout, error, callback, retry) don't belong here even if the repo uses them. Before adding a term, ask: is this concept unique to *this repo's* domain, or is it general programming vocabulary? Only the former earns an entry.
- **Group under subheadings only when natural clusters emerge.** A flat `## Language` list is fine for most repos. Sub-group only when the glossary grows past ~15 terms AND there are obvious clusters.
- **Flag ambiguities explicitly.** If a term is used inconsistently in the codebase, add a `## Flagged ambiguities` section at the bottom with the conflict and the canonical resolution. Don't silently pick one usage.

## Link conventions

Two link types, both pragmatic — they work fully when the reader is in the right tool, and read as legible text otherwise.

- **`_See_: [[Wiki Page]]`** — pointer to a vault wiki page that holds deeper context. Renders as a live link in Obsidian; legible-as-text elsewhere. Use for personal repos. **Do not use for work repos** — work code is proprietary, the vault is personal.
- **`_See_: ndr:area/topic/NNNN-slug`** — pointer to an NDR atom that holds the decision rationale. Resolved via `/decisions` or `@ndr-reader`.

Both link types are optional. Most entries don't need them.

## Single-repo (default)

One `CONTEXT.md` at the repo root. This covers nearly every case.

## Multi-context (work repos only, future)

If a proprietary monorepo grows multiple bounded contexts (Ordering, Billing, Fulfillment, etc.), a `CONTEXT-MAP.md` at the repo root catalogs them and points to per-context glossaries:

```markdown
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) — manages warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment**: Ordering emits `OrderPlaced` events; Fulfillment consumes them
- **Fulfillment → Billing**: Fulfillment emits `ShipmentDispatched` events; Billing consumes them
- **Ordering ↔ Billing**: Shared types for `CustomerId` and `Money`
```

The skill infers which structure applies:

- If `CONTEXT-MAP.md` exists, read it to find contexts
- If only a root `CONTEXT.md` exists, single context
- If neither exists, create a root `CONTEXT.md` lazily when the first term is resolved

**Not for personal repos.** Personal repos use vault wiki pages as the cross-cutting authority; CONTEXT-MAP.md is overhead they don't earn.

## Explicit non-goals

- **No example dialogue.** Definitions only — no demonstrative "dev meets domain expert" conversation. Write-once-never-maintained content. Skip.
- **No rationale.** Why a term was chosen, what alternatives were considered, what trade-offs were weighed — none of that goes in CONTEXT.md. That's NDR territory.
- **No implementation hints.** What functions use a term, what files implement it, what the migration path is — none of that goes here. CONTEXT.md answers "what do we call this?" Only.

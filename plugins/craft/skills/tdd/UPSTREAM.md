# Upstream divergences — tdd

_Upstream: `mattpocock/skills` · `skills/engineering/tdd` · ledger current as of `reviewed_sha: 7afa86d3a5dd`_

Intentional divergences from upstream. Reviewed via `provenance:upstream-review` (2026-06-11) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The red-green-refactor loop, the horizontal-slices anti-pattern, the per-cycle checklist, and the `tests.md` / `mocking.md` / `refactoring.md` / `interface-design.md` siblings are kept verbatim. No fabricated attributions, no silent drops.

| Kind | What | Why |
|------|------|-----|
| changed | Planning §1 grounding: generic "domain glossary" → **CONTEXT.md**; "respect ADRs in the area" → invoke **`/ground`** to surface **NDR atoms** | Routes the upstream's vague grounding step into the concrete CONTEXT.md glossary + NDR decision-ledger primitives. |
| changed | `deep-modules.md` retitled "Deep Modules" → "Deep Modules **in TDD**"; defers the canonical Module/Interface/Depth/Seam/Adapter/Leverage/Locality glossary to shared `../../references/LANGUAGE.md` and adds a TDD-specific depth payoff | De-dupes the shared `craft`-plugin glossary; one source of truth across sibling skills (grill-with-docs, improve-codebase-architecture). |

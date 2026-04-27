# spec-flow

ADR-centric workflow tooling for AI-assisted development. Composes with — does not replace — Claude Code's `CLAUDE.md`, plan mode, and skills.

## Premise

Spec-Driven Development's honest failure mode is stale parallel docs. Humans don't maintain prose alongside code; agents do, but only the prose they touch. The pure spec-first ideal collapses the moment someone types `Edit` instead of writing markdown.

This plugin sidesteps that failure by refusing to maintain a "current system spec" at all. Instead it operates on a three-layer model with bounded drift:

| Layer | Lifecycle | Drift profile |
|---|---|---|
| **ADRs** (durable why) | Punctual: written once, amended or superseded only on real decisions | Drifts only when code diverges from a recorded decision — detectable |
| **Session notes** (disposable plans) | Session-scoped: dated, archived at end of day | Frozen-by-design once the day ends; can't go stale |
| **Generated docs** (derived) | Tied to code | Can't drift; regenerated from source |

The plugin's contribution is **maintenance discipline for the ADR layer** plus **scaffolding for the session-note layer**. Generated docs aren't its concern.

## Skills shipped (v0.1)

- **`adr-drift-check`** — On-demand check: scan an ADR directory, read only `Accepted` ADRs, compare against a diff (working tree, branch range, or commit range), and propose resolutions for each detected divergence: **amend / supersede / revert**. Also surfaces `Proposed` ADRs older than a threshold as a quieter "stalled ratification" signal.
- **`session-spec`** — Scaffold a dated working-session note in an Obsidian vault. Template includes Goal / Tiers / Components / Non-goals / Dependencies / Risks / End-of-day artifacts / **Reflection (with `Decisions to promote to ADRs:` line as the drift-prevention nudge)**.

## Skills deferred

These will earn their existence after v0.1 use exposes the next gap:

- **`adr-evaluate`** — Interactive worthiness gate. Walks through criteria from `references/worthiness-criteria.md`; if the candidate passes, scaffolds a `Status: Proposed` ADR. If it fails, suggests where else it should live (CLAUDE.md gotcha, session-note Reflection, code comment, no record needed).
- **`adr-accept`** — Formal ratification ritual: read Context/Constraints/Decision/Consequences, walk Review Notes, trim resolved items, flip status to `Accepted`. Today this is a manual edit; the skill exists once the ritual gains enough surface area to justify automation.
- **`finding-capture`** — Append AI-dev observations to a Track 2 / experiment scratch note with consistent format and dating.

## ADR conventions

The plugin follows a schema modeled on the voyager project's ADR practice (`docs/arch/`):

- **Filename:** `NNNN-slug.md` under an ADR directory (project default: `notes/adr/`)
- **Schema:** Title / Status / Context / **Constraints** / Decision / Consequences / Alternatives Considered / Review Notes *(to be trimmed before acceptance)*
- **Status lifecycle:** `Proposed` → `Accepted` → (`Rejected` | `Superseded by ADR-NNNN`)
- **Acceptance is a deliberate human step.** New ADRs are always created `Proposed`. The agent never unilaterally accepts.
- **Review Notes section is the agent's question-parking surface during drafting.** The human resolves items there during ratification, then trims before flipping to `Accepted`.

Full schema and template in `references/adr-schema.md`. Worthiness criteria in `references/worthiness-criteria.md`.

## Working session conventions

- **Filename:** `<YYYY-MM-DD> Working Session.md` under the project's vault folder
- **Template** in `references/working-session-template.md`
- **Drift mitigation:** the Reflection section's `Decisions to promote to ADRs:` line is the bridge between session-scoped planning and the durable ADR layer. Anything that locks in a constraint binding future code goes there before end-of-day.

## What this plugin is not

- Not a system-spec maintainer. There is no "current state of the system" doc this plugin keeps current.
- Not a CLAUDE.md replacement. Standards / gotchas / always-loaded context still belong there.
- Not a plan-mode replacement. Plan mode handles per-task planning during agent work; session-spec handles the day-level container around that work.

# Upstream divergences — improve-codebase-architecture

_Upstream: `mattpocock/skills` · `skills/engineering/improve-codebase-architecture` · ledger current as of `reviewed_sha: 321658273cb1`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-27) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The grilling-loop structure is upstream behavior, kept. Upstream itself moved to a live-dispatch model in this revision — the architecture vocabulary and the domain-model side effects now route to the shared `codebase-design` / `domain-modeling` skills rather than living inline, matching upstream's own restructuring. No fabricated attributions, no silent drops.

| Kind | What | Why |
|------|------|-----|
| changed | Report format: upstream self-contained HTML (Tailwind + Mermaid via CDN, written to `$TMPDIR`) → markdown + Mermaid fences + ASCII, written to gitignored `<repo>/.docs/architecture-review-<ts>.md`. Sibling `HTML-REPORT.md` → `MARKDOWN-REPORT.md`. | No CDN; renders natively in GitHub / Obsidian / VS Code. `.docs/` is the ecosystem's standard scratch space, kept out of the tracked tree. |
| changed | Decision layer: in-repo ADRs (`docs/adr/`, `ADR-FORMAT.md`, "ADR conflicts" callout, "Offer an ADR" on rejection) → NDR atoms, captured via `/capture-decision`. That routing now lives entirely inside `Skill(craft:domain-modeling)` rather than being re-specified here (see next row). | NDR is this ecosystem's durable decision layer; same don't-re-litigate / capture-on-rejection discipline, only destination + write-authority change. |
| changed | Architecture vocabulary: inline "Glossary" section (Module/Interface/Depth/Seam/Adapter/Leverage/Locality + key principles, linking `../../references/LANGUAGE.md`) → single dispatch line to `Skill(craft:codebase-design)`. The same repointing was made in `MARKDOWN-REPORT.md`'s 3 vocabulary references. | Matches upstream's live-dispatch restructuring; one glossary owner instead of a second copy that can drift from `references/LANGUAGE.md`. (Citation note, 2026-08-29: upstream has since reworded this dispatch twice — `d28dfdc39bea` then `fcf0071560d3` — and it now reads `call the Skill tool with "codebase-design"`. Phrasing only; the dispatch itself is unchanged.) |
| changed | Grilling-loop domain-model side effects (CONTEXT.md term additions, fuzzy-term sharpening, NDR-atom offer on candidate rejection — previously 3 separate bullets) → single dispatch bullet to `Skill(craft:domain-modeling)`, which now owns that discipline (including the capture-decision gate) centrally. | Matches upstream's live-dispatch restructuring ("run the `/domain-modeling` skill to keep the domain model current"); avoids re-specifying decision-capture rules `domain-modeling` already encodes. |
| removed | `INTERFACE-DESIGN.md` and `DEEPENING.md` deleted from this skill dir; the "explore alternative interfaces" step now dispatches `Skill(craft:codebase-design)` (its `DESIGN-IT-TWICE.md` and `DEEPENING.md` siblings). | Content had already moved to `craft:codebase-design` in an earlier consolidation (see that skill's `UPSTREAM.md`) — this was the deferred rewiring of this skill as a consumer. **Reversed 2026-08-24 — see "Vocabulary re-divergence" below; both files are back in this directory.** |
| removed | `allowed-tools: Edit` dropped. | This skill no longer edits `CONTEXT.md` directly — that responsibility lives entirely in the dispatched `craft:domain-modeling` skill, which carries its own `Edit` grant. |
| added | `effort: high` frontmatter field | Codebase exploration + grilling loop are reasoning-intensive; high effort engages deeper model reasoning for the full skill duration. |
| changed | Explore subagent dispatch: upstream's bare spawn → named `arch-explorer` with bounded task, inputs and deliverables. | Names the agent so it stays addressable via SendMessage during the grilling loop; unnamed agents cannot be continued without full re-dispatch. (Citation note, 2026-08-29: this row originally quoted upstream's `subagent_type=Explore`, which no longer exists — `14bfbbd8654a` made the dispatch harness-neutral and `c0d69015e0cc` trimmed it to a bare "spawn a sub-agent". Our elaboration is additive to that neutral instruction, not a contradiction of it.) |
| not-added | `disallowed-tools:` for source-editing restriction | Considered but skipped: skill legitimately writes to gitignored `.docs/` (report). No tool-level carve-out available for "tracked source only." |
| changed | Step 3 grilling loop dispatches `Skill(craft:grill)`, matching upstream's `run the /grilling skill`. Local addition: the loop is scoped to the picked candidate, and factual questions route to the `arch-explorer` subagent rather than to the user. | Resolves a dangling reference. This step previously read "drop into a grilling conversation" — prose naming a discipline no skill in this marketplace defined, because `grilling` had never been ported. Recorded as a backfilled divergence on 2026-07-27 and closed the same day by porting it as `craft:grill`. The `arch-explorer` routing is local: it makes `grill`'s look-it-up-don't-ask move concrete when an exploration subagent already holds the codebase context. |

Adopted from upstream at `697d4ce9742d` (2026-07-27), now equivalent and needing no divergence row: the step-1 **YAGNI scoping gate** (`45afd80` — take the user's named direction, else find hot spots via `git log --oneline`), placed ahead of the `/ground` call since it determines the area to ground in; and the "design tree" → "decision tree" rename (`3bb587f`).

## Vocabulary re-divergence (2026-08-24)

Upstream keeps the deep-module vocabulary as a model-invoked skill
(`skills/engineering/codebase-design`). This adaptation no longer does. The
glossary now lives at [`../../CODEBASE-DESIGN.md`](../../CODEBASE-DESIGN.md) —
a plugin-root reference file reached by relative path, the same pattern
`RUNTIME.md` and `CONTEXT.md` already use — and the two procedures that build on
it, `DEEPENING.md` and `DESIGN-IT-TWICE.md`, live in this directory, their only
caller.

**Why.** `codebase-design` carried a `description` claiming it could "find
deepening opportunities," which is this skill's job; two skills competing on one
trigger phrase is a router coin-flip. Of its nine inbound references, eight were
glossary lookups and one (`SKILL.md:85`) invoked an actual procedure. A skill
whose body has no Process section and whose frontmatter grants no `Write` tool
is a reference wearing a skill's clothes.

Three ledger heads bear on the new shape and are satisfied by it:

- `ndr:6x3v6p` / `ndr:jsw3nz` — a boundary enforced in one place must also be
  stated in body prose. Every consumer of the glossary now carries the
  use-these-terms-exactly rule inline; the link supplies the full definitions,
  not the discipline.
- `ndr:v4wn6d` — composition gates on structural conditions, not agent
  self-judgment. A file read is structural; a `Skill()` dispatch depended on the
  agent electing to invoke.
- `ndr:kpefq4` — prefer portable wording across runtimes. A relative markdown
  link is target-neutral where `Skill(craft:codebase-design)` is Claude-flavored.

**Attribution.** The glossary, "Deep vs shallow," Principles, "Designing for
testability," Relationships, and Rejected framings remain upstream content
(`mattpocock/skills`, MIT, © 2026 Matt Pocock), reviewed at `697d4ce9742d`.
`DESIGN-IT-TWICE.md` and `DEEPENING.md` are byte-identical to upstream modulo
link paths. The retired skill's own divergence record — including that its
glossary body was itself consolidated from a former `references/LANGUAGE.md`
that predated upstream's restructuring — is preserved in git history at
`plugins/craft/skills/codebase-design/UPSTREAM.md`.

# Upstream divergences — breakdown

_Upstream: `mattpocock/skills` · `skills/engineering/to-issues` · ledger current as of `reviewed_sha: 0172e61e57c9`_

Baseline pin — divergences below are seeded from the adaptation notes in this plugin's README.md Credits section, not from a formal behavioral reconciliation. The skill still owes a first `provenance:upstream-review` pass (`status: baseline`) before these entries can be treated as reviewed. Read by `upstream-review` only; never referenced from `SKILL.md`.

| Kind | What | Why |
|------|------|-----|
| added | ndr grounding pre-pass before slicing | Surfaces relevant NDR decision atoms so slices don't contradict a standing architectural decision. |
| changed | body template conforms to `references/issue-shape.md` | Aligns generated ticket bodies with this workspace's issue-shape convention instead of upstream's generic template. |
| added | native Linear blocks/blocked-by relations | Wires dependency order using Linear's native relation fields rather than prose-only sequencing. |
| added | parent-ticket linking | Links each published slice back to the source ticket/goal for traceability. |
| added | `Decision`-type slice handling with capture-decision follow-up | Routes slices that are themselves architectural decisions into the ndr capture flow instead of treating them as plain work items. |
| added | optional spec-flow handoff for contract-shaped slices | Lets a slice large enough to merit a contract hand off directly into `spec-flow:draft`. |
| dropped | HITL/AFK label split | Considered during the port and deferred — not adopted in this workspace's label set. |

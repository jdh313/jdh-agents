# Upstream divergences — breakdown

_Upstream: `mattpocock/skills` · `skills/engineering/to-tickets` · ledger current as of `reviewed_sha: d29732e49f60`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (2026-07-09) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`. Upstream's `to-issues` skill (this port's original source) has since been merged with `to-plan` into `to-tickets`; this is the first formal reconciliation pass against the merged skill.

| Kind | What | Why |
|------|------|-----|
| added | ndr grounding pre-pass before slicing | Surfaces relevant NDR decision atoms so slices don't contradict a standing architectural decision. |
| changed | body template conforms to `references/issue-shape.md` | Aligns generated ticket bodies with this workspace's issue-shape convention instead of upstream's generic template. |
| added | native Linear blocks/blocked-by relations | Wires dependency order using Linear's native relation fields rather than prose-only sequencing. |
| diverged | parent-ticket linking mechanic: Linear `parent` relation + confirm-parent-ID-before-publish, vs. upstream's native sub-issue / `## Parent` fallback | Upstream's `to-issues` already linked children back to a parent ticket; what this port changed is the mechanic, not whether linking happens at all. |
| added | `Decision`-type slice handling with capture-decision follow-up | Routes slices that are themselves architectural decisions into the ndr capture flow instead of treating them as plain work items. |
| added | optional spec-flow handoff for contract-shaped slices | Lets a slice large enough to merit a contract hand off directly into `spec-flow:draft`. |
| dropped | HITL/AFK label split | Considered during the port and deferred — not adopted in this workspace's label set. |
| adopted (2026-07-09) | Wide-refactor (expand -> migrate -> contract) sequencing for blast-radius-fanning mechanical changes, folded into the draft-vertical-slices step | Adopted upstream's exception to vertical slicing — some changes (a column rename/retype) can't land green as a tracer bullet; expand-contract sequencing keeps CI green batch to batch. Adapted to Linear-native blocks/blocked-by relations. |
| adopted (2026-07-09) | Prefactoring line re-added to the codebase-exploration step ("Make the change easy, then make the easy change.") | Restores a line that was silently dropped during the original to-issues port; upstream still carries it in `to-tickets`. |

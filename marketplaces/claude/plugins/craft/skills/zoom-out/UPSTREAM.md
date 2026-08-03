# Upstream divergences — zoom-out

_Upstream: `mattpocock/skills` · `skills/engineering/zoom-out` · ledger current as of `reviewed_sha: 7afa86d3a5dd` (last live upstream revision)_

Reviewed via `skillsmith:upstream-review` (2026-06-11, re-reviewed 2026-07-27) — do not re-flag as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

## No longer a live fork

**Upstream deleted this skill at `e112a6b03cd7` (2026-06-17, "Remove zoom-out skill and all references"), with no stated rationale.** Our pin `7afa86d3a5dd` (2026-06-11) is the last revision that existed upstream. We are keeping the skill; it is now ours to own outright.

Consequences for future reviews:

- `status: upstream-removed` in the provenance block, with `removed_sha` recording the deletion commit. There is nothing left to drift against — a drift check on this skill will always come back empty, and that is the expected result, not a clean bill.
- Changes made here from now on are local evolution, not divergence. **Stop adding divergence rows.** The table below is frozen as the historical record of the adaptation as it stood while upstream was live.
- The MIT attribution line stays. Upstream retiring the skill does not retire the license obligation on the code we took.

## Historical record (frozen at `7afa86d3a5dd`)

**Verbatim adoption.** The body instruction and description were byte-identical to upstream; `disable-model-invocation: true` matched. The skill is terse by design upstream — its brevity was not a local truncation. No behavioral divergences, no fabricated attributions, no silent drops.

The only local additions were non-behavioral: the MIT attribution line and the `upstream:` provenance block.

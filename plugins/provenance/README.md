# provenance

Marketplace upkeep for borrowed work. Several skills in this marketplace are adapted from upstream sources (e.g. `mattpocock/skills`). Adaptation is fine — but every divergence should be deliberate, documented, and free of fabricated claims about what upstream actually does.

## Skills

- **upstream-review** — Compare an adapted skill against its pinned upstream source. Classifies each behavioral unit as kept / diverged / dropped / added, hunts fabricated attributions (local claims about upstream that upstream doesn't support), proposes fixes for sign-off, and refreshes the reviewed commit SHA.

## Provenance convention

Each adapted skill pins its source in its own SKILL.md frontmatter:

```yaml
upstream:
  repo: owner/name
  path: path/to/skill/dir
  reviewed_sha: <12-char sha>   # last upstream commit touching `path` that we reconciled against
  reviewed: YYYY-MM-DD
  status: reviewed | baseline   # `baseline` = pinned without a behavioral review (still owes a first review)
```

Drift = a newer commit has touched `path` since `reviewed_sha`. A `baseline` pin only catches *future* upstream commits — it does not certify that the current adaptation matches the pinned SHA, so baseline skills still owe a full `upstream-review`. A future scheduled job (GitHub Action) can walk every `upstream:` block and open an issue for skills that have fallen behind; `upstream-review` does the per-skill reconciliation on demand.

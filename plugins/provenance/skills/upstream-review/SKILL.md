---
name: upstream-review
description: Review an adapted/borrowed skill against its upstream source — compare behavior (not just text), flag dropped moves, silent divergences, and fabricated attributions, then refresh the pinned upstream commit SHA. Use when adopting a skill from another repo, when an upstream skill may have changed, or when the user says "review this against upstream", "check upstream drift", "did upstream change", "is our adaptation still honest".
---

Keep adapted skills honest against the source they came from. An adaptation is allowed to diverge — that is the point — but every divergence should be **deliberate and documented**, and no claim about what upstream "does" or "asked for" should be made unless upstream actually does it.

This is a judgment task, not a text diff. It produces a divergence report and proposed fixes; it never auto-rewrites without sign-off.

## Two modes

- **Intake** — adopting a skill from another repo for the first time. No `upstream:` block exists yet. The user supplies the source (repo + path, or a URL). Produce the first review and write the provenance block.
- **Drift** — an already-adapted skill whose `upstream:` block exists. Check whether upstream moved past the pinned SHA; if so, review what changed.

## Provenance block (SKILL.md frontmatter)

Every adapted skill carries this in its own frontmatter — the SHA is pinned next to the skill it governs:

```yaml
upstream:
  repo: owner/name              # GitHub slug
  path: path/to/skill/dir       # path within the upstream repo
  reviewed_sha: <12-char sha>   # the last upstream commit touching `path` that we reconciled against
  reviewed: YYYY-MM-DD          # date of that reconciliation
  status: reviewed | baseline   # see below
```

`reviewed_sha` is the **last commit that touched `path`**, not the repo HEAD. Drift = "a newer commit has touched `path` since `reviewed_sha`."

`status` records what kind of reconciliation produced the pin:

- **`reviewed`** — a full behavioral comparison was run against `reviewed_sha`; divergences are known and documented.
- **`baseline`** — provenance was pinned without a behavioral review (e.g. a backfill). The SHA is captured, but **pre-existing silent divergences between the local adaptation and `reviewed_sha` have not been checked**. A drift check on a baseline skill only catches *future* upstream commits — so a `baseline` skill still owes a first full review. Treat `baseline` as a to-do, not a clean bill.

## Procedure

1. **Resolve provenance.** Drift mode: read the `upstream:` block. Intake mode: take `repo` + `path` from the user (derive from a URL if given).

2. **Detect drift** (drift mode):
   ```bash
   gh api 'repos/<repo>/commits?path=<path>&per_page=1' --jq '.[0].sha[0:12] + "  " + .[0].commit.committer.date'
   ```
   If that SHA equals `reviewed_sha`, upstream is unchanged — report "no drift" and stop. Otherwise continue.

3. **Fetch the upstream files verbatim.** Use the GitHub API, NOT WebFetch — WebFetch routes through a summarizing model that drops content (link conventions, whole sections) and refuses verbatim reproduction past its quote limit. Get the real bytes:
   ```bash
   gh api repos/<repo>/contents/<path>/SKILL.md --jq '.content' | base64 -d
   ```
   List the directory first (`gh api repos/<repo>/contents/<path>`) and pull every relevant file (SKILL.md, FORMAT/template files, referenced docs), not just SKILL.md.

4. **Compare behavior, not prose.** Enumerate the load-bearing units on each side — conversation moves, sections, gates, decision criteria, file/artifact conventions — and classify:
   - **Kept** — present and substantively equivalent.
   - **Diverged** — present on both, behavior changed (renamed concept, narrowed scope, swapped destination/authority).
   - **Dropped** — in upstream, absent locally. Ask: deliberate (and documented as a non-goal) or silent? Silent drops are the main finding.
   - **Added** — local-only. Fine, but should not be attributed to upstream.

5. **Hunt fabricated attributions specifically.** Any local claim of the form "the original did/asked for/required X" must be checked against the fetched upstream. If upstream doesn't contain X, the claim is fabricated — flag it and reword to a positive statement that drops the false provenance. This is the highest-value check; it is the class of error a human adapter most often introduces from memory.

6. **Report**, load-bearing finding first: a short table (kept / diverged / dropped / added) plus a callout list of fabricated attributions and silent divergences. One finding at a time if the user prefers to work through them.

7. **Propose fixes, apply on sign-off** — reword false attributions, document deliberate divergences as explicit non-goals, re-add dropped moves the adaptation didn't mean to lose. Never apply silently.

8. **Refresh provenance.** After review (and any applied fixes), update the `upstream:` block: `reviewed_sha` → the SHA from step 2, `reviewed` → today. For intake, write the block for the first time.

9. **Run the marketplace verify loop** if any file changed — bump the plugin's `plugin.json` version, then:
   ```bash
   uv run python scripts/sync_marketplace.py && uv run python scripts/validate_schema.py && uv run python scripts/lint_plugins.py
   ```

## Non-goals

- **No auto-rewrite.** The behavioral comparison is judgment; surface findings and let the user adjudicate. This skill is the reviewer, not an autopatcher.
- **No license laundering.** Preserve the upstream's license and attribution line. Reviewing for drift never removes a required notice.
- **Not a substitute for the trigger.** This skill reviews on demand. Noticing that upstream moved across the whole marketplace is a scheduled job's role (e.g. a GitHub Action that walks every `upstream:` block and opens an issue for stale ones) — out of scope here.

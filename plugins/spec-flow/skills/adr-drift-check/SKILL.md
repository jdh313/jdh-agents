---
name: adr-drift-check
description: This skill should be used when the user wants to check whether code has drifted from recorded architectural decisions. Trigger phrases include "check ADR drift", "validate ADRs", "audit ADRs against code", "are my ADRs still accurate", "drift check", "is the code still consistent with the ADRs", or when the user asks for an audit of the durable decision layer against current implementation. Reads only `Accepted` ADRs (skipping `Proposed`/`Rejected`/`Superseded`), compares each against a user-specified diff scope, and proposes one of three resolutions per detected divergence: amend the ADR, supersede the ADR, or revert the code. Also surfaces stale `Proposed` ADRs as a separate quieter signal — those are stalled ratifications, not drift. Runs on demand only; not a hook.
---

# adr-drift-check

Audit `Accepted` ADRs against current code to detect drift. Operates on demand. Returns a structured report; never edits ADRs or code on its own.

## When to invoke

- User explicitly asks for a drift check, ADR audit, or coherence check
- After a meaningful refactor or migration, when the user wants to confirm decisions still hold
- Before a release or PR to a major branch, as part of the user's release-readiness check
- During a periodic ADR sweep (weekly / monthly)

Do NOT invoke for:
- Pre-commit hook style automatic checks — this skill is on-demand only by design
- ADRs in `Proposed` state — they are by definition not yet binding (stale-Proposed surfacing is a separate, quieter output)
- Style or convention drift — ADRs operate at the architecture layer, not code style. Use a linter for style.

## Workflow

### 1. Locate the ADR directory

In order of preference:

1. Check the current repo's `CLAUDE.md` for an ADR-directory mention (e.g. `notes/adr/`, `docs/arch/`).
2. Look for conventional locations: `notes/adr/`, `docs/arch/`, `docs/adr/`, `adr/`.
3. Ask the user.

If the directory exists but contains only a template (`0000-template.md` or no Accepted ADRs), report that there's nothing to check and stop.

### 2. Determine diff scope

Ask the user to choose, with sensible defaults:

- **Working tree** — uncommitted + staged changes vs `HEAD`. Default for "drift check before commit".
- **Branch range** — `git diff main...HEAD` or equivalent. Default for "drift check before PR".
- **Commit range** — `git log -p HEAD~N..HEAD` for arbitrary windows. Default `N=10` if user says "recent" without specifying.
- **Full repo audit** — every `Accepted` ADR vs current `HEAD`. Most expensive; reserve for periodic sweeps.

Surface the chosen scope explicitly in the final report — drift detected against working tree changes is different evidence than drift across a 6-month branch range.

### 3. Read all Accepted ADRs

```bash
# Read each ADR; skip non-Accepted
for f in <adr-dir>/*.md; do
  # parse Status field; skip if not "Accepted"
done
```

For each `Accepted` ADR, extract:
- Title
- Constraints section (the forces the decision was supposed to preserve)
- Decision section (the affirmative statement)
- Consequences section (especially negative consequences — those describe what was deliberately accepted)

### 4. For each ADR, check the diff

Read the diff scope. For each ADR, ask:

1. **Does any code in the diff appear to violate the Decision?** Look for: file paths, module structure, library usage, schema shapes, API surfaces explicitly named in the ADR.
2. **Does any code in the diff appear to violate a Constraint?** Constraints are often the most code-bound section — "must not import from", "must run on", "must keep PHI out".
3. **Does any code in the diff invalidate a Consequence?** A consequence that no longer holds is drift even if the surface code looks fine.

If none of the three trigger, the ADR is not in drift for this scope. Move on.

### 5. For each detected divergence, propose three resolutions

Output one report entry per detected divergence with this structure:

```
### ADR-NNNN: <Title>

**Detected divergence:**
<Specific evidence from the diff. Quote the ADR clause that is at risk and the code change that creates the tension. Cite file paths and line numbers where possible.>

**Proposed resolutions:**

1. **Amend ADR** — <What the ADR's Context / Constraints / Decision / Consequences would change to.>
   When this is right: the new code is correct and the ADR's framing was incomplete or outdated.

2. **Supersede ADR** — <Sketch the new ADR title and how it would relate.>
   When this is right: the architectural choice has fundamentally changed, not just been refined. Original ADR stays in the record with a forward link.

3. **Revert code** — <Specify which change in the diff would need to come out.>
   When this is right: the code change was an oversight or shortcut that violated a deliberate constraint. The ADR was right; the diff was wrong.

**Recommendation:** <If the evidence clearly favors one resolution, say so. Otherwise present neutrally and let the user decide.>
```

The skill never *executes* a resolution — it surfaces options. Editing ADRs and code remains the human's call.

### 6. Surface stalled Proposed ADRs (quieter signal)

After the main drift report, scan `Proposed` ADRs and flag any that are older than the staleness threshold:

- Default threshold: **7 days** since `date_created` (or file mtime if no date in frontmatter)
- If user-configurable threshold exists in `.spec-flow.toml`, honor it; otherwise default

Report stalled `Proposed` ADRs in a clearly separate section:

```
## Stalled Proposed ADRs

These ADRs have been Proposed for longer than <N> days. They aren't drift — they're stalled ratifications. Review and either flip to Accepted, mark Rejected, or update the Status section explaining why ratification is deferred.

- ADR-NNNN: <Title> — proposed <N> days ago
- ...
```

Don't mix this into the drift section. Stalled-Proposed is a *process* signal, not a coherence signal.

### 7. Final report shape

```
# ADR Drift Check — <date>

**Scope:** <working tree | branch range main...HEAD | commit range HEAD~10..HEAD | full repo>
**ADRs reviewed:** <N Accepted, <M> skipped (non-Accepted)>
**Divergences detected:** <K>

## Divergences

<Per-ADR entries from step 5, or "(none)" if no drift found.>

## Stalled Proposed ADRs

<From step 6, or "(none)" if none.>

## Notes

<Anything the skill couldn't decide cleanly — ambiguous evidence, ADRs the diff didn't touch but might be worth a manual look, etc.>
```

If divergences = 0 and stalled-Proposed = 0, the report is short and that's fine. The point is verification, not noise.

## What the skill does not do

- **Does not edit ADRs or code.** All resolutions are proposals. The human ratifies.
- **Does not run as a hook.** The user's v0.1 preference is on-demand only. Hook-driven drift detection is a separate decision and a separate skill if it's ever built.
- **Does not check Proposed ADRs against code.** Proposed = in flight = not binding. Stalled-Proposed surfacing is a process check, not a drift check.
- **Does not check style or convention drift.** That's CLAUDE.md / linter territory.
- **Does not invent worthiness criteria.** If a divergence suggests an *unrecorded* decision should become an ADR, surface it as a note for `adr-evaluate` (deferred), not as a drift entry.

## Edge cases

- **No ADRs found.** Report cleanly, suggest the user create the directory + template if they want to start using ADRs. Don't error.
- **All ADRs Proposed.** Report "no Accepted ADRs to check; project's ADR layer is not yet ratified." Surface stalled-Proposed if applicable.
- **Diff is empty.** Report "no changes in the requested scope" and stop. Don't run the per-ADR check on an empty diff.
- **Superseded ADR is referenced by code.** If code matches a Superseded ADR but contradicts the superseding one, report it as drift against the superseding ADR with a note about the historical chain.

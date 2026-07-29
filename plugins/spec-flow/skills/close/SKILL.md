---
name: close
description: This skill should be used when the user runs `/spec-flow close [name]` or otherwise signals that an active contract's work is done and ready to migrate. Trigger phrases include "spec-flow close", "this change is done", "archive the X contract", "wrap up the X change", "close out the okta-auth work". Accepts either a file slug or a Linear ticket ID. Reviews the change against the contract, proposes migrations to the durable layer — ndr atoms via `/capture-decision`, README updates via librarian — applies them after user sign-off. For file-host contracts, moves the file to `.docs/archive/`. For Linear-host contracts, advances the ticket to a review state but never sets a completed state — Done stays the user's call at merge.
argument-hint: "[contract slug or TEAM-N; omit to infer]"
allowed-tools:
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issues
  - mcp__linear-server__list_issue_statuses
  - Read
  - Glob
  - Grep
  - Edit
  - Bash(ls *)
  - Bash(trash *)
---

# spec-flow:close

Close an active contract. Migrate durable findings from the **companion doc** to ndr atoms and README, then delete the companion; archive the **contract doc** or hand the ticket back to the human, depending on host. See `../../references/hosts.md` for the two-document model.

## When to invoke

- User runs `/spec-flow close [name]`.
- User signals end-of-change: "this is done, archive it", "wrap up the okta-auth contract".

## Do NOT invoke for

- Mid-implementation pause — that's just stopping work; the contract stays active.
- Abandoning an unfinished change — close implies completion. For abandonment, the user should manually move or delete the file.
- A contract that has never had implementation work — suggest the user re-evaluate before closing (it may be a stub worth retaining or deleting outright).

## Required skills

- **`Skill(ndr:capture-decision)`** — migrating architectural decisions to ndr atoms.
- **`librarian:*`** as appropriate — any README or vault-doc updates.

## Workflow

### 1. Identify the target contract and detect host

Same logic as `spec-flow:implement` step 1: explicit name, or enumerate active contracts across both hosts (`.docs/` scan plus, when the Linear MCP is connected, tickets carrying the `contracted` label — matched case-insensitively — regardless of workflow state), then prompt match or ask. Host detection:

- Identifier matches `^[A-Z]{2,5}-\d+$` → **linear** host.
- Anything else → **file** host.

If host = linear, check that `mcp__linear-server__*` tools are loaded. If not:

> "Linear MCP server isn't connected — I can't read TEAM-123's description. Pause while you wire up the MCP, or close the migration steps using context held in conversation only?"

Do not install or configure the integration without approval, and never ask the user to paste credentials into chat.

### 2. Read both documents and the actual change

The closer is a **cold reader of both tiers** (`233ar3`) — read the contract doc *and* the companion.

- **Contract doc (front-matter)** — file host: `Read` the file. Linear host: fetch description via `mcp__linear-server__get_issue`.
- **Companion doc (working-matter)** — `Read` `.docs/<date>-<slug>-companion.md` on **both** hosts. Locate it via the contract doc's pointer (`companion:` frontmatter key, or the trailing `Companion:` line in the description); failing that, glob `.docs/*-companion.md` for a matching `contract:` value.
- **No companion** — the contract predates v2.3. Fall back to reading working-matter from the contract doc itself; every gate below then reads its *Approach / wiring*, *Decision log*, and *Not yet specified* from there. Note the absence in the close summary. Do not create a companion at close — there is nothing left to write into it.
- **Detect the VCS first** — if `.jj/` exists at the repo root, use `jj log` / `jj diff`; otherwise `git log` / `git diff`. Survey what actually shipped since the contract was created.
- Compare: what was in the companion's *Approach / wiring* (or *Approach* on a pre-v2.1 contract) vs. what's in the code now.

### 2.5. Done-when check (first gate)

Walk each *Done when* bullet against the actual change:

- **Met** — outcome is observable in the diff / repo state.
- **Not met** — outcome is missing or partial. Surface explicitly.
- **Drifted** — outcome shipped, but the bullet no longer describes it well.
- **Met-with-deferral** — a breakdown migrate slice whose bullet was *relative* ("call sites moved; end-to-end green promised at `<final slice>`"). Honor the deferral: this is met, **not** not-met, provided the named final slice exists (and, if already closed, verified). The cross-batch Done-when is owned by the integrate-and-verify slice, not this one.

Prefer behavioral confirmation over diff-reading. If `implement`'s verify step ran this session, reuse its per-bullet result; otherwise run the **`contract-verifier`** procedure (Done-when bullets + diff scope + detected VCS) in isolated subagent context using the runtime mapping in `../../references/hosts.md` — or fall back to running the checks inline (`/verify` if available). A bullet that only *looks* met in the diff is exactly the drift this gate exists to catch.

**Reconcile a drifted bullet (`reconcile` op).** A `drifted` bullet is corrected to shipped reality — a front-matter edit that does *not* renegotiate the target (the thing shipped; only its wording was off), so it rides this close's sign-off rather than a separate `spec-flow:amend`. `reconcile` is legal ONLY on `drifted`, never on `not_met` (didn't ship → halt-and-ask below). Each reconcile **spawns a Decision-log row** capturing *why* the criterion drifted, so the insight harvests in step 4 instead of evaporating with the reworded bullet. Fold the reconciled wording and the spawned row into the sign-off proposal in step 4/5.

If any bullet is **not met**, halt and ask: continue closing anyway (treat as a known gap, note it in the summary), amend the contract via `spec-flow:amend` to reflect a narrower done, or pause closing until the gap ships? Do not silently archive an unmet contract. Do not reach for `reconcile` here — a not-met bullet is a real gap, not a wording drift.

If the contract has no *Done when* section (older format), surface that and either ask the user to draft one inline before review, or fall back to comparing against *Approach / wiring* (or *Approach* on a pre-v2.1 contract). Note the absence in the close summary so future contracts don't repeat the gap.

### 2a. Offer a drift check (optional)

If the `ndr` plugin is installed and has atoms scoped to this project/repo, prompt once:

> "Want to run a drift check against ndr atoms before archiving? (`Skill(ndr:drift-check)` scoped to the change since the contract was created — a jj revset or git range, per the VCS detected in step 2.)"

If yes, dispatch the skill and weave its findings into the migration proposal in step 3 — e.g. an atom flagged with `recommendation: amend` becomes a candidate successor in the *ndr atoms to capture* list. Do not auto-invoke; this is opt-in per close.

### 2b. Deferral materialization gate (second gate)

The companion is ephemeral — it is **deleted** at close (step 6), so its Decision log genuinely dies. A `[deferred]` row tracked *only* there is just forgetting with better manners, so close will not cleanly archive a contract holding an **un-materialized** deferral.

Scan the companion's Decision log for `[deferred]` rows. Each must carry a **materialized handle** — a link or id to a durable tracked artifact (`tracked in TEAM-456`, `tracked in .docs/…`, `tracked in ndr:…`). For any `[deferred]` row missing one, halt and offer:

- **Spawn a follow-up (default):** invoke `Skill(spec-flow:capture)` to file a zero-ceremony Backlog ticket (linear host) or `status: captured` stub (file host) carrying the row's fork + why-not-now, then **backfill** the returned handle into the row.
- **Link an existing artifact:** the user names the ticket/note that already tracks it; backfill that handle.
- **Reclassify:** the row wasn't really a deliberate punt — downgrade it (`[open]` → flagged as a shipped hole, or `[resolved]` if it was actually decided). Only with the user's explicit call.

Do not archive until every `[deferred]` row carries a handle. The three row states map one-to-one to three close fates: `[open]` flags, `[resolved]` harvests (step 4), `[deferred]` spawns — this gate owns the spawn.

### 2c. Breakdown-parent gate (nested contracts)

Detect whether this contract is a **breakdown parent** — its companion's Decision log or the contract doc's body carries child-slice pointers (child `TEAM-N` relations on the linear host, or referenced child files). If it is:

- **The parent closes last.** Every child slice must already be closed — child files in `.docs/archive/`, or child tickets in a review-or-later state. If any child is still open, halt and list them: the parent cannot close over open slices.
- **Parent-close harvests the parent's own log.** Run the normal migration (steps 3–6) against the parent's front-matter + its **integration / whole-change** Decision-log rows — the cross-slice calls that never belonged to any single slice.
- **Flag literal duplication.** If a decision appears verbatim in both the parent log and a (now-archived) slice log, surface it — a row belongs to exactly one log. This is a duplication flag, not a misplacement audit; correct placement was author judgment at implement time.
- **Drain un-graduated fog.** Read `## Not yet specified` in the parent's **companion**. Every remaining patch is fog the effort never sharpened, and it cannot evaporate with the companion for the same reason a `[deferred]` row can't (gate 2b) — it was written down because it was expected to matter. Present each patch and take the user's disposition, one at a time:
  - **Out of scope** — the destination settled somewhere that leaves this past the boundary. Append one line to the parent **contract doc's** `Out of scope` fence and clear the patch from the companion. This is a contract-doc write, so it rides this close's sign-off (step 5) rather than going in silently; batch it with any `reconcile` edits into one host write. It does **not** enter the migration candidate set: a scope boundary is not a decision the effort made.
  - **Still real** — dispatch `Skill(spec-flow:capture)` to file it as a Backlog ticket, then replace the patch with the returned handle. Capture is built to accept exactly this vagueness; do not make the user sharpen a fog patch into a well-formed ticket just to close.
  - **Was never real** — drop it. Allowed, but make the user say so explicitly rather than defaulting to it, and don't offer it first.

  Do not archive a parent whose `Not yet specified` still holds an undisposed patch. If the section is absent or empty, this bullet is a no-op — that is the normal case for a parent whose fog fully graduated.

A non-parent (single) contract skips this gate. Fog lives only on parents, so a single contract has no `Not yet specified` to drain.

### 3. Post team-facing outcome summary (Linear host only)

Before migrating to the personal durable layer, post a compact outcome summary to the Linear ticket as a comment. This lands in a place both collaborators can see.

**Linear host:** Post via `mcp__linear-server__save_comment`:

```markdown
**Contract closed by @<closer>** — <one-line summary of what shipped> (YYYY-MM-DD)

**What changed:**
- <key outcome or decision, 1–3 bullets max>

**Decisions captured:** <ndr atom slugs, or "none">
**README updated:** <yes/no + which section, or "no">
**Verification:** <"pass" / "fail — gap noted" / "skipped", one word>
```

Keep this compact — it's a team signal, not a prose retrospective. Use `me` if the Linear MCP doesn't expose the current user's display name, otherwise use their @-handle.

**Reviewer routing (optional):** If the user wants a cross-review pass before the ticket moves to a review state, ask: *"Want to route this for review? @-mention who should review."* If yes, @-mention the reviewer in this same comment (or a follow-up comment) and transition to a review state. If no, transition to a review state as normal — self-review is the default. Do not force the reviewer prompt; it's opt-in.

If the contract-verifier ran in this session and the verifier identity is available (e.g. the agent name), note it in the comment (`Verified by: contract-verifier agent`). This keeps attribution visible in the ticket without requiring a separate step.

**File host:** skip this step — no shared visibility surface for file-host contracts.

**If Linear isn't connected** when closing a Linear-host contract (MCP unavailable): note in the conversation that the team-facing summary couldn't be posted, and continue with the rest of close normally.

### 4. Propose migrations

Surface a structured proposal:

**ndr atoms to capture:**

- The **companion's `[resolved]` Decision-log rows are the candidate set** — this is where the change's real forks were logged during implement, and deleting the companion at step 6 is the only thing that makes this harvest load-bearing rather than optional. Each row already carries the atom's live-only fields (`fork → call · because · alt · revisit-if`); drafting an atom is **copy-plus-fill**: copy those, fill the derivable remainder (Scope, Commitments; `/capture-decision` mints the id). Include any rows spawned by a `reconcile` in the done-when gate.
- **Pre-v2.1 fallback (no Decision log).** A contract drafted before the worksheet shape has no Decision log — its architectural decisions live in *Approach*. If the contract has no `## Decision log` section, harvest the candidate set the old way: for each real choice in *Approach* (library, pattern, structural decision), draft an atom. Do not let *Approach* evaporate un-harvested here — that path only applies to the ephemeral *Approach / wiring* of a v2.1 contract, whose calls were already logged as rows.
- **Do not pre-filter with a worksheet gate.** Hand the full `[resolved]` set to `/capture-decision` and let it apply the **canonical ndr worthiness rubric** — the contract's job is to surface candidates, not to adjudicate NDR-grade.
- A `[resolved]` row that *reverses* an earlier one (carries `_supersedes:_ ^rN`) drafts as a **superseding** atom — resolve the predecessor's head and set `supersedes:` per the ndr plugin's conventions.
- **`Approach / wiring` evaporates** — it is ephemeral integration mechanics, not a decision, and it leaves with the deleted companion. Anything durable or user-facing in it reaches README via the README-update proposal below, not an atom. This is the last chance to notice something in it worth keeping.

**README updates:**

- For each user-facing change (new commands, new behavior, new config, new dependencies), draft the README edit.
- Use librarian for vault-resident README work; otherwise edit the repo README directly.

**Vault / personal durable layer (optional, graceful fallback):**

- If the ndr plugin is installed and relevant atoms emerge, invoke `/capture-decision` as usual.
- If the librarian plugin is installed and a vault note is the right home for a finding, invoke it.
- Both are optional — the team-facing outcome summary (step 3) already landed in Linear. Skip vault migrations if the user wants, or if the plugins aren't available; do not hard-depend on them.

**Not migrated:**

- *Out of scope* items (by definition not part of this change).
- Decision-log `[resolved]` rows that `/capture-decision` judged below NDR-grade (the rubric's call, not the worksheet's).
- `[deferred]` rows — already materialized as their own tracked artifact by the deferral gate (step 2b); they don't also migrate here.
- *Approach / wiring* — ephemeral by design; leaves with the deleted companion.
- Conversation history (lives in the companion until it is deleted).

Present as a diff-style list:

```
Linear comment (1):
  - Outcome summary posted to TEAM-123

ndr atoms (2):
  - dishka-di-pattern.md (new)
  - auth-token-adapter.md (new)

README (1):
  - Add `/auth-status` to the commands table (line 42).
```

### 5. Sign-off + apply

Ask: "Apply these migrations?"

If approved, execute each:

- Invoke `/capture-decision` per proposed ndr atom (if any and if ndr plugin is available).
- Apply README edits.
- Commit the repo-facing changes this close touched (README edits and any other tracked files) in the repo's house style via `Skill(commit:commit)`. ndr atoms written by `/capture-decision` may already be committed by that skill — don't double-commit them; let `commit` pick up only what's still uncommitted. If the `commit` plugin isn't installed, commit directly following repo conventions.
- If any migration fails, halt and report; do not proceed to archive.

If the user wants to skip or modify any item, accommodate that.

### 6. Archive the contract doc, delete the companion

**Both hosts — delete the companion.** This runs **after** step 5's migrations have applied, never before: the deletion is the drain's completion signal, and gates 2b (deferrals) and 2c (fog) plus step 4's harvest must all have landed first.

```bash
trash .docs/<date>-<slug>-companion.md
```

Use `trash`, not `rm` — recovery stays available. If the companion is tracked, the deletion is a real commit: under jj (`.jj/` present) it auto-tracks; on pure git use `git rm`. Either way commit it via `Skill(commit:commit)`, folding it into the close commit from step 5 when that hasn't run yet. Git history retains the file's content — deletion removes it from the working set, not from the record, which is what makes "throwaway" honest rather than lossy.

If step 2 found no companion (pre-v2.3 contract), skip this — there is nothing to delete.

**File host — archive the contract doc:**

Move the contract file:

```bash
mkdir -p .docs/archive
mv .docs/<filename>.md .docs/archive/<filename>.md
```

`.docs/` is gitignored by the scratch-artifact convention, so a plain `mv` is usually all that's needed. If the file *is* tracked: under jj (`.jj/` present) the move auto-tracks — still plain `mv`; on a pure-git repo use `git mv`. When the move is tracked, commit it via `Skill(commit:commit)` rather than leaving it as a loose working-copy change — fold it into the close commit from step 5 if that hasn't run yet, otherwise commit the move on its own.

Update the file's frontmatter: flip `status: active` to `status: archived`. Placement in `.docs/archive/` is the canonical signal; the field is informational.

**Linear host:**

First, post the verification record as a ticket comment via `mcp__linear-server__save_comment`, so the review state carries evidence. Use the per-bullet result from the done-when gate (step 2.5):

```markdown
**Done-when verification** (contract-verifier agent, YYYY-MM-DD)

- ✅ met — "<bullet>" (<one-line evidence>)
- ❌ not_met — "<bullet>" (<what was observed instead>)
- ⚠️ drifted — "<bullet>" (<rephrase note>)

Verdict: pass | fail (closed as known gap per user)
```

One comment, compact. If the verification was run inline rather than by the contract-verifier agent, note that too (`verified inline, not by contract-verifier agent`). If the gate was skipped (no *Done when* section, user overrode), say that in the comment instead — the absence of verification is itself worth recording.

Then move the ticket to its review state — the change is done from your side and headed for PR. Do **not** edit the body; the contract stays in the description for retrospective. Only the state advances.

- Fetch the team's workflow states via `mcp__linear-server__list_issue_statuses` (the team comes from the issue read in step 2).
- Find a review state by name (case-insensitive), trying in order: "In Review", "Code Review", "Ready for Review", "Review".
- Set it via `mcp__linear-server__save_issue`.
- If none match, skip with a note — *"No review state on this team; leaving status unchanged."* Never fall through to a completed state: merge hasn't happened, so spec-flow does not set Done/Closed. That transition stays the human's at merge time.

Then strip the `contracted` label — the contract is migrating to the durable layer, so "ready for `/spec-flow implement`" is now stale. `save_issue`'s `labels` field replaces the full label set (there is no remove-labels parameter), so set the issue's current labels **minus** `contracted`: take the labels from the step-2 `get_issue` read, drop any matching `contracted` case-insensitively, and pass the remaining list to `mcp__linear-server__save_issue` (`labels` field). An empty array is honored — if `contracted` was the only label, passing `labels: []` clears it. This is a label removal only — it does not touch state. If the issue didn't carry `contracted`, this is a no-op.

### 7. Verify a clean working tree

Before confirming, check that nothing this change produced is left uncommitted — closing should leave the repo in a clean state. Detect the VCS (per step 2) and check: `git status` shows no tracked changes, or the jj working copy is empty (`jj st`).

- **Leftovers belong to this change** (stray README edit, the archived contract move, a forgotten code tweak) — commit them via `Skill(commit:commit)` so the tree ends clean.
- **Leftovers are unrelated** to the contract — do not sweep them into a close commit. Surface them to the user and let them decide; note in the confirm summary that the tree wasn't left fully clean.
- If the `commit` plugin isn't installed, commit the in-scope leftovers directly in the repo's house style.

### 8. Confirm

Brief summary to the user, wording differs by host:

- **File host:** *"Closed `<slug>`. 2 ndr atoms created, 1 README update applied. Contract archived at `.docs/archive/<filename>.md`; companion deleted."*
- **Linear host:** *"Closed TEAM-123. Outcome summary + verification record posted as comments; 2 ndr atoms created, 1 README update applied. Moved to In Review; `contracted` label removed; ticket body left intact; companion deleted. Set it Done yourself when the PR merges."*

### 8a. Offer to graduate parent fog (breakdown slices only)

When the contract just closed is a **child slice** of a breakdown parent, read `## Not yet specified` in the parent's companion. Ask whether resolving this slice sharpened any patch — a patch graduates when its question can now be *stated*, which is not the same as answered.

If one has, don't spawn the slice here. Say what sharpened and route:

> "Closing this looks like it sharpened *<patch>* on <parent>. Run `/pm:breakdown <parent>` to graduate it into slices?"

`pm:breakdown` owns creating slices and clearing the graduated patch; close only notices. Skip silently when the parent has no fog section, nothing sharpened, or this isn't a breakdown slice.

### 9. Recommend what's next (optional)

After confirming, offer a lightweight pointer to the next ticket — answering "what now?" without making the user switch tools. Opt-in; ask once:

> "Want a suggestion for what to pick up next?"

If yes and the Linear MCP is connected:

- `mcp__linear-server__list_issues` over the team's active cycle plus Backlog (team per the `linear` plugin's conventions).
- Filter to **actionable** candidates: not blocked (no open `blocked-by` relations), assigned to the current user or unassigned, not already in a started/completed state.
- Surface the top 1–3 by priority, and recommend one. Offer to route straight in: *"Pick up TEAM-128 next? I can `/spec-flow TEAM-128` to continue it."*

Keep it shallow. This is a nudge, not a grooming pass — **defer real prioritization to `Skill(pm:groom)`** and say so if the user wants a fuller sweep: *"For a proper cycle groom, run `/pm:groom`."* If Linear isn't connected, or the `pm`/`linear` surfaces aren't available, skip this step silently — never block close on it.

## Notes

- Migrations are *AI-assisted/auto* — AI proposes the diff, applies after user sign-off. No silent migration; no fully manual migration.
- Closing is non-destructive in both hosts. File host: the contract file is archived, not deleted. Linear host: the ticket body is untouched and the contract remains in its description for retrospective; only the state advances to a review state.
- spec-flow advances Linear state through the contract lifecycle (`implement` → In Progress, `close` → a review state) but never sets a completed state (Done/Closed). Merge happens outside the lifecycle, so that final flip stays the user's call. `draft` does not transition state — it applies the `contracted` label; `close` removes that label as the contract migrates to the durable layer.
- If the contract had frequent amendments, surface that observation — it can signal the original drafting was thin and worth thinking about for next time.

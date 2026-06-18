---
name: close
description: This skill should be used when the user runs `/spec-flow close [name]` or otherwise signals that an active contract's work is done and ready to migrate. Trigger phrases include "spec-flow close", "this change is done", "archive the X contract", "wrap up the X change", "close out the okta-auth work". Accepts either a file slug or a Linear ticket ID. Reviews the change against the contract, proposes migrations to the durable layer — ndr atoms via `/capture-decision`, README updates via librarian — applies them after user sign-off. For file-host contracts, moves the file to `.docs/archive/`. For Linear-host contracts, advances the ticket to a review state but never sets a completed state — Done stays the user's call at merge.
---

# spec-flow:close

Close an active contract. Migrate durable findings to ndr atoms and README; archive the file or hand the ticket back to the human, depending on host. See `../../references/hosts.md` for the dual-host model.

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

Same logic as `spec-flow:implement` step 1: explicit name, or enumerate active contracts across both hosts (`.docs/` scan plus, when the Linear MCP is connected, tickets in Contract Review / In Progress with a six-section description), then prompt match or ask. Host detection:

- Identifier matches `^[A-Z]{2,5}-\d+$` → **linear** host.
- Anything else → **file** host.

If host = linear, check that `mcp__linear-server__*` tools are loaded. If not:

> "Linear MCP server isn't connected — I can't read TEAM-123's description. Pause while you wire up the MCP, or close the migration steps using context held in conversation only?"

Do not run `claude mcp add` or suggest a paste-and-go connect command.

### 2. Read the contract and the actual change

- **File host** — `Read` the contract file.
- **Linear host** — Fetch description via `mcp__linear-server__get_issue`.
- **Detect the VCS first** — if `.jj/` exists at the repo root, use `jj log` / `jj diff`; otherwise `git log` / `git diff`. Survey what actually shipped since the contract was created.
- Compare: what was in *Approach* vs. what's in the code now.

### 2.5. Done-when check (first gate)

Walk each *Done when* bullet against the actual change:

- **Met** — outcome is observable in the diff / repo state.
- **Not met** — outcome is missing or partial. Surface explicitly.
- **Drifted** — outcome shipped, but the bullet no longer describes it well (rephrase candidate during close).

Prefer behavioral confirmation over diff-reading. If `implement`'s verify step ran this session, reuse its per-bullet result; otherwise dispatch the **`contract-verifier`** agent (Done-when bullets + diff scope + detected VCS) to run the checks now in isolated context — or fall back to running them inline (`/verify` if available). A bullet that only *looks* met in the diff is exactly the drift this gate exists to catch.

If any bullet is **not met**, halt and ask: continue closing anyway (treat as a known gap, note it in the summary), amend the contract via `spec-flow:amend` to reflect a narrower done, or pause closing until the gap ships? Do not silently archive an unmet contract.

If the contract has no *Done when* section (older format), surface that and either ask the user to draft one inline before review, or fall back to comparing against *Approach*. Note the absence in the close summary so future contracts don't repeat the gap.

### 2a. Offer a drift check (optional)

If the `ndr` plugin is installed and has atoms scoped to this project/repo, prompt once:

> "Want to run a drift check against ndr atoms before archiving? (`Skill(ndr:drift-check)` scoped to the change since the contract was created — a jj revset or git range, per the VCS detected in step 2.)"

If yes, dispatch the skill and weave its findings into the migration proposal in step 3 — e.g. an atom flagged with `recommendation: amend` becomes a candidate successor in the *ndr atoms to capture* list. Do not auto-invoke; this is opt-in per close.

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

- For each architectural decision (anything in *Approach* that constitutes a real choice — library, pattern, structural decision), draft an ndr atom for `/capture-decision`.
- Follow existing supersession-aware conventions from the ndr plugin.

**README updates:**

- For each user-facing change (new commands, new behavior, new config, new dependencies), draft the README edit.
- Use librarian for vault-resident README work; otherwise edit the repo README directly.

**Vault / personal durable layer (optional, graceful fallback):**

- If the ndr plugin is installed and relevant atoms emerge, invoke `/capture-decision` as usual.
- If the librarian plugin is installed and a vault note is the right home for a finding, invoke it.
- Both are optional — the team-facing outcome summary (step 3) already landed in Linear. Skip vault migrations if the user wants, or if the plugins aren't available; do not hard-depend on them.

**Not migrated:**

- *Out of scope* items (by definition not part of this change).
- *Open questions* that were resolved but produced no durable artifact.
- Conversation history (lives in the contract file until archive).

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
- If any migration fails, halt and report; do not proceed to archive.

If the user wants to skip or modify any item, accommodate that.

### 6. Archive the contract (host-aware)

**File host:**

Move the contract file:

```bash
mkdir -p .docs/archive
mv .docs/<filename>.md .docs/archive/<filename>.md
```

`.docs/` is gitignored by the scratch-artifact convention, so a plain `mv` is usually all that's needed. If the file *is* tracked: under jj (`.jj/` present) the move auto-tracks — still plain `mv`; on a pure-git repo use `git mv`.

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

### 7. Confirm

Brief summary to the user, wording differs by host:

- **File host:** *"Closed `<slug>`. 2 ndr atoms created, 1 README update applied. Contract archived at `.docs/archive/<filename>.md`."*
- **Linear host:** *"Closed TEAM-123. Outcome summary + verification record posted as comments; 2 ndr atoms created, 1 README update applied. Moved to In Review; ticket body left intact. Set it Done yourself when the PR merges."*

## Notes

- Migrations are *AI-assisted/auto* — AI proposes the diff, applies after user sign-off. No silent migration; no fully manual migration.
- Closing is non-destructive in both hosts. File host: the contract file is archived, not deleted. Linear host: the ticket body is untouched and the contract remains in its description for retrospective; only the state advances to a review state.
- spec-flow advances Linear state through the contract lifecycle (`draft` → Contract Review, `implement` → In Progress, `close` → a review state) but never sets a completed state (Done/Closed). Merge happens outside the lifecycle, so that final flip stays the user's call.
- If the contract had frequent amendments, surface that observation — it can signal the original drafting was thin and worth thinking about for next time.

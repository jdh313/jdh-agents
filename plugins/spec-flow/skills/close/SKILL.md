---
name: close
description: This skill should be used when the user runs `/spec-flow close [name]` or otherwise signals that an active contract's work is done and ready to migrate. Trigger phrases include "spec-flow close", "this change is done", "archive the X contract", "wrap up the X change", "close out the okta-auth work". Accepts either a file slug or a Linear ticket ID. Reviews the change against the contract, proposes migrations to the durable layer — ndr atoms via `/capture-decision`, README updates via librarian — applies them after user sign-off. For file-host contracts, moves the file to `.docs/archive/`. For Linear-host contracts, advances the ticket to a review state but never sets a completed state — Done stays the user's call at merge.
---

# spec-flow:close

Close an active contract. Migrate durable findings to ndr atoms and README; archive the file or hand the ticket back to the human, depending on host. See `references/hosts.md` for the dual-host model.

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

Same logic as `spec-flow:implement` step 1: explicit name, single active file contract, prompt match, or ask. Host detection:

- Identifier matches `^[A-Z]{2,5}-\d+$` → **linear** host.
- Anything else → **file** host.

If host = linear, check that `mcp__linear-server__*` tools are loaded. If not:

> "Linear MCP server isn't connected — I can't read CAR-49's description. Pause while you wire up the MCP, or close the migration steps using context held in conversation only?"

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

If the repo has ndr atoms (i.e. `~/Loose Ends/Decisions/` is populated and at least one atom's `project:` or `area:` matches this repo), prompt once:

> "Want to run a drift check against ndr atoms before archiving? (`Skill(ndr:drift-check)` with scope `<base>...HEAD`.)"

If yes, dispatch the skill and weave its findings into the migration proposal in step 3 — e.g. an atom flagged with `recommendation: amend` becomes a candidate successor in the *ndr atoms to capture* list. Do not auto-invoke; this is opt-in per close.

### 3. Propose migrations

Surface a structured proposal:

**ndr atoms to capture:**

- For each architectural decision (anything in *Approach* that constitutes a real choice — library, pattern, structural decision), draft an ndr atom for `/capture-decision`.
- Follow existing supersession-aware conventions from the ndr plugin.

**README updates:**

- For each user-facing change (new commands, new behavior, new config, new dependencies), draft the README edit.
- Use librarian for vault-resident README work; otherwise edit the repo README directly.

**Not migrated:**

- *Out of scope* items (by definition not part of this change).
- *Open questions* that were resolved but produced no durable artifact.
- Conversation history (lives in the contract file until archive).

Present as a diff-style list:

```
ndr atoms (2):
  - dishka-di-pattern.md (new)
  - auth-token-adapter.md (new)

README (1):
  - Add `/auth-status` to the commands table (line 42).
```

### 4. Sign-off + apply

Ask: "Apply these migrations?"

If approved, execute each:

- Invoke `/capture-decision` per proposed ndr atom.
- Apply README edits.
- If any migration fails, halt and report; do not proceed to archive.

If the user wants to skip or modify any item, accommodate that.

### 5. Archive the contract (host-aware)

**File host:**

Move the contract file:

```bash
mkdir -p .docs/archive
mv .docs/<filename>.md .docs/archive/<filename>.md
```

`.docs/` is gitignored by the scratch-artifact convention, so a plain `mv` is usually all that's needed. If the file *is* tracked: under jj (`.jj/` present) the move auto-tracks — still plain `mv`; on a pure-git repo use `git mv`.

Update the file's frontmatter: flip `status: active` to `status: archived`. Placement in `.docs/archive/` is the canonical signal; the field is informational.

**Linear host:**

Move the ticket to its review state — the change is done from your side and headed for PR. Do **not** edit the body; the contract stays in the description for retrospective. Only the state advances.

- Fetch the team's workflow states via `mcp__linear-server__list_issue_statuses` (the team comes from the issue read in step 2).
- Find a review state by name (case-insensitive), trying in order: "In Review", "Code Review", "Ready for Review", "Review".
- Set it via `mcp__linear-server__save_issue`.
- If none match, skip with a note — *"No review state on this team; leaving status unchanged."* Never fall through to a completed state: merge hasn't happened, so spec-flow does not set Done/Closed. That transition stays the human's at merge time.

### 6. Confirm

Brief summary to the user, wording differs by host:

- **File host:** *"Closed `<slug>`. 2 ndr atoms created, 1 README update applied. Contract archived at `.docs/archive/<filename>.md`."*
- **Linear host:** *"Closed CAR-49. 2 ndr atoms created, 1 README update applied. Moved to In Review; ticket body left intact. Set it Done yourself when the PR merges."*

## Notes

- Migrations are *AI-assisted/auto* — AI proposes the diff, applies after user sign-off. No silent migration; no fully manual migration.
- Closing is non-destructive in both hosts. File host: the contract file is archived, not deleted. Linear host: the ticket body is untouched and the contract remains in its description for retrospective; only the state advances to a review state.
- spec-flow advances Linear state through the contract lifecycle (`start` → Contract Review, `implement` → In Progress, `close` → a review state) but never sets a completed state (Done/Closed). Merge happens outside the lifecycle, so that final flip stays the user's call.
- If the contract had frequent amendments, surface that observation — it can signal the original drafting was thin and worth thinking about for next time.

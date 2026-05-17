---
name: close
description: This skill should be used when the user runs `/spec-flow close [name]` or otherwise signals that an active contract's work is done and ready to migrate. Trigger phrases include "spec-flow close", "this change is done", "archive the X contract", "wrap up the X change", "close out the okta-auth work". Reviews the change against the contract, proposes migrations to the durable layer — ndr atoms via `/capture-decision`, README updates via librarian — applies them after user sign-off, then moves the contract file to `.docs/archive/`.
---

# spec-flow:close

Close an active contract. Migrate durable findings to ndr atoms and README; archive the contract file.

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

### 1. Identify the target contract

Same logic as `spec-flow:implement` step 1: explicit name, single active, prompt match, or ask.

### 2. Read the contract and the actual change

- Read the contract file.
- Run `git log` / `git diff` since the contract was created to see what actually shipped.
- Compare: what was in *Approach* vs. what's in the code now.

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

### 5. Archive the contract

Move the contract file:

```bash
mkdir -p .docs/archive
mv .docs/<filename>.md .docs/archive/<filename>.md
```

(Use `git mv` if the file is tracked.)

Update the file's frontmatter: flip `status: active` to `status: archived`. Placement in `.docs/archive/` is the canonical signal; the field is informational.

### 6. Confirm

Brief summary to the user:

> "Closed `<slug>`. 2 ndr atoms created, 1 README update applied. Contract archived at `.docs/archive/<filename>.md`."

## Notes

- Migrations are *AI-assisted/auto* — AI proposes the diff, applies after user sign-off. No silent migration; no fully manual migration.
- Closing is non-destructive — the contract file is archived, not deleted, so it remains available for reference and for retrospective.
- If the contract had frequent amendments, surface that observation — it can signal the original drafting was thin and worth thinking about for next time.

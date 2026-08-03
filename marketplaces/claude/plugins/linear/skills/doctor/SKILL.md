---
name: doctor
description: >-
  Read-only setup validator for the linear plugin. Diagnoses the workspace and
  reports a pass/warn/fail checklist with specific fixes. Trigger phrases
  include "check my linear setup", "is linear configured right", "linear
  doctor", "validate linear workspace", "diagnose linear", "is linear working",
  "linear health check", "check linear configuration".
allowed-tools:
  - mcp__linear-server__list_teams
  - mcp__linear-server__get_team
  - mcp__linear-server__list_issue_labels
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__list_users
  - mcp__linear-server__list_cycles
---

# linear:doctor

Read-only setup validator. Diagnoses what the linear plugin expects and reports a checklist. **Never mutates anything.**

## Runtime adapter

Use the active runtime's connected Linear integration. The
`mcp__linear-server__*` names below are Claude Code spellings; in Codex, match
each operation to the connected Linear app or MCP tool exposed in the current
task. Do not use web search or model memory as a fallback for workspace data.

## Checks

Run all checks, then emit a single report. Each check is independent — a failure in one does not abort the rest.

### 1. MCP reachable

Call `mcp__linear-server__list_teams({})`. If it errors or times out → **FAIL: Linear MCP not connected. Check that the linear-server MCP is running and authenticated.**

If it succeeds → **PASS**.

### 2. Team resolves

`TEAM` in this plugin is a placeholder, not a required team name. Resolve the
team from the `list_teams` response:

- **PASS** — exactly one team found; select it and note its name, key, and ID for subsequent calls.
- **PASS** — multiple teams found and applicable repository guidance or the current ticket context identifies one unambiguously; select it and note why.
- **WARN** — multiple teams found with no unambiguous signal. List them and ask which team to validate; do not guess.
- **FAIL** — no teams returned. The integration is reachable but exposes no team to validate.

### 3. Labels present

Call `mcp__linear-server__list_issue_labels({teamId: "<team-id>"})` (use the ID from check 2). Filter client-side.

Expected surface labels (bare child names, part of the `surface` group): `backend`, `frontend`, `infra`, `database`, `pipeline`

Expected type labels: `Feature`, `Improvement`, `Docs`, `Chore`, `Decision`, `Spike`

For each expected label, check if it appears in the response (match on `name`, case-sensitive for types, lowercase for surface).

- **PASS** — all 11 labels present.
- **WARN** — one or more missing. List the missing labels with: "Create these labels in Linear → Settings → Labels."

### 4. Workflow states present

Call `mcp__linear-server__list_issue_statuses({teamId: "<team-id>"})`.

Expected states: `Backlog`, `Todo`, `In Progress`, `In Review`, `Done`, `Canceled`

Check for each by `name` (case-sensitive match).

- **PASS** — all 6 states found.
- **WARN** — one or more missing. List which states are absent and advise: "Add them in Linear → Settings → Workflow."
- Note: extra states beyond this set are fine — they are not flagged.

### 5. Team size (team-oriented check)

From `mcp__linear-server__list_users({teamId: "<team-id>"})`, count members with an `active` status (or equivalent non-deactivated field).

- **PASS** — 2 or more active members.
- **WARN** — fewer than 2 active members. Message: "Assignee routing conventions assume ≥2 active team members. If collaborating, add the other person to the team in Linear."

Also verify that querying by name would work: check that each active member has a non-empty `name` field. If any member has a blank name, **WARN**: "Member(s) with empty names may not resolve correctly when assigning by name."

### 6. Cycles configured (soft warning only)

Call `mcp__linear-server__list_cycles({teamId: "<team-id>", type: "current"})`.

- **PASS** — at least one cycle returned.
- **WARN** (soft — not a failure) — no cycles found. Message: "No active cycle detected. Cycles are optional for the linear plugin itself, but are required by the pm plugin's groom and retro skills. Configure weekly cycles in Linear → Settings → Cycles if you use those."

## Output format

```
## linear:doctor

**MCP reachable**     ✓ PASS
**Team (<resolved>)** ✓ PASS  (name + key)
**Labels**            ✓ PASS  (or ⚠ WARN — missing: Feature, Spike)
**Workflow states**   ✓ PASS  (or ⚠ WARN — missing: In Review)
**Team size**         ✓ PASS  (or ⚠ WARN — 1 active member; add collaborator)
**Cycles**            ⚠ WARN — no active cycle (needed by pm:groom/retro, not by linear itself)

### Fixes needed

- Create label "Spike" in Linear → Settings → Labels (Type group)
- Add collaborator to team in Linear → Settings → Members
```

Emit only the checks that have findings in the "Fixes needed" section. If everything passes, write "No fixes needed — workspace is configured correctly."

FAIL stops the checklist narrative but is still included in the output. A single FAIL does not prevent the remaining checks from running.

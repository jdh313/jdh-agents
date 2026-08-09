# Linear and Fibery projections

Thin, optional, one-way. Local run state is canonical; neither tracker stores
nor defines workflow authority.

## What is supported

**Existing issues only.** This pilot does not create issues and does not manage
a backlog. If there is no issue, the change runs local-only — that is the normal
case, not a degraded one.

When Jacob supplies a Linear key (`TEAM-123`), a Fibery task reference, or an
unambiguous issue URL:

1. Read the issue title, description, and relevant existing context.
2. Record host, stable issue identity, and URL in local state:

   ```bash
   python3 "$HELPER" issue-set --host linear --identity TEAM-123 \
     --url https://linear.app/... --status never-projected
   ```
3. Use the issue as **Frame input** — what prompted the work, prior context,
   constraints already written down.
4. Keep local authority and lifecycle state canonical from that point on.

## Permitted projections

Each of these requires the matching token in the active grant's
`delivery_authorized`, and each is a deliberate write, never a sync:

| Action | Token | When |
|---|---|---|
| Mark in progress | `tracker-in-progress` | after autonomy is granted |
| Post an exception summary | `tracker-exception` | when an exception occurs |
| Post the final outcome plus a compact verification summary | `tracker-outcome` | at Close |
| Move to review or completion | `tracker-transition` | only when that exact transition is in delivery authority *and* the actual outcome supports it |

After a successful projection:

```bash
python3 "$HELPER" issue-set --host linear --identity TEAM-123 --status current
```

## Never

- Store the canonical grant in the issue body.
- Overwrite the issue description with workflow state.
- Mirror every phase, or post periodic progress.
- Infer authority from tracker status.
- Resume solely from tracker content.
- Claim tracker parity silently.

A tracker is a projection surface. It cannot grant authority, and a status
there is not evidence about this change.

## Failure handling

If the tracker is unavailable, ask one bounded question: continue local-only, or
pause? Do not guess.

If a projection fails after being attempted, mark it stale and carry on — local
authority is untouched and must not be corrupted by the failure:

```bash
python3 "$HELPER" issue-set --host linear --identity TEAM-123 --status stale \
  --stale-reason "outcome comment failed: MCP server unreachable"
```

A stale projection is reported as stale. Never describe local and tracker state
as synchronized when the last write did not land.

## Linear

Reuse the `linear` plugin's conventions and its semantic MCP operations — team,
status vocabulary, label rules, and comment shape live there. Do not duplicate
them here and do not invent a second set. This workflow supplies only *what* to
post and *when*; the `linear` plugin supplies *how*.

## Fibery

Discover the connected schema and operations at runtime
(`mcp__fibery__schema`, `mcp__fibery__schema_detailed`,
`mcp__fibery__describe_*`). Do **not** hardcode entity types or field IDs — the
identifiers appearing in the AgentForge baseline transcript are one workspace's
shape, not a contract.

Unverified in this implementation: no Fibery operation has been exercised
against a live workspace as part of this pilot. Whether the connected workspace
exposes a state field matching `tracker-transition`, and what its vocabulary is,
must be discovered at runtime and may be unavailable. Report it as unavailable
rather than approximating it.

## Testing

Automated tests use fakes and fixtures. No test mutates a real Linear or Fibery
issue. The projection surface is exercised through `issue-set` and the local
state it produces, not through the tracker APIs.

# Tracker projections

Thin, optional, one-way. Local run state is canonical; no tracker stores or
defines workflow authority.

## Three layers, no overlap

| Layer | Owns | Lives in |
|---|---|---|
| **When** | which phases project, and at what moment | SKILL.md |
| **What this project chose** | hosts, state names, terminal owner | `config.json` |
| **How to say it here** | identity format, resolution, limits | `references/hosts/<host>.md` |
| **Whether** | permission to write at all | the active grant |

A host reference that says *when* to project has become a second copy of the
workflow. A host reference that says a projection is permitted has become a
second authority surface. Neither belongs there.

## What is supported

**Existing issues only.** This pilot does not create issues and does not manage
a backlog. If there is no issue, the change runs local-only — that is the normal
case, not a degraded one.

When Jacob supplies an issue key, task reference, or unambiguous URL:

1. Read the issue title, description, and relevant existing context.
2. Record host, stable identity, and URL in local state:

   ```bash
   python3 "$HELPER" issue-set --host linear --identity TEAM-123 \
     --url https://linear.app/... --status never-projected
   ```
3. Use the issue as **Frame input** — what prompted the work, prior context,
   constraints already written down.
4. Keep local authority and lifecycle state canonical from that point on.

Read `references/hosts/<host>.md` for that tracker before the first projection.
Only the host in `issue.host` is read; the others are irrelevant to this change.

## Project configuration

```bash
python3 "$HELPER" config-show
python3 "$HELPER" config-set --host linear --host fibery \
  --terminal-owner merge-automation \
  --state "linear:implement=In Progress" --state "linear:verify=In Review"
```

- **`hosts`** — trackers this project uses, primary first. A project may list
  more than one; the per-change `issue.host` decides which this change touches.
- **`terminal_owner`** — `merge-automation` (default), `manual`, or `workflow`.
  The workflow writes a terminal state only under `workflow`, and no host
  reference currently describes doing so.
- **`states`** — this project's name for each projected phase, per host.
  Optional; discovered at runtime and cached here after the first resolution.
- **`on_failure`** — `continue` (default) or `pause`.
- **`ndr`** — `auto` (default), `on`, or `off`. Under `auto` a repository-local
  `.ndr.toml` arms the decision-capture item at Close. A home-level catch-all
  does not: it is a fallback destination, not a claim that this repository
  tracks decisions.

Config says where and how. It never says whether: a tracker write still needs
`tracker-transition` in the active grant, so a configured host with no granted
token writes nothing.

## Permitted projections

Each requires the matching token in the active grant's `delivery_authorized`,
and each is a deliberate write, never a sync:

| Action | Token | When |
|---|---|---|
| Move to the in-progress state | `tracker-transition` | when autonomy is granted, entering Implement |
| Move to the in-review state | `tracker-transition` | when the candidate is submitted, entering Verify |
| Post an exception summary | `tracker-exception` | when an exception occurs |
| Post the final outcome plus a compact verification summary | `tracker-outcome` | at Close |

`tracker-transition` covers reversible moves only. There is no token for a
terminal state, because writing one is not this workflow's to do — see below.

After a successful projection:

```bash
python3 "$HELPER" issue-set --host linear --identity TEAM-123 --status current
```

## The terminal state is not ours

Delivery here is commit or push. The tracker's terminal state usually follows a
merge, and where that automation exists it already owns the transition. Writing
it at Close would mark work complete while the branch is still open, and would
race the automation that is about to do it correctly.

So Close projects an outcome *comment*, not a state. A project whose tracker has
no such automation sets `terminal_owner` to `manual` and moves it by hand.

## Unmapped is a legitimate answer

A host may have no equivalent for a projected phase — plain GitHub Issues has no
in-review state at all. Leave the mapping empty, report the transition as
unmapped, and carry on. Never approximate a state with a label or a nearby
field: a misreported state is worse than an absent one.

## Never

- Store the canonical grant in the issue body.
- Overwrite the issue description with workflow state.
- Mirror every phase, or post periodic progress.
- Infer authority from tracker status.
- Resume solely from tracker content.
- Claim tracker parity silently.

A tracker is a projection surface. It cannot grant authority, and a status there
is not evidence about this change.

## Failure handling

If the tracker is unavailable before any write, ask one bounded question:
continue local-only, or pause? Do not guess. `on_failure` records the project's
usual answer; it does not remove the question when the situation is novel.

If a projection fails after being attempted, mark it stale and carry on — local
authority is untouched and must not be corrupted by the failure:

```bash
python3 "$HELPER" issue-set --host linear --identity TEAM-123 --status stale \
  --stale-reason "in-review transition failed: MCP server unreachable"
```

Never block work on a status write. A stale projection is reported as stale, and
local and tracker state are never described as synchronized when the last write
did not land.

## Testing

Automated tests use fakes and fixtures. No test mutates a real issue on any
tracker. The projection surface is exercised through `config-set`, `issue-set`,
and the local state they produce, not through tracker APIs.

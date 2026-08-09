# State model

Three record classes, one state root. They are separate because they have
different write semantics: a grant must not change, current state must, and a
verification result must be able to land while nobody is listening.

## Where it lives

```text
$AW_STATE_ROOT                                  # explicit override, used by tests
~/.claude/state/attention-workflow/<slug>-<sha1(repo_root)[:12]>/
```

Derived from the repository root, so the same repository resolves to the same
root from any subdirectory and from any session. Nothing is written into the
target repository's tracked working tree — rollback is deleting this directory.

```text
<state root>/
  current.json      mutable projection            atomic replace
  grants/g<N>.json  versioned authority           create-only, never rewritten
  runs/v<N>.json    verification runs             atomic replace, terminal-once
  history.jsonl     append-only transition log
```

## current.json

| Field | Meaning |
|---|---|
| `change_id`, `title` | change identity |
| `repository` | `{root, vcs}` |
| `issue` | optional `{host, identity, url, projection_status, last_projected_at, stale_reason}` |
| `phase` | `frame` \| `design` \| `prepare` \| `implement` \| `verify` \| `deliver` \| `close` |
| `owner` | `jacob` \| `execution` \| `verification` \| `delivery` \| `external` |
| `condition` | `active` \| `holding` \| `exception` |
| `active_grant`, `active_candidate`, `active_verification_run` | current identities |
| `last_transition` | `{from_phase, to_phase, reason, at}` |
| `next_transition` | the next expected consequential transition |
| `attention` | `null`, or the unresolved demand `{kind, summary}` |
| `safe_point` | where work can resume from |
| `closed`, `outcome` | `delivered` \| `stopped` \| `abandoned` |

Phase, owner, and condition are independent axes. Phase answers *where are we
in the work*; owner answers *who must act now*; condition answers *can the
current owner advance under valid authority*. Waiting while authority holds is
`holding` — it is not a phase and not an exception.

Attention demand is a **projection**, recorded on the transition that produced
it and in history. It is not a fourth authoritative axis.

## Fail-safe evaluation

`show` returns `status` of `no-state`, `ok`, or `fail-safe`. It reports
`fail-safe` — forcing phase `prepare`, owner `jacob`, condition `exception` —
when any of these hold:

- `current.json` exists but is not a readable JSON object;
- `phase`, `owner`, or `condition` is outside its vocabulary;
- phase is `implement`, `verify`, or `deliver` with no active grant;
- an active grant or verification run is referenced but its record is missing;
- the active grant has been superseded while phase is not `design`/`prepare`;
- the change is closed but records no outcome.

The recorded values are preserved alongside as `recorded_phase` /
`recorded_owner` / `recorded_condition`, and `problems` names exactly what is
missing. A resumer must not reconstruct authority from git state, issue status,
or chat history.

## grants/g<N>.json

Created only through `grant-create`, which opens with `O_CREAT|O_EXCL` and
refuses an existing path. Required keys are listed in the skill; `grant-create`
rejects a payload missing any of them, rejects a `delivery_authorized` action it
cannot classify, and rejects a `representative_probe` with neither a probe nor a
`waived_reason`.

Supersession is recorded **only on the successor**, in its `supersedes` field.
Stamping a `superseded_by` back-pointer into the old grant would be a rewrite of
an immutable record; `grant-show` derives it instead. A grant may be superseded
once — a second attempt is refused.

Creating a superseding grant marks every non-stale verification run
`stale: true` with a reason. Stale evidence stays inspectable and may not
authorize readiness, delivery, or closure.

## runs/v<N>.json

| Field | Meaning |
|---|---|
| `id` | durable identity, minted before the verifier is dispatched |
| `grant`, `candidate` | what this run is bound to |
| `state` | `requested` \| `running` \| `holding` \| `completed` \| `failed` \| `superseded` |
| `result` | the verifier's report object, including its withheld `verdict` |
| `stale`, `stale_reason` | set when a superseding grant invalidates the evidence |
| `operator_judgment` | `{judgment, decisive, recorded_at}` |
| `revealed_at` | when the verifier's conclusion was revealed |

`run-complete` is **terminal-once and idempotent**. The first terminal write
wins; a duplicate returns the stored record with `duplicate: true` and changes
nothing. `run-state` refuses to move a run out of a terminal state. This is what
makes verifier completion independent of message delivery: a delayed,
duplicated, or reordered notification lands on a record that already decided.

`run-evidence` strips `verdict`, `recommendation`, `overall`, and
`summary_verdict` from the result. `run-reveal` refuses until
`operator_judgment` exists, and `run-judge` refuses an empty `decisive` field.
The judgment-before-verdict ordering is enforced by the helper, not requested in
prose.

## Checkpoint postconditions

`checkpoint-verify` observes actual VCS state rather than accepting a claim.

- **git** — HEAD resolves and the working tree is clean.
- **jj** — the working-copy change `@` is empty. `jj describe` alone does not
  advance it, which is exactly how a delegate can report an isolated checkpoint
  that does not exist.

Exit status 0 means the postcondition holds; 1 means it does not, with the
observation in the payload.

## Helper commands

```text
state-root                 print the resolved state root
init                       open a change
show                       the projection, including fail-safe evaluation
context                    the compact SessionStart card
transition                 move phase / owner / condition, with a reason
grant-create               create a versioned grant (create-only)
grant-show | grant-list    inspect authority, with derived supersession
run-create                 mint a verification-run identity
run-state | run-complete   run lifecycle; terminal-once
run-evidence               the result with the verdict withheld
run-judge | run-reveal     record Jacob's judgment, then reveal the verifier's
run-list                   runs with staleness and judgment status
guard-check --action X     is a delivery action covered by the active grant
checkpoint-verify          observe a claimed VCS checkpoint
issue-set                  record or invalidate a tracker projection
history                    the append-only transition log
```

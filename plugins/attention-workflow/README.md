# attention-workflow

**Status: experimental. Claude-only. The behavioral pilot has not been run.**

An attention-regulating development lifecycle. It spends attention at
consequential decisions and transitions, releases it during safe autonomous
work, and recovers it with enough context to act when the grounds for autonomy
fail.

```text
Frame -> Design -> Prepare --authorize--> Implement -> Verify -> Deliver -> Close
```

Seven semantic states, one skill, no turn per phase. A five-minute change
compresses Frame through Prepare into one authorization and combines
reconciliation with Close; the phases still exist in state and history, because
the same evidence means different things at different points in the work.

The design package this implements lives in `.docs/attention-workflow/`
(gitignored). The governing needs note is
`Manual of Me/Interaction/Attention-Regulating Workflows.md`.

## What it actually does

- **Versioned authority.** A grant records the promise, exclusions, route,
  load-bearing assumptions with falsifiers, residual unlisted risk, baseline,
  representative outcome probe, planned observations, tolerances, enforcement
  classes, and authorized delivery actions. Grants are create-only. A material
  change creates a new grant that supersedes the old one and marks prior
  candidates and verification evidence stale for delivery and closure.
- **Outcome before proxy.** Design records the operator question separately
  from any proposed taxonomy, report shape, or schema, and runs one
  representative probe before authorization when the proxy could mask the
  answer. A test proving the proxy was implemented is not an answer.
- **Quiet implementation.** Routine tool use, red/green iteration, commits, and
  elapsed time produce no messages. On-demand status reports checkable facts,
  never an "on course" self-assessment.
- **Independent verification.** A separate agent receives the promise and the
  candidate scope but not the implementer's success claim, narrative, or
  deviation assessment, and derives the actual route from the repository
  itself. Its terminal result is written to the run record, so a delayed,
  duplicated, or reordered notification cannot lose it or trigger a duplicate
  run.
- **Judgment before verdict.** You see promise-versus-observation evidence with
  the verifier's verdict and recommendation stripped, commit your own judgment
  and the decisive observation, and only then see the verifier's. The helper
  refuses to reveal early — this ordering is structural, not a prompt.
- **Fail-safe resumption.** A SessionStart hook injects the state card on a
  fresh, resumed, or forked session. Incomplete or contradictory state forces
  Prepare / Exception with the missing element named; nothing reconstructs
  authority from git state, issue status, or chat history.

## Enabling it (and disabling spec-flow)

The two lifecycles compete for the same trigger phrases. Run one.

```bash
/plugin disable spec-flow@cc-marketplace
/plugin enable attention-workflow@cc-marketplace
/plugin                     # confirm exactly one lifecycle plugin is enabled
```

Drain or explicitly park active spec-flow contracts first. This plugin does not
disable spec-flow automatically — nothing verified says a plugin can toggle
another, and the manual toggle is the honest mechanism.

`attention-workflow` ships `defaultEnabled: false`, so installing or updating
the marketplace never switches the lifecycle out from under an in-flight
change.

### Rollback

```bash
/plugin disable attention-workflow@cc-marketplace
/plugin enable spec-flow@cc-marketplace
rm -rf "$(python3 <plugin>/scripts/aw_state.py state-root)"   # after preserving evidence
```

No contract migration, tracker conversion, or state conversion. Nothing was
written into the repository's tracked working tree.

## Where state lives

```text
$AW_STATE_ROOT                                           # override, used by tests
~/.claude/state/attention-workflow/<repo-slug>-<hash>/   # default
  current.json      mutable projection
  grants/g<N>.json  versioned authority, create-only
  runs/v<N>.json    verification runs, terminal-once
  history.jsonl     append-only transition log
```

Outside the target repository entirely. See `references/state-model.md`.

## What is actually enforced

| Class | Covers |
|---|---|
| **Hook-guarded** | Direct `Edit`/`Write`/`NotebookEdit`/`MultiEdit` on an existing grant; shell mutation or redirection at a grant path; `git push` and `jj git push` without matching delivery authority — including `git -C`, `git -c`, `jj -R`, and pushes buried in `&&` / `;` chains |
| **Check-gated** | Claimed VCS checkpoints observed from real `git`/`jj` state; verdict reveal blocked until a judgment is recorded; terminal-once run results; grant-creation validation |
| **Agent-monitored** | Semantic scope or route drift, named assumption falsification, API/data-model/security-boundary changes, delivery actions other than the two push forms, tracker projection boundaries |
| **Uncovered** | Unlisted assumptions, general semantic deviation detection, tamper resistance of the state root, `gh pr merge` / deploys / migrations / MCP surfaces, pushes via wrappers and aliases, cross-machine resumption |

Hook-guarded means guarded on those tool surfaces. It is not OS-level
immutability. `references/enforcement-map.md` lists the known bypasses rather
than hiding them.

## Linear and Fibery

Optional one-way projections onto **existing** issues. Local state stays
canonical; neither tracker stores or defines authority. Issue creation and
backlog management are out of scope for this pilot. Each projection requires
its own token in the grant's `delivery_authorized`. A failed projection is
marked stale and never described as synchronized. Fibery operations are
discovered at runtime and are unverified against a live workspace. See
`references/issue-projections.md`.

## Codex

Unsupported in Experiment 1, by decision rather than omission. Codex skips
plugin-bundled hooks until the user separately reviews and trusts them, so a
Codex projection could not exercise the structural-guard behavior this
experiment is built to test.

## Evidence status

**Structural and unit evidence — done.** `scripts/tests/test_attention_workflow.py`
covers grant create-only semantics, supersession preserving old grants,
amendment staling evidence, atomic current-state writes, fail-safe evaluation,
SessionStart context for active / holding / exception / no-state, grant-write
denial, unauthorized and authorized push handling, safe-command allowance,
terminal-once run results under delayed and duplicate completion, tracker
projection failure, and VCS checkpoint postconditions against real temporary
repositories.

**Runtime smoke evidence — partial.** The SessionStart and guard hooks were
exercised end to end as executables against real hook payloads in an isolated
state root. The generated publication was installed into an isolated
`CLAUDE_CONFIG_DIR`, where `claude plugin install` confirmed it arrives
disabled by default and `claude plugin details` confirmed it registers one
skill, one agent, and both hook events. The plugin's behavior inside a **live
Claude session** is unverified: the isolated configuration carries no
credentials, and borrowing the real one would have meant touching the normal
configuration. Nothing here shows a hook firing during an actual turn.

**Behavioral pilot evidence — pending.** None of the three hand-observed runs
has happened. Nothing here demonstrates that the workflow regulates attention:

1. a five-minute low-risk all-PASS change (proportionality, judgment-before-verdict);
2. an ordinary proxy-versus-outcome change with quiet implementation, a cold
   resume, and a delayed verifier notification;
3. an unlisted-assumption failure with handback or verifier containment,
   followed by authority supersession if continued.

Compilation, schema validation, and prompt inspection do not prove the
interaction works.

---
name: workflow
description: Run a code change through the attention-regulating lifecycle — Frame, Design, Prepare, authorize, Implement, Verify, Deliver, Close — with versioned authority, local run state, and an independent verifier whose verdict stays withheld until you have committed your own judgment. Use when starting, resuming, authorizing, verifying, or closing a change under this workflow, when the SessionStart card shows an active change, or when the user says "frame this change", "authorize", "candidate ready", "reconcile", "where does this change stand", "supersede the grant", or "close this out". Experimental; supersedes spec-flow while enabled.
argument-hint: "[what you want to do, or nothing to report state]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - Bash
---

# attention-workflow

One skill spans the whole lifecycle. There is no command per phase, and no
turn per phase.

```text
Frame -> Design -> Prepare --authorize--> Implement -> Verify -> Deliver -> Close
```

These are **semantic states**, not mandatory user turns. A five-minute change
may traverse Frame, Design, and Prepare in one message and combine
reconciliation with Close. Compression removes ceremony; it never erases which
phase an event occurred in, because the same evidence means different things in
different phases.

## The state helper is the only writer

All state lives outside the target repository's tracked tree, under a
Claude-local root keyed by repository root. `AW_STATE_ROOT` overrides it.

```bash
HELPER=<absolute path to the plugin's scripts/aw_state.py>
python3 "$HELPER" show          # the projection to act on
python3 "$HELPER" state-root    # where it lives
```

The SessionStart card prints the helper's absolute path — take it from there.
If no card was injected (this repository has no active change yet), the helper
sits at `scripts/aw_state.py` inside this plugin's installed directory; locate
it once and reuse the absolute path for the rest of the change.

Never hand-edit anything under the state root. Grants are create-only and the
guard hook denies direct writes on the declared tool surfaces.

## Three interaction classes — choose deliberately every time

| Class | When | Shape |
|---|---|---|
| **Interactive** | Jacob must decide, authorize, correct a material misunderstanding, resolve an exception, reconcile verification, or approve an ungranted delivery | One bounded question, why now, what each answer changes, a recommendation — *except* at reconciliation — and an immediate visible state change after he answers |
| **Orienting** | A meaningful transfer of responsibility or a trust-relevant condition change | A short receipt. No reply requested |
| **Suppressed** | Everything else | Recorded in state if useful; not shown |

Suppressed means: individual tool calls, expected red/green iterations,
commit-by-commit narration, percentage estimates, elapsed time, routine
`Verify -> Implement` corrections, retries inside tolerance. Elapsed time never
produces a message on its own.

Promotion is monotonic. A structural rule sets the minimum class; judgment may
promote an unforeseen event but may never demote a fired hook, a failed
deterministic check, or a recognized authority failure. Uncertainty about
whether authority still covers what you are about to do promotes to handback.

## Phase by phase

### Frame

Convert the request into a bounded change: the trigger, the intended boundary,
why it matters, obvious exclusions. A precise request traverses Frame with an
orienting receipt; an ambiguous one needs one bounded question.

```bash
python3 "$HELPER" init --change-id <slug> --title "<one line>"
python3 "$HELPER" transition --phase design --owner execution \
  --reason "request was precise enough to frame directly" \
  --next "Investigate the current behavior and choose the route."
```

If Jacob supplied a Linear key, Fibery task, or issue URL, read it now and
record the projection — see `references/issue-projections.md`. The issue is
Frame *input*. It is never the authority.

### Design

Determine the intended outcomes and a route at the altitude that affects risk
or future behavior.

**Record the operator question separately from any proposed proxy.** The
operator question is what the finished change must let Jacob determine. A
taxonomy, report shape, schema, interface, or summary is a *proxy* for it. They
are not the same object, and this is the failure this workflow exists to catch:
a proxy can be implemented exactly, pass every test written for it, and leave
the operator question unanswered.

When a proxy could mask the outcome, run **one representative probe before
authorization**: take a real or seeded input, produce the artifact the proposed
shape would produce, and check whether it answers the operator question.

- Probe passes → carry on; no interaction.
- Probe fails and exactly one viable correction exists → revise the proposal
  silently and re-probe. Do not spend a turn on it.
- Probe fails and materially different product choices remain → one bounded
  decision.

A test proving the proposed proxy was implemented is not evidence that the
operator question is answered. Say so explicitly if anyone offers it as such.

### Prepare

Risk-reduction work, not a formatting pass over Design. Build the prepared
basis, then present it as one compact authorization card.

Write the basis to a temporary JSON file with these keys, then create the grant:

```bash
python3 "$HELPER" grant-create --file /tmp/aw-basis.json
```

| Key | Content |
|---|---|
| `operator_question` | What the finished change must let Jacob determine |
| `promise` | Observable promised outcomes |
| `exclusions` | What this change will not do |
| `route` | The planned route at decision-relevant altitude only |
| `assumptions` | `[{statement, falsifier}]` — load-bearing ones, each with what would disprove it |
| `assumption_coverage` | `{areas_considered, known_unknowns, residual_unlisted_risk}` |
| `tolerances` | `{permitted: [...], stop_before: [...]}` |
| `baseline` | `{description, classified}` — `classified: false` means adverse context cannot later be called pre-existing |
| `representative_probe` | `{question, probe}` or `{waived_reason}` |
| `planned_observations` | How each promise will be observed at Verify |
| `enforcement` | `{hook_guarded, check_gated, agent_monitored, uncovered}` |
| `delivery_authorized` | Delivery actions this grant covers (see below) |
| `supersedes` | Prior grant id, when this replaces one |

`assumption_coverage.residual_unlisted_risk` must be present and honest. Naming
assumption areas is not proof the inventory is complete. Never present it as if
it were.

**`enforcement` must be accurate, not reassuring.** Copy the classes from
`references/enforcement-map.md`. Do not label anything hook-guarded that this
plugin does not actually intercept and test. Uncovered boundaries are disclosed
as residual risk, not dressed as guardrails.

`delivery_authorized` accepts only: `commit`, `git-push`, `jj-git-push`,
`pr-open`, `pr-merge`, `deploy`, `migrate`, `tracker-in-progress`,
`tracker-exception`, `tracker-outcome`, `tracker-transition`. Only the first
three are enforced structurally; the rest are recorded authority the agent
honors. Grant the smallest set.

The authorization card is interactive. Present promise, route-that-matters,
grounds, representative outcome, autonomy boundary with its honest enforcement
split, and one question: authorize, revise, or stop?

On "authorize":

```bash
python3 "$HELPER" transition --phase implement --owner execution --condition active \
  --active-grant g1 --clear-attention \
  --reason "Jacob authorized the prepared basis" \
  --next "Candidate ready -> independent Verify"
```

Then emit one short `AUTHORIZED` receipt and go quiet.

### Implement

Adapt ordinary mechanics, iterate through expected failures, and correct
implementation defects without interaction while the grounds hold. Emit
nothing.

On demand, report **checkable state** — loaded grant, active guards, changed
files, last check run, recorded findings — from `show`. Never assert that work
"remains on course"; that is a conclusion from the agent the grant constrains.

**Stop and hand back before material departure** when: a promised outcome or
explicit exclusion cannot be preserved; a named load-bearing assumption or
tolerance is falsified; continuing needs an ungranted destructive or external
action; continuing adds or materially changes a public API, dependency, data
model, security boundary, compatibility promise, or migration; planned
verification would be weakened; or you cannot determine whether the grant
covers the departure.

Ordinary difficulty, expected test iteration, and choices inside permitted
adaptation are **not** exceptions.

A handback carries: the failed ground; direct evidence; why authority no longer
suffices; work preserved and its safe state; what you deliberately did not do;
one bounded decision with materially distinct options; a recommendation and its
consequence.

```bash
python3 "$HELPER" transition --phase prepare --owner jacob --condition exception \
  --attention-kind exception --attention-summary "<failed ground>" \
  --safe-point "<what is preserved and where>" \
  --reason "load-bearing assumption falsified: <statement>"
```

Depth scales with accumulated context distance — unobserved material
transitions, changed boundaries, new context, lost safe-point detail. Time away
is a conservative hint that the gap may be larger. It never adds content by
itself.

### Verify

Verify begins at a **readiness handoff**, not when a test runs.

1. Identify the candidate and confirm its scope from actual repository state.
   If anything claims a VCS checkpoint or isolated boundary, verify the
   postcondition: `python3 "$HELPER" checkpoint-verify`. Agent prose is not
   evidence that a checkpoint exists. If it does not, say so and repair it
   without claiming it previously existed.
2. Create the run **before** dispatching, so its identity exists independently
   of any message:

   ```bash
   python3 "$HELPER" run-create --grant g1 --candidate c2
   python3 "$HELPER" transition --phase verify --owner verification \
     --active-candidate c2 --active-verification-run v1 \
     --reason "implementation presented candidate c2 as ready" \
     --next "independent verification result"
   ```
3. Dispatch `workflow-verifier` with: run id, helper path, the grant's promise,
   exclusions, route, planned observations, representative probe, baseline, and
   candidate scope. **Do not pass** the implementer's success claim, narrative,
   claimed actual route, or deviation assessment. Record the implementer's own
   claim separately in your notes so it can be compared afterward.
4. Emit one orienting `CANDIDATE READY` receipt.

**Resolve the run by identity, never by message.** Before starting fallback
verification or reporting a result as unavailable:

```bash
python3 "$HELPER" run-list
python3 "$HELPER" show
```

If the run holds a terminal result, use it — regardless of whether a completion
message arrived, arrived twice, or arrived out of order. A duplicate or delayed
notification produces no operator message and no state change. Never launch a
second verification while a completed run exists for the same grant and
candidate, and never record independent verification as inline.

**Ordinary defect → back to Implement, silently.** Same authority, history
records the reason, no interactive turn, and the final evidence keeps the
failed and corrected observation.

### Reconciliation — the one place recommendation-first is forbidden

```bash
python3 "$HELPER" run-evidence v1     # verdict and recommendation stripped
```

Show Jacob:

- each promised outcome against the observation actually performed, the command,
  and the result;
- the representative outcome: what the artifact lets him determine;
- planned route versus the **verifier-derived** actual route, then the
  implementer's account, and whether they agree — a discrepancy is itself a
  finding;
- adverse context split into new, pre-existing, and unclassified;
- limitations of the observations.

Then ask him to judge — **with no verdict, no recommendation, no preselected
option, no PASS/FAIL labels, and no agreement cue anywhere above the question**:

> Based on the observations: ready, not ready, or do you need one named
> inspection? Name the decisive observation or mismatch in one sentence.

A bare "yes" does not satisfy this. Record it, then reveal:

```bash
python3 "$HELPER" run-judge v1 --judgment ready --decisive "<his sentence>"
python3 "$HELPER" run-reveal v1
```

`run-reveal` refuses until a judgment is recorded — the ordering is structural,
not a promise. Show agreement or disagreement explicitly. **Disagreement keeps
the change in Verify** and opens a bounded investigation; it is never averaged
away and the verifier never outranks his evidence-based objection.

### Deliver

Make the verified change real. Every delivery action must appear in the active
grant's `delivery_authorized`; otherwise stop and return one bounded decision
naming the exact action, target, evidence, reversibility, and consequence of
approval. `git push` and `jj git push` are denied by the guard hook when
unauthorized, so an attempt is a stop, not a slip.

Declining delivery may close the run as **verified but not delivered**, or
leave it explicitly waiting.

A delivery that fails without changing external state stays in Deliver with the
actual outcome recorded. An equivalent retry inside existing authority needs no
new decision; a corrective action that changes risk, target, or rollback
behavior creates an exception first. Close never claims a delivery that did not
succeed.

### Close

Reconcile the final outcome, preserve durable residue, release the thread.

Close **may not begin** while the active candidate's verification is stale or
while a required representative outcome probe remains unobserved. Passing
checks against a proxy do not substitute for the promised operator outcome.

```bash
python3 "$HELPER" transition --phase close --owner jacob --condition active \
  --outcome delivered --reason "delivered as authorized" --clear-attention
```

`--outcome` is `delivered`, `stopped`, or `abandoned`. Abandoned work is never
represented as delivered. Durable residue goes to its usual home —
`/capture-decision` for decisions, README/CLAUDE.md for behavior changes — not
into the run state.

## Supersession

A material change to a promised outcome, exclusion, route commitment,
load-bearing assumption, tolerance, planned observation, or delivery boundary
creates a **new grant** that supersedes the old one. Old grants are never
rewritten; the guard hook denies attempts on the declared surfaces.

`grant-create` with `supersedes` set automatically marks every non-stale
verification run stale. Prior candidates and evidence stay inspectable and may
not authorize readiness, delivery, or closure. Return to Design when the
outcome or route choice is open, to Prepare when the revised basis is known.
After re-authorization, resume at the smallest point that can produce fresh
evidence and bind a **new** run to the new grant.

A clarification that changes no authority and no planned observation may retain
evidence — only with a recorded reason saying why it is non-material.

## Resumption

The SessionStart hook injects the state card. Trust it over chat history, git
state, and issue status.

If the projection reports `status: fail-safe`, the record is incomplete or
contradictory. Do not continue implementation, verification, or delivery, and
do not reconstruct authority optimistically. Preserve the existing candidate,
mark it explicitly untrusted, name exactly what authority is missing, and
return the smallest decision that restores it.

If it reports `status: no-state`, this repository has no active change. Say so
and offer to frame one.

## Proportionality

- A five-minute, precise, low-risk change: one authorization, one combined
  reconciliation-and-close. Phases still exist in state and history.
- A two-hour on-course implementation: no additional interaction at all.
- Messages are justified by consequential decisions, ownership transfers,
  trust-relevant condition changes, and exceptions — never by duration.

No points, streaks, timers, periodic updates, percentage estimates, cockpit
terminology, or phase-per-turn ceremony. If a receipt only echoes what Jacob
just said, it is ceremony; drop it.

## References

- `references/state-model.md` — record shapes, fail-safe rules, helper commands.
- `references/enforcement-map.md` — what is hook-guarded, check-gated,
  agent-monitored, and uncovered, with known bypasses.
- `references/issue-projections.md` — the optional Linear and Fibery projection.

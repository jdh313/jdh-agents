---
name: author
description: >-
  Shape one thought into one well-formed ticket. This skill should be used
  when the user invokes `/pm:author`, says "write a ticket for this", "file
  this properly", "open a ticket", "turn this into a ticket", "make a proper
  ticket out of this", or wants a single issue authored to spec rather than
  captured raw. Runs a short shaping interview for the two obligated body
  slots, composes the body per `references/issue-body.md`, and hands the
  publish to the linear plugin's `linear-ops` agent. One ticket only — use
  `pm:breakdown` to slice a goal into many, or `spec-flow:capture` to file a
  raw thought with no questions asked.
argument-hint: "[the thought — a sentence, a paragraph, or nothing to draw from the conversation]"
allowed-tools:
  # Compose the body against the shared spec
  - Read
  # Publish via the linear plugin's operator agent
  - Agent
  # Optional grounding before authoring a decision-shaped ticket
  - Skill
  - Bash(ndr *)
  # Read-side Linear lookups when the caller needs to see existing tickets
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
---

# author

## Overview

One thought in, one well-formed ticket out.

This is the single-ticket skill the rest of `pm` has been pointing at. It sits
between two neighbours that already existed:

| Skill | Tickets | Questions asked |
|---|---|---|
| `spec-flow:capture` | one | none — captures raw, on purpose |
| **`pm:author`** | **one** | **a short shaping pass** |
| `pm:breakdown` | many | slicing, dependency order |

The value is entirely in the questions. A captured ticket preserves a thought
before it evaporates; an authored ticket is one a third party can pick up
without asking you what you meant. If you do not want to answer questions right
now, you want `spec-flow:capture` — say so and route there rather than
answering reflexively.

## Scope

- **Owns:** the shaping interview, and composing the body.
- **Does NOT own:**
  - **Linear mechanics.** Label values, status flow, priority semantics,
    title shape, milestone naming, and every MCP call pattern belong to the
    `linear` plugin's `linear` skill. This skill decides *what the ticket
    says*; that skill decides *how Linear stores it*.
  - **The write itself.** That goes to `linear-ops` (below).
  - **Whether to open a ticket at all.** That is the project's own floor rule.

## The body spec

The body conforms to `../../references/issue-body.md`. Read it before composing
— do not reconstruct it from memory or from an existing ticket, which may
predate the current spec.

The link carries the definitions. The obligation is restated here because a
consumer that only links to a rule does not enforce it:

- **The aim is expected on every ticket.** First non-empty line, no heading,
  one sentence, present tense, naming what becomes *true* — not what will be
  done. Write it even when the title seems to cover it.
- **`## Done when` is expected at status Todo or beyond.** Observable bullets
  a third party can check without asking you what was meant. A Backlog ticket
  may omit it.
- The other three slots — `## Why now`, `## Sketch`, `## Context` — are
  optional, and an empty one is omitted rather than left as a bare heading.

## Workflow

### 1. Take the input

From the argument if given; otherwise from the conversation — the bug just
hit, the decision that just landed, the thing the user said should be a ticket.
State in one line what you understood the thought to be, so a
misread surfaces before the interview rather than after the write.

### 2. Ground, when the ticket is decision-shaped

**Structural trigger, not a judgment call:** the repo has a `.ndr.toml`, *and*
the ticket's type resolves to `Decision`.

When both hold, invoke `ndr:ground` with the ticket's topic before composing.
A decision ticket that reopens a settled question is the failure this prevents,
and it is cheap to check. Fold any head into `## Context` as an `ndr:` reference
and note that the fork may already be closed.

Skip silently when either condition fails. Do not ground a `Chore`.

### 3. Run the shaping interview

**Ask only what the input has not already answered, one question at a time, and
never more than three.** An interview longer than the ticket is a worse tool
than the raw capture it replaced.

Ask in this order, stopping as soon as the body holds together:

1. **The aim**, when the input is phrased as an action rather than an outcome.
   *"What's true once this ships that isn't true now?"*
2. **`## Why now`**, when there is no evidence in the input. *"What's the cost
   of leaving it — a failure that happened, something blocked behind it, a
   date?"* If the honest answer is "nothing", that is a finding: say so, omit
   the section, and file it to Backlog.
3. **`## Done when`**, when the intended state is Todo or beyond and no
   observable signal is evident. *"How would someone else confirm this is
   done?"*

Infer without asking: the type and surface labels, the title, and the state.
Say what you inferred at the confirmation step; a wrong guess is cheaper to
correct there than to ask about three times.

### 4. Compose and confirm

Show the complete ticket — title, labels, state, priority, and the full body —
in one block, then stop.

**Never publish without explicit sign-off.** No tool filter enforces this: the
publish path is a subagent dispatch, and nothing structurally distinguishes an
approved dispatch from an unapproved one. The rule holds because it is stated
here. A ticket is outward-facing and lands in a shared workspace; the user sees
it before Linear does.

### 5. Publish

Dispatch `linear-ops` (linear plugin) with the intent block its own definition
specifies: operation, team, fields, body, relations. Pass the body verbatim —
the agent does not author prose, and anything you leave for it to fill in comes
back blocked.

**Structural fallback:** if the `linear-ops` agent is not available — the
linear plugin is not installed — do not reimplement the write. Say the agent
is missing, and hand the composed ticket to the `linear` skill's create
operation, or to the user to paste. Cross-plugin references resolve only when
both plugins are installed (`ndr:m7pd8d`).

### 6. Report

Return the ticket ID, the title, and the URL from the agent's result. Surface
its `## Discrepancies` block verbatim when non-empty — a silently dropped
label is exactly the failure the verify step exists to catch, and swallowing
it here defeats it.

## When the ticket is bigger than a ticket

If the shaping pass reveals more than one independently-shippable outcome, stop
and say so rather than writing a body with three unrelated `## Done when`
bullets. Route to `pm:breakdown`, which owns vertical slicing and dependency
order.

The signal is in the finish condition: a ticket whose completion bullets cannot
all be checked on the same day is usually several tickets.

## Composes with

- **`linear-ops`** (linear plugin) — performs the write. Owns identifier
  resolution, the MCP silent-failure workarounds, and post-write verification.
- **`linear`** (linear plugin) — the conventions behind the fields this skill
  infers. Consult it for label values, title shape, priority, and status flow.
- **`../../references/issue-body.md`** — the body spec. Definitional.
- **`../../references/issue-shape.md`** — the required-field checklist around
  the body.
- **`../../references/layer-policy.md`** — which milestone or project the
  ticket belongs to, when the call is not obvious.
- **`ndr:ground`** — invoked on the structural trigger in step 2.
- **`pm:breakdown`** — the escalation when one ticket turns out to be several.
- **`spec-flow:capture`** — the de-escalation when the user does not want an
  interview right now.

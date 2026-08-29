---
name: wayfinder
description: >-
  Chart an effort too large to see the end of — more than one agent session can
  hold, and still fogged — as a shared map of decision tickets in Linear, then
  resolve them one per session until the route to the destination is clear. This
  skill should be used when the user invokes `/pm:wayfinder`, says "chart this",
  "map this out", "I don't know where to start on this", "this is too big to
  plan", "work the map", "what's next on the map", or hands over a loose idea
  whose shape isn't visible yet. Names the destination first, publishes a map
  ticket plus `Decision` / `Spike` / `Chore` question tickets in dependency
  order via the linear plugin, and routes each resolution to an ndr atom via
  `/capture-decision`. Charts questions, not work — once the route is clear,
  `pm:breakdown` slices it. Adapted from mattpocock/skills (MIT, © 2026 Matt
  Pocock).
argument-hint: '[loose idea to chart, or a TEAM-N map ticket to work]'
allowed-tools:
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issue_labels
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__list_projects
  - mcp__linear-server__save_issue
  - mcp__linear-server__save_comment
  - mcp__obsidian-mcp__search_notes
  - mcp__obsidian-mcp__read_multiple_notes
  - Read
  - Grep
  - Glob
  - Bash(ndr *)
  - Skill
  - Agent
---

# wayfinder

## Overview

A loose idea has arrived that is too big for one agent session and still wrapped in fog: the way from here to the **destination** is not visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** in Linear, then works its **decision tickets** — questions whose resolution is a decision, not slices of a build to execute — one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic — engineering work, vault restructuring, whatever fits the shape.

## Where this sits (the handoff chain)

```
wayfinder  →  pm:breakdown  →  spec-flow / clearance
 charts        slices              implements
```

- **`pm:wayfinder` charts a goal you cannot yet see.** Its tickets are *questions*. It produces decisions, not deliverables. It is done when nothing is left to decide.
- **`pm:breakdown` slices a goal you can already see.** Its tickets are *vertical slices of a build* — tracer bullets through every layer. It assumes the route is known.
- **`spec-flow` / `clearance` implement a slice.**

The boundary test: **can you already name the work, or only the questions?** If you can list the things that must be built, you do not need a map — go straight to `pm:breakdown`. If charting surfaces no fog at all (step 3 below), say so and stop; a map with no fog is overhead.

The reverse direction is also live: when the map's last ticket closes, the destination is a spec / decision / change that `pm:breakdown` can now slice, or that `spec-flow:draft` can contract directly.

## Plan, don't do

Wayfinder is **planning** by default: each ticket resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you have reached the edge of the map and it is time to hand off. An effort can override this in its `## Notes`, carrying execution into the map itself, but absent that, produce decisions, not deliverables.

## Refer by name

Every map and ticket is a Linear issue, so it has a **name**: its title. In everything the human reads — narration, the map's `## Decisions so far` — refer to it by that name, never by a bare `TEAM-N`. A wall of `TEAM-42, TEAM-43, TEAM-44` is illegible; names read at a glance. The ID does not vanish; it rides *inside* the name as a link, but it never stands in for it.

## The map

The map is a **single Linear issue**, and it is the canonical artifact.

- **Shape: the map is the parent.** A map clears `references/layer-policy.md`'s earn-it bar by construction — it holds a design substrate, it generates cross-ticket discussion, and it fans out past five tickets. Declare that the tickets hang off the map; **how** that link is expressed is the `linear` skill's call against the layer policy, not this skill's. Do not name a Linear relation type here.
- **Identity: the `wayfinder:map` marker label.** Give the map the `wayfinder:map` marker, plus Type `Decision` and the surface its destination touches — the marker is a third, ungrouped dimension additive to that pair (`references/issue-shape.md`), so maps are found by query rather than by title search. Still title it `Map: <destination noun-phrase>`: the prefix keeps a map legible in a flat list where the label is not rendered.
- **The map is an index, not a store.** It lists the decisions made and points at the tickets that hold their detail. A decision lives in exactly one place — its ticket, and its ndr atom — so the map never restates it, only gists it and links.

### The map body

The whole map at low resolution, loaded once per session. Open tickets are **not** listed; they are found by Linear query — the tickets linked to this map, state not Done/Canceled. Ask `linear` for the query shape; it owns how the link is expressed.

```markdown
## Destination

<what reaching the end of this map looks like: the spec, decision, or change
this effort is finding its way to. One or two lines; every session orients to
it before choosing a ticket.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Decisions so far

<!-- the index: one line per closed ticket, enough to judge relevance -->

- [<closed ticket title>](link): <one-line gist of the answer> — `ndr:<slug>`

## Not yet specified

<!-- in-scope fog you cannot ticket yet; graduates as the frontier advances -->

## Out of scope

<!-- work ruled beyond the destination; closed, never graduates -->
```

### Tickets

Each ticket is a **question**, sized to one fresh agent session. Body per `references/issue-shape.md`:

```markdown
## Context

<the map it belongs to, and why this question is live>

## Done when:

- <the decision or investigation this ticket resolves> is captured and linked here
```

Ticket mechanics:

- **Labels:** one surface + one type, per the `linear` skill. Type comes from the ticket's mode (next section). Map *tickets* take no marker — `wayfinder:map` belongs to the map itself, not to the tickets hanging off it — and the mode is recorded in the body, not in the label set.
- **Claiming:** a session claims a ticket by **assigning it to the driver first**, before any work, so a concurrent session skips it. That assignee *is* the claim; an open unassigned ticket is unclaimed. (This is the `linear` skill's accept ritual, applied at map scale.)
- **Blocking:** use Linear's **native** blocks / blocked-by relation. This is essential, not cosmetic: it renders the frontier visually in Linear's own UI, so the human sees what is takeable without opening the map. A ticket is **unblocked** when every ticket blocking it is closed; the **frontier** is the open, unblocked, unclaimed tickets — the edge of the known.
- **The answer is not in the body.** It is recorded on resolution (see *Work through the map*). Assets produced while resolving are linked from the ticket, not pasted into it.

## Ticket modes

Every ticket is either **worked with the human** — a live exchange the agent never stands in for, so a grilling ticket where the agent answers its own questions has broken the mode — or **driven by the agent alone**.

| Mode | With the human? | Type label | How it resolves |
|---|---|---|---|
| **Research** | no | `Spike` | Reading docs, third-party APIs, or local knowledge bases to surface a fact a decision waits on. Use when knowledge outside the working directory is required. |
| **Prototype** | yes | `Spike` | Raise the fidelity of the discussion with a cheap, rough, concrete artifact to react to — an outline, a stub, UI or logic code. Use when "how should it look" or "how should it behave" is the key question. Dispatch `Skill(craft:prototype)`; link the prototype as an asset. |
| **Grilling** | yes | `Decision` | Conversation. **The default case.** Dispatch `Skill(craft:grill)` and `Skill(craft:domain-modeling)`. Where the repo carries a `CONTEXT.md` glossary or ndr coverage, prefer `Skill(craft:grill-with-docs)`. |
| **Task** | either | `Chore` | Manual work that must happen before a *decision* can be made: nothing to decide, prototype, or research, but the discussion is blocked until it is done — signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. The one mode that *does* rather than decides; it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can, otherwise it hands the human a precise checklist. Resolved when the work is done; the answer records what was done and any facts later tickets depend on (credentials location, new URLs, row counts). |

The `Spike` / `Decision` split above is the `linear` skill's own boundary test — empirical vs judgment — applied to map tickets. Research and prototype are things you go and find out; grilling is a call made from the chair.

**A `Task` ticket blocked on someone else's knowledge is a questionnaire.** Dispatch `Skill(pm:to-questionnaire)` to turn it into a document that person can fill in async, and link the document from the ticket.

## Fog of war, and out of scope

The map is *deliberately* incomplete: do not chart what you cannot yet see. Beyond the live tickets lies the **fog** — decisions and investigations you can tell are coming but cannot yet pin down, because they hang on questions still open. Resolving a ticket clears the fog ahead of it, graduating whatever is now specifiable into fresh tickets, one at a time, until the route is clear and no tickets remain.

**The fog model itself is defined once for this marketplace, in the `spec-flow` plugin's contract template** (`references/contract-template.md`, the `Not yet specified` section) — the dim view ahead, the phrase-it-now sharpness test, and graduation as the frontier advances. Read it there; this skill applies that model to the map rather than restating it, and the two must not drift apart. `pm:breakdown` applies the same model to a contract parent, and `spec-flow:close` drains whatever never graduated.

What this skill adds is **where the fog lives at each stage, so it lives in exactly one place**:

- **While a map is live**, its fog is the map's `## Not yet specified`. A ticket exists for what you can phrase now; a fog patch for what you cannot.
- **When the map closes** and hands off, any patch still fogged **moves to the contract's `## Not yet specified`** (the breakdown parent's companion doc) and is cleared from the map. It does not live in both.
- **Out of scope is scope, not sharpness.** Fog gathers only *toward* the destination; work past the destination goes in the map's `## Out of scope`, never in `## Not yet specified`, and never graduates. If a ticket that already exists turns out to sit past the destination, **close it** — a closed ticket is unambiguously off the frontier — and leave one line in `## Out of scope` with the gist, the reason, and a link to the closed ticket. It stays out of `## Decisions so far`, which records the route actually walked; a scope boundary is not a step on it. Out-of-scope work returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

## Invocation

Two modes. Either way, **never resolve more than one ticket per session** — research tickets excepted, since they run as parallel subagents.

### Chart the map

The user invokes with a loose idea.

1. **Name the destination.** Dispatch `Skill(craft:grill)` and `Skill(craft:domain-modeling)` to pin down what this map is finding its way to — the spec, decision, or change. The destination fixes the scope, so it is settled first.

2. **Ground against ndr heads** (skip without the external `ndr` plugin). Dispatch `Skill(ndr:ground)` against the destination's area. A question already settled by a standing decision is not fog — it is a link into `## Notes`, and charting a ticket for it wastes a session.

3. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** — the route is already clear, the whole journey small enough to plan in one sitting — you do not need a map. Stop and say so, and point at `pm:breakdown` instead.

4. **Confirm the chart before publishing.** Show the destination, the tickets you can specify now (title, mode, type label, blocked-by), and the fog patches as a numbered list. Ask: is the destination right, is anything here actually out of scope, is any ticket really a fog patch (or vice versa). Iterate until the user approves. Publishing is the only destructive step in this skill.

5. **Create the map** — Destination and Notes filled in, `## Decisions so far` empty, the fog sketched into `## Not yet specified`. Set project, milestone (per `references/layer-policy.md`), priority, and labels per the `linear` skill.

6. **Create the tickets, then wire in a second pass.** Save the tickets first so they have real `TEAM-N` IDs, then have `linear` link each one to the map and wire the blocks / blocked-by edges between them — issues need IDs before they can reference each other. Wiring sorts them into the frontier and the blocked; everything you cannot yet specify stays in `## Not yet specified`.

7. **Fire the research subagents.** For each research-mode ticket just created, dispatch a subagent in parallel — `Explore` for questions answerable inside the repo, a web-research agent for anything outside it. Each posts its findings as a resolution comment on its own ticket.

8. **Stop.** Charting is one session's work; it hand-resolves nothing.

### Work through the map

The user invokes with a map (`TEAM-N` or URL). A ticket argument is **optional**: without one, you pick the next decision, not the user.

1. **Load the map** — the low-resolution view, not every ticket body.
2. **Choose the ticket.** If the user named one, use it. Otherwise take the first frontier ticket in order. **Claim it**: assign it before any work.
3. **Resolve it.** **Zoom as needed** — fetch the full body of any related or closed ticket on demand; dispatch whichever skills `## Notes` names. If in doubt, `Skill(craft:grill)` plus `Skill(craft:domain-modeling)`.
4. **Capture the decision.** A `Decision`-mode resolution is an ndr atom: dispatch `Skill(ndr:capture-decision)` and put the returned `ndr:` reference in the resolution. A `Spike` resolution is a **finding** — a vault note or a comment — and becomes an atom only if the finding itself resolves a decision (the `linear` skill's rule). A `Chore` resolution records what was done and the facts later tickets depend on.
5. **Record the resolution.** Post the answer as a comment on the ticket, move the ticket to a completed state, and append one line to the map's `## Decisions so far` — the ticket's name as a link, a one-line gist, and the `ndr:` reference if one was captured.
6. **Advance the frontier.** Add newly-surfaced tickets (create, then wire). Graduate any fog the answer made specifiable, clearing each graduated patch from `## Not yet specified` so it lives only as its new ticket. If the answer reveals that a ticket — this one or another — sits beyond the destination, **rule it out of scope** rather than resolving it on the route. If the decision invalidates other parts of the map, update or cancel those tickets and say so.

The user may run unblocked tickets in parallel, so expect other sessions to be editing Linear concurrently. Re-read the map before writing to it.

### Closing the map

The map is done when no open tickets remain and `## Not yet specified` holds nothing that still blocks the destination. On close:

- Move any still-fogged patch to the successor contract's `## Not yet specified`, or rule it out of scope. Do not leave fog stranded on a closed map.
- Hand off: `/pm:breakdown` if the destination is now a sliceable build, `/spec-flow draft` if it is a single contract-shaped change.
- The map ticket itself stays open until both are true, then moves to a completed state. Its `## Decisions so far` is the durable index of the route walked; the ndr atoms hold the reasoning.

## Rules

- **One ticket per session** (research excepted). A session that resolves three tickets has stopped wayfinding and started guessing — the second decision was made without the first one's consequences settling.
- **Never stand in for the human** on a ticket that needs them. An agent that answers its own grilling questions has produced a decision nobody made.
- **Chart questions, not work.** If you are about to write a ticket whose body describes something to *build*, it belongs to `pm:breakdown`, not here. The one exception is a `Chore` ticket that unblocks a decision.
- **Do not pre-slice the fog.** A patch is coarser than a ticket and may graduate into several tickets, or none. The test is whether you can *state* the question now, not whether you can *answer* it now.
- **The map never restates a decision.** One line and a link. The ticket and its ndr atom hold the detail.
- **Confirm before publishing.** Show the chart once more before any issue is created.

## Composes with

- **`craft:grill` / `craft:domain-modeling`** (craft plugin) — the default resolution move for a `Decision`-mode ticket, and the charting move in step 1.
- **`craft:grill-with-docs`** (craft plugin) — preferred over plain grilling where the repo carries a `CONTEXT.md` glossary or ndr coverage.
- **`craft:prototype`** (craft plugin) — resolves a prototype-mode ticket.
- **`ndr:ground`** (external ndr plugin) — grounding pass before charting, so the map does not re-decide settled architecture.
- **`ndr:capture-decision`** (external ndr plugin) — captures each `Decision`-mode resolution as an atom.
- **`linear`** (linear plugin) — performs the issue saves, and owns the Spike-vs-Decision boundary test, the label set, the status flow, and the accept ritual this skill claims tickets with.
- **`pm:to-questionnaire`** (this plugin) — turns a `Chore` ticket blocked on someone else's knowledge into a document they can fill in async.
- **`pm:breakdown`** (this plugin) — the downstream half of the handoff chain, once the route is clear.
- **`spec-flow:draft`** (spec-flow plugin) — the alternative handoff when the destination is a single contract-shaped change.
- **`Explore` agent** (built-in) — resolves in-repo research tickets in parallel.

## See also

- **`references/issue-shape.md`** — body template and required fields each map ticket conforms to.
- **`references/layer-policy.md`** — the earn-it criteria and the sibling-parent shape the map uses.
- **`references/contract-template.md`** in the `spec-flow` plugin — the canonical definition of the fog-of-war model this skill applies to the map.
- **`breakdown`** skill in this plugin — slices the route once wayfinding has cleared it.

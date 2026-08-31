# Issue body

What goes in the body of a work item, in any tracker. Tracker-agnostic by
construction: this file names *slots*, and each host renders them its own way.
Nothing here knows what Linear is.

Fields the tracker already models natively -- status, priority, assignee,
labels, estimate, dates, relations -- are never restated in the body. A slot
exists only where no tracker carries the content as a first-class field.

## The five slots

In order. Only the aim and `## Done when` carry any obligation.

| Slot | Obligation | Carries |
|---|---|---|
| aim | expected on every ticket | one line: what this ticket makes true |
| `## Why now` | optional | the cost, with evidence |
| `## Sketch` | optional, non-binding | an approach, deliberately hedged |
| `## Done when` | expected at status >= Todo | observable completion bullets |
| `## Context` | optional, last | residual state and caveats |

### aim

The first non-empty line of the body. **No heading.** One sentence, present
tense, naming what becomes true -- not what will be done.

> Make `ndr status` report a stale grounding rule, not just a missing one.

It is the only slot addressed positionally rather than by heading, because a
heading above a single sentence is heavier than the sentence. Hosts with a
one-line text field map the aim to it, where it becomes queryable.

Write it even when the title seems to cover it. A title is a name; the aim is
a claim, and the two are rarely the same sentence.

### `## Why now`

What makes this worth doing *now*, backed by something concrete -- a date, a
duration, a failure that actually happened, a quoted error, work that is
blocked behind it.

The heading is deliberately "why now" rather than "why". A bare "why" invites
the aim restated in different words; "why now" cannot be answered that way,
because it demands a trigger, a cost, or a deadline the aim does not contain.

If there is no answer, omit the section -- and take the omission seriously.
A ticket with no reason to act now is usually a ticket that belongs in the
backlog, which is a useful thing to have learned at filing time.

This is the slot that separates a good ticket from a filed one. It is also
where a defect's reproduction and expected-vs-actual live: they are the
evidence, not a separate ceremony.

### `## Sketch`

An approach, offered and not imposed. Hedged language is correct here --
"consider", "probably", "one option" -- because a sketch that hardens into a
specification defeats its purpose: the person implementing has more
information than the person who filed it.

Keep speculation visibly separate from fact. "The rule file was two versions
behind" is a fact and belongs in `## Why now`; "the cause is probably the
init path" is speculation and belongs here.

Omit the section rather than writing an empty gesture at one.

### `## Done when`

Bullets a third party can check without asking the author what was meant.
Each one names an observable signal.

Good:

- `ndr status` distinguishes current from stale and names the version gap.
- Verified against a deliberately-stale fixture.

Bad:

- ~~Auth works correctly.~~ (no observable signal)
- ~~Tests pass.~~ (which tests?)
- ~~This feels solid.~~ (not observable)

Backlog items may omit it. Promotion past Backlog is where it is expected --
enforced as a review prompt at grooming, never as a hard gate on creation. A
ticket that cannot state its finish condition is usually a ticket whose scope
is not yet settled, and that is the finding, not a lint failure.

### `## Context`

Residual state: what has already been done, what no longer reproduces, which
environment or version it was seen on, what was ruled out. It goes **last**
because it is what a reader needs after understanding the ticket, not before.

This is not the opener. Motivation belongs in `## Why now`.

## Fill guidance by type

The slot set never changes. What changes is what each slot should contain,
keyed off the ticket's type label. A ticket that changes type mid-flight --
a decision that turns out to need evidence first -- is refilled, never
restructured.

| Type | aim | `## Why now` | `## Done when` |
|---|---|---|---|
| Feature / Improvement | what becomes true | the cost of not having it | the shipped, observable outcome |
| Bug | what stops happening | repro + expected vs actual + blast radius | the fix, plus a regression check |
| Spike | the question, stated as a question | why the unknown blocks something | the finding is written up -- never merged code |
| Decision | the fork being closed | what stays blocked while it is open | the decision is captured in the durable record and linked here |
| Docs / Chore | what becomes true | often omitted; the aim usually carries it | the observable end state |

### Defects

A defect is the type whose content diverges most, and it is still the same
five slots. The canonical bug-report elements are not extra sections; each one
already has a slot that wants it.

| Canonical element | Slot | Why there |
|---|---|---|
| Steps to reproduce | `## Why now` | the primary evidence that something is wrong |
| Expected vs actual | `## Why now` | the same evidence, stated as a gap |
| Blast radius, frequency, duration undetected | `## Why now` | this is what makes it worth fixing now |
| Suspected cause | `## Sketch` | speculation, and marked as such |
| The fix plus a regression check | `## Done when` | a defect is not done when it stops reproducing by hand |
| Environment, version, build | `## Context` | residual state a reader needs after the report |
| What was already ruled out or hand-patched | `## Context` | stops the next person re-walking it |

Two rules carry over from the bug-reporting literature and are worth keeping
literally:

- **Separate fact from speculation.** "The rule file was two versions behind"
  is an observation and belongs in `## Why now`. "The cause is probably the
  init path" is a guess and belongs in `## Sketch`. Mixing them costs the
  reader the ability to tell which is which.
- **A reproduction is the most valuable thing in the ticket.** When it is
  cheap to write down, write it down, even for your own bug -- the version of
  you that picks this up has forgotten the state you were in.

A defect found in work that has not yet shipped is usually not a ticket at
all: it is part of finishing the work that produced it. Open a defect ticket
when the broken behavior has already been accepted as done.

### Spikes

A **spike** states its timebox in the tracker's own estimate or duration
field, in hours -- not in the body, and never as story points. The body says
what finding ends it.

A **decision** ticket tracks the work of making the call. The reasoning does
not live in the ticket: it goes to the durable decision record, and the ticket
links to it. A ticket is a unit of work and gets closed; a decision outlives
the work that produced it.

### Adding a type later

A new type earns **fill guidance** -- a row in the table above. It earns a
**new slot** only when it must carry something no existing slot can hold.
Defects were the test case: reproduction steps looked like they needed their
own slot until it was clear they are evidence, and evidence already has one.

## Cross-references

Reference other tickets and durable decision records **inline, where the claim
is made**, not in a dedicated section. A references section collects links
away from the sentences that needed them.

## Rendering

The slots are the contract. How a host stores them is the host's business.

**Markdown-blob hosts** (any tracker whose body is one rich-text field):
render the aim as the first line, and each remaining slot as an `##` heading
with the exact spellings above. Heading text is load-bearing -- tooling that
audits for a finish condition matches on `## Done when` literally.

**Typed-field hosts** (any tracker modeling fields separately): map each slot
to its own field where one exists, since content inside a rich-text blob is
usually invisible to that tracker's query and cross-reference layer. Map the
aim to a one-line text field. Where no field exists for a slot, fall back to
the heading rendering inside the description.

## Anti-conventions

- **No section restating a native field.** No status, priority, assignee, or
  blockers in prose. They go stale the moment someone edits the real field.
- **No free-form notes section.** It serves no reader; whatever it would hold
  belongs in `## Context` or nowhere.
- **No conventional-commit prefixes in titles.** `feat:` / `fix:` / `chore:`
  duplicate the type label.
- **No tracker issue IDs in source code, comments, or decision records.**
  References run ticket to code, not code to ticket.
- **No empty slot left as a heading.** Omit the section.

## See also

- **`issue-shape.md`** — the required-field checklist for a well-formed ticket
  (title, project, priority, labels). That file covers the fields *around* a
  ticket; this one covers what goes *inside* the body.
- **`layer-policy.md`** — the layers above a ticket (milestones, projects).
- **`linear`** (linear plugin) — Linear-specific mechanics: label values, status
  flow, MCP call patterns, priority semantics. It defers to this file for the
  body and carries no template of its own.

---
name: debrief
description: Collect feedback on the attention-workflow itself from the agent that just ran a change through it, and emit it as one sanitized block that can be carried off a work machine without company data. Use after a change closes, when the workflow behaved badly mid-run, or when the user says "debrief this run", "how did the workflow do", "feedback for the maintainer", or "what should I change about the workflow".
argument-hint: "[nothing, or a specific thing that went wrong]"
allowed-tools:
  - Read
  - Bash
---

# debrief

This skill asks **you** — the agent that ran the change — what the workflow cost
and what it returned, and then emits one block of text the operator can paste
somewhere else. The report leaves the machine. The run state does not.

Two obligations, in tension, and both load-bearing:

- **Be specific enough to act on.** "The grant felt heavy" changes nothing.
- **Carry no company data.** The report is going somewhere the change's
  employer, product, and ticket must not follow.

The asymmetry that makes both possible: the *workflow* is public and the
*change* is not. Quote `SKILL.md` exactly, by section and phrase. Describe the
change only by shape.

## Refuse rather than confabulate

You may answer only about a run you actually carried. If you have neither run
state nor first-hand recollection of this change, say so in one line and stop.
A plausible debrief invented from the skill text is worse than none: it reads
like evidence and is not.

If the session compacted mid-change, say which phases you are reporting from
state and which from memory. Partial is fine. Reconstructed is not.

## Read the record before answering from memory

State outranks recollection on anything state holds. None of these commands
mutate:

```bash
python3 "$HELPER" show
python3 "$HELPER" history
python3 "$HELPER" grant-list
python3 "$HELPER" run-list
python3 "$HELPER" config-show
```

Take **counts and shapes** from them — phases traversed, transitions,
supersessions, stale runs, exceptions, fail-safe evaluations, projection
status. Take no free text from them. `title`, `promise`, `route`,
`assumptions`, `exclusions`, and every transition `reason` are the change's
content, and the change's content is exactly what must not travel.

Do not write anything under the state root. The helper is its only writer, and
this report is not state.

## What to answer

Six questions. Answer the ones the run has evidence for and say nothing on the
rest — an empty section is a finding, a padded one is noise.

1. **Where did the workflow cost attention it did not return?** The single
   message, gate, card, or field that took real thought and changed nothing
   about what happened next.
2. **Where did you have to guess?** A rule you could not apply, two rules that
   pointed different ways, or a field you filled by imitating the example
   because you did not know what it meant. Name the section.
3. **What did you do outside the workflow because the workflow was in the
   way?** Skipped a card, paraphrased one, worked around a guard, kept a note
   somewhere the state root does not reach, or stopped to ask for something the
   grant should have covered.
4. **Did the withheld verdict do work?** Was your judgment before the reveal
   different from the verifier's, and did having to commit first change what
   you concluded — or was it a formality on a run where both were obvious?
5. **Which promise could the verifier not observe?** A promise that needed
   interpretation at Verify was authored wrong at Prepare. Include whether the
   `CONTEXT.md` noun check fired, and whether it caught a real ambiguity or
   flagged a term that was fine.
6. **Where did the record go wrong?** Fail-safe, a stale run, a supersession
   that should not have been needed, an unmapped tracker state, or a phase the
   history claims you were in when you were somewhere else.

Then: **the one change you would make.** One sentence, and it must be a change
to the workflow, not to the change you just shipped.

**Report the friction, not the patch.** Do not draft `SKILL.md` edits. One run
is one data point; the maintainer holds the others, and a fix proposed from a
single run usually encodes that run's specifics into a general rule.

## Sanitize as a separate pass

Draft the report first, then read the drafted text once more as someone who
does not know where you work. This is a pass over the text, not a filter
applied while writing — the two catch different things.

**Cut:** company, product, team, repository, and service names; people other
than Jacob; file paths, branch names, hostnames, URLs; issue keys and tracker
workspace names; code, identifiers, schema and column names; error text and log
lines; commit messages; the change's title, promise, route, and domain nouns.

**Keep:** counts, phases, owners, conditions, grant and run numbers, whether
judgment and verdict agreed, coarse durations, which helper command ran, and
exact quotes from the workflow's own skill, agent, and reference files.

**Genericize instead of deleting** where the shape carries the finding: "a
domain entity", "a background job", "a schema migration", "an endpoint",
"roughly a dozen files". The maintainer needs to know a promise was hard to
falsify; they do not need to know what it was about.

**When in doubt, drop the item.** A dropped finding costs one improvement. A
leaked one is not recoverable, and this report is written to be pasted
elsewhere.

Never quote the diff, `git log`, or a tracker field. Never write the report
into the working repository or a vault; emit it in the chat and let the
operator carry it.

## Emit one block

Fenced, fixed field order, so runs compare against each other. Friction items
ranked by attention cost, capped at five.

```text
AW-DEBRIEF  plugin <version>  run <n, if known>
Shape:     <change size and kind, no subject>; phases <traversed | compressed>
Record:    grants <n> (superseded <n>) | runs <n> (stale <n>) | exceptions <n> | fail-safe <yes/no>
Tracker:   <host or none>; projections <n ok, n unmapped, n stale>
Ledger:    <armed | not armed>; capture <n atoms | nothing to capture>
Judgment:  operator <held | changed>; verifier <agreed | disagreed>

Friction
1. [<phase>] <what happened> -> <what would have helped>
2. ...

Worked around
- <or: nothing>

Would change
- <one sentence>

Source: <from state | from recollection | partial, compacted during <phase>>
```

Print it verbatim in a fenced block and add nothing after it. The operator is
going to copy this block; a closing paragraph is one more thing for them to
select around.

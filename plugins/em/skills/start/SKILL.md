---
name: start
description: >-
  Scope one ticket before any code is written: fetch it from whichever tracker
  it lives in (Linear, Fibery, GitHub Issues), ground in current decisions,
  read the touched code, ask only the questions nothing else can answer, and
  stop at a short brief. This skill should be used when the user invokes
  `/em:start`, says "start on TEAM-123", "pick up this ticket", "scope this
  ticket", "what would it take to do #42", or names a ticket and wants a plan
  before implementation. Zero questions is a normal outcome. To go straight to
  execution on a ticket that is already shaped, use `em:lead` instead.
argument-hint: "<ticket reference: key, URL, owner/repo#N, or #N>"
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
  - Skill
  - Bash(ndr *)
  - Bash(jj root)
  - Bash(git rev-parse *)
  - Bash(gh issue view *)
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_comments
---

# start

Turn a ticket reference into a brief the user can approve. Read-only: this
skill writes no code and no tracker state.

## 1. Resolve the tracker and fetch

Resolve the tracker per `../../references/config.md` (reference form, then
`.em.toml`, then ask). Read `../../references/trackers/<tracker>.md` and follow
its **Fetch** section: title, body, and every comment in full, plus the title
and state of each linked or blocking issue.

If the reference does not resolve or the tracker's tools are unavailable, say
which and stop.

## 2. Ground in current decisions

If the `ndr` plugin is installed and the repo has a `.ndr.toml`, invoke
`Skill(ndr:ground)` scoped to the ticket's area before reading code. Treat the
returned heads as ground truth, not a starting point to re-derive. Keep the
`ndr:` references for the brief. Without `ndr`, skip this step and say so in
one line.

## 3. Read the touched code

Read enough to know the actual shape of the change: the files it lands in, the
surrounding module's conventions, the related tests, and any
`.claude/rules/*.md` or nested `CLAUDE.md` that governs the area.

## 4. Decide what is actually undecided

A question is in scope only if **none** of these can answer it:

- the ticket body or its comments
- a current `ndr` head
- the repo's `CLAUDE.md` and rules
- the existing code's own precedent

If you can make the call and defend it, make it. Genuine questions are usually
one of: a product or scope tradeoff the ticket did not resolve; a choice
between two valid designs with different externally visible consequences;
anything destructive or hard to reverse; a real gap in the requirements.

## 5. Ask only what survived step 4

One `AskUserQuestion` call with the surviving questions, each with a
recommended option first. **Zero questions is a valid, expected outcome.** Do
not manufacture one to look thorough.

## 6. Write the brief

- **Files touched**, with the symbols involved.
- **Approach**, in a few bullets.
- **Sequencing**, if order matters.
- **Calls made**: each defensible default you took instead of asking, one line
  each, so the user can overrule it.
- **Done when**: the ticket's bullets, or ones you derived if it had none
  (flag them as derived).
- **Grounding**: the `ndr:` references that govern the change.

## 7. Stop

Wait for the user's go-ahead before any code is written. On go-ahead, hand the
brief to `em:lead` rather than implementing here.

**When `em:lead` runs this procedure itself** (on a ticket that was not yet
shaped), it follows steps 1 to 6 and skips this stop: `lead` has its own
escalation rule.

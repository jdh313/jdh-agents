---
name: session
description: >-
  End-of-session feedback report for plugin testers. This skill should be used
  when the user invokes `/feedback:session`, says "session feedback", "wrap up
  this test", "what worked and what didn't", "write up testing feedback", or
  otherwise signals the end of a session spent exercising Claude Code plugins
  (skills, slash commands, subagents, hooks) and wants a report to hand back to
  the plugin author. Analyzes ONLY the current session transcript, asks no
  questions, and emits a single copy-pasteable report block grading each plugin
  surface that was exercised and citing concrete evidence for every claim.
argument-hint: ""
---

# Session feedback

You are wrapping up a session in which the user was **testing Claude Code
plugins** — skills, slash commands, subagents, and hooks. Your job is to turn
the session transcript into a feedback report the user can hand back to the
plugin author so they can improve the plugins.

## Hard rules

- **Ask no questions.** Work entirely from this session's transcript. If
  something is ambiguous, say so in the report rather than asking or guessing.
- **Evidence over impression.** Every "worked" claim needs a concrete example
  from the session; every "didn't work" claim needs the actual failure (what
  the user asked, what the plugin did). No padding, no invented verdicts.
- **Honest, not flattering.** The author wants to find problems. Skip praise
  that isn't tied to a specific moment.
- **Scope to the plugins.** Judge the plugin surfaces (skills / commands /
  subagents / hooks), not the underlying model. If a plugin came from a
  different repo (e.g. the `ndr` repo vs. this one), note which when you can
  tell.
- **Output one block, then stop.** End after the report. Nothing else.

## Procedure

1. **Inventory what got exercised.** List every plugin skill, slash command,
   subagent, or hook that was invoked or triggered this session, by name. Also
   flag any that the user clearly expected to fire but didn't, or that fired
   when unwanted.

2. **Judge each surface against the transcript:**
   - *Worked:* triggered at the right time? Output correct, useful, and in the
     expected shape? Saved steps?
   - *Didn't:* misfires, wrong or confusing output, missing steps, bad
     defaults, places where the user corrected it, re-prompted, or abandoned
     it. Cite the specific moment.

3. **Capture friction, not just features.** Where did the user repeat
   themselves, clarify, or fight the tool? Where did the agent guess intent
   wrong? Anything that felt slower than doing it by hand?

4. **Assign a one-line verdict per surface:** ✅ worked / ⚠️ mixed / ❌ broke.

## Output format

Emit exactly one fenced report block the user can copy and send:

```
## Plugin testing feedback — <today's date>

**Session summary:** 2-3 sentences on what the tester was trying to do.

**Plugins/surfaces exercised:**
- <name> (<repo if known>) — <✅ / ⚠️ / ❌> one-line verdict
- ...

**What worked well:**
- <claim> — <concrete example from the session>

**What didn't:**
- <failure> — <where it happened / what was asked vs. what it did>

**Friction / rough edges:**
- ...

**Suggested fixes (optional):**
- <only where the fix is obvious from the failure; otherwise omit>
```

Keep it scannable — bullets over prose. If a section has nothing the
transcript supports, write "Nothing notable this session" rather than padding.

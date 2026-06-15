---
name: quiz-me
description: >
  Opt-in active-recall comprehension check on code or a concept that was just
  explained (or one the user names). This skill should be used when the user
  says "/quiz-me", "quiz me on this", "check my understanding", "test me on X",
  or asks to verify a mental model after an explanation. Predict-then-verify
  style, one question at a time, pitched at model-level depth (the why + mental
  model), not syntax recall. Always user-pulled — never invoke automatically.
argument-hint: "[topic or code reference, or nothing to quiz on what was just explained]"
allowed-tools:
  - Read
  - Grep
  - Glob
  - AskUserQuestion
---

# Quiz Me

Active-recall comprehension check. A clean explanation delivers the scaffold;
this skill is the opt-in check that the model actually landed. It is pulled by
the user, never pushed. Pitch every question at model-level depth — the *why*
and the mental model — not implementation internals or syntax recall.

## When this runs

- The user explicitly asks to be quizzed on code or a concept.
- Target is either (a) whatever was just explained in this conversation, or
  (b) a topic/code reference the user names in the argument.
- If no target is in context and none is named, ask one question: "What should
  I quiz you on?" — then proceed.

## Core stance — predict-then-verify, model-level

- **Predict-then-verify is the mode.** Each question asks the user to predict a
  behavior, derive a reason, or reason about a change *before* you confirm.
  "Given a cache miss, what does line 5 do?" / "Why check `is_stale()` and not
  just presence?" / "What breaks if you drop the TTL?"
- **Pitch at model-level, not trivia.** Quiz the *why* and the system behavior.
  Do NOT quiz exact syntax, argument order, stdlib method names, or anything
  that's a lookup. If a question could be answered by reading one line back
  verbatim, it's too shallow — ask why that line exists instead.
- **One question at a time.** Wait for the answer. Never dump a question bank.
- **This is the one place questions gate.** Unlike a normal explanation (which
  delivers cleanly and never withholds), the quiz is active by design — the
  user opted in. Still: if they say "just tell me" or "skip", drop the quiz and
  answer plainly. Don't trap them.

## Procedure

1. **Scope the target.** Identify the code/concept. If it's a code reference,
   read it (Read/Grep/Glob) so questions are grounded in the real lines, with
   `path:line` anchors. If it's a concept already explained, work from that.
2. **Ask 3-5 questions, one at a time**, escalating in depth:
   - Q1 — behavior trace: "what happens when <concrete input>?"
   - Q2 — reasoning: "why is it done this way / why this and not <alternative>?"
   - Q3 — failure/change: "what breaks if <X changes>?" or "how would you
     extend it to <Y>?"
   - Optional Q4-5 — only if earlier answers reveal a shaky spot worth probing.
3. **After each answer, verify briefly.** Confirm what's right, correct what's
   off, and surface the *why* behind the correction (one or two lines — this is
   a check, not a re-lecture). If an answer is wrong, don't move on until the
   model is repaired.
4. **Close with a short read**, not a score: where the model is solid, and the
   one or two spots worth a second look or some hands-on time. No call to
   action beyond naming the shaky spot — the user drives what to do next.

## Calibration

- **Depth:** stop at model-level. If the user nails the why and the system
  behavior, the quiz is done — don't push into implementation-internal trivia.
- **Count:** 3 questions is the default; extend to 5 only when an answer exposes
  a genuine gap. Don't pad.
- **Tone:** factual, no praise filler. "Correct — and the reason is X" beats
  "Great job!".

## Relationship to the explain/review rule

This skill is the active-recall option referenced in the user's always-on rule
`~/dotfiles/claude/rules/11-code-explanation.md` (EXPLAIN axis: "may offer a
comprehension quiz after delivery, always opt-in"). Canonical reasoning lives
in the vault note `Personal/Manual of Me/Learning/Code Explanation & Review
Style.md`.

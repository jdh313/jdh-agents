---
name: first-principles
description: Figure out what the user actually needs or wants — grounded in how they've actually behaved — before any solution research or purchase evaluation. This skill should be used when the user wants to solve a recurring workflow problem ("what should I use for X", "help me organize Y", "let's figure out what I need"), when a prior tool evaluation stalled or feels anchored and they want to restart from requirements ("start from first principles"), or when a want-shaped pull (gear, tool, purchase, acquisition) needs grounding before researching options ("what do I actually want from a Z"). Runs an evidence-first interview (one question at a time) with two evidence modes — friction incidents for problems, behavioral history + trigger provenance for wants — produces a signed-off needs map (must-solve gates / nice-to-haves / explicitly-not-needed), and locks it to a vault note. Hands off to `solution-research` for the research prompt. NOT for clarifying feelings or stance (use `reflect`) or getting a recommendation (use `debate:debate`).
---

# First Principles

Work out what the user actually needs or wants — from evidence of real behavior, not aspirations — before any solution research happens. Requirements are **gates derived from evidence**, never feature wishlists, and nothing option-shaped (tools, products, candidates) enters the conversation until the needs map is signed off and locked.

## Why this exists

Option-first evaluations stall: candidates get compared on features, the matrix grows, no decision lands, and the framing itself (e.g. "inventory tool") is often wrong. Want-shaped pulls have the same failure with a different face: justifications get built after the desire, and research validates the pull instead of testing it. The counter-process is the same for both: interview for evidence → distill needs with hard gates → lock the map → only then research (via `solution-research`), with the map as the gate-check.

## Routing — this skill vs. its neighbors

The boundary is **commitment**: this skill assumes the user is (or is presumed) going to evaluate options, and answers *what must the answer be*. Route away when the question is different:

| The user's real question | Route to |
|---|---|
| "What must it do / what do I actually need from X?" | this skill |
| "Do I even want X / how do I feel about X?" | `reflect` (clarify stance; never confronts with evidence) |
| "Think this through with me, push back" | `mull` |
| "Which one should I pick?" (recommendation wanted) | `debate:debate` — though running this skill first gives the debate its criteria |
| "I want to save for X" (decision already made) | `librarian:savings-goal-add` |

**Empty-map handoff:** when the interview finds no incidents and no behavioral basis — a purely externally-triggered pull — the honest output is "the map is empty; the question is *whether*, not *what*." Say so and hand off to `reflect` rather than forcing a map.

## Evidence modes

Detect the mode from the opening framing; the spine (one question at a time, evidence over aspiration, map → sign-off → lock) is identical.

- **Problem-shaped** ("organize my X", "fix my Y workflow") — evidence is friction incidents: recent breakdowns, where things are tracked today, capture/loss points, upkeep history of systems that survived vs. died, scale, solo vs. shared.
- **Want-shaped** ("what do I want from a Z", a gear/purchase pull) — evidence is behavioral history: what analogous things were actually used/carried/sustained and what killed the ones that weren't; trigger provenance (internal felt-need vs. saw-it-somewhere); what existing owned thing already covers the role; concrete moments of reaching for the thing and not having it.

Both modes' probe sequences, question shapes, and the aspirational-answer detection table live in `references/interview-guide.md`.

## Phases

Run the phases in order. If invoked mid-process (e.g. a signed-off needs map already exists in the vault), confirm which phase to resume from and skip ahead.

### Phase 1 — Evidence interview

Interview the user following `references/interview-guide.md`. Non-negotiables:

- **Anchoring guard first.** Do not search the vault for prior option research, name candidate tools/products, or propose solutions until the needs map is signed off. If prior evaluations exist, acknowledge they exist and defer them explicitly.
- **One question at a time.** Narrow and specific ("walk me through the last time X broke down", "what happened to the last analogous thing you bought") over wide-open ("what are your requirements?").
- **Evidence over aspirations.** Every claimed need must trace to something that actually happened. When the user speaks in "I would use..." voice, surface the gap and ask for the evidence.

### Phase 2 — Needs map + sign-off

Distill the interview into a prioritized needs map presented in chat:

- **Must-solve** — gates. Each traces to evidence. Include constraint-shaped gates (e.g. "event-shaped upkeep only", "must fit the existing carry habit"), not just feature-shaped ones.
- **Nice-to-have** — tiebreakers. Mark speculative items ("no evidence behind it") as such.
- **Explicitly not needed** — exclusions with the evidence ("counting never survived", "already owned by <existing thing>").
- Name the **core insight** if the interview reframed the problem (e.g. "this is a capture-and-recall problem, not an inventory problem"; "this is a carry-friction question, not an image-quality question"). A wrong frame is often why prior evaluations stalled.

Iterate on pushback — examine each challenged bullet individually; user pushback usually sharpens a constraint rather than deleting it. Get explicit sign-off before Phase 3.

### Phase 3 — Lock the map to a vault note

Write the signed-off map to the vault (folder per the vault Location Decision Tree; `owner: ai` frontmatter). The note must contain: the evidence section (incidents or behavioral history, including sustained-use evidence and scale), the core insight, the three priority tiers verbatim as signed off, and a next-step line stating that research is evaluated against this map. Provide the Obsidian URI. This note is the single source of truth downstream — research prompts reference it rather than restating it.

### Next step — research

When the user is ready to evaluate options, invoke `solution-research` with the locked needs map note. It generates the systems-first parallel-research handoff prompt (real-evidence test scenarios, anchoring guard, adversarial verification, composition-aware synthesis).

## Composes with

- `solution-research` — downstream; consumes the locked needs map to generate the research handoff.
- `reflect` — upstream or via empty-map handoff, when the real question is *whether*, not *what*.
- `mull` — upstream, when the user is not yet sure the problem is worth solving.
- `debate:debate` — downstream, when the post-research shortlist needs a recommendation; the map supplies the criteria.
- `librarian:savings-goal-add` — downstream for want-mode, once the map confirms a purchase worth funding.
- `librarian:catalog-evaluate` — further downstream, once research lands on a decision worth cataloging.

# Evidence Interview Guide

Discipline for Phase 1 of `first-principles`. The goal is a needs map grounded in what actually happened, not what the user imagines wanting. Validated in problem mode on the 2026-06 3D-printing organization session, where the interview reframed an "inventory tool" problem into a capture-and-recall problem. Want mode generalizes the same discipline to gear/purchase/acquisition pulls.

## Ground rules (both modes)

- **One question per message.** Build on the previous answer; never batch decision points.
- **Narrow beats wide.** "Walk me through the last time you couldn't find a part" beats "what are your requirements?" Wide-open framings drain the user; specific grounding questions land.
- **Anchoring guard.** No vault searches for prior option research, no candidate tool/product names, no solution proposals until the map is signed off. Naming an option mid-interview contaminates every answer after it.
- **Reflect before advancing.** Open each question with a one-to-two-sentence synthesis of what the last answer established ("So the loss happens at capture, not retrieval...") so the user can correct the model of the problem as it forms.

## Mode A — Problem-shaped probe sequence

For "organize my X" / "fix my Y workflow" framings. Adapt order to the conversation, but cover all six.

### A1. Breakdown incidents (open with this)

"Describe the last project/time where <the activity>'s organization or planning broke down. What were you making, and what specifically went wrong?"

Collect 2–4 distinct incidents. For each, push past the summary to the mechanism: what was lost, at what moment, and what the user did instead.

### A2. What is tracked today, and where

For each incident: "Where did that list/plan/queue live? Is there a written anything, or is it re-derived from looking at the physical state each time?" Expect "in my head" — confirm it explicitly rather than assuming.

### A3. Capture/loss points

Find the exact moment information dies: "When you first notice the need — where are you standing, what is in your hands — what happens in that moment?" Distinguish capture failures (never written down) from retrieval failures (written down but not found). They imply different gates.

### A4. Upkeep tolerance (evidence-based, decides everything)

Ask for the honest history, not the intention: "What is the most upkeep you have ever *sustained* for a tracking system, and what happened to the ones that asked for more?"

- Mine the survivors for the pattern. Common one: a system survives when manual touches happen only at rare, deliberate moments (entering a purchase) and recurring updates are automated; per-item bookkeeping dies.
- Encode the survivor pattern as a **constraint-shaped gate** ("event-shaped upkeep only, never count-shaped"), not a preference.
- Expect pushback on absolutes like "zero upkeep" — the user is usually refining, not rejecting. The refined form: manual work is acceptable when it is transactional (one event decrements a whole BOM) or an occasional reconciliation audit, and when the tradeoff test passes: does this regular bit of manual work prevent a larger pile of manual work or project abandonment later?

### A5. Scale

"Right now, how many <projects/intentions/items> are actually in flight? Name them." Counting concrete items beats asking for an estimate. The answer calibrates solution weight: ~10 in mixed states means an in-head queue mathematically fails but industrial tooling is overkill.

### A6. Solo vs. shared

"Is this all solo, or does anyone else need to see or add to it?" Mark shared-access answers without incidents behind them as speculative nice-to-haves.

## Mode B — Want-shaped probe sequence

For "what do I want from a Z" / gear/purchase/acquisition framings. Same spine; the evidence is behavioral history instead of friction incidents.

### B1. Trigger provenance (open with this)

"When did you first feel this want — what were you doing? Did it start from a moment of reaching for the thing and not having it, or from seeing it somewhere (video, post, someone else's)?"

Externally-triggered pulls with justifications built afterward are the want-mode equivalent of an aspirational answer. Provenance doesn't kill the want, but it sets the evidence bar: a saw-it-somewhere want must earn its gates from B2–B4, or the map comes up empty.

### B2. Behavioral history with analogous things

"What's the closest thing to this you've owned or done before — and what actually happened? How often was it used/carried in month one vs. month six? What killed the ones that lapsed?"

Mine the failures for the recurring killer (carry friction, setup friction, maintenance burden) and encode it as a constraint-shaped gate ("must fit the existing carry habit"), exactly like the upkeep-survivor pattern in A4. A validated failure mode outranks any spec.

### B3. Existing coverage

"What do you currently use when this need comes up? Walk me through the last time — what did you reach for, and where did it actually fall short?" If nothing currently falls short in lived moments, that absence is itself evidence — record it and lower the want's standing.

### B4. Concrete unmet moments

"Name the last 2–3 specific times you needed this and didn't have it. What did each cost you?" These moments become the test scenarios for `solution-research`, same as problem-mode incidents. Vague answers ("it'd be nice for trips") without a nameable moment mark the need speculative.

### B5. Sustain conditions

"For this to still be in use six months from now, what would have to be true — given how the analogous things actually went?" Forces the survivor pattern from B2 into explicit gate form.

## Aspirational-answer detection (both modes)

The interview's main hazard. Signals and counters:

| Signal | Counter |
|---|---|
| "I would use...", "I'm not opposed to...", "I think I could..." | "Based on how you've actually behaved with past systems/things — not how you'd like to behave — what happened?" |
| Vague frequency ("at different times, probably not as often") | Rank the need below evidence-backed ones and say so explicitly. |
| Willingness to adopt heavyweight process or gear | Check it against the behavioral history; if history contradicts it, encode history as the gate and surface the contradiction gently. |
| Stated preference framed as need ("I prefer systems over plain text") | Record as a preference/criterion, not a gate, unless evidence backs it. |
| Identity-aspiration framing ("I want to be the kind of person who...") | Surface the gap; the map gates on behavior, not identity. If the want survives only as identity, route to `reflect`. |

When the user pushes back on a distillation, examine each challenged bullet individually — pushback usually sharpens a constraint (e.g. "zero upkeep" → "event-shaped upkeep") rather than deleting it.

## Distillation rules (Phase 2 input)

- Look for incidents/moments that share a root cause and say so — two "different" problems collapsing into one (e.g. both queues live in-head) is the typical shape of the core insight.
- Distinguish need-shapes that look alike: "what do I have in stock" (inventory) vs. "how many does this project require" (BOM/requirement math) vs. "what was I going to make" (capture/queue). The user's own first framing is frequently the wrong one.
- Existing working systems/things (the survivors from A4/B2/B3) become exclusions: integrate with them, never duplicate them.
- User capabilities are selection criteria too: if the user demonstrably builds automations (homelab, LLM assistants, APIs), "programmable surface (API/MCP/CLI)" is an evidence-backed gate, not gold-plating.
- **Empty map:** if no gate survives the evidence bar, say so plainly — the question was *whether*, not *what* — and hand off to `reflect` per the routing table in SKILL.md.

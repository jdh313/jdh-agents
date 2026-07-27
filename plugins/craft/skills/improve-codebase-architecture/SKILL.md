---
name: improve-codebase-architecture
description: Find deepening opportunities in a codebase, informed by the domain language in CONTEXT.md and the decisions surfaced via NDR atoms. Use when the user wants to improve architecture, find refactoring opportunities, consolidate tightly-coupled modules, or make a codebase more testable and AI-navigable. Adapted from mattpocock/skills (MIT, © 2026 Matt Pocock).
effort: high
upstream:
  repo: mattpocock/skills
  path: skills/engineering/improve-codebase-architecture
  reviewed_sha: 697d4ce9742d
  reviewed: 2026-07-27
  status: reviewed
allowed-tools:
  - Read
  - Grep
  - Glob
  - Agent
  - Write
  - Skill
---

Apply the orchestration mappings in [`../../RUNTIME.md`](../../RUNTIME.md).

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

## Architecture vocabulary

Run `Skill(craft:codebase-design)` for the architecture vocabulary — **module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality** — and its principles: the deletion test, "the interface is the test surface," "one adapter = hypothetical seam, two = real." Use these terms exactly in every suggestion — don't drift into "component," "service," "API," or "boundary."

This skill is _informed_ by the project's domain model. The domain language gives names to good seams; NDR atoms record decisions this skill should not re-litigate.

## Process

### 1. Explore

**Scope before you scan — YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction — a module, a subsystem, a pain point — take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots — the files and areas that keep coming up — and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.

Invoke `/ground` to surface relevant NDR atoms in the area you're touching first. Read the project's domain glossary (CONTEXT.md) alongside the grounded decisions.

Then spawn an isolated exploration subagent named `arch-explorer` to walk the codebase. Give it a bounded task, inputs, deliverable, and done criteria; keep it addressable during the grilling loop for follow-up questions. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates as a markdown report

Write the review to `<repo>/.docs/architecture-review-<timestamp>.md` so nothing lands in the tracked source tree. The `.docs/` directory is gitignored scratch space — each run gets a fresh file named with a timestamp. After writing, open the file with `open <path>` (macOS) and tell the user the absolute path.

The report uses **Mermaid fenced code blocks** for diagrams where a graph, flow, or sequence reliably communicates the structure. These render natively in GitHub, Obsidian, VS Code, and most modern markdown viewers — no CDN needed. For structural shapes that Mermaid's layout fights (mass diagrams, cross-sections), describe them textually or with ASCII art. Each candidate gets a **before/after diagram**. Be visual — the diagrams carry the weight.

For each candidate, rendered as a markdown section (`### Candidate N: <title>`):

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and how tests would improve
- **Before / After diagram** — side by side using Mermaid fences or ASCII; illustrating the shallowness and the deepening
- **Recommendation strength** — `**Strength:** Strong | Worth exploring | Speculative`

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use CONTEXT.md vocabulary for the domain, and the `codebase-design` skill's vocabulary for the architecture.** If `CONTEXT.md` defines "Order," talk about "the Order intake module" — not "the FooBarHandler," and not "the Order service."

**NDR conflicts**: if a candidate contradicts an existing NDR atom, only surface it when the friction is real enough to warrant revisiting the decision. Mark it clearly in the candidate section (e.g. a note callout: _"contradicts ndr:area/topic/NNNN-slug — but worth reopening because…"_). Don't list every theoretical refactor a decision forbids.

See [MARKDOWN-REPORT.md](MARKDOWN-REPORT.md) for the full report scaffold, diagram patterns, and prose guidance.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, run `Skill(craft:grill)` to walk the decision tree with them. Scope it to this candidate: constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive. Keep `arch-explorer` addressable throughout — route factual questions about the codebase to it rather than to the user.

Side effects happen inline as decisions crystallize:

- **Domain model needs updating** — a deepened module named after a concept not in `CONTEXT.md`, a fuzzy term getting sharpened, or a rejected candidate carrying a load-bearing reason worth recording? Run `Skill(craft:domain-modeling)` to keep the domain model current. It already encodes the NDR capture-decision routing (hard-to-reverse / surprising-without-context / real-trade-off) — don't re-specify decision handling here.
- **Want to explore alternative interfaces for the deepened module?** Run `Skill(craft:codebase-design)` and use its design-it-twice parallel sub-agent pattern.

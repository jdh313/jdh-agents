# Systems-First Research Handoff — Template & Design Rules

Reference for `solution-research` — consumes a needs map locked by `first-principles`. Produces a prompt the user pastes into a fresh session; that session dispatches parallel research subagents and synthesizes a shortlist. The prompt below is the validated shape (2026-06 3D-printing organization session) — adapt the bracketed parts, keep every load-bearing property.

## Design rules (why each part exists)

| Property | Failure it prevents |
|---|---|
| Systems as the unit of evaluation; tools fill **roles** | Tool-by-tool comparison matrices that never converge; great components eliminated for missing one feature |
| Role gaps reported with integration cost, not disqualified | Losing a strong backbone because one layer needs DIY glue |
| Real-incident test scenarios, walked end-to-end | Gate verdicts earned by reading marketing feature lists |
| Anchoring guard (no prior notes, no tool names in subagent prompts) | Re-converging on a stalled prior evaluation |
| Primary-source citation or "unverified" | Plausible-but-wrong claims ("has an API") surviving to synthesis |
| Adversarial verification attacking the **seams** | Multi-tool systems failing exactly where tool A meets tool B |
| Composition-aware synthesis | Missing the hybrid that recombines parts of two lanes |
| A community-practice lane | Tool-centric lanes missing how practitioners actually wire things together |

## Assembly checklist

1. Derive **system roles** from the needs map's must-solves (each gate usually implies a role; existing surviving tools become an "integrate, don't duplicate" role).
2. Convert the map's evidence incidents into 2–4 **test scenarios** (S1, S2, ...), each with concrete physical detail (where the user is standing, counts, color) and an explicit pass/fail tripwire line.
3. Pick 4–6 **lanes**, each producing ONE system around a different backbone class; always include an LLM-native/DIY lane if the user has the capability, and a community-practice lane.
4. Name the **search MCP** subagents must use, spelling out the exact tool identifier and, on runtimes where MCP tools load on demand, the loading step that precedes the first call (a deferred tool fails if called before its schema is loaded). Pick whichever web-search MCP the target session has connected — Kagi's search-and-fetch tool is the usual choice here. Look the identifier up in the session's own tool list rather than copying one from this document; server-side renames are silent.
5. Name the prior research artifacts to NOT open (titles only, no content).
6. End with synthesis instructions including the user's interaction preferences (e.g. discuss in chat before any vault write; one question at a time; concrete recommendation over option matrix).

## Template

````markdown
You are picking up work on [user]'s [problem] project at [CWD].

## Goal
Research candidate **systems** that solve [problem] — where a system is an end-to-end architecture ([role chain, e.g. capture → store/queue → retrieval → automation glue]) and tools are assigned to roles within it. The unit of evaluation is the system, never an individual tool.

## Where things stand
A needs-mapping session just concluded. The requirements are locked in a vault note — [N] must-solve gates ([list them briefly]), [N] nice-to-haves, [N] exclusions. Research starts fresh from here.

## Read these first
- `[path to needs map note]` — the requirements AND the evidence section. Must-solves are gates; nice-to-haves are tiebreakers. Read in full before dispatching anything.

## Anchoring guard
Do NOT open `[[prior comparison note]]` or any prior tool-comparison/catalog notes in the vault. A previous evaluation exists and [user] explicitly wants independent research that isn't anchored to it. Subagent prompts must not mention any candidate tool names you happen to know — let each subagent discover its own.

## System roles (derive from the needs map; paste into every subagent prompt)
- **[Role]** — [one-line requirement from the map]
- ...
- **Existing stack** — [surviving tools] must be consumed, not duplicated

## Test scenarios (paste into every subagent prompt)
A system passes a gate only by walking these real incidents end-to-end:
- **S1 — [name]:** [concrete incident walkthrough demand, with physical detail and what "show" means]
- **S2 — [name]:** ...
[Explicit tripwire line, e.g. "A candidate requiring per-item counts fails S3's upkeep constraint."]

## Next concrete action
Dispatch parallel research subagents (one message, multiple Agent calls), each designing/discovering ONE system in its lane — backbone choice, tools filling each role, and the scenario walkthroughs. Suggested lanes — adjust as you see fit:
1. System built around [dedicated domain tool class] as the backbone
2. System built around [general platform class] as the backbone
3. [further backbone classes]
4. LLM-native system — datastore + custom MCP server as the backbone, given [user]'s [capability evidence]
5. Community-practice systems — how [practitioners] with similar pain actually wire things together (forums, Reddit, build logs)

## Subagent instructions (include in each prompt)
- Use the [search MCP] for all web research: load it first via `ToolSearch("select:[tool name]")`, then search with it. Do not use other search tools.
- Design the best system your lane supports: name the backbone, assign a real tool (or explicit DIY component) to every role, and walk the scenarios end-to-end. Gates apply to the system as a whole.
- A role with no good tool is reported as a gap with the integration work needed to fill it — not papered over.
- Every load-bearing tool claim ([the claims that matter for the gates]) must cite a primary source (official docs, repo, API reference). No citation → mark "unverified."
- Return structured findings: system name/sketch, role→tool table with citations, gate-by-gate verdict for the system, scenario walkthroughs, integration/setup work required, upkeep profile (what's manual, what's automated), maintenance health of each tool.

## Verification pass (before synthesis)
For each provisionally viable system, dispatch one adversarial subagent prompted to REFUTE it: re-check primary docs (via [search MCP]) on every load-bearing tool claim, and attack the seams — does [layer A] actually talk to [layer B]? Is the "API" read-only or paywalled? Is the glue work a weekend or a month? A system that survives refutation is confirmed; one that doesn't is downgraded or eliminated with the failing seam named.

## Synthesis
Compare verified systems (2–4 finalists), gate-checked and tiebreaker-scored, including each system's total integration cost and upkeep profile. Tools shared across systems should be called out — they may recombine into a better hybrid than any single lane produced. Present in chat for discussion first — ask before writing any vault note. [User interaction preferences.]
````

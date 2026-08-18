# debate

> **Requires an Obsidian vault.** Skills in this plugin read and write notes in an
> Obsidian vault, defaulting to `~/Loose Ends/`. That default is an example, not a
> requirement — point it at your own vault by editing the paths in the skill bodies
> (search for `Loose Ends`). Without a vault, the vault-writing skills will not work.

Dialectical decision analysis. Instead of giving a single opinion, dispatch
parallel advocate agents to research opposing perspectives, optionally verify
claims and challenge the consensus, and synthesize an opinionated verdict
grounded in evidence.

## When to invoke

- User asks for an opinion on a decision
- Trigger phrases: "should I", "is it worth", "would you recommend", "X vs Y"
- Not for: factual questions, simple preferences, single-answer lookups

## Skill

| Skill | Purpose |
|---|---|
| `debate` | Orchestrates the pipeline: frames the question, dispatches advocates, optionally runs fact-check + devil's advocate + synthesis |

## Agents

| Agent | Role |
|---|---|
| `advocate` | Builds evidence-backed case for an assigned position; web search for sources |
| `fact-checker` | Verifies advocate claims, validates source-quality ratings (1–5), flags logical fallacies |
| `devils-advocate` | Attacks the emerging consensus, surfaces hidden assumptions, maps failure scenarios |
| `synthesizer` | Produces the final independent verdict from all advocate/fact-checker/devil's-advocate outputs |

## Modes

| Mode | Pipeline | Best for |
|---|---|---|
| **Quick** | Advocates only | Low-stakes, reversible decisions |
| **Standard** | Advocates → Fact-checker | Medium-stakes, some evidence concern |
| **Deep** | Advocates R1 → Fact-checker → Advocates R2 → Devil's advocate → Synthesizer | High-stakes, irreversible decisions |

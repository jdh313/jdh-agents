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

## Codex optional agent bundle

Install Debate from the Codex marketplace, then explicitly invoke
`$debate:setup-codex-agents` to register its optional roles for either user or
project scope. The setup skill finds its installed helper from the active
`SKILL.md` path, so it does not depend on a guessed cache version or plugin
path. Run its selected-scope `check` action after setup; open a fresh Codex
session and check the same scope before using an exact registered role such as
`debate:synthesizer` with `agent_type`.

For the JUN-444 local acceptance run, set `AGENTFORGE_BIN` to the absolute path
of the verified unreleased AgentForge binary before starting Codex. The consumer
fixture contains neither Bun nor an AgentForge checkout. This is an unreleased
local-build procedure, not a public-release acceptance claim. The generated
setup helper verifies each lifecycle command through that absolute binary.

The bundle's registered synthesizer declares `gpt-5.6-terra` and high effort.
The devil's advocate keeps canonical high effort while inheriting its model;
advocate and fact-checker inherit both settings. These are Codex settings
chosen for the role itself; they are not translations of the Claude `sonnet` or
`opus` aliases. Confirm applied values from runtime metadata and record
unavailable settings as unknown.

The bundled Markdown role procedures remain usable as explicit generic-child
instructions. That route does not register a Codex role and must not pass an
`agent_type`.

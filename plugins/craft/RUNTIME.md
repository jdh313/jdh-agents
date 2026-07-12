# Runtime mappings

Craft skill bodies are canonical across agent runtimes. Interpret orchestration
terms by capability:

| Capability | Claude Code | Codex |
|---|---|---|
| Invoke another skill | `Skill(plugin:skill)` | Invoke the installed namespaced skill, or follow its `SKILL.md` directly when already composing inside the plugin |
| Independent exploration | `Agent` tool | Spawn an isolated subagent with a bounded task, inputs, deliverable, and done criteria |
| Follow up with an explorer | `SendMessage` | Send a message or follow-up task to the spawned subagent |
| Ask for adjudication | `AskUserQuestion` | Use structured user input when available; otherwise ask one concise question and wait |
| Track a multi-phase workflow | `TodoWrite` | Use the runtime plan/checklist tool and update status incrementally |

Use connected apps or MCP servers for private workspace data. Do not substitute
web search or model memory. Repository conventions come from the active
runtime's native guidance; in Codex, applicable `AGENTS.md` files take
precedence and non-conflicting `CLAUDE.md` facts are supporting documentation.

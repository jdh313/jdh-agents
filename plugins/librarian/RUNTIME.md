# Runtime mappings

Librarian skill bodies and role procedures are canonical across agent runtimes.
Interpret orchestration terms by capability while preserving the boundary:
skills gather intent and draft with the user; isolated roles perform vault I/O.

| Intent | Claude Code | Codex |
|---|---|---|
| `@vault-reader` | Registered agent | Spawn a read-only subagent using `agents/vault-reader.md` as its procedure |
| `@note-editor` | Registered agent | Spawn a one-shot write subagent using `agents/note-editor.md` after approval |
| `@vault-curator` | Registered persistent agent | Spawn one curator subagent using `agents/vault-curator.md`; reuse it for the cleanup session |
| `@vault-inspector` | Registered agent | Spawn a read-only diagnostic subagent using `agents/vault-inspector.md` |
| `SendMessage` | Re-engage agent by id | Send a message or follow-up task to the same spawned subagent |
| `context: fork` | Cold isolated agent context | One-shot isolated subagent with the named role procedure |
| `general-purpose` subagent | Agent tool | Bounded isolated subagent with explicit inputs, deliverable, and done criteria |
| `Skill(name)` | Claude skill dispatch | Invoke `librarian:name` or follow its installed `SKILL.md` directly |
| `AskUserQuestion` | Structured prompt | Structured user input when available; otherwise ask one concise question |

`${CLAUDE_PLUGIN_ROOT}` means the installed Librarian plugin root. Prefer
relative links from a skill or role procedure when reading plugin references.

Vault markdown access uses `obsidian-cli` as the primary interface. Claude MCP
names such as `mcp__obsidian-mcp__patch_note`, `read_multiple_notes`, and
`search_notes` mean the equivalent connected Codex Obsidian operation when one
is available. If it is not, use the documented `obsidian-cli` operation or the
runtime file-edit capability only when the role procedure permits it and vault
filesystem access is approved.

Never replace private vault reads with web search or model memory. Web research
is valid only for workflows that explicitly research public sources. Preserve
read-only roles, approval gates, the note-editor write boundary, and the same
subagent identity across persistent reader or curator follow-ups.

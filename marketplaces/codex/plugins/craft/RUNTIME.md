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

## Codex optional registered review roles

The shared Markdown procedures in `agents/` are not Codex registrations on
their own. A Craft installation can opt into an agent bundle that registers
exactly these roles in one selected scope:

- `craft:house-style-reviewer`
- `craft:comment-reviewer`
- `craft:copy-reviewer`

Explicitly invoke `$craft:setup-codex-agents` to install or update that bundle.
Its active installed `SKILL.md` finds the installed lifecycle helper; do not
guess a Codex cache path or reuse the source checkout. For a later selected-
scope check, derive the same installed root from the active Craft skill path:

```sh
skill_file='<absolute path of the active installed Craft SKILL.md>'
case "$skill_file" in /*) ;; *) exit 1 ;; esac
plugin_root="$(cd -- "$(dirname -- "$(dirname -- "$(dirname -- "$skill_file")")")" && pwd -P)"
helper="$plugin_root/skills/setup-codex-agents/scripts/manage-codex-agent-bundle.sh"
test -f "$plugin_root/.agentforge/codex-agent-bundle/agentforge-codex-agent-bundle.json"
compiler_bin='<absolute path of the verified released AgentForge binary>'
case "$compiler_bin" in /*) ;; *) exit 1 ;; esac
test -x "$compiler_bin"
AGENTFORGE_BIN="$compiler_bin"
"$AGENTFORGE_BIN" --version
```

`AGENTFORGE_BIN` must name the absolute, verified released compiler binary.
Consumer registration and checks do not require Bun or an AgentForge checkout.
Ordinary consumer setup uses its selected Codex scope normally; the explicit
isolation rules below are lifecycle-acceptance requirements.
For lifecycle acceptance, every command explicitly sets an isolated absolute
`CODEX_HOME` and validates it before use. A project-scope command also resolves
the disposable trusted project to a canonical absolute path and passes that
path to the helper, including the check; never run a bare user-scope cleanup.

```sh
isolated_codex_home='<absolute intended isolated CODEX_HOME>'
case "$isolated_codex_home" in /*) ;; *) exit 1 ;; esac
test -d "$isolated_codex_home"
test "$(cd -- "$isolated_codex_home" && pwd -P)" = "$isolated_codex_home"
export CODEX_HOME="$isolated_codex_home"
test "$CODEX_HOME" = "$isolated_codex_home"

project_arg='<absolute intended disposable trusted project>'
case "$project_arg" in /*) ;; *) exit 1 ;; esac
project_root="$(cd -- "$project_arg" && pwd -P)"
test -d "$project_root"
test "$project_root" = "$project_arg"
selected_scope='<user or project>'
case "$selected_scope" in
  user)
    AGENTFORGE_BIN="$AGENTFORGE_BIN" CODEX_HOME="$isolated_codex_home" sh "$helper" check user
    ;;
  project)
    AGENTFORGE_BIN="$AGENTFORGE_BIN" CODEX_HOME="$isolated_codex_home" sh "$helper" check project "$project_root"
    ;;
  *) exit 64 ;;
esac
```

In a fresh Codex session, run the selected-scope `check` immediately before
every exact registered-role dispatch. A current successful check permits only
the matching exact `agent_type` above; a failed or stale check blocks native
dispatch. Do not set a dispatch model or effort. Craft has no justified Codex
model or effort pin: the roles inherit runtime settings, independently of their
Claude `sonnet` aliases. Capture applied values from runtime metadata and mark
unobservable values `unknown`.

For a same-agent follow-up, retain and use the runtime's actual continuation
handle only when it shows that the original role resumed. If that is unavailable
or continuity is unknown, run a new selected-scope check and use a fresh exact
registered dispatch; report that continuity was lost or unknown and never call
the result a same-agent follow-up. A caller may also check immediately before
the follow-up to make the registration evidence explicit.

The Markdown-procedure route remains separate and requires the user's explicit
choice: give a generic bounded child the matching **installed** Markdown body,
omit `agent_type`, and do not claim a registration. An inline literal
procedure is likewise a separately chosen fallback. Generic exploration labels
such as `arch-explorer`, `grok-explorer`, and `model-cartographer` remain
generic labels; they are not Craft registered role types.

Codex strips the Claude tool filters on the three reviewers. Their advisory,
read-only, no-external-action rules remain in their procedures but are not a
mechanical Codex policy. Preserve Claude's model aliases and tool filters in
canonical frontmatter; do not translate them into Codex sandbox policy.

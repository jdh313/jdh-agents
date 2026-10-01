# Runtime mappings

Librarian skill bodies and role procedures are canonical across agent
runtimes. Preserve the Claude routes named in each skill. On Codex, use the
corresponding capability rather than treating a packaged Markdown file as a
role registration.

| Capability | Claude Code | Codex |
|---|---|---|
| Named vault role | Native `@vault-reader` / `@note-editor` / `@vault-curator` / `@vault-inspector` | Exact registered `agent_type`, only after the current selected-scope check below |
| Same-role follow-up | `SendMessage` to the returned agent ID | Follow up only with a runtime handle that proves the same role resumed; otherwise use a fresh checked exact dispatch and record continuity as unknown |
| No registered role | Existing Claude dispatch | User-selected generic child with the installed Markdown procedure, no `agent_type` |
| Plugin references | `${CLAUDE_PLUGIN_ROOT}` | Canonical installed plugin root passed in `## Runtime context` |

## Codex optional registered vault roles

The four Markdown files under `agents/` remain procedures. They do not register
Codex roles by themselves. Explicitly invoke `$librarian:setup-codex-agents`
to install or update one selected scope. It registers exactly:

- `librarian:vault-reader`
- `librarian:note-editor`
- `librarian:vault-curator`
- `librarian:vault-inspector`

The active installed setup skill locates its lifecycle helper. Do not guess a
Codex cache path or reuse the authoring checkout. For later checks, derive the
active installed plugin root from the active Librarian `SKILL.md` path:

```sh
skill_file='<absolute path of the active installed Librarian SKILL.md>'
case "$skill_file" in /*) ;; *) exit 1 ;; esac
plugin_root="$(cd -- "$(dirname -- "$(dirname -- "$(dirname -- "$skill_file")")")" && pwd -P)"
runtime_file="$plugin_root/RUNTIME.md"
helper="$plugin_root/skills/setup-codex-agents/scripts/manage-codex-agent-bundle.sh"
test -f "$runtime_file"
test -f "$plugin_root/.agentforge/codex-agent-bundle/agentforge-codex-agent-bundle.json"
compiler_bin='<absolute path of the verified released AgentForge binary>'
case "$compiler_bin" in /*) ;; *) exit 1 ;; esac
test -x "$compiler_bin"
AGENTFORGE_BIN="$compiler_bin"
"$AGENTFORGE_BIN" --version
```

Consumer registration and checks use that absolute verified released binary;
they do not require Bun or an AgentForge checkout. For lifecycle acceptance,
every command also explicitly sets and validates the intended isolated
`CODEX_HOME`; project commands resolve and pass the disposable trusted project
as an absolute canonical argument. Never run a bare user-scope cleanup.

Run this selected-scope check immediately before every exact dispatch:

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

In a fresh Codex session, run `check` for the selected scope immediately before
every exact dispatch. A current successful check permits only the matching role
name above as `agent_type`. A failed or stale check blocks native dispatch. Do
not set a per-dispatch model or effort. All four roles inherit the runtime
model; the bundle retains role effort with an independent task justification:
`vault-reader` uses medium for bounded multi-note synthesis,
`vault-curator` high for approved merge/split judgment,
`note-editor` low for an approved mechanical write, and `vault-inspector` low
for rule-bound reporting. These are role requirements, not translations of
Claude model aliases. Record applied values from runtime metadata and mark
unobservable values `unknown`.

The Markdown/procedure route is separate and requires the user's explicit
choice: give a generic bounded child the matching **installed** agent Markdown
body, omit `agent_type`, and do not claim registration. An inline procedure is
another separately selected fallback. Neither fallback establishes role
registration, same-agent continuity, or a Codex tool policy.

## Installed resources and vault destination

Before dispatch, provide every Librarian role this context:

```markdown
## Runtime context
plugin_root: <absolute canonical root of the active installed Librarian plugin>
vault_name: <explicit configured vault name>
vault_root: <absolute expected vault root>
vault_conventions_reference: <absolute file beneath plugin_root/references/>
bases_reference: <absolute file beneath plugin_root/references/ when needed>
obsidian_cli_gotchas_reference: <absolute file beneath plugin_root/references/ when needed>
inspect_rules_reference: <absolute file beneath plugin_root/references/ when needed>
```

Treat every path above as data to validate, not a hint. `plugin_root`,
`vault_root`, and each supplied reference path must be absolute and canonical;
each reference must be an existing regular file below
`plugin_root/references/`. If any check fails, stop before the dependent
operation rather than selecting a similarly named file from another install.

For a write-capable role, include the user-approved operation, exact target
paths, and approved draft/diff. The role must resolve `vault=<vault_name>` with
the actual Obsidian integration and verify that it names `vault_root` before a
read or write whose destination matters. Changing the process CWD does not
prove an Obsidian CLI destination. If that mapping cannot be proven, stop the
dependent real-CLI operation. A mocked connector is separate evidence. A direct
filesystem fallback is permitted only when the procedure explicitly names a
synthetic disposable fixture and its bounded expected changes; it never counts
as connector acceptance. Never use the normal vault for an acceptance write.

Plugin references resolve only under `plugin_root/references/` (and a skill's
own installed directory for its assets). Vault rules, templates, Bases, and
`.claude` configuration remain explicit external dependencies under the
verified vault root. Do not substitute web search, model memory, an authoring
checkout, or a current working directory when either kind of dependency is
missing.

Every unqualified `~/Loose Ends/...` path and unqualified `obsidian-cli` or
`mcp__obsidian-mcp__*` example in a shared procedure is Claude's existing
default. On Codex, never execute it literally: use the verified
`vault_root` for vault files, prefix **every** CLI operation (reads included)
with `obsidian-cli vault="<vault_name>"`, and supply the equivalent explicit
validated vault selector to a connector call when that connector exposes one.
If a connector cannot select and prove that same `vault_name`/`vault_root`
pair, do not call it. This applies before a dispatch as well as inside a role;
changing CWD never retargets the vault.

Each caller's active installed `SKILL.md` is the source for its sibling assets
and references. Resolve an asset by canonicalizing that installed skill's
directory, never by using a relative `references/` path from the repository or
the process CWD.

Codex strips Claude's role `tools:`, `model`, `maxTurns`, and `memory` policy
fields. The four procedures retain their role boundaries as advisory prose;
they do not mechanically constrain a Codex sandbox, connector, model, or
reasoning effort. Preserve the Claude frontmatter unchanged.

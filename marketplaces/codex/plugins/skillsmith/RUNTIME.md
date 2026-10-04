# Runtime mappings

Skillsmith skill bodies are canonical across agent runtimes. Interpret
orchestration terms by capability:

| Capability | Claude Code | Codex |
|---|---|---|
| Review one adapted skill | Dispatch `@upstream-reviewer` or follow the procedure inline | Dispatch the registered exact role after a current selected-scope check, or use the separately selected installed Markdown/procedure fallback |
| Fetch upstream bytes | `gh api` plus `base64` | `gh api` plus `base64` when available; report an external blocker if source bytes cannot be fetched |
| Apply an accepted change | Caller edits after adjudication | Caller edits after adjudication |

## Codex optional registered review role

The shared Markdown procedure in `agents/upstream-reviewer.md` is not a Codex
registration on its own. A Skillsmith installation can opt into an agent bundle
that registers exactly this role in one selected scope:

- `skillsmith:upstream-reviewer`

Explicitly invoke `$skillsmith:setup-codex-agents` to install or update that
bundle. Its active installed `SKILL.md` finds the installed lifecycle helper;
do not guess a Codex cache path or reuse the source checkout. For a later
selected-scope check, derive the same installed root from the active Skillsmith
skill path:

```sh
skill_file='<absolute path of the active installed Skillsmith SKILL.md>'
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
isolation rules below are lifecycle-acceptance requirements. For lifecycle
acceptance, every command explicitly sets an isolated absolute `CODEX_HOME` and
validates it before use. A project-scope command also resolves the disposable
trusted project to a canonical absolute path and passes that path to the helper,
including the check; never run a bare user-scope cleanup.

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
every exact `skillsmith:upstream-reviewer` dispatch. A current successful check
permits only that exact `agent_type`; do not set a dispatch model or effort.
The role inherits runtime settings. Give it exactly one `skill_path`,
`upstream_repo`, `upstream_path`, `reviewed_sha`, and `ledger_path` per
invocation; do not merge comparison state from multiple skills.

The Markdown-procedure route remains separate and requires the user's explicit
choice: give a generic bounded child the matching **installed** Markdown body,
omit `agent_type`, and do not claim a registration. An inline literal procedure
is likewise a separately chosen fallback.

Codex strips the Claude tool filter. The procedure's read-only and
one-comparison boundaries remain advisory guidance, not mechanical Codex
policy. Preserve Claude's tool filter in canonical frontmatter; do not
translate it into a Codex sandbox policy.

## Acceptance status

The generated bundle does not establish installed registration or runtime
acceptance. Isolated lifecycle behavior, selected-scope registration,
installed-skill activation, and fresh exact-role dispatch still require
separate acceptance.

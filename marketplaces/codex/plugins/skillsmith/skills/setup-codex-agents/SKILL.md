---
name: setup-codex-agents
description: Register this plugin’s optional Codex agent roles for one scope.
---
# Set up Codex agent roles

This plugin installation makes this setup skill available. It does not register
native Codex agent roles. Registration is an optional companion operation that
writes the selected scope's Codex role files, configuration, and ownership
receipt through the installed AgentForge CLI.

## Locate this plugin's companion bundle

Use the absolute path of this active `SKILL.md` supplied by the skill context.
Set `skill_file` to that path, then derive the plugin root from this skill's
directory layout and validate the result before any change:

```sh
skill_file='<absolute path of this active SKILL.md>'
plugin_root="$(dirname "$(dirname "$(dirname "$skill_file")")")"
bundle_root="$plugin_root/.agentforge/codex-agent-bundle"
test -f "$bundle_root/agentforge-codex-agent-bundle.json"
```

If the active skill path is unavailable, ask the user for the installed plugin
root and set `plugin_root` to that exact absolute path. Do not guess a cache
path, plugin version, or another installed plugin.

## Register, check, update, or remove one scope

Ask whether the user wants `user` or `project` scope. For project scope,
ask for the project root and use it literally as `<project-root>`:

```sh
script="$plugin_root/skills/setup-codex-agents/scripts/manage-codex-agent-bundle.sh"

# user scope: choose one operation
sh "$script" install user
sh "$script" check user
sh "$script" update user
sh "$script" remove user

# project scope: choose one operation
sh "$script" install project '<project-root>'
sh "$script" check project '<project-root>'
sh "$script" update project '<project-root>'
sh "$script" remove project '<project-root>'
```

Run an action only when the user selected it. The script resolves its own
plugin root and invokes the installed `agentforge` command. It checks the
required subcommand first, including the matching preview before update or
removal. If a command is missing or incompatible, stop before modifying Codex files and install a release binary from
`https://github.com/jdh313/agentforge/releases` whose `--help` lists that
subcommand. A version number alone is not compatibility evidence.

Treat a nonzero script result as a failure: report its output and do not
continue to a later lifecycle action. Check is read-only. A role edited by the
user is preserved and remains recorded for review. Plugin removal does not
remove these registered roles. Remove each scope independently with the
receipt-based script action; do not clean up roles automatically.

Project registration needs write access to `<project-root>/.codex`. If a
managed permission profile denies that directory, request access or run this
visible script in a terminal authorized to write it, then rerun `check`.

## Register every installed plugin at once

When the user asks to set up every installed plugin at once, run
`agentforge sync-codex-agents --scope user` (add `--dry-run` to preview). It
installs or updates the roles of every enabled plugin that ships a Codex agent
bundle; treat a nonzero result as a failure, as above. The per-plugin script
above remains available.

## Use a registered role

Before claiming that a role is registered or dispatching it, run the selected
scope's `check` action. A nonzero result means setup is missing, edited, or
otherwise not current; report that setup gap and do not dispatch. After a
successful check, start a fresh Codex session before dispatch.
This bundle emits only these exact role identities:

- `skillsmith:upstream-reviewer`

For one of those roles, pass its emitted identity unchanged as
`agent_type` to `spawn_agent`. If the user names any other role, say that
this companion bundle has no setup for that role. Do not rewrite the requested
name into a different identity or claim that the retained Markdown procedure
registered it.

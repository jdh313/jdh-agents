# Host: Fibery

Read this when `issue.host` is `fibery`. It says **how to address Fibery**.
*When* to project is in SKILL.md; *whether* is in the grant.

## Status of this host

**Unverified.** No Fibery operation has been exercised against a live workspace
as part of this pilot. Everything below is a procedure for finding out at
runtime, not a description of a known workspace. Report what you could not
establish rather than approximating it.

## Identity

There is no universal key format. Existing practice cites tasks as `Fibery #N`
in prose. Record whatever identity the workspace actually returns — public id,
entity id, or URL — in `issue.identity`, and keep the URL alongside it.

## Nothing here is hardcoded

Entity types, field names, and field ids are per-workspace. Identifiers seen in
any transcript are one workspace's shape, not a contract. Discover them:

1. `mcp__fibery__schema` for the connected databases.
2. `mcp__fibery__schema_detailed` for the fields of the one holding the task.
3. Find the workflow field and read its available values.

## Caching what you discover

Once a state name resolves, write it to this project's config so the next
change does not repeat the discovery:

```bash
python3 "$HELPER" config-set --state "fibery:implement=<discovered name>"
```

The cache belongs in `config.json`, never in this file. This file is plugin
source, shared by every project; the discovered vocabulary belongs to one
workspace.

## When the workflow field does not exist

A connected workspace may expose no state field matching the projection at all.
That is a legitimate outcome: leave the mapping empty, report the transition as
unmapped, and carry on. Do not substitute a tag, a checkbox, or a nearby
single-select that looks close enough — a misreported state is worse than an
absent one.

## Writing

Use the workspace's own update operation for the discovered field, one field
per call. Never overwrite a description.

## Two trackers at once

A project may list Fibery alongside Linear in `config.hosts`. The per-change
`issue.host` decides which one this change touches — that is the override, and
it needs no extra mechanism. Do not project the same change onto both.

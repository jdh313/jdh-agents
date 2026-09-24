# Tracker: Fibery

Read this when the resolved tracker is `fibery`. It says **how to address
Fibery**.

## Status of this adapter

**Unverified.** No operation below has been exercised against a live workspace.
It is a procedure for finding things out at runtime, not a description of a
known workspace. Report what you could not establish instead of approximating.

If no `mcp__fibery__*` tools are available, the Fibery MCP server is not
connected or not authorized. Say so and stop; the user connects it with `/mcp`.

## Identity

There is no universal key format. Record whatever identity the workspace
returns (public id, entity id, or URL) and keep the URL alongside it.

## Nothing is hardcoded

Entity types, field names, and field ids are per workspace. Discover them:

1. `mcp__fibery__schema` for the connected databases.
2. `mcp__fibery__schema_detailed` for the fields of the database holding the
   work item (`.em.toml` `[fibery] database`, else the one the entity belongs
   to).
3. Find the workflow field and read its available values.

## Fetch

Read the entity with every rich-text field, its comments, and its relations.
Map fields onto the readiness slots by meaning, not by name: an
acceptance-criteria or done-when field is the `Done when` slot even if it is
not a heading in a description.

## State changes

Write the discovered workflow field with the workspace's own update operation,
one field per call. Never overwrite a description.

If no workflow field matches the transition, report it as unmapped and carry
on. Do not substitute a tag or a nearby single-select that looks close enough;
a misreported state is worse than an absent one.

Every Fibery write is outward-facing: confirm it with the user in the same turn.
The one exception is `em:lead` marking the ticket it was invoked on as in
progress; invoking it is the consent.

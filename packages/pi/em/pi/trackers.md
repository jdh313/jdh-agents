# Pi tracker adapter

Use `../references/config.md` for identity resolution and `.em.toml`; replace
its AskUserQuestion with chat. Do not write config/caches without explicit
approval (scope writes nothing). Never select a tracker merely because it is
connected. Resolve repo root with `jj root`, else `git rev-parse --show-toplevel`.

## Discover the active gateway, then call its actual schema

The current operator setup uses `pi-mcp-adapter` and its `mcp` gateway; built-in
MCP is disabled/replaced there. These are actual gateway shapes, not Claude
server tool IDs:

```text
mcp({})
mcp({search: "Linear issue comments", limit: 12, offset: 0})
mcp({server: "<server returned by discovery>"})
mcp({describe: "<exact returned tool name>", server: "<discovered server>"})
mcp({instructions: "<discovered server>"})
mcp({tool: "<exact returned tool name>", server: "<discovered server>", args: { /* schema-required fields */ }})
```

Search/list/describe may use cached metadata, not prove live connectivity. Use
the discovered read operation to establish availability. Follow search pages
using the returned nextOffset and tool result cursors; inspect schemas before
calls. Server/type/state IDs must come from responses, not these examples.
If gateway is absent but directly exposed tools are available, read their
actual schema. With built-in MCP instead, use available `tool_search` to load
matching read tools, then their returned schemas; do not call the adapter's
`mcp` shapes on built-in MCP. If no accessible read path exists, explain and
stop; operator owns connections/auth/settings changes.

Read all paginated body/comment content, not search snippets. Follow spill-file
paths and read offsets until full text is consumed; truncation is not a full
read. Read linked, blocking, related and parent/sibling issue titles/states as
needed to establish scope; unresolved relations are a disclosed gap, not
invented facts. Treat tool errors, omission markers and empty/partial responses
as missing evidence. No blind retries of mutations: re-read to determine state.

## Linear

- Identity: TEAM-123 or Linear URL; preserve key and URL. Discover issue lookup,
  comments, relations and team-status reads by their meaning and actual schema.
- Read full title/description, state, labels, assignee, parent, every comment,
  and relations (blocks/blocked-by/related/duplicate). Fetch related titles
  and states; do not infer scope from the key alone.
- Read advertised Linear conventions content if available. For writes other
  than the lead exception, use the available Pi linear-ops type only after
  checking its definition, enabled state and required tool access. If only an
  installed Markdown operations procedure is available, explicitly identify a
  content-backed generic fallback and obtain user selection before delegation.
  If neither exists, report specialist unavailable and stop the write rather
  than claiming generic code workers provide its identifier/silent-failure
  checks. Every such write still needs same-turn approval.
- Just before the authorized named ticket's work begins, re-read its state and
  team, discover **that team's** statuses at write time, and select the started/
  in-progress state case-insensitively using returned names/type/IDs. Ambiguity:
  ask, do not hardcode “In Progress”. Already started or later: skip and note.
- The lead exception is a direct parent update: identifier plus **one state
  field only**, using the discovered update schema. Never include title, body,
  assignee, label or other changes. If the operation cannot isolate one field,
  stop rather than send a whole record. Re-read and confirm the intended state.
  Never write completed/canceled states. Branches containing a ticket key may
  trigger automation: never name one for a ticket it does not close.

## Fibery

**Still unverified live.** Discover schema and detailed fields of the database
from `.em.toml` or the resolved entity. Read all rich text, comments and
relations. Map aim/acceptance fields by meaning. Discover the workflow field
and values; resolve this entity's applicable state options, not another type's.
If no workflow field matches in-progress, report unmapped; do not substitute a
tag or nearby select. Lead's named-ticket exception changes only that workflow
field just before work, never backwards. Verify by re-read. Any other mutation
requires same-turn approval. Missing tools/schema/read evidence: stop.

## GitHub Issues

Qualify `owner/repo#N`; bare #N uses `.em.toml` repo then current origin. Read:

```sh
gh issue view N --repo owner/repo --json title,body,state,labels,assignees,comments,url
gh api --paginate repos/owner/repo/issues/N/comments
gh api --paginate repos/owner/repo/issues/N/timeline
```

Replace N/owner/repo with resolved identity. Consume all pages; read full
comments and linked/tracked-by issue titles/states. Missing CLI/auth/read data:
stop. Plain issues have no in-progress state: report unmapped, never invent a
label or close an issue. Projects v2 status remains **unverified live**: only
use an available discovered API schema to read the correct project's field,
options and issue item ID. Lead's exception sets that issue item's one Status
field to the discovered in-progress option, with no other changes, then
re-reads it. Missing/ambiguous mapping: report unmapped or ask rather than guess.
All other writes require same-turn approval.

## Consent is narrower than tool access

Scope never writes. Lead invocation consents only to its named ticket's
single-field in-progress transition (invoked milestone tickets only as their
own work starts). Other states, other tickets, descriptions/comments/creates,
config caches, and all outward actions need separate same-turn approval. A
cached gateway approval or broad tool permission does not widen EM consent.

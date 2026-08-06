---
name: lucid-architecture-diagram
description: Create, review, or edit AWS cloud architecture diagrams in Lucid (lucidchart) via the Lucid MCP server. This skill should be used when the user mentions Lucid by name, asks to create/edit a cloud architecture diagram, shares a Lucid URL, asks to review or critique an existing architecture diagram, or wants to add shapes/lines/labels to a Lucid doc. Captures non-obvious silent-failure modes (AWS shape library bootstrapping, assisted-layout container rejection) and the user-places-then-agent-connects cadence that works around them.
---

# Lucid Architecture Diagram

## Overview

Drive Lucid (lucidchart) cloud architecture diagrams through the Lucid MCP server — fetch structure, add shapes/lines, delete items, edit labels and positions. Optimized for AWS cloud architecture diagrams using the AWS 2024 shape library.

This skill exists because two silent-failure modes in the Lucid MCP API will burn a half-hour each if rediscovered from scratch. Both are documented in "Critical gotchas" below; consult them before any `lucid_add_block` call.

**Runtime adapter.** This document names exact `mcp__lucid__*` tool identifiers and argument names on purpose: the gotchas below are *about* specific parameters of specific calls, and describing them by intent would reproduce the mental model that causes the bugs. On a runtime other than Claude Code, these identifiers will not exist verbatim — map each one to whatever the local Lucid integration calls the same operation (search, fetch, add block, add line, edit item, delete items, export as PNG). If no Lucid integration is connected, the skill has nothing to drive and the conventions sections are all that carries over.

## When to use

- User mentions Lucid by name or shares a `lucid.app` URL
- Request involves a cloud architecture diagram (AWS, Azure, GCP)
- User asks to review, critique, or improve an existing diagram
- User wants to add shapes, draw lines, or restructure a Lucid doc

## Setup

### 1. Authenticate

Lucid MCP uses browser-based OAuth. To start the flow, call `mcp__lucid__authenticate`. The tool returns an authorization URL — present it to the user and wait. The user opens it in a browser and approves; the harness completes the handshake automatically.

If the browser shows a connection error on redirect, ask the user to paste the full callback URL and call `mcp__lucid__complete_authentication` with it.

### 2. Load tool schemas

Lucid tools are deferred. Before calling any `mcp__lucid__*` tool, load its schema via ToolSearch:

```
ToolSearch(query="select:mcp__lucid__search,mcp__lucid__fetch,mcp__lucid__lucid_add_block,mcp__lucid__lucid_add_line,mcp__lucid__lucid_edit_item,mcp__lucid__lucid_delete_items,mcp__lucid__lucid_export_document_as_PNG")
```

### 3. Find the document

Use `mcp__lucid__search` with the document title. The user usually names a tab inside the doc — the search returns the doc, but the relevant page may not be page 1. Always inspect `metadata.page_count` and fetch each page until the right `pageTitle` is found.

## Critical gotchas

These two silent-failure modes are the core reason this skill exists. Verify before each programmatic placement.

### Gotcha 1: AWS shape library is registered per-page by UI drag-in

Calling `lucid_add_block` with an AWS shape class (e.g. `aws2024-containers-ArchAmazonElasticContainerServiceAWS2024`) on a page that has never had that library used returns:

```json
{"success": false, "itemId": null, "error": "Block class ... not ready"}
```

The library activates only after a user drags any AWS shape onto that page through the Lucid UI. Once any AWS shape exists on a page, programmatic adds of AWS classes work.

**Detection:** inspect the fetched page's `flowcharts[].nodes[]` for existing `aws2024-*` shape types. If none, the library is dormant.

**Workaround:** Ask the user to drag in one shape from each AWS category needed (Networking, Compute, Containers, Database, Storage, Security, Management). After that, the agent can place additional AWS shapes programmatically.

**Alternative:** Use generic shapes (`RectangleBlock`, `plugin-geometricshapes-shape-rectangle`) styled with appropriate fill colors — these work on any page, no bootstrapping required.

### Gotcha 2: `container_id` silently ignored on assisted-layout containers

If the target container has `assistedLayoutEnabled: true`, `lucid_add_block` returns `success: true` and creates the block — but the block lands at coordinates `(0, 0)` as a free-floating page-level item, NOT inside the named container. No error, no warning, no rejection.

**Detection:** check the container's `assistedLayoutEnabled` property in the fetch response before calling `lucid_add_block` with `container_id`.

**Workarounds:**
1. Ask the user to disable assisted layout on the container via the Lucid UI (right-click container → Auto layout / Smart container toggle), then place programmatically
2. Place blocks free-floating (omit `container_id`) at x/y coordinates that visually fall inside the container's `BoundingBox`
3. Skip programmatic placement for that container — let the user drop shapes via UI and use the API only for lines, edits, and deletions

## Workflow cadence

This cadence proved out across a full Phase 2 CRUD app diagram. Follow it unless the user signals otherwise.

### 1. Wide shot before drawing

Before any UI placement, lay out the architecture verbally: external actors → AWS Cloud → Region → VPC → subnets → services → lines. Confirm the layer plan with the user. POD-style: load-bearing claim first, hold details in soft focus.

### 2. Walk through layer by layer

Outside-in is the natural order for cloud diagrams. Suggested layers:

| Layer | Contents |
|---|---|
| External actors | Users / browser, identity providers (Okta), external SaaS |
| AWS Cloud (container) | Wraps everything below |
| Region (container) | Region-level services that aren't VPC-scoped: Route 53, ACM, ECR, Secrets Manager, CloudWatch |
| VPC (container) | Network boundary |
| Public subnets | ALB, NAT Gateway |
| Private subnets | Compute (ECS services), data (Aurora, RDS) |
| Connection lines | Solid for request path / data flow, dashed for config / telemetry / secrets / image pulls |

### 3. Split the work

- **User does:** OAuth handshake, AWS shape library bootstrapping (one drag per category needed), initial container scaffolding for new pages, toggling assisted layout
- **Agent does:** `fetch` after each user batch and report what landed, programmatic `add_line` between existing shapes, deletions, edits, positioning

### 4. Verify after every write batch

Always re-fetch the page after a batch of writes. Confirm:
- Lines connect to the intended shapes (check `Endpoint1.connectedBlockId` and `Endpoint2.connectedBlockId`)
- New blocks landed where expected (check `BoundingBox`)
- Container nesting is what the user wanted (check `childrenIds`)

Trust but verify — silent failures (Gotcha 2 especially) won't be obvious from the success response alone.

## Capability matrix

| Operation | Programmatic? |
|---|---|
| `mcp__lucid__search` — find document by title | ✅ |
| `mcp__lucid__fetch` — read full structure | ✅ |
| `mcp__lucid__lucid_export_document_as_PNG` — render | ✅ |
| Add generic shape (RectangleBlock etc.) | ✅ |
| Add AWS shape | ✅ if library registered on page (see Gotcha 1) |
| Add line between existing shapes | ✅ — use `endpoint_auto_link=true` for reliable edge attachment |
| Edit block position, size, color, text | ✅ |
| Edit line endpoints | ✅ |
| Delete items (blocks, lines) | ✅ |
| Place into assisted-layout container | ❌ silently rejected (Gotcha 2) |
| Bootstrap AWS shape library | ❌ requires UI drag |
| Toggle assisted layout on a container | ❌ no API parameter |
| OAuth handshake | ❌ requires browser |

## Common operations

### Adding a line between two shapes

```
mcp__lucid__lucid_add_line(
  document_id=<doc_id>,
  page_id=<page_id>,
  endpoint1_shape_id=<source_block_id>,
  endpoint1_auto_link=true,
  endpoint2_shape_id=<target_block_id>,
  endpoint2_auto_link=true,
  endpoint2_style="Arrow",
  stroke_style="solid"  # or "dashed" for config/telemetry/secrets
  line_shape="elbow",
  text="<optional label>"
)
```

`endpoint_auto_link=true` is strongly preferred — Lucid attaches to the best edge based on direction and re-routes as shapes move. Only set explicit `endpoint_position_x/y` when the user demands a specific anchor (e.g. "connect to the top of the box").

### Batching writes

Multiple deletions and additions are independent — issue them in a single tool-use block so they run in parallel. Re-fetch once after the batch, not between calls.

### Resolving the right page

A document can have many pages (tabs). After `mcp__lucid__search` returns a doc ID, fetch page 1 first, check `metadata.page_count`, and iterate pages until the `pageTitle` matches what the user named.

## Conventions for AWS cloud architecture diagrams

### Line styles

- **Solid line** — synchronous request path, data flow, primary traffic
- **Dashed line** — configuration, telemetry, secrets fetch, image pulls, async dependencies
- **Arrow on target end only** — direction of dependency or flow
- **Bidirectional handshakes** (OIDC, OAuth) — two parallel dashed lines, one each way, with labels (`OIDC redirect`, `JWKS / token validation`)

### Container nesting (AWS)

```
External actors (Users, Okta, third-party APIs)
└── AWS Cloud
    └── Region (us-west-2 etc.)
        ├── Global region services (Route 53, ACM, ECR, Secrets Manager, CloudWatch — outside VPC)
        └── VPC
            ├── Public subnet(s) — ALB, NAT Gateway
            └── Private subnet(s) — ECS/EC2, RDS/Aurora
```

### Layout principles

- Place supporting services **near what they serve** to minimize line crossings (ACM next to ALB, ECR next to ECS, etc.)
- Stack the request path vertically when possible: DNS → ALB → compute → data
- Multi-AZ split is optional for POC diagrams — single-row public/private is acceptable with a label noting "spans 2 AZs"
- External actors live **outside** the AWS Cloud container, typically to the left or top

### AWS shape class naming

Pattern: `aws2024-<category>-Arch<ServiceName>AWS2024`

Examples:
- `aws2024-containers-ArchAmazonElasticContainerServiceAWS2024`
- `aws2024-database-ArchAmazonAuroraAWS2024`
- `aws2024-networkingandcontentdelivery-ArchAmazonRoute53AWS2024`
- `aws2024-securityidentityandcompliance-ArchAWSSecretsManagerAWS2024`

For a fuller catalog of common shape classes, load `references/aws-shape-classes.md`.

## Resources

- `references/aws-shape-classes.md` — catalog of common AWS 2024 shape class names by category, plus naming-pattern notes for resolving unknown services

# Linear MCP gotchas

Silent-failure modes observed in the `mcp__linear-server__*` tool surface. Each is paired with the working shape and a one-line cause. **Read before calling Linear MCP from any skill** — these failures return success-shaped responses with empty or wrong data instead of erroring.

Universal — applies to `linear-workflow`, `pm:groom`, `pm:retro`, `pm:breakdown`, `spec-flow:*`, or any direct Linear MCP usage.

---

## 1. `cycle: "current"` returns empty

**Broken:**

```
mcp__linear-server__list_issues({team: "TEAM", cycle: "current"})
→ {issues: [], hasNextPage: false}
```

Returns an empty array even when the current cycle is active and has tickets. No error; no warning. Looks identical to "cycle is genuinely empty."

**Working:**

```
mcp__linear-server__list_cycles({teamId: "<uuid>", type: "current"})
→ [{number: 2, id: "...", isCurrent: true}]

mcp__linear-server__list_issues({team: "TEAM", cycle: "2", ...})
→ actual issues
```

**Cause:** `cycle` parameter expects a cycle **name, number, or ID** — `"current"` is not a recognized identifier despite reading like a natural shortcut. Always resolve via `list_cycles({type: "current"})` first, then pass the numeric name or ID.

**Why it bites:** Returning an empty array (vs. an error) makes the failure invisible to downstream classification. Caught 2026-05-26 when `pm:groom` reported "cycle empty, 0 push-outs" against a 16-ticket cycle.

---

## 2. Grouped-label colon strings drop silently

**Broken:**

```
mcp__linear-server__save_issue({..., labels: ["surface:pipeline", "Feature"]})
→ issue created with labels: ["Feature"]   # surface:pipeline silently dropped
```

**Working — two forms:**

```
labels: ["pipeline", "Feature"]                          # bare child name (unique workspace-wide)
labels: ["<uuid-of-pipeline-label>", "<uuid-of-Feature>"]  # label IDs
```

**Cause:** Linear stores grouped labels as `{parent: "surface", name: "pipeline"}`, not as a single colon-named label. The MCP `save_issue` tool does not resolve `group:child` strings.

**Related — `list_issue_labels` filter on group names:**

```
list_issue_labels({name: "surface"})  → empty
```

Group names aren't label names. To find children of a group, pull the full list and filter on `parent` client-side.

**Caught 2026-05-15** creating TEAM-123.

---

## 3. `estimate` is team-gated and has no null path

`save_issue` accepts `estimate: number` but has no `null` clear path. If the team requires non-zero estimates (Team settings → Features → Estimates), setting `estimate: 0` fails with:

```
Invalid issue estimate - Team doesn't allow estimates to be 0
```

Once an estimate is set via MCP, clearing it requires UI access — either disable estimates team-wide, or clear per issue (and the latter only works if team config permits null).

**Practical rule:** Don't set `estimate` by reflex when creating issues unless an estimation convention has been agreed for the team. This team currently does not use estimates.

---

## Reporting new gotchas

When a new silent-failure mode surfaces:

1. Reproduce it (capture the broken call shape + the actual response).
2. Identify the working shape and the underlying cause.
3. Add a numbered section here following the same template (broken / working / cause / context).
4. Note the discovery date and the calling skill so future readers can cross-reference.

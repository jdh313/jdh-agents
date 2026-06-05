# Linear MCP gotchas

Silent-failure modes observed in the `mcp__linear-server__*` tool surface. Each is paired with the working shape and a one-line cause. **Read before calling Linear MCP from any skill** — these failures return success-shaped responses with empty or wrong data instead of erroring.

Universal — applies to `linear-workflow`, `pm:groom`, `pm:retro`, `pm:breakdown`, `spec-flow:*`, or any direct Linear MCP usage.

---

## 1. `cycle: "current"` returns empty

**Broken:**

```
mcp__linear-server__list_issues({team: "CAR", cycle: "current"})
→ {issues: [], hasNextPage: false}
```

Returns an empty array even when the current cycle is active and has tickets. No error; no warning. Looks identical to "cycle is genuinely empty."

**Working:**

```
mcp__linear-server__list_cycles({teamId: "<uuid>", type: "current"})
→ [{number: 2, id: "...", isCurrent: true}]

mcp__linear-server__list_issues({team: "CAR", cycle: "2", ...})
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

**Caught 2026-05-15** creating CAR-5; full discussion in `~/Loose Ends/Carta/Projects/CartaOS/Linear Setup — Labels.md` under "MCP gotcha".

---

## 3. `estimate` is team-gated and has no null path

`save_issue` accepts `estimate: number` but has no `null` clear path. If the team requires non-zero estimates (Team settings → Features → Estimates), setting `estimate: 0` fails with:

```
Invalid issue estimate - Team doesn't allow estimates to be 0
```

Once an estimate is set via MCP, clearing it requires UI access — either disable estimates team-wide, or clear per issue (and the latter only works if team config permits null).

**Practical rule:** Don't set `estimate` by reflex when creating issues unless an estimation convention has been agreed for the team. The CAR team currently does not use estimates.

---

## 4. `state: "Duplicate"` + `duplicateOf` in one call fails

**Broken:**

```
mcp__linear-server__save_issue({
  id: "CAR-43",
  state: "Duplicate",
  duplicateOf: "CAR-83"
})
→ Error: Missing duplicate relation - Issues can only be moved to a
  duplicate state when a duplicate issue relation exists.
```

The state transition validates against the duplicate relation, but the relation hasn't been committed yet within the same call.

**Working — pass only `duplicateOf`:**

```
mcp__linear-server__save_issue({id: "CAR-43", duplicateOf: "CAR-83"})
→ issue auto-transitions to state "Duplicate" with statusType "duplicate"
```

Setting `duplicateOf` alone is sufficient — Linear creates the relation AND transitions the state in one operation. The explicit `state` parameter is redundant and triggers the validation race.

**Practical rule:** Never pass both `state: "Duplicate"` and `duplicateOf` together. Pass only `duplicateOf` and let Linear handle the state transition.

**Caught 2026-05-29** while merging CAR-43 into CAR-83 during a Linear backlog grooming pass.

---

## 5. Editing a description re-anchors (corrupts) inline comments

**Broken:** `save_issue({id, description})` does a *full-body replace*. Any **inline** comment (a `list_comments` entry with non-null `quotedText`) anchored to text you change gets re-anchored to the nearest surviving text — Linear serializes the anchor as a `<linear-comment id=... resolved=...>` range inside the markdown, so the tags reappear, often splattered word-by-word, on every subsequent save:

```
save_issue({id: "CAR-84", description: "<rewrite that deletes the anchored text>"})
→ stored body now contains:
  * Full-app<linear-comment id="..." resolved="true"> </linear-comment>host port is 4280 ...
```

Re-saving clean markdown does **not** remove them — the comment entity owns the range and re-injects it each time. Stripping the tags from the body string is unreliable for the same reason.

**Working — two halves:**

- **Prevention:** keep the *exact* anchored substring intact. Fetch the raw body (tags included), edit *around* the `<linear-comment>` ranges, never delete or reword the text a live comment points at.
- **Cure:** the only way to remove the tags is to **delete the inline comment itself** (resolving it is not enough — resolved comments still serialize their anchor). The MCP surface has **no delete-comment tool**, so deletion requires the Linear UI (or a raw GraphQL `commentDelete` mutation outside MCP). Plan around this: if a description rewrite must drop anchored text, expect to clean up the orphaned tags by hand in the UI.

**Cause:** same class as Atlassian's Confluence MCP `updateConfluencePage` (atlassian-mcp-server#54) — the programmatic API replaces whole content instead of structurally diffing the way the web editor does, so inline-comment anchors don't survive. Cross-platform MCP limitation, not Linear-specific.

**Practical rule:** treat text under a live inline comment as immutable. To capture a resolved decision that started as an inline comment, write the resolution into a *new* section and delete the inline comment in the UI — don't rely on editing the anchored text away.

**Caught 2026-06-03** during `spec-flow:start` on CAR-84, replacing an Open-questions section that two resolved inline comments were anchored to.

---

## 6. `save_issue` has no project-removal path

**Broken:**

```
mcp__linear-server__save_issue({id: "CAR-66", project: ""})
→ success-shaped response; issue still assigned to its project
```

Passing an empty string for `project` is a **silent no-op** — no error, no change. There is no value that clears the project assignment via MCP.

**Working:** Reassign to another project instead (e.g. `project: "Parking Lot"`), or clear the field in the Linear UI.

**Cause:** The tool treats empty/falsy `project` as "not provided" rather than "set to null" — same missing-null-path class as `estimate` (§3).

**Practical rule:** Don't plan workflows around moving a ticket to bare no-project via MCP. Mostly moot for team CAR anyway: per `pm`'s `layer-policy.md` (2026-06-05), bare no-project is no longer a legal parked state — parked tickets go to the Parking Lot project, which `save_issue` handles fine.

**Caught 2026-06-05** during the weekly grooming pass, attempting to unfile a ticket before the Parking Lot project existed.

---

## Reporting new gotchas

When a new silent-failure mode surfaces:

1. Reproduce it (capture the broken call shape + the actual response).
2. Identify the working shape and the underlying cause.
3. Add a numbered section here following the same template (broken / working / cause / context).
4. Note the discovery date and the calling skill so future readers can cross-reference.

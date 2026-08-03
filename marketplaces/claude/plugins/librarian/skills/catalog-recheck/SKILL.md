---
name: catalog-recheck
description: >-
  Re-evaluate an existing Software Catalog entry against its own revisit
  triggers — read when it was last evaluated, research what changed in the tool
  since then, score the changes against each trigger, and record the outcome.
  Use when the user says "recheck this catalog entry", "re-evaluate X", "is X
  still on hold", "did anything change with X since we last looked", "has X's
  revisit trigger fired", or "catalog recheck". Discovers whether a stance
  SHOULD change; hands the actual write to `catalog-evaluate`.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(obsidian-cli *)
  - WebFetch
  - WebSearch
---

# Catalog Recheck

Re-evaluate one existing Software Catalog entry against the world as it
is today. The catalog is a decision log — every entry carries a `stance`,
a `last_evaluated` date, and (for `hold` / `adopt` entries) a
`## Revisit Triggers` section listing the conditions that would flip the
stance. This skill closes the loop those triggers imply: **has anything
changed in the tool since `last_evaluated` that fires one?**

The load-bearing move is the *scoring* — taking each trigger and asking,
against fresh research, "did this fire, partially fire, or not fire?"
That step is easy to skip and is the entire reason to run a recheck
rather than eyeball the page.

This skill **discovers** whether a stance should change and records the
recheck. It does **not** own the stance write — that stays with
`catalog-evaluate` (which owns the schema, the category changelog, and
the transition semantics). A recheck always ends by bumping
`last_evaluated` and pinning the evaluated version, even when nothing
changed — that is the proof the recheck happened.

## When to use vs. peer skills

| Scenario | Skill |
|---|---|
| "Did anything change with X? Is its trigger fired?" (discover) | `catalog-recheck` |
| "I've decided to change X's stance" (already decided) | `catalog-evaluate` |
| "Update X's body from new info, no stance change" | `wiki-refresh` |
| "Add a brand-new tool to the catalog" | `catalog-evaluate` |
| "Answer a question using the catalog" | `wiki-query` |

The line between `catalog-recheck` and `catalog-evaluate`: recheck is
pulled when the user does **not yet know** whether anything moved and
wants the triggers tested against reality; `catalog-evaluate` is pulled
when the user has **already decided** on a stance and wants it recorded.
Recheck routinely *ends* in a `catalog-evaluate` handoff — but only if a
trigger actually fired.

> [!note] Single-entry only (for now)
> This skill rechecks one named entry per run. A sweep mode — "which
> `hold`/`adopt` entries are overdue for a recheck" across the whole
> catalog, scored by `last_evaluated` staleness — is a planned extension,
> not yet built. Until it lands, recheck entries one at a time.

## Vault tool usage

Use `obsidian-cli read file=...` (via `@vault-reader`) to pull the entry.
Use `obsidian-cli property:read name=<field> file=...` for spot checks.
This skill is read + research + orchestrate only; it does **not** write
the entry itself — the write is delegated (see step 5). The one write it
may own is a light `last_evaluated` bump on a no-change outcome, via
`obsidian-cli property:set name=last_evaluated value=<ISO date> file=...`.

## Workflow

### 1. Resolve the entry

Dispatch via `@vault-reader`:

```markdown
## Intent
read Software Catalog entry for <Tool> to seed a recheck

## Constraints
- Locate the entry in `Reference/Tools/Software Catalog/` (match name,
  case, space/dash/underscore variants, declared `aliases:`)
- Return frontmatter: `stance`, `last_evaluated`, `summary`, `best_for`,
  `categories`, `homepage_url` / `repo_url` / `docs_url`
- Return the full `## Stance` prose (any prior re-eval log + version pin)
- Return the full `## Revisit Triggers` list verbatim, one item per line
- Return the `## Caveats` bullets (these are re-scored too)
- Note any decision notes that link to this tool (search backlinks) —
  candidates for a supersession cascade if the stance flips

## Output shape
- entry_path
- stance, last_evaluated, summary, best_for
- urls: {homepage, repo, docs}
- revisit_triggers: [verbatim list]
- caveats: [verbatim list]
- linked_decision_notes: [paths, or none]
```

If no entry exists, stop and offer `catalog-evaluate` (fresh create)
instead — there is nothing to recheck.

If the entry is a `lead` or `dropped`, stop: `lead` entries are
unevaluated (nothing to re-score; promote via `catalog-evaluate` on
adoption) and `dropped` is a permanent no with no triggers. Confirm with
the user before proceeding if they insist.

### 2. Research what changed since `last_evaluated`

Define the window: **`last_evaluated` → today**. State the window and the
current head version(s) you are evaluating against up front.

Fan out **parallel research subagents** (this is the step that made the
manual version fast). Split by surface when the tool has an ecosystem —
e.g. core platform vs. integrations/adapters/SDK — so each agent stays
focused. For a simple tool, one agent is enough. Use general-purpose
research agents on an appropriate model (research synthesis → sonnet).

Per-agent prompt template:

```markdown
Research what changed in <Tool> between <last_evaluated> and today
(<today>). Focus on <this surface: core | ecosystem | ...>.

Cover: new releases (version + date + headline), notable new
capabilities, breaking changes, deprecations, and any maturity / company
/ community signals (funding, GA milestones, adoption).

Method: primary sources first — GitHub releases, official docs release
notes, project blog. Cite every claim with a URL. Flag anything you
cannot verify rather than guessing. Pin exact version numbers and dates.

Return: (1) releases in window (version | date | headline),
(2) new capabilities (bulleted, each with a URL), (3) breaking changes,
(4) maturity/company signals, (5) sources.

This feeds a re-evaluation of a decision about <Tool>; the specific
question is whether these changes fire any of its revisit triggers:
<paste the revisit_triggers list so the researcher weights relevant
findings>.
```

For a quick single-tool recheck with no ecosystem, inline `WebSearch` /
`WebFetch` is an acceptable fallback to a spawned agent.

### 3. Classify, then score each trigger

Triggers are not all the same shape, and scoring them as if they were
produces false results. **Classify each trigger first**, then score only
the ones tool research can actually move:

- **Tool-shaped** — fires on a change in *this* tool (a release, a new
  capability, a deprecation). Tool research can evaluate these.
- **Need-shaped** — fires on a change in the *user's* needs or context
  ("if network automation becomes a need", "if VPN modeling is needed").
  Tool research **cannot** fire these. Do not score them Fired/Not-fired
  — that hides the truth. Mark **Not evaluable here** and record the
  current tool context that *would* matter if the need arose.
- **Cross-tool** — the condition depends on a *different* tool ("…and
  NetBox hasn't added equivalent models"). Research that other tool's
  state too; the cross-tool clause is often an AND-gate that decides
  whether the trigger can fire at all.

For each **tool-shaped** trigger (and the tool-side clause of a
cross-tool trigger), produce a verdict:

- **Fired** — a change in the window meets the trigger's condition. Cite
  the specific finding + URL.
- **Partial** — movement toward the trigger, but the condition is not
  fully met (e.g. "gained one-way write stubs" for a "true two-way sync"
  trigger). Say what is still missing.
- **Not fired** — no relevant change.

Raise **trigger-quality flags** — a recheck that improves the triggers is
doing its job:

- **Dead clause** — a condition already permanently satisfied or
  unsatisfiable (e.g. a cross-tool AND-clause that was already false
  *before* the window opened). The trigger can't fire as written;
  recommend rewording or retiring it.
- **All-need-shaped** — if *every* trigger is need-shaped, tool research
  can never move this entry. Note that its cadence should be driven by
  periodic need-review, not tool-recheck, and consider whether a
  tool-shaped trigger is missing.

Also collect, separately from the triggers:

- **New caveats** — anything that would *add* a caveat or worsen an
  existing one.
- **`best_for` relevance** — new capabilities that change what the tool
  is the right pick for (may warrant a `best_for` edit even without a
  stance change).
- **Maturity / viability signals** — funding, GA, community — context,
  not usually a trigger by themselves.

Pin the **version(s) evaluated against** — this gets recorded regardless
of outcome.

### 4. Present the verdict

Lead with the headline: **did any tool-shaped trigger fire?** Then the
per-trigger scoring (showing each trigger's classification, so a "not
evaluable here" reads as honest, not as a silent pass), then any
trigger-quality flags, then the other deltas. Recommend exactly one
route:

- **No trigger fired** → stance holds. Recommend recording the recheck
  (bump `last_evaluated`, pin version, add a one-line re-eval note to
  `## Stance`). Optionally a `best_for` tweak or a new caveat.
- **A trigger fired** → stance should change. Recommend the new stance
  and route to `catalog-evaluate`.
- **Body facts moved but stance holds** → route to `wiki-refresh` for the
  content update, plus the `last_evaluated` bump.

A trigger-quality flag (dead clause, all-need-shaped) is an **additional**
recommendation, not a route on its own — offer to reword/retire the
trigger via `catalog-evaluate` (which owns the `## Revisit Triggers`
edit), independent of whatever the stance route is.

Do not invent a stance change to justify the recheck. "Nothing fired,
stance holds, here's the dated proof" is a complete and valuable outcome
— and "nothing fired, but two of your triggers can never fire as written"
is an even better one.

### 5. Hand off the write

Recheck never writes the stance itself. Route by the step-4 outcome:

- **Stance change** → invoke `catalog-evaluate` (update mode) with the
  new stance, the trigger that fired, the version pin, and the re-eval
  summary as input. It owns the frontmatter write, the category
  `## Changelog` line, and the `## Stance` rewrite.
- **No stance change** → the light path. Bump `last_evaluated` to today
  (`obsidian-cli property:set`), and add a dated one-line re-eval note to
  the `## Stance` prose recording the window, the version evaluated
  against, and "no trigger fired" (dispatch `@note-editor` for the body
  line, or `mcp__obsidian-mcp__patch_note` for a single-line insert).
- **Body refresh** → route to `wiki-refresh` for content, which also
  bumps `last_evaluated`.

Always ensure the version pin lands in the `## Stance` re-eval prose —
there is no frontmatter field for it, and `last_evaluated` records only
the date.

### 6. Cascade check (surface, don't auto)

If the stance flipped **and** step 1 found decision notes linking the
tool, surface them: a stance flip often means a decision that assumed the
old stance is now partly wrong. Offer to supersede/amend those notes (via
`/capture-decision` for NDR atoms, or an in-place status flip + banner
for older Journal decision notes). **Never auto-edit a decision note** —
propose it and let the user choose.

## What this skill does NOT do

- **Does not write the stance** — that is `catalog-evaluate`. Recheck
  discovers and routes.
- **Does not invent change** — a no-fire outcome is valid and complete.
- **Does not auto-supersede decision notes** — it surfaces the cascade;
  the user decides.
- **Does not sweep the catalog** — single named entry per run (sweep mode
  is a planned extension).

## Quality rules

- Every "fired" verdict cites a specific finding + primary-source URL.
- Distinguish **partial** from **fired** honestly — movement toward a
  trigger is not the trigger.
- Classify before scoring. A need-shaped trigger marked "not fired" is a
  false negative — it was never evaluable from tool research. Mark it
  "not evaluable here" and say why.
- Surface dead/unreachable triggers rather than scoring around them —
  improving the triggers is part of the recheck's value.
- Pin exact versions and dates; flag anything unverified rather than
  asserting it.
- Record the recheck even on no change — the `last_evaluated` bump + a
  version-pinned re-eval line is the audit trail.
- Keep the `## Stance` re-eval note tight — a dated line or short block,
  not a full changelog. The category page's `## Changelog` carries the
  event line when the stance actually flips.

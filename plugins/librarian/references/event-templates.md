# Event templates

Page templates for `type: event` notes. Loaded by `@note-editor` when
writing event pages, and by `event-capture` when prompting the user for
fields.

Events sit alongside wiki pages but are not wiki content — they capture
*what happened* (an incident, an appointment) rather than *what is*
(a concept, a how-to). Two `page_type` values are defined:

- `incident` — reactive issue + fix documentation
- `appointment` — provider visit (medical, vet, dental, therapy)

The list is extensible. Add new event_kinds (service calls, travel,
purchases) by adding entries to this file; do not create new
`type: event` page types ad hoc.

## Compositional pattern

Events compose with entity pages via `expands:`. The entity (gist hub)
auto-renders its event history through Breadcrumbs `field-groups:
[expansions]`. Free per-entity dashboards as a side effect of normal
capture.

| Entity (gist hub) | Event children (`expands:` the entity) |
|---|---|
| Gear / device | Incidents |
| Pet (Jackson) | Vet visits, health-log entries |
| Health condition | Appointments, symptom changes |
| Person | Meetings, conversations |
| Project | Project meetings, decisions |

## `page_type: incident`

Standalone issue + fix documentation. Smart home, hobbies, homelab,
devices. Distinct from `how-to` (which is a known recipe) — incidents
are one-off issues that don't belong inside any recipe.

### Frontmatter

```yaml
---
owner: jacob | ai
type: event
page_type: incident
date: YYYY-MM-DD               # when it happened
status: resolved               # open | resolved | recurring
severity: medium               # low | medium | high (optional)
expands:
  - "[[Device/System]]"        # required — the entity affected
participants: []               # optional, e.g. ["[[Vendor Support]]"]
follow_up_by: YYYY-MM-DD       # optional
tags: []
date_created: YYYY-MM-DD HH:mm
date_modified: YYYY-MM-DD HH:mm
---
```

### Body skeleton

1. *Neutral one-sentence summary* (first line, no heading)
2. `## Symptoms` — observable behavior, errors, logs
3. `## Context` — what changed, when it started, what was being attempted
4. `## Diagnosis` — what was actually wrong (the gold — this is what makes the page worth keeping)
5. `## Fix` — what resolved it (steps)
6. `## Prevention` — how to avoid recurrence (optional; omit if no clear answer)
7. `## See also`

### Placement

Incidents typically live near the entity they affect — e.g. in the
same folder as the device's gist hub. Common placements:

- Devices/hardware: same folder as the gist (e.g. `Reference/Hardware/`)
- Homelab: `Reference/Infrastructure/<service>/`
- Personal/health: `Personal/Health/<condition>/`

Filename: `YYYY-MM-DD <Brief Issue Title>.md`.

## `page_type: appointment`

Provider visits — medical, vet, dental, therapy. Single template covers
human and pet (the `expands:` target tells you which).

### Frontmatter

```yaml
---
owner: jacob
type: event
page_type: appointment
date: YYYY-MM-DD               # when the appointment occurred
status: completed              # completed | scheduled | cancelled | no-show
specialty: vet                 # vet | gp | dental | specialist | therapy | etc.
expands:
  - "[[Subject]]"              # human or pet
  - "[[Condition]]"            # optional — for condition-tracking
provider: "[[Dr. ___]]"        # optional, can also be a plain string
cost:                          # optional — useful for vet/uncovered
follow_up_by: YYYY-MM-DD       # next visit / monitoring deadline
tags: []
date_created: YYYY-MM-DD HH:mm
date_modified: YYYY-MM-DD HH:mm
---
```

### Body skeleton

1. *Neutral one-sentence summary* (purpose + outcome; first line, no heading)
2. `## Reason` — why this visit
3. `## Findings` — what the provider observed or determined
4. `## Treatment` — prescribed, performed, recommended
5. `## Follow-up` — next steps, next visit, at-home monitoring
6. `## See also`

### Placement

- Pet appointments: `Personal/Pets/<pet>/` (or wherever the pet gist lives)
- Personal health: `Personal/Health/<condition>/`
- Other: same folder as the subject's gist hub

Filename: `YYYY-MM-DD <Subject> <Specialty>.md` (e.g. `2026-05-16
Jackson Vet.md`).

## Adding new event_kinds

Three or more pages of a new shape justify a new `page_type` entry
here. Until then, the closest existing template covers the case (a
service call is an `incident` with a different `expands:` target; a
travel itinerary log can use `incident` with `severity: low` or stay in
daily notes).

When adding a new kind:

1. Append a new section to this file (frontmatter + body skeleton + placement).
2. Update `references/inspect-rules.md` with a `W-EVENT-*` rule for the new shape.
3. Update `~/Loose Ends/.claude/rules/wiki.md` page-type enumeration so vault inspectors recognize it.

## Pre-write checklist

Before declaring the write complete, verify:

- [ ] `type: event` + a valid `page_type` (`incident` | `appointment`)
- [ ] `date:` set in `YYYY-MM-DD` form
- [ ] `status:` set with a valid value for the kind
- [ ] `expands:` includes the affected entity (incidents require it; appointments require it)
- [ ] First non-frontmatter line is a neutral one-sentence summary
- [ ] H2 ordering matches the skeleton for the declared `page_type`
- [ ] Filename follows the placement convention for the kind
- [ ] If `follow_up_by:` is set, it's a real date in the future

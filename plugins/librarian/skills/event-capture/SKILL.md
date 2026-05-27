---
name: event-capture
description: Capture a `type: event` page — an incident (issue + fix) or an appointment (medical, vet, dental, therapy). Use when user says "the 3D printer crashed", "Jackson had his vet visit", "the homelab service died", "had a dental cleaning", "log this incident", "log this appointment", or describes a discrete one-time event tied to a device, pet, person, or condition. Not for knowledge notes, tips, or how-to content — use wiki-create for those.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(obsidian-cli *)
---

# Event Capture

Capture a one-time event (incident or appointment) as a `type: event`
page. Drafts fields interactively with the user; dispatches an entity
existence check to `@vault-reader` and the write to `@note-editor`.

Schema and skeletons live in the vault Templates folder — the agent
loads the relevant template:

- `~/Loose Ends/Templates/Event Incident.md`
- `~/Loose Ends/Templates/Event Appointment.md`
- `~/Loose Ends/Templates/Pet Treatment.md`
- `~/Loose Ends/Templates/Pet Condition.md`

## Mode detection

Pick `event_kind` from the user's framing:

| Input cues | event_kind | page_type |
|---|---|---|
| "crashed", "broke", "wouldn't start", "error", "fixed", device/system name | issue | `incident` |
| "vet", "doctor", "GP", "dental", "therapy", provider name, "appointment", "visit" | provider visit | `appointment` |

If ambiguous: ask. "Is this a one-off issue, or a provider visit?"

For event kinds beyond incident and appointment (service call, travel,
purchase), check `~/Loose Ends/Templates/` first — if there's no
matching template, decline and suggest the closest fit ("This looks
like a service call. I can log it as an `incident` with `severity: low`
expanding the affected device — okay?").

## Vault tool usage

Use `obsidian-cli create name='...' content='...'` for the event page (incident or appointment). Use `obsidian-cli property:set name=expands value=<[[Entity]]> type=list file=...` to wire the gist-hub relationship. Use `obsidian-cli property:set` for `date`, `status`, `severity` (incident) or `specialty`, `provider` (appointment).

## Workflow

### 1. Identify the entity

Every event has an entity it `expands:` — the device, pet, person, or
condition the event is about. Ask the user (or infer) and dispatch via
`@vault-reader`:

```markdown
## Intent
check whether entity page exists

## Constraints
- Search by exact title and `aliases:` frontmatter
- Vault-wide

## Input
entity: <name>

## Output shape
- exists: <bool>
- path: <path if found>
- aliases: [<list>]
```

If missing:

- For people, devices, pets: ask whether to stub now (route to `wiki-create` stub mode), use a placeholder wikilink (event still writes, link will be unresolved), or cancel.
- For "[[Condition]]" on appointments: optional — skip if no condition page makes sense.

### 2. Gather fields

Walk through the frontmatter for the detected `page_type`. Ask one
question at a time; propose defaults when possible.

**Incident** — required: `date`, `status`, `expands:` entity, summary.
Optional: `severity`, `participants`, `follow_up_by`.

**Appointment** — required: `date`, `status`, `specialty`, `expands:`
subject, summary, reason. Optional: `provider`, `cost`, `expands:`
condition, `follow_up_by`.

Propose defaults from context:
- `date`: today, unless the user mentions a different day
- `status`: `resolved` (incident) or `completed` (appointment) — most captures are after-the-fact
- `severity`: `medium` for incidents, ask if it's high/low

### 3. Draft the body

For `incident`, draft each section with the user:

- `## Symptoms` — what they observed (errors, behavior, logs)
- `## Context` — what changed, what was being attempted
- `## Diagnosis` — what was actually wrong (this is the load-bearing section — push the user to articulate the real cause, not just symptoms)
- `## Fix` — steps that resolved it
- `## Prevention` — how to avoid recurrence (omit if no clear answer)
- `## See also` — related incidents, the device gist, upstream issues/PRs

For `appointment`, draft each section:

- `## Reason` — why this visit
- `## Findings` — what the provider observed or determined
- `## Treatment` — prescribed, performed, recommended
- `## Follow-up` — next steps, next visit, at-home monitoring
- `## See also` — related conditions, prior appointments, the subject's gist

Show the full draft (frontmatter + body) for approval before dispatch.

### 4. Determine placement

Per the placement notes in `~/Loose Ends/Templates/Event Incident.md`
and `~/Loose Ends/Templates/Event Appointment.md`:

| Kind | Subject | Placement |
|---|---|---|
| incident | device/hardware | same folder as the gist (e.g. `Reference/Hardware/`) |
| incident | homelab service | `Reference/Infrastructure/<service>/` |
| incident | personal health | `Personal/Health/<condition>/` |
| appointment | pet | `Personal/Pets/<pet>/` |
| appointment | personal | `Personal/Health/<condition>/` |
| appointment | other | same folder as the subject's gist |

Filename:
- incident: `YYYY-MM-DD <Brief Issue Title>.md`
- appointment: `YYYY-MM-DD <Subject> <Specialty>.md`

If the user prefers a different placement, take theirs.

### 5. Dispatch the write

```markdown
## Intent
write event page at <path>

## Constraints
- page_type: <incident | appointment>
- Schema: per the matching template in `~/Loose Ends/Templates/` (`Event Incident.md` or `Event Appointment.md`)
- expands: must point to an existing entity page (or a placeholder agreed in step 1)
- Verify `follow_up_by:` (if set) is a real future date

## Input
<full drafted frontmatter + body>

## Output shape
Confirm file created with placement path. List any unresolved wikilinks.
```

If the user opted to stub the entity in step 1, dispatch that to
`wiki-create` separately *before* writing the event (so `expands:`
points at a real page).

### 6. Report

Surface the agent's `## Result`:

- Event page path
- Entity it expands (with a note if the link is unresolved)
- Follow-up date (if set) so the user knows when to revisit
- Suggested next step if relevant (e.g. "Schedule the follow-up
  appointment in your calendar?")

## Quality rules

- **`Diagnosis` is the gold** — for incidents, push the user past
  "the service was down" to "the service was down because X". A page
  with `## Symptoms` and `## Fix` but a hand-wave `## Diagnosis` is
  worth less to future-you.
- **Don't fabricate findings** — for appointments, capture what the
  provider actually said. If the user is unsure, mark as unverified
  (`[unverified]`) and ask to confirm later.
- **`expands:` is required** — events without an entity don't compose.
  If the user can't name an entity, suggest stubbing one or routing to
  daily notes (`/note-capture`) instead.
- **Filename starts with the date** — supports chronological sort and
  pairs well with the `## Going deeper` Breadcrumbs codeblock on the
  entity gist.

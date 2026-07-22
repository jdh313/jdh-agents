# Report format

The shared contract between the two `feedback` skills. `session` **emits** a
report in this format; `triage` **parses** a pile of them. Keep them in sync —
if you change the shape here, update both skills.

The whole point: the report is one block a tester can copy and send, *and* it is
structured enough that `triage` can cluster findings across many reports and
route each to a fix. The surface table and the per-finding tags carry that
structure; the prose carries the evidence.

## The block

A report is exactly one fenced block with these sections, in order:

```
## Plugin testing feedback — <YYYY-MM-DD> | <tester>

**Tester:** <name, or [TESTER NAME] if unknown>
**Session summary:** <2-3 sentences: what the tester was trying to do>
**Environment:** <cwd repo @ <short-sha> and branch if in a git repo; repos whose plugins were exercised; "unknown" if not discernible>

### Surfaces exercised

| Surface | Kind | Repo | Verdict |
| --- | --- | --- | --- |
| `feedback:session` | skill | shared-claude-plugins | ✅ |

### Findings

- `[feedback:session]` major/output — <what was asked vs. what happened, with a concrete moment>
- `[pm:groom]` minor/friction — <...>

### Worked well

- `[feedback:session]` <claim tied to a concrete moment>

### Suggested fixes

- `[pm:groom]` <only where the fix is obvious from the failure; otherwise omit the section>
```

If a section has nothing the transcript supports, write `Nothing notable this
session` under it rather than padding — except **Suggested fixes**, which is
omitted entirely when empty.

## Field grammar

These are the parts `triage` reads mechanically. Keep them exact.

### Surface id

`<plugin>:<surface>` so a surface is unambiguous across repos:

- Skill or slash command → `feedback:session`, `pm:groom`
- Subagent → `ndr:@ndr-reader` (the `@` marks an agent)
- Hook → `commit:hook/destructive-vcs-guard`

Always wrap the id in backticks, both in the table and as the `[...]` tag on
each finding. If the plugin a surface belongs to genuinely can't be determined,
use `?:<surface>` — never drop the prefix.

### Kind

One of: `skill` · `command` · `subagent` · `hook`.

### Repo

The repo the surface's plugin came from when discernible (e.g.
`shared-claude-plugins`, `ndr`). `unknown` if it can't be told.

### Verdict (surface-level, in the table)

- `✅` worked — triggered at the right time, output correct and useful
- `⚠️` mixed — worked but with rough edges, or worked sometimes
- `❌` broke — misfired, wrong output, or the tester abandoned it

### Finding tag (line-level, in Findings)

Each finding line starts with the surface tag, then `severity/category`:

```
- `[<surface>]` <severity>/<category> — <evidence>
```

**Severity** — how much it hurt:

- `blocker` — the tester couldn't complete what the surface is for
- `major` — completed, but the output was wrong or the path was painful
- `minor` — polish; didn't block anything

**Category** — what *kind* of problem it is (this drives routing in `triage`):

| Category | Means |
| --- | --- |
| `trigger` | didn't fire when expected, fired on the wrong intent, or fired unwanted |
| `output` | produced wrong, confusing, or incomplete output |
| `defaults` | made a bad default choice the tester had to override |
| `friction` | tester repeated themselves, re-clarified, or it was slower than by hand |
| `docs` | the description / README / argument-hint was inaccurate or misleading |
| `missing` | a capability gap — the surface should have done something it can't |

The evidence after the `—` is free prose: what the tester asked, what the
surface did, and where in the session it happened. Concrete moment over
impression.

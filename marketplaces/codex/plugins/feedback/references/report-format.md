# Report format

The shared contract between the `feedback` skills. `session` **emits** reports
in this format and `jot` emits the note shape under "Jots"; `triage` **parses**
a pile of both. Keep them in sync — if you change the shape here, update all
three skills.

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
**Runtime:** <the agent the session ran in, e.g. Claude Code, Codex; "unknown" if not discernible>
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

`<source>:<surface>` so a surface is unambiguous across repos. The source is
the plugin the surface ships in, or — for agent setup that lives outside any
plugin — `user` (user-level: `~/.claude/`, `~/.codex/`, and whatever manages
them) or `project` (the repo's own `CLAUDE.md`, `AGENTS.md`, `.claude/`):

- Skill, however invoked → `feedback:session`, `pm:groom`, `user:end`
- Delegate → `ndr:@ndr-reader` (the `@` marks a delegated worker)
- Hook → `commit:hook/destructive-vcs-guard`, `user:hook/session-start`
- Rule → `user:rule/output-shape`, `user:claude-md`, `project:claude-md`,
  `user:output-style/concise`
- Config → `user:settings/permissions`, `user:mcp/obsidian-mcp`

Always wrap the id in backticks, both in the table and as the `[...]` tag on
each finding. If the source genuinely can't be determined, use `?:<surface>` —
never drop the prefix.

### Kind

One of: `skill` · `delegate` · `hook` · `rule` · `config`.

These name what a surface *is for*, so one report format covers any agent
runtime. What each runtime calls them:

| Kind | Means | Claude Code | Codex |
| --- | --- | --- | --- |
| `skill` | a capability the agent loads to do a thing — whether it chose to, or you invoked it by name | skill (a slash command is one) | skill (explicit-invocation or not) |
| `delegate` | work dispatched to run in its own context, reporting back | subagent | role procedure |
| `hook` | a handler fired by an event rather than by intent | hook | hook |
| `rule` | instructions loaded into every session rather than on demand | `CLAUDE.md`, rules files, output styles, memory | `AGENTS.md` |
| `config` | settings that shape the runtime without being instructions | `settings.json` (permissions, env), MCP servers | `config.toml`, MCP servers |

**There is no separate `command` kind.** A user-invoked skill is still a
`skill` — the invocation path is not what the surface *is*. When the problem is
*how* it fired (or didn't), that is the `trigger` category on the finding, which
is where invocation complaints belong regardless of kind.

Reading old reports: `command` and `subagent` still parse, mapping to `skill`
and `delegate`. Emit only the current five.

### Repo

The repo the surface's source came from when discernible (e.g.
`shared-claude-plugins`, `ndr`); for `user` and `project` surfaces, the repo
holding the file (e.g. `dotfiles`). `unknown` if it can't be told.

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

## Jots

`jot` emits a **jot**: one note about one surface, shaped as an ordinary
Obsidian vault note rather than a report block. Jot folders are often inside
the vault, so a jot follows its note conventions: every field `triage` needs
lives in frontmatter, and the body holds what the user said plus the session
context that prompted it. There is no length limit on either.

```markdown
---
type: agent-feedback
owner: ai
status: open
source: <plugin name, user, project, or unknown>
surface: <surface id, e.g. spec-flow:capture>
kind: <skill|delegate|hook|rule|config>
repo: <repo, or unknown>
version: "<version, or unknown>"
severity: <blocker|major|minor, or none for a compliment>
category: <category, or worked-well>
runtime: <Claude Code, Codex, or unknown>
environment: <cwd repo@short-sha, or unknown>
tester: <name, or unknown>
host: <hostname -s>
captured_at: <YYYY-MM-DDTHH:MM:SS+ZZZZ>
summary: "<One neutral sentence stating what the note is about, naming the surface in backticks.>"
tags: [topic/agent-feedback]
---

`= this.summary`

## User Feedback

<The user's note, lightly cleaned, including any fix they propose.>

## Context

<What was happening in the session when this came up; omit when nothing in the session plainly led to it.>
```

Body rules, from the vault's page conventions:

- **Summary lives in frontmatter.** The one-sentence summary is the `summary`
  property, and the body's first line renders it with the inline Dataview
  expression `` `= this.summary` ``, as the vault's meeting notes do. Never
  repeat the sentence in the body.
- **No header banner.** The rendered summary above the first H2 is the intro.
- **No padding.** A section with nothing in it is omitted, never filled with
  `Nothing notable`.
- **Never hard-wrap prose.** Each paragraph or list item is one line.
- **Sentence case.** Every sentence starts with a capital letter and ends with
  punctuation, including the user's words under `## User Feedback`.
- **User's words stay whole.** `## User Feedback` holds everything the user
  said, cleaned only for capitalization, punctuation, and typos. A fix they
  propose stays there, wherever it falls; `jot` never authors a fix of its own,
  since choosing one is `triage`'s routing job.
- **Context is observed, not inferred.** `## Context` is `jot`'s own
  contribution: the task underway, what the surface was asked to do, and what
  it did, drawn from the session record. It names concrete moments (the
  command run, the output produced, the file touched) and never guesses at a
  cause the session doesn't show. Omit it when the jot arrives with no session
  activity behind it.
- **Neutral voice.** The summary and `## Context` describe the surface and the
  session, not the tester's feelings.

The frontmatter values follow the field grammar above. The surface verdict is
implied: `✅` for `category: worked-well`, `❌` for `severity: blocker`,
otherwise `⚠️`. An idea for a surface is a `missing` finding, `minor` unless
the note says it blocked something.

## Saved files

The fence exists only so a report pasted into chat copies as one unit. A saved
report is a `.md` file holding the block's contents **unfenced**, as ordinary
markdown. It may carry YAML frontmatter above them, which `triage` ignores for
reports; it parses a report the same whether it arrives fenced or not. A file
whose frontmatter has `type: agent-feedback` and no report block is a jot, and
`triage` reads it from the frontmatter.

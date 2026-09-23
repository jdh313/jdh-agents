---
name: jot
description: >-
  Quick feedback or idea capture for a single surface of the agent setup — a
  plugin skill, delegate, or hook, or setup outside plugins such as a rule,
  `CLAUDE.md`, a user-level skill, or a setting — filed as a file
  `feedback:triage` can read later. This skill should be used when the user
  invokes `/feedback:jot`, says "jot this", "jot that down", "note this feedback
  on <plugin>", "log an idea for the <skill> skill", "jot this about my rules",
  or drops a quick complaint, idea, or compliment about a plugin or setup
  surface mid-session and wants it kept without writing a full report. Asks no
  questions: infers the surface from the argument or from what just ran, writes
  one vault-style note with the user's words and the session context behind
  them, and replies with its path. For a graded report covering a whole test
  session, use `feedback:session`.
---

# Jot

The user has something to say about one surface of their agent setup — a
plugin surface, or a rule, `CLAUDE.md`, user-level skill, or setting outside
any plugin: a rough edge, an idea, or something that worked. Capture it
without interrupting them, in a shape `feedback:triage` can cluster later, and
get out of the way.

A jot is an **Obsidian-style note about one surface**, not a report
block. Emit exactly the jot shape in `../../references/report-format.md` (see
"Jots"); the frontmatter's `surface`, `severity`, and `category` are
load-bearing, since `triage` reads them instead of a body.

## Hard rules

- **No note, no jot.** If the invocation carries no note text (a bare
  `/feedback:jot`, or only a `source:surface` id), write nothing and reply with
  the usage below, then stop. Never guess a note from the session.

  ```
  Usage: /feedback:jot [source:surface] <note>
    e.g. /feedback:jot spec-flow:capture asks too many questions
  ```

- **Ask no questions.** Infer everything. If the surface can't be determined,
  use `?:<surface>` or `?:?` rather than asking.
- **Keep the user's words.** `## User Feedback` is the whole note as given,
  including any fix the user proposes, cleaned only for capitalization,
  punctuation, and typos. Never shorten it, and never add a fix of your own.
- **Add the context.** `## Context` is your contribution: what was underway in
  the session when the note came up, per the report format's rules. Report
  what the session shows; never embellish or guess at causes.
- **One file, one line of reply.** Write the file, reply with its path, stop.

## Procedure

1. **Resolve the destination directory.** The configured jot directory is:

   `${user_config.jot_dir}`

   A value still in placeholder form (starting with `${`) was never set: use
   `.docs/feedback/jots/` under the current repo root
   (`git rev-parse --show-toplevel`), or under the working directory when not
   in a repo. Expand a leading `~` to the home directory. Create the directory
   with `mkdir -p` if it is missing.

2. **Resolve the surface.** In priority order:
   - The argument starts with a `source:surface` id (`spec-flow:capture`,
     `ndr:@ndr-reader`, `user:rule/output-shape`) or names a surface plainly
     ("the groom skill", "my output-shape rule", "the permissions allowlist").
   - The note plainly refers to a surface exercised earlier in this session.
   - Otherwise `?:?`.

   A surface outside any plugin takes the source `user` or `project` per the
   report format. Set the kind (`skill` / `delegate` / `hook` / `rule` /
   `config`) and repo per the report format.

3. **Resolve the version** of the surface's source, first hit wins. For a
   `user` or `project` surface, find the file that defines it, `realpath` it,
   and use `<repo>@<short sha>` of the repo holding it (`git rev-parse` from
   its directory); stop there. For a plugin, first hit wins:
   - The surface ran this session and its base directory is known (Claude
     prints `Base directory for this skill: ...`): walk up to the plugin root
     and read `version` from `.claude-plugin/plugin.json` (Claude) or
     `.codex-plugin/plugin.json` (Codex).
   - Claude: `jq` the entry for `<plugin>@*` in
     `~/.claude/plugins/installed_plugins.json` and take its `version`.
   - Codex: the version directory name under
     `~/.codex/plugins/cache/*/<plugin>/`.
   - Otherwise `unknown`.

4. **Classify.**
   - A complaint → pick severity and category from the report format.
   - An idea → `minor/missing` unless the note says it blocked something.
   - A compliment → severity `none`, category `worked-well`.

5. **Collect metadata** (best effort, no questions): timestamp via
   `date +"%Y-%m-%dT%H:%M:%S%z"`, host via `hostname -s`, tester from the
   session's known user identity, runtime, and the repo `@` short sha when in a
   git repo.

6. **Write the file** `<YYYY-MM-DD>-<HHMMSS>-<plugin>-<surface>.md` in the
   destination, with `?` and `@` stripped from the name and any empty part
   dropped. Its content is the jot shape from the report format: frontmatter
   carrying every field (including the one-sentence `summary`), then a body of
   `` `= this.summary` ``, `## User Feedback`, and `## Context` when the session
   led to the note. Write each frontmatter value on one line and quote `version` and
   `summary` so YAML keeps them strings. Start every sentence with a capital
   letter, never hard-wrap body prose, and never add a section that would be
   empty.

7. **Reply** with one line: the tag and the path written, e.g.
   ``Jotted `[spec-flow:capture]` minor/friction → <path>``. Then stop.

## References

- **`../../references/report-format.md`** — the report contract, including the
  jot note shape. `feedback:triage` reads jots from their frontmatter; point it
  at the jot directory.

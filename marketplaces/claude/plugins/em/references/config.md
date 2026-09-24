# Repo config: `.em.toml`

Which tracker a repo uses is a fact about the repo, the same for everyone who
works in it, so it lives in a small committed file at the repo root rather than
in plugin config. Claude Code's plugin `userConfig` is one value per machine and
ignores project-scoped settings, so it cannot say "this repo uses Fibery".

The file is optional. Every field is optional.

```toml
# .em.toml
tracker = "linear"        # linear | fibery | github

[linear]
team = "TEAM"             # key prefix, e.g. TEAM-123

[fibery]
database = "Tasks"        # the database holding work items

[github]
repo = "owner/repo"       # qualifies a bare #123
```

## Resolving the tracker

First match wins:

1. **The reference itself.** A form that names its tracker settles it: a
   `linear.app` URL or `TEAM-123` key is Linear, a `*.fibery.io` URL is Fibery,
   `owner/repo#123` or a `github.com/.../issues/N` URL is GitHub.
2. **`.em.toml` `tracker`.** For forms that don't name one: a bare `#123`, a
   bare number, a title.
3. **Ask.** One `AskUserQuestion` listing the trackers whose MCP tools or CLI are
   actually available in this session. Offer to write the answer to `.em.toml`;
   write it only on a yes.

Never guess from which MCP servers happen to be connected. Two trackers can be
connected at once, and a repo can use one while the session has both.

## Reading it

Read `.em.toml` from the repository root (`jj root`, else
`git rev-parse --show-toplevel`). A missing file is normal. A file that does
not parse is reported, not silently skipped.

Per-tracker caches of discovered names (a Fibery state field, a GitHub Projects
status option) are written back under that tracker's table, and only with the
user's go-ahead: the file is committed, so a write is a repo change.

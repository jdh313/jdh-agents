# Changes reach `main` through a pull request

**Never push to `main` directly.** Push a bookmark and open a PR, even for a
one-line change.

The `main protection` ruleset requires a pull request and a passing `validate`
check (`.github/workflows/validate.yml`: privacy gate, drift check, native
validation). The repo admin role can bypass both, so a direct
`jj git push` to `main` **succeeds silently** and `validate` runs only after
the commits have already landed. The bypass is for emergencies the user
names, never a shortcut.

## How, in this jj repo

1. Name the stack: `jj bookmark create <slug> -r @-` (or the top commit of the
   stack). Never name a bookmark after a ticket it does not close; ticket keys
   in branch names can auto-transition tickets.
2. Push it: `jj git push --bookmark <slug>`.
3. Open the PR: `gh pr create --base main --head <slug>`.
4. Merge only after `validate` passes.

Pushing and opening a PR are outward-facing: each needs the user's go-ahead in
the same turn.

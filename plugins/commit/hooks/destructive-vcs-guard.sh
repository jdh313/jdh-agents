#!/usr/bin/env bash
# PreToolUse/Bash hook for the commits plugin.
# Blocks destructive VCS commands that would discard uncommitted changes.
# Exits 0 to allow, exits 2 to block (Claude sees stderr and must reconsider).

set -euo pipefail

input="$(cat)"

# Tolerate non-JSON stdin: if the tool_input can't be parsed, fail open (allow)
# rather than letting `set -e` kill the hook with an opaque error.
if ! command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)"; then
  exit 0
fi

[ -z "$command" ] && exit 0

trimmed="$(printf '%s' "$command" | sed -E 's/^[[:space:]]+//')"

block() {
  local reason="$1"
  local alternative="$2"
  cat >&2 <<EOF
[commits plugin] Blocked destructive VCS command.

Command: $trimmed

Why: $reason

Safe alternative: $alternative

If the user has explicitly approved discarding these changes, either ask
them to run the command in their own terminal, or use the safe alternative
above. Do NOT retry this exact command without their renewed approval.
EOF
  exit 2
}

# Strip recognized global flags (with their values) between the binary and
# its subcommand, so `git -C /path reset --hard` / `jj -R /x abandon` etc.
# still match the subcommand checks below. Loops to a fixpoint so multiple
# flags (of the same or different kind) are all removed.
normalize() {
  local s="$1"
  local prev
  while true; do
    prev="$s"
    s="$(printf '%s' "$s" | sed -E \
      -e 's/(^|[;&|][[:space:]]*)git([[:space:]]+)-C[[:space:]]+[^[:space:]]+/\1git/' \
      -e 's/(^|[;&|][[:space:]]*)git([[:space:]]+)-c[[:space:]]+[^[:space:]]+/\1git/' \
      -e 's/(^|[;&|][[:space:]]*)git([[:space:]]+)--git-dir=[^[:space:]]+/\1git/' \
      -e 's/(^|[;&|][[:space:]]*)git([[:space:]]+)--git-dir[[:space:]]+[^[:space:]]+/\1git/' \
      -e 's/(^|[;&|][[:space:]]*)git([[:space:]]+)--work-tree=[^[:space:]]+/\1git/' \
      -e 's/(^|[;&|][[:space:]]*)git([[:space:]]+)--work-tree[[:space:]]+[^[:space:]]+/\1git/' \
      -e 's/(^|[;&|][[:space:]]*)jj([[:space:]]+)--repository[[:space:]]+[^[:space:]]+/\1jj/' \
      -e 's/(^|[;&|][[:space:]]*)jj([[:space:]]+)-R[[:space:]]+[^[:space:]]+/\1jj/' \
    )"
    [ "$prev" = "$s" ] && break
  done
  printf '%s' "$s"
}

normalized="$(normalize "$trimmed")"

# git reset --hard / --merge — discards uncommitted work
if printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+reset[[:space:]]+(--hard|--merge)\b'; then
  block "discards ALL uncommitted changes in the working tree and index" \
        "stash first ('git stash push -m WIP'), or commit changes you want to keep, then reset"
fi

# git restore — without --staged (or with --worktree/-W alongside it), discards working-tree changes
if printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+restore\b'; then
  if printf '%s' "$normalized" | grep -qE '[[:space:]](--worktree|-W)\b'; then
    block "discards working-tree changes (--worktree explicitly overwrites tracked files, even alongside --staged)" \
          "to unstage: 'git restore --staged <file>'. To actually discard: stash first to keep a recoverable copy"
  elif ! printf '%s' "$normalized" | grep -qE '[[:space:]](--staged|-S)\b'; then
    block "discards working-tree changes (missing --staged means it modifies files, not just the index)" \
          "to unstage: 'git restore --staged <file>'. To actually discard: stash first to keep a recoverable copy"
  fi
fi

# git checkout <rev> -- <path> / checkout -- <path> / checkout . — discard working-tree changes
if printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+checkout\b'; then
  if printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+checkout\b.*[[:space:]]--([[:space:]]|$)'; then
    block "discards working-tree changes for the listed paths (checkout <rev> -- <path> overwrites them from <rev>)" \
          "stash first ('git stash push -m WIP'), or use 'git restore --staged' if you only meant to unstage"
  elif printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+checkout[[:space:]]+\.[[:space:]]*($|[;&|])'; then
    block "discards ALL working-tree changes (bare '.' pathspec checks out every tracked file from HEAD)" \
          "stash first ('git stash push -m WIP'), or commit changes you want to keep"
  fi
fi

# git stash drop / clear — destroys the safety copies the skill relies on
if printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+stash[[:space:]]+(drop|clear)\b'; then
  block "destroys stash entries that serve as a recoverable safety copy" \
        "leave the stash in place; 'git stash list' to review — dropping requires explicit user approval"
fi

# jj restore — discards working-copy changes
if printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)jj[[:space:]]+restore\b'; then
  block "discards changes in the current jj working copy" \
        "use 'jj split <file> -m \"msg\"' to move changes to a separate commit, or 'jj describe -m \"msg\"' to label the current change"
fi

# jj abandon — discards the change being abandoned (its content is lost unless empty)
if printf '%s' "$normalized" | grep -qE '(^|[;&|][[:space:]]*)jj[[:space:]]+abandon\b'; then
  block "discards the change being abandoned (its content is lost unless the change is empty)" \
        "to relabel: 'jj describe -m \"new msg\"'. To fold into parent: 'jj squash'. Only abandon empty changes"
fi

exit 0

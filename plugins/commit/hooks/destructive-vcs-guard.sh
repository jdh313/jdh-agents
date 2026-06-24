#!/usr/bin/env bash
# PreToolUse/Bash hook for the commits plugin.
# Blocks destructive VCS commands that would discard uncommitted changes.
# Exits 0 to allow, exits 2 to block (Claude sees stderr and must reconsider).

set -euo pipefail

input="$(cat)"
command="$(printf '%s' "$input" | jq -r '.tool_input.command // empty')"

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

# git reset --hard / --merge — discards uncommitted work
if printf '%s' "$trimmed" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+reset[[:space:]]+(--hard|--merge)\b'; then
  block "discards ALL uncommitted changes in the working tree and index" \
        "stash first ('git stash push -m WIP'), or commit changes you want to keep, then reset"
fi

# git restore — without --staged, discards working-tree changes
if printf '%s' "$trimmed" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+restore\b'; then
  if ! printf '%s' "$trimmed" | grep -qE '[[:space:]]--staged\b'; then
    block "discards working-tree changes (missing --staged means it modifies files, not just the index)" \
          "to unstage: 'git restore --staged <file>'. To actually discard: stash first to keep a recoverable copy"
  fi
fi

# git checkout -- <path> — discards working-tree changes
if printf '%s' "$trimmed" | grep -qE '(^|[;&|][[:space:]]*)git[[:space:]]+checkout[[:space:]]+--[[:space:]]+'; then
  block "discards working-tree changes for the listed paths" \
        "stash first ('git stash push -m WIP'), or use 'git restore --staged' if you only meant to unstage"
fi

# jj restore — discards working-copy changes
if printf '%s' "$trimmed" | grep -qE '(^|[;&|][[:space:]]*)jj[[:space:]]+restore\b'; then
  block "discards changes in the current jj working copy" \
        "use 'jj split <file> -m \"msg\"' to move changes to a separate commit, or 'jj describe -m \"msg\"' to label the current change"
fi

# jj abandon — discards the change being abandoned (its content is lost unless empty)
if printf '%s' "$trimmed" | grep -qE '(^|[;&|][[:space:]]*)jj[[:space:]]+abandon\b'; then
  block "discards the change being abandoned (its content is lost unless the change is empty)" \
        "to relabel: 'jj describe -m \"new msg\"'. To fold into parent: 'jj squash'. Only abandon empty changes"
fi

exit 0

#!/bin/sh
# Read-only SessionStart check: at most one {"systemMessage": "..."} object on
# stdout, nothing when roles are current, always exit 0.
package_id='skillsmith'
script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
plugin_root=${PLUGIN_ROOT:-$(dirname "$script_dir")}
agentforge_bin=${AGENTFORGE_BIN:-agentforge}

warn() {
  escaped=$(printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g')
  printf '{"systemMessage": "%s"}\n' "$escaped"
  exit 0
}

if ! command -v "$agentforge_bin" >/dev/null 2>&1; then
  warn "$package_id: AgentForge not found; install a released AgentForge binary from https://github.com/jdh313/agentforge/releases to register agent roles"
fi

bundle_root="$plugin_root/.agentforge/codex-agent-bundle"

# Sets $status to current, missing, or the first token of a refusing result.
check_scope() {
  if out=$("$agentforge_bin" check-codex-agent "$bundle_root" "$@" 2>/dev/null); then
    status=current
  else
    status=$(printf '%s\n' "$out" | head -n 1 | cut -d: -f1)
  fi
}

# Words the one line for a scope that is not current.
advise() {
  scope=$1
  shift
  extra=$*
  if [ "$status" = missing ]; then
    fix="run agentforge sync-codex-agents --scope $scope"
  else
    fix="run agentforge check-codex-agent $bundle_root --scope $scope${extra:+ $extra} to review"
  fi
  warn "$package_id: agent roles are not current at $scope scope; $fix"
}

# The package is fine when any checked scope is current. The project scope is
# checked only where a receipt exists, nearest ancestor of $PWD first.
check_scope --scope user
[ "$status" = current ] && exit 0
user_status=$status

project_root=
dir=$PWD
while :; do
  if [ -f "$dir/.codex/agents/.agentforge/$package_id.json" ]; then
    project_root=$dir
    break
  fi
  parent=$(dirname "$dir")
  [ "$parent" = "$dir" ] && break
  dir=$parent
done

if [ -n "$project_root" ]; then
  check_scope --scope project --project-root "$project_root"
  [ "$status" = current ] && exit 0
  advise project --project-root "$project_root"
fi
status=$user_status
advise user

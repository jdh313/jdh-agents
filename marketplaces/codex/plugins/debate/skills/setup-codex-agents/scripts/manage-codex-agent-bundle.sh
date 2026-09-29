#!/bin/sh
set -eu

usage() {
  echo "usage: $0 <install|check|update|remove> <user|project> [project-root]" >&2
  exit 64
}

operation=${1:-}
scope=${2:-}
project_root=${3:-}

case "$operation" in
  install) subcommand=install-codex-agent ;;
  check) subcommand=check-codex-agent ;;
  update)
    preview_subcommand=preview-codex-agent-update
    subcommand=update-codex-agent
    ;;
  remove)
    preview_subcommand=preview-codex-agent-remove
    subcommand=remove-codex-agent
    ;;
  *) usage ;;
esac

case "$scope" in
  user)
    [ "$#" -eq 2 ] || usage
    ;;
  project)
    [ "$#" -eq 3 ] && [ -n "$project_root" ] || usage
    ;;
  *) usage ;;
esac

agentforge_bin=${AGENTFORGE_BIN:-agentforge}
incompatible() {
  echo "AgentForge is missing or incompatible: expected \"$agentforge_bin $1 --help\" to succeed." >&2
  echo "Install a released AgentForge binary from https://github.com/jdh313/agentforge/releases whose --help lists $1, put it on PATH, then retry." >&2
  exit 69
}
if ! command -v "$agentforge_bin" >/dev/null 2>&1; then
  incompatible "$subcommand"
fi
if ! "$agentforge_bin" "$subcommand" --help >/dev/null 2>&1; then
  incompatible "$subcommand"
fi
if [ -n "${preview_subcommand:-}" ] && ! "$agentforge_bin" "$preview_subcommand" --help >/dev/null 2>&1; then
  incompatible "$preview_subcommand"
fi

script_dir=$(CDPATH= cd "$(dirname "$0")" && pwd -P)
plugin_root=$(CDPATH= cd "$script_dir/../../.." && pwd -P)
bundle_root="$plugin_root/.agentforge/codex-agent-bundle"
package_id="debate"

if [ "$operation" = remove ]; then
  if [ "$scope" = user ]; then
    "$agentforge_bin" "$preview_subcommand" "$package_id" --scope user
    exec "$agentforge_bin" "$subcommand" "$package_id" --scope user
  fi
  "$agentforge_bin" "$preview_subcommand" "$package_id" --scope project --project-root "$project_root"
  exec "$agentforge_bin" "$subcommand" "$package_id" --scope project --project-root "$project_root"
fi

if [ ! -f "$bundle_root/agentforge-codex-agent-bundle.json" ]; then
  echo "Codex agent bundle is missing: $bundle_root/agentforge-codex-agent-bundle.json" >&2
  exit 66
fi

if [ "$scope" = user ]; then
  if [ "$operation" = update ]; then
    "$agentforge_bin" "$preview_subcommand" "$bundle_root" --scope user
  fi
  exec "$agentforge_bin" "$subcommand" "$bundle_root" --scope user
fi
if [ "$operation" = update ]; then
  "$agentforge_bin" "$preview_subcommand" "$bundle_root" --scope project --project-root "$project_root"
fi
exec "$agentforge_bin" "$subcommand" "$bundle_root" --scope project --project-root "$project_root"

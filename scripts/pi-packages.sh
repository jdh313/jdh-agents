#!/usr/bin/env bash
# Standalone Pi outputs are committed under packages/pi/<plugin>/.
# Each package directory is a complete AgentForge-owned snapshot; never put
# settings, node_modules, or other consumer data inside those directories.
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT="${AGENTFORGE_PROJECT:-${HOME}/Projects/agentforge}"
ACTION="${1:-check}"

if [ "$#" -gt 1 ] || { [ "$ACTION" != compile ] && [ "$ACTION" != check ]; }; then
  echo "Usage: scripts/pi-packages.sh [compile|check] (default: check)" >&2
  exit 2
fi
command -v bun >/dev/null 2>&1 || { echo "error: Bun is required for local AgentForge" >&2; exit 1; }
[ -f "${PROJECT}/src/cli.ts" ] || { echo "error: no AgentForge source CLI at ${PROJECT}/src/cli.ts" >&2; exit 1; }
VERSION="$(bun run "${PROJECT}/src/cli.ts" --version)"
[ "$VERSION" = "2.1.0" ] || { echo "error: tested local AgentForge version is 2.1.0; found ${VERSION}" >&2; exit 1; }
echo "Using local AgentForge ${VERSION} at ${PROJECT} (not the pinned marketplace compiler)." >&2

shopt -s nullglob
DEFINITIONS=("${REPO_ROOT}"/plugins/*/PACKAGE.pi.yaml)
[ "${#DEFINITIONS[@]}" -gt 0 ] || { echo "error: no standalone Pi definitions found" >&2; exit 1; }
for definition in "${DEFINITIONS[@]}"; do
  plugin="$(basename -- "$(dirname -- "$definition")")"
  bun run "${PROJECT}/src/cli.ts" package "$ACTION" "$definition" \
    --target pi --out "${REPO_ROOT}/packages/pi/${plugin}"
done

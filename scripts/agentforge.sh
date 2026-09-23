#!/usr/bin/env bash
# Run the pinned AgentForge compiler.
#
# The compiler is pinned by *release identity*, not by source revision: CI and a
# local run must execute the same bytes. A source build at the equivalent commit
# is not byte-identical to the published binary, so a commit SHA could never give
# that guarantee -- it only ever asserted "you built from the right tree".
#
# The binary is cached under .cache/agentforge/<version>/ (gitignored) and its
# sha256 is re-verified on every run, not just on download, so a corrupted or
# tampered cache is replaced rather than trusted.
#
# Usage:
#   scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces
#   scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
#   scripts/agentforge.sh --print-path      # resolve and verify, print, run nothing
#
# To bump: change AGENTFORGE_VERSION, replace the hash map from the new
# release's own SHA256SUMS, re-run compile, and commit the regenerated tree.

set -euo pipefail

AGENTFORGE_VERSION="1.1.0"

# sha256 of each published asset for AGENTFORGE_VERSION, taken from the release's
# own SHA256SUMS. Verified against the downloaded bytes before the binary is ever
# executed, so a compromised or truncated download fails closed.
sha256_for() {
  case "$1" in
    darwin-arm64) echo "47e9335af7c57c77e930ff09ca181cb29cf0e8d650e1effe015aa74936d13ab1" ;;
    linux-arm64)  echo "03f563bc5e31b148bfd66f2255fc4246271efac34329747fdec72cfb6f93f315" ;;
    linux-x64)    echo "ed3ec68ddd7db0f2f7fdbd13fc1bdc4dd430a4d9e84b7b9891389271ca90d200" ;;
    *)            echo "" ;;
  esac
}

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_DIR="${REPO_ROOT}/.cache/agentforge/${AGENTFORGE_VERSION}"
RELEASE_URL_BASE="https://github.com/jdh313/agentforge/releases/download/v${AGENTFORGE_VERSION}"

die() {
  echo "error: $*" >&2
  exit 1
}

# Release asset suffix for the running machine.
platform_asset() {
  local system arch
  system="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "$(uname -m)" in
    arm64 | aarch64) arch="arm64" ;;
    x86_64 | amd64)  arch="x64" ;;
    *) die "no pinned AgentForge binary for $(uname -s)/$(uname -m). Set AGENTFORGE_BIN to a compatible executable." ;;
  esac
  case "$system" in
    darwin | linux) ;;
    *) die "no pinned AgentForge binary for ${system}. Set AGENTFORGE_BIN to a compatible executable." ;;
  esac
  echo "${system}-${arch}"
}

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d' ' -f1
  else
    sha256sum "$1" | cut -d' ' -f1
  fi
}

# Return the pinned compiler, downloading it on first use.
ensure_pinned() {
  local asset expected cached url staged actual
  asset="$(platform_asset)"
  expected="$(sha256_for "$asset")"
  [ -n "$expected" ] || die "no pinned sha256 for agentforge-${asset} at v${AGENTFORGE_VERSION}. Set AGENTFORGE_BIN, or add the hash from the release's SHA256SUMS."

  cached="${CACHE_DIR}/agentforge-${asset}"
  if [ -f "$cached" ] && [ "$(sha256_of "$cached")" = "$expected" ]; then
    chmod 755 "$cached"
    echo "$cached"
    return
  fi

  url="${RELEASE_URL_BASE}/agentforge-${asset}"
  mkdir -p "$CACHE_DIR"
  # Staged under a unique name, not a fixed `.partial`: two concurrent runs
  # sharing this cache (a developer and a pre-commit hook, two CI jobs) would
  # otherwise download over each other's file, and the bytes one run verified
  # would not be the bytes it promotes to $cached a moment later.
  staged="$(mktemp "${CACHE_DIR}/agentforge-${asset}.XXXXXX")" \
    || die "could not create a staging file in ${CACHE_DIR}"
  echo "Fetching pinned AgentForge v${AGENTFORGE_VERSION} (${asset})..." >&2
  curl -fsSL -o "$staged" "$url" || { rm -f "$staged"; die "could not download ${url}"; }

  actual="$(sha256_of "$staged")"
  if [ "$actual" != "$expected" ]; then
    rm -f "$staged"
    die "checksum mismatch for agentforge-${asset} v${AGENTFORGE_VERSION}:
  expected ${expected}
  actual   ${actual}
Refusing to execute unverified bytes."
  fi

  chmod 755 "$staged"
  mv "$staged" "$cached"
  echo "$cached"
}

# Both escape hatches announce themselves on stderr. A bypass that ran silently
# would be indistinguishable from a pinned run in a CI log, so `AGENTFORGE_BIN=true`
# could pass the drift gate having compiled nothing.
#
# AGENTFORGE_BIN names an arbitrary executable and skips verification.
# AGENTFORGE_PROJECT runs a source checkout as-is via bun, deliberately without
# asserting any revision -- the whole point is to exercise an unreleased tree --
# so it announces itself and is never the merge gate.
resolve_command() {
  if [ -n "${AGENTFORGE_BIN:-}" ]; then
    command -v "$AGENTFORGE_BIN" >/dev/null 2>&1 || [ -x "$AGENTFORGE_BIN" ] \
      || die "AGENTFORGE_BIN does not name an executable: ${AGENTFORGE_BIN}"
    echo "warning: running AGENTFORGE_BIN=${AGENTFORGE_BIN}, not the pinned v${AGENTFORGE_VERSION} release. Its bytes are unverified. This is NOT the merge gate." >&2
    RESOLVED=("$AGENTFORGE_BIN")
    return
  fi

  if [ -n "${AGENTFORGE_PROJECT:-}" ]; then
    local project revision
    project="$(cd -- "$AGENTFORGE_PROJECT" 2>/dev/null && pwd)" \
      || die "AGENTFORGE_PROJECT is not a directory: ${AGENTFORGE_PROJECT}"
    [ -f "${project}/src/cli.ts" ] && [ -f "${project}/package.json" ] \
      || die "AGENTFORGE_PROJECT is not an AgentForge source checkout: ${project}"
    command -v bun >/dev/null 2>&1 || die "AGENTFORGE_PROJECT requires \`bun\` on PATH"
    revision="$(git -C "$project" rev-parse --short HEAD 2>/dev/null || echo unknown)"
    echo "warning: compiling with AGENTFORGE_PROJECT source checkout at ${revision}, not the pinned v${AGENTFORGE_VERSION} release. This is NOT the merge gate." >&2
    RESOLVED=(bun run "${project}/src/cli.ts")
    return
  fi

  RESOLVED=("$(ensure_pinned)")
}

resolve_command

if [ "${1:-}" = "--print-path" ]; then
  [ "${#RESOLVED[@]}" -eq 1 ] \
    || die "--print-path is meaningless for a multi-word command: ${RESOLVED[*]}"
  echo "${RESOLVED[0]}"
  exit 0
fi

exec "${RESOLVED[@]}" "$@"

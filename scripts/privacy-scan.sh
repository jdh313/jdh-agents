#!/usr/bin/env bash
# Privacy gate: scan committed history for secrets and machine-home paths.
#
# Two callers, one code path: the `jj push` wrapper's prek pre-push run, and CI.
# It hard-fails on anything matching `.betterleaks.toml` -- Betterleaks'
# maintained default ruleset plus this repository's two custom rules.
#
# This is the one gate the AgentForge compiler cannot own. AgentForge only ever
# sees files a publication declares, so a leak in an undeclared file -- a doc, a
# workflow, a decision atom -- is invisible to it.
#
# WHY HISTORY AND NOT THE WORKING TREE:
# This repository is public, so its history is public. A machine path committed
# and then deleted three commits later is still served by GitHub forever, and a
# working-tree scan reports that repository clean -- it has no way to see it.
# Scanning commits catches it. It also means the gate never reads gitignored
# files, because they were never committed, so its scope cannot drift from
# .gitignore without a second hand-maintained copy of those rules.
#
# WHY --log-opts, AND WHY IT IS NOT OPTIONAL:
# `betterleaks git` walks every ref by default. In a jj-colocated repository
# that includes refs/jj/keep/* -- 894 of them here -- which jj writes so git
# will not GC commits its operation log still references. Those are unreachable
# from any bookmark and are never pushed, but scanning them reported 42 findings
# instead of 10, most of them against states that no branch ever contained.
# HEAD is what CI checks out and what a push publishes, so HEAD is the scope.
#
# Override the revision when you need a different one, e.g. auditing every local
# bookmark before a cleanup:
#   PRIVACY_SCAN_REV=--branches scripts/privacy-scan.sh
#
# SUPPRESSING A FINDING, in order of preference:
#   1. Fix it. If the commit is not yet pushed, jj makes this cheap (`jj squash`,
#      `jj edit`); the rewrite changes the SHA and the finding is simply gone.
#   2. For a deliberate test fixture, put a `betterleaks:allow` comment on the
#      line IN THE SAME COMMIT that introduces it. Added in a later commit it
#      does NOT clear the earlier one -- history mode scans each commit's patch
#      as it was written.
#   3. Only if it is already pushed and therefore immutable, add it to
#      .betterleaks-baseline.json. That file should not grow in normal use; it
#      exists for findings that predate this gate.
#
# Usage:
#   scripts/privacy-scan.sh              # scan committed history (the gate)
#   scripts/privacy-scan.sh FILE...      # scan explicit files (the self-test)
#   scripts/privacy-scan.sh --print-path # resolve and verify, print, run nothing

set -euo pipefail

BETTERLEAKS_VERSION="1.8.1"

# sha256 of each published archive for BETTERLEAKS_VERSION, from the release's
# own checksums.txt. Verified before the binary is ever executed, so a
# compromised or truncated download fails closed. That release also publishes
# checksums.txt.sigstore.json if you want to verify provenance by hand.
sha256_for() {
  case "$1" in
    darwin_arm64) echo "8e80f33b5f2a7426b390347b9fd466033723cb94b6bdffa7572632e2eaec964e" ;;
    darwin_x64)   echo "6abc37df76f881cffae406aa2cec72bea6e6ae64b4e771b3ed21b4aac472ed10" ;;
    linux_arm64)  echo "bbb578b12a2f65d7082ab436abf37724232bc71d8a078e3c41336574420f1b48" ;;
    linux_x64)    echo "efa407244e1ea8e35f582b8a42becdeac08bdead04f68eb752adda722d583c2a" ;;
    *)            echo "" ;;
  esac
}

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE_DIR="${REPO_ROOT}/.cache/betterleaks/${BETTERLEAKS_VERSION}"
CONFIG="${REPO_ROOT}/.betterleaks.toml"
BASELINE="${REPO_ROOT}/.betterleaks-baseline.json"
RELEASE_URL_BASE="https://github.com/betterleaks/betterleaks/releases/download/v${BETTERLEAKS_VERSION}"

# Baseline entries are compared field by field, and Match/Secret are skipped
# only when redaction is on. Generate the baseline and run the gate with the
# same flag or entries silently stop matching.
REDACT=(--redact)

die() {
  echo "error: $*" >&2
  exit 1
}

platform_asset() {
  local system arch
  system="$(uname -s | tr '[:upper:]' '[:lower:]')"
  case "$(uname -m)" in
    arm64 | aarch64) arch="arm64" ;;
    x86_64 | amd64)  arch="x64" ;;
    *) die "no pinned Betterleaks binary for $(uname -s)/$(uname -m)." ;;
  esac
  case "$system" in
    darwin | linux) ;;
    *) die "no pinned Betterleaks binary for ${system}." ;;
  esac
  echo "${system}_${arch}"
}

sha256_of() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d' ' -f1
  else
    sha256sum "$1" | cut -d' ' -f1
  fi
}

# Return the pinned binary, downloading it on first use.
ensure_pinned() {
  local asset expected cached url staged actual tmpdir
  asset="$(platform_asset)"
  expected="$(sha256_for "$asset")"
  [ -n "$expected" ] || die "no pinned sha256 for betterleaks_${asset} at v${BETTERLEAKS_VERSION}."

  # The pin names the ARCHIVE's hash, but what gets cached and executed is the
  # binary extracted from it. So the binary's own hash is recorded at extraction
  # time and re-verified on every later run: that is what makes a tampered cache
  # fail closed rather than being trusted because it merely exists.
  cached="${CACHE_DIR}/betterleaks"
  if [ -f "$cached" ] && [ -f "${cached}.binsha" ] \
     && [ "$(sha256_of "$cached")" = "$(cat "${cached}.binsha")" ]; then
    chmod 755 "$cached"
    echo "$cached"
    return
  fi

  mkdir -p "$CACHE_DIR"
  url="${RELEASE_URL_BASE}/betterleaks_${BETTERLEAKS_VERSION}_${asset}.tar.gz"
  # Unique staging dir: two concurrent runs sharing this cache (a developer and
  # a pre-push hook, two CI jobs) would otherwise overwrite each other's
  # download, and the bytes one run verified would not be the bytes it promotes.
  tmpdir="$(mktemp -d "${CACHE_DIR}.XXXXXX")" || die "could not create a staging directory"
  trap 'rm -rf "$tmpdir"' EXIT
  staged="${tmpdir}/archive.tar.gz"
  echo "Fetching pinned Betterleaks v${BETTERLEAKS_VERSION} (${asset})..." >&2
  curl -fsSL -o "$staged" "$url" || die "could not download ${url}"

  actual="$(sha256_of "$staged")"
  if [ "$actual" != "$expected" ]; then
    die "checksum mismatch for betterleaks_${asset} v${BETTERLEAKS_VERSION}:
  expected ${expected}
  actual   ${actual}
Refusing to execute unverified bytes."
  fi

  tar xzf "$staged" -C "$tmpdir" betterleaks || die "archive did not contain a betterleaks binary"
  chmod 755 "${tmpdir}/betterleaks"
  mv "${tmpdir}/betterleaks" "$cached"
  sha256_of "$cached" > "${cached}.binsha"
  echo "$cached"
}

BETTERLEAKS="$(ensure_pinned)"
trap - EXIT

if [ "${1:-}" = "--print-path" ]; then
  echo "$BETTERLEAKS"
  exit 0
fi

[ -f "$CONFIG" ] || die "missing config: ${CONFIG}"

# Explicit files: filesystem mode, no baseline. This is the self-test's path --
# it plants fixtures in a temporary directory that is in no commit, so there is
# no history to scan and nothing a baseline could match.
if [ "$#" -gt 0 ]; then
  exec "$BETTERLEAKS" dir "$@" -c "$CONFIG" --no-banner "${REDACT[@]}"
fi

cd "$REPO_ROOT"

# Which revision to scan.
#
# HEAD is right in CI, where actions/checkout leaves it on the pushed tip. It is
# WRONG locally in a jj-colocated repo: jj points git's HEAD at the parent of
# the working-copy commit, so `HEAD` silently excludes @ -- the newest commit,
# and the likeliest place for a fresh leak. Scanning HEAD here reported clean
# while never once reading the commit that held this entire change.
#
# jj's @ is not a git revision, but its commit id is, because a colocated repo
# writes real git objects. Resolve it when jj is present and fall back to HEAD.
default_rev() {
  local sha
  if command -v jj >/dev/null 2>&1 && jj root >/dev/null 2>&1; then
    # No --ignore-working-copy: that flag skips the snapshot, so @'s commit id
    # would predate whatever is currently on disk and the gate would pass over
    # the very edits about to be pushed. Letting jj snapshot first is the point.
    sha="$(jj log -r @ --no-graph -T 'commit_id' 2>/dev/null)"
    if [ -n "$sha" ] && git rev-parse --verify --quiet "${sha}^{commit}" >/dev/null 2>&1; then
      echo "$sha"
      return
    fi
  fi
  echo "HEAD"
}

baseline_args=()
[ -f "$BASELINE" ] && baseline_args=(--baseline-path "$BASELINE")

exec "$BETTERLEAKS" git . \
  -c "$CONFIG" \
  --log-opts "${PRIVACY_SCAN_REV:-$(default_rev)}" \
  --git-workers 8 \
  --no-banner \
  "${REDACT[@]}" \
  "${baseline_args[@]}"

#!/usr/bin/env bash
# Does the privacy gate actually fail on the things it claims to catch?
#
# This exists because the gate's worst failure mode is silence, not noise. The
# config is TOML: a top-level key written below a `[table]` header is silently
# reparented and ignored, a mistyped rule regex still parses, and a scan that
# matches nothing looks exactly like a clean tree. Any of those ships a gate
# that passes everything. Asserting "clean repo exits 0" would not catch a
# single one of them -- so every check below plants a known violation and
# requires the gate to REJECT it.
#
# Run: scripts/tests/test_privacy_gate.sh

set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
SCAN="${REPO_ROOT}/scripts/privacy-scan.sh"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

failures=0
checks=0

# Assert the gate's exit status for a fixture file. `expect` is "reject" or
# "accept"; anything else is a typo in this file rather than a real outcome.
assert_gate() {
  local name="$1" expect="$2" fixture="$3" output status
  checks=$((checks + 1))
  set +e
  output="$("$SCAN" "$fixture" 2>&1)"
  status=$?
  set -e

  case "$expect" in
    reject) [ "$status" -ne 0 ] && return 0 ;;
    accept) [ "$status" -eq 0 ] && return 0 ;;
    *) echo "FAIL: ${name}: bad expectation ${expect}" >&2; failures=$((failures + 1)); return 0 ;;
  esac

  failures=$((failures + 1))
  echo "FAIL: ${name}" >&2
  echo "  expected the gate to ${expect}, got exit ${status}" >&2
  echo "  fixture: ${fixture}" >&2
  printf '  gate output: %s\n' "$output" >&2
}

# Rule `absolute-home-path`. The rule that is not a secret rule, and the one no
# off-the-shelf ruleset would supply -- so it is the one most likely to be lost
# silently in a config edit.
# betterleaks:allow -- this fixture IS the violation; the gate must reject it,
# and would otherwise reject this file for containing it.
printf 'see /Users/someone/Projects/thing for details\n' > "${WORK}/home-path.md"  # betterleaks:allow
assert_gate "absolute home path is rejected" reject "${WORK}/home-path.md"

# Rule `secret-shaped-assignment`. Generic assignment matching no specific
# vendor shape, which is exactly what the inherited default ruleset does not
# cover on its own.
printf 'password = "hunter2longenough"\n' > "${WORK}/generic-secret.md"  # betterleaks:allow
assert_gate "generic secret assignment is rejected" reject "${WORK}/generic-secret.md"

# The inherited default ruleset. If `useDefault` were dropped or the config
# failed to load, the two rules above could still pass while every maintained
# vendor pattern silently disappeared.
#
# The token is assembled from pieces rather than written out, and that is not
# decoration: GitHub's own push protection rejects a push containing the literal
# string, which it did to this very file. Splitting it keeps the literal out of
# the repository while the fixture written to disk still carries the full value
# for Betterleaks to match. Do not "tidy" this back into one string.
vendor_token="sk_${vendor_env:-live}_4eC39HqLyjWDarjtT1zdp7dc"  # betterleaks:allow
printf 'stripe_key = "%s"\n' "$vendor_token" > "${WORK}/vendor-token.md"
assert_gate "inherited vendor ruleset is active" reject "${WORK}/vendor-token.md"

# The other half of correctness: ordinary prose must pass. Without this a gate
# that rejects everything would score as fully working above.
printf 'Ordinary documentation with no secrets in it at all.\n' > "${WORK}/clean.md"
assert_gate "clean file is accepted" accept "${WORK}/clean.md"

# --------------------------------------------------------------------------
# History mode. Everything above exercises explicit-file scanning, which does
# not consult the baseline at all -- so none of it would notice a baseline that
# suppressed every finding rather than the ten it is meant to. These two checks
# run the real gate against a throwaway repository instead.
# --------------------------------------------------------------------------

# The gate resolves its repo root, config, and baseline from its OWN location,
# so it must be invoked from a copy inside the throwaway repo. Calling the real
# one from a different working directory would silently scan the real
# repository instead, and the check would prove nothing.
history_check() {
  local name="$1" expect="$2" status
  checks=$((checks + 1))
  # A rejecting gate exits non-zero, which `set -e` would treat as this script
  # failing rather than as the result being measured.
  set +e
  "${WORK}/hist/scripts/privacy-scan.sh" >/dev/null 2>&1
  status=$?
  set -e

  case "$expect" in
    reject) [ "$status" -ne 0 ] && return 0 ;;
    accept) [ "$status" -eq 0 ] && return 0 ;;
  esac
  failures=$((failures + 1))
  echo "FAIL: ${name}: expected the gate to ${expect}, got exit ${status}" >&2
}

if command -v git >/dev/null 2>&1; then
  git init -q "${WORK}/hist"
  (
    cd "${WORK}/hist"
    git config user.email test@example.com
    git config user.name test
    mkdir -p scripts
    cp "${REPO_ROOT}/scripts/privacy-scan.sh" scripts/
    cp "${REPO_ROOT}/.betterleaks.toml" .
    printf 'Ordinary prose.\n' > readme.md
    git add -A && git commit -qm "clean"

    # Share the already-verified binary rather than re-downloading it, which
    # would make this test need the network. Created AFTER the commit and left
    # untracked on purpose: a symlink's committed content is its target path,
    # so committing this one would store a literal home directory and the
    # "clean history" check would fail on the test's own scaffolding.
    ln -s "${REPO_ROOT}/.cache" .cache
  ) >/dev/null 2>&1
  history_check "clean history is accepted" accept

  # A violation committed and then deleted. This is the case a working-tree scan
  # reports clean while the value stays public in the pushed history forever --
  # the entire reason this gate scans commits.
  (
    cd "${WORK}/hist"
    printf 'note: /Users/someone/Projects/thing/config\n' > leak.md  # betterleaks:allow
    git add -A && git commit -qm "introduce"
    git rm -q leak.md && git commit -qm "delete"
  ) >/dev/null 2>&1
  history_check "violation deleted in a later commit is still rejected" reject
else
  echo "  [skip] history checks: git not on PATH" >&2
fi

if [ "$failures" -ne 0 ]; then
  echo "privacy gate self-test FAILED (${failures}/${checks} checks)" >&2
  exit 1
fi
echo "privacy gate self-test passed (${checks} checks)."

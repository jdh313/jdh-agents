#!/usr/bin/env bash
set -euo pipefail

provider=${1:?usage: run.sh claude|codex}
case "$provider" in
  claude|codex) ;;
  *) printf 'provider must be claude or codex\n' >&2; exit 2 ;;
esac

if [[ "$provider" == codex ]]; then
  codex_sandbox_mode=${COMMIT_EVAL_CODEX_SANDBOX_MODE:-workspace-write}
  case "$codex_sandbox_mode" in
    workspace-write)
      printf '%s\n' \
        'Codex commit evaluation cannot run with workspace-write: its sandbox protects the fixture .git directory recursively, so jj cannot create Git objects.' \
        'Rerun only as the explicit local control: COMMIT_EVAL_CODEX_SANDBOX_MODE=danger-full-access evals/commit/scripts/run.sh codex' >&2
      exit 2
      ;;
    read-only)
      printf '%s\n' \
        'Codex commit evaluation cannot run with read-only: the fixture needs working-tree and .git writes to create the required jj commit.' \
        'Rerun only as the explicit local control: COMMIT_EVAL_CODEX_SANDBOX_MODE=danger-full-access evals/commit/scripts/run.sh codex' >&2
      exit 2
      ;;
  esac
fi

eval_dir=$(cd "$(dirname "$0")/.." && pwd)
repo_root=$(cd "$eval_dir/../.." && pwd)
run_stamp=$(date -u +%Y%m%dT%H%M%SZ)-$$
artifact_dir="$eval_dir/artifacts/$provider-$run_stamp"
repeat=${COMMIT_EVAL_REPEAT:-3}
auth_link=
trap 'if [[ -n "$auth_link" && -L "$auth_link" ]]; then rm "$auth_link"; fi' EXIT
# The beforeEach hook builds one fixture per eval row under this directory.
export COMMIT_EVAL_FIXTURES="$artifact_dir/fixtures"
mkdir -p "$COMMIT_EVAL_FIXTURES"

export PROMPTFOO_CONFIG_DIR="$eval_dir/artifacts/promptfoo-data"
config="$eval_dir/promptfooconfig.$provider.yaml"
promptfoo_bin="$eval_dir/node_modules/.bin/promptfoo"
if [[ ! -x "$promptfoo_bin" ]]; then
  printf 'Promptfoo is not installed; run (cd %s && npm install).\n' "$eval_dir" >&2
  exit 2
fi

if [[ "$provider" == codex ]]; then
  export COMMIT_EVAL_CODEX_SANDBOX_MODE="$codex_sandbox_mode"
  export COMMIT_EVAL_CODEX_HOME="$artifact_dir/codex-home"
  mkdir -p "$COMMIT_EVAL_CODEX_HOME"
  if [[ -z ${OPENAI_API_KEY:-} ]]; then
    host_auth="${CODEX_HOST_AUTH_PATH:-$HOME/.codex/auth.json}"
    if [[ ! -f "$host_auth" ]]; then
      printf 'Codex needs OPENAI_API_KEY or an existing auth file at %s.\n' "$host_auth" >&2
      exit 2
    fi
    ln -s "$host_auth" "$COMMIT_EVAL_CODEX_HOME/auth.json"
    auth_link="$COMMIT_EVAL_CODEX_HOME/auth.json"
  fi
  CODEX_HOME="$COMMIT_EVAL_CODEX_HOME" codex plugin marketplace add "$repo_root/marketplaces/codex" --json > "$artifact_dir/codex-marketplace-add.json"
  CODEX_HOME="$COMMIT_EVAL_CODEX_HOME" codex plugin add commit@jdh-agents --json > "$artifact_dir/codex-plugin-add.json"
  CODEX_HOME="$COMMIT_EVAL_CODEX_HOME" codex plugin list --json > "$artifact_dir/codex-plugin-list.json"
fi

filter=()
if [[ -n ${COMMIT_EVAL_FILTER:-} ]]; then
  filter=(--filter-pattern "$COMMIT_EVAL_FILTER")
fi
set +e
"$promptfoo_bin" eval -c "$config" --no-cache --max-concurrency 1 --repeat "$repeat" ${filter[@]+"${filter[@]}"} \
  -o "$artifact_dir/trace.json" > "$artifact_dir/promptfoo.log" 2>&1
provider_exit=$?
set -e
# Exit 100 means the eval ran and some assertion failed; summarize.mjs decides
# whether those failures gate (plugin arms) or only compare (baseline arm).
set +e
node "$eval_dir/scripts/summarize.mjs" "$artifact_dir/trace.json" > "$artifact_dir/summary.json"
gate_exit=$?
set -e
if [[ "$provider" == codex ]]; then
  node "$eval_dir/scripts/skill-report.mjs" "$provider" "$artifact_dir/trace.json" "$artifact_dir/codex-plugin-list.json" > "$artifact_dir/skill-report.json"
else
  node "$eval_dir/scripts/skill-report.mjs" "$provider" "$artifact_dir/trace.json" > "$artifact_dir/skill-report.json"
fi

printf 'artifact: %s\n' "$artifact_dir"
printf 'promptfoo exit: %s; gate exit: %s; repeat: %s\n' "$provider_exit" "$gate_exit" "$repeat"
if (( (provider_exit != 0 && provider_exit != 100) || gate_exit != 0 )); then
  exit 1
fi

#!/usr/bin/env bash
# Detects when a Claude Code session was spawned programmatically — either by
# babysitter or by a generic `claude -p`/`--print`/`--prompt` invocation — and
# emits a tagged marker trace to Langfuse so post-June-15-2026 per-token-billable
# usage is observable.
#
# Bound to SessionStart in hooks.json. Fail-open: any error exits 0 with no
# decision so the session is never blocked.

set -uo pipefail

emit_decision() { printf '{}\n'; exit 0; }

# Consume payload but tolerate empty stdin
payload=$(cat 2>/dev/null || true)

# Walk parent process tree looking for babysitter
pid=${PPID:-0}
ancestor=""
hops=0
while [ "${pid:-0}" -gt 1 ] && [ "$hops" -lt 16 ]; do
  cmd=$(ps -o command= -p "$pid" 2>/dev/null || true)
  [ -z "$cmd" ] && break
  if printf '%s' "$cmd" | grep -qE 'babysitter|/sdk/dist/cli/main\.js|claude\b.*(-p\b|--prompt\b|--print\b)'; then
    ancestor=$cmd
    break
  fi
  pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ' || echo 0)
  hops=$((hops + 1))
done

[ -z "$ancestor" ] && emit_decision

# Distinguish babysitter from a generic programmatic (-p/--print) invocation.
kind="print-mode"
case "$ancestor" in
  *babysitter*) kind="babysitter" ;;
esac

# Credentials piggyback on the langfuse plugin's userConfig.
PK=${CLAUDE_PLUGIN_OPTION_LANGFUSE_PUBLIC_KEY:-${LANGFUSE_PUBLIC_KEY:-${CC_LANGFUSE_PUBLIC_KEY:-}}}
SK=${CLAUDE_PLUGIN_OPTION_LANGFUSE_SECRET_KEY:-${LANGFUSE_SECRET_KEY:-${CC_LANGFUSE_SECRET_KEY:-}}}
HOST=${CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL:-${LANGFUSE_BASE_URL:-${CC_LANGFUSE_BASE_URL:-https://us.cloud.langfuse.com}}}
HOST=${HOST%/}

sid=$(printf '%s' "$payload" | jq -r '.session_id // ""' 2>/dev/null || echo "")
src=$(printf '%s' "$payload" | jq -r '.source // ""' 2>/dev/null || echo "")
ts=$(date -u +%Y-%m-%dT%H:%M:%S.000Z)

uuid() {
  if command -v uuidgen >/dev/null 2>&1; then
    uuidgen | tr 'A-Z' 'a-z'
  else
    python3 -c 'import uuid; print(uuid.uuid4())' 2>/dev/null \
      || echo "tripwire-$(date +%s)-$$-$RANDOM"
  fi
}

# Fallback local log when langfuse creds are missing so detection isn't lost.
if [ -z "$PK" ] || [ -z "$SK" ]; then
  log_dir=${BABYSITTER_LOG_DIR:-$HOME/.a5c/logs}
  mkdir -p "$log_dir" 2>/dev/null || true
  jq -nc --arg ts "$ts" --arg sid "$sid" --arg src "$src" --arg anc "$ancestor" \
    '{event:"programmatic-claude-spawn",reason:"no-langfuse-creds",timestamp:$ts,session_id:$sid,source:$src,ancestor:$anc}' \
    >> "$log_dir/programmatic-spawns.jsonl" 2>/dev/null || true
  emit_decision
fi

trace_id=$(uuid)
evt_id=$(uuid)

body=$(jq -nc \
  --arg eid  "$evt_id" \
  --arg ts   "$ts" \
  --arg tid  "$trace_id" \
  --arg sid  "$sid" \
  --arg src  "$src" \
  --arg anc  "$ancestor" \
  --arg kind "$kind" \
  --arg host "$(hostname 2>/dev/null || echo unknown)" \
  '{
    batch: [{
      id: $eid,
      type: "trace-create",
      timestamp: $ts,
      body: {
        id: $tid,
        name: ("programmatic claude spawn (" + $kind + ")"),
        sessionId: $sid,
        timestamp: $ts,
        tags: ["programmatic-spawn", $kind],
        metadata: {
          ancestor: $anc,
          hook: "babysitter-spawn-tripwire",
          session_source: $src,
          hostname: $host
        },
        environment: "default"
      }
    }],
    metadata: {}
  }' 2>/dev/null) || emit_decision

printf 'user = "%s:%s"\n' "$PK" "$SK" | curl -fsS -m 5 -K - \
  -H 'Content-Type: application/json' \
  -X POST "$HOST/api/public/ingestion" \
  -d "$body" >/dev/null 2>&1 || true

emit_decision

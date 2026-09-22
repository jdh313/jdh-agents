#!/usr/bin/env bash
# Detects when a Claude Code or Codex session was spawned programmatically — by
# babysitter, `claude -p`, or `codex exec` — and
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
  if printf '%s' "$cmd" | grep -qE 'babysitter|/sdk/dist/cli/main\.js|claude\b.*(-p\b|--prompt\b|--print\b)|codex\b.*exec\b'; then
    ancestor=$cmd
    break
  fi
  pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ' || echo 0)
  hops=$((hops + 1))
done

[ -z "$ancestor" ] && emit_decision

# Distinguish babysitter from a generic programmatic (-p/--print) invocation.
runtime="claude-code"
kind="print-mode"
case "$ancestor" in
  *babysitter*) kind="babysitter" ;;
  *codex*exec*) runtime="codex"; kind="exec-mode" ;;
esac
ancestor_label="$runtime:$kind"

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

# Fallback local log when Langfuse creds are missing so detection isn't lost.
if [ -z "$PK" ] || [ -z "$SK" ]; then
  log_dir=${BABYSITTER_LOG_DIR:-$HOME/.a5c/logs}
  mkdir -p "$log_dir" 2>/dev/null || true
  jq -nc --arg ts "$ts" --arg sid "$sid" --arg src "$src" --arg anc "$ancestor_label" \
    --arg runtime "$runtime" \
    '{event:"programmatic-agent-spawn",runtime:$runtime,reason:"no-langfuse-creds",timestamp:$ts,session_id:$sid,source:$src,ancestor:$anc}' \
    >> "$log_dir/programmatic-spawns.jsonl" 2>/dev/null || true
  emit_decision
fi

trace_id=$(uuid | tr -d '-')
span_id=$(uuid | tr -d '-' | cut -c1-16)
start_ns=$(python3 -c 'import time; print(time.time_ns())' 2>/dev/null \
  || echo "$(date +%s)000000000")
end_ns=$((start_ns + 1000000))
trace_name="programmatic $runtime spawn ($kind)"

body=$(jq -nc \
  --arg tid  "$trace_id" \
  --arg spid "$span_id" \
  --arg sid  "$sid" \
  --arg src  "$src" \
  --arg anc  "$ancestor_label" \
  --arg kind "$kind" \
  --arg runtime "$runtime" \
  --arg trace_name "$trace_name" \
  --arg start_ns "$start_ns" \
  --arg end_ns "$end_ns" \
  --arg host "$(hostname 2>/dev/null || echo unknown)" \
  '{
    resourceSpans: [{scopeSpans: [{spans: [{
      traceId: $tid,
      spanId: $spid,
      name: $trace_name,
      startTimeUnixNano: $start_ns,
      endTimeUnixNano: $end_ns,
      attributes: [
        {key:"langfuse.trace.name", value:{stringValue:$trace_name}},
        {key:"session.id", value:{stringValue:$sid}},
        {key:"langfuse.trace.tags", value:{arrayValue:{values:[
          {stringValue:"programmatic-spawn"},
          {stringValue:$runtime},
          {stringValue:$kind}
        ]}}},
        {key:"langfuse.observation.type", value:{stringValue:"span"}},
        {key:"langfuse.environment", value:{stringValue:"default"}},
        {key:"langfuse.observation.metadata.ancestor", value:{stringValue:$anc}},
        {key:"langfuse.observation.metadata.hook", value:{stringValue:"babysitter-spawn-tripwire"}},
        {key:"langfuse.observation.metadata.session_source", value:{stringValue:$src}},
        {key:"langfuse.observation.metadata.hostname", value:{stringValue:$host}}
      ]
    }]}]}]
  }' 2>/dev/null) || emit_decision

printf 'user = "%s:%s"\n' "$PK" "$SK" | curl -fsS -m 5 -K - \
  -H 'Content-Type: application/json' \
  -H 'x-langfuse-ingestion-version: 4' \
  -X POST "$HOST/api/public/otel/v1/traces" \
  -d "$body" >/dev/null 2>&1 || true

emit_decision

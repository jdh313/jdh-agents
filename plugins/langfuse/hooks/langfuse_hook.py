#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["langfuse>=4.7.1,<5"]
# ///
"""
Claude Code -> Langfuse hook

"""
# Forked from langfuse/Claude-Observability-Plugin v1.0.0
import json
import logging
import os
import re
import sys
import threading
import time
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --- Langfuse import (fail-open) ---
try:
    from langfuse import Langfuse, propagate_attributes
    from opentelemetry import trace as otel_trace_api
except Exception:
    sys.exit(0)

# --- Paths ---
STATE_DIR = Path.home() / ".claude" / "state"
LOG_FILE = STATE_DIR / "langfuse_hook.log"
STATE_FILE = STATE_DIR / "langfuse_state.json"
LOCK_FILE = STATE_DIR / "langfuse_state.lock"

def _opt(name: str) -> str:
    """Read a plugin userConfig value (CLAUDE_PLUGIN_OPTION_<NAME>) with a fallback to a plain env var."""
    return os.environ.get(f"CLAUDE_PLUGIN_OPTION_{name}") or os.environ.get(name) or ""

DEBUG = _opt("CC_LANGFUSE_DEBUG").lower() == "true"
try:
    MAX_CHARS = int(_opt("CC_LANGFUSE_MAX_CHARS") or "20000")
except ValueError:
    MAX_CHARS = 20000

# ----------------- Logging -----------------
_logger: Optional[logging.Logger] = None

def _get_logger() -> Optional[logging.Logger]:
    global _logger
    if _logger is not None:
        return _logger
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        lg = logging.getLogger("langfuse_hook")
        lg.setLevel(logging.DEBUG if DEBUG else logging.INFO)
        if not lg.handlers:
            h = RotatingFileHandler(str(LOG_FILE), maxBytes=5_000_000, backupCount=3)
            h.setFormatter(logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            ))
            lg.addHandler(h)
        _logger = lg
        return _logger
    except Exception:
        return None

def debug(msg: str) -> None:
    if not DEBUG:
        return
    lg = _get_logger()
    if lg is not None:
        try:
            lg.debug(msg)
        except Exception:
            pass

def info(msg: str) -> None:
    lg = _get_logger()
    if lg is not None:
        try:
            lg.info(msg)
        except Exception:
            pass

# ----------------- State locking (best-effort) -----------------
class FileLock:
    def __init__(self, path: Path, timeout_s: float = 2.0):
        self.path = path
        self.timeout_s = timeout_s
        self._fh = None

    def __enter__(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a+", encoding="utf-8")
        self.acquired = False
        try:
            import fcntl  # Unix only
        except ImportError:
            # No fcntl available (e.g. Windows) — proceed without lock.
            return self
        deadline = time.time() + self.timeout_s
        try:
            while True:
                try:
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    self.acquired = True
                    return self
                except BlockingIOError:
                    if time.time() > deadline:
                        raise TimeoutError(
                            f"could not acquire {self.path} within {self.timeout_s}s"
                        )
                    time.sleep(0.05)
        except BaseException:
            # __exit__ is not called when __enter__ raises — close the fh
            # we just opened so it doesn't leak.
            try:
                self._fh.close()
            except Exception:
                pass
            raise

    def __exit__(self, exc_type, exc, tb):
        try:
            import fcntl
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            self._fh.close()
        except Exception:
            pass

def load_state() -> Dict[str, Any]:
    try:
        if not STATE_FILE.exists():
            return {}
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_state(state: Dict[str, Any]) -> None:
    try:
        # Drop session entries older than 30 days to keep the file bounded.
        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        for k in list(state.keys()):
            entry = state.get(k)
            if not isinstance(entry, dict):
                continue
            updated = entry.get("updated")
            if not isinstance(updated, str):
                continue
            try:
                ts = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            except Exception:
                continue
            if ts < cutoff:
                del state[k]
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        debug(f"save_state failed: {e}")

def state_key(session_id: str, transcript_path: str) -> str:
    # stable key even if session_id collides
    raw = f"{session_id}::{transcript_path}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

# ----------------- Hook payload -----------------
def read_hook_payload() -> Dict[str, Any]:
    """
    Claude Code hooks pass a JSON payload on stdin.
    This script tolerates missing/empty stdin by returning {}.
    """
    try:
        data = sys.stdin.read()
        debug(f"stdin received {len(data)} chars")
        if not data.strip():
            return {}
        parsed = json.loads(data)
        if isinstance(parsed, dict):
            debug(f"payload top-level keys: {sorted(parsed.keys())}")
        return parsed
    except Exception as e:
        debug(f"read_hook_payload exception: {e!r}")
        return {}

def extract_session_and_transcript(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[Path]]:
    """
    Tries a few plausible field names; exact keys can vary across hook types/versions.
    Prefer structured values from stdin over heuristics.
    Note: CLAUDE_CODE_SESSION_ID is not set as an env var in hook processes —
    session_id is only available via the stdin JSON payload.
    """
    session_id = (
        payload.get("sessionId")
        or payload.get("session_id")
        or payload.get("session", {}).get("id")
    )

    transcript = (
        payload.get("transcriptPath")
        or payload.get("transcript_path")
        or payload.get("transcript", {}).get("path")
    )

    if transcript:
        try:
            transcript_path = Path(transcript).expanduser().resolve()
        except Exception:
            transcript_path = None
    else:
        transcript_path = None

    return session_id, transcript_path


def extract_agent_context(payload: Dict[str, Any]) -> Dict[str, str]:
    """
    Extracts subagent context fields from the Stop hook payload.
    agent_id and agent_type are present only when the hook fires inside a subagent.
    parent_agent_id is not provided by the Stop hook payload.
    """
    ctx: Dict[str, str] = {}
    agent_id = payload.get("agent_id")
    if isinstance(agent_id, str) and agent_id:
        ctx["agent_id"] = agent_id
    agent_type = payload.get("agent_type")
    if isinstance(agent_type, str) and agent_type:
        ctx["agent_type"] = agent_type
    return ctx

# ----------------- Transcript parsing helpers -----------------
def get_content(msg: Dict[str, Any]) -> Any:
    if not isinstance(msg, dict):
        return None
    if "message" in msg and isinstance(msg.get("message"), dict):
        return msg["message"].get("content")
    return msg.get("content")

def get_role(msg: Dict[str, Any]) -> Optional[str]:
    # Claude Code transcript lines commonly have type=user/assistant OR message.role
    t = msg.get("type")
    if t in ("user", "assistant"):
        return t
    m = msg.get("message")
    if isinstance(m, dict):
        r = m.get("role")
        if r in ("user", "assistant"):
            return r
    return None

def is_tool_result(msg: Dict[str, Any]) -> bool:
    role = get_role(msg)
    if role != "user":
        return False
    content = get_content(msg)
    if isinstance(content, list):
        return any(isinstance(x, dict) and x.get("type") == "tool_result" for x in content)
    return False

def iter_tool_results(content: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(content, list):
        for x in content:
            if isinstance(x, dict) and x.get("type") == "tool_result":
                out.append(x)
    return out

def iter_tool_uses(content: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(content, list):
        for x in content:
            if isinstance(x, dict) and x.get("type") == "tool_use":
                out.append(x)
    return out

def extract_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: List[str] = []
        for x in content:
            if isinstance(x, dict) and x.get("type") == "text":
                parts.append(x.get("text", ""))
            elif isinstance(x, str):
                parts.append(x)
        return "\n".join([p for p in parts if p])
    return ""

def truncate_text(s: str, max_chars: int = MAX_CHARS) -> Tuple[str, Dict[str, Any]]:
    if s is None:
        return "", {"truncated": False, "orig_len": 0}
    orig_len = len(s)
    if orig_len <= max_chars:
        return s, {"truncated": False, "orig_len": orig_len}
    head = s[:max_chars]
    return head, {"truncated": True, "orig_len": orig_len, "kept_len": len(head), "sha256": hashlib.sha256(s.encode("utf-8")).hexdigest()}

def get_model(msg: Dict[str, Any]) -> str:
    m = msg.get("message")
    if isinstance(m, dict):
        return m.get("model") or "claude"
    return "claude"

def get_usage(msg: Dict[str, Any]) -> Optional[Dict[str, int]]:
    """Extract Anthropic token usage from an assistant message, if present."""
    m = msg.get("message")
    if not isinstance(m, dict):
        return None
    u = m.get("usage")
    if not isinstance(u, dict):
        return None
    details: Dict[str, int] = {}
    for src, dst in (
        ("input_tokens", "input"),
        ("output_tokens", "output"),
        ("cache_read_input_tokens", "cache_read_input_tokens"),
        ("cache_creation_input_tokens", "cache_creation_input_tokens"),
    ):
        v = u.get(src)
        if isinstance(v, int) and v > 0:
            details[dst] = v
    return details or None

def get_message_id(msg: Dict[str, Any]) -> Optional[str]:
    m = msg.get("message")
    if isinstance(m, dict):
        mid = m.get("id")
        if isinstance(mid, str) and mid:
            return mid
    return None

def parse_ts(value: Any) -> Optional[datetime]:
    """Parse a Claude Code jsonl row timestamp (ISO 8601 with trailing Z)."""
    if isinstance(value, dict):
        value = value.get("timestamp")
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None

# ----------------- Incremental reader -----------------
@dataclass
class SessionState:
    offset: int = 0
    buffer: str = ""
    turn_count: int = 0
    # Poison-turn guard: identifies the leading not-yet-committed turn by the
    # offset it starts at, and how many consecutive emit failures it has hit.
    # Single-slot is sufficient — offset is a strict linear cursor, so at most
    # one turn can be "stuck" at the front at a time.
    poison_offset: Optional[int] = None
    poison_fail_count: int = 0

def load_session_state(global_state: Dict[str, Any], key: str) -> SessionState:
    s = global_state.get(key, {})
    poison_offset = s.get("poison_offset")
    return SessionState(
        offset=int(s.get("offset", 0)),
        buffer=str(s.get("buffer", "")),
        turn_count=int(s.get("turn_count", 0)),
        poison_offset=poison_offset if isinstance(poison_offset, int) else None,
        poison_fail_count=int(s.get("poison_fail_count", 0)),
    )

def write_session_state(global_state: Dict[str, Any], key: str, ss: SessionState) -> None:
    global_state[key] = {
        "offset": ss.offset,
        "buffer": ss.buffer,
        "turn_count": ss.turn_count,
        "poison_offset": ss.poison_offset,
        "poison_fail_count": ss.poison_fail_count,
        "updated": datetime.now(timezone.utc).isoformat(),
    }

def read_new_jsonl(
    transcript_path: Path, ss: SessionState
) -> Tuple[List[Tuple[Dict[str, Any], int]], str, int]:
    """
    Reads only new bytes since ss.offset. Does NOT mutate ss — the caller
    decides how much of this read to actually commit, since a turn built from
    these rows may fail to emit and need to be retried next invocation.

    Returns:
      - rows: (message, end_offset) pairs for each complete new line, where
        end_offset is the absolute file offset immediately after that line —
        i.e. where it's safe to resume reading from if this row's turn (and
        everything before it) is committed.
      - new_buffer: the leftover partial (unterminated) last line, valid only
        if the caller commits all the way through to full_read_offset.
      - full_read_offset: the absolute file offset after this entire read —
        what ss.offset becomes if every row this round is committed.
    """
    start_offset = ss.offset
    buffer = ss.buffer

    if not transcript_path.exists():
        return [], buffer, start_offset

    try:
        file_size = transcript_path.stat().st_size
        if file_size < start_offset:
            # Transcript was rotated or truncated — restart from the beginning.
            debug(f"transcript shrank ({file_size} < {start_offset}); restarting")
            start_offset = 0
            buffer = ""
        with open(transcript_path, "rb") as f:
            f.seek(start_offset)
            chunk = f.read()
            full_read_offset = f.tell()
    except Exception as e:
        debug(f"read_new_jsonl failed: {e}")
        return [], buffer, start_offset

    if not chunk:
        return [], buffer, start_offset

    try:
        text = chunk.decode("utf-8", errors="replace")
    except Exception:
        text = chunk.decode(errors="replace")

    # buffer holds a fragment with no embedded newline (invariant maintained
    # below), so splitting buffer+text has the same element count as
    # splitting text alone — only the first element gains the buffer prefix.
    text_lines = text.split("\n")
    new_buffer = text_lines[-1]

    rows: List[Tuple[Dict[str, Any], int]] = []
    cum = 0
    for k in range(len(text_lines) - 1):
        line = (buffer + text_lines[k]) if k == 0 else text_lines[k]
        cum += len(text_lines[k].encode("utf-8", errors="replace")) + 1  # +1 for '\n'
        end_offset = start_offset + cum
        line = line.strip()
        if not line:
            continue
        try:
            rows.append((json.loads(line), end_offset))
        except Exception:
            continue

    return rows, new_buffer, full_read_offset

# ----------------- Turn assembly -----------------
@dataclass
class Turn:
    user_msg: Dict[str, Any]
    assistant_msgs: List[Dict[str, Any]]
    tool_results_by_id: Dict[str, Any]
    end_offset: int  # transcript offset immediately after this turn's last contributing row

def build_turns(rows: List[Tuple[Dict[str, Any], int]]) -> Tuple[List[Turn], Dict[str, int]]:
    """
    Groups incremental transcript rows into turns:
    user (non-tool-result) -> assistant messages -> (tool_result rows, possibly interleaved)
    Uses:
    - assistant message dedupe by message.id (latest row wins)
    - tool results dedupe by tool_use_id (latest wins)

    Each row is (message, end_offset) — end_offset is threaded through so each
    finalized Turn knows the transcript offset it's safe to commit through.

    Returns (turns, unknown_row_type_counts) — the latter for observability
    only; unknown rows never contribute to a turn or its end_offset.
    """
    turns: List[Turn] = []
    current_user: Optional[Dict[str, Any]] = None
    current_end_offset: int = 0

    # assistant messages for current turn:
    assistant_order: List[str] = []             # message ids in order of first appearance (or synthetic)
    assistant_latest: Dict[str, Dict[str, Any]] = {}  # id -> latest msg

    tool_results_by_id: Dict[str, Any] = {}     # tool_use_id -> content
    unknown_counts: Dict[str, int] = {}

    def flush_turn():
        nonlocal current_user, assistant_order, assistant_latest, tool_results_by_id, turns
        if current_user is None:
            return
        if not assistant_latest:
            return
        assistants = [assistant_latest[mid] for mid in assistant_order if mid in assistant_latest]
        turns.append(Turn(
            user_msg=current_user,
            assistant_msgs=assistants,
            tool_results_by_id=dict(tool_results_by_id),
            end_offset=current_end_offset,
        ))

    for msg, end_offset in rows:
        role = get_role(msg)

        # tool_result rows show up as role=user with content blocks of type tool_result
        if is_tool_result(msg):
            row_ts = msg.get("timestamp")
            for tr in iter_tool_results(get_content(msg)):
                tid = tr.get("tool_use_id")
                if tid:
                    tool_results_by_id[str(tid)] = {"content": tr.get("content"), "timestamp": row_ts}
            if current_user is not None:
                current_end_offset = end_offset
            continue

        if role == "user":
            # new user message -> finalize previous turn
            flush_turn()

            # start a new turn
            current_user = msg
            current_end_offset = end_offset
            assistant_order = []
            assistant_latest = {}
            tool_results_by_id = {}
            continue

        if role == "assistant":
            if current_user is None:
                # ignore assistant rows until we see a user message
                continue

            mid = get_message_id(msg) or f"noid:{len(assistant_order)}"
            if mid not in assistant_latest:
                assistant_order.append(mid)
            assistant_latest[mid] = msg
            current_end_offset = end_offset
            continue

        # unknown row type — never part of a turn, just tallied for visibility
        row_type = msg.get("type") if isinstance(msg.get("type"), str) else "unknown"
        unknown_counts[row_type] = unknown_counts.get(row_type, 0) + 1

    # flush last
    flush_turn()
    return turns, unknown_counts

# ----------------- Mode / name helpers (edits a, b) -----------------

def _detect_mode(payload: Any) -> str:
    """Inspect payload for permission/mode keys and map to a tag string."""
    if not isinstance(payload, dict):
        return "default-mode"
    for key in payload:
        key_lower = key.lower()
        if key_lower in ("permission_mode", "mode", "defaultmode"):
            val = str(payload[key]).lower()
            if "plan" in val:
                return "plan-mode"
            if "auto" in val:
                return "auto-mode"
    return "default-mode"


def _compose_trace_name(turn_num: int, user_text_raw: str) -> str:
    """Build a human-readable trace name with turn number and content preview."""
    if user_text_raw:
        first_line = user_text_raw.splitlines()[0].strip()
    else:
        first_line = ""

    # Collapse whitespace for snippet
    flat = " ".join(user_text_raw.split()) if user_text_raw else ""
    if len(flat) > 60:
        snippet = flat[:60] + "…"
    else:
        snippet = flat

    if first_line.startswith("/"):
        slash_cmd = first_line.split()[0] if first_line.split() else first_line
        return f"[{slash_cmd}] [Turn {turn_num}] {snippet}"
    return f"[Turn {turn_num}] {snippet}"


# ----------------- Claude version cache (edit f) -----------------

_CLAUDE_VERSION = None
_CLAUDE_VERSION_CHECKED = False


def _get_claude_version():
    global _CLAUDE_VERSION, _CLAUDE_VERSION_CHECKED
    if _CLAUDE_VERSION_CHECKED:
        return _CLAUDE_VERSION
    _CLAUDE_VERSION_CHECKED = True
    try:
        import subprocess
        result = subprocess.run(
            ["claude", "--version"],
            capture_output=True, text=True, timeout=2,
        )
        if result.returncode == 0:
            _CLAUDE_VERSION = result.stdout.strip() or None
    except Exception:
        _CLAUDE_VERSION = None
    return _CLAUDE_VERSION


# ----------------- Langfuse emit -----------------
def _to_ns(ts: Optional[datetime]) -> Optional[int]:
    """Convert a datetime to OTel-style nanoseconds since epoch."""
    if ts is None:
        return None
    return int(ts.timestamp() * 1_000_000_000)


def _start_backdated(langfuse: Langfuse, *, name: str, as_type: str,
                     start_time: Optional[datetime],
                     parent_otel_span: Any = None,
                     **obs_kwargs: Any) -> Any:
    """Create a Langfuse observation with an explicit OTel start_time.

    Bypasses langfuse.start_observation() (which has no start_time kwarg in
    SDK 4.x) by talking to the underlying OTel tracer directly and then
    wrapping the resulting span with the Langfuse observation type.

    Depends on SDK 4.x internals: langfuse._otel_tracer and
    langfuse._create_observation_from_otel_span. If a future SDK version
    renames or removes these, raise a clear error instead of letting an
    AttributeError get swallowed by the broad emit_turn handler.
    """
    if not hasattr(langfuse, "_otel_tracer") or not hasattr(langfuse, "_create_observation_from_otel_span"):
        try:
            sdk_version = getattr(__import__("langfuse"), "__version__", "unknown")
        except Exception:
            sdk_version = "unknown"
        raise RuntimeError(
            f"Langfuse SDK {sdk_version} is missing _otel_tracer or "
            f"_create_observation_from_otel_span. This hook targets SDK 4.x; "
            f"pin with `pip install \"langfuse>=4.0,<5\"` or update the hook script."
        )
    start_ns = _to_ns(start_time)
    if parent_otel_span is not None:
        with otel_trace_api.use_span(parent_otel_span, end_on_exit=False):
            otel_span = langfuse._otel_tracer.start_span(name=name, start_time=start_ns)
    else:
        otel_span = langfuse._otel_tracer.start_span(name=name, start_time=start_ns)
    return langfuse._create_observation_from_otel_span(
        otel_span=otel_span,
        as_type=as_type,
        **obs_kwargs,
    )


def emit_turn(
    langfuse: Langfuse,
    session_id: str,
    turn_num: int,
    turn: Turn,
    transcript_path: Path,
    user_id: str,
    cwd_label: str,
    mode: str,
    agent_context: Optional[Dict[str, str]] = None,
) -> None:
    user_text_raw = extract_text(get_content(turn.user_msg))
    user_text, user_text_meta = truncate_text(user_text_raw)

    last_assistant = turn.assistant_msgs[-1]
    final_assistant_text, _ = truncate_text(extract_text(get_content(last_assistant)))

    user_ts = parse_ts(turn.user_msg)
    last_assistant_ts = parse_ts(last_assistant)
    # Pick a turn end_time: latest among final assistant message or any tool result
    candidate_end_ts = [t for t in [last_assistant_ts] if t is not None]
    for tr in turn.tool_results_by_id.values():
        t = parse_ts(tr)
        if t is not None:
            candidate_end_ts.append(t)
    turn_end_ts = max(candidate_end_ts) if candidate_end_ts else None

    # Edit (b): compose trace name with content preview
    trace_name = _compose_trace_name(turn_num, user_text_raw)

    # Edit (a): user_id + richer tags including cwd and mode
    with propagate_attributes(
        session_id=session_id,
        trace_name=trace_name,
        tags=["claude-code", f"cwd:{cwd_label}", mode],
        user_id=user_id,
    ):
        # Build trace metadata; include agent context fields when present (subagent hooks only)
        trace_metadata: Dict[str, Any] = {
            "source": "claude-code",
            "turn_number": turn_num,
            "transcript_path": str(transcript_path),
            "assistant_message_count": len(turn.assistant_msgs),
        }
        if agent_context:
            trace_metadata.update(agent_context)

        # Edit (b): use composed trace_name for the span name too
        trace_span = _start_backdated(
            langfuse,
            name=trace_name,
            as_type="span",
            start_time=user_ts,
            input={"role": "user", "content": user_text},
            metadata=trace_metadata,
        )
        parent_otel_span = trace_span._otel_span

        # Iterate each assistant message: emit generation, then its tool_use children.
        # prev_ts = the moment the next generation could have started (= when the previous
        # batch of tool results all returned, or the original user message timestamp).
        prev_ts = user_ts
        prev_tool_results: List[Dict[str, Any]] = []  # populated after each batch, surfaced as next gen's input

        for idx, am in enumerate(turn.assistant_msgs):
            am_ts = parse_ts(am)
            am_text_raw = extract_text(get_content(am))
            am_text, am_text_meta = truncate_text(am_text_raw)
            model = get_model(am)
            tool_uses = iter_tool_uses(get_content(am))

            # Build generation input: user message for first generation, otherwise tool results from
            # the prior batch (best partial reconstruction of the prompt context).
            if idx == 0:
                gen_input: Any = {"role": "user", "content": user_text}
            elif prev_tool_results:
                gen_input = {"role": "tool", "tool_results": prev_tool_results}
            else:
                gen_input = None

            # Build generation output: include both the text response and any tool calls the LLM
            # decided to make. Most assistant messages in tool-using turns are tool-call-only, so
            # without tool_calls in the output, the observation looks empty.
            gen_tool_calls = []
            for tu in tool_uses:
                tu_input = tu.get("input")
                if isinstance(tu_input, str):
                    tu_input_serialized, _ = truncate_text(tu_input)
                else:
                    tu_input_serialized = tu_input
                gen_tool_calls.append({
                    "id": tu.get("id"),
                    "name": tu.get("name"),
                    "input": tu_input_serialized,
                })

            gen_output: Dict[str, Any] = {"role": "assistant"}
            if am_text:
                gen_output["content"] = am_text
            if gen_tool_calls:
                gen_output["tool_calls"] = gen_tool_calls

            gen_kwargs: Dict[str, Any] = dict(
                model=model,
                input=gen_input,
                output=gen_output,
                metadata={
                    "assistant_index": idx,
                    "assistant_text": am_text_meta,
                    "tool_count": len(tool_uses),
                },
            )
            usage_details = get_usage(am)
            if usage_details is not None:
                gen_kwargs["usage_details"] = usage_details

            gen_span = _start_backdated(
                langfuse,
                name=f"Claude Generation {idx + 1}",
                as_type="generation",
                start_time=prev_ts or am_ts,
                parent_otel_span=parent_otel_span,
                **gen_kwargs,
            )

            # Tool observations: nested under this generation. Each starts when the assistant
            # emitted the tool_use (am_ts) and ends when its tool_result row arrived.
            batch_result_ts: List[datetime] = []
            batch_tool_results: List[Dict[str, Any]] = []
            for tu in tool_uses:
                tid = str(tu.get("id") or "")
                tname = tu.get("name") or "unknown"
                tinput_raw = tu.get("input") if isinstance(tu.get("input"), (dict, list, str, int, float, bool)) else {}
                if isinstance(tinput_raw, str):
                    tinput, tinput_meta = truncate_text(tinput_raw)
                else:
                    tinput, tinput_meta = tinput_raw, None

                tr_entry = turn.tool_results_by_id.get(tid) if tid else None
                if tr_entry:
                    out_raw = tr_entry.get("content")
                    out_str = out_raw if isinstance(out_raw, str) else json.dumps(out_raw, ensure_ascii=False)
                    out_trunc, out_meta = truncate_text(out_str)
                    tr_ts = parse_ts(tr_entry.get("timestamp"))
                else:
                    out_trunc, out_meta, tr_ts = None, None, None
                if tr_ts is not None:
                    batch_result_ts.append(tr_ts)

                # Edit (d): as_type="agent" for orchestration tools
                tool_as_type = "agent" if tname in ("Skill", "Agent", "Task") else "tool"

                # Edit (e): level="ERROR" when tool failed
                is_error = bool(tr_entry and tr_entry.get("is_error"))
                if not is_error and isinstance(out_trunc, str):
                    if "Error: " in out_trunc or re.match(r"^[45]\d\d\b", out_trunc.strip()):
                        is_error = True
                extra_kwargs: Dict[str, Any] = {"level": "ERROR"} if is_error else {}

                tool_span = _start_backdated(
                    langfuse,
                    name=f"Tool: {tname}",
                    as_type=tool_as_type,
                    start_time=am_ts,
                    parent_otel_span=gen_span._otel_span,
                    input=tinput,
                    metadata={
                        "tool_name": tname,
                        "tool_id": tid,
                        "input_meta": tinput_meta,
                        "output_meta": out_meta,
                    },
                    **extra_kwargs,
                )
                tool_span.update(output=out_trunc)
                tool_span.end(end_time=_to_ns(tr_ts or am_ts))

                batch_tool_results.append({
                    "tool_use_id": tid,
                    "tool_name": tname,
                    "output": out_trunc,
                })

            # End the generation AFTER its tools so the timeline cleanly contains them.
            # If there were tool calls, gen ends with the last result; otherwise at am_ts.
            gen_end_ts = max(batch_result_ts) if batch_result_ts else am_ts
            gen_span.end(end_time=_to_ns(gen_end_ts or am_ts or prev_ts))

            # Carry this batch's results into the next generation's input.
            prev_tool_results = batch_tool_results

            # Advance prev_ts: next generation can only start after this batch's tool results returned.
            if batch_result_ts:
                prev_ts = max(batch_result_ts)
            elif am_ts is not None:
                prev_ts = am_ts

        trace_span.update(output={"role": "assistant", "content": final_assistant_text})
        trace_span.end(end_time=_to_ns(turn_end_ts or last_assistant_ts or user_ts))

# ----------------- Main -----------------
def main() -> int:
    start = time.time()
    debug("Hook started")

    public_key = _opt("LANGFUSE_PUBLIC_KEY") or _opt("CC_LANGFUSE_PUBLIC_KEY")
    secret_key = _opt("LANGFUSE_SECRET_KEY") or _opt("CC_LANGFUSE_SECRET_KEY")
    host = _opt("LANGFUSE_BASE_URL") or _opt("CC_LANGFUSE_BASE_URL") or "https://us.cloud.langfuse.com"

    if not public_key or not secret_key:
        return 0

    payload = read_hook_payload()
    session_id, transcript_path = extract_session_and_transcript(payload)

    if not session_id or not transcript_path:
        # No structured payload; fail open (do not guess)
        debug("Missing session_id or transcript_path from hook payload; exiting.")
        return 0

    if not transcript_path.exists():
        debug(f"Transcript path does not exist: {transcript_path}")
        return 0

    # Edit (a): compute user_id, cwd_label, mode once in main and thread through
    user_id = os.environ.get("LANGFUSE_USER_ID") or os.environ.get("USER") or ""
    cwd_label = os.path.basename(
        (payload.get("cwd") if isinstance(payload, dict) else None) or os.getcwd()
    )
    mode = _detect_mode(payload)
    agent_context = extract_agent_context(payload)

    langfuse = None
    try:
        # Edit (f): pass release= to Langfuse constructor
        # Bounded: a 5s timeout keeps a slow/unreachable host from stalling the
        # Stop hook during client construction (SDK 4.x supports this kwarg).
        langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host,
            timeout=5,
            release=os.environ.get("LANGFUSE_RELEASE") or _get_claude_version(),
        )
    except Exception:
        return 0

    try:
        with FileLock(LOCK_FILE):
            state = load_state()
            key = state_key(session_id, str(transcript_path))
            ss = load_session_state(state, key)

            rows, new_buffer, full_read_offset = read_new_jsonl(transcript_path, ss)
            if not rows:
                # Nothing new (or only an incomplete trailing line) — nothing
                # was attempted, so it's always safe to commit the full read.
                ss.offset = full_read_offset
                ss.buffer = new_buffer
                write_session_state(state, key, ss)
                save_state(state)
                return 0

            turns, unknown_counts = build_turns(rows)
            if unknown_counts:
                n = sum(unknown_counts.values())
                debug(f"skipped {n} unknown transcript rows: {sorted(unknown_counts)}")

            if not turns:
                # Rows existed but none formed a complete turn (e.g. a dangling
                # user message with no reply yet) — nothing was attempted here
                # either, so the full read is still safe to commit.
                ss.offset = full_read_offset
                ss.buffer = new_buffer
                write_session_state(state, key, ss)
                save_state(state)
                return 0

            # Emit turns strictly in order, committing progress one turn at a
            # time so a failure never drops turns that already succeeded, and
            # never silently skips a turn that hasn't (the old bug: offset and
            # turn_count both advanced past every turn in the batch regardless
            # of whether emit_turn raised).
            emitted = 0
            committed_offset = ss.offset
            stopped_early = False

            for i, t in enumerate(turns):
                turn_num = ss.turn_count + i + 1
                # The offset this turn starts at is its identity across retries:
                # whichever turn is currently "stuck" always starts at the same
                # offset each time it's re-attempted, since offset never moves
                # past a failing turn. This holds regardless of the turn's
                # position within any one run's batch (i is just this run's
                # local index, not a stable identity).
                turn_start_offset = committed_offset
                try:
                    emit_turn(
                        langfuse, session_id, turn_num, t, transcript_path,
                        user_id=user_id, cwd_label=cwd_label, mode=mode,
                        agent_context=agent_context,
                    )
                except Exception as e:
                    # Log at INFO so SDK incompatibilities (and other emit failures)
                    # are visible without needing CC_LANGFUSE_DEBUG=true; the full
                    # message (which may include payload fragments) stays at debug.
                    info(f"emit_turn failed: {type(e).__name__}")
                    debug(f"emit_turn failed: {type(e).__name__}: {e}")

                    if ss.poison_offset == turn_start_offset:
                        fail_count = ss.poison_fail_count + 1
                    else:
                        fail_count = 1

                    if fail_count >= 3:
                        # Poison-turn guard: this turn has now failed 3 times.
                        # Force past it so the pipeline can't wedge permanently.
                        info("skipping turn after 3 failed emits")
                        emitted += 1
                        committed_offset = t.end_offset
                        ss.poison_offset = None
                        ss.poison_fail_count = 0
                        continue

                    ss.poison_offset = turn_start_offset
                    ss.poison_fail_count = fail_count
                    stopped_early = True
                    break
                else:
                    emitted += 1
                    committed_offset = t.end_offset
                    if ss.poison_offset == turn_start_offset:
                        ss.poison_offset = None
                        ss.poison_fail_count = 0

            ss.turn_count += emitted
            if stopped_early:
                # Leave offset/buffer at the last success — next Stop event
                # naturally re-reads and retries the failed turn. The buffer
                # is discarded rather than persisted: it describes bytes past
                # committed_offset, which will be re-read from disk next time.
                ss.offset = committed_offset
                ss.buffer = ""
            else:
                ss.offset = full_read_offset
                ss.buffer = new_buffer
            write_session_state(state, key, ss)
            save_state(state)

        dur = time.time() - start
        deferred = len(turns) - emitted
        deferred_note = f", {deferred} turn(s) deferred for retry" if deferred else ""
        info(f"Processed {emitted} turns in {dur:.2f}s (session={session_id}){deferred_note}")

        # Emit a bare BEL via terminalSequence so the terminal gives a subtle
        # flush signal when traces land. Hooks run without a controlling tty so
        # this must go through Claude Code's terminal write path rather than
        # directly to /dev/tty.
        try:
            print(json.dumps({"terminalSequence": "\x07"}))
        except Exception:
            pass

        return 0

    except TimeoutError as e:
        debug(f"lock timeout, skipping: {e}")
        return 0

    except Exception as e:
        debug(f"Unexpected failure: {e}")
        return 0

    finally:
        # Cap flush+shutdown at 5s so a slow/unreachable Langfuse can't stall Claude Code.
        if langfuse is not None:
            try:
                def _flush_and_shutdown():
                    try:
                        langfuse.flush()
                    except Exception:
                        pass
                    langfuse.shutdown()
                t = threading.Thread(target=_flush_and_shutdown, daemon=True)
                t.start()
                t.join(5.0)
            except Exception:
                pass

if __name__ == "__main__":
    sys.exit(main())

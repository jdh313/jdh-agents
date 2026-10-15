# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8.0"]
# ///
"""Behavioral tests for the Claude Code human follow-up pass in the Langfuse hook.

Every transcript here is synthetic. The `langfuse` and `opentelemetry` modules
are stubbed, so nothing leaves the process.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import types
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "plugins" / "langfuse" / "hooks" / "langfuse_hook.py"

SID = "sess-followup-1"
BASE = datetime(2026, 10, 15, 10, 0, 0, tzinfo=timezone.utc)
PUBLIC_KEY = "pk-lf-testpublic"
SECRET_KEY = "sk-lf-testsecret"
SELF_HOSTED = "https://langfuse.example.test"

PROPAGATED: list = []


@pytest.fixture(scope="module")
def hook():
    langfuse = types.ModuleType("langfuse")
    langfuse.Langfuse = object

    @contextmanager
    def propagate_attributes(**kwargs):
        PROPAGATED.append(kwargs)
        yield

    langfuse.propagate_attributes = propagate_attributes
    opentelemetry = types.ModuleType("opentelemetry")

    @contextmanager
    def use_span(_span, end_on_exit=False):
        yield

    opentelemetry.trace = types.SimpleNamespace(use_span=use_span)
    sys.modules["langfuse"] = langfuse
    sys.modules["opentelemetry"] = opentelemetry

    spec = importlib.util.spec_from_file_location("langfuse_followup_under_test", HOOK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENV_NAMES = [
    "CC_LANGFUSE_FOLLOWUP_ENABLED", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY",
    "LANGFUSE_BASE_URL", "CC_LANGFUSE_PUBLIC_KEY", "CC_LANGFUSE_SECRET_KEY",
    "CC_LANGFUSE_BASE_URL",
]


@pytest.fixture
def env(hook, monkeypatch, tmp_path):
    """Enabled, self-hosted configuration with state redirected to tmp_path."""
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
        monkeypatch.delenv(f"CLAUDE_PLUGIN_OPTION_{name}", raising=False)
    for name in ("LANGFUSE_CLAUDE_FEEDBACK_ENABLED", "LANGFUSE_TRACING_ENABLED", "PLUGIN_ROOT"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_CC_LANGFUSE_FOLLOWUP_ENABLED", "true")
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_LANGFUSE_PUBLIC_KEY", PUBLIC_KEY)
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_LANGFUSE_SECRET_KEY", SECRET_KEY)
    monkeypatch.setenv("CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL", SELF_HOSTED)
    monkeypatch.setattr(hook, "RUNTIME", "claude-code")
    state_dir = tmp_path / "state"
    monkeypatch.setattr(hook, "STATE_DIR", state_dir)
    monkeypatch.setattr(hook, "STATE_FILE", state_dir / "langfuse_state.json")
    monkeypatch.setattr(hook, "LOCK_FILE", state_dir / "langfuse_state.lock")
    monkeypatch.setattr(hook, "LOG_FILE", state_dir / "langfuse_hook.log")
    monkeypatch.setattr(hook, "FOLLOWUP_STATE_FILE", state_dir / "langfuse_followup_state.json")
    monkeypatch.setattr(hook, "FOLLOWUP_LOCK_FILE", state_dir / "langfuse_followup.lock")
    logs: list = []
    monkeypatch.setattr(hook, "info", lambda msg: logs.append(("info", msg)))
    monkeypatch.setattr(hook, "debug", lambda msg: logs.append(("debug", msg)))
    monkeypatch.setattr(hook, "_get_runtime_version", lambda: "2.1.300 (Claude Code)")
    return types.SimpleNamespace(state_dir=state_dir, tmp=tmp_path, logs=logs)


# ----------------- synthetic transcript builders -----------------
def T(seconds: float) -> str:
    return (BASE + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")


def human(uuid, parent, t, content, **extra):
    row = {
        "type": "user", "uuid": uuid, "parentUuid": parent, "sessionId": SID,
        "timestamp": T(t), "entrypoint": "cli", "isSidechain": False,
        "origin": {"kind": "human"},
        "message": {"role": "user", "content": content},
    }
    row.update(extra)
    return row


def user_row(uuid, parent, t, content, **extra):
    """A user-typed row without a human origin (commands, interrupts, ...)."""
    row = human(uuid, parent, t, content, **extra)
    row.pop("origin")
    return row


def asst(uuid, parent, t, mid, blocks, model="claude-test-model"):
    return {
        "type": "assistant", "uuid": uuid, "parentUuid": parent, "sessionId": SID,
        "timestamp": T(t), "entrypoint": "cli", "isSidechain": False,
        "message": {"id": mid, "role": "assistant", "model": model, "content": blocks},
    }


def text(s):
    return [{"type": "text", "text": s}]


def tool_result(uuid, parent, t, tool_id, **extra):
    row = user_row(uuid, parent, t, [{"type": "tool_result", "tool_use_id": tool_id, "content": "ok"}])
    row["toolUseResult"] = {"stdout": "ok"}
    row.update(extra)
    return row


def session_state(started=0, cursor=None, recent=None):
    return {
        "started_at": T(started),
        "cursor": T(cursor if cursor is not None else started),
        "recent_uuids": list(recent or []),
    }


def by_uuid(outcomes):
    return {o.uuid: o for o in outcomes}


def write_transcript(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def write_followup_state(hook, state):
    hook.STATE_DIR.mkdir(parents=True, exist_ok=True)
    hook.FOLLOWUP_STATE_FILE.write_text(json.dumps(state), encoding="utf-8")


def read_followup_state(hook):
    return json.loads(hook.FOLLOWUP_STATE_FILE.read_text(encoding="utf-8"))


# ----------------- 1 + 2: pairing and first message -----------------
def split_turn_rows():
    return [
        human("h1", None, 10, "please inspect the repo"),
        asst("a1", "h1", 11, "m1", [{"type": "thinking", "thinking": "hmm"}]),
        asst("a2", "a1", 12, "m1", text("Let me check.")),
        asst("a3", "a2", 13, "m1", [{"type": "tool_use", "id": "tu1", "name": "Bash", "input": {}}]),
        tool_result("t1", "a3", 14, "tu1"),
        asst("a4", "t1", 15, "m2", text("Part one.")),
        asst("a5", "a4", 16, "m2", [{"type": "tool_use", "id": "tu2", "name": "Read", "input": {}}]),
        tool_result("t2", "a5", 17, "tu2"),
        asst("a6", "t2", 18, "m3", [{"type": "tool_use", "id": "tu3", "name": "Read", "input": {}}]),
        tool_result("t3", "a6", 19, "tu3"),
        asst("a7", "t3", 20, "m4", text("Final answer,")),
        asst("a8", "a7", 21, "m4", [{"type": "thinking", "thinking": "x"}]),
        asst("a9", "a8", 22, "m4", text("in two blocks.")),
        human("h2", "a9", 30, "thanks, now fix it"),
    ]


def test_pairs_with_last_text_group_across_split_rows_and_tools(hook, env):
    outcomes = by_uuid(hook.plan_followups(split_turn_rows(), SID, session_state()))

    record = outcomes["h2"].record
    assert record is not None
    assert record.preceding_text == "please inspect the repo"
    assert record.response_text == "Final answer,\nin two blocks."
    assert record.assistant_entry_id == "a9"
    assert record.assistant_message_id == "m4"
    assert record.agent_model == "claude-test-model"
    assert record.followup_text == "thanks, now fix it"
    assert record.submission_kind == "prompt"
    assert record.interrupted_before_followup is False


def test_first_message_of_session_is_skipped(hook, env):
    outcomes = by_uuid(hook.plan_followups(split_turn_rows(), SID, session_state()))
    assert outcomes["h1"].record is None
    assert outcomes["h1"].skip_reason == "no_preceding_human"


# ----------------- 3: exclusions -----------------
def excluded_rows():
    """Rows that must never be a follow-up nor a preceding request."""
    return [
        tool_result("x-tool", "a1", 12, "tu1", origin={"kind": "human"}),
        human("x-meta", "x-tool", 13, "Base directory for this skill: ...", isMeta=True),
        human("x-peer", "x-meta", 14, "teammate says hi", origin={"kind": "peer"}),
        human("x-task", "x-peer", 15, "<task-notification>done</task-notification>",
              origin={"kind": "task-notification"}),
        human("x-side", "x-task", 16, "sidechain prompt", isSidechain=True),
        human("x-sdk", "x-side", 17, "programmatic prompt", entrypoint="sdk-cli"),
        user_row("x-local", "x-sdk", 18,
                 "<command-name>/clear</command-name>\n<local-command-stdout></local-command-stdout>"),
        user_row("x-bash", "x-local", 19, "<bash-input>ls</bash-input>"),
        human("x-compact", "x-bash", 20, "This session is being continued from a previous conversation",
              isCompactSummary=True),
        human("x-other-session", "x-compact", 21, "other session", sessionId="someone-else"),
    ]


def test_excluded_rows_are_never_candidates_or_preceding(hook, env):
    excluded = excluded_rows()
    for row in excluded:
        assert hook.is_genuine_human_row(row, SID) is False, row["uuid"]

    # Rows that end the walk stay off the path here: a foreign-session row aborts
    # it, and a human-origin row that is not exportable (sdk-cli) is a boundary
    # (see test_walk_stops_at_nearest_human_even_without_exportable_text).
    on_path = [r for r in excluded if r["uuid"] not in ("x-other-session", "x-sdk")]
    for i, row in enumerate(on_path):  # relink the chain around the removed rows
        row["parentUuid"] = on_path[i - 1]["uuid"] if i else "a1"
    rows = [
        human("h1", None, 10, "first request"),
        asst("a1", "h1", 11, "m1", text("first answer")),
        *on_path,
        human("h2", on_path[-1]["uuid"], 30, "follow-up"),
    ]
    outcomes = hook.plan_followups(rows, SID, session_state())

    assert [o.uuid for o in outcomes] == ["h1", "h2"]
    record = by_uuid(outcomes)["h2"].record
    assert record is not None
    assert record.preceding_uuid == "h1"
    assert record.response_text == "first answer"


def test_foreign_session_row_on_path_skips(hook, env):
    rows = [
        human("h1", None, 10, "first"),
        asst("a1", "h1", 11, "m1", text("answer")),
        asst("a2", "a1", 12, "m2", text("other"), model="x") | {"sessionId": "elsewhere"},
        human("h2", "a2", 20, "next"),
    ]
    outcome = by_uuid(hook.plan_followups(rows, SID, session_state()))["h2"]
    assert outcome.record is None
    assert outcome.skip_reason == "foreign_session_on_path"


# ----------------- 4: subagents -----------------
def test_subagent_payload_and_path_produce_nothing(hook, env):
    rows = split_turn_rows()
    main_path = write_transcript(env.tmp / "proj" / f"{SID}.jsonl", rows)
    sub_path = write_transcript(env.tmp / "proj" / SID / "subagents" / "agent-1.jsonl", rows)
    write_followup_state(hook, {SID: session_state()})
    emitted: list = []

    hook.run_followup_pass({"agent_id": "agent-1"}, SID, main_path, emit=emitted.append)
    hook.run_followup_pass({}, SID, sub_path, emit=emitted.append)

    assert emitted == []
    assert read_followup_state(hook) == {SID: session_state()}


# ----------------- 5: rewind -----------------
def test_rewind_pairs_with_live_branch_not_abandoned_one(hook, env):
    rows = [
        human("h1", None, 10, "start"),
        asst("a1", "h1", 11, "m1", text("first answer")),
        human("h2-old", "a1", 12, "abandoned question"),
        asst("a2-old", "h2-old", 13, "m2", text("abandoned reply")),
        human("h2-live", "a1", 20, "rewritten question"),
        asst("a2-live", "h2-live", 21, "m3", text("live reply")),
        # Abandoned-branch rows physically between the live reply and the follow-up.
        human("h3-old", "a2-old", 22, "abandoned follow-up"),
        asst("a3-old", "h3-old", 23, "m4", text("abandoned again")),
        human("h3", "a2-live", 30, "follow-up on live branch"),
    ]
    record = by_uuid(hook.plan_followups(rows, SID, session_state()))["h3"].record
    assert record is not None
    assert record.preceding_uuid == "h2-live"
    assert record.preceding_text == "rewritten question"
    assert record.response_text == "live reply"


# ----------------- 6: resume / fork -----------------
def resumed_rows():
    # Copied history keeps its original uuid/timestamp; sessionId is rewritten.
    return [
        human("old-h", None, -100, "copied question"),
        asst("old-a", "old-h", -99, "m0", text("copied answer")),
        human("new-h1", "old-a", 10, "first message after resume"),
        asst("new-a1", "new-h1", 11, "m1", text("fresh answer")),
        human("new-h2", "new-a1", 20, "second message after resume"),
    ]


def test_resume_skips_copied_rows_and_first_new_message(hook, env):
    outcomes = by_uuid(hook.plan_followups(resumed_rows(), SID, session_state(started=0)))

    assert "old-h" not in outcomes
    assert outcomes["new-h1"].record is None
    assert outcomes["new-h1"].skip_reason == "preceding_before_session_start"
    record = outcomes["new-h2"].record
    assert record is not None
    assert record.preceding_uuid == "new-h1"
    assert record.response_text == "fresh answer"


# ----------------- 7: compaction -----------------
def test_compaction_boundary_is_crossed_via_logical_parent(hook, env):
    rows = [
        human("h1", None, 10, "long request"),
        asst("a1", "h1", 11, "m1", text("long answer")),
        {"type": "system", "subtype": "compact_boundary", "uuid": "cb", "parentUuid": None,
         "logicalParentUuid": "a1", "sessionId": SID, "timestamp": T(12)},
        human("summary", "cb", 13, "This session is being continued...", isCompactSummary=True),
        human("h2", "summary", 20, "carry on"),
    ]
    record = by_uuid(hook.plan_followups(rows, SID, session_state()))["h2"].record
    assert record is not None
    assert record.preceding_uuid == "h1"
    assert record.response_text == "long answer"


def test_missing_and_cyclic_ancestry_skip(hook, env):
    rows = [
        human("h1", "ghost", 10, "orphan"),
        asst("c1", "c2", 11, "m1", text("loop")),
        asst("c2", "c1", 12, "m2", text("loop")),
        human("h2", "c2", 20, "cyclic"),
    ]
    outcomes = by_uuid(hook.plan_followups(rows, SID, session_state()))
    assert outcomes["h1"].skip_reason == "missing_ancestry"
    assert outcomes["h2"].skip_reason == "cyclic_ancestry"


# ----------------- 8: interrupts -----------------
def test_interrupted_preceding_human_without_text_skips_without_jumping_back(hook, env):
    rows = [
        human("h1", None, 10, "first"),
        asst("a1", "h1", 11, "m1", text("first answer")),
        human("h2", "a1", 20, "second"),
        asst("a2", "h2", 21, "m2", [{"type": "tool_use", "id": "tu", "name": "Bash", "input": {}}]),
        user_row("int", "a2", 22, text("[Request interrupted by user for tool use]")),
        human("h3", "int", 30, "do something else"),
    ]
    outcome = by_uuid(hook.plan_followups(rows, SID, session_state()))["h3"]
    assert outcome.record is None
    assert outcome.skip_reason == "no_assistant_text"


def test_interrupt_after_partial_text_is_flagged(hook, env):
    rows = [
        human("h1", None, 10, "first"),
        asst("a1", "h1", 11, "m1", text("partial answer")),
        user_row("int", "a1", 12, text("[Request interrupted by user]")),
        human("h2", "int", 20, "stop, try again"),
    ]
    record = by_uuid(hook.plan_followups(rows, SID, session_state()))["h2"].record
    assert record is not None
    assert record.response_text == "partial answer"
    assert record.interrupted_before_followup is True


# ----------------- 9: cursor / ledger / cap -----------------
def test_repeated_invocation_emits_nothing_new_and_ties_still_process(hook, env):
    rows = split_turn_rows()
    path = write_transcript(env.tmp / f"{SID}.jsonl", rows)
    write_followup_state(hook, {SID: session_state()})
    emitted: list = []

    first = hook.run_followup_pass({}, SID, path, emit=emitted.append)
    assert first == {"emitted": 1, "skipped": 1, "failed": 0}
    state = read_followup_state(hook)[SID]
    assert state["cursor"] == T(30)
    assert state["recent_uuids"] == ["h1", "h2"]

    second = hook.run_followup_pass({}, SID, path, emit=emitted.append)
    assert second == {"emitted": 0, "skipped": 0, "failed": 0}
    assert len(emitted) == 1

    # A new submission sharing the cursor timestamp is still picked up once.
    rows += [asst("a10", "h2", 30, "m9", text("fixed")), human("h3", "a10", 30, "great")]
    write_transcript(path, rows)
    third = hook.run_followup_pass({}, SID, path, emit=emitted.append)
    assert third["emitted"] == 1
    assert emitted[-1]["output"] == {"latest_user_message": "great"}
    assert hook.run_followup_pass({}, SID, path, emit=emitted.append)["emitted"] == 0


def test_candidates_are_capped_oldest_first(hook, env):
    rows = [human("h0", None, 0.5, "q0")]
    parent = "h0"
    for i in range(1, 61):
        rows.append(asst(f"a{i}", parent, i, f"m{i}", text(f"answer {i}")))
        rows.append(human(f"h{i}", f"a{i}", i + 0.5, f"q{i}"))
        parent = f"h{i}"
    path = write_transcript(env.tmp / f"{SID}.jsonl", rows)
    write_followup_state(hook, {SID: session_state()})
    emitted: list = []

    hook.run_followup_pass({}, SID, path, emit=emitted.append)
    assert len(emitted) == 49  # 50 candidates, h0 is a first message
    assert emitted[-1]["metadata"]["followup_entry_id"] == "h49"
    hook.run_followup_pass({}, SID, path, emit=emitted.append)
    assert len(emitted) == 60
    assert len(read_followup_state(hook)[SID]["recent_uuids"]) <= hook.FOLLOWUP_RECENT_UUIDS


def test_missing_session_record_starts_now_without_backfill(hook, env):
    path = write_transcript(env.tmp / f"{SID}.jsonl", split_turn_rows())
    emitted: list = []
    now = BASE + timedelta(hours=1)

    hook.run_followup_pass({}, SID, path, emit=emitted.append, now=now)

    assert emitted == []
    state = read_followup_state(hook)[SID]
    assert state["started_at"] == state["cursor"] == now.isoformat().replace("+00:00", "Z")
    assert hook.run_followup_pass({}, SID, path, emit=emitted.append)["emitted"] == 0


# ----------------- 10: truncation + masking -----------------
def test_truncation_metadata_and_credential_masking(hook, env):
    long_answer = "x" * 25_000
    rows = [
        human("h1", None, 10, f"my key is {SECRET_KEY} and {PUBLIC_KEY} and sk-lf-other-123"),
        asst("a1", "h1", 11, "m1", text(long_answer)),
        human("h2", "a1", 20, "pk-lf-zzz leaked again"),
    ]
    record = by_uuid(hook.plan_followups(rows, SID, session_state()))["h2"].record
    config = hook.followup_config()
    obs = hook.build_followup_observation(record, config, "2.1.300 (Claude Code)")

    redacted = "[redacted-langfuse-secret]"
    assert obs["input"]["preceding_user_request"] == f"my key is {redacted} and {redacted} and {redacted}"
    assert obs["output"]["latest_user_message"] == f"{redacted} leaked again"
    assert len(obs["input"]["assistant_response"]) == 20_000
    trunc = obs["metadata"]["truncation"]
    assert trunc["assistant_response"] == {"original_chars": 25_000, "exported_chars": 20_000, "truncated": True}
    assert trunc["latest_user_message"]["truncated"] is False
    assert SECRET_KEY not in json.dumps([obs["input"], obs["output"], obs["metadata"]])

    meta = obs["metadata"]
    assert meta["source"] == "claude-code-feedback"
    assert meta["contract"] == "human-followup" and meta["contract_version"] == 1
    assert meta["schema_version"] == 1 and meta["harness"] == "claude-code"
    assert meta["harness_version"] == "2.1.300 (Claude Code)"
    assert meta["capture_semantics"] == "transcript-ancestry"
    assert meta["max_chars_per_field"] == 20_000
    assert meta["submitted_at"] == T(20)
    assert meta["followup_entry_id"] == "h2" and meta["preceding_user_entry_id"] == "h1"
    assert meta["assistant_entry_id"] == "a1" and meta["assistant_message_id"] == "m1"
    assert obs["name"] == obs["trace_name"] == "Claude Code Human Follow-up"
    assert obs["tags"] == ["claude-code", "claude-code-feedback"]


# ----------------- 11: gating -----------------
DISABLED_CASES = {
    "flag-unset": {"CLAUDE_PLUGIN_OPTION_CC_LANGFUSE_FOLLOWUP_ENABLED": None},
    "flag-false": {"CLAUDE_PLUGIN_OPTION_CC_LANGFUSE_FOLLOWUP_ENABLED": "false"},
    "kill-switch": {"LANGFUSE_CLAUDE_FEEDBACK_ENABLED": "false"},
    "kill-switch-0": {"LANGFUSE_CLAUDE_FEEDBACK_ENABLED": "0"},
    "tracing-disabled": {"LANGFUSE_TRACING_ENABLED": "0"},
    "default-cloud-url": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL": "https://us.cloud.langfuse.com"},
    "apex-cloud-url": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL": "https://langfuse.com"},
    "base-url-empty": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL": None},
    "url-userinfo": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL": "https://u:p@langfuse.example.test"},
    "url-query": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL": "https://langfuse.example.test/?a=1"},
    "url-fragment": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL": "https://langfuse.example.test/#x"},
    "url-scheme": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_BASE_URL": "ftp://langfuse.example.test"},
    "missing-secret": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_SECRET_KEY": None},
    "op-reference": {"CLAUDE_PLUGIN_OPTION_LANGFUSE_SECRET_KEY": "op://vault/item/secret"},
}


@pytest.mark.parametrize("case", sorted(DISABLED_CASES))
def test_disabled_config_emits_nothing_and_writes_no_state(hook, env, monkeypatch, case):
    for name, value in DISABLED_CASES[case].items():
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    path = write_transcript(env.tmp / f"{SID}.jsonl", split_turn_rows())
    emitted: list = []

    assert hook.followup_config() is None
    hook.run_followup_pass({}, SID, path, emit=emitted.append)
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": SID})))
    assert hook.session_start_main() == 0

    assert emitted == []
    assert not hook.FOLLOWUP_STATE_FILE.exists()


def test_codex_runtime_is_a_no_op(hook, env, monkeypatch):
    monkeypatch.setattr(hook, "RUNTIME", "codex")
    path = write_transcript(env.tmp / f"{SID}.jsonl", split_turn_rows())
    emitted: list = []
    assert hook.followup_config() is None
    hook.run_followup_pass({}, SID, path, emit=emitted.append)
    assert emitted == [] and not hook.FOLLOWUP_STATE_FILE.exists()


def test_self_hosted_config_is_enabled(hook, env):
    config = hook.followup_config()
    assert config is not None and config.base_url == SELF_HOSTED
    for allowed in ("http://localhost:3000", "https://langfuse.example.test/base/", "https://notlangfuse.com"):
        assert hook._is_self_hosted_url(allowed), allowed
    for refused in ("https://cloud.langfuse.com", "https://EU.Cloud.Langfuse.com.", "langfuse.example.test"):
        assert not hook._is_self_hosted_url(refused), refused


# ----------------- 12: isolation from the turn pass + SessionStart -----------------
class FakeObservation:
    def __init__(self, sink, name, kwargs):
        self.record = {"name": name, **kwargs}
        self._otel_span = object()
        sink.append(self.record)

    def update(self, **kwargs):
        self.record.update(kwargs)

    def end(self, end_time=None):
        self.record["end_time"] = end_time


class FakeLangfuse:
    instances: list = []

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.observations: list = []
        self._pending_name = None
        tracer = types.SimpleNamespace(start_span=self._start_span)
        self._otel_tracer = tracer
        FakeLangfuse.instances.append(self)

    def _start_span(self, name, start_time=None):
        self._pending_name = name
        return name

    def _create_observation_from_otel_span(self, otel_span, as_type, **kwargs):
        return FakeObservation(self.observations, otel_span, {"as_type": as_type, **kwargs})

    def flush(self):
        pass

    def shutdown(self):
        pass


def test_emit_failure_is_swallowed_and_turn_pass_is_unaffected(hook, env, monkeypatch, capsys):
    rows = split_turn_rows()
    path = write_transcript(env.tmp / f"{SID}.jsonl", rows)
    write_followup_state(hook, {SID: session_state()})
    monkeypatch.setattr(hook, "Langfuse", FakeLangfuse)
    calls: list = []

    def failing_emit(_langfuse, observation, _user_id):
        calls.append(observation["metadata"]["followup_entry_id"])
        raise RuntimeError("boom with secret payload text")

    monkeypatch.setattr(hook, "emit_followup", failing_emit)
    payload = json.dumps({"session_id": SID, "transcript_path": str(path)})

    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    assert hook.main() == 0

    # Turn pass: full read committed and turns emitted as before.
    turn_state = json.loads(hook.STATE_FILE.read_text())
    (entry,) = turn_state.values()
    assert entry["offset"] == path.stat().st_size
    assert entry["turn_count"] == 1
    fake = FakeLangfuse.instances[-1]
    assert any(o["as_type"] == "generation" for o in fake.observations)
    # Follow-up: attempted once, marked processed, failure logged by type only.
    assert calls == ["h2"]
    assert read_followup_state(hook)[SID]["recent_uuids"] == ["h1", "h2"]
    assert ("info", "emit_followup failed: RuntimeError") in env.logs
    assert not any("boom" in msg for _lvl, msg in env.logs if _lvl == "info")
    # Only the turn pass's BEL line reaches stdout.
    assert capsys.readouterr().out == json.dumps({"terminalSequence": "\x07"}) + "\n"

    # Not retried on the next Stop.
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    assert hook.main() == 0
    assert calls == ["h2"]


def test_followup_runs_when_turn_pass_has_no_new_rows(hook, env, monkeypatch):
    rows = split_turn_rows()
    path = write_transcript(env.tmp / f"{SID}.jsonl", rows)
    monkeypatch.setattr(hook, "Langfuse", FakeLangfuse)
    payload = json.dumps({"session_id": SID, "transcript_path": str(path)})

    # First Stop: turn pass consumes the file; follow-up has no record -> starts now.
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    assert hook.main() == 0
    # Pretend SessionStart had recorded an earlier start, then Stop again with no new bytes.
    write_followup_state(hook, {SID: session_state()})
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))
    assert hook.main() == 0

    spans = [o for o in FakeLangfuse.instances[-1].observations if o["name"] == "Claude Code Human Follow-up"]
    assert len(spans) == 1
    span = spans[0]
    assert span["as_type"] == "span"
    assert span["output"] == {"latest_user_message": "thanks, now fix it"}
    assert span["end_time"] == int(datetime.fromisoformat(T(30).replace("Z", "+00:00")).timestamp() * 1e9)
    assert PROPAGATED[-1]["trace_name"] == "Claude Code Human Follow-up"
    assert PROPAGATED[-1]["session_id"] == SID
    assert PROPAGATED[-1]["tags"] == ["claude-code", "claude-code-feedback"]


def test_session_start_records_earliest_and_prints_nothing(hook, env, monkeypatch, capsys):
    monkeypatch.setattr(hook, "Langfuse", None)  # constructing a client would raise
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": SID, "source": "startup"})))
    assert hook.session_start_main() == 0
    first = read_followup_state(hook)[SID]
    assert parse(first["started_at"]) is not None

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"session_id": SID, "source": "compact"})))
    assert hook.session_start_main() == 0
    assert read_followup_state(hook)[SID] == first
    assert capsys.readouterr().out == ""


def parse(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


# ----------------- 13: slash commands -----------------
def test_slash_command_rendering_and_submission_kind(hook, env):
    rows = [
        human("h1", None, 10, "first"),
        asst("a1", "h1", 11, "m1", text("answer")),
        human("h2", "a1", 20,
              "<command-message>review</command-message>\n<command-name>/review</command-name>\n"
              "<command-args>PR 42 carefully</command-args>"),
        human("h2-body", "h2", 20.1, text("Expanded skill body"), isMeta=True),
        asst("a2", "h2-body", 21, "m2", text("reviewed")),
        human("h3", "a2", 30, text(
            "<command-message>commit:commit</command-message>\n<command-name>/commit:commit</command-name>\n"
            "<command-args></command-args>")),
        asst("a3", "h3", 31, "m3", text("committed")),
        human("h4", "a3", 40, [
            {"type": "text", "text": "<system-reminder>ignore me</system-reminder>looks good"},
            {"type": "image", "source": {"data": "..."}},
        ]),
    ]
    outcomes = by_uuid(hook.plan_followups(rows, SID, session_state()))

    assert outcomes["h2"].record.followup_text == "/review PR 42 carefully"
    assert outcomes["h2"].record.submission_kind == "slash_command"
    h3 = outcomes["h3"].record
    assert h3.followup_text == "/commit:commit"
    assert h3.preceding_text == "/review PR 42 carefully"
    assert h3.response_text == "reviewed"
    assert outcomes["h4"].record.followup_text == "looks good"
    assert outcomes["h4"].record.submission_kind == "prompt"
    assert "h2-body" not in outcomes


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))


def test_walk_stops_at_nearest_human_even_without_exportable_text(hook, env):
    # h2 is image-only: walking past it would pair h3 with a reply to h2.
    rows = [
        human("h1", None, 10, "first request"),
        asst("a1", "h1", 11, "m1", text("reply to first")),
        human("h2", "a1", 20, [{"type": "image", "source": {"data": "..."}}]),
        asst("a2", "h2", 21, "m2", text("reply to the screenshot")),
        human("h3", "a2", 30, "that is wrong"),
    ]
    outcomes = by_uuid(hook.plan_followups(rows, SID, session_state()))
    assert "h2" not in outcomes  # no text: never a candidate
    assert outcomes["h3"].record is None
    assert outcomes["h3"].skip_reason == "preceding_human_not_eligible"


def test_command_markup_inside_a_typed_prompt_stays_a_prompt(hook, env):
    typed = "why did you print <command-name>/clear</command-name> here?"
    assert hook.normalize_human_text(typed) == (typed, "prompt")

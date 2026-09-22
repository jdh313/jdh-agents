# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8.0"]
# ///
"""Parser contract tests for the dual-runtime Langfuse hook."""

from __future__ import annotations

import importlib.util
import sys
import types
from contextlib import contextmanager
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "plugins" / "langfuse" / "hooks" / "langfuse_hook.py"


@pytest.fixture(scope="module")
def hook():
    langfuse = types.ModuleType("langfuse")
    langfuse.Langfuse = object

    @contextmanager
    def propagate_attributes(**_kwargs):
        yield

    langfuse.propagate_attributes = propagate_attributes
    opentelemetry = types.ModuleType("opentelemetry")
    opentelemetry.trace = types.SimpleNamespace()
    sys.modules["langfuse"] = langfuse
    sys.modules["opentelemetry"] = opentelemetry

    spec = importlib.util.spec_from_file_location("langfuse_hook_under_test", HOOK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_claude_rows_keep_existing_turn_shape(hook):
    rows = [
        ({
            "type": "user",
            "timestamp": "2026-09-21T10:00:00Z",
            "message": {"role": "user", "content": [{"type": "text", "text": "hello"}]},
        }, 10),
        ({
            "type": "assistant",
            "timestamp": "2026-09-21T10:00:01Z",
            "message": {
                "id": "msg-1",
                "role": "assistant",
                "model": "claude-test",
                "content": [{"type": "text", "text": "hi"}],
            },
        }, 20),
    ]

    turns, unknown = hook.build_turns(rows)

    assert unknown == {}
    assert len(turns) == 1
    assert hook.extract_text(hook.get_content(turns[0].user_msg)) == "hello"
    assert hook.get_model(turns[0].assistant_msgs[0]) == "claude-test"
    assert turns[0].end_offset == 20


def test_codex_rows_map_messages_tools_model_and_timestamps(hook):
    rows = [
        ({"type": "session_meta", "timestamp": "2026-09-21T10:00:00Z", "payload": {"id": "s1"}}, 5),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:01Z",
            "payload": {
                "type": "message", "role": "user", "id": "u1",
                "content": [{"type": "input_text", "text": "inspect"}],
            },
        }, 10),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:01.100Z",
            "payload": {
                "type": "message", "role": "user", "id": "u2",
                "content": [{"type": "input_text", "text": "the repo"}],
            },
        }, 20),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:02Z",
            "payload": {
                "type": "custom_tool_call", "id": "item-1", "call_id": "call-1",
                "name": "exec", "input": '{"cmd":"pwd"}',
            },
        }, 30),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:03Z",
            "payload": {
                "type": "custom_tool_call_output", "id": "item-2", "call_id": "call-1",
                "output": "workspace", "is_error": False,
            },
        }, 40),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:04Z",
            "payload": {
                "type": "message", "role": "assistant", "id": "a1", "phase": "final_answer",
                "content": [{"type": "output_text", "text": "done"}],
            },
        }, 50),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:04.100Z",
            "payload": {"type": "reasoning", "id": "r1", "content": []},
        }, 60),
    ]

    turns, unknown = hook.build_turns(rows, default_model="gpt-test")

    assert len(turns) == 1
    turn = turns[0]
    assert hook.extract_text(hook.get_content(turn.user_msg)) == "inspect\nthe repo"
    assert [hook.get_model(message) for message in turn.assistant_msgs] == ["gpt-test", "gpt-test"]
    tool = hook.iter_tool_uses(hook.get_content(turn.assistant_msgs[0]))[0]
    assert tool == {"type": "tool_use", "id": "call-1", "name": "exec", "input": {"cmd": "pwd"}}
    assert turn.tool_results_by_id["call-1"] == {
        "content": "workspace",
        "timestamp": "2026-09-21T10:00:03Z",
        "is_error": False,
    }
    assert hook.extract_text(hook.get_content(turn.assistant_msgs[-1])) == "done"
    assert turn.end_offset == 50
    assert unknown == {}


def test_codex_function_call_aliases_share_the_same_mapping(hook):
    call = hook.normalize_codex_row({
        "type": "response_item",
        "timestamp": "2026-09-21T10:00:00Z",
        "payload": {
            "type": "function_call", "call_id": "f1", "name": "lookup",
            "arguments": '{"query":"x"}',
        },
    }, "gpt-test")
    result = hook.normalize_codex_row({
        "type": "response_item",
        "timestamp": "2026-09-21T10:00:01Z",
        "payload": {"type": "function_call_output", "call_id": "f1", "output": "ok"},
    }, "gpt-test")

    assert hook.iter_tool_uses(hook.get_content(call))[0]["input"] == {"query": "x"}
    assert hook.iter_tool_results(hook.get_content(result))[0]["tool_use_id"] == "f1"


def test_codex_tool_search_is_retained_as_a_tool_observation(hook):
    rows = [
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:00Z",
            "payload": {
                "type": "message", "role": "user",
                "content": [{"type": "input_text", "text": "find a tool"}],
            },
        }, 10),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:01Z",
            "payload": {
                "type": "tool_search_call", "id": "search-1", "call_id": "call-search",
                "arguments": {"query": "issue tracker"},
            },
        }, 20),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:02Z",
            "payload": {
                "type": "tool_search_output", "call_id": "call-search", "status": "completed",
                "tools": [{"type": "function", "name": "list_issues"}],
            },
        }, 30),
        ({
            "type": "response_item",
            "timestamp": "2026-09-21T10:00:03Z",
            "payload": {
                "type": "message", "role": "assistant",
                "content": [{"type": "output_text", "text": "found it"}],
            },
        }, 40),
    ]

    turns, unknown = hook.build_turns(rows, default_model="gpt-test")

    assert unknown == {}
    tool = hook.iter_tool_uses(hook.get_content(turns[0].assistant_msgs[0]))[0]
    assert tool["name"] == "tool_search"
    assert tool["input"] == {"query": "issue tracker"}
    assert turns[0].tool_results_by_id["call-search"]["content"] == [
        {"type": "function", "name": "list_issues"}
    ]


def test_runtime_detection_and_missing_credentials_remain_fail_open(hook, monkeypatch):
    monkeypatch.setenv("PLUGIN_ROOT", "/tmp/plugin")
    assert hook._runtime_name() == "codex"
    monkeypatch.delenv("PLUGIN_ROOT")
    assert hook._runtime_name() == "claude-code"

    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_PLUGIN_OPTION_LANGFUSE_SECRET_KEY", raising=False)
    assert hook.main() == 0


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))

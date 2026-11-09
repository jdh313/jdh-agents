# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8.0"]
# ///
"""Parser and emit contract tests for the dual-runtime Langfuse hook."""

from __future__ import annotations

import importlib.util
import json
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


def _make_skill(skills_dir, folder):
    (skills_dir / folder).mkdir(parents=True)
    (skills_dir / folder / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")


def _write_lockfile(hook, skills_dir, data):
    text = data if isinstance(data, str) else json.dumps(data)
    (skills_dir / hook.SKILLS_LOCKFILE_NAME).write_text(text, encoding="utf-8")


def _lock_entry(path, version=1, name=None):
    return {"path": path, "name": name or path, "selector": {"label": "production"}, "version": version}


def test_discovery_reports_installed_skills_sorted_with_locked_versions(hook, tmp_path):
    _make_skill(tmp_path, "zeta")
    _make_skill(tmp_path, "commit")
    _make_skill(tmp_path, "local-only")
    _make_skill(tmp_path, ".hidden")
    (tmp_path / "synced").mkdir()
    _write_lockfile(hook, tmp_path, {
        "lockVersion": 1,
        "skills": [
            _lock_entry("zeta", version=4),
            _lock_entry("commit", version=1),
            _lock_entry("uninstalled", version=9),
            _lock_entry(".hidden", version=2),
            _lock_entry("synced", version=3),
        ],
    })

    assert hook.discover_available_skills(tmp_path) == [
        {"name": "commit", "version": 1},
        {"name": "local-only"},
        {"name": "zeta", "version": 4},
    ]


def test_discovery_reports_the_lockfile_name_not_the_folder(hook, tmp_path):
    _make_skill(tmp_path, "folder")
    _write_lockfile(hook, tmp_path, {"skills": [_lock_entry("folder", version=7, name="published")]})

    assert hook.discover_available_skills(tmp_path) == [{"name": "published", "version": 7}]


def test_discovery_without_a_lockfile_is_name_only(hook, tmp_path):
    _make_skill(tmp_path, "commit")

    assert hook.discover_available_skills(tmp_path) == [{"name": "commit"}]


@pytest.mark.parametrize("lockfile", [
    "{not json",
    {"skills": "nope"},
    {"skills": ["nope", 1, None]},
    ["not", "a", "dict"],
])
def test_discovery_survives_an_unusable_lockfile(hook, tmp_path, lockfile):
    _make_skill(tmp_path, "commit")
    _write_lockfile(hook, tmp_path, lockfile)

    assert hook.discover_available_skills(tmp_path) == [{"name": "commit"}]


@pytest.mark.parametrize("version", ["1", 1.5, True, None])
def test_discovery_drops_a_version_that_is_not_an_integer(hook, tmp_path, version):
    _make_skill(tmp_path, "commit")
    _write_lockfile(hook, tmp_path, {"skills": [_lock_entry("commit", version=version)]})

    assert hook.discover_available_skills(tmp_path) == [{"name": "commit"}]


def test_discovery_of_a_missing_directory_is_empty(hook, tmp_path):
    assert hook.discover_available_skills(tmp_path / "absent") == []


class FakeOtelSpan:
    def __init__(self, name):
        self.name = name
        self.attributes = {}
        self.ended = False

    def set_attribute(self, key, value):
        assert not self.ended, f"{self.name}: attribute set after the span ended"
        self.attributes[key] = value


class FakeObservation:
    def __init__(self, otel_span):
        self._otel_span = otel_span

    def update(self, **_kwargs):
        pass

    def end(self, **_kwargs):
        self._otel_span.ended = True


class FakeLangfuse:
    def __init__(self, span_factory=FakeOtelSpan):
        self.spans = []
        self._span_factory = span_factory
        self._otel_tracer = types.SimpleNamespace(start_span=self._start_span)

    def _start_span(self, name, start_time=None):
        span = self._span_factory(name)
        self.spans.append(span)
        return span

    def _create_observation_from_otel_span(self, otel_span, as_type, **_kwargs):
        otel_span.as_type = as_type
        return FakeObservation(otel_span)

    def span_named(self, name):
        return next(span for span in self.spans if span.name == name)


def _turn_with_tools(hook, *tool_names):
    tool_uses = [
        {"type": "tool_use", "id": f"t{i}", "name": name, "input": {}}
        for i, name in enumerate(tool_names)
    ]
    return hook.Turn(
        user_msg={
            "type": "user",
            "timestamp": "2026-09-21T10:00:00Z",
            "message": {"role": "user", "content": "hello"},
        },
        assistant_msgs=[{
            "type": "assistant",
            "timestamp": "2026-09-21T10:00:01Z",
            "message": {"id": "m1", "role": "assistant", "model": "claude-test", "content": tool_uses},
        }],
        tool_results_by_id={},
        end_offset=10,
    )


def _emit(hook, monkeypatch, skills_dir, runtime, span_factory=FakeOtelSpan, tools=("Skill", "Read", "Bash")):
    @contextmanager
    def use_span(_span, end_on_exit=False):
        yield

    monkeypatch.setattr(hook.otel_trace_api, "use_span", use_span, raising=False)
    monkeypatch.setattr(hook, "SKILLS_DIR", skills_dir)
    monkeypatch.setattr(hook, "RUNTIME", runtime)
    langfuse = FakeLangfuse(span_factory)
    turn = _turn_with_tools(hook, *tools)
    hook.emit_turn(langfuse, "s1", 1, turn, Path("t.jsonl"), "u", "cwd", "default-mode")
    return langfuse


def test_emit_turn_sets_skills_on_generation_and_skill_loading_tools_only(hook, monkeypatch, tmp_path):
    _make_skill(tmp_path, "commit")
    _write_lockfile(hook, tmp_path, {"skills": [_lock_entry("commit")]})

    langfuse = _emit(hook, monkeypatch, tmp_path, "claude-code")

    attr = hook.SKILLS_AVAILABLE_ATTR
    expected = {attr: json.dumps([{"name": "commit", "version": 1}])}
    assert langfuse.span_named("Claude Generation 1").attributes == expected
    assert langfuse.span_named("Skill").attributes == expected
    assert langfuse.span_named("Read").attributes == expected
    assert langfuse.span_named("Tool: Bash").attributes == {}


def test_emit_turn_names_skill_loading_spans_with_the_raw_tool_name(hook, monkeypatch, tmp_path):
    langfuse = _emit(hook, monkeypatch, tmp_path, "claude-code")

    assert [span.name for span in langfuse.spans[2:]] == ["Skill", "Read", "Tool: Bash"]


def test_emit_turn_records_skill_as_a_tool_and_orchestration_tools_as_agents(hook, monkeypatch, tmp_path):
    langfuse = _emit(hook, monkeypatch, tmp_path, "claude-code", tools=("Skill", "Agent", "Task"))

    assert langfuse.span_named("Skill").as_type == "tool"
    assert langfuse.span_named("Tool: Agent").as_type == "agent"
    assert langfuse.span_named("Tool: Task").as_type == "agent"


def test_emit_turn_sets_no_skills_attribute_under_codex(hook, monkeypatch, tmp_path):
    _make_skill(tmp_path, "commit")

    langfuse = _emit(hook, monkeypatch, tmp_path, "codex")

    assert langfuse.spans
    assert all(span.attributes == {} for span in langfuse.spans)


def test_emit_turn_keeps_codex_tool_span_names_and_types(hook, monkeypatch, tmp_path):
    langfuse = _emit(hook, monkeypatch, tmp_path, "codex")

    assert [(span.name, span.as_type) for span in langfuse.spans[2:]] == [
        ("Tool: Skill", "agent"),
        ("Tool: Read", "tool"),
        ("Tool: Bash", "tool"),
    ]


def test_emit_turn_completes_without_a_skills_directory(hook, monkeypatch, tmp_path):
    langfuse = _emit(hook, monkeypatch, tmp_path / "absent", "claude-code")

    assert all(span.ended for span in langfuse.spans)
    assert all(span.attributes == {} for span in langfuse.spans)


def test_emit_turn_completes_when_setting_the_attribute_fails(hook, monkeypatch, tmp_path):
    class RaisingSpan(FakeOtelSpan):
        def set_attribute(self, key, value):
            raise RuntimeError("boom")

    _make_skill(tmp_path, "commit")

    langfuse = _emit(hook, monkeypatch, tmp_path, "claude-code", span_factory=RaisingSpan)

    assert all(span.ended for span in langfuse.spans)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))

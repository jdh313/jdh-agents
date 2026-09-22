#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pytest>=8.0"]
# ///
"""Regression coverage for usage-report transcript discovery and attribution.

Run:  uv run scripts/tests/test_introspect_usage_report.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "plugins/introspect/skills/usage-report/scripts/claude-usage-report.py"
)
FIXTURE = Path(__file__).parent / "fixtures/introspect-transcripts"


def load_report_module():
    spec = importlib.util.spec_from_file_location("claude_usage_report", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_separate_subagent_transcript_is_attributed_to_parent_session() -> None:
    report = load_report_module()

    main_only = report.find_transcripts(FIXTURE, "fixture-repo")
    files = report.find_transcripts(
        FIXTURE, "fixture-repo", include_subagents=True
    )

    assert len(main_only) == 1
    assert len(files) == 2
    assert report.transcript_session_root(files[0]) == report.transcript_session_root(files[1])

    stats = report.Stats()
    for path in files:
        report.process_file(path, stats, include_args=False)

    assert stats.sessions == 1
    assert stats.human_prompts == 1
    assert stats.subagents == {"Explore": 1}
    assert stats.tools_main == {"Read": 1, "Agent": 1}
    assert stats.tools_sub == {"Bash": 1, "Write": 1, "Read": 1}
    assert stats.agent_turns == {"researcher-123": 2}

    payload = json.loads(report.to_json(stats))
    assert payload["agent_turns"] == {"researcher-123": 2}
    markdown = report.to_markdown(stats, include_args=False, scope="fixture")
    csv = report.to_csv(stats)
    for rendered in (json.dumps(payload), markdown, csv):
        assert "PRIVATE-PROMPT-DO-NOT-REPORT" not in rendered


def test_bundled_cli_runs_from_loaded_skill_path_without_runtime_env(tmp_path: Path) -> None:
    env = os.environ.copy()
    env.pop("CLAUDE_PLUGIN_ROOT", None)
    env.pop("PLUGIN_ROOT", None)
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--projects-dir",
            str(FIXTURE),
            "--repo",
            "fixture-repo",
            "--stdout",
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert "# Claude Code usage report" in result.stdout
    assert "PRIVATE-PROMPT-DO-NOT-REPORT" not in result.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, *sys.argv[1:]]))

import json
import os
import shutil
from collections.abc import Callable
from pathlib import Path

import pytest

from tests.agentforge_harness import (
    AgentForge,
    age_tree_mtimes,
    resolve_agentforge,
    snapshot_tree,
    snapshot_write_observations,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO_ROOT / "MARKETPLACE.yaml"
CODEX_PACKAGES = {"commit", "craft", "feedback", "librarian", "linear", "spec-flow"}


@pytest.fixture(scope="module")
def clean_compilation(tmp_path_factory: pytest.TempPathFactory) -> tuple[AgentForge, Path]:
    agentforge = resolve_agentforge(REPO_ROOT, MARKETPLACE)
    output_root = tmp_path_factory.mktemp("agentforge-clean-output")
    result = agentforge.compile(output_root)

    assert result.returncode == 0, result.stdout + result.stderr
    registry = json.loads(
        (output_root / "codex/.agents/plugins/marketplace.json").read_text(encoding="utf-8")
    )
    assert {plugin["name"] for plugin in registry["plugins"]} == CODEX_PACKAGES

    return agentforge, output_root


def mutate_content(output_root: Path) -> tuple[str, str]:
    relative_path = "claude/plugins/commit/skills/commit/SKILL.md"
    path = output_root / relative_path
    path.write_bytes(path.read_bytes() + b"\nintentional drift\n")
    return "changed-output", relative_path


def mutate_missing_file(output_root: Path) -> tuple[str, str]:
    relative_path = "codex/plugins/spec-flow/skills/draft/SKILL.md"
    (output_root / relative_path).unlink()
    return "missing-output", relative_path


def mutate_extra_file(output_root: Path) -> tuple[str, str]:
    relative_path = "claude/plugins/commit/unmanaged.txt"
    path = output_root / relative_path
    path.write_text("unmanaged\n", encoding="utf-8")
    return "unexpected-output", relative_path


def mutate_metadata(output_root: Path) -> tuple[str, str]:
    relative_path = "codex/.agents/plugins/marketplace.json"
    path = output_root / relative_path
    registry = json.loads(path.read_text(encoding="utf-8"))
    registry["interface"]["displayName"] = "Drifted Marketplace"
    path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return "changed-output", relative_path


def mutate_permission(output_root: Path) -> tuple[str, str]:
    relative_path = "codex/plugins/commit/.codex-plugin/plugin.json"
    path = output_root / relative_path
    path.chmod((path.stat().st_mode & 0o777) ^ 0o111)
    return "changed-output-mode", relative_path


DRIFT_CASES: tuple[tuple[str, Callable[[Path], tuple[str, str]]], ...] = (
    ("content", mutate_content),
    ("missing-file", mutate_missing_file),
    ("extra-file", mutate_extra_file),
    ("metadata", mutate_metadata),
    ("permission", mutate_permission),
)


@pytest.mark.parametrize(
    ("case_name", "mutate"),
    DRIFT_CASES,
    ids=[case_name for case_name, _ in DRIFT_CASES],
)
def test_agentforge_reports_drift_without_modifying_output(
    case_name: str,
    mutate: Callable[[Path], tuple[str, str]],
    clean_compilation: tuple[AgentForge, Path],
    tmp_path: Path,
) -> None:
    if case_name == "permission" and os.name == "nt":
        pytest.skip("Windows does not expose the POSIX output modes checked by AgentForge")

    agentforge, clean_output = clean_compilation
    output_root = tmp_path / "compiled"
    shutil.copytree(clean_output, output_root)
    issue_code, relative_path = mutate(output_root)
    age_tree_mtimes(output_root)
    drifted_snapshot = snapshot_tree(output_root)
    write_observations = snapshot_write_observations(output_root)

    result = agentforge.check(output_root)

    diagnostics = result.stdout + result.stderr
    assert result.returncode != 0, diagnostics
    assert f"{issue_code}: {relative_path}:" in diagnostics
    assert snapshot_tree(output_root) == drifted_snapshot
    assert snapshot_write_observations(output_root) == write_observations

"""Full-corpus acceptance tests for canonical AgentForge compilation."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.agentforge_harness import AgentForge, resolve_agentforge, snapshot_tree

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO_ROOT / "MARKETPLACE.yaml"

CLAUDE_PACKAGE_IDS = frozenset(
    {
        "coach",
        "commit",
        "compass",
        "craft",
        "debate",
        "feedback",
        "introspect",
        "langfuse",
        "librarian",
        "linear",
        "pm",
        "skillsmith",
        "shake-tune",
        "spec-flow",
        "teach",
    }
)
# Codex enrolls every package except `langfuse`, whose Stop hook parses Claude
# Code's transcript schema and resolves zero turns against a Codex rollout. Its
# exclusion is a reviewed decision, not a pending mapping — see JUN-350 and the
# `langfuse` entry in docs/agentforge-compatibility.md. Deriving the set here
# keeps a new package enrolled-by-default in this assertion, so forgetting to
# update it fails loudly rather than silently under-checking the catalog.
CODEX_ONLY_EXCLUSIONS = frozenset({"langfuse"})
CODEX_PACKAGE_IDS = CLAUDE_PACKAGE_IDS - CODEX_ONLY_EXCLUSIONS


@pytest.fixture(scope="module")
def agentforge() -> AgentForge:
    return resolve_agentforge(REPO_ROOT, MARKETPLACE)


def test_full_corpus_compilation_is_deterministic_and_clean(
    agentforge: AgentForge, tmp_path: Path
) -> None:
    first_output = tmp_path / "first"
    second_output = tmp_path / "second"

    agentforge.compile(first_output)
    agentforge.compile(second_output)

    assert snapshot_tree(first_output / "claude") == snapshot_tree(second_output / "claude")
    assert snapshot_tree(first_output / "codex") == snapshot_tree(second_output / "codex")
    claude_registry_ids = _registry_package_ids(first_output, "claude")
    codex_registry_ids = _registry_package_ids(first_output, "codex")
    assert len(claude_registry_ids) == 15
    assert len(set(claude_registry_ids)) == len(claude_registry_ids)
    assert frozenset(claude_registry_ids) == CLAUDE_PACKAGE_IDS
    assert len(codex_registry_ids) == len(CODEX_PACKAGE_IDS)
    assert len(set(codex_registry_ids)) == len(codex_registry_ids)
    assert frozenset(codex_registry_ids) == CODEX_PACKAGE_IDS
    assert _materialized_package_ids(first_output, "claude") == CLAUDE_PACKAGE_IDS
    assert _materialized_package_ids(first_output, "codex") == CODEX_PACKAGE_IDS
    _assert_explicit_only_codex_skills(first_output)

    check = agentforge.check(first_output)
    assert check.returncode == 0, _command_output(check)
    assert "[claude] ok:" in check.stdout
    assert "[codex] ok:" in check.stdout


def _registry_package_ids(output_root: Path, publication: str) -> list[str]:
    registry_path = {
        "claude": Path(".claude-plugin/marketplace.json"),
        "codex": Path(".agents/plugins/marketplace.json"),
    }[publication]
    registry = _read_json(output_root / publication / registry_path)
    return [plugin["name"] for plugin in registry["plugins"]]


def _materialized_package_ids(output_root: Path, publication: str) -> frozenset[str]:
    plugins_root = output_root / publication / "plugins"
    return frozenset(path.name for path in plugins_root.iterdir() if path.is_dir())


def _assert_explicit_only_codex_skills(output_root: Path) -> None:
    explicit_only_skills = _explicit_only_codex_skills()
    assert explicit_only_skills, "canonical Codex packages contain no explicit-only skills"

    for package_id, skill_id in sorted(explicit_only_skills):
        policy_path = (
            output_root
            / "codex"
            / "plugins"
            / package_id
            / "skills"
            / skill_id
            / "agents"
            / "openai.yaml"
        )
        assert policy_path.is_file(), (
            f"explicit-only source skill {package_id}/{skill_id} has no Codex policy sidecar"
        )
        policy = policy_path.read_text(encoding="utf-8")
        assert re.search(
            r"(?m)^policy:\s*$\n^  allow_implicit_invocation:\s*false\s*$",
            policy,
        ), f"explicit-only source skill {package_id}/{skill_id} allows implicit invocation"


def _explicit_only_codex_skills() -> set[tuple[str, str]]:
    explicit_only: set[tuple[str, str]] = set()
    for package_id in CODEX_PACKAGE_IDS:
        skills_root = REPO_ROOT / "plugins" / package_id / "skills"
        for skill_path in skills_root.glob("*/SKILL.md"):
            frontmatter = skill_path.read_text(encoding="utf-8").split("---", 2)[1]
            if re.search(r"(?m)^disable-model-invocation:\s*true\s*$", frontmatter):
                explicit_only.add((package_id, skill_path.parent.name))
    return explicit_only


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _command_output(result) -> str:
    return "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())

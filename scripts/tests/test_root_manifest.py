"""The repository-root Claude manifest that makes remote install resolve.

`marketplace add jdh313/jdh-agents` reads `.claude-plugin/marketplace.json` at
the repository root.  AgentForge publishes it from the `root-manifest: true`
publication in MARKETPLACE.yaml, rewriting each package source to point back
into the committed `marketplaces/claude/` tree.  These tests pin the two
properties a remote installer depends on -- the file exists, and every source
in it resolves -- plus the parser that surfaces drift in it.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from marketplace.generation import COMPILED_ROOT, parse_drift

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO_ROOT / "MARKETPLACE.yaml"
ROOT_MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"


def _claude_publication() -> dict:
    definition = yaml.safe_load(MARKETPLACE.read_text(encoding="utf-8"))
    return next(pub for pub in definition["publications"] if pub["id"] == "claude")


def test_claude_publication_declares_a_root_manifest() -> None:
    assert _claude_publication().get("root-manifest") is True, (
        "the Claude publication must declare root-manifest, or "
        "`marketplace add jdh313/jdh-agents` will not resolve remotely"
    )


def test_root_manifest_is_committed_at_the_path_claude_reads() -> None:
    destination = _claude_publication()["destination"]
    assert (REPO_ROOT / destination) == ROOT_MANIFEST
    assert ROOT_MANIFEST.is_file()


def test_every_root_manifest_source_resolves_to_a_compiled_package() -> None:
    manifest = json.loads(ROOT_MANIFEST.read_text(encoding="utf-8"))
    nested = json.loads(
        (REPO_ROOT / COMPILED_ROOT / "claude" / ".claude-plugin" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )

    assert {plugin["name"] for plugin in manifest["plugins"]} == {
        plugin["name"] for plugin in nested["plugins"]
    }, "the root copy must enrol exactly the packages the nested publication does"

    for plugin in manifest["plugins"]:
        source = plugin["source"]
        assert source.startswith(f"./{COMPILED_ROOT.as_posix()}/claude/plugins/"), (
            f"{plugin['name']} source {source!r} does not point into the committed tree"
        )
        assert (REPO_ROOT / source).is_dir(), f"{plugin['name']} source {source!r} does not exist"


def test_drift_in_the_root_manifest_is_reported_against_the_repository_root() -> None:
    # AgentForge stands `<root>` in for the marketplace directory, because the
    # root copy lives beside MARKETPLACE.yaml rather than under `--out`.
    drift = parse_drift(
        "error [claude] changed-output: <root>/.claude-plugin/marketplace.json: differs\n",
        "",
    )

    assert [(issue.kind, issue.path.as_posix()) for issue in drift] == [
        ("changed-output", ".claude-plugin/marketplace.json")
    ]


def test_drift_in_the_nested_tree_is_reported_under_the_compiled_root() -> None:
    drift = parse_drift("error [claude] changed-output: claude/plugins/commit/x.md: differs\n", "")

    assert [(issue.kind, issue.path.as_posix()) for issue in drift] == [
        ("changed-output", f"{COMPILED_ROOT.as_posix()}/claude/plugins/commit/x.md")
    ]

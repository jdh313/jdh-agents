"""Focused tests for the compiled-publication cutover.

The repository commits whole AgentForge publications under ``marketplaces/``
rather than projecting a handful of native manifests back into the source tree.
These tests pin the two properties that cutover depends on: a snapshot captures
everything a runtime actually consumes (content *and* executability), and the
comparison that guards the committed tree never writes to it.
"""

from __future__ import annotations

from pathlib import Path

from marketplace.generation import compare_trees, snapshot_tree


def _write(path: Path, content: bytes = b"{}\n", *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    path.chmod(0o755 if executable else 0o644)


def _publication_tree(root: Path) -> None:
    """A miniature of what AgentForge emits: manifests, bodies, and a hook."""
    _write(root / "claude/.claude-plugin/marketplace.json", b"claude-root\n")
    _write(root / "claude/plugins/alpha/.claude-plugin/plugin.json", b"claude-alpha\n")
    _write(root / "claude/plugins/alpha/skills/hello/SKILL.md", b"compiled skill\n")
    _write(root / "claude/plugins/alpha/hooks/guard.sh", b"#!/bin/sh\n", executable=True)
    _write(root / "codex/.agents/plugins/marketplace.json", b"codex-root\n")
    _write(root / "codex/plugins/alpha/.codex-plugin/plugin.json", b"codex-alpha\n")
    _write(root / "codex/plugins/alpha/agents/reviewer.md", b"compiled role\n")


def test_snapshot_captures_whole_tree_including_executability(tmp_path: Path) -> None:
    compiled = tmp_path / "marketplaces"
    _publication_tree(compiled)

    snapshot = snapshot_tree(compiled)

    # Compiled bodies are part of the publication, not incidental content —
    # the previous design dropped exactly these and left Codex resolving
    # canonical Claude sources instead.
    assert set(snapshot) == {
        Path("claude/.claude-plugin/marketplace.json"),
        Path("claude/plugins/alpha/.claude-plugin/plugin.json"),
        Path("claude/plugins/alpha/skills/hello/SKILL.md"),
        Path("claude/plugins/alpha/hooks/guard.sh"),
        Path("codex/.agents/plugins/marketplace.json"),
        Path("codex/plugins/alpha/.codex-plugin/plugin.json"),
        Path("codex/plugins/alpha/agents/reviewer.md"),
    }
    assert snapshot[Path("claude/plugins/alpha/hooks/guard.sh")].executable
    assert not snapshot[Path("claude/plugins/alpha/skills/hello/SKILL.md")].executable


def test_snapshot_of_absent_tree_is_empty(tmp_path: Path) -> None:
    assert snapshot_tree(tmp_path / "never-compiled") == {}


def test_identical_trees_report_no_drift(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    _publication_tree(expected)
    _publication_tree(actual)

    assert compare_trees(snapshot_tree(expected), snapshot_tree(actual)) == []


def test_detects_missing_extra_and_content_drift(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    _publication_tree(expected)
    _publication_tree(actual)

    (actual / "claude/plugins/alpha/skills/hello/SKILL.md").write_bytes(b"hand-edited\n")
    (actual / "codex/.agents/plugins/marketplace.json").unlink()
    _write(actual / "claude/plugins/ghost/.claude-plugin/plugin.json", b"stale\n")

    drift = compare_trees(snapshot_tree(expected), snapshot_tree(actual))

    assert {(issue.kind, issue.path.as_posix()) for issue in drift} == {
        ("changed", "claude/plugins/alpha/skills/hello/SKILL.md"),
        ("missing", "codex/.agents/plugins/marketplace.json"),
        ("extra", "claude/plugins/ghost/.claude-plugin/plugin.json"),
    }


def test_permission_drift_is_reported_separately_from_content(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    _publication_tree(expected)
    _publication_tree(actual)

    # A hook that loses its executable bit is still byte-identical. Reporting
    # it as "changed" would hide why the runtime stopped being able to run it.
    (actual / "claude/plugins/alpha/hooks/guard.sh").chmod(0o644)

    drift = compare_trees(snapshot_tree(expected), snapshot_tree(actual))

    assert [(issue.kind, issue.path.as_posix()) for issue in drift] == [
        ("mode", "claude/plugins/alpha/hooks/guard.sh")
    ]


def test_comparison_is_read_only(tmp_path: Path) -> None:
    expected = tmp_path / "expected"
    actual = tmp_path / "actual"
    _publication_tree(expected)
    _publication_tree(actual)
    (actual / "claude/.claude-plugin/marketplace.json").write_bytes(b"drifted\n")
    before = _snapshot_with_metadata(actual)

    assert compare_trees(snapshot_tree(expected), snapshot_tree(actual))

    assert _snapshot_with_metadata(actual) == before


def _snapshot_with_metadata(root: Path) -> tuple[tuple[str, bytes, int, int, int], ...]:
    return tuple(
        (
            path.relative_to(root).as_posix(),
            path.read_bytes(),
            path.stat().st_mode,
            path.stat().st_mtime_ns,
            path.stat().st_ctime_ns,
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    )

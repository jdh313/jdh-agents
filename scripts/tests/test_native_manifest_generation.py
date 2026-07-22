"""Focused tests for the AgentForge native-manifest cutover."""

from __future__ import annotations

from pathlib import Path

from marketplace.generation import (
    collect_native_manifests,
    compare_native_manifests,
    materialize_native_manifests,
)


def _write(path: Path, content: bytes = b"{}\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _compiled_tree(root: Path) -> None:
    _write(root / "claude/.claude-plugin/marketplace.json", b"claude-root\n")
    _write(root / "claude/plugins/alpha/.claude-plugin/plugin.json", b"claude-alpha\n")
    _write(root / "claude/plugins/beta/.claude-plugin/plugin.json", b"claude-beta\n")
    _write(root / "codex/.agents/plugins/marketplace.json", b"codex-root\n")
    _write(root / "codex/plugins/alpha/.codex-plugin/plugin.json", b"codex-alpha\n")

    # Complete AgentForge publications contain source content too. The cutover
    # must never materialize these files into the maintained repository tree.
    _write(root / "claude/plugins/alpha/skills/hello/SKILL.md", b"compiled skill\n")
    _write(root / "codex/plugins/alpha/agents/reviewer.md", b"compiled role\n")


def test_collects_only_root_and_package_native_manifests(tmp_path: Path) -> None:
    compiled = tmp_path / "compiled"
    _compiled_tree(compiled)

    manifests = collect_native_manifests(compiled)

    assert manifests == {
        Path(".claude-plugin/marketplace.json"): b"claude-root\n",
        Path(".agents/plugins/marketplace.json"): b"codex-root\n",
        Path("plugins/alpha/.claude-plugin/plugin.json"): b"claude-alpha\n",
        Path("plugins/alpha/.codex-plugin/plugin.json"): b"codex-alpha\n",
        Path("plugins/beta/.claude-plugin/plugin.json"): b"claude-beta\n",
    }


def test_detects_root_package_missing_extra_and_content_drift(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    compiled = tmp_path / "compiled"
    _compiled_tree(compiled)
    expected = collect_native_manifests(compiled)

    _write(repo / ".claude-plugin/marketplace.json", b"drifted root\n")
    _write(repo / "plugins/alpha/.claude-plugin/plugin.json", b"drifted package\n")
    _write(repo / "plugins/beta/.claude-plugin/plugin.json", b"claude-beta\n")
    _write(repo / "plugins/extra/.codex-plugin/plugin.json", b"extra\n")

    issues = compare_native_manifests(repo, expected)

    assert {(issue.kind, issue.path.as_posix()) for issue in issues} == {
        ("changed", ".claude-plugin/marketplace.json"),
        ("missing", ".agents/plugins/marketplace.json"),
        ("changed", "plugins/alpha/.claude-plugin/plugin.json"),
        ("missing", "plugins/alpha/.codex-plugin/plugin.json"),
        ("extra", "plugins/extra/.codex-plugin/plugin.json"),
    }


def test_comparison_is_read_only(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    compiled = tmp_path / "compiled"
    _compiled_tree(compiled)
    expected = collect_native_manifests(compiled)
    _write(repo / ".claude-plugin/marketplace.json", b"drifted root\n")
    before = _snapshot(repo)

    assert compare_native_manifests(repo, expected)

    assert _snapshot(repo) == before


def test_materializes_exact_manifest_set_without_replacing_source_content(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    compiled = tmp_path / "compiled"
    _compiled_tree(compiled)
    expected = collect_native_manifests(compiled)
    _write(repo / "plugins/alpha/skills/hello/SKILL.md", b"maintained skill\n")
    _write(repo / "plugins/extra/.codex-plugin/plugin.json", b"extra\n")

    materialize_native_manifests(repo, expected)

    assert compare_native_manifests(repo, expected) == []
    assert (repo / "plugins/alpha/skills/hello/SKILL.md").read_bytes() == b"maintained skill\n"
    assert not (repo / "plugins/extra/.codex-plugin/plugin.json").exists()
    assert not (repo / "plugins/alpha/agents/reviewer.md").exists()


def _snapshot(root: Path) -> tuple[tuple[str, bytes, int, int], ...]:
    return tuple(
        (
            path.relative_to(root).as_posix(),
            path.read_bytes(),
            path.stat().st_mtime_ns,
            path.stat().st_ctime_ns,
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    )

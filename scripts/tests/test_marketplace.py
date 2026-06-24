"""Unit tests for the marketplace package.

All tests use tmp_path fixtures with tiny fake plugin trees —
no dependency on the real plugins/ directory.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from marketplace.discovery import discover_plugins
from marketplace.export import _privacy_gate  # noqa: PLC2701
from marketplace.manifest import build_public
from marketplace.validate import validate_manifest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_plugin(
    plugins_dir: Path, name: str, version: str = "1.0.0", description: str = "A plugin"
) -> Path:
    """Create a minimal valid plugin tree under *plugins_dir*/<name>/."""
    plugin_dir = plugins_dir / name
    meta_dir = plugin_dir / ".claude-plugin"
    meta_dir.mkdir(parents=True)
    skill_dir = plugin_dir / "skills" / "hello"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("# Hello\n\nThis skill does something useful.\n" * 3)
    plugin_json = meta_dir / "plugin.json"
    plugin_json.write_text(
        json.dumps({
            "name": name,
            "version": version,
            "description": description,
            "author": {"name": "Tester"},
            "keywords": ["test"],
        }),
        encoding="utf-8",
    )
    return plugin_dir


def _minimal_config(allowlist: list[str], **overrides) -> dict:
    base = {
        "name": "test-marketplace",
        "description": "Test public marketplace",
        "owner": {"name": "Test User", "email": "test@example.com"},
        "homepage": "https://example.com",
        "metadataVersion": "1.0.0",
        "allowlist": allowlist,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# (a) discover_plugins finds plugins and derives version from plugin.json
# ---------------------------------------------------------------------------


def test_discover_plugins_finds_all(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "alpha", version="2.3.4")
    _make_plugin(plugins_dir, "beta", version="0.1.0")

    found = discover_plugins(plugins_dir)

    assert len(found) == 2
    # Sorted by name
    assert found[0]["name"] == "alpha"
    assert found[0]["version"] == "2.3.4"
    assert found[1]["name"] == "beta"
    assert found[1]["version"] == "0.1.0"


def test_discover_plugins_derives_version_from_plugin_json(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "myplugin", version="9.9.9")

    found = discover_plugins(plugins_dir)

    assert len(found) == 1
    assert found[0]["version"] == "9.9.9"


def test_discover_plugins_source_path_format(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "myplugin")

    found = discover_plugins(plugins_dir)

    assert found[0]["source"] == "./plugins/myplugin"


def test_discover_plugins_skips_invalid_json(tmp_path: Path, capsys) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    bad_dir = plugins_dir / "bad" / ".claude-plugin"
    bad_dir.mkdir(parents=True)
    (bad_dir / "plugin.json").write_text("NOT JSON", encoding="utf-8")

    found = discover_plugins(plugins_dir)

    assert found == []
    captured = capsys.readouterr()
    assert "Warning" in captured.err


# ---------------------------------------------------------------------------
# (b) allowlist filtering
# ---------------------------------------------------------------------------


def test_discover_plugins_allowlist_filters(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "alpha")
    _make_plugin(plugins_dir, "beta")
    _make_plugin(plugins_dir, "gamma")

    found = discover_plugins(plugins_dir, allowlist=["alpha", "gamma"])

    assert len(found) == 2
    names = [p["name"] for p in found]
    assert "beta" not in names
    assert "alpha" in names
    assert "gamma" in names


def test_discover_plugins_allowlist_empty(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "alpha")

    found = discover_plugins(plugins_dir, allowlist=[])

    assert found == []


# ---------------------------------------------------------------------------
# (c) build_public raises when allowlisted plugin dir is missing
# ---------------------------------------------------------------------------


def test_build_public_raises_on_missing_allowlisted_plugin(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "exists")

    config = _minimal_config(["exists", "does-not-exist"])

    with pytest.raises(ValueError, match="does-not-exist"):
        build_public(config, plugins_dir, existing_output_path=None)


def test_build_public_raises_all_missing(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    config = _minimal_config(["missing-a", "missing-b"])

    with pytest.raises(ValueError, match="missing-a"):
        build_public(config, plugins_dir, existing_output_path=None)


# ---------------------------------------------------------------------------
# (d) build_public produces a manifest that passes validate_manifest
# ---------------------------------------------------------------------------


def test_build_public_passes_validation(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "foo")
    _make_plugin(plugins_dir, "bar")

    config = _minimal_config(["foo", "bar"])
    manifest = build_public(config, plugins_dir, existing_output_path=None)

    errors = validate_manifest(manifest, plugins_dir)
    assert errors == [], f"Validation errors: {errors}"


def test_build_public_manifest_structure(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "p1", version="1.2.3")

    config = _minimal_config(["p1"])
    manifest = build_public(config, plugins_dir, existing_output_path=None)

    assert manifest["name"] == "test-marketplace"
    assert manifest["owner"]["email"] == "test@example.com"
    assert manifest["metadata"]["totalPlugins"] == 1
    assert manifest["metadata"]["homepage"] == "https://example.com"
    assert manifest["metadata"]["version"] == "1.0.0"
    assert manifest["plugins"][0]["version"] == "1.2.3"


# ---------------------------------------------------------------------------
# (e) Privacy gate
# ---------------------------------------------------------------------------


def _make_plugin_with_content(plugins_dir: Path, name: str, content: str) -> None:
    """Make a plugin with a README containing *content* for privacy scanning."""
    plugin_dir = plugins_dir / name
    meta_dir = plugin_dir / ".claude-plugin"
    meta_dir.mkdir(parents=True)
    (meta_dir / "plugin.json").write_text(
        json.dumps({"name": name, "version": "1.0.0", "description": "d", "author": {"name": "T"}}),
        encoding="utf-8",
    )
    (plugin_dir / "README.md").write_text(content, encoding="utf-8")


def test_privacy_gate_raises_on_absolute_home_path(tmp_path: Path) -> None:
    """Hard error: absolute home path like /Users/someone/."""
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    private_root = tmp_path
    (private_root / "plugins").mkdir(exist_ok=True)

    _make_plugin_with_content(
        plugins_dir,
        "myplugin",
        "This plugin reads from /Users/jsmith/private-config.json",
    )

    with pytest.raises(ValueError, match="Privacy gate FAILED"):
        _privacy_gate(private_root, ["myplugin"])


def test_privacy_gate_raises_on_secret_assignment(tmp_path: Path) -> None:
    """Hard error: secret-ish assignment like api_key = 'abcdefgh12345'."""
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    private_root = tmp_path

    _make_plugin_with_content(
        plugins_dir,
        "myplugin",
        'Set api_key = "abcdefgh12345" in your environment.',
    )

    with pytest.raises(ValueError, match="Privacy gate FAILED"):
        _privacy_gate(private_root, ["myplugin"])


def test_privacy_gate_warns_not_raises_on_loose_ends(tmp_path: Path, capsys) -> None:
    """Soft warning only: ~/Loose Ends/ vault mention must NOT block export."""
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    private_root = tmp_path

    _make_plugin_with_content(
        plugins_dir,
        "myplugin",
        "Reads notes from ~/Loose Ends/ (configurable default vault path).",
    )

    # Should NOT raise
    _privacy_gate(private_root, ["myplugin"])

    captured = capsys.readouterr()
    # A warning should have been printed
    assert "Loose Ends" in captured.out or "vault" in captured.out.lower()


def test_privacy_gate_passes_clean_plugin(tmp_path: Path) -> None:
    """No secrets, no home paths — gate should pass silently."""
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    private_root = tmp_path

    _make_plugin_with_content(
        plugins_dir,
        "clean",
        "This plugin does useful things and contains no secrets.",
    )

    # Should not raise
    _privacy_gate(private_root, ["clean"])

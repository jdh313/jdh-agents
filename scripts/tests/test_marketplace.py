"""Unit tests for the marketplace package.

All tests use tmp_path fixtures with tiny fake plugin trees —
no dependency on the real plugins/ directory.
"""

from __future__ import annotations

import json
from pathlib import Path

from marketplace.validate import validate_manifest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_plugin(
    plugins_dir: Path,
    name: str,
    version: str = "1.0.0",
    description: str = "A plugin",
    default_enabled: bool | None = None,
) -> Path:
    """Create a minimal valid plugin tree under *plugins_dir*/<name>/."""
    plugin_dir = plugins_dir / name
    meta_dir = plugin_dir / ".claude-plugin"
    meta_dir.mkdir(parents=True)
    skill_dir = plugin_dir / "skills" / "hello"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: hello\ndescription: A useful test skill.\n---\n\n"
        + "# Hello\n\nThis skill does something useful.\n" * 3
    )
    plugin_data = {
        "name": name,
        "version": version,
        "description": description,
        "author": {"name": "Tester"},
        "keywords": ["test"],
    }
    if default_enabled is not None:
        plugin_data["defaultEnabled"] = default_enabled
    plugin_json = meta_dir / "plugin.json"
    plugin_json.write_text(json.dumps(plugin_data), encoding="utf-8")
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
# Codex marketplace validation
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# (a2) defaultEnabled propagation
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# (b) allowlist filtering
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------


def test_private_manifest_accepts_current_agentforge_metadata(tmp_path: Path) -> None:
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    _make_plugin(plugins_dir, "p1")
    manifest = {
        "name": "test-marketplace",
        "owner": {"name": "Test User", "email": "test@example.com"},
        "plugins": [
            {
                "name": "p1",
                "source": "./plugins/p1",
                "description": "A plugin",
                "version": "1.0.0",
                "author": {"name": "Tester"},
            }
        ],
        "metadata": {"description": "Test marketplace", "version": "1.0.0"},
    }

    assert validate_manifest(manifest, plugins_dir) == []


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


# ---------------------------------------------------------------------------
# Enriched export commit message
# ---------------------------------------------------------------------------



"""Manifest builders for private and public marketplaces."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from marketplace.discovery import discover_plugins


def build_private(plugins_root: Path, manifest_path: Path) -> dict[str, Any]:
    """Regenerate the private marketplace manifest.

    Reads the existing manifest at *manifest_path* to preserve the top-level
    identity fields (name, description, owner, metadata.*version*,
    metadata.*homepage*).  Regenerates ``plugins[]`` and
    ``metadata.totalPlugins``.  Bumps ``metadata.lastUpdated`` only when the
    plugin set actually changed vs. what is on-disk — so a re-run on a
    different date with the same plugins is a strict no-op.

    Returns the updated manifest dict (does NOT write to disk).
    """
    with manifest_path.open(encoding="utf-8") as fh:
        existing: dict[str, Any] = json.load(fh)

    new_plugins = discover_plugins(plugins_root)
    old_plugins: list[dict[str, Any]] = existing.get("plugins", [])

    updated = dict(existing)  # shallow copy — we'll replace keys selectively
    updated["plugins"] = new_plugins
    updated["metadata"] = dict(existing.get("metadata", {}))
    updated["metadata"]["totalPlugins"] = len(new_plugins)

    if new_plugins != old_plugins:
        updated["metadata"]["lastUpdated"] = date.today().isoformat()

    return updated


def build_public(
    config: dict[str, Any],
    plugins_root: Path,
    existing_output_path: Path | None,
) -> dict[str, Any]:
    """Build a fresh public marketplace manifest from *config*.

    *config* must contain:
      - name, description, owner (with name + email), homepage
      - allowlist: list of plugin names to include
      - metadataVersion (optional, defaults to "1.0.0")

    *plugins_root* is the **private** plugins/ directory used to discover
    allowlisted plugins.

    *existing_output_path* is the path to the existing public manifest, used
    solely to preserve ``metadata.lastUpdated`` when the plugin set has not
    changed.  Pass ``None`` when no prior manifest exists.

    Raises ``ValueError`` listing any allowlisted names with no plugin dir.
    """
    allowlist: list[str] = config["allowlist"]

    # Existence gate — all allowlisted names must have a plugin dir
    missing = [
        name
        for name in allowlist
        if not (plugins_root / name / ".claude-plugin" / "plugin.json").exists()
    ]
    if missing:
        raise ValueError(
            f"build_public: allowlisted plugins not found in {plugins_root}: "
            + ", ".join(missing)
        )

    new_plugins = discover_plugins(plugins_root, allowlist=allowlist)

    # Preserve lastUpdated if the plugin set is unchanged
    last_updated = date.today().isoformat()
    if existing_output_path is not None and existing_output_path.exists():
        try:
            with existing_output_path.open(encoding="utf-8") as fh:
                old_manifest: dict[str, Any] = json.load(fh)
            old_plugins = old_manifest.get("plugins", [])
            if old_plugins == new_plugins:
                last_updated = old_manifest.get("metadata", {}).get(
                    "lastUpdated", last_updated
                )
        except (json.JSONDecodeError, OSError):
            pass  # If we can't read the old manifest, use today

    metadata_version: str = config.get("metadataVersion", "1.0.0")

    return {
        "name": config["name"],
        "description": config["description"],
        "owner": config["owner"],
        "plugins": new_plugins,
        "metadata": {
            "description": config["description"],
            "version": metadata_version,
            "homepage": config["homepage"],
            "totalPlugins": len(new_plugins),
            "lastUpdated": last_updated,
        },
    }

"""Schema validation for marketplace.json manifests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

REQUIRED_ROOT_FIELDS = ["name", "owner", "plugins"]
REQUIRED_OWNER_FIELDS = ["name", "email"]
REQUIRED_METADATA_FIELDS = ["description", "version"]
REQUIRED_PLUGIN_FIELDS = ["name", "source", "description", "version", "author"]
REQUIRED_AUTHOR_FIELDS = ["name"]


def validate_manifest(manifest: dict[str, Any], plugins_root: Path) -> list[str]:
    """Return a list of error strings for *manifest*.

    Checks required fields at each nesting level, then verifies that every
    plugin's source path resolves to an existing
    ``<plugins_root>/<name>/.claude-plugin/plugin.json``.

    *plugins_root* is the directory that contains the plugin subdirectories
    (i.e. the ``plugins/`` directory for either the private or public repo).
    """
    errors: list[str] = []

    # Root-level required fields
    for field in REQUIRED_ROOT_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required root field: {field}")

    if "owner" in manifest:
        owner = manifest["owner"]
        if isinstance(owner, dict):
            for field in REQUIRED_OWNER_FIELDS:
                if field not in owner:
                    errors.append(f"Missing required owner field: {field}")
        else:
            errors.append("owner must be an object")

    if "metadata" in manifest:
        meta = manifest["metadata"]
        if isinstance(meta, dict):
            for field in REQUIRED_METADATA_FIELDS:
                if field not in meta:
                    errors.append(f"Missing required metadata field: {field}")
        else:
            errors.append("metadata must be an object")

    if "plugins" in manifest:
        plugins = manifest["plugins"]
        if not isinstance(plugins, list):
            errors.append("plugins must be an array")
        else:
            for idx, plugin in enumerate(plugins):
                errors.extend(_validate_plugin_entry(plugin, idx, plugins_root))

    return errors


def _validate_plugin_entry(
    plugin: dict[str, Any], idx: int, plugins_root: Path
) -> list[str]:
    """Validate a single plugin entry within the plugins[] array."""
    errors: list[str] = []
    prefix = f"Plugin[{idx}]"

    for field in REQUIRED_PLUGIN_FIELDS:
        if field not in plugin:
            errors.append(f"{prefix}: Missing required field: {field}")

    if "author" in plugin:
        author = plugin["author"]
        if isinstance(author, dict):
            for field in REQUIRED_AUTHOR_FIELDS:
                if field not in author:
                    errors.append(f"{prefix}.author: Missing required field: {field}")
        else:
            errors.append(f"{prefix}.author must be an object")

    # Verify that the source path points to an existing plugin.json.
    # source is "./plugins/<name>" — strip leading "./" then resolve against
    # the repo root (parent of plugins_root).
    if "source" in plugin:
        source: str = plugin["source"]
        # Strip "./" prefix to get "plugins/<name>"
        stripped = source.lstrip("./")
        # The source path is relative to the repo root, which is the parent of
        # plugins_root (plugins_root IS the plugins/ dir).
        repo_root = plugins_root.parent
        candidate = repo_root / stripped / ".claude-plugin" / "plugin.json"
        if not candidate.exists():
            errors.append(f"{prefix}: Plugin not found at: {stripped}")

    return errors

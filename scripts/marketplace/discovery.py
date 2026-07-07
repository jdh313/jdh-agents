"""Plugin discovery: scan plugins_dir for valid plugin.json entries."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def discover_plugins(
    plugins_dir: Path,
    allowlist: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Return a sorted list of plugin registry entries from *plugins_dir*.

    Each entry matches the marketplace.json plugin shape:
        name, source, description, version, author,
        [keywords], [homepage], [repository], [defaultEnabled]

    If *allowlist* is given, only plugins whose name appears in the list are
    included.  Missing allowlisted names are NOT warned here — callers that need
    strict existence checks (e.g. build_public) should verify separately.

    Invalid plugin.json files are skipped with a warning to stderr.
    """
    plugins: list[dict[str, Any]] = []

    if not plugins_dir.exists():
        return plugins

    for plugin_json_path in plugins_dir.rglob("plugin.json"):
        try:
            with plugin_json_path.open(encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            print(
                f"Warning: Skipping invalid plugin.json at {plugin_json_path}: {exc}",
                file=sys.stderr,
            )
            continue

        # plugin_json_path: plugins/<name>/.claude-plugin/plugin.json
        # plugin_dir:       plugins/<name>/
        plugin_dir = plugin_json_path.parent.parent
        try:
            rel = plugin_dir.relative_to(plugins_dir)
        except ValueError:
            print(
                f"Warning: plugin.json outside plugins_dir, skipping: {plugin_json_path}",
                file=sys.stderr,
            )
            continue

        plugin_name = data.get("name", plugin_dir.name)

        if allowlist is not None and plugin_name not in allowlist:
            continue

        entry: dict[str, Any] = {
            "name": plugin_name,
            "source": f"./plugins/{rel}",
            "description": data.get("description", ""),
            "version": data.get("version", "1.0.0"),
            "author": data.get("author", {"name": "Unknown"}),
        }
        for optional_field in ("keywords", "homepage", "repository", "defaultEnabled"):
            if optional_field in data:
                entry[optional_field] = data[optional_field]

        plugins.append(entry)

    return sorted(plugins, key=lambda p: p["name"])

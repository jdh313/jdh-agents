#!/usr/bin/env python3
"""
Auto-sync marketplace.json from plugins directory

Scans plugins/ directory and updates marketplace.json with discovered plugins.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def discover_plugins(plugins_dir: Path) -> list[dict[str, Any]]:
    """Discover all plugins in the plugins directory."""
    plugins = []

    if not plugins_dir.exists():
        return plugins

    # Find all plugin.json files
    for plugin_json in plugins_dir.rglob("plugin.json"):
        try:
            with plugin_json.open() as f:
                plugin_data = json.load(f)

            # Calculate relative path from plugins dir
            # plugin_json is at: plugins/<plugin-name>/.claude-plugin/plugin.json
            # We want source to be just the plugin directory name (relative to plugins/)
            plugin_dir = plugin_json.parent.parent  # Go up from .claude-plugin to plugin root
            source_path = plugin_dir.relative_to(plugins_dir)

            plugin_entry = {
                "name": plugin_data.get("name", plugin_dir.name),
                "source": f"./plugins/{source_path}",
                "description": plugin_data.get("description", ""),
                "version": plugin_data.get("version", "1.0.0"),
                "author": plugin_data.get("author", {"name": "Unknown"}),
            }

            # Add optional fields if present
            if "keywords" in plugin_data:
                plugin_entry["keywords"] = plugin_data["keywords"]
            if "homepage" in plugin_data:
                plugin_entry["homepage"] = plugin_data["homepage"]
            if "repository" in plugin_data:
                plugin_entry["repository"] = plugin_data["repository"]

            plugins.append(plugin_entry)

        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Skipping invalid plugin.json at {plugin_json}: {e}", file=sys.stderr)

    return sorted(plugins, key=lambda p: p["name"])


def update_marketplace(marketplace_path: Path, plugins: list[dict[str, Any]]) -> None:
    """Update marketplace.json with discovered plugins."""
    with marketplace_path.open() as f:
        marketplace = json.load(f)

    old_plugins = marketplace.get("plugins", [])

    marketplace["plugins"] = plugins
    marketplace["metadata"]["totalPlugins"] = len(plugins)

    # Only bump lastUpdated when the plugin set actually changed, so CI re-runs
    # on later dates don't produce a no-op diff that fails the auto-sync check.
    if plugins != old_plugins:
        marketplace["metadata"]["lastUpdated"] = datetime.now().strftime("%Y-%m-%d")

    # Write back with pretty formatting
    with marketplace_path.open("w") as f:
        json.dump(marketplace, f, indent=2)
        f.write("\n")


def main() -> int:
    """Main sync entry point."""
    base_dir = Path(__file__).parent.parent
    plugins_dir = base_dir / "plugins"
    marketplace_path = base_dir / ".claude-plugin" / "marketplace.json"

    if not marketplace_path.exists():
        print(f"Error: {marketplace_path} not found", file=sys.stderr)
        return 1

    plugins = discover_plugins(plugins_dir)

    try:
        update_marketplace(marketplace_path, plugins)
        print(f"✅ Synced {len(plugins)} plugin(s) to marketplace.json")
        return 0
    except Exception as e:
        print(f"Error updating marketplace: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

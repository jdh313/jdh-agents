#!/usr/bin/env python3
"""
Plugin linter for Claude Code plugins

Validates plugin files for correctness and best practices.
"""

import json
import sys
from pathlib import Path
from typing import Any


def lint_plugin_file(plugin_path: Path) -> list[str]:
    """Lint a single plugin file."""
    errors = []
    warnings = []

    # Check file exists
    if not plugin_path.exists():
        return [f"File not found: {plugin_path}"]

    # Check file extension
    if plugin_path.suffix not in [".json", ".md", ".py", ".js"]:
        warnings.append(f"Unusual plugin file extension: {plugin_path.suffix}")

    # If JSON, validate structure
    if plugin_path.suffix == ".json":
        try:
            with plugin_path.open() as f:
                data = json.load(f)

            # Check for common plugin.json fields
            if "name" not in data:
                warnings.append("Missing 'name' field in plugin.json")
            if "version" not in data:
                warnings.append("Missing 'version' field in plugin.json")
            if "description" not in data:
                warnings.append("Missing 'description' field in plugin.json")

        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON: {e}")

    # If Markdown, check for basic structure
    if plugin_path.suffix == ".md":
        content = plugin_path.read_text()
        if not content.strip():
            errors.append("Empty plugin file")
        if len(content) < 50:
            warnings.append("Plugin file seems very short")

    return errors + [f"⚠️  {w}" for w in warnings]


def main() -> int:
    """Main linting entry point."""
    plugins_dir = Path(__file__).parent.parent / "plugins"

    if not plugins_dir.exists():
        print("No plugins directory found", file=sys.stderr)
        return 0

    plugin_files = list(plugins_dir.rglob("*"))
    plugin_files = [f for f in plugin_files if f.is_file() and not f.name.startswith(".")]

    if not plugin_files:
        print("No plugin files found to lint")
        return 0

    all_errors = []
    for plugin_file in plugin_files:
        rel_path = plugin_file.relative_to(plugins_dir)
        errors = lint_plugin_file(plugin_file)
        if errors:
            all_errors.append((rel_path, errors))

    if all_errors:
        print("Linting issues found:", file=sys.stderr)
        for path, errors in all_errors:
            print(f"\n{path}:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"✅ Linted {len(plugin_files)} plugin file(s) successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())

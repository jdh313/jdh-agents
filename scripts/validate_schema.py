#!/usr/bin/env python3
"""
Schema validator for Claude Code marketplace.json

Validates marketplace.json structure against the expected schema.
"""

import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_ROOT_FIELDS = ["name", "owner", "metadata", "plugins"]
REQUIRED_OWNER_FIELDS = ["name", "email"]
REQUIRED_METADATA_FIELDS = ["description", "version", "homepage"]
REQUIRED_PLUGIN_FIELDS = ["name", "source", "description", "version", "author"]
REQUIRED_AUTHOR_FIELDS = ["name"]


def validate_marketplace(data: dict[str, Any]) -> list[str]:
    """Validate marketplace.json structure."""
    errors = []

    # Check root fields
    for field in REQUIRED_ROOT_FIELDS:
        if field not in data:
            errors.append(f"Missing required root field: {field}")

    if "owner" in data:
        for field in REQUIRED_OWNER_FIELDS:
            if field not in data["owner"]:
                errors.append(f"Missing required owner field: {field}")

    if "metadata" in data:
        for field in REQUIRED_METADATA_FIELDS:
            if field not in data["metadata"]:
                errors.append(f"Missing required metadata field: {field}")

    # Validate plugins array
    if "plugins" in data:
        if not isinstance(data["plugins"], list):
            errors.append("plugins must be an array")
        else:
            for idx, plugin in enumerate(data["plugins"]):
                errors.extend(validate_plugin(plugin, idx))

    return errors


def validate_plugin(plugin: dict[str, Any], idx: int) -> list[str]:
    """Validate individual plugin entry."""
    errors = []
    prefix = f"Plugin[{idx}]"

    for field in REQUIRED_PLUGIN_FIELDS:
        if field not in plugin:
            errors.append(f"{prefix}: Missing required field: {field}")

    # Validate author
    if "author" in plugin:
        if isinstance(plugin["author"], dict):
            for field in REQUIRED_AUTHOR_FIELDS:
                if field not in plugin["author"]:
                    errors.append(f"{prefix}.author: Missing required field: {field}")
        else:
            errors.append(f"{prefix}.author must be an object")

    # Validate source path exists (source is relative to plugins/ directory)
    if "source" in plugin:
        source_path = Path(__file__).parent.parent / "plugins" / plugin["source"]
        plugin_json = source_path / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            errors.append(f"{prefix}: Plugin not found at: plugins/{plugin['source']}")

    return errors


def main() -> int:
    """Main validation entry point."""
    marketplace_file = Path(__file__).parent.parent / ".claude-plugin" / "marketplace.json"

    if not marketplace_file.exists():
        print(f"Error: {marketplace_file} not found", file=sys.stderr)
        return 1

    try:
        with marketplace_file.open() as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1

    errors = validate_marketplace(data)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("✅ Validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

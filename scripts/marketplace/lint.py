"""Plugin file linter — ports scripts/lint_plugins.py behaviour."""

from __future__ import annotations

import json
from pathlib import Path

ALLOWED_EXTENSIONS: frozenset[str] = frozenset(
    [
        # Core plugin files
        ".json",
        ".md",
        ".py",
        ".js",
        ".ts",
        # Asset / config files
        ".yaml",
        ".yml",
        ".txt",
        ".toml",
        ".base",
        # Web assets
        ".html",
        ".css",
        ".svg",
        # Shell scripts
        ".sh",
        ".bash",
    ]
)


def lint_plugins(plugins_root: Path) -> tuple[list[str], list[str]]:
    """Lint every non-dotfile under *plugins_root*.

    Returns ``(errors, warnings)``.  Errors represent definite problems
    (empty markdown, invalid JSON).  Warnings are advisory (unusual extension,
    suspiciously short markdown, missing plugin.json metadata fields).

    Mirrors the original ``lint_plugins.py`` logic exactly so that callers
    can reproduce the same output while also distinguishing severity.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not plugins_root.exists():
        # No plugins directory is not an error — nothing to lint.
        return errors, warnings

    plugin_files = [
        f for f in plugins_root.rglob("*") if f.is_file() and not f.name.startswith(".")
    ]

    for plugin_file in plugin_files:
        rel = plugin_file.relative_to(plugins_root)
        file_errors, file_warnings = _lint_file(plugin_file)
        for e in file_errors:
            errors.append(f"{rel}: {e}")
        for w in file_warnings:
            warnings.append(f"{rel}: {w}")

    return errors, warnings


def _lint_file(path: Path) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for a single file."""
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        return [f"File not found: {path}"], []

    if path.suffix not in ALLOWED_EXTENSIONS:
        warnings.append(f"Unusual plugin file extension: {path.suffix}")

    if path.suffix == ".json":
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)

            if path.name == "plugin.json":
                for field in ("name", "version", "description"):
                    if field not in data:
                        warnings.append(f"Missing '{field}' field in plugin.json")

        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSON: {exc}")

    if path.suffix == ".md":
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = path.read_bytes().decode("latin-1")

        if not content.strip():
            errors.append("Empty plugin file")
        elif len(content) < 50:
            warnings.append("Plugin file seems very short")

    return errors, warnings

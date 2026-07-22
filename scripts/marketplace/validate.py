"""Schema validation for marketplace.json manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

REQUIRED_ROOT_FIELDS = ["name", "owner", "metadata", "plugins"]
REQUIRED_OWNER_FIELDS = ["name", "email"]
REQUIRED_METADATA_FIELDS = ["description", "version", "homepage"]
REQUIRED_PLUGIN_FIELDS = ["name", "source", "description", "version", "author"]
REQUIRED_AUTHOR_FIELDS = ["name"]

CODEX_INSTALLATION_POLICIES = {
    "NOT_AVAILABLE",
    "AVAILABLE",
    "INSTALLED_BY_DEFAULT",
}
CODEX_AUTHENTICATION_POLICIES = {"ON_INSTALL", "ON_USE"}
CODEX_REQUIRED_INTERFACE_FIELDS = [
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
    "capabilities",
    "defaultPrompt",
]
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


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


def _validate_plugin_entry(plugin: dict[str, Any], idx: int, plugins_root: Path) -> list[str]:
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


def validate_codex_marketplace(manifest: dict[str, Any], repo_root: Path) -> list[str]:
    """Validate a repo-local Codex marketplace and each referenced plugin."""
    errors: list[str] = []

    _require_non_empty_string(manifest, "name", "Marketplace", errors)
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append("Marketplace: interface must be an object")
    else:
        _require_non_empty_string(interface, "displayName", "Marketplace.interface", errors)

    plugins = manifest.get("plugins")
    if not isinstance(plugins, list):
        errors.append("Marketplace: plugins must be an array")
        return errors

    seen: set[str] = set()
    for idx, entry in enumerate(plugins):
        prefix = f"Plugin[{idx}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix}: entry must be an object")
            continue

        name = _require_non_empty_string(entry, "name", prefix, errors)
        if name is not None:
            if name in seen:
                errors.append(f"{prefix}: duplicate plugin name: {name}")
            seen.add(name)

        _require_non_empty_string(entry, "category", prefix, errors)
        _validate_codex_policy(entry.get("policy"), prefix, errors)
        plugin_root = _validate_codex_source(entry.get("source"), repo_root, prefix, errors)
        if plugin_root is not None:
            errors.extend(_validate_codex_plugin(plugin_root, name, prefix))

    return errors


def _validate_codex_policy(policy: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(policy, dict):
        errors.append(f"{prefix}: policy must be an object")
        return
    if policy.get("installation") not in CODEX_INSTALLATION_POLICIES:
        errors.append(f"{prefix}.policy: invalid installation policy")
    if policy.get("authentication") not in CODEX_AUTHENTICATION_POLICIES:
        errors.append(f"{prefix}.policy: invalid authentication policy")


def _validate_codex_source(
    source: Any, repo_root: Path, prefix: str, errors: list[str]
) -> Path | None:
    if not isinstance(source, dict):
        errors.append(f"{prefix}: source must be an object")
        return None
    if source.get("source") != "local":
        errors.append(f"{prefix}.source: source must be 'local'")
    raw_path = source.get("path")
    if not isinstance(raw_path, str) or not raw_path.startswith("./"):
        errors.append(f"{prefix}.source: path must start with './'")
        return None

    candidate = (repo_root / raw_path[2:]).resolve()
    try:
        candidate.relative_to(repo_root.resolve())
    except ValueError:
        errors.append(f"{prefix}.source: path escapes the marketplace root")
        return None
    return candidate


def _validate_codex_plugin(plugin_root: Path, expected_name: str | None, prefix: str) -> list[str]:
    errors: list[str] = []
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{prefix}: Codex plugin manifest not found at {manifest_path}"]
    except json.JSONDecodeError as exc:
        return [f"{prefix}: invalid Codex plugin manifest JSON: {exc}"]

    if not isinstance(manifest, dict):
        return [f"{prefix}: Codex plugin manifest must be an object"]

    name = _require_non_empty_string(manifest, "name", f"{prefix}.manifest", errors)
    version = _require_non_empty_string(manifest, "version", f"{prefix}.manifest", errors)
    _require_non_empty_string(manifest, "description", f"{prefix}.manifest", errors)
    if expected_name is not None and name != expected_name:
        errors.append(f"{prefix}: marketplace name does not match Codex manifest name")
    if name is not None and plugin_root.name != name:
        errors.append(f"{prefix}: plugin directory does not match Codex manifest name")
    if version is not None and SEMVER_RE.fullmatch(version) is None:
        errors.append(f"{prefix}.manifest: version must use strict semver")

    author = manifest.get("author")
    if not isinstance(author, dict):
        errors.append(f"{prefix}.manifest: author must be an object")
    else:
        _require_non_empty_string(author, "name", f"{prefix}.manifest.author", errors)

    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{prefix}.manifest: interface must be an object")
    else:
        for field in CODEX_REQUIRED_INTERFACE_FIELDS:
            if field in {"capabilities", "defaultPrompt"}:
                values = interface.get(field)
                if (
                    not isinstance(values, list)
                    or not values
                    or not all(isinstance(value, str) and value.strip() for value in values)
                ):
                    errors.append(
                        f"{prefix}.manifest.interface: {field} must be a non-empty string array"
                    )
            else:
                _require_non_empty_string(interface, field, f"{prefix}.manifest.interface", errors)

    claude_path = plugin_root / ".claude-plugin" / "plugin.json"
    if claude_path.is_file():
        try:
            claude_manifest = json.loads(claude_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{prefix}: invalid Claude plugin manifest JSON: {exc}")
        else:
            if claude_manifest.get("name") != name:
                errors.append(f"{prefix}: Claude and Codex manifest names differ")
            if claude_manifest.get("version") != version:
                errors.append(f"{prefix}: Claude and Codex manifest versions differ")

    errors.extend(_validate_codex_skill_frontmatter(plugin_root, prefix))
    return errors


def _validate_codex_skill_frontmatter(plugin_root: Path, prefix: str) -> list[str]:
    errors: list[str] = []
    for skill_path in sorted((plugin_root / "skills").glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            errors.append(f"{prefix}: {skill_path} has no YAML frontmatter")
            continue
        raw_frontmatter = text[4:].split("\n---\n", 1)[0]
        try:
            frontmatter = yaml.safe_load(raw_frontmatter)
        except yaml.YAMLError as exc:
            errors.append(f"{prefix}: invalid skill frontmatter in {skill_path}: {exc}")
            continue
        if not isinstance(frontmatter, dict):
            errors.append(f"{prefix}: skill frontmatter in {skill_path} must be an object")
            continue
        _require_non_empty_string(frontmatter, "name", str(skill_path), errors)
        _require_non_empty_string(frontmatter, "description", str(skill_path), errors)
    return errors


def _require_non_empty_string(
    payload: dict[str, Any], key: str, prefix: str, errors: list[str]
) -> str | None:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}: {key} must be a non-empty string")
        return None
    return value

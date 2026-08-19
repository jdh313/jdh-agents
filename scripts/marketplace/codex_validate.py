"""Validate agent-marketplace's generated local Codex publication layout.

Codex does not currently expose a non-interactive ``plugin validate`` command,
so agent-marketplace validates the generated local publication shape it owns. This
module deliberately validates only packages declared by the supplied
marketplace; it does not infer support from unrelated canonical packages or
attempt to validate every Codex marketplace source form.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

_KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
_INSTALLATION_POLICIES = {"AVAILABLE", "INSTALLED_BY_DEFAULT", "NOT_AVAILABLE"}
_AUTHENTICATION_POLICIES = {"ON_INSTALL", "ON_FIRST_USE"}
_HOOK_EVENTS = {
    "PreToolUse",
    "PermissionRequest",
    "PostToolUse",
    "PreCompact",
    "PostCompact",
    "UserPromptSubmit",
    "SubagentStart",
    "SubagentStop",
    "Stop",
    "SessionStart",
    "SessionEnd",
}
# Codex caps a configured SessionEnd timeout at three seconds.
_SESSION_END_TIMEOUT_CAP = 3
# Companion scripts are referenced either through the plugin root — natively or
# through Codex's legacy Claude alias — or as a plain plugin-relative ./ path.
_COMPANION_REFERENCES = (
    re.compile(r"\$\{(?:CLAUDE_)?PLUGIN_ROOT\}/([^\s\"']+)"),
    re.compile(r"(?:^|[\s\"'])\./([^\s\"']+)"),
)


def validate_codex_marketplace(manifest: Any, plugins_root: Path) -> list[str]:
    """Return errors for agent-marketplace's materialized local Codex publication.

    ``plugins_root`` is the publication's ``plugins/`` directory.  Local
    marketplace sources are resolved relative to its parent, matching Codex's
    repository-marketplace path rules.
    """

    if not isinstance(manifest, dict):
        return ["Marketplace manifest must be an object"]

    errors: list[str] = []
    publication_root = plugins_root.resolve().parent

    _require_nonempty_string(manifest, "name", "Marketplace", errors)
    interface = manifest.get("interface")
    if interface is not None:
        if not isinstance(interface, dict):
            errors.append("Marketplace.interface must be an object")
        else:
            _require_nonempty_string(interface, "displayName", "Marketplace.interface", errors)

    entries = manifest.get("plugins")
    if not isinstance(entries, list):
        errors.append("Marketplace.plugins must be an array")
        return errors

    declared_names: list[str] = []
    for index, entry in enumerate(entries):
        prefix = f"Plugin[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue

        name = entry.get("name")
        if not isinstance(name, str) or not _KEBAB_CASE.fullmatch(name):
            errors.append(f"{prefix}.name must be a non-empty kebab-case string")
            continue
        if name in declared_names:
            errors.append(f"{prefix}.name duplicates declared plugin: {name}")
        declared_names.append(name)

        plugin_dir = _validate_local_source(
            entry.get("source"), name, prefix, publication_root, plugins_root, errors
        )
        _validate_policy(entry.get("policy"), prefix, errors)
        _require_nonempty_string(entry, "category", prefix, errors)
        if plugin_dir is not None:
            _validate_plugin(plugin_dir, name, errors)

    if plugins_root.is_dir():
        materialized_names = sorted(
            path.name
            for path in plugins_root.iterdir()
            if path.is_dir() and (path / ".codex-plugin" / "plugin.json").is_file()
        )
        declared_set = set(declared_names)
        for name in sorted(declared_set - set(materialized_names)):
            errors.append(f"Declared Codex plugin is not materialized: {name}")
        for name in sorted(set(materialized_names) - declared_set):
            errors.append(f"Undeclared Codex plugin is materialized: {name}")
    else:
        errors.append(f"Codex plugins root not found: {plugins_root}")

    return errors


def _validate_local_source(
    source: Any,
    name: str,
    prefix: str,
    publication_root: Path,
    plugins_root: Path,
    errors: list[str],
) -> Path | None:
    if not isinstance(source, dict):
        errors.append(f"{prefix}.source must be a local source object")
        return None
    if source.get("source") != "local":
        errors.append(f'{prefix}.source.source must be "local"')
    path_value = source.get("path")
    if not isinstance(path_value, str) or not path_value.startswith("./"):
        errors.append(f"{prefix}.source.path must be a ./-prefixed relative path")
        return None

    candidate = (publication_root / path_value).resolve()
    try:
        candidate.relative_to(publication_root)
    except ValueError:
        errors.append(f"{prefix}.source.path escapes the marketplace root: {path_value}")
        return None

    expected = (plugins_root / name).resolve()
    if candidate != expected:
        errors.append(f"{prefix}.source.path must point to ./plugins/{name}, got {path_value}")
    if not candidate.is_dir():
        errors.append(f"{prefix}.source.path does not resolve to a plugin directory: {path_value}")
        return None
    return candidate


def _validate_policy(policy: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(policy, dict):
        errors.append(f"{prefix}.policy must be an object")
        return
    installation = policy.get("installation")
    if installation not in _INSTALLATION_POLICIES:
        errors.append(
            f"{prefix}.policy.installation must be one of "
            f"{', '.join(sorted(_INSTALLATION_POLICIES))}"
        )
    authentication = policy.get("authentication")
    if authentication not in _AUTHENTICATION_POLICIES:
        errors.append(
            f"{prefix}.policy.authentication must be one of "
            f"{', '.join(sorted(_AUTHENTICATION_POLICIES))}"
        )


def _validate_plugin(plugin_dir: Path, expected_name: str, errors: list[str]) -> None:
    manifest_path = plugin_dir / ".codex-plugin" / "plugin.json"
    prefix = f"Plugin[{expected_name}]"
    manifest = _read_json_object(manifest_path, prefix, errors)
    if manifest is None:
        return

    name = manifest.get("name")
    if name != expected_name:
        errors.append(f"{prefix} manifest name must be {expected_name!r}, got {name!r}")
    version = manifest.get("version")
    if not isinstance(version, str) or not _is_strict_semver(version):
        errors.append(f"{prefix} manifest version must be strict semantic versioning")
    _require_nonempty_string(manifest, "description", f"{prefix} manifest", errors)

    author = manifest.get("author")
    if not isinstance(author, dict):
        errors.append(f"{prefix} manifest.author must be an object")
    else:
        _require_nonempty_string(author, "name", f"{prefix} manifest.author", errors)

    interface = manifest.get("interface")
    if interface is not None and not isinstance(interface, dict):
        errors.append(f"{prefix} manifest.interface must be an object")
    elif isinstance(interface, dict):
        for field in (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
        ):
            if field in interface and not _is_nonempty_string(interface[field]):
                errors.append(f"{prefix} manifest.interface.{field} must be a non-empty string")
        for field in ("capabilities", "defaultPrompt", "screenshots"):
            if field in interface and not _is_string_list(interface[field]):
                errors.append(f"{prefix} manifest.interface.{field} must be an array of strings")

    for field in ("skills", "mcpServers", "apps", "hooks"):
        if field in manifest:
            _validate_component_paths(manifest[field], field, plugin_dir, prefix, errors)

    for skill_file in sorted(plugin_dir.glob("skills/*/SKILL.md")):
        _validate_skill(skill_file, errors)
    for sidecar in sorted(plugin_dir.glob("skills/*/agents/openai.yaml")):
        _validate_skill_sidecar(sidecar, errors)


def _validate_component_paths(
    value: Any, field: str, plugin_dir: Path, prefix: str, errors: list[str]
) -> None:
    paths = value if isinstance(value, list) else [value]
    if not paths or not all(isinstance(path, str) for path in paths):
        errors.append(f"{prefix} manifest.{field} must be a path or array of paths")
        return
    for path_value in paths:
        if not path_value.startswith("./"):
            errors.append(f"{prefix} manifest.{field} path must start with ./: {path_value}")
            continue
        candidate = (plugin_dir / path_value).resolve()
        try:
            candidate.relative_to(plugin_dir.resolve())
        except ValueError:
            errors.append(f"{prefix} manifest.{field} path escapes plugin root: {path_value}")
            continue
        if not candidate.exists():
            errors.append(f"{prefix} manifest.{field} path does not exist: {path_value}")
            continue
        if field == "hooks":
            _validate_hook_configuration(candidate, path_value, plugin_dir, prefix, errors)


def _validate_hook_configuration(
    hook_file: Path, path_value: str, plugin_dir: Path, prefix: str, errors: list[str]
) -> None:
    """Check a declared hook configuration against what was materialized.

    A declared path that merely exists is not enough: the handler commands
    inside it name companion scripts, and a hook whose script was never
    materialized is skipped at runtime rather than reported.
    """
    label = f"{prefix} manifest.hooks[{path_value}]"
    try:
        document = json.loads(hook_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        errors.append(f"{label} could not be read: {error}")
        return
    except json.JSONDecodeError as error:
        errors.append(f"{label} is not valid JSON: {error}")
        return

    if not isinstance(document, dict):
        errors.append(f"{label} must be a JSON object")
        return
    events = document.get("hooks")
    if not isinstance(events, dict):
        errors.append(f"{label} must declare a hooks object")
        return

    for event, groups in sorted(events.items()):
        if event not in _HOOK_EVENTS:
            errors.append(f"{label} declares unknown Codex hook event: {event}")
            continue
        if not isinstance(groups, list) or not groups:
            errors.append(f"{label} event {event} must be a non-empty array")
            continue
        for group in groups:
            if not isinstance(group, dict):
                errors.append(f"{label} event {event} entries must be objects")
                continue
            handlers = group.get("hooks")
            if not isinstance(handlers, list) or not handlers:
                errors.append(f"{label} event {event} must declare a non-empty hooks array")
                continue
            for handler in handlers:
                _validate_hook_handler(handler, event, label, plugin_dir, errors)


def _validate_hook_handler(
    handler: Any, event: str, label: str, plugin_dir: Path, errors: list[str]
) -> None:
    if not isinstance(handler, dict):
        errors.append(f"{label} event {event} handlers must be objects")
        return
    if handler.get("type") != "command":
        errors.append(f"{label} event {event} handler type must be \"command\"")
    if "args" in handler:
        errors.append(
            f"{label} event {event} handler declares args, which Codex has no field for; "
            "fold arguments into command"
        )
    command = handler.get("command")
    if not _is_nonempty_string(command):
        errors.append(f"{label} event {event} handler command must be a non-empty string")
        return

    timeout = handler.get("timeout")
    capped = isinstance(timeout, (int, float)) and timeout > _SESSION_END_TIMEOUT_CAP
    if event == "SessionEnd" and capped:
        errors.append(
            f"{label} event SessionEnd declares a {timeout}s timeout; "
            f"Codex caps it at {_SESSION_END_TIMEOUT_CAP}s"
        )

    references = {
        reference for pattern in _COMPANION_REFERENCES for reference in pattern.findall(command)
    }
    for reference in sorted(references):
        companion = (plugin_dir / reference).resolve()
        try:
            companion.relative_to(plugin_dir.resolve())
        except ValueError:
            errors.append(f"{label} event {event} handler command escapes plugin root: {reference}")
            continue
        if not companion.exists():
            errors.append(
                f"{label} event {event} handler command references a path that was not "
                f"materialized: {reference}"
            )


def _validate_skill(skill_file: Path, errors: list[str]) -> None:
    relative = skill_file.parent.name
    prefix = f"Skill[{skill_file.as_posix()}]"
    try:
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        if isinstance(error, UnicodeDecodeError):
            errors.append(f"{prefix} must be UTF-8")
        else:
            errors.append(f"{prefix} could not be read: {error}")
        return
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"{prefix} must start with YAML frontmatter")
        return
    try:
        closing = lines.index("---", 1)
    except ValueError:
        errors.append(f"{prefix} has unterminated YAML frontmatter")
        return
    try:
        frontmatter = yaml.safe_load("\n".join(lines[1:closing]))
    except yaml.YAMLError as error:
        errors.append(f"{prefix} has invalid YAML frontmatter: {error}")
        return
    if not isinstance(frontmatter, dict):
        errors.append(f"{prefix} YAML frontmatter must be an object")
        return

    name = frontmatter.get("name")
    if not isinstance(name, str) or name != relative or not _KEBAB_CASE.fullmatch(name):
        errors.append(f"{prefix} name must match its skill directory: {relative}")
    if not _is_nonempty_string(frontmatter.get("description")):
        errors.append(f"{prefix} description must not be empty")


def _validate_skill_sidecar(sidecar: Path, errors: list[str]) -> None:
    prefix = f"Skill sidecar[{sidecar.as_posix()}]"
    try:
        text = sidecar.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        if isinstance(error, UnicodeDecodeError):
            errors.append(f"{prefix} must be UTF-8")
        else:
            errors.append(f"{prefix} could not be read: {error}")
        return
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as error:
        errors.append(f"{prefix} is invalid YAML: {error}")
        return
    if not isinstance(value, dict):
        errors.append(f"{prefix} must be a YAML object")
        return
    policy = value.get("policy")
    if not isinstance(policy, dict) or policy.get("allow_implicit_invocation") is not False:
        errors.append(f"{prefix} must set policy.allow_implicit_invocation: false")


def _is_strict_semver(value: str) -> bool:
    if not _SEMVER.fullmatch(value):
        return False
    without_build = value.split("+", 1)[0]
    if "-" not in without_build:
        return True
    prerelease = without_build.split("-", 1)[1]
    return all(
        not (identifier.isdigit() and len(identifier) > 1 and identifier.startswith("0"))
        for identifier in prerelease.split(".")
    )


def _read_json_object(path: Path, prefix: str, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"{prefix} manifest not found: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        errors.append(f"{prefix} manifest is invalid JSON: {error}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{prefix} manifest must be an object")
        return None
    return value


def _require_nonempty_string(
    value: dict[str, Any], field: str, prefix: str, errors: list[str]
) -> None:
    if not _is_nonempty_string(value.get(field)):
        errors.append(f"{prefix}.{field} must be a non-empty string")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_is_nonempty_string(item) for item in value)

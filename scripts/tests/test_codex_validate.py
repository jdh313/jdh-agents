"""Tests for agent-marketplace's Codex-native publication validator."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from marketplace.__main__ import _build_parser, _cmd_validate  # noqa: PLC2701
from marketplace.codex_validate import validate_codex_marketplace


def _make_codex_publication(root: Path, names: tuple[str, ...] = ("alpha",)) -> dict:
    plugins = []
    for name in names:
        plugin_root = root / "plugins" / name
        (plugin_root / ".codex-plugin").mkdir(parents=True)
        (plugin_root / "skills" / "hello").mkdir(parents=True)
        (plugin_root / ".codex-plugin" / "plugin.json").write_text(
            json.dumps(
                {
                    "name": name,
                    "version": "1.2.3",
                    "description": f"The {name} plugin",
                    "author": {"name": "Tester"},
                    "interface": {
                        "displayName": name.title(),
                        "capabilities": ["Read"],
                        "defaultPrompt": ["Use this plugin."],
                    },
                }
            ),
            encoding="utf-8",
        )
        (plugin_root / "skills" / "hello" / "SKILL.md").write_text(
            "---\nname: hello\ndescription: Say hello.\n---\n\n# Hello\n",
            encoding="utf-8",
        )
        plugins.append(
            {
                "name": name,
                "source": {"source": "local", "path": f"./plugins/{name}"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools",
            }
        )
    return {
        "name": "test-marketplace",
        "interface": {"displayName": "Test Marketplace"},
        "plugins": plugins,
    }


def test_validates_declared_codex_packages(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path, ("alpha", "beta"))

    assert validate_codex_marketplace(manifest, tmp_path / "plugins") == []


def test_validate_cli_accepts_codex_generated_paths(tmp_path: Path, capsys) -> None:
    manifest = _make_codex_publication(tmp_path)
    manifest_path = tmp_path / ".agents/plugins/marketplace.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    args = _build_parser().parse_args(
        [
            "validate",
            "--format",
            "codex",
            "--manifest",
            str(manifest_path),
            "--plugins-root",
            str(tmp_path / "plugins"),
        ]
    )

    assert _cmd_validate(args) == 0
    assert "Codex validation passed (1 plugins)." in capsys.readouterr().out


def test_rejects_undeclared_materialized_package(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path, ("alpha", "extra"))
    manifest["plugins"] = manifest["plugins"][:1]

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert "Undeclared Codex plugin is materialized: extra" in errors


def test_ignores_source_package_without_codex_manifest(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    (tmp_path / "plugins/claude-only/skills/hello").mkdir(parents=True)
    (tmp_path / "plugins/claude-only/skills/hello/SKILL.md").write_text(
        "---\nname: hello\ndescription: Claude only.\n---\n",
        encoding="utf-8",
    )

    assert validate_codex_marketplace(manifest, tmp_path / "plugins") == []


def test_rejects_missing_declared_package(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path, ("alpha",))
    manifest["plugins"].append(
        {
            "name": "missing",
            "source": {"source": "local", "path": "./plugins/missing"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }
    )

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("does not resolve to a plugin directory" in error for error in errors)
    assert "Declared Codex plugin is not materialized: missing" in errors


def test_rejects_manifest_identity_and_semver_drift(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    plugin_manifest = tmp_path / "plugins/alpha/.codex-plugin/plugin.json"
    value = json.loads(plugin_manifest.read_text(encoding="utf-8"))
    value["name"] = "different"
    value["version"] = "latest"
    plugin_manifest.write_text(json.dumps(value), encoding="utf-8")

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("manifest name must be 'alpha'" in error for error in errors)
    assert any("strict semantic versioning" in error for error in errors)


@pytest.mark.parametrize("version", ("1.0.0-01", "1.0.0-alpha.00", "01.0.0"))
def test_rejects_non_strict_semver(tmp_path: Path, version: str) -> None:
    manifest = _make_codex_publication(tmp_path)
    plugin_manifest = tmp_path / "plugins/alpha/.codex-plugin/plugin.json"
    value = json.loads(plugin_manifest.read_text(encoding="utf-8"))
    value["version"] = version
    plugin_manifest.write_text(json.dumps(value), encoding="utf-8")

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("strict semantic versioning" in error for error in errors)


def test_accepts_strict_semver_prerelease(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    plugin_manifest = tmp_path / "plugins/alpha/.codex-plugin/plugin.json"
    value = json.loads(plugin_manifest.read_text(encoding="utf-8"))
    value["version"] = "1.0.0-alpha.0+build.01"
    plugin_manifest.write_text(json.dumps(value), encoding="utf-8")

    assert validate_codex_marketplace(manifest, tmp_path / "plugins") == []


def test_rejects_invalid_skill_and_explicit_only_sidecar(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    skill_root = tmp_path / "plugins/alpha/skills/hello"
    (skill_root / "SKILL.md").write_text(
        "---\nname: wrong\ndescription:\n---\n",
        encoding="utf-8",
    )
    (skill_root / "agents").mkdir()
    (skill_root / "agents/openai.yaml").write_text(
        "policy:\n  allow_implicit_invocation: true\n",
        encoding="utf-8",
    )

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("name must match its skill directory" in error for error in errors)
    assert any("description must not be empty" in error for error in errors)
    assert any("allow_implicit_invocation: false" in error for error in errors)


def test_rejects_malformed_skill_frontmatter(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    skill_file = tmp_path / "plugins/alpha/skills/hello/SKILL.md"
    skill_file.write_text(
        "---\nname: [hello\ndescription: Broken YAML.\n---\n",
        encoding="utf-8",
    )

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("invalid YAML frontmatter" in error for error in errors)


def test_requires_exact_skill_frontmatter_delimiter(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    skill_file = tmp_path / "plugins/alpha/skills/hello/SKILL.md"
    skill_file.write_text(
        "---\nname: hello\ndescription: Not really closed.\n---garbage\n",
        encoding="utf-8",
    )

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("unterminated YAML frontmatter" in error for error in errors)


def test_rejects_misplaced_sidecar_policy(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    sidecar = tmp_path / "plugins/alpha/skills/hello/agents/openai.yaml"
    sidecar.parent.mkdir()
    sidecar.write_text("allow_implicit_invocation: false\n", encoding="utf-8")

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("must set policy.allow_implicit_invocation: false" in error for error in errors)


def test_rejects_malformed_sidecar_yaml(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    sidecar = tmp_path / "plugins/alpha/skills/hello/agents/openai.yaml"
    sidecar.parent.mkdir()
    sidecar.write_text("policy: [unterminated\n", encoding="utf-8")

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("is invalid YAML" in error for error in errors)


def test_rejects_non_utf8_skill_and_sidecar_without_raising(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    skill_root = tmp_path / "plugins/alpha/skills/hello"
    (skill_root / "SKILL.md").write_bytes(b"\xff")
    sidecar = skill_root / "agents/openai.yaml"
    sidecar.parent.mkdir()
    sidecar.write_bytes(b"\xff")

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    utf8_errors = [error for error in errors if "must be UTF-8" in error]
    assert len(utf8_errors) == 2


@pytest.mark.parametrize("value", (None, [], "marketplace"))
def test_rejects_non_object_marketplace(value: object, tmp_path: Path) -> None:
    assert validate_codex_marketplace(value, tmp_path / "plugins") == [
        "Marketplace manifest must be an object"
    ]


def test_validate_cli_rejects_non_object_json_without_raising(tmp_path: Path, capsys) -> None:
    manifest_path = tmp_path / "marketplace.json"
    manifest_path.write_text("[]", encoding="utf-8")
    args = _build_parser().parse_args(
        [
            "validate",
            "--format",
            "codex",
            "--manifest",
            str(manifest_path),
            "--plugins-root",
            str(tmp_path / "plugins"),
        ]
    )

    assert _cmd_validate(args) == 1
    assert "Marketplace manifest must be an object" in capsys.readouterr().err


def test_rejects_source_escape(tmp_path: Path) -> None:
    manifest = _make_codex_publication(tmp_path)
    manifest["plugins"][0]["source"]["path"] = "./plugins/../../outside"

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("escapes the marketplace root" in error for error in errors)


# TEAM-341, bullet 2 (second clause): `marketplace validate --format codex` must
# reject a manifest whose declared hook configuration does not match what was
# materialized -- not just check that the declared `hooks` path itself exists.
#
# `_validate_component_paths` today only confirms the manifest-declared
# `hooks` path (e.g. `./hooks/hooks.json`) exists on disk; it never opens that
# file to check the handler commands it references. A hooks.json whose
# PreToolUse handler points at a companion script that was never materialized
# currently validates cleanly, which is the gap this test exercises.
def test_rejects_hook_configuration_referencing_a_missing_companion_script(
    tmp_path: Path,
) -> None:
    manifest = _make_codex_publication(tmp_path)
    plugin_dir = tmp_path / "plugins/alpha"
    hooks_dir = plugin_dir / "hooks"
    hooks_dir.mkdir()
    hooks_dir.joinpath("hooks.json").write_text(
        json.dumps(
            {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Bash",
                            "hooks": [
                                {"type": "command", "command": "./hooks/missing-guard.sh"}
                            ],
                        }
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    # Intentionally not created: ./hooks/missing-guard.sh

    plugin_manifest = plugin_dir / ".codex-plugin/plugin.json"
    value = json.loads(plugin_manifest.read_text(encoding="utf-8"))
    value["hooks"] = "./hooks/hooks.json"
    plugin_manifest.write_text(json.dumps(value), encoding="utf-8")

    errors = validate_codex_marketplace(manifest, tmp_path / "plugins")

    assert any("missing-guard.sh" in error for error in errors)

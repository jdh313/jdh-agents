#!/usr/bin/env python3
"""Guarded native-plugin lifecycle acceptance for Craft's Codex agent bundle.

This is intentionally a thin Craft specialization of the Linear lifecycle
harness. It consumes a committed source archive for the initial native plugin
installation; it creates only disposable, compiler-generated Craft updates
under RUN_ROOT to exercise content update, rename, and deletion receipts.

Example (use a fresh directory under /private/tmp):

  python3 scripts/tests/run_craft_codex_lifecycle.py \\
    --agentforge-bin /absolute/agentforge-darwin-arm64 \\
    --codex-bin /absolute/codex --source-repo "$PWD" \\
    --source-commit <committed-sha> \\
    --run-root /private/tmp/craft-codex-lifecycle/run-001

It establishes only lifecycle/native-cache evidence. Setup-skill activation,
dispatch, reviewer behavior, and applied runtime settings belong to the
separate Craft probe evidence.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from typing import Iterable

from run_linear_codex_lifecycle import (  # Shared sealed lifecycle mechanics.
    Harness,
    HarnessError,
    Scope,
    agent_definition,
    bundle_data,
    byte_mode_snapshot,
    replace_version,
    sha256,
    snapshot,
    write_json,
)


PACKAGE_ID = "craft"
BASE_VERSION = "0.16.0"
CONTENT_VERSION = "0.16.1"
RENAME_DELETE_VERSION = "0.16.2"
RENAMED_AGENT = "comment-reviewer-renamed"
DELETED_AGENT = "copy-reviewer"


class CraftHarness(Harness):
    """Craft package operations over Linear's guarded native lifecycle shell."""

    def __init__(self, args) -> None:  # argparse namespace owned by the shared parser.
        super().__init__(args)
        self.package_id = PACKAGE_ID

    @staticmethod
    def package_version(authoring: Path) -> str:
        package = authoring / "plugins" / PACKAGE_ID / "PACKAGE.yaml"
        match = re.search(r'"version": "([0-9]+\.[0-9]+\.[0-9]+)"', package.read_text())
        if match is None:
            raise HarnessError(f"Craft PACKAGE.yaml has no JSON-style version: {package}")
        return match.group(1)

    def require_agents(self, bundle: Path, expected: Iterable[str], label: str) -> None:
        actual = {str(agent["id"]) for agent in bundle_data(bundle)["agents"]}
        wanted = set(expected)
        if actual != wanted:
            raise HarnessError(f"{label} agent IDs are {sorted(actual)}, expected {sorted(wanted)}")

    def authoring_fixtures(self, source_archive: Path, marketplace_archive: Path):
        authoring = self.run_root / "authoring"
        base_marketplace = self.run_root / "marketplace-base"
        authoring.mkdir()
        base_marketplace.mkdir()
        from run_linear_codex_lifecycle import safe_extract

        safe_extract(source_archive, authoring)
        safe_extract(marketplace_archive, base_marketplace)
        self.command("fixture-git-init", ["git", "init", "-q"], cwd=authoring)
        self.command("fixture-git-add-base", ["git", "add", "-A"], cwd=authoring)
        self.command(
            "fixture-git-commit-base",
            ["git", "-c", "user.name=Craft lifecycle harness", "-c", "user.email=craft-lifecycle@example.invalid",
             "commit", "-qm", "fixture: committed Craft source archive"],
            cwd=authoring,
        )

        bundle = base_marketplace / "plugins" / PACKAGE_ID / ".agentforge" / "codex-agent-bundle"
        if self.package_version(authoring) != BASE_VERSION:
            raise HarnessError(
                f"Craft lifecycle requires committed v{BASE_VERSION}; got v{self.package_version(authoring)}"
            )
        self.assert_bundle_version(bundle, BASE_VERSION, "committed Craft")
        self.require_agents(bundle, {"comment-reviewer", "copy-reviewer", "house-style-reviewer"}, "committed Craft")
        self.save_snapshot("committed-marketplace", base_marketplace)

        package = authoring / "plugins" / PACKAGE_ID / "PACKAGE.yaml"
        changed = authoring / "plugins" / PACKAGE_ID / "agents" / "comment-reviewer.md"
        if replace_version(package, CONTENT_VERSION) != BASE_VERSION:
            raise HarnessError("Craft content fixture did not start from v" + BASE_VERSION)
        changed.write_text(changed.read_text() + "\n<!-- disposable Craft lifecycle content update -->\n")
        self.compile_fixture(authoring, "content", CONTENT_VERSION)
        content_marketplace = self.run_root / f"marketplace-update-{CONTENT_VERSION}"
        shutil.copytree(authoring / "marketplaces" / "codex", content_marketplace)
        content_bundle = content_marketplace / "plugins" / PACKAGE_ID / ".agentforge" / "codex-agent-bundle"
        self.assert_bundle_version(content_bundle, CONTENT_VERSION, "Craft content fixture")
        self.require_agents(content_bundle, {"comment-reviewer", "copy-reviewer", "house-style-reviewer"}, "Craft content fixture")
        self.save_snapshot("content-marketplace", content_marketplace)

        old = changed
        renamed = old.with_name(RENAMED_AGENT + ".md")
        old.rename(renamed)
        renamed.write_text(renamed.read_text().replace("name: comment-reviewer\n", "name: " + RENAMED_AGENT + "\n", 1))
        deleted = authoring / "plugins" / PACKAGE_ID / "agents" / (DELETED_AGENT + ".md")
        if not deleted.is_file():
            raise HarnessError("Craft rename/deletion fixture lacks " + str(deleted))
        deleted.unlink()
        if replace_version(package, RENAME_DELETE_VERSION) != CONTENT_VERSION:
            raise HarnessError("Craft rename/deletion fixture did not start from v" + CONTENT_VERSION)
        self.compile_fixture(authoring, "rename-delete", RENAME_DELETE_VERSION)
        renamed_marketplace = self.run_root / f"marketplace-update-{RENAME_DELETE_VERSION}"
        shutil.copytree(authoring / "marketplaces" / "codex", renamed_marketplace)
        renamed_bundle = renamed_marketplace / "plugins" / PACKAGE_ID / ".agentforge" / "codex-agent-bundle"
        self.assert_bundle_version(renamed_bundle, RENAME_DELETE_VERSION, "Craft rename/deletion fixture")
        self.require_agents(renamed_bundle, {RENAMED_AGENT, "house-style-reviewer"}, "Craft rename/deletion fixture")
        self.save_snapshot("rename-delete-marketplace", renamed_marketplace)
        return base_marketplace, content_marketplace, renamed_marketplace

    def compile_fixture(self, authoring: Path, label: str, version: str) -> None:
        """Compile only the disposable authoring archive with the released binary."""
        import os
        import subprocess
        from run_linear_codex_lifecycle import COMMAND_TIMEOUT_SECONDS, SYSTEM_PATH

        env = {"PATH": os.environ.get("PATH", SYSTEM_PATH), "AGENTFORGE_BIN": str(self.agentforge_bin)}
        for suffix, argv in (
            ("compile", [str(authoring / "scripts" / "agentforge.sh"), "compile", "MARKETPLACE.yaml", "--out", "marketplaces"]),
            ("check", [str(authoring / "scripts" / "agentforge.sh"), "check", "MARKETPLACE.yaml", "--out", "marketplaces"]),
        ):
            self.sequence += 1
            stem = f"{self.sequence:03d}-fixture-{label}-{suffix}"
            write_json(self.evidence / f"{stem}.command.json", {"argv": argv, "cwd": str(authoring), "env": env, "authoring_fixture": True})
            completed = subprocess.run(argv, cwd=authoring, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       check=False, timeout=COMMAND_TIMEOUT_SECONDS)
            (self.evidence / f"{stem}.stdout").write_bytes(completed.stdout)
            (self.evidence / f"{stem}.stderr").write_bytes(completed.stderr)
            (self.evidence / f"{stem}.exit").write_text(f"{completed.returncode}\n")
            self.summary.append({"label": f"fixture-{label}-{suffix}", "exit": completed.returncode, "expected": 0})
            if completed.returncode:
                raise HarnessError(f"fixture {label} {suffix} failed; evidence: {stem}")
        self.command("fixture-git-add-" + label, ["git", "add", "plugins/craft", "marketplaces", ".claude-plugin"], cwd=authoring)
        self.command(
            "fixture-git-commit-" + label,
            ["git", "-c", "user.name=Craft lifecycle harness", "-c", "user.email=craft-lifecycle@example.invalid",
             "commit", "-qm", f"fixture: Craft {label} {version}"],
            cwd=authoring,
        )

    def install_native(self, scope: Scope, label: str, marketplace: Path):
        self.native(scope, label + "-marketplace-add", "plugin", "marketplace", "add", str(marketplace))
        self.native(scope, label + "-plugin-add", "plugin", "add", PACKAGE_ID + "@jdh-agents", "--json")
        output = self.evidence / f"{self.sequence:03d}-{label}-plugin-add.stdout"
        from run_linear_codex_lifecycle import installed_plugin_root

        cache = installed_plugin_root(output)
        if scope.codex_home / "plugins" / "cache" not in cache.parents:
            raise HarnessError("native Craft cache escaped isolated CODEX_HOME: " + str(cache))
        bundle = cache / ".agentforge" / "codex-agent-bundle"
        bundle_data(bundle)
        compiled_plugin = marketplace / "plugins" / PACKAGE_ID
        if not compiled_plugin.is_dir():
            raise HarnessError("committed marketplace lacks Craft plugin: " + str(compiled_plugin))
        compiled_snapshot, cache_snapshot = snapshot(compiled_plugin), snapshot(cache)
        equality = byte_mode_snapshot(compiled_snapshot) == byte_mode_snapshot(cache_snapshot)
        write_json(self.evidence / f"native-cache-equality-{label}.json", {
            "compiled_plugin": str(compiled_plugin), "installed_cache": str(cache),
            "compiled_byte_mode_snapshot": byte_mode_snapshot(compiled_snapshot),
            "installed_byte_mode_snapshot": byte_mode_snapshot(cache_snapshot), "equal": equality,
        })
        if not equality:
            raise HarnessError("native cache bytes or modes differ from committed Craft plugin archive for " + label)
        self.save_snapshot(label + "-native-cache", cache)
        return cache, bundle

    def remove_native(self, scope: Scope, label: str, cache: Path) -> None:
        self.native(scope, label + "-plugin-remove", "plugin", "remove", PACKAGE_ID + "@jdh-agents")
        if cache.exists():
            raise HarnessError("native Craft cache remains after plugin removal: " + str(cache))
        self.native(scope, label + "-marketplace-remove", "plugin", "marketplace", "remove", "jdh-agents")

    def run_scope(self, scope: Scope, base: Path, content: Path, renamed: Path) -> None:
        self.link_auth(scope)
        base_cache, base_bundle = self.install_native(scope, "base-" + scope.name, base)
        base_data = bundle_data(base_bundle)
        self.package_id = str(base_data["package"]["id"])
        self.require_agents(base_bundle, {"comment-reviewer", "copy-reviewer", "house-style-reviewer"}, "installed base Craft")
        base_definition = agent_definition(base_data, "comment-reviewer")
        root = scope.registration_root
        before = self.save_snapshot(scope.name + "-before", root)
        self.lifecycle(scope, "base-" + scope.name + "-check-missing", "check-codex-agent", str(base_bundle), "--scope", scope.name, "--project-root", str(scope.project_root), failure=True)
        self.lifecycle(scope, "base-" + scope.name + "-preview-install", "preview-codex-agent", str(base_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.lifecycle(scope, "base-" + scope.name + "-install", "install-codex-agent", str(base_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.assert_bundle_bytes("base-" + scope.name, base_bundle, root)
        self.lifecycle(scope, "base-" + scope.name + "-check", "check-codex-agent", str(base_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        installed = self.save_snapshot("base-" + scope.name + "-installed", root)
        self.lifecycle(scope, "base-" + scope.name + "-install-repeat", "install-codex-agent", str(base_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        repeat = self.save_snapshot("base-" + scope.name + "-repeat", root)
        self.same_snapshot(installed, repeat, "Craft " + scope.name + " repeat install including mtimes")
        if before.read_bytes() == installed.read_bytes():
            raise HarnessError("Craft base install made no observable registration change for " + scope.name)
        self.remove_native(scope, "base-" + scope.name, base_cache)

        content_cache, content_bundle = self.install_native(scope, "content-" + scope.name, content)
        self.lifecycle(scope, "content-" + scope.name + "-preview-update", "preview-codex-agent-update", str(content_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.lifecycle(scope, "content-" + scope.name + "-update", "update-codex-agent", str(content_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.assert_bundle_bytes("content-" + scope.name, content_bundle, root)
        self.lifecycle(scope, "content-" + scope.name + "-check", "check-codex-agent", str(content_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        # Native removal deletes the cache that owns this bundle. Preserve the
        # old definition path before removing it for the deletion assertion.
        deleted_definition = agent_definition(bundle_data(content_bundle), DELETED_AGENT)
        self.remove_native(scope, "content-" + scope.name, content_cache)

        renamed_cache, renamed_bundle = self.install_native(scope, "rename-" + scope.name, renamed)
        renamed_data = bundle_data(renamed_bundle)
        renamed_definition = agent_definition(renamed_data, RENAMED_AGENT)
        self.lifecycle(scope, "rename-" + scope.name + "-preview-update", "preview-codex-agent-update", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.lifecycle(scope, "rename-" + scope.name + "-update", "update-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.assert_bundle_bytes("rename-" + scope.name, renamed_bundle, root)
        if (root / base_definition).exists() or (root / deleted_definition).exists() or not (root / renamed_definition).is_file():
            raise HarnessError("Craft rename/deletion did not produce expected registration files for " + scope.name)
        self.lifecycle(scope, "rename-" + scope.name + "-check", "check-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))

        managed, config = root / renamed_definition, root / "config.toml"
        managed_before, config_before = self.run_root / (scope.name + ".managed.before"), self.run_root / (scope.name + ".config.before")
        shutil.copy2(managed, managed_before)
        shutil.copy2(config, config_before)
        managed.write_text(managed.read_text() + "\n# deliberate lifecycle conflict\n")
        identity = PACKAGE_ID + ":" + RENAMED_AGENT
        config_text = config.read_text()
        header = f'[agents."{identity}"]\n'
        start = config_text.find(header)
        end = config_text.find("\n[", start + len(header)) if start >= 0 else -1
        if start < 0:
            raise HarnessError("Craft conflict target registration is absent for " + scope.name)
        end = len(config_text) if end < 0 else end + 1
        section = config_text[start:end]
        if 'description = "' not in section:
            raise HarnessError("Craft conflict target has no editable description for " + scope.name)
        edited = section.replace('description = "', 'description = "deliberate lifecycle conflict ', 1)
        config.write_text(config_text[:start] + edited + config_text[end:])
        managed_hash, config_hash = sha256(managed), sha256(config)
        self.lifecycle(scope, "conflict-" + scope.name + "-check", "check-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root), failure=True)
        self.lifecycle(scope, "conflict-" + scope.name + "-update-refused", "update-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root), failure=True)
        if sha256(managed) != managed_hash or sha256(config) != config_hash:
            raise HarnessError("refused Craft update overwrote deliberate conflict for " + scope.name)
        self.remove_native(scope, "rename-" + scope.name, renamed_cache)
        self.lifecycle(scope, "conflict-" + scope.name + "-remove-preserves", "remove-codex-agent", PACKAGE_ID, "--scope", scope.name, "--project-root", str(scope.project_root))
        if not managed.is_file() or "deliberate lifecycle conflict" not in config.read_text():
            raise HarnessError("Craft receipt cleanup overwrote conflict for " + scope.name)
        from run_linear_codex_lifecycle import restore_registration

        shutil.copy2(managed_before, managed)
        restore_registration(config_before, config, identity)
        definitions = [str(agent["definition"]) for agent in renamed_data["agents"]]
        self.lifecycle(scope, "cleanup-" + scope.name + "-remove", "remove-codex-agent", PACKAGE_ID, "--scope", scope.name, "--project-root", str(scope.project_root))
        self.lifecycle(scope, "cleanup-" + scope.name + "-remove-repeat", "remove-codex-agent", PACKAGE_ID, "--scope", scope.name, "--project-root", str(scope.project_root))
        self.assert_cleanup(scope, definitions)
        self.save_snapshot("cleanup-" + scope.name, root)


def main(argv: list[str]) -> int:
    from run_linear_codex_lifecycle import parse_args

    harness = None
    try:
        harness = CraftHarness(parse_args(argv))
        harness.run()
        return 0
    except HarnessError as error:
        print("error: " + str(error), file=sys.stderr)
        if harness is not None and harness.evidence.exists():
            write_json(harness.evidence / "summary.json", {"status": "FAIL", "error": str(error), "commands": harness.summary})
        return 1
    finally:
        if harness is not None and harness.initialized:
            harness.cleanup_auth()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

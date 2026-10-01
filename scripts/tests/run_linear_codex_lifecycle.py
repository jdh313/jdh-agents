#!/usr/bin/env python3
"""Guarded, native-plugin lifecycle acceptance for Linear's Codex agent bundle.

This is deliberately an executable acceptance harness rather than a unit test.
It consumes only a committed source archive and native Codex plugin caches.  A
successful run leaves a complete command/evidence record below ``RUN_ROOT``.

Example (use a new directory under /private/tmp):

  python3 scripts/tests/run_linear_codex_lifecycle.py \\
    --agentforge-bin /absolute/agentforge-darwin-arm64 \\
    --codex-bin /absolute/codex \\
    --source-repo "$PWD" --source-commit <committed-sha> \\
    --run-root /private/tmp/jun-444-linear-lifecycle/run-001

The harness is intentionally direct-CLI only.  It does not establish Codex
sandbox acceptance, setup-skill activation, dispatch behavior, or applied
model/effort settings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
PINNED_VERSION = "1.2.0"
COMMAND_TIMEOUT_SECONDS = 120
PINNED_SHA256 = {
    ("Darwin", "arm64"): "67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54",
    ("Linux", "aarch64"): "6c18babe7d7b11dd6e581468b32091a8e7667ef73c67ca7cd4017a2cc5ae2e1f",
    ("Linux", "x86_64"): "6c40a48b42066b4323eb0b3adaf88f926576a69667364ef952ec877ad770b335",
}


class HarnessError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_absolute_file(value: str, label: str, executable: bool = False) -> Path:
    path = Path(value)
    if not path.is_absolute() or not path.is_file():
        raise HarnessError(f"{label} must be an existing absolute file: {value}")
    if executable and not os.access(path, os.X_OK):
        raise HarnessError(f"{label} is not executable: {path}")
    return path.resolve()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def safe_extract(archive: Path, destination: Path) -> None:
    """Extract a committed archive without allowing archive path traversal."""
    with tarfile.open(archive) as tar:
        for item in tar.getmembers():
            if item.issym() or item.islnk():
                raise HarnessError(f"archive links are not allowed in the disposable fixture: {item.name}")
            target = (destination / item.name).resolve()
            if destination.resolve() != target and destination.resolve() not in target.parents:
                raise HarnessError(f"archive member escapes fixture root: {item.name}")
        try:
            tar.extractall(destination, filter="data")
        except TypeError:  # Python <3.12: members were already path-checked.
            tar.extractall(destination)


def snapshot(root: Path) -> dict[str, dict[str, Any]]:
    """Return a byte, mode, and mtime snapshot; symlinks are recorded as links."""
    if not root.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        relative = str(path.relative_to(root))
        metadata = path.lstat()
        entry: dict[str, Any] = {
            "mode": stat.S_IMODE(metadata.st_mode),
            "mtime_ns": metadata.st_mtime_ns,
        }
        if path.is_symlink():
            entry.update(type="symlink", target=os.readlink(path))
        elif path.is_file():
            entry.update(type="file", sha256=sha256(path))
        elif path.is_dir():
            entry.update(type="directory")
        else:
            entry.update(type="other")
        result[relative] = entry
    return result


def byte_mode_snapshot(value: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Keep the payload properties native installation must preserve exactly."""
    return {
        path: {
            key: entry[key]
            for key in ("type", "mode", "sha256", "target")
            if key in entry
        }
        for path, entry in value.items()
    }


def replace_version(package: Path, version: str) -> str:
    text = package.read_text()
    match = re.search(r'"version": "([0-9]+\.[0-9]+\.[0-9]+)"', text)
    if not match:
        raise HarnessError(f"could not find JSON-style package version in {package}")
    previous = match.group(1)
    package.write_text(text[: match.start(1)] + version + text[match.end(1) :])
    return previous


def next_patch(version: str) -> str:
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def bundle_data(bundle: Path) -> dict[str, Any]:
    index = bundle / "agentforge-codex-agent-bundle.json"
    if not index.is_file():
        raise HarnessError(f"native cache has no Codex agent bundle index: {index}")
    data = json.loads(index.read_text())
    if not isinstance(data.get("agents"), list) or not data["agents"]:
        raise HarnessError(f"bundle index has no agents: {index}")
    return data


def agent_definition(data: dict[str, Any], agent_id: str) -> str:
    for agent in data["agents"]:
        if agent["id"] == agent_id:
            return str(agent["definition"])
    raise HarnessError(f"bundle lacks agent id {agent_id}")


def installed_plugin_root(plugin_json: Path) -> Path:
    data = json.loads(plugin_json.read_text())
    paths: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, str) and "/plugins/cache/" in value:
            paths.append(value)
        elif isinstance(value, dict):
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    visit(data)
    unique = {Path(value).resolve() for value in paths}
    if len(unique) != 1:
        raise HarnessError(f"native plugin result did not contain one cache root: {sorted(map(str, unique))}")
    root = unique.pop()
    if not root.is_dir():
        raise HarnessError(f"native plugin cache root is absent: {root}")
    return root


def restore_registration(saved: Path, current: Path, identity: str) -> None:
    header = f'[agents."{identity}"]\n'

    def bounds(text: str) -> tuple[int, int]:
        start = text.find(header)
        if start < 0:
            raise HarnessError(f"registration is absent: {identity}")
        end = text.find("\n[", start + len(header))
        return start, len(text) if end < 0 else end + 1

    old = saved.read_text()
    new = current.read_text()
    old_start, old_end = bounds(old)
    new_start, new_end = bounds(new)
    current.write_text(new[:new_start] + old[old_start:old_end] + new[new_end:])


@dataclass(frozen=True)
class Scope:
    name: str
    codex_home: Path
    project_root: Path

    @property
    def registration_root(self) -> Path:
        return self.codex_home if self.name == "user" else self.project_root / ".codex"


class Harness:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.run_root = Path(args.run_root).resolve()
        self.evidence = self.run_root / "evidence"
        self.sequence = 0
        self.summary: list[dict[str, Any]] = []
        self.auth_link: Path | None = None
        self.package_id = "linear"
        self.initialized = False

    def assert_isolated(self, scope: Scope) -> None:
        home = scope.codex_home.resolve()
        project = scope.project_root.resolve()
        if scope.codex_home.is_symlink() or scope.project_root.is_symlink():
            raise HarnessError(f"scope {scope.name} uses a symlinked CODEX_HOME or project root")
        if self.run_root not in home.parents or self.run_root not in project.parents:
            raise HarnessError(f"scope {scope.name} is outside RUN_ROOT")
        if home == Path.home().resolve() / ".codex":
            raise HarnessError("refusing to use the normal CODEX_HOME")
        if not (project / ".git").is_dir():
            raise HarnessError(f"scope {scope.name} lacks its trusted disposable project: {project}")

    def command(
        self,
        label: str,
        argv: list[str],
        *,
        cwd: Path,
        scope: Scope | None = None,
        expect: int | None = 0,
        lifecycle: bool = False,
    ) -> subprocess.CompletedProcess[bytes]:
        if scope is not None:
            self.assert_isolated(scope)
        self.sequence += 1
        stem = f"{self.sequence:03d}-{label}"
        environment = {"PATH": SYSTEM_PATH}
        if scope is not None:
            environment["CODEX_HOME"] = str(scope.codex_home)
        if lifecycle and cwd.resolve() != (self.run_root / "consumer-cwd").resolve():
            raise HarnessError("lifecycle consumer command must run from the isolated consumer CWD")
        command_record = {
            "argv": argv,
            "cwd": str(cwd.resolve()),
            "env": environment,
            "consumer_boundary": lifecycle,
        }
        write_json(self.evidence / f"{stem}.command.json", command_record)
        completed = subprocess.run(
            argv,
            cwd=cwd,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
        (self.evidence / f"{stem}.stdout").write_bytes(completed.stdout)
        (self.evidence / f"{stem}.stderr").write_bytes(completed.stderr)
        (self.evidence / f"{stem}.exit").write_text(f"{completed.returncode}\n")
        row = {"label": label, "exit": completed.returncode, "expected": expect}
        self.summary.append(row)
        if expect is not None and completed.returncode != expect:
            raise HarnessError(f"{label} exited {completed.returncode}, expected {expect}; evidence: {stem}")
        return completed

    def expect_failure(self, label: str, argv: list[str], **kwargs: Any) -> None:
        completed = self.command(label, argv, expect=None, **kwargs)
        if completed.returncode == 0:
            raise HarnessError(f"{label} unexpectedly succeeded; expected refusal")

    def lifecycle(self, scope: Scope, label: str, *arguments: str, failure: bool = False) -> None:
        scope_positions = [index for index, value in enumerate(arguments) if value == "--scope"]
        project_positions = [index for index, value in enumerate(arguments) if value == "--project-root"]
        if len(scope_positions) != 1 or len(project_positions) != 1:
            raise HarnessError("each lifecycle invocation must name exactly one scope and project root")
        scope_index = scope_positions[0]
        project_index = project_positions[0]
        if scope_index + 1 >= len(arguments) or arguments[scope_index + 1] != scope.name:
            raise HarnessError(f"lifecycle scope does not match isolated {scope.name} fixture")
        if project_index + 1 >= len(arguments):
            raise HarnessError("lifecycle invocation has no project-root value")
        raw_project = Path(arguments[project_index + 1])
        if not raw_project.is_absolute() or raw_project.resolve() != scope.project_root.resolve():
            raise HarnessError(f"lifecycle project-root does not match isolated {scope.name} fixture")
        argv = [str(self.agentforge_bin), *arguments]
        kwargs = dict(cwd=self.run_root / "consumer-cwd", scope=scope, lifecycle=True)
        if failure:
            self.expect_failure(label, argv, **kwargs)
        else:
            self.command(label, argv, **kwargs)

    def native(self, scope: Scope, label: str, *arguments: str) -> subprocess.CompletedProcess[bytes]:
        return self.command(
            label,
            [str(self.codex_bin), *arguments],
            cwd=scope.project_root,
            scope=scope,
        )

    def save_snapshot(self, label: str, root: Path) -> Path:
        target = self.evidence / f"snapshot-{label}.json"
        write_json(target, snapshot(root))
        return target

    def assert_bundle_version(self, bundle: Path, expected: str, label: str) -> None:
        observed = str(bundle_data(bundle)["package"].get("version", ""))
        if observed != expected:
            raise HarnessError(f"{label} bundle version is {observed}, expected {expected}")

    def same_snapshot(self, left: Path, right: Path, description: str) -> None:
        left_data = json.loads(left.read_text())
        right_data = json.loads(right.read_text())
        # Directories may have an mtime change from an internal lock operation.
        # No-op acceptance covers every file/link byte, mode, and mtime instead.
        left_files = {key: value for key, value in left_data.items() if value["type"] != "directory"}
        right_files = {key: value for key, value in right_data.items() if value["type"] != "directory"}
        if left_files != right_files:
            raise HarnessError(f"snapshot changed unexpectedly: {description}")

    def initialize(self) -> None:
        raw_run_root = Path(self.args.run_root)
        if not raw_run_root.is_absolute() or not str(raw_run_root).startswith("/private/tmp/"):
            raise HarnessError("RUN_ROOT must be a fresh path below /private/tmp")
        if not str(self.run_root).startswith("/private/tmp/"):
            raise HarnessError("RUN_ROOT resolves outside /private/tmp")
        if self.run_root.exists():
            raise HarnessError(f"refusing to reuse RUN_ROOT: {self.run_root}")
        self.run_root.mkdir(parents=True)
        self.evidence.mkdir()
        self.initialized = True
        (self.run_root / ".started").write_text("fresh guarded lifecycle run\n")
        (self.run_root / "consumer-cwd").mkdir()

        self.agentforge_bin = require_absolute_file(self.args.agentforge_bin, "AGENTFORGE_BIN", True)
        self.codex_bin = require_absolute_file(self.args.codex_bin, "CODEX_BIN", True)
        raw_source_repo = Path(self.args.source_repo)
        if not raw_source_repo.is_absolute() or not (raw_source_repo / ".git").exists():
            raise HarnessError(f"SOURCE_REPO must be an absolute Git repository: {self.args.source_repo}")
        self.source_repo = raw_source_repo.resolve()
        if not (self.source_repo / ".git").exists():
            raise HarnessError(f"SOURCE_REPO resolved to a non-Git path: {self.source_repo}")
        if not re.fullmatch(r"[0-9a-f]{40}", self.args.source_commit):
            raise HarnessError("SOURCE_COMMIT must be a full 40-character Git SHA")
        resolved = self.command(
            "source-commit",
            ["git", "-C", str(self.source_repo), "rev-parse", f"{self.args.source_commit}^{{commit}}"],
            cwd=self.run_root,
            expect=None,
        )
        if resolved.returncode or resolved.stdout.decode().strip() != self.args.source_commit:
            raise HarnessError("SOURCE_COMMIT is not a commit in SOURCE_REPO")

        platform_key = (platform.system(), platform.machine())
        expected_hash = PINNED_SHA256.get(platform_key)
        if expected_hash is None:
            raise HarnessError(f"no v{PINNED_VERSION} hash recorded for {platform_key}")
        actual_hash = sha256(self.agentforge_bin)
        if actual_hash != expected_hash:
            raise HarnessError(
                f"AGENTFORGE_BIN is not the verified v{PINNED_VERSION} release for {platform_key}: {actual_hash}"
            )
        version = self.command("agentforge-version", [str(self.agentforge_bin), "--version"], cwd=self.run_root)
        version_output = version.stdout.decode(errors="replace")
        if PINNED_VERSION not in version_output:
            raise HarnessError(f"AGENTFORGE_BIN did not report v{PINNED_VERSION}")
        help_result = self.command("agentforge-help", [str(self.agentforge_bin), "--help"], cwd=self.run_root)
        help_text = help_result.stdout.decode(errors="replace")
        required = {
            "preview-codex-agent",
            "install-codex-agent",
            "check-codex-agent",
            "preview-codex-agent-update",
            "update-codex-agent",
            "remove-codex-agent",
        }
        missing = sorted(item for item in required if item not in help_text)
        if missing:
            raise HarnessError(f"released compiler lacks lifecycle commands: {', '.join(missing)}")
        write_json(
            self.evidence / "inputs.json",
            {
                "agentforge_bin": str(self.agentforge_bin),
                "agentforge_sha256": actual_hash,
                "agentforge_version_required": PINNED_VERSION,
                "codex_bin": str(self.codex_bin),
                "source_repo": str(self.source_repo),
                "source_commit": self.args.source_commit,
                "system_path": SYSTEM_PATH,
                "claims": {
                    "direct_cli_lifecycle_only": True,
                    "codex_sandbox_acceptance": "unknown",
                    "skill_activation": "untested",
                    "dispatch": "untested",
                    "runtime_model_effort": "unknown",
                },
            },
        )

    def create_archives(self) -> tuple[Path, Path]:
        source_archive = self.run_root / "source-committed.tar"
        marketplace_archive = self.run_root / "marketplace-codex-committed.tar"
        source = self.command(
            "archive-committed-source",
            ["git", "-C", str(self.source_repo), "archive", "--format=tar", self.args.source_commit],
            cwd=self.run_root,
        )
        source_archive.write_bytes(source.stdout)
        marketplace = self.command(
            "archive-committed-codex-marketplace",
            ["git", "-C", str(self.source_repo), "archive", "--format=tar", f"{self.args.source_commit}:marketplaces/codex"],
            cwd=self.run_root,
        )
        marketplace_archive.write_bytes(marketplace.stdout)
        write_json(
            self.evidence / "committed-archives.json",
            {
                "source_archive": {"path": str(source_archive), "sha256": sha256(source_archive)},
                "marketplace_archive": {"path": str(marketplace_archive), "sha256": sha256(marketplace_archive)},
            },
        )
        return source_archive, marketplace_archive

    def authoring_fixtures(self, source_archive: Path, marketplace_archive: Path) -> tuple[Path, Path, Path]:
        authoring = self.run_root / "authoring"
        base_marketplace = self.run_root / "marketplace-base"
        authoring.mkdir()
        base_marketplace.mkdir()
        safe_extract(source_archive, authoring)
        safe_extract(marketplace_archive, base_marketplace)
        self.command("fixture-git-init", ["git", "init", "-q"], cwd=authoring)
        self.command("fixture-git-add-base", ["git", "add", "-A"], cwd=authoring)
        self.command(
            "fixture-git-commit-base",
            ["git", "-c", "user.name=Linear lifecycle harness", "-c", "user.email=linear-lifecycle@example.invalid", "commit", "-qm", "fixture: committed source archive"],
            cwd=authoring,
        )
        bundle = base_marketplace / "plugins" / "linear" / ".agentforge" / "codex-agent-bundle"
        base_data = bundle_data(bundle)
        source_version = re.search(r'"version": "([0-9]+\.[0-9]+\.[0-9]+)"', (authoring / "plugins" / "linear" / "PACKAGE.yaml").read_text())
        if source_version is None:
            raise HarnessError("Linear PACKAGE.yaml has no JSON-style version")
        if str(base_data["package"].get("version", "")) != source_version.group(1):
            raise HarnessError("committed Linear bundle version differs from committed package metadata")
        self.save_snapshot("committed-marketplace", base_marketplace)

        package = authoring / "plugins" / "linear" / "PACKAGE.yaml"
        agent = authoring / "plugins" / "linear" / "agents" / "linear-ops.md"
        content_version = next_patch(source_version.group(1))
        replace_version(package, content_version)
        agent.write_text(agent.read_text() + "\n<!-- disposable Linear lifecycle content update -->\n")
        synthetic = authoring / "plugins" / "linear" / "agents" / "linear-ops-synthetic.md"
        synthetic.write_text(
            "---\nname: linear-ops-synthetic\ndescription: Disposable lifecycle fixture role.\n---\n\n"
            "# Disposable lifecycle fixture\n\nThis file exists only to exercise registration deletion.\n"
        )
        self.compile_fixture(authoring, "content", content_version)
        content_marketplace = self.run_root / f"marketplace-update-{content_version}"
        shutil.copytree(authoring / "marketplaces" / "codex", content_marketplace)
        self.assert_bundle_version(content_marketplace / "plugins" / "linear" / ".agentforge" / "codex-agent-bundle", content_version, "content fixture")
        self.save_snapshot("content-marketplace", content_marketplace)

        rename_version = next_patch(content_version)
        renamed = agent.with_name("linear-ops-renamed.md")
        agent.rename(renamed)
        renamed.write_text(renamed.read_text().replace("name: linear-ops\n", "name: linear-ops-renamed\n", 1))
        synthetic.unlink()
        replace_version(package, rename_version)
        self.compile_fixture(authoring, "rename-delete", rename_version)
        rename_marketplace = self.run_root / f"marketplace-update-{rename_version}"
        shutil.copytree(authoring / "marketplaces" / "codex", rename_marketplace)
        self.assert_bundle_version(rename_marketplace / "plugins" / "linear" / ".agentforge" / "codex-agent-bundle", rename_version, "rename fixture")
        self.save_snapshot("rename-delete-marketplace", rename_marketplace)
        return base_marketplace, content_marketplace, rename_marketplace

    def compile_fixture(self, authoring: Path, label: str, version: str) -> None:
        env = {"PATH": os.environ.get("PATH", SYSTEM_PATH), "AGENTFORGE_BIN": str(self.agentforge_bin)}
        for suffix, argv in (
            ("compile", [str(authoring / "scripts" / "agentforge.sh"), "compile", "MARKETPLACE.yaml", "--out", "marketplaces"]),
            ("check", [str(authoring / "scripts" / "agentforge.sh"), "check", "MARKETPLACE.yaml", "--out", "marketplaces"]),
        ):
            self.sequence += 1
            stem = f"{self.sequence:03d}-fixture-{label}-{suffix}"
            write_json(self.evidence / f"{stem}.command.json", {"argv": argv, "cwd": str(authoring), "env": env, "authoring_fixture": True})
            completed = subprocess.run(
                argv,
                cwd=authoring,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
            (self.evidence / f"{stem}.stdout").write_bytes(completed.stdout)
            (self.evidence / f"{stem}.stderr").write_bytes(completed.stderr)
            (self.evidence / f"{stem}.exit").write_text(f"{completed.returncode}\n")
            self.summary.append({"label": f"fixture-{label}-{suffix}", "exit": completed.returncode, "expected": 0})
            if completed.returncode:
                raise HarnessError(f"fixture {label} {suffix} failed; evidence: {stem}")
        self.command("fixture-git-add-" + label, ["git", "add", "plugins/linear", "marketplaces", ".claude-plugin"], cwd=authoring)
        self.command(
            "fixture-git-commit-" + label,
            ["git", "-c", "user.name=Linear lifecycle harness", "-c", "user.email=linear-lifecycle@example.invalid", "commit", "-qm", f"fixture: Linear {label} {version}"],
            cwd=authoring,
        )

    def scope(self, name: str) -> Scope:
        root = self.run_root / "scopes" / name
        home = root / "codex-home"
        project = root / "trusted-project"
        home.mkdir(parents=True)
        project.mkdir()
        self.command("scope-project-git-init-" + name, ["git", "init", "-q"], cwd=project)
        scope = Scope(name, home, project)
        self.assert_isolated(scope)
        (project / "KEEP.txt").write_text("unrelated project marker\n")
        (home / "agents").mkdir()
        (home / "agents" / "unrelated.toml").write_text("unrelated user agent\n")
        (home / "config.toml").write_text(
            'model = "unrelated-model"\n\n'
            f'[projects."{project}"]\ntrust_level = "trusted"\n'
        )
        codex = project / ".codex"
        (codex / "agents").mkdir(parents=True)
        (codex / "agents" / "unrelated.toml").write_text("unrelated project agent\n")
        (codex / "config.toml").write_text('model = "unrelated-project-model"\n')
        (codex / "KEEP.txt").write_text("unrelated project configuration\n")
        write_json(
            self.evidence / f"unrelated-{name}.json",
            {
                "home_agent": {"path": str(home / "agents" / "unrelated.toml"), "sha256": sha256(home / "agents" / "unrelated.toml")},
                "project_marker": {"path": str(project / "KEEP.txt"), "sha256": sha256(project / "KEEP.txt")},
                "project_agent": {"path": str(codex / "agents" / "unrelated.toml"), "sha256": sha256(codex / "agents" / "unrelated.toml")},
                "project_marker_in_codex": {"path": str(codex / "KEEP.txt"), "sha256": sha256(codex / "KEEP.txt")},
            },
        )
        return scope

    def link_auth(self, scope: Scope) -> None:
        source = Path(self.args.codex_auth_file).expanduser().resolve()
        if not source.is_file():
            raise HarnessError(f"normal auth file is unavailable for native plugin installation: {source}")
        link = scope.codex_home / "auth.json"
        if link.exists() or link.is_symlink():
            raise HarnessError(f"refusing to overwrite disposable auth path: {link}")
        link.symlink_to(source)
        self.auth_link = link

    def install_native(self, scope: Scope, label: str, marketplace: Path) -> tuple[Path, Path]:
        self.native(scope, label + "-marketplace-add", "plugin", "marketplace", "add", str(marketplace))
        result = self.native(scope, label + "-plugin-add", "plugin", "add", "linear@jdh-agents", "--json")
        output = self.evidence / f"{self.sequence:03d}-{label}-plugin-add.stdout"
        cache = installed_plugin_root(output)
        expected_root = scope.codex_home / "plugins" / "cache"
        if expected_root not in cache.parents:
            raise HarnessError(f"native cache escaped isolated CODEX_HOME: {cache}")
        bundle = cache / ".agentforge" / "codex-agent-bundle"
        bundle_data(bundle)
        compiled_plugin = marketplace / "plugins" / "linear"
        if not compiled_plugin.is_dir():
            raise HarnessError(f"committed marketplace lacks Linear plugin: {compiled_plugin}")
        compiled_snapshot = snapshot(compiled_plugin)
        cache_snapshot = snapshot(cache)
        write_json(
            self.evidence / f"native-cache-equality-{label}.json",
            {
                "compiled_plugin": str(compiled_plugin),
                "installed_cache": str(cache),
                "compiled_snapshot": compiled_snapshot,
                "installed_snapshot": cache_snapshot,
                "compiled_byte_mode_snapshot": byte_mode_snapshot(compiled_snapshot),
                "installed_byte_mode_snapshot": byte_mode_snapshot(cache_snapshot),
                "equal": byte_mode_snapshot(compiled_snapshot) == byte_mode_snapshot(cache_snapshot),
            },
        )
        if byte_mode_snapshot(compiled_snapshot) != byte_mode_snapshot(cache_snapshot):
            raise HarnessError(f"native cache bytes or modes differ from committed plugin archive for {label}")
        self.save_snapshot(label + "-native-cache", cache)
        return cache, bundle

    def assert_bundle_bytes(self, label: str, bundle: Path, registration: Path) -> None:
        rows: list[dict[str, str]] = []
        for agent in bundle_data(bundle)["agents"]:
            definition = str(agent["definition"])
            actual = sha256(registration / definition)
            expected = str(agent["sha256"])
            rows.append({"definition": definition, "expected": expected, "actual": actual})
            if actual != expected:
                raise HarnessError(f"registered bytes differ from native bundle for {definition}")
        write_json(self.evidence / f"bundle-bytes-{label}.json", rows)

    def assert_cleanup(self, scope: Scope, managed_definitions: Iterable[str]) -> None:
        root = scope.registration_root
        receipt = root / "agents" / ".agentforge" / f"{self.package_id}.json"
        if receipt.exists():
            raise HarnessError(f"receipt remains after cleanup: {receipt}")
        config = (root / "config.toml").read_text()
        if f'[agents."{self.package_id}:' in config:
            raise HarnessError(f"managed registrations remain after cleanup for {scope.name}")
        for definition in managed_definitions:
            if (root / definition).exists():
                raise HarnessError(f"managed definition remains after cleanup: {definition}")
        if scope.name == "user":
            if 'model = "unrelated-model"' not in config or "trust_level = \"trusted\"" not in config:
                raise HarnessError("unrelated user configuration was not preserved")
        else:
            if 'model = "unrelated-project-model"' not in config:
                raise HarnessError("unrelated project configuration was not preserved")
        unrelated = json.loads((self.evidence / f"unrelated-{scope.name}.json").read_text())
        for label, expected in unrelated.items():
            path = Path(expected["path"])
            if not path.is_file() or sha256(path) != expected["sha256"]:
                raise HarnessError(f"unrelated sibling changed during lifecycle cleanup: {label}")

    def remove_native(self, scope: Scope, label: str, cache: Path) -> None:
        self.native(scope, label + "-plugin-remove", "plugin", "remove", "linear@jdh-agents")
        if cache.exists():
            raise HarnessError(f"native cache remains after plugin removal: {cache}")
        self.native(scope, label + "-marketplace-remove", "plugin", "marketplace", "remove", "jdh-agents")

    def run_scope(self, scope: Scope, base: Path, content: Path, renamed: Path) -> None:
        self.link_auth(scope)
        base_cache, base_bundle = self.install_native(scope, "base-" + scope.name, base)
        base_data = bundle_data(base_bundle)
        self.package_id = str(base_data["package"]["id"])
        base_definition = str(base_data["agents"][0]["definition"])
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
        self.same_snapshot(installed, repeat, f"base {scope.name} repeat install including mtimes")
        if before.read_bytes() == installed.read_bytes():
            raise HarnessError(f"base install made no observable registration change for {scope.name}")
        self.remove_native(scope, "base-" + scope.name, base_cache)

        content_cache, content_bundle = self.install_native(scope, "content-" + scope.name, content)
        content_data = bundle_data(content_bundle)
        self.lifecycle(scope, "content-" + scope.name + "-preview-update", "preview-codex-agent-update", str(content_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.lifecycle(scope, "content-" + scope.name + "-update", "update-codex-agent", str(content_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.assert_bundle_bytes("content-" + scope.name, content_bundle, root)
        self.lifecycle(scope, "content-" + scope.name + "-check", "check-codex-agent", str(content_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.remove_native(scope, "content-" + scope.name, content_cache)

        renamed_cache, renamed_bundle = self.install_native(scope, "rename-" + scope.name, renamed)
        renamed_data = bundle_data(renamed_bundle)
        renamed_definition = agent_definition(renamed_data, "linear-ops-renamed")
        synthetic_definition = agent_definition(content_data, "linear-ops-synthetic")
        self.lifecycle(scope, "rename-" + scope.name + "-preview-update", "preview-codex-agent-update", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.lifecycle(scope, "rename-" + scope.name + "-update", "update-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))
        self.assert_bundle_bytes("rename-" + scope.name, renamed_bundle, root)
        if (root / base_definition).exists() or (root / synthetic_definition).exists() or not (root / renamed_definition).is_file():
            raise HarnessError(f"rename/deletion did not produce expected registration files for {scope.name}")
        self.lifecycle(scope, "rename-" + scope.name + "-check", "check-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root))

        managed = root / renamed_definition
        config = root / "config.toml"
        managed_before = self.run_root / f"{scope.name}.managed.before"
        config_before = self.run_root / f"{scope.name}.config.before"
        shutil.copy2(managed, managed_before)
        shutil.copy2(config, config_before)
        managed.write_text(managed.read_text() + "\n# deliberate lifecycle conflict\n")
        identity = f"{self.package_id}:linear-ops-renamed"
        config_text = config.read_text()
        if 'description = "' not in config_text:
            raise HarnessError(f"registered config has no editable description for {scope.name}")
        config.write_text(config_text.replace('description = "', 'description = "deliberate lifecycle conflict ', 1))
        managed_hash = sha256(managed)
        config_hash = sha256(config)
        self.lifecycle(scope, "conflict-" + scope.name + "-check", "check-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root), failure=True)
        self.lifecycle(scope, "conflict-" + scope.name + "-update-refused", "update-codex-agent", str(renamed_bundle), "--scope", scope.name, "--project-root", str(scope.project_root), failure=True)
        if sha256(managed) != managed_hash or sha256(config) != config_hash:
            raise HarnessError(f"refused update overwrote deliberate conflict for {scope.name}")

        self.remove_native(scope, "rename-" + scope.name, renamed_cache)
        self.lifecycle(scope, "conflict-" + scope.name + "-remove-preserves", "remove-codex-agent", self.package_id, "--scope", scope.name, "--project-root", str(scope.project_root))
        if not managed.is_file() or "deliberate lifecycle conflict" not in config.read_text():
            raise HarnessError(f"receipt cleanup overwrote conflict for {scope.name}")
        shutil.copy2(managed_before, managed)
        restore_registration(config_before, config, identity)
        definitions = [str(agent["definition"]) for agent in renamed_data["agents"]]
        self.lifecycle(scope, "cleanup-" + scope.name + "-remove", "remove-codex-agent", self.package_id, "--scope", scope.name, "--project-root", str(scope.project_root))
        self.lifecycle(scope, "cleanup-" + scope.name + "-remove-repeat", "remove-codex-agent", self.package_id, "--scope", scope.name, "--project-root", str(scope.project_root))
        self.assert_cleanup(scope, definitions)
        self.save_snapshot("cleanup-" + scope.name, root)

    def cleanup_auth(self) -> None:
        # Only remove a link we created inside RUN_ROOT; never touch normal auth.
        for link in self.run_root.glob("scopes/*/codex-home/auth.json"):
            if link.is_symlink():
                link.unlink()
        if self.evidence.is_dir():
            (self.evidence / "auth-link-cleanup.txt").write_text("removed only disposable auth symlinks\n")

    def run(self) -> None:
        self.initialize()
        if self.args.initialize_only:
            write_json(self.evidence / "summary.json", {"status": "INITIALIZED_ONLY", "commands": self.summary})
            (self.evidence / "summary.txt").write_text("INITIALIZED_ONLY\n")
            return
        source_archive, marketplace_archive = self.create_archives()
        base, content, renamed = self.authoring_fixtures(source_archive, marketplace_archive)
        for name in ("user", "project"):
            self.run_scope(self.scope(name), base, content, renamed)
        write_json(self.evidence / "summary.json", {"status": "PASS", "commands": self.summary})
        (self.evidence / "summary.txt").write_text("\n".join(f"{row['label']} {row['exit']}" for row in self.summary) + "\nPASS\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agentforge-bin", required=True, help="absolute verified AgentForge v1.2.0 binary")
    parser.add_argument("--codex-bin", required=True, help="absolute Codex executable")
    parser.add_argument("--source-repo", required=True, help="absolute jdh-agents repository")
    parser.add_argument("--source-commit", required=True, help="full committed source SHA")
    parser.add_argument("--run-root", required=True, help="fresh absolute directory below /private/tmp")
    parser.add_argument("--codex-auth-file", default=str(Path.home() / ".codex" / "auth.json"), help="normal auth file to link unread into isolated homes")
    parser.add_argument("--initialize-only", action="store_true", help="validate inputs and released lifecycle CLI without creating archives or installing plugins")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    harness: Harness | None = None
    try:
        harness = Harness(parse_args(argv))
        harness.run()
        return 0
    except HarnessError as error:
        print(f"error: {error}", file=sys.stderr)
        if harness is not None and harness.evidence.exists():
            write_json(harness.evidence / "summary.json", {"status": "FAIL", "error": str(error), "commands": harness.summary})
        return 1
    finally:
        if harness is not None and harness.initialized:
            harness.cleanup_auth()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

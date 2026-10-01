#!/usr/bin/env python3
"""Prepare and run bounded Craft Codex acceptance sessions.

``--prepare`` creates three fresh isolated Codex homes and disposable trusted
Git projects from the exact committed Codex marketplace archive. It native-
installs Craft but deliberately registers no Craft roles. The default mode
runs one saved prompt in one prepared scope and rejects any app or MCP config.

An unrestricted project-setup control is available only behind a dedicated
flag and must be separately approved after ordinary setup is denied.
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
import tempfile
import tomllib
from pathlib import Path
from typing import Any


SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
AGENTFORGE_VERSION = "1.2.0"
AGENTFORGE_SHA256 = {
    ("Darwin", "arm64"): "67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54",
    ("Linux", "aarch64"): "6c18babe7d7b11dd6e581468b32091a8e7667ef73c67ca7cd4017a2cc5ae2e1f",
    ("Linux", "x86_64"): "6c40a48b42066b4323eb0b3adaf88f926576a69667364ef952ec877ad770b335",
}
SCOPES = ("user", "project", "fallback")
PACKAGE_ID = "craft"


class ProbeError(RuntimeError):
    pass


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def require_absolute_executable(value: Path, label: str, *, allow_symlink: bool) -> Path:
    """Resolve the explicit Codex launcher, but never a compiler symlink."""
    if not value.is_absolute() or not value.is_file() or (value.is_symlink() and not allow_symlink):
        raise ProbeError(label + " must be an absolute executable file: " + str(value))
    resolved = value.resolve()
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ProbeError(label + " does not resolve to an executable file: " + str(value))
    return resolved


def consumer_env(home: Path, agentforge: Path) -> dict[str, str]:
    """Do not inherit shell hooks, Git redirects, credentials, or tool paths."""
    return {"PATH": SYSTEM_PATH, "CODEX_HOME": str(home), "AGENTFORGE_BIN": str(agentforge)}


def safe_extract(archive: Path, destination: Path) -> None:
    with tarfile.open(archive) as tar:
        for item in tar.getmembers():
            if item.issym() or item.islnk():
                raise ProbeError("committed marketplace archive contains a link: " + item.name)
            target = (destination / item.name).resolve()
            if destination.resolve() != target and destination.resolve() not in target.parents:
                raise ProbeError("marketplace archive member escapes fixture: " + item.name)
        try:
            tar.extractall(destination, filter="data")
        except TypeError:
            tar.extractall(destination)


def snapshot_files(root: Path) -> dict[str, dict[str, Any]]:
    """Record the reviewer fixture source tree, excluding Git and Codex state."""
    result: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] in {".git", ".codex"}:
            continue
        info = path.lstat()
        item: dict[str, Any] = {"mode": stat.S_IMODE(info.st_mode), "mtime_ns": info.st_mtime_ns}
        if path.is_symlink():
            item.update(type="symlink", target=os.readlink(path))
        elif path.is_file():
            item.update(type="file", sha256=sha256(path))
        elif path.is_dir():
            item.update(type="directory")
        else:
            item.update(type="other")
        result[str(relative)] = item
    return result


def byte_mode(snapshot: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {name: {key: entry[key] for key in ("type", "mode", "sha256", "target") if key in entry}
            for name, entry in snapshot.items()}


def command(evidence: Path, sequence: int, label: str, argv: list[str], cwd: Path, env: dict[str, str], expect: int = 0) -> subprocess.CompletedProcess[bytes]:
    stem = f"{sequence:03d}-{label}"
    write_json(evidence / (stem + ".command.json"), {"argv": argv, "cwd": str(cwd), "env": env})
    completed = subprocess.run(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               check=False, timeout=180)
    (evidence / (stem + ".stdout")).write_bytes(completed.stdout)
    (evidence / (stem + ".stderr")).write_bytes(completed.stderr)
    (evidence / (stem + ".exit")).write_text(str(completed.returncode) + "\n")
    if completed.returncode != expect:
        raise ProbeError(f"{label} exited {completed.returncode}, expected {expect}; evidence: {stem}")
    return completed


def installed_plugin_root(output: bytes) -> Path:
    try:
        data = json.loads(output)
    except json.JSONDecodeError as error:
        raise ProbeError("native plugin add did not return JSON") from error
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
    roots = {Path(path).resolve() for path in paths}
    if len(roots) != 1:
        raise ProbeError("native plugin result did not name exactly one cache root")
    root = roots.pop()
    if not root.is_dir():
        raise ProbeError("native plugin cache is absent: " + str(root))
    return root


def validate_agentforge(binary: Path) -> None:
    key = (platform.system(), platform.machine())
    expected = AGENTFORGE_SHA256.get(key)
    if expected is None:
        raise ProbeError("no verified AgentForge v1.2.0 hash for " + repr(key))
    if sha256(binary) != expected:
        raise ProbeError("agentforge-bin is not the verified AgentForge v1.2.0 release")
    result = subprocess.run([str(binary), "--version"], env={"PATH": SYSTEM_PATH}, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, timeout=30, check=False)
    if result.returncode or not re.search(r"(?<![0-9.])1\.2\.0(?![0-9.])", result.stdout):
        raise ProbeError("agentforge-bin did not report version 1.2.0")


def validate_root(root: Path, *, must_exist: bool) -> Path:
    raw = Path(root)
    resolved = raw.resolve()
    allowed = Path("/private/tmp").resolve()
    if (not raw.is_absolute() or raw != resolved or raw.is_symlink()
            or allowed not in resolved.parents or not str(resolved).startswith(str(allowed / "craft-codex-"))):
        raise ProbeError("run-root must be an absolute non-symlink /private/tmp/craft-codex-* path")
    if must_exist:
        if not raw.is_dir():
            raise ProbeError("prepared run-root must exist as a real directory: " + str(raw))
    elif raw.exists():
        raise ProbeError("refusing to reuse run-root: " + str(raw))
    return resolved


def validate_self_test_output(value: Path) -> Path:
    raw = Path(value)
    resolved = raw.resolve()
    allowed = Path("/private/tmp").resolve()
    parent = raw.parent
    allowed_parent = parent == allowed or str(parent).startswith(str(allowed / "craft-codex-"))
    if (not raw.is_absolute() or raw != resolved or raw.exists() or raw.name in {"", ".", ".."}
            or parent != parent.resolve() or not allowed_parent):
        raise ProbeError("self-test output must be a fresh canonical file below /private/tmp or a craft fixture")
    return resolved


def config_without_external_integrations(path: Path, *, require_apps_false: bool = True) -> None:
    if path.is_symlink() or not path.is_file():
        raise ProbeError("isolated config must be a regular file: " + str(path))
    try:
        config = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as error:
        raise ProbeError("isolated config is invalid TOML: " + str(path)) from error
    features = config.get("features")
    if require_apps_false and (not isinstance(features, dict) or features.get("apps") is not False):
        raise ProbeError("isolated config must set features.apps = false")
    if not require_apps_false and isinstance(features, dict) and features.get("apps") not in (None, False):
        raise ProbeError("project config must not enable apps")
    if "mcp_servers" in config:
        raise ProbeError("Craft probe forbids all MCP server configuration")


def no_craft_registrations(*configs: Path) -> None:
    for config in configs:
        parsed = tomllib.loads(config.read_text())
        agents = parsed.get("agents", {})
        if not isinstance(agents, dict):
            raise ProbeError("isolated agents setting is not a table: " + str(config))
        if any(isinstance(name, str) and name.startswith(PACKAGE_ID + ":") for name in agents):
            raise ProbeError("prepared fixture unexpectedly has a Craft registration: " + str(config))


def registration_state(root: Path) -> dict[str, Any]:
    """Record only Craft-owned role state; do not read authentication material."""
    agents = root / "agents"
    receipt = agents / ".agentforge" / (PACKAGE_ID + ".json")
    craft_definitions = agents / PACKAGE_ID
    state: dict[str, Any] = {"root": str(root), "receipt": None, "definitions": {}}
    if receipt.exists() or receipt.is_symlink():
        info = receipt.lstat()
        state["receipt"] = {"mode": stat.S_IMODE(info.st_mode), "symlink": receipt.is_symlink()}
        if receipt.is_file() and not receipt.is_symlink():
            state["receipt"]["sha256"] = sha256(receipt)
    if craft_definitions.is_dir() and not craft_definitions.is_symlink():
        for path in sorted(craft_definitions.rglob("*")):
            if path.is_file() and not path.is_symlink():
                state["definitions"][str(path.relative_to(agents))] = sha256(path)
            elif path.is_symlink():
                state["definitions"][str(path.relative_to(agents))] = "SYMLINK:" + os.readlink(path)
    return state


def assert_no_craft_state(root: Path) -> None:
    state = registration_state(root)
    if state["receipt"] is not None or state["definitions"]:
        raise ProbeError("Craft receipt or role definition remains in " + str(root))


def fixture_files(project: Path) -> None:
    (project / "src").mkdir()
    (project / ".gitignore").write_text("/.codex/\n")
    (project / "AGENTS.md").write_text(
        "# Fixture rules\n\nPublic functions use snake_case. Reviews are advisory-only and must not edit files.\n"
    )
    (project / "CONVENTIONS.md").write_text(
        "# UI conventions\n\nDeclared: UI strings use sentence case and omit terminal punctuation.\n"
    )
    (project / "pyproject.toml").write_text("[tool.ruff]\nselect = [\"E4\", \"F\"]\n")
    (project / "src" / "accounts.py").write_text(
        "def fetch_invoice(invoice_id):\n    return invoice_id\n\n\ndef list_invoices():\n    return []\n\n\ndef delete_invoice(invoice_id):\n    return invoice_id\n\n\ndef get_invoice_status(invoice_id):\n    return \"open\"\n"
    )
    (project / "src" / "money.py").write_text(
        "def amount_in_cents(amount):\n    \"\"\"Return the amount in cents.\"\"\"\n    return amount\n"
    )
    (project / "src" / "cli.py").write_text(
        "SAVE_LABEL = \"Save changes\"\nCANCEL_LABEL = \"Cancel\"\nDELETE_LABEL = \"Delete account\"\nUPDATE_LABEL = \"Update account\"\n"
    )
    (project / "notes.txt").write_text("unrelated fixture marker\n")


def apply_working_diff(project: Path) -> None:
    accounts = project / "src" / "accounts.py"
    accounts.write_text(accounts.read_text().replace("def fetch_invoice(", "def fetchInvoice(", 1))
    money = project / "src" / "money.py"
    money.write_text(money.read_text().replace("    return amount\n", "    return amount / 100\n", 1))
    cli = project / "src" / "cli.py"
    cli.write_text(cli.read_text().replace('"Delete account"', '"DELETE ACCOUNT NOW!!!"'))


def git_output(project: Path, arguments: list[str]) -> str:
    result = subprocess.run(["git", *arguments], cwd=project, env={"PATH": SYSTEM_PATH}, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True, timeout=30, check=False)
    if result.returncode:
        raise ProbeError("git fixture inspection failed: " + result.stderr.strip())
    return result.stdout


def vcs_snapshot(project: Path) -> dict[str, Any]:
    """Detect semantic repository mutations without treating harmless index refreshes as writes."""
    config = project / ".git" / "config"
    return {
        "files": snapshot_files(project),
        "head": git_output(project, ["rev-parse", "HEAD"]),
        "symbolic_head": git_output(project, ["symbolic-ref", "HEAD"]),
        "status": git_output(project, ["status", "--porcelain=v1"]),
        "refs": git_output(project, ["show-ref", "--head", "--dereference"]),
        "local_config_sha256": sha256(config),
        "local_config_mode": stat.S_IMODE(config.stat().st_mode),
        "local_config": git_output(project, ["config", "--local", "--list"]),
        "reflog": git_output(project, ["reflog", "show", "--all", "--format=%H %gD %gs"]),
    }


def prepare(args: argparse.Namespace) -> None:
    root = validate_root(args.run_root, must_exist=False)
    source = args.source_repo.resolve()
    if not args.source_repo.is_absolute() or not (source / ".git").exists():
        raise ProbeError("source-repo must be an absolute Git repository")
    if not re.fullmatch(r"[0-9a-f]{40}", args.source_commit):
        raise ProbeError("source-commit must be a full 40-character Git SHA")
    resolved_commit = subprocess.run(
        ["git", "-C", str(source), "rev-parse", args.source_commit + "^{commit}"],
        env={"PATH": SYSTEM_PATH}, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        timeout=30, check=False,
    )
    if resolved_commit.returncode or resolved_commit.stdout.strip() != args.source_commit:
        raise ProbeError("source-commit must resolve exactly to a commit in source-repo")
    agentforge = require_absolute_executable(args.agentforge_bin, "agentforge-bin", allow_symlink=False)
    codex = require_absolute_executable(args.codex_bin, "codex-bin", allow_symlink=True)
    validate_agentforge(agentforge)
    auth = args.codex_auth_file.expanduser().resolve()
    if not auth.is_file():
        raise ProbeError("normal auth file is unavailable for unread disposable symlink")

    root.mkdir(parents=True)
    evidence = root / "evidence"
    evidence.mkdir()
    archive = command(evidence, 1, "archive-committed-codex-marketplace",
                      ["git", "-C", str(source), "archive", "--format=tar", f"{args.source_commit}:marketplaces/codex"],
                      root, {"PATH": SYSTEM_PATH})
    archive_path = root / "marketplace-codex-committed.tar"
    archive_path.write_bytes(archive.stdout)
    marketplace = root / "marketplace-codex"
    marketplace.mkdir()
    safe_extract(archive_path, marketplace)
    compiled_plugin = marketplace / "plugins" / PACKAGE_ID
    if not (compiled_plugin / ".agentforge" / "codex-agent-bundle" / "agentforge-codex-agent-bundle.json").is_file():
        raise ProbeError("committed marketplace lacks Craft Codex bundle")
    write_json(evidence / "inputs.json", {
        "source_repo": str(source), "source_commit": args.source_commit, "marketplace_archive_sha256": sha256(archive_path),
        "agentforge_bin": str(agentforge), "agentforge_sha256": sha256(agentforge), "agentforge_version": AGENTFORGE_VERSION,
        "codex_bin": str(codex), "path": SYSTEM_PATH,
        "external_integrations": "disabled: apps=false and no mcp_servers",
    })
    sequence = 1
    for scope in SCOPES:
        base = root / scope
        home, project = base / "codex-home", base / "project"
        home.mkdir(parents=True)
        project.mkdir()
        command(evidence, sequence + 1, scope + "-git-init", ["git", "init", "-q"], project, {"PATH": SYSTEM_PATH})
        sequence += 1
        fixture_files(project)
        command(evidence, sequence + 1, scope + "-git-add", ["git", "add", "-A"], project, {"PATH": SYSTEM_PATH})
        sequence += 1
        command(evidence, sequence + 1, scope + "-git-commit", ["git", "-c", "user.name=Craft probe fixture", "-c", "user.email=craft-probe@example.invalid", "commit", "-qm", "fixture: review baseline"], project, {"PATH": SYSTEM_PATH})
        sequence += 1
        apply_working_diff(project)
        (home / "config.toml").write_text(
            "[features]\napps = false\nmulti_agent = true\n\n[projects.\"" + str(project) + "\"]\ntrust_level = \"trusted\"\n"
        )
        (home / "auth.json").symlink_to(auth)  # Do not read or copy normal credentials.
        env = {"PATH": SYSTEM_PATH, "CODEX_HOME": str(home)}
        command(evidence, sequence + 1, scope + "-marketplace-add", [str(codex), "plugin", "marketplace", "add", str(marketplace)], project, env)
        sequence += 1
        added = command(evidence, sequence + 1, scope + "-plugin-add", [str(codex), "plugin", "add", PACKAGE_ID + "@jdh-agents", "--json"], project, env)
        sequence += 1
        cache = installed_plugin_root(added.stdout)
        if home / "plugins" / "cache" not in cache.parents:
            raise ProbeError("native cache escaped isolated CODEX_HOME: " + str(cache))
        equal = byte_mode(snapshot_files(compiled_plugin)) == byte_mode(snapshot_files(cache))
        write_json(evidence / (scope + "-cache-equality.json"), {
            "compiled_plugin": str(compiled_plugin), "installed_cache": str(cache), "equal": equal,
            "compiled": byte_mode(snapshot_files(compiled_plugin)), "installed": byte_mode(snapshot_files(cache)),
        })
        if not equal:
            raise ProbeError("native Craft cache differs from committed plugin output for " + scope)
        config_without_external_integrations(home / "config.toml")
        no_craft_registrations(home / "config.toml")
        if (project / ".codex").exists():
            raise ProbeError("prepare must not pre-create project .codex: " + str(project / ".codex"))
        fixture_snapshot = vcs_snapshot(project)
        fixture_snapshot["cache"] = str(cache)
        write_json(evidence / (scope + "-fixture-before.json"), fixture_snapshot)
    write_json(evidence / "prepare-summary.json", {"status": "READY", "scopes": list(SCOPES), "roles_registered": False})
    print("READY", root)


def run_probe(args: argparse.Namespace) -> int:
    root = validate_root(args.run_root, must_exist=True)
    validate_control_args(args)
    if args.scope not in SCOPES:
        raise ProbeError("unknown prepared scope: " + args.scope)
    if not args.label or any(char not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for char in args.label):
        raise ProbeError("label must use lowercase letters, digits, hyphens, or underscores")
    agentforge = require_absolute_executable(args.agentforge_bin, "agentforge-bin", allow_symlink=False)
    codex = require_absolute_executable(args.codex_bin, "codex-bin", allow_symlink=True)
    validate_agentforge(agentforge)
    evidence = root / "evidence"
    base = root / args.scope
    home, project = base / "codex-home", base / "project"
    if any(path.is_symlink() or not path.is_dir() or path.resolve() != path for path in (base, home, project)):
        raise ProbeError("prepared scope contains missing or symlinked fixture directories")
    if not (project / ".git").is_dir():
        raise ProbeError("prepared project is not a disposable Git repository")
    configs = [(home / "config.toml", True)]
    project_config = project / ".codex" / "config.toml"
    if project_config.exists():
        configs.append((project_config, False))
    for config, require_apps_false in configs:
        config_without_external_integrations(config, require_apps_false=require_apps_false)
    prompt = base / (args.label + ".prompt.txt")
    if prompt.is_symlink() or not prompt.is_file():
        raise ProbeError("missing regular prompt file: " + str(prompt))
    stem = base / args.label
    if stem.with_suffix(".events.jsonl").exists():
        raise ProbeError("refusing to overwrite session evidence")
    before = json.loads((evidence / (args.scope + "-fixture-before.json")).read_text())
    env = consumer_env(home, agentforge)
    argv = [str(codex), "exec", "-C", str(project), "--skip-git-repo-check", "--json", "-s", args.sandbox,
            "-m", "gpt-5.6-luna", "-c", 'model_reasoning_effort="medium"', "-c", "allow_login_shell=false",
            "-o", str(stem) + ".last.txt", "-"]
    if args.allow_user_registration_write:
        if args.scope != "user" or args.sandbox != "workspace-write":
            raise ProbeError("--allow-user-registration-write requires user scope and workspace-write sandbox")
        argv[2:2] = ["--add-dir", str(home)]
    stem.with_suffix(".command.json").write_text(json.dumps({
        "argv": argv, "env": {key: env[key] for key in ("CODEX_HOME", "AGENTFORGE_BIN", "PATH")},
        "stdin": str(prompt), "package_model_effort": "inherit", "fixture_parent_model_effort": "gpt-5.6-luna/medium",
        "external_integrations": "apps=false; no mcp_servers",
        "control": args.control_project_setup,
    }, indent=2) + "\n")
    with stem.with_suffix(".events.jsonl").open("w") as stdout, stem.with_suffix(".stderr").open("w") as stderr:
        result = subprocess.run(argv, input=prompt.read_text(), text=True, env=env, stdout=stdout, stderr=stderr,
                                timeout=600, check=False)
    stem.with_suffix(".exit").write_text(str(result.returncode) + "\n")
    after = vcs_snapshot(project)
    write_json(stem.with_suffix(".fixture-after.json"), after)
    expected = {key: before[key] for key in after}
    if after != expected:
        raise ProbeError("Craft reviewer probe changed the disposable repository; see " + str(stem) + ".fixture-after.json")
    print(args.scope, args.label, "process exit", result.returncode, "(inspect tool calls and trace metadata separately)")
    return result.returncode


def validate_control_args(args: argparse.Namespace) -> None:
    if args.control_project_setup:
        if (args.scope != "project" or args.label != "setup-control" or args.sandbox != "danger-full-access"
                or args.allow_user_registration_write or args.prepare or args.cleanup):
            raise ProbeError(
                "--control-project-setup is limited to project/setup-control with danger-full-access and no add-dir"
            )
    elif args.sandbox == "danger-full-access":
        raise ProbeError("danger-full-access requires --control-project-setup")


def self_test(output: Path | None) -> int:
    target = validate_self_test_output(output or Path("/private/tmp") / ("craft-probe-guard-results-" + str(os.getpid()) + ".json"))
    with tempfile.TemporaryDirectory(prefix="craft-codex-probe-guards-", dir="/private/tmp") as directory:
        root = Path(directory)
        valid = root / "valid.toml"
        valid.write_text("[features]\napps = false\n")
        config_without_external_integrations(valid)
        failures: dict[str, str] = {}
        for name, contents in {
            "apps-enabled": "[features]\napps = true\n",
            "missing-apps": "model = \"test\"\n",
            "mcp-present": "[features]\napps = false\n\n[mcp_servers.fixture]\ncommand = \"/bin/false\"\n",
        }.items():
            path = root / (name + ".toml")
            path.write_text(contents)
            try:
                config_without_external_integrations(path)
            except ProbeError as error:
                failures[name] = str(error)
            else:
                raise ProbeError("guard accepted invalid config: " + name)
        symlink = root / "symlink.toml"
        symlink.symlink_to(valid)
        try:
            config_without_external_integrations(symlink)
        except ProbeError as error:
            failures["symlinked-config"] = str(error)
        else:
            raise ProbeError("guard accepted a symlinked config")
        poison = {"BASH_ENV": "/tmp/evil", "ENV": "/tmp/evil", "ZDOTDIR": "/tmp/evil", "GIT_DIR": "/tmp/evil",
                  "GIT_WORK_TREE": "/tmp/evil", "GIT_CONFIG_GLOBAL": "/tmp/evil", "OPENAI_API_KEY": "not-used"}
        from unittest.mock import patch

        with patch.dict(os.environ, poison, clear=False):
            observed = consumer_env(Path("/private/tmp/home"), Path("/private/tmp/agentforge"))
        if set(observed) != {"PATH", "CODEX_HOME", "AGENTFORGE_BIN"} or any(key in observed for key in poison):
            raise ProbeError("consumer environment did not exclude poisoned inherited variables")
        for name, scope, label, sandbox, add_dir in (
            ("control-wrong-scope", "user", "setup-control", "danger-full-access", False),
            ("control-wrong-label", "project", "other", "danger-full-access", False),
            ("control-add-dir", "project", "setup-control", "danger-full-access", True),
            ("danger-without-control", "project", "setup-control", "danger-full-access", False),
        ):
            control = name != "danger-without-control"
            candidate = argparse.Namespace(scope=scope, label=label, sandbox=sandbox,
                                           allow_user_registration_write=add_dir, control_project_setup=control,
                                           prepare=False, cleanup=False)
            try:
                validate_control_args(candidate)
            except ProbeError as error:
                failures[name] = str(error)
            else:
                raise ProbeError("control guard accepted " + name)
        for mode in ("prepare", "cleanup"):
            candidate = argparse.Namespace(scope="project", label="setup-control", sandbox="danger-full-access",
                                           allow_user_registration_write=False, control_project_setup=True,
                                           prepare=mode == "prepare", cleanup=mode == "cleanup")
            try:
                validate_control_args(candidate)
            except ProbeError as error:
                failures["control-" + mode] = str(error)
            else:
                raise ProbeError("control guard accepted " + mode)
        traversal_root = Path("/private/tmp/craft-codex-guard/../outside")
        try:
            validate_root(traversal_root, must_exist=False)
        except ProbeError as error:
            failures["path-traversal-root"] = str(error)
        else:
            raise ProbeError("root guard accepted path traversal")
        link = root / "link-parent"
        link.symlink_to(Path("/private/tmp"))
        try:
            validate_root(link / "craft-codex-escaped", must_exist=False)
        except ProbeError as error:
            failures["symlink-parent-root"] = str(error)
        else:
            raise ProbeError("root guard accepted a symlink parent")
        for name, candidate in {
            "path-traversal-output": Path("/private/tmp/craft-codex-guard/../outside.json"),
            "symlink-parent-output": link / "craft-codex-escaped.json",
        }.items():
            try:
                validate_self_test_output(candidate)
            except ProbeError as error:
                failures[name] = str(error)
            else:
                raise ProbeError("self-test output guard accepted " + name)
        write_json(target, {"status": "PASS", "rejected": failures, "consumer_env_keys": sorted(observed),
                            "codex_started": False})
    print("PASS", target)
    return 0


def cleanup(args: argparse.Namespace) -> None:
    """Remove only the selected isolated Craft plugin and its receipt-owned roles."""
    root = validate_root(args.run_root, must_exist=True)
    if args.scope not in SCOPES:
        raise ProbeError("cleanup requires one explicit prepared scope")
    agentforge = require_absolute_executable(args.agentforge_bin, "agentforge-bin", allow_symlink=False)
    codex = require_absolute_executable(args.codex_bin, "codex-bin", allow_symlink=True)
    validate_agentforge(agentforge)
    base, evidence = root / args.scope, root / "evidence"
    home, project = base / "codex-home", base / "project"
    if any(path.is_symlink() or not path.is_dir() or path.resolve() != path for path in (base, home, project)):
        raise ProbeError("cleanup scope contains missing or symlinked fixture directories")
    if not (project / ".git").is_dir():
        raise ProbeError("cleanup project is not a disposable Git repository")
    config_without_external_integrations(home / "config.toml")
    project_config = project / ".codex" / "config.toml"
    if project_config.exists():
        config_without_external_integrations(project_config, require_apps_false=False)
    env = consumer_env(home, agentforge)
    before = json.loads((evidence / (args.scope + "-fixture-before.json")).read_text())
    cache = Path(before["cache"])
    if not cache.is_absolute() or home / "plugins" / "cache" not in cache.parents:
        raise ProbeError("cleanup cache is outside the intended isolated CODEX_HOME")
    user_root, project_root = home, project / ".codex"
    config_paths = [home / "config.toml"]
    if project_config.exists():
        config_paths.append(project_config)
    if args.scope == "fallback":
        no_craft_registrations(*config_paths)
        assert_no_craft_state(user_root)
        assert_no_craft_state(project_root)
    selected_root = user_root if args.scope == "user" else project_root
    opposite_root = project_root if args.scope == "user" else user_root
    opposite_before = registration_state(opposite_root)
    sequence = 800 + SCOPES.index(args.scope) * 10
    command(evidence, sequence + 1, args.scope + "-cleanup-plugin-remove",
            [str(codex), "plugin", "remove", PACKAGE_ID + "@jdh-agents"], project, env)
    if cache.exists():
        raise ProbeError("native Craft cache remains after isolated cleanup: " + str(cache))
    command(evidence, sequence + 2, args.scope + "-cleanup-marketplace-remove",
            [str(codex), "plugin", "marketplace", "remove", "jdh-agents"], project, env)
    if args.scope != "fallback":
        scope_args = [str(agentforge), "remove-codex-agent", PACKAGE_ID, "--scope", args.scope, "--project-root", str(project)]
        preview_args = [str(agentforge), "preview-codex-agent-remove", PACKAGE_ID, "--scope", args.scope, "--project-root", str(project)]
        command(evidence, sequence + 3, args.scope + "-cleanup-receipt-preview", preview_args, project, env)
        command(evidence, sequence + 4, args.scope + "-cleanup-receipt-remove", scope_args, project, env)
        command(evidence, sequence + 5, args.scope + "-cleanup-receipt-remove-repeat", scope_args, project, env)
    configs = [home / "config.toml"]
    if project_config.exists():
        configs.append(project_config)
    no_craft_registrations(*configs)
    assert_no_craft_state(selected_root)
    if registration_state(opposite_root) != opposite_before:
        raise ProbeError("cleanup changed the opposite scope's Craft state")
    if args.scope == "fallback":
        assert_no_craft_state(opposite_root)
    auth = home / "auth.json"
    if auth.is_symlink():
        auth.unlink()
    elif auth.exists():
        raise ProbeError("refusing to remove unexpected non-symlink auth object: " + str(auth))
    if auth.exists() or auth.is_symlink():
        raise ProbeError("disposable auth path remains after cleanup: " + str(auth))
    write_json(evidence / (args.scope + "-cleanup-summary.json"), {"status": "PASS", "scope": args.scope,
        "codex_home": str(home), "project_root": str(project), "cache_absent": not cache.exists(),
        "auth_link_removed": True, "selected_registration_root": str(selected_root),
        "opposite_registration_root": str(opposite_root), "fallback_has_no_agentforge_scope": args.scope == "fallback"})
    print("CLEANUP PASS", args.scope)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prepare", action="store_true", help="create native-installed isolated fixtures from committed output")
    parser.add_argument("--self-test", action="store_true", help="run config guard tests without starting Codex")
    parser.add_argument("--self-test-output", type=Path, help="fresh persistent /private/tmp result path for --self-test")
    parser.add_argument("--cleanup", action="store_true", help="remove one selected isolated Craft plugin and receipt")
    parser.add_argument("--control-project-setup", action="store_true", help="record the separately approved project setup control only")
    parser.add_argument("--run-root", type=Path, required=False)
    parser.add_argument("--scope", choices=SCOPES)
    parser.add_argument("--label")
    parser.add_argument("--sandbox", choices=("read-only", "workspace-write", "danger-full-access"))
    parser.add_argument("--allow-user-registration-write", action="store_true", help="allow isolated home only for user workspace-write setup")
    parser.add_argument("--source-repo", type=Path)
    parser.add_argument("--source-commit")
    parser.add_argument("--codex-bin", type=Path)
    parser.add_argument("--agentforge-bin", type=Path)
    parser.add_argument("--codex-auth-file", type=Path, default=Path.home() / ".codex" / "auth.json")
    args = parser.parse_args(argv)
    if args.self_test:
        if args.prepare or args.cleanup or args.allow_user_registration_write or args.control_project_setup:
            parser.error("--self-test cannot be combined with preparation, cleanup, or registration write access")
        return args
    required = ("run_root", "codex_bin", "agentforge_bin")
    if args.prepare:
        required += ("source_repo", "source_commit")
    elif args.cleanup:
        required += ("scope",)
    else:
        required += ("scope", "label", "sandbox")
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        parser.error("missing required arguments: " + ", ".join("--" + item.replace("_", "-") for item in missing))
    if args.allow_user_registration_write and (args.prepare or args.cleanup or args.scope != "user" or args.sandbox != "workspace-write"):
        parser.error("--allow-user-registration-write is only valid for user workspace-write probe runs")
    try:
        validate_control_args(args)
    except ProbeError as error:
        parser.error(str(error))
    return args


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        if args.self_test:
            return self_test(args.self_test_output)
        if args.prepare:
            prepare(args)
            return 0
        if args.cleanup:
            cleanup(args)
            return 0
        return run_probe(args)
    except ProbeError as error:
        print("error: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Save one fresh Codex acceptance session in an explicitly isolated fixture.

This runner does not install plugins or roles. Prepare an isolated home and
trusted project from committed output, then supply an exact saved prompt.
Project write-access controls require explicit user approval outside this runner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import tomllib


SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"
AGENTFORGE_VERSION = "1.2.0"
AGENTFORGE_DARWIN_ARM64_SHA256 = "67107b2a96892a1a3429010bbb8475d61c4100e1ac01783367e23aef402c2d54"
CANONICAL_MOCK = Path(__file__).resolve().with_name("linear_mock_mcp.py")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_regular(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(label + " must be a regular non-symlink file: " + str(path))


def validate_agentforge(binary: Path) -> None:
    if platform.system() != "Darwin" or platform.machine() not in ("arm64", "aarch64"):
        raise ValueError("this acceptance probe requires the verified Darwin arm64 AgentForge release")
    if file_sha256(binary) != AGENTFORGE_DARWIN_ARM64_SHA256:
        raise ValueError("agentforge-bin is not the verified AgentForge v1.2.0 Darwin arm64 binary")
    try:
        version = subprocess.run(
            [str(binary), "--version"],
            env={"PATH": SYSTEM_PATH},
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise ValueError("agentforge-bin --version timed out") from error
    if version.returncode or not re.search(r"(?<![0-9.])1\.2\.0(?![0-9.])", version.stdout):
        raise ValueError("agentforge-bin did not report version 1.2.0")


def validate_mock_write_fixture(root: Path, scope: str, home: Path) -> None:
    """Prove that preapproval names only the copied local mock connector."""
    if root.is_symlink() or not root.is_dir() or root.resolve() != root:
        raise ValueError("fixture root must be a real non-symlink directory")
    config_path = home / "config.toml"
    require_regular(config_path, "fixture config")
    fixture_mock = root / "linear_mock_mcp.py"
    expected_mock_root = root / scope / "mock"
    if (not expected_mock_root.is_dir() or expected_mock_root.is_symlink()
            or expected_mock_root.resolve() != expected_mock_root):
        raise ValueError("mock root must be the real scope-specific fixture directory")
    require_regular(fixture_mock, "fixture mock server")
    require_regular(CANONICAL_MOCK, "repository canonical mock server")
    if fixture_mock.resolve().parent != root or fixture_mock.read_bytes() != CANONICAL_MOCK.read_bytes():
        raise ValueError("fixture mock server must be an unchanged regular copy of the repository canonical source")
    try:
        config = tomllib.loads(config_path.read_text())
    except tomllib.TOMLDecodeError as error:
        raise ValueError("fixture config is not valid TOML") from error
    features = config.get("features")
    servers = config.get("mcp_servers")
    if not isinstance(features, dict) or features.get("apps") is not False:
        raise ValueError("mock write approval requires features.apps = false")
    if not isinstance(servers, dict) or set(servers) != {"linear-fixture"}:
        raise ValueError("mock write approval requires exactly one mcp_servers.linear-fixture entry")
    server = servers["linear-fixture"]
    expected_args = [str(fixture_mock), "--root", str(expected_mock_root)]
    if not isinstance(server, dict) or server.get("command") != "/usr/bin/python3" or server.get("args") != expected_args:
        raise ValueError("mock write approval requires the exact local Python fixture command and arguments")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--scope", choices=("user", "project", "fallback"), required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--sandbox", choices=("read-only", "workspace-write"), required=True)
    parser.add_argument("--codex-bin", type=Path, required=True)
    parser.add_argument("--agentforge-bin", type=Path, required=True)
    parser.add_argument("--mock-writes", action="store_true", help="preapprove only local fixture save_issue/save_comment; requires apps disabled")
    args = parser.parse_args()
    root = args.run_root.resolve()
    if (not args.run_root.is_absolute() or args.run_root.is_symlink() or not args.run_root.is_dir()
            or root != args.run_root or not str(root).startswith("/private/tmp/linear-codex-")):
        parser.error("run-root must be an absolute /private/tmp/linear-codex-* fixture")
    if not args.label or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in args.label):
        parser.error("label must use lowercase letters, digits, hyphens, or underscores")
    for binary in (args.codex_bin, args.agentforge_bin):
        if not binary.is_absolute() or not binary.is_file() or not os.access(binary, os.X_OK):
            parser.error("binaries must be absolute executable files")
    if args.agentforge_bin.is_symlink():
        parser.error("agentforge-bin must not be a symlink")
    try:
        validate_agentforge(args.agentforge_bin)
    except ValueError as error:
        parser.error(str(error))
    base = root / args.scope
    home, project = base / "codex-home", base / "project"
    for path in (base, home, project):
        if not path.is_dir() or path.is_symlink() or path.resolve() != path:
            parser.error("fixture directories must already exist without symlinks: " + str(path))
    prompt = base / (args.label + ".prompt.txt")
    if not prompt.is_file():
        parser.error("missing prompt: " + str(prompt))
    stem = base / args.label
    if stem.with_suffix(".events.jsonl").exists():
        parser.error("refusing to overwrite session evidence")
    env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTFORGE_")}
    env.update(CODEX_HOME=str(home), AGENTFORGE_BIN=str(args.agentforge_bin), PATH="/usr/bin:/bin:/usr/sbin:/sbin")
    command = [str(args.codex_bin), "exec", "-C", str(project), "--skip-git-repo-check", "--json",
               "-s", args.sandbox, "-m", "gpt-5.6-luna", "-c", 'model_reasoning_effort="medium"',
               "-c", "allow_login_shell=false", "--add-dir", str(home), "-o", str(stem) + ".last.txt", "-"]
    if args.mock_writes:
        try:
            validate_mock_write_fixture(root, args.scope, home)
        except ValueError as error:
            parser.error(str(error))
        command[2:2] = ["-c", 'mcp_servers.linear-fixture.tools.save_issue.approval_mode="approve"',
                        "-c", 'mcp_servers.linear-fixture.tools.save_comment.approval_mode="approve"']
    stem.with_suffix(".command.json").write_text(json.dumps({"argv": command,
        "env": {k: env[k] for k in ("CODEX_HOME", "AGENTFORGE_BIN", "PATH")}, "stdin": str(prompt),
        "mock_write_approval": args.mock_writes}, indent=2) + "\n")
    with stem.with_suffix(".events.jsonl").open("w") as out, stem.with_suffix(".stderr").open("w") as err:
        result = subprocess.run(command, input=prompt.read_text(), text=True, env=env, stdout=out, stderr=err, timeout=600)
    stem.with_suffix(".exit").write_text(str(result.returncode) + "\n")
    # A completed Codex turn can report a failed tool with process exit 0.
    # Acceptance must inspect tool exits, output, and selected-scope state.
    print(args.scope, args.label, "process exit", result.returncode, "(semantic result requires evidence review)")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

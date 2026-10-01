#!/usr/bin/env python3
"""Save one fresh Codex acceptance session in an explicitly isolated fixture.

This runner does not install plugins or roles. Prepare an isolated home and
trusted project from committed output, then supply an exact saved prompt.
Project write-access controls require explicit user approval outside this runner.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--scope", choices=("user", "project", "fallback"), required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--sandbox", choices=("read-only", "workspace-write"), required=True)
    parser.add_argument("--codex-bin", type=Path, required=True)
    parser.add_argument("--agentforge-bin", type=Path, required=True)
    args = parser.parse_args()
    root = args.run_root.resolve()
    if not args.run_root.is_absolute() or not str(root).startswith("/private/tmp/linear-codex-"):
        parser.error("run-root must be an absolute /private/tmp/linear-codex-* fixture")
    if not args.label or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in args.label):
        parser.error("label must use lowercase letters, digits, hyphens, or underscores")
    for binary in (args.codex_bin, args.agentforge_bin):
        if not binary.is_absolute() or not binary.is_file() or not os.access(binary, os.X_OK):
            parser.error("binaries must be absolute executable files")
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
    stem.with_suffix(".command.json").write_text(json.dumps({"argv": command,
        "env": {k: env[k] for k in ("CODEX_HOME", "AGENTFORGE_BIN", "PATH")}, "stdin": str(prompt)}, indent=2) + "\n")
    with stem.with_suffix(".events.jsonl").open("w") as out, stem.with_suffix(".stderr").open("w") as err:
        result = subprocess.run(command, input=prompt.read_text(), text=True, env=env, stdout=out, stderr=err, timeout=600)
    stem.with_suffix(".exit").write_text(str(result.returncode) + "\n")
    # A completed Codex turn can report a failed tool with process exit 0.
    # Acceptance must inspect tool exits, output, and selected-scope state.
    print(args.scope, args.label, "process exit", result.returncode, "(semantic result requires evidence review)")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

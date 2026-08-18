"""CLI entry point: ``uv run marketplace <cmd>`` or ``python -m marketplace <cmd>``."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from marketplace.codex_validate import validate_codex_marketplace
from marketplace.export import run_export
from marketplace.generation import (
    COMPILED_ROOT,
    GenerationError,
    check_publications,
    sync_publications,
)
from marketplace.lint import lint_plugins
from marketplace.privacy import scan_paths
from marketplace.validate import validate_manifest

# ---------------------------------------------------------------------------
# Repo-root helper
# ---------------------------------------------------------------------------

# This file lives at scripts/marketplace/__main__.py
# parents[0] = scripts/marketplace/
# parents[1] = scripts/
# parents[2] = repo root
_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parents[2]
_CANONICAL_MARKETPLACE = _REPO_ROOT / "MARKETPLACE.yaml"
_DEFAULT_EXPORT_CONFIG = _REPO_ROOT / "export" / "public.json"

# Authoring source. `lint` reads this, because lint grades what a human wrote;
# every other consumer below reads a compiled publication instead.
_PLUGINS_ROOT = _REPO_ROOT / "plugins"

# Compiled publications. Each is a self-contained marketplace root, so a
# runtime is pointed at the directory rather than at this repository.
_COMPILED_ROOT = _REPO_ROOT / COMPILED_ROOT
_CLAUDE_ROOT = _COMPILED_ROOT / "claude"
_CODEX_ROOT = _COMPILED_ROOT / "codex"

# Per-format defaults: a manifest is only meaningful against the plugins tree
# of its own publication, so the two always move together.
_NATIVE_PUBLICATIONS = {
    "claude": (
        _CLAUDE_ROOT / ".claude-plugin" / "marketplace.json",
        _CLAUDE_ROOT / "plugins",
    ),
    "codex": (
        _CODEX_ROOT / ".agents" / "plugins" / "marketplace.json",
        _CODEX_ROOT / "plugins",
    ),
}


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_sync(args: argparse.Namespace) -> int:
    root = COMPILED_ROOT.as_posix()
    try:
        if args.check:
            result = check_publications(_REPO_ROOT, _CANONICAL_MARKETPLACE)
        else:
            result = sync_publications(_REPO_ROOT, _CANONICAL_MARKETPLACE)
    except GenerationError as error:
        print(f"Publication compilation failed: {error}", file=sys.stderr)
        return 1
    _print_agentforge_output(result.stdout, result.stderr)

    if not args.check:
        print(f"Synced {result.file_count} compiled file(s) into {root}/.")
        return 0

    if not result.drift:
        print(f"Compiled publications are up-to-date ({result.file_count} files).")
        return 0

    print(f"Compiled publications in {root}/ are OUT OF SYNC:", file=sys.stderr)
    for issue in result.drift:
        print(f"  {issue.kind}: {root}/{issue.path.as_posix()}", file=sys.stderr)
    print("Run `uv run marketplace sync` to regenerate.", file=sys.stderr)
    return 1


def _cmd_validate(args: argparse.Namespace) -> int:
    default_manifest, default_plugins_root = _NATIVE_PUBLICATIONS[args.format]
    manifest_path = Path(args.manifest) if args.manifest else default_manifest
    plugins_root = Path(args.plugins_root) if args.plugins_root else default_plugins_root

    if not manifest_path.exists():
        print(f"Error: manifest not found: {manifest_path}", file=sys.stderr)
        print(
            "Compiled publications are generated; run `uv run marketplace sync`.",
            file=sys.stderr,
        )
        return 1

    try:
        with manifest_path.open(encoding="utf-8") as fh:
            manifest = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in {manifest_path}: {exc}", file=sys.stderr)
        return 1

    if args.format == "codex":
        errors = validate_codex_marketplace(manifest, plugins_root)
    else:
        errors = validate_manifest(manifest, plugins_root)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(
        f"{args.format.capitalize()} validation passed "
        f"({len(manifest.get('plugins', []))} plugins)."
    )
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    plugins_root = Path(args.plugins_root) if args.plugins_root else _PLUGINS_ROOT

    errors, warnings = lint_plugins(plugins_root)

    if warnings:
        print("Lint warnings:")
        for w in warnings:
            print(f"  [warn] {w}")

    if errors:
        print("Lint errors:", file=sys.stderr)
        for e in errors:
            print(f"  [error] {e}", file=sys.stderr)
        return 1

    n = 0
    if plugins_root.exists():
        n = sum(1 for p in plugins_root.rglob("*") if p.is_file() and not p.name.startswith("."))
    print(f"Lint passed ({n} files checked, {len(warnings)} warning(s)).")
    return 0


def _cmd_export(args: argparse.Namespace) -> int:
    config_path = Path(args.config) if args.config else _DEFAULT_EXPORT_CONFIG

    public_dir_str = args.public_dir or os.environ.get("PUBLIC_REPO_DIR")
    if not public_dir_str:
        print(
            "Error: --public-dir or PUBLIC_REPO_DIR env var required for export.",
            file=sys.stderr,
        )
        return 1

    public_root = Path(public_dir_str).expanduser().resolve()
    do_commit = args.commit
    do_push = args.push
    # dry_run is default-true unless --commit or --push given
    do_dry_run = args.dry_run or (not do_commit and not do_push)

    try:
        run_export(
            private_root=_REPO_ROOT,
            public_root=public_root,
            config_path=config_path,
            dry_run=do_dry_run,
            commit=do_commit,
            push=do_push,
        )
    except (ValueError, RuntimeError) as exc:
        print(f"Export failed: {exc}", file=sys.stderr)
        return 1

    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    """Repo-wide privacy gate: machine paths, secret-shaped strings, email/vault warnings.

    Scans git-tracked files under the given root (default: repo root) unless
    explicit paths are given. Used by the prek pre-push hook and by CI, so
    both run the exact same scanner as `marketplace export`.
    """
    root = Path(args.root).resolve() if args.root else _REPO_ROOT

    if args.paths:
        targets = [Path(p).resolve() for p in args.paths]
    else:
        result = subprocess.run(  # noqa: S603
            ["git", "-C", str(root), "ls-files", "-z"],  # noqa: S607
            capture_output=True,
            check=True,
        )
        targets = [
            root / name.decode("utf-8")
            for name in result.stdout.split(b"\x00")
            if name and not name.decode("utf-8").startswith("scripts/tests/")
        ]

    hard, soft = scan_paths(targets)

    for msg in soft:
        print(f"  [privacy warn] {msg}")

    if hard:
        print("Privacy gate FAILED:", file=sys.stderr)
        for e in hard:
            print(f"  {e}", file=sys.stderr)
        return 1

    print(f"Privacy gate passed ({len(targets)} file(s) scanned, {len(soft)} warning(s)).")
    return 0


def _cmd_check(args: argparse.Namespace) -> int:  # noqa: ARG001
    """CI entrypoint: generated drift + native validation + lint + privacy gate."""
    rc = 0

    # 1. sync --check
    print("=== sync --check ===")
    sync_ns = argparse.Namespace(check=True)
    rc |= _cmd_sync(sync_ns)

    # 1b. privacy gate — unskippable backstop for the prek pre-push hook
    print("\n=== privacy scan ===")
    scan_ns = argparse.Namespace(root=None, paths=[])
    rc |= _cmd_scan(scan_ns)

    # 2. validate committed Claude publication
    print("\n=== validate Claude ===")
    validate_ns = argparse.Namespace(manifest=None, plugins_root=None, format="claude")
    rc |= _cmd_validate(validate_ns)

    # 3. validate committed Codex publication
    print("\n=== validate Codex ===")
    codex_validate_ns = argparse.Namespace(manifest=None, plugins_root=None, format="codex")
    rc |= _cmd_validate(codex_validate_ns)

    # 4. lint
    print("\n=== lint ===")
    lint_ns = argparse.Namespace(plugins_root=None)
    rc |= _cmd_lint(lint_ns)

    if rc == 0:
        print("\nAll checks passed.")
    else:
        print("\nOne or more checks FAILED.", file=sys.stderr)

    return rc


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="marketplace",
        description="cc-marketplace plugin registry tooling",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # sync
    sync_p = sub.add_parser(
        "sync",
        help=f"Recompile the committed publications under {COMPILED_ROOT.as_posix()}/",
    )
    sync_p.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if the committed publications are out of sync; do NOT write.",
    )

    # validate
    val_p = sub.add_parser("validate", help="Validate a compiled marketplace manifest")
    val_p.add_argument(
        "--format",
        choices=("claude", "codex"),
        default="claude",
        help="Native marketplace format to validate (default: claude)",
    )
    val_p.add_argument(
        "--manifest",
        metavar="PATH",
        help="Path to manifest (default: the compiled publication for --format)",
    )
    val_p.add_argument(
        "--plugins-root",
        metavar="PATH",
        help="Path to plugins/ dir (default: the compiled publication for --format)",
    )

    # lint
    lint_p = sub.add_parser("lint", help="Lint plugin files")
    lint_p.add_argument("--plugins-root", metavar="PATH", help="Path to plugins/ dir")

    # export
    exp_p = sub.add_parser("export", help="Export allowlisted plugins to a public repo dir")
    exp_p.add_argument("--public-dir", metavar="PATH", help="Public repo root directory")
    exp_p.add_argument(
        "--config", metavar="PATH", help="Export config JSON (default: export/public.json)"
    )
    exp_p.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Show git diff/status without committing (the default when neither "
        "--commit nor --push is given)",
    )
    exp_p.add_argument("--commit", action="store_true", help="Commit after export")
    exp_p.add_argument("--push", action="store_true", help="Push after commit")

    # scan (privacy gate — repo-wide)
    scan_p = sub.add_parser(
        "scan", help="Repo-wide privacy gate: machine paths, secrets, email/vault warnings"
    )
    scan_p.add_argument("--root", metavar="PATH", help="Root to scan (default: repo root)")
    scan_p.add_argument(
        "paths", nargs="*", help="Explicit files to scan instead of the full git-tracked tree"
    )

    # check (CI entrypoint)
    sub.add_parser(
        "check", help="Run manifest drift checks + native validation + lint"
    )

    return parser


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    dispatch = {
        "sync": _cmd_sync,
        "validate": _cmd_validate,
        "lint": _cmd_lint,
        "export": _cmd_export,
        "scan": _cmd_scan,
        "check": _cmd_check,
    }

    handler = dispatch.get(args.command)
    if handler is None:
        parser.print_help()
        return 1

    return handler(args)


def _print_agentforge_output(stdout: str, stderr: str) -> None:
    if stdout:
        print(stdout, end="" if stdout.endswith("\n") else "\n")
    if stderr:
        print(
            stderr,
            end="" if stderr.endswith("\n") else "\n",
            file=sys.stderr,
        )


if __name__ == "__main__":
    sys.exit(main())

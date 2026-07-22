"""CLI entry point: ``uv run marketplace <cmd>`` or ``python -m marketplace <cmd>``."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from marketplace.codex_validate import validate_codex_marketplace
from marketplace.export import run_export
from marketplace.generation import (
    GenerationError,
    compare_native_manifests,
    compile_native_manifests,
    materialize_native_manifests,
)
from marketplace.lint import lint_plugins
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
_PLUGINS_ROOT = _REPO_ROOT / "plugins"
_PRIVATE_MANIFEST = _REPO_ROOT / ".claude-plugin" / "marketplace.json"
_CODEX_MANIFEST = _REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
_CANONICAL_MARKETPLACE = _REPO_ROOT / "MARKETPLACE.yaml"
_DEFAULT_EXPORT_CONFIG = _REPO_ROOT / "export" / "public.json"


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_sync(args: argparse.Namespace) -> int:
    try:
        compilation = compile_native_manifests(_REPO_ROOT, _CANONICAL_MARKETPLACE)
    except GenerationError as error:
        print(f"Native manifest generation failed: {error}", file=sys.stderr)
        return 1
    _print_agentforge_output(compilation.stdout, compilation.stderr)

    if args.check:
        issues = compare_native_manifests(_REPO_ROOT, compilation.manifests)
        if not issues:
            print(
                f"Native manifests are up-to-date ({len(compilation.manifests)} files)."
            )
            return 0
        print("Native manifests are OUT OF SYNC (drift detected):", file=sys.stderr)
        for issue in issues:
            print(f"  {issue.kind}: {issue.path.as_posix()}", file=sys.stderr)
        print("Run `uv run marketplace sync` to regenerate.", file=sys.stderr)
        return 1

    materialize_native_manifests(_REPO_ROOT, compilation.manifests)
    print(f"Synced {len(compilation.manifests)} generated native manifest(s).")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    default_manifest = _CODEX_MANIFEST if args.format == "codex" else _PRIVATE_MANIFEST
    manifest_path = Path(args.manifest) if args.manifest else default_manifest
    plugins_root = Path(args.plugins_root) if args.plugins_root else _PLUGINS_ROOT

    if not manifest_path.exists():
        print(f"Error: manifest not found: {manifest_path}", file=sys.stderr)
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


def _cmd_check(args: argparse.Namespace) -> int:  # noqa: ARG001
    """CI entrypoint: generated drift + native validation + lint."""
    rc = 0

    # 1. sync --check
    print("=== sync --check ===")
    sync_ns = argparse.Namespace(check=True)
    rc |= _cmd_sync(sync_ns)

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
        "sync", help="Regenerate committed native manifests from AgentForge definitions"
    )
    sync_p.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if native manifests are out of sync; do NOT write.",
    )

    # validate
    val_p = sub.add_parser("validate", help="Validate marketplace.json schema")
    val_p.add_argument(
        "--format",
        choices=("claude", "codex"),
        default="claude",
        help="Native marketplace format to validate (default: claude)",
    )
    val_p.add_argument("--manifest", metavar="PATH", help="Path to manifest (default: private)")
    val_p.add_argument("--plugins-root", metavar="PATH", help="Path to plugins/ dir")

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

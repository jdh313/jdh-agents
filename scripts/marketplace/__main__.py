"""CLI entry point: ``uv run marketplace <cmd>`` or ``python -m marketplace <cmd>``."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from marketplace.export import run_export
from marketplace.lint import lint_plugins
from marketplace.manifest import build_private
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
_DEFAULT_EXPORT_CONFIG = _REPO_ROOT / "export" / "public.json"


# ---------------------------------------------------------------------------
# JSON writer (matches existing format: indent=2, ensure_ascii=True, trailing \n)
# ---------------------------------------------------------------------------


def _write_manifest(path: Path, manifest: dict) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=True)
        fh.write("\n")


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------


def _cmd_sync(args: argparse.Namespace) -> int:
    if not _PRIVATE_MANIFEST.exists():
        print(f"Error: {_PRIVATE_MANIFEST} not found", file=sys.stderr)
        return 1

    new_manifest = build_private(_PLUGINS_ROOT, _PRIVATE_MANIFEST)

    if args.check:
        # Read the on-disk manifest and compare
        with _PRIVATE_MANIFEST.open(encoding="utf-8") as fh:
            on_disk = json.load(fh)

        on_disk_plugins = on_disk.get("plugins", [])
        new_plugins = new_manifest.get("plugins", [])

        if on_disk_plugins == new_plugins:
            n = len(new_plugins)
            print(f"marketplace.json is up-to-date ({n} plugins).")
            return 0
        else:
            old_names = {p["name"] for p in on_disk_plugins}
            new_names = {p["name"] for p in new_plugins}
            added = sorted(new_names - old_names)
            removed = sorted(old_names - new_names)
            print("marketplace.json is OUT OF SYNC (drift detected):", file=sys.stderr)
            if added:
                print(f"  Added:   {', '.join(added)}", file=sys.stderr)
            if removed:
                print(f"  Removed: {', '.join(removed)}", file=sys.stderr)
            # Check for version/description changes on common plugins
            old_map = {p["name"]: p for p in on_disk_plugins}
            new_map = {p["name"]: p for p in new_plugins}
            for name in sorted(old_names & new_names):
                if old_map[name] != new_map[name]:
                    print(f"  Changed: {name}", file=sys.stderr)
            print(
                f"  On-disk: {len(on_disk_plugins)} plugins  |  "
                f"Discovered: {len(new_plugins)} plugins",
                file=sys.stderr,
            )
            print("Run `marketplace sync` (without --check) to update.", file=sys.stderr)
            return 1

    # Write mode
    _write_manifest(_PRIVATE_MANIFEST, new_manifest)
    n = len(new_manifest["plugins"])
    names = ", ".join(p["name"] for p in new_manifest["plugins"])
    print(f"Synced {n} plugin(s) to marketplace.json: {names}")
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest) if args.manifest else _PRIVATE_MANIFEST
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

    errors = validate_manifest(manifest, plugins_root)

    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"Validation passed ({len(manifest.get('plugins', []))} plugins).")
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
        n = sum(
            1
            for p in plugins_root.rglob("*")
            if p.is_file() and not p.name.startswith(".")
        )
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
    """CI entrypoint: sync --check + validate + lint."""
    rc = 0

    # 1. sync --check
    print("=== sync --check ===")
    sync_ns = argparse.Namespace(check=True)
    rc |= _cmd_sync(sync_ns)

    # 2. validate private manifest
    print("\n=== validate ===")
    validate_ns = argparse.Namespace(manifest=None, plugins_root=None)
    rc |= _cmd_validate(validate_ns)

    # 3. lint
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
    sync_p = sub.add_parser("sync", help="Regenerate marketplace.json from plugins/")
    sync_p.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if marketplace.json is out of sync; do NOT write.",
    )

    # validate
    val_p = sub.add_parser("validate", help="Validate marketplace.json schema")
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
    sub.add_parser("check", help="Run sync --check + validate + lint (CI entrypoint)")

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


if __name__ == "__main__":
    sys.exit(main())

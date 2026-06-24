"""Export allowlisted plugins to a separate public repo directory."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from marketplace.manifest import build_public
from marketplace.validate import validate_manifest

# ---------------------------------------------------------------------------
# Privacy gate patterns
# ---------------------------------------------------------------------------

# Absolute machine-home paths — fail hard
_ABSOLUTE_HOME_RE = re.compile(r"(?:Users|home)/[A-Za-z0-9._-]+/")

# Secret-ish assignments — fail hard
_SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)

# Bare vault-name mentions — warn only (intentional configurable-default examples)
_VAULT_WARN_RE = re.compile(r"Loose Ends")


def _scan_privacy(file_path: Path) -> tuple[list[str], list[str]]:
    """Return (hard_errors, soft_warnings) for one file.

    Skips binary files gracefully.
    """
    hard: list[str] = []
    soft: list[str] = []

    try:
        text = file_path.read_text(encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
        # Binary file — skip
        return hard, soft

    for lineno, line in enumerate(text.splitlines(), start=1):
        loc = f"{file_path}:{lineno}"
        if _ABSOLUTE_HOME_RE.search(line):
            hard.append(f"Absolute home path in {loc}: {line.strip()!r}")
        if _SECRET_RE.search(line):
            hard.append(f"Secret-ish value in {loc}: {line.strip()!r}")
        if _VAULT_WARN_RE.search(line):
            soft.append(f"Vault name mention in {loc} (intentional default, OK)")

    return hard, soft


def _privacy_gate(private_root: Path, allowlist: list[str]) -> None:
    """Scan every text file in the allowlisted plugin dirs.

    Raises ``ValueError`` with all hard errors concatenated if any are found.
    Prints soft warnings to stdout (does NOT raise).
    """
    plugins_dir = private_root / "plugins"
    all_hard: list[str] = []

    for name in allowlist:
        plugin_dir = plugins_dir / name
        if not plugin_dir.exists():
            continue
        for fpath in sorted(plugin_dir.rglob("*")):
            if not fpath.is_file():
                continue
            hard, soft = _scan_privacy(fpath)
            all_hard.extend(hard)
            for msg in soft:
                print(f"  [privacy warn] {msg}")

    if all_hard:
        detail = "\n".join(f"  {e}" for e in all_hard)
        raise ValueError(f"Privacy gate FAILED:\n{detail}")


# ---------------------------------------------------------------------------
# Copy helpers
# ---------------------------------------------------------------------------

_IGNORE_NAMES: frozenset[str] = frozenset(
    [".git", ".jj", ".DS_Store", "__pycache__", ".a5c", ".docs"]
)
_IGNORE_SUFFIXES: frozenset[str] = frozenset([".pyc"])


def _copy_ignore(src: str, names: list[str]) -> set[str]:
    """shutil.copytree ignore callable — filters by name and suffix."""
    ignored: set[str] = set()
    for name in names:
        if name in _IGNORE_NAMES or any(name.endswith(s) for s in _IGNORE_SUFFIXES):
            ignored.add(name)
    return ignored


# ---------------------------------------------------------------------------
# git helpers
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path) -> str:
    """Run a git command; print its output and return stdout."""
    cmd = ["git", "-C", str(cwd)] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed (exit {result.returncode})")
    return result.stdout


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def run_export(
    private_root: Path,
    public_root: Path,
    config_path: Path,
    *,
    dry_run: bool,
    commit: bool,
    push: bool,
) -> None:
    """Export allowlisted plugins from *private_root* to *public_root*.

    Steps:
      1. Read config; verify allowlisted plugins exist.
      2. Privacy gate — hard-fail on secrets/home paths; warn on vault names.
      3. Copy plugin dirs; remove demoted dirs.
      4. Write public manifest and validate.
      5. Dry-run or commit/push.
    """
    # --- 1. Load config --------------------------------------------------
    with config_path.open(encoding="utf-8") as fh:
        config: dict[str, Any] = json.load(fh)

    allowlist: list[str] = config["allowlist"]
    plugins_dir = private_root / "plugins"

    missing = [
        name
        for name in allowlist
        if not (plugins_dir / name / ".claude-plugin" / "plugin.json").exists()
    ]
    if missing:
        raise ValueError(
            f"Export config lists plugins not found in {plugins_dir}: "
            + ", ".join(missing)
        )

    print(f"Exporting {len(allowlist)} plugins: {', '.join(allowlist)}")

    # --- 2. Privacy gate -------------------------------------------------
    print("Running privacy gate...")
    _privacy_gate(private_root, allowlist)
    print("  Privacy gate passed.")

    # --- 3. Copy plugin dirs ---------------------------------------------
    public_plugins_dir = public_root / "plugins"
    public_plugins_dir.mkdir(parents=True, exist_ok=True)

    for name in allowlist:
        src = plugins_dir / name
        dst = public_plugins_dir / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=_copy_ignore)
        print(f"  Copied plugins/{name}")

    # Remove demoted dirs (present in public but not in allowlist)
    if public_plugins_dir.exists():
        for entry in public_plugins_dir.iterdir():
            if entry.is_dir() and entry.name not in allowlist:
                shutil.rmtree(entry)
                print(f"  Removed demoted plugins/{entry.name}")

    # --- 4. Write manifest and validate ----------------------------------
    public_manifest_dir = public_root / ".claude-plugin"
    public_manifest_dir.mkdir(parents=True, exist_ok=True)
    public_manifest_path = public_manifest_dir / "marketplace.json"

    manifest = build_public(config, plugins_dir, existing_output_path=public_manifest_path)

    # Validate against the public plugins dir (already copied)
    errors = validate_manifest(manifest, public_plugins_dir)
    if errors:
        detail = "\n".join(f"  {e}" for e in errors)
        raise ValueError(f"Public manifest validation failed:\n{detail}")

    with public_manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=True)
        fh.write("\n")
    print(f"  Wrote {public_manifest_path}")

    # --- 5. Dry-run or commit/push ---------------------------------------
    if dry_run:
        print("\n--- dry-run: git status (intent-to-add) ---")
        try:
            _git(["add", "-A", "-N"], public_root)
            _git(["status", "--short"], public_root)
            _git(["diff", "--stat"], public_root)
        except RuntimeError as exc:
            print(f"  [dry-run git error — repo may not be initialized]: {exc}")
        print("--- dry-run complete; no commit made ---")
        return

    if commit or push:
        _git(["add", "-A"], public_root)
        # Skip cleanly on a no-op export (nothing staged) so idempotent re-runs
        # — and CI on unrelated pushes — don't fail on "nothing to commit".
        status = subprocess.run(
            ["git", "-C", str(public_root), "status", "--porcelain"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        if not status:
            print("  No changes to export; nothing to commit.")
            return
        today = date.today().isoformat()
        _git(
            ["commit", "-m", f"export: sync from cc-marketplace ({today})"],
            public_root,
        )

    if push:
        _git(["push"], public_root)

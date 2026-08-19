"""Export allowlisted plugins to a separate public repo directory."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

from marketplace.generation import COMPILED_ROOT
from marketplace.manifest import build_public
from marketplace.privacy import scan_file as _scan_privacy  # noqa: F401 (re-exported for tests)
from marketplace.privacy import scan_paths
from marketplace.validate import validate_manifest

# Repository-relative plugins tree of the compiled Claude publication.
COMPILED_CLAUDE_PLUGINS = COMPILED_ROOT / "claude" / "plugins"


def _privacy_gate(plugins_dir: Path, allowlist: list[str]) -> None:
    """Scan every text file in the allowlisted plugin dirs.

    Takes the plugins directory rather than the repository root: what ships is
    the compiled Claude publication, so the gate must scan the bytes actually
    being published, not the authoring source they were compiled from.

    Raises ``ValueError`` with all hard errors concatenated if any are found.
    Prints soft warnings to stdout (does NOT raise).
    """
    files: list[Path] = []
    for name in allowlist:
        plugin_dir = plugins_dir / name
        if not plugin_dir.exists():
            continue
        files.extend(fpath for fpath in plugin_dir.rglob("*") if fpath.is_file())

    hard, soft = scan_paths(files)
    for msg in soft:
        print(f"  [privacy warn] {msg}")

    if hard:
        detail = "\n".join(f"  {e}" for e in hard)
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
# Commit-message changelog
# ---------------------------------------------------------------------------


def _published_versions(manifest_path: Path) -> dict[str, str]:
    """Map plugin name -> version from an existing public manifest (empty if none)."""
    if not manifest_path.exists():
        return {}
    try:
        with manifest_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return {p["name"]: p.get("version") for p in data.get("plugins", [])}
    except (json.JSONDecodeError, OSError, KeyError):
        return {}


def _changed_plugins(porcelain_status: str) -> set[str]:
    """Plugin names whose files changed, parsed from `git status --porcelain`."""
    names: set[str] = set()
    for line in porcelain_status.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:  # rename: "old -> new"
            path = path.split(" -> ", 1)[1]
        parts = path.strip().strip('"').split("/")
        if len(parts) >= 2 and parts[0] == "plugins":
            names.add(parts[1])
    return names


def _export_commit_message(
    old_versions: dict[str, str],
    new_versions: dict[str, str],
    changed: set[str],
    today: str,
) -> tuple[str, str]:
    """Build (subject, body) summarizing version deltas + touched plugins."""
    added = sorted(n for n in new_versions if n not in old_versions)
    removed = sorted(n for n in old_versions if n not in new_versions)

    bumped: list[str] = []
    touched: list[str] = []
    for name in sorted(changed):
        if name in added or name in removed:
            continue
        ov, nv = old_versions.get(name), new_versions.get(name)
        if ov != nv:
            bumped.append(f"* {name} {ov} -> {nv}")
        else:
            touched.append(f"* {name} {nv} (files changed)")

    lines: list[str] = []
    lines += [f"+ {n} {new_versions[n]} (added)" for n in added]
    lines += [f"- {n} (removed)" for n in removed]
    lines += bumped
    lines += touched

    n = len(added) + len(removed) + len(bumped) + len(touched)
    if n:
        subject = f"export: sync {n} plugin(s) from jdh-agents ({today})"
        body = "\n".join(lines)
    else:
        subject = f"export: refresh manifest from jdh-agents ({today})"
        body = "Manifest/metadata refresh; no plugin file changes."
    return subject, body


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

    # The public repo is a Claude marketplace, so it receives the compiled
    # Claude publication — not the authoring source. This is what keeps
    # authoring-layer frontmatter out of a published plugin.
    plugins_dir = private_root / COMPILED_CLAUDE_PLUGINS

    if not plugins_dir.is_dir():
        raise ValueError(
            f"Compiled Claude publication not found at {plugins_dir}; "
            "run `uv run marketplace sync` first."
        )

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
    _privacy_gate(plugins_dir, allowlist)
    print("  Privacy gate passed.")

    # --- 3. Copy plugin dirs ---------------------------------------------
    public_plugins_dir = public_root / "plugins"
    public_plugins_dir.mkdir(parents=True, exist_ok=True)

    canonical_plugins_dir = private_root / "plugins"

    for name in allowlist:
        src = plugins_dir / name
        dst = public_plugins_dir / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=_copy_ignore)

        # The compiler publishes what a runtime loads, which excludes the
        # package-level README. That file is the public repo's only
        # human-facing description of a plugin, so carry it across explicitly
        # rather than letting the cutover silently drop it.
        readme = canonical_plugins_dir / name / "README.md"
        if readme.is_file():
            readme_hard, readme_soft = _scan_privacy(readme)
            for msg in readme_soft:
                print(f"  [privacy warn] {msg}")
            if readme_hard:
                detail = "\n".join(f"  {e}" for e in readme_hard)
                raise ValueError(f"Privacy gate FAILED:\n{detail}")
            shutil.copy2(readme, dst / "README.md")

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

    # Capture the previously-published versions BEFORE overwriting, so the
    # commit message can summarize what changed in this export.
    old_versions = _published_versions(public_manifest_path)

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

    new_versions = {p["name"]: p.get("version") for p in manifest["plugins"]}

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
        subject, body = _export_commit_message(
            old_versions, new_versions, _changed_plugins(status), date.today().isoformat()
        )
        print(f"  Commit: {subject}")
        _git(["commit", "-m", subject, "-m", body], public_root)

    if push:
        _git(["push"], public_root)

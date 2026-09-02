#!/usr/bin/env python3
"""Privacy gate: scan text for signals that shouldn't ship in a public repo.

Two callers: the prek pre-push hook and CI, so both run the exact same scanner.

This is the one gate AgentForge cannot own. AgentForge only ever sees files a
publication declares, so a leak in an undeclared file -- a doc, a workflow, a
decision atom -- is invisible to it. This scans the whole git-tracked tree.

Scope note: this scans the current working tree, not git history. It catches
what's about to ship; it does not catch a leak introduced and later reverted
in an earlier commit. That's a real gap, but closing it generically means
diffing every commit in a push range, which is a separate, heavier tool than
this gate.

Pattern coverage is necessarily partial. Machine paths and secret-shaped
strings are mechanically detectable; a coworker's name, an employer's name,
or an internal workspace slug are not -- nothing here replaces a human read
before a first publish or before enrolling a new plugin.

Stdlib only, by design: it must run from a bare `python3` with no environment
to set up, because the hook that invokes it runs on every push.

Usage:
    python3 scripts/privacy_scan.py              # whole git-tracked tree
    python3 scripts/privacy_scan.py FILE...      # explicit files
    python3 scripts/privacy_scan.py --root DIR   # a different repo root
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Absolute machine-home paths — fail hard
_ABSOLUTE_HOME_RE = re.compile(r"(?:Users|home)/[A-Za-z0-9._-]+/")

# Secret-ish assignments — fail hard
_SECRET_RE = re.compile(
    r"(?i)(api[_-]?key|secret|token|passwd|password)\s*[:=]\s*['\"][^'\"]{8,}['\"]"
)

# Bare vault-name mentions — warn only (intentional configurable-default examples)
_VAULT_WARN_RE = re.compile(r"Loose Ends")

# Email addresses — warn only. Legitimate hits are common (LICENSE/PACKAGE.yaml
# author fields, third-party notices); a personal address slipping into skill
# or agent body text is the thing worth a human glance.
_EMAIL_WARN_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def scan_file(file_path: Path) -> tuple[list[str], list[str]]:
    """Return (hard_errors, soft_warnings) for one file.

    Skips binary files gracefully.
    """
    hard: list[str] = []
    soft: list[str] = []

    try:
        text = file_path.read_text(encoding="utf-8", errors="strict")
    except (UnicodeDecodeError, OSError):
        return hard, soft

    for lineno, line in enumerate(text.splitlines(), start=1):
        loc = f"{file_path}:{lineno}"
        if _ABSOLUTE_HOME_RE.search(line):
            hard.append(f"Absolute home path in {loc}: {line.strip()!r}")
        if _SECRET_RE.search(line):
            hard.append(f"Secret-ish value in {loc}: {line.strip()!r}")
        if _VAULT_WARN_RE.search(line):
            soft.append(f"Vault name mention in {loc} (intentional default, OK)")
        if _EMAIL_WARN_RE.search(line):
            soft.append(f"Email address in {loc}: {line.strip()!r}")

    return hard, soft


def scan_paths(paths: list[Path]) -> tuple[list[str], list[str]]:
    """Scan a flat list of file paths. Returns (hard_errors, soft_warnings)."""
    all_hard: list[str] = []
    all_soft: list[str] = []
    for fpath in sorted(paths):
        if not fpath.is_file():
            continue
        hard, soft = scan_file(fpath)
        all_hard.extend(hard)
        all_soft.extend(soft)
    return all_hard, all_soft


def git_tracked_files(root: Path) -> list[Path]:
    """Every git-tracked file under *root*."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True,
        check=True,
    )
    return [
        root / name.decode("utf-8")
        for name in result.stdout.split(b"\x00")
        if name
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="privacy_scan.py",
        description="Repo-wide privacy gate: machine paths, secrets, email/vault warnings",
    )
    parser.add_argument("--root", metavar="PATH", help="Root to scan (default: repo root)")
    parser.add_argument(
        "paths", nargs="*", help="Explicit files to scan instead of the full git-tracked tree"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    targets = [Path(p).resolve() for p in args.paths] if args.paths else git_tracked_files(root)

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


if __name__ == "__main__":
    sys.exit(main())

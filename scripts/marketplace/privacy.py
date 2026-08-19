"""Privacy gate: scan text for signals that shouldn't ship in a public repo.

Shared by three callers: `marketplace export` (allowlisted plugin dirs only),
`marketplace scan` (repo-wide, used by the prek pre-push hook and CI), and
the test suite.

Scope note: this scans the current working tree, not git history. It catches
what's about to ship; it does not catch a leak introduced and later reverted
in an earlier commit. That's a real gap — see `THIRD-PARTY-NOTICES.md`-style
history rewrites for the one-time cleanup — but closing it generically means
diffing every commit in a push range, which is a separate, heavier tool than
this gate.

Pattern coverage is necessarily partial. Machine paths and secret-shaped
strings are mechanically detectable; a coworker's name, an employer's name,
or an internal workspace slug are not — nothing here replaces a human read
before a first publish or before enrolling a new plugin.
"""

from __future__ import annotations

import re
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

# Directories never worth scanning: VCS internals and generated/vendor trees.
_SKIP_DIR_NAMES = frozenset(
    {".git", ".jj", "__pycache__", ".venv", "node_modules", ".ruff_cache", ".pytest_cache"}
)


def scan_file(file_path: Path) -> tuple[list[str], list[str]]:
    """Return (hard_errors, soft_warnings) for one file.

    Skips binary files gracefully.
    """
    hard: list[str] = []
    soft: list[str] = []

    try:
        text = file_path.read_text(encoding="utf-8", errors="strict")
    except UnicodeDecodeError:
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


def scan_tree(root: Path) -> tuple[list[str], list[str]]:
    """Scan every file under root, skipping VCS/vendor/cache directories."""
    files: list[Path] = []
    for fpath in root.rglob("*"):
        if not fpath.is_file():
            continue
        if _SKIP_DIR_NAMES & set(fpath.relative_to(root).parts):
            continue
        files.append(fpath)
    return scan_paths(files)

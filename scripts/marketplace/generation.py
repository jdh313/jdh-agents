"""AgentForge-backed publication compilation for jdh-agents.

AgentForge owns deterministic publication compilation, including atomic
materialization and total pruning of stale files.  This module owns only the
repository-specific policy: complete publications are committed under
``marketplaces/<publication-id>/``, and drift is measured against that tree.

Earlier revisions projected *only* the native manifest files back into the
source tree, discarding every compiled body.  That made the repository root
simultaneously the canonical source and a partial publication, which is what
let Codex install canonical Claude sources instead of its own projection.
Committing the whole compiled tree removes the ambiguity: ``plugins/`` is
authoring source, ``marketplaces/`` is compiler output, and each runtime is
pointed at its own publication root.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

PINNED_AGENTFORGE_REVISION = "1dba647fe872ef6422132cee82e03fb386f82eb8"

# Repository-relative root holding every compiled publication.  Each immediate
# child is a self-contained marketplace root for one target runtime.
COMPILED_ROOT = Path("marketplaces")


class GenerationError(RuntimeError):
    """Raised when AgentForge cannot produce the compiled publications."""


@dataclass(frozen=True, order=True)
class PublicationDrift:
    """One difference between canonical compilation and committed output."""

    kind: str
    path: Path


@dataclass(frozen=True)
class FileState:
    """The content and executability of one compiled file."""

    content: bytes
    executable: bool


@dataclass(frozen=True)
class CompilationResult:
    """AgentForge's diagnostics plus the size of the tree it produced."""

    file_count: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class CheckResult(CompilationResult):
    """A read-only comparison of a fresh compilation against the committed tree."""

    drift: tuple[PublicationDrift, ...]


def sync_publications(repo_root: Path, marketplace: Path) -> CompilationResult:
    """Compile publications directly into the committed ``marketplaces/`` tree.

    AgentForge stages into a temporary directory and publishes by rename, so a
    failed compile leaves the existing tree untouched and a successful one
    prunes every stale file.
    """

    destination = repo_root / COMPILED_ROOT
    stdout, stderr = _run_compile(repo_root, marketplace, destination)
    return CompilationResult(_count_files(destination), stdout, stderr)


def check_publications(repo_root: Path, marketplace: Path) -> CheckResult:
    """Compare the committed tree against a fresh plan without writing anything.

    This delegates to AgentForge's own ``check``, which diffs the compilation
    plan against the committed output in memory.  A throwaway compile is not an
    option once a publication declares ``root-manifest``: the compiler requires
    ``--out`` to resolve inside the marketplace directory, and it writes the root
    copy to the marketplace root itself -- so a temp-directory compile is
    rejected outright, and an in-tree one would clobber the committed root
    manifest during what is supposed to be a read-only check.  Delegating also
    covers the root manifest, which lives outside ``marketplaces/`` and is
    therefore invisible to a tree snapshot rooted there.
    """

    stdout, stderr, drift = _run_check(repo_root, marketplace, repo_root / COMPILED_ROOT)
    return CheckResult(_count_files(repo_root / COMPILED_ROOT), stdout, stderr, drift)


def snapshot_tree(root: Path) -> dict[Path, FileState]:
    """Map every regular file under *root* to its content and executability."""

    if not root.is_dir():
        return {}
    snapshot: dict[Path, FileState] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file():
            continue
        snapshot[path.relative_to(root)] = FileState(
            path.read_bytes(),
            bool(path.stat().st_mode & 0o111),
        )
    return snapshot


def compare_trees(
    expected: dict[Path, FileState],
    actual: dict[Path, FileState],
) -> list[PublicationDrift]:
    """Compare two tree snapshots without touching either one.

    Permission drift is reported separately from content drift: a compiled hook
    that loses its executable bit is still byte-identical, and calling that
    "changed" would hide why the runtime stopped being able to run it.
    """

    expected_paths = set(expected)
    actual_paths = set(actual)

    issues = [PublicationDrift("missing", path) for path in expected_paths - actual_paths]
    issues.extend(PublicationDrift("extra", path) for path in actual_paths - expected_paths)
    for path in expected_paths & actual_paths:
        if expected[path].content != actual[path].content:
            issues.append(PublicationDrift("changed", path))
        elif expected[path].executable != actual[path].executable:
            issues.append(PublicationDrift("mode", path))
    return sorted(issues, key=lambda issue: (issue.path.as_posix(), issue.kind))


def _run_compile(repo_root: Path, marketplace: Path, output_root: Path) -> tuple[str, str]:
    command = _resolve_agentforge_command()
    result = subprocess.run(
        [*command, "compile", str(marketplace.resolve()), "--out", str(output_root)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        details = "\n".join(
            part.strip() for part in (result.stdout, result.stderr) if part.strip()
        )
        suffix = f"\n{details}" if details else ""
        raise GenerationError(f"AgentForge compile exited {result.returncode}{suffix}")
    if not output_root.is_dir():
        raise GenerationError(
            f"AgentForge compile reported success but wrote no tree at {output_root}"
        )
    return result.stdout, result.stderr


def _run_check(
    repo_root: Path,
    marketplace: Path,
    output_root: Path,
) -> tuple[str, str, tuple[PublicationDrift, ...]]:
    """Run AgentForge's read-only drift check and parse its findings."""

    command = _resolve_agentforge_command()
    result = subprocess.run(
        [*command, "check", str(marketplace.resolve()), "--out", str(output_root)],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout, result.stderr, ()

    drift = tuple(parse_drift(result.stdout, result.stderr))
    if drift:
        return result.stdout, result.stderr, drift

    # A non-zero exit with no parsable drift line is a compile or load failure,
    # not an out-of-date tree; surfacing it as drift would tell the user to run
    # `sync`, which would fail the same way.
    details = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    suffix = f"\n{details}" if details else ""
    raise GenerationError(f"AgentForge check exited {result.returncode}{suffix}")


# AgentForge stands this token in for the marketplace root in reported paths.
_ROOT_TOKEN = "<root>"

# `error [<publication>] <kind>: <path>: <message>` -- the compiler's drift line.
_DRIFT_LINE = re.compile(r"^error \[(?P<publication>[^\]]+)\] (?P<kind>[\w-]+): (?P<path>[^:]+):")


def parse_drift(stdout: str, stderr: str) -> list[PublicationDrift]:
    """Extract drift findings from AgentForge's diagnostic stream."""

    issues: list[PublicationDrift] = []
    for line in f"{stdout}\n{stderr}".splitlines():
        match = _DRIFT_LINE.match(line.strip())
        if match is None:
            continue
        issues.append(PublicationDrift(match["kind"], _repo_relative(match["path"].strip())))
    return sorted(issues, key=lambda issue: (issue.path.as_posix(), issue.kind))


def _repo_relative(reported: str) -> Path:
    """Normalise a reported drift path to be relative to the repository root.

    AgentForge reports nested output relative to ``--out`` (``claude/...``) but
    prefixes the root manifest with a literal ``<root>`` token, because that file
    lives beside ``MARKETPLACE.yaml`` rather than under the output tree.  Both
    are rendered against the repository root so the printed path is one a user
    can actually open.
    """

    if reported == _ROOT_TOKEN or reported.startswith(f"{_ROOT_TOKEN}/"):
        return Path(reported[len(_ROOT_TOKEN) :].lstrip("/"))
    return COMPILED_ROOT / reported


def _count_files(root: Path) -> int:
    return sum(1 for path in root.rglob("*") if path.is_file() and not path.is_symlink())


def _resolve_agentforge_command() -> list[str]:
    configured_binary = os.environ.get("AGENTFORGE_BIN")
    if configured_binary:
        executable = _resolve_executable(configured_binary)
        if executable is None:
            raise GenerationError(
                f"AGENTFORGE_BIN does not name an executable: {configured_binary}"
            )
        return [str(executable)]

    configured_project = os.environ.get("AGENTFORGE_PROJECT")
    if configured_project:
        project = Path(configured_project).expanduser().resolve()
        cli = project / "src" / "cli.ts"
        if not cli.is_file() or not (project / "package.json").is_file():
            raise GenerationError(
                f"AGENTFORGE_PROJECT is not an AgentForge source checkout: {project}"
            )
        bun = shutil.which("bun")
        if bun is None:
            raise GenerationError("AGENTFORGE_PROJECT requires `bun` on PATH")
        revision = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        actual_revision = revision.stdout.strip() if revision.returncode == 0 else "unknown"
        if actual_revision != PINNED_AGENTFORGE_REVISION:
            raise GenerationError(
                "AGENTFORGE_PROJECT must be checked out at "
                f"{PINNED_AGENTFORGE_REVISION}; found {actual_revision}"
            )
        return [bun, "run", str(cli)]

    installed = shutil.which("agentforge")
    if installed:
        return [installed]

    raise GenerationError(
        "AgentForge is required. Set AGENTFORGE_PROJECT to the pinned checkout at "
        f"{PINNED_AGENTFORGE_REVISION}, set AGENTFORGE_BIN, or install `agentforge`."
    )


def _resolve_executable(command: str) -> Path | None:
    resolved = shutil.which(command)
    if resolved is not None:
        return Path(resolved).resolve()
    candidate = Path(command).expanduser()
    if candidate.is_file() and os.access(candidate, os.X_OK):
        return candidate.resolve()
    return None

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

import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# The compiler is pinned by *release identity*, not by source revision: CI and a
# local run must execute the same bytes.  A source build at the equivalent commit
# is not byte-identical to the published binary, so a commit SHA could never give
# that guarantee -- it only ever asserted "you built from the right tree".
AGENTFORGE_VERSION = "0.2.0"

# sha256 of each published asset for AGENTFORGE_VERSION, from the release's own
# SHA256SUMS.  Verified against the downloaded bytes before the binary is ever
# executed, so a compromised or truncated download fails closed.  The linux-x64
# entry is the same hash `.github/workflows/validate.yml` pins.
AGENTFORGE_SHA256 = {
    "darwin-arm64": "736648d63689091de5d0f3d2d127280a5d4b9adc3f8242aa8ae5607d62c54344",
    "darwin-x64": "43386490d4bb09aee74386c9d1bfce6a355b515403c9fe6a10d4f6f8b8f7bc7a",
    "linux-arm64": "2b537197588fdd3b465a5b093824a150e026b5d1536669c6735d1c1ee3bc1cc3",
    "linux-x64": "47f06c4f1baf7bed04e137ab6c2ca1a4fbab10a7c6f93a34db74f4e94d8c337b",
}

AGENTFORGE_RELEASE_URL = (
    "https://github.com/jdh313/agentforge/releases/download/v{version}/agentforge-{platform}"
)

# Downloaded compilers live here, keyed by version so a pin bump never reuses
# stale bytes.  Gitignored.  Anchored to the repository root rather than the
# process CWD: callers run the compiler with `cwd=` set elsewhere (the test
# harness compiles from a tmpdir), and a relative path would resolve to nothing
# there while still looking correct in a repo-root run.
AGENTFORGE_CACHE = Path(__file__).resolve().parents[2] / ".cache" / "agentforge"

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

    # Escape hatch for working *on* AgentForge: run a source checkout as-is.  No
    # revision assertion -- the whole point is to exercise an unreleased tree --
    # so this path is never the merge gate.  It announces itself for that reason.
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
            ["git", "-C", str(project), "rev-parse", "--short", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
        actual = revision.stdout.strip() if revision.returncode == 0 else "unknown"
        print(
            f"warning: compiling with AGENTFORGE_PROJECT source checkout at {actual}, "
            f"not the pinned v{AGENTFORGE_VERSION} release. This is NOT the merge gate.",
            file=sys.stderr,
        )
        return [bun, "run", str(cli)]

    return [str(ensure_pinned_agentforge())]


def _agentforge_platform() -> str:
    """Release asset suffix for the running machine."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64", "amd64": "x64"}.get(machine)
    if system not in {"darwin", "linux"} or arch is None:
        raise GenerationError(
            f"No pinned AgentForge binary for {system}/{machine}. "
            "Set AGENTFORGE_BIN to a compatible executable."
        )
    return f"{system}-{arch}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_pinned_agentforge() -> Path:
    """Return the pinned compiler, downloading it on first use.

    Cached under ``.cache/agentforge/<version>/`` and verified by sha256 on every
    resolution, not just on download -- a cached file that no longer matches the
    pin is replaced rather than trusted.
    """
    asset = _agentforge_platform()
    expected = AGENTFORGE_SHA256.get(asset)
    if expected is None:
        raise GenerationError(
            f"No pinned sha256 for agentforge-{asset} at v{AGENTFORGE_VERSION}. "
            "Set AGENTFORGE_BIN, or add the hash from the release's SHA256SUMS."
        )

    cached = AGENTFORGE_CACHE / AGENTFORGE_VERSION / f"agentforge-{asset}"
    if cached.is_file() and _sha256(cached) == expected:
        cached.chmod(0o755)
        return cached

    url = AGENTFORGE_RELEASE_URL.format(version=AGENTFORGE_VERSION, platform=asset)
    cached.parent.mkdir(parents=True, exist_ok=True)
    staged = cached.with_suffix(".partial")
    print(f"Fetching pinned AgentForge v{AGENTFORGE_VERSION} ({asset})...", file=sys.stderr)
    try:
        with urllib.request.urlopen(url) as response, staged.open("wb") as fh:  # noqa: S310
            shutil.copyfileobj(response, fh)
    except OSError as exc:
        staged.unlink(missing_ok=True)
        raise GenerationError(f"Could not download {url}: {exc}") from exc

    actual = _sha256(staged)
    if actual != expected:
        staged.unlink(missing_ok=True)
        raise GenerationError(
            f"Checksum mismatch for agentforge-{asset} v{AGENTFORGE_VERSION}:\n"
            f"  expected {expected}\n  actual   {actual}\n"
            "Refusing to execute unverified bytes."
        )

    staged.chmod(0o755)
    staged.replace(cached)
    return cached


def _resolve_executable(command: str) -> Path | None:
    resolved = shutil.which(command)
    if resolved is not None:
        return Path(resolved).resolve()
    candidate = Path(command).expanduser()
    if candidate.is_file() and os.access(candidate, os.X_OK):
        return candidate.resolve()
    return None

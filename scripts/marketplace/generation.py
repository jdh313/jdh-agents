"""AgentForge-backed native-manifest projection for cc-marketplace.

AgentForge owns deterministic publication compilation.  This module owns only
the repository-specific projection from those complete publications into the
native manifest paths consumed directly from this source tree.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

PINNED_AGENTFORGE_REVISION = "8a6b894d122daa78ca5e0c471ab2d3ebc100d451"

_ROOT_MANIFESTS = {
    Path("claude/.claude-plugin/marketplace.json"): Path(
        ".claude-plugin/marketplace.json"
    ),
    Path("codex/.agents/plugins/marketplace.json"): Path(
        ".agents/plugins/marketplace.json"
    ),
}


class GenerationError(RuntimeError):
    """Raised when AgentForge cannot produce the native manifest projection."""


@dataclass(frozen=True, order=True)
class ManifestDrift:
    """One difference between canonical compilation and committed output."""

    kind: str
    path: Path


@dataclass(frozen=True)
class NativeManifestCompilation:
    """The projected manifests and AgentForge's compatibility diagnostics."""

    manifests: dict[Path, bytes]
    stdout: str
    stderr: str


def compile_native_manifests(
    repo_root: Path,
    marketplace: Path,
) -> NativeManifestCompilation:
    """Compile with AgentForge and retain only native marketplace manifests."""

    command = _resolve_agentforge_command()
    with tempfile.TemporaryDirectory(prefix="cc-marketplace-agentforge-") as temporary:
        output_root = Path(temporary) / "compiled"
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
            raise GenerationError(
                f"AgentForge compile exited {result.returncode}{suffix}"
            )
        manifests = collect_native_manifests(output_root)
    return NativeManifestCompilation(manifests, result.stdout, result.stderr)


def collect_native_manifests(compilation_root: Path) -> dict[Path, bytes]:
    """Map complete AgentForge publications to repository native-manifest paths."""

    manifests: dict[Path, bytes] = {}
    missing_roots: list[str] = []
    for compiled_path, repository_path in _ROOT_MANIFESTS.items():
        source = compilation_root / compiled_path
        if not source.is_file():
            missing_roots.append(compiled_path.as_posix())
        else:
            manifests[repository_path] = source.read_bytes()
    if missing_roots:
        raise GenerationError(
            "AgentForge compilation omitted required root manifest(s): "
            + ", ".join(missing_roots)
        )

    projections = (
        ("claude", ".claude-plugin"),
        ("codex", ".codex-plugin"),
    )
    for publication, native_directory in projections:
        pattern = f"{publication}/plugins/*/{native_directory}/plugin.json"
        for source in sorted(compilation_root.glob(pattern)):
            package_name = source.parents[1].name
            destination = Path("plugins") / package_name / native_directory / "plugin.json"
            manifests[destination] = source.read_bytes()

    if not any(path.match("plugins/*/.claude-plugin/plugin.json") for path in manifests):
        raise GenerationError("AgentForge compilation produced no Claude package manifests")
    return dict(sorted(manifests.items()))


def compare_native_manifests(
    repo_root: Path,
    expected: dict[Path, bytes],
) -> list[ManifestDrift]:
    """Compare committed native manifests to compilation without writing files."""

    actual_paths = _existing_native_manifest_paths(repo_root)
    expected_paths = set(expected)
    issues = [
        ManifestDrift("missing", path) for path in sorted(expected_paths - actual_paths)
    ]
    issues.extend(ManifestDrift("extra", path) for path in sorted(actual_paths - expected_paths))
    issues.extend(
        ManifestDrift("changed", path)
        for path in sorted(actual_paths & expected_paths)
        if (repo_root / path).read_bytes() != expected[path]
    )
    return sorted(issues, key=lambda issue: (issue.path.as_posix(), issue.kind))


def materialize_native_manifests(
    repo_root: Path,
    expected: dict[Path, bytes],
) -> None:
    """Replace the exact generated manifest set, leaving source content in place."""

    actual_paths = _existing_native_manifest_paths(repo_root)
    for relative_path in sorted(actual_paths - set(expected)):
        target = repo_root / relative_path
        target.unlink()
        try:
            target.parent.rmdir()
        except OSError:
            pass

    for relative_path, content in sorted(expected.items()):
        target = repo_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def _existing_native_manifest_paths(repo_root: Path) -> set[Path]:
    paths: set[Path] = set()
    for relative_path in _ROOT_MANIFESTS.values():
        if (repo_root / relative_path).is_file():
            paths.add(relative_path)
    for pattern in (
        "plugins/*/.claude-plugin/plugin.json",
        "plugins/*/.codex-plugin/plugin.json",
    ):
        paths.update(path.relative_to(repo_root) for path in repo_root.glob(pattern))
    return paths


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

"""Test support for exercising AgentForge against the canonical marketplace."""

from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class TreeEntry:
    """One stable, content-aware entry in a generated filesystem tree."""

    path: str
    kind: str
    mode: int
    content: bytes | None


@dataclass(frozen=True)
class WriteObservation:
    """Write-sensitive metadata for one path in an existing output tree."""

    path: str
    kind: str
    mtime_ns: int | None
    ctime_ns: int | None


class AgentForgeCommandError(RuntimeError):
    """Raised when AgentForge cannot complete a requested operation."""


@dataclass(frozen=True)
class AgentForge:
    """Run either an installed AgentForge CLI or its source checkout."""

    marketplace: Path
    project: Path | None = None
    executable: Path | None = None

    def run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        if self.executable is not None:
            command = [str(self.executable), *arguments]
            working_directory = self.marketplace.parent
            missing_command = str(self.executable)
        elif self.project is not None:
            command = ["bun", "run", "src/cli.ts", *arguments]
            working_directory = self.project
            missing_command = "bun"
        else:
            raise AgentForgeCommandError(
                "AgentForge requires either an installed executable or a source checkout"
            )
        try:
            return subprocess.run(
                command,
                cwd=working_directory,
                check=False,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as error:
            raise AgentForgeCommandError(
                f"AgentForge acceptance tests could not execute `{missing_command}`"
            ) from error

    def compile(self, output_root: Path) -> subprocess.CompletedProcess[str]:
        result = self.run(
            "compile",
            str(self.marketplace),
            "--out",
            str(output_root),
        )
        if result.returncode != 0:
            raise AgentForgeCommandError(_command_failure("compile", result))
        return result

    def check(self, output_root: Path, *extra_arguments: str) -> subprocess.CompletedProcess[str]:
        return self.run(
            "check",
            str(self.marketplace),
            "--out",
            str(output_root),
            *extra_arguments,
        )


@contextmanager
def marketplace_without_root_manifest(marketplace: Path) -> Iterator[Path]:
    """Yield a throwaway marketplace root with root-manifest publication off.

    A publication that declares ``root-manifest`` forces ``--out`` to resolve
    inside the marketplace directory and writes its root copy beside
    ``MARKETPLACE.yaml``.  Tests that compile the corpus into a pytest tmpdir
    want neither: the first is rejected outright, and the second would overwrite
    the repository's committed root manifest from a test run.  Those tests cover
    corpus compilation and target translation, not root-manifest publication, so
    they compile an otherwise identical definition with the flag removed.

    AgentForge requires the definition to be named exactly ``MARKETPLACE.yaml``,
    so this is a whole directory rather than a sibling file.  ``plugins/`` is
    copied so the compiler's package and artifact globs resolve.
    """

    definition = yaml.safe_load(marketplace.read_text(encoding="utf-8"))
    for publication in definition.get("publications", []):
        publication.pop("root-manifest", None)

    source_root = marketplace.parent
    with tempfile.TemporaryDirectory(prefix="agentforge-no-root-manifest-") as temporary:
        root = Path(temporary)
        (root / marketplace.name).write_text(
            yaml.safe_dump(definition, sort_keys=False), encoding="utf-8"
        )
        # The package and artifact globs do not descend through symlinks at any
        # depth, so the corpus is copied rather than linked.  At ~2 MB it is
        # cheap; the callers hold the copy for a whole module where they can.
        shutil.copytree(source_root / "plugins", root / "plugins", symlinks=True)
        yield root / marketplace.name


def require_agentforge_project(repo_root: Path) -> Path:
    """Resolve and validate the explicitly configured AgentForge checkout."""

    configured = os.environ.get("AGENTFORGE_PROJECT")
    if not configured:
        raise RuntimeError(
            "AgentForge acceptance tests require AGENTFORGE_PROJECT to name a compatible "
            f"AgentForge checkout while testing {repo_root} "
            "(for example, AGENTFORGE_PROJECT=/path/to/agentforge)"
        )

    project = Path(configured).expanduser().resolve()
    required_paths = (project / "package.json", project / "src" / "cli.ts")
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        raise RuntimeError(
            f"AGENTFORGE_PROJECT is not an AgentForge source checkout: {project}; "
            f"missing {', '.join(missing)}"
        )
    if shutil.which("bun") is None:
        raise RuntimeError("AgentForge acceptance tests require `bun` on PATH")
    return project


def resolve_agentforge(repo_root: Path, marketplace: Path) -> AgentForge:
    """Prefer explicit configuration, then an installed CLI, then fail clearly."""

    configured_binary = os.environ.get("AGENTFORGE_BIN")
    if configured_binary:
        executable = _resolve_executable(configured_binary)
        if executable is None:
            raise RuntimeError(f"AGENTFORGE_BIN does not name an executable: {configured_binary}")
        return AgentForge(marketplace=marketplace, executable=executable)

    if os.environ.get("AGENTFORGE_PROJECT"):
        return AgentForge(
            marketplace=marketplace,
            project=require_agentforge_project(repo_root),
        )

    installed = shutil.which("agentforge")
    if installed:
        return AgentForge(marketplace=marketplace, executable=Path(installed).resolve())

    raise RuntimeError(
        "AgentForge acceptance tests require `agentforge` on PATH, AGENTFORGE_BIN, "
        "or AGENTFORGE_PROJECT"
    )


def _resolve_executable(command: str) -> Path | None:
    resolved = shutil.which(command)
    if resolved is not None:
        return Path(resolved).resolve()

    candidate = Path(command).expanduser()
    if candidate.is_file() and os.access(candidate, os.X_OK):
        return candidate.resolve()
    return None


def snapshot_tree(root: Path) -> tuple[TreeEntry, ...]:
    """Capture every generated path, type, normalized mode, and file byte."""

    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"cannot snapshot missing output directory: {root}")

    entries: list[TreeEntry] = []
    pending = [root]
    while pending:
        directory = pending.pop()
        for path in sorted(directory.iterdir(), key=lambda item: item.name, reverse=True):
            relative_path = path.relative_to(root).as_posix()
            metadata = path.lstat()
            mode = stat.S_IMODE(metadata.st_mode)

            if stat.S_ISLNK(metadata.st_mode):
                entries.append(
                    TreeEntry(relative_path, "symlink", mode, os.readlink(path).encode())
                )
            elif stat.S_ISDIR(metadata.st_mode):
                entries.append(TreeEntry(relative_path, "directory", mode, None))
                pending.append(path)
            elif stat.S_ISREG(metadata.st_mode):
                entries.append(TreeEntry(relative_path, "file", mode, path.read_bytes()))
            else:
                entries.append(
                    TreeEntry(
                        relative_path,
                        f"special:{stat.S_IFMT(metadata.st_mode):o}",
                        mode,
                        None,
                    )
                )

    return tuple(sorted(entries, key=lambda entry: entry.path))


def age_tree_mtimes(root: Path) -> None:
    """Give existing files and directories an old mtime before observing writes.

    Aging avoids missing a rewrite when a filesystem rounds closely spaced writes
    to the same timestamp. Directories are aged after their children so setup does
    not itself invalidate their final timestamp.
    """

    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"cannot age missing output directory: {root}")

    old_timestamp_ns = 946_684_800_000_000_000  # 2000-01-01T00:00:00Z
    paths = [root, *root.rglob("*")]
    for path in sorted(paths, key=lambda item: len(item.parts), reverse=True):
        metadata = path.lstat()
        if stat.S_ISREG(metadata.st_mode) or stat.S_ISDIR(metadata.st_mode):
            os.utime(path, ns=(old_timestamp_ns, old_timestamp_ns))


def snapshot_write_observations(root: Path) -> tuple[WriteObservation, ...]:
    """Capture metadata that changes when existing output is written or replaced."""

    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"cannot observe missing output directory: {root}")

    observations: list[WriteObservation] = []
    for path in (root, *root.rglob("*")):
        metadata = path.lstat()
        relative_path = "." if path == root else path.relative_to(root).as_posix()
        if stat.S_ISLNK(metadata.st_mode):
            kind = "symlink"
        elif stat.S_ISDIR(metadata.st_mode):
            kind = "directory"
        elif stat.S_ISREG(metadata.st_mode):
            kind = "file"
        else:
            kind = f"special:{stat.S_IFMT(metadata.st_mode):o}"
        observations.append(
            WriteObservation(
                path=relative_path,
                kind=kind,
                mtime_ns=getattr(metadata, "st_mtime_ns", None),
                ctime_ns=getattr(metadata, "st_ctime_ns", None),
            )
        )

    return tuple(sorted(observations, key=lambda observation: observation.path))


def _command_failure(operation: str, result: subprocess.CompletedProcess[str]) -> str:
    details = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    suffix = f"\n{details}" if details else ""
    return f"AgentForge {operation} exited {result.returncode}{suffix}"

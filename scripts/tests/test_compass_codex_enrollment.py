"""TEAM-344, bullet 1: `compass` must compile and validate for the Codex target.

`uv run marketplace check` must pass with Codex validation covering every
enrolled package, the compiled `plugins/compass/.codex-plugin/plugin.json`
must be a committed file alongside the regenerated registries, and a repeat
`sync` must leave the committed tree clean (which `check`'s `sync --check`
step already proves).

The enrolled count moved from seven to fourteen in TEAM-352, which enrolled the
remaining catalog. `langfuse` is the one package still absent, by decision
rather than by omission — see TEAM-350. The canonical enrolled set lives in
`test_agentforge_full_corpus.CODEX_PACKAGE_IDS`; this module asserts only the
count, because its subject is `compass`'s presence in a passing `check` run,
not the composition of the catalog.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from marketplace.__main__ import _build_parser, _cmd_check

from .test_agentforge_full_corpus import CODEX_PACKAGE_IDS

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_marketplace_check_passes_for_every_enrolled_codex_plugin(capsys) -> None:
    args = _build_parser().parse_args(["check"])

    returncode = _cmd_check(args)

    output = capsys.readouterr().out
    assert returncode == 0, output
    assert f"Codex validation passed ({len(CODEX_PACKAGE_IDS)} plugins)." in output


def test_compass_codex_plugin_manifest_is_committed() -> None:
    manifest = "marketplaces/codex/plugins/compass/.codex-plugin/plugin.json"
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", manifest],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, (
        f"{manifest} is not tracked in git: {result.stderr.strip()}"
    )

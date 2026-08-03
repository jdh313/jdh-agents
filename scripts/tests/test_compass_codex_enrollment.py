"""TEAM-344, bullet 1: `compass` must compile and validate for the Codex target.

`uv run marketplace check` must pass with Codex validation covering all seven
enrolled packages (the six accepted pilots plus `compass`), the compiled
`plugins/compass/.codex-plugin/plugin.json` must be a committed file
alongside the regenerated registries, and a repeat `sync` must leave the
committed tree clean (which `check`'s `sync --check` step already proves).

Today `compass` declares no `targets.codex` block in its `PACKAGE.yaml` and
is absent from the Codex publication's `enrollment.packages` in
`MARKETPLACE.yaml`, so Codex validation only covers the six existing pilots
and no `.codex-plugin/plugin.json` exists for `compass` at all.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from marketplace.__main__ import _build_parser, _cmd_check

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_marketplace_check_passes_with_seven_codex_plugins(capsys) -> None:
    args = _build_parser().parse_args(["check"])

    returncode = _cmd_check(args)

    output = capsys.readouterr().out
    assert returncode == 0, output
    assert "Codex validation passed (7 plugins)." in output


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

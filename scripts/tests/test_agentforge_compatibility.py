import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PORTABLE_ARGUMENT_SKILLS = (
    "plugins/craft/skills/design-by-stories/SKILL.md",
    "plugins/craft/skills/interrogate-model/SKILL.md",
    "plugins/librarian/skills/base-add/SKILL.md",
    "plugins/librarian/skills/note-capture/SKILL.md",
)


@pytest.mark.parametrize("relative_path", PORTABLE_ARGUMENT_SKILLS)
def test_codex_enrolled_argument_instructions_are_portable(relative_path: str) -> None:
    source = (REPO_ROOT / relative_path).read_text(encoding="utf-8")

    assert "$ARGUMENTS" not in source
    assert all(f"${index}" not in source for index in range(10))


# JUN-341, bullet 1: commit's PreToolUse guard must appear in generated Codex
# output, and the committed `.codex-plugin` baseline in this repo must reflect
# it. `manifest.hooks` is the field cc-marketplace's Codex validator already
# checks generically for any plugin (`codex_validate._validate_plugin` scans
# "skills", "mcpServers", "apps", "hooks"), so a translated hook configuration
# is expected to surface there, pointing at a materialized file.
#
# Today `plugins/commit/.codex-plugin/plugin.json` has no `hooks` field at
# all -- AgentForge's Codex target does not yet project hook artifacts, so
# there is nothing for this baseline to declare. This test fails against that
# gap; it is expected to pass once the baseline is regenerated against a
# compiler that projects `commit`'s hook.
def test_commit_codex_baseline_declares_its_translated_hook_configuration() -> None:
    manifest_path = REPO_ROOT / "plugins/commit/.codex-plugin/plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert "hooks" in manifest, (
        "commit's committed Codex baseline must declare its translated PreToolUse "
        "guard hook configuration"
    )
    declared = manifest["hooks"]
    paths = declared if isinstance(declared, list) else [declared]
    assert paths, "commit's Codex baseline hooks field must not be empty"
    for path_value in paths:
        assert isinstance(path_value, str) and path_value.startswith("./"), (
            f"commit's Codex baseline hooks path must be ./-prefixed, got {path_value!r}"
        )
        assert (manifest_path.parent.parent / path_value).is_file(), (
            f"commit's Codex baseline declares a hooks path that is not materialized: "
            f"{path_value}"
        )

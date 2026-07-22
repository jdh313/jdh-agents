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

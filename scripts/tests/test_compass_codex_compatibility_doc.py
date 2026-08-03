"""TEAM-344, bullet 4: `docs/agentforge-compatibility.md` must carry an
explicit disposition for every field the Codex compiler strips from compass's
three skills -- `argument-hint`, `allowed-tools`, and `effort` -- plus the
silently-dropped `disallowed-tools`, a field the "Codex compatibility" section
has no vocabulary for today (no other package entry mentions it either).

Today the doc's "## Codex compatibility" section has no `compass` entry at
all -- it only lists the six existing pilots (`commit`, `craft`, `feedback`,
`librarian`, `linear`, `spec-flow`).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOC_PATH = REPO_ROOT / "docs/agentforge-compatibility.md"

COMPASS_ENTRY = re.compile(r"^- `compass`:.*?(?=\n- `|\n\n)", re.DOTALL | re.MULTILINE)
REQUIRED_FIELD_MENTIONS = ("argument-hint", "allowed-tools", "effort", "disallowed-tools")


def test_compass_codex_entry_documents_disposition_for_every_stripped_field() -> None:
    doc_text = DOC_PATH.read_text(encoding="utf-8")

    match = COMPASS_ENTRY.search(doc_text)
    assert match is not None, (
        "docs/agentforge-compatibility.md has no `## Codex compatibility` entry for `compass` yet"
    )

    entry_text = match.group(0)
    missing = [field for field in REQUIRED_FIELD_MENTIONS if field not in entry_text]
    assert not missing, (
        f"compass's Codex compatibility entry does not mention: {', '.join(missing)}"
    )

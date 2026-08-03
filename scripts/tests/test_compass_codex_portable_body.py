"""JUN-344, bullet 2: compass's skill bodies must name intent, not Claude tool
identifiers, so its Codex enrollment declares zero `targets.codex.losses` and
needs no `targets.codex.body` override -- and reflect/mull must state their
"never research, never delegate" boundary in body prose, not just imply it
through frontmatter `disallowed-tools`.

Today all three skill bodies interpolate `$ARGUMENTS` and name `mcp__*` tool
identifiers directly (see `references/*.md` and the "Method" sections), and
neither `reflect` nor `mull` states a no-research/no-delegate boundary as
prose -- their bodies only offer a hand-off to `mull`/`converge`, they never
say outright that they will not research or delegate themselves.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPASS_SKILLS = ("converge", "mull", "reflect")

# Deliberately loose: any phrasing that plainly denies research/delegation in
# prose satisfies the bullet. This is the narrowest assumption we could make
# about wording the implementer has not chosen yet.
NO_RESEARCH_BOUNDARY = re.compile(
    r"never\s+research|does\s+not\s+research|won.t\s+research|no\s+(?:web\s+)?research",
    re.IGNORECASE,
)
NO_DELEGATE_BOUNDARY = re.compile(
    r"never\s+delegat\w*|does\s+not\s+delegat\w*|won.t\s+delegat\w*|no\s+delegat\w*",
    re.IGNORECASE,
)


def _skill_body(skill_name: str) -> str:
    path = REPO_ROOT / "plugins/compass/skills" / skill_name / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    _, _, body = text.split("---", 2)
    return body


@pytest.mark.parametrize("skill_name", COMPASS_SKILLS)
def test_compass_skill_body_names_intent_not_tool_identifiers(skill_name: str) -> None:
    body = _skill_body(skill_name)

    assert "$ARGUMENTS" not in body, (
        f"compass/{skill_name}'s body still interpolates $ARGUMENTS instead of naming intent"
    )
    assert "mcp__" not in body, (
        f"compass/{skill_name}'s body still names an mcp__* tool identifier instead of intent"
    )


def test_compass_package_declares_zero_codex_losses_and_no_body_override() -> None:
    package = yaml.safe_load(
        (REPO_ROOT / "plugins/compass/PACKAGE.yaml").read_text(encoding="utf-8")
    )

    targets = package.get("targets") or {}
    assert "codex" in targets, "compass PACKAGE.yaml has no targets.codex block yet"

    codex_target = targets["codex"] or {}
    assert "losses" not in codex_target, (
        "compass should declare zero targets.codex.losses: its skill bodies name intent, "
        "not tool identifiers, so there is nothing to declare"
    )
    assert "body" not in codex_target, (
        "compass should need no targets.codex.body override once bodies are portable"
    )


@pytest.mark.parametrize("skill_name", ("reflect", "mull"))
def test_stance_states_no_research_no_delegate_boundary_in_prose(skill_name: str) -> None:
    body = _skill_body(skill_name)

    assert NO_RESEARCH_BOUNDARY.search(body), (
        f"compass/{skill_name}'s body prose does not state an explicit no-research boundary"
    )
    assert NO_DELEGATE_BOUNDARY.search(body), (
        f"compass/{skill_name}'s body prose does not state an explicit no-delegate boundary"
    )

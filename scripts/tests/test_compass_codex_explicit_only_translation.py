"""TEAM-344, bullet 3: AgentForge must generate a Codex `agents/openai.yaml`
sidecar carrying `policy: allow_implicit_invocation: false` for all three
compass skills. This is a faithful translation of `disable-model-invocation:
true`, not a loss, so compass's Codex enrollment takes no declared-loss entry
for it.

Today `compass` is not enrolled for the Codex target at all, so compiling the
canonical marketplace never materializes `codex/plugins/compass/...` and none
of the three sidecars exist.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.agentforge_harness import marketplace_without_root_manifest, resolve_agentforge

REPO_ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = REPO_ROOT / "MARKETPLACE.yaml"
COMPASS_SKILLS = ("converge", "mull", "reflect")

ALLOW_IMPLICIT_INVOCATION_FALSE = re.compile(
    r"(?m)^policy:\s*$\n^  allow_implicit_invocation:\s*false\s*$",
)


def test_compass_skills_each_get_a_codex_explicit_only_policy_sidecar(tmp_path: Path) -> None:
    with marketplace_without_root_manifest(MARKETPLACE) as definition:
        agentforge = resolve_agentforge(REPO_ROOT, definition)
        output_root = tmp_path / "compiled"

        result = agentforge.compile(output_root)

    diagnostics = result.stdout + result.stderr
    assert "[codex/compass] declared-loss" not in diagnostics, (
        "compass's explicit-only skill translation must not declare a loss: "
        "Codex omits these skills from the model context and keeps them "
        "invocable from the $-picker"
    )

    for skill_name in COMPASS_SKILLS:
        policy_path = (
            output_root
            / "codex"
            / "plugins"
            / "compass"
            / "skills"
            / skill_name
            / "agents"
            / "openai.yaml"
        )
        assert policy_path.is_file(), (
            f"compass/{skill_name} has no Codex explicit-only policy sidecar -- "
            "compass is not yet enrolled for the Codex target"
        )
        policy = policy_path.read_text(encoding="utf-8")
        assert ALLOW_IMPLICIT_INVOCATION_FALSE.search(policy), (
            f"compass/{skill_name}'s Codex policy sidecar does not set "
            "policy.allow_implicit_invocation: false"
        )

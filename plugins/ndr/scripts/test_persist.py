#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0", "pytest>=8.0"]
# ///
"""Unit tests for persist.py.

Run with:
    uv run pytest plugins/ndr/scripts/test_persist.py -v

All tests use pytest tmp_path fixtures — never touches the real vault.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

# Make persist importable as a sibling module.
sys.path.insert(0, str(Path(__file__).parent))
import persist  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    """Build a fresh vault Decisions/ directory with a starter taxonomy."""
    decisions = tmp_path / "Decisions"
    decisions.mkdir()
    taxonomy = decisions / ".taxonomy"
    taxonomy.mkdir()
    (taxonomy / "areas.yaml").write_text(
        "- process\n- tooling\n- scope\n- substrate\n"
    )
    (taxonomy / "topics.yaml").write_text(
        "- substrate\n- read-side\n- write-side\n- granularity\n- mvp-scope\n"
    )
    return decisions


def make_draft(
    title: str = "Use FastAPI for auth",
    area: str = "tooling",
    topic: str = "substrate",
    supersedes: list[str] | None = None,
    aliases: list[str] | None = None,
    body: str | None = None,
) -> dict[str, Any]:
    body = body or (
        "# PLACEHOLDER — " + title + "\n\n"
        "## Decision\n\n" + title + ".\n\n"
        "## Why\n\nAsync without rewriting the ORM layer.\n\n"
        "> [!info]- Full reasoning\n> Pydantic v2 lands as a useful transitive.\n"
    )
    return {
        "frontmatter": {
            "id": "PLACEHOLDER",
            "title": title,
            "status": "current",
            "decision_date": "2026-05-15",
            "aliases": aliases or [],
            "project": "[[Auth Rewrite]]",
            "derived_from": [],
            "informed_by": [],
            "supersedes": supersedes or [],
            "superseded_by": [],
            "area": area,
            "topic": topic,
            "impacts": [],
            "revisit_triggers": [],
            "reversibility": "medium",
            "tags": ["decision"],
        },
        "body": body,
    }


def read_atom(path: Path) -> tuple[dict[str, Any], str]:
    return persist.split_frontmatter(path.read_text())


# ---------------------------------------------------------------------------
# Clean writes
# ---------------------------------------------------------------------------


def test_clean_write_assigns_id_starting_at_0001(vault: Path) -> None:
    payload = {"vault_decisions": str(vault), "drafts": [make_draft()]}
    result, code = persist.run(payload)

    assert code == 0
    assert result["written"][0]["id"] == "0001"
    assert result["written"][0]["path"] == "Decisions/0001-use-fastapi-for-auth.md"
    assert result["errors"] == []

    written = vault / "0001-use-fastapi-for-auth.md"
    assert written.exists()
    fm, body = read_atom(written)
    assert fm["id"] == "0001"
    assert "# 0001 — Use FastAPI for auth" in body


def test_clean_write_increments_past_existing_ids(vault: Path) -> None:
    # Seed a couple existing atoms (file + directory form to exercise both).
    (vault / "0007-existing.md").write_text("---\nid: \"0007\"\n---\nbody\n")
    (vault / "0009-existing-dir").mkdir()
    payload = {"vault_decisions": str(vault), "drafts": [make_draft()]}
    result, code = persist.run(payload)
    assert code == 0
    assert result["written"][0]["id"] == "0010"


def test_multiple_drafts_get_sequential_ids(vault: Path) -> None:
    payload = {
        "vault_decisions": str(vault),
        "drafts": [
            make_draft(title="Decision A"),
            make_draft(title="Decision B"),
        ],
    }
    result, code = persist.run(payload)
    assert code == 0
    assert [w["id"] for w in result["written"]] == ["0001", "0002"]


# ---------------------------------------------------------------------------
# Supersession
# ---------------------------------------------------------------------------


def seed_predecessor(
    vault: Path,
    atom_id: str = "0001",
    title: str = "Use Flask for auth",
    aliases: list[str] | None = None,
) -> Path:
    slug = persist.kebab(title)
    filename = f"{atom_id}-{slug}.md"
    fm = {
        "id": atom_id,
        "title": title,
        "status": "current",
        "decision_date": "2026-04-01",
        "aliases": aliases or [],
        "project": "[[Auth Rewrite]]",
        "derived_from": [],
        "informed_by": [],
        "supersedes": [],
        "superseded_by": [],
        "area": "tooling",
        "topic": "substrate",
        "impacts": [],
        "revisit_triggers": [],
        "reversibility": "medium",
        "tags": ["decision"],
    }
    body = f"# {atom_id} — {title}\n\n## Decision\n\n{title}.\n"
    text = persist.join_frontmatter(fm, body)
    p = vault / filename
    p.write_text(text)
    return p


def test_supersession_without_aliases(vault: Path) -> None:
    pred = seed_predecessor(vault, "0001", "Use Flask for auth")
    pred_link = f"[[Decisions/{pred.stem}]]"
    payload = {
        "vault_decisions": str(vault),
        "drafts": [make_draft(supersedes=[pred_link])],
    }
    result, code = persist.run(payload)
    assert code == 0, result
    assert result["aliases_moved"] == []
    assert result["superseded"][0]["id"] == "0001"

    pred_fm, _ = read_atom(pred)
    assert pred_fm["status"] == "superseded"
    successor_link = f"[[Decisions/{result['written'][0]['path'].split('/')[1][:-3]}]]"
    assert successor_link in pred_fm["superseded_by"]
    assert pred_fm["aliases"] == []


def test_supersession_with_alias_handover(vault: Path) -> None:
    pred = seed_predecessor(
        vault, "0011", "Monorepo symmetric apps", aliases=["ndr-monorepo-shape"]
    )
    pred_link = f"[[Decisions/{pred.stem}]]"
    payload = {
        "vault_decisions": str(vault),
        "drafts": [
            make_draft(
                title="Split apps into services",
                supersedes=[pred_link],
            )
        ],
    }
    result, code = persist.run(payload)
    assert code == 0, result

    moved = result["aliases_moved"]
    assert len(moved) == 1
    assert moved[0]["slug"] == "ndr-monorepo-shape"
    assert moved[0]["from"] == "0011"
    assert moved[0]["to"] == result["written"][0]["id"]

    pred_fm, _ = read_atom(pred)
    assert pred_fm["aliases"] == []
    assert pred_fm["status"] == "superseded"

    successor = vault / result["written"][0]["path"].split("/", 1)[1]
    succ_fm, _ = read_atom(successor)
    assert "ndr-monorepo-shape" in succ_fm["aliases"]


def test_already_superseded_by_other_atom_is_refused(vault: Path) -> None:
    pred = seed_predecessor(vault, "0001", "Use Flask for auth")
    pred_fm, pred_body = read_atom(pred)
    pred_fm["status"] = "superseded"
    pred_fm["superseded_by"] = ["[[Decisions/0050-some-other-successor]]"]
    pred.write_text(persist.join_frontmatter(pred_fm, pred_body))

    pred_link = f"[[Decisions/{pred.stem}]]"
    payload = {
        "vault_decisions": str(vault),
        "drafts": [make_draft(supersedes=[pred_link])],
    }
    result, code = persist.run(payload)
    assert code == 2
    assert any(
        e.get("kind") == "supersession_conflict" for e in result["errors"]
    ), result
    # Half-state report: successor was written before the conflict was detected.
    assert len(result["written"]) == 1


def test_mid_transaction_failure_reports_half_state(vault: Path) -> None:
    # Supersedes a predecessor that does not exist on disk → patch fails after
    # successor lands. Persist must report the half-state and exit 3.
    payload = {
        "vault_decisions": str(vault),
        "drafts": [
            make_draft(
                supersedes=["[[Decisions/9999-does-not-exist]]"],
            )
        ],
    }
    result, code = persist.run(payload)
    assert code == 3
    assert len(result["written"]) == 1, "successor should have been written"
    assert any(e.get("kind") == "patch_failure" for e in result["errors"])
    err = next(e for e in result["errors"] if e.get("kind") == "patch_failure")
    assert "half_state" in err
    assert err["half_state"]["successor_written"].startswith("Decisions/")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def test_taxonomy_violation_blocks_all_writes(vault: Path) -> None:
    bad = make_draft(area="not-a-real-area")
    good = make_draft(title="Good one")
    payload = {"vault_decisions": str(vault), "drafts": [good, bad]}
    result, code = persist.run(payload)
    assert code == 1
    assert any(
        "area `not-a-real-area`" in msg
        for e in result["errors"]
        if e.get("kind") == "validation"
        for msg in e.get("messages", [])
    )
    # Crucially: nothing was written. Validation happens first.
    assert list(vault.glob("*.md")) == []


def test_missing_required_field_blocks(vault: Path) -> None:
    draft = make_draft()
    draft["frontmatter"]["project"] = None
    payload = {"vault_decisions": str(vault), "drafts": [draft]}
    result, code = persist.run(payload)
    assert code == 1
    msgs = [
        msg
        for e in result["errors"]
        if e.get("kind") == "validation"
        for msg in e.get("messages", [])
    ]
    assert any("project" in m for m in msgs)


def test_missing_supersedes_field_blocks(vault: Path) -> None:
    draft = make_draft()
    del draft["frontmatter"]["supersedes"]
    payload = {"vault_decisions": str(vault), "drafts": [draft]}
    result, code = persist.run(payload)
    assert code == 1
    msgs = [
        msg
        for e in result["errors"]
        if e.get("kind") == "validation"
        for msg in e.get("messages", [])
    ]
    assert any("supersedes" in m for m in msgs)


def test_alias_without_ndr_prefix_blocks(vault: Path) -> None:
    draft = make_draft(aliases=["monorepo-shape"])  # missing ndr- prefix
    payload = {"vault_decisions": str(vault), "drafts": [draft]}
    result, code = persist.run(payload)
    assert code == 1


def test_invalid_status_blocks(vault: Path) -> None:
    draft = make_draft()
    draft["frontmatter"]["status"] = "draft"  # not allowed
    payload = {"vault_decisions": str(vault), "drafts": [draft]}
    result, code = persist.run(payload)
    assert code == 1


# ---------------------------------------------------------------------------
# Frontmatter parsing helpers
# ---------------------------------------------------------------------------


def test_kebab_handles_punctuation_and_spacing() -> None:
    assert persist.kebab("  Use FastAPI for the auth service! ") == "use-fastapi-for-the-auth-service"
    assert persist.kebab("Postgres / Redis decision") == "postgres-redis-decision"


def test_parse_decision_wikilink() -> None:
    assert persist.parse_decision_wikilink("[[Decisions/0042-foo-bar]]") == (
        "0042",
        "0042-foo-bar",
    )
    assert persist.parse_decision_wikilink("not a link") is None

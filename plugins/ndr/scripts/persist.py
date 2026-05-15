#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
persist.py — deterministic persistence for NDR decision atoms.

Reads structured drafts (from ndr-drafter) on stdin as JSON, validates them
against the on-disk taxonomy, assigns IDs, writes atoms to the vault, and
handles supersession (three-write with alias handover) atomically.

No LLM in the loop. No prose generation. This is the only path that touches
disk in the capture pipeline.

Input shape (stdin JSON):
{
  "vault_decisions": "~/Loose Ends/Decisions",          // optional; default
  "drafts": [
    {
      "frontmatter": {... full atom frontmatter ...},
      "body": "...atom body markdown...",
      "supersedes": ["[[Decisions/0042-use-fastapi-for-auth]]"]  // optional; overrides frontmatter.supersedes if present
    }
  ]
}

Output shape (stdout JSON):
{
  "written": [{"id": "0052", "path": "Decisions/0052-...", "title": "..."}],
  "superseded": [{"id": "0031", "path": "Decisions/0031-...", "by": "0052"}],
  "aliases_moved": [{"slug": "ndr-monorepo-shape", "from": "0031", "to": "0052"}],
  "errors": []
}

Exit codes:
  0 = success
  1 = validation error (taxonomy, missing required fields, malformed input)
  2 = supersession conflict (predecessor already superseded by a different successor)
  3 = mid-transaction failure (half-state; details in "errors")
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


REQUIRED_FIELDS = [
    "title",
    "status",
    "decision_date",
    "project",
    "area",
    "topic",
    "reversibility",
]
SUPERSEDES_FIELD = "supersedes"
VALID_STATUS = {"current", "superseded", "retracted"}
VALID_REVERSIBILITY = {"easy", "medium", "hard"}
ID_FILE_PATTERN = re.compile(r"^(\d{4})-.*\.md$")
ID_DIR_PATTERN = re.compile(r"^(\d{4})-.*$")
WIKILINK_DECISION_PATTERN = re.compile(r"\[\[Decisions/(\d{4})-([^\]]+)\]\]")


@dataclass
class Plan:
    vault_decisions: Path
    taxonomy_areas: list[str]
    taxonomy_topics: list[str]
    next_id_counter: int
    written: list[dict[str, str]] = field(default_factory=list)
    superseded: list[dict[str, str]] = field(default_factory=list)
    aliases_moved: list[dict[str, str]] = field(default_factory=list)
    errors: list[dict[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------------


def expand_path(value: str | Path) -> Path:
    return Path(os.path.expanduser(str(value)))


def load_taxonomy(decisions_path: Path) -> tuple[list[str], list[str]]:
    taxonomy_dir = decisions_path / ".taxonomy"
    areas_file = taxonomy_dir / "areas.yaml"
    topics_file = taxonomy_dir / "topics.yaml"
    if not areas_file.exists():
        raise FileNotFoundError(f"Taxonomy file missing: {areas_file}")
    if not topics_file.exists():
        raise FileNotFoundError(f"Taxonomy file missing: {topics_file}")
    areas = yaml.safe_load(areas_file.read_text()) or []
    topics = yaml.safe_load(topics_file.read_text()) or []
    if not isinstance(areas, list) or not isinstance(topics, list):
        raise ValueError("Taxonomy files must be YAML lists.")
    return areas, topics


def list_existing_ids(decisions_path: Path) -> list[int]:
    ids: list[int] = []
    if not decisions_path.exists():
        return ids
    for entry in decisions_path.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.is_file():
            m = ID_FILE_PATTERN.match(entry.name)
        elif entry.is_dir():
            m = ID_DIR_PATTERN.match(entry.name)
        else:
            m = None
        if m:
            ids.append(int(m.group(1)))
    return ids


def format_id(n: int) -> str:
    return f"{n:04d}"


def kebab(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s\-]+", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    s = re.sub(r"-+", "-", s)
    return s


def parse_decision_wikilink(link: str) -> tuple[str, str] | None:
    """Parse `[[Decisions/0042-slug]]` → ("0042", "0042-slug")."""
    m = WIKILINK_DECISION_PATTERN.match(link.strip())
    if not m:
        return None
    return m.group(1), f"{m.group(1)}-{m.group(2)}"


def find_decision_file(decisions_path: Path, atom_id: str) -> Path | None:
    for entry in decisions_path.iterdir():
        if entry.is_file() and entry.name.startswith(f"{atom_id}-") and entry.suffix == ".md":
            return entry
    return None


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a markdown file into (frontmatter dict, body string)."""
    if not text.startswith("---\n"):
        raise ValueError("File does not start with YAML frontmatter delimiter.")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("Frontmatter end delimiter not found.")
    fm_text = text[4:end]
    body = text[end + 5 :]
    fm = yaml.safe_load(fm_text) or {}
    if not isinstance(fm, dict):
        raise ValueError("Frontmatter did not parse as a mapping.")
    return fm, body


def join_frontmatter(fm: dict[str, Any], body: str) -> str:
    fm_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=False, default_flow_style=False)
    return f"---\n{fm_text}---\n{body}"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_draft(
    draft: dict[str, Any],
    index: int,
    taxonomy_areas: list[str],
    taxonomy_topics: list[str],
) -> list[str]:
    """Return a list of error strings; empty list means valid."""
    errors: list[str] = []
    fm = draft.get("frontmatter")
    body = draft.get("body")
    if not isinstance(fm, dict):
        errors.append(f"draft[{index}]: frontmatter must be an object")
        return errors
    if not isinstance(body, str) or not body.strip():
        errors.append(f"draft[{index}]: body must be a non-empty string")

    for fld in REQUIRED_FIELDS:
        v = fm.get(fld)
        if v is None or (isinstance(v, str) and not v.strip()):
            errors.append(f"draft[{index}]: required field `{fld}` is missing or empty")

    if SUPERSEDES_FIELD not in fm:
        errors.append(f"draft[{index}]: `supersedes` must be present (may be [])")

    status = fm.get("status")
    if status is not None and status not in VALID_STATUS:
        errors.append(f"draft[{index}]: status `{status}` not in {sorted(VALID_STATUS)}")

    rev = fm.get("reversibility")
    if rev is not None and rev not in VALID_REVERSIBILITY:
        errors.append(
            f"draft[{index}]: reversibility `{rev}` not in {sorted(VALID_REVERSIBILITY)}"
        )

    area = fm.get("area")
    if area is not None and area not in taxonomy_areas:
        errors.append(
            f"draft[{index}]: area `{area}` not in taxonomy areas {taxonomy_areas}"
        )

    topic = fm.get("topic")
    if topic is not None and topic not in taxonomy_topics:
        errors.append(
            f"draft[{index}]: topic `{topic}` not in taxonomy topics {taxonomy_topics}"
        )

    aliases = fm.get("aliases", [])
    if not isinstance(aliases, list):
        errors.append(f"draft[{index}]: aliases must be a list")
    else:
        for a in aliases:
            if not isinstance(a, str) or not a.startswith("ndr-"):
                errors.append(
                    f"draft[{index}]: alias `{a}` must be a string with `ndr-` prefix"
                )

    return errors


# ---------------------------------------------------------------------------
# Core write logic
# ---------------------------------------------------------------------------


def write_atom(plan: Plan, draft: dict[str, Any]) -> dict[str, Any]:
    """Allocate id, render file, write to disk. Returns the written record."""
    atom_id = format_id(plan.next_id_counter)
    plan.next_id_counter += 1

    fm = dict(draft["frontmatter"])
    body = draft["body"]
    title = fm["title"]

    fm["id"] = atom_id
    slug_part = kebab(title)
    filename = f"{atom_id}-{slug_part}.md"

    # Patch body placeholders. The drafter uses literal "PLACEHOLDER" in both
    # the H1 heading and frontmatter id; replace just those occurrences.
    body = body.replace("# PLACEHOLDER —", f"# {atom_id} —")
    body = body.replace("# PLACEHOLDER -", f"# {atom_id} -")

    content = join_frontmatter(fm, body)
    out_path = plan.vault_decisions / filename
    if out_path.exists():
        raise FileExistsError(f"Target already exists: {out_path}")
    out_path.write_text(content)

    record = {"id": atom_id, "path": f"Decisions/{filename}", "title": title}
    plan.written.append(record)
    return record


def patch_predecessor(
    plan: Plan,
    predecessor_link: str,
    successor_id: str,
    successor_filename: str,
    successor_fm: dict[str, Any],
    successor_path: Path,
) -> None:
    """Three-write supersession: flip status, append back-pointer, move aliases."""
    parsed = parse_decision_wikilink(predecessor_link)
    if not parsed:
        raise ValueError(
            f"supersedes entry `{predecessor_link}` is not a recognizable wikilink"
        )
    pred_id, _ = parsed
    pred_file = find_decision_file(plan.vault_decisions, pred_id)
    if pred_file is None:
        raise FileNotFoundError(f"Predecessor atom file not found for id {pred_id}")

    pred_text = pred_file.read_text()
    pred_fm, pred_body = split_frontmatter(pred_text)

    pred_status = pred_fm.get("status", "current")
    pred_superseded_by = pred_fm.get("superseded_by") or []
    if not isinstance(pred_superseded_by, list):
        raise ValueError(f"{pred_file.name}: superseded_by is not a list")

    successor_wikilink = f"[[Decisions/{successor_filename[:-3]}]]"

    if pred_status == "superseded":
        # already superseded — only OK if by THIS same successor (idempotent)
        if successor_wikilink not in pred_superseded_by:
            raise SupersessionConflict(
                f"Predecessor {pred_file.name} is already `superseded` by "
                f"{pred_superseded_by!r}; refusing to add a competing successor."
            )

    pred_aliases = pred_fm.get("aliases") or []
    moved_slugs: list[str] = []
    if pred_aliases:
        successor_aliases = list(successor_fm.get("aliases") or [])
        for slug in pred_aliases:
            if slug not in successor_aliases:
                successor_aliases.append(slug)
            moved_slugs.append(slug)
        successor_fm["aliases"] = successor_aliases
        # rewrite successor file with merged aliases
        successor_text = join_frontmatter(successor_fm, _strip_frontmatter(successor_path))
        successor_path.write_text(successor_text)

    pred_fm["status"] = "superseded"
    if successor_wikilink not in pred_superseded_by:
        pred_superseded_by.append(successor_wikilink)
    pred_fm["superseded_by"] = pred_superseded_by
    if pred_aliases:
        pred_fm["aliases"] = []
    pred_file.write_text(join_frontmatter(pred_fm, pred_body))

    plan.superseded.append(
        {"id": pred_id, "path": f"Decisions/{pred_file.name}", "by": successor_id}
    )
    for slug in moved_slugs:
        plan.aliases_moved.append(
            {"slug": slug, "from": pred_id, "to": successor_id}
        )


def _strip_frontmatter(path: Path) -> str:
    """Return only the body portion of an on-disk atom."""
    _, body = split_frontmatter(path.read_text())
    return body


class SupersessionConflict(Exception):
    pass


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def run(payload: dict[str, Any]) -> tuple[dict[str, Any], int]:
    vault_decisions = expand_path(
        payload.get("vault_decisions", "~/Loose Ends/Decisions")
    )
    if not vault_decisions.exists():
        return (
            {"errors": [{"kind": "missing_vault", "path": str(vault_decisions)}]},
            1,
        )

    areas, topics = load_taxonomy(vault_decisions)
    drafts = payload.get("drafts", [])
    if not isinstance(drafts, list) or not drafts:
        return ({"errors": [{"kind": "no_drafts"}]}, 1)

    # validate all drafts before writing any
    validation_errors: list[str] = []
    for idx, draft in enumerate(drafts):
        validation_errors.extend(validate_draft(draft, idx, areas, topics))
    if validation_errors:
        return (
            {
                "written": [],
                "superseded": [],
                "aliases_moved": [],
                "errors": [{"kind": "validation", "messages": validation_errors}],
            },
            1,
        )

    existing = list_existing_ids(vault_decisions)
    next_id = (max(existing) + 1) if existing else 1
    plan = Plan(
        vault_decisions=vault_decisions,
        taxonomy_areas=areas,
        taxonomy_topics=topics,
        next_id_counter=next_id,
    )

    for idx, draft in enumerate(drafts):
        try:
            record = write_atom(plan, draft)
        except Exception as exc:  # noqa: BLE001 — surfacing message
            plan.errors.append(
                {"kind": "write_failure", "draft_index": str(idx), "message": str(exc)}
            )
            return (
                {
                    "written": plan.written,
                    "superseded": plan.superseded,
                    "aliases_moved": plan.aliases_moved,
                    "errors": plan.errors,
                },
                3,
            )

        supersedes_links = draft.get("supersedes") or draft["frontmatter"].get(
            "supersedes"
        ) or []
        if not supersedes_links:
            continue

        successor_path = vault_decisions / record["path"].split("/", 1)[1]
        successor_fm = dict(draft["frontmatter"])
        successor_fm["id"] = record["id"]

        for pred_link in supersedes_links:
            try:
                patch_predecessor(
                    plan,
                    pred_link,
                    record["id"],
                    successor_path.name,
                    successor_fm,
                    successor_path,
                )
            except SupersessionConflict as exc:
                plan.errors.append(
                    {
                        "kind": "supersession_conflict",
                        "draft_index": str(idx),
                        "predecessor": pred_link,
                        "message": str(exc),
                    }
                )
                return (
                    {
                        "written": plan.written,
                        "superseded": plan.superseded,
                        "aliases_moved": plan.aliases_moved,
                        "errors": plan.errors,
                    },
                    2,
                )
            except Exception as exc:  # noqa: BLE001
                plan.errors.append(
                    {
                        "kind": "patch_failure",
                        "draft_index": str(idx),
                        "predecessor": pred_link,
                        "message": str(exc),
                        "half_state": {
                            "successor_written": record["path"],
                            "aliases_moved_so_far": list(plan.aliases_moved),
                            "patched_so_far": list(plan.superseded),
                        },
                    }
                )
                return (
                    {
                        "written": plan.written,
                        "superseded": plan.superseded,
                        "aliases_moved": plan.aliases_moved,
                        "errors": plan.errors,
                    },
                    3,
                )

    return (
        {
            "written": plan.written,
            "superseded": plan.superseded,
            "aliases_moved": plan.aliases_moved,
            "errors": [],
        },
        0,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Persist NDR decision atoms.")
    parser.add_argument(
        "--input",
        help="Path to JSON input file. If omitted, read JSON from stdin.",
        default=None,
    )
    args = parser.parse_args(argv)

    if args.input:
        raw = Path(args.input).read_text()
    else:
        raw = sys.stdin.read()

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        json.dump({"errors": [{"kind": "bad_json", "message": str(exc)}]}, sys.stdout)
        sys.stdout.write("\n")
        return 1

    result, exit_code = run(payload)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

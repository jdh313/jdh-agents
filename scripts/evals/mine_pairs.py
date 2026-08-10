#!/usr/bin/env python3
"""Mine (utterance -> skill) routing pairs from local transcripts into Langfuse.

Reads Claude Code session transcripts under ``~/.claude/projects/``, pairs each
``Skill`` tool call with the user turn that triggered it, and pushes the result
as a Langfuse dataset for human labeling.

Only *inferred* invocations are routing signal — see
``transcripts.SkillInvocation``. A typed ``/plugin:skill`` never emits a Skill
call, so in practice every mined pair qualifies.

This is private eval tooling. It is NOT part of the introspect plugin and is
never compiled into ``marketplaces/``; it only borrows the plugin's shared
parsing so the miner and the shipped reports agree on what a prompt is.

Credentials come from 1Password at runtime (item "Langfuse Code Agent API",
fields public-key / secret-key / base-url) so nothing lands in a dotfile.

Usage::

    uv run scripts/evals/mine_pairs.py --dry-run       # print, push nothing
    uv run scripts/evals/mine_pairs.py                 # push to Langfuse
    uv run scripts/evals/mine_pairs.py --per-skill 3   # tighter sampling

Note: utterances are your own prompts and may contain anything you typed,
including secrets. They go only to the self-hosted instance the langfuse
plugin already streams full prompts to.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "plugins" / "introspect" / "shared"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _langfuse import api  # noqa: E402
from transcripts import (  # noqa: E402
    build_skill_alias,
    find_transcripts,
    iter_skill_invocations,
)

DATASET = "skill-routing"
# Utterances shorter than this are almost always "yes" / "go" / "continue" —
# real turns, but they carry no routing signal a description could match.
MIN_UTTERANCE_CHARS = 25


def collect(per_skill: int) -> list[dict]:
    """Mine every transcript, then sample at most ``per_skill`` cases per skill.

    Sampling matters: ``commit:commit`` alone accounts for a fifth of all pairs,
    and a dataset dominated by one skill measures that skill, not the routing.
    Utterances are deduplicated per skill so repeated phrasings of the same ask
    ("commit this") do not consume the whole quota.
    """
    rows = []
    for path in find_transcripts(Path.home() / ".claude" / "projects", scan_all=True):
        rows.extend(iter_skill_invocations(path))

    alias = build_skill_alias({r.skill for r in rows})
    by_skill: dict[str, list] = defaultdict(list)
    for r in rows:
        if r.trigger != "inferred":
            continue
        text = " ".join(r.utterance.split())
        if len(text) < MIN_UTTERANCE_CHARS:
            continue
        skill = alias.get(r.skill, r.skill)
        seen = {" ".join(x["input"].split()).lower() for x in by_skill[skill]}
        if text.lower() in seen:
            continue
        by_skill[skill].append(
            {
                "input": text,
                "expected": skill,
                "session": r.session,
                "ts": r.ts.isoformat() if r.ts else None,
            }
        )

    items = []
    for skill, cases in sorted(by_skill.items()):
        # Longest-first: a fuller utterance gives the judge more to route on
        # than the terse restatements that follow it in a session.
        cases.sort(key=lambda c: len(c["input"]), reverse=True)
        items.extend(cases[:per_skill])
    return items


def push(items: list[dict]) -> None:
    """Create the dataset (idempotent) and upload every item."""
    api(
        "/api/public/datasets",
        {
            "name": DATASET,
            "description": (
                "Utterance -> skill routing cases mined from local Claude Code "
                "transcripts. expectedOutput is what actually fired, NOT ground "
                "truth — correct it in Human Annotation before scoring."
            ),
        },
    )
    for i, item in enumerate(items, 1):
        api(
            "/api/public/dataset-items",
            {
                "datasetName": DATASET,
                # Stable id so re-running updates rather than duplicating.
                "id": f"mined-{item['session'][:8]}-{i:04d}",
                "input": item["input"],
                "expectedOutput": item["expected"],
                "metadata": {"split": "mined", "session": item["session"], "ts": item["ts"]},
            },
        )
    print(f"pushed {len(items)} item(s) to dataset {DATASET!r}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--per-skill", type=int, default=5, help="max cases per skill (default 5)")
    ap.add_argument("--dry-run", action="store_true", help="print the sample, push nothing")
    args = ap.parse_args()

    items = collect(args.per_skill)
    skills = sorted({i["expected"] for i in items})
    print(f"{len(items)} case(s) across {len(skills)} skill(s)\n")

    if args.dry_run:
        for item in items:
            text = item["input"]
            print(f"  {item['expected']:<34} {text[:88]}{'…' if len(text) > 88 else ''}")
        print("\n(dry run — nothing pushed)")
        return

    push(items)


if __name__ == "__main__":
    main()

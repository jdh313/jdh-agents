#!/usr/bin/env python3
"""Publish the skill-routing judge prompt to Langfuse as a versioned prompt.

The judge's context is the assembled description corpus — every skill's
``description:`` from the compiled Claude marketplaces named in
``CATALOG_SOURCES``. That corpus changes on every plugin edit, so it is
GENERATED from those repos and pushed here, never hand-written in the Langfuse
UI.

Same contract as ``marketplaces/``: the repos are authoritative, Langfuse holds
a published copy. Editing the prompt in the UI makes Langfuse the head while
this generator still believes it owns the content, and the next push silently
reverts the edit. Don't.

Each version records a short SHA per source repo, so an experiment can always
be traced back to the descriptions it actually tested.

Usage::

    uv run scripts/evals/push_prompt.py --dry-run   # print the prompt, push nothing
    uv run scripts/evals/push_prompt.py             # publish a new version
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _langfuse import api  # noqa: E402

PROMPT_NAME = "skill-routing-judge"

# The judge must choose among the same skills the routing model sees, and that
# is not one repo: ndr is its own marketplace and supplies the second-most-fired
# skill in the corpus. Both are directory-sourced marketplaces with the same
# compiled shape, so both are read the same way. Skills installed from the other
# 20 marketplaces are deliberately out of scope for now — their cases are
# filtered out of the run rather than judged against a catalog that omits them.
CATALOG_SOURCES = [
    REPO / "marketplaces" / "claude" / "plugins",
    Path.home() / "Projects" / "ndr" / "marketplaces" / "claude" / "plugins",
]

INSTRUCTIONS = """\
You route a user's message to the single Claude Code skill that should handle it.

Below is the full catalog of available skills, each with the description the \
routing model actually sees. Read the user's message and answer with exactly one \
skill name from the catalog, verbatim, and nothing else.

If no skill in the catalog is a good fit — the message is ordinary conversation, \
a direct question, or a task needing no specialized workflow — answer with the \
single word NONE. Answering NONE when unsure is correct behavior; a wrong skill \
is worse than no skill.

Do not explain. Output one line: a skill name, or NONE.

<catalog>
{catalog}
</catalog>"""


def load_catalog() -> list[tuple[str, str]]:
    """Return sorted ``(plugin:skill, description)`` pairs across every source."""
    entries: dict[str, str] = {}
    for root in CATALOG_SOURCES:
        if not root.is_dir():
            sys.exit(f"catalog source missing: {root}")
        for path in sorted(root.glob("*/skills/*/SKILL.md")):
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            _, _, rest = text.partition("---\n")
            front, _, _ = rest.partition("\n---")
            try:
                meta = yaml.safe_load(front) or {}
            except yaml.YAMLError:
                continue
            description = str(meta.get("description") or "").strip()
            if not description:
                continue
            plugin = path.parents[2].name
            name = str(meta.get("name") or path.parents[0].name)
            entries[f"{plugin}:{name}"] = " ".join(description.split())
    return sorted(entries.items())


def build_catalog_block(entries: list[tuple[str, str]]) -> str:
    return "\n\n".join(f"{name}\n  {desc}" for name, desc in entries)


def source_versions() -> str:
    """Provenance stamp: one short SHA per catalog source, dirty trees marked.

    A version is only reproducible if every source repo is clean, so each is
    recorded separately rather than collapsed into one.
    """
    stamps = []
    for root in CATALOG_SOURCES:
        # marketplaces/<target>/plugins -> repo root
        repo = root.parents[2]

        def git(*args: str, _repo: Path = repo) -> str:
            return subprocess.run(
                ["git", "-C", str(_repo), *args], capture_output=True, text=True, check=False
            ).stdout.strip()

        sha = git("rev-parse", "--short", "HEAD") or "unknown"
        stamps.append(f"{repo.name}@{sha}{'-dirty' if git('status', '--porcelain') else ''}")
    return " ".join(stamps)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="print the prompt, push nothing")
    ap.add_argument(
        "--label",
        action="append",
        default=None,
        help="label for this version (repeatable; defaults to 'production')",
    )
    args = ap.parse_args()

    entries = load_catalog()
    if not entries:
        sys.exit("no skills found in any catalog source — run `marketplace sync` first")
    system = INSTRUCTIONS.format(catalog=build_catalog_block(entries))
    stamp = source_versions()

    print(f"{len(entries)} skill(s), ~{len(system) // 4} tokens of catalog, {stamp}")

    if args.dry_run:
        print("\n" + system[:1200] + "\n...[truncated]\n(dry run — nothing pushed)")
        return
    if "-dirty" in stamp:
        print("warning: a source tree is dirty; this version will not be reproducible")

    result = api(
        "/api/public/v2/prompts",
        {
            "name": PROMPT_NAME,
            "type": "chat",
            "prompt": [
                {"role": "system", "content": system},
                {"role": "user", "content": "{{utterance}}"},
            ],
            "labels": args.label or ["production"],
            "config": {"model": "claude-haiku-4-5-20251001", "temperature": 0, "max_tokens": 32},
            "commitMessage": f"catalog of {len(entries)} skills from {stamp}",
        },
    )
    print(f"published {PROMPT_NAME} v{result.get('version')} labels={result.get('labels')}")


if __name__ == "__main__":
    main()

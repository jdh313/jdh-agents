"""Shared Claude Code transcript parsing for the introspect skills.

Both ``usage-report`` and ``conversation-temperature`` read the same JSONL
session transcripts under ``~/.claude/projects/``. The discovery, timestamp,
user-text, and skill-naming helpers live here so the two agree on what a
prompt is and what a skill is called.

Standard library only, Python 3.9+.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

COMMAND_NAME_RE = re.compile(r"<command-name>\s*(/?[^<]+?)\s*</command-name>")

# Built-in session-management commands — listed separately from workflow skills.
SESSION_COMMANDS = {
    "/compact",
    "/clear",
    "/cost",
    "/context",
    "/config",
    "/model",
    "/resume",
    "/help",
    "/exit",
    "/quit",
    "/login",
    "/logout",
    "/status",
    "/init",
}

# Bare names NOT to merge even when they uniquely match a canonical skill —
# they also exist as independent standalone skills (e.g. the built-in `/review`
# is distinct from `commits:review`).
SKILL_ALIAS_EXCLUDE = {"review"}

# Canonical-name renames applied after alias-collapsing, folding a renamed
# plugin's skills into their current home. The `commits` plugin was renamed to
# `commit` and collapsed its review/split skills into a single `commit` skill.
SKILL_RENAMES = {
    "commits:commits": "commit:commit",
    "commits:review": "commit:commit",
    "commits:split": "commit:commit",
}

# Plugin-rollup renames — the same rename at plugin grain (for plugin_attribution).
PLUGIN_RENAMES = {"commits": "commit"}

# System tags that the harness injects into user turns. Hooks, skill loads, and
# slash-command expansion all arrive inside the user message, so anything that
# measures what a person typed has to remove them first.
_TAGGED_BLOCK_RE = re.compile(
    r"<(system-reminder|local-command-stdout|task-notification"
    r"|command-name|command-message|command-args)[^>]*>.*?</\1>",
    re.DOTALL,
)
_ANY_TAGGED_BLOCK_RE = re.compile(r"<[a-z-]+>.*?</[a-z-]+>", re.DOTALL)
_SKILL_PREAMBLE_RE = re.compile(r"Base directory for this skill:.*", re.DOTALL)
_CHANGELOG_RE = re.compile(r"Version \d+\.\d+\.\d+:.*", re.DOTALL)
_CONTINUATION_RE = re.compile(
    r"This session is being continued from a previous conversation.*?(?=\n\n|\Z)",
    re.DOTALL,
)


def find_transcripts(
    projects_dir: Path, repo_keyword: str | None = None, scan_all: bool = False
) -> list[Path]:
    """Return JSONL transcript paths for matching project dirs.

    Args:
        projects_dir: The ``~/.claude/projects`` directory (or an override).
        repo_keyword: Case-insensitive substring a project dir must contain.
        scan_all: If True, ignore ``repo_keyword`` and take every project dir.

    Returns:
        Sorted list of ``*.jsonl`` transcript file paths.
    """
    if not projects_dir.is_dir():
        return []
    files: list[Path] = []
    for child in projects_dir.iterdir():
        if not child.is_dir():
            continue
        if not scan_all and repo_keyword and repo_keyword.lower() not in child.name.lower():
            continue
        files.extend(child.glob("*.jsonl"))
    return sorted(files)


def parse_ts(value: object) -> datetime | None:
    """Parse an ISO-8601 timestamp (with trailing ``Z``) to a naive UTC datetime."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def raw_user_text(content: object) -> str:
    """Join the text blocks of a user-message ``content`` field, tags intact.

    Tool-result blocks are skipped, so a record carrying only tool results
    yields ``""``. Returns text exactly as recorded — use this when the system
    tags themselves are the signal (e.g. reading ``<command-name>``), and
    ``clean_user_text`` when measuring what a person actually typed.
    """
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict):
            if block.get("type") == "tool_result":
                continue
            if block.get("type") == "text":
                parts.append(block.get("text") or "")
    return "\n".join(parts)


def strip_system_tags(text: str) -> str:
    """Remove harness-injected blocks from a user turn.

    Strips tagged blocks (``<system-reminder>``, ``<command-args>``, …), skill
    load preambles, hook-injected version changelogs, and session-continuation
    banners. What remains is as close to the typed message as the transcript
    permits.
    """
    text = _TAGGED_BLOCK_RE.sub("", text)
    text = _ANY_TAGGED_BLOCK_RE.sub("", text)
    text = _SKILL_PREAMBLE_RE.sub("", text)
    text = _CHANGELOG_RE.sub("", text)
    text = _CONTINUATION_RE.sub("", text)
    return text.strip()


def is_meta_summary(text: str) -> bool:
    """True for auto-compaction / continuation summaries injected as user turns.

    These are machine-generated recaps ('Primary Request and Intent', numbered
    analysis) that badly skew every section (corrections, goals, tone): they're
    long, third-person, and full of 'the user'/'we' — not authored register.
    Distinctive template phrases only, to avoid catching real messages.
    """
    head = text[:600]
    return (
        "Primary Request and Intent" in head
        or ("Analysis:" in head and "Summary:" in head)
        or head.lstrip().lower().startswith("this session is being continued")
    )


def clean_user_text(content: object) -> str:
    """Extract what the person typed: text blocks, tags stripped, recaps dropped.

    Returns ``""`` for tool-result-only records and for machine-generated
    compaction summaries, so a falsy result means "not an authored prompt".
    """
    text = strip_system_tags(raw_user_text(content))
    return "" if is_meta_summary(text) else text


def classify_command(name: str) -> str:
    """Bucket a command-name into the session-management or workflow lane."""
    base = name.split()[0] if name else name
    return "session" if base in SESSION_COMMANDS else "workflow"


def build_skill_alias(names: set[str]) -> dict[str, str]:
    """Map non-namespaced skill aliases to their canonical ``plugin:skill`` form.

    Two recording quirks produce aliases for the same skill: a bare skill name
    with no plugin prefix (``linear-workflow`` for ``linear:linear-workflow``)
    and a dash-joined form (``spec-flow-implement`` for ``spec-flow:implement``).
    A canonical name is any that already contains ``:``. An alias is merged only
    when it maps to exactly one canonical — ambiguous collisions are left alone.
    """
    canonical = {n for n in names if ":" in n}
    bare: dict[str, set[str]] = defaultdict(set)
    dash: dict[str, set[str]] = defaultdict(set)
    for c in canonical:
        plugin, _, skill = c.partition(":")
        bare[skill].add(c)
        dash[f"{plugin}-{skill}"].add(c)

    alias: dict[str, str] = {}
    for key, matches in list(bare.items()) + list(dash.items()):
        if key in canonical or key in SKILL_ALIAS_EXCLUDE or len(matches) != 1:
            continue
        alias.setdefault(key, next(iter(matches)))
    return alias

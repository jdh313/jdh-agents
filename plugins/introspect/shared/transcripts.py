"""Shared Claude Code transcript parsing for the introspect skills.

Both ``usage-report`` and ``conversation-temperature`` read the same JSONL
session transcripts under ``~/.claude/projects/``. The discovery, timestamp,
user-text, and skill-naming helpers live here so the two agree on what a
prompt is and what a skill is called.

Standard library only, Python 3.9+.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterator, NamedTuple

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


class SkillInvocation(NamedTuple):
    """One ``Skill`` tool call paired with the user turn that preceded it.

    ``trigger`` is ``"explicit"`` when the user typed the slash command by name
    and ``"inferred"`` when the model chose the skill from its description.
    Only inferred rows carry routing signal — an explicit invocation tests
    nothing, since there was no choice to make.

    Empirically ``"explicit"`` does not occur: the harness expands a typed
    ``/plugin:skill`` inline as ``<command-name>`` plus injected body, without
    ever emitting a ``Skill`` tool call. Every recorded ``Skill`` call is
    therefore a model choice. The field stays as a guard — if that expansion
    ever changes, explicit rows appear here instead of silently polluting the
    inferred set.
    """

    utterance: str
    skill: str
    trigger: str
    session: str
    ts: datetime | None


def iter_records(path: Path) -> Iterator[dict]:
    """Yield the parsed JSON records of one transcript, skipping malformed lines."""
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(rec, dict):
                yield rec


def _matches_command(skill: str, commands: list[str]) -> bool:
    """True when one of the typed slash commands names this skill.

    Accepts the canonical ``plugin:skill`` form plus the two recording quirks
    ``build_skill_alias`` handles — a bare skill name and a dash-joined form.
    """
    plugin, _, bare = skill.partition(":")
    forms = {skill, bare or skill}
    if plugin and bare:
        forms.add(f"{plugin}-{bare}")
    for cmd in commands:
        base = cmd.strip().split()[0].lstrip("/") if cmd.strip() else ""
        if base and base in forms:
            return True
    return False


def iter_skill_invocations(path: Path) -> Iterator[SkillInvocation]:
    """Pair each main-thread ``Skill`` call with the user turn that preceded it.

    The held utterance persists across several skill calls, so a turn that fires
    two skills yields two rows sharing one utterance. Sidechain (subagent)
    records are skipped — a subagent's skill call answers the orchestrator's
    prompt, not the user's. Turns with no recoverable typed text are dropped,
    since an empty utterance cannot serve as a routing case.
    """
    utterance = ""
    commands: list[str] = []
    ts: datetime | None = None
    session = path.stem

    for rec in iter_records(path):
        if rec.get("isSidechain"):
            continue
        msg = rec.get("message")
        if not isinstance(msg, dict):
            continue
        rtype = rec.get("type")

        if rtype == "user" and not rec.get("isMeta"):
            content = msg.get("content")
            raw = raw_user_text(content)
            typed = clean_user_text(content)
            cmds = COMMAND_NAME_RE.findall(raw)
            # Tool-result-only records carry neither; they are not a new turn.
            if typed or cmds:
                utterance = typed
                commands = cmds
                ts = parse_ts(rec.get("timestamp"))

        elif rtype == "assistant":
            content = msg.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not (isinstance(block, dict) and block.get("type") == "tool_use"):
                    continue
                if block.get("name") != "Skill":
                    continue
                inp = block.get("input")
                if not isinstance(inp, dict) or not inp.get("skill"):
                    continue
                skill = SKILL_RENAMES.get(str(inp["skill"]), str(inp["skill"]))
                if not utterance:
                    continue
                yield SkillInvocation(
                    utterance=utterance,
                    skill=skill,
                    trigger="explicit" if _matches_command(skill, commands) else "inferred",
                    session=session,
                    ts=ts,
                )


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

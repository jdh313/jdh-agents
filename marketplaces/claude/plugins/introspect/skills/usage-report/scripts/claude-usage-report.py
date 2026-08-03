#!/usr/bin/env python3
"""Summarize how a user works with Claude Code in a given repo, from local transcripts.

Reads Claude Code session transcripts (JSONL) under ``~/.claude/projects/`` and
emits an aggregate workflow report: how tasks get kicked off (slash command vs
bare prompt vs plan mode), which skills / slash commands / subagents / MCP tools
get used, tool-usage distribution, models, and activity over time.

Privacy: by default the report contains only NAMES, COUNTS, and DATES — no prompt
text, command arguments, skill arguments, or subagent prompts ever leave the file.
Pass ``--include-args`` to additionally surface slash-command and skill argument
strings (still never raw prompt/agent bodies). Nothing is sent anywhere.

By default the report scopes to the current directory's name and is SAVED to that
repo's ``.claude/usage-reports/usage-report.md`` (a ``.gitignore`` is dropped there
so it is never committed). Use ``--stdout`` to print instead, or ``--out FILE`` for
an explicit path. Hand the saved file back however you like.

Usage (run from inside the repo you want to analyze)::

    python3 claude-usage-report.py                 # scope = cwd name; saves report into the repo
    python3 claude-usage-report.py --repo myrepo    # override the scope keyword
    python3 claude-usage-report.py --all --stdout   # every project, printed to the terminal
    python3 claude-usage-report.py --csv            # save tidy CSV instead of markdown
    python3 claude-usage-report.py --since 2026-06-01 --out report.md

No third-party dependencies — standard library only, Python 3.9+.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from collections import Counter, defaultdict
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


def find_transcripts(projects_dir: Path, repo_keyword: str | None, scan_all: bool) -> list[Path]:
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


def text_of(content: object) -> str | None:
    """Extract typed human text from a user-message ``content`` field, if any.

    Returns the string for plain-string content, or the first ``text`` block of a
    list (tool-result-only records yield ``None`` and are thus skipped as prompts).
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                return block.get("text")
    return None


class Stats:
    """Accumulator for all extracted workflow metrics across every transcript."""

    def __init__(self) -> None:
        self.sessions = 0
        self.session_dates: list[datetime] = []
        self.first_ts: datetime | None = None
        self.last_ts: datetime | None = None
        self.human_prompts = 0
        self.kickoffs: Counter[str] = Counter()  # how each session opened
        self.slash_workflow: Counter[str] = Counter()
        self.slash_session: Counter[str] = Counter()
        self.skill_invocations: Counter[str] = Counter()  # Skill tool_use
        self.skill_attribution: Counter[str] = Counter()  # actions under a skill
        self.plugin_attribution: Counter[str] = Counter()
        self.subagents: Counter[str] = Counter()
        self.tools_main: Counter[str] = Counter()
        self.tools_sub: Counter[str] = Counter()
        self.mcp_tools: Counter[str] = Counter()
        self.permission_modes: Counter[str] = Counter()
        self.models: Counter[str] = Counter()
        self.entrypoints: Counter[str] = Counter()
        self.prompts_per_branch: Counter[str] = Counter()
        self.prompts_per_day: Counter[str] = Counter()
        self.sessions_per_day: Counter[str] = Counter()
        self.worktree_sessions = 0
        self.cwds: Counter[str] = Counter()  # session cwd -> count, for repo-root resolution
        # opt-in argument samples
        self.slash_args: dict[str, list[str]] = defaultdict(list)
        self.skill_args: dict[str, list[str]] = defaultdict(list)

    def bump_ts(self, ts: datetime | None) -> None:
        """Track earliest/latest timestamps seen across the whole corpus."""
        if ts is None:
            return
        if self.first_ts is None or ts < self.first_ts:
            self.first_ts = ts
        if self.last_ts is None or ts > self.last_ts:
            self.last_ts = ts


def classify_command(name: str) -> str:
    """Bucket a command-name into the session-management or workflow lane."""
    base = name.split()[0] if name else name
    return "session" if base in SESSION_COMMANDS else "workflow"


def process_file(path: Path, st: Stats, include_args: bool) -> None:
    """Fold one transcript file's records into the running ``Stats``."""
    st.sessions += 1
    first_human_seen = False
    file_min: datetime | None = None
    is_worktree = False
    file_entrypoint: str | None = None
    file_cwd: str | None = None

    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            rtype = rec.get("type")
            ts = parse_ts(rec.get("timestamp"))
            st.bump_ts(ts)
            if ts and (file_min is None or ts < file_min):
                file_min = ts

            cwd = rec.get("cwd")
            if isinstance(cwd, str):
                if file_cwd is None:
                    file_cwd = cwd
                if "worktrees" in cwd:
                    is_worktree = True
            if file_entrypoint is None and rec.get("entrypoint"):
                file_entrypoint = str(rec["entrypoint"])
            if rec.get("attributionSkill"):
                st.skill_attribution[str(rec["attributionSkill"])] += 1
            if rec.get("attributionPlugin"):
                st.plugin_attribution[str(rec["attributionPlugin"])] += 1
            if rtype == "permission-mode" and rec.get("permissionMode"):
                st.permission_modes[str(rec["permissionMode"])] += 1

            msg = rec.get("message")
            if not isinstance(msg, dict):
                continue
            if msg.get("model"):
                st.models[str(msg["model"])] += 1

            if rtype == "user" and not rec.get("isSidechain") and not rec.get("isMeta"):
                txt = text_of(msg.get("content"))
                if txt:
                    st.human_prompts += 1
                    branch = rec.get("gitBranch") or "(none)"
                    st.prompts_per_branch[str(branch)] += 1
                    if ts:
                        st.prompts_per_day[ts.strftime("%Y-%m-%d")] += 1

                    cmds = COMMAND_NAME_RE.findall(txt)
                    opener = "bare prompt"
                    if cmds:
                        first_cmd = cmds[0].strip()
                        opener = f"command {first_cmd.split()[0]}"
                        for c in cmds:
                            c = c.strip()
                            base = c.split()[0]
                            if classify_command(c) == "session":
                                st.slash_session[base] += 1
                            else:
                                st.slash_workflow[base] += 1
                                if include_args:
                                    args = re.search(
                                        r"<command-args>(.*?)</command-args>", txt, re.S
                                    )
                                    if args and args.group(1).strip():
                                        st.slash_args[base].append(args.group(1).strip()[:120])
                    if not first_human_seen:
                        first_human_seen = True
                        st.kickoffs[opener if cmds else "bare prompt"] += 1

            if rtype == "assistant":
                content = msg.get("content")
                if isinstance(content, list):
                    sidechain = bool(rec.get("isSidechain"))
                    for block in content:
                        if not (isinstance(block, dict) and block.get("type") == "tool_use"):
                            continue
                        name = block.get("name") or "?"
                        (st.tools_sub if sidechain else st.tools_main)[name] += 1
                        inp = block.get("input") or {}
                        if name.startswith("mcp__"):
                            st.mcp_tools[name] += 1
                        if name == "Skill" and isinstance(inp, dict) and inp.get("skill"):
                            sk = str(inp["skill"])
                            st.skill_invocations[sk] += 1
                            if include_args and inp.get("args"):
                                st.skill_args[sk].append(str(inp["args"])[:120])
                        if name in ("Agent", "Task") and isinstance(inp, dict):
                            st.subagents[str(inp.get("subagent_type") or "(default)")] += 1

    if file_min:
        st.session_dates.append(file_min)
        st.sessions_per_day[file_min.strftime("%Y-%m-%d")] += 1
    if is_worktree:
        st.worktree_sessions += 1
    if file_entrypoint:
        st.entrypoints[file_entrypoint] += 1
    if file_cwd:
        st.cwds[file_cwd] += 1


def _table(counter: Counter[str], limit: int = 20) -> list[str]:
    """Render a counter as markdown table rows, most-common first."""
    rows = ["| name | count |", "| --- | ---: |"]
    for name, count in counter.most_common(limit):
        rows.append(f"| `{name}` | {count} |")
    if not counter:
        rows.append("| _(none)_ | 0 |")
    return rows


def _multi_table(headers: list[str], data_rows: list[list[str]]) -> list[str]:
    """Render a markdown table from header labels and pre-formatted string rows.

    The first column is left-aligned; all remaining columns are right-aligned
    (they hold numeric values). Cells are emitted verbatim — callers wrap names
    in backticks and stringify numbers themselves.
    """
    align = ["---"] + ["---:"] * (len(headers) - 1)
    rows = ["| " + " | ".join(headers) + " |", "| " + " | ".join(align) + " |"]
    for row in data_rows:
        rows.append("| " + " | ".join(row) + " |")
    if not data_rows:
        rows.append("| _(none)_ |" + " |" * (len(headers) - 1))
    return rows


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


def normalized_view(st: Stats) -> dict[str, object]:
    """Return alias-collapsed copies of the skill and slash-command counters.

    Built once from the union of skill names, then applied to skill and slash
    counters so invocations, attribution, and typed-command tallies all key on
    the same canonical names. ``plugin_attribution`` is left untouched — it is
    already clean and intentionally keeps the legacy/renamed plugin split.
    """
    names = set(st.skill_invocations) | set(st.skill_attribution)
    alias = build_skill_alias(names)

    def collapse(counter: Counter[str], strip_slash: bool = False) -> Counter[str]:
        out: Counter[str] = Counter()
        for key, count in counter.items():
            base = key.lstrip("/") if strip_slash else key
            canon = alias.get(base, base)
            out[SKILL_RENAMES.get(canon, canon)] += count
        return out

    plugin_rollup: Counter[str] = Counter()
    for plugin, count in st.plugin_attribution.items():
        plugin_rollup[PLUGIN_RENAMES.get(plugin, plugin)] += count

    return {
        "alias": alias,
        "skill_invocations": collapse(st.skill_invocations),
        "skill_attribution": collapse(st.skill_attribution),
        "slash_workflow": collapse(st.slash_workflow, strip_slash=True),
        "slash_session": collapse(st.slash_session, strip_slash=True),
        "plugin_attribution": plugin_rollup,
    }


def to_markdown(st: Stats, include_args: bool, scope: str) -> str:
    """Assemble the full markdown report from accumulated stats."""
    nv = normalized_view(st)
    skill_inv: Counter[str] = nv["skill_invocations"]  # type: ignore[assignment]
    skill_act: Counter[str] = nv["skill_attribution"]  # type: ignore[assignment]
    slash_workflow: Counter[str] = nv["slash_workflow"]  # type: ignore[assignment]
    slash_session: Counter[str] = nv["slash_session"]  # type: ignore[assignment]
    plugin_attr: Counter[str] = nv["plugin_attribution"]  # type: ignore[assignment]
    out: list[str] = []
    span = "n/a"
    if st.first_ts and st.last_ts:
        span = f"{st.first_ts:%Y-%m-%d} -> {st.last_ts:%Y-%m-%d}"
    active_days = len(st.sessions_per_day)

    out.append("# Claude Code usage report")
    out.append("")
    out.append(f"_Scope:_ {scope}")
    out.append("")
    out.append("## Overview")
    out.append("")
    out.append(f"- **Sessions:** {st.sessions}")
    out.append(f"- **Human prompts (main-thread):** {st.human_prompts}")
    out.append(f"- **Date span:** {span}  ({active_days} active days)")
    out.append(f"- **Sessions in a git worktree:** {st.worktree_sessions}")
    if st.entrypoints:
        ep = ", ".join(f"{k}: {v}" for k, v in st.entrypoints.most_common())
        out.append(f"- **Entrypoints:** {ep}")
    out.append("")

    out.append("## How tasks get kicked off")
    out.append("_(first main-thread message of each session)_")
    out.append("")
    out.extend(_table(st.kickoffs, limit=25))
    out.append("")
    if st.permission_modes:
        out.append("### Permission / plan mode (mode-change records)")
        out.append("")
        out.extend(_table(st.permission_modes))
        out.append("")

    out.append("## Skills")
    out.append("")
    out.append(
        "_typed = times you typed `/cmd` · invocations = `Skill` tool starts (any trigger) · "
        "actions = steps performed while the skill ran (`attributionSkill`) · "
        "act/inv = depth per run. Sorted by invocations._"
    )
    out.append("")
    skill_keys = set(skill_inv) | set(skill_act)
    skill_rows: list[list[str]] = []
    ranked = sorted(skill_keys, key=lambda k: (-skill_inv[k], -skill_act[k], k))
    for name in ranked[:30]:
        inv = skill_inv[name]
        act = skill_act[name]
        typed = slash_workflow.get(name, 0)
        ratio = f"{act / inv:.0f}" if inv else "-"
        skill_rows.append([f"`{name}`", str(typed), str(inv), str(act), ratio])
    out.extend(_multi_table(["skill", "typed", "invocations", "actions", "act/inv"], skill_rows))
    out.append("")
    if plugin_attr:
        out.append("### Actions by plugin (skills rolled up to their plugin)")
        out.append("")
        out.extend(_table(plugin_attr, limit=20))
        out.append("")

    out.append("## Slash commands typed")
    out.append("")
    kind_of = {k: "workflow" for k in slash_workflow}
    kind_of.update({k: "session" for k in slash_session})
    combined_slash: Counter[str] = Counter()
    combined_slash.update(slash_workflow)
    combined_slash.update(slash_session)
    slash_rows = [
        [f"`/{name}`", kind_of.get(name, "?"), str(count)]
        for name, count in combined_slash.most_common(40)
    ]
    out.extend(_multi_table(["command", "kind", "count"], slash_rows))
    out.append("")

    out.append("## Subagents spawned (by type)")
    out.append("")
    out.extend(_table(st.subagents, limit=30))
    out.append("")

    out.append("## MCP tools used")
    out.append("")
    out.extend(_table(st.mcp_tools, limit=30))
    out.append("")

    out.append("## Tool usage")
    out.append("")
    out.append("_main = main thread · sub = inside subagents (when inlined) · sorted by total._")
    out.append("")
    tool_keys = set(st.tools_main) | set(st.tools_sub)
    tool_rows: list[list[str]] = []
    for name in sorted(tool_keys, key=lambda k: (-(st.tools_main[k] + st.tools_sub[k]), k))[:35]:
        main = st.tools_main[name]
        sub = st.tools_sub[name]
        tool_rows.append([f"`{name}`", str(main), str(sub), str(main + sub)])
    out.extend(_multi_table(["tool", "main", "sub", "total"], tool_rows))
    out.append("")

    out.append("## Models")
    out.append("")
    out.extend(_table(st.models))
    out.append("")

    out.append("## Activity")
    out.append("")
    out.append("### Prompts per git branch (top 20)")
    out.append("")
    out.extend(_table(st.prompts_per_branch, limit=20))
    out.append("")
    out.append("### Sessions per day")
    out.append("")
    rows = ["| day | sessions | prompts |", "| --- | ---: | ---: |"]
    for day in sorted(st.sessions_per_day):
        rows.append(f"| {day} | {st.sessions_per_day[day]} | {st.prompts_per_day.get(day, 0)} |")
    out.extend(rows)
    out.append("")

    if include_args and (st.slash_args or st.skill_args):
        out.append("## Argument samples (opt-in via --include-args)")
        out.append("")
        for base, samples in sorted(st.slash_args.items()):
            uniq = list(dict.fromkeys(samples))[:8]
            out.append(f"- `{base}`: " + "; ".join(f"`{s}`" for s in uniq))
        for sk, samples in sorted(st.skill_args.items()):
            uniq = list(dict.fromkeys(samples))[:8]
            out.append(f"- skill `{sk}`: " + "; ".join(f"`{s}`" for s in uniq))
        out.append("")

    return "\n".join(out)


def to_json(st: Stats) -> str:
    """Serialize the accumulated stats to a JSON string (names + counts only)."""
    nv = normalized_view(st)
    payload = {
        "sessions": st.sessions,
        "human_prompts": st.human_prompts,
        "date_span": [
            st.first_ts.isoformat() if st.first_ts else None,
            st.last_ts.isoformat() if st.last_ts else None,
        ],
        "worktree_sessions": st.worktree_sessions,
        "kickoffs": dict(st.kickoffs),
        "permission_modes": dict(st.permission_modes),
        "skill_aliases_applied": nv["alias"],
        "skill_invocations": dict(nv["skill_invocations"]),  # type: ignore[arg-type]
        "skill_attribution": dict(nv["skill_attribution"]),  # type: ignore[arg-type]
        "plugin_attribution": dict(nv["plugin_attribution"]),  # type: ignore[arg-type]
        "slash_workflow": dict(nv["slash_workflow"]),  # type: ignore[arg-type]
        "slash_session": dict(nv["slash_session"]),  # type: ignore[arg-type]
        "subagents": dict(st.subagents),
        "tools_main": dict(st.tools_main),
        "tools_sub": dict(st.tools_sub),
        "mcp_tools": dict(st.mcp_tools),
        "models": dict(st.models),
        "entrypoints": dict(st.entrypoints),
        "prompts_per_branch": dict(st.prompts_per_branch),
        "prompts_per_day": dict(st.prompts_per_day),
        "sessions_per_day": dict(st.sessions_per_day),
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def to_csv(st: Stats) -> str:
    """Serialize stats as a tidy long-format CSV with columns section,key,metric,value.

    One row per (section, key, metric) so every table — skills, slash commands,
    tools, models, activity — lands in a single file that pivots cleanly in
    pandas or a spreadsheet. Uses the same alias-normalized counts as the other
    outputs. Names and counts only — no prompt text.
    """
    nv = normalized_view(st)
    skill_inv: Counter[str] = nv["skill_invocations"]  # type: ignore[assignment]
    skill_act: Counter[str] = nv["skill_attribution"]  # type: ignore[assignment]
    slash_workflow: Counter[str] = nv["slash_workflow"]  # type: ignore[assignment]
    slash_session: Counter[str] = nv["slash_session"]  # type: ignore[assignment]
    plugin_attr: Counter[str] = nv["plugin_attribution"]  # type: ignore[assignment]

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(["section", "key", "metric", "value"])

    writer.writerow(["overview", "sessions", "count", st.sessions])
    writer.writerow(["overview", "human_prompts", "count", st.human_prompts])
    writer.writerow(["overview", "worktree_sessions", "count", st.worktree_sessions])
    writer.writerow(
        ["overview", "date_first", "date", st.first_ts.date().isoformat() if st.first_ts else ""]
    )
    writer.writerow(
        ["overview", "date_last", "date", st.last_ts.date().isoformat() if st.last_ts else ""]
    )

    for name, count in st.kickoffs.most_common():
        writer.writerow(["kickoff", name, "count", count])
    for name, count in st.permission_modes.most_common():
        writer.writerow(["permission_mode", name, "count", count])

    for name in sorted(set(skill_inv) | set(skill_act), key=lambda k: (-skill_inv[k], k)):
        writer.writerow(["skill", name, "typed", slash_workflow.get(name, 0)])
        writer.writerow(["skill", name, "invocations", skill_inv[name]])
        writer.writerow(["skill", name, "actions", skill_act[name]])

    for name, count in plugin_attr.most_common():
        writer.writerow(["plugin", name, "actions", count])

    kind_of = {k: "workflow" for k in slash_workflow}
    kind_of.update({k: "session" for k in slash_session})
    combined_slash: Counter[str] = Counter()
    combined_slash.update(slash_workflow)
    combined_slash.update(slash_session)
    for name, count in combined_slash.most_common():
        writer.writerow(["slash", "/" + name, "count", count])
        writer.writerow(["slash", "/" + name, "kind", kind_of.get(name, "")])

    for name, count in st.subagents.most_common():
        writer.writerow(["subagent", name, "count", count])
    for name, count in st.mcp_tools.most_common():
        writer.writerow(["mcp_tool", name, "count", count])
    for name in sorted(
        set(st.tools_main) | set(st.tools_sub),
        key=lambda k: (-(st.tools_main[k] + st.tools_sub[k]), k),
    ):
        writer.writerow(["tool", name, "main", st.tools_main[name]])
        writer.writerow(["tool", name, "sub", st.tools_sub[name]])
    for name, count in st.models.most_common():
        writer.writerow(["model", name, "count", count])
    for name, count in st.entrypoints.most_common():
        writer.writerow(["entrypoint", name, "count", count])
    for name, count in st.prompts_per_branch.most_common():
        writer.writerow(["branch", name, "prompts", count])
    for day in sorted(st.sessions_per_day):
        writer.writerow(["day", day, "sessions", st.sessions_per_day[day]])
        writer.writerow(["day", day, "prompts", st.prompts_per_day.get(day, 0)])

    return buf.getvalue().rstrip("\n")


def resolve_repo_root(cwds: Counter[str]) -> Path | None:
    """Infer the repo root from session cwds, rolling worktrees back to their parent.

    Worktree sessions live under ``<repo>/.claude/worktrees/<name>`` (or
    ``/.worktrees/``); those are folded back to ``<repo>`` so the dominant root
    reflects the main checkout rather than a worktree. Returns the most common
    resolved root, or None if no cwd was recorded.
    """
    if not cwds:
        return None
    rolled: Counter[str] = Counter()
    for cwd, count in cwds.items():
        root = cwd
        for marker in ("/.claude/worktrees/", "/.worktrees/"):
            if marker in root:
                root = root.split(marker, 1)[0]
                break
        rolled[root] += count
    return Path(rolled.most_common(1)[0][0])


def main() -> None:
    """CLI entrypoint: discover transcripts, accumulate stats, emit the report."""
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--repo",
        default=Path.cwd().name,
        help="Case-insensitive substring matching project dirs (default: current directory name).",
    )
    ap.add_argument("--all", action="store_true", help="Scan every project dir, ignoring --repo.")
    ap.add_argument(
        "--projects-dir",
        type=Path,
        default=Path.home() / ".claude" / "projects",
        help="Override the ~/.claude/projects location.",
    )
    ap.add_argument(
        "--since",
        help="Ignore sessions whose latest activity is before this YYYY-MM-DD.",
    )
    ap.add_argument(
        "--include-args",
        action="store_true",
        help="Also surface slash-command / skill argument strings (never raw prompt bodies).",
    )
    fmt = ap.add_mutually_exclusive_group()
    fmt.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON (full structured payload) instead of markdown.",
    )
    fmt.add_argument(
        "--csv",
        action="store_true",
        help="Emit tidy long-format CSV (columns: section,key,metric,value) instead of markdown.",
    )
    ap.add_argument(
        "--out", type=Path, help="Write to this explicit path (overrides the default in-repo save)."
    )
    ap.add_argument(
        "--stdout",
        action="store_true",
        help="Print to stdout instead of saving the report file.",
    )
    args = ap.parse_args()

    since_dt = parse_ts(args.since + "T00:00:00Z") if args.since else None

    files = find_transcripts(args.projects_dir, args.repo, args.all)
    if not files:
        scope = "all projects" if args.all else f"projects matching '{args.repo}'"
        print(f"No transcripts found under {args.projects_dir} for {scope}.")
        print("If Claude Code stores history elsewhere, pass --projects-dir, or try --all.")
        return

    st = Stats()
    used = 0
    for f in files:
        if since_dt:
            try:
                if datetime.fromtimestamp(f.stat().st_mtime) < since_dt:
                    continue
            except OSError:
                pass
        process_file(f, st, args.include_args)
        used += 1

    scope_label = "all projects" if args.all else f"project dirs matching '{args.repo}'"
    scope = f"{scope_label} — {used} session file(s) under `{args.projects_dir}`"
    if args.json:
        rendered = to_json(st)
    elif args.csv:
        rendered = to_csv(st)
    else:
        rendered = to_markdown(st, args.include_args, scope)

    ext = "json" if args.json else "csv" if args.csv else "md"
    summary = f"({used} sessions, {st.human_prompts} prompts)"

    if args.stdout:
        print(rendered)
        return
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
        print(f"Wrote {args.out} {summary}.")
        return

    # Default: save into the analyzed repo's .claude/usage-reports/.
    root = resolve_repo_root(st.cwds)
    if root is None or not root.exists():
        print("Could not resolve the repo root from session cwds; printing to stdout instead.")
        print("(Use --out PATH for an explicit location, or --stdout to silence this.)\n")
        print(rendered)
        return
    report_dir = root / ".claude" / "usage-reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    gitignore = report_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Local Claude usage reports - not committed\n*\n", encoding="utf-8")
    target = report_dir / f"usage-report.{ext}"
    target.write_text(rendered, encoding="utf-8")
    print(f"Wrote {target} {summary}.")


if __name__ == "__main__":
    main()

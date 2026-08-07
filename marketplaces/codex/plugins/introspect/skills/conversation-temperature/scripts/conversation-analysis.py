#!/usr/bin/env python3
"""Analyze Claude Code conversation history and produce a structured report.

Reads from two sources:
  1. ~/.claude/projects/*/  — full JSONL conversations (tool calls, assistant text)
  2. ~/.claude/history.jsonl — user prompt log (goes back further, lighter weight)

Usage:
    uv run scripts/conversation-analysis.py
"""
# /// script
# requires-python = ">=3.13"
# ///

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Shared transcript parsing lives at the plugin root so both introspect skills
# agree on what a prompt is. Resolved from __file__ rather than
# ${CLAUDE_PLUGIN_ROOT} so the script also works under Codex, which renames
# that variable to ${PLUGIN_ROOT}. Bytecode is disabled so importing never
# drops a __pycache__ into the plugin tree, where the payload sweep would
# copy it into the compiled marketplaces.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))

from transcripts import clean_user_text, raw_user_text  # noqa: E402

PROJECTS_DIR = Path.home() / ".claude" / "projects"
HISTORY_FILE = Path.home() / ".claude" / "history.jsonl"
# Full-report output goes to `.docs/` under the working directory, not under the
# script. This file ships inside a plugin, so a script-relative path would write
# reports into the installed plugin tree. The `--temperature` fast path prints to
# stdout and never touches this.
OUTPUT_DIR = Path.cwd() / ".docs"
MIN_USER_TURNS = 3
RECENT_DAYS = 30

# Patterns that suggest actual secret values (not just mentions of the concept)
SECRET_PATTERNS = re.compile(
    r"("
    r"(API_KEY|SECRET|PASSWORD|TOKEN|CREDENTIAL)\s*[=:]\s*\S+"
    r"|\.env\b(?!iron)"
    r"|sk-[a-zA-Z0-9]{20,}"
    r"|ghp_[a-zA-Z0-9]{20,}"
    r"|Bearer\s+[a-zA-Z0-9._-]{20,}"
    r")",
    re.IGNORECASE,
)

# --- Correction detection ---
# Two tiers: strong (explicit disagreement) and soft (clarification/redirect)

STRONG_CORRECTION_PATTERNS = re.compile(
    r"("
    r"please don.t\b"
    r"|\bthat.s not (right|correct|what)"
    r"|\byou (missed|forgot|ignored|skipped|broke|deleted|removed)\b"
    r"|\bi didn.t (ask|want|say|mean)\b"
    r"|\bthat broke\b"
    r"|\bundo (that|this|what)\b"
    r"|\brevert (that|this|what|the)\b"
    r"|\bwhy did you\b"
    r"|\bnot what i (asked|wanted|meant)\b"
    r"|\bdon.t do that\b"
    r"|\bno,?\s+i (said|meant|wanted)\b"
    r"|\bstop (doing|adding|using|making|creating)\b"
    r"|\bput (it|that|them) back\b"
    r"|\bdon.t (change|touch|modify|delete|remove)\b"
    r"|\bwithout (my |asking|permission)\b"
    r"|\blet.s not\b"
    r"|update memory so we don.t"
    r"|\bdon.t make this mistake\b"
    r")",
    re.IGNORECASE,
)

SOFT_CORRECTION_PATTERNS = re.compile(
    r"("
    r"\bsorry,?\s+i meant\b"
    r"|\bi meant\s+(the|more|that|to)\b"
    r"|\bactually,?\s+(i |the |it |we |let)\b"
    r"|\bno,?\s+(not that|the other|i was|let.s)\b"
    r"|\binstead of\s+\w"
    r"|\brather than\b"
    r"|\bthat.s not quite\b"
    r"|\bclose,?\s+but\b"
    r"|\bnot exactly\b"
    r"|\bwhat i.m (looking|asking)\b"
    r"|\blet me (clarify|rephrase|restate)\b"
    r"|\bto be clear\b"
    r")",
    re.IGNORECASE,
)

# Categories for correction themes
CORRECTION_THEME_PATTERNS = {
    "scope creep / over-engineering": re.compile(
        r"(don.t (add|create|make|include|introduce)|too (much|many)|over.?engineer|unnecessary|overkill|keep.+simple|just.+the)",
        re.IGNORECASE,
    ),
    "wrong target / misunderstood intent": re.compile(
        r"(i meant|not (that|what i)|wrong (file|thing|one)|the other|misunderstand)",
        re.IGNORECASE,
    ),
    "destructive action / safety": re.compile(
        r"(broke|revert|undo|without permission|don.t (touch|delete|remove|change)|put.+back|mistake.+again)",
        re.IGNORECASE,
    ),
    "style / formatting preference": re.compile(
        r"(instead of|rather than|prefer|style|format|wording|rephras|reword|tone)",
        re.IGNORECASE,
    ),
    "missing context / forgot prior info": re.compile(
        r"(you (missed|forgot|ignored|skipped)|i (already|said|told|mentioned)|we (already|discussed))",
        re.IGNORECASE,
    ),
}


def parse_project_name(dir_name: str) -> str:
    """Convert a project dir name like -Users-alex-Projects-foo to a readable name.

    The home prefix is derived from the running user rather than hardcoded, so
    this works on any machine. Fallback only — project_label_from_cwd below is
    preferred whenever a real cwd is available on the records.
    """
    home_prefix = os.path.expanduser("~").replace("/", "-") + "-"
    parts = dir_name.replace(home_prefix, "").split("-")
    if parts and parts[0] == "Projects":
        parts = parts[1:]
    return "/".join(parts) if parts else dir_name


def project_label_from_cwd(cwd: str) -> str:
    """Readable project label from a real cwd. Preferred over parse_project_name:
    the project-dir name encodes the path with both '/' and '.' collapsed to '-',
    which is lossy (team-200 vs a path separator are indistinguishable). The cwd on
    the JSONL records is the real path, so invert it precisely.

    Examples:
      ~/dotfiles                                            -> dotfiles
      ~/projects/acmeos                                    -> acmeos
      ~/projects/acmeos/.claude/worktrees/team-200-.../ecs  -> acmeos/team-200-...
    """
    home = os.path.expanduser("~")
    p = cwd[len(home) + 1:] if cwd.startswith(home + "/") else cwd.lstrip("/")
    parts = [x for x in p.split("/") if x]
    if not parts:
        return cwd
    if parts[0] == "projects":
        parts = parts[1:]
    if not parts:
        return "projects"
    repo = parts[0]
    # worktree: <repo>/.claude/worktrees/<name>/... -> keep repo + worktree name
    if len(parts) >= 4 and parts[1] == ".claude" and parts[2] == "worktrees":
        return f"{repo}/{parts[3]}"
    return repo


def project_from_path(path: str) -> str:
    """Project label from a full path (history.jsonl cwd). Delegates to the same
    labeler as JSONL sessions so history- and session-derived names match exactly
    (otherwise 'acmeos' and 'projects/acmeos' split in per-project tables)."""
    return project_label_from_cwd(path)


# --- Tone / temperature detection ---
# Register markers, split into a "heat" axis (friction/intensity) and a
# "warmth" axis (affect). Terseness is measured separately from length.
# NOTE: matched AFTER clean_for_tone() strips code/URLs, so e.g. a charity.wtf
# link no longer counts as profanity and a code `return` no longer counts as a word.

GRATITUDE_PATTERN = re.compile(r"\b(thanks|thank you|thx|much appreciated|appreciate(?:d|s)?)\b", re.IGNORECASE)
PRAISE_PATTERN = re.compile(
    r"\b(perfect|love it|lovely|beautiful|excellent|awesome|brilliant|elegant|slick|"
    r"nailed it|well done|nicely done|great work|great job|looks great|much better|much cleaner)\b"
    r"|^(great|nice|perfect|beautiful|excellent)\b",  # standalone opener, e.g. "Perfect."
    re.IGNORECASE,
)
POLITENESS_PATTERN = re.compile(
    r"\bplease\b|\bcould you\b|\bwould you mind\b|\bif you could\b|\bwhen you (?:get|have) a\b",
    re.IGNORECASE,
)
PROFANITY_PATTERN = re.compile(r"\b(fuck\w*|shit\w*|damn|dammit|wtf|crap|bloody|arse|goddamn)\b", re.IGNORECASE)
COLLAB_PATTERN = re.compile(r"\b(we|us|our|let'?s)\b", re.IGNORECASE)
HEDGE_PATTERN = re.compile(r"\b(maybe|i think|sort of|kind of|perhaps|i guess|probably|might|not sure)\b", re.IGNORECASE)
# A real "!" — not "!=" (code) and not "!important" (css/markdown).
EXCLAIM_PATTERN = re.compile(r"(?<![!=])!(?!=)")
# A standalone shout: whole (short) message is upper-case words, >=2 words, >=6 letters.
SHOUT_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9 ,.'?!-]*$")


def clean_for_tone(text: str) -> str:
    """Strip content that isn't authored register: fenced code, inline code,
    URLs, and markdown-link targets. Leaves the human's actual prose so tone
    markers match words the user chose, not pasted material."""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)  # fenced code blocks
    text = re.sub(r"`[^`]*`", " ", text)                      # inline code
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)      # md links -> keep text, drop url
    text = re.sub(r"https?://\S+", " ", text)                 # bare urls
    return text.strip()


def extract_text_content(content: list | str) -> str:
    """Extract text from message content blocks."""
    return raw_user_text(content)


def extract_tool_calls(content: list | str) -> list[dict]:
    """Extract tool_use blocks from assistant content."""
    if isinstance(content, str):
        return []
    return [
        {"name": b.get("name", ""), "input": b.get("input", {})}
        for b in content
        if isinstance(b, dict) and b.get("type") == "tool_use"
    ]


def extract_user_text(record: dict) -> str:
    """Extract user text from a message record, stripping tool results and system tags.

    Auto-compaction / continuation summaries yield ``""`` — they are
    machine-generated recaps, not authored register, and skew every downstream
    section (corrections, goals, tone). See ``transcripts.is_meta_summary``.
    """
    return clean_user_text(record.get("message", {}).get("content", ""))


def detect_corrections(text: str) -> list[dict]:
    """Detect correction patterns in user text. Returns list of {tier, match, themes}."""
    if len(text) < 10:
        return []

    corrections = []

    for m in STRONG_CORRECTION_PATTERNS.finditer(text):
        themes = []
        for theme, pat in CORRECTION_THEME_PATTERNS.items():
            if pat.search(text):
                themes.append(theme)
        corrections.append({
            "tier": "strong",
            "match": m.group(0),
            "themes": themes or ["uncategorized"],
        })

    if not corrections:
        for m in SOFT_CORRECTION_PATTERNS.finditer(text):
            themes = []
            for theme, pat in CORRECTION_THEME_PATTERNS.items():
                if pat.search(text):
                    themes.append(theme)
            corrections.append({
                "tier": "soft",
                "match": m.group(0),
                "themes": themes or ["uncategorized"],
            })

    return corrections


def parse_session(filepath: Path) -> dict | None:
    """Parse a JSONL conversation file, pre-filtering heavy content."""
    session_id = filepath.stem
    project_dir = filepath.parent.name
    project_name = parse_project_name(project_dir)  # fallback; overridden by cwd below
    cwd_seen = None

    user_messages = []
    assistant_texts = []
    tool_calls = []
    skill_invocations = []
    agent_launches = []
    commit_messages = []
    scripts_generated = []
    timestamps = []
    corrections = []
    contains_secrets = False

    try:
        with open(filepath) as f:
            prev_assistant_text = ""
            for line in f:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                rec_type = record.get("type")
                if cwd_seen is None and record.get("cwd"):
                    cwd_seen = record["cwd"]
                ts = record.get("timestamp")
                if ts and isinstance(ts, str):
                    try:
                        timestamps.append(
                            datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        )
                    except ValueError:
                        pass

                if rec_type == "user":
                    text = extract_user_text(record)
                    if not text:
                        continue

                    if SECRET_PATTERNS.search(text):
                        contains_secrets = True

                    user_messages.append(text)

                    # Check for corrections
                    corrs = detect_corrections(text)
                    for c in corrs:
                        corrections.append({
                            **c,
                            "user_text": text[:300],
                            "prev_assistant": prev_assistant_text[:200],
                        })

                elif rec_type == "assistant":
                    msg = record.get("message", {})
                    content = msg.get("content", [])

                    text = extract_text_content(content)
                    if text.strip():
                        assistant_texts.append(text.strip())
                        prev_assistant_text = text.strip()

                    for tc in extract_tool_calls(content):
                        name = tc["name"]
                        inp = tc["input"]
                        tool_calls.append(name)

                        if name == "Skill":
                            skill_invocations.append(inp.get("skill", "unknown"))
                        elif name == "Agent":
                            agent_launches.append(
                                inp.get("subagent_type", "general-purpose")
                            )

                        if name == "Write":
                            fp = inp.get("file_path", "")
                            content_text = inp.get("content", "")
                            if fp.endswith((".py", ".sh", ".fish")) and len(content_text) > 100:
                                scripts_generated.append({
                                    "path": fp,
                                    "size": len(content_text),
                                    "first_line": content_text.split("\n")[0][:100],
                                })

                        if name == "Bash":
                            cmd = inp.get("command", "")
                            m = re.search(
                                r'(?:jj\s+new|git\s+commit)\s+.*-m\s+["\']([^"\']+)',
                                cmd,
                            )
                            if m:
                                commit_messages.append(m.group(1))
                            m2 = re.search(r"<<['\"]?EOF\n(.+?)(?:\n|$)", cmd)
                            if m2:
                                commit_messages.append(m2.group(1).strip())

    except (OSError, UnicodeDecodeError):
        return None

    # Prefer the real path from the records over the lossy encoded dir name.
    if cwd_seen:
        project_name = project_label_from_cwd(cwd_seen)

    if len(user_messages) < MIN_USER_TURNS:
        return {"skipped": True, "reason": "< 3 user turns", "session_id": session_id}

    if contains_secrets:
        return {"skipped": True, "reason": "contains secret references", "session_id": session_id}

    date_range = None
    if timestamps:
        date_range = (min(timestamps), max(timestamps))

    return {
        "skipped": False,
        "session_id": session_id,
        "project": project_name,
        "project_dir": project_dir,
        "user_messages": user_messages,
        "assistant_texts": assistant_texts,
        "tool_calls": tool_calls,
        "skill_invocations": skill_invocations,
        "agent_launches": agent_launches,
        "commit_messages": commit_messages,
        "scripts_generated": scripts_generated,
        "corrections": corrections,
        "date_range": date_range,
        "user_turn_count": len(user_messages),
    }


def parse_history_file() -> list[dict]:
    """Parse ~/.claude/history.jsonl for user prompts (goes back further than JSONL conversations)."""
    if not HISTORY_FILE.exists():
        return []

    entries = []
    with open(HISTORY_FILE) as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            text = record.get("display", "").strip()
            ts = record.get("timestamp", 0)
            project = record.get("project", "")

            if not text or not ts:
                continue

            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
            entries.append({
                "text": text,
                "date": dt,
                "project": project_from_path(project),
            })

    return entries


def classify_goal(user_messages: list[str]) -> list[str]:
    """Classify session goals from user message keywords."""
    combined = " ".join(user_messages).lower()
    goals = []

    patterns = {
        "nix/home-manager config": r"\b(nix|home-manager|darwin-rebuild|flake|home\.nix|darwin\.nix)\b",
        "neovim config": r"\b(nvim|neovim|init\.lua|lazy|lsp|treesitter)\b",
        "shell config (zsh/fish)": r"\b(zsh|fish|shell|zshrc|fish\.nix|abbreviation|alias)\b",
        "git/jj workflow": r"\b(git|jj|jujutsu|commit|branch|merge|rebase)\b",
        "obsidian vault ops": r"\b(obsidian|vault|note|markdown|wikilink|frontmatter)\b",
        "claude code config": r"\b(claude\.md|skill|hook|agent|mcp|claude code|settings\.json)\b",
        "debugging": r"\b(debug|error|fix|broken|fail|traceback|exception)\b",
        "python development": r"\b(python|uv|pip|pytest|pyproject|\.py)\b",
        "infrastructure/devops": r"\b(terraform|pulumi|aws|docker|k8s|kubernetes|ci|cd|deploy)\b",
        "web/api development": r"\b(api|endpoint|fastapi|flask|express|frontend|react|nextjs)\b",
        "3D printing": r"\b(voron|klipper|printer|filament|slicer|gcode|shake.tune)\b",
        "resume/job search": r"\b(resume|job|interview|application|cover.letter|linkedin)\b",
        "tmux/terminal": r"\b(tmux|terminal|zellij|ghostty|iterm)\b",
        "starship prompt": r"\b(starship|prompt|starship\.toml)\b",
        "homebrew packages": r"\b(brew|homebrew|cask)\b",
        "linear/project management": r"\b(linear|issue|project.manage|ticket|sprint)\b",
        "todoist/task management": r"\b(todoist|task|todo|due.date|priority)\b",
        "anki/learning": r"\b(anki|flashcard|spaced.repetition|memorize)\b",
        "home automation": r"\b(home.assistant|ha|zigbee|mqtt|automation|sensor|entity)\b",
    }

    for label, pattern in patterns.items():
        if re.search(pattern, combined):
            goals.append(label)

    if not goals:
        goals.append("general/other")

    return goals


def classify_prompt(text: str) -> list[str]:
    """Classify a single history prompt into workflow categories."""
    return classify_goal([text])


def is_recent(date_range: tuple | None, cutoff: datetime) -> bool:
    if not date_range:
        return False
    return date_range[1] >= cutoff


def _band(value: float, edges=(15, 40, 70)) -> str:
    """Directional band for a 0-100 index. Heuristic thresholds, not calibrated."""
    lo, mid, hi = edges
    if value < lo:
        return "Low"
    if value < mid:
        return "Moderate"
    if value < hi:
        return "Elevated"
    return "High"


def analyze_temperature(analyzed: list[dict], cutoff: datetime, examples: int = 6) -> list[str]:
    """Build the Temperature / Tone report section.

    Measures the user's register across all analyzed sessions on three axes:
    terseness (message length), heat (friction: profanity, strong corrections,
    shouting, exclamations), and warmth (affect: gratitude, praise, politeness,
    collaboration). Emits rate tables, directional indices, a per-project and
    monthly breakdown, and real quoted examples per loaded category.
    """
    import statistics

    # Flatten to one record per authored message, tagged with date/project/month.
    msgs = []
    for s in analyzed:
        date = s["date_range"][0] if s.get("date_range") else None
        recent = is_recent(s.get("date_range"), cutoff)
        for raw in s.get("user_messages", []):
            # compaction summaries are already dropped in extract_user_text
            clean = clean_for_tone(raw)
            if not clean:
                continue  # pure code/url paste — no authored register
            msgs.append({
                "clean": clean,
                "project": s["project"],
                "date": date,
                "month": date.strftime("%Y-%m") if date else "unknown",
                "recent": recent,
                "words": len(clean.split()),
            })

    lines: list[str] = []
    lines.append("## 5. Temperature / Tone")
    lines.append("")
    lines.append("*Your authored register across all sessions — terseness, heat (friction), "
                 "and warmth (affect). Code blocks, inline code, and URLs are stripped before "
                 "matching, so markers reflect words you chose, not pasted material.*")
    lines.append("")

    if not msgs:
        lines.append("_No authored messages found._")
        lines.append("")
        return lines

    n = len(msgs)

    def flag(pat):
        return sum(1 for m in msgs if pat.search(m["clean"]))

    def is_shout(m):
        # short, multi-word, all-caps, enough letters — a genuine shout not an acronym
        if m["words"] < 2 or len(m["clean"]) > 60:
            return False
        letters = [c for c in m["clean"] if c.isalpha()]
        return len(letters) >= 6 and bool(SHOUT_PATTERN.match(m["clean"]))

    # Strong corrections attributed per-message so we can quote them.
    strong_msgs = [m for m in msgs if STRONG_CORRECTION_PATTERNS.search(m["clean"])]
    soft_msgs = [m for m in msgs if not STRONG_CORRECTION_PATTERNS.search(m["clean"])
                 and SOFT_CORRECTION_PATTERNS.search(m["clean"])]
    prof_msgs = [m for m in msgs if PROFANITY_PATTERN.search(m["clean"])]
    praise_msgs = [m for m in msgs if PRAISE_PATTERN.search(m["clean"])]
    grat_msgs = [m for m in msgs if GRATITUDE_PATTERN.search(m["clean"])]
    shout_msgs = [m for m in msgs if is_shout(m)]

    counts = {
        "gratitude": len(grat_msgs),
        "praise": len(praise_msgs),
        "politeness": flag(POLITENESS_PATTERN),
        "collaboration": flag(COLLAB_PATTERN),
        "hedging": flag(HEDGE_PATTERN),
        "questions": sum(1 for m in msgs if "?" in m["clean"]),
        "exclamations": sum(1 for m in msgs if EXCLAIM_PATTERN.search(m["clean"])),
        "profanity": len(prof_msgs),
        "strong corrections": len(strong_msgs),
        "soft corrections": len(soft_msgs),
        "shouting": len(shout_msgs),
    }

    def rate(k):  # per 1000 messages
        return 1000.0 * counts[k] / n

    # --- Terseness ---
    wc = [m["words"] for m in msgs]
    buckets = {"1-3": 0, "4-10": 0, "11-30": 0, "31-80": 0, "80+": 0}
    for w in wc:
        if w <= 3: buckets["1-3"] += 1
        elif w <= 10: buckets["4-10"] += 1
        elif w <= 30: buckets["11-30"] += 1
        elif w <= 80: buckets["31-80"] += 1
        else: buckets["80+"] += 1
    median_w = statistics.median(wc)
    terse_share = 100.0 * (buckets["1-3"] + buckets["4-10"]) / n

    # --- Directional indices (heuristic weights; treat as direction, not score) ---
    # Warmth = affect only (gratitude/praise/politeness). Collaboration ("we/let's")
    # is deliberately EXCLUDED — it's normal technical framing, not affect, and
    # including it saturated the index. It's reported as its own marker instead.
    heat = min(100, rate("profanity") * 8 + rate("strong corrections") * 4
               + rate("shouting") * 4 + rate("exclamations") * 1.5)
    warmth = min(100, rate("gratitude") * 5 + rate("praise") * 1.5
                 + rate("politeness") * 0.4)

    lines.append(f"Analyzed **{n:,} authored messages**.")
    lines.append("")
    lines.append("| Axis | Index (0-100, directional) | Band |")
    lines.append("|------|---------------------------|------|")
    lines.append(f"| Heat (friction/intensity) | {heat:.0f} | {_band(heat)} |")
    lines.append(f"| Warmth (affect) | {warmth:.0f} | {_band(warmth)} |")
    lines.append(f"| Terseness (median words/msg) | {median_w:.0f} | "
                 f"{terse_share:.0f}% of msgs are <=10 words |")
    lines.append("")
    lines.append("*Indices are heuristic weighted sums of the marker rates below — directional, "
                 "not calibrated. Lead with the raw rates and quoted examples. Collaboration "
                 "framing (we/let's) is intentionally NOT counted as warmth.*")
    lines.append("")

    lines.append("### Length distribution")
    lines.append("")
    lines.append("| Words | Messages | Share |")
    lines.append("|-------|----------|-------|")
    for b, c in buckets.items():
        lines.append(f"| {b} | {c:,} | {100.0*c/n:.0f}% |")
    lines.append("")

    lines.append("### Marker rates (per 1,000 messages)")
    lines.append("")
    lines.append("| Marker | Count | Rate |")
    lines.append("|--------|-------|------|")
    for k in ["gratitude", "praise", "politeness", "collaboration", "hedging",
              "questions", "exclamations", "profanity", "strong corrections",
              "soft corrections", "shouting"]:
        lines.append(f"| {k} | {counts[k]:,} | {rate(k):.1f} |")
    lines.append("")

    # --- Per-project ---
    proj_msgs: dict[str, list] = defaultdict(list)
    for m in msgs:
        proj_msgs[m["project"]].append(m)
    top_projects = sorted(proj_msgs.items(), key=lambda kv: len(kv[1]), reverse=True)[:10]
    lines.append("### By project (top 10 by volume)")
    lines.append("")
    lines.append("| Project | Msgs | Median words | Profanity/1k | Strong corr/1k | Praise/1k |")
    lines.append("|---------|------|-------------|-------------|---------------|-----------|")
    for proj, pm in top_projects:
        pn = len(pm)
        pmed = statistics.median([m["words"] for m in pm])
        pprof = 1000.0 * sum(1 for m in pm if PROFANITY_PATTERN.search(m["clean"])) / pn
        pstrong = 1000.0 * sum(1 for m in pm if STRONG_CORRECTION_PATTERNS.search(m["clean"])) / pn
        ppraise = 1000.0 * sum(1 for m in pm if PRAISE_PATTERN.search(m["clean"])) / pn
        lines.append(f"| {proj} | {pn:,} | {pmed:.0f} | {pprof:.1f} | {pstrong:.1f} | {ppraise:.1f} |")
    lines.append("")

    # --- Monthly trend ---
    month_msgs: dict[str, list] = defaultdict(list)
    for m in msgs:
        month_msgs[m["month"]].append(m)
    lines.append("### Monthly trend")
    lines.append("")
    lines.append("| Month | Msgs | Median words | Heat idx | Warmth idx |")
    lines.append("|-------|------|-------------|----------|-----------|")
    for month in sorted(k for k in month_msgs if k != "unknown"):
        mm = month_msgs[month]
        mn = len(mm)
        def mrate(pat):
            return 1000.0 * sum(1 for m in mm if pat.search(m["clean"])) / mn
        mshout = 1000.0 * sum(1 for m in mm if is_shout(m)) / mn
        mexcl = 1000.0 * sum(1 for m in mm if EXCLAIM_PATTERN.search(m["clean"])) / mn
        mheat = min(100, mrate(PROFANITY_PATTERN) * 8 + mrate(STRONG_CORRECTION_PATTERNS) * 4
                    + mshout * 4 + mexcl * 1.5)
        mwarm = min(100, mrate(GRATITUDE_PATTERN) * 5 + mrate(PRAISE_PATTERN) * 1.5
                    + mrate(POLITENESS_PATTERN) * 0.4)
        mmed = statistics.median([m["words"] for m in mm])
        lines.append(f"| {month} | {mn:,} | {mmed:.0f} | {mheat:.0f} | {mwarm:.0f} |")
    lines.append("")

    # --- Examples per loaded category ---
    def quote(sample, header):
        if not sample:
            return
        lines.append(f"### {header}")
        lines.append("")
        seen = set()
        shown = 0
        for m in sorted(sample, key=lambda x: (x["date"] or datetime.min.replace(tzinfo=timezone.utc)), reverse=True):
            key = m["clean"][:80]
            if key in seen:
                continue
            seen.add(key)
            d = m["date"].strftime("%Y-%m-%d") if m["date"] else "unknown"
            txt = " ".join(m["clean"].split())[:200]
            lines.append(f'- **[{d}] {m["project"]}** — *"{txt}"*')
            shown += 1
            if shown >= examples:
                break
        lines.append("")

    quote(prof_msgs, f"Profanity examples ({len(prof_msgs)})")
    quote(shout_msgs, f"Shouting examples ({len(shout_msgs)})")
    quote(strong_msgs, f"Strong-correction examples ({len(strong_msgs)})")
    quote(praise_msgs, f"Praise examples ({len(praise_msgs)})")
    quote(grat_msgs, f"Gratitude examples ({len(grat_msgs)})")

    lines.append("> **Caveat:** markers are lexical, not semantic. Cleaning removes code/URLs "
                 "but not everything — pasted agent output the user reintroduces as prose can "
                 "still register, and 'great'/'nice' catch some non-praise uses. Treat rates as "
                 "directional and read the quoted examples to confirm the qualitative read.")
    lines.append("")
    return lines


def generate_report(
    sessions: list[dict],
    skipped: list[dict],
    history_entries: list[dict],
) -> str:
    """Generate the markdown report."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=RECENT_DAYS)

    analyzed = [s for s in sessions if not s.get("skipped")]

    # Determine date range from both sources
    jsonl_dates = [s["date_range"] for s in analyzed if s.get("date_range")]
    history_dates = [e["date"] for e in history_entries] if history_entries else []

    all_earliest = []
    all_latest = []
    if jsonl_dates:
        all_earliest.append(min(d[0] for d in jsonl_dates))
        all_latest.append(max(d[1] for d in jsonl_dates))
    if history_dates:
        all_earliest.append(min(history_dates))
        all_latest.append(max(history_dates))

    if all_earliest:
        date_range_str = f"{min(all_earliest).strftime('%Y-%m-%d')} to {max(all_latest).strftime('%Y-%m-%d')}"
    else:
        date_range_str = "unknown"

    lines: list[str] = []
    lines.append("# Claude Code Conversation Analysis")
    lines.append("")
    lines.append("## Metadata")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Date range covered | {date_range_str} |")
    lines.append(f"| Conversation files analyzed | {len(analyzed)} |")
    lines.append(f"| Conversation files skipped | {len(skipped)} |")
    lines.append(f"| History prompts (history.jsonl) | {len(history_entries)} |")
    lines.append(f"| Report generated | {now.strftime('%Y-%m-%d %H:%M UTC')} |")
    lines.append(f"| Recent window | last {RECENT_DAYS} days |")
    lines.append("")

    # Data source note
    jsonl_start = min(d[0] for d in jsonl_dates).strftime("%Y-%m-%d") if jsonl_dates else "N/A"
    history_start = min(history_dates).strftime("%Y-%m-%d") if history_dates else "N/A"
    lines.append(f"> **Note:** Full conversation JSONL files start at {jsonl_start}. "
                 f"User prompt history goes back to {history_start}. "
                 f"Sections 1-2 use history.jsonl for full coverage. "
                 f"Sections 3-4 require JSONL (tool calls, corrections).")
    lines.append("")

    skip_reasons = Counter(s.get("reason", "unknown") for s in skipped)
    if skip_reasons:
        lines.append("### Skip Reasons")
        lines.append("")
        for reason, count in skip_reasons.most_common():
            lines.append(f"- **{reason}:** {count} sessions")
        lines.append("")

    # =========================================================
    # Section 1: Common Goals & Workflows (from history.jsonl)
    # =========================================================
    lines.append("## 1. Common Goals & Workflows")
    lines.append("")
    lines.append("*Source: history.jsonl (all user prompts)*")
    lines.append("")

    # Group history entries by month + workflow
    monthly_goals: dict[str, Counter] = defaultdict(Counter)
    goal_entries: dict[str, list] = defaultdict(list)
    goal_projects: dict[str, Counter] = defaultdict(Counter)

    for entry in history_entries:
        month = entry["date"].strftime("%Y-%m")
        goals = classify_prompt(entry["text"])
        for g in goals:
            monthly_goals[month][g] += 1
            goal_entries[g].append(entry)
            goal_projects[g][entry["project"]] += 1

    # Overall frequency table
    goal_totals = Counter()
    goal_recent = Counter()
    goal_last_seen: dict[str, datetime] = {}
    for g, entries in goal_entries.items():
        goal_totals[g] = len(entries)
        for e in entries:
            if e["date"] >= cutoff:
                goal_recent[g] += 1
            if g not in goal_last_seen or e["date"] > goal_last_seen[g]:
                goal_last_seen[g] = e["date"]

    lines.append("| Workflow | Total Prompts | Recent (30d) | Last Seen | Top Projects |")
    lines.append("|----------|--------------|-------------|-----------|-------------|")

    for goal, total in goal_totals.most_common():
        recent = goal_recent.get(goal, 0)
        last = goal_last_seen[goal].strftime("%Y-%m-%d")
        top_projs = ", ".join(
            f"{p} ({c})" for p, c in goal_projects[goal].most_common(3) if p
        )
        flag = " **\u2606**" if recent > 0 else ""
        lines.append(f"| {goal}{flag} | {total} | {recent} | {last} | {top_projs} |")

    lines.append("")
    lines.append("*\u2606 = active in last 30 days*")
    lines.append("")

    # Monthly trend heatmap for top 10 workflows
    lines.append("### Monthly Trend (top 10 workflows)")
    lines.append("")
    months_sorted = sorted(monthly_goals.keys())
    top_goals = [g for g, _ in goal_totals.most_common(10)]

    header = "| Workflow | " + " | ".join(m[-5:] for m in months_sorted) + " |"
    sep = "|----------|" + "|".join("-----" for _ in months_sorted) + "|"
    lines.append(header)
    lines.append(sep)
    for g in top_goals:
        cells = []
        for m in months_sorted:
            count = monthly_goals[m].get(g, 0)
            cells.append(str(count) if count > 0 else ".")
        lines.append(f"| {g} | " + " | ".join(cells) + " |")
    lines.append("")

    # --- Project Activity (from history.jsonl) ---
    lines.append("### Project Activity")
    lines.append("")

    project_entries: dict[str, list] = defaultdict(list)
    for entry in history_entries:
        if entry["project"]:
            project_entries[entry["project"]].append(entry)

    lines.append("| Project | Total Prompts | Recent (30d) | First Seen | Last Active |")
    lines.append("|---------|--------------|-------------|------------|-------------|")

    project_sorted = sorted(project_entries.items(), key=lambda x: -len(x[1]))
    for proj, entries in project_sorted[:25]:
        total = len(entries)
        recent = sum(1 for e in entries if e["date"] >= cutoff)
        first = min(e["date"] for e in entries).strftime("%Y-%m-%d")
        last = max(e["date"] for e in entries).strftime("%Y-%m-%d")
        lines.append(f"| {proj} | {total} | {recent} | {first} | {last} |")

    lines.append("")

    # =========================================================
    # Section 2: One-off Scripts (from JSONL)
    # =========================================================
    lines.append("## 2. One-Off Scripts Generated")
    lines.append("")

    all_scripts = []
    script_paths_seen = Counter()
    for s in analyzed:
        for script in s.get("scripts_generated", []):
            all_scripts.append({
                **script,
                "session_id": s["session_id"],
                "project": s["project"],
                "date": s["date_range"][0].strftime("%Y-%m-%d") if s.get("date_range") else "unknown",
                "recent": is_recent(s.get("date_range"), cutoff),
            })
            script_paths_seen[script["path"]] += 1

    if all_scripts:
        reused = {p for p, c in script_paths_seen.items() if c > 1}
        lines.append(f"Total scripts detected: **{len(all_scripts)}**")
        lines.append(f"Unique paths: **{len(script_paths_seen)}**")
        lines.append(f"Reused across sessions: **{len(reused)}**")
        lines.append("")

        lines.append("| Script Path | Project | Date | Reused? | Size |")
        lines.append("|-------------|---------|------|---------|------|")
        for script in sorted(all_scripts, key=lambda x: x["date"], reverse=True)[:50]:
            path_short = script["path"].replace(str(Path.home()), "~")
            is_reused = "\u2713" if script["path"] in reused else ""
            recent_marker = " **\u2606**" if script["recent"] else ""
            lines.append(
                f"| `{path_short}` | {script['project']}{recent_marker} | {script['date']} | {is_reused} | {script['size']:,}b |"
            )
        lines.append("")
    else:
        lines.append("*No standalone scripts detected.*")
        lines.append("")

    # =========================================================
    # Section 3: Tool/Skill/Agent Invocations (from JSONL)
    # =========================================================
    lines.append("## 3. Repeated Tool, Skill & Agent Invocations")
    lines.append("")

    all_tools: Counter = Counter()
    recent_tools: Counter = Counter()
    all_skills: Counter = Counter()
    recent_skills: Counter = Counter()
    all_agents: Counter = Counter()
    recent_agents: Counter = Counter()

    for s in analyzed:
        recent = is_recent(s.get("date_range"), cutoff)
        for t in s.get("tool_calls", []):
            all_tools[t] += 1
            if recent:
                recent_tools[t] += 1
        for sk in s.get("skill_invocations", []):
            all_skills[sk] += 1
            if recent:
                recent_skills[sk] += 1
        for ag in s.get("agent_launches", []):
            all_agents[ag] += 1
            if recent:
                recent_agents[ag] += 1

    # Skills
    lines.append("### Skills")
    lines.append("")
    if all_skills:
        lines.append("| Skill | Total | Recent (30d) |")
        lines.append("|-------|-------|-------------|")
        for skill, count in all_skills.most_common(30):
            recent = recent_skills.get(skill, 0)
            flag = " **\u2606**" if recent > 0 else ""
            lines.append(f"| {skill}{flag} | {count} | {recent} |")
        lines.append("")
    else:
        lines.append("*No skill invocations found.*")
        lines.append("")

    # Agents
    lines.append("### Subagent Types")
    lines.append("")
    if all_agents:
        lines.append("| Agent Type | Total | Recent (30d) |")
        lines.append("|------------|-------|-------------|")
        for agent, count in all_agents.most_common(20):
            recent = recent_agents.get(agent, 0)
            flag = " **\u2606**" if recent > 0 else ""
            lines.append(f"| {agent}{flag} | {count} | {recent} |")
        lines.append("")
    else:
        lines.append("*No subagent launches found.*")
        lines.append("")

    # MCP tools
    lines.append("### MCP Tools")
    lines.append("")
    mcp_tools = {k: v for k, v in all_tools.items() if k.startswith("mcp__")}
    if mcp_tools:
        mcp_sorted = sorted(mcp_tools.items(), key=lambda x: -x[1])
        lines.append("| MCP Tool | Total | Recent (30d) |")
        lines.append("|----------|-------|-------------|")
        for tool, count in mcp_sorted[:30]:
            recent = recent_tools.get(tool, 0)
            # Keys here are already filtered to the MCP prefix, so strip it, then
            # strip the connector segment that hosted servers add on top of it.
            short_name = tool.removeprefix("mcp__").removeprefix("claude_ai_")
            flag = " **\u2606**" if recent > 0 else ""
            lines.append(f"| `{short_name}`{flag} | {count} | {recent} |")
        lines.append("")
    else:
        lines.append("*No MCP tool calls found.*")
        lines.append("")

    # Core tools
    lines.append("### Core Tools (top 15)")
    lines.append("")
    core_tools = {k: v for k, v in all_tools.items() if not k.startswith("mcp__")}
    if core_tools:
        core_sorted = sorted(core_tools.items(), key=lambda x: -x[1])
        lines.append("| Tool | Total | Recent (30d) |")
        lines.append("|------|-------|-------------|")
        for tool, count in core_sorted[:15]:
            recent = recent_tools.get(tool, 0)
            flag = " **\u2606**" if recent > 0 else ""
            lines.append(f"| {tool}{flag} | {count} | {recent} |")
        lines.append("")
    else:
        lines.append("*No core tool calls found.*")
        lines.append("")

    # =========================================================
    # Section 4: Correction Patterns (from JSONL + history.jsonl)
    # =========================================================
    lines.append("## 4. Correction Patterns")
    lines.append("")
    lines.append("*Detects where you corrected, redirected, or clarified Claude's actions.*")
    lines.append("")

    # Collect corrections from JSONL sessions (have context)
    jsonl_corrections = []
    for s in analyzed:
        for c in s.get("corrections", []):
            jsonl_corrections.append({
                **c,
                "project": s["project"],
                "date": s["date_range"][0].strftime("%Y-%m-%d") if s.get("date_range") else "unknown",
                "recent": is_recent(s.get("date_range"), cutoff),
            })

    # Collect corrections from history.jsonl (broader date range, no context)
    history_corrections = []
    for entry in history_entries:
        corrs = detect_corrections(entry["text"])
        for c in corrs:
            history_corrections.append({
                **c,
                "user_text": entry["text"][:300],
                "prev_assistant": "",
                "project": entry["project"],
                "date": entry["date"].strftime("%Y-%m-%d"),
                "recent": entry["date"] >= cutoff,
            })

    all_corrections = jsonl_corrections + history_corrections

    # Summary stats
    strong = [c for c in all_corrections if c["tier"] == "strong"]
    soft = [c for c in all_corrections if c["tier"] == "soft"]
    recent_strong = [c for c in strong if c["recent"]]
    recent_soft = [c for c in soft if c["recent"]]

    lines.append("### Summary")
    lines.append("")
    lines.append("| Type | Total | Recent (30d) |")
    lines.append("|------|-------|-------------|")
    lines.append(f"| Strong corrections (explicit disagreement) | {len(strong)} | {len(recent_strong)} |")
    lines.append(f"| Soft corrections (clarification/redirect) | {len(soft)} | {len(recent_soft)} |")
    lines.append(f"| **Total** | **{len(all_corrections)}** | **{len(recent_strong) + len(recent_soft)}** |")
    lines.append("")

    # Theme breakdown
    theme_counter: Counter = Counter()
    theme_recent: Counter = Counter()
    theme_projects: dict[str, Counter] = defaultdict(Counter)
    for c in all_corrections:
        for theme in c["themes"]:
            theme_counter[theme] += 1
            if c["recent"]:
                theme_recent[theme] += 1
            theme_projects[theme][c["project"]] += 1

    lines.append("### Correction Themes")
    lines.append("")
    lines.append("| Theme | Total | Recent (30d) | Top Projects |")
    lines.append("|-------|-------|-------------|-------------|")
    for theme, count in theme_counter.most_common():
        recent = theme_recent.get(theme, 0)
        top_projs = ", ".join(
            f"{p} ({c})" for p, c in theme_projects[theme].most_common(3) if p
        )
        flag = " **\u2606**" if recent > 0 else ""
        lines.append(f"| {theme}{flag} | {count} | {recent} | {top_projs} |")
    lines.append("")

    # Monthly correction trend
    monthly_corrections: Counter = Counter()
    for c in all_corrections:
        monthly_corrections[c["date"][:7]] += 1

    if monthly_corrections:
        lines.append("### Monthly Correction Trend")
        lines.append("")
        lines.append("| Month | Corrections | Prompts | Rate |")
        lines.append("|-------|------------|---------|------|")
        monthly_prompts: Counter = Counter()
        for entry in history_entries:
            monthly_prompts[entry["date"].strftime("%Y-%m")] += 1

        for month in sorted(monthly_corrections.keys()):
            corr = monthly_corrections[month]
            prompts = monthly_prompts.get(month, 0)
            rate = f"{corr / prompts * 100:.1f}%" if prompts > 0 else "?"
            lines.append(f"| {month} | {corr} | {prompts} | {rate} |")
        lines.append("")

    # Project correction rates
    project_corr_count: Counter = Counter()
    project_prompt_count: Counter = Counter()
    for c in all_corrections:
        project_corr_count[c["project"]] += 1
    for entry in history_entries:
        project_prompt_count[entry["project"]] += 1

    lines.append("### Correction Rate by Project")
    lines.append("")
    lines.append("| Project | Corrections | Prompts | Rate |")
    lines.append("|---------|------------|---------|------|")
    for proj, corr in project_corr_count.most_common(15):
        prompts = project_prompt_count.get(proj, 0)
        rate = f"{corr / prompts * 100:.1f}%" if prompts > 0 else "?"
        lines.append(f"| {proj} | {corr} | {prompts} | {rate} |")
    lines.append("")

    # Detailed examples: strong corrections (deduplicated by user text)
    lines.append("### Strong Correction Examples (most recent 20)")
    lines.append("")
    strong_sorted = sorted(strong, key=lambda x: x["date"], reverse=True)
    seen_texts = set()
    shown = 0
    for c in strong_sorted:
        if shown >= 20:
            break
        text_key = c["user_text"][:100]
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)
        themes_str = ", ".join(c["themes"])
        lines.append(f"- **[{c['date']}] {c['project']}** ({themes_str})")
        # Clean up the user text for display
        user_text = c["user_text"].replace("\n", " ").strip()[:200]
        shown += 1
        lines.append(f"  - User: *\"{user_text}\"*")
        if c.get("prev_assistant"):
            prev = c["prev_assistant"].replace("\n", " ").strip()[:150]
            lines.append(f"  - Claude had said: *\"{prev}\"*")
    lines.append("")

    # Soft correction examples (deduplicated)
    lines.append("### Soft Correction Examples (most recent 15)")
    lines.append("")
    soft_sorted = sorted(soft, key=lambda x: x["date"], reverse=True)
    seen_texts = set()
    shown = 0
    for c in soft_sorted:
        if shown >= 15:
            break
        text_key = c["user_text"][:100]
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)
        themes_str = ", ".join(c["themes"])
        lines.append(f"- **[{c['date']}] {c['project']}** ({themes_str})")
        user_text = c["user_text"].replace("\n", " ").strip()[:200]
        shown += 1
        lines.append(f"  - *\"{user_text}\"*")
    lines.append("")

    # =========================================================
    # Section 5: Temperature / Tone
    # =========================================================
    lines.extend(analyze_temperature(analyzed, cutoff))

    return "\n".join(lines)


def main():
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--temperature", action="store_true",
                    help="Emit ONLY the Temperature / Tone section to stdout "
                         "(skips history.jsonl parsing and the full report file).")
    ap.add_argument("--examples", type=int, default=6,
                    help="Quoted examples per category in the temperature section (default 6).")
    args = ap.parse_args()

    if not PROJECTS_DIR.exists():
        print(f"Error: {PROJECTS_DIR} does not exist", file=sys.stderr)
        sys.exit(1)

    if args.temperature:
        _run_temperature_only(args.examples)
        return

    # Parse history.jsonl (lightweight, full date range)
    print("Parsing history.jsonl...")
    history_entries = parse_history_file()
    print(f"  {len(history_entries)} prompt entries")
    if history_entries:
        earliest = min(e["date"] for e in history_entries)
        latest = max(e["date"] for e in history_entries)
        print(f"  Date range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")

    # Parse JSONL conversation files
    conversation_files = []
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        for jsonl_file in project_dir.glob("*.jsonl"):
            conversation_files.append(jsonl_file)

    print(f"Parsing {len(conversation_files)} conversation files...")

    sessions = []
    skipped = []
    for i, filepath in enumerate(conversation_files):
        if (i + 1) % 50 == 0:
            print(f"  Processing {i + 1}/{len(conversation_files)}...")
        result = parse_session(filepath)
        if result is None:
            skipped.append({"session_id": filepath.stem, "reason": "parse error"})
        elif result.get("skipped"):
            skipped.append(result)
        else:
            sessions.append(result)

    print(f"  Analyzed: {len(sessions)}, Skipped: {len(skipped)}")

    report = generate_report(sessions, skipped, history_entries)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"conversation-analysis-{today}.md"
    output_path.write_text(report)
    print(f"\nReport written to {output_path}")


def _run_temperature_only(examples: int):
    """Fast path for the temperature skill: parse sessions, emit just Section 5."""
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=RECENT_DAYS)

    files = [f for d in sorted(PROJECTS_DIR.iterdir()) if d.is_dir()
             for f in d.glob("*.jsonl")]
    print(f"Parsing {len(files)} conversation files...", file=sys.stderr)
    analyzed = []
    for i, filepath in enumerate(files):
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(files)}...", file=sys.stderr)
        result = parse_session(filepath)
        if result and not result.get("skipped"):
            analyzed.append(result)
    print(f"  Analyzed {len(analyzed)} sessions.", file=sys.stderr)

    print("\n".join(analyze_temperature(analyzed, cutoff, examples=examples)))


if __name__ == "__main__":
    main()

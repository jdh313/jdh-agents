---
name: conversation-temperature
description: >-
  Use when the user asks about their own tone, register, temperature, or
  demeanor across their Claude Code sessions — "what's my temperature", "how do
  I come across to you", "am I too harsh/terse/blunt", "analyze my tone", "have
  I gotten warmer/colder over time", "do I run hotter in one project". Analyzes
  the user's authored messages across all local transcripts and returns an
  evidence-led read of terseness, heat (friction), and warmth (affect), grounded
  in real quoted examples. NOT for operational retrospection (what am I working
  on, where do I correct Claude — that is the full conversation-analysis
  report), and NOT for analyzing anyone other than the local user.
---

# Conversation Temperature

Read the user's *authored register* across their whole Claude Code history — how they come across, in evidence, not vibes. Three axes: **terseness** (message length), **heat** (friction/intensity: profanity, strong corrections, shouting, exclamations), **warmth** (affect: gratitude, praise, politeness). Collaboration framing (`we`/`let's`) is reported but deliberately not scored as warmth — it is normal technical speech.

**Core principle:** lead with raw marker rates and *quoted real messages*; the composite indices are heuristic and directional. If the numbers and the examples disagree, the examples win.

## How to run

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/conversation-temperature/scripts/conversation-analysis.py" --temperature --examples 6
```

- The script is bundled with this skill; stdlib-only, read-only, no network calls. If `${CLAUDE_PLUGIN_ROOT}` does not expand in your runtime, locate `skills/conversation-temperature/scripts/conversation-analysis.py` inside the installed plugin directory and run that path. `python3` works in place of `uv run` on Python 3.13+.
- Reads every transcript under `~/.claude/projects/*/` (all projects, ~200+ files; takes a minute). Progress goes to stderr; the markdown report goes to stdout.
- `--examples N` sets quoted examples per category (default 6).
- The tone logic lives in `analyze_temperature()` in that script; the same section (`## 5. Temperature / Tone`) is also included in the full report when the script runs with no flags. That no-flag run writes a dated markdown file to `.docs/` under the current working directory instead of printing.

## Interpreting the output

The report gives you, in order: an index table (Heat / Warmth / Terseness with directional bands), a length distribution, **marker rates per 1,000 messages**, a per-project breakdown, a monthly trend, and quoted examples per loaded category (profanity, shouting, strong corrections, praise, gratitude).

- **Anchor on the marker-rate table and the examples**, not the indices. Bands (Low/Moderate/Elevated/High) use uncalibrated thresholds — treat them as arrows, not scores.
- **Near-zero rates are signal.** Gratitude ~0, profanity ~0, shouting ~0 is a real, cool-and-even reading — not missing data.
- **Per-project and monthly are the "zoom" axes** — answer "hotter in acmeos than dotfiles?" and "warmer since June?" straight from those tables.

## The contamination caveat (always surface it)

Markers are **lexical, not semantic**, and the corpus is noisy. The script already filters auto-compaction summaries (`Primary Request and Intent` recaps) and strips code blocks / inline code / URLs before matching. But it cannot catch everything: pasted agent output, Slack threads, or ticket bodies the user reintroduces as prose can still register as their words, and `great`/`nice` catch some non-praise uses. So:

- **Read the quoted examples before asserting anything** — a category count is only as good as its examples. Downgrade any rate whose examples are mostly pasted content.
- State the caveat in the delivered read; report exact counts as *soft*.

## Delivering the read

Verdict-first (dense labeled shape): open with a one-clause temperature verdict, then a compressed "why" grounded in the rates, then quote 2-4 real examples that confirm it, then the caveat. Offer the per-project / over-time cuts as follow-ups if not already central to the ask.

## When NOT to use

- Operational retrospection (goals, tool/skill usage, where the user corrects Claude) → run the full report (no flag), whose other sections cover that.
- Analyzing a specific single conversation's tone → just read that transcript directly.
- Anyone other than the local user — this only sees local transcripts.

---
name: shake-tune:shake-tune
description: >-
  Use when the user says "/shake-tune", "analyze shake tune", "interpret my
  shake tune results", "read my shaper graphs", "check my belt comparison",
  "what do my vibration graphs show", "diagnose printer vibration", or
  "shake tune results". Interprets Klippain Shake Tune PNG graphs for 3D
  printers — diagnoses issues, explains findings, recommends fixes, and
  tracks results over time.
argument-hint: "[results-directory]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Write
  - AskUserQuestion
---

# /shake-tune — Interpret Shake Tune Results

Analyze Klippain Shake Tune graphs for 3D printers. Reads PNG outputs using multimodal vision, diagnoses issues, explains findings in plain language, and recommends mechanical or firmware fixes. Supports all 5 test types: belt comparison, input shaper, vibration profile, axes map, and excitation.

## Flow

Execute these steps in order. Keep the conversation practical — printer tuning should feel approachable, not academic.

### Step 1: Locate Results Directory

Ask the user for the path to their Shake Tune results:

> Where are your Shake Tune results? Provide the directory path (e.g., `~/printer_data/config/ShakeTune_results/`)

If the user provides a path, verify it exists. If not found, suggest common locations:
- `~/printer_data/config/ShakeTune_results/`
- `~/printer_data/config/K-ShakeTune_results/`

### Step 2: Detect Available Tests

Use glob patterns from `references/file-detection.md` to find all available test PNGs.

Search for each test type:
- `**/beltscomparison_*.png` → Belt comparison
- `**/inputshaper_*_x.png` → Input shaper X
- `**/inputshaper_*_y.png` → Input shaper Y
- `**/vibrations_profile_*.png` → Vibration profile
- `**/axesmap_*.png` → Axes map
- `**/staticfreq_*.png` → Excitation test

Group results by session (timestamps within 5 minutes = same session) per `references/file-detection.md`.

Present findings:

> Found [N] test results across [M] sessions:
>
> **Latest session (YYYY-MM-DD HH:MM):**
> - Belt comparison
> - Input shaper (X and Y)
> - Vibration profile
>
> **Previous session (YYYY-MM-DD HH:MM):**
> - Belt comparison
> - Input shaper (X and Y)

### Step 3: Load Printer Profile

Check for a printer profile per `references/printer-profiles.md`:
1. Look for `.shake-tune-profile.json` in the parent of the results directory
2. Fall back to `.shake-tune-profile.json` in the results directory itself

**If found:** Load and confirm: "Loaded profile for [printer_name] ([kinematics])."

**If not found:** Offer to create one:

> No printer profile found. A profile helps me give more specific advice. Want to set one up? (Takes 30 seconds — I'll ask 5 questions.)

If user declines, proceed without profile. Analysis still works — recommendations are just more generic.

### Step 4: Select Scope

Based on what was detected, ask the user what they want to analyze:

**If single session with multiple tests:**
> Want me to analyze all tests from this session, or focus on a specific one?

**If multiple sessions:**
> Want me to analyze the latest session, compare sessions, or look at a specific test?

**If single PNG:**
Skip this step — analyze the one file.

### Step 5: Analyze Tests

For each selected test, use the Read tool to view the PNG and apply the interpretation framework from the corresponding agent's reference file.

**Analysis order** (when multiple tests selected):
1. Axes map (if present) — validates accelerometer setup
2. Belt comparison (if present) — checks mechanical foundation
3. Input shaper X, then Y — calibrates motion system
4. Vibration profile (if present) — validates speed ranges
5. Excitation (if present) — targeted investigation

**For each test:**

1. **Read the PNG** using the Read tool (multimodal vision)
2. **Load the reference patterns** from the corresponding file in `references/`:
   - Belt: `references/belt-patterns.md`
   - Shaper: `references/shaper-patterns.md`
   - Vibration: `references/vibration-patterns.md`
   - Axes map: `references/axes-map-patterns.md`
3. **Apply printer profile context** if available (see `references/printer-profiles.md` § How Profiles Influence Analysis)
4. **Present findings** using this structure:

```
### [Test Name]

**Reading:** [1-2 sentences describing what the graph shows]

**Assessment:** [Good / Acceptable / Needs attention / Problem detected]

**Key observations:**
- [Observation 1]
- [Observation 2]

**Recommendations:**
- [Action 1 — specific and actionable]
- [Action 2]
```

If the assessment is "Good", keep recommendations brief or skip them: "No action needed — this looks solid."

### Step 6: Synthesize Combined Assessment

After analyzing all selected tests, provide a combined summary:

```
## Summary

**Overall printer health:** [Brief assessment]

**Priority actions:**
1. [Most important fix — what and why]
2. [Second priority]
3. [Third priority, if any]

**Klipper config changes** (if applicable):
```ini
[input_shaper]
shaper_freq_x: XX.X
shaper_type_x: mzv
shaper_freq_y: XX.X
shaper_type_y: mzv
```

**What to test next:**
- [Recommended follow-up test or print test]
```

Only include config changes if input shaper results were analyzed. Only include "what to test next" if there are actionable follow-ups.

### Step 7: Offer Historical Tracking

After analysis is complete:

> Want me to save a summary of these results? I'll store it in a `.shake-tune-history/` directory alongside your results for future comparison.

**If user agrees:**
- Create `.shake-tune-history/` in the results directory (if it doesn't exist)
- Write a markdown summary file: `.shake-tune-history/YYYY-MM-DD_summary.md`

Summary format:
```markdown
# Shake Tune Summary — YYYY-MM-DD

**Printer:** [name from profile, or "Unknown"]
**Tests analyzed:** [list]

## Results

### [Test 1]
- Assessment: [rating]
- Key finding: [1-liner]

### [Test 2]
...

## Recommendations
1. [Priority 1]
2. [Priority 2]

## Config Applied
[Klipper config snippet if applicable, or "No changes recommended"]
```

**If previous summaries exist:** Mention them: "I see a previous summary from [date]. Want me to compare changes?"

## Edge Cases

| Situation | Behavior |
|-----------|----------|
| No PNG files found | "No Shake Tune results found in that directory. Check the path, or run a test first with `COMPARE_BELTS_RESPONSES` or `AXES_SHAPER_CALIBRATION`." |
| Only raw .stdata files, no PNGs | "I found raw data files but no PNG graphs. Run the Shake Tune post-processing macro to generate the graphs, then point me at the results." |
| Single PNG provided directly | Skip Steps 1-4. Detect test type from filename, analyze immediately. |
| Corrupted or unreadable PNG | "I can't read this graph clearly. It may be corrupted — try regenerating it from the raw data." |
| Multiple sessions, same day | Differentiate by time: "Session 1 (09:30) vs Session 2 (14:15)" |
| User asks about a specific test type | Skip to that test's analysis. Read the relevant agent reference for interpretation. |
| Profile says cartesian, belt comparison found | Note the inconsistency: "Belt comparison is typically for CoreXY printers. Your profile says cartesian — is the kinematics type correct?" |
| Results directory is remote (SSH path) | "I can only read local files. Copy the results to a local directory first, or paste the specific PNGs." |

## What This Skill Does NOT Do

- Parse raw .stdata or .csv accelerometer data (requires Python decompression)
- Run Shake Tune macros on the printer
- Modify Klipper configuration files directly
- Connect to the printer or Moonraker API
- Make changes without user confirmation
- Guarantee specific print quality outcomes

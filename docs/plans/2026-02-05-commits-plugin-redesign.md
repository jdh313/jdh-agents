# Commits Plugin Redesign

> Refactor `atomic-commits` into `commits` — decouple commit message format from VCS operations, modernize to skills-only structure.

## Problem

The `atomic-commits` plugin couples three concerns:
1. **VCS detection** (git vs jj)
2. **Atomic commit splitting** (grouping changes into logical units)
3. **Conventional Commits formatting** (hardcoded as the only message format)

This is problematic because different repos use different commit conventions. The plugin forces conventional commits even when the repo doesn't use them.

## Design

### Detection Hierarchy

The skill uses a unified detection flow for both VCS and commit format:

```
1. CLAUDE.md context (already loaded in agent context)
   ├── VCS mentioned? (jj / git) → use it
   └── Commit style mentioned? (conventional / freeform) → use it

2. VCS fallback (if not in CLAUDE.md):
   └── [[ -d .jj ]] → jj, otherwise → git

3. Commit format fallback (if not in CLAUDE.md):
   └── Analyze last ~20 commits from log
       ├── >60% have type prefixes (feat:, fix:, etc.) → conventional
       └── otherwise → freeform
```

No CLAUDE.md parsing code needed — the agent already has it in context. The skill just instructs: "Check what the repo's CLAUDE.md says about VCS and commit style before falling back to auto-detection."

### Plugin Rename

`atomic-commits` → `commits`

- Slash commands become: `/commits:commit`, `/commits:split`, `/commits:review`
- Plugin directory: `plugins/commits/`

### Structure Migration

**Before (atomic-commits):**
```
plugins/atomic-commits/
├── .claude-plugin/plugin.json
├── commands/
│   ├── commit.md
│   ├── split.md
│   └── review.md
├── skills/atomic-commits/
│   ├── SKILL.md
│   └── references/
│       ├── conventional-commits.md
│       ├── git-workflow.md
│       └── jj-workflow.md
└── README.md
```

**After (commits):**
```
plugins/commits/
├── .claude-plugin/plugin.json
├── skills/
│   ├── commits/
│   │   ├── SKILL.md                    # Main skill (auto-invoked for commit requests)
│   │   └── references/
│   │       ├── conventional-commits.md  # Kept as-is
│   │       ├── freeform-commits.md      # New
│   │       ├── git-workflow.md          # Kept as-is
│   │       └── jj-workflow.md           # Kept as-is
│   ├── commit/
│   │   └── SKILL.md                    # Was commands/commit.md
│   ├── split/
│   │   └── SKILL.md                    # Was commands/split.md
│   └── review/
│       └── SKILL.md                    # Was commands/review.md
├── README.md
└── (no commands/ directory)
```

### Skill Changes

#### Main skill (`skills/commits/SKILL.md`)

- Remove all hardcoded "Angular/Conventional Commits" language
- Add detection section at the top:
  1. Check CLAUDE.md context for VCS type and commit style
  2. If VCS unknown, detect via `.jj` directory check
  3. If commit style unknown, analyze recent commits
- Workflows reference "the detected format" and load the appropriate reference file
- Safety rules section stays unchanged

#### Commit skill (`skills/commit/SKILL.md`)

- Previously `commands/commit.md`
- Add frontmatter: `disable-model-invocation: true` (user invokes via `/commits:commit`)
- Replace "Read conventional-commits.md" with "Read the appropriate format reference based on detected commit style"

#### Split skill (`skills/split/SKILL.md`)

- Previously `commands/split.md`
- Same frontmatter updates
- Same format-neutral language

#### Review skill (`skills/review/SKILL.md`)

- Previously `commands/review.md`
- Evaluates messages against the detected format, not always conventional
- For freeform repos: checks clarity, imperative mood, conciseness — skips type prefix checks

### New Reference: `freeform-commits.md`

Covers:
- Imperative mood ("Add feature" not "Added feature")
- Clear, specific summary
- Optional body for context (WHY not WHAT)
- No type prefix required
- No rigid structure beyond clarity and conciseness
- Examples of good freeform messages

### What Stays the Same

- All VCS reference files (git-workflow.md, jj-workflow.md)
- Conventional commits reference
- Safety rules (forbidden destructive operations, confirmation for discards)
- Atomic commit principles (one purpose, complete, independent, logical order)
- PostToolUse hook for destructive command detection

## Implementation Steps

1. Create `plugins/commits/` directory with new structure
2. Move and adapt `SKILL.md` (main skill) — remove hardcoded conventional commits, add detection flow
3. Convert `commands/commit.md` → `skills/commit/SKILL.md` with updated frontmatter
4. Convert `commands/split.md` → `skills/split/SKILL.md` with updated frontmatter
5. Convert `commands/review.md` → `skills/review/SKILL.md` with updated frontmatter
6. Create `references/freeform-commits.md`
7. Copy VCS references unchanged
8. Update `plugin.json` (rename, bump version to 2.0.0)
9. Update README.md
10. Delete `plugins/atomic-commits/`
11. Run sync + validate + lint
12. Verify the plugin installs and works

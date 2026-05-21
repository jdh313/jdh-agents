---
name: review
description: Review and improve a commit message for compliance with the repo's commit style. Opportunistically peeks at the working-tree diff to verify the message matches the actual change.
argument-hint: "[message]"
disable-model-invocation: true
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Bash(test:*)
  - Read
  - Grep
  - Glob
---

# Review Commit Message Command

## Instructions

### Step 1: Receive Message

User's message: $ARGUMENTS

If no message was provided, ask the user for their draft commit message.

### Step 2: Detect Commit Style

Run the canonical algorithm in `skills/commits/references/detection.md` to determine commit style (conventional/freeform). It reads CLAUDE.md for explicit declarations and auto-detects from recent commits otherwise.

Then load the matching style reference named in that file.

### Step 3: Opportunistically Peek at the Diff

Style-only review can only catch surface issues. A real review checks whether the message's claims match the actual change. Try to read the diff:

**For git:**
```bash
git diff --staged 2>/dev/null | head -200    # prefer staged
# If empty:
git diff 2>/dev/null | head -200             # fall back to unstaged
```

**For jj:**
```bash
jj diff 2>/dev/null | head -200              # working-copy change
```

**If the diff is empty or unavailable** (not in a repo, no changes, command errored), skip to Step 4 with style-only review and note that no diff was visible.

**If the diff is available**, use it to check:

- **Type match (conventional)**: Does `feat:` actually add behavior? Does `fix:` actually fix something? Does `refactor:` actually preserve behavior?
- **Scope honesty**: Does the message claim what the diff actually does? `fix: resolve memory leak` on a diff that only adds tests is a mismatch.
- **Specificity opportunities**: If the diff touches one specific function or module, the message can name it instead of saying "auth code".
- **Hidden bundling**: Does the diff actually contain multiple atomic units? If so, recommend `/commits:split` instead of approving the message.

Do not paste the diff back at the user — just use it as context for sharper feedback.

### Step 4: Analyze Against Detected Style

**Universal checks (both styles):**
- [ ] Purpose immediately clear?
- [ ] Imperative mood? ("add" not "added" or "adds")
- [ ] Concise and specific? (not vague like "update stuff")
- [ ] Body (if present) explains WHY, not just WHAT?
- [ ] Body is concise (max 5 lines)?
- [ ] No `Co-Authored-By:` footer? (house style — strip if present)
- [ ] No trailing period on summary?
- [ ] No issue numbers in summary? (those go in the PR description)

**Additional checks for conventional style:**
- [ ] Has proper type? (feat, fix, chore, docs, style, refactor, perf, test, build, ci, revert)
- [ ] Type is appropriate for the change? (verify against the diff if visible)
- [ ] Lowercase?

**Common issues to flag:**
- Past tense: `added feature` → `add feature`
- Vague: `update stuff` → `update user authentication logic`
- Wrong type (conventional only): `feat: fix bug` → `fix: resolve memory leak`
- No type when repo uses conventional: `added new endpoint` → `feat: add user endpoint`
- Unnecessary type when repo uses freeform: `feat: add login` → `Add login flow`
- Co-Authored-By footer: strip it
- Diff mismatch (only with visible diff): "the message says `fix:` but the diff is pure refactor — suggest `refactor:`"

### Step 5: Provide Feedback

**Original message:**
```
[user's message]
```

**Issues identified:**
- [list specific problems; if diff was visible, cite mismatches concretely]

**Improved version:**
```
[improved message in the detected style]
```

**Changes made:**
- [explain each change and why]

If a diff was visible and the message claim doesn't match the diff, flag this prominently — it's the highest-value catch of this skill.

### Step 6: Offer to Commit (Optional)

If the user wants to proceed with the improved message, ask if they'd like to create the commit now.

If yes, detect VCS and execute:
- **jj**: `jj commit -m "<improved message>"` (describes @ and creates new empty change)
- **git**: `git commit -m "<improved message>"` (assumes changes are already staged)

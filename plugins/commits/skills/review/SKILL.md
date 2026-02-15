---
name: review
description: Review and improve a commit message for compliance with the repo's commit style
argument-hint: "[message]"
disable-model-invocation: true
allowed-tools:
  - Read
---

# Review Commit Message Command

## Instructions

### Step 1: Receive Message

User's message: $ARGUMENTS

If no message was provided, ask the user for their draft commit message.

### Step 2: Detect Commit Style

Determine the repo's commit convention:

1. **Check CLAUDE.md context** — does the repo specify a commit style (conventional/freeform)?
2. **Style fallback:** Analyze the last ~20 commits — if >60% have type prefixes like `feat:`, `fix:`, etc., use conventional style; otherwise use freeform

Read the appropriate format reference:
- **Conventional:** Read `skills/commits/references/conventional-commits.md`
- **Freeform:** Read `skills/commits/references/freeform-commits.md`

### Step 3: Analyze Against Detected Style

**Universal checks (both styles):**
- [ ] Purpose immediately clear?
- [ ] Imperative mood? ("add" not "added" or "adds")
- [ ] Concise and specific? (not vague like "update stuff")
- [ ] Body (if present) explains WHY, not just WHAT?
- [ ] Body is concise (max 5 lines)?

**Additional checks for conventional style:**
- [ ] Has proper type? (feat, fix, chore, docs, style, refactor, perf, test, build, ci, revert)
- [ ] Type is appropriate for the change?
- [ ] Lowercase?
- [ ] No period at end of summary?

**Common issues to flag:**
- Past tense: "added feature" -> "add feature"
- Vague: "update stuff" -> "update user authentication logic"
- Wrong type (conventional only): "feat: fix bug" -> "fix: resolve memory leak"
- No type when repo uses conventional: "added new endpoint" -> "feat: add user endpoint"
- Unnecessary type when repo uses freeform: "feat: add login" -> "Add login flow"

### Step 4: Provide Feedback

**Original message:**
```
[user's message]
```

**Issues identified:**
- [list specific problems]

**Improved version:**
```
[improved message in the detected style]
```

**Changes made:**
- [explain each change and why]

### Step 5: Offer to Commit (Optional)

If the user wants to proceed with the improved message, ask if they'd like to create the commit now.

If yes, detect VCS and execute:
- **jj**: `jj describe -m "<improved message>"` then `jj new`
- **git**: `git commit -m "<improved message>"` (assumes changes are staged)

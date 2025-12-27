---
description: Review and improve a commit message for conventional commits compliance
argument-hint: "[message]"
allowed-tools:
  - Read
---

# Review Commit Message Command

## Instructions

### Step 1: Receive Message

User's message: $ARGUMENTS

If no message was provided, ask the user for their draft commit message.

### Step 2: Analyze Against Standards

Read `skills/atomic-commits/references/conventional-commits.md` for the full specification.

Evaluate the message:

**Format compliance:**
- [ ] Has proper type? (feat, fix, chore, docs, style, refactor, perf, test, build, ci, revert)
- [ ] Type is appropriate for the change?
- [ ] Imperative mood? ("add" not "added" or "adds")
- [ ] Lowercase?
- [ ] No period at end of summary?

**Clarity assessment:**
- [ ] Purpose immediately clear?
- [ ] Summary explains WHAT changed?
- [ ] Body (if present) explains WHY, not just WHAT?
- [ ] Body is concise (max 5 lines)?

**Common issues to flag:**
- Past tense: "added feature" -> "add feature"
- Vague: "update stuff" -> "update user authentication logic"
- Wrong type: "feat: fix bug" -> "fix: resolve memory leak"
- No type: "added new endpoint" -> "feat: add user endpoint"
- Uppercase/period: "Fix: Added Feature." -> "fix: add feature"

### Step 3: Provide Feedback

**Original message:**
```
[user's message]
```

**Issues identified:**
- [list specific problems]

**Improved version:**
```
<type>: <improved summary>

[optional improved body]
```

**Changes made:**
- [explain each change and why]

### Step 4: Offer to Commit (Optional)

If the user wants to proceed with the improved message, ask if they'd like to create the commit now.

If yes, detect VCS and execute:
- **jj**: `jj describe -m "<improved message>"` then `jj new`
- **git**: `git commit -m "<improved message>"` (assumes changes are staged)

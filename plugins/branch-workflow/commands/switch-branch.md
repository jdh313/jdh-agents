---
description: Switch to an existing branch (git) or change (jj) with safety checks for uncommitted changes
argument-hint: <branch-name>
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Switch Branch/Change

Switches to an existing branch in git or an existing change in jj with automatic VCS detection and safety checks for uncommitted changes.

## Immediate Execution

**VCS:** !`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS shown above, follow these steps to switch to an existing branch or change.

### Step 1: List Available Branches/Changes

Display the list of available branches or changes for the user to select from.

**For git (if detected above):**
```bash
git branch -a
```

This will show all local branches (with `*` indicating the current branch) and remote branches (prefixed with `remotes/`).

**For jj (if detected above):**
```bash
jj log --limit 20
```

This will show the 20 most recent changes with their IDs and descriptions, ordered from newest to oldest.

### Step 2: Prompt User for Selection

Present the user with a clear prompt to select which branch or change they want to switch to:

```
Select a branch or change to switch to:
- For git: Enter the branch name (e.g., main, develop, feature-login)
- For jj: Enter the change ID from the list above (e.g., abcd1234)
```

### Step 3: Check for Uncommitted Changes (Git Only)

Before switching, check if there are any uncommitted changes in git repositories.

**For git only:**
```bash
git status --porcelain
```

If this command returns any output (indicating uncommitted changes):

1. **Warn the user:**
   ```
   ⚠️  WARNING: You have uncommitted changes in your current branch
   ```

2. **Show the uncommitted changes:**
   ```bash
   git status
   ```

3. **Offer options:**
   ```
   You have the following options:
   a) Stash changes (git stash) and switch branch
   b) Commit changes first and then switch
   c) Cancel switch operation

   Which option would you like? (a/b/c)
   ```

4. **If user selects (a) - Stash:**
   ```bash
   git stash push -m "WIP: before switching to <branch-name>"
   ```
   Then proceed with the switch in Step 4.

5. **If user selects (b) - Commit first:**
   ```
   Please commit your changes first using your preferred commit tool, then run this command again.
   ```
   Exit without switching.

6. **If user selects (c) - Cancel:**
   ```
   Switch operation cancelled.
   ```
   Exit without switching.

**For jj:**
jj automatically tracks all changes, so there's no need to check for uncommitted work. Proceed directly to Step 4.

### Step 4: Execute Switch Command

Switch to the selected branch or change.

**For git:**
```bash
git checkout <branch-name>
```

Replace `<branch-name>` with the branch name selected by the user in Step 2.

**For jj:**
```bash
jj edit <change-id>
```

Replace `<change-id>` with the change ID selected by the user in Step 2.

### Step 5: Verify Switch

Display the current status to confirm the switch was successful:

**For git:**
```bash
git status
```

**For jj:**
```bash
jj status
```

### Step 6: Show Success Message

Display a success message indicating:
- The branch/change that was switched to
- The VCS that was used (git or jj)
- The current branch/change identifier

Example output:

```
✓ Successfully switched to branch 'develop' in git
  You are now on: develop

OR

✓ Successfully switched to change 'abcd1234' in jj
  Current change: abcd1234 - feature description
  Parents: efgh5678
```

### Step 7: Show Stash Message (Git Only, If Stashed)

If changes were stashed in Step 3, show a reminder:

```
ℹ️  Your changes were stashed. Retrieve them later with:
    git stash pop
    or
    git stash list  (to see all stashes)
```

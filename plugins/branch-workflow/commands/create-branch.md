---
description: Create a new branch (git) or change (jj) with proper naming validation
allowed-tools:
  - Bash(git:*)
  - Bash(jj:*)
  - Read
---

# Create Branch/Change

Creates a new branch in git or a new change in jj with automatic VCS detection and naming validation.

## Immediate Execution

**VCS:** !`[[ -d .jj ]] && echo "jj" || echo "git"`

**Current Status:**
!`if [[ -d .jj ]]; then jj status; else git status; fi`

## Instructions

Based on the detected VCS shown above, follow these steps to create a new branch or change.

### Step 1: Get Branch/Change Name

Prompt the user for a branch or change name with the following guidance:

```
Enter branch/change name (kebab-case, no spaces):
- Use lowercase letters, numbers, and hyphens
- Example: feature-login-page, bugfix-null-pointer
- Avoid spaces, underscores, UPPERCASE
```

### Step 2: Validate the Name

Validate the provided name against kebab-case pattern:
- Must contain only lowercase letters (a-z), numbers (0-9), and hyphens (-)
- Cannot contain spaces, underscores, uppercase letters, or special characters
- Cannot start or end with a hyphen
- Must be at least 1 character long

If validation fails, inform the user and ask them to provide a valid name.

### Step 3: Create Branch or Change

**For git (if detected above):**
```bash
git checkout -b <name>
```

Replace `<name>` with the validated branch name from Step 1.

**For jj (if detected above):**
```bash
jj new -m "<name>"
```

Replace `<name>` with the validated change name from Step 1.

### Step 4: Verify Creation

Display the current status to confirm the branch/change was created successfully:

**For git:**
```bash
git status
```

**For jj:**
```bash
jj status
```

### Step 5: Show Success Message

Display a success message indicating:
- The branch/change name that was created
- The VCS that was used (git or jj)
- The current branch/change ID (from the status output)

Example output:
```
Created new branch 'feature-login-page' in git
  You are now on: feature-login-page

OR

Created new change 'bugfix-null-pointer' in jj
  Current change ID: <hash>
```

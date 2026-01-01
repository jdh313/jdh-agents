# PRD: VCS Tools - Phase 3

**Contract**: ./contract.md
**Phase**: 3 of 4
**Focus**: Merge, rebase, and conflict resolution automation

## Phase Overview

Phase 3 addresses the most complex and error-prone VCS workflow: integrating changes through merging and rebasing while handling conflicts. This phase creates the `merge-workflow` plugin to automate common merge/rebase operations and provide guided conflict resolution, significantly reducing the cognitive load and risk associated with these operations.

This phase is sequenced after review prep because merge/rebase operations benefit from the patterns established in Phases 1-2: VCS auto-detection, non-interactive command patterns, and diff analysis capabilities. The complexity of conflict resolution justifies a dedicated phase with focused testing and iteration.

The plugin recognizes fundamental differences between git and jj conflict handling: git treats conflicts as blocking states requiring immediate resolution, while jj treats conflicts as first-class objects that can persist and evolve. The plugin will embrace each system's philosophy while providing a consistent user experience.

## User Stories

1. As a developer starting work on a feature, I want to rebase my branch on latest main so that I avoid conflicts later
2. As a developer with conflicts, I want guided resolution steps so that I don't have to remember conflict marker syntax
3. As a developer using jj, I want to leverage jj's automatic rebasing so that my changes stay up-to-date without manual intervention
4. As a developer finishing a feature, I want to merge to main with a clear merge commit message so that history is readable
5. As a developer resolving conflicts, I want to see what changed on both sides so that I can make informed decisions
6. As a developer using jj, I want to work with conflicts as normal files so that I can commit partial resolutions and iterate

## Functional Requirements

### Branch/Change Rebase

- **FR-3.1**: For git: Check if branch needs rebasing (commits behind main/master)
- **FR-3.2**: For git: Execute non-interactive rebase (`git rebase origin/main --no-edit`)
- **FR-3.3**: For jj: Execute rebase with automatic conflict handling (`jj rebase -d main`)
- **FR-3.4**: Detect if conflicts occurred during rebase
- **FR-3.5**: If conflicts: invoke conflict resolution workflow (FR-3.11+)
- **FR-3.6**: If successful: show updated commit graph/change history

### Merge Operations

- **FR-3.7**: For git: Execute merge with commit message (`git merge <branch> -m "<message>" --no-edit`)
- **FR-3.8**: For git: Support fast-forward merges when possible
- **FR-3.9**: For jj: Merge changes with description (`jj merge <change-id> -m "<message>"`)
- **FR-3.10**: Detect conflicts and invoke resolution workflow

### Conflict Detection

- **FR-3.11**: For git: Parse `git status` for conflict markers
- **FR-3.12**: For git: List conflicted files with conflict count
- **FR-3.13**: For jj: Detect conflicts via `jj status` and `jj diff`
- **FR-3.14**: Categorize conflicts (content conflicts vs. delete conflicts vs. rename conflicts)
- **FR-3.15**: Show conflict summary with affected files and conflict types

### Guided Conflict Resolution

- **FR-3.16**: Present conflicts one file at a time
- **FR-3.17**: For each conflict, show:
  - Current branch/change version (ours)
  - Incoming branch/change version (theirs)
  - Common ancestor version (base) if available
  - Context lines around conflict
- **FR-3.18**: Offer resolution strategies:
  - Accept ours (keep current version)
  - Accept theirs (take incoming version)
  - Manual edit (open file for editing)
  - Show full diff (display entire file with conflicts)
- **FR-3.19**: For git: Mark resolved files (`git add <file>`)
- **FR-3.20**: For jj: Conflicts remain in working copy until explicitly resolved
- **FR-3.21**: After all conflicts resolved:
  - For git: Continue rebase/merge (`git rebase --continue` or `git merge --continue`)
  - For jj: Describe resolution and create new change
- **FR-3.22**: Verify resolution succeeded (no remaining conflicts)

### Abort/Rollback

- **FR-3.23**: Allow user to abort merge/rebase at any time
- **FR-3.24**: For git: Execute abort command (`git rebase --abort` or `git merge --abort`)
- **FR-3.25**: For jj: Abandon conflict resolution change
- **FR-3.26**: Verify repository returned to pre-operation state

## Non-Functional Requirements

- **NFR-3.1**: Conflict detection must complete in under 2 seconds even with 100+ conflicted files
- **NFR-3.2**: All merge/rebase operations must use non-interactive modes
- **NFR-3.3**: Plugin must safely handle partial conflict resolution (some files resolved, others not)
- **NFR-3.4**: Conflict resolution UI must work in Claude Code's text-based interface
- **NFR-3.5**: Plugin must preserve uncommitted work when aborting operations

## Dependencies

### Prerequisites

- Phase 1 complete (shared VCS references, branch management patterns)
- Phase 2 complete (diff analysis functions for showing conflict context)
- Understanding of git conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`)
- Understanding of jj's conflict-as-files model

### Outputs for Next Phase

- Conflict detection patterns that could be used for pre-merge validation
- Diff analysis enhancements that benefit history investigation (Phase 4)
- Rebase workflows that inform change stack management

## Acceptance Criteria

- [ ] merge-workflow plugin created with symlink to shared-references/
- [ ] Can rebase git branches on main non-interactively
- [ ] Can rebase jj changes with automatic conflict handling
- [ ] Can merge branches/changes with custom messages
- [ ] Detects conflicts in both git and jj repositories
- [ ] Lists all conflicted files with conflict types
- [ ] Provides guided resolution for content conflicts
- [ ] Can abort merge/rebase and return to clean state
- [ ] Marks files as resolved in git after manual edits
- [ ] Verifies no conflicts remain after resolution
- [ ] All operations complete without interactive prompts
- [ ] Plugin works in both git and jj repositories

## Open Questions

- Should we support three-way merge tools (vimdiff, meld) or stay text-based?
- How should we handle binary file conflicts (take ours/theirs only)?
- Should we integrate with git rerere (reuse recorded resolution)?
- For jj, should we provide workflows for evolving conflicted changes?

---

*Review this PRD and provide feedback before spec generation.*

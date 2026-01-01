# PRD: VCS Tools - Phase 1

**Contract**: ./contract.md
**Phase**: 1 of 4
**Focus**: Shared VCS foundation and branch/change management automation

## Phase Overview

Phase 1 establishes the foundational infrastructure for all VCS plugins while delivering immediate value through branch/change management automation. This phase creates the shared VCS reference documentation structure (git-commands.md, jj-commands.md) that all subsequent plugins will use via symlinks, reducing maintenance overhead and ensuring consistency.

The `branch-workflow` plugin is chosen as the first functional plugin because branch/change management is a straightforward workflow with clear success criteria, making it ideal for establishing dual VCS support patterns. Users will immediately benefit from automated branch creation, context switching, and cleanup—common daily operations that currently require verbose manual commands.

This phase de-risks future phases by validating the shared documentation approach and non-interactive command patterns before tackling more complex workflows like merge/rebase and conflict resolution.

## User Stories

1. As a developer using jj, I want to create a new change with proper naming so that I can start feature work without remembering jj command syntax
2. As a developer using git, I want to create and switch to a feature branch with one command so that I don't have to remember the multi-step git workflow
3. As a developer switching between jj and git projects, I want the plugin to auto-detect which VCS I'm using so that I don't have to specify it manually
4. As a developer finishing feature work, I want to clean up old branches/changes with guided selection so that my repository stays organized
5. As a plugin maintainer, I want VCS command references in one shared location so that updating command patterns doesn't require editing multiple plugin files

## Functional Requirements

### Shared VCS Reference Documentation

- **FR-1.1**: Create `shared-references/` directory in cc-marketplace root containing git-commands.md and jj-commands.md
- **FR-1.2**: Document git command patterns for branch operations (create, switch, list, delete, cleanup)
- **FR-1.3**: Document jj command patterns for change operations (new, describe, list, abandon)
- **FR-1.4**: Include non-interactive flags and patterns to prevent agent prompts (--no-edit, -m, etc.)
- **FR-1.5**: Create symlinks from plugin directories to shared-references/ following documented pattern

### VCS Auto-Detection

- **FR-1.6**: Implement VCS detection logic: `[[ -d .jj ]] && echo "jj" || echo "git"`
- **FR-1.7**: Load appropriate command reference based on detected VCS
- **FR-1.8**: Display detected VCS to user for verification

### Branch/Change Creation

- **FR-1.9**: Prompt user for branch/change name with validation (kebab-case, no spaces)
- **FR-1.10**: For git: create and checkout branch (`git checkout -b <name>`)
- **FR-1.11**: For jj: create new change with description (`jj new -m "<name>"`)
- **FR-1.12**: Verify creation and show status

### Branch/Change Switching

- **FR-1.13**: List available branches/changes for selection
- **FR-1.14**: For git: checkout selected branch (`git checkout <name>`)
- **FR-1.15**: For jj: edit selected change (`jj edit <change-id>`)
- **FR-1.16**: Handle uncommitted changes safely (warn user, offer stash for git)

### Branch/Change Cleanup

- **FR-1.17**: List branches/changes eligible for cleanup (merged, old, abandoned)
- **FR-1.18**: Allow multi-select for batch deletion
- **FR-1.19**: For git: delete selected branches (`git branch -d <name>`, -D for unmerged)
- **FR-1.20**: For jj: abandon selected changes (`jj abandon <change-id>`)
- **FR-1.21**: Confirm deletion before execution
- **FR-1.22**: Show cleanup summary (what was deleted)

## Non-Functional Requirements

- **NFR-1.1**: All VCS commands must complete in under 5 seconds for typical repositories
- **NFR-1.2**: Plugin must never trigger interactive mode (use --no-edit, -m flags, etc.)
- **NFR-1.3**: Shared reference documentation must be accessible via symlinks across all plugins
- **NFR-1.4**: Error messages must clearly distinguish between git and jj errors
- **NFR-1.5**: Plugin must work in repositories with 100+ branches/changes without performance degradation

## Dependencies

### Prerequisites

- cc-marketplace repository structure exists
- atomic-commits plugin available as reference for VCS patterns
- Claude Code supports symlinks in plugins (verified from documentation)

### Outputs for Next Phase

- Shared VCS reference documentation (shared-references/git-commands.md, shared-references/jj-commands.md)
- Established symlink pattern for other plugins to follow
- Validated non-interactive command patterns
- branch-workflow plugin as reference implementation for dual VCS support

## Acceptance Criteria

- [ ] shared-references/ directory exists with git-commands.md and jj-commands.md
- [ ] branch-workflow plugin has symlink to shared-references/
- [ ] Plugin correctly detects git vs jj in test repositories
- [ ] Can create branches (git) and changes (jj) with proper naming
- [ ] Can list and switch between branches/changes
- [ ] Can clean up multiple old branches/changes in one operation
- [ ] No commands trigger interactive mode during agent execution
- [ ] Plugin works in both git and jj repositories without modification
- [ ] Reference documentation is DRY (no duplication of command patterns)
- [ ] All plugin commands complete successfully in test repositories

## Open Questions

- Should branch naming follow a specific convention (feature/, bugfix/, etc.) or allow free-form?
- For jj cleanup, should we also handle obsolete changes (changes with no descendants)?
- Should the plugin integrate with branch protection rules (e.g., prevent deletion of main/master)?

---

*Review this PRD and provide feedback before spec generation.*

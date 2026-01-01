# PRD: VCS Tools - Phase 2

**Contract**: ./contract.md
**Phase**: 2 of 4
**Focus**: Code review preparation automation (PR descriptions, commit cleanup, diff analysis)

## Phase Overview

Phase 2 tackles one of the most time-consuming weekly workflows: preparing code for review. This phase creates the `review-prep` plugin to automate PR description generation, commit history cleanup, and diff analysis—tasks that developers currently perform manually before every code review submission.

This phase builds on the foundation established in Phase 1, leveraging the shared VCS reference documentation and dual support patterns. By addressing code review prep now (before merge/rebase workflows), we deliver high-impact value early while keeping complexity manageable. The plugin will help users generate comprehensive PR descriptions from commit messages and diffs, clean up messy commit histories (squash, reorder, split), and review all changes before submission.

The phase recognizes that code review preparation differs between git and jj: git requires interactive rebase for history cleanup, while jj uses `jj squash` and `jj describe` for simpler workflows. The plugin will abstract these differences while respecting each VCS's idioms.

## User Stories

1. As a developer finishing feature work, I want to generate a PR description from my commits so that I don't have to manually summarize what changed
2. As a developer with messy commit history, I want to squash related commits into logical units so that reviewers see clean, atomic commits
3. As a developer preparing for code review, I want to see all my changes in one summary so that I can verify nothing is missing
4. As a developer using jj, I want to easily update change descriptions to match my final implementation so that the history reflects reality
5. As a developer using git, I want to reorder commits into a logical sequence without entering interactive rebase so that the PR tells a clear story

## Functional Requirements

### PR Description Generation

- **FR-2.1**: Analyze all commits/changes in current branch/change
- **FR-2.2**: Extract commit messages and generate structured PR description with:
  - Summary of what changed (1-2 sentences)
  - Bulleted list of key changes grouped by area
  - Technical details section if warranted
  - Testing notes if tests were modified
- **FR-2.3**: Include diff statistics (files changed, lines added/removed)
- **FR-2.4**: Format output in markdown suitable for GitHub/GitLab
- **FR-2.5**: Allow user to review and edit before copying to clipboard

### Commit History Cleanup (Git)

- **FR-2.6**: Show current commit history for the branch
- **FR-2.7**: Identify commits that could be squashed (e.g., "fixup!" commits, related changes)
- **FR-2.8**: Allow user to select commits to squash together
- **FR-2.9**: Execute non-interactive rebase to squash selected commits (`git rebase -i --autosquash`)
- **FR-2.10**: Allow commit reordering via numbered list (executes rebase with new order)
- **FR-2.11**: Verify rebase succeeded and show updated history

### Change Description Update (jj)

- **FR-2.12**: Show current change description
- **FR-2.13**: Suggest improved description based on diff content
- **FR-2.14**: Allow user to update description (`jj describe -m "new description"`)
- **FR-2.15**: Handle change squashing (`jj squash` for combining changes)
- **FR-2.16**: Show change evolution after updates

### Diff Analysis

- **FR-2.17**: Generate comprehensive diff summary showing:
  - All modified files grouped by directory
  - New files created
  - Deleted files
  - Renamed/moved files
- **FR-2.18**: Highlight potentially risky changes (large files, config changes, dependencies)
- **FR-2.19**: Show file-by-file diffs for review
- **FR-2.20**: For git: include both unstaged and staged changes
- **FR-2.21**: For jj: show diff against parent change
- **FR-2.22**: Calculate and display impact metrics (files changed, churn, complexity)

## Non-Functional Requirements

- **NFR-2.1**: PR description generation must complete in under 10 seconds for branches with 50+ commits
- **NFR-2.2**: All rebase/squash operations must use non-interactive modes
- **NFR-2.3**: Plugin must handle branches that diverged significantly from main (100+ commits behind)
- **NFR-2.4**: Diff analysis must work with repositories containing 1000+ files
- **NFR-2.5**: Plugin must safely abort operations if conflicts are detected during rebase

## Dependencies

### Prerequisites

- Phase 1 complete (shared VCS references available)
- Established symlink pattern from Phase 1
- Understanding of non-interactive git rebase (`--autosquash`, `--no-edit`)
- Knowledge of jj change descriptions and squash operations

### Outputs for Next Phase

- Reusable diff analysis functions that Phase 3 can use for conflict detection
- Commit history manipulation patterns that inform merge/rebase workflows
- PR description templates that could be extended for changelog generation

## Acceptance Criteria

- [ ] review-prep plugin created with symlink to shared-references/
- [ ] Can generate PR descriptions from git branches and jj changes
- [ ] Can squash multiple git commits non-interactively
- [ ] Can update jj change descriptions based on diff analysis
- [ ] Can reorder git commits without entering interactive mode
- [ ] Diff analysis shows all modified, new, deleted, and renamed files
- [ ] Diff analysis highlights risky changes (configs, dependencies)
- [ ] All operations complete without triggering interactive prompts
- [ ] Plugin works in both git and jj repositories
- [ ] Generated PR descriptions are formatted in valid markdown

## Open Questions

- Should PR descriptions follow a specific template (conventional changelog format?)
- How should we handle commits with no messages or generic messages like "wip"?
- For git interactive rebase, should we support fixup vs squash distinction?
- Should diff analysis include code complexity metrics (cyclomatic complexity)?

---

*Review this PRD and provide feedback before spec generation.*

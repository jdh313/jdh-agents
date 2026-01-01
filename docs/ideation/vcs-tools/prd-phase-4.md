# PRD: VCS Tools - Phase 4

**Contract**: ./contract.md
**Phase**: 4 of 4
**Focus**: History investigation and analysis (bisect, evolution, branch comparison)

## Phase Overview

Phase 4 completes the VCS tools suite by addressing history investigation workflows—tools for understanding code evolution, finding when bugs were introduced, and comparing divergent branches. This phase creates the `history-detective` plugin to automate common debugging and analysis tasks that currently require complex command sequences.

This phase is sequenced last because it's independent of the other workflows and less time-critical than daily operations like branch management, code review prep, and conflict resolution. However, when debugging production issues or understanding unfamiliar code, these tools become invaluable for reducing time-to-resolution.

The plugin leverages git bisect for binary search through history, git log for evolution analysis, and branch comparison tools for understanding divergence. For jj, it uses jj log with revsets and jj evolog for tracking change evolution—a powerful feature unique to jj that can reveal how code changed over time through automatic rebasing.

## User Stories

1. As a developer debugging a regression, I want to find the exact commit that introduced a bug so that I can understand what broke and why
2. As a developer reading unfamiliar code, I want to see how a file evolved over time so that I understand the design decisions
3. As a developer comparing branches, I want to see what diverged between my feature branch and main so that I can plan integration
4. As a developer using jj, I want to track change evolution through rebases so that I can see how my implementation changed in response to feedback
5. As a developer investigating authorship, I want to see who changed specific lines and when so that I can ask the right person for context

## Functional Requirements

### Git Bisect Automation

- **FR-4.1**: For git: Initiate bisect with good and bad commits (`git bisect start <bad> <good>`)
- **FR-4.2**: For git: Support automated bisect with test command (`git bisect run <test-command>`)
- **FR-4.3**: For git: Support manual bisect (user marks each commit as good/bad)
- **FR-4.4**: Display current commit being tested with diff summary
- **FR-4.5**: Track bisect progress (commits remaining to test)
- **FR-4.6**: When culprit found, show full commit details (message, diff, author, date)
- **FR-4.7**: Support bisect abort and reset (`git bisect reset`)

### File Evolution Analysis

- **FR-4.8**: Show commit history for a specific file (`git log -- <file>` or `jj log <file>`)
- **FR-4.9**: Display file changes over time with commit messages
- **FR-4.10**: Allow jumping to specific commit to see file state at that point
- **FR-4.11**: Show blame/annotate view (line-by-line authorship with commit context)
- **FR-4.12**: For jj: Show change evolution graph (`jj evolog <change-id>`)
- **FR-4.13**: Highlight major refactorings or rewrites in file history

### Branch/Change Comparison

- **FR-4.14**: For git: Compare two branches (`git diff <branch1>..<branch2>`)
- **FR-4.15**: For jj: Compare two changes (`jj diff --from <change1> --to <change2>`)
- **FR-4.16**: Show summary of divergence:
  - Commits/changes unique to each branch
  - Files modified differently
  - Conflicts that would occur if merged
- **FR-4.17**: Display commit graph showing where branches diverged
- **FR-4.18**: Identify common ancestor (merge base)
- **FR-4.19**: Show what would be merged if branches were integrated

### Code Evolution Patterns

- **FR-4.20**: Identify "hot spots" - files changed frequently
- **FR-4.21**: Show commit frequency over time (histogram)
- **FR-4.22**: Identify code churn (files with many additions/deletions)
- **FR-4.23**: For jj: Visualize change evolution chains (predecessors/successors)
- **FR-4.24**: Show authors contributing to specific file or directory

### Search and Filter

- **FR-4.25**: Search commit messages for keywords (`git log --grep="<pattern>"`)
- **FR-4.26**: Search code changes for keywords (`git log -S "<code>"`)
- **FR-4.27**: Filter commits by author, date range, or file path
- **FR-4.28**: For jj: Use revsets for complex queries (`jj log -r 'description(keyword)'`)

## Non-Functional Requirements

- **NFR-4.1**: Bisect operations must handle repositories with 10,000+ commits
- **NFR-4.2**: File evolution analysis must complete in under 5 seconds for files with 500+ commits
- **NFR-4.3**: Branch comparison must work with branches that diverged 1,000+ commits ago
- **NFR-4.4**: All log operations must use pagination for large result sets
- **NFR-4.5**: Plugin must cache expensive operations (large diffs, commit graphs) when possible

## Dependencies

### Prerequisites

- Phase 1 complete (shared VCS references, VCS auto-detection)
- Phase 2 complete (diff analysis functions)
- Phase 3 complete (merge base calculation from branch comparison)
- Understanding of git bisect workflow (good/bad commit marking)
- Understanding of jj evolution log and revsets

### Outputs for Next Phase

This is the final phase. Outputs are:
- Complete VCS tools suite covering all 4 pain point areas
- Reusable history analysis functions
- Patterns for pagination and caching that could improve other plugins

## Acceptance Criteria

- [ ] history-detective plugin created with symlink to shared-references/
- [ ] Can run automated bisect with test command (git)
- [ ] Can run manual bisect with good/bad marking (git)
- [ ] Shows file evolution history with commit messages
- [ ] Shows line-by-line blame with commit context
- [ ] Compares two branches/changes and shows divergence
- [ ] Identifies common ancestor and merge preview
- [ ] Searches commit messages and code changes
- [ ] For jj: shows change evolution graph
- [ ] Handles large repositories (1000+ commits) without performance issues
- [ ] Uses pagination for large result sets
- [ ] Plugin works in both git and jj repositories

## Open Questions

- Should bisect support skip functionality for broken commits (`git bisect skip`)?
- How should we visualize change evolution for jj (ASCII art graph or text-based tree)?
- Should we integrate with external tools like tig or gitk for visualization?
- Should we support advanced git log options (--graph, --decorate, --stat)?

---

*Review this PRD and provide feedback before spec generation.*

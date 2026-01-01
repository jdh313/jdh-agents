# VCS Tools Contract

**Created**: 2025-12-29
**Confidence Score**: 95/100
**Status**: Draft

## Problem Statement

The user maintains projects using two different version control systems: Jujutsu (jj) for personal projects and git for work projects. While the existing `atomic-commits` plugin handles commit creation and messaging, four critical VCS workflows remain time-consuming and error-prone on a weekly basis:

1. **Branch/change management**: Creating feature branches/changes, switching between contexts, and cleaning up old branches requires repetitive manual commands
2. **Merge/rebase/conflict resolution**: Integrating changes from main branches, rebasing feature work, and handling merge conflicts is tedious and error-prone
3. **Code review preparation**: Generating PR descriptions, cleaning up commit history (squashing, reordering, splitting), and reviewing diffs before submission takes significant time
4. **History investigation**: Finding when bugs were introduced (bisect), understanding code evolution over time, and comparing branches/changes requires multiple manual commands and context switching

Additionally, Claude Code agents frequently encounter interactive mode when executing VCS commands (e.g., interactive rebase, merge editors), which blocks automated workflows and requires manual intervention.

Without dedicated plugins for these workflows, the user must manually execute verbose command sequences, increasing cognitive load and risk of errors. The dual VCS requirement (git + jj) compounds this complexity, as command patterns differ significantly between systems.

## Goals

1. **Cover the 4 pain point areas**: Create plugins that automate or streamline branch management, merge/rebase operations, code review prep, and history investigation workflows
2. **Dual VCS support**: Ensure all plugins work seamlessly with both git and jj, automatically detecting which VCS is in use
3. **Reduce maintenance burden**: Use shared VCS reference documentation (via symlinks) across plugins to minimize duplication and simplify updates
4. **Prevent interactive mode issues**: Design plugins to use non-interactive command patterns, preventing agents from getting stuck in interactive prompts
5. **Faster than manual execution**: Each plugin should make workflows faster and less error-prone than running VCS commands manually

## Success Criteria

- [ ] Plugins exist for each of the 4 pain point areas (branch management, merge/rebase, review prep, history investigation)
- [ ] Each plugin successfully executes workflows in both git and jj repositories
- [ ] Shared VCS reference documentation (git-commands.md, jj-commands.md) is used via symlinks across multiple plugins
- [ ] No plugin triggers interactive mode during agent execution (all commands use non-interactive flags)
- [ ] User can complete common VCS workflows faster with plugins than with manual commands
- [ ] Plugin maintenance is manageable (shared docs reduce update overhead)

## Scope Boundaries

### In Scope

**Workflows to automate:**
- Branch/change creation, switching, and cleanup
- Merging, rebasing, and conflict resolution workflows
- PR description generation from commits/diffs
- Commit history cleanup (squash, reorder, split commits)
- Diff checking and impact analysis before review
- Finding when bugs were introduced (bisect workflow)
- Understanding code evolution (file history, log analysis)
- Comparing branches/changes (branch diff analysis)

**Technical requirements:**
- Dual VCS support (git and jj) in all plugins
- Non-interactive command patterns (--no-edit, --non-interactive, -m flags, etc.)
- Shared reference documentation via symlinks (git-commands.md, jj-commands.md)
- VCS auto-detection at runtime ([[ -d .jj ]] && echo "jj" || echo "git")

**jj-specific workflows:**
- Change evolution tracking
- First-class conflict handling
- Multiple working copy management
- Change stack management with automatic rebasing

### Out of Scope

**Excluded for now:**
- GitHub/GitLab/Bitbucket API integrations - Could be separate plugins for PR management, issue linking, etc.
- Visual diff/merge tools - Claude Code is text-based, defer to external tools
- IDE integrations beyond Claude Code - Focus on command-line workflows
- Support for other VCS systems (Mercurial, SVN, Fossil) - Only git and jj
- Team collaboration features (code review comments, approvals) - Defer to platform tools
- CI/CD pipeline integration - Separate concern from core VCS workflows

### Future Considerations

**Potential future plugins:**
- `github-workflow` - PR creation, review, merging via GitHub API
- `gitlab-integration` - Similar to GitHub but for GitLab
- `vcs-hooks` - Managing git/jj hooks, pre-commit checks
- `changelog-generator` - Automated changelog from commit history
- `release-automation` - Tagging, versioning, release notes

**Deferred enhancements:**
- Visual conflict resolution (text-based visualization could be added later)
- Advanced bisect strategies (e.g., bisect with test commands)
- Worktree/multiple working copy advanced management
- Custom merge strategies

---

*This contract was generated from brain dump input. Review and approve before proceeding to PRD generation.*

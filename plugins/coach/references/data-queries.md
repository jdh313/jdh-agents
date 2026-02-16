# Data Query Patterns

Proven query patterns for coaching skills and agents. Reference this doc instead of
hardcoding query parameters — fixes here propagate to all consumers.

## Todoist

### Today's Tasks (includes overdue)
- Tool: `find-tasks-by-date`
- Params: `startDate: "today"`, `limit: 50`
- Why limit 50: Default of 10 truncates real task lists
- Note: `startDate: "today"` automatically includes overdue items
- Post-query: Count overdue (due date < today) vs due today for triage decisions

### Completed Tasks (date range)
- Tool: `find-completed-tasks`
- Params: `since: "YYYY-MM-DD"`, `until: "YYYY-MM-DD"`

### Reschedule Tasks
- Tool: `update-tasks`
- Params: `tasks: [{ id, dueString: "tomorrow" | "Monday" | "YYYY-MM-DD" }]`
- Always confirm with user before executing

## Linear

### My Active Issues
- Tool: `list_issues`
- Params: `assignee: "me"` — NO state filter
- Why no state filter: State names vary by team. "active" is not a valid state type.
  Valid states include: Backlog, Todo, In Progress, In Review, Done, Canceled — but
  teams can customize these.
- Post-filter: Exclude Done and Canceled in-context to surface actionable issues
- Fallback: If zero results, retry without cycle parameter

### Project Issues
- Tool: `list_issues`
- Params: `project: "<name>"`, `assignee: "me"`

### All Projects
- Tool: `list_projects`
- Params: none required
- Returns: name, description, status, teams
- Used by: `/align`, `/review`, `/sunset`, `project-pulse`

### Initiatives
- Tool: `list_initiatives`
- Params: none required
- Returns: name, description, associated projects
- Used by: `/align`, `/review`

### Project Details
- Tool: `get_project`
- Params: `id: "<project-id>"` (from `list_projects` results)
- Returns: full description, tech stack details, members, status
- Used by: `/align` (for deeper matching against goals)

## Obsidian

### Yesterday's Daily Note
- Tool: `read_note`
- Path: `Daily Notes/YYYY-MM-DD.md` (yesterday's date)
- Look for: `## Today's Focus`, `## Field Notes`, carry-forward items

### Today's Daily Note
- Tool: `read_note`
- Path: `Daily Notes/YYYY-MM-DD.md` (today's date)
- Look for: existing `## Today's Focus` heading (replace if present)

## Routing Convention: Todoist vs Linear

**Todoist** is for life-admin tasks and tasks with hard external deadlines:
- Appointments, errands, chores, bills, renewals
- Anything with a real-world due date that can't slip (e.g., "file taxes by April 15")
- One-off tasks that don't belong to a project

**Linear** is for everything else:
- Project work, engineering tasks, creative tasks
- Tasks that belong to a project (create as issues under the project)
- Soft-deadline or no-deadline work that's tracked by progress, not date

**When routing from `/dump`**: Categorize items by destination, not just type. A "task" that belongs to a project routes to Linear as an issue, not to Todoist.

**When routing from `/intake`**: Project first-steps and sub-tasks go to Linear issues, not Todoist. Only offer Todoist if a task is genuinely life-admin or has a hard external deadline.

## Graceful Degradation

All queries follow the same pattern:
1. Attempt the query silently
2. If MCP server unavailable — skip, do not error or mention
3. If query returns empty — note it, continue with other sources
4. If all sources unavailable — conversation works without external data

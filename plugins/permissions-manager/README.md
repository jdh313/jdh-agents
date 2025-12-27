# permissions-manager

Manage Claude Code permissions and troubleshoot permission errors.

## What It Does

This skill helps you manage and configure Claude Code's `settings.json` permissions. It handles:
- Adding commands and patterns to the allowlist
- Troubleshooting permission denied errors
- Understanding Claude Code permission patterns
- Configuring permission rules for sandboxed environments

## When to Use

Use this skill when you:
- Encounter "Permission to use X has been auto-denied" errors
- Need to add a command or tool to the allowlist
- Are setting up Claude Code permissions for the first time
- Want to understand how permission patterns work
- Need to troubleshoot why a command or operation is blocked

## Key Triggers

Invoke this skill using these phrases:
- "allow this command"
- "add to permissions"
- "why is blocked"
- "Claude Code settings"
- "permission error"
- "allowlist"
- "permissions denied"

## Permission Management Patterns

### Adding to Allowlist

The skill provides guidance on:
- Wildcard patterns (e.g., `bash:*` to allow all bash commands)
- Specific command patterns (e.g., `bash:git_*` for git operations)
- Tool-specific patterns based on tool type

### Common Permission Scenarios

- **Bash commands**: Wildcard patterns for git, docker, npm, etc.
- **File operations**: Read/write patterns for specific directories
- **Network operations**: URL patterns for web requests
- **System access**: Patterns for environment or system information

## Examples

Common use cases demonstrated by this skill:
1. Troubleshooting denied operations with error context
2. Suggesting appropriate wildcard patterns
3. Understanding nested permission structures
4. Validating permission rule syntax

## Integration

This skill is typically invoked before attempting blocked operations, or to resolve permission errors when they occur. It works in conjunction with Claude Code's sandboxed execution model.

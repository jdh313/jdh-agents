---
name: permissions-manager
description: INVOKE when encountering permission denied errors or when managing Claude Code allowlists. Triggers include "permission denied", "auto-denied", "add to allowlist", "why is blocked", "settings.json", "sandbox error", "command not allowed", "tool blocked", or when troubleshooting any Claude Code permission issues. Provides systematic diagnosis of permission errors and guidance on configuring allowlists correctly.
---

# Permissions Manager

## Overview

Manage Claude Code's permission system by diagnosing permission errors, configuring allowlists in settings.json, and troubleshooting sandbox restrictions. This skill helps users understand and resolve permission issues efficiently.

## When to Use This Skill

Invoke this skill when:

- **Permission errors occur** - "Permission to use bash:docker has been auto-denied"
- **Adding allowlists** - "Allow git commands", "Add npm to allowlist"
- **Understanding errors** - "Why is this command blocked?", "What does this error mean?"
- **Configuring settings** - "Update settings.json", "Set up permissions for new project"
- **Troubleshooting blocks** - "Tool was blocked but shouldn't be", "Why can't Claude run this?"

## Core Capabilities

### 1. Understanding Claude Code Permissions

**Permission system architecture:**

Claude Code uses an allowlist-based permission system in `settings.json`:
- **Default behavior**: Most tools are denied by default in sandboxed mode
- **Allowlist required**: Commands/tools must be explicitly allowed
- **Pattern matching**: Supports wildcards (`*`) for flexible rules
- **Location**: Settings stored at `~/.config/claude/settings.json` (macOS/Linux) or `%APPDATA%\claude\settings.json` (Windows)

**Key permission categories:**

1. **Bash commands** - `bash:*` pattern for terminal operations
2. **File operations** - Controls read/write/delete access
3. **Network operations** - Web requests and API calls
4. **Tool-specific** - Individual tools like grep, glob, read, write
5. **MCP servers** - Model Context Protocol server access

**Permission inheritance:**

```
bash:*               → Allows all bash commands
bash:git*            → Allows bash:git_status, bash:git_commit, etc.
bash:docker_build    → Allows only bash:docker_build specifically
```

### 2. Diagnosing Permission Errors

**Step 1: Extract error details**

When a permission error occurs, identify:
1. **Tool/command name** - What was blocked? (e.g., `bash:docker`, `Write`)
2. **Error message** - Exact text of the denial
3. **Context** - What was the user trying to do?

**Example error:**
```
Permission to use bash:docker_ps has been auto-denied by your Claude Code settings
```

**Extracted info:**
- Tool: `bash:docker_ps`
- Pattern needed: `bash:docker*` or `bash:*`
- Action: View running Docker containers

**Step 2: Determine appropriate pattern**

Use this decision tree:

```
Is this a bash command?
├─ Yes → Use bash:<pattern>
│  ├─ Allow all bash? → bash:*
│  ├─ Allow specific tool? → bash:<tool>*
│  └─ Allow one command? → bash:<exact_name>
│
├─ No → Is it a built-in tool?
   ├─ Yes → Tool name (Read, Write, Bash, etc.)
   ├─ No → Is it an MCP server?
      └─ Yes → mcp__<server>__<tool>
```

**Step 3: Verify pattern scope**

Consider security implications:
- `bash:*` - Most permissive, allows ALL bash commands
- `bash:git*` - Allows all git operations (status, commit, push, etc.)
- `bash:git_status` - Most restrictive, single command only

**Recommendation approach:**
1. **Start narrow**: Suggest specific pattern first
2. **Explain trade-offs**: Security vs. convenience
3. **Offer alternatives**: Multiple specific patterns OR broader wildcard
4. **User decides**: Let user choose based on trust level

### 3. Configuring Allowlists

**Locate settings file:**

```bash
# macOS/Linux
~/.config/claude/settings.json

# Windows
%APPDATA%\claude\settings.json
```

**Settings.json structure:**

```json
{
  "allowedTools": [
    "bash:*",
    "Read",
    "Write",
    "Edit",
    "Grep",
    "Glob"
  ],
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/server.js"]
    }
  }
}
```

**Adding permissions:**

**For bash commands:**
```json
"allowedTools": [
  "bash:git*",           // All git commands
  "bash:docker*",        // All docker commands
  "bash:npm_install",    // Specific npm command
  "bash:*"               // All bash commands (most permissive)
]
```

**For built-in tools:**
```json
"allowedTools": [
  "Read",                // Read files
  "Write",               // Write files
  "Edit",                // Edit files
  "Bash",                // All bash (alternative to bash:*)
  "Grep",                // Search files
  "Glob"                 // Find files
]
```

**For MCP tools:**
```json
"allowedTools": [
  "mcp__git__*",                    // All git MCP tools
  "mcp__Obsidian__*",               // All Obsidian MCP tools
  "mcp__Graphiti__add_memory",      // Specific Graphiti tool
  "mcp__*"                          // All MCP tools (very permissive)
]
```

**Workflow for adding permissions:**

1. **Identify the blocked tool** from error message
2. **Determine appropriate pattern** using decision tree
3. **Edit settings.json** with text editor or using Claude Code:
   ```
   User: "Read my settings.json file"
   Claude: [reads file]
   User: "Add bash:docker* to allowedTools"
   Claude: [edits file with new permission]
   ```
4. **Verify syntax** - Ensure valid JSON (commas, brackets)
5. **Restart Claude Code** if needed (usually picks up changes automatically)
6. **Test** - Retry the operation that was blocked

### 4. Common Permission Scenarios

**Scenario 1: Git operations blocked**

**Error:**
```
Permission to use bash:git_status has been auto-denied
```

**Solution:**
```json
"allowedTools": [
  "bash:git*"  // Allows all git commands
]
```

**Explanation:** Git workflows typically need multiple commands (status, add, commit, push, etc.). Using `bash:git*` is more practical than listing each command individually.

---

**Scenario 2: Docker operations blocked**

**Error:**
```
Permission to use bash:docker_ps has been auto-denied
```

**Solution options:**

**Option A - Specific command only:**
```json
"allowedTools": [
  "bash:docker_ps"
]
```

**Option B - All docker commands:**
```json
"allowedTools": [
  "bash:docker*"
]
```

**Recommendation:** Option B for Docker workflows, since most tasks require multiple docker commands (build, run, ps, logs, etc.).

---

**Scenario 3: File operations blocked**

**Error:**
```
Permission to use Write has been auto-denied
```

**Solution:**
```json
"allowedTools": [
  "Read",
  "Write",
  "Edit"
]
```

**Explanation:** File tools are frequently needed together. If Write is needed, Read and Edit are often required too.

---

**Scenario 4: Package manager blocked**

**Error:**
```
Permission to use bash:npm_install has been auto-denied
```

**Solution options:**

**Option A - Specific commands:**
```json
"allowedTools": [
  "bash:npm_install",
  "bash:npm_run",
  "bash:npm_test"
]
```

**Option B - All npm commands:**
```json
"allowedTools": [
  "bash:npm*"
]
```

**Option C - All package managers:**
```json
"allowedTools": [
  "bash:npm*",
  "bash:pip*",
  "bash:uv*",
  "bash:cargo*"
]
```

**Recommendation:** Start with Option A if only specific commands are needed, expand to Option B if using npm frequently.

---

**Scenario 5: MCP server tools blocked**

**Error:**
```
Permission to use mcp__Graphiti__add_memory has been auto-denied
```

**Solution options:**

**Option A - Specific tool:**
```json
"allowedTools": [
  "mcp__Graphiti__add_memory"
]
```

**Option B - All tools from server:**
```json
"allowedTools": [
  "mcp__Graphiti__*"
]
```

**Option C - All MCP servers:**
```json
"allowedTools": [
  "mcp__*"
]
```

**Recommendation:** Option B is usually best - trust an MCP server fully or not at all.

---

**Scenario 6: Web operations blocked**

**Error:**
```
Permission to use WebFetch has been auto-denied
```

**Solution:**
```json
"allowedTools": [
  "WebFetch",
  "WebSearch"
]
```

**Explanation:** Web tools enable Claude to search and fetch documentation. Generally safe to allow.

### 5. Troubleshooting Permission Issues

**Problem: Permission added but still denied**

**Checklist:**
1. **Valid JSON?** Check for syntax errors (missing commas, brackets)
2. **Correct pattern?** Verify pattern matches the blocked tool name exactly
3. **Correct file?** Ensure editing the right settings.json location
4. **Saved?** File must be saved to disk
5. **Case sensitive?** Tool names are case-sensitive (bash:Git ≠ bash:git)

**Solution steps:**
```bash
# 1. Validate JSON syntax
cat ~/.config/claude/settings.json | python -m json.tool

# 2. Check if pattern matches
# Error: bash:git_status denied
# Pattern in settings: bash:git*  → Should work
# Pattern in settings: bash:Git*  → Won't work (case mismatch)

# 3. Verify file location
ls -la ~/.config/claude/settings.json

# 4. Test with explicit pattern
# If bash:git* doesn't work, try bash:* temporarily to isolate issue
```

---

**Problem: Settings file not found**

**Solution:**

```bash
# Create directory and file
mkdir -p ~/.config/claude
touch ~/.config/claude/settings.json

# Initialize with basic structure
cat > ~/.config/claude/settings.json << 'EOF'
{
  "allowedTools": [
    "Read",
    "Write",
    "Edit",
    "Grep",
    "Glob",
    "bash:*"
  ]
}
EOF
```

---

**Problem: Don't know what pattern to use**

**Solution workflow:**

1. **Copy exact error message**:
   ```
   Permission to use bash:unknown_command has been auto-denied
   ```

2. **Extract tool name**: `bash:unknown_command`

3. **Determine pattern type**:
   - Starts with `bash:` → Bash command pattern
   - Starts with `mcp__` → MCP tool pattern
   - Other → Built-in tool name

4. **Choose scope**:
   - Need just this? → Use exact name: `bash:unknown_command`
   - Need related commands? → Use prefix wildcard: `bash:unknown*`
   - Need all from this category? → Use full wildcard: `bash:*`

5. **Add to settings and test**

---

**Problem: Too permissive, want to restrict**

**Current state (too open):**
```json
"allowedTools": [
  "bash:*",
  "mcp__*"
]
```

**Narrowed down:**
```json
"allowedTools": [
  "bash:git*",
  "bash:docker*",
  "bash:npm*",
  "mcp__Graphiti__*",
  "mcp__Obsidian__*"
]
```

**Strategy:**
1. Start with broad permissions (`bash:*`) during initial setup
2. Monitor what tools are actually used
3. Narrow down to specific patterns once workflow is established
4. Remove unused patterns periodically

### 6. Best Practices

**Security recommendations:**

1. **Principle of least privilege**: Grant minimum permissions needed
2. **Audit regularly**: Review allowedTools list periodically
3. **Use specific patterns**: Prefer `bash:git*` over `bash:*` when possible
4. **Trust MCP servers**: Only install MCP servers from trusted sources
5. **Version control settings**: Include settings.json in dotfiles repo (without secrets)

**Convenience recommendations:**

1. **Start broad for exploration**: Use `bash:*` during learning phase
2. **Narrow for production**: Restrict to needed tools for production work
3. **Group by workflow**: Allow related tools together (git, docker, npm)
4. **Document decisions**: Comment why certain patterns are allowed
5. **Share team settings**: Use consistent allowlists across team

**Common allowlist templates:**

**Basic development:**
```json
{
  "allowedTools": [
    "Read",
    "Write",
    "Edit",
    "Grep",
    "Glob",
    "bash:git*",
    "bash:npm*"
  ]
}
```

**Full stack development:**
```json
{
  "allowedTools": [
    "Read",
    "Write",
    "Edit",
    "Grep",
    "Glob",
    "bash:*",
    "WebFetch",
    "WebSearch",
    "mcp__*"
  ]
}
```

**Restricted (production):**
```json
{
  "allowedTools": [
    "Read",
    "Edit",
    "bash:git_status",
    "bash:git_diff",
    "bash:git_log"
  ]
}
```

## Quick Reference

**Permission pattern syntax:**

| Pattern | Matches | Example |
|---------|---------|---------|
| `bash:*` | All bash commands | git, docker, npm, python, etc. |
| `bash:git*` | All git commands | git_status, git_commit, git_push |
| `bash:git_status` | Exact command only | git_status (nothing else) |
| `mcp__*` | All MCP tools | Any MCP server tool |
| `mcp__ServerName__*` | All tools from server | mcp__Graphiti__add_memory, etc. |
| `mcp__ServerName__tool` | Specific MCP tool | mcp__Graphiti__add_memory only |
| `Read` | Built-in Read tool | File reading |
| `Write` | Built-in Write tool | File writing |

**Settings file locations:**

| OS | Path |
|----|------|
| macOS | `~/.config/claude/settings.json` |
| Linux | `~/.config/claude/settings.json` |
| Windows | `%APPDATA%\claude\settings.json` |

**Common commands to allow:**

```json
{
  "allowedTools": [
    // Core file operations
    "Read", "Write", "Edit", "Grep", "Glob",

    // Version control
    "bash:git*",

    // Package managers
    "bash:npm*", "bash:pip*", "bash:uv*",

    // Docker
    "bash:docker*",

    // Testing
    "bash:pytest*", "bash:jest*",

    // Web access
    "WebFetch", "WebSearch",

    // MCP servers (if trusted)
    "mcp__Graphiti__*",
    "mcp__Obsidian__*"
  ]
}
```

## Workflow Decision Tree

**When permission error occurs:**

```
1. Read error message
   ↓
2. Extract tool name (e.g., "bash:docker_ps")
   ↓
3. Determine pattern type
   ├─ bash:* → Bash command
   ├─ mcp__* → MCP tool
   └─ Other → Built-in tool
   ↓
4. Choose scope
   ├─ Need just this? → Exact name
   ├─ Need related? → Prefix wildcard
   └─ Need all? → Full wildcard
   ↓
5. Edit settings.json
   ↓
6. Validate JSON syntax
   ↓
7. Save file
   ↓
8. Retry operation
   ↓
9. Success? → Done
   ↓
10. Still blocked? → Troubleshoot
    ├─ Check pattern matches exactly
    ├─ Verify file saved
    ├─ Check JSON syntax
    └─ Try broader pattern to isolate issue
```

## Examples

### Example 1: First-time setup

**User:** "Claude keeps saying commands are denied. How do I fix this?"

**Response:**
1. Explain permission system briefly
2. Locate settings file (`~/.config/claude/settings.json`)
3. Suggest basic allowlist for development:
   ```json
   {
     "allowedTools": [
       "Read",
       "Write",
       "Edit",
       "Grep",
       "Glob",
       "bash:*",
       "WebFetch",
       "WebSearch"
     ]
   }
   ```
4. Help create file if it doesn't exist
5. Verify syntax and save

### Example 2: Specific git error

**User:** "Getting 'Permission to use bash:git_status has been auto-denied'"

**Response:**
1. Identify tool: `bash:git_status`
2. Recommend pattern: `bash:git*` (allow all git operations)
3. Show how to add:
   ```json
   "allowedTools": [
     "bash:git*"
   ]
   ```
4. Explain why `bash:git*` is better than just `bash:git_status`
5. Verify and test

### Example 3: Narrowing permissions

**User:** "I added bash:* but want to be more secure now"

**Response:**
1. Ask what commands are actually used
2. Help identify patterns from usage:
   - Git operations → `bash:git*`
   - Docker commands → `bash:docker*`
   - npm scripts → `bash:npm*`
3. Replace `bash:*` with specific patterns
4. Test workflow still works
5. Remove unused patterns

### Example 4: MCP permission issue

**User:** "mcp__Graphiti__add_memory is denied"

**Response:**
1. Identify MCP server: Graphiti
2. Recommend: `mcp__Graphiti__*` (trust server fully)
3. Add to allowedTools
4. Explain MCP servers should be trusted or not used
5. Verify server is from trusted source

## Common Pitfalls

1. **Case sensitivity**: `bash:Git*` will NOT match `bash:git_status`
2. **Missing comma**: JSON syntax error breaks entire settings file
3. **Wrong file location**: Editing wrong settings.json
4. **Pattern too narrow**: `bash:git_status` when multiple git commands needed
5. **Pattern typo**: `bash:git_*` instead of `bash:git*` (underscore vs. nothing)
6. **Forgetting to save**: File not written to disk
7. **Invalid JSON**: Missing quotes, brackets, or commas
8. **Overly permissive**: Using `bash:*` when only git needed (security)

## When to Escalate

**Ask user for clarification when:**
- Unsure whether to allow broad wildcard (security trade-off)
- User wants maximum security but also maximum convenience
- Complex MCP permission needs (multiple servers, interactions)
- Custom bash scripts with unusual names

**Limitations of this skill:**
- Cannot modify settings.json automatically (requires user action)
- Cannot restart Claude Code process
- Cannot validate settings without user testing
- Cannot determine if specific bash commands are safe (user judgment required)

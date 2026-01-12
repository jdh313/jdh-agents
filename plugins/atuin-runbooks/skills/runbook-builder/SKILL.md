---
name: runbook-builder
description: >
  Use Skill(atuin-runbooks:runbook-builder) when creating Atuin runbooks, adding blocks
  to runbooks, or working with .atrb files. Trigger phrases: "create runbook", "add to
  runbook", "atuin runbook", "new runbook", or when discussing executable documentation
  for Atuin Desktop.
allowed-tools:
  - Read
  - Write
  - Glob
  - Bash(uuidgen:*)
  - Bash(find:*)
---

# Atuin Runbook Builder

Create and modify Atuin Desktop runbooks (.atrb files) from natural language.

## Overview

Atuin Desktop runbooks are executable documentation files that combine rich text with interactive terminal blocks, scripts, and automation. This skill helps you:

- Create new runbooks from natural language descriptions
- Add blocks to existing runbooks
- Generate proper UUIDs and YAML structure

**Reference:** See `references/block-types.md` for complete block type documentation.

## Workspace Detection

Before creating or modifying runbooks, locate the Atuin workspace:

```bash
# Find atuin.toml to locate workspace
find ~/Documents -name "atuin.toml" -maxdepth 3 2>/dev/null | head -1
```

The workspace directory is the parent of `atuin.toml`. Store runbooks there or in subdirectories.

**Default location:** `~/Documents/Atuin Runbooks`

## UUID Generation

Every block and runbook needs a unique lowercase UUID:

```bash
uuidgen | tr '[:upper:]' '[:lower:]'
```

Generate one UUID for the runbook itself, then one for each block.

## File Format

Runbooks are YAML files with `.atrb` extension:

```yaml
id: <uuid>
name: Runbook Title
version: 1
content:
  - <block 1>
  - <block 2>
  - ...
```

---

## Workflow: Create New Runbook

### Step 1: Understand the Request

Parse the user's description to identify:
- Runbook purpose/title
- Key steps or commands
- Any variables or configuration needed
- Working directory context

### Step 2: Propose Structure

Present a proposed structure before generating:

```
Proposed runbook structure:

1. [heading] Deploy to Production
2. [paragraph] Brief description of the deployment process
3. [local-directory] Select project directory
4. [script] Install dependencies (npm ci)
5. [script] Run tests (npm test)
6. [run] Build and deploy
```

Ask for confirmation or adjustments.

### Step 3: Generate UUIDs

Generate UUIDs for:
- The runbook itself
- Each block in the content array

```bash
# Generate multiple UUIDs
for i in {1..6}; do uuidgen | tr '[:upper:]' '[:lower:]'; done
```

### Step 4: Build YAML

Construct the runbook YAML:

```yaml
id: <runbook-uuid>
name: Deploy to Production
version: 1
content:
  - id: <uuid-1>
    type: heading
    props:
      level: 1
      backgroundColor: default
      textColor: default
      textAlignment: left
      isToggleable: false
    content:
      - type: text
        text: Deploy to Production
        styles: {}
    children: []
  - id: <uuid-2>
    type: paragraph
    props:
      backgroundColor: default
      textColor: default
      textAlignment: left
    content:
      - type: text
        text: "This runbook guides you through deploying the application to production."
        styles: {}
    children: []
  # ... more blocks
```

### Step 5: Write File

Save to the workspace with descriptive filename:

```
{workspace}/Deploy to Production.atrb
```

Or in a subdirectory for organization:

```
{workspace}/Deployments/Deploy to Production.atrb
```

---

## Workflow: Add Block to Existing Runbook

### Step 1: Read Existing Runbook

```bash
# Find the runbook
find ~/Documents -name "*.atrb" | grep -i "runbook-name"
```

Read and parse the existing content.

### Step 2: Determine Insert Position

Options:
- Append to end (default)
- After specific block (by name or type)
- Before specific block

### Step 3: Generate Block

Create the new block with a fresh UUID. See `references/block-types.md` for block schemas.

### Step 4: Insert and Write

Add block to the content array and write back the full YAML.

**Important:** Preserve exact YAML formatting. Use `|` for multiline code blocks.

---

## Block Templates

### Quick Terminal Block

```yaml
- id: <uuid>
  type: run
  props:
    type: bash
    name: "Command Name"
    code: |
      your-command-here
    pty: ''
    global: false
    outputVisible: true
    dependency: '{}'
  children: []
```

### Quick Script with Output Capture

```yaml
- id: <uuid>
  type: script
  props:
    interpreter: zsh
    name: "Get Value"
    code: |
      echo "captured output"
    outputVariable: my_variable
    outputVisible: false
    dependency: '{}'
  children: []
```

### Section with Heading + Paragraph

```yaml
- id: <uuid-1>
  type: heading
  props:
    level: 2
    backgroundColor: default
    textColor: default
    textAlignment: left
    isToggleable: false
  content:
    - type: text
      text: "Section Title"
      styles: {}
  children: []
- id: <uuid-2>
  type: paragraph
  props:
    backgroundColor: default
    textColor: default
    textAlignment: left
  content:
    - type: text
      text: "Section description goes here."
      styles: {}
  children: []
```

### Working Directory Setup

```yaml
- id: <uuid>
  type: local-directory
  props: {}
  children: []
```

Or with fixed path:

```yaml
- id: <uuid>
  type: directory
  props:
    path: /path/to/project
  children: []
```

### Environment Variable

```yaml
- id: <uuid>
  type: env
  props:
    name: NODE_ENV
    value: production
  children: []
```

---

## Best Practices

1. **Use `local-directory` for team runbooks** - Lets each user select their own path
2. **Add explanatory paragraphs** - Document what each command does
3. **Use `script` for captured values** - Set `outputVariable` when you need to reuse output
4. **Use `run` for interactive commands** - Terminal blocks support full PTY interaction
5. **Group related commands** - Use headings to organize sections
6. **Name blocks descriptively** - The `name` prop appears in the UI

## Anti-Patterns

- Don't hardcode absolute paths in team runbooks (use `local-directory`)
- Don't skip explanatory text between commands
- Don't use `run` when `script` suffices (scripts are lighter weight)
- Don't forget to generate unique UUIDs for each block

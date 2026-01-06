# Atuin Runbook Block Types

Complete reference for all block types in Atuin Desktop runbooks (.atrb files).

## Common Patterns

### All Blocks Have

```yaml
id: <uuid>           # Unique identifier (lowercase UUID)
type: <block-type>   # One of the types below
props: {}            # Type-specific properties
children: []         # Nested blocks (usually empty)
```

### Text Content Structure

Text blocks (heading, paragraph, lists, quote) have a `content` array:

```yaml
content:
  - type: text
    text: "Plain text"
    styles: {}
  - type: text
    text: "Bold text"
    styles:
      bold: true
  - type: text
    text: "Italic text"
    styles:
      italic: true
  - type: text
    text: "Code text"
    styles:
      code: true
  - type: link
    href: "https://example.com"
    content:
      - type: text
        text: "Link text"
        styles: {}
```

---

## Text Blocks

### heading

Section headers (H1-H3).

```yaml
- id: <uuid>
  type: heading
  props:
    level: 1                    # 1, 2, or 3
    backgroundColor: default
    textColor: default
    textAlignment: left
    isToggleable: false
  content:
    - type: text
      text: "Heading Text"
      styles: {}
  children: []
```

### paragraph

Regular text paragraphs.

```yaml
- id: <uuid>
  type: paragraph
  props:
    backgroundColor: default
    textColor: default
    textAlignment: left
  content:
    - type: text
      text: "Paragraph text here."
      styles: {}
  children: []
```

### bulletListItem

Unordered list item.

```yaml
- id: <uuid>
  type: bulletListItem
  props:
    backgroundColor: default
    textColor: default
    textAlignment: left
  content:
    - type: text
      text: "List item text"
      styles: {}
  children: []
```

### numberedListItem

Ordered list item.

```yaml
- id: <uuid>
  type: numberedListItem
  props:
    backgroundColor: default
    textColor: default
    textAlignment: left
  content:
    - type: text
      text: "Numbered item text"
      styles: {}
  children: []
```

### quote

Blockquote for callouts and highlights.

```yaml
- id: <uuid>
  type: quote
  props:
    backgroundColor: default
    textColor: default
  content:
    - type: text
      text: "Quoted text here"
      styles:
        italic: true
  children: []
```

---

## Executable Blocks

### run

Interactive terminal block with play button. Runs in a full PTY session.

```yaml
- id: <uuid>
  type: run
  props:
    type: bash              # Shell type
    name: "Block Name"      # Displayed name
    code: |
      echo "Hello"
      ls -la
    pty: ''                 # PTY reference (usually empty)
    global: false
    outputVisible: true
    dependency: '{}'        # JSON string
  children: []
```

**Use for:** Interactive commands, long-running processes, commands needing user input.

### script

Non-interactive script execution. Can capture output to a variable.

```yaml
- id: <uuid>
  type: script
  props:
    interpreter: zsh        # zsh, bash, python3, nodejs
    name: "Script Name"
    code: |
      echo "output value"
    outputVariable: ''      # Variable name to store output (optional)
    outputVisible: true
    dependency: '{}'
  children: []
```

**Use for:** Background scripts, output capture, variable population.

**Output capture example:**

```yaml
- id: <uuid>
  type: script
  props:
    interpreter: zsh
    name: "Get version"
    code: grep '^version' Cargo.toml | cut -d'=' -f2 | xargs
    outputVariable: app_version
    outputVisible: false
    dependency: '{}'
  children: []
```

Then use in templates: `{{ var.app_version }}`

---

## Context Blocks

### directory

Sets working directory for subsequent blocks.

```yaml
- id: <uuid>
  type: directory
  props:
    path: /path/to/directory
  children: []
```

**With template variable:**

```yaml
- id: <uuid>
  type: directory
  props:
    path: '{{ var.project_dir }}'
  children: []
```

### local-directory

User-selectable directory (not synced with runbook). Perfect for team-shared runbooks.

```yaml
- id: <uuid>
  type: local-directory
  props: {}
  children: []
```

### env

Set environment variable for subsequent blocks.

```yaml
- id: <uuid>
  type: env
  props:
    name: API_KEY
    value: secret123
  children: []
```

### var

Define a template variable.

```yaml
- id: <uuid>
  type: var
  props:
    name: project_name
    value: my-project
  children: []
```

**Usage:** `{{ var.project_name }}`

---

## Display Blocks

### var_display

Display current value of a variable.

```yaml
- id: <uuid>
  type: var_display
  props:
    name: app_version
  children: []
```

---

## Interactive Blocks

### dropdown

Selection from options (static or command-generated).

```yaml
- id: <uuid>
  type: dropdown
  props:
    name: release              # Variable name for selection
    options: gh release list --json name --jq '.[].name'
    fixedOptions: ''
    variableOptions: ''
    commandOptions: gh release list --json name --jq '.[].name'
    value: v1.0.0              # Default/current selection
    optionsType: command       # command, fixed, or variable
    interpreter: bash
  children: []
```

**Usage:** `{{ var.release }}`

### editor

Editable code/text block with optional variable sync.

```yaml
- id: <uuid>
  type: editor
  props:
    name: "Release Notes"
    code: ''                   # Initial content
    language: markdown         # Syntax highlighting
    variableName: release_notes
    syncVariable: true         # Auto-update when variable changes
  children: []
```

---

## Template Syntax

Atuin uses Jinja-like templating:

| Syntax | Description |
|--------|-------------|
| `{{ var.name }}` | Variable reference |
| `{{ var.name \| trim }}` | Trim whitespace |
| `{{ var.name \| replace("x", "y") }}` | String replacement |

**Example in script:**

```yaml
code: |
  git tag -a "v{{ var.version | trim }}" -m "Release v{{ var.version | trim }}"
```

---

## Default Props Quick Reference

| Block Type | Required Props |
|------------|----------------|
| heading | level |
| paragraph | (none) |
| bulletListItem | (none) |
| numberedListItem | (none) |
| quote | (none) |
| run | type, name, code |
| script | interpreter, name, code |
| directory | path |
| local-directory | (none) |
| env | name, value |
| var | name, value |
| var_display | name |
| dropdown | name, optionsType, options/commandOptions |
| editor | name, language |

**Standard text props (all text blocks):**

```yaml
backgroundColor: default
textColor: default
textAlignment: left
```

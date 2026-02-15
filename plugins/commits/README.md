# Commits

Format-aware atomic commits for git and jj (Jujutsu).

## What It Does

- **Auto-detects VCS**: Checks for `.jj` directory to determine git vs jj
- **Auto-detects commit style**: Analyzes recent commits to match the repo's convention (conventional or freeform), with CLAUDE.md config taking priority
- **Atomic splitting**: Groups changes into logical, independently-reversible units
- **Safety-first**: Never discards uncommitted changes without explicit permission

## Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `commits` | Auto-invoked | Main skill for all commit operations |
| `commit` | `/commits:commit` | Create a single commit |
| `split` | `/commits:split` | Split changes into atomic commits |
| `review` | `/commits:review [message]` | Review/improve a commit message |

## Commit Style Detection

The plugin determines commit message format in this order:

1. **CLAUDE.md** — If the repo's CLAUDE.md mentions a commit style, use it
2. **Git log analysis** — Analyze the last ~20 commits; if >60% use type prefixes (`feat:`, `fix:`, etc.), use conventional style; otherwise use freeform

### Supported Styles

- **Conventional**: `feat: add user auth` — type prefix, lowercase, imperative mood
- **Freeform**: `Add user auth` — capitalized, imperative mood, no type prefix

## Configuration

Add to your repo's `CLAUDE.md` to skip auto-detection:

```markdown
## VCS
- VCS: jj
- Commit style: conventional
```

Or for freeform:

```markdown
## VCS
- Commit style: freeform
```

If unspecified, the plugin auto-detects both from the repository state.

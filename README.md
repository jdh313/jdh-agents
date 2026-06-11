# feedback

Tester-facing feedback helpers for sessions spent exercising Claude Code
plugins.

## Skills

### `session` — `/feedback:session`

End-of-session feedback report for plugin testers. Analyzes **only the current
session transcript**, asks no questions, and emits a single copy-pasteable
report block that grades each plugin surface (skill / slash command / subagent
/ hook) the tester exercised and cites concrete evidence for every claim.

**Use it at the end of a test session.** A tester runs `/feedback:session`,
copies the report block, and sends it back to the plugin author.

The report covers:

- **Plugins/surfaces exercised** — with a ✅ worked / ⚠️ mixed / ❌ broke
  verdict each
- **What worked well** — each claim tied to a concrete moment
- **What didn't** — each failure with the actual ask-vs-behavior
- **Friction / rough edges** — repeats, clarifications, wrong-intent guesses
- **Suggested fixes** — only where the fix is obvious

It works across plugins from multiple repos (this one and others, e.g. `ndr`)
and notes which repo a surface came from when that's discernible.

## Requirements

The tester must have this plugin installed and enabled for the slash command to
appear. If that's not the case, the same workflow can be pasted in as a plain
prompt instead.

# Linear ticket mod

Status: **shipped in `linear` v0.10.0 for Claude only**, on top of the AgentForge v1.3.0 pin. The work is committed locally and not pushed.

## What shipped

- **`plugins/linear/hooks/register.tsx`:** a Claude Code mod. `hooks/hooks.json` is `{ "modules": ["./register.tsx"] }`, and `types/index.d.ts` declares `PluginState.linear.tickets`.
- **Detection from tool calls:** after `mcp__linear-server__get_issue` or `save_issue` succeeds, the result's `text` is parsed as JSON. In that JSON, `id` is the identifier (`JUN-468`) and `uuid` is the database id. The issue is promoted to the front of the active set, and its team key is saved in `$.store`.
- **Detection from prompts:** the pattern `\b[A-Z]{2,10}-\d+\b` is matched against prompt text, keeping only team keys already seen. `list_teams` returns no team key (checked live), so keys are learned from issue results, and a prompt mention only counts after one fetch from that team.
- **Display:** an `AbovePrompt` band, `󰔖 JUN-468 <dim title> +N` (Nerd Font `md-ticket`, U+F0516, since v0.10.1), with a blank line above it. It draws only while the set is non-empty and no survey is on screen. The band replaced `$.ui.status`, because Claude Code prefixes a status entry with `⚠ <plugin>:`.
- **Prompt and command:** a `prompt.compose` section `linear:active` (`scope: 'session'`) lists the active tickets. `/ticket` lists them, `/ticket clear` empties the set, and `/ticket drop <ID>` removes one.
- **Codex:** declared as a `hook-module` loss (`stripped`). `marketplaces/codex/plugins/linear/` has no `hooks.json`, `register.tsx` or `types/`.

## Commits

1. **`build[agentforge]: pin compiler v1.3.0`:** the bump also adds a Codex SessionStart agent-role check to every codex-agent-bundle package, so craft, debate, librarian and linear get patch bumps.
2. **`feat[linear]: track the session's active tickets in a mod (v0.10.0)`**

## Gate output

- `claude plugin validate marketplaces/claude/plugins/linear`: passed. It lists the hooks `session.start, tool.call, prompt.submit, prompt.compose, ui.render{AbovePrompt}, command.run{ticket}` and the state `linear.tickets`.
- `claude plugin test` (compiled plugin plus `plugins/linear/tests`): 5 pass, 0 fail. The tests cover both detection signals, the team-key filter, the band text on terminal and desktop, compose injection, and `/ticket drop` and `clear`. With the filter removed, 2 tests fail.
- `tsc` (strict, against the engine-laid types): exit 0.
- `scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native`: passed.
- `scripts/privacy-scan.sh`: no leaks found.

## Corrections made during the work

- **AgentForge 1.2.0 already passed `native.types` through.** An earlier draft of this report claimed it didn't. That came from a probe whose `sd` edit never matched: `sd` exits 0 when nothing matches, and I didn't re-read the file.
- **A separate coloured Text for the glyph took no width on the terminal**, although the drawn tree contained it. The glyph now lives inside the bold ID Text.
- **`marginBottom={-1}` hid the band entirely**, so it was reverted. The gap between the band and the prompt box is Claude Code's, and the documented `AbovePrompt` props don't control it.

## Open questions

- Should a ticket mentioned in passing in a prompt become active, or should only an explicit fetch make it active?
- Should there be a cold-start team-key seed? It would be a `teamKeys` userConfig, which AgentForge passes through via `native.userConfig`.
- The `/reload-plugins` check in a fresh session hasn't been run yet; it needs the user.

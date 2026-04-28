---
description: Start a Socratic reflection — clarify your own thoughts on a topic and save it to your Obsidian vault
argument-hint: "[topic or continuation]"
---

# /reflect

Begin a reflection session using the `reflect` skill. The agent stays neutral, asks one question at a time, and saves the result to `~/Loose Ends/Reflections/`.

## Argument

`$ARGUMENTS` — optional. May be:
- A topic phrase: `should I buy a new keyboard`, `nix vs brew`, `career direction`
- A continuation prompt block pasted from a prior open reflection
- Empty — the agent will ask what to think through

## Execution

1. Load the `reflect` skill and follow its methodology strictly.
2. If `$ARGUMENTS` looks like a continuation prompt (starts with `/reflect <slug>` and contains "Where I left off"), search `~/Loose Ends/Reflections/` for the matching slug. Open the prior note for context, but start a fresh dated note for this session unless the user asks otherwise.
3. If `$ARGUMENTS` is a topic phrase, use it as the seed but confirm or sharpen it before drilling.
4. If `$ARGUMENTS` is empty, ask the user what they want to think through.

## Reminder

This command's value is in the *neutrality* of the agent. Do not recommend, quantify, or decide for the user. The skill file has the full method — defer to it.

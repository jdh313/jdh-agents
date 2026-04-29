# compass

A suite of conversational thinking tools. The plugin name is the metaphor: it points, it doesn't command. Two skills today — one strictly neutral, one a thinking partner. Both save the session to your Obsidian vault.

| Skill | Stance | Use when |
|---|---|---|
| `/reflect` | Strict mirror — only questions, never opinions | You want to find your own answer without influence |
| `/mull` | Thinking partner — questions plus honest takes, pushback, and feedback | You want a collaborator who'll probe AND weigh in |

## /reflect — Socratic mirror

When you don't know what you actually think — about a purchase, a career move, a tool choice, a vague unease — `/reflect` helps you find your own answer through neutral questioning. It will refuse to recommend, quantify, or decide for you.

Output goes to `~/Loose Ends/Reflections/YYYY-MM-DD_<topic>.md`.

```
/reflect should I buy a new keyboard
/reflect career direction
/reflect
```

## /mull — Thinking partner

When you want a real collaborator — someone who'll probe the root of the issue AND share their read, push back on weak reasoning, or name patterns you might be missing. Still question-led, but the agent is allowed (and expected) to bring something to the table when invited or when silence would be evasive.

Output goes to `~/Loose Ends/Mulling/YYYY-MM-DD_<topic>.md` and captures agent contributions inline as Obsidian callouts so future-you can scan what was said.

```
/mull should I leave my job
/mull am I overengineering this
/mull
```

Natural language also works for both:

> Help me figure out how I feel about switching from Brew to Nix. *(reflect)*
>
> Mull this over with me — I'm not sure my current architecture is right. *(mull)*

## Output format

Each session produces a note with:

- **Prompt** — the original question, in your words
- **Conversation / Exploration** — condensed Q&A. `mull` notes use `> [!note] Take` callouts to mark agent contributions, including ones that didn't land.
- **Conclusion** *or* **Where I Left Off** — depending on whether the session resolved
- **Open Threads** *(mull only)* — unresolved disagreements logged for next time
- **Continuation Prompt** — only on open sessions; paste-ready to resume later
- **Related** — wikilinks to people, projects, or prior sessions surfaced

## Choosing between them

- **Decision is yours alone, you just need clarity** → `/reflect`
- **You want a sanity check or pushback** → `/mull`
- **You want adversarial argument with structured pro/con** → see the `debate` plugin
- **You want a recommendation or external research** → not this plugin

The two skills share question and bias references — they're different stances on the same conversational craft.

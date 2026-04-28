# reflect

A Socratic clarification skill. The opposite of a recommendation engine.

When you don't know what you actually think — about a purchase, a career move, a tool choice, a vague unease — `/reflect` helps you find your own answer through neutral questioning, then saves the reflection to your Obsidian vault.

## What it does

- Asks one open question at a time
- Drills into vague words and hidden tensions
- Refuses to recommend, quantify, or decide for you
- Saves the result to `~/Loose Ends/Reflections/YYYY-MM-DD_<topic>.md`
- For unfinished reflections, writes a paste-ready continuation prompt so future-you can pick up the thread

## Usage

```
/reflect should I buy a new keyboard
/reflect career direction
/reflect
```

Natural language also works:

> Help me figure out how I feel about switching from Brew to Nix.

## Output

Each session produces a note with:

- **Prompt** — the original question, in your words
- **Exploration** — condensed Q&A (the moves that opened things up)
- **Conclusion** *or* **Where I Left Off** — depending on whether the session resolved
- **Continuation Prompt** — only on open sessions; paste-ready to resume later
- **Related** — wikilinks to people, projects, prior reflections surfaced

## What it is not

- Not a debate engine — see the `debate` plugin for adversarial argument
- Not a recommender — it will never tell you which keyboard to buy
- Not a journal prompt generator — it works on the topic you bring

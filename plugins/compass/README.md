# compass

> **Requires an Obsidian vault.** Skills in this plugin read and write notes in an
> Obsidian vault, defaulting to `~/Loose Ends/`. That default is an example, not a
> requirement — point it at your own vault by editing the paths in the skill bodies
> (search for `Loose Ends`). Without a vault, the vault-writing skills will not work.

A suite of conversational thinking tools. The plugin name is the metaphor: it points, it doesn't command.

Three **stance** skills sit on one axis — how much the agent commits. `reflect` always saves; `mull` saves only substantive sessions; `converge` picks its artifact by subject.

| Skill | Stance | Use when |
|---|---|---|
| `/reflect` | Strict mirror — only questions, never opinions | You want to find your own answer without influence |
| `/mull` | Thinking partner — questions plus honest takes, pushback, and feedback | You want a collaborator who'll probe AND weigh in |
| `/converge` | Advisor — a recommendation with a confidence %, refined one question at a time | You want an actual answer, stress-tested against your context |

Two **evaluation** skills form a pipeline for the case where you're going to pick something and want the criteria settled before any option is named.

| Skill | Produces | Use when |
|---|---|---|
| `first-principles` | A signed-off needs map — must-solve gates, nice-to-haves, exclusions — locked to a vault note | You need to know what the answer must do before comparing answers |
| `solution-research` | A parallel-research handoff prompt for a fresh session | A needs map exists and you want the solution space researched against it |

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

When the session is substantive — unresolved, has open threads, contributed a landing take, or the user asks — output goes to `~/Loose Ends/Mulling/YYYY-MM-DD_<topic>.md` and captures agent contributions inline as Obsidian callouts so future-you can scan what was said. Short or trivial mulls end without filing.

```
/mull should I leave my job
/mull am I overengineering this
/mull
```

## /converge — Recommendation, then interview

When you want a real answer, not clarity and not a take. `/converge` researches the question, commits to a recommendation on turn one with an explicit confidence percentage, then asks exactly one question per turn — chosen for its power to *change* the recommendation, not confirm it. The number moves both directions; a flip is announced loudly. When confidence plateaus, the skill volunteers that you've converged.

Every turn has the same shape:

```
**Recommendation:** Use Postgres, not SQLite. **Confidence: 72%.**

<2-3 sentences of why>

**Question:** <one question, and why the answer moves the number>
```

The close is chosen by subject: throwaway questions print and end, durable ones file to `~/Loose Ends/Advice/YYYY-MM-DD_<topic>.md` with the full confidence trail and what got ruled out, and decisions that govern a repo hand off to `/capture-decision` instead.

```
/converge should I use Postgres or SQLite for this
/converge best approach for batch-editing RAW photos
/converge
```

## Explicit invocation only

All three skills set `disable-model-invocation: true`. They never auto-trigger from natural language — you invoke them by name. This is deliberate: these are stances you choose, and an agent that decides *for* you that a question needs a Socratic mirror (or, worse, silently switches you into recommendation mode) defeats the point. The skills still hand off to each other mid-session, but only by offering the switch and waiting for you to take it.

How you invoke them differs by runtime, and all three behave the same way on each:

| Runtime | Invoke with | Shows up in the model's catalog? |
|---|---|---|
| Claude Code | `/reflect`, `/mull`, `/converge` | No — hidden from auto-trigger, listed for you |
| Codex | `$compass:reflect`, `$compass:mull`, `$compass:converge` | No — the skill is not injected into the model context at all |

On Codex the policy compiles to `allow_implicit_invocation: false`, which goes further than gating auto-trigger: the skill is absent from the model's context entirely and only reachable from the `$`-picker. That is the intended behavior, not a limitation — asking Codex in prose to "reflect on this" is *supposed* to do nothing.

## Output format

`reflect` and `mull` sessions produce a note with:

- **Prompt** — the original question, in your words
- **Conversation / Exploration** — condensed Q&A. `mull` notes use `> [!note] Take` callouts to mark agent contributions, including ones that didn't land.
- **Conclusion** *or* **Where I Left Off** — depending on whether the session resolved
- **Open Threads** *(mull only)* — unresolved disagreements logged for next time
- **Continuation Prompt** — only on open sessions; paste-ready to resume later
- **Related** — wikilinks to people, projects, or prior sessions surfaced

`converge` sessions that file produce a different shape — Question, Recommendation, Confidence, Confidence Trail, Ruled Out, Evidence, Open, Related.

## Choosing between them

- **Decision is yours alone, you just need clarity** → `/reflect`
- **You want a sanity check or pushback** → `/mull`
- **You want an actual recommendation, researched and stress-tested** → `/converge`
- **You want adversarial argument with structured pro/con** → see the `debate` plugin. `converge` and `debate` share confidence bands and hand off both ways: `converge` escalates to `debate` when it's stuck low because the *evidence* conflicts, and `debate` hands a sub-80% or situationally-caveated verdict back to `converge` to refine against your context.
- **The decision is already made and just needs recording** → `coach:decide`, or `/capture-decision` for repo decisions

All three share question and bias references — they're different stances on the same conversational craft, ordered by how much the agent commits: `reflect` commits nothing, `mull` commits a take, `converge` commits an answer.

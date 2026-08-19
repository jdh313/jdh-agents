# Lesson Design System

A composable base for lesson and reference notes. The goal is twofold: every
lesson shares a consistent, readable look that fits the vault's native
rendering, and the interactive component that justifies giving lessons a
feedback loop — the self-grading quiz — is drop-in rather than reinvented
each time.

**This is a design system, not a template.** Compose lessons from these
components; override or break them the moment a topic genuinely needs
something bespoke. A locked template would flatten the per-topic craft the
skill prizes — these are primitives, not a cage.

## Markdown, backed by one CSS snippet

Lessons are `type: lesson` markdown notes — real vault notes, not files
outside the graph. They carry no CSS boilerplate themselves. All styling
lives in one shipped snippet, `assets/teach-lesson.css`, installed once to
`.obsidian/snippets/teach-lesson.css` and enabled under Settings →
Appearance → CSS snippets. Every lesson in every workspace shares it — this
is the one place D1 (`SKILL.md`) trades the old self-contained-HTML
guarantee for graph participation. See `UPSTREAM.md` for why that trade is
now worth making.

**Setup, once per vault:** copy `assets/teach-lesson.css` into
`.obsidian/snippets/`, enable it. Nothing further — no plugin, no JS.

## Components

### Quiz — the load-bearing component

Immediate, automatic feedback with zero JavaScript: a radio input plus a CSS
`:has(:checked) + sibling` reveal. Per `SKILL.md`, every answer in a set
should be the same word/character length so formatting leaks no clue.

```html
<div class="tl-quiz">
<p class="tl-quiz-q"><strong>Which builds storage strength?</strong></p>
<label class="tl-quiz-opt"><input type="radio" name="q1"> Massed cramming the night before</label>
<div class="tl-quiz-feedback tl-no">Not quite — try again.</div>
<label class="tl-quiz-opt"><input type="radio" name="q1"> Spaced retrieval over several days</label>
<div class="tl-quiz-feedback tl-ok">Correct.</div>
</div>
```

Each option is its own radio + the feedback div that immediately follows it;
checking the radio reveals only that option's feedback via the sibling
selector — there's nothing to grade, the correct option's feedback text
just says so.

**Write the quiz as one unbroken run of lines.** No blank lines anywhere
inside the block, and no `markdown="1"`. This is not cosmetic: a blank line
ends the HTML block, so the next chunk begins with an inline `<label>`,
which Obsidian wraps in a `<p>`; the browser then auto-closes that `<p>` at
the following `<div>`, and the feedback div stops being the label's sibling.
The `+` selector no longer matches and **that option silently reveals
nothing** — no error, just a dead radio. Opening with the block-level
`<p class="tl-quiz-q">` is what protects the first option from the same fate
(a markdown question paragraph above it absorbs it identically).

The consequence: nothing inside the block is parsed as markdown, so use
`<strong>` and `<code>` inline rather than `**` and backticks.

**Vary which position holds the correct answer** across a lesson's quizzes.
Always-first is a position tell that lets recognition substitute for recall —
the exact failure the quiz exists to catch.

### Reveal / spoiler — desirable difficulty before the answer

Use the vault's native collapsed callout, not a widget. Forces a retrieval
attempt before the answer shows (don't let the eye coast to it):

```markdown
> [!question]- Predict the output, then open
> …the answer and why…
```

### Visual vocabulary — reuse, don't invent

Use the vault's existing custom callouts (`explainer-callouts.css`) for
everything a lesson needs to flag:

```markdown
> [!key-idea] The concept in one line
> The thing to actually retain.

> [!gotcha] Where this trips people up
> The specific misconception or edge case.

> [!good] Do this
> A concrete correct pattern.

> [!bad] Not this
> The tempting-but-wrong alternative.

> [!test] Check yourself
> A quick self-check before moving on.
```

Do not define lesson-specific callout types. If a lesson needs a callout
`explainer-callouts.css` doesn't cover, that's a signal to extend the shared
vault snippet, not to fork a parallel one scoped to `teach`.

For a set of related items shown side by side (e.g. comparing three
approaches, or a set of terms), use the vault's `[!cards]` grid
(`explainer-cards.css`) rather than a table when a table would cram — cards
read better for short, parallel chunks:

```markdown
> [!cards]
> ##### Rung 1 — Predict-then-verify
> Real material, zero blast radius.
>
> ##### Rung 2 — Review, don't author
> Judgment under real conditions, nothing shipped.
```

### Code snapshot — pinned, self-contained code

The markdown home of the "Citing a live codebase" rule (`SKILL.md`). Embed
the snippet inline in a fenced code block; stamp the pinned ref immediately
below it:

````markdown
```typescript
export function requireRole(r) { /* … */ }
```
`services/auth/guard.ts` · [atlas-app@a1b2c3d (2026-06-15)](PERMALINK)
````

### Lesson footer — the standing reminders

Every lesson ends with the two fixtures `SKILL.md` requires: the primary
source and the ask-your-teacher nudge.

```html
<div class="tl-footer" markdown="1">

**Read next:** [primary source](SOURCE_URL) — the highest-trust resource on this.

Stuck or curious? *Ask me* — I'm your teacher for this, not just the author of the page.

</div>
```

### Provenance stamp — for lessons bound to a live codebase

When a lesson is tightly bound to live code (its snapshots and line
references track a moving repo), stamp the lesson *as a whole* so a future
reader knows how old it is and what to diff against. This complements the
per-snapshot pins from "Citing a live codebase" in `SKILL.md` — the snapshot
pins each citation; this dates the whole lesson.

```html
<p class="tl-provenance">Lesson authored 2026-08-10 09:34 EDT · grounded against <a href="PERMALINK">repo@sha</a> (committed YYYY-MM-DD). Code citations are pinned snapshots — diff against current <code>HEAD</code> before trusting line numbers if you revisit this later.</p>
```

Re-resolve the SHA (`git -C <repo> rev-parse --short HEAD`) and the
timestamp at authoring time — don't copy a stale stamp from a prior lesson.

### Transclusion — where the lesson's prose comes from

Per `SKILL.md`'s wiki/lesson split, a lesson does not restate prose that
already lives on a wiki concept page — it transcludes the canonical gist:

```markdown
![[Postgres MVCC#Gist]]
```

Embed only from the small canonical heading set (`## Gist` and peers) — see
`SKILL.md` for the rename-fragility constraint this exists to bound.

## Reference-doc note

Reference material — glossaries, syntax cards, algorithm notes — is now
ordinary wiki content (D3, `SKILL.md`), so it uses the vault's normal wiki
conventions, not this system. The quiz component is lesson-specific (a
reference page is state, not process, and has nothing to "check yourself"
on); the reveal, callout, and code-snapshot components are shared vocabulary
and apply equally to wiki pages, via the vault's existing snippets rather
than this one.

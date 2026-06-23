# Lesson Design System

A composable base for lesson and reference HTML. The goal is twofold: every lesson shares a consistent, beautiful, print-friendly look (Tufte-leaning), and the interactive components that justify HTML over markdown — the tight, automatic feedback loop — are drop-in rather than reinvented each time.

**This is a design system, not a template.** Compose lessons from these tokens and components; override or break them the moment a topic genuinely needs something bespoke. A locked template would flatten the per-topic craft the skill prizes — these are primitives, not a cage.

## Self-contained, always

Lessons are single, portable HTML files (no shared external stylesheet — relative anchor links between lessons must resolve from anywhere). So the design system is **copy-in**, not linked: paste the tokens into a `<style>` block and the components inline. Don't factor them out to a shared `.css`/`.js` file — that would break the self-contained guarantee.

## Tokens

Drop into each lesson's `<style>`. Tuned for screen reading and clean print.

```css
:root {
  /* Type — a restrained Tufte-ish scale */
  --font-body: et-book, Palatino, "Palatino Linotype", Georgia, serif;
  --font-mono: "SF Mono", "JetBrains Mono", ui-monospace, monospace;
  --size-base: 1.125rem;     --line-base: 1.6;
  --size-h1: 2.2rem;         --size-h2: 1.5rem;       --size-small: 0.85rem;

  /* Ink & ground — high contrast, low saturation */
  --ink: #1a1a1a;            --ink-soft: #555;
  --ground: #fdfdfb;        --rule: #e4e2dc;
  --accent: #5a3e85;         /* sparingly: links, focus */
  --ok: #2e7d4f;             --no: #b03030;
  --snap-bg: #f6f4ee;        /* code-snapshot background */

  --measure: 38rem;          /* line length cap — readability */
  --space: 1.4rem;
}
body {
  font: var(--size-base)/var(--line-base) var(--font-body);
  color: var(--ink); background: var(--ground);
  max-width: var(--measure); margin: 3rem auto; padding: 0 1.2rem;
}
@media print { body { background:#fff; color:#000; max-width:none; margin:0; } .no-print { display:none; } }
```

## Components

Minimal, dependency-free (vanilla JS, inline). Each carries the feedback loop where one applies.

### Auto-grading quiz — the load-bearing component

The whole reason lessons are HTML: immediate, automatic feedback. Per `SKILL.md`, every answer in a set should be the same word/character length so formatting leaks no clue.

```html
<form class="quiz" data-answer="b">
  <p class="q">Which builds storage strength?</p>
  <label><input type="radio" name="q1" value="a"> Massed cramming the night before</label>
  <label><input type="radio" name="q1" value="b"> Spaced retrieval over several days</label>
  <button type="submit" class="no-print">Check</button>
  <p class="verdict" hidden></p>
</form>
<script>
document.querySelectorAll('form.quiz').forEach(f => f.addEventListener('submit', e => {
  e.preventDefault();
  const picked = f.querySelector('input:checked');
  const v = f.querySelector('.verdict'); v.hidden = false;
  const ok = picked && picked.value === f.dataset.answer;
  v.textContent = ok ? 'Correct.' : 'Not quite — try again.';
  v.style.color = ok ? 'var(--ok)' : 'var(--no)';
}));
</script>
```

### Reveal — desirable difficulty before the answer

Forces a retrieval attempt before showing the answer (don't let the eye coast to it).

```html
<details class="reveal"><summary>Predict the output, then open</summary>
  <p>…the answer and why…</p>
</details>
```

### Callout — aside without breaking flow

```html
<aside class="note"><strong>Note —</strong> a margin-ish aside; use for caveats, not core content.</aside>
```
```css
.note { border-left: 3px solid var(--rule); padding-left: 1rem; color: var(--ink-soft); font-size: var(--size-small); }
```

### Code snapshot — pinned, self-contained code

The HTML home of the "Citing a live codebase" rule (`SKILL.md`). Embed the snippet inline; stamp the pinned ref; link the permalink.

```html
<figure class="snap">
  <figcaption><code>services/auth/guard.ts</code> · <a href="PERMALINK">cartaos@a1b2c3d (2026-06-15)</a></figcaption>
  <pre><code>export function requireRole(r) { /* … */ }</code></pre>
</figure>
```
```css
.snap { background: var(--snap-bg); border: 1px solid var(--rule); border-radius: 4px; padding: 0.6rem 0.9rem; }
.snap figcaption { font: var(--size-small)/1.4 var(--font-mono); color: var(--ink-soft); margin-bottom: 0.4rem; }
.snap pre { margin: 0; overflow-x: auto; font-family: var(--font-mono); }
```

### Diagrams (Mermaid)

For flows, handshakes, and state machines, a diagram beats prose. Mermaid is the lightest authoring format — but it is **not** bundled; load it from a pinned CDN and write diagrams as `<pre class="mermaid">` blocks:

```html
<pre class="mermaid">
sequenceDiagram
    actor U as Browser
    participant S as App
    U->>S: request a protected route
    S->>U: respond
</pre>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
</script>
```

**Self-containment caveat.** This is the one component that breaks the offline guarantee — the diagram needs a network connection to render. Note the dependency in the lesson's provenance footer. (If a Mermaid renderer like `mmdc` is available at authoring time, pre-render to inline SVG instead and the lesson stays fully self-contained — but that pulls a headless browser, so it's rarely worth it.)

**Sequence-diagram syntax gotchas** — these silently break the parser:
- No parentheses in `participant X as <label>` aliases — write `participant O as Okta`, not `Okta (auth server)`.
- Keep message text plain — avoid `<br/>`, `;`, and `&`.

### Lesson footer — the standing reminders

Every lesson ends with the two fixtures `SKILL.md` requires: the primary source and the ask-your-teacher nudge.

```html
<footer class="lesson-end">
  <p><strong>Read next:</strong> <a href="SOURCE_URL">primary source</a> — the highest-trust resource on this.</p>
  <p>Stuck or curious? <em>Ask me</em> — I'm your teacher for this, not just the author of the page.</p>
</footer>
```

### Provenance footer — for codebase-bound lessons

When a lesson is tightly bound to live code (its snapshots and line references track a moving repo), stamp the lesson *as a whole* so a future reader knows how old it is and what to diff against. This complements the per-snapshot pins from "Citing a live codebase" in `SKILL.md` — the snapshot pins each citation; this dates the whole lesson.

```html
<p class="provenance">Lesson authored 2026-06-17 09:34 EDT · grounded against <a href="PERMALINK">repo@sha</a> (committed YYYY-MM-DD). Code citations are pinned snapshots — diff against current <code>HEAD</code> before trusting line numbers if you revisit this later.</p>
```
```css
.provenance { font-family: var(--font-mono); font-size: 0.78rem; color: var(--ink-soft); margin-top: 1.2rem; padding-top: 0.6rem; border-top: 1px dotted var(--rule); }
```

Re-resolve the SHA (`git -C <repo> rev-parse --short HEAD`) and the timestamp at authoring time — don't copy a stale stamp from a prior lesson. If the lesson uses a CDN-rendered diagram (Mermaid above), note that network dependency in this same line.

## Reference-doc note

Print-beautiful cheat sheets in `./reference/` use the same tokens but lean harder on the print rules (`@media print`) and density — they exist to be printed and pinned up, not scrolled. The quiz/reveal components rarely apply there; the code-snapshot and callout do.

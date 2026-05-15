# Taxonomy

`area:` and `topic:` are finite, hand-edited lists. The capture skill validates every write against them and refuses unknown values.

## Why finite

At ~50–200 decisions/year (personal scale), enforced taxonomy is more reliable than embedding-distance matching. The cost of mis-grouping later is real — finding a decision by `area:` six months later only works if `area:` was the same value six months earlier.

The Bases view renders the current taxonomy as a visible reference, so "I forgot my own tag names" stays manageable.

## Files

- `taxonomy/areas.yaml` — the *what is this decision about* axis.
- `taxonomy/topics.yaml` — finer-grained, within an area.

Both are flat YAML lists of strings. One value per decision (not lists).

## Current bootstrap

Seeded with the values that actually appear in the A–H meta-chain, so the bootstrap exercises itself rather than starting from abstract guesses.

### Areas

| Value | Use for |
| --- | --- |
| `process` | How decisions get made / written / read |
| `tooling` | What we use to make / store / read them |
| `scope` | What's in vs out (MVP, pilot, team-product) |
| `substrate` | Storage and retrieval medium |

### Topics

| Value | Use for |
| --- | --- |
| `substrate` | Storage choice (markdown, graph DB, CMS) |
| `read-side` | Context-loading, retrieval, supersession resolution |
| `write-side` | Capture, materialization, schema enforcement |
| `granularity` | Atomic vs bundled, file vs directory |
| `mvp-scope` | What's in / out of MVP |
| `test-method` | How we validate the discipline (Q1 / Q2a / Q2b) |
| `discipline` | What humans must do without tool support |

## Growth rule

Adding a value is explicit. The capture skill prompts:

> "`<value>` is not in `taxonomy/topics.yaml`. Use existing (`a`, `b`, `c`, …) or add new?"

Choosing "add new" appends the value to the relevant `*.yaml` and commits the change. **Friction is the feature** — silent acceptance is how taxonomies drift.

## Drift-prevention rules

- **Don't rename existing values.** A rename invalidates every prior decision that used the old name. If a value name turns out wrong, write a decision about it, then do the rename as a deliberate corpus-wide migration.
- **Don't add overlapping values.** If `tooling` and `substrate` start blurring, write a decision about whether to merge them, don't quietly add a third overlapping value.
- **Don't add catch-alls.** "other" or "misc" defeat the point.

## When the bootstrap is wrong

The bootstrap was chosen at install time to fit the A–H meta-chain only. It will be wrong for some real decisions. The expected pattern: discover the gap during a real `/capture-decision` invocation, decide on the new value, add it, capture the new value as a (small, low-altitude) decision so the choice survives.

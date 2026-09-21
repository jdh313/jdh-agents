---
name: term
description: >-
  Name the precise term for what you were fumbling to say, rewrite your sentence
  with it, and log it to your vault word log
---

# Term

The user reached for a word and missed. Answer what they were asking, hand them the precise term, and log it to their word log without asking.

## Usage

```
/term
/term the thing where running it twice doesn't charge the card twice
```

**The fumble** is the text the term replaces: the arguments if given, otherwise the user's previous message. Never ask the user to re-describe it; the previous message is the whole point of the no-argument form.

## 1. Answer

Answer the question the fumble was asking, exactly as you would have if they had used the right word. The term is an addition to the answer, never a substitute for it. If the fumble was a statement rather than a question, skip to the block.

## 2. The term block

After the answer, one short block:

```markdown
**Term:** idempotency: an operation that has the same effect whether applied once or many times.
**Your sentence:** "The charge endpoint needs to be idempotent, so a retried request can't bill the card twice."
**Near misses:**
- *deduplication*: removes repeats after they arrive; idempotency makes repeats harmless.
- *at-most-once*: guarantees delivery never repeats, at the cost of sometimes not delivering.
```

- **Term** is the single most precise word or phrase, with a one-line definition.
- **Your sentence** rewrites the fumble with the term in it, keeping the user's meaning and register.
- **Near misses** are up to 2 terms the user could plausibly confuse with it, each with the one distinction that separates them. Omit the line when no real near miss exists; padding with a loose synonym teaches nothing.

**Repo-specific terms** (a name this codebase coined, or a general word this repo uses in a narrower sense) get one more line after the block, suggesting the user record the term in the repo's `CONTEXT.md` with `/craft:domain-modeling`. Suggest only: leave `CONTEXT.md` untouched.

## 3. Log

Every term goes to this machine's word log, relative to `~/Loose Ends/`: `${user_config.word_log}`. A value still in placeholder form (starting with `${`) was never set; use `Reference/Word Log.md`.

The repo is the last path component of `git rev-parse --show-toplevel`; use `none` when that fails.

Dispatch the append to `@note-editor` in the background, and carry on without waiting or reporting it:

```markdown
## Intent
append one word-log entry to <resolved log path>

## Constraints
- Append exactly one line at the end of the file; change nothing else.
- If the file is missing, create it first with this frontmatter and heading, then append:
  ---
  owner: ai
  type: log
  tags:
    - topic/vocabulary
  ---
  # <file name without .md>

  Terms reached for and missed, logged by `/term`. One line per entry: date | term | original phrasing | near misses | repo.

## Input
- **<YYYY-MM-DD>** | <term> | "<the fumble, trimmed to one line>" | <near misses, comma-separated, or -> | <repo>

## Output shape
File path and the appended line.
```

The entry is one unwrapped line; replace any newline in the fumble with a space. Surface the log only if the dispatch fails: one line naming the file and the error.

---
name: screen-critique
description: >-
  Critique a UI screen design — a mockup, a design-tool board, or a built screen
  — in a fixed order: purpose, then structure, then copy, then consistency. Use
  when a screen "doesn't feel right", before iterating on a board, or when asked
  to review or critique a screen's design.
---

# Screen critique

Four passes, in order. Each pass can only fix what the passes before it leave standing: copy edits cannot rescue a screen with no question of its own, and a hierarchy fix that restates another screen's answer makes the screen worse. Finish a pass, report it, then start the next.

Before the first pass, gather the **neighbours**: every other screen a user can reach in one step from this one (the tabs on the same rail, the parent list, the dashboard above it). Purpose is judged against them, never alone. Gather the repo's glossary (`CONTEXT.md` or equivalent) and any decision ledger too; pass 3 and 4 check against both.

## Pass 1 — Purpose

Write the screen's **question** in one line, in the user's words: the thing they open this screen to find out ("what has been done to this car?"). Then check it against each neighbour's question.

- **Unique.** No neighbour already answers it. If one does, the screen has no job; say so and stop here. The fix is a split or a merge, not a redesign.
- **One time frame.** The content answers about one of: the past (records), now (current condition, what is open), or next (what is coming). A screen that mixes frames answers two questions and usually shares one with a neighbour.
- **First thing read.** The answer to the question sits top-left, before anything else of equal weight.

Done when: the question is written, every neighbour's question is written beside it, and each check has a yes or a named failure.

## Pass 2 — Structure

- **Density fits the task.** A user scanning many records gets a table, one row per record at the grain they compare (one row per line item, not per visit, when they compare line items). Cards and timelines spend space on few data points; use them only for few items.
- **Group fields print once.** Fields shared by a group (a visit's date, total, invoice) appear on the group's first row only.
- **One spine.** Sections on one screen share a column grid, so the eye runs down a column across sections.
- **Weight follows importance.** Sections of unequal importance do not get equal headings, row height, and contrast.
- **Each section earns its place.** For every section, name what breaks if it is removed. If nothing breaks, it moves to the neighbour that owns it or goes.

Done when: every section has a named reason to exist on this screen, and every failure names the section and the fix.

## Pass 3 — Copy

- **Each fact once.** List every fact the screen states. A fact stated twice (a rule in a subtitle and again in a cell, a total in two columns) keeps the home where it is read and loses the other.
- **Subtitles state rules.** A section subtitle survives only if it states a rule the data cannot show. Sort order, legends, and restated headings go — sort order to a header indicator, legends to the thing they explain.
- **One action, one label.** The same operation has the same visible verb everywhere; different destinations have different text. Verb plus noun, with the noun in the accessible name when the visible label is short.
- **Labels match state.** A label on an open item does not use a past tense ("Resolved by" on something unresolved); a column header names what its cells hold.
- **Glossary terms.** UI labels may differ from canonical terms, but each label is used for one concept and does not use a term the glossary lists to avoid.

Done when: every repeated fact, subtitle, and action label has a keep or cut verdict, with the replacement text for each cut.

## Pass 4 — Consistency

- **Sample data agrees** across every board or fixture that shows the same entity: the same event has the same date and reading everywhere.
- **Navigation agrees.** Every screen that draws the shared rail or menu lists the same items in the same order.
- **Decisions hold.** The design follows the current decision heads that bind it; a deliberate departure is named as a supersession candidate, not shipped silently.
- **Rendered, not assumed.** Check the exported or screenshotted render, not the source tree. Design tools can keep drawing stale text after an edit.

Done when: every board or screen in scope has been compared, and every mismatch names both locations.

## Precedent

When pass 1 or 3 stalls on a name or a split, look at how two or three established products in the same field structure the same content. Precedent settles naming ("issue" over "tag" because the fleet tool the product already borrows from uses it) and splits (every surveyed maintenance product separates history from the due list). It does not override a recorded decision.

## Report

One section per pass, failures first, each as: location, what fails, the fix. End with the single change that would move the screen most. Sources behind each check: [`references/sources.md`](references/sources.md).

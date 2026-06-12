---
name: triage
description: >-
  Author-facing companion to `feedback:session`. Use when the user invokes
  `/feedback:triage`, says "triage the feedback", "digest these reports", "go
  through the tester feedback", "what should I fix first", or otherwise has a
  pile of session-feedback reports and wants them turned into a prioritized,
  routed action plan. Ingests one or many reports (a directory of `.md` files, a
  single file, or report blocks pasted into the conversation), parses them
  against the shared report format, clusters findings by surface and category,
  ranks by severity x corroboration, and routes each cluster to a concrete
  actuator (skill-improver, a description/trigger edit, hookify, skill-creator).
  Proposes actions and offers handoffs — never auto-applies fixes.
argument-hint: "[path to a report file or directory; omit to use reports pasted in this conversation]"
---

# Feedback triage

You are on the **plugin author's** side now. The tester ran `feedback:session`
one or more times and handed back reports. Your job is to turn that pile into a
short, prioritized punch list where every item names a concrete next action
against a specific surface — so the author can go fix the highest-leverage
things first.

This skill is the parsing counterpart to `feedback:session`. Both agree on
`../../references/report-format.md`; read it first so you parse the surface
table and the `[surface] severity/category` tags exactly as `session` emits
them.

## Hard rules

- **Propose, never apply.** Triage outputs a plan and offers handoffs. It does
  not edit skills, run `skill-improver`, write hooks, or open tickets on its own
  — the author triggers those after reviewing.
- **Corroboration is signal.** The same finding in N reports outranks a louder
  one-off. Track and surface the count.
- **Evidence travels.** Carry the tester's concrete moment into each cluster.
  Don't abstract a finding into "output issues" — keep the quote.
- **Don't invent findings.** Only cluster what the reports actually contain. If
  a report is malformed or off-format, note it under "Unparseable" rather than
  guessing its meaning.
- **Scope to surfaces.** Route to plugin fixes, not model behavior.

## Procedure

1. **Ingest.** Resolve the input:
   - **Arg is a directory** → read every `*.md` in it; each file is one report.
   - **Arg is a file** → read it (may contain one or several report blocks).
   - **No arg** → use the report block(s) pasted into the current conversation.

   If you find zero reports, say so and stop.

2. **Parse** each report against the contract into normalized findings. For each
   `Findings` line capture: source report (filename or "pasted #n"), surface id,
   kind, repo, severity, category, and the evidence prose. Also capture the
   table verdict per surface and the `Worked well` notes. Lines that don't match
   the tag grammar go to an "Unparseable" bucket — don't discard silently.

3. **Cluster** findings by `(surface, category)`. Within a cluster, merge the
   evidence from each source and count corroboration (how many distinct reports
   raised it). Keep the highest severity seen in the cluster.

4. **Rank.** Score each cluster `severity_weight x corroboration`, where
   `blocker = 3`, `major = 2`, `minor = 1`. Break ties by corroboration, then by
   worst verdict (`❌` over `⚠️`). The top of this ranking is "fix first".

5. **Route** each cluster to a concrete actuator by category:

   | Category | Proposed action |
   | --- | --- |
   | `trigger` | Tune the skill's `description:` trigger phrases; if it's an unwanted *behavior* to block, propose a `hookify` rule. |
   | `output` | Run `skill-improver` on the surface, or propose a targeted body edit when the fix is obvious. |
   | `defaults` | Propose a specific body edit changing the default. |
   | `friction` | Reduce questions / add a default in the skill body; cite the friction moment. |
   | `docs` | Edit the `description:` / README / `argument-hint` to match real behavior. |
   | `missing` | Scope a new skill via `skill-creator`, or a feature in the existing surface. |

   Name the actual file when you can infer it (`plugins/<plugin>/skills/<skill>/SKILL.md`).

6. **Output** the punch list (format below).

7. **Offer handoffs.** End by offering, as a numbered menu, to: run
   `skill-improver` on the top item, draft the proposed description/body edits,
   write the proposed `hookify` rule, or open `pm`/`linear` tickets for the
   backlog. Wait for the author to choose — apply nothing unprompted.

## Output format

```
# Feedback triage — <N> reports · <M> surfaces · <K> findings

## Fix first
1. `[<surface>]` <severity>/<category> ×<count> — <merged evidence> → <proposed action + file>
2. ...

## By surface
### `<plugin>:<surface>` — <✅×a ⚠️×b ❌×c across reports>
- <severity>/<category> ×<count> — <evidence> → <action>
- ...

## Corroborated wins
- `[<surface>]` <what worked, raised in ×<count> reports>

## Unparseable / needs more info
- <source> — <why it couldn't be triaged>
```

Omit any section that's empty (except keep "Fix first" — if nothing is
actionable, say so explicitly there). Keep it scannable; the author should be
able to read the top three lines and know what to do next.

## References

- **`../../references/report-format.md`** — the report contract this skill
  parses. Single source of truth for the surface-id grammar, verdicts, and the
  severity/category tags that drive clustering and routing.

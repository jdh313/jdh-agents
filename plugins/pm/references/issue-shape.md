# AcmeOS issue shape

What a well-formed AcmeOS Linear ticket contains. Source of truth for the Missing-fields bucket in `pm:groom`, the proposal shape in `pm:triage`, and the template in `pm:author`. Defers to `linear-workflow` (linear plugin) for title, labels, priority, and status conventions — this file covers what goes **inside the description body** plus the required-field checklist.

## Required fields

A ticket is "well-formed" when it has all six:

1. **Title** — per `linear-workflow` conventions (`Area: noun-phrase` or bare noun-phrase)
2. **Project** — assigned to the active AcmeOS phase project (rotates per phase)
3. **Priority** — set to one of `urgent` / `high` / `medium` / `low`; not `None`
4. **Surface label** — exactly one of `pipeline`, `backend`, `frontend`, `infra`, `database`
5. **Type label** — exactly one of `Feature`, `Improvement`, `Docs`, `Chore`, `Decision`, `Spike`
6. **Description body** — with the sections below

A ticket missing any of #1–6 lands in `pm:groom`'s Missing-fields bucket. The body-section requirements (see next section) are checked as part of #6.

## Description body structure

Sections in order. All optional **except `## Done when:` for tickets at status `Todo` or beyond**.

### `## Context` (optional)

One paragraph: why this ticket exists, what triggered it. Link to vault notes, related tickets, or conversations that motivated the work. Skip when the title alone makes the motivation obvious.

Example:
> Work Workspace's API Access controls block gcloud's default OAuth client from requesting Workspace scopes. Need a custom Desktop OAuth client in a Work-owned GCP project so `acmeos sheets fetch` works from local dev.

### `## Done when:` (REQUIRED for status ≥ Todo)

One or more bullets describing **observable, verifiable** completion criteria. Backlog tickets may omit this section; promoting to Todo requires it.

Good:
- `Done when: \`just sheets-fetch\` succeeds from a clean dev env using the new OAuth client.`
- `Done when: \`dim_customer\` includes alias-resolved Contract Source customers; \`pytest tests/test_dim_customer.py\` passes.`
- `Done when: \`/pm:groom\` produces a punch list against the live backlog without errors.`

Bad (aspirational / unverifiable):
- ~~`Done when: auth works correctly`~~ (no observable signal)
- ~~`Done when: tests pass`~~ (which tests?)
- ~~`Done when: this feels solid`~~ (not observable)

A ticket at status Todo or beyond missing this section lands in `pm:groom`'s Missing-fields bucket.

### `## NDR references` (optional but preferred)

`ndr:` references governing this ticket. The `pm:groom` NDR-moot bucket scans this section to detect tickets anchored to superseded decisions.

Three resolvable grains (per the `ndr` plugin):

- `ndr:0087` — atom ID; historical anchor that doesn't follow supersession
- `ndr:#auth-substrate` — slug; follows supersession to the current head
- `ndr:auth/perimeter` — area/topic pair; resolves to all current atoms in that slot

Format (one per line, with short label):

```
- ndr:0087 — auth perimeter (SPA-type browser OIDC)
- ndr:#monorepo-shape — current head
- ndr:backend/framework — all current backend-framework decisions
```

Inline `ndr:` mentions in the Context paragraph also count for the NDR-moot scan, but a dedicated section is preferred when the ticket is governed by ≥1 atom.

### `## Notes` (optional)

Anything else: observations, risk flags, decisions deferred, links to related work. Free-form.

### Spike variant

`Spike`-labeled tickets open with `## Question` instead of `## Context` — the unknown stated as a question, with the timebox in the description. Their `## Done when:` is always `question answered; finding written up` (vault note; ndr atom only if the finding resolves a decision) — never "code merged"; spike code is throwaway. Boundary test (Spike vs Decision) and full conventions live in `linear-workflow`'s "Spike vs Decision" section (linear plugin).

## Anti-conventions

- **No PR or branch links in titles or labels.** Solo direct-to-main workflow — tracking happens in Linear, not in branch names.
- **No `D# — phrase` titles.** Use the `Decision` label; the label carries the marker.
- **No conventional-commit prefixes (`feat:`, `fix:`, `chore:`) in titles.** House style is noun-phrase.
- **No `Bug` label.** Defects are `Feature` regressions or `Chore` cleanups depending on framing.
- **No Linear issue IDs inside source code, comments, docstrings, ADRs, or NDRs.** Per AcmeOS `CLAUDE.local.md`: references go ticket → code, not code → ticket.

## How the PM skills use this file

| Skill | Use |
|---|---|
| `pm:groom` | Missing-fields bucket checks #1–6 (description body checked against `## Done when:` requirement). NDR-moot bucket scans `## NDR references` section + inline `ndr:` mentions in prose. |
| `pm:triage` | Proposes specific missing pieces with this file's criteria (e.g. "no `Done when:` — propose: `Done when: <verifiable signal>`"). |
| `pm:author` | Uses the body structure as a template when drafting new tickets. |

## See also

- **`linear-workflow`** (linear plugin) — title, labels, priority, status flow, MCP call patterns
- **AcmeOS `CLAUDE.md`** — repo-level conventions and known gotchas
- **`Linear Setup.md`** in the vault — workspace shape (cycles, milestones, label groups, projects)
- **`CLAUDE.local.md`** in the AcmeOS repo — per-user conventions (e.g. no Linear IDs in code)

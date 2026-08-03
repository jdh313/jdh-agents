---
name: infra-review
description: >-
  Reviews an AWS Terraform pull request whose plans are produced by Atlantis,
  from a local checkout. This skill should be used when the user runs
  `/infra-review <pr-number-or-url>`, says "review this terraform PR", "infra
  review", "review the atlantis plan", "review this infrastructure change", or
  asks for an architecture/security review of a Terraform/Atlantis PR. Treats
  the Atlantis-posted plan as the review artifact, reconstructs before/after
  topology, and stays read-only against AWS and the PR until an explicit
  human-approved posting gate. NOT for application-code review (use
  `/code-review` or `/review`), non-Terraform IaC (CloudFormation, Pulumi, CDK),
  or repos that do not post Atlantis plans.
argument-hint: <pr-number-or-url>
allowed-tools:
  - Bash(gh *)
  - Bash(tflint *)
  - Bash(checkov *)
  - Bash(trivy *)
  - Bash(infracost *)
  - Bash(ndr *)
  - Bash(command -v *)
  - Read
  - Glob
  - Grep
  - AskUserQuestion
  - TodoWrite
---

Apply the orchestration mappings in [`../../RUNTIME.md`](../../RUNTIME.md).

# Infra Review (v0 — local-first)

Review an AWS Terraform PR whose plans are produced by **Atlantis**, run from a
local clone of the repo. Repo-agnostic: works on any Terraform + Atlantis repo.

## Core principle

**The `terraform plan` Atlantis posted is the review artifact — not the HCL
diff.** The diff says what the author typed; the plan says what will happen to
the cloud. Reconstruct the resource graph (compute, data stores, network paths,
IAM trust edges) and state the **before → after topology** before judging
safety or fit.

## Essential principles

1. **Never review a stale plan.** If the Atlantis plan predates the PR's head
   commit, STOP and tell the user to re-run `atlantis plan`. A plan that doesn't
   match the code under review is worse than no plan — it reviews fiction. (Phase 2.)
2. **Never post without per-run human approval.** Everything is read-only —
   against AWS and against the PR — until the posting gate. The user picks which
   findings post; nothing reaches a teammate's PR unilaterally. This gate is the
   point of v0 and is structurally unskippable. (Phase 7.)
3. **Flag truncation; never silently review a partial plan.** GitHub caps
   comment size; Atlantis truncates large plans. A partial plan yields a partial
   review — say so and mark the project `unverifiable`.
4. **Degrade gracefully on tooling.** Run whichever scanners are installed;
   report which were skipped. A missing scanner narrows coverage, it does not
   abort the review.
5. **Plain-text parsing is lossy.** v0 has no plan JSON (that is v1). Mark every
   finding's confidence; state caveats rather than overclaim from ambiguous text.

## When to use

- Reviewing a Terraform PR before approving/merging it, where Atlantis posts the plan.
- Auditing an infrastructure change for security, SPOFs, or destroy-and-recreate hazards.
- Checking whether a plan's actual resource changes match the PR's stated intent.
- Grounding an infra change against recorded decisions (NDR heads) in a tracked repo.

## When NOT to use

- **Application/library code review** — use `/code-review` or `/review`.
- **Non-Terraform IaC** (CloudFormation, CDK, Pulumi) — the plan-parsing assumes `terraform plan`.
- **Repos without Atlantis** — there is no plan artifact to fetch; this skill does not run `terraform plan` locally.
- **Re-planning or changing Atlantis config** — out of scope (v1+); v0 only reads what Atlantis already posted.

---

## Workflow

Pipeline of 7 phases. **At the start, create a runtime plan with the 7 phases** as the tracker,
then mark each `in_progress`/`completed` as you go. Phases 2 and 7 are **gates** —
the pipeline halts there until a condition is met (2) or the user approves (7).

### Phase 1 — Fetch
**Entry:** A PR number or URL was supplied; CWD is inside a Terraform repo clone.
**Actions:**
1. Resolve the PR: `gh pr view`, `gh pr diff`, and the Atlantis comments via `gh api`.
2. Group multi-comment plans by project (dir/workspace); detect truncation.
3. Confirm the local checkout matches the PR head (offer `gh pr checkout`; ask before switching a dirty tree).

Follow **[references/plan-parsing.md](references/plan-parsing.md)** for exact
commands, Atlantis-author detection, multi-comment grouping, and truncation markers.

**Exit:** Have the head SHA, the diff, the grouped per-project plan text, and a
truncation flag per project.

### Phase 2 — Staleness GATE (hard stop)
**Entry:** Phase 1 complete.
**Actions:**
1. For each project, verify its plan comment corresponds to the PR's current
   head commit — prefer an explicit SHA in the comment body; else confirm the
   latest plan comment's `created_at` is **after** the head commit's
   `committedDate` (per `plan-parsing.md` §4).
2. If any reviewed project's plan is **stale** (a commit landed after the plan):
   **STOP.** Report which projects are stale and tell the user to re-run
   `atlantis plan` (comment `atlantis plan` on the PR), then re-invoke. Do not
   proceed to review a stale project.

**Exit:** Every project to be reviewed has a confirmed-fresh plan — **or the
skill has halted.**

### Phase 3 — Mechanical pass
**Entry:** Phase 2 passed (fresh plans).
**Actions:**
1. Detect installed scanners; run the present ones against the **changed dirs**, credential-free.
2. Triage JSON output — dedupe across scanners, filter to the diff, severity-rank, map to `file:line` + resource.

Follow **[references/mechanical-scanners.md](references/mechanical-scanners.md)**
for per-scanner commands, JSON fields, and triage discipline.

**Exit:** A triaged mechanical-findings list, plus an explicit list of skipped scanners.

### Phase 4 — Decision grounding (conditional)
**Entry:** Phase 3 complete.
**Actions:**
1. Check for an `.ndr.toml` at the repo root (Glob). **If absent, skip this
   phase** and note "repo is not NDR-tracked" — the skill stays repo-agnostic.
2. If present, pull current decision heads via the `ndr` CLI:
   `ndr current --verbose`, then `ndr resolve <area/topic>` for the area the
   change touches (e.g. infra/networking, infra/data). Treat returned heads as
   **ground truth** for the intent check.

**Exit:** Relevant decision heads captured with their `ndr:` references, or
"not NDR-tracked" noted.

### Phase 5 — Architecture pass
**Entry:** Phases 1–4 complete.
**Actions:**
1. Reconstruct the **before → after topology** per project from the plan text + HCL diff.
2. Walk the review dimensions: plan-level hazards, security, change safety,
   architecture/resilience, one-way-vs-two-way doors, intent check.
3. Draft findings into two tiers, each with a confidence rating.

Follow **[references/review-dimensions.md](references/review-dimensions.md)** for
the topology-first method, per-dimension checklists, and the two-tier structure.

**Exit:** Tiered findings drafted: design concerns (with before/after) and
mechanical issues, each with confidence.

### Phase 6 — Report (terminal ONLY)
**Entry:** Phase 5 complete.
**Actions:**
1. Print to the terminal, in this order:
   - **Coverage line** — projects reviewed, scanners run/skipped, any truncated
     or `unverifiable` projects, NDR-tracked or not.
   - **Before → after topology** per project.
   - **Tier 1 — Design concerns** (before/after, risk, reversibility, recommendation).
   - **Tier 2 — Mechanical issues** (`file:line` + resource, inline-ready).
2. **Post nothing.** Output is terminal-only at this phase.

**Exit:** The full review is on screen; the PR is untouched.

### Phase 7 — Selective posting GATE (two confirmations, unskippable)
**Entry:** Phase 6 report presented.
**Actions:**
1. **GATE 1 — select.** Use the runtime's structured user-input capability (multi-select when available) listing each finding
   as an option, plus "post nothing". The user chooses which findings to post.
   Default is **post nothing**.
2. If the user selects none (or "post nothing"): stop here. Report nothing was posted.
3. **GATE 2 — confirm exact command.** Show the **exact** `gh pr review` command(s)
   that will run, with the rendered comment body. Ask for explicit yes/no.
4. On `yes`, post the approved findings:
   ```bash
   gh pr review "$PR" --comment --body "<approved findings, markdown>"
   ```
   (Inline mechanical comments may use `gh api repos/$OWNER_REPO/pulls/$PR/comments`
   with `commit_id`/`path`/`line` — still only the approved ones.)
5. Report exactly what was posted and what was withheld.

**Exit:** Only user-approved findings were posted (or nothing was). The user
knows precisely what landed on the PR.

---

## Quick reference

| Need | Command |
|------|---------|
| PR metadata + head SHA | `gh pr view "$PR" --json headRefOid,title,body,commits,url` |
| Changed paths | `gh pr diff "$PR" --name-only` |
| Atlantis comments | `gh api "repos/$OWNER_REPO/issues/$PR/comments" --paginate` |
| Decision heads | `ndr current --verbose` · `ndr resolve <area/topic>` |
| Post (after gate) | `gh pr review "$PR" --comment --body "..."` |

| Plan sigil | Meaning | Signal |
|------------|---------|--------|
| `+` / `~` / `-` | create / update / destroy | `-` on stateful = data loss |
| `-/+` | **replace (destroy+recreate)** | top hazard on stateful resources |

## Reference index

| File | Content |
|------|---------|
| [references/plan-parsing.md](references/plan-parsing.md) | Fetching PR + Atlantis comments via `gh`; multi-comment grouping; truncation detection; staleness verification; plan-text extraction |
| [references/mechanical-scanners.md](references/mechanical-scanners.md) | tflint / checkov / trivy / infracost — detection, JSON invocation, graceful degradation, triage |
| [references/review-dimensions.md](references/review-dimensions.md) | Topology reconstruction; per-dimension checklists; two-tier findings structure |

## Success criteria

- [ ] Atlantis plan fetched and confirmed **fresh** vs PR head (Phase 2 passed or skill halted).
- [ ] Truncated/partial plans flagged; affected projects marked `unverifiable`.
- [ ] Scanners run where installed; skipped ones reported.
- [ ] NDR heads consulted iff the repo is NDR-tracked.
- [ ] Before → after topology stated per project before any judgment.
- [ ] Findings tiered (design vs mechanical), each with confidence.
- [ ] Report printed to terminal only; **nothing posted without both gates passing.**

## Future (out of scope for v0)

v0 reads only what Atlantis already posted (plain-text plan comments). **Not
built here:** the v1 S3 `$SHOWFILE` plan-JSON artifact path (enables structured
`terraform show -json` parsing), Atlantis workflow/policy-check (Conftest/OPA)
changes, CI promotion as a merge gate, and any companion subagent. See the
design note `Work/Infra Review Agent.md` (Rollout Plan) for the full arc.

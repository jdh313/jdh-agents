# Upstream divergences — grill

_Upstream: `mattpocock/skills` · `skills/productivity/grilling` · ledger current as of `reviewed_sha: 697d4ce9742d`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (intake, 2026-07-27) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

All four upstream moves port intact: the decision-tree walk with a recommended answer per question, the one-question-at-a-time block, the fact/decision split, and the shared-understanding gate before acting. Nothing dropped, nothing fabricated.

| Kind | What | Why |
|------|------|-----|
| changed | Name `grilling` → `grill`. | `craft:grill-with-docs` was already named as a specialization of a primitive called "grill"; the bare imperative also matches craft's house style (`diagnose`, `prototype`, `grok`, `tdd`). |
| changed | Voice: upstream is first-person, the user speaking to the agent ("Interview me", "put each one to me", "my answer") → second-person, agent-facing. | Every craft skill body is written as instructions to the agent. Behavior is identical; only the addressee changes. |
| changed | Description trigger surface narrowed: upstream's `Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases` → grill-specific phrasing only. | The "stress-test their thinking" clause is a wide net that competes with three model-invocable siblings — `debate:debate` ("should I", "X vs Y"), `craft:design-by-stories` ("let's design X"), and `ndr:interrogate-decision` ("stress-test this before I capture it"). Narrowing the description is a cleaner fix than a soft "explicit invocation only" prohibition, and keeps the skill auto-firing where it should. |
| changed | Fact-lookup scope: upstream's `exploring the environment (filesystem, tools, etc.)` → `(filesystem, tools, connected apps)`. | Names the MCP/connected-app surface this ecosystem actually has, per `../../RUNTIME.md`'s private-workspace-data rule. Same move, enumerated for the runtime. |
| added | `allowed-tools: Read, Grep, Glob`. | Upstream declares none. The fact-lookup move requires filesystem reads; pre-approving them keeps the interview from stalling on permission prompts mid-loop. |
| not-added | `disable-model-invocation: true`, and the `grill-me` sibling skill that carries it upstream. | The flag strips a skill's description from the agent's reach, so **no other skill can dispatch it** (`skillsmith:writing-great-skills`). `craft:improve-codebase-architecture` and `craft:grill-with-docs` both dispatch this skill; the flag would break exactly the wiring this port exists to create. Explicit `/grill` invocation still works without it. |
| not-added | `agents/openai.yaml` interface metadata. | Codex manifests in this marketplace are generated from `PACKAGE.yaml`, not authored per-skill. |
| not-added | `../../RUNTIME.md` preamble. | This skill dispatches nothing and spawns nothing, so no orchestration terms need runtime mapping — matching `diagnose`, `prototype`, and `zoom-out`. |

## Provenance note — where this content lived before

The four loop moves were already in this marketplace, inlined into `craft:grill-with-docs` at its adoption, because upstream's `grill-with-docs` is a thin dispatcher over `/grilling` and we chose to flatten it. That inlined copy silently rotted: upstream `170ad48` (2026-07-13) renamed "design tree" → "decision tree" and rescoped "codebase" → "environment", but `grill-with-docs`'s provenance pins `skills/engineering/grill-with-docs`, so a path-scoped drift check could never see a commit to `skills/productivity/grilling`. **Content inlined from another skill's upstream path is invisible to drift review.** Extracting the loop here — pinned to the path that actually governs it — closes that hole. See `../grill-with-docs/UPSTREAM.md` for the reversal of the original no-extract decision.

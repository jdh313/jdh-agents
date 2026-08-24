---
id: "m7pd8d"
title: Package a shared vocabulary as a plugin-root reference, not a skill
status: current
decision_date: 2026-08-24
author: Jacob Hoehler
conviction: strong
project: jdh-agents
labels:
  - architecture
  - repo-shape
binds:
  - plugins/*/PACKAGE.yaml
  - plugins/craft/**
supersedes: []
superseded_by: []
derived_from: []
informed_by:
  - 6x3v6p
  - v4wn6d
  - kpefq4
---

# m7pd8d — Package a shared vocabulary as a plugin-root reference, not a skill

## Decision

Shared vocabulary consumed by sibling skills lives as a plugin-root markdown file reached by relative path, not as a model-invoked skill. A skill earns its registry entry by owning a procedure; a glossary that only defines terms does not.

## Scope

- Binds: artifacts in this marketplace whose content is definitional — glossaries, term lists, shared conventions — consumed by two or more sibling skills in the same plugin.
- Does not bind: reference material consumed by exactly one skill, which belongs in that skill's own directory.
- Does not bind: cross-plugin sharing, where no relative path resolves.

## Commitments

- A new plugin-root reference must be declared in that package's `payloads.include`. The compiler copies an explicit allowlist, not the directory — an undeclared file stays in source and never reaches either compiled tree.
- After adding one, confirm the file exists under both `marketplaces/claude/` and `marketplaces/codex/` before committing. `marketplace check` passes while a declared consumer points at a file absent from both trees, so the gate does not cover this.
- Every consumer restates inline whatever discipline the reference enforces, per `ndr:6x3v6p`. The link carries definitions; it does not carry obligations.
- Retiring a skill this way forfeits user invocation of it. Accept that cost only where no procedure is being removed.
- Attribution for adapted third-party content must move with the content, into the receiving skills' `UPSTREAM.md` files and `THIRD-PARTY-NOTICES.md`.

## Revisit if

- The harness gains a way to keep a skill model-invocable while withholding it from the router's trigger matching.
- A third consumer needs one of the procedures now co-located with its sole caller.
- The compiler begins projecting plugin-root files without an explicit `payloads.include` entry.

## Context

- `craft:codebase-design` carried a description claiming it could "find deepening opportunities," the same trigger phrase as `craft:improve-codebase-architecture`.
- Eight of its nine inbound references were glossary lookups; one invoked a procedure.
- Its body had no Process section and its frontmatter granted no `Write` tool.
- `RUNTIME.md` and `CONTEXT.md` already sat at the `craft` plugin root and were reached by nine skills via `../../` relative paths.
- Both files reached the compiled Claude and Codex trees because `PACKAGE.yaml` named them under `payloads.include`.
- A first compile of the new reference produced a file present in source and absent from both compiled trees, and the full `marketplace check` reported all checks passed.
- `disable-model-invocation: true` exists as a frontmatter construct, and withholds a skill from the model while leaving it user-invocable.

## Why

Two artifacts competing on one trigger phrase make routing a coin flip, and no description rewrite fixes it while both remain in the registry — the collision is structural. Removing one from the registry is the only move that resolves it rather than papering over it, which settles the question of whether to redescribe or retire.

Reference is the right destination because it matches what the consumers actually do. The vocabulary's purpose is that consuming skills name things identically, which requires the terms verbatim in the consumer's own context. A relative-path read delivers exactly that, and it is a structural condition in the sense `ndr:v4wn6d` requires — the file is read or it is not, where a `Skill()` dispatch depended on the agent electing to invoke. It is also target-neutral where `Skill(craft:codebase-design)` is Claude-flavored syntax, which `ndr:kpefq4` prefers.

The cost is real and bounded: the glossary is no longer user-invocable. That is acceptable only because nothing procedural was lost — the two procedures moved to their sole caller rather than being deleted.

The verification commitment above is load-bearing rather than incidental. The failure mode it guards is silent in both directions: the source tree looks correct, and the merge gate reports success, while every consumer in every install points at nothing. A convention whose breakage is invisible to its own gate needs the check written down.

## Alternatives

- **Rewrite both descriptions to disambiguate** — rejected: both entries stay in the registry, so the router still weighs two candidates on overlapping trigger phrases.
- **Keep it as a skill but withhold it from direct user invocation** — rejected: `disable-model-invocation` points the wrong way, withholding a skill from the model rather than the user, and the collision is a router problem that a user-facing change cannot reach.
- **Convert it to an agent** — rejected: an agent returns a synthesis and terminates, so consumers would receive a paraphrase of the terms they must reproduce exactly, which is the drift the vocabulary exists to prevent.
- **Restore the former `references/LANGUAGE.md` path** — rejected: `payloads.include` excludes `skills/*/references/**` from projection, and plugin root is where the two working precedents already live.

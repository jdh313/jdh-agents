---
id: "a8bqxj"
title: Derive enrollment assertions from an exclusion list
status: current
decision_date: 2026-08-03
author: Jacob Hoehler
conviction: tentative
project: cc-marketplace
labels:
  - process
  - write-side
binds:
  - scripts/tests/**
supersedes: []
superseded_by: []
derived_from:
  - linear:TEAM-352
  - https://github.com/jdh313/cc-marketplace/pull/26
informed_by: []
---

# a8bqxj — Derive enrollment assertions from an exclusion list

## Decision

Test assertions about which packages a target enrolls derive that set from the full catalog minus a named exclusion list, rather than enumerating the enrolled packages directly. A new package is then enrolled by default in the assertion, and leaving it out requires saying so.

## Scope

- Binds: acceptance assertions over publication membership and generated counts.
- Does not bind: assertions about a single package's own content, which name that package directly.

## Commitments

- Each exclusion carries a comment naming why the package is out and what would put it back.
- The enrolled set has one owning definition; other test modules import it rather than restating it.

## Revisit if

- Targets diverge enough that enrollment is better expressed per-target than as catalog-minus-exclusions.
- The exclusion list grows large enough that reading it stops conveying the shape of the catalog.

## Context

- Assertions enumerated the enrolled packages as a literal set and a literal count.
- Three separate test modules each carried their own copy of that set.
- Adding seven packages required editing every copy, and the literals had already drifted behind the catalog once.
- A package that is silently absent from an enumerated set is not tested, and nothing reports that it went unchecked.

## Why

The failure modes of the two shapes are not symmetric. An enumerated set that falls behind under-checks silently: the suite still passes, over a smaller catalog than exists, and the gap is invisible because a passing test looks the same either way. A derived set that falls behind fails loudly the moment a package is added without a decision about it, and the failure names the package.

Loud-and-wrong is strictly preferable to quiet-and-incomplete for an acceptance assertion, whose entire job is to notice. Choosing the shape whose failure mode is noisy costs nothing at author time and converts a class of silent drift into a build error.

The exclusion list also puts the interesting fact where it can be read. A literal set of fourteen names does not say which package is missing or why; a full catalog minus a named exclusion says both, at the point where someone would otherwise have to reconstruct it.

Conviction is tentative because this is a small structural preference proven on one catalog, and a target whose enrollment is genuinely unrelated to the catalog would make the derivation more contrived than clarifying.

## Alternatives

- **Enumerate the enrolled set literally** — rejected: its failure mode is a silently smaller catalog, which is the one outcome an acceptance assertion must not have.
- **Derive the set from the compiled registry at test time** — rejected: the assertion would then be checking the output against itself, and could never detect a package that failed to enroll.

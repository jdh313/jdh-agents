# Shake Tune and Skillsmith runtime acceptance

Recorded 2026-09-22 from an authenticated Luna run against the freshly
installed Codex marketplace packages:

- `shake-tune` 0.5.0
- `skillsmith` 2.2.0
- Codex CLI 0.155.1, model `gpt-5.6-luna`

This record is observed runtime evidence. It is separate from AgentForge
compilation, generated publications, and source mappings.

## Shake Tune

The installed router was invoked with a multi-image diagnostic request and
the scope `all available tests + missing excitation`. It dispatched exactly
five sequential, bounded, read-only analyzers:

| Analyzer | Input | Observed result |
| --- | --- | --- |
| `shaper-analyzer` | `shaper-x.png`, `shaper-y.png` | Read both synthetic traces. X had irregular alternating peaks/valleys; Y was smooth/increasing without a distinct peak. No numeric shaper recommendation was made because the images had no units, labels, profile, or history. |
| `belt-analyzer` | `belts.png` | Read the synthetic trace. No reliable belt comparison or mechanical diagnosis was made from one unlabeled image. |
| `vibration-analyzer` | `vibration.png` | Read the synthetic increasing trace. No reliable frequency, amplitude, or diagnosis was made without peaks, axes, units, or scale. |
| `axes-map-analyzer` | `axes-map.png` | Read the synthetic circular/diagonal plot. No calibration claim was made without labels, scale, legend, or metadata. |
| `excitate-analyzer` | no `staticfreq_*.png` supplied | Correctly reported that excitation could not be analyzed and requested the missing static-frequency image. |

All four supplied PNGs were read successfully. They were synthetic fixtures,
so this run proves routing, bounded analyzer dispatch, multimodal input
handling, uncertainty reporting, and the no-write boundary; it does not prove
mechanical conclusions or numeric tuning on authentic Shake Tune exports. The
run created or modified no files, configuration, or history.

## Skillsmith

### `writing-for-agents`

The installed skill and its companion references were read, including
`references/SKILL-MECHANICS.md`, `references/GLOSSARY.md`, and
`references/ADDENDA.md`. An inline draft was reviewed for runtime selection,
branch-specific reference loading, explicit ordered steps, observable
completion criteria, target-runtime tool boundaries, and approval-gated
no-write behavior.

The observed assessment was **partially predictable, not yet sufficient**:
the draft had the right controls, but did not make runtime detection,
branch-to-reference mapping, step order, or per-step completion evidence
checkable. The review recommended naming Claude/Codex enforcement differences
and the concrete fallback mechanism, and either inlining universally needed
material or naming the trigger for each referenced branch.

### `upstream-review`

The installed review procedure inspected the adapted local
`writing-for-agents` skill and its ledger, then fetched the upstream path
`mattpocock/skills` / `skills/productivity/writing-for-agents` using `gh api`
and base64 decoding. The reviewed SHA was `321658273cb1`; the latest
path-touching commit matched it, so no upstream drift was observed.

The review classified the core writing concepts as kept, the local
`references/` layout and richer model-facing description as packaging/runtime
divergences, Claude/Codex runtime guidance as added behavior, and upstream
`agents/openai.yaml` as dropped metadata. No fabricated upstream attribution
was found. It did identify a ledger gap: the local runtime-split section is
not upstream, and the ledger's broad adopted/no-dropped-content wording should
be narrowed or updated. The procedure ran inline, made no writes, and the
final `git diff --quiet` check returned zero.

## Harness boundary

An unauthenticated fresh `CODEX_HOME` smoke path remains blocked separately:

```text
401 Unauthorized: Missing bearer or basic authentication in header
```

That is a CLI authentication-harness blocker, not the result of the
authenticated Luna runtime traces above. The traces also do not establish
hard sandbox enforcement: no-write behavior was observed under explicit
read-only prompts and inspected diffs, not proven as an independent policy
mechanism.

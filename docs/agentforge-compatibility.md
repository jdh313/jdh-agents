# AgentForge compatibility

`MARKETPLACE.yaml` and each plugin's `PACKAGE.yaml` are the authoritative
AgentForge collection definitions. Native Claude and Codex manifests remain
committed at the repository paths consumed by both runtimes, but they are now
generated outputs rather than independently maintained metadata.

The compiler baseline for this enrollment is AgentForge commit `0ebebbb`
(`agentforge` 0.0.1).

## Acceptance-suite ownership

cc-marketplace owns full-corpus acceptance and drift detection against its real
canonical `MARKETPLACE.yaml`. AgentForge retains its focused five-package
compiler fixture as compiler-level coverage; that fixture is not a substitute
for validating all sixteen packages in this repository.

The cc-marketplace suite runs the pinned compiler twice in separate temporary
output roots and compares paths, file types, bytes, and normalized permissions.
It then runs AgentForge's read-only `check` command and exercises drift in five
dimensions: changed content, a missing file, an extra file, changed registry
metadata, and changed permissions. Every drift case fingerprints the generated
tree before and after the check to prove that checking does not repair or
rewrite output.

The merge gate also applies the runtime-native checks that are available:

- `claude plugin validate --strict` validates the complete generated Claude
  publication.
- `uv run marketplace validate --format codex` validates the generated Codex
  marketplace and only its seven declared packages. It checks local source
  resolution, manifest identity and semantic versions, required skill metadata,
  explicit-only sidecars, and exact agreement between declared and materialized
  package directories. Codex currently provides marketplace management but no
  non-interactive `plugin validate` command, so this is cc-marketplace's native
  Codex validation boundary.

Generated publication roots are committed, not disposable. `uv run marketplace
sync` compiles complete publications into `marketplaces/claude/` (196 files, 16
packages) and `marketplaces/codex/` (120 files, 7 packages), and each root is
self-contained enough for its runtime to be pointed directly at it. `sync
--check` recompiles into a temporary root and diffs the whole tree — content and
executable bits — against the committed one; it never writes. The acceptance
suite likewise never updates checked-in output.

An earlier revision projected only the native manifest files back into the
source tree and discarded every compiled body. That left the repository root
acting as both canonical source and partial publication, which is what let a
Codex marketplace rooted at the repository install canonical Claude sources
instead of the Codex projection.

AgentForge owns explicit-only skill translation. When a canonical Claude skill
declares `disable-model-invocation: true`, the Codex projection generates a
skill-local `agents/openai.yaml` containing
`policy.allow_implicit_invocation: false`. Supplied sidecars remain subject to
AgentForge's normal collision policy and cannot silently replace generated
policy. cc-marketplace owns verifying those compiler results across the real
16-package corpus and validating the seven declared Codex packages; it does not
duplicate the translation in repository tooling.

## Target enrollment

- Claude enrolls all sixteen packages with `all-compatible`.
- Codex enrolls fourteen: `coach`, `commit`, `compass`, `craft`, `debate`,
  `feedback`, `introspect`, `librarian`, `linear`, `pm`, `shake-tune`,
  `skillsmith`, `spec-flow`, and `teach`.
- `langfuse` and `attention-workflow` are the two packages that do not declare
  Codex support, and both omissions are deliberate rather than pending. See the
  entries below.

`feedback` carries a **native mapping but not yet fresh-runtime acceptance**.
Its Codex projection compiles, validates, and is drift-clean, and its report
format was rewritten to name surfaces by intent rather than by Claude's surface
set. The Codex smoke test in TEAM-342 has not been run — no Codex runtime was
available — so under `ndr:v0a3bm` this package is enrolled on the mapping half
of the gate only. Treat its Codex support as unverified until that test runs.

`langfuse` is **deliberately not enrolled for Codex**, and the reason is not
that it fails to compile. It compiles cleanly: both its `Stop` and
`SessionStart` events are Codex lifecycle events, the argument arrays fold into
Codex's single `command` string with meaning preserved, `${CLAUDE_PLUGIN_ROOT}`
becomes `${PLUGIN_ROOT}`, and the executable payload keeps its `0755` mode. The
plugin would install and its hooks would fire.

They would also produce nothing. The `Stop` hook exists to parse a session
transcript, and it keys on Claude Code's JSONL row shape — `msg["type"]` in
`("user", "assistant")`, then `msg["message"]["role"]`. Codex rollout rows are
`{"type": "response_item", "payload": {…}}`: they carry `payload`, never
`message`, and their `type` values are `session_meta`, `event_msg`,
`response_item`, `world_state`, `turn_context`, and `compacted`. Run against
three real Codex rollouts, the plugin's own parser resolved **0 turns from
8,127 rows**. Every row falls to the unknown tally and no turn is ever flushed.

Enrolling it would therefore ship a package that runs `uv` on every turn, reads
a transcript it cannot parse, writes `Processed 0 turns` to a `~/.claude`-named
log on a Codex machine, and exits 0 — silent, continuous, and indistinguishable
from working. An observability tool that fails silently is worse than an absent
one, because it retires the user's suspicion that anything is wrong. Enrollment
waits on TEAM-350, which owns porting the transcript reader to dispatch on
payload shape so one file serves both runtimes.

Target omission is an explicit compatibility decision. AgentForge must not emit
an empty or untested package merely because its definition validates.

## Source and payload handling

- Skill `SKILL.md` files are canonical skill artifacts. Nested `scripts/`,
  `references/`, and `assets/` are projected by the skill renderer.
- Package agents, commands, and hooks are declared as their native artifact
  types. Claude preserves those artifacts directly.
- Package-root references, `craft/CONTEXT.md`, and arbitrary skill sidecars are
  supplied payloads.
- The commit guard, Langfuse hook companions, and the attention-workflow hooks
  and state helper are Claude-only payloads.
- Native plugin manifests are represented by canonical defaults and target
  overlays, never copied as payloads.
- Plugin READMEs stay in the source repository but are intentionally excluded
  from runtime payloads.
- Symbolic links are not supported as package payload sources. The enrolled
  inventory contains none.

AgentForge derives executable intent from source mode. The commit guard, the
Langfuse tripwire, and the two attention-workflow hook scripts are the
executable payloads and compile as `0755`; all other compiled files normalize to
`0644`. `attention-workflow`'s `scripts/aw_state.py` is invoked as
`python3 <path>` by the skill and the verifier agent, so it is a plain payload.

## Claude compatibility

All sixteen packages compile for Claude and pass `claude plugin validate
--strict`. The canonical marketplace omits three legacy generated metadata
fields—`metadata.homepage`, `metadata.totalPlugins`, and
`metadata.lastUpdated`—because current strict validation reports them as
unknown. Supported `metadata.description` and `metadata.version` remain.

Skill names are leaf identifiers in canonical source. Claude applies the plugin
namespace at runtime, so `skills/today` declares `name: today` and is invoked as
`coach:today` after installation.

## Codex compatibility

The fourteen-package publication compiles and passes cc-marketplace's
Codex-native validator. Compilation diagnostics are reviewed limitations, not
parity claims:

- `coach`: sixteen skills strip `allowed-tools` (all) and `when_to_use`
  (several); three — `checkin`, `decide`, and `spark` — also strip
  `disallowed-tools`, and three agents (`momentum`, `overdue-rescue`,
  `project-pulse`) lose their `tools:` allowlist as a declared
  `agent-tools-filter` loss. Disposition: **accepted.** `allowed-tools`,
  `when_to_use`, and `effort` are the same permission-prompt and
  reasoning-budget conveniences accepted elsewhere. The `disallowed-tools`
  loss needed more than that. Those three skills are designed never to write —
  no adding, updating, or completing a Todoist task; no creating, saving, or
  updating a Linear issue or project — and unlike `compass`'s `reflect` and
  `mull`, that boundary did not originally survive anywhere in body prose.
  It was the frontmatter or nothing. Each of the three now states the same
  boundary in its body, where it holds on any runtime regardless of what the
  frontmatter can carry; `disallowed-tools` stays in place and continues to
  enforce on Claude. Note also that all sixteen skills are ungated — none
  declares `disable-model-invocation` — making `coach` the largest single
  contributor to the Codex skills-context budget in this publication.
- `commit`: `allowed-tools` is stripped. The PreToolUse hook is translated into
  Codex's handler schema and the executable guard ships with it at `0755`;
  `${CLAUDE_PLUGIN_ROOT}` becomes the native `${PLUGIN_ROOT}`. Codex skips
  plugin-bundled hooks until the user reviews and trusts the definition, so the
  guard is present but inert until then.
- `compass`: four fields are stripped on all three skills — `argument-hint`,
  `allowed-tools`, `disallowed-tools`, and `effort` — and none is a declarable
  loss. Disposition: **accepted.** `allowed-tools` is a permission-prompt
  convenience rather than a capability; `argument-hint` documents an
  autocomplete hint whose guidance already survives in each skill's body;
  `effort` requests a reasoning budget Codex does not expose. All three skills
  declare `disable-model-invocation: true`, which is translated rather than
  stripped — see the explicit-only note above.
  `disallowed-tools` is the one worth stating plainly. Codex enforces no tool
  filter, so the field is stripped there exactly as `allowed-tools` is — and on
  `reflect` and `mull` it was the *only* enforcement of a no-research /
  no-delegate boundary. That boundary is now stated in each skill's body prose,
  where it survives to any runtime regardless of what the frontmatter can carry.
  Under the previous compiler baseline `a0701ec` this field was additionally
  invisible: absent from the canonical schema, discarded at parse, and reported
  nowhere. AgentForge tracked that as L-001 and fixed it; under the current
  baseline `0ebebbb` the key is enumerated, round-trips into the Claude
  projection, and is reported as stripped on Codex. The enforcement gap is
  unchanged — only its visibility improved, so the prose remains load-bearing.
  No `targets.codex.losses` entries: the two declarable constructs the package
  once carried — a `$ARGUMENTS` body template variable and `mcp__*` tool
  identifiers in prose — were rewritten to name intent rather than declared.
- `craft`: Claude-only invocation and tool-policy fields are stripped where
  reported.
- `debate`: the skill's `allowed-tools` is stripped, and `advocate`,
  `fact-checker`, `devils-advocate`, and `synthesizer` project as Codex role
  procedures. Disposition: **accepted, with the research fence restated in
  prose.** `agent-tools-filter` is a declared loss — Codex runs all four
  unrestricted rather than fenced to web-only research (the first three) or
  read-only (the synthesizer). Only `advocate` originally carried that fence
  in body prose; the other three now do as well, each in its own terms, since
  the synthesizer's boundary is not "web-only research" but "work the evidence
  you were given and gather none of your own." Worth separating from the loss:
  cross-advocate isolation and the synthesizer's independence from orchestrator
  framing are **structural** — separate dispatches, no shared transcripts, raw
  evidence passed in-prompt — and never depended on the tool fence at all. Both
  hold unchanged on Codex.
- `feedback`: two fields are stripped, and neither is a declarable loss —
  the `session` skill's `argument-hint` and `allowed-tools`, and the `triage`
  skill's `argument-hint`. Disposition: **accepted, no behavioral gap worth
  gating.** The `allowed-tools` entries (`Bash(git rev-parse *)`, `Bash(date *)`)
  are a permission-prompt convenience, not a capability — a Codex tester is
  prompted where a Claude tester is not. The `argument-hint` values document the
  optional `--save` flag and triage's path argument; both are restated in each
  skill's body, so the guidance survives even though the autocomplete hint does
  not. No `targets.codex.losses` entries: the package declares zero Claude-only
  constructs, which is the whole reason it was picked as the M2 opener.
- `introspect`: nothing is stripped. The `usage-report` body's
  `${CLAUDE_PLUGIN_ROOT}` is **translated** to `${PLUGIN_ROOT}`, so no loss is
  declarable and none is declared. Disposition: **accepted, with a scope note
  at the point of discovery.** The skill reads `~/.claude` transcripts, so a
  Codex user running it gets a report about a *different* runtime's session
  history than the one invoking it. That is inherent to what the skill
  measures, not a translation defect, but it is surprising enough that the
  Codex `longDescription` states it outright rather than leaving a user to
  discover it from an empty or foreign-looking report.
- `librarian`: Claude-only policy fields are stripped. Four Claude agents
  become reusable Codex role procedures without Claude model, turn, or tool
  enforcement.
- `linear`: the doctor skill's `allowed-tools` field is stripped.
- `pm`: `argument-hint` and `allowed-tools` are stripped on all three skills,
  neither a declarable loss, for the same reasons as `compass` and `feedback`
  above. Disposition: **accepted, with eleven of twelve tool references
  rewritten.** The package carried twelve body `mcp__linear-server__*` and
  `mcp__obsidian-mcp__*` references. Eleven were decorative — the sentence
  named a generic action and read identically once the tool name became
  "Linear" or "the vault" ("fetch via `mcp__linear-server__get_issue`" →
  "fetch it from Linear") — and were rewritten to name intent, following
  `compass`. One was not. `groom`'s step 2 documents a specific Linear MCP
  call-shape gotcha: `list_cycles({type: "current"})` must resolve the cycle's
  numeric name before it is passed to `list_issues({cycle: N})`, because
  passing `cycle: "current"` directly returns `[]` silently. Rewriting that
  would either drop the warning or assert a behavior for a Codex user's Linear
  access that nothing here has evidence for, so it is declared
  `mcp-tool-reference` / `retained-unenforced` in the `linear` manner instead.
- `shake-tune`: the skill's `argument-hint` and `allowed-tools` are stripped,
  and five analyzer agents — `axes-map`, `belt`, `excitate`, `shaper`,
  `vibration` — project as inferred Codex role procedures. Disposition:
  **accepted, one loss declared and one gap documented for want of a
  construct.** `agent-tools-filter` is declared: Codex enforces no allowlist,
  so all five agents' read-only `Read`/`Glob`/`Grep` scoping is unenforced, and
  a role standing in for one could write to printer config. The second gap has
  no declaration mechanism. The author tiers model and effort per agent —
  `opus`/high for the three PSD and spectrogram interpretation agents,
  `inherit`/low for the two mechanical checks — and Codex ignores that tiering,
  running all five at whatever model the session is on. No `agent-model-pin`
  construct exists (see the note below on the closed construct set), so it is
  recorded in the plugin's loss note as prose rather than declared. Neither
  boundary is restated in agent body prose; both rode entirely on frontmatter.
- `skillsmith`: `upstream-review` strips `allowed-tools`, `disallowed-tools`,
  and `effort`; `writing-great-skills`'s `disable-model-invocation: true` is
  translated to a skill-local `agents/openai.yaml`, keeping it explicit-only.
  Disposition: **accepted.** The `upstream-reviewer` agent projects as a role
  procedure and loses its `Read, Grep, Glob, Bash(gh api *), Bash(base64 *)`
  allowlist as a declared `agent-tools-filter` loss, but its read-only boundary
  already survives in body prose — "Read-only: never write, edit, or delete
  files" — so the agent is undirected on Codex rather than unsafe.
- `spec-flow`: the verifier becomes a reusable role procedure. The `spec-flow`
  dispatcher is a user-invocable skill, so its `disable-model-invocation` flag
  is translated rather than lost. Claude argument hints and tool restrictions
  are retained as source evidence but are not enforced by Codex.
- `teach`: `argument-hint`, `allowed-tools`, `disallowed-tools`, and `effort`
  are stripped, none a declarable loss, for the same reasons as `compass` and
  `feedback` above; `disable-model-invocation: true` is translated to the
  skill-local `agents/openai.yaml`, keeping the skill explicit-only.
  Disposition: **accepted, with a mixed outcome on two tool references.** The
  `mcp__obsidian-mcp__patch_note` mention was rewritten to name intent: the
  sentence already named three mechanisms for editing notes, and losing the
  middle identifier does not break it. The DEVONthink reference was not.
  `teach`'s "search DEVONthink first" step surfaces the user's owned textbooks
  — the highest-trust source class the skill prioritizes — before falling back
  to the web, and Codex has no DEVONthink integration to substitute. Rewriting
  it would have turned a real instruction into a silent no-op, so it is
  declared `mcp-tool-reference` / `retained-unenforced` and a Codex user is
  told plainly that teaching proceeds from web sources only. Note that `teach`
  also hard-requires an Obsidian vault via `obsidian-cli` on both runtimes;
  that is a local dependency, not a Codex gap, and is stated in the
  `longDescription`.

Constructs that would otherwise be lost with nothing reported must be declared
in canonical YAML under `targets.codex.losses`, and compilation fails
against the declaration when one is missing. Three constructs are gated today:
an agent `tools:` filter (`coach`, `debate`, `librarian`, `shake-tune`,
`skillsmith`, `spec-flow`), an `mcp__*` tool reference (`librarian`, `linear`,
`pm`, `spec-flow`, `teach`), and a `$ARGUMENTS` body template variable
(`librarian`, `spec-flow`). A skill's own `allowed-tools` is not among them — it is stripped
with a warning, not a declared loss, so converting a command to a skill trades
a gated construct for a reported one. A construct that is translated rather
than lost — `disable-model-invocation`, or a hook
handler's `args` folded into `command` — reports a warning instead; see the
TEAM-341 companion for that narrowing.

Declaring a loss does not buy silence. Every declaration that matches a
detected construct emits a `declared-loss` note on each compile and check,
carrying the author's statement of what a Codex user does not get.

**The declarable set is closed, and two real losses fall outside it.** A
`losses` entry's `construct` is validated against a fixed enum, so a loss with
no matching construct name cannot be declared at all — it can only be written
into some other entry's prose, which is where both of the following currently
live.

The first is agent **model and effort pinning**. The construct detector reads
only `tools:` from agent frontmatter; nothing reads `model:` or `effort:`. The
`inferred-artifact-projection` note does say "Claude model, turn, and tool
constraints … are not enforced by Codex," but that sentence is fixed boilerplate
emitted for every agent — it never names the pinned value, so it reads the same
whether an agent pins `opus` or inherits. Any package that tiers its agents by
model loses that tiering on Codex with no diagnostic naming it. `shake-tune` is
where this surfaced, but it applies equally to `coach`, `debate`, `librarian`,
`skillsmith`, and `spec-flow`.

The second is **hook-event support**, which is not in the capability table at
all. `ConstructSurface` admits only `skill` and `prompt`, so `supportFor`
cannot be asked whether a hook event exists on a target. The answer instead
lives in a hardcoded set inside the Codex marketplace adapter whose only
citation is a code comment — outside the per-row doc-citation discipline every
other capability fact is held to. The set is accurate as of codex 0.146.0,
verified against the binary's embedded JSON schemas, but nothing structural
keeps it that way.

Both are AgentForge gaps rather than cc-marketplace ones, and both are tracked
separately. They are recorded here because a reader auditing this document's
dispositions would otherwise reasonably conclude that a construct absent from
the gated list is a construct that does not exist.

Schema validation and deterministic compilation establish collection integrity,
not behavioral equivalence.

## Reproducing the gate

Use a checkout at the recorded compiler baseline:

```bash
export AGENTFORGE_PROJECT=/path/to/agentforge-at-0ebebbb
uv run marketplace sync
uv run marketplace check
uv run pytest -q

# Verify the committed publications, not a throwaway compile.
bun run "$AGENTFORGE_PROJECT/src/cli.ts" check \
  MARKETPLACE.yaml --out marketplaces --claude-native
```

CI checks out `jdh313/agentforge` at full commit
`0ebebbb8f0cf23f9223792a4b625ca302c9d655d`. Since that repository is private,
the workflow requires the `AGENTFORGE_DEPLOY_KEY` repository secret with read
access and fails closed when it is not configured. The runner toolchain pins
Bun `1.3.14` and Claude Code `2.1.216`, the versions used for the local
acceptance run.

Runtime references: [Claude plugin validation](https://code.claude.com/docs/en/plugin-marketplaces#validation-and-testing)
and [Codex plugin and marketplace structure](https://developers.openai.com/codex/plugins/build/).

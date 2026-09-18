# AgentForge compatibility

`MARKETPLACE.yaml` and each plugin's `PACKAGE.yaml` are the authoritative
AgentForge collection definitions. Native Claude and Codex manifests remain
committed at the repository paths consumed by both runtimes, but they are now
generated outputs rather than independently maintained metadata.

The compiler baseline for this enrollment is the AgentForge **v0.4.0** release
binary, pinned by version and per-platform sha256 in
[`scripts/agentforge.sh`](../scripts/agentforge.sh).
The pin is a release identity rather than a source revision so that CI and a
local run execute the same bytes; a source build at the equivalent commit is
not byte-identical to the published asset.

That pin does not currently validate this tree. `librarian` and `skillsmith`
declare a `body-agent-reference` loss — a construct AgentForge added after
v0.4.0 — so the pinned binary rejects the definition on an invalid enum before
it diffs anything, and the regenerated `marketplaces/` tree for those two
packages is therefore not committed either. The gate is restored by bumping
`AGENTFORGE_VERSION` to a release carrying that construct and recompiling; this
is a release prerequisite, not a supported state.

## Gate ownership

Acceptance and drift detection are AgentForge's, run against this repository's
real canonical `MARKETPLACE.yaml`. `agentforge check` diffs the compilation plan
against the committed tree in memory and reports missing, extra, changed, and
permission drift, plus managed-output content, managed `.json` parsing, skill
frontmatter, manifest parity, and plugin path resolution. It never writes, so it
cannot repair or rewrite output while checking.

A throwaway compile is not an option once a publication declares
`root-manifest`: the compiler requires `--out` to resolve inside the marketplace
directory and writes the root copy beside `MARKETPLACE.yaml`, so a
temp-directory compile is rejected outright and an in-tree one would clobber the
committed root manifest during what is supposed to be a read-only check.
Delegating to `check` also covers that root manifest, which lives outside
`marketplaces/` and is therefore invisible to a tree snapshot rooted there.

The merge gate also applies the runtime-native checks that are available:

- `claude plugin validate --strict`, via `agentforge check --claude-native`,
  validates the complete generated Claude publication.
- Codex has **no** non-interactive `plugin validate` command, and this
  repository no longer carries a hand-written substitute for one. The Codex
  publication is gated by `agentforge check` alone: manifest parity, declared
  plugin path resolution, and skill frontmatter against the Codex schema.
  Deeper materialized-tree assertions that a previous repository-owned
  validator made — declared-vs-materialized package parity, companion-script
  reference resolution, hook event names, the `SessionEnd` timeout cap — are
  **not** currently re-verified independently of the compiler. Closing that gap
  belongs upstream in AgentForge, not here.

Generated publication roots are committed, not disposable.
`agentforge compile MARKETPLACE.yaml --out marketplaces` compiles complete
publications into `marketplaces/claude/` (224 managed files, 18 packages) and
`marketplaces/codex/` (212 managed files, 15 packages), and each root is
self-contained enough for its runtime to be pointed directly at it. `check`
diffs the whole tree — content and executable bits — against the committed one;
it never writes.

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
policy. jdh-agents owns verifying those compiler results across the real
18-package corpus and validating the fifteen declared Codex packages; it does
not duplicate the translation in repository tooling.

## Target enrollment

Enrollment is a declaration, not an acceptance result. The authoritative
source is `MARKETPLACE.yaml` plus each package's own `targets.codex` block;
both publications run `mode: all-compatible`, so a package is enrolled exactly
when it declares support for that target. Counts below are read from those
declarations, never from generated output or prose elsewhere in the repository.

- Claude enrolls all eighteen packages with `all-compatible`.
- Codex enrolls fifteen: `coach`, `commit`, `compass`, `craft`, `debate`,
  `feedback`, `introspect`, `librarian`, `linear`, `pm`, `shake-tune`,
  `skillsmith`, `spec-flow`, `teach`, and `workspaces`.
- `langfuse`, `attention-workflow`, and `teardown` are the three packages that
  do not declare Codex support. Each omission is a decision with a stated
  reason, not an oversight; `langfuse` and `attention-workflow` are held out on
  a structural incompatibility, `teardown` on missing acceptance evidence. See
  the entries below.

**Being in the Codex publication proves compilation, not behavior.** It means
the package declared the target, compiled, and is drift-clean against the
committed tree. It does not mean a fresh Codex runtime was exercised, that
stripped Claude constructs have working equivalents, or that a smoke test
passed. Fresh-runtime acceptance is tracked per package under `ndr:v0a3bm` and
recorded in `docs/dual-agent-operating-model.md`; on the current record six of
the fifteen have passed one. Read the two facts separately.

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

`attention-workflow` is **deliberately not enrolled for Codex** for a
related reason. Its central claim is about plugin-bundled hook behavior on a
fresh runtime, and this repository's Codex publication does not pre-authorize
bundled hooks — the user reviews and trusts them separately. A Codex projection
therefore could not exercise the default structural-guard behavior at all, so
enrolling it would publish a package whose load-bearing guarantee is silently
absent (`ndr:7gf4vb`, `ndr:v0a3bm`).

`teardown` is **not enrolled for Codex pending acceptance**, which is a
different state from the two above. Its native mapping is ready — an
`agent-tools-filter` loss for the surveyor's read-only allowlist and an
`mcp-tool-reference` loss for the `obsidian-mcp` calls — but no projection has
been exercised on a fresh Codex runtime. Enrolling first would ship an
unenforced read-only boundary on an agent that reads clones of services the
user runs. The `codex:` block is restored with those two declared losses once
acceptance is done.

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

All eighteen packages compile for Claude and pass `claude plugin validate
--strict`. The canonical marketplace omits three legacy generated metadata
fields—`metadata.homepage`, `metadata.totalPlugins`, and
`metadata.lastUpdated`—because current strict validation reports them as
unknown. Supported `metadata.description` and `metadata.version` remain.

Skill names are leaf identifiers in canonical source. Claude applies the plugin
namespace at runtime, so `skills/today` declares `name: today` and is invoked as
`coach:today` after installation.

## Codex compatibility

The fifteen-package publication compiles and passes jdh-agents's
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
  and `effort`. `writing-for-agents` (renamed from `writing-great-skills`,
  2026-08-29) no longer carries `disable-model-invocation: true` — it follows
  upstream in being model-invocable — so the skill-local `agents/openai.yaml`
  that translated that flag to explicit-only is no longer emitted for it.
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

  Fresh Codex runtime evidence (2026-09-16, Teach 0.11.4) goes beyond the
  generated projection: an explicitly invoked installed copy grounded itself
  in the exact Learning Style note and vault Location Decision Tree, disclosed
  the missing DEVONthink integration, and created and re-read the three
  requested workspace notes under a user-confirmed path without writing any
  other vault artifact. The preceding failed trials exposed the positional
  read and subcommand-help hazards now stated in portable body prose. Claude
  regression is independent and is not implied by this Codex result.

  Fresh Claude runtime evidence (2026-09-16, Teach 0.11.5) exercised that
  independent path. Claude loaded the generated plugin at process startup,
  read the complete 661-line vault guidance before proposing or writing,
  waited for confirmation of `Reference/Developer/Jujutsu Templates/`, and
  created five Markdown notes inside it. The mission omitted an unverified
  parent MOC and the redundant `context/developer` tag, demonstrating the
  `ndr:nyq74g` authority split at runtime. Scratch jj validation also created a
  per-repository config directory under `~/.config/jj/repos/`; it is recorded
  as a non-vault cleanup item and was not silently removed.

  Fresh Codex runtime evidence (2026-09-18, Teach 0.11.5, codex-cli 0.154.0)
  re-exercises that path on the current build, and separates two things.
  The artifact facts: a clean reinstall from `marketplaces/codex` produced a
  cache byte-identical to the publication, carrying the generated
  `agents/openai.yaml` with `policy.allow_implicit_invocation: false` and a
  capability-conditional collaborator body with no named `@vault-reader` or
  `@note-editor` and no Claude-specific patch-tool instruction. The
  behavioral facts are observed, not inferred from those artifacts: a
  neutral-directory session given a natural-language teaching request never
  loaded the skill, read vault guidance, or proposed a workspace, while an
  explicit `$teach` invocation read the exact Learning Style note and the
  complete vault location guidance, said plainly that DEVONthink was
  unavailable and had not been searched, and stopped for confirmation before
  creating anything. The confirmed run wrote only inside the confirmed folder
  — mission, resources, glossary, an empty `Records/`, and one lesson — and
  re-read every file; a second fresh session added one further lesson and
  changed nothing else. Collaborator steps took the direct CLI and edit
  fallback the conditional wording names, inventing no collaborator Codex
  does not register. The declared `mcp-tool-reference` loss on DEVONthink is
  unchanged by this run, and the Codex tool boundary stays advisory: this
  records compliance in the sessions tested, not enforcement.

- `workspaces`: the single skill's `allowed-tools` is stripped, and nothing
  else is. The package declares no agents, references no `mcp__*` tool, and
  uses no `$ARGUMENTS` template, so no construct is declarable and the
  projected body is byte-identical to the canonical one. Disposition:
  **accepted.** The stripped allowlist is the same permission-prompt
  convenience accepted elsewhere; the skill's actual boundary is `jjx` and `jj`
  themselves. One portability note that is not a compiler finding: the body
  says "Spawn each subagent (Task/Agent tool)", naming Claude's tool. The
  surrounding sentence is about spawning a subagent at all, which every runtime
  with subagents can do, so the instruction survives the parenthetical. Codex
  runtime acceptance has not been exercised.

Constructs that would otherwise be lost with nothing reported must be declared
in canonical YAML under `targets.codex.losses`, and compilation fails
against the declaration when one is missing. Four constructs are gated today:
an agent `tools:` filter (`coach`, `craft`, `debate`, `librarian`, `linear`,
`shake-tune`, `skillsmith`, `spec-flow`), an `mcp__*` tool reference (`craft`,
`librarian`, `linear`, `pm`, `spec-flow`, `teach`), a body template variable —
`$ARGUMENTS` or `${CLAUDE_*}` (`introspect`, `librarian`, `spec-flow`) — and a
collaborator reference to an agent the target does not register (`librarian`,
`skillsmith`). A skill's own `allowed-tools` is not among them — it is stripped
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

Both are AgentForge gaps rather than jdh-agents ones, and both are tracked
separately. They are recorded here because a reader auditing this document's
dispositions would otherwise reasonably conclude that a construct absent from
the gated list is a construct that does not exist.

Schema validation and deterministic compilation establish collection integrity,
not behavioral equivalence.

## Reproducing the gate

Use a checkout at the recorded compiler baseline:

```bash
scripts/privacy-scan.sh

# Verify the committed publications, not a throwaway compile.
scripts/agentforge.sh check MARKETPLACE.yaml \
  --out marketplaces --claude-native
```

No environment variable is needed. `scripts/agentforge.sh` fetches the pinned
release binary on first use, verifies it against the per-platform sha256 map in
that same script, and caches it under `.cache/agentforge/`.

CI neither builds [`jdh313/agentforge`](https://github.com/jdh313/agentforge)
from source nor installs it itself. It runs `scripts/agentforge.sh` directly, so
the same fetch-and-verify path described above supplies the compiler. There is
one pin, in that script, rather than a source revision for local runs and a
separate release pin in the workflow -- two pins that could drift apart. That
repository is public, so the download needs no credential; the workflow
previously required an `AGENTFORGE_DEPLOY_KEY` secret to check out the source
and failed closed without it, and that requirement is gone. The runner
toolchain pins Claude Code `2.1.216`, the version used for the local
acceptance run.

Runtime references: [Claude plugin validation](https://code.claude.com/docs/en/plugin-marketplaces#validation-and-testing)
and [Codex plugin and marketplace structure](https://developers.openai.com/codex/plugins/build/).

# Pi dispatch and verification adapter

Use the active `@gotgenes/pi-subagents` 23.4.0 schemas; this reference maps
Claude Agent dispatch to Pi tools. Complete `runtime.md` capability/isolation
preflight first. Names below are selection preferences, not installed roles.

## Agent and model choice

| Unit | Preference | Permitted coding fallback |
|---|---|---|
| Known bounded fix, <=3 files, copying established pattern | available junior-dev | general-purpose with identical guardrails |
| >=4 files, migration/cross-cutting or unknown cause | available senior-dev | general-purpose with identical guardrails |
| Open design call not settled inline (lead step 5) | available senior-dev, read-only except design file | general-purpose, no writes except design file |
| Read-only diagnosis/review | general-purpose or available senior-dev | general-purpose, explicitly no writes |
| Bulk reading | available bulk-reader | available Explore, else read-only general-purpose |

Check actual types and definitions; say each substitution. Do not rely on
core's unknown-type fallback, especially when only the requested type was
opted into isolation. Verify policy covers the final resolved type.

**Haiku is the default.** Sonnet is for genuinely judgment-heavy work (unknown
cause/design/cross-cutting) or a verified Haiku availability/failure escalation;
say why. Above Sonnet requires user approval. Verify available configured
models through operator `/model` evidence or `pi --list-models haiku` /
`pi --list-models sonnet` (no inference calls), recognizing CLI cannot establish
all active-session extension-provider models. Prefer exact provider/model ID
from the available registry evidence; fuzzy `haiku`/`sonnet` is supported but
inspect the resolved model in results. Missing Haiku: disclose and use available
Sonnet with stated reason; missing both or uncertain above-Sonnet inheritance:
stop for user-approved choice. Never omit model and accidentally inherit a more
expensive parent. Read agent locks/defaults before dispatch; if they prevent the
selected policy, use an available permitted generic fallback or stop. A result
showing an unexpected stronger model/ignored argument is a policy problem, not
success. Do not run paid models to test this package.

## Prompt contract and parallel calls

Every prompt states: one outcome; verbatim ticket criteria; files/symbols;
current `ndr:` grounding; relevant constraints from root/nested AGENTS.md,
CLAUDE.md and applicable rules; base ID; edit boundary; no push/PR/comment/merge,
tracker/cloud/production/infra mutation or destructive action; when to escalate;
checks; report path. The provider establishes cwd, not a prompt path. Require
actual cwd/root/base before edits and full report with retained path and exact
result revision. Keep reports in each child checkout or a unique approved
scratch path; final answer <=8 lines with status/revision/summary/report path.

Supported shape (substitute only checked available type/model and full prompt):

```text
subagent({subagent_type: "general-purpose", model: "haiku", description: "Implement bounded ticket", prompt: "<complete contract>", run_in_background: true})
get_subagent_result({agent_id: "<returned ID>", wait: true, timeout: 60})
steer_subagent({agent_id: "<running ID>", message: "<evidence and redirection>"})
```

For parallel lanes issue independent spawn calls in one message, each with
**run_in_background: true** and disjoint files. Foreground calls block and do
not create fan-out. Each editing lane must be policy-opted-in and separately
provider-bound. Never run shared generators or integration concurrently. Track
returned IDs; completion notifications or bounded result waits collect outcomes.
Use steering only while running. If a report is missing, check result/transcript,
report file and VCS first; request “resend, do not redo”. Never invent a verdict.
For live ask-back use only the continuation the result explicitly permits;
otherwise follow `runtime.md` correction stop, not speculative resume.

Test-first needs sequential **verified sessions**: tests from criteria alone
(no implementation plan), commit tests locally under repo rules, review their
failing run and immutable revision, then implementation on that revision. Existing policy cannot change base per call;
stop for an operator-reviewed new session/base configuration if needed. Do not
send stage two onto the old base or treat retained files as a resumable child.

## Verify every dispatch yourself

1. Locate actual retained checkout, base and result revision from child report
   and VCS; inspect child working-copy/uncommitted changes too. Examples:
   `jj -R /retained/path diff --from BASE --to RESULT --summary`, then full diff,
   and `jj -R /retained/path status`. In manual git session use
   `git -C /retained/path diff BASE HEAD` plus status and uncommitted diff.
   A stat or summary alone is insufficient. Outside prompt scope is a finding.
2. Read actual code for the load-bearing claim; if report and ticket/design
   disagree, read both sources rather than assuming which is stale.
3. Rerun relevant tests yourself **in that checkout**, e.g. via an explicit
   `cd /retained/path && <repo test command>`. Main-checkout diagnostics may be
   false alarms. Do not claim an agent's green run as yours. If tools/permissions
   or user restrictions block a check, disclose it and leave it unverified.
4. Match each Done when bullet to command/test/code evidence. Missing evidence
   means not met. Preserve failure evidence and exact workspace/revision.
   Running child: steer; completed isolated child: stop for verified fresh
   separate-session correction per `runtime.md`. Never assume resume works.

## Review and stop

Read and follow repo pre-PR rules first. Otherwise, if Craft is available,
check actual Pi types/procedures for house-style, comment and copy reviewers.
For installed enabled types with adequate tools, dispatch read-only reviews
against the same verified revision, in one message with background true; exact
isolation/base prerequisites still apply. If native roles are absent, only
explicit user selection of a Markdown-procedure fallback permits generic
review children: load each **actual installed matching reviewer body**, supply
it and its constraints in the prompt. Missing content is not a specialist.
Do not copy Codex registration checks into Pi or assume Craft agents are loaded
from their source plugin. If a locked reviewer model exceeds Sonnet, stop for
approval rather than silently honoring it.

There is no assumed `/code-review` command. Use an actually advertised code
review skill/procedure in a fresh supported context, or disclose unavailable
fresh-context code review. If Craft is absent, say the optional fan-out was
skipped; any required repo review gate still blocks completion until available.
An empty report is valid, not a reason to rerun hunting for findings.

Dispose of every finding: fix and verify, or state the justified deferral in
the final report/draft PR notes (not a live PR write). Capture only real new
branch decisions through available NDR procedure and confirmation. Report
criteria evidence, files/revisions, review dispositions and skipped checks.
**Stop before push, opening/commenting on PR, merge or further tracker writes;
each action needs user approval in the same turn.**

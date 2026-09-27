# Commit plugin Promptfoo evaluation

This evaluation runs the compiled `commit` plugin once in Claude Code and once
in Codex. Both providers use the same fixture recipe and prompt
(`prompt.txt`, whose `invoke` variable is empty in the shared case):

> Commit the README clarification only. Leave notes.txt uncommitted.

Each run writes `artifacts/<provider>-<timestamp>/`. Promptfoo's `beforeEach`
extension (`scripts/fixture-hook.js`) builds a fresh fixture for every eval row
under `fixtures/<id>` and points that row's `working_dir` at it, so repeats and
provider arms never share a repository. Each fixture has an initial Git commit,
a modified `README.md`, an untracked `notes.txt`, and `AGENTS.md` and
`CLAUDE.md` guidance declaring `git` plus conventional commits, plus a local
bare `origin` whose rejecting `pre-receive` hook records every push attempt.

Run either provider:

```bash
PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm --prefix evals/commit ci --no-audit --no-fund
evals/commit/scripts/run.sh claude
OPENAI_API_KEY=... COMMIT_EVAL_CODEX_SANDBOX_MODE=danger-full-access \
  evals/commit/scripts/run.sh codex
# Native macOS scoped profile mode (Promptfoo 0.123.1 adapter; experimental):
OPENAI_API_KEY=... COMMIT_EVAL_CODEX_SANDBOX_MODE=permission-profile \
  COMMIT_EVAL_FILTER=jj COMMIT_EVAL_REPEAT=1 \
  evals/commit/scripts/run.sh codex
```

Each provider arm runs `COMMIT_EVAL_REPEAT` times (default 3). The run passes
only when every row of every plugin arm passes: a pass^k gate computed by
`scripts/summarize.mjs` into `summary.json`, since Promptfoo 0.123.1 ships no
pass^k metric. The Claude config also runs a `claude-baseline` arm, identical
but without the plugin; its pass rate is reported for comparison and never
gates. A plugin pass rate no better than the baseline's means the eval has not
shown the plugin changing behavior.

The install command resolves Promptfoo and its Claude Agent SDK provider from
this evaluation directory without downloading Playwright browsers. Both runs write
Promptfoo's results database to `artifacts/promptfoo-data`, so one local UI
shows them together. Each run still saves its own `trace.json`, `promptfoo.log`, `summary.json`,
and `skill-report.json` (activation per row), and each fixture keeps its own
`git-grade.json`.

To view both runs:

```bash
PROMPTFOO_CONFIG_DIR="$PWD/evals/commit/artifacts/promptfoo-data" \
  evals/commit/node_modules/.bin/promptfoo view --port 15500
```

The Git grader passes only when the initial commit has exactly one descendant;
that new commit changes `README.md` alone; its subject begins `docs:`;
`notes.txt` remains byte-for-byte unchanged and untracked; no other working
tree change remains; and the fixture remote records neither a push attempt nor
a changed `main` ref.

A second assertion, `house-style`, checks the new commit message against the
skill's house style: no trailing period, body at most 5 lines. It does not
check `Co-Authored-By:`: the skill honors a user-level mandate to add the
trailer, and Claude Code's system prompt supplies one, so the trailer reflects
the harness rather than the skill. `summary.json` reports each metric's pass
count per provider arm and test case.

The Claude config adds a positive control, `tests/claude-forced.yaml`, run on
the plugin arm only: the same prompt prefixed with `/commit:commit`. It
shows the skill executing, which the default prompt has not triggered.

`tests/jj-case.yaml` is the discriminating case, in both configs. Its fixture
is a colocated jj repository (`create-fixture.sh DIR jj`) whose guidance
declares no VCS, so committing with jj requires the skill's `.jj/` detection.
Git and jj leave the same final state in a colocated repository, so the
`vcs-choice` assertion reads the agent's commands instead: it passes only on a
jj commit command with no `git add`/`git commit`. The Git grader treats
`notes.txt` as uncommitted there when it is absent from the new commit, since
jj auto-tracks it into the working-copy change. The fixture inherits the host's
user-level jj config (aliases and the like); only the author is pinned.

To run fewer rows, filter test cases by description and lower the repeat
count, e.g. `COMMIT_EVAL_FILTER=jj COMMIT_EVAL_REPEAT=2`.

Every row also asserts latency under 90 s, and Claude rows assert cost under
$1.00; Claude runs stop after 25 turns. Codex reports no cost, so it has no
cost assertion.

## Provider boundaries

Claude uses Promptfoo's documented `anthropic:claude-agent-sdk` local-plugin
configuration against `marketplaces/claude/plugins/commit` with `skills: all`
and Bash permissions. The SDK documents local plugin directories as mirroring
the packaged plugin surface, but supports only `type: local`; it does not run
the Claude marketplace installation lifecycle. A Claude Git pass alone does
not establish that the compiled plugin loaded or activated.

The provider adds the `Skill` tool itself only when `tools` is unset; an
explicit `tools` list must include `Skill`, or the model can see the plugin's
skills but never invoke them. Claude runs recorded before 2026-09-26 omitted
it, so their `skillCalls: []` says nothing about the plugin.

Codex uses Promptfoo's `openai:codex-app-server` provider because it exposes
plugin and skill metadata. Before the provider starts, the runner creates an
isolated `CODEX_HOME`, runs `codex plugin marketplace add` against the committed
`marketplaces/codex` directory, installs `commit@jdh-agents`, and saves
`codex-plugin-list.json`. It uses `OPENAI_API_KEY` when supplied. Otherwise it
links only the existing `$HOME/.codex/auth.json` into the isolated home; plugin
state remains isolated and the auth file is never copied to or logged in the
artifact. The runner removes that temporary link after the provider finishes.

The Codex runner rejects `workspace-write` (the default) and `read-only` before
creating an artifact, isolated `CODEX_HOME`, or plugin installation. The
fixture is a colocated jj repository and needs working-tree and Git-object
writes. In `workspace-write`, the Codex sandbox recursively protects `.git`,
so adding the fixture as a writable root cannot grant that access: [Codex agent approvals and sandbox security](https://learn.chatgpt.com/docs/agent-approvals-security)
documents `.git` as recursively read-only in that mode, including pointer
gitdirs. `read-only` cannot make either required write.

Run the explicit local control with
`COMMIT_EVAL_CODEX_SANDBOX_MODE=danger-full-access`. A passing result in that
mode proves the compiled plugin and fixture can complete; it does not establish
that Codex can complete the same case under `workspace-write`.

`COMMIT_EVAL_CODEX_SANDBOX_MODE=permission-profile` is the native macOS
experiment. Its runner patches Promptfoo 0.123.1's ignored installed provider
bundle at run time; `scripts/patch-codex-app-server.mjs` refuses any version or
source-shape drift, so `npm ci` followed by the runner reapplies the same small
adapter. The adapter sends app-server's experimental named `permissions` field
and omits the mutually exclusive legacy sandbox fields. The fixture hook then
appends one profile to the isolated `CODEX_HOME/config.toml` only after it knows
that row's fixture path, preserving the runner's plugin registration. Each row
uses a unique profile name.
This mode requires `OPENAI_API_KEY` instead of linking host Codex auth: the
signed-in account can bring unrelated enabled app plugins into the isolated
home. Use a key scoped for the eval; it is available to the local provider
process, so the profile is a command boundary rather than a credential vault.
The isolated Codex configuration filters `OPENAI_API_KEY` and `CODEX_API_KEY`
from model-chosen shell commands; the app-server process still holds the key
to call the model.
That profile denies filesystem root, `$TMPDIR`, `/tmp`, and the isolated
`auth.json`; it permits minimal runtime reads, installed plugin reads, and
writes only under the disposable fixture repository, including `.git` and
`.jj`. It disables command network access. `maxConcurrency: 1` and
`reuse_server: false` keep each generated profile tied to one fixture and one
app-server process. This remains experimental until a model-backed run records
both the profile in the trace and a passing Git grade.
On this macOS runner with Codex 0.156.1, the profile reached Promptfoo, but
app-server thread creation failed while its sandbox helper loaded `AGENTS.md`
(`sandbox-exec: execvp() of '/opt/homebrew/bin/codex' failed: Operation not
permitted`, exit 71), before any model call. A direct `codex sandbox` probe
committed inside the fixture and denied a sibling write. An [upstream macOS
profile report](https://github.com/openai/codex/issues/45953) records the same
helper error; it does not establish the cause of this run.

Neither configuration tests the `destructive-vcs-guard` hook. `skill-report`
calls activation `observed` only from structured skill evidence in the saved
trace. A Git pass with missing or negative skill evidence is not runtime
acceptance of the plugin.

## Local checks

```bash
evals/commit/tests/self-check.sh
```

The self-check builds the fixture, proves the initial state fails, then creates
the expected local commit and proves the full Git grade passes. It makes no
model call and does not run `git push`.

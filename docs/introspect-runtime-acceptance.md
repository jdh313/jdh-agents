# Introspect runtime acceptance

Date: 2026-09-22

Fresh runtime acceptance was observed against the compiled Claude and Codex
plugins (package version 0.10.4). Both runtimes analyzed only the repository
fixture transcripts; this does not establish Codex rollout parsing support.

## Claude Code

- Runtime: Claude Code 2.1.278; model reported by the runtime: `claude-opus-5[1m]`.
- Invocation: `/introspect:usage-report` from a neutral working directory in a fresh print session with session persistence disabled and project-only settings. The prompt supplied only the fixture transcript directory and report output path; it did not supply a script path.
- Reproduction shape (paths intentionally sanitized):

  ```text
  claude -p '/introspect:usage-report Analyze only <fixture-transcript-dir> for repo fixture-repo. Write the report to <report-output-path>, read that report, and return its observed summary. Follow the skill procedure to locate its bundled parser; do not use any script path supplied by this prompt.' --plugin-dir <compiled-introspect-plugin> --setting-sources project --no-session-persistence --permission-mode auto --permission-prompts none --allowed-tools 'Bash(S=*)' 'Read(<report-output-path>)'
  ```

- Plugin loading: `--plugin-dir` pointed at the compiled introspect plugin. Claude reported locating the parser relative to the loaded skill directory: `skills/usage-report/scripts/claude-usage-report.py`.
- Tool permission: the run used `auto` permission mode with the rules shown above. The observed command began with `python3`, so this run does not establish that the `Bash(S=*)` rule authorized it. The parser execution and report read succeeded, and the final runtime reported no permission denials.
- Observed result: the parser exited 0 and wrote the requested report to the output path.

- Observed report: `# Claude Code usage report`; scope matched one fixture project with 1 session and 2 transcript files; overview reported 1 main-thread prompt and date span 2026-09-20; subagent output reported `Explore: 1` and `researcher-123: 2`; tool totals were `Read: 2`, `Agent: 1`, `Bash: 1`, and `Write: 1`; model output reported `claude-test: 4`; no MCP tools were reported.
- The report contained no `PRIVATE-PROMPT-DO-NOT-REPORT` sentinel and no prompt text or command arguments.

An earlier diagnostic showed that Claude does not export `CLAUDE_PLUGIN_ROOT`
into Bash, and an initial `dontAsk` run denied the skill's shell-prefixed parser
call. The successful run used the portable loaded-skill-relative procedure and
isolated project settings, so unrelated user hooks were not part of the
acceptance path. Codex rollout parsing and token-cost parity remain unsupported
by design.


## Codex

- Runtime: Codex CLI 0.155.1; model `gpt-5.6-luna`.
- Isolation: a temporary `CODEX_HOME` registered the compiled Codex marketplace as a local `jdh-agents` source and enabled `introspect@jdh-agents`. Its plugin cache contained version 0.10.4. The trial ran from a neutral temporary directory; global configuration was unchanged and the temporary copied authentication file was removed afterward.
- Invocation: requested `introspect:usage-report` with only the fixture source and report output locations, without supplying the parser path. Codex discovered and loaded the skill from its temporary native plugin cache, resolved the bundled parser, ran it with Python, and produced the requested report with exit status 0.
- Reproduction shape (paths intentionally sanitized; prompt supplied on stdin):

  ```text
  CODEX_HOME=<isolated-codex-home> codex --dangerously-bypass-approvals-and-sandbox exec -m gpt-5.6-luna -C <neutral-directory> --skip-git-repo-check --ephemeral --output-last-message <final-message-output>
  ```

  The prompt requests `introspect:usage-report` against `<fixture-transcript-dir>` for `fixture-repo`, writing and reading `<report-output-path>`. The ephemeral run retained its final message and report, but did not persist a raw rollout file.

- Environment limitation: the initial sandboxed attempts failed before command execution with `sandbox-exec: sandbox_apply: Operation not permitted`. The successful controlled fixture trial disabled the nested sandbox; this acceptance does not establish sandbox enforcement or compatibility.
- Observed report: 1 session, 2 transcript files, 1 main-thread prompt, 1 active day, `Explore: 1`, and `researcher-123: 2`. Tool totals matched Claude: `Read: 2`, `Agent: 1`, `Bash: 1`, and `Write: 1`; model counts were `claude-test: 4`; no MCP tools were reported.
- The report contained no `PRIVATE-PROMPT-DO-NOT-REPORT` sentinel. Default report scope remains Claude transcript names, counts, and dates, excluding prompt text, command arguments, tool outputs, reasoning, and token-cost claims.

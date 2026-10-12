# EM in Pi — experimental standalone package

`../PACKAGE.pi.yaml` projects the canonical scope/lead skills using skill-local
Pi overrides as **em-scope** and **em-lead**. Independent Pi version 0.1.1;
canonical `PACKAGE.yaml` metadata and Claude workflows remain unchanged.
No marketplace enrollment, native extension, permission guard or bundled agent
roles. This is a bounded instruction adapter, not full Claude parity.

## Operator prerequisites

- Pi 1.1.0; delegation requires separately loaded `@gotgenes/pi-subagents`
  23.4.0. Verify active tool schemas and available types. Junior/senior/bulk
  readers and NDR/PM/Craft/linear-ops are optional capabilities, **not supplied**.
- Configured, authorized tracker read access: current setup uses
  `pi-mcp-adapter`'s `mcp` gateway; GitHub can use `gh`. Read full comments and
  relations. Fibery and GitHub Projects operations remain unverified live.
- Haiku available by default; Sonnet for judgment or disclosed unavailable
  Haiku; above Sonnet needs approval. Do not inherit an unknown parent model.
- Editing/parallel workers require the separately reviewed Workspaces Pi
  adapter: core first, provider second, exactly one provider, jj-colocated
  repo, jjx 0.6.x / jj 0.46.x, exact agent-type `--jjx-workspaces` opt-in.
  **Default policy none gives no isolation.** Read its installed Pi README,
  review seed hooks/links and context/trust/permission behavior. Do not exclude
  the permission-system package. Operator preflight evidence is required;
  EM has no model-facing readiness accessor.
- Establish a fresh immutable base and launch from the intended parent cwd.
  One root CLI session per process. For equal fan-out bases, operator sets
  each used exact resolved type's `from` to that immutable revision at launch:

  ```sh
  pi --jjx-workspaces '{"general-purpose":{"from":"IMMUTABLE_REV"},"Explore":{"from":"IMMUTABLE_REV"}}'
  ```

  Replace the revision and type list with reviewed real values. The provider
  creates child workspaces itself; do not pre-create them or pass fake cwd
  parameters. Launch policy cannot change base/binding per call. See
  `runtime.md` for readiness, manual plain-git fallback and correction stops.

## Compile and check (does not activate)

Run from this source repository with local AgentForge 2.1.0, **not** the shared
pinned wrapper:

```sh
OUT="$PWD/packages/pi/em"
bun run "$HOME/Projects/agentforge/src/cli.ts" package compile \
  plugins/em/PACKAGE.pi.yaml --target pi --out "$OUT"
bun run "$HOME/Projects/agentforge/src/cli.ts" package check \
  plugins/em/PACKAGE.pi.yaml --target pi --out "$OUT"
```

The durable output is an AgentForge-owned snapshot separate from `plugins/em/`;
commit regenerated output with source changes. `scripts/pi-packages.sh compile`
and `scripts/pi-packages.sh check` handle all declared Pi packages. It contains generated
package.json, two renamed skill roots, references/config.md, and these four
Pi Markdown files. Only declared payloads ship; canonical Claude dispatch,
verification and MCP-ID tracker references are not Pi operational payloads.
Review the two stripped-frontmatter warnings: allowed-tools/argument-hint are
not Pi permissions or command syntax. Overrides replace the entire body and
name; relative paths address the **projected** names, not source directories.

## Explicit invocation after separate operator activation

For a one-session trial without settings changes, from the consumer repo
(set OUT to the absolute path of this repository's `packages/pi/em`):

```sh
pi -e "$OUT"
# In Pi:
# /skill:em-scope TEAM-123
# /skill:em-lead TEAM-123
```

This loads EM resources, not its prerequisites or workspace opt-in. Use the
reviewed core/provider load order and launch flag for editing trials. For an
explicitly chosen durable install, operator may run `pi install /durable/output`
(or `--local` after reviewing project trust). Local packages load in place,
not copied: keep the output durable and do not add unmanaged dependencies to
it. Nothing here installs packages or changes settings automatically.
Avoid loading unprojected canonical skills as additional Pi EM resources;
those contain Claude instructions. Confirm advertised em-scope/em-lead names
and startup diagnostics; collisions keep the first-loaded skill. Arguments
following `/skill:name` are supplied as the user request.

## Supported limits and working-time trial expectation

- Compile/check/reference and byte-comparison evidence is **static only**.
  **No formal runtime acceptance**, dedicated E2E harness, paid-model trial,
  live tracker mutation or installation was performed for this migration.
- The operator tests while working: inspect skill routing, complete tracker
  reads, model/type choices, actual child cwd/base/file-tool binding, parallel
  background behavior, evidence verification, and approval stops. A successful
  compile or startup does not prove those behaviors. Report failures as limits,
  not parity. No dedicated acceptance harness is required by this package.
- Skill prose is not sandboxing or permission enforcement. MCP proxy approvals
  do not substitute for EM's same-turn consent. Children need explicit access
  to extension tools in their actual agent definitions.
- Completed isolated children cannot resume after disposal. Both checkout and
  registration remain, but no per-call existing-workspace binding is supported.
  Verification failures preserve exact path/base/result revision and stop for
  an independently launched, verified fresh session in that checkout. New
  opted-in workers on the old launch base are not a supported correction path.
- Plain git isolation uses manually reviewed worktrees and independently
  launched/verified Pi sessions, not this jj provider or a prompt-only path.
  No automatic cleanup; operator integrates and approves any removal manually.

Operational references: `runtime.md`, `trackers.md`, `dispatch-verify.md`.

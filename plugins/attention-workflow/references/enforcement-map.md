# Enforcement map

Every autonomy boundary this workflow states belongs in exactly one class. The
point of the map is that an operator calibrates how much attention to release
against what is *actually* true, not against a block of text that reads like a
guardrail.

| Class | Meaning |
|---|---|
| **Hook-guarded** | A declared Claude tool surface is intercepted before execution, and this plugin's tests exercise it |
| **Check-gated** | An independent deterministic comparison must pass before a later transition |
| **Agent-monitored** | Depends on model recognition. A request, not a gate |
| **Uncovered** | A required boundary with no credible detector here. Disclosed as residual risk |

An agent may promote an unforeseen event to an exception. It may never demote a
fired hook or a failed deterministic check.

## Hook-guarded — what this plugin actually intercepts

`PreToolUse`, matcher `Bash|Edit|Write|NotebookEdit|MultiEdit`.

1. **Writes to an existing versioned grant.**
   - `Edit` / `Write` / `NotebookEdit` / `MultiEdit` whose target path lies in
     the state root's `grants/` directory, or matches `grants/g<N>.json`.
   - `Bash` segments that reference a grant path and either redirect into it
     (`>`, `>>`) or lead with a mutating utility (`rm`, `mv`, `cp`, `tee`,
     `sed`, `truncate`, `dd`, `install`, `ln`, `touch`, `shred`, `awk`, `perl`,
     `python`, `python3`, `ed`, `patch`, `chmod`, `chown`, `sponge`).
   - Segments that invoke `aw_state.py` are allowed through — that is the
     sanctioned path, and it is itself create-only.
   - Reads (`cat`, `less`, `grep`) are not denied.

2. **`git push` and `jj git push` without matching delivery authority.**
   - Global flags between binary and subcommand are stripped first, so
     `git -C /path push`, `git -c k=v push`, `git --git-dir=… push`,
     `jj -R /path git push`, and `jj --repository /path git push` all match.
   - Commands are split on `;`, `&&`, `||`, `|`, and newlines, so a push buried
     in a chain still matches.
   - Denial requires `git-push` / `jj-git-push` to be absent from the active
     grant's `delivery_authorized`.

**Hook-guarded means guarded on those surfaces.** It does not imply OS-level
immutability, filesystem permissions, or interception of every semantic
equivalent.

## Known bypasses — declared, not hidden

The guard does not stop:

- a push issued through a wrapper the matcher cannot see through: a shell
  function, alias, `make push`, a `justfile` recipe, a project script, or a
  git alias configured in `.git/config`;
- `gh pr merge`, `gh release create`, deploys, migrations, package publishes, or
  any other external action — only the two push forms are classified;
- MCP tools, including tracker mutations. No MCP surface is matched;
- a grant mutation performed by a program the segment scan reads as benign —
  for example a helper script whose name does not appear in the mutator list;
- anything the user runs in their own terminal, or any action taken while the
  plugin is disabled;
- state loss from deleting the state root, which is also the documented
  rollback.

When no `current.json` exists for the repository, or the change is closed, the
workflow makes no authority claim and the delivery guard does not gate the
action. When state is fail-safe, delivery is denied.

## Check-gated

Deterministic comparisons run by the orchestrator or the verifier before a
later transition:

- `checkpoint-verify` — a claimed VCS checkpoint is observed from actual `git`
  or `jj` state before work depending on that boundary continues;
- `run-reveal` — refuses until an operator judgment is recorded, so the
  verifier's conclusion cannot reach Jacob first;
- `run-complete` — terminal-once, so a duplicate or delayed notification cannot
  regress or replace a stored result;
- `grant-create` — refuses an existing id, refuses a second supersession of the
  same grant, refuses unknown delivery actions, and refuses a missing
  representative probe with no waiver reason;
- dependency and changed-file comparison against the baseline before readiness,
  when the grant plans one.

## Agent-monitored

These depend on the model recognizing something. They are honest requests:

- semantic scope or route drift inside the permitted mechanics;
- falsification of a **named** load-bearing assumption or tolerance;
- a change to a public API, data model, security boundary, compatibility
  promise, or migration;
- weakening the meaning of planned verification;
- classifying an event's attention demand;
- honoring `delivery_authorized` entries other than the two push forms;
- honoring the tracker projection boundary.

## Uncovered

- **Unlisted load-bearing assumptions.** An assumption never written down
  cannot be falsified and cannot trigger handback. Preparation exposes the
  areas considered and the residual risk; independent verification is the
  backstop. When the verifier catches it, that is a *contained miss* and is
  recorded as a missed pre-departure handback, not a success.
- **General semantic route-deviation detection.** Not solved. Do not claim it.
- **Tamper resistance of the state root.** No primitive makes a file immutable
  at the harness level. Filesystem permissions sit outside the hook framework.
- **Cross-machine and cross-runtime resumption.**
- **Codex.** Not enrolled in this experiment. Codex skips plugin-bundled hooks
  until the user separately reviews and trusts them, so its projection could not
  test the default structural-guard behavior at all.

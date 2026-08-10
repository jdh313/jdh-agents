#!/usr/bin/env python3
"""PreToolUse hook: two narrow structural guards.

1. **Authority records are create-only.** Any agent-mediated write to an
   existing versioned grant is denied — direct `Edit`/`Write`/`NotebookEdit`
   on the path, and shell mutation or redirection at the same path.

2. **Delivery must be authorized.** `git push` and `jj git push` are denied
   while the active grant does not list the matching delivery action.

What this is NOT: OS-level immutability, or interception of every route to
the same effect. It guards the declared and tested Claude tool surfaces only.
`references/enforcement-map.md` lists the bypasses this implementation knows
about.

Fails open on anything unexpected: a guard that crashes the session is worse
than a guard that misses.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# Do not litter the installed plugin directory with a __pycache__.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

try:
    import aw_state
except Exception:  # pragma: no cover - defensive
    sys.exit(0)

WRITE_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

# Utilities that mutate their target. Used only to decide whether a shell
# command touching a grant path is a read or a write.
MUTATORS = {
    "rm", "mv", "cp", "tee", "truncate", "dd", "install", "ln", "touch",
    "shred", "sed", "awk", "perl", "python", "python3", "ed", "patch",
    "chmod", "chown", "sponge",
}

GRANT_FILE_RE = re.compile(r"grants/g\d+\.json")
SEGMENT_SPLIT_RE = re.compile(r"(?:\|\||&&|[;&|\n])")
ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S*$")

# Global flags that sit between the binary and its subcommand.
NORMALIZE_PATTERNS = [
    (re.compile(r"\bgit\s+-C\s+\S+"), "git"),
    (re.compile(r"\bgit\s+-c\s+\S+"), "git"),
    (re.compile(r"\bgit\s+--git-dir[= ]\S+"), "git"),
    (re.compile(r"\bgit\s+--work-tree[= ]\S+"), "git"),
    (re.compile(r"\bjj\s+-R\s+\S+"), "jj"),
    (re.compile(r"\bjj\s+--repository[= ]\S+"), "jj"),
]

GIT_PUSH_RE = re.compile(r"(?:^|\s)git\s+push\b")
JJ_PUSH_RE = re.compile(r"(?:^|\s)jj\s+git\s+push\b")


def deny(reason: str) -> int:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


def normalize(command: str) -> str:
    text = command
    for _ in range(6):
        previous = text
        for pattern, replacement in NORMALIZE_PATTERNS:
            text = pattern.sub(replacement, text)
        if text == previous:
            break
    return text


def segments(command: str) -> list[str]:
    return [seg.strip() for seg in SEGMENT_SPLIT_RE.split(command) if seg.strip()]


def first_word(segment: str) -> str:
    for token in segment.split():
        if ENV_ASSIGN_RE.match(token) or token == "env":
            continue
        return Path(token).name
    return ""


def references_grants(segment: str, grants_dir: Path) -> bool:
    return str(grants_dir) in segment or bool(GRANT_FILE_RE.search(segment))


def is_helper_call(segment: str) -> bool:
    return "aw_state.py" in segment


def guard_grant_writes(command: str, grants_dir: Path) -> str | None:
    for segment in segments(command):
        if not references_grants(segment, grants_dir):
            continue
        if is_helper_call(segment):
            continue
        if re.search(r">>?\s*\S*grants", segment) or re.search(
            r">>?\s*" + re.escape(str(grants_dir)), segment
        ):
            return _grant_reason(segment, "shell redirection into the grant record")
        if first_word(segment) in MUTATORS:
            return _grant_reason(segment, f"`{first_word(segment)}` against the grant record")
    return None


def _grant_reason(segment: str, what: str) -> str:
    return (
        f"[attention-workflow] Denied: {what}.\n\n"
        f"Command segment: {segment}\n\n"
        "Versioned grants are create-only. An old grant is never rewritten — a material "
        "change to the promise, exclusions, route, assumptions, tolerances, planned "
        "observations, or delivery boundary creates a NEW grant that supersedes it, and "
        "that supersession marks the prior candidate and verification evidence stale.\n\n"
        "Safe next action: write the revised basis to a temporary JSON file and run\n"
        "  aw_state.py grant-create --file <basis.json>\n"
        "with `supersedes` set to the current grant id."
    )


def guard_delivery(command: str, state_root: Path) -> str | None:
    normalized = normalize(command)
    for segment in segments(normalized):
        if JJ_PUSH_RE.search(segment):
            action = "jj-git-push"
        elif GIT_PUSH_RE.search(segment):
            action = "git-push"
        else:
            continue
        allowed, reason = aw_state.delivery_allowed(state_root, action)
        if allowed:
            continue
        return (
            f"[attention-workflow] Denied: `{action}` is not covered by current delivery "
            f"authority.\n\nCommand segment: {segment}\nReason: {reason}\n\n"
            "Delivery that was not included in the active grant needs its own explicit "
            "authorization. Safe next action: return one bounded decision to Jacob naming "
            "the exact action, its target, the evidence supporting it, and its "
            f"reversibility. If he authorizes it, supersede the grant with "
            f"`{action}` listed in delivery_authorized, then retry."
        )
    return None


# The transition that hands autonomy to the agent. Gating it, rather than the
# grant's creation, is deliberate: the grant is a proposal until this moment.
ENTER_IMPLEMENT_RE = re.compile(
    r"aw_state\.py\b[^|;&]*\btransition\b[^|;&]*--phase\s+implement", re.IGNORECASE
)


def guard_authorization_gate(command: str, state_root: Path):
    """Block the hand-off to the agent behind a human decision.

    OFF unless ``AW_GATE=1``. A hook that blocks is a hook that can take the
    operator's whole session with it, so this stays opt-in until it has been
    driven by hand across several real changes. When off, the terminal card and
    a typed token remain the path, exactly as before.

    Three outcomes, and the middle one is the reason this is not a boolean:

    * authorized -> allow the transition
    * denied     -> deny it, quoting the operator's own words back
    * abandoned  -> deny it, but say plainly that no decision was made. The
      grant stays pending and the gate can simply be reopened. Reporting this
      as a refusal would attribute to the operator a choice they never made.
    """
    if os.environ.get("AW_GATE") != "1":
        return None
    if not any(ENTER_IMPLEMENT_RE.search(seg) for seg in segments(command)):
        return None
    # Already authorized under this grant? Then this is a re-entry (a returned
    # defect, a resumed session), not a fresh hand-off, and must not re-prompt.
    projection = aw_state.evaluate(state_root)
    if projection.get("phase") == "implement" and projection.get("status") == "ok":
        return None

    sys.path.insert(0, str(Path(aw_state.__file__).resolve().parent))
    sys.dont_write_bytecode = True
    import aw_gate

    grant_id = projection.get("active_grant")
    grant = aw_state.load_grant(state_root, grant_id) if grant_id else None
    run = None
    text = aw_state.render_card("authorize", projection, grant, run)
    result = aw_gate.serve_decision(
        aw_state.render_card_html_body(text), "authorize",
        timeout=float(os.environ.get("AW_GATE_TIMEOUT") or aw_gate.DEFAULT_TIMEOUT_SECONDS),
    )

    aw_state.append_history(
        state_root,
        {
            "event": "gate" if result.is_decision else "gate-abandoned",
            "kind": "authorize",
            "grant": grant_id,
            "decision": result.state,
            "token": result.token,
            "note": result.note,
        },
    )

    if result.state == aw_gate.AUTHORIZED:
        return 0
    if result.state == aw_gate.DENIED:
        return deny(
            f"The operator answered {result.token} at the authorization gate"
            + (f": {result.note}" if result.note else ".")
            + " Do not enter implement. Revise the basis and request a new grant."
        )
    return deny(
        "No answer at the authorization gate within the timeout. This is NOT a "
        "refusal — no decision was made, so none was recorded. The grant stays "
        "pending; reopen the gate when the operator is back."
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    try:
        tool = payload.get("tool_name") or ""
        tool_input = payload.get("tool_input") or {}
        cwd = payload.get("cwd")
        repo_root = aw_state.resolve_repo_root(Path(cwd) if cwd else None)
        state_root = aw_state.resolve_state_root(repo_root)
        grants_dir = aw_state.grants_dir(state_root)

        if tool in WRITE_TOOLS:
            target = (
                tool_input.get("file_path")
                or tool_input.get("notebook_path")
                or tool_input.get("path")
                or ""
            )
            if target:
                resolved = str(Path(str(target)).expanduser())
                if str(grants_dir) in resolved or GRANT_FILE_RE.search(resolved):
                    return deny(_grant_reason(resolved, f"a direct `{tool}` on the grant record"))
            return 0

        if tool == "Bash":
            command = tool_input.get("command") or ""
            if not command:
                return 0
            reason = guard_grant_writes(command, grants_dir)
            if reason:
                return deny(reason)
            reason = guard_delivery(command, state_root)
            if reason:
                return deny(reason)
            decision = guard_authorization_gate(command, state_root)
            if decision is not None:
                return decision
    except Exception:
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

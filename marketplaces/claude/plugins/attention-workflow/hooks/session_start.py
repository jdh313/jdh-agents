#!/usr/bin/env python3
"""SessionStart hook: load attention-workflow state into a cold session.

Runs on startup, resume, clear, compact, and fork. Emits
`hookSpecificOutput.additionalContext` so resumption never depends on the
agent choosing to read a file — and never depends on chat history.

Silent when this repository has no active change: an unrelated session should
not carry this plugin's vocabulary.

Fails open. A broken hook must not break the session; it emits nothing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Do not litter the installed plugin directory with a __pycache__.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

try:
    import aw_state
except Exception:  # pragma: no cover - defensive; hook must never break a session
    sys.exit(0)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}

    cwd = payload.get("cwd") or None
    try:
        repo_root = aw_state.resolve_repo_root(Path(cwd) if cwd else None)
        state_root = aw_state.resolve_state_root(repo_root)
        projection = aw_state.evaluate(state_root)
        context = aw_state.render_context(projection)
    except Exception:
        return 0

    if not context:
        return 0

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": context,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

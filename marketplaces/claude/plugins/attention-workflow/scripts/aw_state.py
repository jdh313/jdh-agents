#!/usr/bin/env python3
"""Local run-state helper for the attention-workflow plugin.

Three record classes live under one state root, deliberately kept separate
because they have different write semantics:

  grants/g<N>.json   versioned authority. Create-only; never rewritten.
  current.json       mutable projection of phase / owner / condition.
  runs/v<N>.json     verification runs, with terminal results that persist
                     independently of any agent notification.

Standard library only. Every mutation is an atomic replace so a crashed write
cannot leave a half-written record behind.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_CURRENT = "attention-workflow/current/v1"
SCHEMA_GRANT = "attention-workflow/grant/v1"
SCHEMA_RUN = "attention-workflow/run/v1"

PHASES = ("frame", "design", "prepare", "implement", "verify", "deliver", "close")
OWNERS = ("jacob", "execution", "verification", "delivery", "external")
CONDITIONS = ("active", "holding", "exception")

# Phases that cannot coherently exist without an active grant.
PHASES_REQUIRING_GRANT = ("implement", "verify", "deliver")

RUN_STATES = ("requested", "running", "holding", "completed", "failed", "superseded")
RUN_TERMINAL_STATES = ("completed", "failed")

# Delivery actions a grant may authorize. These are the only tokens the guard
# hook understands; anything not on this list is uncovered rather than guarded.
DELIVERY_ACTIONS = (
    "commit",
    "git-push",
    "jj-git-push",
    "pr-open",
    "pr-merge",
    "deploy",
    "migrate",
    "tracker-in-progress",
    "tracker-exception",
    "tracker-outcome",
    "tracker-transition",
)

GRANT_REQUIRED_KEYS = (
    "operator_question",
    "promise",
    "exclusions",
    "route",
    "assumptions",
    "assumption_coverage",
    "tolerances",
    "baseline",
    "representative_probe",
    "planned_observations",
    "enforcement",
    "delivery_authorized",
)


class StateError(Exception):
    """A refusal the caller is expected to surface, not a crash."""


# ---------------------------------------------------------------------------
# Location
# ---------------------------------------------------------------------------


def resolve_repo_root(start: Path | None = None) -> Path:
    """Repository root for *start*, falling back to *start* itself."""
    cwd = (start or Path.cwd()).resolve()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip()).resolve()
    except (OSError, subprocess.SubprocessError):
        pass
    return cwd


def resolve_state_root(repo_root: Path | None = None) -> Path:
    """State root for *repo_root*.

    ``AW_STATE_ROOT`` overrides the derived location outright, which is how
    tests (and anyone wanting an isolated run) keep off the real one.
    """
    override = os.environ.get("AW_STATE_ROOT")
    if override:
        return Path(override).expanduser().resolve()

    root = (repo_root or resolve_repo_root()).resolve()
    digest = hashlib.sha1(str(root).encode("utf-8")).hexdigest()[:12]
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", root.name).strip("-").lower() or "repo"
    base = Path(os.environ.get("CLAUDE_CONFIG_DIR", Path.home() / ".claude")).expanduser()
    return (base / "state" / "attention-workflow" / f"{slug}-{digest}").resolve()


def current_path(state_root: Path) -> Path:
    return state_root / "current.json"


def grants_dir(state_root: Path) -> Path:
    return state_root / "grants"


def runs_dir(state_root: Path) -> Path:
    return state_root / "runs"


def history_path(state_root: Path) -> Path:
    return state_root / "history.jsonl"


# ---------------------------------------------------------------------------
# Durable IO
# ---------------------------------------------------------------------------


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _serialize(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def atomic_write_json(path: Path, payload: Any) -> None:
    """Serialize first, then replace. A bad payload never truncates the file."""
    text = _serialize(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def create_json_exclusive(path: Path, payload: Any) -> None:
    """Create *path*; refuse if it already exists.

    This is what makes a grant immutable at the helper layer: there is no code
    path here that opens an existing grant for writing.
    """
    text = _serialize(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
    except FileExistsError as exc:
        raise StateError(f"refusing to overwrite existing record: {path}") from exc
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def append_history(state_root: Path, entry: dict[str, Any]) -> None:
    path = history_path(state_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = dict(entry)
    record.setdefault("at", _now())
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------


def _numbered_ids(directory: Path, prefix: str) -> list[str]:
    if not directory.is_dir():
        return []
    found = []
    for child in directory.glob(f"{prefix}*.json"):
        match = re.fullmatch(rf"{prefix}(\d+)", child.stem)
        if match:
            found.append((int(match.group(1)), child.stem))
    return [name for _, name in sorted(found)]


def next_id(directory: Path, prefix: str) -> str:
    existing = _numbered_ids(directory, prefix)
    highest = max((int(name[len(prefix) :]) for name in existing), default=0)
    return f"{prefix}{highest + 1}"


def load_grant(state_root: Path, grant_id: str) -> dict[str, Any]:
    path = grants_dir(state_root) / f"{grant_id}.json"
    if not path.is_file():
        raise StateError(f"grant {grant_id} does not exist")
    return read_json(path)


def all_grants(state_root: Path) -> list[dict[str, Any]]:
    return [load_grant(state_root, gid) for gid in _numbered_ids(grants_dir(state_root), "g")]


def superseding_grant(state_root: Path, grant_id: str) -> str | None:
    """Grant id that supersedes *grant_id*, derived from successors.

    Supersession is recorded only on the new grant. Stamping a back-pointer
    into the old one would be a rewrite of an immutable record.
    """
    for grant in all_grants(state_root):
        if grant.get("supersedes") == grant_id:
            return grant.get("id")
    return None


def load_run(state_root: Path, run_id: str) -> dict[str, Any]:
    path = runs_dir(state_root) / f"{run_id}.json"
    if not path.is_file():
        raise StateError(f"verification run {run_id} does not exist")
    return read_json(path)


def all_runs(state_root: Path) -> list[dict[str, Any]]:
    return [load_run(state_root, rid) for rid in _numbered_ids(runs_dir(state_root), "v")]


def load_current(state_root: Path) -> dict[str, Any] | None:
    path = current_path(state_root)
    if not path.is_file():
        return None
    try:
        data = read_json(path)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {"__unreadable__": True}
    if not isinstance(data, dict):
        return {"__unreadable__": True}
    return data


# ---------------------------------------------------------------------------
# Evaluation — the fail-safe projection
# ---------------------------------------------------------------------------


def evaluate(state_root: Path) -> dict[str, Any]:
    """Return the projection a resumer should act on.

    ``status`` is one of:

      no-state   nothing here; this repository has no active change
      ok         the record is internally coherent
      fail-safe  incomplete or contradictory; forced into Prepare/Exception
    """
    raw = load_current(state_root)
    if raw is None:
        return {"status": "no-state", "state_root": str(state_root)}

    problems: list[str] = []
    if raw.get("__unreadable__"):
        problems.append("current.json is present but not readable as a JSON object")
        raw = {}

    phase = raw.get("phase")
    owner = raw.get("owner")
    condition = raw.get("condition")
    grant_id = raw.get("active_grant")
    run_id = raw.get("active_verification_run")

    if phase not in PHASES:
        problems.append(f"phase {phase!r} is not one of {list(PHASES)}")
    if owner not in OWNERS:
        problems.append(f"owner {owner!r} is not one of {list(OWNERS)}")
    if condition not in CONDITIONS:
        problems.append(f"condition {condition!r} is not one of {list(CONDITIONS)}")

    grant: dict[str, Any] | None = None
    if grant_id:
        try:
            grant = load_grant(state_root, grant_id)
        except StateError:
            problems.append(f"active grant {grant_id} is referenced but its record is missing")
    elif phase in PHASES_REQUIRING_GRANT:
        problems.append(f"phase {phase!r} requires an active grant but none is recorded")

    if grant_id and grant is not None:
        successor = superseding_grant(state_root, grant_id)
        if successor and phase not in ("design", "prepare"):
            problems.append(
                f"active grant {grant_id} was superseded by {successor}; "
                "authority must be re-established before work continues"
            )

    run: dict[str, Any] | None = None
    if run_id:
        try:
            run = load_run(state_root, run_id)
        except StateError:
            problems.append(f"verification run {run_id} is referenced but its record is missing")

    if raw.get("closed") and not raw.get("outcome"):
        problems.append("change is marked closed but records no outcome")

    projection: dict[str, Any] = {
        "state_root": str(state_root),
        "change_id": raw.get("change_id"),
        "title": raw.get("title"),
        "repository": raw.get("repository"),
        "issue": raw.get("issue"),
        "phase": phase,
        "owner": owner,
        "condition": condition,
        "active_grant": grant_id,
        "active_candidate": raw.get("active_candidate"),
        "active_verification_run": run_id,
        "last_transition": raw.get("last_transition"),
        "next_transition": raw.get("next_transition"),
        "attention": raw.get("attention"),
        "safe_point": raw.get("safe_point"),
        "closed": bool(raw.get("closed")),
        "outcome": raw.get("outcome"),
    }

    if run is not None:
        projection["verification_run"] = {
            "id": run.get("id"),
            "grant": run.get("grant"),
            "candidate": run.get("candidate"),
            "state": run.get("state"),
            "stale": bool(run.get("stale")),
            "has_terminal_result": run.get("state") in RUN_TERMINAL_STATES,
            "operator_judgment_recorded": bool(run.get("operator_judgment")),
            "verdict_revealed": bool(run.get("revealed_at")),
        }

    if grant is not None:
        projection["grant_summary"] = {
            "id": grant.get("id"),
            "supersedes": grant.get("supersedes"),
            "operator_question": grant.get("operator_question"),
            "promise": grant.get("promise"),
            "delivery_authorized": grant.get("delivery_authorized"),
        }

    if problems:
        projection.update(
            {
                "status": "fail-safe",
                "recorded_phase": phase,
                "recorded_owner": owner,
                "recorded_condition": condition,
                "phase": "prepare",
                "owner": "jacob",
                "condition": "exception",
                "problems": problems,
                "next_transition": (
                    "Restore the missing or contradictory authority before any "
                    "implementation, verification, or delivery action."
                ),
                "attention": {
                    "kind": "exception",
                    "summary": "Workflow state is incomplete or contradictory.",
                },
            }
        )
    else:
        projection["status"] = "ok"

    return projection


# ---------------------------------------------------------------------------
# Context rendering (SessionStart)
# ---------------------------------------------------------------------------


def _bullets(label: str, values: Any, limit: int = 4) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    lines = [f"{label}:"]
    for value in list(values)[:limit]:
        lines.append(f"  - {value}")
    if len(values) > limit:
        lines.append(f"  - (+{len(values) - limit} more in the grant record)")
    return lines


def _clip(text: Any, limit: int = 140) -> str:
    """Keep the card scannable. The full text always stays in the record."""
    value = str(text or "").strip().replace("\n", " ")
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def render_context(projection: dict[str, Any]) -> str:
    """Compact orientation text for a fresh, resumed, or forked session."""
    if projection.get("status") == "no-state":
        return ""

    # A closed change owns no attention. Reprinting its whole card in every
    # later session is exactly the ceremony this workflow exists to remove, so
    # it collapses to one line that says the thread is released.
    if projection.get("closed") and projection.get("status") == "ok":
        return (
            f"ATTENTION-WORKFLOW: no active change. Last change "
            f"{projection.get('change_id')} is {projection.get('outcome') or 'closed'}; "
            "attention released. Ask for its state only if you need the history."
        )

    lines = ["ATTENTION-WORKFLOW STATE (loaded from local run state, not chat history)"]
    lines.append("")

    if projection.get("status") == "fail-safe":
        lines.append("CONDITION  Exception - state is incomplete or contradictory.")
        lines.append("PHASE      Prepare (fail-safe; recorded phase was "
                     f"{projection.get('recorded_phase')!r})")
        lines.append("OWNER      Jacob")
        lines.append("")
        lines.append("Do not infer authority from git state, issue status, or chat history.")
        lines.append("Problems found:")
        for problem in projection.get("problems", []):
            lines.append(f"  - {problem}")
        lines.append("")
        lines.append(
            "Next: return the smallest decision that restores the missing authority. "
            "No implementation, verification, or delivery action may continue."
        )
        return "\n".join(lines)

    lines.append(f"CHANGE     {projection.get('title') or projection.get('change_id')}")
    lines.append(f"PHASE      {projection.get('phase')}")
    lines.append(f"OWNER      {projection.get('owner')}")
    lines.append(f"CONDITION  {projection.get('condition')}")

    grant = projection.get("grant_summary")
    if grant:
        lines.append(
            f"AUTHORITY  grant {grant.get('id')}"
            + (f" (supersedes {grant['supersedes']})" if grant.get("supersedes") else "")
        )
        if grant.get("operator_question"):
            lines.append(f"QUESTION   {_clip(grant['operator_question'])}")
    else:
        lines.append("AUTHORITY  none recorded")

    if projection.get("active_candidate"):
        lines.append(f"CANDIDATE  {projection['active_candidate']}")

    run = projection.get("verification_run")
    if run:
        detail = f"run {run['id']} state={run['state']}"
        if run.get("stale"):
            detail += " STALE"
        if run.get("has_terminal_result"):
            detail += "; terminal result persisted"
        if run.get("operator_judgment_recorded"):
            detail += "; operator judgment recorded"
        lines.append(f"VERIFY     {detail}")

    issue = projection.get("issue")
    if issue:
        lines.append(
            f"ISSUE      {issue.get('host')} {issue.get('identity')} "
            f"(projection {issue.get('projection_status')}) - local state stays canonical"
        )

    last = projection.get("last_transition") or {}
    if last:
        lines.append(
            f"LAST MOVE  {last.get('from_phase')} -> {last.get('to_phase')}: {last.get('reason')}"
        )
    if projection.get("next_transition"):
        lines.append(f"NEXT MOVE  {projection['next_transition']}")
    if projection.get("safe_point"):
        lines.append(f"SAFE POINT {projection['safe_point']}")

    attention = projection.get("attention")
    if attention:
        lines.append(f"ATTENTION  {attention.get('kind')}: {attention.get('summary')}")
    else:
        lines.append("ATTENTION  released; no operator action pending")

    lines.append("")
    lines.append(f"State helper: python3 {Path(__file__).resolve()}")
    lines.append(
        "Read and write this state only through that helper. "
        "Do not reconstruct authority from git state, issue status, or chat history."
    )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Delivery authority
# ---------------------------------------------------------------------------


def delivery_allowed(state_root: Path, action: str) -> tuple[bool, str]:
    """Is *action* covered by the active grant?

    Returns ``(allowed, reason)``. When no change is active in this repository
    the workflow makes no authority claim, so it does not gate the action.
    """
    projection = evaluate(state_root)
    status = projection.get("status")

    if status == "no-state":
        return True, "no active attention-workflow change in this repository"
    if projection.get("closed"):
        return True, "the active change is closed; the workflow no longer gates delivery"
    if status == "fail-safe":
        return False, (
            "workflow state is incomplete or contradictory, so no delivery action is "
            "authorized. Problems: " + "; ".join(projection.get("problems", []))
        )

    grant_id = projection.get("active_grant")
    if not grant_id:
        return False, "no active grant is recorded, so no delivery action is authorized"

    grant = load_grant(state_root, grant_id)
    authorized = grant.get("delivery_authorized") or []
    if action in authorized:
        return True, f"grant {grant_id} authorizes {action}"
    return False, (
        f"grant {grant_id} does not authorize {action}. It authorizes: "
        + (", ".join(authorized) if authorized else "(nothing)")
    )


# ---------------------------------------------------------------------------
# Checkpoint postconditions
# ---------------------------------------------------------------------------


def _run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def detect_vcs(repo_root: Path) -> str:
    if (repo_root / ".jj").is_dir():
        return "jj"
    return "git"


def verify_checkpoint(repo_root: Path, vcs: str | None = None) -> dict[str, Any]:
    """Observe whether a checkpoint boundary actually exists.

    Agent prose is not the postcondition. For git the observable is a clean
    working tree at a resolvable HEAD; for jj it is an empty working-copy
    change, which is what `jj describe` alone fails to produce.
    """
    vcs = vcs or detect_vcs(repo_root)
    result: dict[str, Any] = {"vcs": vcs, "repo": str(repo_root)}

    if vcs == "jj":
        code, out, err = _run(["jj", "log", "-r", "@", "--no-graph", "-T", "empty"], repo_root)
        if code != 0:
            result.update(
                {"checkpoint": False, "observed": err or out, "reason": "jj query failed"}
            )
            return result
        empty = out.strip() == "true"
        result.update(
            {
                "checkpoint": empty,
                "observed": f"@ empty={out.strip()}",
                "reason": (
                    "working-copy change is empty; the checkpoint advanced"
                    if empty
                    else "working-copy change is NOT empty; `jj describe` alone does not "
                    "advance it, so later work shares the same change"
                ),
            }
        )
        return result

    code, head, err = _run(["git", "rev-parse", "HEAD"], repo_root)
    if code != 0:
        result.update({"checkpoint": False, "observed": err, "reason": "no resolvable HEAD"})
        return result
    _, status, _ = _run(["git", "status", "--porcelain"], repo_root)
    clean = status == ""
    result.update(
        {
            "checkpoint": clean,
            "head": head,
            "observed": status or "(clean)",
            "reason": (
                "working tree is clean at the claimed commit"
                if clean
                else "working tree still carries uncommitted changes; "
                "the claimed checkpoint does not isolate them"
            ),
        }
    )
    return result


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def _state_root_from_args(args: argparse.Namespace) -> Path:
    if getattr(args, "state_root", None):
        return Path(args.state_root).expanduser().resolve()
    repo = Path(args.repo).resolve() if getattr(args, "repo", None) else None
    return resolve_state_root(repo)


def _emit(payload: Any) -> None:
    sys.stdout.write(_serialize(payload))


def cmd_state_root(args: argparse.Namespace) -> int:
    sys.stdout.write(str(_state_root_from_args(args)) + "\n")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    path = current_path(state_root)
    if path.exists() and not args.force:
        raise StateError(
            f"a change is already active at {path}. Close it, or pass --force to replace it."
        )
    repo_root = Path(args.repo).resolve() if args.repo else resolve_repo_root()
    issue = None
    if args.issue_host:
        issue = {
            "host": args.issue_host,
            "identity": args.issue_id,
            "url": args.issue_url,
            "projection_status": "never-projected",
            "last_projected_at": None,
            "stale_reason": None,
        }
    record = {
        "schema": SCHEMA_CURRENT,
        "change_id": args.change_id,
        "title": args.title,
        "repository": {"root": str(repo_root), "vcs": detect_vcs(repo_root)},
        "issue": issue,
        "phase": "frame",
        "owner": "jacob",
        "condition": "active",
        "active_grant": None,
        "active_candidate": None,
        "active_verification_run": None,
        "last_transition": {
            "from_phase": None,
            "to_phase": "frame",
            "reason": "change opened",
            "at": _now(),
        },
        "next_transition": "Frame the bounded change, then design the route.",
        "attention": None,
        "safe_point": None,
        "closed": False,
        "outcome": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    atomic_write_json(path, record)
    append_history(state_root, {"event": "init", "change_id": args.change_id})
    _emit(evaluate(state_root))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    _emit(evaluate(_state_root_from_args(args)))
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    text = render_context(evaluate(_state_root_from_args(args)))
    if text:
        sys.stdout.write(text + "\n")
    return 0


def cmd_transition(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    raw = load_current(state_root)
    if raw is None or raw.get("__unreadable__"):
        raise StateError("no readable current state; run `init` or repair the record first")

    before_phase = raw.get("phase")
    updates: dict[str, Any] = {}
    if args.phase:
        if args.phase not in PHASES:
            raise StateError(f"unknown phase {args.phase!r}")
        updates["phase"] = args.phase
    if args.owner:
        if args.owner not in OWNERS:
            raise StateError(f"unknown owner {args.owner!r}")
        updates["owner"] = args.owner
    if args.condition:
        if args.condition not in CONDITIONS:
            raise StateError(f"unknown condition {args.condition!r}")
        updates["condition"] = args.condition
    for field in ("active_grant", "active_candidate", "active_verification_run"):
        value = getattr(args, field)
        if value is not None:
            updates[field] = None if value == "" else value
    if args.next is not None:
        updates["next_transition"] = args.next
    if args.safe_point is not None:
        updates["safe_point"] = args.safe_point
    if args.clear_attention:
        updates["attention"] = None
    elif args.attention_kind:
        updates["attention"] = {"kind": args.attention_kind, "summary": args.attention_summary}
    if args.outcome:
        updates["outcome"] = args.outcome
        updates["closed"] = True

    raw.update(updates)
    raw["last_transition"] = {
        "from_phase": before_phase,
        "to_phase": raw.get("phase"),
        "reason": args.reason,
        "at": _now(),
    }
    raw["updated_at"] = _now()
    atomic_write_json(current_path(state_root), raw)
    append_history(
        state_root,
        {
            "event": "transition",
            "from_phase": before_phase,
            "to_phase": raw.get("phase"),
            "owner": raw.get("owner"),
            "condition": raw.get("condition"),
            "reason": args.reason,
            "attention": raw.get("attention"),
        },
    )
    _emit(evaluate(state_root))
    return 0


def cmd_grant_create(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    payload = read_json(Path(args.file))
    if not isinstance(payload, dict):
        raise StateError("grant payload must be a JSON object")

    missing = [key for key in GRANT_REQUIRED_KEYS if key not in payload]
    if missing:
        raise StateError(f"grant payload is missing required keys: {', '.join(missing)}")

    unknown = [a for a in payload.get("delivery_authorized") or [] if a not in DELIVERY_ACTIONS]
    if unknown:
        raise StateError(
            f"delivery_authorized contains actions this workflow cannot classify: "
            f"{', '.join(unknown)}. Known actions: {', '.join(DELIVERY_ACTIONS)}"
        )

    probe = payload.get("representative_probe") or {}
    if not probe.get("probe") and not probe.get("waived_reason"):
        raise StateError(
            "representative_probe must name a probe, or record waived_reason explaining why "
            "a probe would add no information for this change"
        )

    supersedes = payload.get("supersedes")
    if supersedes:
        load_grant(state_root, supersedes)  # raises if it does not exist
        existing = superseding_grant(state_root, supersedes)
        if existing:
            raise StateError(f"grant {supersedes} is already superseded by {existing}")

    grant_id = args.id or next_id(grants_dir(state_root), "g")
    payload["id"] = grant_id
    payload["schema"] = SCHEMA_GRANT
    payload["created_at"] = _now()

    create_json_exclusive(grants_dir(state_root) / f"{grant_id}.json", payload)
    append_history(
        state_root, {"event": "grant-created", "grant": grant_id, "supersedes": supersedes}
    )

    stale_runs: list[str] = []
    if supersedes:
        for run in all_runs(state_root):
            if run.get("stale"):
                continue
            run["stale"] = True
            run["stale_reason"] = f"grant {supersedes} superseded by {grant_id}"
            run["updated_at"] = _now()
            atomic_write_json(runs_dir(state_root) / f"{run['id']}.json", run)
            stale_runs.append(run["id"])
        append_history(
            state_root,
            {"event": "evidence-stale", "grant": grant_id, "runs": stale_runs},
        )

    _emit({"grant": grant_id, "supersedes": supersedes, "runs_marked_stale": stale_runs})
    return 0


def cmd_grant_show(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    grant = load_grant(state_root, args.id)
    grant["superseded_by"] = superseding_grant(state_root, args.id)
    _emit(grant)
    return 0


def cmd_grant_list(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    _emit(
        [
            {
                "id": g["id"],
                "created_at": g.get("created_at"),
                "supersedes": g.get("supersedes"),
                "superseded_by": superseding_grant(state_root, g["id"]),
                "operator_question": g.get("operator_question"),
            }
            for g in all_grants(state_root)
        ]
    )
    return 0


def cmd_run_create(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    load_grant(state_root, args.grant)
    run_id = next_id(runs_dir(state_root), "v")
    record = {
        "schema": SCHEMA_RUN,
        "id": run_id,
        "grant": args.grant,
        "candidate": args.candidate,
        "state": "requested",
        "result": None,
        "stale": False,
        "stale_reason": None,
        "operator_judgment": None,
        "revealed_at": None,
        "created_at": _now(),
        "updated_at": _now(),
    }
    create_json_exclusive(runs_dir(state_root) / f"{run_id}.json", record)
    append_history(
        state_root,
        {"event": "run-created", "run": run_id, "grant": args.grant, "candidate": args.candidate},
    )
    _emit(record)
    return 0


def cmd_run_state(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    run = load_run(state_root, args.id)
    if args.state not in RUN_STATES:
        raise StateError(f"unknown run state {args.state!r}")
    if run["state"] in RUN_TERMINAL_STATES and args.state != run["state"]:
        raise StateError(
            f"run {args.id} already holds terminal state {run['state']!r}; "
            "a terminal result is never regressed"
        )
    run["state"] = args.state
    run["updated_at"] = _now()
    atomic_write_json(runs_dir(state_root) / f"{args.id}.json", run)
    append_history(state_root, {"event": "run-state", "run": args.id, "state": args.state})
    _emit(run)
    return 0


def cmd_run_complete(args: argparse.Namespace) -> int:
    """Record a terminal result. Idempotent: the first terminal write wins.

    This is the join point that makes verifier completion independent of
    message delivery. A delayed, duplicated, or reordered notification lands
    here and changes nothing.
    """
    state_root = _state_root_from_args(args)
    run = load_run(state_root, args.id)

    if run["state"] in RUN_TERMINAL_STATES:
        _emit({"run": run, "duplicate": True, "note": "terminal result already recorded"})
        return 0

    result = read_json(Path(args.result)) if args.result else None
    run["state"] = args.state
    run["result"] = result
    run["updated_at"] = _now()
    atomic_write_json(runs_dir(state_root) / f"{args.id}.json", run)
    append_history(
        state_root, {"event": "run-complete", "run": args.id, "state": args.state}
    )
    _emit({"run": run, "duplicate": False})
    return 0


def _withheld(run: dict[str, Any]) -> dict[str, Any]:
    """The run record with the verifier's conclusion removed."""
    shown = dict(run)
    result = dict(run.get("result") or {})
    for key in ("verdict", "recommendation", "overall", "summary_verdict"):
        result.pop(key, None)
    shown["result"] = result
    shown["verdict_withheld"] = True
    return shown


def cmd_run_evidence(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    run = load_run(state_root, args.id)
    if run["state"] not in RUN_TERMINAL_STATES:
        raise StateError(f"run {args.id} has no terminal result yet (state={run['state']!r})")
    _emit(_withheld(run))
    return 0


def cmd_run_judge(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    run = load_run(state_root, args.id)
    if run.get("operator_judgment"):
        raise StateError(f"run {args.id} already records an operator judgment")
    if args.judgment not in ("ready", "not-ready", "inspect"):
        raise StateError("judgment must be one of: ready, not-ready, inspect")
    if not args.decisive or not args.decisive.strip():
        raise StateError(
            "record the decisive observation or the named inspection; "
            "a bare ratification does not satisfy reconciliation"
        )
    run["operator_judgment"] = {
        "judgment": args.judgment,
        "decisive": args.decisive.strip(),
        "recorded_at": _now(),
    }
    run["updated_at"] = _now()
    atomic_write_json(runs_dir(state_root) / f"{args.id}.json", run)
    append_history(
        state_root, {"event": "operator-judgment", "run": args.id, "judgment": args.judgment}
    )
    _emit(run["operator_judgment"])
    return 0


def cmd_run_reveal(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    run = load_run(state_root, args.id)
    if not run.get("operator_judgment"):
        raise StateError(
            f"run {args.id} has no recorded operator judgment. The verifier's verdict and "
            "recommendation stay withheld until Jacob commits his own."
        )
    if not run.get("revealed_at"):
        run["revealed_at"] = _now()
        run["updated_at"] = _now()
        atomic_write_json(runs_dir(state_root) / f"{args.id}.json", run)

    result = run.get("result") or {}
    verifier = result.get("verdict")
    operator = run["operator_judgment"]["judgment"]
    agreement = None
    if verifier in ("pass", "fail"):
        agreement = (verifier == "pass") == (operator == "ready")
    _emit(
        {
            "run": args.id,
            "operator_judgment": run["operator_judgment"],
            "verifier_verdict": verifier,
            "verifier_recommendation": result.get("recommendation"),
            "agreement": agreement,
        }
    )
    return 0


def cmd_run_list(args: argparse.Namespace) -> int:
    _emit(
        [
            {
                "id": r["id"],
                "grant": r.get("grant"),
                "candidate": r.get("candidate"),
                "state": r.get("state"),
                "stale": bool(r.get("stale")),
                "judgment": (r.get("operator_judgment") or {}).get("judgment"),
            }
            for r in all_runs(_state_root_from_args(args))
        ]
    )
    return 0


def cmd_guard_check(args: argparse.Namespace) -> int:
    allowed, reason = delivery_allowed(_state_root_from_args(args), args.action)
    _emit({"action": args.action, "allowed": allowed, "reason": reason})
    return 0 if allowed else 1


def cmd_checkpoint_verify(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve() if args.repo else resolve_repo_root()
    result = verify_checkpoint(repo, args.vcs)
    _emit(result)
    return 0 if result.get("checkpoint") else 1


def cmd_issue_set(args: argparse.Namespace) -> int:
    state_root = _state_root_from_args(args)
    raw = load_current(state_root)
    if raw is None or raw.get("__unreadable__"):
        raise StateError("no readable current state")
    raw["issue"] = {
        "host": args.host,
        "identity": args.identity,
        "url": args.url,
        "projection_status": args.status,
        "last_projected_at": _now() if args.status == "current" else None,
        "stale_reason": args.stale_reason,
    }
    raw["updated_at"] = _now()
    atomic_write_json(current_path(state_root), raw)
    append_history(
        state_root,
        {"event": "issue-projection", "host": args.host, "identity": args.identity,
         "status": args.status, "stale_reason": args.stale_reason},
    )
    _emit(raw["issue"])
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    path = history_path(_state_root_from_args(args))
    if not path.is_file():
        _emit([])
        return 0
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if args.limit:
        entries = entries[-args.limit :]
    _emit(entries)
    return 0


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aw_state", description=__doc__)
    parser.add_argument("--repo", help="repository root (defaults to the discovered one)")
    parser.add_argument("--state-root", help="explicit state root (overrides AW_STATE_ROOT)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("state-root").set_defaults(func=cmd_state_root)

    p = sub.add_parser("init")
    p.add_argument("--change-id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--issue-host", choices=["linear", "fibery"])
    p.add_argument("--issue-id")
    p.add_argument("--issue-url")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    sub.add_parser("show").set_defaults(func=cmd_show)
    sub.add_parser("context").set_defaults(func=cmd_context)

    p = sub.add_parser("transition")
    p.add_argument("--phase", choices=list(PHASES))
    p.add_argument("--owner", choices=list(OWNERS))
    p.add_argument("--condition", choices=list(CONDITIONS))
    p.add_argument("--reason", required=True)
    p.add_argument("--next", dest="next")
    p.add_argument("--safe-point")
    p.add_argument("--active-grant", dest="active_grant")
    p.add_argument("--active-candidate", dest="active_candidate")
    p.add_argument("--active-verification-run", dest="active_verification_run")
    p.add_argument("--attention-kind", choices=["decision", "authorization", "reconciliation",
                                                "exception", "delivery"])
    p.add_argument("--attention-summary", default="")
    p.add_argument("--clear-attention", action="store_true")
    p.add_argument("--outcome", choices=["delivered", "stopped", "abandoned"])
    p.set_defaults(func=cmd_transition)

    p = sub.add_parser("grant-create")
    p.add_argument("--file", required=True, help="JSON file holding the prepared basis")
    p.add_argument("--id", help="explicit grant id (defaults to the next free one)")
    p.set_defaults(func=cmd_grant_create)

    p = sub.add_parser("grant-show")
    p.add_argument("id")
    p.set_defaults(func=cmd_grant_show)

    sub.add_parser("grant-list").set_defaults(func=cmd_grant_list)

    p = sub.add_parser("run-create")
    p.add_argument("--grant", required=True)
    p.add_argument("--candidate", required=True)
    p.set_defaults(func=cmd_run_create)

    p = sub.add_parser("run-state")
    p.add_argument("id")
    p.add_argument("--state", required=True, choices=list(RUN_STATES))
    p.set_defaults(func=cmd_run_state)

    p = sub.add_parser("run-complete")
    p.add_argument("id")
    p.add_argument("--result", help="JSON file holding the verifier's report")
    p.add_argument("--state", default="completed", choices=["completed", "failed"])
    p.set_defaults(func=cmd_run_complete)

    p = sub.add_parser("run-evidence")
    p.add_argument("id")
    p.set_defaults(func=cmd_run_evidence)

    p = sub.add_parser("run-judge")
    p.add_argument("id")
    p.add_argument("--judgment", required=True)
    p.add_argument("--decisive", required=True)
    p.set_defaults(func=cmd_run_judge)

    p = sub.add_parser("run-reveal")
    p.add_argument("id")
    p.set_defaults(func=cmd_run_reveal)

    sub.add_parser("run-list").set_defaults(func=cmd_run_list)

    p = sub.add_parser("guard-check")
    p.add_argument("--action", required=True)
    p.set_defaults(func=cmd_guard_check)

    p = sub.add_parser("checkpoint-verify")
    p.add_argument("--vcs", choices=["git", "jj"])
    p.set_defaults(func=cmd_checkpoint_verify)

    p = sub.add_parser("issue-set")
    p.add_argument("--host", required=True, choices=["linear", "fibery"])
    p.add_argument("--identity", required=True)
    p.add_argument("--url")
    p.add_argument("--status", required=True,
                   choices=["never-projected", "current", "stale"])
    p.add_argument("--stale-reason")
    p.set_defaults(func=cmd_issue_set)

    p = sub.add_parser("history")
    p.add_argument("--limit", type=int, default=0)
    p.set_defaults(func=cmd_history)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except StateError as exc:
        sys.stderr.write(f"attention-workflow: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

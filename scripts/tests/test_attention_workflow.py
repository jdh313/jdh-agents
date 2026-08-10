"""Behavioral tests for the attention-workflow plugin.

Two layers, kept apart on purpose:

* **Publication** — the committed Claude publication really carries the skill,
  agent, hooks, references, and executable payloads, and really carries no
  Codex projection.
* **State and guards** — grant immutability, supersession, fail-safe
  evaluation, judgment-before-verdict ordering, terminal-once verification
  runs, and the two PreToolUse guards, exercised as subprocesses against
  isolated state roots and real temporary repositories.

Neither layer is evidence that the workflow regulates attention. That needs the
three hand-observed pilot runs, which have not happened.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "plugins" / "attention-workflow"
PUBLISHED = REPO_ROOT / "marketplaces" / "claude" / "plugins" / "attention-workflow"
HELPER = SOURCE / "scripts" / "aw_state.py"
SESSION_START_HOOK = SOURCE / "hooks" / "session_start.py"
GUARD_HOOK = SOURCE / "hooks" / "authority_delivery_guard.py"


def _load_helper() -> Any:
    # Do not leave a __pycache__ inside the plugin source tree: the marketplace
    # linter walks that directory and would report the .pyc as an unusual file.
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("aw_state_under_test", HELPER)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous


aw_state = _load_helper()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


BASIS: dict[str, Any] = {
    "operator_question": "For this invalid file, can Jacob name the failing key and tell nothing was written?",
    "promise": ["exits 0 for valid configuration", "names the failing key for invalid configuration"],
    "exclusions": ["no repair mode", "no network calls"],
    "route": ["reuse the existing parser and validator", "add a read-only command surface"],
    "assumptions": [
        {
            "statement": "validation failures map back to configuration keys",
            "falsifier": "a nested malformed fixture produces an error with no key",
        }
    ],
    "assumption_coverage": {
        "areas_considered": ["parser data", "local-file behavior", "existing dependencies"],
        "known_unknowns": ["nested error shape"],
        "residual_unlisted_risk": "unlisted assumptions may still exist; this is not an inventory",
    },
    "tolerances": {
        "permitted": ["helper placement", "internal wiring"],
        "stop_before": ["changing the parser model", "adding a dependency"],
    },
    "baseline": {"description": "current unit suite passes", "classified": True},
    "representative_probe": {
        "question": "does the diagnostic name the key and rule?",
        "probe": "run the nested-invalid fixture and compare bytes before/after",
    },
    "planned_observations": ["black-box CLI tests", "byte-for-byte no-write check"],
    "enforcement": {
        "hook_guarded": ["grant record writes", "unauthorized git push"],
        "check_gated": ["dependency diff before readiness"],
        "agent_monitored": ["semantic scope drift"],
        "uncovered": ["unlisted assumptions"],
    },
    "delivery_authorized": ["commit"],
}


@pytest.fixture
def state_root(tmp_path: Path) -> Path:
    root = tmp_path / "state"
    root.mkdir()
    return root


@pytest.fixture
def env(state_root: Path) -> dict[str, str]:
    merged = dict(os.environ)
    merged["AW_STATE_ROOT"] = str(state_root)
    # The developer's global git config signs every commit through a 1Password
    # agent. Temporary fixture repositories must not depend on it.
    merged["GIT_CONFIG_GLOBAL"] = os.devnull
    merged["GIT_CONFIG_SYSTEM"] = os.devnull
    return merged


def helper(env: dict[str, str], *args: str, expect: int | None = 0) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        [sys.executable, str(HELPER), *args],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    if expect is not None:
        assert proc.returncode == expect, f"args={args}\nstdout={proc.stdout}\nstderr={proc.stderr}"
    return proc


def helper_json(env: dict[str, str], *args: str) -> Any:
    return json.loads(helper(env, *args).stdout)


def write_basis(tmp_path: Path, **overrides: Any) -> Path:
    payload = json.loads(json.dumps(BASIS))
    payload.update(overrides)
    path = tmp_path / f"basis-{len(list(tmp_path.glob('basis-*.json')))}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def open_change(env: dict[str, str], tmp_path: Path, **overrides: Any) -> str:
    helper(env, "init", "--change-id", "demo", "--title", "Demo change")
    created = helper_json(env, "grant-create", "--file", str(write_basis(tmp_path, **overrides)))
    helper(
        env,
        "transition",
        "--phase",
        "implement",
        "--owner",
        "execution",
        "--active-grant",
        created["grant"],
        "--reason",
        "Jacob authorized the prepared basis",
    )
    return created["grant"]


def run_hook(script: Path, payload: dict[str, Any], env: dict[str, str]) -> dict[str, Any]:
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, f"hook exited {proc.returncode}: {proc.stderr}"
    if not proc.stdout.strip():
        return {}
    return json.loads(proc.stdout)


def bash_payload(command: str, cwd: str) -> dict[str, Any]:
    return {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": cwd,
    }


def decision(result: dict[str, Any]) -> str | None:
    return (result.get("hookSpecificOutput") or {}).get("permissionDecision")


def _isolated_vcs_env(tmp_path: Path) -> dict[str, str]:
    """Environment for fixture repositories, free of the developer's config.

    The global git and jj configs here sign every commit through a 1Password
    agent, which is neither available nor relevant to these tests.
    """
    merged = dict(os.environ)
    merged["GIT_CONFIG_GLOBAL"] = os.devnull
    merged["GIT_CONFIG_SYSTEM"] = os.devnull
    jj_config = tmp_path / "jj-config.toml"
    jj_config.write_text(
        '[user]\nname = "Test"\nemail = "test@example.com"\n'
        '[signing]\nbehavior = "drop"\n',
        encoding="utf-8",
    )
    merged["JJ_CONFIG"] = str(jj_config)
    return merged


@pytest.fixture
def git_repo(tmp_path: Path) -> Iterator[Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    vcs_env = _isolated_vcs_env(tmp_path)
    run = lambda *args: subprocess.run(  # noqa: E731 - terse local helper
        args, cwd=repo, capture_output=True, text=True, check=True, env=vcs_env
    )
    run("git", "init", "-q")
    run("git", "config", "user.email", "test@example.com")
    run("git", "config", "user.name", "Test")
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    run("git", "add", "README.md")
    run("git", "commit", "-qm", "initial")
    yield repo


# ---------------------------------------------------------------------------
# Publication
# ---------------------------------------------------------------------------


def test_source_package_declares_claude_only() -> None:
    text = (SOURCE / "PACKAGE.yaml").read_text(encoding="utf-8")
    assert "id: attention-workflow" in text
    assert "  claude:" in text
    assert "  codex:" not in text, "Experiment 1 is Claude-only; a Codex target would publish a package whose hook guarantee is absent"


def test_claude_publication_carries_every_declared_surface() -> None:
    manifest = json.loads((PUBLISHED / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "attention-workflow"
    assert manifest["version"] == "0.6.0"
    # Experimental: installing the marketplace must not switch the lifecycle
    # out from under an in-flight spec-flow change.
    assert manifest["defaultEnabled"] is False

    # Payloads are copied verbatim — the executables the hooks actually run,
    # and the references the skill points at.
    for relative in (
        "hooks/hooks.json",
        "hooks/session_start.py",
        "hooks/authority_delivery_guard.py",
        "scripts/aw_state.py",
        "references/state-model.md",
        "references/enforcement-map.md",
        "references/issue-projections.md",
    ):
        published = PUBLISHED / relative
        assert published.is_file(), f"missing from the Claude publication: {relative}"
        assert published.read_bytes() == (SOURCE / relative).read_bytes()

    # Artifacts have their front-matter re-emitted by the compiler, so compare
    # identity and body rather than bytes.
    skill = (PUBLISHED / "skills" / "workflow" / "SKILL.md").read_text(encoding="utf-8")
    assert "name: workflow" in skill
    assert "Frame -> Design -> Prepare --authorize--> Implement" in skill
    # Run 1 left an ordinary defect recorded as verify -> verify; the skill must
    # spell out the phase change so the record stays honest about who is acting.
    assert "--phase implement --owner execution" in skill
    assert "VERIFIER VERDICT" in skill or "no verdict, no recommendation" in skill

    agent = (PUBLISHED / "agents" / "workflow-verifier.md").read_text(encoding="utf-8")
    assert "name: workflow-verifier" in agent
    assert agent.split("---", 2)[2] == (SOURCE / "agents" / "workflow-verifier.md").read_text(
        encoding="utf-8"
    ).split("---", 2)[2]


def test_published_executable_payloads_keep_their_exec_bit() -> None:
    for relative in ("hooks/session_start.py", "hooks/authority_delivery_guard.py"):
        assert os.access(PUBLISHED / relative, os.X_OK), relative


def test_published_hooks_declare_sessionstart_and_pretooluse() -> None:
    hooks = json.loads((PUBLISHED / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    assert "SessionStart" in hooks
    matchers = [entry.get("matcher") for entry in hooks["PreToolUse"]]
    assert matchers == ["Bash|Edit|Write|NotebookEdit|MultiEdit"]


def test_no_codex_publication_for_this_package() -> None:
    codex = REPO_ROOT / "marketplaces" / "codex" / "plugins" / "attention-workflow"
    assert not codex.exists(), "Codex is deliberately out of scope for Experiment 1"

    registry = json.loads(
        (REPO_ROOT / "marketplaces" / "codex" / ".agents" / "plugins" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )
    names = {plugin["name"] for plugin in registry["plugins"]}
    assert "attention-workflow" not in names


def test_claude_registry_lists_the_package() -> None:
    registry = json.loads(
        (REPO_ROOT / "marketplaces" / "claude" / ".claude-plugin" / "marketplace.json").read_text(
            encoding="utf-8"
        )
    )
    entry = next(p for p in registry["plugins"] if p["name"] == "attention-workflow")
    assert entry["version"] == "0.6.0"


def test_verifier_agent_is_read_and_execute_only() -> None:
    text = (SOURCE / "agents" / "workflow-verifier.md").read_text(encoding="utf-8")
    frontmatter = text.split("---", 2)[1]
    assert "- Bash" in frontmatter and "- Read" in frontmatter
    for forbidden in ("- Edit", "- Write", "- NotebookEdit"):
        assert forbidden not in frontmatter
    # ndr:6x3v6p — a sole-enforcement tool filter is restated in body prose.
    assert "never edits source" in text.lower() or "never edit source" in text.lower()


# ---------------------------------------------------------------------------
# Grants: create-only, supersession, staleness
# ---------------------------------------------------------------------------


def test_grant_creation_refuses_to_overwrite(env: dict[str, str], tmp_path: Path) -> None:
    helper(env, "init", "--change-id", "demo", "--title", "Demo")
    helper(env, "grant-create", "--file", str(write_basis(tmp_path)), "--id", "g1")
    before = (Path(env["AW_STATE_ROOT"]) / "grants" / "g1.json").read_bytes()

    proc = helper(env, "grant-create", "--file", str(write_basis(tmp_path)), "--id", "g1", expect=2)
    assert "refusing to overwrite" in proc.stderr
    assert (Path(env["AW_STATE_ROOT"]) / "grants" / "g1.json").read_bytes() == before


def test_grant_creation_requires_a_probe_or_a_recorded_waiver(
    env: dict[str, str], tmp_path: Path
) -> None:
    helper(env, "init", "--change-id", "demo", "--title", "Demo")
    basis = write_basis(tmp_path, representative_probe={})
    proc = helper(env, "grant-create", "--file", str(basis), expect=2)
    assert "representative_probe" in proc.stderr

    ok = write_basis(tmp_path, representative_probe={"waived_reason": "one-character typo fix"})
    helper(env, "grant-create", "--file", str(ok))


def test_grant_creation_rejects_an_unclassifiable_delivery_action(
    env: dict[str, str], tmp_path: Path
) -> None:
    helper(env, "init", "--change-id", "demo", "--title", "Demo")
    basis = write_basis(tmp_path, delivery_authorized=["commit", "ssh-into-prod"])
    proc = helper(env, "grant-create", "--file", str(basis), expect=2)
    assert "ssh-into-prod" in proc.stderr


def test_supersession_preserves_the_old_grant_and_records_only_forward(
    env: dict[str, str], tmp_path: Path
) -> None:
    grant = open_change(env, tmp_path)
    original = (Path(env["AW_STATE_ROOT"]) / "grants" / f"{grant}.json").read_bytes()

    helper(env, "grant-create", "--file", str(write_basis(tmp_path, supersedes=grant)))

    assert (Path(env["AW_STATE_ROOT"]) / "grants" / f"{grant}.json").read_bytes() == original, (
        "the superseded grant must be byte-identical: supersession is recorded on the successor"
    )
    old = helper_json(env, "grant-show", grant)
    assert old["superseded_by"] == "g2"  # derived, not stored
    assert json.loads(original).get("superseded_by") is None

    # A grant may only be superseded once.
    proc = helper(env, "grant-create", "--file", str(write_basis(tmp_path, supersedes=grant)), expect=2)
    assert "already superseded" in proc.stderr


def test_material_amendment_makes_candidate_and_evidence_stale(
    env: dict[str, str], tmp_path: Path
) -> None:
    grant = open_change(env, tmp_path)
    helper(env, "run-create", "--grant", grant, "--candidate", "c1")
    result = tmp_path / "result.json"
    result.write_text(json.dumps({"verdict": "pass", "recommendation": "ship"}), encoding="utf-8")
    helper(env, "run-complete", "v1", "--result", str(result))
    assert helper_json(env, "run-list")[0]["stale"] is False

    created = helper_json(env, "grant-create", "--file", str(write_basis(tmp_path, supersedes=grant)))
    assert created["runs_marked_stale"] == ["v1"]

    run = helper_json(env, "run-list")[0]
    assert run["stale"] is True
    assert run["state"] == "completed", "stale evidence stays inspectable rather than being erased"

    # Close cannot proceed on an active grant that a successor superseded.
    projection = helper_json(env, "show")
    assert projection["status"] == "fail-safe"
    assert any("superseded" in problem for problem in projection["problems"])


# ---------------------------------------------------------------------------
# Current state: atomicity and fail-safe evaluation
# ---------------------------------------------------------------------------


def test_current_state_writes_are_atomic_and_leave_no_debris(
    env: dict[str, str], tmp_path: Path, state_root: Path
) -> None:
    open_change(env, tmp_path)
    for index in range(5):
        helper(env, "transition", "--phase", "verify", "--reason", f"pass {index}")
    assert list(state_root.glob(".current.json.*")) == []
    json.loads((state_root / "current.json").read_text(encoding="utf-8"))


def test_a_bad_payload_never_truncates_an_existing_record(state_root: Path) -> None:
    target = state_root / "current.json"
    aw_state.atomic_write_json(target, {"phase": "implement"})
    original = target.read_bytes()

    class Unserializable:
        pass

    with pytest.raises(TypeError):
        aw_state.atomic_write_json(target, {"phase": Unserializable()})

    assert target.read_bytes() == original
    assert list(state_root.glob(".current.json.*")) == []


def test_no_state_is_reported_as_no_state_not_guessed(env: dict[str, str]) -> None:
    assert helper_json(env, "show")["status"] == "no-state"


def test_missing_authority_fails_safe_into_prepare(env: dict[str, str], tmp_path: Path) -> None:
    open_change(env, tmp_path)
    (Path(env["AW_STATE_ROOT"]) / "grants" / "g1.json").unlink()

    projection = helper_json(env, "show")
    assert projection["status"] == "fail-safe"
    assert (projection["phase"], projection["owner"], projection["condition"]) == (
        "prepare",
        "jacob",
        "exception",
    )
    assert projection["recorded_phase"] == "implement"
    assert any("g1" in problem for problem in projection["problems"])


def test_contradictory_state_fails_safe(env: dict[str, str], tmp_path: Path) -> None:
    open_change(env, tmp_path)
    current = Path(env["AW_STATE_ROOT"]) / "current.json"
    data = json.loads(current.read_text(encoding="utf-8"))
    data["active_grant"] = None  # implement phase with no authority
    current.write_text(json.dumps(data), encoding="utf-8")

    projection = helper_json(env, "show")
    assert projection["status"] == "fail-safe"
    assert any("requires an active grant" in problem for problem in projection["problems"])


def test_unreadable_current_state_fails_safe(env: dict[str, str]) -> None:
    root = Path(env["AW_STATE_ROOT"])
    (root / "current.json").write_text("{not json", encoding="utf-8")
    projection = helper_json(env, "show")
    assert projection["status"] == "fail-safe"


def test_closed_without_an_outcome_fails_safe(env: dict[str, str], tmp_path: Path) -> None:
    open_change(env, tmp_path)
    current = Path(env["AW_STATE_ROOT"]) / "current.json"
    data = json.loads(current.read_text(encoding="utf-8"))
    data["closed"] = True
    current.write_text(json.dumps(data), encoding="utf-8")
    assert helper_json(env, "show")["status"] == "fail-safe"


# ---------------------------------------------------------------------------
# SessionStart context
# ---------------------------------------------------------------------------


def test_sessionstart_is_silent_without_a_change(env: dict[str, str], git_repo: Path) -> None:
    result = run_hook(SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env)
    assert result == {}, "an unrelated repository must not receive this plugin's vocabulary"


def test_sessionstart_reports_an_active_change(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    helper(
        env,
        "transition",
        "--phase",
        "verify",
        "--owner",
        "verification",
        "--active-candidate",
        "c2",
        "--reason",
        "candidate c2 presented as ready",
        "--next",
        "independent verification result",
        "--safe-point",
        "candidate c2 awaiting verification",
    )
    context = run_hook(
        SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env
    )["hookSpecificOutput"]["additionalContext"]

    assert "PHASE      verify" in context
    assert "OWNER      verification" in context
    assert "CONDITION  active" in context
    assert "grant g1" in context
    assert "CANDIDATE  c2" in context
    assert "independent verification result" in context
    assert "candidate c2 awaiting verification" in context
    assert "not chat history" in context


def _completed_run(env: dict[str, str], tmp_path: Path, grant: str) -> None:
    helper(env, "run-create", "--grant", grant, "--candidate", "c1")
    result = tmp_path / "verifier.json"
    result.write_text(
        json.dumps(
            {
                "verdict": "pass",
                "recommendation": "deliver",
                "observations": [
                    {"promise": "exits 0 for valid configuration", "result": "met",
                     "command": "cli --check ok.toml", "evidence": "exit 0"}
                ],
                "representative_outcome": {"answer": "named key and rule",
                                           "answers_the_question": True},
                "route": {"planned": ["reuse validator"],
                          "verifier_derived_actual": ["validator reused"],
                          "material_deviations": []},
                "context": {"new": [], "pre_existing": ["one deprecation warning"],
                            "unclassified": []},
            }
        ),
        encoding="utf-8",
    )
    helper(env, "run-complete", "v1", "--result", str(result))
    helper(env, "transition", "--phase", "verify", "--owner", "jacob",
           "--active-verification-run", "v1", "--active-candidate", "c1",
           "--reason", "candidate presented as ready")


def test_cards_are_rendered_by_the_helper_and_saved_to_disk(
    env: dict[str, str], tmp_path: Path, state_root: Path
) -> None:
    open_change(env, tmp_path)
    out = helper(env, "card", "authorize").stdout

    assert out.startswith("GRANT REQUEST  g1")
    for label in ("QUESTION", "PROMISE", "EXCLUDES", "ROUTE", "STOP BEFORE",
                  "GUARDED", "UNCOVERED", "DELIVERY", "OWNER", "ATTENTION"):
        assert label in out, label

    saved = state_root / "cards" / "001-authorize.txt"
    assert saved.is_file()
    assert saved.read_text(encoding="utf-8").startswith("GRANT REQUEST  g1")

    # Rendering again appends rather than overwriting: the card an operator
    # returns to an hour later must not be clobbered.
    helper(env, "card", "authorize")
    assert (state_root / "cards" / "002-authorize.txt").is_file()


def test_reconcile_card_leads_with_the_frame_and_withholds_the_verdict(
    env: dict[str, str], tmp_path: Path
) -> None:
    grant = open_change(env, tmp_path)
    _completed_run(env, tmp_path, grant)
    out = helper(env, "card", "reconcile").stdout

    question_at = out.index("QUESTION")
    excludes_at = out.index("EXCLUDES")
    evidence_at = out.index("promised / observed")
    assert question_at < excludes_at < evidence_at, (
        "the frame must precede the evidence; an hour after authorization it is "
        "the frame that has gone missing"
    )

    assert "VERIFIER VERDICT AND RECOMMENDATION WITHHELD" in out
    # The verifier's recommendation ("deliver") must not appear anywhere above
    # the operator's own call.
    assert "deliver" not in out.lower().split("respond")[0]
    assert "RESPOND" in out and "THEN STATE" in out


def test_status_language_never_borrows_an_authorization_word(
    env: dict[str, str], tmp_path: Path
) -> None:
    """Tenerife 1977: a status report phrased like a clearance killed 583 people.

    "We are at takeoff" was heard as a takeoff clearance because status
    language and authorization language shared a sentence pattern. The words
    the operator uses to grant — AUTHORIZE, READY — must never appear in a
    line where the system is asserting its own status.
    """
    grant = open_change(env, tmp_path)
    _completed_run(env, tmp_path, grant)

    granting_words = ("AUTHORIZE", "AUTHORIZED", "READY")
    for kind in ("authorize", "ready", "reconcile", "closed", "exception"):
        out = helper(env, "card", kind).stdout
        for line in out.splitlines():
            # The RESPOND line is where the operator's own tokens belong; it is
            # the one place these words are not a status claim.
            if line.startswith("RESPOND") or line.startswith("NOT READY"):
                continue
            for word in granting_words:
                assert word not in line, f"{kind}: status line borrows {word!r}: {line!r}"


def test_card_labels_are_a_closed_vocabulary(env: dict[str, str], tmp_path: Path) -> None:
    """One label, one meaning, one slot — a synonym defeats the whole point."""
    with pytest.raises(AssertionError):
        aw_state._field("GOAL", "a synonym for QUESTION")
    assert "QUESTION" in aw_state.CARD_LABELS
    for synonym in ("GOAL", "INTENT", "SUMMARY", "NOTES", "STATUS"):
        assert synonym not in aw_state.CARD_LABELS, synonym


def test_empty_fields_state_the_finding_rather_than_going_silent(
    env: dict[str, str], tmp_path: Path
) -> None:
    """'No new adverse context' is a finding; an absent line is an open question."""
    grant = open_change(env, tmp_path)
    _completed_run(env, tmp_path, grant)
    out = helper(env, "card", "reconcile").stdout

    assert f"NEW         {aw_state.CLEAN}" in out
    assert f"DEVIATION   {aw_state.CLEAN}" in out
    assert "PRIOR       one deprecation warning" in out


def test_actionable_cards_name_their_response_tokens(
    env: dict[str, str], tmp_path: Path
) -> None:
    grant = open_change(env, tmp_path)
    assert "RESPOND     AUTHORIZE | REVISE | STOP" in helper(env, "card", "authorize").stdout
    _completed_run(env, tmp_path, grant)
    assert "RESPOND     READY | NOT READY | INSPECT" in helper(env, "card", "reconcile").stdout


def test_cards_fit_a_terminal_and_keep_the_label_column_clear(
    env: dict[str, str], tmp_path: Path
) -> None:
    """A card the terminal wraps for you is a card that stops being scannable."""
    grant = open_change(env, tmp_path, operator_question=(
        "When I or an agent types a reference in the form the rules, skills, and "
        "the CLI's own error text all prescribe, does resolve give the right "
        "answer, and is it now impossible to be told coverage is missing when "
        "the reference was merely prefixed?"
    ))
    _completed_run(env, tmp_path, grant)

    for kind in ("authorize", "ready", "reconcile", "closed", "exception"):
        out = helper(env, "card", kind).stdout
        for line in out.splitlines():
            assert len(line) <= aw_state.CARD_WIDTH_DEFAULT, f"{kind}: {line!r}"

    out = helper(env, "card", "authorize").stdout
    wrapped = [ln for ln in out.splitlines() if ln.startswith(" " * 12)]
    assert wrapped, "the long question should have wrapped at all"
    for line in wrapped:
        # Continuation text must never land in the label column, or the labels
        # stop reading as a column.
        assert line[:12].strip() == ""


def test_card_width_follows_the_environment(env: dict[str, str], tmp_path: Path) -> None:
    open_change(env, tmp_path)
    narrow = helper({**env, "AW_CARD_WIDTH": "56"}, "card", "authorize").stdout
    assert max(len(ln) for ln in narrow.splitlines()) <= 56
    # Out-of-range values clamp rather than producing an unreadable card.
    absurd = helper({**env, "AW_CARD_WIDTH": "4"}, "card", "authorize").stdout
    assert max(len(ln) for ln in absurd.splitlines()) <= aw_state.CARD_WIDTH_MIN


def test_cards_never_leak_python_list_syntax(env: dict[str, str], tmp_path: Path) -> None:
    grant = open_change(env, tmp_path)
    _completed_run(env, tmp_path, grant)
    for kind in ("authorize", "ready", "reconcile"):
        out = helper(env, "card", kind).stdout
        assert "['" not in out and "']" not in out, f"{kind} leaked a list repr"


def test_sessionstart_collapses_a_closed_change_to_one_line(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    helper(
        env,
        "transition",
        "--phase",
        "close",
        "--owner",
        "jacob",
        "--outcome",
        "delivered",
        "--reason",
        "delivered as authorized",
        "--clear-attention",
    )
    context = run_hook(
        SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env
    )["hookSpecificOutput"]["additionalContext"]

    assert context.count("\n") == 0, "a closed change must not reprint the full card"
    assert "no active change" in context
    assert "delivered" in context
    assert "PHASE" not in context and "QUESTION" not in context


def test_sessionstart_clips_a_long_operator_question(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    question = (
        "When I or an agent type a reference in the form the rules, skills, and the CLI's own "
        "error text all prescribe, does resolve give the right answer, and is it now impossible "
        "to be told coverage is missing when the reference was merely prefixed?"
    )
    open_change(env, tmp_path, operator_question=question)
    context = run_hook(
        SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env
    )["hookSpecificOutput"]["additionalContext"]

    line = next(ln for ln in context.splitlines() if ln.startswith("QUESTION"))
    assert len(line) <= 155, line
    assert line.endswith("…")
    # The record keeps the whole thing; only the card is clipped.
    assert helper_json(env, "grant-show", "g1")["operator_question"] == question


def test_sessionstart_reports_a_holding_condition_without_asking_for_a_decision(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    helper(
        env,
        "transition",
        "--phase",
        "verify",
        "--owner",
        "verification",
        "--condition",
        "holding",
        "--reason",
        "required test environment is unavailable",
        "--next",
        "environment becomes reachable",
    )
    context = run_hook(
        SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env
    )["hookSpecificOutput"]["additionalContext"]

    assert "CONDITION  holding" in context
    assert "released; no operator action pending" in context
    assert "Exception" not in context


def test_sessionstart_reports_an_exception_and_names_the_pending_decision(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    helper(
        env,
        "transition",
        "--phase",
        "prepare",
        "--owner",
        "jacob",
        "--condition",
        "exception",
        "--attention-kind",
        "exception",
        "--attention-summary",
        "validator does not retain nested key identity",
        "--safe-point",
        "command shell and fixtures preserved",
        "--reason",
        "load-bearing assumption falsified",
    )
    context = run_hook(
        SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env
    )["hookSpecificOutput"]["additionalContext"]

    assert "CONDITION  exception" in context
    assert "exception: validator does not retain nested key identity" in context
    assert "command shell and fixtures preserved" in context


def test_sessionstart_fail_safe_forbids_optimistic_continuation(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    (Path(env["AW_STATE_ROOT"]) / "grants" / "g1.json").unlink()
    context = run_hook(
        SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env
    )["hookSpecificOutput"]["additionalContext"]

    assert "fail-safe" in context
    assert "Do not infer authority from git state, issue status, or chat history." in context
    assert "No implementation, verification, or delivery action may continue." in context


# ---------------------------------------------------------------------------
# PreToolUse guard: authority records
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tool", ["Edit", "Write", "NotebookEdit", "MultiEdit"])
def test_direct_writes_to_a_grant_record_are_denied(
    env: dict[str, str], tmp_path: Path, git_repo: Path, tool: str
) -> None:
    open_change(env, tmp_path)
    target = str(Path(env["AW_STATE_ROOT"]) / "grants" / "g1.json")
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    result = run_hook(
        GUARD_HOOK,
        {
            "hook_event_name": "PreToolUse",
            "tool_name": tool,
            "tool_input": {key: target, "content": "{}"},
            "cwd": str(git_repo),
        },
        env,
    )
    assert decision(result) == "deny"
    assert "supersede" in result["hookSpecificOutput"]["permissionDecisionReason"]


@pytest.mark.parametrize(
    "command",
    [
        "echo forged > {grant}",
        "echo forged >> {grant}",
        "rm {grant}",
        "cp /tmp/other.json {grant}",
        "mv /tmp/other.json {grant}",
        "sed -i '' s/a/b/ {grant}",
        "cat /tmp/other.json | tee {grant}",
        "true && rm {grant}",
    ],
)
def test_shell_mutation_of_a_grant_record_is_denied(
    env: dict[str, str], tmp_path: Path, git_repo: Path, command: str
) -> None:
    open_change(env, tmp_path)
    grant = str(Path(env["AW_STATE_ROOT"]) / "grants" / "g1.json")
    result = run_hook(GUARD_HOOK, bash_payload(command.format(grant=grant), str(git_repo)), env)
    assert decision(result) == "deny", command


def test_reading_a_grant_and_using_the_helper_are_allowed(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    grants = Path(env["AW_STATE_ROOT"]) / "grants"
    for command in (
        f"cat {grants}/g1.json",
        f"grep operator_question {grants}/g1.json",
        f"python3 {HELPER} grant-create --file /tmp/basis.json",
        f"python3 {HELPER} grant-show g1",
    ):
        assert run_hook(GUARD_HOOK, bash_payload(command, str(git_repo)), env) == {}, command


# ---------------------------------------------------------------------------
# PreToolUse guard: delivery
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "command",
    [
        "git push",
        "git push origin main",
        "git push --force-with-lease origin main",
        "git -C /somewhere/else push origin main",
        "git -c user.name=x push",
        "git --git-dir=/tmp/x/.git push",
        "uv run pytest && git push",
        "echo hi; git push origin main",
        "jj git push",
        "jj git push --bookmark main",
        "jj -R /somewhere/else git push",
        "jj --repository /somewhere/else git push",
    ],
)
def test_unauthorized_pushes_are_denied(
    env: dict[str, str], tmp_path: Path, git_repo: Path, command: str
) -> None:
    open_change(env, tmp_path)  # delivery_authorized == ["commit"]
    result = run_hook(GUARD_HOOK, bash_payload(command, str(git_repo)), env)
    assert decision(result) == "deny", command
    reason = result["hookSpecificOutput"]["permissionDecisionReason"]
    assert "delivery authority" in reason
    assert "reversibility" in reason


def test_an_authorized_push_is_allowed(env: dict[str, str], tmp_path: Path, git_repo: Path) -> None:
    open_change(env, tmp_path, delivery_authorized=["commit", "git-push", "jj-git-push"])
    for command in ("git push origin main", "jj git push", "uv run pytest && git push"):
        assert run_hook(GUARD_HOOK, bash_payload(command, str(git_repo)), env) == {}, command


def test_safe_unrelated_commands_are_allowed(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    for command in (
        "uv run pytest -q",
        "git status",
        "git commit -m 'work'",
        "git log --oneline | head -5",
        "ls -la",
        "rg 'push' README.md",
        "echo 'git push is documented here' >> notes.md",
    ):
        assert run_hook(GUARD_HOOK, bash_payload(command, str(git_repo)), env) == {}, command


def test_the_guard_does_not_gate_a_repository_with_no_change(
    env: dict[str, str], git_repo: Path
) -> None:
    assert run_hook(GUARD_HOOK, bash_payload("git push origin main", str(git_repo)), env) == {}


def test_fail_safe_state_denies_delivery(env: dict[str, str], tmp_path: Path, git_repo: Path) -> None:
    open_change(env, tmp_path, delivery_authorized=["commit", "git-push"])
    (Path(env["AW_STATE_ROOT"]) / "grants" / "g1.json").unlink()
    result = run_hook(GUARD_HOOK, bash_payload("git push origin main", str(git_repo)), env)
    assert decision(result) == "deny"


def test_the_guard_fails_open_on_junk_input(env: dict[str, str]) -> None:
    proc = subprocess.run(
        [sys.executable, str(GUARD_HOOK)],
        input="not json at all",
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


# ---------------------------------------------------------------------------
# Verification runs
# ---------------------------------------------------------------------------


def test_terminal_result_survives_delayed_and_duplicate_completion(
    env: dict[str, str], tmp_path: Path
) -> None:
    grant = open_change(env, tmp_path)
    helper(env, "run-create", "--grant", grant, "--candidate", "c1")

    first = tmp_path / "first.json"
    first.write_text(json.dumps({"verdict": "fail", "recommendation": "return to implement"}), encoding="utf-8")
    completed = helper_json(env, "run-complete", "v1", "--result", str(first))
    assert completed["duplicate"] is False
    assert completed["run"]["state"] == "completed"

    # A duplicate notification arrives, carrying a different (later) payload.
    second = tmp_path / "second.json"
    second.write_text(json.dumps({"verdict": "pass", "recommendation": "ship"}), encoding="utf-8")
    duplicate = helper_json(env, "run-complete", "v1", "--result", str(second))
    assert duplicate["duplicate"] is True
    assert duplicate["run"]["result"]["verdict"] == "fail", "the first terminal result wins"

    # A reordered "still running" message cannot regress the record.
    proc = helper(env, "run-state", "v1", "--state", "running", expect=2)
    assert "terminal" in proc.stderr
    assert helper_json(env, "run-list")[0]["state"] == "completed"


def test_a_completed_run_is_resolvable_by_identity_so_no_fallback_is_needed(
    env: dict[str, str], tmp_path: Path
) -> None:
    grant = open_change(env, tmp_path)
    helper(env, "run-create", "--grant", grant, "--candidate", "c1")
    result = tmp_path / "result.json"
    result.write_text(json.dumps({"verdict": "pass"}), encoding="utf-8")
    helper(env, "run-complete", "v1", "--result", str(result))

    helper(
        env,
        "transition",
        "--phase",
        "verify",
        "--owner",
        "verification",
        "--active-verification-run",
        "v1",
        "--reason",
        "candidate presented as ready",
    )
    # No message was delivered; the projection alone establishes completion.
    projection = helper_json(env, "show")
    assert projection["verification_run"]["has_terminal_result"] is True
    assert projection["verification_run"]["state"] == "completed"
    assert len(helper_json(env, "run-list")) == 1, "no fallback run may be created"


def test_the_verifier_verdict_is_withheld_until_a_judgment_is_recorded(
    env: dict[str, str], tmp_path: Path
) -> None:
    grant = open_change(env, tmp_path)
    helper(env, "run-create", "--grant", grant, "--candidate", "c1")
    result = tmp_path / "result.json"
    result.write_text(
        json.dumps(
            {
                "verdict": "pass",
                "recommendation": "deliver",
                "observations": [{"promise": "exits 0", "result": "met", "command": "cli --check"}],
            }
        ),
        encoding="utf-8",
    )
    helper(env, "run-complete", "v1", "--result", str(result))

    evidence = helper_json(env, "run-evidence", "v1")
    assert evidence["verdict_withheld"] is True
    assert "verdict" not in evidence["result"]
    assert "recommendation" not in evidence["result"]
    assert evidence["result"]["observations"][0]["command"] == "cli --check"

    proc = helper(env, "run-reveal", "v1", expect=2)
    assert "withheld until" in proc.stderr

    bare = helper(env, "run-judge", "v1", "--judgment", "ready", "--decisive", "   ", expect=2)
    assert "bare ratification" in bare.stderr

    helper(env, "run-judge", "v1", "--judgment", "ready", "--decisive", "the no-write comparison held")
    revealed = helper_json(env, "run-reveal", "v1")
    assert revealed["verifier_verdict"] == "pass"
    assert revealed["agreement"] is True

    again = helper(env, "run-judge", "v1", "--judgment", "not-ready", "--decisive", "changed my mind", expect=2)
    assert "already records" in again.stderr


def test_disagreement_is_representable(env: dict[str, str], tmp_path: Path) -> None:
    grant = open_change(env, tmp_path)
    helper(env, "run-create", "--grant", grant, "--candidate", "c1")
    result = tmp_path / "result.json"
    result.write_text(json.dumps({"verdict": "pass", "recommendation": "deliver"}), encoding="utf-8")
    helper(env, "run-complete", "v1", "--result", str(result))
    helper(env, "run-judge", "v1", "--judgment", "not-ready", "--decisive", "the nested case never named a key")

    revealed = helper_json(env, "run-reveal", "v1")
    assert revealed["agreement"] is False


# ---------------------------------------------------------------------------
# Tracker projection
# ---------------------------------------------------------------------------


def test_a_failed_tracker_projection_leaves_local_state_valid_and_marks_it_stale(
    env: dict[str, str], tmp_path: Path
) -> None:
    open_change(env, tmp_path)
    helper(
        env,
        "issue-set",
        "--host",
        "linear",
        "--identity",
        "TEAM-123",
        "--url",
        "https://linear.app/x/issue/TEAM-123",
        "--status",
        "current",
    )
    assert helper_json(env, "show")["issue"]["projection_status"] == "current"

    helper(
        env,
        "issue-set",
        "--host",
        "linear",
        "--identity",
        "TEAM-123",
        "--status",
        "stale",
        "--stale-reason",
        "outcome comment failed: MCP server unreachable",
    )

    projection = helper_json(env, "show")
    assert projection["status"] == "ok", "a failed projection must not corrupt local authority"
    assert projection["issue"]["projection_status"] == "stale"
    assert "unreachable" in projection["issue"]["stale_reason"]
    assert projection["active_grant"] == "g1"
    assert projection["phase"] == "implement"


def test_tracker_identity_appears_in_the_session_card_as_a_projection(
    env: dict[str, str], tmp_path: Path, git_repo: Path
) -> None:
    open_change(env, tmp_path)
    helper(env, "issue-set", "--host", "fibery", "--identity", "task-34", "--status", "current")
    context = run_hook(
        SESSION_START_HOOK, {"hook_event_name": "SessionStart", "cwd": str(git_repo)}, env
    )["hookSpecificOutput"]["additionalContext"]
    assert "fibery task-34" in context
    assert "local state stays canonical" in context


# ---------------------------------------------------------------------------
# Checkpoint postconditions — observed from real VCS state
# ---------------------------------------------------------------------------


def test_a_git_checkpoint_is_observed_not_accepted(env: dict[str, str], git_repo: Path) -> None:
    ok = helper_json(env, "--repo", str(git_repo), "checkpoint-verify")
    assert ok["checkpoint"] is True
    assert ok["vcs"] == "git"

    (git_repo / "README.md").write_text("changed\n", encoding="utf-8")
    proc = helper(env, "--repo", str(git_repo), "checkpoint-verify", expect=1)
    observed = json.loads(proc.stdout)
    assert observed["checkpoint"] is False
    assert "uncommitted" in observed["reason"]


def test_jj_checkpoint_requires_an_advanced_working_copy(env: dict[str, str], tmp_path: Path) -> None:
    if subprocess.run(["which", "jj"], capture_output=True, check=False).returncode != 0:
        pytest.skip("jj is not installed")

    repo = tmp_path / "jjrepo"
    repo.mkdir()
    vcs_env = _isolated_vcs_env(tmp_path)
    run = lambda *args: subprocess.run(  # noqa: E731
        args, cwd=repo, capture_output=True, text=True, check=True, env=vcs_env
    )
    run("jj", "git", "init")
    (repo / "tests.py").write_text("def test_x():\n    assert False\n", encoding="utf-8")

    # `jj describe` alone does not advance the working-copy change: this is the
    # exact shape of a delegate reporting a checkpoint that does not exist.
    run("jj", "describe", "-m", "red phase")
    described = helper(env, "--repo", str(repo), "checkpoint-verify", expect=1)
    assert json.loads(described.stdout)["checkpoint"] is False

    run("jj", "new")
    advanced = helper_json(env, "--repo", str(repo), "checkpoint-verify")
    assert advanced["checkpoint"] is True


# ---------------------------------------------------------------------------
# State root resolution
# ---------------------------------------------------------------------------


def test_state_root_is_keyed_by_repository_and_stays_out_of_the_worktree(
    git_repo: Path, tmp_path: Path
) -> None:
    clean = {k: v for k, v in os.environ.items() if k != "AW_STATE_ROOT"}
    clean["CLAUDE_CONFIG_DIR"] = str(tmp_path / "claude-home")

    from_root = subprocess.run(
        [sys.executable, str(HELPER), "state-root"],
        cwd=git_repo,
        capture_output=True,
        text=True,
        env=clean,
        check=True,
    ).stdout.strip()

    nested = git_repo / "a" / "b"
    nested.mkdir(parents=True)
    from_nested = subprocess.run(
        [sys.executable, str(HELPER), "state-root"],
        cwd=nested,
        capture_output=True,
        text=True,
        env=clean,
        check=True,
    ).stdout.strip()

    assert from_root == from_nested
    assert str(git_repo) not in from_root, "state must not live in the target repository"
    assert from_root.startswith(str(tmp_path / "claude-home"))

#!/usr/bin/env python3
"""Local-only Linear acceptance connector. No network or real tracker access.

Run as a Codex stdio MCP server with --root <fresh disposable directory>.
Logs every semantic operation; deliberately drops a label for title
``Fixture: silent drop`` to test post-write verification without a real write.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def operate(name, args, root):
    with (root / "calls.jsonl").open("a") as log:
        log.write(json.dumps({"operation": name, "arguments": args}) + "\n")
    if name == "list_teams":
        return {"teams": [{"id": "fixture-team", "name": "Fixture", "key": "FIX"}]}
    if name == "list_projects":
        return {"projects": [{"id": "fixture-project", "name": "Fixture active", "state": "started"}]}
    if name == "list_issue_labels":
        return {"labels": [{"id": "label-" + n, "name": n} for n in ("backend", "Feature")]}
    if name == "list_issue_statuses":
        return {"statuses": [{"id": "state-" + n, "name": n} for n in ("Backlog", "Todo", "Done")]}
    if name in ("list_comments", "list_milestones", "list_cycles", "list_issues"):
        return {name[5:]: []}
    state_path = root / "state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if name == "save_issue":
        issue_id = args.get("id", "FIX-" + str(len(state) + 1))
        issue = dict(state.get(issue_id, {}), **args)
        issue.update(id=issue_id, identifier=issue_id, url="https://fixture.invalid/" + issue_id)
        if issue.get("title") == "Fixture: silent drop":
            issue["labels"] = ["Feature"]
        state[issue_id] = issue
        state_path.write_text(json.dumps(state, indent=2) + "\n")
        return issue
    if name == "get_issue":
        if args["id"] == "FIX-NESTED":
            return {"id": "FIX-NESTED", "title": "Fixture nested parent", "parentId": "FIX-PARENT"}
        return state.get(args["id"], {"id": args["id"], "title": "Fixture parent", "parentId": None})
    if name == "save_comment":
        return {"id": "fixture-comment", **args}
    raise ValueError("unknown mock operation: " + name)


def tools():
    text = {"type": "string"}
    fields = {n: text for n in ("id", "team", "teamId", "project", "title", "state", "description", "assignee", "milestone", "parentId", "issueId", "body", "type", "cycle")}
    fields.update(priority={"type": "integer"}, labels={"type": "array", "items": text})
    names = ("list_teams", "list_projects", "list_issue_labels", "list_issue_statuses", "list_milestones", "list_cycles", "list_comments", "list_issues", "save_issue", "get_issue", "save_comment")
    return [{"name": n, "description": "LOCAL MOCK ONLY: Linear " + n,
             "inputSchema": {"type": "object", "properties": fields, "additionalProperties": True},
             "annotations": {"readOnlyHint": n not in ("save_issue", "save_comment"), "openWorldHint": False}}
            for n in names]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if not str(root).startswith("/private/tmp/linear-codex-"):
        parser.error("mock root must be inside /private/tmp/linear-codex-* fixture")
    root.mkdir(parents=True, exist_ok=True)
    for line in sys.stdin:
        request = json.loads(line)
        method = request.get("method")
        if "id" not in request:
            continue
        try:
            if method == "initialize":
                result = {"protocolVersion": request["params"]["protocolVersion"], "capabilities": {"tools": {}}, "serverInfo": {"name": "linear-fixture", "version": "1.0"}}
            elif method == "ping":
                result = {}
            elif method == "tools/list":
                result = {"tools": tools()}
            elif method == "tools/call":
                params = request["params"]
                data = operate(params["name"], params.get("arguments", {}), root)
                result = {"content": [{"type": "text", "text": json.dumps(data)}]}
            else:
                raise ValueError("unsupported method: " + str(method))
            response = {"jsonrpc": "2.0", "id": request["id"], "result": result}
        except (ValueError, KeyError) as exc:
            response = {"jsonrpc": "2.0", "id": request["id"], "error": {"code": -32602, "message": str(exc)}}
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    main()

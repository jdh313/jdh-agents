# Fetching & Parsing Atlantis Plans (v0)

v0 has **no plan JSON**. The structured `terraform show -json` / `$SHOWFILE`
artifact is a v1 capability (S3 upload from an Atlantis run step). In v0 the
only plan artifact is the **text Atlantis posts as PR comments**. Reason from
that text plus the HCL diff — do not try to produce plan JSON locally (running
`terraform plan` against a teammate's branch is out of scope and would need
credentials).

---

## 1. Fetch PR metadata and diff

```bash
# Accepts a number (42) or a full URL. Strip to the number for gh.
gh pr view "$PR" --json number,title,body,headRefOid,headRefName,baseRefName,url,state,commits
gh pr diff "$PR"            # full unified diff
gh pr diff "$PR" --name-only   # changed paths — filter to *.tf / *.hcl / *.tfvars
```

Capture from `--json`:
- `headRefOid` — the **current head commit SHA**. Load-bearing for the staleness gate.
- `commits[].oid` / `commits[].committedDate` — the latest entry's `committedDate`
  is the freshness bar plan comments must clear.
- `title` + `body` — intent source for the intent-vs-resources check.

## 2. Fetch Atlantis comments

PR comments are issue comments. Pull them with the API (newest meaningful
fields are `user.login`, `body`, `created_at`):

```bash
OWNER_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)   # owner/repo of the CWD's repo
gh api "repos/$OWNER_REPO/issues/$PR/comments" --paginate \
  --jq '.[] | {login: .user.login, created_at, len: (.body|length), body}'
```

### Identify the Atlantis author
The bot login is install-specific (`atlantis`, `atlantis[bot]`, or a custom
GitHub App name). Do **not** hardcode it. Detect a comment as an Atlantis plan
by body markers, in priority order:
- `Ran Plan for dir:` / `Ran Plan for project:` (per-project plan comment)
- `Plan: N to add, M to change, K to destroy` (the plan summary line)
- A `terraform plan` fenced block containing `# ... will be created/destroyed/updated`
- A `<details>` block wrapping `Show Output`

If the author is ambiguous (multiple bots, custom app name), surface the
candidate logins to the user and confirm which is Atlantis before parsing.

## 3. Group multi-comment plans

Atlantis posts **one plan comment per project** (dir + workspace). A PR
touching N projects has N plan comments, plus an "Ran Plan for N projects"
summary comment. Group by the `dir:`/`workspace:` header so each project's plan
is reviewed as a unit. Note any changed-HCL directory that has **no**
corresponding plan comment — that is itself a finding (a project Atlantis
didn't plan, or a plan that never posted).

## 4. Detect truncation — never silently review a partial plan

GitHub caps a comment body at 65,536 characters. Atlantis truncates large plans
rather than failing. Treat a plan comment as **truncated** if any of:
- Body length is at/near 65,536 chars.
- Explicit markers: `Plan output is too large`, `output has been truncated`,
  `... (truncated)`, or a link to an external gist / `Show Output` that points
  off-comment.
- A `<details>` block whose summary promises output the body doesn't contain.

On truncation: **flag it loudly in the report and mark the affected project's
architecture verdict as `unverifiable`.** Review only what is fully present;
state plainly which projects were partial. Do not infer the missing actions.
(Removing this limitation is the entire motivation for v1's `$SHOWFILE`.)

## 5. What to extract from the plan text

Per project, pull from the plan body:
- The summary line: `Plan: A to add, C to change, D to destroy`.
- Each resource action header. Terraform encodes the action as a sigil:

| Sigil | Action | Watch for |
|-------|--------|-----------|
| `+`   | create | new public surfaces, new IAM |
| `~`   | update in place | usually safe |
| `-`   | destroy | data loss on stateful resources |
| `-/+` | **destroy and recreate (replace)** | the highest-signal hazard |
| `<=`  | read (data source) | benign |

- For each `-/+`, capture the `# forces replacement` annotations Terraform
  prints next to the attributes that triggered the replace — that names the
  exact cause.

Plain-text parsing is lossy (no `replace_paths`, no typed values). When the
text is ambiguous about whether a replace hits a stateful resource, say so and
downgrade confidence rather than guessing.

## 6. Resolve the local checkout

The skill runs from a local clone. Confirm the checkout is on the PR branch (or
fetch it) so scanners and HCL reads match the diff under review:

```bash
gh pr checkout "$PR"   # offer this; do not force-switch a dirty tree without asking
```

If the working tree is dirty or on another branch, ask before switching.
Scanners (next phase) read the on-disk HCL, so the checkout must match `headRefOid`.

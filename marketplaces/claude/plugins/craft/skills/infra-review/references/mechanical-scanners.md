# Mechanical Scanners (v0)

All scanners run **credential-free against the local HCL checkout**. None need
a planfile or AWS access — they lint source. Detect what's installed, run only
those, **report which were skipped** so the user knows the mechanical pass is
partial. Prefer JSON output and triage it — never paste raw scanner output into
the report.

## Detection

```bash
for t in tflint checkov trivy infracost; do
  command -v "$t" >/dev/null 2>&1 && echo "$t: present" || echo "$t: SKIPPED (not installed)"
done
```

Scope every scanner to the changed directories (from `gh pr diff --name-only`,
the dirs containing changed `*.tf`), not the whole repo — keeps signal on the
diff under review.

## tflint — Terraform linter

```bash
tflint --chdir "$DIR" --format json
```

- The AWS ruleset is a plugin: it runs only if a `.tflint.hcl` declares it and
  `tflint --init` has installed it. If the repo has no AWS ruleset configured,
  core rules still run — note in the report that AWS-specific tflint rules were
  not active.
- Triage `issues[]`: `rule.name`, `message`, `range.filename`+`range.start.line`,
  `rule.severity`.

## checkov — policy/security scanner

```bash
checkov -d "$DIR" --output json --compact --quiet
```

- Triage `results.failed_checks[]`: `check_id`, `check_name`, `severity`,
  `file_path`, `file_line_range`, `resource`.
- High volume by default. Keep only failures on **resources the PR changes**
  (cross-ref the changed resource addresses from the diff/plan); drop findings
  on untouched files.

## trivy — config scanner (absorbed tfsec)

Use trivy **or** checkov, not both unless they disagree — they overlap heavily.
Prefer whichever is installed; if both, run checkov and use trivy only to
corroborate high-severity hits.

```bash
trivy config "$DIR" --format json --severity HIGH,CRITICAL
```

- Triage `Results[].Misconfigurations[]`: `ID`, `Title`, `Severity`,
  `CauseMetadata.Resource`, `CauseMetadata.StartLine`.

## infracost — cost delta (optional, needs API key)

Only if an API key is configured (`INFRACOST_API_KEY` env var, or
`infracost configure get api_key` returns a value). If absent, skip and report
"cost delta not computed (no infracost API key)".

```bash
infracost breakdown --path "$DIR" --format json
# If a baseline can be produced cheaply, infracost diff is richer; breakdown is the v0 floor.
```

- Surface the **monthly delta** and any single resource that dominates the
  change. Feeds the architecture pass's "cost shape" dimension — not a
  standalone gate.

## Triage discipline

1. **Dedupe** across scanners — the same `0.0.0.0/0` ingress will fire in tflint,
   checkov, and trivy. Report it once, note which scanners flagged it.
2. **Filter to the diff** — a finding on a file the PR doesn't touch is pre-existing
   noise. Either drop it or park it in a clearly-labeled "pre-existing, not from
   this PR" subsection. Never let pre-existing findings inflate the PR's risk.
3. **Severity-rank** — lead with CRITICAL/HIGH. Collapse LOW/INFO into a count.
4. **Map to resource + line** — every kept finding cites `file:line` and the
   resource address so the user can post it as an inline comment verbatim.
5. **Scanner findings are mechanical-tier**, not design concerns — they go in
   the report's second tier. A scanner finding that implies an architectural
   problem (e.g. world-open ingress to a data store) gets *escalated* into the
   design tier with that reasoning made explicit.

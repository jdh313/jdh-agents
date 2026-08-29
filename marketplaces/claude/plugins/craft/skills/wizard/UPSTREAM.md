# Upstream divergences — wizard

_Upstream: `mattpocock/skills` · `skills/engineering/wizard` · ledger current as of `reviewed_sha: 321658273cb1`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (intake 2026-08-29) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

`template.sh` is byte-identical to upstream at `321658273cb1` (`shasum c7e7454cb8ce3c4b5ff744c2119d4a431ad41597`). The four-step process, its done-criteria, the helper-usage bar, and the "never hand-edit the library" rule track upstream. The divergences are below.

| Kind | What | Why |
|------|------|-----|
| added | A `## Secrets` section: never echo a captured value, never route a secret through the conversation, no literal credential in the wizard's source, and check that the `.env` it writes is gitignored before committing it. Upstream has no equivalent section. | This ecosystem's standing safety rule is that secrets are never printed and never asked for in the transcript; a credential-capture wizard is the highest-risk artifact this plugin generates. Mirrors the `## Redact` section `craft:diagnose` carries for the same reason. Additive only — it constrains authoring, changes no upstream step. |
| changed | Frontmatter `description` expanded with explicit trigger phrases ("write me a wizard", "walk me through this setup", "script the manual setup steps") and the attribution clause. Upstream's ends at "Don't invoke this for steps the agent can perform itself." | Model-invocation tuning for this marketplace, where skills are discovered by description match. The negative trigger is kept verbatim in substance. Upstream's wizard carries no `disable-model-invocation`, so the **invocation policy is unchanged** — both sides are model-invocable. |
| added | `allowed-tools` frontmatter (`Read`/`Grep`/`Glob`/`Write`/`Edit` plus `Bash(bash -n *)`, `Bash(shellcheck *)`, `Bash(chmod +x *)`) | Upstream declares none. Pre-approves exactly the step-4 verification commands the skill runs inline, so authoring a wizard doesn't stall on three permission prompts. Pre-approval, not restriction — see this repo's CLAUDE.md on skill `allowed-tools` semantics. |
| changed | House punctuation restored: em-dashes where upstream uses colons or commas (e.g. "that consistency is the point — never hand-edit it", "which variable it fills — e.g. …"). Upstream deliberately removed every em-dash repo-wide at `321658273cb1`. | This marketplace's house style uses em-dashes; upstream's sweep was a stylistic choice for its own repo, not a behavioral change. Wording is otherwise upstream's. |
| dropped | `agents/openai.yaml` (Codex interface sidecar: display name + short description) | Codex manifests here are generated from `plugins/craft/PACKAGE.yaml` by `marketplace sync`; a hand-written sidecar in the skill directory would be ignored, and would drift. No behavior lost. |

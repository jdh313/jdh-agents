# Upstream divergences — wait-what

_Upstream: `mattpocock/skills` · `skills/productivity/wait-what` · ledger current as of `reviewed_sha: 5c89081d4bbe`_

Intentional divergences from upstream. Reviewed via `skillsmith:upstream-review` (intake 2026-08-29) — do not re-flag these as findings. Read by `upstream-review` only; never referenced from `SKILL.md`.

The skill is one paragraph and it is kept: the re-pitch request, the ASD-STE100 Simplified Technical English constraint, and the `CONTEXT.md` / `CONTEXT-MAP.md` vocabulary lookup are upstream's, verbatim in substance. The body stays written in the user's voice, as upstream wrote it.

`reviewed_sha` is `5c89081d4bbe` rather than the repo HEAD `321658273cb1`: a later commit touching this path re-quoted the description scalar after the em-dash sweep left an unquoted colon in it.

| Kind | What | Why |
|------|------|-----|
| changed | Frontmatter `description` rewritten from upstream's `"Stop. That last message did not land: re-pitch it."` to a longer form naming the constraints (context, Simplified Technical English, repo vocabulary) and the trigger phrases, plus the attribution clause. | The description is the discovery surface in this marketplace, and it is what the user sees in the skill picker for a user-invoked skill. Upstream's colon-quoting workaround is moot here since the rewrite carries no colon-space. |
| kept-deliberately | `disable-model-invocation: true`, matching upstream. | Recorded because the invocation policy was adjudicated at intake rather than inherited by default: an auto-firing "that message didn't land" would be the model volunteering that the user is confused, which is noise at best. Both sides land on user-invoked, so this is agreement, not divergence. |
| dropped | `agents/openai.yaml` (Codex interface sidecar: display name, short description, and `policy.allow_implicit_invocation: false`) | Codex manifests here are generated from `plugins/craft/PACKAGE.yaml` by `marketplace sync`; a hand-written sidecar would be ignored and would drift. The invocation policy it encoded is carried by `disable-model-invocation` in the frontmatter, which the compiler translates. |

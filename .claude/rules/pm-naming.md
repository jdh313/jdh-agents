---
description: Reserved skill name in the pm plugin — don't reuse `wayfinder` for a local identity.
paths:
  - "plugins/pm/**"
  - "marketplaces/*/plugins/pm/**"
---

# Reserved name in `pm`: `wayfinder`

**Don't name a skill, agent, command, or label `wayfinder`.** The name conflicts
with an unrelated project, so it resolves to the wrong thing in the reader's head
before they ever reach the description. The skill that would have carried it is
`pm:chart`.

This applies to the **local identity only**. Where upstream's own skill is
*named*, `wayfinder` is correct and must stay:

- `plugins/pm/skills/chart/SKILL.md` — the `upstream:` block's `path:`
- `plugins/pm/skills/chart/UPSTREAM.md` — every row describing what upstream does
- `THIRD-PARTY-NOTICES.md` — the attribution row
- `plugins/spec-flow/references/contract-template.md` — the fog-of-war credit

Renaming those breaks the provenance link, and in the attribution row it breaks a
license notice. See "Renaming an adapted skill" in the root `CLAUDE.md` for why a
bulk find-and-replace across those files is the hazard.

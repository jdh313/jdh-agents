## What changed, and why

<!-- One or two sentences. Link the issue if there is one. -->

## Verification

```
scripts/privacy-scan.sh
scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

- [ ] Both pass locally.
- [ ] If I changed a plugin, I bumped its `PACKAGE.yaml` version (Codex caches by version).
- [ ] If I changed anything under `plugins/`, the regenerated `marketplaces/` output is in this PR.
- [ ] I did not hand-edit anything under `marketplaces/` or `.claude-plugin/`.

## Risk and rollback

<!-- What breaks if this is wrong, and how to undo it. "Docs only" is a complete answer. -->

# Contributing

Thanks for looking. Read this first — the shape of this project determines what
kind of contribution is likely to land.

## What this repository is

`jdh-agents` is one person's working set of Claude Code and Codex plugins,
published so that other people can install it. It is a **personal marketplace**,
not a community catalog. The plugins encode one maintainer's workflow opinions,
and several of them assume a specific local environment (an Obsidian vault, a
Linear workspace, particular MCP servers) that is documented but not optional.

That framing sets expectations honestly:

| Contribution | Reception |
|---|---|
| Bug report with a reproduction | Welcome — the most useful thing you can file |
| Fix for a bug in an existing plugin | Welcome; open an issue first if the fix is more than a few lines |
| Documentation correction | Welcome, no issue needed |
| Behavioral change to an existing plugin | Discuss in an issue first; these encode deliberate workflow opinions |
| A brand-new plugin | Unlikely to be merged — fork instead, or publish your own marketplace |

If you want a plugin from here with different behavior, forking is a first-class
answer, not a consolation prize. The catalog is small and the licence is
permissive.

## Reporting a bug

Open an issue using the **Plugin bug** template. Three things make a report
actionable:

1. **Which plugin and which skill/agent/command.** `librarian:vault-reader`,
   not "the Obsidian thing".
2. **Which runtime.** Claude Code and Codex resolve plugins completely
   differently, and a bug in one frequently does not exist in the other.
3. **Whether you re-installed after the last change.** See the install trap
   below — it accounts for a real share of "this is stale" reports.

Security issues do **not** go in the issue tracker. See
[`SECURITY.md`](SECURITY.md).

### The install trap, before you file "my copy is stale"

The two runtimes disagree about whether a local checkout is live, and they
disagree in opposite directions.

- **Claude Code resolves out of the directory you registered.** If you added
  `<clone>/marketplaces/claude`, an edit there — including one produced by a
  `sync` you ran — is immediately live in every Claude session on the machine.
- **Codex copies into a version-keyed cache** at
  `~/.codex/plugins/cache/jdh-agents/<plugin>/<version>/`. The working tree is
  *not* live, and because the cache key is the version, an unchanged version
  number means it is never invalidated. `codex plugin list` will print the
  current marketplace path while serving months-old bytes. Re-run
  `codex plugin add <name>@jdh-agents` after any change you expect Codex to see.

So a smoke test that passes under Claude proves nothing about Codex: Claude read
your edit and Codex read its cache.

## Development setup

Everything runs from a plain clone. There is nothing to install: both the
compiler and the secret scanner are pinned binaries that fetch and verify
themselves on first use.

```bash
git clone https://github.com/jdh313/jdh-agents
cd jdh-agents
scripts/tests/test_privacy_gate.sh   # proves the gate is not silently inert
scripts/privacy-scan.sh
scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

Install the privacy pre-push hook once per clone — it is the gate that keeps
machine paths and secret-shaped strings out of a public repository:

```bash
prek install --hook-type pre-push
```

`prek` is a Rust reimplementation of the pre-commit framework
([j178/prek](https://github.com/j178/prek)); the hook runs
`scripts/privacy-scan.sh` over the repository's committed history.

Note that `jj git push` does **not** run git hooks -- jj has no native hook
support -- so in a jj workflow the hook only fires if you push through a wrapper
that invokes prek explicitly. CI runs the same gate regardless.

### Regenerating `marketplaces/` (needs the compiler)

```bash
scripts/agentforge.sh compile MARKETPLACE.yaml --out marketplaces
```

[`scripts/agentforge.sh`](scripts/agentforge.sh) holds the pin: a release
version plus a per-platform sha256 map taken from that release's own
`SHA256SUMS`. It downloads the matching binary on first use, verifies the hash
before executing a single byte, and caches it under `.cache/agentforge/<version>/`
(gitignored). The hash is re-verified on every run, so a corrupted or tampered
cache is replaced rather than trusted. CI runs this same script — there is no
separate CI pin.

To bump the compiler: change `AGENTFORGE_VERSION`, replace the hash map from the
new release's `SHA256SUMS`, re-run compile, and commit the regenerated tree.

**Do not run a bare `agentforge` off your `PATH`.** It typically symlinks into a
working checkout that tracks whatever branch is being developed, and it has
rejected canonical keys the pinned release accepts. When that happens the
failure looks like a bug in your change, and is not. Two escape hatches exist
for working *on* AgentForge — `AGENTFORGE_BIN` names an arbitrary executable and
skips verification, `AGENTFORGE_PROJECT` runs a source checkout via `bun` and
announces itself every time — and neither is the merge gate. If a result
surprises you, re-run with both unset.

## Generated output is not editable

```
plugins/       <- authoring source. Edit here.
marketplaces/  <- compiler output. Never edit here.
.claude-plugin/marketplace.json  <- compiler output (the root manifest).
```

`agentforge compile` republishes the whole `marketplaces/` tree by rename and
prunes every stale file. An edit made there is discarded without warning, and
`agentforge check` will fail on it in CI. If you need different output, change
`MARKETPLACE.yaml` or the relevant `plugins/<name>/PACKAGE.yaml` and recompile.

One compile per batch. It regenerates every publication, so parallel work must
collect its changes first and compile once.

## Version bumping

Bump the version in `plugins/<name>/PACKAGE.yaml` in the same commit as any
change to that plugin's behavior. Codex's cache key is the version, so skipping
the bump means Codex users never receive the change.

| Change | Bump | Example |
|---|---|---|
| New feature or skill | Minor | 0.1.0 → 0.2.0 |
| Bug fix | Patch | 0.1.0 → 0.1.1 |
| Breaking change | Major | 0.1.0 → 1.0.0 |

Then re-run `compile` so the compiled manifests carry the new version.

## Before you open a pull request

```bash
scripts/tests/test_privacy_gate.sh
scripts/privacy-scan.sh
scripts/agentforge.sh check MARKETPLACE.yaml --out marketplaces --claude-native
```

All three must pass. CI re-runs exactly these against the pinned binaries; a
clean local run is the merge gate.

Commit messages follow `type[scope]: subject (vX.Y.Z)`, e.g.
`feat[librarian]: vault-reader handles empty folders (v0.4.0)`. The version
suffix is mandatory on any commit that changes a plugin and tracks that
plugin's own `PACKAGE.yaml` version.

Keep pull requests single-concern. If you touched `plugins/` and re-synced,
commit the regenerated `marketplaces/` output in the same pull request — source
and generated tree must land together or the drift check fails.

## Licence

Contributions are accepted under [Apache-2.0](LICENSE), the repository's
licence. Some skills derive from MIT-licensed upstreams; if you are modifying
one, keep its `upstream:` frontmatter and add a line to that plugin's
`UPSTREAM.md`. See [`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md).

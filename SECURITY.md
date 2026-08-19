# Security policy

## Reporting a vulnerability

**Do not open a public issue for a security problem.**

Use GitHub's private vulnerability reporting:
[**Report a vulnerability**](https://github.com/jdh313/jdh-agents/security/advisories/new)
(repository → Security → Advisories). That creates a private thread visible only
to you and the maintainer.

Include what you would want in any bug report — which plugin, which runtime,
which version — plus what an attacker gains and what they need to already have
in order to try.

This is a personal project with one maintainer and no service-level agreement.
Expect an acknowledgement within about a week. If a report warrants a fix, the
fix and an advisory land together.

## What is supported

Only the current `main` branch. There are no maintained release branches and no
backports; upgrade by re-adding the marketplace or re-running
`codex plugin add <name>@jdh-agents`.

## Threat model — read this before installing

Plugins here are **instructions and scripts that your coding agent executes with
your permissions**. They are not sandboxed, and installing a marketplace is
closer to `curl | sh` than to installing a browser extension. The security
boundary is the agent's own permission system, not anything in this repository.

Concretely, an installed plugin can:

- Put instructions into your agent's context that shape what it does, including
  what files it reads and what commands it proposes.
- Ship **hooks that run automatically**, without a prompt, on session or tool
  events. Three plugins do: `attention-workflow`, `commit`, and `langfuse`.
- Ship scripts that a skill invokes through `Bash`, subject to your permission
  settings.
- Reach whatever your agent can reach — your filesystem, your MCP servers, your
  connected integrations.

Two consequences worth stating plainly:

- **Read before you install.** Everything is plain text in `plugins/`. The
  hooks are short; read those first. `marketplaces/` is compiled output of the
  same content.
- **`langfuse` exports telemetry.** It is an observability plugin: it sends
  conversation traces to the Langfuse instance you configure. That is its
  purpose, not a defect — but it means installing it routes conversation content
  somewhere. Do not install it without deciding where that is.

Several plugins are built to touch private data (an Obsidian vault, a Linear
workspace) by design. Grant them access deliberately.

## In scope

- A plugin in this repository that induces an agent to take a destructive or
  exfiltrating action outside what its documentation describes.
- Credentials, tokens, or private paths committed to this repository. The
  `marketplace scan` privacy gate is meant to prevent this; a leak that slipped
  past it is a finding about the gate as well.
- A hook or script here that escalates beyond the permission the user granted.
- Supply-chain problems in the compiled `marketplaces/` tree — output that does
  not correspond to the committed source in `plugins/`.
- A dependency of the marketplace tooling with a known exploitable vulnerability
  reachable from how this repository uses it.

## Out of scope

- Claude Code, Codex, or the Claude API themselves. Report those to Anthropic
  ([anthropic.com/responsible-disclosure](https://www.anthropic.com/responsible-disclosure))
  or OpenAI respectively.
- The general fact that an agent can run commands, or that a skill can instruct
  it to. That is the product working as designed; see the threat model above.
- Third-party MCP servers a plugin expects. Report to that server's maintainer.
- Vulnerabilities that require an attacker who can already write to your
  filesystem or to this repository.
- Findings against a fork, or against `jdh313/shared-claude-plugins`, a
  superseded export of a subset of this catalog that no longer receives
  updates.

## What the privacy gate does and does not cover

`uv run marketplace scan` (`scripts/marketplace/privacy.py`) runs on every push
via a `prek` pre-push hook and inside `marketplace check`. It hard-fails on
absolute machine-home paths and secret-shaped assignments, and warns on a few
softer signals.

It scans the **working tree, not git history** — it stops a leak from shipping,
it does not find one that was introduced and later reverted. And its coverage is
necessarily pattern-based: a person's name, an employer, or an internal slug are
not mechanically detectable. Nothing in it replaces reading a diff.

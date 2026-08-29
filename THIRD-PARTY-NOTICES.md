# Third-party notices

This repository is licensed under Apache-2.0 (see [`LICENSE`](LICENSE)). Portions
of it are derived from third-party work under different terms, reproduced below
as those licenses require.

## mattpocock/skills (MIT)

Several skills in this marketplace are adaptations of skills from
[`mattpocock/skills`](https://github.com/mattpocock/skills). Each adapted skill
carries `upstream:` provenance in its frontmatter and an `UPSTREAM.md` ledger
recording intentional divergences from the source.

Derived skills, by plugin:

| Plugin | Skill | Upstream path | Reviewed at |
|---|---|---|---|
| `craft` | `CODEBASE-DESIGN.md` (plugin-root reference, formerly the `codebase-design` skill) | `skills/engineering/codebase-design` | `697d4ce9742d` |
| `craft` | `diagnose` | `skills/engineering/diagnosing-bugs` | `321658273cb1` |
| `craft` | `domain-modeling` | `skills/engineering/domain-modeling` | `321658273cb1` |
| `craft` | `grill` | `skills/productivity/grilling` | `85f83d3fde1d` |
| `craft` | `grill-with-docs` | `skills/engineering/grill-with-docs` | `447ca7087202` |
| `craft` | `improve-codebase-architecture` | `skills/engineering/improve-codebase-architecture` | `321658273cb1` |
| `craft` | `prototype` | `skills/engineering/prototype` | `321658273cb1` |
| `craft` | `resolve-conflicts` | `skills/engineering/resolving-merge-conflicts` | `321658273cb1` |
| `craft` | `tdd` | `skills/engineering/tdd` | `321658273cb1` |
| `craft` | `wait-what` | `skills/productivity/wait-what` | `5c89081d4bbe` |
| `craft` | `wizard` | `skills/engineering/wizard` | `321658273cb1` |
| `craft` | `zoom-out` | `skills/engineering/zoom-out` | `7afa86d3a5dd` |
| `pm` | `breakdown` | `skills/engineering/to-tickets` | `321658273cb1` |
| `pm` | `to-questionnaire` | `skills/productivity/to-questionnaire` | `321658273cb1` |
| `pm` | `chart` (renamed from upstream's `wayfinder`) | `skills/engineering/wayfinder` | `321658273cb1` |
| `skillsmith` | `writing-for-agents` | `skills/productivity/writing-for-agents` | `321658273cb1` |
| `teach` | `teach` | `skills/productivity/teach` | `321658273cb1` |

Additionally, and separately from the `pm:chart` port above, the
`Not yet specified` section of
`plugins/spec-flow/references/contract-template.md` adapts the "fog of war"
model from that repository's `wayfinder` skill -- the idea only, predating
and independent of the skill's own adoption.

### License

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## langfuse/Claude-Observability-Plugin

The `langfuse` plugin is a fork of
[`langfuse/Claude-Observability-Plugin`](https://github.com/langfuse/Claude-Observability-Plugin)
v1.0.0 (upstream `ea5eca1dfa26`, as of 2026-07-06). Divergences are listed in
`plugins/langfuse/README.md`.

### License

```
MIT License

Copyright (c) 2026 Langfuse GmbH

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

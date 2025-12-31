# python-dev

Comprehensive Python development skills for writing Pythonic code, systematic debugging, and test fixing.

## Features

| Skill | Purpose | Trigger Phrases |
|-------|---------|-----------------|
| `pythonic-code` | Write idiomatic, maintainable Python following PEPs and modern patterns | "make this pythonic", "review Python style", "write Python" |
| `python-debugger` | Systematic hypothesis-driven debugging with structured diagnosis | "debug", "traceback", "fix bug", "getting an error" |
| `test-fixer` | Diagnose and fix failing tests (test vs source fault triage) | "fix failing tests", "tests are failing", "debug test failure" |

## Skills Overview

### pythonic-code

Comprehensive guidance for clean, idiomatic Python code:

- **Project context discovery:** Checks `pyproject.toml` for version/dependencies
- **PEP standards:** Covers 18 PEPs (PEP 8, 20, 257, 484, 526, etc.)
- **Modern features:** Python 3.7-3.12+ patterns (dataclasses, match, walrus operator, etc.)
- **Anti-patterns:** Identifies and fixes 10 common anti-patterns
- **Advanced patterns:** 11 pattern categories (async, typing, context managers, etc.)

**Reference materials:**
- `references/pep-standards.md` - Comprehensive PEP guide (18 PEPs)
- `references/modern-features.md` - Python 3.7-3.12 feature catalog
- `references/anti-patterns.md` - Common mistakes and fixes
- `references/advanced-patterns.md` - Advanced Python patterns

**Typical workflow:**
1. Reads `pyproject.toml` to determine Python version and dependencies
2. Applies version-appropriate patterns and features
3. Follows configured tool settings (ruff, mypy, etc.)
4. Provides actionable refactoring suggestions

### python-debugger

Systematic debugging workflow for Python errors:

1. **Clarify:** Infer intended behavior from error messages and code context
2. **Reproduce:** Isolate minimal reproduction case
3. **Hypothesize:** Generate ranked hypotheses based on evidence
4. **Test:** Design experiments to validate/refute hypotheses
5. **Fix:** Implement minimal, well-justified fix
6. **Verify:** Confirm fix resolves issue without side effects

**Covers:**
- Traceback analysis and stack navigation
- Hypothesis-driven debugging methodology
- Evidence gathering and ranking
- Minimal fix proposals with clear rationale

**Integration:** Cross-references `pythonic-code` for ensuring fixes follow best practices

### test-fixer

Diagnose and fix failing tests with test vs source fault triage:

**Workflow:**
1. **Reproduce:** Run tests and capture exact failures
2. **Triage:** Determine if fault is in test or source code
3. **Fix (test fault):** Update assertions, fixtures, or test logic
4. **Propose (source fault):** Prepare minimal patch and wait for approval
5. **Verify:** Run full test suite and check for regressions

**Test fault indicators:**
- Brittle timing assumptions
- Overspecified assertions (implementation details)
- Environment coupling (filesystem, network, time)
- Stale fixture data

**Source fault indicators:**
- Public contract violations
- Documented invariant breakage
- Business logic errors
- Regression from recent changes

**Supported frameworks:**
- Python: pytest, unittest
- JavaScript: npm test, jest, vitest
- Go: go test
- Rust: cargo test

## Quick Start

### Write Pythonic Code

```
User: "Review this Python code for best practices"

Claude invokes pythonic-code skill:
1. Reads pyproject.toml to determine Python version
2. Checks for PEP compliance
3. Suggests modern patterns (dataclasses, type hints, etc.)
4. Provides refactoring guidance
```

### Debug Python Errors

```
User: "Getting a KeyError on line 45, can you debug?"

Claude invokes python-debugger skill:
1. Analyzes traceback and error context
2. Generates hypotheses (missing key, wrong dict, etc.)
3. Tests hypotheses with evidence
4. Proposes minimal fix with rationale
```

### Fix Failing Tests

```
User: "My pytest tests are failing after refactoring"

Claude invokes test-fixer skill:
1. Runs tests and captures failures
2. Triages: test fault vs source fault
3. Fixes brittle assertions or proposes source changes
4. Verifies fix with full test suite
```

## Cross-Skill Integration

The three skills are designed to work together:

- **pythonic-code + python-debugger:** After debugging, apply Pythonic patterns to fixes
- **test-fixer + python-debugger:** Use debugger for complex test diagnostics
- **test-fixer + pythonic-code:** Ensure fixed tests follow Python best practices

## Installation

Install via Claude Code marketplace:

```bash
/plugin install python-dev@cc-marketplace
```

Or enable in `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "python-dev@cc-marketplace": true
  }
}
```

## Version

1.0.0 - Initial release with three mature Python development skills

## License

MIT

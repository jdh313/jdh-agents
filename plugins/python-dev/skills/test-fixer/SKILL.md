---
name: test-fixer
description: Use Skill(python-dev:test-fixer) when failing tests need to be diagnosed and fixed. Provides systematic test diagnosis to determine whether faults are in tests or source code, then fixes test issues or proposes source changes. Trigger phrases include "fix failing tests", "tests are failing", "debug test failure", "why is this test broken", or when test output shows failures.
agent: junior-dev
allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - Bash(uv run pytest *)
  - Bash(pytest *)
  - Bash(npm test *)
  - Bash(cargo test *)
  - Bash(go test *)
---

# Test Fixer

## Overview

Systematically diagnose and fix failing tests by determining whether the fault lies in the tests themselves or in the source code. Provides a structured workflow for reproducing failures, triaging root causes, and implementing appropriate fixes.

## When to Use This Skill

Invoke this skill when:
- Tests are failing and need diagnosis
- Test suite has regressions after code changes
- Unclear whether test or source code is at fault
- Flaky tests need stabilization
- Test assertions need correction

## When NOT to Use

Skip this skill for:
- Writing new tests from scratch (use junior-dev or senior-developer)
- General code debugging without test failures (use python-debugger)
- Test design or architecture decisions (use senior-developer)

## Diagnostic Workflow

### 1. Reproduce the Failure

**Run the test suite and capture failures:**

```bash
# Python
uv run pytest                    # Run all tests
uv run pytest path/to/test.py    # Run specific test file
uv run pytest -k "test_name"     # Run specific test

# JavaScript
npm test                         # Run all tests
npm test -- path/to/test.js      # Run specific test

# Go
go test ./...                    # Run all tests
go test -run TestName            # Run specific test

# Rust
cargo test                       # Run all tests
cargo test test_name             # Run specific test
```

**Capture and analyze:**
- Exact failure messages and stack traces
- Random seeds (for randomized tests)
- Flaky indicators (passes sometimes, fails others)
- Minimal reproduction (isolate to smallest failing test)

### 2. Triage: Test vs Source Fault

**Inspect the failure to determine root cause:**

**Indicators of TEST fault:**
- Test has brittle timing assumptions (sleeps, race conditions)
- Assertions are overspecified (implementation details, not behavior)
- Test is environment-coupled (filesystem, network, time-dependent)
- Fixture data is stale or incorrect
- Test expects outdated API or behavior
- Mock/stub configuration is wrong

**Indicators of SOURCE fault:**
- Public contract is violated (API changed unexpectedly)
- Documented invariant is broken
- Business logic produces incorrect results
- Error handling is missing or wrong
- Regression from recent code change

**Supporting evidence to check:**
- Recent git history (what changed?)
- Test file vs source file modification dates
- Documentation and specs (what's the expected behavior?)
- Other tests (do related tests also fail?)

**Decision:**
- If ambiguous, present both hypotheses with evidence
- Choose the higher-probability path and proceed
- Note uncertainty in output

### 3a. If TEST is at Fault → Fix and Verify

**Fix the test issues:**

Common test fixes:
- **Brittle assertions:** Make assertions behavior-focused, not implementation-focused
- **Timing issues:** Use deterministic waits, proper async handling, fixed seeds
- **Stale fixtures:** Update test data to match current schema/API
- **Overspecification:** Relax assertions to test behavior, not exact implementation
- **Environment coupling:** Mock external dependencies, use deterministic data

**Apply fixes:**
```
Edit(file_path="tests/test_module.py",
     old_string="assert result == specific_implementation_detail",
     new_string="assert result.status == 'success'")
```

**Verify:**
1. Run the fixed tests to confirm they pass
2. Run full test suite to ensure no new failures
3. Check for flakiness (rerun 3-5 times if previously flaky)

**Output:**
- Diffs showing test changes
- Rationale: root cause and why fix is correct
- Verification results
- Follow-up suggestions (if test design needs improvement)
- Optional commit message: `test: fix brittle assertion in user creation test`

### 3b. If SOURCE is at Fault → Propose Changes

**Prepare source fix proposal (DO NOT apply yet):**

1. **Create minimal patch:**
   - Identify exact source location needing fix
   - Prepare unified diff with file paths and line numbers
   - Show before/after code clearly

2. **Document the fix:**
   - Explain what contract/behavior is being restored
   - Note any edge cases or risks
   - Mention alternatives considered

3. **Prepare supporting tests:**
   - Update existing tests to pass with fix
   - Add regression test if fixing a bug
   - Show test diffs ready to apply

4. **Wait for approval:**
   - Present proposal clearly
   - Do NOT modify source files yet
   - Wait for explicit approval: `APPROVE: <description>`

5. **After approval:**
   - Apply source changes using Edit tool
   - Apply test changes
   - Run full test suite
   - Report results

### 4. Quality Gates

Before finishing, verify:

- All tests pass locally
- No new test failures introduced
- Flaky tests rerun 3-5 times successfully
- Linting passes (run ruff/eslint/etc.)
- Code formatting applied
- Backwards compatibility maintained (or breaking changes documented)
- Test coverage unchanged or improved

### 5. Structured Reporting

Provide single, comprehensive response:

```markdown
## Test Fix Summary

**Root cause:** [Test fault | Source fault]
**Evidence:** [Key indicators that led to diagnosis]
**Files affected:** [List with line numbers]

## Changes Applied (or Proposed)

[Diffs with clear before/after]

## Verification

- Tests run: [Command used]
- Results: [Pass/fail counts]
- Flakiness check: [If applicable]

## Risks & Assumptions

- [Any risks from changes]
- [Assumptions made during fix]

## Follow-up (if any)

- [Suggested improvements]
- [Technical debt notes]
```

## Edge Cases

**Flaky tests:**
- Stabilize with fixed random seeds
- Use deterministic timeouts/waits
- Document flake cause and mitigation
- Consider quarantining if unfixable

**Environment-specific failures:**
- Note OS/Python/Node version dependencies
- Document environment requirements
- Use environment detection in tests if needed

**Missing fixtures:**
- Create minimal, deterministic test data
- Store fixtures in version control
- Document fixture setup requirements

## Integration with Skills

- **python-debugger:** Use for complex Python test debugging
- **pythonic-code:** Ensure fixed tests follow Python best practices
- **atomic-commits:** Use for committing test fixes

## Principles

- **Small, surgical changes:** Minimal diffs that fix the issue
- **Behavior over implementation:** Assert what code does, not how
- **Evidence-based:** Support diagnosis with concrete evidence
- **Safety first:** Require approval for source changes
- **Cite sources:** Link to specs, docs, or commits for context
- **Ask when blocked:** Use AskUserQuestion only if truly stuck

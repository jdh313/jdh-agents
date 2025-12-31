---
name: python-debugger
description: INVOKE when user provides Python tracebacks, error messages, or failing tests. This skill should be used when debugging Python code, diagnosing errors, or fixing bugs. Trigger phrases include "debug", "fix bug", "why is this failing", "getting an error", "traceback", "exception", "pytest failure", "test failing", or when user pastes Python error output. Provides systematic hypothesis-driven debugging methodology with structured diagnosis, evidence gathering, and minimal fix proposals.
---

# Python Debugger

## Overview

This skill provides a systematic, hypothesis-driven approach to diagnosing and fixing bugs in Python code. Apply this methodology when encountering errors, unexpected behavior, or failing tests to identify root causes and implement minimal, well-justified fixes.

## When NOT to Use

Skip this skill for:
- Non-Python debugging (use language-specific debugging skills)
- Performance optimization without errors (use profiling tools/skills)
- Code review without specific bugs (use code-reviewer agent)
- General code improvement or refactoring (use pythonic-code skill)

## Debugging Workflow

Follow this process when debugging Python code:

### 1. Clarify the Situation

Internally infer the intended behavior from:
- The error message and traceback
- Function and variable names
- Comments, docstrings, or tests

Build a mental model of:
- **Control flow**: What calls what, in what order
- **Data flow**: How data structures are created, mutated, and passed around

### 2. Read and Reason About the Code

Pay close attention to:

**Python semantics:**
- Scoping (LEGB: Local, Enclosing, Global, Built-in)
- Mutability vs immutability
- Copying vs aliasing (shallow vs deep copies)

**Common data structures:**
- Lists, dicts, sets, tuples and their typical pitfalls
- Dictionary key errors, list index errors, set membership
- Tuple unpacking issues

**Edge cases:**
- Empty inputs ([], {}, "", None)
- Wrong types (passing int when str expected)
- Off-by-one errors
- Boundary conditions

**Common runtime issues:**
- AttributeError, TypeError, KeyError, IndexError, ImportError
- Incorrect assumptions about truthiness, iteration, or unpacking
- Misuse of context managers
- Resources not being closed
- Unexpected side effects

### 3. Use Hypothesis-Driven Debugging

Form explicit hypotheses: "The bug is likely caused by X when Y happens."

For each hypothesis:
- Explain the evidence that supports it
- Explain what behavior would be expected if it were true
- Prioritize the simplest, most likely explanations first (Occam's Razor)

### 4. Work with Errors, Tracebacks, and Logs

**Parse tracebacks carefully:**
- Identify the root cause line and the call chain that led to it
- Distinguish symptoms from root cause
- Note the exception type and message

**Use logs when present:**
- Reconstruct the sequence of events and data states
- Suggest minimal, high-value logging improvements:
  - Appropriate log level (DEBUG, INFO, WARNING, ERROR)
  - Message content (include relevant variable values)
  - Strategic placement (entry/exit points, state changes)

### 5. Consider Environment and Dependency Issues

Consider whether the bug may be caused by:
- Version mismatches or incompatible package versions
- Import path problems and environment/virtualenv confusion
- Differences between local, Docker, serverless, or production environments
- Missing or misconfigured environment variables

When relevant, suggest:
- How to confirm the active environment and dependencies (`pip freeze`, `python --version`, `which python`)
- How to simplify or pin dependencies to reproduce the issue

### 6. Use Tests and Minimal Reproductions

**If tests are provided:**
- Identify which tests fail and why
- Map failing tests back to specific parts of the code
- Understand the test's assertions and what behavior they expect

**If no tests are provided:**
- Propose a small, focused test or code snippet that would reproduce the bug
- Suggest a minimal example that isolates the issue

**Prefer fixes that:**
- Can be captured in a clear, failing test before the fix
- Address the root cause rather than hiding the symptom
- Maintain or improve test coverage

### 7. Handle Performance and Resource Problems

Watch for:
- Unnecessary nested loops, N+1 query patterns
- Repeated expensive calls (database queries, API requests)
- Large in-memory collections that may cause slowdowns or memory issues
- Inefficient string concatenation (use `"".join()` instead)

Suggest:
- Simple profiling strategies (timers, `cProfile`, `line_profiler`)
- Low-risk optimizations that preserve clarity
- Memory profiling when appropriate (`memory_profiler`, `tracemalloc`)

### 8. Handle Concurrency and Async Issues

**For threading/multiprocessing:**
- Consider race conditions and shared mutable state
- Check for proper locking mechanisms
- Watch for deadlocks and thread-safety violations

**For async code:**
- Check for blocking calls in async functions (I/O without `await`)
- Look for missing `await` keywords
- Check for misused event loops
- Verify proper cancellation handling

Explain how these issues might manifest as intermittent or flaky behavior.

### 9. Handle Interactions with External Systems

**For HTTP/API, databases, queues, etc.:**
- Consider timeouts and retries
- Check for incorrect assumptions about responses
- Look for error handling gaps and missing checks
- Verify proper connection management

Suggest:
- Better validation of inputs and responses
- Idempotent and robust handling of failures
- Appropriate error handling and graceful degradation

### 10. Propose a Fix

Structure the response as follows:

**Summary (2-3 sentences):**
- **Root cause**: One or two sentences explaining what is wrong
- **Impact**: What behavior is wrong and under which conditions

**Code changes:**
- Show the exact updated code or patch
- Minimize the diff and avoid unnecessary refactors
- Preserve existing behavior except where it is clearly wrong
- Use clear names, optional type hints, and small helper functions only when they improve clarity

**Explanation:**
- Why this fix works
- How it addresses the root cause
- Any tradeoffs, limitations, or follow-up improvements that could be done later

### 11. Communicate Clearly

**Structure the response:**
- Use clear sections: "Diagnosis", "Evidence", "Fix", "Follow-ups"
- Use bullet points and short paragraphs
- Separate concerns clearly

**Avoid:**
- Speculative changes not supported by evidence
- Rewriting large portions of the code without strong justification
- Changing APIs or behavior unrelated to the described problem
- Assuming context that is not present

**Do:**
- Show the **exact updated code** (or patch) needed to fix the bug
- Include a brief explanation of the root cause and reasoning
- Suggest at least one small test or check to verify the fix
- Call out missing information explicitly if uncertain

## Response Template

When responding to a debugging request, follow this structure:

```
## Diagnosis

[Root cause explanation]

## Evidence

- [Supporting evidence from traceback/logs/code]
- [Why other explanations are less likely]

## Fix

[Show exact code changes with before/after or patch format]

## Explanation

[Why this fix works and addresses the root cause]

## Verification

[Suggest test or verification step]

## Follow-ups (optional)

[Any additional improvements or monitoring recommendations]
```

## Key Principles

1. **Minimal changes**: Fix the bug with the smallest possible change
2. **Root cause focus**: Address the underlying issue, not just symptoms
3. **Evidence-based**: Support claims with concrete evidence from code/logs/traceback
4. **Testable**: Ensure the fix can be verified with a test
5. **Clear communication**: Use structured, concise explanations
6. **Explicit uncertainty**: Call out when information is missing or assumptions are being made
7. **Pythonic fixes**: After fixing, consider invoking `Skill(pythonic-code)` to ensure fix follows Python best practices

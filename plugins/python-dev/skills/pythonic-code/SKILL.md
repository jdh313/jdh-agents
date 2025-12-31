---
name: pythonic-code
description: INVOKE for ANY Python code reading, writing, reviewing, or refactoring. Do NOT write Python without checking this skill first. Triggers: "make this pythonic", "improve Python code", "review Python style", "modernize this code", "Python code review", "refactor Python", "write Python", "PEP 8". Checks pyproject.toml for version/dependencies. Covers style, type hints, comprehensions, dataclasses, and modern patterns (3.10+).
---

# Pythonic Code

## Overview

This skill provides comprehensive guidance for writing clean, idiomatic, and maintainable Python code that follows modern best practices and community standards. This skill is automatically active when working with Python code.

## Project Context Discovery (MANDATORY FIRST STEP)

**Before writing or modifying Python code, ALWAYS check pyproject.toml:**

```
# Read pyproject.toml to determine:
# 1. Python version requirement (e.g., requires-python = ">=3.11")
# 2. Dependencies and their versions
# 3. Tool configurations (ruff, mypy, pytest)
# 4. Project metadata and structure
```

**Use this information to:**
- Match the project's Python version (don't suggest 3.13 features for 3.10 projects)
- Align with existing dependencies (Pydantic version, FastAPI version, etc.)
- Follow configured tool settings (line length, type checking strictness)
- Respect project conventions and structure

**Example workflow:**
```bash
# 1. Check pyproject.toml
Read("pyproject.toml")

# 2. Note Python version and key dependencies
# Python 3.11+ → Can use match/case, ExceptionGroup, etc.
# Python 3.10 → Use | unions but not 3.11+ features
# Pydantic v2 → Use model_config, field_validator
# Pydantic v1 → Use Config class, validator

# 3. Write code matching the project's constraints
```

## Core Principles

1. **Readability counts**: Code is read more than written
2. **Explicit is better than implicit**: Clear intent over clever tricks
3. **Simple is better than complex**: Favor straightforward solutions
4. **Practicality beats purity**: Pragmatic decisions when appropriate
5. **Errors should never pass silently**: Proper exception handling

## Code Style & Formatting

### PEP 8 Fundamentals

**Indentation and whitespace:**
- Use 4 spaces per indentation level (never tabs)
- Maximum line length: 88 characters (Black style) or 100 characters (check pyproject.toml)
- Use blank lines to separate logical sections
- Two blank lines between top-level functions and classes
- One blank line between methods within a class

**Naming conventions:**
- `snake_case` for functions, methods, variables
- `PascalCase` for classes
- `SCREAMING_SNAKE_CASE` for constants
- `_leading_underscore` for internal/private members
- `__double_leading` for name mangling (rare use)

**Imports:**
- Group imports: stdlib, third-party, local (separated by blank lines)
- Use absolute imports over relative imports
- One import per line for readability
- Avoid wildcard imports (`from module import *`)

```python
# Good
import os
import sys
from pathlib import Path

import requests
from pydantic import BaseModel

from myapp.models import User
from myapp.utils import sanitize

# Bad
import os, sys  # Multiple imports on one line
from myapp.utils import *  # Wildcard import
```

### Type Hints

**Always use type hints for:**
- Function signatures (parameters and return types)
- Class attributes
- Complex variables where type isn't obvious

**Match project Python version:**

```python
# Python 3.9+ - Modern built-in generics
def process_items(items: list[str], count: int = 10) -> dict[str, int]:
    """Process a list of items and return counts."""
    return {item: len(item) for item in items[:count]}

# Python 3.10+ - Union with |
def parse_value(value: str | int | None) -> int:
    """Parse value to integer."""
    if value is None:
        return 0
    return int(value)

# Python 3.7-3.8 - Use typing module
from typing import Dict, List, Optional, Union

def process_items(items: List[str], count: int = 10) -> Dict[str, int]:
    """Process a list of items and return counts."""
    return {item: len(item) for item in items[:count]}
```

**Type aliases for clarity:**
```python
# Good - Clear intent
UserMapping = dict[str, list[User]]

def group_users(users: list[User]) -> UserMapping:
    """Group users by department."""
    result: UserMapping = {}
    for user in users:
        result.setdefault(user.department, []).append(user)
    return result
```

## Data Structures and Idioms

### List Comprehensions

**Use list comprehensions for transformations:**
```python
# Good - Clear and concise
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]

# Bad - Verbose loop
squares = []
for x in range(10):
    squares.append(x**2)
```

**Keep comprehensions simple:**
```python
# Good - Simple transformation
names = [user.name for user in users if user.active]

# Bad - Too complex, use explicit loop instead
result = [
    process(item) for sublist in nested
    for item in sublist if validate(item) and check(item)
]
```

### Dictionary and Set Operations

**Dictionary comprehensions:**
```python
# Good - Create mappings
user_map = {user.id: user for user in users}
word_lengths = {word: len(word) for word in words}

# Good - Dictionary merging (Python 3.9+)
defaults = {"timeout": 30, "retries": 3}
config = defaults | user_config  # Merge operator
```

**Set operations:**
```python
# Good - Use sets for membership tests
valid_statuses = {"pending", "active", "completed"}
if status in valid_statuses:
    process(status)

# Good - Set operations
common = set_a & set_b  # Intersection
all_items = set_a | set_b  # Union
difference = set_a - set_b  # Difference
```

### Generator Expressions

**Use generators for memory efficiency:**
```python
# Good - Memory efficient for large sequences
sum_of_squares = sum(x**2 for x in range(1_000_000))

# Good - Generator function for lazy evaluation
def read_large_file(file_path: Path) -> Iterator[str]:
    """Read file line by line without loading into memory."""
    with open(file_path) as f:
        for line in f:
            yield line.strip()
```

## Modern Python Features

See `references/modern-features.md` for detailed guidance on version-specific features:
- Structural pattern matching (3.10+)
- Dataclasses and Pydantic (v1 vs v2)
- Type hint evolution (3.9+ built-in generics, 3.10+ unions, 3.11+ Self)
- Protocol for structural typing
- Context managers
- Generator expressions and performance patterns

## Error Handling

### Exception Best Practices

**Be specific with exceptions:**
```python
# Good - Specific exceptions
try:
    user = db.get_user(user_id)
except UserNotFoundError:
    logger.warning(f"User {user_id} not found")
    raise
except DatabaseConnectionError as e:
    logger.error(f"Database error: {e}")
    raise ServiceUnavailableError from e

# Bad - Bare except
try:
    risky_operation()
except:  # Catches everything, including KeyboardInterrupt
    pass
```

**Use context managers for resource cleanup:**
```python
# Good - Context manager ensures cleanup
from contextlib import contextmanager

@contextmanager
def database_transaction(db: Database):
    """Manage database transaction with rollback."""
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

# Usage
with database_transaction(db) as session:
    session.execute(query)
```

**Custom exceptions with context:**
```python
# Good - Descriptive exception hierarchy
class ApplicationError(Exception):
    """Base exception for application errors."""

class ValidationError(ApplicationError):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f"Validation error on {field}: {message}")

# Usage
if not email:
    raise ValidationError("email", "Email is required")
```

## Functions and Methods

### Function Design

**Keep functions focused (Single Responsibility):**
```python
# Good - Single purpose
def calculate_total_price(items: list[Item]) -> Decimal:
    """Calculate total price of items."""
    return sum(item.price * item.quantity for item in items)

def apply_discount(price: Decimal, discount: Decimal) -> Decimal:
    """Apply discount percentage to price."""
    return price * (1 - discount / 100)

# Bad - Multiple responsibilities
def process_order(items, user, payment_info):
    # Validates, calculates, applies discount, processes payment,
    # charges card, sends email, updates inventory
    # Too many concerns in one function
    pass
```

**Use default arguments carefully:**
```python
# Good - Immutable defaults
def create_user(name: str, tags: list[str] | None = None) -> User:
    """Create user with optional tags."""
    if tags is None:
        tags = []
    return User(name=name, tags=tags)

# Bad - Mutable default (COMMON BUG!)
def create_user(name: str, tags: list[str] = []) -> User:
    # Same list object shared across calls!
    return User(name=name, tags=tags)
```

### Docstrings

**Use Google-style or NumPy-style docstrings:**
```python
def calculate_metrics(
    data: list[float],
    weights: list[float] | None = None,
) -> dict[str, float]:
    """Calculate statistical metrics for weighted data.

    Args:
        data: List of numeric values to analyze
        weights: Optional weights for each value. If None, equal weights used.

    Returns:
        Dictionary containing 'mean', 'median', and 'std' keys

    Raises:
        ValueError: If data is empty or weights length doesn't match data

    Example:
        >>> calculate_metrics([1, 2, 3, 4, 5])
        {'mean': 3.0, 'median': 3.0, 'std': 1.41}
    """
    if not data:
        raise ValueError("Data cannot be empty")

    if weights and len(weights) != len(data):
        raise ValueError("Weights must match data length")

    # Implementation...
```

## Object-Oriented Design

### Class Design Principles

**Use properties for computed attributes:**
```python
class Rectangle:
    """Rectangle with computed area."""

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @property
    def area(self) -> float:
        """Calculate area on access."""
        return self.width * self.height

    @property
    def perimeter(self) -> float:
        """Calculate perimeter."""
        return 2 * (self.width + self.height)
```

**Favor composition over inheritance:**
```python
# Good - Composition
class EmailService:
    """Service for sending emails."""

    def send(self, to: str, message: str) -> None:
        """Send email."""
        ...

class NotificationManager:
    """Manage user notifications via multiple channels."""

    def __init__(self, email_service: EmailService) -> None:
        self._email = email_service

    def notify_user(self, user: User, message: str) -> None:
        """Send notification to user."""
        self._email.send(user.email, message)
```

**Use Protocol for structural typing (3.8+):**
```python
from typing import Protocol

class Drawable(Protocol):
    """Protocol for objects that can be drawn."""

    def draw(self) -> str:
        """Return string representation."""
        ...

def render(items: list[Drawable]) -> list[str]:
    """Render all drawable items."""
    return [item.draw() for item in items]

# Any class with draw() method works
class Circle:
    def draw(self) -> str:
        return "Circle"

class Square:
    def draw(self) -> str:
        return "Square"

render([Circle(), Square()])  # Type safe!
```

## Performance and Best Practices

### Efficient Python

**Use built-in functions and operators:**
```python
# Good - Use built-ins
numbers = [1, 2, 3, 4, 5]
total = sum(numbers)
maximum = max(numbers)
all_positive = all(n > 0 for n in numbers)

# Bad - Manual implementation
total = 0
for n in numbers:
    total += n
```

**String operations:**
```python
# Good - Join for concatenation
result = "".join(parts)  # Efficient
result = ", ".join(str(x) for x in items)

# Bad - String concatenation in loop
result = ""
for part in parts:
    result += part  # Creates new string each time
```

**Use slots for memory optimization:**
```python
# Good - Slots reduce memory for many instances
class Point:
    """Memory-efficient point class."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```

## Anti-Patterns to Avoid

See `references/anti-patterns.md` for detailed explanations of common mistakes:
- Mutable default arguments (most common Python bug)
- Catching and ignoring exceptions
- Using bare `except:`
- Modifying list while iterating
- Old-style string formatting
- Not using context managers
- Using `==` with None/True/False
- Not using comprehensions when appropriate
- Not using enumerate
- Inefficient string concatenation in loops

## Tooling Integration

**Check pyproject.toml for configured tools:**

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Common tool commands (use `uv` per CLAUDE.md):**
```bash
uv run ruff format .        # Format code
uv run ruff check .         # Lint code
uv run mypy src/            # Type check
uv run pytest               # Run tests
```

## Workflow Pattern

When working with Python code:

1. **Check pyproject.toml first**: Determine Python version, dependencies, tool configs
2. **Match project constraints**: Use appropriate syntax and dependency versions
3. **Follow project conventions**: Line length, import style, etc.
4. **Apply pythonic patterns**: Comprehensions, context managers, type hints
5. **Handle errors explicitly**: Specific exceptions with context
6. **Write testable code**: Dependency injection, pure functions
7. **Document clearly**: Docstrings for public APIs
8. **Validate with tools**: Ruff, mypy, pytest

## Key Takeaways

1. **ALWAYS check pyproject.toml before writing code**
2. Match the project's Python version and dependency constraints
3. Prioritize readability and maintainability over cleverness
4. Use type hints consistently for better tooling
5. Leverage modern Python features appropriate to the version
6. Follow PEP 8 and community standards
7. Write testable code with dependency injection
8. Use context managers for resource management
9. Prefer composition over inheritance
10. Handle errors explicitly and specifically
11. For debugging specific errors, use `Skill(python-debugger)` first, then apply pythonic patterns

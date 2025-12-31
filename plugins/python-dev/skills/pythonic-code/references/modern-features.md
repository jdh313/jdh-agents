# Modern Python Features

Version-specific features and patterns for Python 3.10+.

---

## Structural Pattern Matching (3.10+)

**Check Python version before using.**

### Basic Pattern Matching

```python
# Python 3.10+ only
def handle_response(response: dict) -> str:
    match response:
        case {"status": "success", "data": data}:
            return f"Success: {data}"
        case {"status": "error", "message": msg}:
            return f"Error: {msg}"
        case _:
            return "Unknown response"
```

### Type-Based Matching

```python
def process_value(value: int | str | list) -> str:
    match value:
        case int(x) if x > 0:
            return f"Positive: {x}"
        case str(s):
            return f"String: {s}"
        case list(items):
            return f"List with {len(items)} items"
        case _:
            return "Unknown"
```

### Sequence Pattern Matching

```python
def process_coordinates(point: tuple) -> str:
    match point:
        case (0, 0):
            return "Origin"
        case (0, y):
            return f"Y-axis at {y}"
        case (x, 0):
            return f"X-axis at {x}"
        case (x, y):
            return f"Point at ({x}, {y})"
```

---

## Dataclasses and Pydantic

### Pydantic v2 (Modern)

**Check dependencies in pyproject.toml for Pydantic version.**

```python
from pydantic import BaseModel, Field, field_validator

class UserCreate(BaseModel):
    """User creation with validation."""
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    age: int = Field(ge=0, le=150)

    @field_validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v: str) -> str:
        """Ensure email is lowercase."""
        return v.lower()

    model_config = {"frozen": True}  # v2 syntax
```

### Pydantic v1 (Legacy)

```python
from pydantic import BaseModel, Field, validator

class UserCreate(BaseModel):
    """User creation with validation."""
    name: str = Field(min_length=1, max_length=100)
    email: str
    age: int = Field(ge=0, le=150)

    @validator("email")
    @classmethod
    def email_must_be_lowercase(cls, v: str) -> str:
        """Ensure email is lowercase."""
        return v.lower()

    class Config:  # v1 syntax
        frozen = True
```

### Standard Library Dataclasses

```python
from dataclasses import dataclass, field

@dataclass
class User:
    """User model with sensible defaults."""
    id: int
    name: str
    email: str
    active: bool = True
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate after initialization."""
        if not self.email or "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
```

### Dataclass Features

```python
from dataclasses import dataclass, field, asdict

@dataclass(frozen=True)  # Immutable
class Point:
    x: float
    y: float

@dataclass(order=True)  # Comparable
class Priority:
    level: int
    name: str

@dataclass
class Config:
    """Config with computed field."""
    host: str
    port: int
    timeout: int = 30

    @property
    def url(self) -> str:
        """Compute URL from host and port."""
        return f"http://{self.host}:{self.port}"
```

---

## Type Hints Evolution

### Python 3.9+ - Built-in Generics

```python
# Python 3.9+ - Use built-in types
def process_items(items: list[str], count: int = 10) -> dict[str, int]:
    """Process a list of items and return counts."""
    return {item: len(item) for item in items[:count]}

# No need for typing.List, typing.Dict
```

### Python 3.10+ - Union with |

```python
# Python 3.10+ - Use | for unions
def parse_value(value: str | int | None) -> int:
    """Parse value to integer."""
    if value is None:
        return 0
    return int(value)

# No need for typing.Union or typing.Optional
```

### Python 3.11+ - Self Type

```python
from typing import Self

class Builder:
    """Builder pattern with Self type."""

    def __init__(self) -> None:
        self.value = 0

    def add(self, n: int) -> Self:
        """Add value and return self."""
        self.value += n
        return self

    def multiply(self, n: int) -> Self:
        """Multiply value and return self."""
        self.value *= n
        return self

# Usage with type safety
builder = Builder().add(5).multiply(2)  # Type: Builder
```

### Python 3.7-3.8 - Legacy Typing

```python
from typing import Dict, List, Optional, Union

def process_items(items: List[str], count: int = 10) -> Dict[str, int]:
    """Process a list of items and return counts."""
    return {item: len(item) for item in items[:count]}

def parse_value(value: Union[str, int, None]) -> int:
    """Parse value to integer."""
    if value is None:
        return 0
    return int(value)
```

---

## Advanced Patterns

### Protocol for Structural Typing (3.8+)

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

# Any class with draw() method works (duck typing with type safety)
class Circle:
    def draw(self) -> str:
        return "Circle"

class Square:
    def draw(self) -> str:
        return "Square"

render([Circle(), Square()])  # Type safe!
```

### Context Managers

```python
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

### Custom Context Manager Class

```python
class Timer:
    """Context manager for timing code blocks."""

    def __enter__(self) -> Self:
        self.start = time.time()
        return self

    def __exit__(self, *args) -> None:
        self.elapsed = time.time() - self.start
        print(f"Elapsed: {self.elapsed:.2f}s")

# Usage
with Timer() as t:
    expensive_operation()
# Automatically prints elapsed time
```

---

## Performance Patterns

### Generator Expressions

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

### Slots for Memory Optimization

```python
# Good - Slots reduce memory for many instances
class Point:
    """Memory-efficient point class."""
    __slots__ = ("x", "y")

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```

### String Operations

```python
# Good - Join for concatenation
result = "".join(parts)  # Efficient
result = ", ".join(str(x) for x in items)

# Bad - String concatenation in loop
result = ""
for part in parts:
    result += part  # Creates new string each time
```

---

## When to Use Which Feature

| Feature | Python Version | Use Case |
|---------|---------------|----------|
| `list[str]` built-in generics | 3.9+ | Type hints |
| `str \| int` unions | 3.10+ | Union types |
| `match/case` | 3.10+ | Pattern matching |
| `Self` type | 3.11+ | Builder patterns, method chaining |
| `ExceptionGroup` | 3.11+ | Multiple exception handling |
| Protocol | 3.8+ | Structural typing |
| Dataclasses | 3.7+ | Simple data containers |
| f-strings | 3.6+ | String formatting |

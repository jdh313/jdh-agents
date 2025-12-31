# PEP Standards Reference

Quick reference for key Python Enhancement Proposals (PEPs) that define Python standards and best practices.

## PEP 8 - Style Guide for Python Code

**Official style guide:** https://peps.python.org/pep-0008/

### Key Points

**Code Layout:**
- Indentation: 4 spaces per level
- Maximum line length: 79 characters (docstrings/comments), 99 characters (code)
- Note: Many modern projects use 88 (Black) or 100
- Blank lines: 2 between top-level definitions, 1 between methods

**Naming Conventions:**
- Modules: `lowercase`, `lower_with_underscores`
- Classes: `CapWords` (PascalCase)
- Functions/methods: `lowercase_with_underscores`
- Constants: `UPPERCASE_WITH_UNDERSCORES`
- Private: `_leading_underscore`

**Imports:**
- Standard library, then third-party, then local
- Absolute imports preferred over relative
- One import per line

## PEP 20 - The Zen of Python

Run `import this` in Python to see:

```
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
```

## PEP 257 - Docstring Conventions

**Official docstring conventions:** https://peps.python.org/pep-0257/

**One-line docstrings:**
```python
def square(x: int) -> int:
    """Return the square of x."""
    return x * x
```

**Multi-line docstrings:**
```python
def complex_function(arg1: str, arg2: int) -> dict:
    """Summary line.

    Extended description of function behavior and parameters.
    Can span multiple lines.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When condition occurs
    """
    pass
```

## PEP 484 - Type Hints

**Type annotations:** https://peps.python.org/pep-0484/

```python
def greeting(name: str) -> str:
    return f"Hello {name}"

# Variables
age: int = 30
names: list[str] = ["Alice", "Bob"]

# Optional
from typing import Optional
result: Optional[int] = None  # or int | None in 3.10+

# Union types
from typing import Union
value: Union[int, str] = 42  # or int | str in 3.10+

# Callable
from typing import Callable
func: Callable[[int, int], int] = lambda x, y: x + y
```

## PEP 526 - Variable Annotations

**Syntax for variable annotations:** https://peps.python.org/pep-0526/

```python
# Class variables
class User:
    name: str
    age: int
    active: bool = True  # With default

# Instance variables in __init__
def __init__(self) -> None:
    self.items: list[str] = []

# Module-level
count: int = 0
users: dict[int, User] = {}
```

## PEP 557 - Data Classes

**Decorator for creating data classes:** https://peps.python.org/pep-0557/

```python
from dataclasses import dataclass, field

@dataclass
class User:
    name: str
    age: int
    active: bool = True
    tags: list[str] = field(default_factory=list)

@dataclass(frozen=True)  # Immutable
class Point:
    x: float
    y: float
```

## PEP 585 - Type Hinting Generics in Standard Collections

**Use built-in types for generics (Python 3.9+):** https://peps.python.org/pep-0585/

```python
# Python 3.9+ - Use built-ins
def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

# Older style (3.7-3.8)
from typing import List, Dict

def process(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}
```

## PEP 604 - Union Operator

**Allow X | Y syntax for Union types (Python 3.10+):** https://peps.python.org/pep-0604/

```python
# Python 3.10+
def parse(value: int | str | None) -> int:
    if value is None:
        return 0
    return int(value)

# Older style
from typing import Union, Optional

def parse(value: Union[int, str, None]) -> int:
    if value is None:
        return 0
    return int(value)
```

## PEP 634, 635, 636 - Structural Pattern Matching

**Match statement (Python 3.10+):** https://peps.python.org/pep-0634/

```python
def handle_command(command: dict) -> str:
    match command:
        case {"action": "create", "name": name}:
            return f"Creating {name}"
        case {"action": "delete", "id": id}:
            return f"Deleting {id}"
        case {"action": "update", "id": id, "data": data}:
            return f"Updating {id} with {data}"
        case _:
            return "Unknown command"
```

## PEP 654 - Exception Groups

**Handle multiple exceptions (Python 3.11+):** https://peps.python.org/pep-0654/

```python
def process_all(items: list[str]) -> None:
    errors = []
    for item in items:
        try:
            process(item)
        except ValueError as e:
            errors.append(e)

    if errors:
        raise ExceptionGroup("Processing failed", errors)

# Handling exception groups
try:
    process_all(items)
except* ValueError as eg:
    for e in eg.exceptions:
        logger.error(f"Validation error: {e}")
except* IOError as eg:
    for e in eg.exceptions:
        logger.error(f"IO error: {e}")
```

## PEP 673 - Self Type

**Type for self parameter (Python 3.11+):** https://peps.python.org/pep-0673/

```python
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        """Return self for method chaining."""
        self.name = name
        return self

    def set_value(self, value: int) -> Self:
        self.value = value
        return self

# Usage
builder = Builder().set_name("test").set_value(42)
```

## PEP 695 - Type Parameter Syntax

**New type parameter syntax (Python 3.12+):** https://peps.python.org/pep-0695/

```python
# Python 3.12+
def first[T](items: list[T]) -> T:
    """Return first item."""
    return items[0]

class Stack[T]:
    """Generic stack."""
    def __init__(self) -> None:
        self.items: list[T] = []

# Type alias
type Point = tuple[float, float]
type IntOrStr = int | str

# Older style
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T:
    return items[0]
```

## PEP 3107 / 3119 - Function Annotations and ABCs

**Abstract base classes:** https://peps.python.org/pep-3119/

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def save(self, entity: Any) -> None:
        """Save entity."""
        pass

    @abstractmethod
    def get(self, id: int) -> Any:
        """Get entity by ID."""
        pass
```

## PEP 498 - Literal String Interpolation

**F-strings (Python 3.6+):** https://peps.python.org/pep-0498/

```python
name = "Alice"
age = 30

# Basic f-string
message = f"Hello {name}, you are {age} years old"

# Expressions
result = f"2 + 2 = {2 + 2}"

# Format specifiers
pi = 3.14159
formatted = f"Pi: {pi:.2f}"  # "Pi: 3.14"

# Debug mode (Python 3.8+)
value = 42
debug = f"{value=}"  # "value=42"
```

## PEP 572 - Assignment Expressions (Walrus)

**Walrus operator := (Python 3.8+):** https://peps.python.org/pep-0572/

```python
# In if conditions
if (match := pattern.search(text)) is not None:
    print(match.group(0))

# In while loops
while (line := file.readline()) != "":
    process(line)

# In list comprehensions
results = [value for item in items if (value := compute(item)) > threshold]
```

## PEP 589 - TypedDict

**Type hints for dictionaries (Python 3.8+):** https://peps.python.org/pep-0589/

```python
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    email: str

def create_user(data: UserDict) -> User:
    """Create user from typed dictionary."""
    return User(**data)

# Optional fields
class UserOptional(TypedDict, total=False):
    name: str  # Required
    age: int   # Required
    phone: str # Optional
```

## PEP 544 - Protocols

**Structural subtyping (Python 3.8+):** https://peps.python.org/pep-0544/

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> str:
        """Return string representation."""
        ...

# Any class with draw() method is compatible
class Circle:
    def draw(self) -> str:
        return "Circle"

def render(obj: Drawable) -> str:
    return obj.draw()

render(Circle())  # Works without inheritance!
```

## Version-Specific Feature Matrix

| Feature | PEP | Python Version | Example |
|---------|-----|----------------|---------|
| f-strings | 498 | 3.6+ | `f"{name}"` |
| Walrus operator | 572 | 3.8+ | `if (x := func()) > 0` |
| Built-in generics | 585 | 3.9+ | `list[str]` |
| Union with \| | 604 | 3.10+ | `int \| str` |
| Match statement | 634 | 3.10+ | `match value:` |
| Exception groups | 654 | 3.11+ | `except* ValueError` |
| Self type | 673 | 3.11+ | `-> Self` |
| Type parameter syntax | 695 | 3.12+ | `def func[T]` |

## Best Practices Summary

1. **Always check Python version before using modern features**
2. **Use type hints for better tooling and documentation**
3. **Follow PEP 8 for consistent style** (or project's configured style)
4. **Prefer built-in generics (3.9+) over typing module**
5. **Use dataclasses for simple data structures**
6. **Leverage Protocols for structural typing**
7. **Write clear docstrings following PEP 257**
8. **Use f-strings for string formatting**
9. **Apply walrus operator for cleaner conditionals**
10. **Check pyproject.toml for project-specific standards**

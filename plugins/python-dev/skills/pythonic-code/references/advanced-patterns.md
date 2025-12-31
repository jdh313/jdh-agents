# Advanced Python Patterns

This reference provides detailed examples of advanced Python patterns and idioms beyond the basics covered in SKILL.md.

## Descriptors

**Custom attribute access control:**
```python
class ValidatedString:
    """Descriptor for validated string attributes."""

    def __init__(self, min_length: int = 0, max_length: int = 100) -> None:
        self.min_length = min_length
        self.max_length = max_length

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj: object, objtype: type = None) -> str:
        if obj is None:
            return self
        return getattr(obj, self.private_name, "")

    def __set__(self, obj: object, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a string")
        if len(value) < self.min_length:
            raise ValueError(f"{self.name} too short")
        if len(value) > self.max_length:
            raise ValueError(f"{self.name} too long")
        setattr(obj, self.private_name, value)

class User:
    """User with validated fields."""
    name = ValidatedString(min_length=1, max_length=50)
    email = ValidatedString(min_length=5, max_length=100)

    def __init__(self, name: str, email: str) -> None:
        self.name = name  # Triggers validation
        self.email = email  # Triggers validation
```

## Metaclasses

**Registry pattern with metaclasses:**
```python
from typing import Any, Dict, Type

class PluginRegistry(type):
    """Metaclass that automatically registers plugin classes."""

    _registry: Dict[str, Type] = {}

    def __new__(
        mcs,
        name: str,
        bases: tuple,
        namespace: dict[str, Any],
    ) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        if name != "Plugin":  # Don't register base class
            mcs._registry[name] = cls
        return cls

    @classmethod
    def get_plugin(mcs, name: str) -> Type:
        """Get plugin class by name."""
        return mcs._registry[name]

class Plugin(metaclass=PluginRegistry):
    """Base plugin class."""

class JSONPlugin(Plugin):
    """JSON serialization plugin."""
    def serialize(self, data: dict) -> str:
        return json.dumps(data)

class XMLPlugin(Plugin):
    """XML serialization plugin."""
    def serialize(self, data: dict) -> str:
        # Implementation...
        pass

# Plugins auto-registered
plugin = PluginRegistry.get_plugin("JSONPlugin")()
```

## Abstract Base Classes (ABC)

**Enforce interface contracts:**
```python
from abc import ABC, abstractmethod
from typing import Iterator

class Repository(ABC):
    """Abstract repository interface."""

    @abstractmethod
    def get(self, id: int) -> Any:
        """Get entity by ID."""
        pass

    @abstractmethod
    def save(self, entity: Any) -> None:
        """Save entity."""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """Delete entity by ID."""
        pass

    @abstractmethod
    def list(self) -> Iterator[Any]:
        """List all entities."""
        pass

class UserRepository(Repository):
    """Concrete user repository."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def get(self, id: int) -> User:
        return self._db.query(User).filter_by(id=id).first()

    def save(self, entity: User) -> None:
        self._db.add(entity)
        self._db.commit()

    def delete(self, id: int) -> None:
        user = self.get(id)
        self._db.delete(user)
        self._db.commit()

    def list(self) -> Iterator[User]:
        return iter(self._db.query(User).all())
```

## Async Patterns

**Async context managers:**
```python
from contextlib import asynccontextmanager
from typing import AsyncIterator

@asynccontextmanager
async def async_database_transaction(
    db: AsyncDatabase,
) -> AsyncIterator[AsyncDatabase]:
    """Async context manager for database transactions."""
    try:
        yield db
        await db.commit()
    except Exception:
        await db.rollback()
        raise

# Usage
async with async_database_transaction(db) as session:
    await session.execute(query)
```

**Async generators:**
```python
async def fetch_pages(url: str, max_pages: int = 10) -> AsyncIterator[dict]:
    """Fetch pages asynchronously with pagination."""
    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            async with session.get(f"{url}?page={page}") as response:
                data = await response.json()
                yield data
                if not data.get("next"):
                    break

# Usage
async for page_data in fetch_pages("https://api.example.com/items"):
    process(page_data)
```

**Gather with error handling:**
```python
import asyncio
from typing import Sequence

async def safe_gather(
    *coros: Coroutine,
    return_exceptions: bool = True,
) -> Sequence[Any]:
    """Gather coroutines with individual error handling."""
    results = await asyncio.gather(*coros, return_exceptions=return_exceptions)

    errors = [r for r in results if isinstance(r, Exception)]
    if errors and not return_exceptions:
        raise ExceptionGroup("Multiple failures", errors)

    return results

# Usage
results = await safe_gather(
    fetch_user(1),
    fetch_user(2),
    fetch_user(3),
)
```

## Functools Patterns

**LRU cache for memoization:**
```python
from functools import lru_cache, cache

@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """Calculate fibonacci with caching."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

@cache  # Unlimited cache (Python 3.9+)
def expensive_computation(x: int, y: int) -> int:
    """Cache results of expensive computation."""
    return x ** y + y ** x
```

**Partial application:**
```python
from functools import partial

def power(base: float, exponent: float) -> float:
    """Calculate power."""
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(square(5))  # 25
print(cube(5))    # 125
```

**singledispatch for function overloading:**
```python
from functools import singledispatch

@singledispatch
def process(value):
    """Default processor."""
    raise NotImplementedError(f"Cannot process {type(value)}")

@process.register(int)
def _(value: int) -> str:
    """Process integer."""
    return f"Integer: {value}"

@process.register(str)
def _(value: str) -> str:
    """Process string."""
    return f"String: {value.upper()}"

@process.register(list)
def _(value: list) -> str:
    """Process list."""
    return f"List with {len(value)} items"
```

## Itertools Patterns

**Chunking iterables:**
```python
from itertools import islice
from typing import Iterator, TypeVar

T = TypeVar("T")

def chunked(iterable: Iterable[T], size: int) -> Iterator[tuple[T, ...]]:
    """Split iterable into fixed-size chunks."""
    it = iter(iterable)
    while chunk := tuple(islice(it, size)):
        yield chunk

# Usage
for chunk in chunked(range(100), 10):
    process_batch(chunk)
```

**Grouping consecutive items:**
```python
from itertools import groupby
from operator import itemgetter

data = [
    {"name": "Alice", "dept": "Engineering"},
    {"name": "Bob", "dept": "Engineering"},
    {"name": "Carol", "dept": "Sales"},
    {"name": "Dave", "dept": "Sales"},
]

# Group by department
for dept, group in groupby(data, key=itemgetter("dept")):
    members = list(group)
    print(f"{dept}: {[m['name'] for m in members]}")
```

## Context Managers

**Multiple context managers:**
```python
from contextlib import ExitStack

def process_files(file_paths: list[str]) -> None:
    """Process multiple files with single context manager."""
    with ExitStack() as stack:
        files = [stack.enter_context(open(path)) for path in file_paths]
        for f in files:
            process(f.read())
```

**Custom context manager class:**
```python
class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.start_time: float = 0

    def __enter__(self) -> "Timer":
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        elapsed = time.time() - self.start_time
        print(f"{self.name} took {elapsed:.2f} seconds")

# Usage
with Timer("database query"):
    results = db.query(User).all()
```

## Weak References

**Cache without preventing garbage collection:**
```python
import weakref

class Cache:
    """Cache using weak references."""

    def __init__(self) -> None:
        self._cache: weakref.WeakValueDictionary = weakref.WeakValueDictionary()

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self._cache[key] = value

# Objects are removed from cache when no other references exist
cache = Cache()
user = User(name="Alice")
cache.set("alice", user)
del user  # Cache entry automatically removed
```

## Slots with Inheritance

**Combining slots across inheritance hierarchy:**
```python
class Base:
    """Base class with slots."""
    __slots__ = ("id", "created_at")

    def __init__(self, id: int) -> None:
        self.id = id
        self.created_at = datetime.now()

class User(Base):
    """User class extending slots."""
    __slots__ = ("name", "email")  # Only add new slots

    def __init__(self, id: int, name: str, email: str) -> None:
        super().__init__(id)
        self.name = name
        self.email = email
```

## Property Decorators

**Cached properties:**
```python
from functools import cached_property

class DataAnalyzer:
    """Analyzer with expensive computed properties."""

    def __init__(self, data: list[float]) -> None:
        self._data = data

    @cached_property
    def mean(self) -> float:
        """Calculate mean (cached)."""
        return sum(self._data) / len(self._data)

    @cached_property
    def std_dev(self) -> float:
        """Calculate standard deviation (cached)."""
        mean = self.mean
        variance = sum((x - mean) ** 2 for x in self._data) / len(self._data)
        return variance ** 0.5
```

## Operator Overloading

**Rich comparison methods:**
```python
from functools import total_ordering

@total_ordering
class Version:
    """Semantic version with comparison support."""

    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )

    def __lt__(self, other: "Version") -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

# Usage
v1 = Version(1, 0, 0)
v2 = Version(2, 0, 0)
assert v1 < v2
assert v2 > v1
assert v1 <= v2
```

## Type Guards and Narrowing

**Custom type guards (3.10+):**
```python
from typing import TypeGuard

def is_string_list(val: list) -> TypeGuard[list[str]]:
    """Check if list contains only strings."""
    return all(isinstance(x, str) for x in val)

def process_data(data: list[Any]) -> None:
    """Process data with type narrowing."""
    if is_string_list(data):
        # Type checker knows data is list[str] here
        result = ",".join(data)
```

## Generic Classes

**Type-safe generic containers:**
```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Stack(Generic[T]):
    """Type-safe stack implementation."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        """Push item onto stack."""
        self._items.append(item)

    def pop(self) -> T:
        """Pop item from stack."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self) -> T:
        """Peek at top item."""
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]

# Usage with type checking
int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
value: int = int_stack.pop()  # Type checker knows this is int
```

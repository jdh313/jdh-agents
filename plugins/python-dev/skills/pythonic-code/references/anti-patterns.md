# Python Anti-Patterns to Avoid

Common mistakes and pitfalls in Python code with correct alternatives.

---

## 1. Mutable Default Arguments

**The most common Python bug.**

### The Problem

```python
# Bad - Same list object shared across all calls
def append_to(element, target=[]):
    target.append(element)
    return target

# First call
result1 = append_to(1)  # [1]
# Second call
result2 = append_to(2)  # [1, 2] - UNEXPECTED!
# The same list is reused!
```

### The Fix

```python
# Good - Create new list per call
def append_to(element, target=None):
    if target is None:
        target = []
    target.append(element)
    return target

# Each call gets a fresh list
result1 = append_to(1)  # [1]
result2 = append_to(2)  # [2]
```

### Why It Happens

Default arguments are evaluated once at function definition time, not at call time. Mutable defaults (lists, dicts, sets) are shared across all calls.

**Rule:** Use `None` as default, create mutable object inside function.

---

## 2. Catching and Ignoring Exceptions

### The Problem

```python
# Bad - Silent failure hides bugs
try:
    risky_operation()
except Exception:
    pass  # What went wrong? We'll never know

# Bad - Too broad
try:
    process_data()
except:  # Catches KeyboardInterrupt, SystemExit too!
    log_error()
```

### The Fix

```python
# Good - Log and handle appropriately
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise for upstream handling

# Good - Catch specific exceptions only
try:
    process_data()
except (ValueError, KeyError) as e:
    logger.warning(f"Expected error: {e}")
    return default_value
```

### Why It Matters

- Silent failures make debugging nearly impossible
- Bare `except:` catches system signals (Ctrl+C, exits)
- Specific exceptions document what can go wrong

---

## 3. Modifying List While Iterating

### The Problem

```python
# Bad - Skips elements unpredictably
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)  # Modifies list during iteration

# Result: [1, 3, 5] - but 4 was skipped!
```

### The Fix

```python
# Good - Create new list
items = [1, 2, 3, 4, 5]
items = [item for item in items if item % 2 != 0]

# Good - Iterate over copy
items = [1, 2, 3, 4, 5]
for item in items[:]:  # Slice creates copy
    if item % 2 == 0:
        items.remove(item)

# Good - Use filter
items = list(filter(lambda x: x % 2 != 0, items))
```

### Why It Happens

Iterator index gets out of sync when list size changes during iteration.

---

## 4. Old-Style String Formatting

### The Problem

```python
# Bad - printf-style (ancient)
message = "User %s has %d items" % (name, count)

# Bad - .format() (verbose)
message = "User {} has {} items".format(name, count)
message = "User {name} has {count} items".format(name=name, count=count)
```

### The Fix

```python
# Good - f-strings (Python 3.6+)
message = f"User {name} has {count} items"

# Good - Complex expressions
message = f"Total: ${total:.2f}"
message = f"User {user.name.upper()} (ID: {user.id})"

# Good - Multi-line
message = (
    f"User {name} has {count} items.\n"
    f"Total value: ${total:.2f}"
)
```

### Benefits

- More readable and concise
- Less error-prone
- Better performance
- Supports expressions in {}

---

## 5. Not Using Context Managers

### The Problem

```python
# Bad - Manual resource management
f = open("data.txt")
try:
    data = f.read()
    process(data)
finally:
    f.close()

# Bad - Forgot to close
connection = create_connection()
connection.execute(query)
# Connection never closed!
```

### The Fix

```python
# Good - Automatic cleanup
with open("data.txt") as f:
    data = f.read()
    process(data)
# File automatically closed

# Good - Database connections
with create_connection() as conn:
    conn.execute(query)
# Connection automatically closed
```

### Why It Matters

- Guarantees cleanup even if exceptions occur
- Prevents resource leaks
- More readable

---

## 6. Using `==` to Compare with None/True/False

### The Problem

```python
# Bad - Uses == for singletons
if value == None:
    return default

if flag == True:
    do_something()
```

### The Fix

```python
# Good - Use 'is' for singletons
if value is None:
    return default

# Good - Direct boolean check
if flag:
    do_something()

# Good - Explicit False check when needed
if flag is False:
    do_something()
```

### Why

- `None`, `True`, `False` are singletons - use identity check
- More efficient (identity vs equality)
- More Pythonic

---

## 7. Not Using Comprehensions

### The Problem

```python
# Bad - Verbose loop
result = []
for item in items:
    if item.active:
        result.append(item.name.upper())

# Bad - Nested loops
matrix = []
for i in range(5):
    row = []
    for j in range(5):
        row.append(i * j)
    matrix.append(row)
```

### The Fix

```python
# Good - List comprehension
result = [item.name.upper() for item in items if item.active]

# Good - Nested comprehension (when simple)
matrix = [[i * j for j in range(5)] for i in range(5)]
```

### When NOT to Use

Don't use comprehensions if:
- Logic is complex (multiple conditions, transformations)
- Need intermediate variables
- Side effects are involved
- Reduces readability

---

## 8. Not Using Enumerate

### The Problem

```python
# Bad - Manual index tracking
index = 0
for item in items:
    print(f"{index}: {item}")
    index += 1

# Bad - Range with len
for i in range(len(items)):
    print(f"{i}: {items[i]}")
```

### The Fix

```python
# Good - Enumerate
for i, item in enumerate(items):
    print(f"{i}: {item}")

# Good - Custom start index
for i, item in enumerate(items, start=1):
    print(f"{i}: {item}")
```

---

## 9. Not Using dict.get() or dict.setdefault()

### The Problem

```python
# Bad - KeyError risk
value = my_dict[key]

# Bad - Verbose check
if key in my_dict:
    value = my_dict[key]
else:
    value = default_value

# Bad - Repeated key lookups
if key not in my_dict:
    my_dict[key] = []
my_dict[key].append(value)
```

### The Fix

```python
# Good - get() with default
value = my_dict.get(key, default_value)

# Good - setdefault()
my_dict.setdefault(key, []).append(value)

# Good - defaultdict for repeated patterns
from collections import defaultdict
my_dict = defaultdict(list)
my_dict[key].append(value)  # No KeyError
```

---

## 10. Inefficient String Concatenation

### The Problem

```python
# Bad - Creates new string each iteration
result = ""
for item in items:
    result += str(item)
    result += ", "
```

### The Fix

```python
# Good - Join (much faster)
result = ", ".join(str(item) for item in items)

# Good - For simple cases
parts = [str(item) for item in items]
result = ", ".join(parts)
```

### Performance Impact

String concatenation in loops is O(n²) due to string immutability. Join is O(n).

---

## Quick Reference: Avoid These

| Anti-Pattern | Instead Use |
|-------------|-------------|
| `def func(items=[]):` | `def func(items=None):` then check `if items is None` |
| `except:` or `except Exception: pass` | `except SpecificError as e:` with logging |
| Modify list during `for item in items:` | List comprehension or iterate over `items[:]` |
| `"str %s" % val` | `f"str {val}"` (f-strings) |
| Manual file open/close | `with open(...) as f:` |
| `if x == None:` | `if x is None:` |
| Verbose loops for simple transforms | List/dict comprehensions |
| `for i in range(len(items)):` | `for i, item in enumerate(items):` |
| `result = ""; result += ...` in loop | `"".join(...)` |
| `if key in dict: dict[key]` | `dict.get(key, default)` |

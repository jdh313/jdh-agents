# Deep Modules in TDD

Canonical glossary for Module / Interface / Depth / Seam / Adapter / Leverage / Locality lives at `../../references/LANGUAGE.md`. This file applies that vocabulary to TDD specifically.

## What Makes a Module Deep

From "A Philosophy of Software Design":

**Deep module** = small interface + lots of implementation

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
│                     │
└─────────────────────┘
```

**Shallow module** = large interface + little implementation (avoid)

```
┌─────────────────────────────────┐
│       Large Interface           │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

For the formal definitions of Module, Interface, Depth, Seam, Adapter, Leverage, and Locality — see [`../../references/LANGUAGE.md`](../../references/LANGUAGE.md).

## Applying Depth to TDD

When designing interfaces during the planning phase, ask:

- Can I reduce the number of methods?
- Can I simplify the parameters?
- Can I hide more complexity inside?

The payoff is directly testable: a deep module has a small test surface. Fewer methods and simpler params mean simpler test setup — fewer fixtures, fewer mocks, fewer assertions about call order.

Depth also concentrates bugs. When a test fails on a deep module's interface, the failure points at one place. When a test fails on a shallow pass-through, the bug could be anywhere in the call chain the pass-through delegates to.

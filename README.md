# minimum_excluding_set_kit

Maintains a dynamic set of non-negative integers and reports the smallest missing value (the MEX) in O(1) after each add or remove.

```python
from minimum_excluding_set_kit import MinimumExcludingSet

s = MinimumExcludingSet()
s.add(0); s.add(1); s.add(2)
assert s.mex() == 3
s.remove(1)
assert s.mex() == 1
s.add(1)
assert s.mex() == 3
```

Exported names: `MinimumExcludingSet` with methods `add(value)`, `remove(value)`, `discard(value) -> bool`, `contains(value) -> bool`, `mex() -> int`, `clear()`, plus `__len__` and `__contains__`. The constructor accepts an optional `max_value` (default `1_000_000`) bounding the largest accepted integer; inserting anything larger raises `ValueError`.

## Why this exists

Allocators that hand out short-lived integer IDs (port numbers, temporary file indices, ephemeral session slots) often want the smallest currently-free value, not just any free value, so that identifiers stay compact and human-readable as slots churn. Scanning for the first hole on every request is wasteful; this library caches the contiguous-present prefix starting at zero so the common case (`mex`, `add` of a value past the prefix, `remove` of a value past the prefix) is O(1), with a lazy recompute only when a hole is punched inside the prefix.

The trade-off is memory: the internal cache is bounded by `max_value`, and the element set is proportional to how many values you actually hold. If your workload routinely inserts values in the billions, raise `max_value` deliberately — an accidental huge insert is treated as an error rather than silently bloating memory.

## Awkward edges

- Only **non-negative** integers are supported. Negative values raise `ValueError`; `bool` and `float` raise `TypeError` (booleans are not silently treated as ints).
- `remove` raises `KeyError` on absent values; use `discard` if you want no-throw semantics.
- The MEX is defined over `0, 1, 2, …`; if you need a different domain, translate before inserting.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.


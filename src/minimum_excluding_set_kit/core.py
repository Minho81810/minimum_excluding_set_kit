"""Core implementation of the minimum excluding set.

Design decision
---------------
This library tracks a dynamic set of **non-negative integers** and reports the
smallest non-negative integer that is NOT present in the set (a.k.a. the MEX).

For small, sparse workloads where individual elements are well under 10**6 a
straightforward Python ``set`` plus a tiny ``present_until`` cache gives O(1)
queries and O(1) updates in the common case while keeping memory proportional
to the number of stored elements rather than to the largest element seen.

We deliberately refuse negative values rather than trying to give them meaning,
and we cap values at a configurable ``max_value`` so an accidental huge insert
does not silently blow up memory.
"""


class MinimumExcludingSet:
    """Maintain a dynamic set of non-negative integers; report the smallest missing value.

    Parameters
    ----------
    max_value:
        Largest integer the set is allowed to hold. Defaults to 10**6, which
        keeps the ``present_until`` cache small while supporting the common case
        of page-slot / port-allocation style workloads. Raise this if you need
        larger ranges; the cache size is bounded by ``max_value``.
    """

    def __init__(self, max_value: int = 1_000_000) -> None:
        if max_value < 0:
            raise ValueError("max_value must be non-negative")
        self._max_value = max_value
        self._elements: set[int] = set()
        # Cached count of consecutive present values starting at 0. When an
        # element in [0, mex) is removed this cache is dropped; the next query
        # re-scans lazily. Keeping it lets the hot path stay O(1).
        self._present_until: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _recompute_present_until(self) -> None:
        """Rebuild ``_present_until`` from ``_elements``.

        Called only on the cold path (a removal inside the current prefix).
        Amortised O(1) per update because each newly scanned element is only
        scanned once until it is removed.
        """
        p = 0
        elems = self._elements
        while p in elems:
            p += 1
        self._present_until = p

    def _validate(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError("value must be an int")
        if value < 0:
            raise ValueError("value must be non-negative")
        if value > self._max_value:
            raise ValueError(
                f"value {value} exceeds max_value {self._max_value}"
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def add(self, value: int) -> None:
        """Insert ``value`` into the set. Idempotent."""
        self._validate(value)
        self._elements.add(value)
        if value == self._present_until:
            self._recompute_present_until()

    def remove(self, value: int) -> None:
        """Remove ``value``. Raises ``KeyError`` if absent."""
        self._validate(value)
        self._elements.remove(value)
        # If we just punched a hole in the present prefix, drop the cache so
        # the next query recomputes the correct (smaller) mex.
        if value < self._present_until:
            self._present_until = value

    def discard(self, value: int) -> bool:
        """Remove ``value`` if present; return whether it was actually removed."""
        self._validate(value)
        if value not in self._elements:
            return False
        self._elements.discard(value)
        if value < self._present_until:
            self._present_until = value
        return True

    def contains(self, value: int) -> bool:
        """Return True if ``value`` is currently in the set."""
        if not isinstance(value, int) or isinstance(value, bool):
            return False
        if value < 0 or value > self._max_value:
            return False
        return value in self._elements

    def mex(self) -> int:
        """Return the smallest non-negative integer NOT in the set."""
        return self._present_until

    def __len__(self) -> int:
        return len(self._elements)

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, int) or isinstance(item, bool):
            return False
        if item < 0 or item > self._max_value:
            return False
        return item in self._elements

    def clear(self) -> None:
        """Remove every element."""
        self._elements.clear()
        self._present_until = 0

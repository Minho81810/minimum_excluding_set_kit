"""Tests for MinimumExcludingSet."""

import unittest

from minimum_excluding_set_kit import MinimumExcludingSet


class TestMinimumExcludingSet(unittest.TestCase):
    def test_empty_returns_zero(self):
        s = MinimumExcludingSet()
        self.assertEqual(s.mex(), 0)
        self.assertEqual(len(s), 0)

    def test_add_then_fill_prefix(self):
        s = MinimumExcludingSet()
        for i in (0, 1, 2):
            s.add(i)
        self.assertEqual(s.mex(), 3)
        self.assertEqual(len(s), 3)

    def test_add_out_of_order(self):
        s = MinimumExcludingSet()
        s.add(5)
        s.add(0)
        s.add(2)
        self.assertEqual(s.mex(), 1)

    def test_duplicate_add_is_idempotent(self):
        s = MinimumExcludingSet()
        s.add(0)
        s.add(0)
        self.assertEqual(s.mex(), 1)
        self.assertEqual(len(s), 1)

    def test_remove_extending_prefix(self):
        # {0,1,2}; remove 2 -> mex drops to 2.
        s = MinimumExcludingSet()
        for i in (0, 1, 2):
            s.add(i)
        s.remove(2)
        self.assertEqual(s.mex(), 2)

    def test_remove_from_middle_of_prefix(self):
        # {0,1,2}; remove 1 -> mex drops to 1, even though 2 is still present.
        s = MinimumExcludingSet()
        for i in (0, 1, 2):
            s.add(i)
        s.remove(1)
        self.assertEqual(s.mex(), 1)

    def test_remove_zero(self):
        s = MinimumExcludingSet()
        for i in (0, 1, 2):
            s.add(i)
        s.remove(0)
        self.assertEqual(s.mex(), 0)

    def test_re_add_after_remove_restores_prefix(self):
        s = MinimumExcludingSet()
        for i in (0, 1, 2):
            s.add(i)
        s.remove(1)  # mex now 1
        s.add(1)
        self.assertEqual(s.mex(), 3)

    def test_discard_present(self):
        s = MinimumExcludingSet()
        for i in (0, 1):
            s.add(i)
        self.assertTrue(s.discard(0))
        self.assertFalse(s.contains(0))
        self.assertEqual(s.mex(), 0)

    def test_discard_absent(self):
        s = MinimumExcludingSet()
        s.add(0)
        self.assertFalse(s.discard(99))
        self.assertEqual(s.mex(), 1)

    def test_remove_absent_raises_keyerror(self):
        s = MinimumExcludingSet()
        s.add(0)
        with self.assertRaises(KeyError):
            s.remove(5)

    def test_contains_via_method_and_in(self):
        s = MinimumExcludingSet()
        s.add(3)
        self.assertTrue(s.contains(3))
        self.assertIn(3, s)
        self.assertFalse(s.contains(4))
        self.assertNotIn(4, s)

    def test_contains_rejects_invalid_types(self):
        s = MinimumExcludingSet()
        s.add(0)
        self.assertFalse(s.contains(-1))
        self.assertFalse(s.contains(True))
        self.assertFalse(s.contains(1.0))
        self.assertNotIn(True, s)

    def test_add_rejects_negative(self):
        s = MinimumExcludingSet()
        with self.assertRaises(ValueError):
            s.add(-1)

    def test_add_rejects_bool(self):
        s = MinimumExcludingSet()
        with self.assertRaises(TypeError):
            s.add(True)

    def test_add_rejects_float(self):
        s = MinimumExcludingSet()
        with self.assertRaises(TypeError):
            s.add(1.0)

    def test_max_value_default_accepts_million(self):
        s = MinimumExcludingSet()
        s.add(1_000_000)
        self.assertEqual(s.mex(), 0)

    def test_max_value_rejects_too_large(self):
        s = MinimumExcludingSet(max_value=10)
        with self.assertRaises(ValueError):
            s.add(11)

    def test_max_value_zero(self):
        s = MinimumExcludingSet(max_value=0)
        self.assertEqual(s.mex(), 0)
        s.add(0)
        self.assertEqual(s.mex(), 1)
        s.remove(0)
        self.assertEqual(s.mex(), 0)

    def test_negative_max_value_rejected(self):
        with self.assertRaises(ValueError):
            MinimumExcludingSet(max_value=-1)

    def test_clear(self):
        s = MinimumExcludingSet()
        for i in (0, 1, 2):
            s.add(i)
        s.clear()
        self.assertEqual(len(s), 0)
        self.assertEqual(s.mex(), 0)

    def test_large_gap(self):
        s = MinimumExcludingSet()
        s.add(1_000)
        self.assertEqual(s.mex(), 0)
        s.add(0)
        self.assertEqual(s.mex(), 1)

    def test_stress_interleaved(self):
        s = MinimumExcludingSet()
        expected = set()
        mex = 0
        for i in range(2000):
            if i % 3 == 0:
                s.add(i)
                expected.add(i)
                while mex in expected:
                    mex += 1
            elif i % 3 == 1 and expected:
                target = min(expected)
                s.remove(target)
                expected.discard(target)
                if target < mex:
                    mex = target
            self.assertEqual(s.mex(), mex, f"mismatch at step {i}")
            self.assertEqual(len(s), len(expected), f"len mismatch at step {i}")


if __name__ == "__main__":
    unittest.main()

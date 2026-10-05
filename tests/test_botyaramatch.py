import unittest
from typing import ClassVar

from botyaramatch import closest, closest_n, normalize, score, switch_layout


class TestScore(unittest.TestCase):
    def test_identical_and_empty(self):
        self.assertEqual(score("abc", "abc"), 1.0)
        self.assertEqual(score("", ""), 1.0)
        self.assertEqual(score("abc", ""), 0.0)

    def test_known_levenshtein_value(self):
        self.assertAlmostEqual(score("kitten", "sitting"), 1 - 3 / 7, places=6)

    def test_all_methods_in_range(self):
        for m in ("levenshtein", "jaro", "trigram"):
            s = score("martha", "marhta", method=m)
            self.assertTrue(0.0 <= s <= 1.0, m)

    def test_jaro_winkler_classic(self):
        self.assertAlmostEqual(score("martha", "marhta", method="jaro"), 0.9611, places=3)

    def test_unknown_method(self):
        with self.assertRaisesRegex(ValueError, "Unknown method 'nope'"):
            score("a", "b", method="nope")


class TestNormalize(unittest.TestCase):
    def test_normalize(self):
        self.assertEqual(normalize("  ЁЛКА   Большая "), "елка большая")

    def test_yo_ye_equal(self):
        self.assertEqual(score("ёлка", "елка"), 1.0)

    def test_layout(self):
        self.assertEqual(switch_layout("ghbdtn"), "привет")
        self.assertEqual(switch_layout("руддщ"), "hello")


class TestClosest(unittest.TestCase):
    FRUITS: ClassVar[list[str]] = ["яблоко", "груша", "банан"]

    def test_closest(self):
        self.assertEqual(closest("яблко", self.FRUITS), "яблоко")

    def test_closest_n_sorted(self):
        res = closest_n("pyton", ["java", "python", "ruby"], n=2)
        self.assertEqual(res[0][0], "python")
        self.assertEqual(len(res), 2)
        self.assertGreaterEqual(res[0][1], res[1][1])

    def test_threshold_and_default(self):
        self.assertIsNone(closest("zzzzzz", self.FRUITS, threshold=0.8))
        self.assertEqual(closest("zzzzzz", self.FRUITS, threshold=0.8, default="?"), "?")

    def test_layout_fix(self):
        self.assertEqual(closest("ghbdtn", ["привет", "пока"], layout_fix=True), "привет")
        self.assertEqual(closest("руддщ", ["hello", "world"], layout_fix=True), "hello")

    def test_empty_choices(self):
        self.assertEqual(closest_n("a", []), [])


if __name__ == "__main__":
    unittest.main()

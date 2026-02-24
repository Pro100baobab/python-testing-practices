import unittest
import math
from main import calculate_result, g


class TestCompositeFunction(unittest.TestCase):
    def test_left_branch(self):
        self.assertEqual(calculate_result(0, 5), 0.0)
        self.assertAlmostEqual(calculate_result(1, 5), math.sin(1))
        self.assertAlmostEqual(calculate_result(-1, 5), math.sin(-1))

    def test_right_branch(self):
        self.assertEqual(calculate_result(8, 5), 1.0)
        self.assertEqual(calculate_result(6, 5), -1.0)
        self.assertEqual(calculate_result(10, 5), 1/3)

    def test_boundary(self):
        """Проверка граничного значения x = n."""
        # n = 5, правая ветка
        self.assertEqual(calculate_result(5, 5), -0.5)
        # n = 7, правая ветка должна вернуть None (разрыв)
        self.assertIsNone(calculate_result(7, 7))
        # n = 7, x < 7 -> левая ветка
        self.assertAlmostEqual(calculate_result(6, 7), math.sin(6))

    def test_discontinuity1(self):
        self.assertRaises(ZeroDivisionError, g, 7)
        with self.assertRaises(ZeroDivisionError):
            g(7)

    def test_discontinuity(self):
        """Проверка точки разрыва x = 7."""
        # x = 7, n > 7 => левая ветка (sin(7))
        self.assertAlmostEqual(calculate_result(7, 10), math.sin(7))
        # x = 7, n <= 7 => правая ветка (None)
        self.assertIsNone(calculate_result(7, 5))
        self.assertIsNone(calculate_result(7, 7))

    def test_invalid_input(self):
        """Проверка реакции на некорректные типы данных."""
        with self.assertRaises(TypeError):
            calculate_result('a', 5)
        with self.assertRaises(TypeError):
            calculate_result(5, 'b')
        with self.assertRaises(TypeError):
            calculate_result(None, 5)

    def test_multiple_values_with_subtest(self):
        """Проверка множества значений с использованием subTest."""
        test_cases = [
            (0, 5, 0.0),                 # левая ветка, sin(0)
            (2, 5, math.sin(2)),         # левая ветка
            (5, 5, -0.5),                # граница, правая ветка
            (8, 5, 1.0),                 # правая ветка
            (7, 10, math.sin(7)),        # x=7, левая ветка
            (7, 5, None),                # x=7, правая ветка (разрыв)
            (7, 7, None),                # x=7, граница n=7 -> правая ветка (разрыв)
        ]
        for x, n, expected in test_cases:
            with self.subTest(x=x, n=n):
                if expected is None:
                    self.assertIsNone(calculate_result(x, n))
                else:
                    self.assertAlmostEqual(calculate_result(x, n), expected)


if __name__ == '__main__':
    unittest.main()

"""自動化測試（AI 使用聲明：由 ChatGPT／GPT-6 協助撰寫）。"""

import math
import unittest

from main import (
    derivative,
    exact_square_integral,
    gradient,
    hyperrectangle_volume,
    integral,
    monte_carlo_integral_1d,
    monte_carlo_integral_nd,
    numerical_integral_1d,
    riemann_integral_nd,
    sum_of_squares,
)


class TestWeek11Homework(unittest.TestCase):
    def test_01_derivative(self):
        self.assertAlmostEqual(derivative(lambda x: x**2, 2), 4.0, places=7)

    def test_02_one_dimension_riemann(self):
        self.assertAlmostEqual(numerical_integral_1d(lambda x: x**2, 0, 1), 1 / 3, delta=1e-8)

    def test_03_one_dimension_monte_carlo(self):
        value = monte_carlo_integral_1d(lambda x: x**2, 0, 1, samples=80_000, seed=7)
        self.assertAlmostEqual(value, 1 / 3, delta=0.01)

    def test_04_gradient(self):
        actual = gradient(sum_of_squares, [1, 2, 3])
        for got, expected in zip(actual, [2.0, 4.0, 6.0]):
            self.assertAlmostEqual(got, expected, delta=1e-8)

    def test_05_multidimensional_riemann(self):
        value = riemann_integral_nd(sum_of_squares, [0, 0], [1, 1], partitions=100)
        self.assertAlmostEqual(value, 2 / 3, delta=2e-5)

    def test_06_hyperrectangle_volume(self):
        self.assertEqual(hyperrectangle_volume([0, 0, 0], [2, 3, 4]), 24)

    def test_07_multidimensional_mc(self):
        value = monte_carlo_integral_nd(sum_of_squares, [0] * 3, [1] * 3, samples=80_000, seed=7)
        self.assertAlmostEqual(value, 1, delta=0.02)

    def test_08_mc_volume(self):
        value = monte_carlo_integral_nd(lambda x: 1.0, [0, 0, 0], [2, 3, 4], samples=1000)
        self.assertAlmostEqual(value, 24, places=12)

    def test_09_all_dimensions_riemann(self):
        for n, m in ((1, 1000), (2, 100), (5, 10), (100, 100)):
            with self.subTest(n=n):
                got = integral(sum_of_squares, [0] * n, [1] * n)
                expected_midpoint = n * (1 / 3 - 1 / (12 * m**2))
                self.assertAlmostEqual(got, expected_midpoint, delta=1e-8)

    def test_10_all_dimensions_monte_carlo(self):
        for n in (1, 2, 5, 100):
            with self.subTest(n=n):
                got = monte_carlo_integral_nd(
                    sum_of_squares, [0] * n, [1] * n, samples=50_000, seed=2026+n
                )
                self.assertAlmostEqual(got, exact_square_integral(n), delta=0.2)

    def test_11_separable_reduction_matches_full_midpoint_grid(self):
        # 直接比較「完整 n 維網格」與「分離求和」，確保 100 維最佳化在數學上等價。
        n = 4
        m = 7
        full = riemann_integral_nd(sum_of_squares, [0.2] * n, [1.3] * n, partitions=m)
        # 使用 8 維、每維 10 格會超過 2,000,000，不便對同一網格直接比較；
        # 這裡藉由相同的 4 維公式直接計算因式分解後的黎曼和。
        width = (1.3 - 0.2) / m
        avg_1d = sum((0.2 + (k + .5) * width) ** 2 for k in range(m)) / m
        reduced = (1.3 - 0.2) ** n * n * avg_1d
        self.assertAlmostEqual(full, reduced, places=11)

    def test_12_general_function_supported(self):
        f = lambda v: v[0] * v[1]
        value = integral(f, [0, 0], [1, 1], partitions=20)
        self.assertAlmostEqual(value, 1 / 4, places=10)

    def test_13_nonseparable_large_grid_rejected(self):
        with self.assertRaisesRegex(ValueError, "網格點"):
            integral(lambda v: v[0] * v[1], [0] * 100, [1] * 100)

    def test_14_invalid_bounds(self):
        with self.assertRaises(ValueError):
            integral(sum_of_squares, [0, 0], [1])
        with self.assertRaises(ValueError):
            monte_carlo_integral_nd(sum_of_squares, [1], [0])
        with self.assertRaises(ValueError):
            integral(sum_of_squares, [], [])

    def test_15_invalid_parameters(self):
        with self.assertRaises(ValueError):
            derivative(lambda x: x, 0, h=0)
        with self.assertRaises(ValueError):
            numerical_integral_1d(lambda x: x, 0, 1, partitions=0)
        with self.assertRaises(ValueError):
            monte_carlo_integral_nd(sum_of_squares, [0], [1], samples=0)

    def test_16_zero_volume(self):
        self.assertEqual(integral(sum_of_squares, [0, 0], [0, 1]), 0.0)
        self.assertEqual(monte_carlo_integral_nd(sum_of_squares, [0], [0]), 0.0)

    def test_17_monte_carlo_reproducibility(self):
        params = (sum_of_squares, [0, 0], [1, 1])
        self.assertEqual(
            monte_carlo_integral_nd(*params, samples=1000, seed=99),
            monte_carlo_integral_nd(*params, samples=1000, seed=99),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""第 11 週習題：數值微積分與蒙地卡羅隨機法。

AI 使用聲明：本程式使用 OpenAI ChatGPT（GPT-6）協助撰寫程式、註解與測試。
所有範例皆可執行，請在繳交前自行確認、理解並遵守課程的 AI 使用規範。
依賴：僅使用 Python 標準函式庫（Python 3.10 以上）。
"""

from __future__ import annotations

import itertools
import math
import random
from collections.abc import Callable, Sequence


# 完整的 n 維黎曼網格最多枚舉這麼多個點，避免 100 維造成記憶體／時間爆炸。
MAX_GRID_POINTS = 2_000_000


def _validate_bounds(
    low: Sequence[float], high: Sequence[float]
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """檢查 n 維上下界；兩者必須是同樣長度的非空陣列。"""
    if len(low) == 0 or len(low) != len(high):
        raise ValueError("low 與 high 必須是長度相同、至少包含一維的陣列")
    lows = tuple(float(x) for x in low)
    highs = tuple(float(x) for x in high)
    for a, b in zip(lows, highs):
        if not math.isfinite(a) or not math.isfinite(b):
            raise ValueError("積分上下界必須為有限數值")
        if b < a:
            raise ValueError("每一維都必須滿足 low[i] <= high[i]")
    return lows, highs


def _positive_integer(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} 必須是正整數")


def _positive_step(h: float) -> None:
    if not math.isfinite(h) or h <= 0:
        raise ValueError("微分步長 h 必須為正的有限數值")


# 第 1 題：單變數數值微分（中央差分）與數值積分（中點黎曼和）
def derivative(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    """中央差分公式：f'(x) ≈ [f(x+h)-f(x-h)]/(2h)。"""
    _positive_step(h)
    return (f(x + h) - f(x - h)) / (2.0 * h)


def numerical_integral_1d(
    f: Callable[[float], float], low: float, high: float, partitions: int = 10_000
) -> float:
    """單變數積分：將 [low, high] 切成 partitions 等份，取每份中點。"""
    _positive_integer(partitions, "partitions")
    (a,), (b,) = _validate_bounds([low], [high])
    dx = (b - a) / partitions
    return dx * math.fsum(f(a + (k + 0.5) * dx) for k in range(partitions))


# 第 2 題：單變數蒙地卡羅積分
def monte_carlo_integral_1d(
    f: Callable[[float], float],
    low: float,
    high: float,
    samples: int = 50_000,
    seed: int = 42,
) -> float:
    """對 [low, high] 均勻抽樣，以區間長度乘上 f 的樣本平均。"""
    return monte_carlo_integral_nd(
        lambda xs: f(xs[0]), [low], [high], samples=samples, seed=seed
    )


# 第 3 題：n 變數數值梯度與超體積
def gradient(
    f: Callable[[Sequence[float]], float],
    point: Sequence[float],
    h: float = 1e-5,
) -> list[float]:
    """各座標使用中央差分，回傳 [∂f/∂x1, ..., ∂f/∂xn]。"""
    _positive_step(h)
    if not point:
        raise ValueError("point 至少要有一個座標")
    p = list(point)
    result: list[float] = []
    for i in range(len(p)):
        right = p.copy()
        left = p.copy()
        right[i] += h
        left[i] -= h
        result.append((f(right) - f(left)) / (2.0 * h))
    return result


def hyperrectangle_volume(low: Sequence[float], high: Sequence[float]) -> float:
    """n 維長方體超體積：∏(high[i] - low[i])。"""
    lows, highs = _validate_bounds(low, high)
    return math.prod(b - a for a, b in zip(lows, highs))


def riemann_integral_nd(
    f: Callable[[Sequence[float]], float],
    low: Sequence[float],
    high: Sequence[float],
    partitions: int = 10,
    max_grid_points: int = MAX_GRID_POINTS,
) -> float:
    """一般 n 維中點黎曼和：枚舉所有 partitions**n 個小超立方體。

    此函數適合維度較低、網格可完整枚舉的情況。若超出點數上限，
    直接報錯，不會假裝少量抽樣等於完整的黎曼網格。
    """
    _positive_integer(partitions, "partitions")
    _positive_integer(max_grid_points, "max_grid_points")
    lows, highs = _validate_bounds(low, high)
    dimension = len(lows)
    number_of_cells = partitions**dimension
    if number_of_cells > max_grid_points:
        raise ValueError(
            f"完整黎曼網格需要 {partitions}^{dimension} 個點，"
            f"超過上限 {max_grid_points:,}；請減少切割數或使用可分離函數最佳化"
        )

    volume = math.prod(b - a for a, b in zip(lows, highs))
    if volume == 0.0:
        return 0.0
    widths = [(b - a) / partitions for a, b in zip(lows, highs)]
    result = 0.0
    for indices in itertools.product(range(partitions), repeat=dimension):
        midpoint = [
            lows[i] + (indices[i] + 0.5) * widths[i] for i in range(dimension)
        ]
        result += f(midpoint)
    return volume * (result / number_of_cells)


# 第 4、6 題：n 變數蒙地卡羅積分
def monte_carlo_integral_nd(
    f: Callable[[Sequence[float]], float],
    low: Sequence[float],
    high: Sequence[float],
    samples: int = 50_000,
    seed: int = 42,
) -> float:
    """n 維蒙地卡羅積分：超體積 × 均勻亂數樣本之函數平均。"""
    _positive_integer(samples, "samples")
    lows, highs = _validate_bounds(low, high)
    volume = math.prod(b - a for a, b in zip(lows, highs))
    if volume == 0.0:
        return 0.0

    generator = random.Random(seed)
    widths = tuple(b - a for a, b in zip(lows, highs))
    total = 0.0
    for _ in range(samples):
        point = [a + width * generator.random() for a, width in zip(lows, widths)]
        total += f(point)
    return volume * total / samples


# 第 5 題：integral(f, low, high) 自動由 low/high 長度判斷維度。
# 對 100 維的「加法可分離」函數，可把完整網格黎曼和代數化簡為一維和。
def _separable_riemann_integral(
    f: Callable[[Sequence[float]], float],
    lows: Sequence[float],
    highs: Sequence[float],
    partitions: int,
) -> float:
    component = getattr(f, "additive_component", None)
    if not callable(component):
        raise ValueError("此函數未宣告 additive_component，無法以加法可分離方式簡化")

    constant = float(getattr(f, "additive_constant", 0.0))
    average = constant
    for i, (a, b) in enumerate(zip(lows, highs)):
        width = (b - a) / partitions
        average += math.fsum(
            component(i, a + (k + 0.5) * width) for k in range(partitions)
        ) / partitions
    return math.prod(b - a for a, b in zip(lows, highs)) * average


def integral(
    f: Callable[[Sequence[float]], float],
    low: Sequence[float],
    high: Sequence[float],
    partitions: int | None = None,
) -> float:
    """n 維中點黎曼積分；n 由 len(low) = len(high) 自動決定。

    直接呼叫 integral(f, low, high) 即可。若 partitions 不指定，為了讓
    1、2、5、100 維的例子都能實際執行，依維度選取合理的切割數。
    超大網格僅在 f 宣告加法可分離結構時作「數學等價」最佳化。
    """
    lows, highs = _validate_bounds(low, high)
    n = len(lows)
    if partitions is None:
        partitions = 1000 if n == 1 else 100 if n == 2 else 10 if n <= 5 else 100
    _positive_integer(partitions, "partitions")
    number_of_cells = partitions**n

    if number_of_cells > MAX_GRID_POINTS:
        if callable(getattr(f, "additive_component", None)):
            return _separable_riemann_integral(f, lows, highs, partitions)
        raise ValueError(
            f"{n} 維使用每維 {partitions} 等份，需要 {partitions}^{n} 個網格點。"
            "一般函數無法直接完整枚舉；請降低 partitions，或提供已知"
            "加法可分離函數的 additive_component，或改用蒙地卡羅法。"
        )
    return riemann_integral_nd(f, lows, highs, partitions=partitions)


def sum_of_squares(xs: Sequence[float]) -> float:
    """題目指定的 f(x1, ..., xn) = x1² + x2² + ... + xn²。"""
    return sum(x * x for x in xs)


def _square_component(index: int, value: float) -> float:
    """宣告 f(x) 是各維 g_i(x_i) = x_i² 的總和（index 是座標索引）。"""
    return value * value


# 只有「已經知道」具有加法可分離結構的函數才可以宣告這兩項屬性。
# 這不是估測可分離性，而是提供數學上成立的代數分解供 100 維黎曼和使用。
sum_of_squares.additive_component = _square_component  # type: ignore[attr-defined]
sum_of_squares.additive_constant = 0.0  # type: ignore[attr-defined]


def exact_square_integral(dimension: int) -> float:
    """[0,1]^n 上 sum(x_i²) 的解析解是 n/3。"""
    _positive_integer(dimension, "dimension")
    return dimension / 3.0


def main() -> None:
    print("第 11 週習題：數值微積分、黎曼積分與蒙地卡羅法")
    print("AI 使用聲明：本程式由 ChatGPT（GPT-6）協助撰寫與測試。")

    print("\n[第 1 題] 單變數數值微分與積分：f(x)=x²")
    print(f"  f'(2) 中央差分 = {derivative(lambda x: x*x, 2.0):.8f}，解析解 = 4")
    print(
        "  ∫[0,1] x² dx 中點黎曼 = "
        f"{numerical_integral_1d(lambda x: x*x, 0.0, 1.0):.8f}，解析解 = 0.33333333"
    )

    print("\n[第 2 題] 單變數蒙地卡羅積分：f(x)=x²，區間 [0,1]")
    print(
        "  估計值 = "
        f"{monte_carlo_integral_1d(lambda x: x*x, 0, 1, samples=50_000, seed=42):.8f}"
        "，解析解 = 0.33333333"
    )

    print("\n[第 3 題] n 變數梯度、數值積分與超體積")
    print(f"  梯度 ∇f(1,2,3) = {[round(x, 6) for x in gradient(sum_of_squares, [1,2,3])]}，解析解 = [2,4,6]")
    print(
        "  二維積分 ∫[0,1]²(x²+y²) dxdy = "
        f"{riemann_integral_nd(sum_of_squares, [0,0], [1,1], partitions=100):.8f}"
        "，解析解 = 0.66666667"
    )
    print(
        "  三維長方體超體積 [0,2]×[0,3]×[0,4] = "
        f"{hyperrectangle_volume([0,0,0], [2,3,4]):.0f}，解析解 = 24"
    )

    print("\n[第 4 題] n 變數蒙地卡羅積分與超體積")
    print(
        "  三維積分 ∫[0,1]³(x²+y²+z²) dV = "
        f"{monte_carlo_integral_nd(sum_of_squares, [0]*3, [1]*3, samples=50_000, seed=42):.8f}"
        "，解析解 = 1"
    )
    print(
        "  三維體積 ∫[0,2]×[0,3]×[0,4] 1 dV = "
        f"{monte_carlo_integral_nd(lambda x: 1.0, [0,0,0], [2,3,4], samples=50_000, seed=42):.8f}"
        "，解析解 = 24"
    )

    print("\n[第 5、6 題] 比較 n 維中點黎曼積分與蒙地卡羅積分")
    print("  f(x)=x1²+...+xn²，所有維度 low=0、high=1，解析解為 n/3")
    print("  n   黎曼(m)        黎曼結果        蒙地卡羅(N)        MC結果          解析解")
    for n in (1, 2, 5, 100):
        low = [0.0] * n
        high = [1.0] * n
        m = 1000 if n == 1 else 100 if n in (2, 100) else 10
        monte_carlo_samples = 50_000
        value_riemann = integral(sum_of_squares, low, high)
        value_mc = monte_carlo_integral_nd(
            sum_of_squares, low, high, samples=monte_carlo_samples, seed=2026 + n
        )
        print(
            f"  {n:>3}  {m:>6}      {value_riemann:>12.8f}      "
            f"{monte_carlo_samples:>9}      {value_mc:>12.8f}      {exact_square_integral(n):>12.8f}"
        )
    print("\n  說明：100 維黎曼結果利用可分離加法的代數恆等式，仍與完整中點網格和相等。")
    print("  說明：蒙地卡羅為隨機近似；固定 seed 可重現相同結果。")


if __name__ == "__main__":
    main()

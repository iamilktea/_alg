"""方法 3：模擬退火法，採用 2-opt 鄰居及 Metropolis 接受機率。"""

from __future__ import annotations

import math
import random

import numpy as np

from tsp_common import random_route, route_length, validate_distance_matrix


def solve(distance_matrix, seed=42, *, iterations=30000,
          initial_temperature=None, final_temperature=None):
    """以幾何降溫控制接受較差解的機率，回傳搜尋中的歷史最佳路徑。

    預設起溫為正距離的中位數，終溫為起溫的 1/10000；全零距離
    則使用起溫 1。history 只記錄新的最佳完整路徑，metadata 中的
    history_steps 記錄它們出現於第幾次候選。沒有追加其他改良方法。
    """
    distances = validate_distance_matrix(distance_matrix)
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 1:
        raise ValueError("iterations 必須是正整數。")
    positive_edges = distances[distances > 0]
    if initial_temperature is None:
        initial_temperature = float(np.median(positive_edges)) if positive_edges.size else 1.0
    initial_temperature = float(initial_temperature)
    if not math.isfinite(initial_temperature) or initial_temperature <= 0:
        raise ValueError("initial_temperature 必須是有限且大於 0 的數值。")
    if final_temperature is None:
        # 即使距離非常小，也避免預設終溫下溢為 0。
        final_temperature = max(initial_temperature * 1e-4, float(np.nextafter(0.0, 1.0)))
    final_temperature = float(final_temperature)
    if (not math.isfinite(final_temperature) or final_temperature <= 0
            or final_temperature > initial_temperature):
        raise ValueError("final_temperature 必須大於 0 且不高於 initial_temperature。")

    n = len(distances)
    route = random_route(n, seed)
    initial_route = route.copy()
    current_distance = route_length(route, distances)
    best_route = route.copy()
    best_distance = current_distance
    history = [best_distance]
    history_steps = [0]
    rng = random.Random(seed)
    accepted_moves = 0
    accepted_uphill = 0
    evaluated_neighbors = 0
    log_start = math.log(initial_temperature)
    log_end = math.log(final_temperature)
    temperature = initial_temperature

    # 1～3 個城市的對稱 TSP，固定起點後各可行巡迴長度相同。
    if n > 3:
        for step in range(iterations):
            fraction = step / max(iterations - 1, 1)
            temperature = math.exp(log_start + fraction * (log_end - log_start))
            i, j = sorted(rng.sample(range(1, n), 2))
            candidate = route.copy()
            candidate[i:j + 1] = reversed(candidate[i:j + 1])
            candidate_distance = route_length(candidate, distances)
            delta = candidate_distance - current_distance
            evaluated_neighbors += 1

            # 較短／等長直接接受；較長則以 exp(-delta / T) 的機率接受。
            if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                route = candidate
                current_distance = candidate_distance
                accepted_moves += 1
                if delta > 0:
                    accepted_uphill += 1
                if current_distance < best_distance:
                    best_route = route.copy()
                    best_distance = current_distance
                    history.append(best_distance)
                    history_steps.append(step + 1)

    return {
        "route": best_route,
        "distance": float(best_distance),
        "history": history,
        "metadata": {
            "initial_route": initial_route,
            "initial_distance": history[0],
            "iterations": iterations,
            "evaluated_neighbors": evaluated_neighbors,
            "accepted_moves": accepted_moves,
            "accepted_uphill": accepted_uphill,
            "initial_temperature": initial_temperature,
            "target_final_temperature": final_temperature,
            "last_temperature": temperature,
            "final_distance": float(current_distance),
            "history_steps": history_steps,
            "stop_reason": "trivial_small_instance" if n <= 3 else "iteration_limit",
            "neighborhood": "2-opt reversal",
            "selection": "Metropolis acceptance",
        },
    }


if __name__ == "__main__":
    from tsp_common import run_cli

    run_cli(solve, method_key="simulated_annealing")

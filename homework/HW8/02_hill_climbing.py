"""方法 2：爬山演算法，以交換兩個城市作為鄰域，選取最佳改善。"""

from __future__ import annotations

import math

from tsp_common import random_route, route_length, validate_distance_matrix


def solve(distance_matrix, seed=42, *, max_iterations=1000, tolerance=1e-12):
    """反覆選取所有兩城交換鄰居中最短者，只接受嚴格改善。

    TSP 要最小化距離，因此此處的爬山相當於最大化負距離。
    與方法 1 不同：此方法交換兩個位置，而非反轉整個區段，且
    必須看完當輪所有鄰居才移動。只用一個隨機起點，沒有重新啟動。
    """
    distances = validate_distance_matrix(distance_matrix)
    if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or max_iterations < 1:
        raise ValueError("max_iterations 必須是正整數。")
    tolerance = float(tolerance)
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance 必須是有限且非負的數值。")

    n = len(distances)
    route = random_route(n, seed)
    initial_route = route.copy()
    distance = route_length(route, distances)
    history = [distance]
    moves = 0
    evaluated_neighbors = 0
    stop_reason = "iteration_limit"

    while moves < max_iterations:
        best_route = None
        best_distance = distance
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                candidate = route.copy()
                candidate[i], candidate[j] = candidate[j], candidate[i]
                candidate_distance = route_length(candidate, distances)
                evaluated_neighbors += 1
                if candidate_distance < best_distance - tolerance:
                    best_route = candidate
                    best_distance = candidate_distance
        if best_route is None:
            stop_reason = "local_optimum"
            break
        route, distance = best_route, best_distance
        moves += 1
        history.append(distance)

    return {
        "route": route,
        "distance": float(distance),
        "history": history,
        "metadata": {
            "initial_route": initial_route,
            "initial_distance": history[0],
            "accepted_improvements": moves,
            "evaluated_neighbors": evaluated_neighbors,
            "max_iterations": max_iterations,
            "tolerance": tolerance,
            "stop_reason": stop_reason,
            "history_steps": list(range(len(history))),
            "neighborhood": "swap two cities",
            "selection": "best improvement",
        },
    }


if __name__ == "__main__":
    from tsp_common import run_cli

    run_cli(solve, method_key="hill_climbing")

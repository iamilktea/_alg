"""方法 1：改良法，以首個改善策略進行 2-opt 路徑反轉。"""

from __future__ import annotations

import math

from tsp_common import random_route, route_length, validate_distance_matrix


def solve(distance_matrix, seed=42, *, max_iterations=1000, tolerance=1e-12):
    """由隨機路徑開始，每次採用掃描到的第一個較短 2-opt 鄰居。

    固定城市 0 為起點。反轉 route[i:j+1]，等同拆除兩條邊再交叉
    接回；距離矩陣必須對稱。沒有可改善的鄰居，或達到改良次數
    上限時停止。結果中的 route 不重複附加終點 0，distance 包含回程。
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
        improved = False
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                # 對稱 TSP 中，反轉全部非起點城市只是整圈反向行走。
                if i == 1 and j == n - 1:
                    continue
                evaluated_neighbors += 1
                a, b = route[i - 1], route[i]
                c, d = route[j], route[(j + 1) % n]
                delta = float(distances[a, c] + distances[b, d]
                              - distances[a, b] - distances[c, d])
                if delta >= -tolerance:
                    continue

                candidate = route.copy()
                candidate[i:j + 1] = reversed(candidate[i:j + 1])
                candidate_distance = route_length(candidate, distances)
                # 以完整路徑重算，避免長時間累加 delta 產生誤差。
                if candidate_distance < distance - tolerance:
                    route, distance = candidate, candidate_distance
                    moves += 1
                    history.append(distance)
                    improved = True
                    break
            if improved:
                break
        if not improved:
            stop_reason = "local_optimum"
            break

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
            "neighborhood": "2-opt reversal",
            "selection": "first improvement",
        },
    }


if __name__ == "__main__":
    from tsp_common import run_cli

    run_cli(solve, method_key="improvement")


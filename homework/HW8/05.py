"""方法 5：貪婪演算法，每一步選擇最近的未拜訪城市。"""

from __future__ import annotations

from tsp_common import route_length, validate_distance_matrix


def solve(distance_matrix, seed=42):
    """從城市 0 出發；距離相同時選城市編號較小者。

    seed 只為保持五種方法的呼叫介面一致，此方法不使用隨機數。
    每個城市選擇一次，最後返回城市 0。history 只放完整巡迴距離，
    不把尚未走完的部分路程誤當成 TSP 解。
    """
    distances = validate_distance_matrix(distance_matrix)
    n = len(distances)
    route = [0]
    unvisited = set(range(1, n))
    evaluated_choices = 0

    while unvisited:
        current = route[-1]
        evaluated_choices += len(unvisited)
        next_city = min(unvisited, key=lambda city: (distances[current, city], city))
        route.append(next_city)
        unvisited.remove(next_city)

    distance = route_length(route, distances)
    return {
        "route": route,
        "distance": float(distance),
        "history": [float(distance)],
        "metadata": {
            "start_city": 0,
            "evaluated_choices": evaluated_choices,
            "tie_break": "smallest city index",
            "history_steps": [n - 1],
            "stop_reason": "all_cities_visited",
        },
    }


if __name__ == "__main__":
    from tsp_common import run_cli

    run_cli(solve, method_key="greedy")

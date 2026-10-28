"""方法 4：連續指派鬆弛 + 投影梯度下降 + 線性指派解碼。

P[i, k] 代表城市 i 放在位置 k 的連續權重。將 D 除以最大距離後，最小化
  F(P) = sum_k p_k.T D p_(k+1)
       + a/2 * (||P 1 - 1||² + ||P.T 1 - 1||²)
       + b * sum(P * (1 - P)),  0 <= P <= 1。
位置 k 以模 n 計算，因此目標包含回到起點的距離。
固定城市 0 在位置 0；其餘行列和約束以有限懲罰近似，並非精確滿足。
最後以線性指派解碼，保證城市不重複。這是啟發式，不保證 TSP 最佳解。
"""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from tsp_common import validate_distance_matrix


def objective_and_gradient(
    p: np.ndarray,
    normalized_distance: np.ndarray,
    constraint_penalty: float = 20.0,
    binary_penalty: float = 0.25,
) -> tuple[float, np.ndarray]:
    """回傳代理目標及對完整 P 的解析梯度，方便用有限差分驗證。

    路長梯度為 D @ roll(P, -1) + D.T @ roll(P, 1)。
    固定位置的分量也會回傳；實際下降時由投影函式固定它們。
    """
    next_p = np.roll(p, -1, axis=1)
    previous_p = np.roll(p, 1, axis=1)
    row_error = p.sum(axis=1) - 1.0
    col_error = p.sum(axis=0) - 1.0
    loss = float(np.sum(p * (normalized_distance @ next_p)))
    loss += constraint_penalty / 2 * float(
        row_error @ row_error + col_error @ col_error
    )
    loss += binary_penalty * float(np.sum(p * (1.0 - p)))
    grad = normalized_distance @ next_p + normalized_distance.T @ previous_p
    grad += constraint_penalty * (row_error[:, None] + col_error[None, :])
    grad += binary_penalty * (1.0 - 2.0 * p)
    return loss, grad


def _project(p: np.ndarray) -> np.ndarray:
    """投影到盒狀限制，同時固定城市 0 在位置 0。"""
    q = np.clip(p, 0.0, 1.0)
    q[0, :] = 0.0
    q[:, 0] = 0.0
    q[0, 0] = 1.0
    return q


def _decode(p: np.ndarray) -> list[int]:
    """最大化指派權重；每個城市／位置恰好使用一次。"""
    city_indices, positions = linear_sum_assignment(-p[1:, 1:])
    route = np.empty(len(p), dtype=int)
    route[0] = 0
    route[positions + 1] = city_indices + 1
    return route.tolist()


def solve(
    distance_matrix: np.ndarray,
    seed: int = 42,
    *,
    restarts: int = 8,
    max_iterations: int = 1200,
    constraint_penalty: float = 20.0,
    binary_penalty: float = 0.25,
    learning_rate: float = 0.25,
    tolerance: float = 1e-6,
    decode_every: int = 20,
) -> dict:
    """回傳最好的已解碼巡迴，不對路線追加離散局部搜尋。

    history 為各次解碼後的「歷來最短實際路長」，不是代理目標。
    metadata['objective_traces'] 記錄各次重新初始化的代理目標。
    Armijo 回溯只保證所接受的連續代理目標下降；解碼路長可能上升。
    """
    d = validate_distance_matrix(distance_matrix)
    for name, value in (("restarts", restarts), ("max_iterations", max_iterations),
                        ("decode_every", decode_every)):
        if not isinstance(value, (int, np.integer)) or isinstance(value, bool) or value < 1:
            raise ValueError(f"{name} 必須是正整數。")
    if not all(np.isfinite(v) and v > 0 for v in
               (constraint_penalty, learning_rate, tolerance)):
        raise ValueError("懲罰係數、學習率與容忍值必須是有限正數。")
    if not np.isfinite(binary_penalty) or binary_penalty < 0:
        raise ValueError("binary_penalty 必須是有限非負數。")

    n = len(d)
    scale = float(d.max()) or 1.0
    normalized_distance = d / scale
    rng = np.random.default_rng(seed)
    best_route: list[int] = list(range(n))
    best_distance = float("inf")
    best_source: dict = {}
    history: list[float] = []
    objective_traces: list[list[float]] = []
    runs: list[dict] = []

    def evaluate(p: np.ndarray) -> tuple[float, np.ndarray]:
        return objective_and_gradient(
            p, normalized_distance, constraint_penalty, binary_penalty
        )

    def record(p: np.ndarray, restart: int, iteration: int) -> None:
        nonlocal best_route, best_distance, best_source
        route = _decode(p)
        length = float(d[route, np.roll(route, -1)].sum())
        if length < best_distance:
            best_route, best_distance = route, length
            best_source = {"restart": restart + 1, "iteration": iteration}
        history.append(best_distance)

    for restart in range(restarts):
        # 中性隨機連續權重；不使用貪婪法或其他離散方法作為起始路線。
        p = np.zeros((n, n), dtype=float)
        p[0, 0] = 1.0
        if n > 1:
            q = np.exp(rng.normal(size=(n - 1, n - 1)))
            for _ in range(20):
                q /= q.sum(axis=1, keepdims=True)
                q /= q.sum(axis=0, keepdims=True)
            p[1:, 1:] = q
        value, grad = evaluate(p)
        trace = [value]
        record(p, restart, 0)
        step = learning_rate
        converged = False
        stop_reason = "max_iterations"
        iterations = 0

        for iteration in range(1, max_iterations + 1):
            # 投影梯度映射為 0，才表示抵達這個盒狀問題的一階停駐點。
            residual = float(np.max(np.abs(p - _project(p - grad))))
            if residual <= tolerance:
                converged, stop_reason = True, "projected_gradient_tolerance"
                break
            trial_step = min(step, learning_rate)
            for _ in range(60):
                candidate = _project(p - trial_step * grad)
                delta = candidate - p
                candidate_value, candidate_grad = evaluate(candidate)
                if candidate_value <= value + 1e-4 * float(np.sum(grad * delta)):
                    break
                trial_step *= 0.5
            else:
                stop_reason = "line_search_failed"
                break

            p, value, grad = candidate, candidate_value, candidate_grad
            iterations = iteration
            step = min(trial_step * 1.5, learning_rate)
            if iteration % decode_every == 0:
                trace.append(value)
                record(p, restart, iteration)

        # 最終一步也解碼，避免遺漏停止點的可行巡迴。
        trace.append(value)
        record(p, restart, iterations)
        objective_traces.append(trace)
        residual = float(np.max(np.abs(p - _project(p - grad))))
        if residual <= tolerance:
            converged, stop_reason = True, "projected_gradient_tolerance"
        runs.append({
            "restart": restart + 1, "iterations": iterations,
            "converged": converged, "stop_reason": stop_reason,
            "projected_gradient_residual": residual,
            "row_sum_max_error": float(np.max(np.abs(p.sum(axis=1) - 1))),
            "column_sum_max_error": float(np.max(np.abs(p.sum(axis=0) - 1))),
            "final_objective": value,
        })

    return {
        "route": best_route, "distance": best_distance, "history": history,
        "metadata": {
            "model": "penalized_continuous_assignment",
            "distance_scale": scale,
            "constraint_penalty": constraint_penalty,
            "binary_penalty": binary_penalty,
            "learning_rate": learning_rate, "tolerance": tolerance,
            "restarts": restarts, "max_iterations": max_iterations,
            "decode_every": decode_every,
            "best_source": best_source,
            "history_unit": "best discrete distance after each decoding",
            "objective_traces": objective_traces,
            "converged": all(run["converged"] for run in runs),
            "runs": runs,
        },
    }


if __name__ == "__main__":
    from tsp_common import run_cli

    run_cli(solve, method_key="gradient_descent")

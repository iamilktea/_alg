# Unified Iteration Framework (全系列經典迭代演算法統一抽象框架)

這份文件展示了如何利用「抽象化」與「函數式程式設計（Functional Programming）」的概念，將各種看似毫無關聯的數學與工程演算法，統一在一個核心的「迭代框架」之下。

透過單一的通用迭代函數，本專案成功實作了 9 種橫跨數值分析、線性代數、機器學習與圖論的經典演算法。

---

## 1. 核心架構：通用迭代函數

整個專案的心臟是 `generic_iterator` 函數。它不關心正在解決什麼具體問題，只負責嚴格執行「更新狀態」與「檢查收斂」的迴圈。

### 參數說明：
* **`transition_func` (狀態推進函數)**: 定義如何從「目前狀態」計算出「下一步狀態」。即數學上的 $x_{n+1} = f(x_n)$。
* **`is_converged` (收斂判定函數)**: 回傳布林值 (True/False)，判斷新舊狀態之間的差異是否已經小到可以停止計算，或達到終止條件。
* **`initial_state` (初始狀態)**: 迭代的起點，支援純量（數字）、向量、矩陣，甚至 Tuple。
* **`max_iter` (最大迭代次數)**: 安全機制，防止遇到無法收斂的問題時產生無窮迴圈。

---

## 2. 九種經典演算法實作解析

本專案將以下 9 種經典演算法無縫套用至通用框架中：

### 2.1 二維不動點迭代法 (Fixed-Point Iteration)
* **用途**：求解聯立方程式的根。
* **狀態轉移**：將二維變數帶入線性轉換矩陣產生新狀態。
* **收斂條件**：新舊向量的歐幾里得距離（L2 Norm）小於 $10^{-6}$。

### 2.2 牛頓法求根 (Newton's Method)
* **用途**：快速尋找非線性方程式的根（示範解 $x^2 - 4 = 0$）。
* **狀態轉移**：利用切線公式 $x_{new} = x - \frac{f(x)}{f'(x)}$ 進行更新。
* **收斂條件**：新舊 $x$ 值的絕對差值小於 $10^{-6}$。

### 2.3 高斯-賽得爾法 (Gauss-Seidel Linear Solver)
* **用途**：解大型線性方程組 $Ax = b$。
* **狀態轉移**：輪流更新向量中的每一個元素，且在計算當下**立即使用**其他元素最新被更新過的值。
* **收斂條件**：新舊向量之間的最大絕對誤差（L-infinity Norm）小於 $10^{-6}$。

### 2.4 冪次迭代法 (Power Iteration)
* **用途**：尋找矩陣的「最大特徵值」與對應的「主特徵向量」。
* **狀態轉移**：矩陣乘上目前向量，並將結果「單位化」以防止數值爆炸。
* **收斂條件**：向量不再改變方向（各元素變化極小）。

### 2.5 QR 演算法 (QR Algorithm)
* **用途**：計算一個矩陣的「所有特徵值」。
* **狀態轉移**：將矩陣 $A$ 分解為 $Q$ 與 $R$ ($A = QR$)，反過來相乘產生下一個狀態 ($A_{next} = RQ$)。
* **收斂條件**：矩陣非對角線上的元素總和趨近於 0（收斂成對角/上三角矩陣）。

### 2.6 龍格-庫塔法 (RK4 ODE Solver)
* **用途**：數值求解常微分方程式（ODE），模擬時間推進。
* **狀態轉移**：計算 4 個不同位置的斜率，取加權平均來預測下一步狀態 `(時間t, 數值y)`。
* **收斂條件**：時間 $t$ 抵達使用者設定的終點。

### 2.7 PageRank (隨機衝浪者模型)
* **用途**：Google 早期網頁排序核心演算法。
* **狀態轉移**：網頁權重分佈向量乘上包含阻尼係數 (Damping factor) 的 Google 轉移矩陣。
* **收斂條件**：網頁權重分佈穩定，新舊向量距離小於 $10^{-6}$。

### 2.8 K-Means 聚類 (Hard EM 演算法)
* **用途**：非監督式分類（分群）。
* **狀態轉移**：
  * *E-step*: 計算距離，將資料點分配給最近的中心。
  * *M-step*: 將中心點移動到被分配到的點群幾何中心。
* **收斂條件**：所有中心點的位置不再發生變動。

### 2.9 EM 演算法 (雙硬幣潛在變數問題)
* **用途**：在有隱藏變數的情況下估計模型機率參數。
* **狀態轉移**：
  * *E-step*: 計算每一回合實驗結果由硬幣A或硬幣B產生的期望機率權重。
  * *M-step*: 根據權重重新統計次數，更新硬幣機率。
* **收斂條件**：機率估計值收斂穩定。

---

## 3. 完整 Python 程式碼實作

以下為包含通用迭代框架及上述所有演算法展示的完整 Python 程式碼：

```python
import numpy as np

# =====================================================================
# 1. 核心通用迭代框架 (Core Abstract Framework)
# =====================================================================
def generic_iterator(transition_func, is_converged, initial_state, max_iter=1000):
    """
    通用迭代法框架
    :param transition_func: 狀態推進函數 g(state) -> next_state
    :param is_converged: 終止/收斂判定函數 is_converged(state, next_state, iteration) -> bool
    :param initial_state: 初始狀態（純量、向量、矩陣或 Tuple）
    :return: 最終狀態, 實際迭代次數
    """
    state = initial_state
    
    for iteration in range(max_iter):
        next_state = transition_func(state)
        
        if is_converged(state, next_state, iteration):
            return next_state, iteration + 1
            
        state = next_state
        
    print("  [警告] 達到最大迭代次數仍未完全收斂")
    return state, max_iter


# =====================================================================
# 2. 各種經典迭代法的具體實作 (Concrete Implementations)
# =====================================================================

def demo_fixed_point():
    print("--- 1. 二維不動點迭代法 (Fixed-Point Iteration) ---")
    transition = lambda X: np.array([0.5 * X[0] - 0.2 * X[1] + 0.3, 0.2 * X[0] + 0.5 * X[1] + 0.4])
    converged = lambda old, new, i: np.linalg.norm(new - old) < 1e-6
    result, iters = generic_iterator(transition, converged, initial_state=np.array([0.0, 0.0]))
    print(f"結果: {np.round(result, 6)} (耗時 {iters} 次迭代)\n")


def demo_newton():
    print("--- 2. 牛頓法求根 (Newton's Method: x^2 - 4 = 0) ---")
    f = lambda x: x**2 - 4.0
    df = lambda x: 2.0 * x
    transition = lambda x: x - f(x) / df(x)
    converged = lambda old, new, i: abs(new - old) < 1e-6
    result, iters = generic_iterator(transition, converged, initial_state=1.0)
    print(f"結果: 根 x = {result:.6f} (耗時 {iters} 次迭代)\n")


def demo_gauss_seidel():
    print("--- 3. 高斯-賽得爾法 (Gauss-Seidel Linear Solver) ---")
    A = np.array([[4.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 4.0]])
    b = np.array([7.0, 2.0, 13.0])
    n = len(b)
    
    def transition(x):
        x_new = x.copy()
        for i in range(n):
            s = sum(A[i, j] * x_new[j] for j in range(n) if j != i)
            x_new[i] = (b[i] - s) / A[i, i]
        return x_new
        
    converged = lambda old, new, i: np.max(np.abs(new - old)) < 1e-6
    result, iters = generic_iterator(transition, converged, initial_state=np.zeros(n))
    print(f"結果: x = {np.round(result, 6)} (耗時 {iters} 次迭代)\n")


def demo_power_iteration():
    print("--- 4. 冪次迭代法 (Power Iteration: SVD / 主特徵向量) ---")
    A = np.array([[4.0, 1.0, 0.5], [1.0, 3.0, 0.2], [0.5, 0.2, 2.0]])
    n = A.shape[0]
    transition = lambda v: np.dot(A, v) / np.linalg.norm(np.dot(A, v))
    converged = lambda old, new, i: np.allclose(old, new, atol=1e-6)
    
    np.random.seed(42)
    v_init = np.random.rand(n)
    v_init /= np.linalg.norm(v_init)
    
    v_result, iters = generic_iterator(transition, converged, initial_state=v_init)
    eigenval = np.dot(v_result, np.dot(A, v_result))
    print(f"結果: 最大特徵值 = {eigenval:.6f} (耗時 {iters} 次迭代)\n")


def demo_qr_algorithm():
    print("--- 5. QR 演算法 (QR Algorithm: 計算所有特徵值) ---")
    A = np.array([[4.0, 1.0, -2.0], [1.0, 2.0, 0.0], [-2.0, 0.0, 3.0]], dtype=float)
    transition = lambda Ak: np.dot(*reversed(np.linalg.qr(Ak)))
    converged = lambda old, new, i: np.sum(np.abs(new - np.diag(np.diagonal(new)))) < 1e-6
    
    A_final, iters = generic_iterator(transition, converged, initial_state=A)
    print(f"結果: 所有特徵值 = {np.round(np.diagonal(A_final), 6)} (耗時 {iters} 次迭代)\n")


def demo_rk4():
    print("--- 6. 龍格-庫塔法 (RK4 ODE Solver: dy/dt = y - t + 1) ---")
    f = lambda t, y: y - t + 1
    t_end, h = 2.0, 0.2
    
    def transition(state):
        t, y = state
        k1 = f(t, y)
        k2 = f(t + 0.5 * h, y + 0.5 * h * k1)
        k3 = f(t + 0.5 * h, y + 0.5 * h * k2)
        k4 = f(t + h, y + h * k3)
        return (t + h, y + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4))
        
    converged = lambda old, new, i: new[0] >= t_end - 1e-9
    final_state, iters = generic_iterator(transition, converged, initial_state=(0.0, 1.0))
    print(f"結果: 於 t = {final_state[0]:.1f} 時, y = {final_state[1]:.6f} (耗時 {iters} 步)\n")


def demo_pagerank():
    print("--- 7. PageRank (Power Iteration 隨機衝浪者模型) ---")
    # 網頁跳轉轉移矩陣 M
    M = np.array([[0.0, 0.0, 1.0, 0.5],
                  [1/3, 0.0, 0.0, 0.5],
                  [1/3, 0.5, 0.0, 0.0],
                  [1/3, 0.5, 0.0, 0.0]])
    d = 0.85
    n = M.shape[0]
    G = d * M + (1 - d) / n * np.ones((n, n)) # Google 矩陣
    
    transition = lambda r: np.dot(G, r)
    converged = lambda old, new, i: np.linalg.norm(new - old) < 1e-6
    
    r_init = np.ones(n) / n
    r_result, iters = generic_iterator(transition, converged, initial_state=r_init)
    print(f"結果: 網頁權重分佈 = {np.round(r_result, 4)} (耗時 {iters} 次迭代)\n")


def demo_kmeans():
    print("--- 8. K-Means 聚類 (Hard EM 演算法) ---")
    np.random.seed(42)
    X = np.vstack([np.random.randn(15, 2) + np.array([2, 2]),
                   np.random.randn(15, 2) + np.array([-2, -2])])
    k = 2
    init_centroids = X[:k].copy()
    
    def transition(centroids):
        # E-step: 分配標籤
        distances = np.linalg.norm(X[:, np.newaxis] - centroids, axis=2)
        labels = np.argmin(distances, axis=1)
        # M-step: 更新中心點
        return np.array([X[labels == j].mean(axis=0) for j in range(k)])
        
    converged = lambda old, new, i: np.max(np.abs(new - old)) < 1e-6
    centroids_result, iters = generic_iterator(transition, converged, initial_state=init_centroids)
    print(f"結果: 最終分群中心 = \n{np.round(centroids_result, 4)} (耗時 {iters} 次迭代)\n")


def demo_em_two_coin():
    print("--- 9. EM 演算法 (Two-Coin Problem 潛在變數估計) ---")
    trials = np.array([[5, 5], [9, 1], [8, 2], [4, 6], [7, 3]])
    init_theta = (0.6, 0.5) # (theta_A, theta_B)
    
    def transition(theta):
        theta_A, theta_B = theta
        cA_h = cA_t = cB_h = cB_t = 0.0
        
        # E-step: 計算期望機率權重
        for h, t in trials:
            l_A = (theta_A ** h) * ((1 - theta_A) ** t)
            l_B = (theta_B ** h) * ((1 - theta_B) ** t)
            p_A = l_A / (l_A + l_B) if (l_A + l_B) > 0 else 0.5
            p_B = 1.0 - p_A
            
            cA_h += p_A * h; cA_t += p_A * t
            cB_h += p_B * h; cB_t += p_B * t
            
        # M-step: 更新參數
        return (cA_h / (cA_h + cA_t), cB_h / (cB_h + cB_t))
        
    converged = lambda old, new, i: abs(new[0] - old[0]) < 1e-6 and abs(new[1] - old[1]) < 1e-6
    theta_result, iters = generic_iterator(transition, converged, initial_state=init_theta)
    print(f"結果: 估計硬幣機率 Theta_A = {theta_result[0]:.4f}, Theta_B = {theta_result[1]:.4f} (耗時 {iters} 次迭代)\n")


# =====================================================================
# 4. 執行所有經典演算法總覽
# =====================================================================
if __name__ == "__main__":
    print("=========================================================")
    print("   全系列經典迭代演算法 - 統一抽象框架展示 (Unified Framework)")
    print("=========================================================\n")
    
    demo_fixed_point()
    demo_newton()
    demo_gauss_seidel()
    demo_power_iteration()
    demo_qr_algorithm()
    demo_rk4()
    demo_pagerank()
    demo_kmeans()
    demo_em_two_coin()
```

---

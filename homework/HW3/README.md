
# SAT 求解與真值表窮舉法說明

## 1. 簡介 (Introduction)
布林可滿足性問題 (Boolean Satisfiability Problem, 簡稱 **SAT**) 是計算機科學與數理邏輯中的核心問題。給定一個包含多個布林變數的邏輯公式，SAT 問題的核心目標在於尋找一組變數指派（True 或 False），使得整個邏輯公式的計算結果為真（True）。如果存在這樣的指派，則該公式稱為**可滿足 (SAT)**；若所有可能的組合都無法使公式成立，則稱為**不可滿足 (UNSAT)**。

**真值表窮舉法 (Brute-Force Truth Table Enumeration)** 是一種最直觀的求解方式：透過系統性地列舉所有可能的真值組合來驗證公式。

---

## 2. 數學原理與複雜度
若一個邏輯公式包含 $n$ 個獨立的布林變數 $x_1, x_2, \dots, x_n$，每一個變數都有兩種可能的取值（$\text{True}$ 或 $\text{False}$，或以 $1$ 和 $0$ 表示）。
    
根據排列組合原理，總共會有 $2^n$ 種不同的真值組合：
$$\text{總組合數} = 2^n$$

隨著變數數量 $n$ 增加，真值表的規模呈指數級成長：
* 當 $n = 10$ 時，$2^{10} = 1,024$ 種組合。
* 當 $n = 20$ 時，$2^{20} = 1,048,576$ 種組合。
* 當 $n = 50$ 時，$2^{50} \approx 1.12 \times 10^{15}$ 種組合（以現今電腦運算速度而言，窮舉將變得極其緩慢）。

---

## 3. Python 程式實作解析
在先前提供的程式碼中，我們利用了 Python 的 `itertools.product` 來高效產生笛卡兒積組合：

```python
import itertools

def solve_sat_by_truth_table(variables, formula_func):
    n = len(variables)
    satisfiable = False
    solutions = []

    # 遍歷所有 2^n 種 True/False 組合
    for values in itertools.product([False, True], repeat=n):
        assignment = dict(zip(variables, values))
        result = formula_func(assignment)
        
        if result:
            satisfiable = True
            solutions.append(assignment)

    return satisfiable, solutions
```

### 關鍵元件說明：
1. **`itertools.product([False, True], repeat=n)`**：自動生成長度為 $n$ 的布林組合序列。
2. **變數對應 (`dict(zip(...))`)**：將每次產生的布林值陣列對應回變數名稱（例如 `{'A': True, 'B': False}`），便於在自定義邏輯函式中直覺操作。
3. **結果判定**：只要迴圈中出現任一組 `result == True`，即標記為可滿足（SAT）並記錄該解。

---

## 4. 適用場景與限制
* **優點**：實作簡單直觀、絕對不會漏掉任何可能的解、對於變數數量較少（如 $n \le 20$）的小型問題執行速度極快。
* **缺點**：面對大規模的 SAT 問題（如工業級電路驗證、密碼學分析或軟體模型檢測中常有成千上萬個變數），時間複雜度 $O(2^n)$ 會導致空間與時間資源耗盡。
* **未來進階方向**：真實世界的大型 SAT 求解器（如 MiniSat、Glucose 等）不會使用窮舉法，而是採用 **DPLL 演算法** 或 **CDCL (Conflict-Driven Clause Learning)**，透過啟發式搜尋、變數選擇與子句學習來進行強大且高效的剪枝。

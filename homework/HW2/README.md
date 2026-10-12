# 遞迴方程式求解與複雜度分析指南

本文件整理了四個常見遞迴方程式（Recurrence Relations）的精確數學解、Big O 演算法複雜度分析，以及使用 Python 進行符號求解與數值驗證的方法。

---

## 1. 遞迴方程式總結比較表

| 編號 | 遞迴方程式 | 精確解 (Closed-form) | Big O 複雜度 | 應用場景 / 類型 |
| :---: | :--- | :--- | :--- | :--- |
| **1** | $T(n) = T(n-1) + 8, \quad T(1)=1$ | $8n - 7$ | $O(n)$ | 線性遞減（如迴圈） |
| **2** | $T(n) = 2T(n-1) + 9, \quad T(1)=1$ | $10 \cdot 2^{n-1} - 9$ | $O(2^n)$ | 指數成長（如費波那契非優化版） |
| **3** | $T(n) = 2T(n/2) + 1, \quad T(1)=1$ | $2n - 1$ | $O(n)$ | 分治法（如歸併排序 Merge Sort） |
| **4** | $T(n) = T(n/2) + 1, \quad T(1)=1$ | $\log_2 n + 1$ | $O(\log n)$ | 分治法（如二分搜尋 Binary Search） |

---

## 2. 詳細解析與推導

### 題目一：$T(n) = T(n-1) + 8$
* **方法**：遞迴展開法（Substitution Method）
* **推導**：
  $$T(n) = T(n-2) + 8 + 8 = T(n-2) + 2 \times 8$$
  展開 $k$ 次後：$T(n) = T(n-k) + 8k$
  令 $n-k = 1 \implies k = n-1$，代入可得：
  $$T(n) = T(1) + 8(n-1) = 1 + 8n - 8 = 8n - 7$$

### 題目二：$T(n) = 2T(n-1) + 9$
* **方法**：遞迴展開法與等比級數求和
* **推導**：
  展開 $k$ 次後：$T(n) = 2^k T(n-k) + 9 \sum_{i=0}^{k-1} 2^i$
  令 $n-k = 1 \implies k = n-1$，代入可得：
  $$T(n) = 2^{n-1}T(1) + 9(2^{n-1} - 1) = 2^{n-1} + 9 \cdot 2^{n-1} - 9 = 10 \cdot 2^{n-1} - 9$$

### 題目三：$T(n) = 2T(n/2) + 1$
* **方法**：主定理（Master Theorem）
* **分析**：參數 $a=2, b=2, f(n)=1$。
  計算 $n^{\log_b a} = n^{\log_2 2} = n^1 = n$。
  由於 $f(n) = O(n^0)$ 小於 $n^1$，符合主定理第一種情況，複雜度為 $\Theta(n)$。

### 題目四：$T(n) = T(n/2) + 1$
* **方法**：主定理（Master Theorem）
* **分析**：參數 $a=1, b=2, f(n)=1$。
  計算 $n^{\log_b a} = n^{\log_2 1} = n^0 = 1$。
  由於 $f(n) = \Theta(n^0) = \Theta(1)$，符合主定理第二種情況，複雜度為 $\Theta(\log n)$。

---

## 3. Python 程式碼驗證

使用 Python 的 `sympy` 庫進行符號求解，並用遞迴函數進行數值驗證：

```python
import sympy as sp

# 定義符號與函數
n = sp.Symbol('n', integer=True)
T = sp.Function('T')

# 1. 求解 T(n) = T(n-1) + 8, T(1) = 1
eq1 = sp.Eq(T(n), T(n - 1) + 8)
sol1 = sp.rsolve(eq1, T(n), {T(1): 1})
print("方程式 1 精確解:", sol1)  # 輸出: 8*n - 7

# 2. 求解 T(n) = 2*T(n-1) + 9, T(1) = 1
eq2 = sp.Eq(T(n), 2 * T(n - 1) + 9)
sol2 = sp.rsolve(eq2, T(n), {T(1): 1})
print("方程式 2 精確解:", sol2)  # 輸出: 10*2**(n-1) - 9


# 3 & 4 數值驗證函數
def T3(n):
  if n <= 1:
    return 1
  return 2 * T3(n // 2) + 1


def T4(n):
  if n <= 1:
    return 1
  return T4(n // 2) + 1


print("方程式 3 當 n=8 時:", T3(8))  # 輸出: 15
print("方程式 4 當 n=8 時:", T4(8))  # 輸出: 4
```

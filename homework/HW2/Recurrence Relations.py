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


# 3 & 4 屬於分治法型態，可用遞迴函數進行數值驗證
def T3(n):
  if n <= 1:
    return 1
  return 2 * T3(n // 2) + 1


def T4(n):
  if n <= 1:
    return 1
  return T4(n // 2) + 1


print("方程式 3 當 n=8 時:", T3(8))  # 輸出: 15 (2*8 - 1)
print("方程式 4 當 n=8 時:", T4(8))  # 輸出: 4 (log2(8) + 1)

import sys
import time

# 調整遞迴深度限制（以防萬一，雖然 n = 100 預設的 1000 就夠用）
sys.setrecursionlimit(2000)

# ==========================================
# 各種方法實作
# ==========================================


# 方法 1：使用 Python 內建次方運算子
def power2n_method1(n):
  return 2**n


# 方法 2a：用遞迴（加法展開：power2n(n-1) + power2n(n-1)）
def power2n_method2a(n):
  if n == 0:
    return 1
  return power2n_method2a(n - 1) + power2n_method2a(n - 1)


# 方法 2b：用遞迴（乘法：2 * power2n(n-1)）
def power2n_method2b(n):
  if n == 0:
    return 1
  return 2 * power2n_method2b(n - 1)


# 方法 3：用遞迴 + 查表（Memoization）
memo = {0: 1}


def power2n_method3(n):
  if n in memo:
    return memo[n]
  # 根據題目提示使用加法並查表
  memo[n] = power2n_method3(n - 1) + power2n_method3(n - 1)
  return memo[n]


# ==========================================
# 主程式測試
# ==========================================
if __name__ == "__main__":
  n = 100
  print(f"================ 測試 n = {n} ================\n")

  # 1. 測試方法 1
  start = time.perf_counter()
  ans1 = power2n_method1(n)
  end = time.perf_counter()
  print(f"[方法 1] 2**n")
  print(f"結果: {ans1}")
  print(f"耗時: {(end - start) * 1000:.6f} 毫秒\n")

  # 2. 測試方法 2b
  start = time.perf_counter()
  ans2b = power2n_method2b(n)
  end = time.perf_counter()
  print(f"[方法 2b] 遞迴乘法 (2 * f(n-1))")
  print(f"結果: {ans2b}")
  print(f"耗時: {(end - start) * 1000:.6f} 毫秒\n")

  # 3. 測試方法 3
  start = time.perf_counter()
  ans3 = power2n_method3(n)
  end = time.perf_counter()
  print(f"[方法 3] 遞迴 + 查表 (Memoization)")
  print(f"結果: {ans3}")
  print(f"耗時: {(end - start) * 1000:.6f} 毫秒\n")

  # 4. 方法 2a 說明
  print(f"[方法 2a] 遞迴加法 (f(n-1) + f(n-1))")
  print(
      "狀態：【出不來】當 n = 100 時，時間複雜度為 O(2^n)。"
      "\n總共需要執行約 2^100 次運算（約 1.26 × 10^30 次），"
      "\n若實際執行會卡死在無窮無盡的重複計算中，因此在主程式中略過不測。"
  )

import sys
import time

sys.setrecursionlimit(2000)

def power2n_method1(n):
  return 2**n

def power2n_method2a(n):
  if n == 0:
    return 1
  return power2n_method2a(n - 1) + power2n_method2a(n - 1)

def power2n_method2b(n):
  if n == 0:
    return 1
  return 2 * power2n_method2b(n - 1)

memo = {0: 1}

def power2n_method3(n):
  if n in memo:
    return memo[n]
  memo[n] = power2n_method3(n - 1) + power2n_method3(n - 1)
  return memo[n]

if __name__ == "__main__":
  n = 100
  print(f"================ 測試 n = {n} ================\n")

  start = time.perf_counter()
  ans1 = power2n_method1(n)
  end = time.perf_counter()
  print(f"[方法 1] 2**n")
  print(f"結果: {ans1}")
  print(f"耗時: {(end - start) * 1000:.6f} 毫秒\n")

  start = time.perf_counter()
  ans2b = power2n_method2b(n)
  end = time.perf_counter()
  print(f"[方法 2b] 遞迴乘法 (2 * f(n-1))")
  print(f"結果: {ans2b}")
  print(f"耗時: {(end - start) * 1000:.6f} 毫秒\n")

  start = time.perf_counter()
  ans3 = power2n_method3(n)
  end = time.perf_counter()
  print(f"[方法 3] 遞迴 + 查表 (Memoization)")
  print(f"結果: {ans3}")
  print(f"耗時: {(end - start) * 1000:.6f} 毫秒\n")

  print(f"[方法 2a] 遞迴加法 (f(n-1) + f(n-1))")
  print(
      "狀態：【出不來】當 n = 100 時，時間複雜度為 O(2^n)。"
      "\n總共需要執行約 2^100 次運算（約 1.26 × 10^30 次），"
      "\n若實際執行會卡死在無窮無盡的重複計算當中，因此在主程式中不進行測試。"
  )
